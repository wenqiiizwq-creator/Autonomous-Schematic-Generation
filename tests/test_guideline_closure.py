"""Tasks 1.1 and 5.1 (user 2026-10-31: 请开始执行这个方案): the design declares its guideline scope, cites the shared
guideline rules it meets in its calculations and work items, holds the others not applicable with a reason, and hands
a rule closing after the schematic downstream with a work item. An empty rule library asks nothing."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import guideline_rules
import render_design_report
from audit_design_closure import audit, sha256

ASG = Path(__file__).resolve().parents[1]
SR = Path.home() / '.agents' / 'skills' / 'schematic-review'
SHARED = ('references/guideline-rules.json', 'references/guideline-rules.md', 'scripts/guideline_rules.py')


def setUpModule():
    global _env
    _env = mock.patch.dict('os.environ', {'HARDWARE_WIKI': str(Path(tempfile.gettempdir()) / 'asg-no-library')})
    _env.start()


def tearDownModule():
    _env.stop()


def card(rid, **changes):
    out = {'id': rid, 'title': '示例规则 ' + rid, 'spec': rid[:3], 'version': '0.1', 'status': 'active',
           'nature': 'shall', 'applies_when': {'board': True}, 'inputs': [], 'asg_action': '设计动作',
           'sr_check': '审查方法', 'source': [{'document': 'GB/T 17799.2', 'edition': '2023', 'clause': '表4', 'page': 9}],
           'closing_stage': 'schematic'}
    out.update(changes)
    return out


def library(*cards):
    out = copy.deepcopy(guideline_rules.load())
    out['rules'] = sorted(cards, key=lambda r: r['id'])
    out['content_sha256'] = guideline_rules.content_sha256(out['rules'])
    return out


LIBRARY = library(card('G01-001'),
                  card('G04-001', applies_when={'circuit_types': ['RS485']}),
                  card('G07-001', applies_when={'board': True}, closing_stage='pcb'),
                  card('G05-001', applies_when={'device_kinds': ['fuse']}))


class GuidelineClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.intent = self.root / 'intent.json'
        self.intent.write_text(json.dumps({'components': [{'ref': 'U1', 'lib_id': 'Interface:RS485', 'value': 'X'}]}))
        (self.root / 'design.txt').write_text('evidence\n')
        self.record = {
            'schema_version': 1, 'coverage': 'complete', 'intent_sha256': sha256(self.intent), 'guideline_version': 1,
            'guideline_scope': {'library_version': LIBRARY['library_version'], 'baseline': 'industrial_telecom',
                                'circuit_types': ['RS485'], 'device_kinds': [],
                                'not_applicable': []},
            'evidence': [{'id': 'E1', 'path': 'design.txt', 'sha256': sha256(self.root / 'design.txt'), 'locator': 'l1'}],
            'requirements': [{'id': 'R1', 'status': 'design_supported', 'refs': ['U1'], 'evidence': ['E1'],
                              'implementation': 'RS-485 接口', 'depends_on': []}],
            'work_items': [{'id': 'W1', 'stage': 'pcb', 'status': 'handoff', 'requirements': ['R1'], 'evidence': ['E1'],
                            'scope': 'layout_implementation', 'electrical_preconditions': [], 'owner': 'PCB',
                            'action': '端口防护靠近连接器', 'guidelines': ['G07-001']}],
            'calculations': [{'id': 'C1', 'requirements': ['R1'], 'evidence': ['E1'], 'refs': ['U1'],
                              'coverage': 'bounded', 'conclusion': 'supported', 'assumptions': [],
                              'omitted_terms': [], 'guidelines': ['G01-001', 'G04-001']}]}

    def run_audit(self, lib=LIBRARY):
        with mock.patch.object(guideline_rules, 'load', lambda *args: lib):
            return audit(self.record, self.intent, self.root)

    def codes(self, result):
        return {e['code'] for e in result['errors']} | {p['code'] for p in result['pending']}

    def test_every_applicable_rule_is_cited_and_listed(self):
        result = self.run_audit()
        self.assertFalse({c for c in self.codes(result) if c.startswith('guideline')}, result)
        self.assertEqual(result['guidelines']['applicable'], ['G01-001', 'G04-001', 'G07-001'])
        self.assertEqual(result['guidelines']['covered']['G07-001'], ['work:W1'])
        self.assertEqual(result['guidelines']['downstream'], ['G07-001'])

    def test_an_uncited_rule_is_pending_until_cited_or_held_not_applicable(self):
        self.record['calculations'][0]['guidelines'] = ['G01-001']
        self.assertIn('guideline_uncovered', self.codes(self.run_audit()))
        self.record['guideline_scope']['not_applicable'] = [{'id': 'G04-001', 'reason': '只接本板内部总线'}]
        result = self.run_audit()
        self.assertNotIn('guideline_uncovered', self.codes(result))
        self.assertEqual(result['guidelines']['not_applicable'], {'G04-001': '只接本板内部总线'})

    def test_a_downstream_rule_needs_a_work_item(self):
        self.record['work_items'][0]['guidelines'] = []
        self.record['calculations'][0]['guidelines'].append('G07-001')
        self.assertIn('guideline_downstream_without_work_item', self.codes(self.run_audit()))

    def test_unknown_and_not_applicable_citations_are_errors(self):
        self.record['calculations'][0]['guidelines'] += ['G09-099', 'G05-001']
        codes = self.codes(self.run_audit())
        self.assertIn('guideline_unknown', codes)
        self.assertIn('guideline_cited_not_applicable', codes)

    def test_the_scope_is_checked_against_the_library(self):
        self.record['guideline_scope']['circuit_types'] = ['RS-485']
        self.assertIn('guideline_scope', self.codes(self.run_audit()))
        self.record['guideline_scope']['circuit_types'] = ['RS485']
        self.record['guideline_scope']['library_version'] = '9.9.9'
        self.assertIn('guideline_scope', self.codes(self.run_audit()))

    def test_a_library_with_rules_asks_for_the_scope_and_an_empty_one_does_not(self):
        del self.record['guideline_version'], self.record['guideline_scope']
        self.assertIn('guideline_scope_missing', self.codes(self.run_audit()))
        result = self.run_audit(guideline_rules.load())
        self.assertNotIn('guideline_scope_missing', self.codes(result))
        self.assertEqual(result['guidelines'], 'NOT_CHECKED')

    def test_the_report_lists_the_rules_and_the_downstream_ones(self):
        self.record['guideline_scope']['device_kinds'] = ['fuse']
        self.record['guideline_scope']['not_applicable'] = [{'id': 'G05-001', 'reason': '输入由上级设备熔断'}]
        result = self.run_audit()
        with mock.patch.object(guideline_rules, 'load', lambda *args: LIBRARY):
            text = '\n'.join(render_design_report.render_guidelines(result['guidelines']))
        self.assertIn('| G04-001 | 示例规则 G04-001 | GB/T 17799.2 2023 表4 第9页 | calc:C1 | 原理图 |', text)
        self.assertIn('| G05-001 | 示例规则 G05-001 | GB/T 17799.2 2023 表4 第9页 | 不适用：输入由上级设备熔断 | 原理图 |', text)
        self.assertIn('| G07-001 | PCB | work:W1 | 设计动作 |', text.split('## 下游约束（共用规范）')[1])
        self.assertEqual(render_design_report.render_guidelines(None), [])

    @unittest.skipUnless((SR / SHARED[0]).is_file(), 'schematic-review without the rule library')
    def test_schematic_review_holds_the_same_files(self):
        for name in SHARED:
            self.assertEqual((SR / name).read_bytes(), (ASG / name).read_bytes(), name)


if __name__ == '__main__':
    unittest.main()
