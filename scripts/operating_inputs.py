#!/usr/bin/env python3
"""Calculation inputs that describe the world around the board: each needs a source (user 2026-11-04).

Matrix R2 CALC-CH-START checked "启动浪涌 ≤ I(OL) 下限" with a 1 A load written into the script and the parameter's name;
no requirement, datasheet or user gave it, and the requirement's 1.5 A reverses the result. G03-017 had listed the startup
load all along, but a rule's `inputs` are free text no audit read. Three layers (references/design-closure.md):

- declared inputs (`input_role`) must have a source, whatever the role; a startup calculation must declare its load, and
  its surge must be recomputable from a `formula` that uses that load;
- a number added inside a name or derivation and declared nowhere is an error, in any calculation;
- the rest cannot be judged by a script: the roles the cited rules' free-text `inputs` name are classified here by keyword
  and listed for review, so no rule needs annotating by hand. The list blocks nothing.
"""
import ast
import math
import operator
import re

from schematic_layout import part_classes

# role: (title, pattern on a rule's `inputs` text, pattern on a parameter's name). The first is deliberately broad, it only
# fills a review list; the second names the quantity itself, and is what the weak-source list reads.
ROLES = {
    'startup_load': ('启动期负载特性', r'启动期.{0,4}负载|负载启动特性|内部变换器启动电流',
                     r'启动.{0,8}负载|负载.{0,8}启动|启动期.{0,12}(电流|功率)|软启动.{0,4}(输入)?(电流|功率)'),
    'load_capacitance': ('外接负载电容', r'下游总电容|负载输入电容|允许热插入的负载电容|负载电容',
                         r'负载.{0,6}电容|设备.{0,4}输入电容|下游.{0,4}电容'),
    'load_demand': ('负载功率与电流', r'工况矩阵|各模式负载|负载功率|最大负载|最小负载电流|负载范围|最大正常电流|负载阻抗|任务阶段的峰值|负载类型|实际负载|'
                    r'代表性负载|各支路负载|最大工作电流|最大持续电流|中断期间保持的轨与负载',
                    r'负载(电流|功率)|单路最大|满载电流|负载阻抗'),
    'source_impedance': ('源阻抗与线路阻抗', r'源阻抗|源、负载阻抗|源最小阻抗|串联阻抗|输入线路电感|线束与输入滤波电感', r'源阻抗|源内阻|线路(阻抗|电感|电阻)|线缆(电阻|阻抗|电感)'),
    'input_window': ('输入电压窗与上电斜率', r'输入电压窗|输入电压范围|额定电压范围|稳态电压|输入电压上升斜率|最低输入电压|交流额定电压|适配器电压|输入最低值',
                     r'输入电压|母线电压(上限|下限|范围)|供电范围'),
    'ambient_temperature': ('环境温度', r'环境温度|工作温度|高低温|最坏工况|温度、负载', r'环境温度|壳内温度|机箱内温度|\bT_?A\b'),
    'external_transient': ('外部瞬态与误接', r'浪涌等级|尖峰与浪涌|暂降|中断与|最大负向电压|过压幅度|共模干扰等级|地电位差|可能短到的最高电压|非正常行为|差分噪声',
                           r'浪涌等级|地电位差|共模(电压|干扰)'),
    'cable_topology': ('线缆与总线拓扑', r'线长|线缆(?!侧)|总线长度|电缆总长|节点数|节点间距|分支长度|最远两节点|线束与连接器', r'线缆长度|线长|总线长度|节点数'),
}
ROLE_NAMES = tuple(ROLES)
# How a requirement says it has the condition, for the review list only.
_REQUIREMENT = {'startup_load': re.compile(r'启动|上电'), 'load_capacitance': re.compile(r'电容'), 'load_demand': re.compile(r'负载|功耗|单路|每路'),
                'source_impedance': re.compile(r'源阻抗|故障电流|线路压降|线缆'), 'input_window': re.compile(r'输入|供电.{0,20}\d+(\.\d+)?\s*V'),
                'ambient_temperature': re.compile(r'温度|℃'), 'external_transient': re.compile(r'浪涌|ESD|EFT|反接|暂降|中断|误接|共模|尖峰'),
                'cable_topology': re.compile(r'线缆|总线|节点|线长|距离|航插')}
_INPUT = {k: re.compile(v[1], re.I) for k, v in ROLES.items()}
_PARAM = {k: re.compile(v[2], re.I) for k, v in ROLES.items()}

