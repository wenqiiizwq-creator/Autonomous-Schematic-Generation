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
from audit_design_closure import calculation_basis, check_delegate, failing_checks, load_task, self_assigned, severity_of, squeeze, vendor_items_of  # noqa: E402
import find_parts  # noqa: E402
import typical_circuits  # noqa: E402
import guideline_criteria  # noqa: E402
import operating_inputs  # noqa: E402
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
    ('design_closure', '设计记录闭合审计'),
])
GATE_RESULTS = OrderedDict([('PASS', '通过（PASS）'), ('FAIL', '没通过（FAIL）'),
                            ('INSUFFICIENT', '资料不足（INSUFFICIENT）'), ('CONDITIONAL', '有条件通过'),
                            ('INCOMPLETE', '未完成（INCOMPLETE）')])
# Shown in the conclusion count only when some gate has them.
OPTIONAL_RESULTS = ('CONDITIONAL', 'INCOMPLETE')
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
# Task 1.3: key functional blocks list the rules that can exclude a candidate scheme (record/scheme-criteria.json).
# Circuit types of the five key-block families: power conversion, protection, isolation, signal chain, external interface.
KEY_CIRCUIT_TYPES = ('POWER_CONVERTER', 'HOLD_UP', 'POWER_PROTECTION', 'SIGNAL_PROTECTION', 'ISOLATION', 'ANALOG',
                     'DC_48V', 'DC_24V', 'AC_MAINS', 'INDUSTRIAL_DI', 'POE_PD', 'VEHICLE_28V', 'SHIP_AC')
# Only a requirement, a standard's text or a datasheet absolute rating excludes a candidate outright; an engineering
# inference is recorded as one and never as a hard exclusion (user 2026-11-05).
EXCLUSION_BASES = OrderedDict([('requirement', '需求'), ('standard', '标准原文'), ('datasheet_abs_max', '手册绝对额定'),
                               ('inference', '工程推论，不作硬排除')])
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
# A confirmation already given in the requirement or scheme documents (SKILL 1.4): scheme:<evidence id>, with locator and quote.
SCHEME_SOURCE = re.compile(r'^scheme:(\S+)$')
# Files ASG writes itself; a scheme confirmation must cite the user's documents, not ASG's own basis.
OWN_WRITING = ('设计资料/', 'record/')


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
    """Words the terminology table says not to use: its first table's last column, without the header and the
    |---| delimiter row (Matrix R3 S30: '---' was read as a banned word and caught every Markdown table in notes)."""
    words = []
    table = path.read_text(encoding='utf-8').split('## 术语', 1)[-1].split('\n## ', 1)[0]
    rows = [line for line in table.splitlines() if line.strip().startswith('|')]
    for line in rows[1:]:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) == 3 and not re.fullmatch(r':?-+:?', cells[2]):
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


CIRCUITS_DIR = Path(__file__).resolve().parent.parent / 'references' / 'typical-circuits'


def circuit_implementations(circuits_dir=CIRCUITS_DIR):
    return {pid: set(info['implementations']) for pid, info in typical_circuits.load(circuits_dir).items()}


def check_knowledge_event(event, where):
    errors = []
    if event.get('knowledge_kind') not in ('approach', 'criterion', 'pitfall'):
        errors.append(where + ' knowledge_kind 必须是 approach/criterion/pitfall')
    if event.get('impact') not in ('observed', 'uncertain'):
        errors.append(where + ' impact 必须是 observed/uncertain')
    if not text(event.get('problem')):
        errors.append(where + ' 要写 problem：缺少的知识及其如何造成具体问题')
    if event.get('impact') == 'observed':
        evidence = event.get('evidence')
        if not text(event.get('consequence')) or not isinstance(evidence, list) or not evidence:
            errors.append(where + ' observed 要写 consequence 和非空 evidence')
    if event.get('impact') == 'uncertain':
        for field in ('uncertainty', 'pending'):
            if not text(event.get(field)):
                errors.append(where + ' uncertain 要写 ' + field)
    if 'evidence' in event and (not isinstance(event['evidence'], list) or any(
            not text(v) or not SOURCE_PATTERN.fullmatch(v) for v in event['evidence'])):
        errors.append(where + ' evidence 必须是现有来源格式的列表')
    return errors


def check_record_locator(value, base):
    """Resolve a delivery file and entry; never treat a planned library target as evidence."""
    if not text(value):
        return False
    file, sep, entry = value.partition('#')
    path = (Path(base) / file).resolve()
    if not sep or not entry.strip() or not path.is_relative_to(Path(base).resolve()) or not path.is_file():
        return False
    try:
        content = path.read_text(encoding='utf-8')
        if path.suffix == '.json':
            data = json.loads(content)
            if entry.startswith('/'):
                for key in entry[1:].split('/'):
                    key = key.replace('~1', '/').replace('~0', '~')
                    data = data[int(key)] if isinstance(data, list) else data[key]
                return True
            def has_id(node):
                if isinstance(node, dict):
                    return node.get('id') == entry or entry in node or any(has_id(v) for v in node.values())
                return isinstance(node, list) and any(has_id(v) for v in node)
            return has_id(data)
        return entry in content or any(
            entry == re.sub(r'[^\w\- ]', '', h.strip().lower()).replace(' ', '-')
            for h in re.findall(r'^#+ (.+)$', content, re.M))
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return False


def library_hits(gap, circuits_dir=CIRCUITS_DIR):
    """Typical circuits an open library gap must say why it does not use (whole-board baseline 2026-11-07, A5: Matrix
    registered its reset block U702 as missing while multi-domain-reset covers MCU reset split from network reset).
    The search find_parts.py --circuits runs for the block name, plus each word of the target file name (mcu, reset,
    supervisor) that is a word of a typical circuit's file name; block names are often refs, the target names the
    function."""
    hits = [h['id'] for h in find_parts.search_circuits([gap['block']], Path(circuits_dir))['results']] if text(gap.get('block')) else []
    words = {w for w in re.split(r'[-_]', Path(str(gap.get('target') or '')).stem.lower()) if len(w) >= 3} - {'and', 'the', 'with', 'for'}
    hits += [pid for pid in find_parts.circuit_index(Path(circuits_dir)) if words & set(pid.lower().split('-'))]
    return list(OrderedDict.fromkeys(hits))


