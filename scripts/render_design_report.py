#!/usr/bin/env python3
"""Write 设计报告.md for one delivery folder from its own records.

Every number and status comes from <delivery>/record/; the agent adds plain-language
text only through notes.json {summary, changes, items{work_id: text}, highlights[≤8]}.
Records that are missing or inconsistent are reported at the top instead of guessed.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_design_closure import calculation_basis, failing_checks, severity_of, vendor_items_of  # noqa: E402
from schematic_layout.citations import check as check_citation, check_source  # noqa: E402
from schematic_layout import lifecycle, part_classes  # noqa: E402
from schematic_layout.sexpr import all_nodes, first, parse  # noqa: E402
from schematic_layout.component_requirements import package_audit, DEFINITIONS, SELECTIONS  # noqa: E402

REPORT = '设计报告.md'
SEVERITIES = ('P0', 'P1', 'P2', 'P3')
SEVERITY_WORDS = {'P0': '可能损坏器件或危及安全', 'P1': '必需功能可能不达标',
                  'P2': '局部或次要问题', 'P3': '可选优化'}
SEVERITY_LEGEND = ('可能后果：P0 可能损坏器件或危及安全；P1 必需功能可能不达标；P2 局部或次要问题；P3 可选优化。'
                   '等级由后果类别和出现条件推出：安全 P0；器件损坏 P0（仅故障时 P1）；功能失效 P1（仅故障时 P2）；'
                   '性能余量 P2（仅故障时 P3）；优化 P3。')
CONSEQUENCE_WORDS = {'safety': '安全', 'damage': '器件损坏', 'function': '功能失效', 'margin': '性能余量', 'optimization': '优化'}
OCCURRENCE_WORDS = {'normal': '正常工作', 'condition': '特定工况', 'fault': '仅故障时'}
GATES = OrderedDict([
    ('erc', 'KiCad 电气规则检查（ERC）'),
    ('intent_netlist', '导出网表与设计网表逐脚对照'),
    ('hierarchy', '图纸层次与页数'),
    ('system_block', '系统框图（箭头标注、隔离边界、无悬空线）'),
    ('symbol_integrity', '符号引脚完整'),
    ('discrete_semantics', '分立器件符号与手册一致（TVS单/双向、MOS沟道、NPN/PNP）'),
    ('readability', '图面可读性'),
    ('geometry', '图面几何（重叠、穿线）'),
    ('external_supply', '外部供电声明'),
    ('reference_contract', '外围电路按手册核对'),
    ('design_change', '改动与预期一致'),
    ('component_requirements', '器件性能要求、选型状态及图面/BOM一致性'),
])
GATE_RESULTS = OrderedDict([('PASS', '通过（PASS）'), ('FAIL', '没通过（FAIL）'),
                            ('INSUFFICIENT', '资料不足（INSUFFICIENT）'), ('CONDITIONAL', '有条件通过')])
VISUAL = {'REVIEWED': '已完成', 'REVIEW_PENDING': '未完成', 'REWORK_REQUIRED': '发现需返工的问题'}
STAGES = {'requirement': '用户暂缓的需求', 'design': '设计未完成', 'external': '外部资料缺口', 'validation': '样机或试验验证', 'pcb': 'PCB 实现'}
REQUIREMENTS = OrderedDict([('design_supported', '有设计依据'), ('conditional', '有条件成立'), ('open', '还没有设计')])
# parameter_version 2: what a calculation rests on, derived from its inputs.
TIERS = OrderedDict([('supported', '设计成立'), ('estimate', '依赖工程估计'), ('vendor_data', '依赖厂家资料'),
                     ('user_deferred', '依赖暂缓的需求'), ('failed', '不满足')])
# Tiers shown only when a calculation falls in them.
OPTIONAL_TIERS = ('user_deferred',)
LEVEL_NAMES = {'I': 'I 级', 'II': 'II 级', 'III': 'III 级'}
DECISIONS = {'DECIDED': '用户给定', 'ADOPTED_PROPOSAL': '采纳建议', 'DEFERRED': '用户暂缓'}
RESPONSES = OrderedDict([
    ('REDESIGN', ('改图', 'changes')), ('CALC_DOC', ('补计算/补文档', 'changes')), ('DESIGN', ('补设计', 'work_items')),
    ('OBTAIN_DATA', ('补资料', 'work_items')), ('ASK_USER', ('请用户定需求', 'clarifications')),
    ('HANDOFF', ('技术转交', 'work_items')), ('DECLINE', ('不采纳', 'evidence')),
    ('DEFERRED', ('已暂缓', 'detail'))])
RESPONSE_STAGE = {'DESIGN': ('design',), 'OBTAIN_DATA': ('external',), 'HANDOFF': ('validation', 'pcb')}
REF_PATTERN = re.compile(r'(?<![A-Za-z0-9])[A-Z]{1,3}\d{1,4}(?![A-Za-z0-9])')
PAGE_PATTERN = re.compile(r'(?<![A-Za-z0-9])\d{2}_[A-Za-z][A-Za-z0-9_]*|System_block')
# Words that describe the review process, not a design basis.
REQUIRED = ('electrical-intent.json', 'design-closure.json', 'design-closure-audit.json',
            'summary.json', 'visual-review.json', 'page-plan.json', 'selection.json', 'lessons.json')
CAUSES = ('rule_missing', 'rule_not_enforced', 'knowledge_missing', 'knowledge_wrong', 'judgment')
# A comment left unfixed this version still says why the skill missed it (R6: nine deferrals marked none).
ATTRIBUTION_DEFERRED = re.compile(r'再归因|未归因|暂不归因|未做根因|没做根因|之后归因')
CAUSE_WORDS = {'rule_missing': '缺规则', 'rule_not_enforced': '规则没执行', 'knowledge_missing': '缺知识',
               'knowledge_wrong': '知识有错', 'judgment': '判断失误', 'none': '无需改'}
# Where a change for each cause class must land: rules become gates, knowledge goes to references or the library.
CAUSE_TARGETS = {'rule_missing': ('scripts/',), 'rule_not_enforced': ('scripts/',),
                 'knowledge_missing': ('references/', 'wiki/', 'raw/'), 'knowledge_wrong': ('references/', 'wiki/', 'raw/'),
                 'judgment': ('SKILL.md', 'references/')}
# A lesson's change made in the delivery folder is not a change to the skill (R8 wrote its new patterns there).
DELIVERY_PATH = re.compile(r'(?:^|[\s:：，,；;（(])(?:设计资料|record|原理图)/')
SOURCE_PATTERN = re.compile(r'^(review:[^/\s]+/\S+|datasheet:.+#p\d+|test:\S+|user:\d{4}-\d{2}-\d{2})$')
SELECTION_STATUS = ('selected', 'rejected', 'alternate')
OPS = ('<=', '>=', 'covers', 'equals', 'has')
# A rejection that is not a failed decisive condition must say what kind it is.
REJECT_KINDS = {'dependency': '依赖拿不到', 'data': '资料不足', 'availability': '可得性', 'cost': '成本',
                'preference': '都能用，按优先规则落选'}
CORE_REF = re.compile(r'^[UQT]\d')
OPTION_FIELDS = (('name', '方案名'), ('parts', '涉及型号'), ('cost', '代价'), ('pros', '优点'), ('cons', '缺点'))
# Words that carry an earlier version's review over instead of looking at this version's PDF.
CARRIED_OVER = ('沿用', '同上一版', '同上版', '与上一版相同', '上一版已审')
# KiCad stamps each PDF export with its time; the review binds to the drawing, so its hash leaves the dates out.
PDF_DATES = re.compile(rb'/(CreationDate|ModDate) \([^)]*\)')
TERMINOLOGY = Path(__file__).resolve().parent.parent / 'references' / 'terminology.md'
# A written total and what it is counted against (references/terminology.md).
COUNT_PATTERN = re.compile(r'(?:共|全部)\s*(\d+)\s*(项计算|件未关闭项|条需求|条审查意见|个器件|页)')
USER_SOURCE = re.compile(r'^user:\d{4}-\d{2}-\d{2}$')


def text(value):
    return isinstance(value, str) and bool(value.strip())


OPERATOR_SIGNS = {'<=': '≤', '<': '<', '>=': '≥', '>': '>', '==': '='}
SIDE_WORDS = {'no_false_trip': '不误动作', 'protection': '能保护'}


def english_sentence(value):
    """Prose written in English rather than Chinese. Part numbers, units and
    all-caps acronyms (PFC, OVP, NTC) are allowed inside Chinese text."""
    if not text(value):
        return False
    words = [w for w in re.findall(r'(?<![A-Za-z0-9])[A-Za-z]{3,}(?![A-Za-z0-9])', value) if not w.isupper()]
    cjk = len(re.findall(r'[\u4e00-\u9fff]', value))
    return len(words) >= 4 and cjk < 2 * len(words)


def prose(closure, notes, responses=None):
    """(where, text) for every piece of record and notes text the report shows to engineers."""
    found = []
    for c in closure.get('calculations') or []:
        if not isinstance(c, dict):
            continue
        for field, word in (('assumptions', '假设'), ('omitted_terms', '没算进去的项')):
            for i, v in enumerate(c.get(field) or []):
                found.append(('计算 %s %s %d' % (c.get('id'), word, i + 1), v.get('term') if isinstance(v, dict) else v))
        for i, chk in enumerate(c.get('checks') or []):
            if isinstance(chk, dict):
                found.append(('计算 %s 核对项 %d' % (c.get('id'), i + 1), chk.get('name')))
    for w in closure.get('work_items') or []:
        if isinstance(w, dict):
            for field in ('action', 'owner', 'fallback', 'assumption', 'progress'):
                found.append(('待办 %s %s' % (w.get('id'), field), w.get(field)))
    for r in closure.get('requirements') or []:
        if isinstance(r, dict):
            found.append(('需求 %s 实现说明' % r.get('id'), r.get('implementation')))
    for q in closure.get('clarifications') or []:
        if isinstance(q, dict):
            for field in ('question', 'requirement_text', 'proposed_requirement'):
                found.append(('需求澄清 %s %s' % (q.get('id'), field), q.get(field)))
            found.append(('需求澄清 %s 答复' % q.get('id'), (q.get('answer') or {}).get('text')))
    for i in (responses or {}).get('items') or []:
        if isinstance(i, dict):
            found.append(('审查意见 %s 处置说明' % i.get('id'), i.get('detail')))
    for field in ('summary', 'changes'):
        found.append(('notes %s' % field, notes.get(field)))
    for key, v in (notes.get('items') or {}).items():
        found.append(('notes 待办 %s' % key, v))
    for i, v in enumerate(notes.get('highlights') or []):
        found.append(('notes 关键依据 %d' % (i + 1), v))
    return [(where, v) for where, v in found if text(v)]


def quote(where, value):
    return '%s：“%s”' % (where, value.strip()[:40] + ('…' if len(value.strip()) > 40 else ''))


def check_language(texts):
    """Everything the report shows to engineers is written in Chinese."""
    found = [quote(where, v) for where, v in texts if english_sentence(v)]
    if not found:
        return []
    return ['下列给人看的文字是英文，要改成中文（器件型号、单位和缩写可以保留）：' + '；'.join(found[:6])
            + ('；等共 %d 处' % len(found) if len(found) > 6 else '')]


def banned_terms(path=TERMINOLOGY):
    """Words the terminology table says not to use: its first table's last column."""
    words = []
    table = path.read_text(encoding='utf-8').split('## 术语', 1)[-1].split('\n## ', 1)[0]
    for line in table.splitlines()[2:]:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) == 3:
            words += [w for w in re.split(r'[、,，]', cells[2]) if w.strip()]
    return words