# The switch parts G03-017 is about: by what the datasheet library files them under, or their name and series.
HOT_FOLDER = re.compile(r'热插拔|eFuse|负载开关', re.I)
HOT_CUES = ('efuse', 'hotswap', 'loadswitch', 'surgestopper', 'powerdistributionswitch', 'currentlimitswitch')
HOT_SERIES = re.compile(r'^(?:TPS2[2-6]\d{2,3}|TPS16\d\d|LM506\d|LM749\d\d|LTC42\d\d|LTC43[68]\d|LT42\d\d|ADM12\d\d|AP22\d\d|FPF2\d{2,3}|'
                        r'MAX5[89]\d\d|SIP32\d{3})', re.I)
# A check of startup behaviour (current, power, energy or time): a TVS's 8/20 µs surge current is not one.
STARTUP_CHECK = re.compile(r'启动|合闸|软启|缓启|预充|dv/?dt|inrush|soft.?start', re.I)
SURGE_CHECK = re.compile(r'启动浪涌|合闸浪涌|浪涌电流|^浪涌|启动电流|充电电流|inrush', re.I)
PULSE_WAVE = re.compile(r'\d+\s*/\s*\d+\s*µ?s')
STARTUP_UNIT = re.compile(r'^(?:[munµ]?[AWJ]|[munµ]?s)$')
CURRENT_UNIT = re.compile(r'^[munµ]?A$')

# A number added or subtracted inside a name: "负载电容上限 + 1 A", "VBR 上限＋1 V 动态". A space on one side only is a sign
# ("共模 +7 V"), a value before it is two values ("24V+5V 轨").
_SI = {'p': 1e-12, 'n': 1e-9, 'µ': 1e-6, 'u': 1e-6, 'm': 1e-3, '': 1, 'k': 1e3, 'M': 1e6}
_ADDED = re.compile(r'(?<=[^\s+＋−\d.（(，,/])(\s*)([+＋−])(\s*)(\d+(?:\.\d+)?)\s*([pnµumkM]?)(A|V|W|F|Ω|H|s|J|Hz)(?![A-Za-z])')
_VALUE_BEFORE = re.compile(r'\d\s*[pnµumkM]?(?:A|V|W|F|Ω|H|s|J|Hz)$')
_UNIT = re.compile(r'^([pnµumkM]?)(A|V|W|F|Ω|H|s|J|Hz)$')


def text(value):
    return isinstance(value, str) and bool(value.strip())


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def params_of(row):
    return [p for p in row.get('parameters') or [] if isinstance(p, dict)]


def checks_of(row):
    return [c for c in row.get('checks') or [] if isinstance(c, dict)]


def classify_input(words):
    """The roles a free-text rule input names; a clause about a part's datasheet values is that part's data, not a condition."""
    clauses = [c for c in re.split(r'[；;]', str(words or '')) if not re.search(r'手册(极值|保证值|的)|（手册）|准确料号', c)]
    return [role for role in ROLE_NAMES if any(_INPUT[role].search(c) for c in clauses)]


def rule_roles(rule):
    """{role: [input text]} of a shared guideline rule."""
    found = {}
    for words in rule.get('inputs') or []:
        for role in classify_input(words):
            found.setdefault(role, []).append(words)
    return found


def library_stats(library):
    """How many rules, and which, list each role."""
    stats = {role: [] for role in ROLE_NAMES}
    for rule in library['criteria']:
        for role in rule_roles(rule):
            stats[role].append(rule['id'])
    return stats


def hot_part(comp):
    """An eFuse, hot-swap controller, load switch or surge stopper, from its library folder, name or series."""
    if part_classes.kind_of(comp)[0] != 'ic':
        return False    # a resettable fuse holds "efuse" too
    names = ' '.join(str(comp.get(k) or '') for k in ('lib_id', 'value', 'mpn', 'description'))
    fields = ' '.join(str(v) for v in part_classes.fields(comp).values())
    flat = part_classes.squash(names + ' ' + fields)
    parts = [str(comp.get(k) or '').split(':')[-1].strip() for k in ('value', 'mpn', 'lib_id')]
    return bool(HOT_FOLDER.search(str(comp.get('datasheet') or ''))
                or any(cue in flat for cue in HOT_CUES) or any(HOT_SERIES.match(p) for p in parts))