def check_library_gaps(lessons, plan=None, root=None, circuits_dir=CIRCUITS_DIR):
    """Schema 2 structure and cross-record bindings; return only valid open (page, block) pairs."""
    if not isinstance(lessons, dict) or lessons.get('schema_version') != 2:
        return [], set()
    gaps = lessons.get('library_gaps')
    if not isinstance(gaps, list):
        return ['lessons.json schema 2 要写 library_gaps 列表（没有缺口写空列表）'], set()
    errors, valid, ids, pairs = [], set(), Counter(), Counter()
    for gap in gaps:
        if isinstance(gap, dict):
            if text(gap.get('id')):
                ids[gap['id']] += 1
            if text(gap.get('page')) and text(gap.get('block')):
                pairs[(gap['page'], gap['block'])] += 1
    pages = {p.get('file'): p for p in plan.get('pages', []) if isinstance(p, dict) and text(p.get('file'))} if isinstance(plan, dict) else {}
    for i, gap in enumerate(gaps, 1):
        where = 'library_gaps 第 %d 项' % i
        bad = []
        if not isinstance(gap, dict):
            errors.append(where + ' 必须是对象')
            continue
        for field in ('id', 'page', 'block', 'reason', 'source', 'design_basis', 'target', 'status'):
            if not text(gap.get(field)):
                bad.append(where + ' 要写 ' + field)
        if 'cause' in gap:
            bad.append(where + ' 是资料覆盖待办，不能带 cause')
        if text(gap.get('id')) and ids[gap['id']] > 1:
            bad.append(where + ' id 重复')
        pair = (gap.get('page'), gap.get('block'))
        if all(text(v) for v in pair) and pairs[pair] > 1:
            bad.append(where + ' page/block 重复')
        if not text(gap.get('source')) or not SOURCE_PATTERN.fullmatch(gap['source']):
            bad.append(where + ' source 格式不对')
        if gap.get('status') not in ('open', 'closed'):
            bad.append(where + ' status 必须是 open/closed')
        target = gap.get('target')
        if not text(target) or not re.fullmatch(r'references/typical-circuits/[^/\\#]+\.md', target) or '..' in target:
            bad.append(where + ' target 必须是 references/typical-circuits/<功能>.md')
        if root is not None and not check_record_locator(gap.get('design_basis'), root):
            bad.append(where + ' design_basis 文件/条目不存在或超出本版目录')
        if plan is not None:
            page = pages.get(gap.get('page')) if text(gap.get('page')) else None
            blocks = page.get('blocks') if page else None
            if not isinstance(blocks, dict) or not text(gap.get('block')) or gap['block'] not in blocks:
                bad.append(where + ' 没有对应 page/block')
        if gap.get('status') == 'closed':
            if not text(gap.get('resolution')):
                bad.append(where + ' closed 要写 resolution')
            elif not check_record_locator(gap['resolution'], Path(circuits_dir).parent.parent):
                bad.append(where + ' resolution 文件/条目不存在')
            if text(target):
                pid = Path(target).stem
                implementations = circuit_implementations(circuits_dir)
                if pid not in implementations:
                    bad.append(where + ' closed 的典型电路不存在')
                if plan is not None and page:
                    circuits = page.get('circuits')
                    ref = circuits.get(gap['block']) if isinstance(circuits, dict) and text(gap.get('block')) else None
                    if not text(ref) or ref.partition('#')[0] != pid or ref.partition('#')[2] not in implementations.get(pid, set()):
                        bad.append(where + ' closed 页计划没有标注目标文件的有效实现方案')
                if text(gap.get('resolution')) and gap['resolution'].partition('#')[0] != target:
                    bad.append(where + ' resolution 必须指向 target 的补写位置')
        if gap.get('status') == 'open':
            unexplained = [pid for pid in library_hits(gap, circuits_dir) if pid not in str(gap.get('reason') or '')]
            if unexplained:
                bad.append(where + ' 登记库内没有，但按块名和 target 检索典型电路命中 %s；在 reason 里逐个写明它为什么不适用'
                           % '、'.join(unexplained))
        if not bad and gap.get('status') == 'open':
            valid.add(pair)
        errors += bad
    return errors, valid


def check_block_circuits(name, blocks, patterns, implementations, lessons, root=None, key_blocks=()):
    """Each key functional block names an existing pattern approach, or lessons.json registers the gap."""
    errors = []
    lessons = lessons if isinstance(lessons, dict) else {}
    version = lessons.get('schema_version', 1)
    registered = version == 1 and any(
        isinstance(e, dict) and e.get('cause') == 'knowledge_missing'
        and 'typical-circuits' in str(e.get('change') or '')
        for e in lessons.get('events') or [])
    _, valid_gaps = check_library_gaps(lessons, root=root)
    patterns = patterns if isinstance(patterns, dict) else {}
    for block in blocks:
        ref = patterns.get(block)
        if not text(ref):
            if block in key_blocks and not registered and (name, block) not in valid_gaps:
                errors.append('%s：功能块“%s”没有标注典型电路（patterns），没有合适典型电路时在 lessons.json 登记 knowledge_missing 并补写 references/typical-circuits/' % (name, block) if version == 1 else '%s：功能块“%s”没有典型电路或有效的 library_gaps 逐块覆盖待办' % (name, block))
            continue
        pid, _, approach = ref.partition('#')
        if pid not in implementations:
            errors.append('%s：功能块“%s”标注的典型电路 %s 在 references/typical-circuits/ 里不存在' % (name, block, pid))
        elif approach not in implementations[pid]:
            errors.append('%s：功能块“%s”标注的实现方案“%s”不在典型电路 %s 里（有：%s）' % (name, block, approach, pid, '、'.join(sorted(implementations[pid]))))
    return errors


