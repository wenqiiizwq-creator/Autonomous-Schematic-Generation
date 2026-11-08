#!/usr/bin/env python3
"""Audit evidence-bound design claims, not electrical physics or certification.

A record can be consistent yet INCOMPLETE. PASS means its declared design work
is closed; native checks and visual review remain separate.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from design_frontier import frontier
import guideline_criteria
import operating_inputs
import stress_check
from schematic_layout import boundary as boundary_nets, part_classes
from schematic_layout.citations import check_source


SEVERITIES = ('P0', 'P1', 'P2', 'P3')
# What happens if an open item is left undone, and when it shows; the level follows from the two.
CONSEQUENCES = ('safety', 'damage', 'function', 'margin', 'optimization')
OCCURRENCES = ('normal', 'condition', 'fault')
SEVERITY_RULE = {'safety': ('P0', 'P0', 'P0'), 'damage': ('P0', 'P0', 'P1'), 'function': ('P1', 'P1', 'P2'),
                 'margin': ('P2', 'P2', 'P3'), 'optimization': ('P3', 'P3', 'P3')}


def severity_of(row):
    """P0-P3 from consequence_class and occurrence, or None when either is missing or unknown."""
    consequence, occurrence = row.get('consequence_class'), row.get('occurrence')
    if consequence not in CONSEQUENCES or occurrence not in OCCURRENCES:
        return None
    return SEVERITY_RULE[consequence][OCCURRENCES.index(occurrence)]
OPERATORS = {'<=': lambda v, l: v <= l, '<': lambda v, l: v < l,
             '>=': lambda v, l: v >= l, '>': lambda v, l: v > l,
             # A consistency check: two records of one quantity agree (R8 C-LIFE wrote "218 ≤ 218 Wh").
             '==': lambda v, l: math.isclose(v, l, rel_tol=1e-9, abs_tol=1e-12)}
# Parts whose job is to set or clamp a voltage. Each one needs a calculation
# naming it, so a protection threshold cannot ship as prose only.
THRESHOLD_PART = re.compile(r'zener|tvs|tl431|atl431|lm4040|shunt.?ref|voltage.?ref|^power:vref', re.I)
# The same parts drawn with a generic diode or IC symbol, known by their series prefix.
THRESHOLD_SERIES = re.compile(r'^(1N47|1N52|1N53|1SMA|BZX|BZT|BZV|MMSZ|SMAJ|SMBJ|SMCJ|SMF|P6KE|P4SMA|P6SMB|PESD|TPD|ESD|'
                              r'TL431|TLV431|ATL431|AZ431|LM385|LM4040|LM4041|REF30|REF50)', re.I)


def threshold_part(c):
    """A part whose job is to set or clamp a voltage: by symbol, series prefix or a declared role."""
    return bool(THRESHOLD_PART.search(str(c.get('lib_id', '')))
                or any(THRESHOLD_SERIES.match(str(c.get(k, '')).strip()) for k in ('value', 'mpn'))
                or (c.get('fields') or {}).get('ComponentRole') == 'threshold')
WINDOW_SIDES = ('no_false_trip', 'protection')
# Where each number in a calculation comes from (parameter_version 1). A device
# parameter cites the datasheet page it was read from; one the datasheet does
# not give is "unspecified" and ties to a recorded operating-point decision.
# Version 2 adds requirement inputs and physical constants, no longer filed as models.
PARAMETER_BASES = ('guaranteed', 'typical', 'derived', 'design_choice', 'model', 'unspecified')
PARAMETER_BASES_V2 = PARAMETER_BASES + ('requirement', 'constant')
# Version 3 (R8, user 2026-10-27): each check also says where its limit comes from, so a limit ASG set itself
# ("20 J 采购资格", "60 V 筛查值") no longer reads like a rating; and every requirement is checked or says why not.
LIMIT_BASES = ('requirement', 'guaranteed', 'typical', 'standard', 'derived', 'model')
# Version 2: the conclusion follows from the inputs. A typical or unspecified device value, or an open
# vendor-data item, leaves it resting on the vendor; an engineering model or a term not calculated
# leaves it resting on ASG's own estimate; otherwise the design holds.
VENDOR_BASES, ESTIMATE_BASES = ('typical', 'unspecified'), ('model',)
SCENARIOS = ('best', 'worst', 'nominal')
OMISSION_KINDS = ('not_calculated', 'verify_by_test')
DATASHEET = re.compile(r'^datasheet:.+#p\d+$')
# Where a data gap was found (gap_version 1): a datasheet page, a review item or a user decision.
GAP_SOURCE = re.compile(r'^(datasheet:.+#p\d+|review:[^/\s]+/\S+|user:\d{4}-\d{2}-\d{2})$')
GAP_FIELDS = ('missing', 'why_external', 'calculations', 'consequence', 'questions', 'owner', 'fallback', 'action')
# gap_version 2 (R8): what kind of data each gap lacks. Tests, approvals, certification and quotes are not datasheet
# gaps but validation hand-offs; a value given only as typical, or not at all, first rules out a part that guarantees it.
GAP_KINDS = ('unspecified', 'typical_only', 'firmware', 'internal')
# A requirement question put to the user (requirement-clarifications.md) is answered in one of three ways.
DECISIONS = ('DECIDED', 'ADOPTED_PROPOSAL', 'DEFERRED')
CLARIFICATION_ID = re.compile(r'^CL-\S+$')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
# Whether the user let ASG write a decided requirement into the original requirement files.
FILE_DECISIONS = ('UPDATED', 'KEPT')
# derating_version 1 (user 2026-10-27): stresses are checked against the I/II/III column of the shared derating spec.
DERATING_RULES = Path(__file__).resolve().parent.parent / 'references' / 'shared' / 'derating-rules.json'
DERATING_SOURCE = re.compile(r'^(req:|clarification:)(\S+)$')
RATING_SOURCE = re.compile(r'^(datasheet:.+#p\d+|req:\S+|calc:\S+)$')
# A resistor whose power matters carries its power rating (user 2026-10-27: 设计时考虑功耗，除阻值和精度外还要写上功率等级，
# 作为给以后的约束). The same rule as schematic-review's passive_stress: the weakest part the written fields allow is half the
# package's commodity floor (RG1005 0.032 W), derated by the level's RES-SMD-P value (with no level, the spec's
# engineering value unset_level, in the rule library since 2026-11-02; user 2026-10-29: 删掉 2 倍，按降额规范取); a part without a footprint is judged as 0402.
# The floors and the two judgement values are the shared layer's (commodity-floors.json; G02 weakest_share,
# assumed_resistor_package), the same bytes SR's passive_stress reads (2026-11-02).
RESISTOR_FLOORS = {p: v['power_w_70c'] for p, v in guideline_criteria.commodity_floors()['chip_resistor']['packages'].items()}
WEAKEST_SHARE = guideline_criteria.engineering_value('weakest_share')
ASSUMED_PACKAGE = guideline_criteria.engineering_value('assumed_resistor_package')
RESISTOR_PACKAGE = re.compile(r'^Resistor_SMD:R_(0201|0402|0603|0805|1206|1210|2010|2512)_', re.I)
WATTS = re.compile(r'^(\d+(?:\.\d+)?)\s*(m?)W$')
SEGMENT_SPLIT = re.compile(r'[/，,；;、\s]+')


def text(value):
    return isinstance(value, str) and bool(value.strip())


def squeeze(value):
    return re.sub(r'\s+', '', str(value or ''))


# Who made a decision (整板评测 2026-11-07 A3/A6): words a runner writes when it answers in the user's place.
# A user answer or confirmation carrying any of them was not the user's (Matrix: source user:<日期>, basis eval-run:auto).
SELF_ASSIGNED = re.compile(r'eval-run|(?<![A-Za-z])auto(?![A-Za-z])|无用户|运行者|预先授权|代填', re.I)


def self_assigned(value):
    """The runner-marker words found in a decision's strings (nested dicts and lists included)."""
    if isinstance(value, str):
        return SELF_ASSIGNED.findall(value)
    items = value.values() if isinstance(value, dict) else value if isinstance(value, list) else ()
    return [w for v in items for w in self_assigned(v)]


def load_task(root):
    """The dispatching task.json copied into the delivery (workflow-handoff.md); None when absent or unreadable."""
    path = Path(root) / 'record' / 'task.json' if root else None
    try:
        data = json.loads(path.read_text(encoding='utf-8')) if path and path.is_file() else None
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


# A decision the task file delegated (workflow-handoff.md delegation): delegate:<代答人>:<日期>, adopting ASG's recommendation.
DELEGATE_SOURCE = re.compile(r'^delegate:([^:\s]+):(\d{4}-\d{2}-\d{2})$')
DELEGATE_RULES = ('adopt_recommendation',)


def check_delegate(source, scope, root):
    """(code, why) when a delegate:<by>:<date> source has no matching authorisation in record/task.json, else None."""
    m = DELEGATE_SOURCE.match(source if isinstance(source, str) else '')
    if not m:
        return 'delegate_mismatch', '代答来源要写成 delegate:<代答人>:<日期>'
    granted = (load_task(root) or {}).get('delegation')
    if not isinstance(granted, dict):
        return 'delegate_without_task', '交付目录 record/task.json 没有 delegation（代答授权）'
    if (granted.get('by'), granted.get('date')) != m.groups():
        return 'delegate_mismatch', '代答人或日期与任务书 delegation（%s:%s）不一致' % (granted.get('by'), granted.get('date'))
    if scope not in (granted.get('scope') or []):
        return 'delegate_mismatch', '任务书 delegation 的 scope 不含 %s' % scope
    if granted.get('rule') not in DELEGATE_RULES:
        return 'delegate_mismatch', '任务书 delegation 的 rule 要是 %s' % '/'.join(DELEGATE_RULES)
    return None


def audit_operating_points(record, work, refs, error, need):
    """Pin operating modes: one the datasheet does not specify needs every specified alternative ruled out."""
    points = {}
    rows = record.get('operating_points', [])
    if not isinstance(rows, list):
        error('schema', 'operating_points must be a list')
        return points
    for row in rows:
        if not isinstance(row, dict) or not text(row.get('id')):
            error('schema', 'operating_points entry requires a nonempty string id')
            continue
        key = row['id']
        if key in points:
            error('duplicate_id', 'operating_points:' + key)
        points[key] = row
        if not isinstance(row.get('refs'), list) or not row['refs'] or any(r not in refs for r in row['refs']):
            error('operating_point_refs', key)
        if not isinstance(row.get('pins'), list) or not row['pins'] or not all(text(p) for p in row['pins']):
            error('schema', key + ':pins must be a nonempty string list')
        if not text(row.get('mode')) or not isinstance(row.get('specified'), bool):
            error('schema', key + ':needs mode and specified (true/false)')
            continue
        # specified: where the datasheet specifies this mode; otherwise where it was looked for and is absent.
        if not (isinstance(row.get('source'), str) and DATASHEET.match(row['source']) and text(row.get('locator'))):
            error('operating_point_source', key)
        if row['specified']:
            continue
        alternatives = row.get('alternatives')
        if not isinstance(alternatives, list) or not alternatives:
            error('unspecified_operation_without_alternatives', key)
            alternatives = []
        for i, alt in enumerate(alternatives):
            if (not isinstance(alt, dict) or not text(alt.get('approach')) or not text(alt.get('reason'))
                    or not isinstance(alt.get('specified'), bool) or not isinstance(alt.get('feasible'), bool)):
                error('schema', key + ':alternatives[%d] needs approach, specified, feasible and reason' % i)
            elif alt['specified'] and alt['feasible']:
                error('unspecified_operation_with_specified_alternative', key + ':' + alt['approach'])
        item = work.get(row.get('work_item'))
        if not item or item.get('stage') != 'external':
            error('unspecified_operation_without_vendor_item', key)
        need('unspecified_operation', key)
    return points