def startup_calculation(row, hot):
    """Why this calculation is a startup calculation: it cites G03-017, or it checks a switch part's startup."""
    if 'G03-017' in (row.get('guidelines') or []):
        return 'G03-017'
    parts = sorted(set(r for r in row.get('refs') or [] if isinstance(r, str)) & hot)
    if parts and any(STARTUP_CHECK.search(str(c.get('name') or '')) and not PULSE_WAVE.search(str(c.get('name') or ''))
                     and STARTUP_UNIT.match(str(c.get('unit') or '').strip()) for c in checks_of(row)):
        return parts[0]
    return None


def surge_checks(row):
    return [c for c in checks_of(row) if SURGE_CHECK.search(str(c.get('name') or '')) and not PULSE_WAVE.search(str(c.get('name') or ''))
            and CURRENT_UNIT.match(str(c.get('unit') or '').strip()) and finite(c.get('value'))]


# --- formula: a derived value the audit can recompute -------------------------------------------------------------------

_BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow}
_CALLS = {'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp, 'abs': abs, 'min': min, 'max': max}


def _evaluate(node, values):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body, values)
    if isinstance(node, ast.Constant) and finite(node.value):
        return float(node.value)
    if isinstance(node, ast.Name):
        return float(values[node.id])
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        return _BINARY[type(node.op)](_evaluate(node.left, values), _evaluate(node.right, values))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_evaluate(node.operand, values)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _CALLS and not node.keywords:
        return _CALLS[node.func.id](*[_evaluate(a, values) for a in node.args])
    raise ValueError('只能用四则、乘方和 %s' % '、'.join(_CALLS))


def _constant(node):
    """The value of a subexpression made of numbers only, else None."""
    if isinstance(node, ast.Constant) and finite(node.value):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _constant(node.operand)
        return None if inner is None else -inner
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        a, b = _constant(node.left), _constant(node.right)
        if a is None or b is None:
            return None
        try:
            value = _BINARY[type(node.op)](a, b)
        except (ArithmeticError, ValueError):
            return None
        return value if finite(value) else None
    return None


def _plain_factor(value):
    """A unit conversion or a textbook factor (½CV²), not a quantity."""
    if value == 0 or not finite(value):
        return False
    magnitude = abs(value)
    return magnitude in (0.5, 2, 3, 4) or math.isclose(math.log10(magnitude), round(math.log10(magnitude)), abs_tol=1e-9)


def _ratio(node):
    return isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Pow))


def literal_problems(root):
    """Numbers in a formula that are quantities: every one has to be a declared parameter, with its own source."""
    problems = []

    def terms(node):
        """The additive terms of the root, through factors that are plain numbers."""
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            return terms(node.left) + terms(node.right)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Div)):
            right, left = _constant(node.right), _constant(node.left)
            if right is not None and _plain_factor(right):
                return terms(node.left)
            if left is not None and _plain_factor(left) and isinstance(node.op, ast.Mult):
                return terms(node.right)
        return [node]

    def walk(node, sibling_ratio=False):
        value = _constant(node)
        if value is not None:
            if not (_plain_factor(value) or (value == 1 and sibling_ratio)):
                problems.append('%g' % value)
            return
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            left, right = _constant(node.left), _constant(node.right)
            if left is not None or right is not None:
                # Only 1 + R1/R2 and 1 − x/y: a dimensionless ratio. Anything else adds a quantity.
                number, other = (left, node.right) if left is not None else (right, node.left)
                if number != 1 or not _ratio(other):
                    problems.append('%g' % number)
                walk(other)
                return
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            walk(node.left)     # an exponent is a textbook form
            return
        if isinstance(node, ast.Call):
            for arg in node.args:
                if _constant(arg) is not None:
                    problems.append('%g' % _constant(arg))
                else:
                    walk(arg)
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.expr):
                walk(child)

    for term in terms(root):
        value = _constant(term)
        if value is not None:
            problems.append('%g' % value)
        else:
            walk(term)
    return problems