def check_page_plan(plan, intent, visual, lessons=None, circuits_dir=CIRCUITS_DIR, root=None, scheme=None):
    """Every drawn page has a plan (reader tasks, blocks of parts, the pattern of each block) and a review that traced each task."""
    if not isinstance(plan, dict) or plan.get('schema_version') != 1 or not isinstance(plan.get('pages'), list):
        return ['page-plan.json 必须是 schema_version 1、带 pages 列表的对象']
    errors, _ = check_library_gaps(lessons, plan=plan, root=root, circuits_dir=circuits_dir)
    implementations = circuit_implementations(circuits_dir)
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
        key_blocks = page.get('key_blocks', [])
        if not isinstance(key_blocks, list) or any(not text(b) or b not in blocks for b in key_blocks):
            errors.append('%s：key_blocks 必须列出本页 blocks 中的关键功能块名' % name)
            key_blocks = []
        key_blocks = set(key_blocks) | {b['block'] for b in ((scheme or {}).get('blocks') or [])
                                        if isinstance(b, dict) and text(b.get('block')) and b['block'] in blocks}
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
            errors += check_block_circuits(name, blocks, page.get('circuits'), implementations, lessons, root=root, key_blocks=key_blocks)
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
    if not chosen:
        problems.append('选型角色“%s”还没有你的决定：decision 要写 {option: 方案名, source: user:<日期>}，'
                        '定下来之前不进入设计网表' % name)
    elif norm_mpn(selected.get('mpn', '')) not in {norm_mpn(p) for p in chosen.get('parts') or [] if text(p)}:
        problems.append('选型角色“%s”选定的 %s 不在你选的方案“%s”里' % (name, selected.get('mpn'), chosen['name']))
    return problems


def check_confirmation(name, role, selected, evidence, root):
    """Every core role carries who confirmed it (整板评测 2026-11-07 A2/A6): the user (user:<日期>), or the user's
    requirement or scheme documents (scheme:<证据编号> with the quoted words naming the selected part)."""
    decision = role.get('decision') if isinstance(role.get('decision'), dict) else {}
    source = decision.get('source') if text(decision.get('source')) else ''
    if source.startswith('delegate:'):
        # Delegated by the task file (workflow-handoff.md delegation): only ASG's recommended option may be taken.
        found = check_delegate(source, 'selection', root)
        if found:
            return ['选型角色“%s”的任务书代答不成立（%s）：%s' % (name, found[0], found[1])]
        picked = next((o for o in role.get('options') or [] if isinstance(o, dict) and o.get('name') == decision.get('option')), None)
        if role.get('options') and not (picked and picked.get('recommended') is True):
            return ['选型角色“%s”的任务书代答只能采纳 ASG 推荐的方案（recommended）' % name]
        return []
    marks = self_assigned({k: v for k, v in decision.items() if k not in ('option', 'quote')})
    if marks:
        return ['选型角色“%s”的确认记录是运行者自拟的（%s），不是用户的确认：无人当场确认时不能自填 user:，'
                '按任务书代答授权写 delegate:，没有授权就停下来问' % (name, '、'.join(sorted(set(marks))))]
    if USER_SOURCE.match(source):
        return [] if text(decision.get('locator')) else [
            '选型角色“%s”的用户确认要写 locator（对话里哪一处）' % name]
    m = SCHEME_SOURCE.match(source)
    if not m:
        return ['选型角色“%s”还没有确认记录：decision.source 写 user:<日期>（用户确认，另写 locator）、scheme:<证据编号>'
                '（需求或方案文档已写明用户确认，另写 locator 与原文 quote），或 delegate:<代答人>:<日期>（任务书代答）；'
                '确认前不进入步骤 ②' % name]
    row = (evidence or {}).get(m.group(1))
    path = row.get('path') if isinstance(row, dict) and text(row.get('path')) else ''
    quote = decision.get('quote') if text(decision.get('quote')) else ''
    where = '选型角色“%s”的确认引用 %s' % (name, source)
    if not path:
        return ['%s 不在 design-closure.json 的 evidence 里' % where]
    if path.startswith(OWN_WRITING):
        return ['%s 指向 ASG 自己写的 %s：要引用户的需求或方案文档' % (where, path)]
    if not text(decision.get('locator')) or not quote:
        return ['%s 要写 locator（文档里哪一处）和 quote（原文）' % where]
    try:
        body = (Path(root) / path).read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return ['%s：%s 读不到或不是文本文件，核对不了原文' % (where, path)]
    if squeeze(quote) not in squeeze(body):
        return ['%s 的原文在 %s 里找不到' % (where, path)]
    if selected and text(selected.get('mpn')) and norm_mpn(selected['mpn']) not in norm_mpn(quote):
        return ['%s 的原文不含选定型号 %s：文档确认的不是这颗器件，要另交用户确认' % (where, selected['mpn'])]
    return []


def check_selection(data, intent, root, evidence=None):
    """Every core part was chosen from compared candidates whose datasheets are in the library. The refs and part
    numbers are bound to the design netlist only once it exists: task 1.4 runs before task 2.4 writes it (Matrix R3 S06)."""
    roles = data.get('roles') if isinstance(data, dict) else None
    if not isinstance(roles, list) or not roles:
        return ['selection.json 没有 roles：每个核心器件角色都要有候选比较（见 core-part-selection.md）']
    problems = []
    comps = {c.get('ref'): c for c in intent.get('components') or [] if isinstance(c, dict)}
    netlist = 'components' in intent
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
        problems += check_confirmation(name, role, selected[0] if len(selected) == 1 else None, evidence, root)
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
        for ref in refs if netlist else []:
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
    version = data.get('schema_version', 1) if isinstance(data, dict) else None
    if type(version) is not int or version not in (1, 2):
        return ['lessons.json schema_version 只支持 1（历史）或 2'], {}
    gap_problems, _ = check_library_gaps(data)
    events = data.get('events') if isinstance(data, dict) else None
    if version == 2 and isinstance(events, list) and not events and data.get('library_gaps') and not gap_problems:
        return [], {}
    if not isinstance(events, list) or not events:
        return gap_problems + ['lessons.json 没有 events：每次设计至少登记一条学到的东西，没有就登记 cause=none 并写明核对了什么'], {}
    problems, by_source = gap_problems, {}
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
        if version == 2 and cause == 'knowledge_missing':
            problems += check_knowledge_event(e, 'lessons.json 第 %d 条' % i)
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
    lesson_events = (lessons or {}).get('events')
    for i, e in enumerate(lesson_events if isinstance(lesson_events, list) else [], 1):
        result = check_source(e.get('source'), (), [root]) if isinstance(e, dict) else None
        if result:
            note(result, 'lessons.json 第 %d 条' % i, e['source'])
        if isinstance(e, dict) and (lessons or {}).get('schema_version') == 2:
            for source in e.get('evidence') if isinstance(e.get('evidence'), list) else []:
                result = check_source(source, (), [root])
                if result:
                    note(result, 'lessons.json 第 %d 条 evidence' % i, source)
    if isinstance(lessons, dict) and lessons.get('schema_version') == 2:
        for gap in lessons.get('library_gaps') if isinstance(lessons.get('library_gaps'), list) else []:
            if isinstance(gap, dict):
                result = check_source(gap.get('source'), (), [root])
                if result:
                    note(result, 'library_gaps %s' % gap.get('id'), gap.get('source'))
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