def holds(c, limit_key='limit'):
    """Whether a well-formed check meets its limit (or its rating); None when it cannot be compared.
    Against a negative rating (an off-state gate voltage of -10 V) the magnitudes are compared (derating-rules.md R8)."""
    if not (isinstance(c, dict) and c.get('operator') in OPERATORS and finite(c.get('value')) and finite(c.get(limit_key))):
        return None
    if finite(c.get('rating')) and c['rating'] < 0:
        return OPERATORS[c['operator']](abs(c['value']), abs(c[limit_key]))
    return OPERATORS[c['operator']](c['value'], c[limit_key])


def derating_deviation(c):
    """A derating check beyond its derated limit but within the part's rating: a pass with a stress risk (stress-spec.md)."""
    return bool(text(c.get('derating_rule')) and holds(c) is False and holds(c, 'rating') is True)


def failing_checks(row):
    """The checks of a calculation that miss their limit, a derating deviation within its rating aside."""
    return [c for c in row.get('checks') or [] if isinstance(c, dict) and holds(c) is False and not derating_deviation(c)]


def estimate_margin(c, uncertainty):
    """(margin, reference) of a check that holds, as a share of what it is compared with, when the margin is smaller
    than the uncertainty of the engineering estimates it rests on; otherwise None. A derating check's margin is taken to
    its rating, its derated limit being the one allowance already (derating-rules.md R12)."""
    if not uncertainty or holds(c) is not True or c.get('operator') == '==':
        return None
    key = 'rating' if text(c.get('derating_rule')) else 'limit'
    if key == 'rating' and (not finite(c.get('rating')) or c['operator'] not in ('<=', '<')):
        return None
    reference = c[key]
    if not reference:
        return None
    value = abs(c['value']) if key == 'rating' else c['value']
    margin = ((abs(reference) - value) if key == 'rating' else
              (reference - value) if c['operator'] in ('<=', '<') else (value - reference)) / abs(reference)
    return (margin, key) if margin < uncertainty else None


def calculation_basis(row, vendor_items=(), deferred_items=()):
    """(conclusion, rests_on, reasons) a parameter_version 2 calculation follows to.

    ``vendor_items`` are the open external work items whose ``calculations`` name this one;
    ``deferred_items`` the open requirement work items (requirements the user deferred) that do.
    A stress over the derated value but within the rating passes with a stress risk; it neither fails nor conditions.
    """
    checks = [c for c in row.get('checks') or [] if isinstance(c, dict)]
    failing = [c.get('name') for c in failing_checks(row)]
    if failing:
        return 'failed', None, failing
    params = [p for p in row.get('parameters') or [] if isinstance(p, dict)]
    vendor =[p.get('name') for p in params if p.get('basis') in VENDOR_BASES] + ['待办 %s' % w for w in vendor_items]
    vendor += ['门槛 %s' % c.get('name') for c in checks if c.get('limit_basis') == 'typical']
    estimate = [p.get('name') for p in params if p.get('basis') in ESTIMATE_BASES]
    estimate += ['门槛 %s' % c.get('name') for c in checks if c.get('limit_basis') == 'model']
    estimate += ['没算：%s' % o.get('term') for o in row.get('omitted_terms') or []
                 if isinstance(o, dict) and o.get('kind') == 'not_calculated']
    deferred = ['待办 %s' % w for w in deferred_items]
    if vendor:
        return 'conditional', 'vendor_data', vendor + deferred + estimate
    if deferred:
        return 'conditional', 'user_deferred', deferred + estimate
    if estimate:
        return 'conditional', 'estimate', estimate
    return 'supported', None, []


def vendor_items_of(work, stage='external'):
    """{calculation id: [open work item ids of this stage naming it]}; external by default."""
    found = {}
    for key, row in work.items():
        if row.get('stage') == stage and row.get('status') != 'closed' and isinstance(row.get('calculations'), list):
            for cid in row['calculations']:
                found.setdefault(cid, []).append(key)
    return found


def audit_clarifications(record, requirements, work, error, root=None):
    """Requirement questions put to the user: each one answered, the answer written back as a requirement,
    or, when the user deferred it, carried by an open requirement work item on the proposed text."""
    rows = record.get('clarifications', [])
    if not isinstance(rows, list):
        error('schema', 'clarifications must be a list')
        return {}
    found = {}
    for row in rows:
        if not isinstance(row, dict) or not (isinstance(row.get('id'), str) and CLARIFICATION_ID.match(row['id'])):
            error('schema', 'clarifications entry requires an id CL-<name>')
            continue
        key = row['id']
        if key in found:
            error('duplicate_id', 'clarifications:' + key)
        found[key] = row
        for field in ('found_in', 'question', 'requirement_text', 'proposed_requirement'):
            if not text(row.get(field)):
                error('schema', key + ':needs ' + field)
        ids = row.get('requirement_ids')
        if not isinstance(ids, list) or not all(isinstance(r, str) for r in ids):
            error('schema', key + ':requirement_ids must be a string list')
            ids = []
        for rid in ids:
            if rid not in requirements:
                error('unknown_requirement_ids', key + ':' + rid)
        answer = row.get('answer')
        if answer is None:
            error('clarification_unanswered', key)
            continue
        source = answer.get('source') if isinstance(answer, dict) else None
        if (not isinstance(answer, dict) or answer.get('decision') not in DECISIONS
                or not text(answer.get('text')) or not text(answer.get('by'))
                or not (isinstance(answer.get('date'), str) and DATE.match(answer['date']))
                or not (isinstance(source, dict) and text(source.get('source')) and text(source.get('locator')))):
            error('schema', key + ':answer needs decision (%s), text, by, date YYYY-MM-DD and source {source, locator}'
                  % '/'.join(DECISIONS))
            continue
        if answer['by'].startswith('delegate:'):
            # Delegated by the task file: the answer adopts ASG's proposal (rule adopt_recommendation).
            found_problem = check_delegate(answer['by'], 'clarification', root)
            if found_problem:
                error(found_problem[0], '%s：%s' % (key, found_problem[1]))
            elif answer['decision'] != 'ADOPTED_PROPOSAL':
                error('delegate_mismatch', '%s：任务书代答只能采纳建议条文（ADOPTED_PROPOSAL）' % key)
            elif source['source'].strip() != '任务书':
                error('delegate_mismatch', '%s：代答的 source 要写 {source: 任务书, locator: <任务 id> delegation}' % key)
            marks = []
        else:
            marks = self_assigned([answer['by'], source])
        if marks:
            error('decision_self_assigned', '%s：答复人或来源写的是运行者自拟（%s），不是用户的答复；'
                  '无人当场答复时只能用任务书里的答复' % (key, '、'.join(sorted(set(marks)))))
        if source['source'].strip() == '任务书' and not answer['by'].startswith('delegate:'):
            task = load_task(root)
            given = next((a for a in (task or {}).get('clarification_answers') or []
                          if isinstance(a, dict) and a.get('id') == key), None)
            if given is None:
                error('delegate_without_task', '%s：来源写任务书，但交付目录 record/task.json 没有这项 clarification_answers' % key)
            elif any(given.get(f) != answer.get(f) for f in ('decision', 'text', 'by', 'date')):
                error('delegate_mismatch', '%s：答复与任务书 clarification_answers 不一致（decision/text/by/date）' % key)
        if answer['decision'] == 'ADOPTED_PROPOSAL' and answer['text'] != row.get('proposed_requirement'):
            error('adopted_text_differs', key)
        if answer['decision'] != 'DEFERRED':
            merged = answer.get('merged_into')
            if merged is not None:
                # Calibration board #8 (2026-11-02): an answer folded into an existing requirement is cited there, not copied
                # as a duplicate requirement; the requirement carries the answer's words (or the quoted part it became).
                target = requirements.get(merged) if isinstance(merged, str) else None
                quote = answer.get('merged_quote') if text(answer.get('merged_quote')) else answer['text']
                if (target is None or key not in (target.get('clarifications') or [])
                        or squeeze(quote) not in squeeze(target.get('text')) or (quote != answer['text']
                        and not set(re.findall(r'\d+(?:\.\d+)?', answer['text'])) <= set(re.findall(r'\d+(?:\.\d+)?', quote)))):
                    error('clarification_not_written_back', '%s：merged_into 的需求要在 clarifications 里列它，'
                          '需求文字含答复（或 merged_quote 引的那段，答复里的数都在其中）' % key)
            elif requirements.get(key, {}).get('text') != answer['text']:
                error('clarification_not_written_back', key)
            files = answer.get('requirement_files')
            if not isinstance(files, dict) or files.get('decision') not in FILE_DECISIONS:
                error('requirement_files_not_asked', key)
            elif files['decision'] == 'UPDATED' and not (
                    isinstance(files.get('files'), list) and files['files'] and all(text(f) for f in files['files'])):
                error('requirement_files_without_files', key)
            continue
        if not any(w.get('stage') == 'requirement' and w.get('status') == 'open' and w.get('clarification') == key
                   for w in work.values()):
            error('deferred_without_requirement_item', key)
        for rid in ids:
            if requirements.get(rid, {}).get('status') == 'design_supported':
                error('deferred_requirement_claimed_supported', key + ':' + rid)
    return found


def audit_omissions(key, row, work, error):
    """Version 2 omitted terms: a term not calculated is open design work, or open vendor data it waits for;
    one only a test can settle is handed off."""
    omitted = row.get('omitted_terms', [])
    if not isinstance(omitted, list):
        error('schema', key + ':omitted_terms must be a list')
        return []
    kinds = []
    for i, o in enumerate(omitted):
        if not isinstance(o, dict) or not text(o.get('term')) or o.get('kind') not in OMISSION_KINDS:
            error('schema', key + ':omitted_terms[%d] needs term and kind (%s)' % (i, '/'.join(OMISSION_KINDS)))
            continue
        kinds.append(o['kind'])
        item = work.get(o.get('work_item'), {})
        if o['kind'] == 'verify_by_test' and not (item.get('stage') == 'validation' and item.get('status') == 'handoff'):
            error('verify_by_test_without_validation_handoff', key + ':' + o['term'])
        if o['kind'] == 'not_calculated' and not (item.get('stage') in ('design', 'external') and item.get('status') == 'open'):
            error('not_calculated_without_design_item', key + ':' + o['term'])
    return kinds


def audit_parameters(key, row, refs, points, calculations, error, version=1, requirements=()):
    params = row.get('parameters')
    if not isinstance(params, list) or not params:
        error('missing_parameters', key)
        return
    for i, p in enumerate(params):
        where = key + ':parameters[%d]' % i
        if not isinstance(p, dict) or not text(p.get('name')) or not isinstance(p.get('unit'), str):
            error('schema', where + ' needs name and unit')
            continue
        where = key + ':' + p['name']
        basis = p.get('basis')
        bases = PARAMETER_BASES_V2 if version >= 2 else PARAMETER_BASES
        if basis not in bases:
            error('schema', where + ':basis must be one of ' + '/'.join(bases))
            continue
        if basis != 'unspecified' and not finite(p.get('value')):
            error('schema', where + ':value must be a finite number')
        if basis in ('guaranteed', 'typical', 'design_choice', 'unspecified') and p.get('ref') not in refs:
            error('parameter_ref', where)
        cited = isinstance(p.get('source'), str) and DATASHEET.match(p['source']) and text(p.get('locator'))
        if basis in ('guaranteed', 'typical', 'unspecified') and not cited:
            error('parameter_without_datasheet_location', where)
        if basis == 'derived':
            source = p.get('source')
            if not text(p.get('derivation')) or not (
                    (isinstance(source, str) and DATASHEET.match(source)) or
                    (isinstance(source, str) and source.startswith('calc:') and source[5:] in calculations)):
                error('derived_parameter_without_basis', where)
        if basis in ('model', 'constant') and not text(p.get('reason')):
            error(basis + '_parameter_without_reason', where)
        if basis == 'requirement' and not (isinstance(p.get('source'), str) and p['source'].startswith('req:')
                                           and p['source'][4:] in requirements):
            error('requirement_parameter_without_requirement', where)
        if basis == 'unspecified':
            point = points.get(p.get('operating_point'))
            if not point or point.get('specified') is not False:
                error('unspecified_parameter_without_operating_point', where)
        if version == 1 and basis in ('typical', 'unspecified') and row.get('conclusion') == 'supported':
            error('supported_with_unguaranteed_parameter', where)


