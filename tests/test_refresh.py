"""refresh.py: what follows from other records by rule is rewritten before a gate, and nothing else is (user
2026-11-15: 你给的这些建议，都分别做; H-001 runs: a third of the gate problems were stale copies and hashes)."""
import framework_required  # noqa: F401
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import refresh  # noqa: E402
from schematic_layout import component_requirements as cr  # noqa: E402
from test_component_requirements import fixture  # noqa: E402


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.record = self.root / 'record'
        self.record.mkdir()

    def write(self, name, data):
        (self.record / name).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def read(self, name):
        return json.loads((self.record / name).read_text(encoding='utf-8'))

    def test_the_performance_contract_is_projected_and_a_second_run_writes_nothing(self):
        intent, record = fixture(self.root)
        self.write('electrical-intent.json', intent)
        self.write('component-requirements.json', record)
        done, skipped = refresh.refresh(self.root, 'C4')
        self.assertEqual((1, []), (len(done), skipped))
        self.assertEqual([], cr.audit(self.read('electrical-intent.json'), record, self.root)['errors'])
        self.assertEqual(([], []), refresh.refresh(self.root, 'C4'))

    def test_conclusion_coverage_intent_hash_and_requirement_status_follow_the_record(self):
        check = {'name': 'R1 功耗', 'value': 1, 'operator': '<=', 'limit': 2, 'unit': 'W'}
        self.write('electrical-intent.json', {'components': []})
        self.write('design-closure.json', {
            'intent_sha256': 'old', 'work_items': [],
            'calculations': [
                {'id': 'C-OK', 'requirements': ['R1'], 'checks': [check], 'parameters': [],
                 'conclusion': 'failed', 'rests_on': 'estimate', 'coverage': 'partial'},
                {'id': 'C-TYP', 'requirements': ['R2'], 'checks': [check], 'conclusion': 'supported', 'coverage': 'bounded',
                 'parameters': [{'name': 'x', 'value': 1, 'unit': 'V', 'basis': 'typical'}]}],
            'traceability': [{'requirement': 'R1', 'status': 'design_supported'},
                             {'requirement': 'R2', 'status': 'design_supported'}]})
        refresh.refresh(self.root)
        closure = self.read('design-closure.json')
        ok, typical = closure['calculations']
        self.assertEqual(('supported', 'bounded', False), (ok['conclusion'], ok['coverage'], 'rests_on' in ok))
        self.assertEqual(('conditional', 'vendor_data'), (typical['conclusion'], typical['rests_on']))
        self.assertEqual(['design_supported', 'conditional'], [r['status'] for r in closure['traceability']])
        self.assertEqual(hashlib.sha256((self.record / 'electrical-intent.json').read_bytes()).hexdigest(),
                         closure['intent_sha256'])
        self.assertEqual(([], []), refresh.refresh(self.root))


if __name__ == '__main__':
    unittest.main()