def check_terms(texts):
    """Records and notes use the terms in references/terminology.md."""
    words = banned_terms()
    found = ['%s（%s）' % (quote(where, v), '、'.join(w for w in words if w in v))
             for where, v in texts if any(w in v for w in words)]
    if not found:
        return []
    return ['下列文字用了术语表不用的词，按 references/terminology.md 改：' + '；'.join(found[:6])
            + ('；等共 %d 处' % len(found) if len(found) > 6 else '')]


def check_counts(texts, actual):
    """A total written as 共/全部 N … matches the records; partial counts are not checked."""
    problems = []
    for where, v in texts:
        for m in COUNT_PATTERN.finditer(v):
            n, unit = int(m.group(1)), m.group(2)
            if actual.get(unit) is not None and n != actual[unit]:
                problems.append('%s 写“%s”，记录里是 %d' % (where, m.group(0), actual[unit]))
    return problems


def symbol_refs(sch_path):
    """Placed symbol uuid -> reference, from one native sheet."""
    refs = {}
    for sym in all_nodes(parse(sch_path.read_text(encoding='utf-8')), 'symbol'):
        uid = first(sym, 'uuid')
        ref = next((str(p[2]) for p in all_nodes(sym, 'property') if len(p) > 2 and p[1] == 'Reference'), None)
        if uid and len(uid) > 1 and ref:
            refs[str(uid[1])] = ref
    return refs


PATTERNS_DIR = Path(__file__).resolve().parent.parent / 'references' / 'circuit-patterns'


def pattern_approaches(patterns_dir=PATTERNS_DIR):
    out = {}
    for md in sorted(patterns_dir.glob('*.md')) if patterns_dir.is_dir() else []:
        out[md.stem] = {line[4:].strip() for line in md.read_text(encoding='utf-8').splitlines() if line.startswith('### ')}
    return out


def check_block_patterns(name, blocks, patterns, approaches, lessons):
    """Each functional block names an existing pattern approach, or lessons.json registers the gap."""
    errors = []
    registered = any(isinstance(e, dict) and e.get('cause') == 'knowledge_missing' and 'circuit-patterns' in str(e.get('change') or '')
                     for e in (lessons or {}).get('events') or [])
    patterns = patterns if isinstance(patterns, dict) else {}
    for block in blocks:
        ref = patterns.get(block)
        if not text(ref):
            if not registered:
                errors.append('%s：功能块“%s”没有标注电路模式（patterns），没有合适模式时在 lessons.json 登记 knowledge_missing 并补写 references/circuit-patterns/' % (name, block))
            continue
        pid, _, approach = ref.partition('#')
        if pid not in approaches:
            errors.append('%s：功能块“%s”标注的模式 %s 在 references/circuit-patterns/ 里不存在' % (name, block, pid))
        elif approach not in approaches[pid]:
            errors.append('%s：功能块“%s”标注的做法“%s”不在模式 %s 里（有：%s）' % (name, block, approach, pid, '、'.join(sorted(approaches[pid]))))
    return errors


def check_page_plan(plan, intent, visual, lessons=None, patterns_dir=PATTERNS_DIR):
    """Every drawn page has a plan (reader tasks, blocks of parts, the pattern of each block) and a review that traced each task."""
    if not isinstance(plan, dict) or plan.get('schema_version') != 1 or not isinstance(plan.get('pages'), list):
        return ['page-plan.json 必须是 schema_version 1、带 pages 列表的对象']
    errors = []
    approaches = pattern_approaches(patterns_dir)
    known = {c.get('ref') for c in intent.get('components') or [] if isinstance(c, dict)}
    on_page = {}
    for c in intent.get('components') or []:
        if isinstance(c, dict) and isinstance(c.get('fields'), dict) and text(c['fields'].get('Circuit')):
            on_page.setdefault(c['fields']['Circuit'], set()).add(c.get('ref'))
    reviewed = {p.get('file'): p for p in (visual.get('pages') or []) if isinstance(p, dict)}
    for index, page in enumerate(plan['pages']):
        name = page.get('file') if isinstance(page, dict) else None
        if not text(name):
            errors.append('page-plan.json 有一页没有 file')
            continue
        tasks = page.get('reader_tasks')
        blocks = page.get('blocks')
        if not isinstance(tasks, list) or not tasks or not all(text(t) for t in tasks):
            errors.append('%s：要写明读者任务（reader_tasks）' % name)
        if not isinstance(blocks, dict) or not blocks or not all(isinstance(v, list) and v for v in blocks.values()):
            errors.append('%s：要按功能块列出器件（blocks）' % name)
            continue
        placed = {}
        for block, refs in blocks.items():
            for ref in refs:
                if ref not in known:
                    errors.append('%s：功能块“%s”里的 %s 不在设计网表里' % (name, block, ref))
                elif ref in placed:
                    errors.append('%s：%s 同时在功能块“%s”和“%s”里' % (name, ref, placed[ref], block))
                placed[ref] = block
        cover = index == 0 and len(plan['pages']) > 1          # the first page is the System_block cover (SKILL.md task 3.3)
        if not cover and 'system_block' not in name.lower():
            errors += check_block_patterns(name, blocks, page.get('patterns'), approaches, lessons)
        missing = sorted(on_page.get(Path(name).stem, set()) - set(placed))
        if missing:
            errors.append('%s：这些器件不属于任何功能块：%s' % (name, '、'.join(missing[:6])))
        review = reviewed.get(name)
        if review is None:
            errors.append('%s：图面审阅没有这一页的记录' % name)
        elif isinstance(tasks, list) and len(review.get('paths') or []) < len(tasks):
            errors.append('%s：读者任务 %d 条，图面审阅只追了 %d 条路径' % (name, len(tasks), len(review.get('paths') or [])))
    return errors


def render_sha256(path):
    """SHA-256 of a KiCad PDF without its export time: two exports of the same sheets give the same value."""
    return hashlib.sha256(PDF_DATES.sub(b'', Path(path).read_bytes())).hexdigest()


def check_visual_items(root, visual, summary=None):
    """Every object handed to the render review is dispositioned from this version's PDF.

    Each item in summary.json geometry.render_review_items has a nonempty disposition on its page,
    the symbol it names is on that page, and no disposition carries over an earlier version's review.
    A finished review names the PDF it was made on (R6 redraw: an earlier PDF's review read as finished).
    """
    errors = []
    pdf = root / '原理图' / 'schematic.pdf'
    if visual.get('status') == 'REVIEWED' and pdf.is_file() and visual.get('pdf_sha256') != render_sha256(pdf):
        errors.append('visual-review.json 的 pdf_sha256 不是本版 原理图/schematic.pdf 的（render_design_report.py --pdf-sha256 '
                      '原理图/schematic.pdf 给出）：按本版 PDF 重新审阅，做完前 status 写 REVIEW_PENDING')
    if any(w in str(visual.get('method', '')) for w in CARRIED_OVER):
        errors.append('visual-review.json 的 method 写了沿用上一版：没改动的页面也要按本版 PDF 重新看')
    done = {}
    for page in visual.get('pages') or []:
        if not isinstance(page, dict):
            continue
        name = page.get('file')
        notes = [x for x in (page.get('paths') or []) + (page.get('problems') or []) if text(x)]
        items = [i for i in page.get('render_review_items') or [] if isinstance(i, dict)]
        carried = [x for x in notes + [str(i.get('disposition', '')) for i in items] if any(w in x for w in CARRIED_OVER)]
        if carried:
            errors.append('%s：处置“%s”沿用上一版：没改动的页面也要按本版 PDF 重新看' % (name, carried[0][:30]))
        if not items:
            continue
        sch = root / '原理图' / str(name)
        if not text(name) or not sch.is_file():
            errors.append('第 %s 页：有图面待审对象但找不到原理图/%s' % (page.get('page'), name))
            continue
        try:
            refs = symbol_refs(sch)
        except (OSError, ValueError) as error:
            errors.append('原理图/%s 读不出来：%s' % (name, error))
            continue
        for item in items:
            key = str(item.get('item', ''))
            parts = key.split(':')
            if len(parts) > 1 and parts[1] not in refs and parts[0] != 'hierarchical_label':
                errors.append('%s：条目“%s”的符号在图里找不到' % (name, key[:48]))
            elif text(item.get('disposition')):
                done.setdefault(name, set()).add(key)
    listed = ((summary or {}).get('gates') or {}).get('geometry', {}).get('render_review_items') or {}
    for name, keys in listed.items():
        left = [k for k in keys if k not in done.get(name, set())]
        if left:
            errors.append('%s：%d 个图面待审对象在 visual-review.json 里没有处置（如 %s）' % (name, len(left), left[0][:48]))
    return list(OrderedDict.fromkeys(errors))