def shown(value, words):
    from schematic_layout.citations import _shown
    return _shown(value, str(words or ''))


def named_limits(c):
    """Numbers the check's name gives on its limit side (after the last 对 or vs) in the check's unit: calibration
    board #23 (2026-11-02) named a check 100 kbit/s and set its limit to 200 kbit/s."""
    name, unit = str(c.get('name') or ''), str(c.get('unit') or '').strip()
    parts = re.split(r'对|\bvs\.?\b', name)
    if len(parts) < 2 or not unit or re.search(r'[×*÷+−%]|\d\s*-\s*\d', parts[-1]):
        return []   # a limit written as arithmetic (1 W×0.75, 120 Ω−3 %) is checked by its reason, not read here
    return [float(n) for n in re.findall(r'(\d+(?:\.\d+)?)\s*' + re.escape(unit) + r'(?![A-Za-z])', parts[-1])]


def audit_limits(key, row, requirements, calculations, error):
    """Version 3: each check names where its limit comes from."""
    for i, c in enumerate(row.get('checks') or []):
        if not isinstance(c, dict):
            continue
        where = '%s:%s' % (key, c.get('name') if text(c.get('name')) else 'checks[%d]' % i)
        basis, source = c.get('limit_basis'), c.get('limit_source')
        source = source if isinstance(source, str) else ''
        if basis not in LIMIT_BASES:
            error('check_limit_without_basis', where)
        elif not {'model': text(c.get('limit_reason')),
                  'requirement': source.startswith('req:') and source[4:] in requirements,
                  'guaranteed': bool(DATASHEET.match(source)), 'typical': bool(DATASHEET.match(source)),
                  'standard': source.startswith('standard:') and text(source[9:]),
                  'derived': bool(DATASHEET.match(source)) or (source.startswith('calc:') and source[5:] in calculations)}[basis]:
            error('check_limit_without_source', where)
        elif basis == 'model' and finite(c.get('limit')) and not shown(c['limit'], c['limit_reason']):
            error('model_limit_not_in_reason', '%s：自定门槛 %g %s 要在 limit_reason 里写出这个数和它的依据' % (
                where, c['limit'], c.get('unit') or ''))
        named = named_limits(c)
        if named and finite(c.get('limit')) and not any(math.isclose(n, c['limit'], rel_tol=1e-6) for n in named):
            error('check_name_contradicts_limit', '%s：检查名里门槛一侧写的是 %s，limit 是 %g' % (
                where, '、'.join('%g' % n for n in named), c['limit']))


def audit_gap_kinds(key, row, error):
    """gap_version 2: each missing entry is a kind of datasheet or firmware gap; an unguaranteed value rules out the
    alternatives that would guarantee it."""
    for i, m in enumerate(row.get('missing') if isinstance(row.get('missing'), list) else []):
        where = '%s:missing[%d]' % (key, i)
        kind = m.get('kind') if isinstance(m, dict) else None
        if kind is None:
            error('gap_kind_missing', where)
            continue
        if kind not in GAP_KINDS:
            error('gap_not_external', '%s:%s（试验、认证、承认、报价交 validation）' % (where, kind))
            continue
        if kind not in ('unspecified', 'typical_only'):
            continue
        alternatives = m.get('alternatives')
        if not isinstance(alternatives, list) or not alternatives:
            error('gap_without_alternatives', where)
            continue
        for j, alt in enumerate(alternatives):
            if (not isinstance(alt, dict) or not text(alt.get('approach')) or not text(alt.get('reason'))
                    or not isinstance(alt.get('specified'), bool) or not isinstance(alt.get('feasible'), bool)):
                error('schema', where + ':alternatives[%d] needs approach, specified, feasible and reason' % j)
            elif alt['specified'] and alt['feasible']:
                error('gap_alternative_feasible', where + ':' + alt['approach'])


def audit_gaps(work, calculations, error, version=1):
    """Open external items say which data is missing, why only the owner has it and what to ask."""
    fallbacks, reasons = {}, {}
    for key, row in work.items():
        if row.get('stage') != 'external' or row.get('status') == 'closed':
            continue
        for field in GAP_FIELDS:
            value = row.get(field)
            # A behaviour or qualification gap that no calculation rests on says so instead of linking one.
            if field == 'calculations' and value == [] and text(row.get('no_calculation_reason')):
                continue
            if not (text(value) or (isinstance(value, list) and value)):
                error('gap_missing_fields', key + ':' + field)
        for i, m in enumerate(row.get('missing') if isinstance(row.get('missing'), list) else []):
            if not isinstance(m, dict) or not all(text(m.get(f)) for f in ('source', 'given', 'needed')):
                error('schema', key + ':missing[%d] needs source, given and needed' % i)
            elif not GAP_SOURCE.match(m['source']):
                error('gap_bad_source', key + ':missing[%d]' % i)
        for field in ('questions', 'calculations'):
            if isinstance(row.get(field), list) and not all(text(x) for x in row[field]):
                error('schema', key + ':' + field + ' must be a nonempty string list')
        for cid in row.get('calculations') if isinstance(row.get('calculations'), list) else []:
            if calculations.get(cid, {}).get('conclusion') != 'conditional':
                error('gap_unlinked_calculation', key + ':' + str(cid))
        if text(row.get('fallback')):
            fallbacks.setdefault(' '.join(row['fallback'].split()), []).append(key)
        if version == 2:
            audit_gap_kinds(key, row, error)
            if text(row.get('why_external')):
                reasons.setdefault(' '.join(row['why_external'].split()), []).append(key)
    for keys in fallbacks.values():
        if len(keys) > 1:
            error('gap_generic_fallback', '、'.join(keys))
    for keys in reasons.values():        # R8: one sentence for all seven items says nothing about any of them
        if len(keys) > 1:
            error('gap_reason_repeated', '、'.join(keys))


def load_derating(path=DERATING_RULES):
    """The shared derating spec: {rule id: rule} plus the spec itself."""
    spec = json.loads(Path(path).read_text(encoding='utf-8'))
    return {r['id']: r for r in spec['rules']}, spec


def written_power(comp):
    """The power rating a resistor's value or a field writes as a segment of its own (620/1%/0.125W, 250mW), or None."""
    contract = comp.get('performance_contract')
    if isinstance(contract, dict):
        powers = [r['value'] / (1000 if r['unit'] == 'mW' else 1)
                  for r in contract.get('requirements', []) if isinstance(r, dict)
                  and r.get('parameter') in ('power', 'rated_power', 'continuous_power')
                  and r.get('op') == 'ge' and r.get('unit') in ('W', 'mW')
                  and isinstance(r.get('value'), (int, float)) and not isinstance(r['value'], bool)
                  and math.isfinite(r['value']) and r['value'] > 0]
        if len(powers) == 1:
            return powers[0]
    found = set()
    for value in [comp.get('value')] + list(part_classes.fields(comp).values()):
        for segment in SEGMENT_SPLIT.split(str(value or '')):
            m = WATTS.match(segment)
            if m:
                found.add(float(m.group(1)) / (1000 if m.group(2) else 1))
    return found.pop() if len(found) == 1 else None


def power_rating_needed(comp, watts, share):
    """The minimum power rating a resistor must write (worst power ÷ the level's RES-SMD-P value), when its power
    matters and it writes none; otherwise None."""
    m = RESISTOR_PACKAGE.match(str(comp.get('footprint') or ''))
    floor = RESISTOR_FLOORS[m.group(1) if m else ASSUMED_PACKAGE]
    if written_power(comp) is not None or watts <= floor * WEAKEST_SHARE * share:
        return None
    return watts / share


# A check against a guaranteed rating that names no rule (stress-spec.md, 2026-10-28, user: 按推荐都做): the quantity is
# the unit's; which rule fits and how the stress is judged are the shared stress_check (same code as SR's derating.implied_ratio).
UNIT_DIMENSIONS = (('current', re.compile(r'^[mµu]?A$')), ('voltage', re.compile(r'^[mk]?V$')), ('power', re.compile(r'^m?W$')))


def implied_rule(c, comp, kind, rules, level):
    """(rule, derated) for a check of a stress against the part's guaranteed rating that names no rule, when exactly one
    steady or worst-case ratio rule fits the part's kind and the unit's quantity and the stress is over the derated
    value; else None. R8 (2026-10-28): VBUS 5 A against the connector's 5 A rating passed with zero margin."""
    if not (level and kind and not text(c.get('derating_rule')) and c.get('limit_basis') == 'guaranteed'
            and c.get('operator') in ('<=', '<') and finite(c.get('value')) and finite(c.get('limit')) and c['limit'] > 0):
        return None
    dimension = next((d for d, pattern in UNIT_DIMENSIONS if pattern.match(str(c.get('unit') or '').strip())), None)
    identity = ' '.join(str(comp.get(k) or '') for k in ('mpn', 'value', 'lib_id'))
    fits = stress_check.fit_rules(rules.values(), (kind,), dimension, identity)
    if len(fits) != 1:
        return None
    judged = stress_check.verdict(c['value'], c['limit'], fits[0], level)
    return (fits[0], judged[1]) if judged and judged[0] != stress_check.OK else None


# A stress risk that is more than a deviation (Matrix R2, 2026-11-04: LM70880 estimated at 146 °C against 95 °C at level II and
# 150 °C absolute, reported only as a pass with risk). Both thresholds come from the shared layer, none is set here:
# for a project below the loosest level, beyond the loosest level's derated value (no level of the spec allows it); or closer to the rating than the margin
# an estimate needs (temperatures: G02 est_junction_margin; other stresses: the check's own uncertainty).
TEMPERATURE_MEASURES = ('max_c', 'tj_percent', 'margin_c')
JUNCTION_MARGIN = guideline_criteria.engineering_value('est_junction_margin')


def severe_stress(c, rule, rating, level):
    """(required severity, detail) for a stress risk that needs an unclosed design or validation work item, else None.
    P1 when the stress is closer to the rating than the margin an estimate needs, P2 when it is only beyond every level."""
    loosest = stress_check.LEVELS[-1]
    widest = stress_check.derated_limit(rule, loosest, rating) if level != loosest else None
    beyond = widest is not None and holds({'value': c.get('value'), 'operator': c.get('operator'), 'limit': widest,
                                           'rating': rating}) is False
    margin = need = None
    if finite(rating) and finite(c.get('value')) and c.get('operator') in ('<=', '<'):
        if rule['measure'] in TEMPERATURE_MEASURES:
            margin, need = rating - c['value'], JUNCTION_MARGIN
        elif finite(c.get('uncertainty')) and c['uncertainty'] > 0 and rating:
            margin, need = (abs(rating) - abs(c['value'])) / abs(rating), c['uncertainty']
    short = margin is not None and margin < need
    if not (beyond or short):
        return None
    return ('P1' if short else 'P2'), {'loosest_level': loosest, 'loosest_limit': widest, 'beyond_levels': beyond,
                                       'margin_to_rating': margin, 'margin_needed': need}


def audit_severe_stress(where, c, risk, rule, rating, level, work, error):
    """A severe stress risk names an unclosed design or validation work item (`work_item`) at least as urgent as it needs."""
    found = severe_stress(c, rule, rating, level)
    if found is None:
        return
    required, detail = found
    risk.update(detail, required_severity=required, work_item=c.get('work_item'))
    why = ('超过最宽一级（%s 级）的降额值 %g' % (detail['loosest_level'], detail['loosest_limit'])) if detail['beyond_levels'] else ''
    if detail['margin_to_rating'] is not None and detail['margin_to_rating'] < detail['margin_needed']:
        why += ('，' if why else '') + '距额定 %.3g 小于要求的 %.3g' % (detail['margin_to_rating'], detail['margin_needed'])
    item = work.get(c.get('work_item')) if isinstance(c.get('work_item'), str) else None
    if item is None:
        error('severe_stress_without_work_item', '%s：%s，不只是降额偏离；写 work_item 指向一件未关闭的 design 或 validation 待办'
              '（不做的后果定级至少 %s）' % (where, why, required))
        return
    if item.get('stage') not in ('design', 'validation') or item.get('status') == 'closed':
        error('severe_stress_work_item_not_open', '%s：%s 要是未关闭的 design 或 validation 待办' % (where, c['work_item']))
    level = severity_of(item)
    if level is None or SEVERITIES.index(level) > SEVERITIES.index(required):
        error('severe_stress_work_item_severity', '%s：%s 按 consequence_class/occurrence 定级 %s，这处应力要求至少 %s' % (
            where, c['work_item'], level or '未定', required))