STAGE_WORDS = {'schematic': '原理图', 'pcb': 'PCB', 'simulation': '仿真', 'prototype': '样机', 'production': '生产'}


def render_operating_inputs(found):
    """The declared condition inputs and the review list of design-closure.md 工况输入; an error is listed with the others."""
    if not found:
        return []
    out = ['## 工况输入来源', '', '计算用到的外部工况（负载、源阻抗、环境温度……）从哪来。第一张表审计核过来源；后面是核对清单，脚本判不了，不挡交付，要人看。', '']
    declared = found.get('declared') or []
    if declared:
        out += ['| 计算 | 输入 | 类别 | 值 | 依据 | 来源 |', '|---|---|---|---|---|---|']
        for d in declared:
            out.append('| %s | %s | %s | %s %s | %s | %s |' % (d['calculation'], cell(d.get('parameter') or ''), operating_inputs.ROLES[d['role']][0],
                                                              num(d.get('value')), d.get('unit') or '', d.get('basis'), cell(str(d.get('source') or ''))))
        out.append('')
    listed = found.get('checklist') or {}
    weak = listed.get('weak_sources') or []
    if weak:
        out += ['**看名字像工况、由 ASG 自定的参数**（没写 `input_role`）：'
                + '；'.join('%s 的 %s（%s %s，%s）' % (w['calculation'], w['parameter'], num(w.get('value')), w.get('unit') or '', w['basis']) for w in weak)
                + '。外部给定的要有来源，本板自己的不用管。', '']
    several = listed.get('multiple_candidates') or []
    if several:
        out += ['**需求里还写了同一量的其他值**（有多个候选时取不利值，理由写进参数；审计不判取得对不对）：'
                + '；'.join('%s 的 %s 取 %s %s，%s 还写了 %s（理由：%s）' % (
                    c['calculation'], c['parameter'], num(c.get('value')), c.get('unit') or '', c['requirement'],
                    '、'.join(num(v) for v in c['others']), c.get('reason') or '**没写**') for c in several) + '。', '']
    parts = listed.get('switch_parts_without_startup_calculation') or []
    if parts:
        out += ['**没有启动计算的 eFuse、热插拔或负载开关**：%s。没有启动限流问题的不用管。' % '、'.join(parts), '']
    missing = {}
    for row in listed.get('calculations') or []:
        for role in row['missing']:
            missing.setdefault(role, []).append(row['calculation'])
    roles = listed.get('roles') or []
    if roles:
        out += ['| 工况 | 适用准则列它的条数 | 需求里提到 | 引用这些准则、参数里没写它的计算 |', '|---|---|---|---|']
        for r in roles:
            calcs = missing.get(r['role']) or []
            out.append('| %s | %d | %s | %s |' % (r['title'], r['rules'], '、'.join(r.get('requirements') or []) or '**没有**',
                                                  ('、'.join(calcs[:5]) + ('等 %d 条' % len(calcs) if len(calcs) > 5 else '')) or '—'))
        out.append('')
    return out


def render_batch_guidelines(guidelines, cards):
    """The rules covered in bulk (user 2026-11-04), one table per class: which baseline item answers each project_input
    rule, and the downstream handoff list."""
    classes = guidelines.get('by_coverage') or {}
    out = []
    if classes.get('project_input'):
        out += ['## 需求基线回答的设计准则', '',
                '这些设计准则由一份需求基线或需求澄清记录一次回答；TBR 是还没有答复的项。', '',
                '| 设计准则 | 内容 | 回答项 |', '|---|---|---|']
        for gid in classes['project_input']:
            answer = '不适用：' + guidelines['not_applicable'][gid] if gid in guidelines['not_applicable'] else \
                '、'.join(w.partition(':')[2] for w in guidelines['covered'].get(gid) or []) or '未回答'
            out.append('| %s | %s | %s |' % (gid, cell(cards.get(gid, {}).get('title', '')), cell(answer)))
        out.append('')
    down = [gid for gid in classes.get('handoff') or [] if gid not in guidelines['not_applicable']]
    if down:
        out += ['## 下游交接清单', '',
                '这些设计准则进下游交接清单，由所列待办或交接表带给下游；原理图阶段只列出，不宣布已满足。', '',
                '| 设计准则 | 关闭阶段 | 交接处 | 下游要做的（设计准则 asg_action） |', '|---|---|---|---|']
        for gid in down:
            c = cards.get(gid, {'closing_stage': '', 'asg_action': ''})
            where = '、'.join(w for w in guidelines['covered'].get(gid) or [] if w.startswith(('work:', 'evidence:')))
            out.append('| %s | %s | %s | %s |' % (gid, STAGE_WORDS.get(c['closing_stage'], ''), where or '无', cell(c['asg_action'])))
        out.append('')
    return out