def norm_mpn(value):
    return re.sub(r'[\s\-_/]+', '', value if text(value) else '').lower()


def judge(cond, entry):
    """(ok, shown) for one decisive condition against one candidate's recorded value; ok is None when unusable."""
    op, limit = cond.get('op'), cond.get('limit')
    if not isinstance(entry, dict) or 'value' not in entry or not (text(entry.get('page')) or isinstance(entry.get('page'), int)):
        return None, '没有值或页码'
    value = entry['value']
    unit = cond.get('unit') or ''
    try:
        if op in ('<=', '>='):
            ok = float(value) <= float(limit) if op == '<=' else float(value) >= float(limit)
            return ok, '%s %s %s %s' % (num(value), op, num(limit), unit)
        if op == 'covers':
            ok = float(value[0]) <= float(limit[0]) and float(value[1]) >= float(limit[1])
            return ok, '%s–%s 覆盖 %s–%s %s' % (num(value[0]), num(value[1]), num(limit[0]), num(limit[1]), unit)
        if op == 'equals':
            return norm_mpn(str(value)) == norm_mpn(str(limit)), '%s = %s' % (value, limit)
        if op == 'has':
            want = limit if isinstance(limit, bool) else True
            return bool(value) == want, '%s%s' % ('有' if value else '无', '' if want else '（要求无）')
    except (TypeError, ValueError, IndexError):
        pass
    return None, '值 %r 无法按 %s 判定' % (value, op)


def check_conditions(name, conds, cands):
    """Selected and alternate candidates satisfy every decisive condition; a rejected one fails at least one or says why."""
    problems, basis = [], []
    for c in cands:
        mpn = c.get('mpn') if text(c.get('mpn')) else '?'
        verdicts = [(d['param'], *judge(d, (c.get('values') or {}).get(d['param']))) for d in conds]
        failed = [(param, shown) for param, ok, shown in verdicts if ok is False]
        if c.get('status') in ('selected', 'alternate'):
            for param, ok, shown in verdicts:
                if ok is None:
                    problems.append('选型角色“%s”候选 %s 没有给出条件“%s”的值和页码（%s）' % (name, mpn, param, shown))
                elif not ok:
                    problems.append('选型角色“%s”候选 %s 不满足条件“%s”（%s）却被%s' % (name, mpn, param, shown, '选定' if c.get('status') == 'selected' else '列为备选'))
        else:
            kind = c.get('reject_kind')
            if failed:
                basis.append('%s：%s %s' % (mpn, failed[0][0], failed[0][1]))
            elif kind in REJECT_KINDS:
                basis.append('%s：%s' % (mpn, REJECT_KINDS[kind]))
            else:
                problems.append('选型角色“%s”淘汰候选 %s 没有一条决定性条件判定不满足，也没写 reject_kind（%s）'
                                % (name, mpn, '/'.join(REJECT_KINDS)))
    return problems, basis


def check_options(name, role, selected):
    """A selected part that rests on unpublished data comes with 2-3 options, a recommendation and the user's choice."""
    problems = []
    options = [o for o in role.get('options') or [] if isinstance(o, dict)]
    if not 2 <= len(options) <= 3 or len(options) != len(role.get('options') or []):
        return ['选型角色“%s”的选定候选依赖未公开资料，要列 2–3 个选型方案（options），现在 %d 个' % (name, len(options))]
    for o in options:
        label = o.get('name') if text(o.get('name')) else '?'
        missing = [w for k, w in OPTION_FIELDS if not (text(o.get(k)) or (k == 'parts' and o.get(k)))]
        if missing or not isinstance(o.get('external_dependencies'), list):
            problems.append('选型角色“%s”的方案“%s”没有写%s' % (name, label, '、'.join(missing + (
                [] if isinstance(o.get('external_dependencies'), list) else ['外部依赖']))))
    if sum(1 for o in options if o.get('recommended') is True) != 1 or not text(role.get('recommendation')):
        problems.append('选型角色“%s”要恰好一个推荐方案（recommended），并在 recommendation 写明理由' % name)
    cons = [' '.join(o['cons'].split()) for o in options if text(o.get('cons'))]
    if len(cons) != len(set(cons)):
        problems.append('选型角色“%s”有方案的缺点写得一字不差，每个方案要写自己的缺点' % name)
    decision = role.get('decision') if isinstance(role.get('decision'), dict) else {}
    chosen = next((o for o in options if o.get('name') == decision.get('option')), None)
    if not chosen or not (isinstance(decision.get('source'), str) and USER_SOURCE.match(decision['source'])):
        problems.append('选型角色“%s”还没有你的决定：decision 要写 {option: 方案名, source: user:<日期>}，'
                        '定下来之前不进入设计网表' % name)
    elif norm_mpn(selected.get('mpn', '')) not in {norm_mpn(p) for p in chosen.get('parts') or [] if text(p)}:
        problems.append('选型角色“%s”选定的 %s 不在你选的方案“%s”里' % (name, selected.get('mpn'), chosen['name']))
    return problems


def check_selection(data, intent, root):
    """Every core part was chosen from compared candidates whose datasheets are in the library."""
    roles = data.get('roles') if isinstance(data, dict) else None
    if not isinstance(roles, list) or not roles:
        return ['selection.json 没有 roles：每个核心器件角色都要有候选比较（见 core-part-selection.md）']
    problems = []
    comps = {c.get('ref'): c for c in intent.get('components') or [] if isinstance(c, dict)}
    library = Path(os.path.expanduser(data.get('library_root') if text(data.get('library_root')) else ''))
    covered, undeclared = set(), []
    for i, role in enumerate(roles, 1):
        if not isinstance(role, dict):
            problems.append('selection.json 第 %d 个角色不是对象' % i)
            continue
        name = role.get('role') if text(role.get('role')) else '第 %d 个角色' % i
        refs = [r for r in role.get('refs') or [] if text(r)]
        cands = [c for c in role.get('candidates') or [] if isinstance(c, dict)]
        for key, label in (('refs', '位号'), ('decisive', '决定性条件')):
            if not role.get(key):
                problems.append('选型角色“%s”没有写%s' % (name, label))
        conds = [d for d in role.get('decisive') or [] if isinstance(d, dict)]
        if role.get('decisive') and (len(conds) != len(role['decisive']) or not all(
                text(d.get('param')) and d.get('op') in OPS and 'limit' in d for d in conds)):
            problems.append('选型角色“%s”的决定性条件要写成 {param, op, limit[, unit, requirement]}，op 取 %s' % (name, '/'.join(OPS)))
            conds = []
        if conds:
            cond_problems, basis = check_conditions(name, conds, cands)
            problems += cond_problems
            role['_basis'] = basis
        if len(cands) < 2 and not text(role.get('single_candidate_reason')):
            problems.append('选型角色“%s”只有 %d 个候选又没写 single_candidate_reason' % (name, len(cands)))
        selected = [c for c in cands if c.get('status') == 'selected']
        if len(selected) != 1:
            problems.append('选型角色“%s”要恰好一个 selected 候选，现在 %d 个' % (name, len(selected)))
        else:
            deps = selected[0].get('external_dependencies')
            if not isinstance(deps, list) or not all(text(x) for x in deps):
                undeclared.append(name)
            elif deps:
                problems += check_options(name, role, selected[0])
        for c in cands:
            mpn = c.get('mpn') if text(c.get('mpn')) else '?'
            if c.get('status') not in SELECTION_STATUS:
                problems.append('候选 %s 的 status 必须是 %s 之一' % (mpn, '/'.join(SELECTION_STATUS)))
            if not text(c.get('reason')):
                problems.append('候选 %s 没有写选中或淘汰的理由' % mpn)
            sheet = c.get('datasheet') if text(c.get('datasheet')) else ''
            if not sheet or not ((library / sheet).is_file() or (root / sheet).is_file()):
                problems.append('候选 %s 的资料 %s 不在知识库 %s 或交付目录内' % (mpn, sheet or '（没写）', library))
        for ref in refs:
            covered.add(ref)
            if ref not in comps:
                problems.append('选型角色“%s”的位号 %s 不在设计网表里' % (name, ref))
            elif len(selected) == 1:
                mpn = selected[0].get('mpn') if text(selected[0].get('mpn')) else ''
                fields = [str(comps[ref][k]) for k in ('value', 'mpn') if text(comps[ref].get(k))]
                if not mpn:
                    problems.append('选型角色“%s”的选定候选没有写 mpn' % name)
                elif not any(norm_mpn(mpn) in norm_mpn(f) for f in fields):
                    problems.append('位号 %s 的 value/mpn “%s” 都不含选定型号 %s' % (ref, '、'.join(fields), mpn))
    if undeclared:
        problems.append('选型角色 %s 的选定候选没有写 external_dependencies（依赖的未公开资料，没有写空列表）'
                        % '、'.join('“%s”' % n for n in undeclared))
    missing = sorted(r for r in comps if CORE_REF.match(r if text(r) else '') and r not in covered)
    if missing:
        problems.append('核心器件没有选型记录：%s' % '、'.join(missing))
    return problems


