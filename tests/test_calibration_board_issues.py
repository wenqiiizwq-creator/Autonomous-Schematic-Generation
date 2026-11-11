"""Process issues from the industrial I/O calibration board run (~/Documents/ASG-calibration/industrial-io-rs485-can/
record/issues.md; user 2026-11-02: 这里面找到的问题，请提醒主对话进行修改). Each fix has a failing and a passing case."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_design_closure import audit, sha256  # noqa: E402
import guideline_criteria  # noqa: E402
from test_estimate_margins import Fixture  # noqa: E402
import test_guideline_closure  # noqa: E402
LIBRARY = test_guideline_closure.LIBRARY


def setUpModule():
    global _env
    _env = mock.patch.dict('os.environ', {'HARDWARE_WIKI': str(Path(tempfile.gettempdir()) / 'asg-no-library')})
    _env.start()


def tearDownModule():
    _env.stop()


class ModelLimitTests(Fixture):
    """#23: a limit ASG set itself shows its number in its reason and agrees with the number the check's name gives."""

    def model_check(self, **changes):
        check = {'name': '115.2 kbit/s 对 线长曲线 100 kbit/s', 'value': 115.2, 'operator': '<=', 'limit': 200,
                 'unit': 'kbit/s', 'limit_basis': 'model', 'limit_reason': '常见经验曲线 1200 m 约 100 kbit/s'}
        check.update(changes)
        self.calc['checks'].append(check)

    def test_a_name_and_limit_that_disagree_fail(self):
        self.model_check()
        self.assertIn('check_name_contradicts_limit', self.codes())

    def test_the_model_limit_appears_in_its_reason(self):
        self.model_check(limit=100, value=90, limit_reason='常见经验曲线，线长 1200 m')
        codes = self.codes()
        self.assertIn('model_limit_not_in_reason', codes)
        self.assertNotIn('check_name_contradicts_limit', codes)

    def test_a_consistent_model_limit_passes(self):
        self.model_check(limit=100, value=90)
        codes = self.codes()
        self.assertFalse({'model_limit_not_in_reason', 'check_name_contradicts_limit'} & codes, codes)

    def test_numbers_before_the_comparison_are_not_the_limit(self):
        self.calc['checks'][1]['name'] = '21 V 输出时峰值 对 动作下限'
        self.assertNotIn('check_name_contradicts_limit', self.codes())


class CheckEstimateTests(Fixture):
    """#6: a check names the estimates it rests on; without that the risk says it took the calculation's largest."""

    def setUp(self):
        super().setUp()
        self.calc['checks'][1]['value'] = 96.9      # 0.7 % short of 97.6 V against a ±10 % estimate

    def test_a_check_resting_on_no_estimate_carries_no_margin_risk(self):
        self.calc['checks'][1]['estimates'] = []
        result = self.run_audit()
        self.assertEqual([], result['estimate_margins'])
        self.assertNotIn('estimate_margin_risk_without_improvement', {e['code'] for e in result['errors']})

    def test_without_estimates_the_calculations_largest_is_named(self):
        result = self.run_audit()
        self.assertEqual('calculation_max', result['estimate_margins'][0]['uncertainty_from'])
        self.assertIn('写 estimates', json.dumps(result['errors'], ensure_ascii=False))

    def test_named_estimates_are_used(self):
        self.calc['checks'][1]['estimates'] = ['漏感尖峰']
        result = self.run_audit()
        self.assertEqual('estimates', result['estimate_margins'][0]['uncertainty_from'])

    def test_an_unknown_estimate_name_is_a_schema_error(self):
        self.calc['checks'][1]['estimates'] = ['不存在']
        self.assertIn('schema', self.codes())