def audit_formula(key, p, by_name, error):
    """A parameter's `formula` {expr, vars: {symbol: parameter name}} is recomputed: result, and no quantity in the expression."""
    where = '%s:%s' % (key, p.get('name'))
    formula = p.get('formula')
    if not isinstance(formula, dict) or not text(formula.get('expr')) or not isinstance(formula.get('vars'), dict):
        error('formula_schema', where + '：formula 写 {expr, vars: {符号: 本计算的参数名}}')
        return False
    unknown = [n for n in formula['vars'].values() if n not in by_name]
    if unknown:
        error('formula_schema', '%s：vars 里的 %s 不是本计算的参数' % (where, '、'.join(map(str, unknown))))
        return False
    values = {s: by_name[n].get('value') for s, n in formula['vars'].items()}
    try:
        tree = ast.parse(formula['expr'], mode='eval')
        result = _evaluate(tree, values)
        if not finite(result):
            raise ValueError('结果不是有限实数')
    except (SyntaxError, ValueError, KeyError, TypeError, ArithmeticError) as exc:
        error('formula_schema', '%s：算式 %s 算不了（%s）' % (where, formula['expr'], exc))
        return False
    good = True
    hidden = literal_problems(tree.body)
    if hidden:
        error('formula_hidden_literal', '%s：算式 %s 里的 %s 是写死的数；声明成参数并写来源（只允许单位换算的 10 的幂、½CV² 这类系数、1+R1/R2 的 1）' % (
            where, formula['expr'], '、'.join(hidden)))
        good = False
    if not (finite(p.get('value')) and math.isclose(result, p['value'], rel_tol=1e-3, abs_tol=1e-12)):
        error('formula_mismatch', '%s：算式 %s 用声明的参数算出 %g，写的是 %s；差的那部分没有声明' % (where, formula['expr'], result, p.get('value')))
        good = False
    return good


def _uses_role(p, role, by_name, seen=()):
    if p.get('input_role') == role:
        return True
    formula = p.get('formula')
    if p.get('name') in seen or not isinstance(formula, dict) or not isinstance(formula.get('vars'), dict):
        return False
    return any(n in by_name and _uses_role(by_name[n], role, by_name, seen + (p.get('name'),)) for n in formula['vars'].values())


# --- where a declared input comes from ------------------------------------------------------------------------------------


def source_problem(key, p, calculations, requirements, clarifications, work, comps, hot, by_name, shown):
    """Why a declared input has no acceptable source, or None. Accepted: a requirement (a user's answer is written back as
    one) showing the number; a datasheet page; a load this board carries itself (`load_refs`), which ASG may estimate; a
    requirement question the user deferred; a value derived from inputs that have sources."""
    basis, source = p.get('basis'), str(p.get('source') or '')
    if basis == 'requirement':
        req = requirements.get(source[4:]) if source.startswith('req:') else None
        if req is not None and finite(p.get('value')) and not shown(p['value'], req.get('text')):
            return '需求 %s 的文字里没有 %g；写需求给的数，换算出来的写 derived 和 formula' % (source[4:], p['value'])
        return None     # a missing requirement is already requirement_parameter_without_requirement
    if basis in ('guaranteed', 'typical'):
        return None     # the datasheet citation is checked with every parameter
    if basis == 'derived':
        if source.startswith('calc:') and source[5:] != key:
            if any(q.get('input_role') == p.get('input_role') for q in params_of(calculations.get(source[5:]) or {})):
                return None
            return '%s 没有声明这个工况' % source[5:]
        if isinstance(p.get('formula'), dict) and isinstance(p['formula'].get('vars'), dict):
            def unsourced(q):
                if q.get('basis') in ('model', 'design_choice', 'unspecified', 'constant'):
                    return not q.get('load_refs') and not q.get('clarification')
                return q.get('basis') == 'derived' and str(q.get('source')) == 'calc:' + key and not isinstance(q.get('formula'), dict)
            weak = [n for n in p['formula']['vars'].values() if n in by_name and unsourced(by_name[n])]
            return ('算式用的 %s 自己没有来源' % '、'.join(weak)) if weak else None
        return '写 formula（用有来源的参数算出），或 source 指向另一条声明了它的计算'
    if basis in ('model', 'design_choice', 'unspecified'):
        loads = p.get('load_refs')
        if isinstance(loads, list) and loads:
            wrong = [r for r in loads if r not in comps or r in hot or part_classes.kind_of(comps[r])[0] == 'connector']
            if wrong:
                return 'load_refs 的 %s 不是本板上的负载器件（不能是开关自身或连接器）' % '、'.join(map(str, wrong))
            return None
        cl = p.get('clarification')
        if text(cl):
            answer = (clarifications.get(cl) or {}).get('answer') or {}
            if answer.get('decision') != 'DEFERRED':
                return '%s 不是用户暂缓的需求澄清；用户已答复的写回需求，引 req:' % cl
            if not any(w.get('stage') == 'requirement' and w.get('status') == 'open' and w.get('clarification') == cl
                       and key in (w.get('calculations') or []) for w in work.values()):
                return '%s 要有一件未关闭的 requirement 待办，calculations 列这条计算' % cl
            return None
        return '工况不能由 ASG 自定：写进需求澄清问用户，答复写回需求后引 req:，或引手册页；负载在本板上的写 load_refs'
    return '依据 %s 不能作工况来源' % basis


