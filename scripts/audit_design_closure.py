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
from schematic_layout import part_classes
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
DERATING_RULES = Path(__file__).resolve().parent.parent / 'references' / 'derating-rules.json'
DERATING_SOURCE = re.compile(r'^(req:|clarification:)(\S+)$')
RATING_SOURCE = re.compile(r'^(datasheet:.+#p\d+|req:\S+|calc:\S+)$')
# A resistor whose power matters carries its power rating (user 2026-10-27: 设计时考虑功耗，除阻值和精度外还要写上功率等级，
# 作为给以后的约束). Mirrors schematic-review's passive_stress: the weakest part the written fields allow is half the
# package's commodity floor (RG1005 0.032 W), derated by the level's RES-SMD-P value (0.5 with no level); a part without
# a footprint is judged as 0402.
RESISTOR_FLOORS = {'0201': 0.05, '0402': 1 / 16, '0603': 1 / 16, '0805': 0.1,
                   '1206': 0.125, '1210': 0.25, '2010': 0.5, '2512': 1.0}
WEAKEST_SHARE, UNSET_POWER_SHARE, ASSUMED_PACKAGE = 0.5, 0.5, '0402'
RESISTOR_PACKAGE = re.compile(r'^Resistor_SMD:R_(0201|0402|0603|0805|1206|1210|2010|2512)_', re.I)
WATTS = re.compile(r'^(\d+(?:\.\d+)?)\s*(m?)W$')
SEGMENT_SPLIT = re.compile(r'[/，,；;、\s]+')


def text(value):
    return isinstance(value, str) and bool(value.strip())


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


def audit_clarifications(record, requirements, work, error):
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
        if answer['decision'] == 'ADOPTED_PROPOSAL' and answer['text'] != row.get('proposed_requirement'):
            error('adopted_text_differs', key)
        if answer['decision'] != 'DEFERRED':
            if requirements.get(key, {}).get('text') != answer['text']:
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


def derated_limit(rule, level, rating):
    """The limit a rule sets at this level, or None when the measure has no single number to compare.
    A ratio of a negative rating is the allowed magnitude (R8)."""
    v, m = rule['values'][level], rule['measure']
    if m in ('ratio', 'pulse_ratio', 'min_ratio', 'margin_c', 'tj_percent') and not finite(rating):
        return None
    if m in ('ratio', 'pulse_ratio', 'min_ratio'):
        rating = abs(rating)
    return {'ratio': lambda: rating * v, 'pulse_ratio': lambda: rating * v, 'min_ratio': lambda: rating * v,
            'margin_c': lambda: rating - v, 'tj_percent': lambda: (rating - 25) * v + 25,
            'max_c': lambda: v, 'max_rise_k': lambda: v, 'max_v': lambda: v, 'min_hours': lambda: v,
            'min_years': lambda: v, 'max_dvdt': lambda: v}.get(m, lambda: None)()


# A check against a guaranteed rating that names no rule (stress-spec.md, 2026-10-28, user: 按推荐都做): the quantity is
# the unit's, and rules of one kind are told apart by the part's identity, the "其他…" rule taking a part none names.
# Mirrors schematic-review's derating.implied_ratio.
UNIT_DIMENSIONS = (('current', re.compile(r'^[mµu]?A$')), ('voltage', re.compile(r'^[mk]?V$')), ('power', re.compile(r'^m?W$')))
DIMENSION_WORDS = {'current': ('电流',), 'voltage': ('电压',), 'power': ('功率', '功耗')}
TYPE_WORDS = {'USB 母座': re.compile(r'USB', re.I),
              '器具耦合器': re.compile(r'耦合器|IEC ?60320|appliance coupler|\bC(?:5|6|7|8|13|14|15|16)\b', re.I)}


def implied_rule(c, comp, kind, rules, level):
    """(rule, derated) for a check of a stress against the part's guaranteed rating that names no rule, when exactly one
    steady or worst-case ratio rule fits the part's kind and the unit's quantity and the stress is over the derated
    value; else None. R8 (2026-10-28): VBUS 5 A against the connector's 5 A rating passed with zero margin."""
    if not (level and kind and not text(c.get('derating_rule')) and c.get('limit_basis') == 'guaranteed'
            and c.get('operator') in ('<=', '<') and finite(c.get('value')) and finite(c.get('limit')) and c['limit'] > 0):
        return None
    words = next((DIMENSION_WORDS[d] for d, pattern in UNIT_DIMENSIONS if pattern.match(str(c.get('unit') or '').strip())), ())
    fits = [r for r in rules.values() if r['measure'] == 'ratio' and r['condition'] in ('worst', 'steady')
            and kind in r['kinds'] and any(w in r['parameter'] for w in words)]
    if len(fits) > 1:
        identity = ' '.join(str(comp.get(k) or '') for k in ('mpn', 'value', 'lib_id'))
        named = [r for r in fits if TYPE_WORDS.get(r['type']) and TYPE_WORDS[r['type']].search(identity)]
        fits = named or [r for r in fits if r['type'].startswith('其他') and not any(
            TYPE_WORDS.get(o['type']) and TYPE_WORDS[o['type']].search(identity) for o in fits)]
    if len(fits) != 1:
        return None
    derated = c['limit'] * fits[0]['values'][level]
    return (fits[0], derated) if c['value'] > derated else None