def check_lessons(data):
    """What this version taught the skill: each event has a source, a cause class and a concrete change."""
    events = data.get('events') if isinstance(data, dict) else None
    if not isinstance(events, list) or not events:
        return ['lessons.json 没有 events：每次设计至少登记一条学到的东西，没有就登记 cause=none 并写明核对了什么'], {}
    problems, by_source = [], {}
    for i, e in enumerate(events, 1):
        if not isinstance(e, dict):
            problems.append('lessons.json 第 %d 条不是对象' % i)
            continue
        source = e.get('source') if text(e.get('source')) else ''
        if not SOURCE_PATTERN.match(source):
            problems.append('lessons.json 第 %d 条的 source 要写成 review:<审查目录>/<待办编号>、datasheet:<库内路径>#p<页>、test:<记录> 或 user:<日期>' % i)
        else:
            by_source[source] = e
        cause = e.get('cause')
        if cause not in CAUSES and cause != 'none':
            problems.append('lessons.json 第 %d 条的 cause 必须是 %s 或 none' % (i, '/'.join(CAUSES)))
            continue
        if cause == 'none':
            if not text(e.get('why_none')):
                problems.append('lessons.json 第 %d 条 cause=none 要在 why_none 里写明核对了什么' % i)
            elif ATTRIBUTION_DEFERRED.search(e['why_none']):
                problems.append('lessons.json 第 %d 条 cause=none 只用于不反映技能缺口的意见；'
                                '本版暂缓修改的意见也要按“技能为什么没拦住”归因，不留到下一轮' % i)
            continue
        change = e.get('change') if text(e.get('change')) else ''
        if not any(t in change for t in CAUSE_TARGETS[cause]):
            problems.append('lessons.json 第 %d 条归因 %s，change 要指向 %s 下的具体文件' % (i, cause, '/'.join(CAUSE_TARGETS[cause])))
        elif DELIVERY_PATH.search(change):
            problems.append('lessons.json 第 %d 条的 change 写在交付目录里：学到的东西要改技能的 references/、scripts/ 或知识库，'
                            '交付目录里的文件不算技能改动' % i)
        if cause == 'judgment' and not text(e.get('why_not_rule')):
            problems.append('lessons.json 第 %d 条归因 judgment 要写 why_not_rule：为什么规则和知识都拦不住' % i)
    return problems, by_source


def check_citations(selection, lessons, root):
    """Selection values are on the datasheet pages they cite; lesson sources name a real file and page.

    Returns (problems, review, not_checked): a wrong file or page is a problem, a value the page
    text does not show is listed for a person to check.
    """
    problems, review, unchecked = [], [], []
    def note(result, where, source):
        if result['status'] == 'FAIL':
            problems.append('%s：手册引用不对，%s' % (where, result['reason']))
        elif result['reason'] and result['reason'] not in unchecked:
            unchecked.append(result['reason'])
        if result['unshown']:
            review.append({'item': where, 'source': source, 'values': result['unshown']})
    library = Path(os.path.expanduser(selection.get('library_root') if text(selection.get('library_root')) else ''))
    for role in selection.get('roles') or []:
        for c in (role.get('candidates') or []) if isinstance(role, dict) else []:
            sheet = c.get('datasheet') if isinstance(c, dict) and text(c.get('datasheet')) else ''
            for param, entry in ((c.get('values') or {}) if sheet else {}).items():
                page = re.match(r'\d+', str(entry.get('page'))) if isinstance(entry, dict) else None
                if page:
                    page = int(page.group())
                    note(check_citation(sheet, page, [entry.get('value')], [library, root]),
                         '候选 %s 的“%s”' % (c.get('mpn', '?'), param), '%s#p%d' % (sheet, page))
    for i, e in enumerate((lessons or {}).get('events') or [], 1):
        result = check_source(e.get('source'), (), [root]) if isinstance(e, dict) else None
        if result:
            note(result, 'lessons.json 第 %d 条' % i, e['source'])
    return problems, review, unchecked