def _opaque_currents(key, p, by_name, seen=()):
    """Currents a surge formula adds that are derived here without a formula of their own: the load could sit inside one."""
    found = []
    formula = p.get('formula')
    for n in (formula.get('vars') or {}).values() if isinstance(formula, dict) and isinstance(formula.get('vars'), dict) else ():
        q = by_name.get(n)
        if q is None or n in seen:
            continue
        if isinstance(q.get('formula'), dict):
            found += _opaque_currents(key, q, by_name, seen + (n,))
        elif (q.get('basis') == 'derived' and str(q.get('source')) == 'calc:' + key and q.get('input_role') is None
              and CURRENT_UNIT.match(str(q.get('unit') or '').strip())):
            found.append(n)
    return found


def audit_roles(calculations, requirements, clarifications, work, intent, error, shown):
    """The hard layer. Returns what the record declared."""
    comps = {c['ref']: c for c in intent.get('components') or [] if isinstance(c, dict) and 'ref' in c}
    hot = {r for r, c in comps.items() if hot_part(c)}
    declared = []
    startup = {}
    for key, row in calculations.items():
        params = params_of(row)
        by_name = {}
        for p in params:
            by_name.setdefault(p.get('name'), p)
        for p in params:
            if 'formula' in p:
                audit_formula(key, p, by_name, error)
            role = p.get('input_role')
            if role is None:
                continue
            where = '%s:%s' % (key, p.get('name'))
            if role not in ROLES:
                error('schema', '%s：input_role 取 %s' % (where, '/'.join(ROLE_NAMES)))
                continue
            problem = source_problem(key, p, calculations, requirements, clarifications, work, comps, hot, by_name, shown)
            declared.append({'calculation': key, 'parameter': p.get('name'), 'role': role, 'basis': p.get('basis'),
                             'value': p.get('value'), 'unit': p.get('unit'), 'source': p.get('source') or p.get('clarification') or p.get('load_refs')})
            if problem:
                error('operating_input_without_source', '%s（%s）：%s' % (where, ROLES[role][0], problem))
        why = startup_calculation(row, hot)
        if why is None:
            continue
        startup[key] = why
        loads = [p for p in params if p.get('input_role') == 'startup_load']
        if not loads:
            looks = [p.get('name') for p in params if _PARAM['startup_load'].search(str(p.get('name') or ''))]
            error('startup_load_undeclared', '%s（%s）：启动计算要把启动期负载（阻性/恒流/恒功率的值，后级 UVLO 开启前的负载）声明成参数，写 '
                  'input_role: startup_load，来源是需求、用户决定或手册；需求没给就进需求澄清问用户%s' % (
                      key, why if why == 'G03-017' else '%s 的启动' % why,
                      '；疑似的参数：%s' % '、'.join(map(str, looks)) if looks else ''))
        for p in params:    # the load's capacitance is the same kind of number: G03-017 lists both
            if p.get('input_role') is None and p.get('basis') in ('model', 'design_choice') and _PARAM['load_capacitance'].search(str(p.get('name') or '')):
                problem = source_problem(key, p, calculations, requirements, clarifications, work, comps, hot, by_name, shown)
                if problem:
                    error('operating_input_without_source', '%s:%s（%s，%s）：%s' % (key, p.get('name'), ROLES['load_capacitance'][0], p.get('basis'), problem))
        for c in surge_checks(row):
            where = '%s:%s' % (key, c.get('name'))
            unit = str(c.get('unit') or '').strip()
            found = [p for p in params if finite(p.get('value')) and str(p.get('unit') or '').strip() == unit
                     and math.isclose(p['value'], c['value'], rel_tol=1e-3)]
            if not found:
                error('startup_surge_unbound', '%s：检查值 %g %s 不是本计算的任何参数；把它写成 derived 参数和 formula，看得出由哪些量相加' % (where, c['value'], unit))
                continue
            p = found[0]
            if not isinstance(p.get('formula'), dict) and p.get('input_role') != 'startup_load':
                error('startup_surge_without_formula', '%s：%s 是 %s，写 formula {expr, vars} 让审计复算，负载不能藏在算式或名字里' % (where, p.get('name'), p.get('basis')))
            elif _opaque_currents(key, p, by_name):
                error('startup_surge_without_formula', '%s：算式用的电流 %s 也要写 formula，负载不能藏在里面' % (where, '、'.join(_opaque_currents(key, p, by_name))))
            elif loads and not _uses_role(p, 'startup_load', by_name) and not all(q.get('value') == 0 for q in loads):
                error('startup_surge_ignores_load', '%s：%s 的算式没有用声明的启动期负载 %s' % (
                    where, p.get('name'), '、'.join(str(q.get('name')) for q in loads)))
    return {'declared': declared, 'startup_calculations': startup, 'hot_parts': sorted(hot)}


