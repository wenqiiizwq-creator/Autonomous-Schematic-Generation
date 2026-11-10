"""Bring a minimal test record of design-closure.json to the current format (user 2026-11-08: the audit reads only
CURRENT_VERSIONS). Fills in only what the format asks for and the test does not care about, so the test's own case is
the only finding: version keys, a derating level, one constant per calculation, limit sources, part values, a
temperature matrix of not-applicable cells and an empty reference input."""
import copy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_design_closure import (C1_SECTIONS, CURRENT_VERSIONS, REQUIREMENT_FIELDS, REQUIREMENTS_FILE,  # noqa: E402
                                  TRACE_FIELDS, sha256)

NA = {'verdict': 'not_applicable', 'reason': '测试夹具，与本例无关'}


def make_current(record, intent=None, root=None):
    record.update(CURRENT_VERSIONS)
    reqs = [r['id'] for r in record.get('requirements') or [] if isinstance(r, dict)]
    if reqs:
        record.setdefault('derating', {'level': 'III', 'source': 'req:' + reqs[0]})
    for calc in record.get('calculations') or []:
        if not isinstance(calc, dict):
            continue
        calc.setdefault('parameters', [{'name': '测试常数', 'value': 1, 'unit': '1', 'basis': 'constant',
                                        'reason': '测试夹具'}])
        own = (calc.get('requirements') or reqs or ['?'])[0]
        for check in calc.get('checks') or []:
            if isinstance(check, dict) and 'limit_basis' not in check:
                check.update(limit_basis='requirement', limit_source='req:' + own)
    refs = []
    if intent is not None:
        intent = Path(intent)
        data = json.loads(intent.read_text(encoding='utf-8'))
        refs = [comp['ref'] for comp in data.get('components') or []]
        # a stale intent is the test's own case: leave the file and its hash alone
        if record.get('intent_sha256') == sha256(intent) and any('value' not in c for c in data.get('components') or []):
            for comp in data['components']:
                comp.setdefault('value', comp['ref'] + '_VALUE')
            intent.write_text(json.dumps(data), encoding='utf-8')
            record['intent_sha256'] = sha256(intent)
    if reqs:
        rng = {'min': -40, 'max': 85, 'source': 'req:' + reqs[0]}
        matrices = record.setdefault('matrices', {'supervised_rails': [], 'port_stress': [], 'protection_states': [],
                                                  'temperature': {'operating': rng, 'storage': dict(rng), 'rows': []}})
        rows = matrices['temperature']['rows'] if isinstance(matrices.get('temperature'), dict) else []
        listed = {r for row in rows for r in row.get('refs') or []}
        rows += [{'refs': [r], 'operating': NA, 'storage': NA} for r in refs if r not in listed]
    if root is not None:
        path = Path(root) / 'record' / 'reference-input.json'
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({'sources': {}, 'pin_maps': {}}), encoding='utf-8')
    return record


def split(record):
    """A one-dict test record (the audit's merged view) as the two files of trace_version 1: design-closure.json with
    the traceability, and requirements.json with the requirement text and source, clarifications, derating level and
    guideline scope. The evidence the requirement rows cite moves along."""
    closure = copy.deepcopy(record)
    rows = [r for r in closure.pop('requirements', None) or [] if isinstance(r, dict)]
    own = {e for r in rows for e in r.get('evidence') or [] if isinstance(e, str)}
    evidence = closure.get('evidence') if isinstance(closure.get('evidence'), list) else []
    requirements = {'schema_version': 1, 'evidence': [e for e in evidence if isinstance(e, dict) and e.get('id') in own],
                    'requirements': [{k: v for k, v in r.items() if k in REQUIREMENT_FIELDS} for r in rows]}
    for key in C1_SECTIONS:
        if key in closure:
            requirements[key] = closure.pop(key)
    if 'evidence' in closure:
        closure['evidence'] = [e for e in evidence if not (isinstance(e, dict) and e.get('id') in own)]
    closure['traceability'] = [dict({'requirement': r.get('id')}, **{k: v for k, v in r.items() if k in TRACE_FIELDS})
                               for r in rows if any(k in r for k in TRACE_FIELDS)]
    return closure, requirements


def write_record(record, path):
    """Write a test record as design-closure.json at `path` and requirements.json next to it (split)."""
    path = Path(path)
    closure, requirements = split(record)
    path.write_text(json.dumps(closure, ensure_ascii=False), encoding='utf-8')
    (path.parent / REQUIREMENTS_FILE).write_text(json.dumps(requirements, ensure_ascii=False), encoding='utf-8')
    return closure, requirements