def audit_derating(record, intent, calculations, requirements, clarifications, error, loaded=None, work=None):
    """derating_version 1, judged by stress-spec.md (user 2026-10-27): the level and where it was decided; each check that
    names a rule uses that rule's limit for the level; over the derated value but within the rating is a stress risk with
    an improvement; only the stresses written are checked, and a stress compared with a rating that names no rule while
    the spec has rules for that kind is a hint."""
    rules, spec = loaded or load_derating()
    info = record.get('derating') if isinstance(record.get('derating'), dict) else {}
    level = info.get('level')
    if level not in stress_check.LEVELS:
        error('derating_level_missing', 'derating.level must be I, II or III')
        level = None
    m = DERATING_SOURCE.match(info.get('source') or '')
    if not m or (m.group(1) == 'req:' and m.group(2) not in requirements) or (
            m.group(1) == 'clarification:' and ((clarifications.get(m.group(2)) or {}).get('answer') or {}).get('decision') != 'DEFERRED'):
        error('derating_level_without_source', 'derating.source: req:<需求编号>，或 clarification:<用户暂缓的需求澄清>')
    comps = {c['ref']: c for c in intent.get('components') or []}
    ruled = {k for r in rules.values() for k in r['kinds']}
    share_level = level or guideline_criteria.engineering_value('unset_level')
    share = rules['RES-SMD-P']['values'][share_level]
    risks, hints = [], []
    for key, row in calculations.items():
        for c in row.get('checks') or []:
            if not isinstance(c, dict):
                continue
            where, ref = '%s:%s' % (key, c.get('name')), c.get('ref')
            kind = part_classes.kind_of(comps[ref])[0] if ref in comps else None
            if kind == 'resistor' and c.get('unit') in ('W', 'mW') and finite(c.get('value')):
                need = power_rating_needed(comps[ref], abs(c['value']) / (1000 if c['unit'] == 'mW' else 1), share)
                if need is not None:
                    error('resistor_power_rating_missing', '%s：%s 的功耗要考虑，值写成 阻值/公差/额定功率（如 620/1%%/0.125W），'
                          '额定功率取 ≥ %.4g W 的标准档（应力 ÷ %s 级 RES-SMD-P %g%s）' % (
                              where, ref, need, share_level, share, '' if level else '，降额等级未定按 %s 级' % share_level))
            if not text(c.get('derating_rule')):
                implied = implied_rule(c, comps.get(ref) or {}, kind, rules, level)
                if implied:
                    rule, derated = implied
                    risks.append({'calculation': key, 'check': c.get('name'), 'ref': ref, 'rule': rule['id'],
                                  'value': c.get('value'), 'limit': derated, 'rating': c.get('limit'),
                                  'unit': c.get('unit'), 'improvement': c.get('improvement')})
                    audit_severe_stress(where, c, risks[-1], rule, c.get('limit'), level, work or {}, error)
                    if not text(c.get('improvement')):
                        error('stress_risk_without_improvement', '%s：应力超过 %s 级 %s 的降额值 %g %s，写 improvement'
                              '（换额定更高的件或降低应力）' % (where, level, rule['id'], derated, c.get('unit')))
                elif c.get('rating') is not None and kind in ruled:
                    hints.append('derating_rule_available %s：%s 是%s，降额规范有这类器件的规则' % (where, ref, kind))
                continue
            rule = rules.get(c['derating_rule'])
            if rule is None:
                error('derating_rule_unknown', where + ':' + c['derating_rule'])
                continue
            if not set(rule['kinds']) <= {'pcb', 'wire', 'enclosure'} and kind not in rule['kinds']:
                error('derating_rule_kind', '%s: %s 是%s，规则 %s 用于 %s' % (where, ref, kind, rule['id'], '/'.join(rule['kinds'])))
            if c.get('limit_basis') != 'standard' or c.get('limit_source') != 'standard:derating-rules#' + rule['id']:
                error('derating_limit_source', where + '：limit_basis 写 standard，limit_source 写 standard:derating-rules#' + rule['id'])
            if c.get('rating') is not None and not (finite(c['rating']) and RATING_SOURCE.match(str(c.get('rating_source') or ''))):
                error('derating_rating_without_source', where)
            expected = stress_check.derated_limit(rule, level, c.get('rating')) if level else None
            if rule['measure'] in ('ratio', 'pulse_ratio', 'min_ratio', 'margin_c', 'tj_percent') and not finite(c.get('rating')):
                error('derating_rating_missing', where)
            elif expected is not None and finite(c.get('limit')) and not math.isclose(
                    abs(c['limit']) if finite(c.get('rating')) and c['rating'] < 0 else c['limit'], expected, rel_tol=1e-6, abs_tol=1e-9):
                error('derating_limit_mismatch', '%s：写的 %g，%s 级 %s 是 %g' % (where, c['limit'], level, rule['id'], expected))
            if derating_deviation(c):
                risks.append({'calculation': key, 'check': c.get('name'), 'ref': ref, 'rule': rule['id'],
                              'value': c.get('value'), 'limit': c.get('limit'), 'rating': c.get('rating'),
                              'unit': c.get('unit'), 'improvement': c.get('improvement')})
                audit_severe_stress(where, c, risks[-1], rule, c.get('rating'), level, work or {}, error)
                if not text(c.get('improvement')):
                    error('stress_risk_without_improvement', where + '：写 improvement（换额定更高的件或降低应力）')
    return {'level': level, 'source': info.get('source'), 'stress_risks': risks, 'hints': hints,
            'severe_thresholds': {'loosest_level': stress_check.LEVELS[-1], 'junction_margin_c': JUNCTION_MARGIN,
                                  'other_margin': 'uncertainty'}}


def audit_operating_inputs(record, calculations, requirements, clarifications, work, intent, error):
    """references/design-closure.md 工况输入: the hard layer and the review list (operating_inputs.py)."""
    found = operating_inputs.audit_roles(calculations, requirements, clarifications, work, intent, error, shown)
    operating_inputs.audit_hidden_literals(calculations, error)
    library = guideline_criteria.load()
    scope = record.get('guideline_scope') if isinstance(record.get('guideline_scope'), dict) else {}
    applicable = []
    if all(isinstance(scope.get(k), list) for k in ('circuit_types', 'device_kinds')):
        applicable = [r['id'] if isinstance(r, dict) else r for r in guideline_criteria.select(
            library, scope.get('baseline') or library['default_baseline'], scope['circuit_types'], scope['device_kinds'])]
    found['checklist'] = operating_inputs.checklist(calculations, requirements, library, applicable,
                                                    set(found['hot_parts']), found['startup_calculations'])
    return found


def audit_citations(record, calculations, work, extra, error):
    """Each datasheet citation names a file in the library and a page it has; cited values are looked up."""
    cited = [('operating_points:%s' % r.get('id'), r.get('source'), ())
             for r in record.get('operating_points') or [] if isinstance(r, dict)]
    cited += [('%s:%s' % (key, p.get('name')), p.get('source'), (p.get('value'),) if p.get('basis') in ('guaranteed', 'typical') else ())
              for key, row in calculations.items() for p in row.get('parameters') or [] if isinstance(p, dict)]
    cited += [('%s:missing[%d]' % (key, i), m.get('source'), ())
              for key, row in work.items() for i, m in enumerate(row.get('missing') or []) if isinstance(m, dict)]
    cited += [('%s:%s 的门槛' % (key, c.get('name')), c.get('limit_source'),
               (c.get('limit'),) if c.get('limit_basis') in ('guaranteed', 'typical') else ())
              for key, row in calculations.items() for c in row.get('checks') or [] if isinstance(c, dict)]
    cited += [('%s:%s 的额定' % (key, c.get('name')), c.get('rating_source'), (c.get('rating'),))
              for key, row in calculations.items() for c in row.get('checks') or []
              if isinstance(c, dict) and str(c.get('rating_source') or '').startswith('datasheet:')]
    cited += [('pin_dispositions:%s' % r.get('pin'), r.get('source'), ())
              for r in record.get('pin_dispositions') or [] if isinstance(r, dict)]
    cited += [('net_voltages:%s' % r.get('net'), r.get('source'), ())
              for r in record.get('net_voltages') or [] if isinstance(r, dict) and str(r.get('source') or '').startswith('datasheet:')]
    summary = {'checked': 0, 'not_checked': [], 'review': []}
    for where, source, values in cited:
        result = check_source(source, values, extra)
        if result is None:
            continue
        summary['checked'] += 1
        if result['status'] == 'FAIL':
            error('citation_not_in_library' if result.get('not_library') else 'citation_wrong', where + ': ' + result['reason'])
        elif result['reason'] and result['reason'] not in summary['not_checked']:   # not checked, or values not checked
            summary['not_checked'].append(result['reason'])
        if result['unshown']:
            summary['review'].append({'item': where, 'source': source, 'values': result['unshown']})
    return summary


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(p, root, inputs):
    """Evidence lives under the artifact root, or in a declared input (requirements, datasheets)."""
    path = (root / p).resolve()
    if path.is_relative_to(root) and path.is_file():
        return path
    for base in inputs or ():
        base = Path(base).resolve()
        for candidate in ((base / p, base / Path(p).name) if base.is_dir() else (base,)):
            if candidate.is_file() and candidate.name == Path(p).name:
                return candidate
    return None


def audit_calculation_v2(key, row, work, vendor_items, deferred_items, derived, error, need):
    """The written conclusion, rests_on and coverage must be the ones the record follows to."""
    kinds = audit_omissions(key, row, work, error)
    assumptions = row.get('assumptions', [])
    if not isinstance(assumptions, list) or any(not isinstance(x, str) for x in assumptions):
        error('schema', key + ':assumptions must be a string list')
    checks = row.get('checks')
    if not isinstance(checks, list) or not checks:
        error('missing_checks', key)
        checks = []
    sides = set()
    for i, c in enumerate(checks):
        where = key + ':checks[' + str(i) + ']'
        if (not isinstance(c, dict) or not isinstance(c.get('name'), str) or not c['name'].strip()
                or not finite(c.get('value')) or not finite(c.get('limit'))
                or c.get('operator') not in OPERATORS or not isinstance(c.get('unit'), str)):
            error('schema', where + ' needs name, finite value/limit, operator (<=, <, >=, >, ==) and unit')
            continue
        if c.get('side') is not None:
            if c['side'] not in WINDOW_SIDES:
                error('schema', where + ':side must be no_false_trip or protection')
            sides.add(c['side'])
        if c.get('scenario') is not None and c['scenario'] not in SCENARIOS:
            error('schema', where + ':scenario must be best, worst or nominal')
    if row.get('kind') == 'threshold':
        for side in WINDOW_SIDES:
            if side not in sides:
                error('threshold_window_incomplete', key + ':' + side)
    elif row.get('kind') is not None:
        error('schema', key + ':kind must be threshold when present')
    contributors = row.get('contributors')
    if contributors is not None and (not isinstance(contributors, list) or not all(
            isinstance(t, dict) and text(t.get('name')) and finite(t.get('value')) and isinstance(t.get('unit'), str)
            for t in contributors)):
        error('schema', key + ':contributors is a list of {name, value, unit}')
    # R10 ENERGY: even the favourable end of the loss ranges missed the target, so no datasheet can close it; the work
    # item proposes a design change (user 2026-10-28: 先改前四条), which is the user's to approve.
    if any(c.get('scenario') == 'best' for c in failing_checks(row)) and not any(
            w.get('stage') == 'design' and w.get('status') == 'open' and key in (w.get('calculations') or [])
            and text(w.get('redesign')) for w in work.values()):
        error('best_case_failed_without_redesign', '%s：最好情景也不满足，要有一件 design 待办在 calculations 里写它，'
              '并在 redesign 写改设计的候选（改什么、预计效果），由用户批准' % key)
    conclusion, rests_on, reasons = calculation_basis(row, vendor_items, deferred_items)
    derived[key] = {'conclusion': conclusion, 'rests_on': rests_on, 'reasons': reasons}
    if (row.get('conclusion'), row.get('rests_on')) != (conclusion, rests_on):
        error('conclusion_not_derived', '%s: 写的 %s/%s，按记录是 %s/%s' % (
            key, row.get('conclusion'), row.get('rests_on'), conclusion, rests_on))
    coverage = 'partial' if 'not_calculated' in kinds else 'bounded'
    if row.get('coverage') != coverage:
        error('coverage_not_derived', '%s: 写的 %s，按遗漏项是 %s' % (key, row.get('coverage'), coverage))
    if conclusion == 'failed':
        need('calculation_failed', key)