def audit_derating(record, intent, calculations, requirements, clarifications, error, loaded=None):
    """derating_version 1, judged by stress-spec.md (user 2026-10-27): the level and where it was decided; each check that
    names a rule uses that rule's limit for the level; over the derated value but within the rating is a stress risk with
    an improvement; only the stresses written are checked, and a stress compared with a rating that names no rule while
    the spec has rules for that kind is a hint."""
    rules, _ = loaded or load_derating()
    info = record.get('derating') if isinstance(record.get('derating'), dict) else {}
    level = info.get('level')
    if level not in ('I', 'II', 'III'):
        error('derating_level_missing', 'derating.level must be I, II or III')
        level = None
    m = DERATING_SOURCE.match(info.get('source') or '')
    if not m or (m.group(1) == 'req:' and m.group(2) not in requirements) or (
            m.group(1) == 'clarification:' and ((clarifications.get(m.group(2)) or {}).get('answer') or {}).get('decision') != 'DEFERRED'):
        error('derating_level_without_source', 'derating.source: req:<需求编号>，或 clarification:<用户暂缓的需求澄清>')
    comps = {c['ref']: c for c in intent.get('components') or []}
    ruled = {k for r in rules.values() for k in r['kinds']}
    share = rules['RES-SMD-P']['values'][level] if level else UNSET_POWER_SHARE
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
                          '额定功率取 ≥ %.4g W 的标准档（%s）' % (where, ref, need, '应力 ÷ %s 级 RES-SMD-P %g' % (level, share)
                                                               if level else '降额等级未定，取应力 2 倍'))
            if not text(c.get('derating_rule')):
                implied = implied_rule(c, comps.get(ref) or {}, kind, rules, level)
                if implied:
                    rule, derated = implied
                    risks.append({'calculation': key, 'check': c.get('name'), 'ref': ref, 'rule': rule['id'],
                                  'value': c.get('value'), 'limit': derated, 'rating': c.get('limit'),
                                  'unit': c.get('unit'), 'improvement': c.get('improvement')})
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
            expected = derated_limit(rule, level, c.get('rating')) if level else None
            if rule['measure'] in ('ratio', 'pulse_ratio', 'min_ratio', 'margin_c', 'tj_percent') and not finite(c.get('rating')):
                error('derating_rating_missing', where)
            elif expected is not None and finite(c.get('limit')) and not math.isclose(
                    abs(c['limit']) if finite(c.get('rating')) and c['rating'] < 0 else c['limit'], expected, rel_tol=1e-6, abs_tol=1e-9):
                error('derating_limit_mismatch', '%s：写的 %g，%s 级 %s 是 %g' % (where, c['limit'], level, rule['id'], expected))
            if derating_deviation(c):
                risks.append({'calculation': key, 'check': c.get('name'), 'ref': ref, 'rule': rule['id'],
                              'value': c.get('value'), 'limit': c.get('limit'), 'rating': c.get('rating'),
                              'unit': c.get('unit'), 'improvement': c.get('improvement')})
                if not text(c.get('improvement')):
                    error('stress_risk_without_improvement', where + '：写 improvement（换额定更高的件或降低应力）')
    return {'level': level, 'source': info.get('source'), 'stress_risks': risks, 'hints': hints}


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
        found = []
        for p in row.get('parameters') or []:
            if isinstance(p, dict) and p.get('basis') in ESTIMATE_BASES:
                u = p.get('uncertainty')
                if not finite(u) or not 0 < u < 1:
                    error('model_without_uncertainty', '%s:%s：工程估计写 uncertainty（相对值，0–1，如 0.1 即 ±10%%）'
                          % (key, p.get('name')))
                else:
                    found.append(u)
        for c in row.get('checks') or []:
            if not isinstance(c, dict):
                continue
            if c.get('uncertainty') is not None and not (finite(c['uncertainty']) and 0 <= c['uncertainty'] < 1):
                error('schema', '%s:%s：uncertainty 是 0–1 的相对值' % (key, c.get('name')))
                continue
            u = c['uncertainty'] if c.get('uncertainty') is not None else max(found, default=None)
            hit = estimate_margin(c, u)
            if hit is None:
                continue
            risks.append({'calculation': key, 'check': c.get('name'), 'value': c['value'], 'limit': c[hit[1]],
                          'against': hit[1], 'unit': c.get('unit'), 'margin': hit[0], 'uncertainty': u,
                          'improvement': c.get('improvement')})
            if not text(c.get('improvement')):
                error('estimate_margin_risk_without_improvement', '%s:%s：余量 %.2g%% 小于工程估计的不确定度 %.2g%%，'
                      '写 improvement（加大余量，或把估计收紧到余量以内）' % (key, c.get('name'), hit[0] * 100, u * 100))
    return risks


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
    clarifications = audit_clarifications(record, requirements, work, error)
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
            derating = audit_derating(record, intent, calculations, requirements, clarifications, error)
    margins = None
    if 'uncertainty_version' in record:
        if record['uncertainty_version'] != 1 or version not in (2, 3):
            error('schema', 'uncertainty_version must be 1, with parameter_version 2 or 3')
        else:
            margins = audit_estimate_margins(calculations, error)
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
            'estimate_margins': margins if margins is not None else 'NOT_CHECKED',
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