def audit_hidden_literals(calculations, error):
    """A number added inside a derived parameter's name or derivation, or a check's name, that no parameter declares."""
    for key, row in calculations.items():
        declared = set()
        for p in params_of(row):
            m = _UNIT.match(str(p.get('unit') or '').strip())
            if m and finite(p.get('value')):
                declared.add((m.group(2), round(abs(p['value']) * _SI[m.group(1)], 12)))
        places = [(p.get('name'), '参数名') for p in params_of(row) if p.get('basis') == 'derived']
        places += [(p.get('derivation'), '推导') for p in params_of(row) if p.get('basis') == 'derived']
        places += [(c.get('name'), '检查名') for c in checks_of(row)]
        for words, place in places:
            for m in _ADDED.finditer(str(words or '')):
                if bool(m.group(1)) != bool(m.group(3)) or _VALUE_BEFORE.search(str(words)[:m.start()].rstrip()):
                    continue
                number = round(float(m.group(4)) * _SI[m.group(5)], 12)
                if (m.group(6), number) not in declared:
                    error('hidden_literal_in_name', '%s：%s“%s”里的 %s%s %s%s 没有声明成参数；声明它并写来源' % (
                        key, place, words, m.group(2), m.group(4), m.group(5), m.group(6)))


# --- the review list: what the free-text inputs ask for and the record does not show ------------------------------------


def _has_role(row, role):
    return any(p.get('input_role') == role or _PARAM[role].search(str(p.get('name') or '')) for p in params_of(row))


def checklist(calculations, requirements, library, applicable, hot, startup):
    """Nothing here is an error. By calculation: the condition inputs the rules it cites list and it does not declare. By
    role: whether the requirements or any parameter give it at all. Plus declared-looking parameters ASG set itself."""
    rules = {r['id']: r for r in library['criteria']}
    calcs, weak = [], []
    for key, row in calculations.items():
        missing = {}
        for gid in row.get('guidelines') or []:
            for role in rule_roles(rules.get(gid) or {}):
                if not _has_role(row, role):
                    missing.setdefault(role, []).append(gid)
        if missing:
            calcs.append({'calculation': key, 'missing': {r: sorted(set(g)) for r, g in missing.items()}})
        for p in params_of(row):
            if p.get('input_role') is None and p.get('basis') in ('model', 'design_choice'):
                for role in ROLE_NAMES:
                    if _PARAM[role].search(str(p.get('name') or '')):
                        weak.append({'calculation': key, 'parameter': p.get('name'), 'role': role, 'basis': p.get('basis'),
                                     'value': p.get('value'), 'unit': p.get('unit')})
                        break
    req_text = {k: str(v.get('text') or '') for k, v in requirements.items()}
    roles = []
    for role in ROLE_NAMES:
        ids = sorted(g for g in applicable if rule_roles(rules.get(g) or {}).get(role))
        if not ids:
            continue
        reqs = sorted(k for k, words in req_text.items() if _REQUIREMENT[role].search(words))
        params = sorted({k for k, row in calculations.items() if _has_role(row, role)})
        roles.append({'role': role, 'title': ROLES[role][0], 'rules': len(ids), 'rule_ids': ids[:12],
                      'requirements': reqs[:8], 'calculations': params[:8], 'sourced': bool(reqs or params)})
    covered = {r for key in startup for r in calculations[key].get('refs') or []}
    return {'calculations': calcs, 'weak_sources': weak, 'roles': roles,
            'switch_parts_without_startup_calculation': sorted(hot - covered)}