def render_guidelines(guidelines):
    """共用设计准则覆盖与下游约束（references/shared/guideline-criteria.md）：适用准则、出处、在哪里落实；关闭阶段在原理图之后的单列。"""
    if not (guidelines and guidelines.get('applicable')):
        return []
    cards = {r['id']: r for r in guideline_criteria.load()['criteria']}
    where = lambda gid: ('、'.join(guidelines['covered'].get(gid) or [])
                         or ('不适用：' + guidelines['not_applicable'][gid] if gid in guidelines['not_applicable'] else '未覆盖'))
    out = ['## 共用设计准则覆盖', '',
           '本设计按设计准则库 %s 适用的共用设计准则；“落实处”是引用它的计算（calc）、待办（work）或器件性能要求（component）。' % guidelines['library_version'], '',
           '| 设计准则 | 内容 | 出处 | 落实处 | 关闭阶段 |', '|---|---|---|---|---|']
    classes = guidelines.get('by_coverage') or {}
    batch = set(classes.get('project_input') or ()) | set(classes.get('handoff') or ())
    for gid in guidelines['applicable']:
        if gid in batch:
            continue
        c = cards.get(gid, {'title': '', 'source': [], 'closing_stage': ''})
        source = '；'.join('%s %s %s 第%s页' % (s['document'], s['edition'], s['clause'], s['page']) for s in c['source'])
        out.append('| %s | %s | %s | %s | %s |' % (gid, cell(c['title']), cell(source), cell(where(gid)),
                                                    STAGE_WORDS.get(c['closing_stage'], '')))
    out.append('')
    out += render_batch_guidelines(guidelines, cards)
    down = [gid for gid in guidelines['downstream'] if gid not in guidelines['not_applicable'] and gid not in batch]
    if down:
        out += ['## 下游约束（共用规范）', '',
                '这些设计准则在原理图之后的环节关闭，由所列待办交给下游；原理图阶段不宣布它们已满足。', '',
                '| 设计准则 | 关闭阶段 | 技术转交待办 | 下游要做的（设计准则 asg_action） |', '|---|---|---|---|']
        for gid in down:
            c = cards.get(gid, {'closing_stage': '', 'asg_action': ''})
            work = [w for w in guidelines['covered'].get(gid) or [] if w.startswith('work:')]
            out.append('| %s | %s | %s | %s |' % (gid, STAGE_WORDS.get(c['closing_stage'], ''), '、'.join(work) or '无',
                                                  cell(c['asg_action'])))
        out.append('')
    return out


def check_scheme_candidates(block, where, plan=None):
    """核对选择记录；来源语义和决定条件的工程充分性仍须回原文人工核对。"""
    problems = []
    decisive = block.get('decisive')
    if not isinstance(decisive, list) or not decisive or any(
            not isinstance(d, dict) or not text(d.get('condition')) or not text(d.get('value')) for d in decisive):
        problems.append(where + ' decisive 要列出 {condition, value}：决定条件及本板取值')
    candidates = block.get('candidates')
    if not isinstance(candidates, list) or not candidates:
        return problems + [where + ' candidates 要写候选比较或只有一种可行方案及检索说明']
    if len(candidates) == 1 and not text(block.get('only_viable')):
        problems.append(where + ' 只有一种可行方案时要在 only_viable 写明查过哪些资料及原因')
    chosen, names = [], set()
    for candidate in candidates:
        if not isinstance(candidate, dict) or not text(candidate.get('name')):
            problems.append(where + ' 候选要写 name')
            continue
        name = candidate['name']
        if name in names:
            problems.append(where + ' 候选名称重复：' + name)
        names.add(name)
        sources = candidate.get('source')
        if not isinstance(sources, list) or not sources or any(not text(v) or not SOURCE_PATTERN.fullmatch(v) for v in sources):
            problems.append(where + ' 候选“%s”要写 source 来源列表（沿用 datasheet/review/test/user 格式）' % name)
        if 'unverified' in candidate and not isinstance(candidate['unverified'], bool):
            problems.append(where + ' 候选“%s”的 unverified 必须是布尔值' % name)
        if candidate.get('status') not in ('selected', 'rejected'):
            problems.append(where + ' 候选“%s”status 必须是 selected/rejected' % name)
        if not text(candidate.get('reason')):
            problems.append(where + ' 候选“%s”要写选中或淘汰理由 reason' % name)
        if candidate.get('status') == 'selected':
            chosen.append(candidate)
            if candidate.get('unverified') is not None and candidate.get('unverified') is not False:
                problems.append(where + ' 未证实（unverified）候选不能被选定：' + name)
    if len(chosen) != 1:
        problems.append(where + ' 必须有且只有一个 selected 候选')
    if plan is not None and len(chosen) == 1:
        pages = plan.get('pages') if isinstance(plan, dict) else []
        pages = pages if isinstance(pages, list) else []
        matches = [p for p in pages if isinstance(p, dict) and isinstance(p.get('blocks'), dict)
                   and block['block'] in p['blocks']]
        selected = chosen[0]
        expected = selected.get('circuit') or selected['name']
        if 'circuit' in selected and (not text(selected['circuit']) or '#' not in selected['circuit']):
            problems.append(where + ' circuit 要写 文件名#方案名')
        if not matches:
            problems.append(where + ' 在 page-plan.json 中没有对应功能块')
        for page in matches:
            ref = (page.get('circuits') or {}).get(block['block']) if isinstance(page.get('circuits'), dict) else None
            if not text(expected) or not text(ref) or expected not in ((ref,) if 'circuit' in selected else (ref, ref.partition('#')[2])):
                problems.append(where + ' selected 方案与 page-plan.json 的 circuits 不一致')
    return problems


def closes(check, name):
    """A check closes a deferred value when its name mentions the value ("LDO 结温 对 Tjmax 125 °C×0.8" closes
    "LDO 结温") or its `defer` field (a string or a list) names it, and it has a conclusion: value, operator and limit."""
    named = check.get('defer') if isinstance(check.get('defer'), list) else [check.get('defer')]
    return holds(check) is not None and (squeeze(name) in squeeze(check.get('name'))
                                         or squeeze(name) in {squeeze(n) for n in named if text(n)})


def check_deferred(where, gid, defer, closure):
    """Each value task 1.3 left to task 2.2 is closed there: a calculation that cites the rule in its guidelines has a
    check that closes it (closes). A rule cited by a calculation that computes none of it is covered in form only
    (whole-board baseline 2026-11-07, A4: the calibration board deferred "SM712 钳位对收发器总线额定", CALC-RS485 cited
    G05-033 and G04-005 but compared no clamp voltage with the transceiver's bus rating)."""
    rows = closure.get('calculations')
    rows = list(rows.values()) if isinstance(rows, dict) else rows if isinstance(rows, list) else []
    citing = [r for r in rows if isinstance(r, dict) and isinstance(r.get('guidelines'), list) and gid in r['guidelines']]
    problems = []
    for name in defer:
        if not any(closes(c, name) for r in citing for c in r.get('checks') or [] if isinstance(c, dict)):
            problems.append('%s 的 %s 留给 2.2 的“%s”没有闭合：在引用 %s 的计算里加一项核对（name 含这个数值名，或 defer 字段写它），'
                            '给出 value、operator、limit%s' % (
                                where, gid, name, gid, '；现引用它的 %s 没算这一项，只是形式覆盖' % '、'.join(
                                    'calc:%s' % r.get('id') for r in citing) if citing else ''))
    return problems