def num(value):
    """A number with three significant digits; integers and non-numbers unchanged."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, int) or value == 0 or value != value:
        return str(value)
    if abs(value) < 1e-3:
        return '%.3g' % value          # 3.79e-07, not 0 (R8 showed 379 ns > 343 ns as "0 > 0 s")
    rounded = float('%.3g' % value)
    return str(int(rounded)) if rounded == int(rounded) and abs(rounded) >= 1 else ('%f' % rounded).rstrip('0').rstrip('.')


def check_text(chk):
    if not isinstance(chk, dict):
        return ''
    side = SIDE_WORDS.get(chk.get('side'))
    return '%s%s：%s %s %s %s' % ('[%s] ' % side if side else '', chk.get('name'), num(chk.get('value')),
                                 OPERATOR_SIGNS.get(chk.get('operator'), chk.get('operator')),
                                 num(chk.get('limit')), chk.get('unit') or '')


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ').strip()


def load(path):
    try:
        return json.loads(path.read_text(encoding='utf-8')), None
    except FileNotFoundError:
        return None, '缺少 record/%s' % path.name
    except (OSError, ValueError) as error:
        return None, 'record/%s 读不出来：%s' % (path.name, error)


def review_sources(data, root=None):
    """Registered review sources whose file no longer matches its sha256, and those that could not be read."""
    changed, unread = [], []
    for s in (data or {}).get('sources') or []:
        if not (isinstance(s, dict) and text(s.get('id')) and text(s.get('path'))):
            continue
        path = Path(os.path.expanduser(s['path']))
        if not path.is_absolute() and root is not None:
            path = Path(root) / path
        if not path.is_file():
            unread.append(s['id'])
        elif hashlib.sha256(path.read_bytes()).hexdigest() != s.get('sha256'):
            changed.append(s['id'])
    return changed, unread


def check_responses(data, work, intent=None, closure=None, root=None, lessons=None):
    """Each review comment has one allowed response and what that response requires.

    A response is work done this version, not a transcription of the comment:
    the same explanation may not serve several comments, 补设计 points at a
    work item that records this version's progress, 改图 names the parts it
    changed, and 补计算/补文档 names the calculation or design document.
    """
    errors = []
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        return ['review-responses.json 必须是 schema_version 1 的对象']
    known_refs = {c.get('ref') for c in (intent or {}).get('components') or [] if isinstance(c, dict)}
    calc_ids = {c.get('id') for c in (closure or {}).get('calculations') or [] if isinstance(c, dict)}
    asked = {q.get('id') for q in (closure or {}).get('clarifications') or [] if isinstance(q, dict)}
    details = Counter(i.get('detail') for i in data.get('items') or [] if isinstance(i, dict) and text(i.get('detail')))
    for detail, n in details.items():
        if n > 1:
            errors.append('处理说明“%s”在 %d 条意见里重复：每条意见要写它自己怎么处理' % (detail[:30] + ('…' if len(detail) > 30 else ''), n))
    sources = {s.get('id') for s in data.get('sources') or [] if isinstance(s, dict)
               and text(s.get('id')) and text(s.get('path')) and text(s.get('sha256'))}
    if not sources:
        errors.append('review-responses.json 没有登记意见来源（id、path、sha256）')
    changed, _ = review_sources(data, root)
    for sid in changed:
        errors.append('审查意见来源 %s 的文件与登记的 sha256 不一致：意见原文改过，要按现在的原文重新登记' % sid)
    seen = set()
    for item in data.get('items') or []:
        key = item.get('id') if isinstance(item, dict) else None
        if not text(key) or key in seen:
            errors.append('审查意见编号缺失或重复：%s' % key)
            continue
        seen.add(key)
        response = item.get('response')
        if response not in RESPONSES:
            errors.append('%s：处理方式必须是 %s 之一' % (key, '/'.join(RESPONSES)))
            continue
        if item.get('source') not in sources or not text(item.get('locator')) or not text(item.get('comment')):
            errors.append('%s：要写明来源、在原文中的位置和意见内容' % key)
        if not text(item.get('detail')):
            errors.append('%s：要说明怎么处理、为什么' % key)
        # A comment raised again was not stopped by a rule or by knowledge the first time: not a judgment slip.
        if 'recurs_from' in item:
            if not (text(item['recurs_from']) and SOURCE_PATTERN.match(item['recurs_from']) and item['recurs_from'].startswith('review:')):
                errors.append('%s：recurs_from 要写成 review:<上一轮审查目录>/<意见编号>' % key)
            elif item.get('cause') == 'judgment':
                errors.append('%s：意见复发自 %s，不能归因为判断失误（judgment）：复发说明规则或知识没有拦住' % (key, item['recurs_from']))
        if lessons is not None:
            cause = item.get('cause')
            if cause not in CAUSES and cause != 'none':
                errors.append('%s：要归因（cause）：%s 或 none' % (key, '/'.join(CAUSES)))
            elif cause != 'none':
                event = next((e for src, e in lessons.items() if src.startswith('review:') and src.endswith('/' + key)), None)
                if event is None:
                    errors.append('%s：归因 %s，lessons.json 里要有 source 以 /%s 结尾的事件写明改了什么' % (key, cause, key))
                elif event.get('cause') != cause:
                    errors.append('%s：review-responses 归因 %s，lessons.json 同一事件归因 %s，要一致' % (key, cause, event.get('cause')))
        field = RESPONSES[response][1]
        if field != 'detail' and not (isinstance(item.get(field), list) and item[field]):
            errors.append('%s：处理方式为“%s”时必须填 %s' % (key, RESPONSES[response][0], field))
        changes = [c for c in item.get('changes') or [] if text(c)]
        if response == 'REDESIGN' and changes and not any(
                (known_refs & set(REF_PATTERN.findall(c))) or PAGE_PATTERN.search(c) for c in changes):
            errors.append('%s：“改图”的 changes 没有点名改了哪个位号或哪一页' % key)
        if response == 'CALC_DOC':
            for c in changes:
                if c not in calc_ids and not (root is not None and (Path(root) / '设计资料' / c).is_file()):
                    errors.append('%s：“补计算/补文档”的 changes 项“%s”既不是计算编号也不是设计资料文件' % (key, c[:30]))
        for cid in item.get('clarifications') or [] if response == 'ASK_USER' else ():
            if cid not in asked:
                errors.append('%s：引用的需求澄清 %s 不在 design-closure.json 里' % (key, cid))
        for wid in item.get('work_items') or []:
            row = work.get(wid)
            if row is None:
                errors.append('%s：引用的待办 %s 不在 design-closure.json 里' % (key, wid))
            elif response in RESPONSE_STAGE and row.get('stage') not in RESPONSE_STAGE[response]:
                errors.append('%s：待办 %s 的阶段与处理方式“%s”不符' % (key, wid, RESPONSES[response][0]))
            elif response == 'DESIGN' and row.get('status') != 'closed' and not text(row.get('progress')):
                errors.append('%s：“补设计”引用的待办 %s 没有写本版进展（progress）' % (key, wid))
    if not seen:
        errors.append('review-responses.json 没有登记任何意见')
    return errors


def worst(levels):
    found = [s for s in SEVERITIES if s in levels]
    return found[0] if found else None


def render(root, notes=None, title=None):
    root = Path(root)
    record = root / 'record'
    notes = notes or {}
    problems = []
    data = {}
    for name in REQUIRED:
        data[name], problem = load(record / name)
        if problem:
            problems.append(problem)
    intent = data['electrical-intent.json'] or {}
    # Recompute against the current package, never trust a previously saved PASS.
    performance = package_audit(root, intent)
    if performance['status'] == 'FAIL':
        problems += ['器件性能要求：' + e for e in performance['errors']]
    closure = data['design-closure.json'] or {}
    audit = data['design-closure-audit.json'] or {}
    summary = data['summary.json'] or {}
    visual = data['visual-review.json'] or {}
    responses, change = None, None
    if (record / 'review-responses.json').exists():
        responses, problem = load(record / 'review-responses.json')
        if problem:
            problems.append(problem)
    if (record / 'design-change.json').exists():
        change, problem = load(record / 'design-change.json')
        if problem:
            problems.append(problem)

    work = {w['id']: w for w in closure.get('work_items') or [] if isinstance(w, dict) and text(w.get('id'))}
    requirements = [r for r in closure.get('requirements') or [] if isinstance(r, dict)]
    calculations = [c for c in closure.get('calculations') or [] if isinstance(c, dict)]
    if closure and closure.get('parameter_version') not in (1, 2, 3):
        problems.append('计算没有逐项登记参数来源：design-closure.json 要写 parameter_version 3，'
                        '每条计算的 parameters 写明每个器件参数的值、依据和手册页码，每条检查写明门槛的依据和出处（见 design-closure.md）')
    layered = closure.get('parameter_version') in (2, 3)
    if closure.get('parameter_version') == 3:
        reasons = Counter(' '.join(p['reason'].split()) for c in calculations for p in c.get('parameters') or []
                          if isinstance(p, dict) and p.get('basis') == 'model' and text(p.get('reason')))
        for reason, n in reasons.items():
            if n > 3:
                problems.append('%d 个工程估计参数共用同一句理由“%s”：每个估计写它自己的依据（见 design-closure.md）' % (n, reason[:40]))
    vendor_items, deferred_items = vendor_items_of(work), vendor_items_of(work, 'requirement')
    basis = {c.get('id'): calculation_basis(c, vendor_items.get(c.get('id'), []), deferred_items.get(c.get('id'), []))
             for c in calculations} if layered else {}
    clarifications = [q for q in closure.get('clarifications') or [] if isinstance(q, dict)]
    unanswered = [q.get('id') for q in clarifications if not q.get('answer')]
    if unanswered:
        problems.append('需求澄清 %s 还没有答复：要当场问用户，答复写回需求清单后再往下设计（见 requirement-clarifications.md）'
                        % '、'.join(map(str, unanswered)))
    tier = {cid: rests or conclusion for cid, (conclusion, rests, _) in basis.items()}
    open_external = any(isinstance(w, dict) and w.get('stage') == 'external' and w.get('status') != 'closed'
                        for w in closure.get('work_items') or [])
    if closure.get('gap_version') not in (1, 2) and open_external:
        problems.append('缺外部资料的待办没有写清缺口：design-closure.json 要写 gap_version 2，每件写明手册给了什么、'
                        '还缺什么、缺的是哪一类、影响哪些计算、要问的问题和本项的替代做法（见 design-closure.md）')
    if visual and visual.get('status') not in VISUAL:
        problems.append('visual-review.json 的 status 必须是 %s 之一' % '/'.join(VISUAL))
    lessons, events = {}, None
    if data['lessons.json'] is not None:
        lesson_problems, events = check_lessons(data['lessons.json'])
        problems += lesson_problems
        lessons = data['lessons.json']
    if data['page-plan.json'] is not None:
        problems += check_page_plan(data['page-plan.json'], intent, visual, lessons)
    problems += check_visual_items(root, visual, summary)
    selection = data['selection.json'] or {}
    if data['selection.json'] is not None:
        problems += check_selection(selection, intent, root)
    ordering = lifecycle.audit(intent, [root, root / 'record'])
    for f in ordering['flagged']:
        if not text(f['reason']):
            problems.append('位号 %s 的料号 %s 在手册 %s 里列在“%s”下（停产或不推荐新设计）：换在售料号，'
                            '或在设计网表该器件写 lifecycle_reason 说明为什么保留' % (f['ref'], f['mpn'], f['datasheet'], f['marker']))
    # Parts whose parameters only a datasheet guarantees are named exactly (part-roles.md section 1).
    contract = None
    if (record / 'change-contract.json').exists():
        contract, problem = load(record / 'change-contract.json')
        if problem:
            problems.append(problem)
    bases = [root, record]
    touched = part_classes.touched_refs(contract)
    identity, inherited, kinds_unchecked = part_classes.audit_identity(intent, bases, touched)
    safety, safety_inherited = part_classes.audit_safety(intent, closure, touched)
    if identity:
        problems.append('关键器件和特殊器件要写确切料号、数据手册和类型声明，常规件要写规格（见 part-roles.md 第 1 节）：' + '；'.join(identity[:6])
                        + ('；等共 %d 个' % len(identity) if len(identity) > 6 else ''))
    if safety:
        problems.append('保护器件与安全防护位置（见 part-roles.md 第 1 节）：' + '；'.join(safety[:6])
                        + ('；等共 %d 项' % len(safety) if len(safety) > 6 else ''))
    problems += part_classes.audit_citations(intent, closure, bases)
    cite_problems, cite_review, cite_unchecked = check_citations(selection, data['lessons.json'], root)
    problems += cite_problems
    cite_review = list((audit.get('citations') or {}).get('review') or []) + cite_review
    cite_unchecked = list((audit.get('citations') or {}).get('not_checked') or []) + cite_unchecked
    if responses is not None:
        problems += check_responses(responses, work, intent, closure, root, events)
    texts = prose(closure, notes, responses)
    problems += check_language(texts) + check_terms(texts)
    problems += check_counts(texts, {
        '项计算': len(calculations), '件未关闭项': sum(1 for w in work.values() if w.get('status') == 'open'),
        '条需求': len(requirements), '条审查意见': len((responses or {}).get('items') or []) if responses else None,
        '个器件': len(intent.get('components') or []), '页': len(summary.get('sheets') or []) if summary else None})

    gates = summary.get('gates') or {}
    shown = [(key, label, (gates.get(key) or {}).get('status')) for key, label in GATES.items() if key in gates]
    gate_counts = Counter(status for _, _, status in shown)
    # Drawing gates are ASG's own work: a failed one is redrawn, never delivered.
    # Listing it as a problem also makes pack_design.py refuse the delivery.
    for key, label, status in shown:
        if key in ('readability', 'geometry') and status == 'FAIL':
            problems.append('“%s”没通过：这是画图问题，改图到 PASS 再重新验证后才能交付' % label)
    open_work = [w for w in work.values() if w.get('status') == 'open']
    handoffs = [w for w in work.values() if w.get('status') == 'handoff']
    req_counts = Counter(r.get('status') for r in requirements)
    items = (responses or {}).get('items') or []
    reply_counts = Counter(i.get('response') for i in items if isinstance(i, dict))

    out = ['# %s' % (title or '原理图设计报告'), '']
    if problems:
        out += ['> **设计记录本身有问题，下面的结论不可靠。** 先改正记录再重新生成报告：' +
                '；'.join(cell(p) for p in problems[:6]), '']
    out += ['## 结论', '']
    parts = len(intent.get('components') or [])
    sheets = len(summary.get('sheets') or [])
    out.append('- **规模**：器件 %d 个，图纸 %d 页。' % (parts, sheets))
    out.append('- **图纸自动检查**：共 %d 项。%s。' % (len(shown), '，'.join(
        '%s %d 项' % (label, gate_counts.get(key, 0)) for key, label in GATE_RESULTS.items()
        if key != 'CONDITIONAL' or gate_counts.get(key))))
    out.append('- **图面审阅**：%s。' % VISUAL.get(visual.get('status'), '没有记录'))
    if performance['status'] == 'NOT_CHECKED':
        out.append('- **器件性能流程**：旧记录未检查（NOT_CHECKED）。')
    else:
        define_counts = Counter(performance.get('definition', {}).values())
        select_counts = Counter(performance.get('selection', {}).values())
        out.append('- **器件性能流程**：%s；%s；%s。' % (
            {'PASS': '通过', 'FAIL': '不通过', 'INCOMPLETE': '未完成'}.get(performance['status'], performance['status']),
            '、'.join('%s %d 项' % (DEFINITIONS[k], n) for k, n in define_counts.items()) or '无专项性能项',
            '、'.join('%s %d 项' % (SELECTIONS[k], n) for k, n in select_counts.items()) or '无专项选型项'))
        out.extend('- **性能未关闭项**：%s。' % cell(p) for p in performance['pending'])
        out.extend('- **样件验收（外部，不挡交付，未定型）**：%s。' % cell(p) for p in performance.get('acceptance') or [])
        if performance.get('procurement'):
            out.append('- **按 BOM 规格转交采购（外部，不挡交付）**：%d 颗，采购按 BOM 的 RequirementSpec 找料并核对保证值。'
                       % len(performance['procurement']))
        out.extend('- **性能要求提示**：%s。' % cell(h) for h in performance.get('hints') or [])
    out.append('- **需求**：共 %d 条。%s。' % (len(requirements), '，'.join(
        '%s %d 条' % (label, req_counts.get(key, 0)) for key, label in REQUIREMENTS.items())))
    if layered:
        tier_counts = Counter(tier.values())
        out.append('- **计算**：共 %d 项。%s。' % (len(calculations), '，'.join(
            '%s %d 项' % (label, tier_counts.get(key, 0)) for key, label in TIERS.items()
            if key not in OPTIONAL_TIERS or tier_counts.get(key))))
        # A conditional requirement rests on the vendor when any of its calculations or dependencies does.
        rests = Counter()
        for r in requirements:
            if r.get('status') != 'conditional':
                continue
            tiers = {tier.get(c.get('id')) for c in calculations if r.get('id') in (c.get('requirements') or [])}
            if 'vendor_data' in tiers or any(work.get(d, {}).get('stage') == 'external' and work[d].get('status') == 'open'
                                             for d in r.get('depends_on') or []):
                rests['vendor_data'] += 1
            elif 'user_deferred' in tiers or any(work.get(d, {}).get('stage') == 'requirement' and work[d].get('status') == 'open'
                                                 for d in r.get('depends_on') or []):
                rests['user_deferred'] += 1
            elif 'estimate' in tiers:
                rests['estimate'] += 1
        if rests:
            out[-2] = out[-2][:-1] + '（有条件成立的需求中%s）。' % '、'.join(
                '%s %d 条' % (TIERS[k], rests[k]) for k in ('vendor_data', 'user_deferred', 'estimate') if rests.get(k))
    else:
        out.append('- **计算**：共 %d 项，记录是 parameter_version 1，结论没有按依据分层。' % len(calculations))
    old = (['parameter_version 2（检查门槛的出处、每条需求有没有检查没核对）'] if closure.get('parameter_version') == 2 else []) + \
          (['gap_version 1（外部资料缺口没有分类）'] if closure.get('gap_version') == 1 and open_external else []) + \
          (['没有 derating_version（器件应力没有按降额等级核对）'] if closure and layered and 'derating_version' not in closure else []) + \
          (['没有 uncertainty_version（工程估计的余量没有对不确定度核对）'] if closure and layered and 'uncertainty_version' not in closure else [])
    if old:
        out.append('- **记录版本**：%s。新设计按 parameter_version 3、gap_version 2、derating_version 1、uncertainty_version 1 写。'
                   % '；'.join(old))
    derating = audit.get('derating') if isinstance(audit.get('derating'), dict) else None
    if derating:
        risks, hints = derating.get('stress_risks') or [], derating.get('hints') or []
        out.append('- **降额等级**：%s（%s，见 stress-spec.md）。%s%s' % (
            LEVEL_NAMES.get(derating.get('level'), '未定'), derating.get('source') or '没有写来源',
            '合格但有风险（应力）%d 处，见“应力风险”。' % len(risks) if risks else '写出的应力都在降额值以内。',
            '另有 %d 处应力比较没点名降额规则（提示）。' % len(hints) if hints else ''))
    margins = audit.get('estimate_margins') if isinstance(audit.get('estimate_margins'), list) else []
    if margins:
        out.append('- **估计余量**：%d 处检查的余量小于所依赖工程估计的不确定度，合格但有风险，见“余量不足以覆盖估计误差”。' % len(margins))
    if clarifications:
        asked = Counter((q.get('answer') or {}).get('decision') for q in clarifications)
        out.append('- **需求澄清**：问过用户 %d 个问题。%s。' % (len(clarifications), '，'.join(
            '%s %d 个' % (label, asked[key]) for key, label in list(DECISIONS.items()) + [(None, '还没有答复')] if asked.get(key))))
    if items:
        out.append('- **收到的审查意见**：%d 条。%s。' % (len(items), '，'.join(
            '%s %d 条' % (label, reply_counts[key]) for key, (label, _) in RESPONSES.items() if reply_counts.get(key))))
    missing = []
    if performance['status'] not in ('PASS', 'NOT_CHECKED'):
        missing.append('器件性能定义、选型或原生图面核对尚未完成：%s' % performance['status'])
    failed = [label for _, label, status in shown if status == 'FAIL']
    short = [label for _, label, status in shown if status not in ('PASS', 'FAIL', 'CONDITIONAL')]
    if failed:
        missing.append('%d 项图纸自动检查没通过：%s' % (len(failed), '、'.join(failed)))
    if short:
        missing.append('%d 项图纸自动检查资料不足或未执行：%s' % (len(short), '、'.join(short)))
    # Task 2.1 checks every core part's peripherals against its datasheet; not doing it leaves the design unfinished.
    reference_skipped = summary.get('reference_contract') == 'NOT_CHECKED'
    if reference_skipped:
        missing.append('外围电路按手册核对：未执行')
    if visual.get('status') != 'REVIEWED':
        missing.append('图面审阅%s' % VISUAL.get(visual.get('status'), '没有记录'))
    if inherited:
        missing.append('%d 个沿用基线的器件缺确切料号、数据手册、类型声明或规格：%s' % (len(inherited), '、'.join(
            line.split('（')[0].split(' ')[-1] for line in inherited)))
    if safety_inherited:
        missing.append('沿用基线的保护器件与安全防护位置有 %d 项未补：%s' % (len(safety_inherited), '；'.join(safety_inherited[:6])))
    by_stage = Counter(w.get('stage') for w in open_work)
    if open_work:
        missing.append('%d 件未关闭项（%s）' % (len(open_work), '，'.join(
            '%s %d 件' % (STAGES[s], by_stage[s]) for s in STAGES if by_stage.get(s))))
    if problems:
        missing.append('设计记录有问题，见开头')
    if missing:
        out.append('- **设计完成状态**：未完成。未完成项：')
        out += ['  %d. %s；' % (i, m) for i, m in enumerate(missing, 1)]
        out[-1] = out[-1][:-1] + '。'
    else:
        out.append('- **设计完成状态**：已完成。自动检查、图面审阅和设计待办都已处理完。')
    asks = [w for w in open_work if w.get('stage') == 'requirement']
    if asks:
        out.append('- **用户暂缓的需求**：%d 件（%s）。本版按建议条文设计，定下来后可能要改图，列在“未关闭项”最前面。'
                   % (len(asks), '、'.join(w['id'] for w in asks)))
    external = [w for w in open_work if w.get('stage') == 'external']
    if external:
        owners = Counter(w.get('owner') or '未指定' for w in external)
        linked = {c for w in external for c in w.get('calculations') or [] if isinstance(c, str)}
        out.append('- **外部资料缺口**：%d 件（%s）%s。待确认问题汇总在“外部资料需求”一节。' % (
            len(external), '；'.join('%s %d 件' % kv for kv in owners.most_common()),
            '，影响有条件成立的计算 %d 项' % len(linked) if linked else ''))
    optioned = [r for r in selection.get('roles') or [] if isinstance(r, dict) and r.get('options')]
    if optioned:
        out.append('- **外部条件不确定的选型**：%d 个角色（%s），方案与 ASG 的建议见“外部条件不确定的选型”一节。' % (
            len(optioned), '、'.join('%s→%s' % (r.get('role', ''), (r.get('decision') or {}).get('option') or '未决定')
                                    for r in optioned)))
    if open_work:
        out.append('- **未关闭项**：共 %d 件，%s按后果等级从重到轻列在“未关闭项”一节。'
                   % (len(open_work), '用户暂缓的需求排最前，其余' if asks else ''))
    out.append('- 本报告只说明 ASG 的设计与自检完成情况，不代替独立审查。')
    out.append('')
    if notes.get('summary'):
        out += [notes['summary'], '']
    if items:
        redrawn = reply_counts.get('REDESIGN', 0) + reply_counts.get('CALC_DOC', 0)
        out += ['本版共收到 %d 条审查意见：改图或补计算/补文档 %d 条，其余 %d 条登记为待办、技术转交或不采纳。'
                % (len(items), redrawn, len(items) - redrawn), '']

    if clarifications:
        out += ['## 需求澄清记录', '',
                '设计中问过用户的需求问题。给定和采纳的已写回需求清单并按它设计；暂缓的按建议条文设计，列在“未关闭项”。', '',
                '| 编号 | 需求原文 | 问题 | 建议条文 | 答复 | 答复人与日期 | 涉及的需求 | 原始需求文件 |', '|---|---|---|---|---|---|---|---|']
        for q in clarifications:
            answer = q.get('answer') or {}
            files = answer.get('requirement_files') or {}
            out.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
                q.get('id'), cell(q.get('requirement_text') or ''), cell(q.get('question') or ''),
                cell(q.get('proposed_requirement') or ''),
                cell('%s：%s' % (DECISIONS.get(answer.get('decision'), answer.get('decision')), answer.get('text', '')) if answer else '还没有答复'),
                cell('%s %s' % (answer.get('by', ''), answer.get('date', '')) if answer else ''),
                '、'.join(q.get('requirement_ids') or []),
                cell('已改：' + '、'.join(files.get('files') or []) if files.get('decision') == 'UPDATED'
                     else '用户不让改' if files.get('decision') == 'KEPT' else '')))
        out.append('')

    roles = [r for r in selection.get('roles') or [] if isinstance(r, dict)]
    if roles:
        out += ['## 核心器件选型', '', '| 角色 | 位号 | 选定 | 候选数 | 理由 | 淘汰依据 |', '|---|---|---|---|---|---|']
        for r in roles:
            chosen = [c for c in r.get('candidates') or [] if isinstance(c, dict) and c.get('status') == 'selected']
            out.append('| %s | %s | %s | %d | %s | %s |' % (
                cell(r.get('role', '')), '、'.join(r.get('refs') or []),
                cell(chosen[0].get('mpn', '')) if chosen else '未选定', len(r.get('candidates') or []),
                cell(chosen[0].get('reason', '')) if chosen else cell(r.get('single_candidate_reason', '')),
                cell('；'.join(r.get('_basis') or []))))
        out.append('')
        optioned = [r for r in roles if r.get('options')]
        if optioned:
            out += ['## 外部条件不确定的选型', '',
                    '这些角色的推荐器件依赖未公开的资料，ASG 列出了可选方案和建议，按你的决定选用。', '']
            for r in optioned:
                decision = r.get('decision') if isinstance(r.get('decision'), dict) else {}
                out += ['### %s（%s）' % (r.get('role', ''), '、'.join(r.get('refs') or [])), '',
                        '| 方案 | 型号 | 外部依赖 | 代价 | 优点 | 缺点 |', '|---|---|---|---|---|---|']
                for o in r['options']:
                    if not isinstance(o, dict):
                        continue
                    deps = [d for d in o.get('external_dependencies') or [] if text(d)]
                    out.append('| %s%s | %s | %s | %s | %s | %s |' % (
                        cell(o.get('name', '')), '（ASG 推荐）' if o.get('recommended') is True else '',
                        cell('、'.join(o.get('parts') or [])), cell('%d 项：%s' % (len(deps), '；'.join(deps)) if deps else '无'),
                        cell(o.get('cost', '')), cell(o.get('pros', '')), cell(o.get('cons', ''))))
                out += ['', '- **ASG 的建议**：%s' % (r.get('recommendation') or ''),
                        '- **用户决定**：%s' % ('%s（%s）' % (decision['option'], decision.get('source', ''))
                                              if text(decision.get('option')) else '未决定'), '']

    if notes.get('changes') or change:
        out += ['## 本版变更', '']
        if change:
            out += ['器件数：%s → %s。' % (change.get('old_components', '?'), change.get('new_components', '?')), '']
        if notes.get('changes'):
            out += [notes['changes'], '']

    if items:
        out += ['## 审查意见处置', '', '| 编号 | 意见 | 处理 | 说明 |', '|---|---|---|---|']
        for i in items:
            label = RESPONSES.get(i.get('response'), ('?',))[0]
            out.append('| %s | %s | %s | %s |' % (cell(i.get('id', '')), cell(i.get('comment', '')), label,
                                                   cell(i.get('detail', '') + ('（复发自 %s）' % i['recurs_from']
                                                                              if text(i.get('recurs_from')) else ''))))
        out.append('')
        _, unread = review_sources(responses, root)
        if unread:
            out += ['意见来源 %s 的原文读不到，来源未核对：上面的意见内容按登记照录。' % '、'.join(unread), '']

    events_list = [e for e in (lessons.get('events') or []) if isinstance(e, dict)]
    if events_list:
        out += ['## 改进记录', '', '| 来源 | 归因 | 改了什么 |', '|---|---|---|']
        for e in events_list:
            out.append('| %s | %s | %s |' % (cell(e.get('source', '')), CAUSE_WORDS.get(e.get('cause'), cell(e.get('cause', ''))),
                                            cell(e.get('change') or e.get('why_none') or '')))
        out.append('')

    if open_work:
        out += ['## 未关闭项', '', SEVERITY_LEGEND, '']
        order = lambda w: (w.get('stage') != 'requirement', SEVERITIES.index(severity_of(w)) if severity_of(w) else len(SEVERITIES),
                           -len(w.get('requirements') or []))
        item_notes = notes.get('items') or {}
        for w in sorted(open_work, key=order):
            level = severity_of(w)
            out += ['### %s（%s）' % (w['id'], '%s：%s；%s，%s' % (
                level, SEVERITY_WORDS[level], CONSEQUENCE_WORDS[w['consequence_class']], OCCURRENCE_WORDS[w['occurrence']])
                if level else '后果等级未定'), '']
            if item_notes.get(w['id']):
                out += [item_notes[w['id']], '']
            gap = w.get('stage') == 'external' and isinstance(w.get('missing'), list)
            if gap:
                fields = (('类型', STAGES['external']), ('责任方', w.get('owner')), ('外部依赖原因', w.get('why_external')),
                          ('失效后果', w.get('consequence')), ('关闭方式', w.get('action')),
                          ('替代方案', w.get('fallback')), ('前置项', '、'.join(w.get('blocked_by') or [])),
                          ('关联需求', '、'.join(w.get('requirements') or [])))
            else:
                fields = (('类型', STAGES.get(w.get('stage'), w.get('stage'))),
                          ('需求澄清', w.get('clarification')),
                          ('设计假设', w.get('assumption')), ('本版进展', w.get('progress')),
                          ('处理措施', w.get('action')),
                          ('改设计候选（须用户批准后实施）', w.get('redesign')),
                          ('责任方', w.get('owner')), ('替代方案', w.get('fallback')),
                          ('前置项', '、'.join(w.get('blocked_by') or [])),
                          ('关联需求', '、'.join(w.get('requirements') or [])))
            for label, value in fields:
                if text(value):
                    out.append('- **%s**：%s' % (label, value))
            if gap:
                out.append('- **缺失资料**：')
                for m in w['missing']:
                    if isinstance(m, dict):
                        out.append('  - 手册已给出：%s；设计所需：%s（%s）' % (m.get('given', ''), m.get('needed', ''), m.get('source', '')))
                calcs = {c.get('id'): c for c in calculations}
                if w.get('calculations'):
                    out.append('- **关联计算**：')
                    out += ['  - %s：%s' % (cid, ('依赖 ' + '、'.join(map(str, basis[cid][2]))) if cid in basis
                                            else calcs.get(cid, {}).get('missing_guarantee') or '（计算不存在）')
                            for cid in w['calculations']]
                elif text(w.get('no_calculation_reason')):
                    out.append('- **关联计算**：无。%s' % w['no_calculation_reason'])
                if w.get('questions'):
                    out.append('- **待确认问题**：')
                    out += ['  %d. %s' % (i, q) for i, q in enumerate(w['questions'], 1)]
            out.append('')

        asked = [w for w in sorted(open_work, key=order) if w.get('stage') == 'external' and w.get('questions')]
        if asked:
            out += ['## 外部资料需求', '',
                    '按责任方汇总外部资料缺口的待确认问题，每组可整段发给对应责任方；括号里是对应待办。', '']
            for owner in OrderedDict.fromkeys(w.get('owner') or '未指定' for w in asked):
                out += ['### %s' % owner, '']
                n = 0
                for w in asked:
                    if (w.get('owner') or '未指定') == owner:
                        for q in w['questions']:
                            n += 1
                            out.append('%d. %s（%s）' % (n, q, w['id']))
                out.append('')

    if handoffs:
        out += ['## 技术转交要求', '',
                '下列要求在 PCB、结构、样机测试等后续环节落实，不属于原理图未完成项。原理图交付时将本表一并转交对应责任方。', '',
                '| 责任方 | 环节 | 要落实的要求 |', '|---|---|---|']
        for w in handoffs:
            out.append('| %s | %s | %s |' % (cell(w.get('owner') or '未指定'), STAGES.get(w.get('stage'), ''),
                                            cell(w.get('action') or '')))
        out.append('')

    # A calculation that misses its target leads the calculation tables, with the terms it sums (R10 ENERGY was listed
    # only as a work item; user 2026-10-28: 先改前四条).
    failed = [c for c in calculations if (tier.get(c.get('id')) if layered else c.get('conclusion')) == 'failed']
    if failed:
        out += ['## 不满足的计算', '',
                '这些计算算出的值没达到门槛，设计未完成。“最好情景”是各项取有利端仍不满足，等资料关不掉，要改设计；'
                '改设计候选须用户批准后实施。', '',
                '| 计算 | 涉及的需求 | 不满足的检查：值与门槛 | 最大的分项 | 改设计候选 | 对应待办 |', '|---|---|---|---|---|---|']
        for c in failed:
            items = [w for w in open_work if c.get('id') in (w.get('calculations') or [])]
            terms = sorted((t for t in c.get('contributors') or [] if isinstance(t, dict) and isinstance(t.get('value'), (int, float))),
                           key=lambda t: -abs(t['value']))[:5]
            out.append('| %s | %s | %s | %s | %s | %s |' % (
                c.get('id'), '、'.join(c.get('requirements') or []),
                cell('；'.join(check_text(k) + ('（最好情景）' if k.get('scenario') == 'best' else '') for k in failing_checks(c))),
                cell('；'.join('%s %s %s' % (t.get('name'), num(t['value']), t.get('unit') or '') for t in terms)),
                cell('；'.join(w['redesign'] for w in items if text(w.get('redesign')))), '、'.join(w['id'] for w in items)))
        out.append('')

    for key in ('vendor_data', 'user_deferred', 'estimate') if layered else ():
        group = [c for c in calculations if tier.get(c.get('id')) == key]
        if not group:
            continue
        out += ['## %s的计算' % TIERS[key], '',
                {'vendor_data': '这些计算的输入里有典型值、手册没给的参数，或挂着未关闭的缺资料待办；按“外部资料需求”取得资料后复算。',
                 'user_deferred': '这些计算用到用户暂缓的需求，本版按建议条文设计；用户定下需求后按定下的数值复算。',
                 'estimate': '这些计算的输入里有 ASG 自己的工程估计或没算的项；收紧估计、补算，或在样件上验证。'}[key],
                '逐个参数的形式化最坏情况证明留给独立审查。', '',
                '| 计算 | 涉及的需求 | 算出的值与门槛 | 依赖的参数或项 | 对应待办 |', '|---|---|---|---|---|']
        for c in group:
            owed = [w['id'] for w in open_work if c.get('id') in (w.get('calculations') or [])]
            owed += [o['work_item'] for o in c.get('omitted_terms') or []
                     if isinstance(o, dict) and o.get('kind') == 'not_calculated' and text(o.get('work_item'))]
            out.append('| %s | %s | %s | %s | %s |' % (c.get('id'), '、'.join(c.get('requirements') or []),
                                                     cell('；'.join(check_text(k) for k in c.get('checks') or [])),
                                                     cell('、'.join(map(str, basis[c.get('id')][2]))), '、'.join(owed)))
        out.append('')
    conditional = [c for c in calculations if c.get('conclusion') == 'conditional'] if not layered else []
    if conditional:
        out += ['## 有条件成立的计算', '',
                '这些计算按设计用途已经够用，不阻塞出图；结论建立在下面写明的假设或没算进去的项上，'
                '按最坏情况逐条证明留给独立审查。', '',
                '| 计算 | 涉及的需求 | 算出的值与门槛 | 假设或没算进去的项 | 对应待办 |', '|---|---|---|---|---|']
        for c in conditional:
            owed = [w['id'] for w in open_work if c.get('id') in (w.get('calculations') or [])]
            out.append('| %s | %s | %s | %s | %s |' % (c.get('id'), '、'.join(c.get('requirements') or []),
                                            cell('；'.join(check_text(k) for k in c.get('checks') or [])),
                                            cell('；'.join((c.get('assumptions') or []) + (c.get('omitted_terms') or []))),
                                            '、'.join(owed)))
        out.append('')

    risks = (derating or {}).get('stress_risks') or []
    if risks:
        out += ['## 应力风险', '',
                '这些应力在器件额定之内，但超过了本项目降额等级的降额值：合格但有风险（应力），不挡定稿（见 stress-spec.md）。', '',
                '| 计算 | 位号 | 降额规则 | 应力 / 降额值 / 额定 | 改进 |', '|---|---|---|---|---|']
        for d in risks:
            out.append('| %s | %s | %s | %s / %s / %s %s | %s |' % (d['calculation'], d.get('ref') or '', d['rule'], num(d.get('value')),
                                                              num(d.get('limit')), num(d.get('rating')), d.get('unit') or '',
                                                              cell(d.get('improvement') or '')))
        out.append('')
    if margins:
        out += ['## 余量不足以覆盖估计误差', '',
                '这些检查满足门槛，但余量小于所依赖工程估计的不确定度：合格但有风险，不挡交付；加大余量或把估计收紧。'
                '降额检查的余量对额定算，不和降额值叠加（derating-rules.md R12）。', '',
                '| 计算 | 检查 | 值 / 门槛 | 余量 / 不确定度 | 改进 |', '|---|---|---|---|---|']
        for m in margins:
            out.append('| %s | %s | %s / %s%s %s | %.2g%% / %.2g%% | %s |' % (
                m['calculation'], cell(m.get('check') or ''), num(m.get('value')), num(m.get('limit')),
                '（额定）' if m.get('against') == 'rating' else '', m.get('unit') or '', m['margin'] * 100,
                m['uncertainty'] * 100, cell(m.get('improvement') or '')))
        out.append('')
    unspecified = [p for p in closure.get('operating_points') or [] if isinstance(p, dict) and p.get('specified') is False]
    if unspecified:
        out += ['## 手册未规定的工作点', '',
                '这些引脚工作在手册没有规定的方式下，手册规定内的替代做法都已评估且不可行，保留为厂家确认项。', '',
                '| 器件引脚 | 工作方式 | 已评估的替代做法 | 厂家确认待办 |', '|---|---|---|---|']
        for p in unspecified:
            alts = '；'.join('%s：%s' % (a.get('approach'), a.get('reason')) for a in p.get('alternatives') or []
                            if isinstance(a, dict))
            out.append('| %s | %s | %s | %s |' % (cell('、'.join(p.get('refs') or []) + ' ' + '、'.join(p.get('pins') or [])),
                                                  cell(p.get('mode') or ''), cell(alts), cell(p.get('work_item') or '')))
        out.append('')

    if cite_review or cite_unchecked:
        out += ['## 引用待人工核对', '',
                '下面的数值在所引手册页的文字里没有找到（表格、单位换算或扫描页都可能读不出），请对照原页确认。', '']
        if cite_review:
            out += ['| 位置 | 手册页 | 数值 |', '|---|---|---|']
            out += ['| %s | %s | %s |' % (cell(r.get('item', '')), cell(r.get('source', '')),
                                          '、'.join(num(v) for v in r.get('values') or [])) for r in cite_review]
            out.append('')
        out += ['- %s' % reason for reason in cite_unchecked] + ([''] if cite_unchecked else [])

    if kinds_unchecked:
        out += ['## 类型声明没核对', '',
                '下面器件的类型声明所引手册页取不出文字（扫描版或没有 pdftotext），原文是否在页上没有核对，请对照原页确认。', '']
        out += ['- %s' % line for line in kinds_unchecked] + ['']

    kept = [f for f in ordering['flagged'] if text(f['reason'])]
    if kept or ordering['not_checked']:
        out += ['## 停产料号', '']
        out += ['- %s %s：手册列在“%s”下，保留理由：%s' % (f['ref'], f['mpn'], f['marker'], f['reason']) for f in kept]
        out += ['- %s' % reason for reason in ordering['not_checked']] + ['']

    if shown:
        out += ['## 自动检查明细', '', '| 检查 | 结果 |', '|---|---|']
        for key, label, status in shown:
            detail = gates[key]
            extra = '，'.join('%s %s' % (k, v) for k, v in detail.items() if k in ('violations', 'errors') and v)
            if detail.get('ignored_rules'):
                extra = '，'.join(x for x in (extra, '工程设为忽略的规则：%s' % '、'.join(detail['ignored_rules'])) if x)
            if key == 'geometry':
                gaps = sum(len(v) for v in (detail.get('coverage_gaps') or {}).values())
                pins = sum(len(v) for v in (detail.get('render_review_items') or {}).values())
                extra = '，'.join(x for x in (extra, '未覆盖对象 %d 项' % gaps if gaps else '',
                                              '%d 个对象交图面审阅' % pins if pins else '') if x)
            out.append('| %s | %s%s |' % (label, GATE_RESULTS.get(status, status), ('（%s）' % extra) if extra else ''))
        if reference_skipped:
            out.append('| %s | 未执行 |' % GATES['reference_contract'])
        out.append('')

    docs = sorted(p.relative_to(root).as_posix() for p in (root / '设计资料').rglob('*') if p.is_file()) \
        if (root / '设计资料').is_dir() else []
    if docs:
        out += ['## 设计资料', ''] + ['- [%s](%s)' % (Path(d).stem, d) for d in docs] + ['']
    if notes.get('highlights'):
        out += ['## 关键设计依据', ''] + ['- ' + h for h in notes['highlights'][:8]] + ['']

    cov = Counter(c.get('coverage') for c in calculations)
    con = Counter(c.get('conclusion') for c in calculations)
    stage_status = Counter((w.get('stage'), w.get('status')) for w in work.values())
    shown_tiers = [k for k in TIERS if k not in OPTIONAL_TIERS or k in tier.values()]
    out += ['## 统计', '', '| 项目 | 数量 |', '|---|---|',
            '| 器件 / 图纸页数 | %d / %d |' % (parts, sheets),
            '| 需求：%s | %s |' % (' / '.join(REQUIREMENTS.values()), ' / '.join(str(req_counts.get(k, 0)) for k in REQUIREMENTS)),
            '| 计算：上下界完整 / 只算了一部分 | %d / %d |' % (cov.get('bounded', 0), cov.get('partial', 0)),
            ('| 计算结论：%s | %s |' % (' / '.join(TIERS[k] for k in shown_tiers), ' / '.join(str(Counter(tier.values()).get(k, 0)) for k in shown_tiers))
             if layered else
             '| 计算结论：满足 / 有条件满足 / 不满足 | %d / %d / %d |' % (con.get('supported', 0), con.get('conditional', 0), con.get('failed', 0))),
            '| 未关闭项：设计未完成 / 外部资料缺口 | %d / %d |' % (stage_status.get(('design', 'open'), 0), stage_status.get(('external', 'open'), 0)),
        ] + (['| 未关闭项：用户暂缓的需求 | %d |' % stage_status[('requirement', 'open')]]
             if stage_status.get(('requirement', 'open')) else []) + [
            '| 技术转交要求 | %d |' % len(handoffs),
            '| 已关闭的待办 | %d |' % sum(v for (s, st), v in stage_status.items() if st == 'closed'), '']
    out += ['## 详细记录', '',
            '原理图在 `原理图/`（KiCad 工程、PDF、网表、BOM）。`record/` 里是生成这份报告用的记录：'
            '`electrical-intent.json` 是设计网表，`design-closure.json` 是需求、待办和计算的处理情况，'
            '`summary.json` 是自动检查结果，`visual-review.json` 是图面审阅记录，`manifest.json` 记录用到的需求、'
            '原厂资料和前一版设计的位置与校验码。', '']
    return '\n'.join(out), problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('delivery', nargs='?', help='delivery folder holding record/')
    parser.add_argument('--notes', help='notes.json written by the agent')
    parser.add_argument('--title')
    parser.add_argument('--pdf-sha256', metavar='PDF', help='print the hash visual-review.json names its PDF by, and exit')
    args = parser.parse_args(argv)
    if args.pdf_sha256:
        print(render_sha256(args.pdf_sha256))
        return 0
    if not args.delivery:
        parser.error('the delivery folder is required')
    notes = json.loads(Path(args.notes).read_text(encoding='utf-8')) if args.notes else None
    report, problems = render(args.delivery, notes, args.title)
    target = Path(args.delivery) / REPORT
    target.write_text(report + '\n', encoding='utf-8')
    print('wrote', target)
    for p in problems:
        print('PROBLEM:', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