class MergedClarificationTests(Fixture):
    """#8: an answer folded into an existing requirement is cited there instead of copied into a duplicate requirement."""

    def setUp(self):
        super().setUp()
        self.record['requirements'][0]['text'] = '反激主开关；RS-485 速率 115.2 kbit/s，线长 1200 m。'
        self.record['clarifications'] = [{
            'id': 'CL-485', 'found_in': '需求 2.3', 'question': '速率和线长？', 'requirement_text': '未写',
            'proposed_requirement': 'RS-485 速率 115.2 kbit/s，线长 1200 m。', 'requirement_ids': ['R1'],
            'answer': {'decision': 'ADOPTED_PROPOSAL', 'text': 'RS-485 速率 115.2 kbit/s，线长 1200 m。', 'by': 'user',
                       'date': '2026-11-02', 'source': {'source': 'chat', 'locator': '第 3 问'},
                       'requirement_files': {'decision': 'KEPT'}, 'merged_into': 'R1'}}]

    def test_a_merged_answer_cited_by_its_requirement_passes(self):
        self.record['requirements'][0]['clarifications'] = ['CL-485']
        self.assertNotIn('clarification_not_written_back', self.codes())

    def test_the_requirement_must_cite_the_clarification(self):
        self.assertIn('clarification_not_written_back', self.codes())

    def test_a_quote_keeps_every_number_of_the_answer(self):
        self.record['requirements'][0]['clarifications'] = ['CL-485']
        self.record['clarifications'][0]['answer']['merged_quote'] = '线长 1200 m'
        self.assertIn('clarification_not_written_back', self.codes())
        self.record['clarifications'][0]['answer']['merged_quote'] = 'RS-485 速率 115.2 kbit/s，线长 1200 m'
        self.assertNotIn('clarification_not_written_back', self.codes())


class GuidelineEvidenceTests(unittest.TestCase):
    """#9/#24: a closed work item covers a rule only where it points at the place that does it."""
    setUp = test_guideline_closure.GuidelineClosureTests.setUp

    def closed_item(self, ids, evidence=None):
        self.record['work_items'].append({'id': 'W-DOC', 'stage': 'design', 'status': 'closed', 'requirements': ['R1'],
                                          'evidence': ['E1'], 'guidelines': ids,
                                          **({'guideline_evidence': evidence} if evidence is not None else {})})
        self.record['requirements'][0]['depends_on'] = ['W-DOC']

    def audit_codes(self):
        with mock.patch.object(guideline_criteria, 'load', lambda *a: LIBRARY):
            return {e['code'] for e in audit(self.record, self.intent, self.root)['errors']}

    def test_a_closed_item_without_evidence_does_not_cover(self):
        self.closed_item(['G01-001'])
        self.assertIn('guideline_work_without_evidence', self.audit_codes())

    def test_each_rule_points_at_its_own_place(self):
        self.closed_item(['G01-001'], {'G01-001': 'E1#第 2 节 需求编号表'})
        self.assertNotIn('guideline_work_without_evidence', self.audit_codes())

    def test_one_place_for_many_rules_is_a_batch_citation(self):
        from audit_design_closure import audit_guideline_evidence
        found = []
        ids = ['G01-00%d' % i for i in range(1, 6)]
        audit_guideline_evidence('W-DOC', {'evidence': ['E1'], 'guideline_evidence': {g: 'E1#全文' for g in ids}},
                                 ids, lambda code, item: found.append(code))
        self.assertEqual(['guideline_evidence_repeated'], found)