def check_scheme_criteria(data, closure, bundle=None, plan=None):
    """record/scheme-criteria.json (SKILL.md task 1.3): required when guideline_scope names a key-block circuit type.
    Each key circuit type of the scope is in some block; each listed rule exists, is active and is triggered by that
    block's types and kinds (with the G07 port rules when the block has external ports); a block with no rule says
    what it searched. Returns the problems."""
    closure = closure if isinstance(closure, dict) else {}
    scope = closure.get('guideline_scope') if isinstance(closure.get('guideline_scope'), dict) else {}
    key = [t for t in scope.get('circuit_types') or [] if t in KEY_CIRCUIT_TYPES]
    pages = plan.get('pages') if isinstance(plan, dict) else []
    pages = pages if isinstance(pages, list) else []
    page_keys = {b for p in pages if isinstance(p, dict) and isinstance(p.get('key_blocks'), list)
                 for b in p['key_blocks'] if isinstance(b, str)}
    if data is None:
        return ['缺少 record/scheme-criteria.json：关键功能块（%s）定方案时要写会淘汰候选的规则或查过的范围（见 SKILL.md 任务 1.3）'
                % '、'.join(key or sorted(page_keys))] if key or page_keys else []
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('blocks'), list) or not data['blocks']:
        return ['scheme-criteria.json 要写 version 1 和非空的 blocks 列表（见 delivery-report.md）']
    bundle = bundle or guideline_criteria.load()
    cards = {r['id']: r for r in bundle['criteria']}
    baseline = scope.get('baseline')
    problems, named = [], set()
    block_names = set()
    for i, block in enumerate(data['blocks'], 1):
        where = 'scheme-criteria.json 第 %d 块' % i
        if not isinstance(block, dict) or not text(block.get('block')):
            problems.append('%s 要写 block（功能块名）' % where)
            continue
        where = 'scheme-criteria.json“%s”' % block['block']
        if block['block'] in block_names:
            problems.append(where + ' 功能块名重复')
        block_names.add(block['block'])
        types, kinds = block.get('circuit_types'), block.get('device_kinds', [])
        if not isinstance(types, list) or not types or not isinstance(kinds, list):
            problems.append('%s 要写 circuit_types（非空列表）和 device_kinds（列表）' % where)
            continue
        outside = [v for v in types + kinds if v not in (scope.get('circuit_types') or []) + (scope.get('device_kinds') or [])]
        if outside:
            problems.append('%s 的 %s 不在 guideline_scope 里' % (where, '、'.join(map(str, outside))))
        named |= set(types)
        problems += check_scheme_candidates(block, where, plan)
        allowed = {r['id'] for r in guideline_criteria.select(bundle, baseline, types, kinds, typed_only=True,
                                                               ports=block.get('ports') is True)}
        criteria = block.get('criteria')
        if not isinstance(criteria, list):
            problems.append('%s 要写 criteria 列表（没有能淘汰候选的规则时写空列表）' % where)
            continue
        if not criteria and not text(block.get('searched')):
            problems.append('%s 没有能淘汰候选的规则，要在 searched 写明查过的规则范围' % where)
        for item in criteria:
            gid = item.get('id') if isinstance(item, dict) else None
            if gid not in cards or cards[gid]['status'] != 'active':
                problems.append('%s 引用的 %s 不是设计准则库里的有效规则' % (where, gid))
                continue
            if gid not in allowed:
                problems.append('%s 引用的 %s 不由该块的电路类型、器件类别或端口触发' % (where, gid))
            if not (text(item.get('excludes')) and text(item.get('how'))):
                problems.append('%s 的 %s 要写 excludes（排除的候选）和 how（选定方案怎样满足）' % (where, gid))
            if item.get('basis') not in EXCLUSION_BASES:
                problems.append('%s 的 %s 要写 basis（%s 之一）：只有需求、标准原文或手册绝对额定能硬排除，工程推论写 inference'
                                % (where, gid, '/'.join(EXCLUSION_BASES)))
            elif item.get('basis') == 'standard' and cards[gid].get('nature') not in ('shall', 'should'):
                problems.append('%s 的 %s 写 basis: standard，但规则卡 nature 为 %s；standard 只用于 shall/should，'
                                'method 是工程方法，project 是项目输入，请按实际依据改成 requirement 或 inference'
                                % (where, gid, cards[gid].get('nature')))
            defer = item.get('defer', [])
            if not (isinstance(defer, list) and all(text(d) for d in defer)):
                problems.append('%s 的 %s 的 defer 是留给任务 2.2 核算的数值名列表' % (where, gid))
            else:
                problems += check_deferred(where, gid, defer, closure)
    recorded_blocks = {b.get('block') for b in data['blocks'] if isinstance(b, dict) and text(b.get('block'))}
    if page_keys - recorded_blocks:
        problems.append('scheme-criteria.json 没有比较关键功能块：' + '、'.join(sorted(page_keys - recorded_blocks)))
    missing = [t for t in key if t not in named]
    if missing:
        problems.append('scheme-criteria.json 没有功能块覆盖关键电路类型 %s' % '、'.join(missing))
    return problems