def audit_estimate_margins(calculations, error):
    """uncertainty_version 1 (user 2026-10-28: 先改前四条; 判风险): each engineering estimate writes its relative
    uncertainty; a check resting on estimates whose margin is smaller than the largest of them passes with a margin
    risk and an improvement, like a stress risk."""
    risks = []
    for key, row in calculations.items():
        found, models = [], {}
        for p in row.get('parameters') or []:
            if isinstance(p, dict) and p.get('basis') in ESTIMATE_BASES:
                u = p.get('uncertainty')
                if not finite(u) or not 0 < u < 1:
                    error('model_without_uncertainty', '%s:%s：工程估计写 uncertainty（相对值，0–1，如 0.1 即 ±10%%）'
                          % (key, p.get('name')))
                else:
                    found.append(u)
                    models[p.get('name')] = u
        for c in row.get('checks') or []:
            if not isinstance(c, dict):
                continue
            if c.get('uncertainty') is not None and not (finite(c['uncertainty']) and 0 <= c['uncertainty'] < 1):
                error('schema', '%s:%s：uncertainty 是 0–1 的相对值' % (key, c.get('name')))
                continue
            # Calibration board #6 (2026-11-02): a check names the estimates it rests on (`estimates`, parameter names);
            # [] means none. Without either it takes the calculation's largest, and the risk says so.
            basis = 'check'
            if c.get('uncertainty') is not None:
                u = c['uncertainty']
            elif isinstance(c.get('estimates'), list):
                u = max((models[n] for n in c['estimates'] if n in models), default=None)
                unknown = [n for n in c['estimates'] if n not in models]
                if unknown:
                    error('schema', '%s:%s：estimates 列的 %s 不是本计算写了 uncertainty 的 model 参数' % (
                        key, c.get('name'), '、'.join(map(str, unknown))))
                basis = 'estimates'
            else:
                u, basis = max(found, default=None), 'calculation_max'
            hit = estimate_margin(c, u)
            if hit is None:
                continue
            risks.append({'calculation': key, 'check': c.get('name'), 'value': c['value'], 'limit': c[hit[1]],
                          'against': hit[1], 'unit': c.get('unit'), 'margin': hit[0], 'uncertainty': u,
                          'uncertainty_from': basis, 'improvement': c.get('improvement')})
            if not text(c.get('improvement')):
                error('estimate_margin_risk_without_improvement', '%s:%s：余量 %.2g%% 小于工程估计的不确定度 %.2g%%，'
                      '写 improvement（加大余量，或把估计收紧到余量以内）%s' % (
                          key, c.get('name'), hit[0] * 100, u * 100,
                          '；这个不确定度是整条计算里最大的一个，检查不依赖它时写 estimates（它用到的 model 参数名，'
                          '不依赖估计写 []）' if basis == 'calculation_max' else ''))
    return risks


def component_guidelines(artifact_root, error):
    """{ref: guidelines} of record/component-requirements.json: task 2.3's selection requirements may cite rules too
    (user 2026-11-01: 开工). The file's own audit checks the field's shape."""
    path = Path(artifact_root) / 'record' / 'component-requirements.json'
    if not path.is_file():
        return {}
    try:
        entries = json.loads(path.read_text(encoding='utf-8')).get('components', [])
        return {e['ref']: e for e in entries if e.get('guidelines')}
    except (ValueError, AttributeError, TypeError, KeyError) as exc:
        error('schema', 'record/component-requirements.json: %s' % exc)
        return {}


GUIDELINE_EVIDENCE_SHARE = 3


def audit_guideline_evidence(key, row, ids, error):
    """A closed work item covers a rule only where it points at what does it: `guideline_evidence` maps each rule it cites
    to `<evidence id>#<locator>` in its own evidence; one locator standing for more than three rules is a batch citation
    (calibration board #9/#24, 2026-11-02: one closed W-DOC item cited 205 rules)."""
    found = row.get('guideline_evidence') if isinstance(row.get('guideline_evidence'), dict) else {}
    evidence = set(row.get('evidence') or [])
    missing, shared = [], {}
    for gid in ids:
        where = found.get(gid)
        eid, _, locator = str(where or '').partition('#')
        if eid not in evidence or not text(locator):
            missing.append(gid)
        else:
            shared.setdefault(squeeze(where), []).append(gid)
    if missing:
        error('guideline_work_without_evidence', '%s：已关闭的待办引用 %s，guideline_evidence 要逐条写 <证据编号>#<节/表/行>，'
              '指到落实它的那一处' % (key, '、'.join(missing)))
    for where, gids in sorted(shared.items()):
        if len(gids) > GUIDELINE_EVIDENCE_SHARE:
            error('guideline_evidence_repeated', '%s：%d 条准则指向同一处 %s（%s）；每条指到落实它的那一处' % (
                key, len(gids), where, '、'.join(gids)))


def audit_project_input(record, classes, requirements, clarifications, evidence, error):
    """guideline_project_input (user 2026-11-04): one requirement baseline answers the project_input rules. The record
    names the baseline (evidence or clarification ids) and, rule by rule, the item that answers it (a requirement, a
    clarification or <baseline>#<locator>) or TBR. Returns {rule id: answer}; an item rule never gets an answer here."""
    section = record.get('guideline_project_input')
    if section is None:
        return {}
    if not (isinstance(section, dict) and not set(section) - {'baseline', 'answers'} and isinstance(section.get('baseline'), list)
            and section['baseline'] and isinstance(section.get('answers'), dict)):
        error('guideline_project_input', 'guideline_project_input 写 baseline（证据或需求澄清编号的列表）和 answers（{准则编号: 回答项或 TBR}）')
        return {}
    baseline = section['baseline']
    absent = [b for b in baseline if b not in (evidence or {}) and b not in clarifications]
    if absent:
        error('guideline_project_input', '需求基线 %s 不在 evidence 或 clarifications 里' % '、'.join(map(str, absent)))
        return {}
    answered = {}
    for gid, answer in section['answers'].items():
        if classes.get(gid, 'project_input') != 'project_input':
            error('guideline_batch_mixed_item', '%s：覆盖方式是 %s，不能由需求基线批量回答' % (gid, classes[gid]))
        elif (answer == 'TBR' or answer in requirements or answer in clarifications
              or (isinstance(answer, str) and answer.partition('#')[0] in baseline and text(answer.partition('#')[2]))):
            answered[gid] = answer
        else:
            error('guideline_project_input', '%s：回答项 %s 不是需求、需求澄清、<基线>#<节/表/行> 或 TBR' % (gid, answer))
    return answered


def audit_guidelines(record, calculations, work, error, need, library=None, artifact_root=None, evidence=None,
                     requirements=None, clarifications=None):
    """guideline_version 1 (user 2026-10-31: 请开始执行这个方案): the shared guideline rules this design triggers
    (references/shared/guideline-criteria.md). Each applicable rule is cited by a calculation, work item, component requirement
    or evidence entry (user 2026-11-03: 照此写入 — a documentation rule hangs on the interface table, operating matrix or FMEA
    entry that implements it, not on one closed work item), or held not applicable with a reason; one that closes after the schematic is cited by a work item, its handoff
    downstream. Rules whose library card says so are covered in bulk (user 2026-11-04): project_input by the baseline's
    answers, handoff by one work item or evidence entry. An item rule is never carried along with them."""
    library = library or guideline_criteria.load()
    scope = record.get('guideline_scope')
    problems = guideline_criteria.scope_errors(scope, library)
    for problem in problems:
        error('guideline_scope', problem)
    if problems:
        return None
    classes = {r['id']: guideline_criteria.coverage_class(r) for r in library['criteria']}
    answered = audit_project_input(record, classes, requirements or {}, clarifications or {}, evidence, error)
    cited, by_work, by_evidence = {gid: ['baseline:' + answer] for gid, answer in answered.items()}, set(), set()
    components = component_guidelines(artifact_root, error) if artifact_root else {}
    for kind, table in (('calc', calculations), ('work', work), ('component', components), ('evidence', evidence or {})):
        for key, row in table.items():
            ids = row.get('guidelines', [])
            if not (isinstance(ids, list) and all(isinstance(i, str) for i in ids)):
                error('schema', key + ':guidelines must be a string list')
                continue
            for gid in ids:
                cited.setdefault(gid, []).append(kind + ':' + key)
                if kind == 'work':
                    by_work.add(gid)
                elif kind == 'evidence':
                    by_evidence.add(gid)
            items = [i for i in ids if classes.get(i, 'item') == 'item']
            if kind in ('work', 'evidence') and items and len(items) < len(ids):
                error('guideline_batch_mixed_item', '%s：%s 是逐条覆盖的准则，不能和批量覆盖的 %s 写在同一条里；分开写' % (
                    key, '、'.join(items), '、'.join(i for i in ids if i not in items)))
            if kind == 'work' and row.get('status') == 'closed' and items:
                audit_guideline_evidence(key, row, items, error)
    applicable = guideline_criteria.select(library, scope['baseline'], scope['circuit_types'], scope['device_kinds'])
    found = guideline_criteria.coverage(library, applicable, cited,
                                     {i['id']: i['reason'] for i in scope.get('not_applicable', [])}, answered)
    for gid in found['unknown_cited']:
        error('guideline_unknown', gid)
    for gid in sorted(set(cited) - set(found['applicable']) - set(found['unknown_cited'])):
        error('guideline_cited_not_applicable', '%s：设计准则库判它不适用；补 guideline_scope 的电路类型或器件类别，或去掉引用' % gid)
    for gid in found['uncovered']:
        if classes.get(gid) == 'project_input':
            need('guideline_uncovered', '%s：写进 guideline_project_input.answers（由哪项需求回答或 TBR），或在 guideline_scope.not_applicable 写理由' % gid)
        else:
            need('guideline_uncovered', '%s：在计算、待办、器件性能要求或证据条目的 guidelines 里引用，或在 guideline_scope.not_applicable 写理由' % gid)
    for gid in found['downstream']:
        if gid in found['covered'] and gid not in by_work and not (classes.get(gid) == 'handoff' and gid in by_evidence) \
                and classes.get(gid) != 'project_input':
            error('guideline_downstream_without_work_item', '%s：关闭阶段在原理图之后，用一件待办交给下游' % gid)
    found.update(guideline_criteria.shared_versions(bundle=library))
    if found.get('by_coverage'):
        found['project_input_tbr'] = [g for g in found['by_coverage']['project_input'] if answered.get(g) == 'TBR']
    return found


