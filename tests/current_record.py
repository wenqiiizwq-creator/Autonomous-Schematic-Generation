"""Bring a minimal test record of design-closure.json to the current format (user 2026-11-08: the audit reads only
CURRENT_VERSIONS). Fills in only what the format asks for and the test does not care about, so the test's own case is
the only finding: version keys, a derating level, one constant per calculation, limit sources, part values, a
temperature matrix of not-applicable cells and an empty reference input."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_design_closure import CURRENT_VERSIONS, sha256  # noqa: E402

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