def render_scheme_criteria(data):
    """方案阶段对照的规则：每个关键功能块会淘汰候选的规则，或查过的范围。"""
    blocks = [b for b in (data.get('blocks') or []) if isinstance(b, dict)] if isinstance(data, dict) and isinstance(data.get('blocks'), list) else []
    if not blocks:
        return []
    out = ['## 功能块方案比较', '', '| 功能块 | 决定条件及本板取值 | 候选 | 处置及理由 | 来源 |', '|---|---|---|---|---|']
    for b in blocks:
        decisive = '；'.join('%s：%s' % (d.get('condition', ''), d.get('value', ''))
                             for d in (b.get('decisive') if isinstance(b.get('decisive'), list) else []) if isinstance(d, dict))
        for c in b.get('candidates', []) if isinstance(b.get('candidates'), list) else []:
            if not isinstance(c, dict):
                continue
            status = '选定' if c.get('status') == 'selected' else '淘汰'
            if c.get('unverified'):
                status += '（未证实）'
            out.append('| %s | %s | %s | %s：%s | %s |' % (
                cell(b.get('block')), cell(decisive), cell(c.get('name')), status,
                cell(c.get('reason', '')), cell('；'.join(map(str, c.get('source', []))) if isinstance(c.get('source'), list) else '')))
        if text(b.get('only_viable')):
            out += ['', '%s：只有一种可行方案，%s' % (cell(b.get('block')), cell(b['only_viable'])), '']
    out += ['', '## 方案阶段对照的规则', '',
           '关键功能块定方案时找出的会淘汰候选的规则（SKILL.md 任务 1.3）。这里的结论不代替任务 2.2 的核算，'
           '这些规则在设计闭环时仍按“共用设计准则覆盖”核对；依据为工程推论的不作硬排除。', '',
           '| 功能块 | 设计准则 | 排除的候选 | 依据 | 选定方案怎样满足 | 留给 2.2 核算 |', '|---|---|---|---|---|---|']
    for b in blocks:
        items = [c for c in b.get('criteria') or [] if isinstance(c, dict)]
        if not items:
            out.append('| %s | 无 | 无（查过：%s） | | | |' % (cell(b.get('block')), cell(b.get('searched') or '')))
        for c in items:
            out.append('| %s | %s | %s | %s | %s | %s |' % (
                cell(b.get('block')), c.get('id'), cell(c.get('excludes')), EXCLUSION_BASES.get(c.get('basis'), '未写'),
                cell(c.get('how')), cell('、'.join(c.get('defer') or [])) or '无'))
    out.append('')
    return out


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
    if isinstance(audit.get('guidelines'), dict):
        problems += ['共用层身份：' + e for e in guideline_criteria.identity_errors(audit['guidelines'])]
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
    problems += check_visual_items(root, visual, summary)
    scheme, problem = None, None
    if (record / 'scheme-criteria.json').exists():
        scheme, problem = load(record / 'scheme-criteria.json')
    problems += [problem] if problem else check_scheme_criteria(scheme, closure, plan=data['page-plan.json'])
    if data['page-plan.json'] is not None:
        problems += check_page_plan(data['page-plan.json'], intent, visual, lessons, root=root, scheme=scheme if isinstance(scheme, dict) else None)
    selection = data['selection.json'] or {}
    if data['selection.json'] is not None:
        evidence = {e.get('id'): e for e in closure.get('evidence') or [] if isinstance(e, dict)}
        problems += check_selection(selection, intent, root, evidence)
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
    # Matrix R3 S35: every counted gate has a listed state, so the states add up to the gate count.
    assert sum(gate_counts[k] for k in GATE_RESULTS) == len(shown), 'gate states not in GATE_RESULTS: %s' % sorted(
        '%s=%s' % (k, st) for k, _, st in shown if st not in GATE_RESULTS)
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
        if key not in OPTIONAL_RESULTS or gate_counts.get(key))))
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
          (['没有 uncertainty_version（工程估计的余量没有对不确定度核对）'] if closure and layered and 'uncertainty_version' not in closure else []) + \
          (['没有 binding_version（料号与手册、符号脚类型、未用脚处置和电源轨最高电压没有核对）']
           if closure and layered and 'binding_version' not in closure else []) + \
          (['没有 matrix_version（复位门限、温度、端口应力没有对全部对象核对，保护逻辑没有状态表）']
           if closure and layered and 'matrix_version' not in closure else [])
    if old:
        out.append('- **记录版本**：%s。新设计按 parameter_version 3、gap_version 2、derating_version 1、uncertainty_version 1、'
                   'binding_version 1、matrix_version 1 写。'
                   % '；'.join(old))
    matrices = audit.get('matrices') if isinstance(audit.get('matrices'), dict) else None
    if matrices:
        titles = {'supervised_rails': '受监督轨门限×负载', 'temperature': '温度×器件', 'port_stress': '端口应力×路径器件',
                  'protection_states': '保护逻辑状态'}
        out.append('- **对全部对象核对**：%s。缺结论和不满足的格逐条列在 design-closure-audit.json 的 matrices。' % '；'.join(
            '%s %d 格，有结论 %d，缺 %d，不满足 %d' % (titles.get(k, k), v.get('cells', 0), v.get('concluded', 0),
                                                 len(v.get('missing') or []), len(v.get('failed') or []))
            for k, v in matrices.items() if isinstance(v, dict)))
    derating = audit.get('derating') if isinstance(audit.get('derating'), dict) else None
    if derating:
        risks, hints = derating.get('stress_risks') or [], derating.get('hints') or []
        out.append('- **降额等级**：%s（%s，见 stress-spec.md）。%s%s' % (
            LEVEL_NAMES.get(derating.get('level'), '未定'), derating.get('source') or '没有写来源',
            '合格但有风险（应力）%d 处，见“应力风险”。' % len(risks) if risks else '写出的应力都在降额值以内。',
            '另有 %d 处应力比较没点名降额规则（提示）。' % len(hints) if hints else ''))
    guidelines = audit.get('guidelines') if isinstance(audit.get('guidelines'), dict) else None
    if guidelines and guidelines.get('applicable'):
        classes = guidelines.get('by_coverage') or {}
        batch = '其中需求基线回答 %d 条（TBR %d 条）、进交接清单 %d 条；' % (
            len(classes['project_input']), len(guidelines.get('project_input_tbr') or ()), len(classes['handoff'])) if classes else ''
        out.append('- **共用规范**：%s，适用 %d 条：已引用 %d 条、写明不适用 %d 条、未覆盖 %d 条；%s交下游 %d 条。见“共用设计准则覆盖”。' % (
            guideline_criteria.shared_label(identity=guidelines), len(guidelines['applicable']), len(guidelines['covered']),
            len(guidelines['not_applicable']), len(guidelines['uncovered']), batch, len(guidelines['downstream'])))
    inputs_found = audit.get('operating_inputs') if isinstance(audit.get('operating_inputs'), dict) else None
    if inputs_found:
        out.append('- **工况输入**：声明了来源的 %d 项；启动计算 %d 条。见“工况输入来源”。' % (
            len(inputs_found.get('declared') or []), len(inputs_found.get('startup_calculations') or {})))
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
    delegated = ['选型“%s”' % r.get('role', '') for r in selection.get('roles') or [] if isinstance(r, dict)
                 and str((r.get('decision') or {}).get('source') or '').startswith('delegate:')]
    delegated += ['澄清 %s' % q.get('id') for q in clarifications
                  if str((q.get('answer') or {}).get('by') or '').startswith('delegate:')]
    if delegated:
        granted = (load_task(root) or {}).get('delegation') or {}
        out.append('- **任务书代答**：以下 %d 处无人当场答复，由任务书代答（%s，授权原文：%s）：%s。' % (
            len(delegated), granted.get('by', '?'), granted.get('text', '未找到'), '、'.join(delegated)))
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
        out += ['## 核心器件选型', '', '| 角色 | 位号 | 选定 | 候选数 | 理由 | 淘汰依据 | 确认来源 |', '|---|---|---|---|---|---|---|']
        for r in roles:
            chosen = [c for c in r.get('candidates') or [] if isinstance(c, dict) and c.get('status') == 'selected']
            confirmed = r.get('decision') if isinstance(r.get('decision'), dict) else {}
            out.append('| %s | %s | %s | %d | %s | %s | %s |' % (
                cell(r.get('role', '')), '、'.join(r.get('refs') or []),
                cell(chosen[0].get('mpn', '')) if chosen else '未选定', len(r.get('candidates') or []),
                cell(chosen[0].get('reason', '')) if chosen else cell(r.get('single_candidate_reason', '')),
                cell('；'.join(r.get('_basis') or [])),
                cell(' '.join(str(confirmed[k]) for k in ('source', 'locator') if text(confirmed.get(k))) or '未确认')))
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

    lesson_events = lessons.get('events')
    events_list = [e for e in lesson_events if isinstance(e, dict)] if isinstance(lesson_events, list) else []
    if events_list:
        if lessons.get('schema_version', 1) == 1:
            out += ['历史归因，尚未按 schema 2 新口径复核；不计入有证据后果统计。', '']
        out += ['## 改进记录', '', '| 来源 | 归因 | 改了什么 |', '|---|---|---|']
        for e in events_list:
            out.append('| %s | %s | %s |' % (cell(e.get('source', '')), CAUSE_WORDS.get(e.get('cause'), cell(e.get('cause', ''))),
                                            cell(e.get('change') or e.get('why_none') or '')))
        out.append('')

    if lessons.get('schema_version') == 2:
        unique_events = list({json.dumps(e, sort_keys=True, ensure_ascii=False): e for e in events_list}.values())
        observed = [e for e in unique_events if e.get('cause') == 'knowledge_missing'
                    and e.get('impact') == 'observed' and not check_knowledge_event(e, '')]
        uncertain = [e for e in unique_events if e.get('cause') == 'knowledge_missing' and e.get('impact') == 'uncertain']
        out += ['缺知识归因（按事件计数，来源不另计）：有证据后果 %d；待核归因 %d。来源可定位不证明因果成立。' % (len(observed), len(uncertain)), '']
        for label, group in (('有证据后果', observed), ('待核归因', uncertain)):
            for e in group:
                out += ['- %s：%s；问题：%s；后果/不确定原因：%s；证据：%s；待核：%s' % (
                    label, cell(e.get('source', '')), cell(e.get('problem', '')),
                    cell(e.get('consequence') if label == '有证据后果' else e.get('uncertainty', '')),
                    cell('、'.join(str(v) for v in e.get('evidence', []) if text(v))) if isinstance(e.get('evidence', []), list) else '', cell(e.get('pending', ''))), '']
        gaps = lessons.get('library_gaps') if isinstance(lessons.get('library_gaps'), list) else []
        out += ['## 资料覆盖待办', '', '共 %d 项，独立于问题事件。' % len(gaps), '',
                '| 编号 | 图页/功能块 | 状态 | 检索与不适用理由 | 来源 | 本版依据 | 拟补文件/补写位置 |',
                '|---|---|---|---|---|---|---|']
        for g in gaps:
            if isinstance(g, dict):
                fields = [cell(g.get(k, '')) for k in ('id', 'page', 'block', 'status', 'reason', 'source', 'design_basis')]
                fields.append(cell(g.get('target', '')) + ' / ' + cell(g.get('resolution', '')))
                out.append('| %s | %s / %s | %s | %s | %s | %s | %s |' % tuple(fields))
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
        severe = (derating or {}).get('severe_thresholds') or {}
        out += ['## 应力风险', '',
                '这些应力在器件额定之内，但超过了本项目降额等级的降额值：合格但有风险（应力），不挡定稿（见 stress-spec.md）。', '']
        if severe:
            out += ['超幅较大的要挂未关闭的 design 或 validation 待办（design-closure.md“应力超幅”）：项目等级比 %s 级严时，'
                    '应力超过 %s 级的降额值至少 P2；离额定的余量小于估算所需的余量（温度类 %g ℃，即共用层 G02 '
                    'est_junction_margin；其他应力取该检查的 uncertainty）为 P1。' % (
                        severe.get('loosest_level'), severe.get('loosest_level'), severe.get('junction_margin_c')), '']
        out += ['| 计算 | 位号 | 降额规则 | 应力 / 降额值 / 额定 | 改进 | 超幅待办 |', '|---|---|---|---|---|---|']
        for d in risks:
            owed = ('%s 要求 %s' % (d.get('work_item') or '缺', d['required_severity'])) if d.get('required_severity') else '—'
            out.append('| %s | %s | %s | %s / %s / %s %s | %s | %s |' % (d['calculation'], d.get('ref') or '', d['rule'], num(d.get('value')),
                                                                   num(d.get('limit')), num(d.get('rating')), d.get('unit') or '',
                                                                   cell(d.get('improvement') or ''), owed))
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
    out += render_operating_inputs(inputs_found)
    out += render_scheme_criteria(scheme)
    out += render_guidelines(guidelines)
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