# --- Placeholders, part identity binding, unused pins and rail voltages (binding_version 1) ---------------------------
# From the 86 open boards SR reviewed (user 2026-11-02: 把这86块板子上找到的问题，在规则库、ASG和SR技能中进行改进):
# R_Small/C/BZT52Bxx/xx/- values shipped (DOC-D01, DEV-D01), part number, package and datasheet named three parts (DEV-D04),
# HWSON pins wired as SO8 and outputs declared as inputs (DEV-D02), unused inputs and RSVD pins left open against the
# datasheet (NET-A07, DEV-D05), 25 V capacitors and 33 V TVS on 36 V rails (DEV-C01, PRO-E02).
PLACEHOLDER_VALUES = {'~', '-', '—', '?', '??', 'TBD', 'tbd', 'TBA', 'x', 'xx', 'XX', '待定', '未定',
                      'R', 'R_Small', 'R_US', 'C', 'C_Small', 'C_Polarized', 'CP', 'CP_Small', 'L', 'L_Small',
                      'D', 'D_Small', 'D_Zener', 'D_TVS', 'D_Schottky', 'LED', 'Crystal', 'Crystal_Small',
                      'Crystal_GND24', 'Crystal_GND23', 'Q_NPN', 'Q_PNP', 'Q_NMOS', 'Q_PMOS', 'FerriteBead', 'Fuse'}
# A lower-case x standing for a digit or letter of a part number (BZT52Bxx, BQ769x2), or a ? or * in it.
WILDCARD = re.compile(r'(?<=[A-Z0-9])x+(?=[A-Z0-9]|$)|[?*]')
# Kinds whose value is a rating or a frequency, not a part number; a value equal to the symbol name is a placeholder.
# G09-018: whether a part is fitted is its DNP flag and the BOM Assembly column; NC/DNP in the value is a state, not a value.
FIT_STATE_IN_VALUE = re.compile(r'(?<![A-Za-z0-9])(?:NC|N\.C\.|DNP|DNI|DNF|不装|未装)(?![A-Za-z0-9])')
VALUE_KINDS = ('resistor', 'capacitor', 'inductor', 'ferrite', 'crystal', 'diode', 'zener', 'tvs', 'fuse', 'bjt', 'mosfet')
NOT_PART_NUMBER = ('resistor', 'capacitor', 'inductor', 'ferrite', 'crystal', 'connector', 'testpoint', 'mechanical',
                   'jumper', 'switch', 'battery')