import inspect  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import test_deliver  # noqa: E402
import deliver  # noqa: E402
from schematic_layout import part_classes as pc  # noqa: E402
from schematic_layout import component_requirements as cr  # noqa: E402
from schematic_layout import recipes, generate, net_roles  # noqa: E402
from schematic_layout.geometry import Box  # noqa: E402
from schematic_layout.reference_contract import verify_reference  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class ClassificationTests(unittest.TestCase):
    """#7 crystals by specification, #21 connector ratings, #18/#19 a surge protection device is a TVS, #5 Kind words."""

    def intent(self, **changes):
        out = {'components': [{'ref': 'Y1', 'lib_id': 'Device:Crystal', 'value': '8MHz 12pF ±20ppm'},
                              {'ref': 'J1', 'lib_id': 'Connector:Conn_01x02', 'value': 'Conn 2P 300V 8A'}],
               'nets': {'VIN': ['J1.1'], 'GND': ['J1.2'], 'X1': ['Y1.1'], 'X2': ['Y1.2']},
               'net_roles': {'VIN': 'power'}, 'high_voltage_nets': []}
        out.update(changes)
        return out

    def test_a_common_crystal_and_a_rated_connector_pass(self):
        self.assertEqual([], pc.audit_identity(self.intent(), [])[0])

    def test_a_crystal_bought_to_spec_writes_its_spec(self):
        intent = self.intent()
        intent['components'][0]['value'] = '8MHz'
        self.assertIn('负载电容', pc.audit_identity(intent, [])[0][0])

    def test_a_crystal_contract_may_be_bought_to_spec(self):
        comp = self.intent()['components'][0]
        entry = {'ref': 'Y1', 'kind': 'crystal', 'purpose': 'MCU 主时钟', 'definition_status': 'pending', 'gaps': ['CL'],
                 'display': 'note', 'required_parameters': ['load_capacitance'], 'requirements': [],
                 'procurement': {'mode': 'spec', 'reason': '常规晶体'}, 'selection': {'status': 'not_selected'}}
        self.assertFalse([e for e in cr.entry_errors(entry, comp) if 'needs mpn' in e])
        entry['binding_dependencies'] = ['频温曲线']
        self.assertTrue([e for e in cr.entry_errors(entry, comp) if 'needs mpn' in e])

    def test_a_connector_on_a_rail_writes_its_ratings(self):
        intent = self.intent()
        intent['components'][1]['value'] = 'Conn 2P'
        self.assertIn('额定电压', pc.audit_identity(intent, [])[0][0])

    def test_an_undeclared_high_voltage_list_is_named_as_the_reason(self):
        intent = self.intent()
        del intent['high_voltage_nets']
        self.assertIn('没写 high_voltage_nets', ' '.join(pc.audit_identity(intent, [])[0]))

    def test_a_surge_protection_device_is_a_tvs_and_a_varistor_stays_a_varistor(self):
        self.assertEqual({'tvs'}, pc.cues('TVS3300 33-V Flat-Clamp Surge Protection Device'))
        self.assertEqual({'varistor'}, pc.cues('Metal Oxide Varistor surge protection device'))

    def test_a_lan_magnetic_module_is_a_transformer(self):
        self.assertEqual({'transformer'}, pc.cues('1Gigabit Magnetic Modules'))
        self.assertNotIn('transformer', pc.cues('Magnetic shielded power inductor'))

    def test_maker_wordings_name_their_kind(self):
        # Titles from the library that named no kind before (Bourns SRF, Würth WE-CNSW, Littelfuse AXGD1, NATIONSTAR)
        self.assertEqual({'common_mode_choke'}, pc.cues('SRF3216 Series - Common Mode Chip Inductors'))
        self.assertEqual({'common_mode_choke'}, pc.cues('WE-CNSW SMT Common Mode Line Filter'))
        self.assertEqual({'tvs'}, pc.cues('XTREME-GUARD™ ESD Suppressors'))
        self.assertEqual({'diode'}, pc.cues('片 式 发 光 二 极 管'))
        self.assertEqual({'zener'}, pc.cues('稳压二极管'))
        self.assertEqual({'common_mode_choke'}, pc.cues('共模电感'))
        self.assertEqual({'varistor'}, pc.cues('贴片压敏电阻'))
        self.assertEqual({'crystal'}, pc.cues('ＣＲＹＳＴＡＬ ＵＮＩＴ'))

    def test_a_chinese_quote_is_looked_for_as_written(self):
        self.assertEqual('片式发光二极管', pc.squash_text('片 式 发 光 二 极 管'))
        self.assertNotIn(pc.squash_text('稳压二极管'), pc.squash_text('片式发光二极管'))

    def test_a_project_symbol_named_after_its_part_is_no_placeholder(self):
        from audit_design_closure import audit_placeholders
        found = []
        audit_placeholders({'components': [{'ref': 'Q1', 'lib_id': 'iio:STL110N10F7', 'value': 'STL110N10F7'},
                                           {'ref': 'Y1', 'lib_id': 'Device:Crystal_GND24', 'value': 'Crystal_GND24'}]},
                           lambda code, item: found.append(item))
        self.assertEqual(1, len(found))
        self.assertIn('Y1', found[0])

    def test_an_unfitted_part_is_marked_by_dnp_not_by_its_value(self):
        # G09-018: DNP and the BOM assembly column carry the state; NC/DNP written into the value does not.
        from audit_design_closure import audit_placeholders
        found = []
        audit_placeholders({'components': [{'ref': 'R1', 'lib_id': 'Device:R', 'value': '10k DNP'},
                                           {'ref': 'R2', 'lib_id': 'Device:R', 'value': 'NC'},
                                           {'ref': 'R3', 'lib_id': 'Device:R', 'value': '0R', 'dnp': True},
                                           {'ref': 'U1', 'lib_id': 'iio:NC7SZ125', 'value': 'NC7SZ125'}]},
                           lambda code, item: found.append((code, item)))
        self.assertEqual(['R1', 'R2'], [item.split('：')[0] for code, item in found if code == 'dnp_in_value'])

    def test_a_common_mlcc_writes_its_dielectric(self):
        # G09-021 (g09_commodity_fields mlcc: 容值、耐压、介质): the dielectric is checked by script.
        intent = self.intent(components=[{'ref': 'C1', 'lib_id': 'Device:C', 'value': '100nF 50V'}], nets={},
                             net_roles={})
        self.assertIn('介质', ' '.join(pc.audit_identity(intent, [])[0]))
        intent['components'][0]['value'] = '100nF 50V X7R'
        self.assertEqual([], pc.audit_identity(intent, [])[0])
        intent['components'][0].update(value='10pF', fields={'Specification': '50V C0G 0402'})
        self.assertEqual([], pc.audit_identity(intent, [])[0])
        intent['components'][0].update(lib_id='Device:C_Polarized', value='100uF 35V', fields={})
        self.assertEqual([], pc.audit_identity(intent, [])[0])

    def test_a_kind_outside_the_vocabulary_fails_at_the_closure_audit(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        intent = tmp / 'intent.json'
        intent.write_text(json.dumps({'components': [{'ref': 'D1', 'lib_id': 'Device:D', 'value': 'SS34',
                                                      'fields': {'Kind': 'schottky'}}]}))
        result = audit({'schema_version': 1, 'intent_sha256': sha256(intent)}, intent, tmp)
        self.assertIn('kind_not_in_vocabulary', {e['code'] for e in result['errors']})


class ToolMessageTests(unittest.TestCase):
    """#1, #3, #11, #15, #16: errors name what to change and the docs match the code."""

    def test_the_overlap_names_the_parts(self):
        sym = lambda ref, box: type('S', (), {'ref': ref, 'body': box})()
        found = generate.body_conflicts([sym('U1', Box(0, 0, 10, 10)), sym('C1', Box(10.5, 0, 12, 2)),
                                         sym('R1', Box(30, 30, 32, 32))])
        self.assertEqual([('U1', 'C1')], found)

    def test_the_documented_justify_is_the_codes(self):
        params = list(inspect.signature(recipes.Sheet.justify).parameters)[1:]
        text = (ROOT / 'references' / 'drawing-recipes.md').read_text(encoding='utf-8')
        for args in re.findall(r'justify\(([^)]*)\)', text):
            self.assertEqual(len(params), len([a for a in args.split(',') if a.strip()]), args)

    def test_an_inline_requirement_points_to_the_note(self):
        self.assertIn('display to note', recipes.field_failure('R1', {'performance_contract': {'display': 'inline'}}))
        self.assertNotIn('display to note', recipes.field_failure('R1', {}))

    def test_a_supply_node_declared_signal_is_told_to_be_power(self):
        with self.assertRaisesRegex(ValueError, 'declare it power in net_roles'):
            net_roles.validate_net_roles({'nets': {'VS_N': []}, 'net_roles': {'VS_N': 'signal'}}, ['VS_N'])

    def test_performance_notes_returns_its_line_count(self):
        fake = type('F', (), {})()
        fake.components = {'R1': {'performance_contract': {
            'ref': 'R1', 'purpose': 'p', 'definition_status': 'complete', 'display': 'note',
            'selection': {'status': 'not_selected'},
            'requirements': [{'parameter': 'power', 'op': 'ge', 'value': 1, 'unit': 'W'}]}}}
        fake.placed = []
        fake.text = lambda text, at, font: fake.placed.append(text)
        self.assertEqual(2, recipes.Sheet.performance_notes(fake, (10, 10)))
        self.assertEqual(2, len(fake.placed[0].splitlines()))

    def test_performance_note_width_is_measured_and_overflow_fails_at_build(self):
        # Matrix R2 (2026-11-04): CR titles mixing Chinese and Latin text wrapped by character count, and the
        # wrapped title was no longer found on the PDF. Sample: R2's CR-R301 entry (67.0 columns measured).
        fake = type('F', (), {})()
        fake.components = {'R301': {'performance_contract': {
            'ref': 'R301', 'purpose': '主路检流，设定 LM5069 限流 14.6～18.8 A', 'definition_status': 'complete',
            'display': 'note', 'selection': {'status': 'by_bom_spec'},
            'requirements': [{'parameter': 'resistance', 'op': 'eq', 'value': 0.0033, 'unit': 'ohm'},
                             {'parameter': 'tolerance', 'op': 'le', 'value': 1, 'unit': '%'}]}}}
        fake.placed = []
        fake.text = lambda text, at, font: fake.placed.append(text)
        title = 'CR-R301: 主路检流，设定 LM5069 限流 14.6～18.8 A [性能定义完整; BOM规格已写全]'
        self.assertLessEqual(len(title), 60)      # by character count it fit width=60 ...
        with self.assertRaisesRegex(ValueError, r'CR-R301 "CR-R301: 主路检流.*67\.0 columns > width=60.*use width=67'):
            recipes.Sheet.performance_notes(fake, (10, 10), width=60)   # ... measured it does not
        self.assertEqual([], fake.placed)
        self.assertEqual(3, recipes.Sheet.performance_notes(fake, (10, 10), width=67))
        self.assertEqual(title, fake.placed[0].splitlines()[0])   # the title stays on one line


class StageWithoutChecksTests(unittest.TestCase):
    """#17: a stage proven by its parts' pin maps alone lists no peripheral check."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base)
        for p in (ROOT / 'tests/fixtures/reference_contract').iterdir():
            shutil.copy2(p, self.base / p.name)
        self.contract = json.loads((self.base / 'contract.json').read_text())
        self.stage = self.contract['features'][0]['stages'][0]

    def test_a_pin_mapped_stage_passes_without_checks(self):
        self.stage.update(refs=['U1'], checks=[])
        result = verify_reference(self.base / 'netlist.xml', self.contract, self.base)
        self.assertEqual('PASS', result['features'][self.contract['features'][0]['id']]['stages'][0]['status'])

    def test_a_stage_without_checks_needs_pin_maps(self):
        self.stage.update(refs=['C1'], checks=[])     # C1 has no pin map
        with self.assertRaisesRegex(ValueError, 'every ref needs a pin map'):
            verify_reference(self.base / 'netlist.xml', self.contract, self.base)


class ForReviewTests(unittest.TestCase):
    """#20: a run for the visual review stops after the automatic checks."""
    setUp = test_deliver.DeliverTests.setUp
    write_config = test_deliver.DeliverTests.write_config

    def test_it_stops_after_the_checks(self):
        import os
        os.environ['STUB_STATUS'] = '{}'
        os.environ['STUB_LOG'] = str(self.stubs / 'calls.jsonl')
        self.addCleanup(os.environ.pop, 'STUB_STATUS', None)
        self.addCleanup(os.environ.pop, 'STUB_LOG', None)
        code, steps, failure = deliver.deliver(self.root, log=lambda *_: None, for_review=True)
        self.assertEqual((0, None, '自动检查'), (code, failure, steps[-1]['step']))
        self.assertFalse((self.root / '设计报告.md').exists())


class ProjectionDigestTests(unittest.TestCase):
    """#26: editing a calculation script does not change the drawn RequirementsSHA256."""

    def test_source_hashes_do_not_enter_the_projection_digest(self):
        record = {'components': [{'ref': 'R1', 'requirements': [
            {'parameter': 'power', 'value': 1, 'source': {'path': 'calc.py', 'sha256': 'a' * 64, 'locator': 'l1'}}]}]}
        other = copy.deepcopy(record)
        other['components'][0]['requirements'][0]['source']['sha256'] = 'b' * 64
        self.assertEqual(cr.projection_digest(record), cr.projection_digest(other))
        other['components'][0]['requirements'][0]['value'] = 2
        self.assertNotEqual(cr.projection_digest(record), cr.projection_digest(other))


if __name__ == '__main__':
    unittest.main()
