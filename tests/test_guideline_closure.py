"""Tasks C1.1 and C5.2 (user 2026-10-31: 请开始执行这个方案): the design declares its guideline scope, cites the shared
guideline rules it meets in its calculations and work items, holds the others not applicable with a reason, and hands
a rule closing after the schematic downstream with a work item. An empty rule library asks nothing."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import guideline_criteria
from audit_design_closure import audit, sha256

ASG = Path(__file__).resolve().parents[1]
SHARED = guideline_criteria.SHARED_FILES


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
    out = copy.deepcopy(guideline_criteria.load())
    out['criteria'] = sorted(cards, key=lambda r: r['id'])
    out['content_sha256'] = guideline_criteria.content_sha256(out['criteria'])
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
        with mock.patch.object(guideline_criteria, 'load', lambda *args: lib):
            return audit(self.record, self.intent, self.root)

    def codes(self, result):
        return {e['code'] for e in result['errors']} | {p['code'] for p in result['pending']}

    def test_every_applicable_rule_is_cited_and_listed(self):
        result = self.run_audit()
        self.assertFalse({c for c in self.codes(result) if c.startswith('guideline')}, result)
        self.assertEqual(result['guidelines']['applicable'], ['G01-001', 'G04-001', 'G07-001'])
        self.assertEqual(result['guidelines']['covered']['G07-001'], ['work:W1'])
        self.assertEqual(result['guidelines']['downstream'], ['G07-001'])

    def test_an_uncited_rule_is_listed_not_pending(self):
        # user 2026-11-08 (按草案实施): only rules that rule out a scheme, change a selection or enter a calculation are cited.
        self.record['calculations'][0]['guidelines'] = ['G01-001']
        result = self.run_audit()
        self.assertFalse({c for c in self.codes(result) if c.startswith('guideline')}, result)
        self.assertEqual(result['guidelines']['uncited'], ['G04-001'])
        self.record['guideline_scope']['not_applicable'] = [{'id': 'G04-001', 'reason': '只接本板内部总线'}]
        result = self.run_audit()
        self.assertEqual(result['guidelines']['uncited'], [])
        self.assertEqual(result['guidelines']['not_applicable'], {'G04-001': '只接本板内部总线'})

    def test_an_evidence_entry_may_cite_a_rule(self):
        # user 2026-11-03: 照此写入 — a documentation rule hangs on the evidence entry that implements it.
        self.record['calculations'][0]['guidelines'] = ['G01-001']
        self.record['evidence'][0]['guidelines'] = ['G04-001']
        result = self.run_audit()
        self.assertEqual(result['guidelines']['covered']['G04-001'], ['evidence:E1'])
        self.record['evidence'][0]['guidelines'] = 'G04-001'
        self.assertIn('schema', self.codes(self.run_audit()))

    def test_a_component_requirement_may_cite_a_rule(self):
        self.record['calculations'][0]['guidelines'] = ['G01-001']
        record_dir = self.root / 'record'
        record_dir.mkdir()
        (record_dir / 'component-requirements.json').write_text(
            json.dumps({'components': [{'ref': 'U1', 'guidelines': ['G04-001']}]}), encoding='utf-8')
        result = self.run_audit()
        self.assertEqual(result['guidelines']['covered']['G04-001'], ['component:U1'])

    def test_the_six_external_interface_types_select_their_rules(self):
        real = guideline_criteria.load(guideline_criteria.BUNDLE_PATH)
        for name in ('DC_48V', 'AC_MAINS', 'INDUSTRIAL_DI', 'POE_PD', 'VEHICLE_28V', 'SHIP_AC'):
            self.assertIn(name, real['vocabulary']['circuit_types'])
        none = guideline_criteria.select(real, 'industrial_telecom', [], [])
        poe = guideline_criteria.select(real, 'industrial_telecom', ['POE_PD'], [])
        self.assertGreater(len(poe), len(none))

    def test_dc_24v_selects_its_own_rules_and_no_telecom_48v_rule(self):
        real = guideline_criteria.load(guideline_criteria.BUNDLE_PATH)
        ids = lambda types: {r['id'] for r in guideline_criteria.select(real, 'industrial_telecom', types, [])}
        added = ids(['DC_24V']) - ids([])
        self.assertEqual(added, {'G01-051', 'G01-052', 'G01-053', 'G01-054',
                                'G07-009', 'G07-012', 'G07-023', 'G07-034'})
        self.assertFalse({i for i in added if i.startswith('G01-')} & (ids(['DC_48V']) - ids([])))

    def test_library_1_7_0_board_identity_rules_and_usb_port_rules(self):
        # user 2026-11-02: 按草案入库 — the nine rules drafted from the 86 open-hardware boards are in the library;
        # the identity/placeholder rules apply board-wide, the Type-C CC rule only with USB.
        real = guideline_criteria.load(guideline_criteria.BUNDLE_PATH)
        ids = lambda types: {r['id'] for r in guideline_criteria.select(real, 'industrial_telecom', types, [])}
        new = {'G02-036', 'G02-037', 'G02-038', 'G02-039', 'G03-059', 'G04-101', 'G04-102', 'G04-103', 'G04-104'}
        self.assertTrue(new <= {r['id'] for r in real['criteria']})
        self.assertTrue({'G02-036', 'G02-037', 'G02-038'} <= ids([]))
        self.assertTrue({'G04-103', 'G04-104'} <= ids(['USB']) - ids([]))
        by_id = {r['id']: r for r in real['criteria']}
        self.assertIn('Type-C', by_id['G01-029']['title'])
        self.assertEqual(by_id['G01-029']['version'], '1.1')

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
        empty = dict(LIBRARY, criteria=[], content_sha256=guideline_criteria.content_sha256([]))
        result = self.run_audit(empty)
        self.assertNotIn('guideline_scope_missing', self.codes(result))
        self.assertEqual(result['guidelines'], 'NOT_CHECKED')

    def test_the_audit_binds_the_shared_layer_it_read(self):
        self.record['guideline_scope']['device_kinds'] = ['fuse']
        self.record['guideline_scope']['not_applicable'] = [{'id': 'G05-001', 'reason': '输入由上级设备熔断'}]
        result = self.run_audit()
        self.assertEqual(result['guidelines']['fingerprint_format'], 'shared-paths-sha256-v2')
        self.assertEqual(result['guidelines']['shared_sha256'], guideline_criteria.shared_versions(bundle=LIBRARY)['shared_sha256'])   # binds the actual test input
        self.assertEqual(result['guidelines']['covered']['G04-001'], ['calc:C1'])
        self.assertEqual(result['guidelines']['not_applicable']['G05-001'], '输入由上级设备熔断')

    def test_the_shared_directory_holds_exactly_the_shared_files(self):
        listed = {Path(n).name for n in SHARED if n.startswith('references/shared/')}
        self.assertEqual(sorted(p.name for p in guideline_criteria.SHARED_DIR.iterdir() if p.name != '__pycache__'), sorted(listed))
        self.assertRegex(guideline_criteria.shared_label(), r'^共用层 [0-9a-f]{12} \[shared-paths-sha256-v2\]，设计准则库 \S+，降额 v\d+$')

    def batch_library(self):
        return library(card('G01-001'), card('G04-001', applies_when={'circuit_types': ['RS485']}),
                       card('G07-001', closing_stage='pcb', coverage='handoff'),
                       card('G07-002', closing_stage='pcb', coverage='handoff'),
                       card('G08-001', coverage='project_input'), card('G08-002', coverage='project_input'))

    def batch_record(self):
        self.record['work_items'][0]['guidelines'] = ['G07-001', 'G07-002']
        self.record['evidence'][0].pop('guidelines', None)
        self.record['clarifications'] = []

    def test_one_work_item_hands_off_many_downstream_rules(self):
        self.batch_record()
        result = self.run_audit(self.batch_library())
        self.assertFalse({c for c in self.codes(result) if c.startswith('guideline')}, result)
        found = result['guidelines']
        self.assertEqual(found['covered']['G07-002'], ['work:W1'])
        self.assertEqual(found['uncited'], ['G08-001', 'G08-002'])     # project-input rules need no baseline answer now
        self.assertNotIn('by_coverage', found)

    def test_a_clarification_can_be_the_baseline_and_the_answer(self):
        self.batch_record()
        self.record['clarifications'] = [{'id': 'CL-ENV', 'question': '环境', 'requirement_field': 'x', 'blocks': [],
                                          'answer': {'decision': 'ANSWERED', 'text': '室内'}, 'merged_into': ['R1']}]
        self.record['guideline_project_input'] = {'baseline': ['CL-ENV'], 'answers': {'G08-001': 'CL-ENV', 'G08-002': 'CL-ENV#答复'}}
        self.assertNotIn('guideline_project_input', self.codes(self.run_audit(self.batch_library())))

    def test_handoff_rules_share_a_closed_item_or_a_table_without_per_rule_evidence(self):
        self.batch_record()
        self.record['work_items'][0].update(status='closed', closure={'type': 'x'})
        codes = self.codes(self.run_audit(self.batch_library()))
        self.assertNotIn('guideline_evidence_repeated', codes)
        self.assertNotIn('guideline_work_without_evidence', codes)
        self.batch_record()
        self.record['work_items'][0]['guidelines'] = []
        self.record['evidence'][0]['guidelines'] = ['G07-001', 'G07-002']
        result = self.run_audit(self.batch_library())
        self.assertNotIn('guideline_downstream_without_work_item', self.codes(result))
        self.assertEqual(result['guidelines']['covered']['G07-001'], ['evidence:E1'])

    def test_a_calculation_does_not_hand_a_rule_off(self):
        self.batch_record()
        self.record['work_items'][0]['guidelines'] = []
        self.record['calculations'][0]['guidelines'] += ['G07-001', 'G07-002']
        self.assertIn('guideline_downstream_without_work_item', self.codes(self.run_audit(self.batch_library())))

    def test_item_rules_still_trip_the_repeated_evidence_check_beside_a_batch(self):
        # the calibration board's single closed item citing 205 rules stays refused
        rules = ['G01-%03d' % n for n in range(1, 5)]
        lib = library(*[card(r) for r in rules], card('G07-001', closing_stage='pcb', coverage='handoff'))
        self.record['calculations'][0]['guidelines'] = []
        self.record['work_items'][0].update(status='closed', closure={'type': 'x'}, guidelines=rules,
                                            guideline_evidence={r: 'E1#一处' for r in rules})
        self.assertIn('guideline_evidence_repeated', self.codes(self.run_audit(lib)))

    def test_the_library_checks_the_field(self):
        field_errors = lambda *cards: [e for e in guideline_criteria.bundle_errors(library(*cards))
                                       if ': coverage must' in e or 'a handoff rule closes' in e]
        self.assertEqual(field_errors(card('G01-001'), card('G07-001', closing_stage='pcb', coverage='handoff'),
                                      card('G08-001', coverage='project_input'), card('G08-002', coverage='item')), [])
        self.assertEqual(len(field_errors(card('G07-001', coverage='batch'))), 1)
        self.assertEqual(len(field_errors(card('G07-001', coverage='handoff'))), 1)   # closing_stage is schematic

    def test_local_installed_release_matches_its_manifest(self):
        manifest = guideline_criteria.verify_installed(ASG)
        self.assertEqual(manifest['payload'], guideline_criteria.shared_files(ASG))
        self.assertEqual(manifest['fingerprint'], guideline_criteria.shared_digest(ASG))


if __name__ == '__main__':
    unittest.main()