PART_NUMBER = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9][A-Za-z0-9.\-_/+#,()]{3,}$')
FREQUENCY = re.compile(r'(\d+(?:\.\d+)?)\s*([kKM]?)HZ', re.I)
# What the datasheet pin table says a pin is, and the KiCad electrical types that say the same (DEV-D02: outputs drawn as
# inputs hide a driver conflict from ERC).
DATASHEET_PIN_TYPES = {'I': {'input'}, 'O': {'output', 'tri_state'}, 'IO': {'bidirectional', 'tri_state'},
                       'OD': {'open_collector'}, 'OS': {'open_emitter'}, 'PWR': {'power_in'}, 'PWR_OUT': {'power_out'},
                       'GND': {'power_in', 'passive'}, 'A': {'passive', 'input', 'output', 'bidirectional'},
                       'NC': {'no_connect', 'passive', 'unspecified', 'free'}}
DISPOSITIONS = ('open', 'tie_low', 'tie_high', 'pull_down', 'pull_up', 'per_datasheet')
NET_VOLTAGE_SOURCE = re.compile(r'^(req:|calc:)(\S+)$|^datasheet:.+#p\d+$')
RETURN_NET = re.compile(r'(?:^|[/_])(?:[ADPS]?GND\w*|VSS\w*|RTN\w*|0V|COM)$', re.I)
# TVS series named by their stand-off voltage VRWM: SMAJ/SMBJ/SMCJ/SMDJ/SMLJ/SMF<VRWM>[C]A and Nexperia PESD/PTVS<a>V<b>
# (a.b V). Series named by breakdown voltage (P6KE, 1.5KE, P4SMA, P6SMB) are not read.
TVS_VRWM = (re.compile(r'^(?:SMAJ|SMBJ|SMCJ|SMDJ|SMLJ|SMF)(\d+(?:\.\d+)?)C?A', re.I),
            re.compile(r'^(?:PESD|PTVS)(\d+)V(\d+)', re.I))
VOLTS = re.compile(r'(\d+(?:\.\d+)?)\s*(k?)V(?![A-Za-z])')


def audit_placeholders(intent, error, strict=False):
    """A value or part number still holding a library default or a wildcard never ships (DOC-D01: R_Small, C, BZT52Bxx,
    xx, - on real boards); a reference still carrying ? is unannotated (DOC-Q01: K?). With ``strict`` (binding_version 1)
    an empty value counts too."""
    for c in intent.get('components') or []:
        if not isinstance(c, dict):
            continue
        ref, value, mpn = str(c.get('ref') or ''), str(c.get('value') or '').strip(), str(c.get('mpn') or '').strip()
        if '?' in ref:
            error('unannotated_reference', '%s：位号没有编号，按页编好号再出图' % ref)
        kind, problem = part_classes.kind_of(c)
        declared = part_classes.fields(c).get('Kind')
        if text(declared) and declared not in part_classes.KINDS:
            # Calibration board #5 (2026-11-02): tvs_bidirectional, mosfet_n, schottky passed until the BOM was written.
            error('kind_not_in_vocabulary', '%s：%s' % (ref, problem))
        symbol = str(c.get('lib_id') or '').partition(':')[2]
        generic = str(c.get('lib_id') or '').partition(':')[0] == 'Device'   # a project symbol named after its part is no default
        if value in PLACEHOLDER_VALUES or (kind in VALUE_KINDS and value and value == symbol and generic):
            error('placeholder_value', '%s：值 %s 是库默认名或占位，写设计值（阻值/容值/稳压值/型号）' % (ref, value))
        elif strict and not value and kind not in ('mechanical', 'testpoint', 'connector'):
            error('placeholder_value', '%s：没有写值' % ref)
        if FIT_STATE_IN_VALUE.search(value):
            error('dnp_in_value', '%s：值 %s 里写了装配状态；值只写值和规格，不装用 dnp 标明（BOM 的 Assembly 列随之写“%s”），'
                  '位号留在 BOM 里（G09-018）' % (ref, value, '不装（DNP）'))
        for field, text_ in (('mpn', mpn), ('value', value if kind not in VALUE_KINDS[:5] else '')):
            if text_ and WILDCARD.search(text_):
                error('placeholder_value', '%s：%s %s 含通配符（x、?、*），写手册订货信息里的完整订货码' % (ref, field, text_))


def datasheet_names(path):
    """The part names a library datasheet's file name gives (`Vendor - LM5163_LM5164.pdf` → lm5163, lm5164), squashed."""
    stem = Path(str(path)).stem.split(' - ')[-1]
    return [n for n in (part_classes.squash(p) for p in re.split(r'[_,&/+\s]|\band\b', stem)) if len(n) >= 3]


def names_part(name, mpn):
    """The datasheet name covers the part: it starts the part number (a lower-case x in the name matches any one
    character), or the part number starts it."""
    pattern = ''.join('[0-9a-z]' if ch == 'x' else re.escape(ch) for ch in name)
    return bool(re.match(pattern, mpn)) or name.startswith(mpn)


def datasheet_covers(comp, bases):
    """Whether the part's datasheet is the part's own: its file name names the part, or its text carries the part number."""
    mpn = part_classes.squash(comp.get('mpn'))
    if any(names_part(n, mpn) for n in datasheet_names(comp['datasheet'])):
        return True
    found = part_classes.find(comp['datasheet'], bases)
    if found is None:
        return None   # the identity audit reports a datasheet it cannot find
    from schematic_layout.component_requirements import document_text
    body = document_text(found)
    return None if body is None else mpn in part_classes.squash(body)


def hertz(text_):
    m = FREQUENCY.search(str(text_ or ''))
    return float(m.group(1)) * {'': 1, 'k': 1e3, 'K': 1e3, 'M': 1e6}[m.group(2)] if m else None


def audit_identity_binding(intent, bases, error):
    """Value, part number and datasheet name one part (DEV-D04/D01): value is the part number or its leading part, the
    datasheet file names it or carries it, a crystal's frequency agrees with its part number (CLK-C01)."""
    ctx = part_classes.context(intent)
    for c in intent.get('components') or []:
        if not isinstance(c, dict):
            continue
        ref, kind = c.get('ref'), part_classes.kind_of(c)[0]
        value, mpn = str(c.get('value') or '').strip(), str(c.get('mpn') or '').strip()
        if mpn and kind not in NOT_PART_NUMBER and PART_NUMBER.match(value):
            a, b = part_classes.squash(value), part_classes.squash(mpn)
            if not (a.startswith(b) or b.startswith(a)):
                error('part_value_contradicts_mpn', '%s：值 %s 与料号 %s 不是同一型号；值写料号或它的前段' % (ref, value, mpn))
        if kind == 'crystal' and mpn and hertz(value) and hertz(mpn) and not math.isclose(hertz(value), hertz(mpn), rel_tol=1e-6):
            error('crystal_frequency_contradicts_mpn', '%s：值 %s 与料号 %s 的频率不同' % (ref, value, mpn))
        if (mpn and text(c.get('datasheet')) and not part_classes.design_sheet(c)
                and part_classes.part_class(c, ctx) in (part_classes.KEY, part_classes.SPECIAL)
                and datasheet_covers(c, bases) is False):
            error('part_datasheet_contradicts_mpn', '%s：数据手册 %s 不是料号 %s 的手册（文件名不含它，正文也找不到）；'
                  '换成这个料号的手册，或把料号改成手册里的订货码' % (ref, c['datasheet'], mpn))


def net_table(intent):
    """{net: [ref.pin]} from either form of the design netlist."""
    nets = intent.get('nets') or {}
    if isinstance(nets, dict):
        return {k: list(v) for k, v in nets.items() if isinstance(v, list)}
    return {n['name']: list(n.get('pins') or []) for n in nets if isinstance(n, dict) and text(n.get('name'))}


def audit_pin_maps(intent, root, bases, error, need):
    """record/reference-input.json: each pin map reads the part's own datasheet (DEV-D04: the pin table of one part, the
    datasheet field of another) and writes what the datasheet pin table says each pin is, whose KiCad types must say the
    same (DEV-D02)."""
    path = Path(root) / 'record' / 'reference-input.json'
    if not path.is_file():
        need('reference_input_missing', 'record/reference-input.json：核心器件的引脚表与外围核对（任务 2.1）')
        return
    try:
        contract = json.loads(path.read_text(encoding='utf-8'))
        sources, maps = contract.get('sources') or {}, contract.get('pin_maps') or {}
    except (ValueError, AttributeError) as exc:
        error('schema', 'record/reference-input.json: %s' % exc)
        return
    comps = {c.get('ref'): c for c in intent.get('components') or [] if isinstance(c, dict)}
    for ref, spec in maps.items():
        comp = comps.get(ref) or {}
        source = (sources.get(spec.get('source')) or {}).get('path') if isinstance(spec, dict) else None
        sheet = comp.get('datasheet')
        if text(source) and text(sheet):
            local = (path.parent / source).resolve()
            if not part_classes.same_document(str(local) if local.is_file() else source, sheet, bases):
                error('pin_map_datasheet_mismatch', '%s：引脚表读的是 %s，设计网表的数据手册是 %s；按所选料号的手册重读引脚表'
                      % (ref, source, sheet))
        for number, pin in ((spec.get('pins') or {}) if isinstance(spec, dict) else {}).items():
            if not isinstance(pin, dict):
                continue
            # Calibration board #25 (2026-11-02): pin maps generated from the project symbol only checked the symbol's names.
            # Each pin writes the name as the datasheet prints it; where the symbol says it otherwise the map says why.
            printed = pin.get('datasheet_name')
            if not text(printed):
                error('pin_map_without_datasheet_name', '%s.%s：照手册引脚表写 datasheet_name（手册印的脚名）' % (ref, number))
            elif pin_name(printed) not in {pin_name(n) for n in pin.get('names') or []} and not text(pin.get('name_note')):
                error('pin_name_differs_from_datasheet', '%s.%s：手册脚名 %s，符号脚名 %s；改符号，或在 name_note 写两者为何是同一个脚'
                      % (ref, number, printed, '/'.join(pin.get('names') or [])))
            # type_note (Matrix R2, 2026-11-04): how the vendor code was read (TI P → PWR_OUT) or why the symbol type
            # differs; an explanation only — it does not waive pin_type_contradicts_datasheet.
            if 'type_note' in pin and not text(pin.get('type_note')):
                error('schema', '%s.%s：type_note 写手册类型码的读法或与符号类型不同的原因（非空文字）' % (ref, number))
            declared = pin.get('datasheet_type')
            if declared is None:
                error('pin_map_without_datasheet_type', '%s.%s：照手册引脚表写 datasheet_type（%s）'
                      % (ref, number, '/'.join(DATASHEET_PIN_TYPES)))
                continue
            allowed = DATASHEET_PIN_TYPES.get(declared)
            if allowed is None:
                error('schema', '%s.%s：datasheet_type 取 %s' % (ref, number, '/'.join(DATASHEET_PIN_TYPES)))
            elif not set(pin.get('types') or []) <= allowed:
                error('pin_type_contradicts_datasheet', '%s.%s：手册是 %s，符号脚类型写了 %s（应为 %s）' % (
                    ref, number, declared, '/'.join(pin.get('types') or []), '/'.join(sorted(allowed))))


def pin_name(name):
    """A pin name compared across symbol and datasheet: KiCad's ~{..} overbar and the punctuation dropped, case folded."""
    return re.sub(r'[^0-9a-z]', '', re.sub(r'~\{([^}]*)\}', r'\1', str(name)).lower())


def audit_pin_dispositions(record, intent, error, boundary=()):
    """Each pin left unconnected on a part other than a connector has a disposition read from its datasheet, and the
    netlist does what it says (NET-A07/DEV-D05: unused CMOS inputs and RSVD pins open against the datasheet); a net with
    one endpoint is an open pin in disguise (NET-A01: a Type-C CC on a one-node net), unless it is a boundary net whose
    contract row was found (Matrix R3 S25: the other end is off the board)."""
    nets = net_table(intent)
    comps = {c.get('ref'): c for c in intent.get('components') or [] if isinstance(c, dict)}
    where = {p: n for n, pins in nets.items() for p in pins}
    for name, pins in sorted(nets.items()):
        if len(set(pins)) == 1 and name not in boundary:
            error('single_endpoint_net', '%s：网络只接 %s 一个脚；接到它该接的网络，或放进 no_connect 并写处置' % (name, pins[0]))
    rows = record.get('pin_dispositions') or []
    if not isinstance(rows, list):
        error('schema', 'pin_dispositions must be a list')
        rows = []
    written = {}
    for row in rows:
        if not isinstance(row, dict) or not text(row.get('pin')):
            error('schema', 'pin_dispositions entry needs pin (ref.pin)')
            continue
        pin, disposition = row['pin'], row.get('disposition')
        if pin in written:
            error('duplicate_id', 'pin_dispositions:' + pin)
        written[pin] = row
        if disposition not in DISPOSITIONS:
            error('schema', '%s：disposition 取 %s' % (pin, '/'.join(DISPOSITIONS)))
            continue
        if not (isinstance(row.get('source'), str) and DATASHEET.match(row['source']) and text(row.get('locator'))):
            error('disposition_without_source', '%s：写手册里规定这个脚未用时怎么处理的页（source、locator）' % pin)
        nc, net = pin in (intent.get('no_connect') or []), where.get(pin)
        if disposition == 'open':
            wrong = not nc
        elif disposition in ('tie_low', 'tie_high'):
            wrong = net is None or net != row.get('net')
        elif disposition in ('pull_down', 'pull_up'):
            wrong = net is None or not any(part_classes.kind_of(comps.get(p.rsplit('.', 1)[0]) or {})[0] == 'resistor'
                                           for p in nets.get(net, []) if p != pin)
        else:
            wrong = not text(row.get('note'))
        if wrong:
            error('disposition_contradicts_netlist', '%s：处置写 %s%s，设计网表里它%s' % (
                pin, disposition, '（%s）' % row['net'] if row.get('net') else '',
                '在 no_connect' if nc else '在 %s' % net if net else '不在任何网络'))
    for pin in intent.get('no_connect') or []:
        comp = comps.get(str(pin).rsplit('.', 1)[0]) or {}
        if pin in written or is_connector_part(comp):
            continue
        error('no_connect_without_disposition', '%s：不接的脚要按手册写处置（pin_dispositions：悬空、接地、上下拉…及手册页）' % pin)


def is_connector_part(comp):
    from schematic_layout.component_role import is_connector
    return is_connector(comp) or part_classes.kind_of(comp)[0] in ('connector', 'testpoint', 'mechanical')


def rated_volts(comp, parameters=('working_voltage', 'rated_voltage')):
    """The voltage rating a part's record or fields write: its contract's ≥ requirement, else the largest voltage written."""
    contract = comp.get('performance_contract')
    if isinstance(contract, dict):
        for r in contract.get('requirements') or []:
            if isinstance(r, dict) and r.get('parameter') in parameters and r.get('op') == 'ge' and finite(r.get('value')) \
                    and r.get('unit') in ('V', 'kV'):
                return r['value'] * (1000 if r['unit'] == 'kV' else 1)
    found = [float(a) * (1000 if k else 1) for a, k in VOLTS.findall(part_classes.spec_text(comp))]
    return max(found) if found else None


def tvs_vrwm(comp):
    for value in (comp.get('mpn'), comp.get('value')):
        for i, pattern in enumerate(TVS_VRWM):
            m = pattern.match(str(value or '').strip())
            if m:
                return float(m.group(1)) if i == 0 else float('%s.%s' % (m.group(1), m.group(2)))
    return rated_volts(comp)


def audit_net_voltages(record, intent, requirements, calculations, error):
    """Each rail writes its worst-case maximum and where it comes from; a capacitor rated below the rail it sits on, or a
    TVS whose stand-off voltage is below it, fails (DEV-C01: 25 V across 30 V, 10 V on 15 V; PRO-E02: SMBJ33A on 36 V)."""
    rows = record.get('net_voltages') or []
    if not isinstance(rows, list):
        error('schema', 'net_voltages must be a list')
        rows = []
    maxima = {}
    for row in rows:
        if not isinstance(row, dict) or not text(row.get('net')) or not finite(row.get('max')) or row.get('unit') != 'V':
            error('schema', 'net_voltages entry needs net, finite max and unit V')
            continue
        m = NET_VOLTAGE_SOURCE.match(str(row.get('source') or ''))
        if not m or (m.group(1) == 'req:' and m.group(2) not in requirements) or (
                m.group(1) == 'calc:' and m.group(2) not in calculations):
            error('net_voltage_without_source', '%s：最高电压写来源 req:<需求编号>、calc:<计算编号> 或 datasheet:<手册>#p<页>' % row['net'])
        maxima[row['net']] = row['max']
    nets = net_table(intent)
    roles = intent.get('net_roles') or {}
    for name, role in sorted(roles.items()):
        if role == 'power' and name not in maxima:
            error('net_voltage_missing', '%s：电源轨写最坏最高电压（net_voltages：含容差、纹波和需求给的输入上限）' % name)
    where = {}
    for name, pins in nets.items():
        for p in pins:
            where.setdefault(p.rsplit('.', 1)[0], []).append(name)
    returns = {n for n in nets if roles.get(n) == 'return' or (roles.get(n) is None and RETURN_NET.search(n))}
    for c in intent.get('components') or []:
        kind = part_classes.kind_of(c)[0] if isinstance(c, dict) else None
        if kind not in ('capacitor', 'tvs'):
            continue
        on = where.get(c.get('ref'), [])
        live = [n for n in on if n not in returns]
        if len(on) != 2 or len(live) != 1 or live[0] not in maxima:
            continue
        rail, top = live[0], maxima[live[0]]
        rating = rated_volts(c) if kind == 'capacitor' else tvs_vrwm(c)
        if rating is not None and rating < top:
            error('capacitor_rating_below_net_voltage' if kind == 'capacitor' else 'tvs_vrwm_below_net_voltage',
                  '%s：%s %g V 低于 %s 的最高电压 %g V' % (c['ref'], '额定电压' if kind == 'capacitor' else 'VRWM', rating, rail, top))
    return maxima


def audit_binding(record, intent, artifact_root, requirements, calculations, error, need, boundary=()):
    """binding_version 1 (user 2026-11-02): the generation-side guard for the defect classes of the 86 boards."""
    root = Path(artifact_root)
    bases = [root, root / 'record']
    audit_identity_binding(intent, bases, error)
    audit_pin_maps(intent, root, bases, error, need)
    audit_pin_dispositions(record, intent, error, boundary)
    maxima = audit_net_voltages(record, intent, requirements, calculations, error)
    return {'net_voltages': maxima, 'pin_dispositions': len(record.get('pin_dispositions') or [])}


def audit(record, intent_path, artifact_root, inputs=None):
    errors, pending = [], []
    def error(code, item):
        errors.append({'code': code, 'item': str(item)})
    def need(code, item):
        pending.append({'code': code, 'item': str(item)})
    if not isinstance(record, dict):
        return {'status': 'FAIL', 'errors': [{'code': 'schema', 'item': 'record must be an object'}], 'pending': []}
    if record.get('schema_version') != 1:
        error('schema', 'schema_version must be 1')
    if record.get('intent_sha256') != sha256(intent_path):
        error('stale_intent', intent_path.name)
    intent = json.loads(intent_path.read_text(encoding='utf-8'))
    refs = {c['ref'] for c in intent['components']}
    threshold_parts = sorted(c['ref'] for c in intent['components'] if threshold_part(c))
    root = artifact_root.resolve()
    tables = {}
    for key in ('evidence', 'requirements', 'work_items', 'calculations'):
        entries = record.get(key)
        table = {}
        if not isinstance(entries, list):
            error('schema', key + ' must be a list')
            entries = []
        for row in entries:
            if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id'].strip():
                error('schema', key + ' entry requires a nonempty string id')
                continue
            if row['id'] in table:
                error('duplicate_id', key + ':' + row['id'])
            table[row['id']] = row
        tables[key] = table
    evidence, requirements, work, calculations = (tables[k] for k in ('evidence', 'requirements', 'work_items', 'calculations'))
    clarifications = audit_clarifications(record, requirements, work, error, artifact_root)
    if not requirements:
        need('missing_requirements', 'No requirements reviewed')
    for key, row in evidence.items():
        p = row.get('path')
        if not isinstance(p, str) or not p or Path(p).is_absolute():
            error('evidence_path', key)
            continue
        path = resolve(p, root, inputs)
        if path is None:
            error('evidence_missing_or_outside_root', key)
        elif row.get('sha256') != sha256(path):
            error('stale_evidence', key)

    def linked(row, field, table, required=False):
        values = row.get(field)
        if not isinstance(values, list) or any(not isinstance(x, str) for x in values):
            error('schema', row['id'] + ':' + field + ' must be a string list')
            return []
        if required and not values:
            error('missing_' + field, row['id'])
        for key in values:
            if key not in table:
                error('unknown_' + field, row['id'] + ':' + key)
        return values

    for key, row in work.items():
        affected = linked(row, 'requirements', requirements, True)
        linked(row, 'evidence', evidence, row.get('status') == 'closed')
        stage, state = row.get('stage'), row.get('status')
        if stage not in ('requirement', 'design', 'external', 'validation', 'pcb') or state not in ('open', 'closed', 'handoff'):
            error('schema', key + ':invalid stage/status')
        if state == 'handoff' and stage not in ('validation', 'pcb'):
            error('unfinished_design_handoff', key)
        if state != 'closed':
            for field in ('action', 'owner'):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    error('missing_' + field, key)
            if stage in ('validation', 'pcb') and state == 'handoff':
                linked(row, 'evidence', evidence, True)
            else:
                need('open_' + str(stage), key)
                # Possible consequence if left undone; its level orders the report's to-do list.
                level = severity_of(row)
                if level is None:
                    error('missing_consequence', key)
                elif row.get('severity') not in (None, level):
                    error('severity_contradicts_rule', '%s: %s, rule gives %s' % (key, row['severity'], level))
        if stage == 'pcb':
            if row.get('scope') not in ('footprint_library', 'layout_implementation', 'dfm'):
                error('pcb_scope', key)
            prerequisites = linked(row, 'electrical_preconditions', work, True)
            for dep in prerequisites:
                item = work.get(dep, {})
                if item.get('stage') != 'design' or item.get('status') != 'closed':
                    error('pcb_electrical_precondition', key + ':' + dep)
        # A requirement the user deferred is designed on the proposed text; one never asked is asked now, not at delivery.
        if stage == 'requirement' and state != 'closed':
            asked = clarifications.get(row.get('clarification')) or {}
            if not text(row.get('assumption')):
                error('missing_assumption', key)
            if (asked.get('answer') or {}).get('decision') != 'DEFERRED':
                error('requirement_without_clarification', key)
            elif text(row.get('assumption')) and row['assumption'] != asked.get('proposed_requirement'):
                error('assumption_differs_from_proposal', key)
            if 'calculations' in row:
                linked(row, 'calculations', calculations)
        for rid in affected:
            if rid in requirements and key not in requirements[rid].get('depends_on', []):
                error('unlinked_dependency', rid + ':' + key)

    for key, row in requirements.items():
        state = row.get('status')
        if state not in ('design_supported', 'conditional', 'open'):
            error('schema', key + ':invalid requirement status')
        linked(row, 'evidence', evidence, True)
        linked(row, 'refs', refs)
        deps = linked(row, 'depends_on', work)
        if not isinstance(row.get('implementation'), str) or not row['implementation'].strip():
            error('missing_implementation', key)
        if state != 'design_supported':
            need('requirement_not_supported', key)
        for dep in deps:
            item = work.get(dep, {})
            closed = item.get('status') == 'closed' or (item.get('stage') in ('validation', 'pcb') and item.get('status') == 'handoff')
            if state == 'design_supported' and not closed:
                error('unsupported_requirement_claim', key + ':' + dep)

    parameters = 'parameter_version' in record
    if parameters and record['parameter_version'] not in (1, 2, 3):
        error('schema', 'parameter_version must be 1, 2 or 3')
        parameters = False
    version = record['parameter_version'] if parameters else None
    points = audit_operating_points(record, work, refs, error, need) if parameters else {}
    vendor_items, deferred_items, derived = vendor_items_of(work), vendor_items_of(work, 'requirement'), {}
    for key, row in calculations.items():
        if parameters:
            audit_parameters(key, row, refs, points, calculations, error, version, requirements)
        linked(row, 'requirements', requirements, True)
        linked(row, 'evidence', evidence, True)
        coverage, conclusion = row.get('coverage'), row.get('conclusion')
        if coverage not in ('bounded', 'partial') or conclusion not in ('supported', 'conditional', 'failed'):
            error('schema', key + ':invalid coverage/conclusion')
        if version in (2, 3):
            audit_calculation_v2(key, row, work, vendor_items.get(key, []), deferred_items.get(key, []), derived, error, need)
            if version == 3:
                audit_limits(key, row, requirements, calculations, error)
            continue
        omitted = row.get('omitted_terms')
        if not isinstance(omitted, list) or any(not isinstance(x, str) for x in omitted):
            error('schema', key + ':omitted_terms must be a string list')
            omitted = []
        if coverage == 'bounded' and omitted:
            error('contradictory_coverage', key)
        if conclusion == 'supported' and (coverage != 'bounded' or omitted):
            error('partial_calculation_claimed_supported', key)
        assumptions = row.get('assumptions', [])
        if not isinstance(assumptions, list) or any(not isinstance(x, str) for x in assumptions):
            error('schema', key + ':assumptions must be a string list')
            assumptions = []
        # Design-level threshold: a conditional result with its assumptions written down is enough to
        # draw the schematic; proving it under every guaranteed condition belongs to independent review.
        if conclusion == 'conditional' and not (omitted or assumptions):
            error('conditional_without_assumptions', key)
        # Conditional is not a hedge: it names the guarantee the datasheet or the
        # requirement does not give; partial coverage names what was left out.
        if conclusion == 'conditional' and not (isinstance(row.get('missing_guarantee'), str) and row['missing_guarantee'].strip()):
            error('conditional_without_missing_guarantee', key)
        if coverage == 'partial' and not omitted:
            error('partial_without_omitted_terms', key)
        linked(row, 'refs', refs, True)
        # The conclusion follows from the numbers: each check compares a computed
        # value with the limit it must meet. A failed check cannot be called
        # conditional, and a calculation without any check proves nothing.
        checks = row.get('checks')
        if not isinstance(checks, list) or not checks:
            error('missing_checks', key)
            checks = []
        results, sides = [], set()
        for i, c in enumerate(checks):
            where = key + ':checks[' + str(i) + ']'
            if (not isinstance(c, dict) or not isinstance(c.get('name'), str) or not c['name'].strip()
                    or not finite(c.get('value')) or not finite(c.get('limit'))
                    or c.get('operator') not in OPERATORS or not isinstance(c.get('unit'), str)):
                error('schema', where + ' needs name, finite value/limit, operator (<=, <, >=, >, ==) and unit')
                continue
            results.append(holds(c))
            if c.get('side') is not None:
                if c['side'] not in WINDOW_SIDES:
                    error('schema', where + ':side must be no_false_trip or protection')
                sides.add(c['side'])
        if results and conclusion in ('supported', 'conditional') and not all(results):
            error('conclusion_contradicts_checks', key)
        if results and conclusion == 'failed' and all(results):
            error('conclusion_contradicts_checks', key)
        # A threshold has two sides: normal operation must stay clear of the
        # minimum trip point, and the maximum trip point must still protect.
        if row.get('kind') == 'threshold':
            for side in WINDOW_SIDES:
                if side not in sides:
                    error('threshold_window_incomplete', key + ':' + side)
        elif row.get('kind') is not None:
            error('schema', key + ':kind must be threshold when present')
        if conclusion == 'failed':
            need('calculation_failed', key)
            for rid in row.get('requirements', []):
                if rid in requirements and requirements[rid].get('status') == 'design_supported':
                    error('unsupported_calculation_dependency', rid + ':' + key)
    if version in (2, 3):
        for rid, req in requirements.items():
            weak = [k for k, row in calculations.items() if rid in (row.get('requirements') or [])
                    and derived.get(k, {}).get('conclusion') != 'supported']
            if req.get('status') == 'design_supported' and weak:
                error('requirement_status_not_derived', rid + ': rests on ' + '、'.join(weak))
    if version == 3:
        # R8: the cost target was "estimated in the selection record" and never was; every requirement is checked.
        checked = {r for row in calculations.values() for r in row.get('requirements') or [] if isinstance(r, str)}
        for rid, req in requirements.items():
            if rid not in checked and not text(req.get('no_check_reason')):
                error('requirement_without_check', rid)
    derating = None
    if 'derating_version' in record:
        if record['derating_version'] != 1 or version not in (2, 3):
            error('schema', 'derating_version must be 1, with parameter_version 2 or 3')
        else:
            derating = audit_derating(record, intent, calculations, requirements, clarifications, error, work=work)
    # Inputs that describe the board's surroundings have a source, whatever the record version since parameter_version 2
    # (Matrix R2, user 2026-11-04: a 1 A startup load written into a script and a parameter's name reversed a check).
    inputs_found = None
    if version in (2, 3):
        inputs_found = audit_operating_inputs(record, calculations, requirements, clarifications, work, intent, error)
    margins = None
    if 'uncertainty_version' in record:
        if record['uncertainty_version'] != 1 or version not in (2, 3):
            error('schema', 'uncertainty_version must be 1, with parameter_version 2 or 3')
        else:
            margins = audit_estimate_margins(calculations, error)
    guidelines = None
    if 'guideline_version' in record:
        if record['guideline_version'] != 1:
            error('schema', 'guideline_version must be 1')
        else:
            guidelines = audit_guidelines(record, calculations, work, error, need, artifact_root=artifact_root, evidence=evidence,
                                          requirements=requirements, clarifications=clarifications)
    elif guideline_criteria.load()['criteria']:
        need('guideline_scope_missing', '写 guideline_version 1 和 guideline_scope（references/shared/guideline-criteria.md）')
    # Placeholders never ship, whatever the record version (DOC-D01); binding_version 1 adds the identity, pin and rail checks.
    audit_placeholders(intent, error, strict='binding_version' in record)
    # Nets declared to leave the design to another board each have a row in their interface contract (Matrix R2).
    verified = set()
    boundary = boundary_nets.audit_contracts(intent, lambda p: resolve(p, root, inputs) if isinstance(p, str) and not Path(p).is_absolute() else None, error, verified)
    binding = None
    if 'binding_version' in record:
        if record['binding_version'] != 1:
            error('schema', 'binding_version must be 1')
        else:
            binding = audit_binding(record, intent, artifact_root, requirements, calculations, error, need, verified)
    gaps = 'gap_version' in record
    if gaps and record['gap_version'] not in (1, 2):
        error('schema', 'gap_version must be 1 or 2')
        gaps = False
    if gaps:
        audit_gaps(work, calculations, error, record['gap_version'])
    citations = audit_citations(record, calculations, work, [root, *(inputs or ())], error)
    covered = {r for row in calculations.values() if isinstance(row.get('refs'), list) for r in row['refs']}
    for ref in threshold_parts:
        if ref not in covered:
            error('threshold_part_uncalculated', ref)
    if not calculations and not record.get('no_calculations_reason'):
        need('calculation_scope_missing', 'Declare necessary calculations or explain why none apply')
    if record.get('coverage') not in ('complete', 'partial'):
        error('schema', 'coverage must be complete or partial')
    if record.get('coverage') != 'complete':
        need('partial_review', 'Not all requirements/design obligations reviewed')
    convergence = {'status': 'NOT_ASSESSED'}
    if 'convergence_version' in record:
        if record['convergence_version'] != 1:
            error('schema', 'convergence_version must be 1')
        else:
            convergence = frontier(work, evidence)
            errors.extend(convergence['errors'])
    status = 'FAIL' if errors else 'INCOMPLETE' if pending else 'PASS'
    return {'status': status, 'scope': 'Declared design evidence and dependency consistency; not physics, native ERC or visual approval',
            'intent_sha256': sha256(intent_path), 'errors': errors, 'pending': pending,
            'severities': {k: severity_of(v) for k, v in work.items() if v.get('status') == 'open' and severity_of(v)},
            'pcb_handoffs': [k for k, v in work.items() if v.get('stage') == 'pcb' and v.get('status') == 'handoff'],
            'counts': {k: len(v) for k, v in tables.items()}, 'convergence': convergence,
            'parameters': 'CHECKED' if parameters else 'NOT_CHECKED', 'parameter_version': version,
            'calculation_basis': derived,
            'gaps': 'CHECKED' if gaps else 'NOT_CHECKED', 'citations': citations,
            'derating': derating if derating is not None else 'NOT_CHECKED',
            'operating_inputs': inputs_found if inputs_found is not None else 'NOT_CHECKED',
            'estimate_margins': margins if margins is not None else 'NOT_CHECKED',
            'guidelines': guidelines if guidelines is not None else 'NOT_CHECKED',
            'binding': binding if binding is not None else 'NOT_CHECKED',
            'boundary_nets': boundary,
            'unspecified_operations': sorted(k for k, v in points.items() if v.get('specified') is False),
            'downstream_handoffs': [k for k, v in work.items() if v.get('stage') in ('validation', 'pcb') and v.get('status') == 'handoff']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('record', type=Path)
    ap.add_argument('--intent', type=Path, required=True)
    ap.add_argument('--artifact-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--input', action='append', default=[], metavar='NAME=PATH',
                    help='declared input (requirements, datasheets) where cited evidence may live, as pack_design takes it')
    args = ap.parse_args()
    inputs = [v.split('=', 1)[-1] for v in args.input]
    try:
        result = audit(json.loads(args.record.read_text(encoding='utf-8')), args.intent, args.artifact_root, inputs)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'status': 'FAIL', 'errors': [{'code': 'invalid_input', 'item': str(exc)}], 'pending': []}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(result['status'])
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
