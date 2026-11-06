"""Task 2.2, judged by stress-spec.md (user 2026-10-27): a check that names a derating rule uses the rule's value at the
project's level; a stress over the derated value but within the rating passes with a stress risk and an improvement, one
over the rating fails; only the stresses written are checked, and a stress against a rating that names no rule is a hint;
the level is a requirement and says where it was decided."""
import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import guideline_criteria
import audit_design_closure as adc
from audit_design_closure import audit, sha256

SR_PASSIVE = Path.home() / '.agents' / 'skills' / 'schematic-review' / 'scripts' / 'checkers' / 'passive_stress.py'


def setUpModule():
    global _env
    # the installed shared guideline rules would ask every record here for its guideline scope; test_guideline_closure
    # covers that with its own library
    library = guideline_criteria.load(guideline_criteria.BUNDLE_PATH)
    library.update(library_version='0.0.0', specs={}, criteria=[],
                   content_sha256=guideline_criteria.content_sha256([], library.get('engineering_values')))
    empty = Path(tempfile.gettempdir()) / 'asg-empty-guideline-criteria.json'
    empty.write_text(guideline_criteria.dump(library), encoding='utf-8')
    _env = mock.patch.dict('os.environ', {'HARDWARE_WIKI': str(Path(tempfile.gettempdir()) / 'asg-no-library'),
                                          'GUIDELINE_CRITERIA': str(empty), 'GUIDELINE_CRITERIA_TESTING': '1'})
    _env.start()


def tearDownModule():
    _env.stop()


class DeratingAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.intent = self.root / 'intent.json'
        self.intent.write_text(json.dumps({'components': [
            {'ref': 'Q1', 'lib_id': 'Transistor_FET:Q_NMOS_GDS', 'value': 'NMOS', 'mpn': 'X650N'},
            {'ref': 'C1', 'lib_id': 'Device:C', 'value': '100n'}]}))
        (self.root / 'design.txt').write_text('evidence\n')
        self.record = {
            'schema_version': 1, 'coverage': 'complete', 'intent_sha256': sha256(self.intent),
            'parameter_version': 3, 'derating_version': 1,
            'derating': {'level': 'III', 'source': 'req:R-DER'},
            'evidence': [{'id': 'E1', 'path': 'design.txt', 'sha256': sha256(self.root / 'design.txt'), 'locator': 'l1'}],
            'requirements': [
                {'id': 'R1', 'status': 'design_supported', 'refs': ['Q1'], 'evidence': ['E1'], 'implementation': '反激主开关',
                 'depends_on': []},
                {'id': 'R-DER', 'status': 'design_supported', 'refs': [], 'evidence': ['E1'], 'implementation': '降额 III 级',
                 'depends_on': [], 'no_check_reason': '降额等级本身不对应电路'}],
            'work_items': [],
            'calculations': [{
                'id': 'C-VDS', 'requirements': ['R1'], 'evidence': ['E1'], 'refs': ['Q1'], 'coverage': 'bounded',
                'conclusion': 'supported', 'rests_on': None, 'omitted_terms': [],
                'parameters': [{'name': 'Vin', 'value': 373, 'unit': 'V', 'basis': 'requirement', 'source': 'req:R1'}],
                'checks': [{'name': '漏源电压', 'value': 560, 'operator': '<=', 'limit': 585, 'unit': 'V',
                            'derating_rule': 'MOS-VDS-S', 'ref': 'Q1', 'rating': 650,
                            'rating_source': 'datasheet:Datasheet/09_MOSFET/X - X650N.pdf#p2',
                            'limit_basis': 'standard', 'limit_source': 'standard:derating-rules#MOS-VDS-S'}]}]}

    def run_audit(self):
        return audit(self.record, self.intent, self.root)

    def codes(self):
        return {e['code'] for e in self.run_audit()['errors']}

    @property
    def check(self):
        return self.record['calculations'][0]['checks'][0]

    def deviate(self, value=600):
        self.check['value'] = value

    def test_a_check_within_the_derated_limit_passes(self):
        result = self.run_audit()
        self.assertEqual('PASS', result['status'], result['errors'])
        self.assertEqual({'level': 'III', 'source': 'req:R-DER', 'stress_risks': [], 'hints': [],
                          'severe_thresholds': {'loosest_level': 'III', 'junction_margin_c': 20, 'other_margin': 'uncertainty'}},
                         result['derating'])

    def test_the_level_is_a_requirement_or_a_deferred_clarification(self):
        self.record['derating']['level'] = 'IV'
        self.assertIn('derating_level_missing', self.codes())
        self.record['derating'].update(level='III', source='user:2026-10-27')
        self.assertIn('derating_level_without_source', self.codes())
        self.record['derating']['source'] = 'clarification:CL-DER'
        self.assertIn('derating_level_without_source', self.codes())   # no such clarification, so not deferred

    def test_the_limit_is_the_rules_value_at_the_level(self):
        self.check['limit'] = 600
        self.assertIn('derating_limit_mismatch', self.codes())
        self.record['derating']['level'] = 'II'           # II: 80% of 650 V
        self.check['limit'] = 520
        self.check['value'] = 500
        self.assertNotIn('derating_limit_mismatch', self.codes())
        del self.check['rating']
        self.assertIn('derating_rating_missing', self.codes())

    def test_the_rule_exists_fits_the_part_and_is_cited_as_the_spec(self):
        self.check['derating_rule'] = 'MOS-VDS-X'
        self.assertIn('derating_rule_unknown', self.codes())
        self.check['derating_rule'] = 'CAP-MLCC-CHIP-V'
        self.check['limit_source'] = 'standard:derating-rules#CAP-MLCC-CHIP-V'
        self.assertIn('derating_rule_kind', self.codes())
        self.check.update(derating_rule='MOS-VDS-S', limit_source='standard:T/CPSS 1013 表4')
        self.assertIn('derating_limit_source', self.codes())
        self.check['limit_source'] = 'standard:derating-rules#MOS-VDS-S'
        self.check['rating_source'] = '规格书'
        self.assertIn('derating_rating_without_source', self.codes())

    def test_over_the_derated_value_within_the_rating_is_a_stress_risk(self):
        self.deviate()
        self.assertIn('stress_risk_without_improvement', self.codes())
        self.check['improvement'] = '换 700 V 管或加钳位'
        result = self.run_audit()
        self.assertEqual('PASS', result['status'], result['errors'])
        self.assertEqual({'conclusion': 'supported', 'rests_on': None, 'reasons': []}, result['calculation_basis']['C-VDS'])
        risk = result['derating']['stress_risks'][0]
        self.assertEqual(('Q1', 'MOS-VDS-S', 600, 585, 650, '换 700 V 管或加钳位'),
                         (risk['ref'], risk['rule'], risk['value'], risk['limit'], risk['rating'], risk['improvement']))

    def test_a_negative_rating_is_compared_by_magnitude(self):
        # R8 (synthetic): a GaN off-state gate rated -10 V at 50% allows 5 V of magnitude; -8 V is over it, -4 V within.
        self.intent.write_text(json.dumps({'components': [
            {'ref': 'Q1', 'lib_id': 'Transistor_FET:Q_NMOS_GDS', 'value': 'GaN', 'mpn': 'X650G'}]}))
        self.record['intent_sha256'] = sha256(self.intent)
        self.check.update(name='关断负栅压', value=-8, limit=-5, rating=-10, derating_rule='GAN-VGS-OFF',
                          limit_source='standard:derating-rules#GAN-VGS-OFF', improvement='负压改 -3 V')
        result = self.run_audit()
        self.assertEqual('PASS', result['status'], result['errors'])
        self.assertEqual(['GAN-VGS-OFF'], [r['rule'] for r in result['derating']['stress_risks']])
        self.check['limit'] = 5                              # the allowed magnitude may be written either way
        self.assertNotIn('derating_limit_mismatch', self.codes())
        self.check['value'] = -4
        result = self.run_audit()
        self.assertEqual([], result['derating']['stress_risks'])
        self.assertEqual('supported', result['calculation_basis']['C-VDS']['conclusion'])
        self.check['value'] = -12                            # over the rating's magnitude
        self.assertEqual('failed', self.run_audit()['calculation_basis']['C-VDS']['conclusion'])

    def test_the_relay_rules_set_their_limits(self):
        # RLY-HOLD is a min_ratio (hold voltage >= 90% of the rated coil voltage); RLY-LIFE takes 1.0 at II and III
        # (no derating); RLY-PARALLEL is a text rule with no number to compare.
        self.intent.write_text(json.dumps({'components': [
            {'ref': 'Q1', 'lib_id': 'Transistor_FET:Q_NMOS_GDS', 'value': 'NMOS', 'mpn': 'X650N'},
            {'ref': 'K1', 'lib_id': 'Relay:G5LE-1', 'value': 'G5LE-1 12VDC', 'mpn': 'G5LE-1'}]}))
        self.record['intent_sha256'] = sha256(self.intent)
        self.record['derating']['level'] = 'II'
        source = 'datasheet:Datasheet/31_Relay/X - G5LE.pdf#p2'
        self.record['calculations'][0].update(refs=['K1'], checks=[
            {'name': '维持电压', 'value': 11.4, 'operator': '>=', 'limit': 10.8, 'unit': 'V', 'derating_rule': 'RLY-HOLD',
             'ref': 'K1', 'rating': 12, 'rating_source': source},
            {'name': '动作次数', 'value': 5e4, 'operator': '<=', 'limit': 1e5, 'unit': '次', 'derating_rule': 'RLY-LIFE',
             'ref': 'K1', 'rating': 1e5, 'rating_source': source},
            {'name': '触点不并联', 'value': 1, 'operator': '==', 'limit': 1, 'unit': '组', 'derating_rule': 'RLY-PARALLEL',
             'ref': 'K1'}])
        for c in self.record['calculations'][0]['checks']:
            c.update(limit_basis='standard', limit_source='standard:derating-rules#' + c['derating_rule'])
        result = self.run_audit()
        self.assertEqual('PASS', result['status'], result['errors'])
        self.record['calculations'][0]['checks'][1]['limit'] = 5e4
        self.assertIn('derating_limit_mismatch', self.codes())

    def test_over_the_rating_fails(self):
        self.deviate(700)
        self.check['improvement'] = '换 800 V 管'
        self.assertEqual('failed', self.run_audit()['calculation_basis']['C-VDS']['conclusion'])
        self.assertEqual([], self.run_audit()['derating']['stress_risks'])

    def test_only_the_stresses_written_are_checked(self):
        # A key part with one stress written is not asked for every rule of its type.
        self.assertEqual([], self.run_audit()['errors'])
        self.record['derating']['parts'] = {}      # an old declaration is ignored, not required
        self.assertEqual([], self.run_audit()['errors'])

    def test_a_stress_against_a_rating_without_a_rule_is_a_hint(self):
        for k in ('derating_rule', 'limit_basis', 'limit_source'):
            del self.check[k]
        self.check.update(limit_basis='guaranteed', limit_source='datasheet:Datasheet/09_MOSFET/X - X650N.pdf#p2', limit=650)
        result = self.run_audit()
        self.assertNotIn('derating_rule_available', {e['code'] for e in result['errors']})
        self.assertEqual(1, len(result['derating']['hints']))
        self.assertTrue(result['derating']['hints'][0].startswith('derating_rule_available C-VDS:漏源电压'))

    def add_connector(self, lib_id, value, current=5, operator='<='):
        intent = json.loads(self.intent.read_text())
        intent['components'].append({'ref': 'J1', 'lib_id': lib_id, 'value': value})
        self.intent.write_text(json.dumps(intent))
        self.record['intent_sha256'] = sha256(self.intent)
        self.record['requirements'][0]['refs'].append('J1')
        self.record['calculations'].append({
            'id': 'C-VBUS', 'requirements': ['R1'], 'evidence': ['E1'], 'refs': ['J1'], 'coverage': 'bounded',
            'conclusion': 'supported', 'rests_on': None, 'omitted_terms': [],
            'parameters': [{'name': 'Ivbus', 'value': current, 'unit': 'A', 'basis': 'requirement', 'source': 'req:R1'}],
            'checks': [{'name': 'VBUS 电流', 'value': current, 'operator': operator, 'limit': 5, 'unit': 'A', 'ref': 'J1',
                        'rating': 5, 'limit_basis': 'guaranteed', 'limit_source': 'datasheet:Datasheet/USB.pdf#p2'}]})
        return self.record['calculations'][-1]['checks'][0]

    def test_a_stress_against_a_rating_without_a_rule_is_judged_by_the_one_fitting_rule(self):
        # R8 (2026-10-28): VBUS 5 A on a 5 A USB-C receptacle passed with zero margin; USB-I allows 90 % at III, 4.5 A.
        check = self.add_connector('Connector:USB_C_Receptacle_USB2.0', 'USB_C_Receptacle')
        self.assertIn('stress_risk_without_improvement', self.codes())
        check['improvement'] = '换 6 A 母座或限流 4.5 A'
        result = self.run_audit()
        self.assertEqual('PASS', result['status'], result['errors'])
        risk = result['derating']['stress_risks'][0]
        self.assertEqual(('J1', 'USB-I', 5, 4.5, 5), (risk['ref'], risk['rule'], risk['value'], risk['limit'], risk['rating']))
        self.assertFalse(any(h.startswith('derating_rule_available C-VBUS') for h in result['derating']['hints']))

    def test_a_connector_no_type_names_takes_the_other_rule(self):
        self.add_connector('Connector:Screw_Terminal_01x02', 'Screw_Terminal_01x02')['improvement'] = '换 10 A 端子'
        risk = self.run_audit()['derating']['stress_risks'][0]
        self.assertEqual(('CONN-I', 4.25), (risk['rule'], risk['limit']))

    def test_within_the_implied_derated_value_is_only_a_hint(self):
        self.add_connector('Connector:USB_C_Receptacle_USB2.0', 'USB_C_Receptacle', current=4)
        result = self.run_audit()
        self.assertEqual([], result['derating']['stress_risks'])
        self.assertTrue(any(h.startswith('derating_rule_available C-VBUS') for h in result['derating']['hints']))

    def test_a_named_rule_or_another_comparison_is_not_reinterpreted(self):
        check = self.add_connector('Connector:USB_C_Receptacle_USB2.0', 'USB_C_Receptacle', current=4)
        check.update(derating_rule='CONN-I', limit=4.25, limit_basis='standard',
                     limit_source='standard:derating-rules#CONN-I', rating_source='datasheet:Datasheet/USB.pdf#p2')
        result = self.run_audit()
        self.assertNotIn('derating_limit_mismatch', {e['code'] for e in result['errors']})
        self.assertEqual([], result['derating']['stress_risks'])     # 4 A within CONN-I's 4.25 A, USB-I not applied
        for update in ({'limit_basis': 'requirement', 'limit_source': 'req:R1'}, {'operator': '>='}):
            self.setUp()
            check = self.add_connector('Connector:USB_C_Receptacle_USB2.0', 'USB_C_Receptacle')
            check.update(update)
            self.assertEqual([], self.run_audit()['derating']['stress_risks'], update)

    def test_a_common_part_is_not_checked_one_by_one(self):
        errors = [e['item'] for e in self.run_audit()['errors']]
        self.assertFalse(any(e.startswith('C1') for e in errors), errors)

    def add_resistor(self, value, watts, footprint='Resistor_SMD:R_0603_1608Metric'):
        intent = json.loads(self.intent.read_text())
        intent['components'].append({'ref': 'R1', 'lib_id': 'Device:R', 'value': value, 'footprint': footprint})
        self.intent.write_text(json.dumps(intent))
        self.record['intent_sha256'] = sha256(self.intent)
        self.record['requirements'][0]['refs'].append('R1')
        self.record['calculations'].append({
            'id': 'C-R1', 'requirements': ['R1'], 'evidence': ['E1'], 'refs': ['R1'], 'coverage': 'bounded',
            'conclusion': 'supported', 'rests_on': None, 'omitted_terms': [],
            'parameters': [{'name': 'Vin', 'value': 373, 'unit': 'V', 'basis': 'requirement', 'source': 'req:R1'}],
            'checks': [{'name': '电阻功耗', 'value': watts, 'operator': '<=', 'limit': 0.1, 'unit': 'W', 'ref': 'R1',
                        'limit_basis': 'derived'}]})

    def test_a_resistor_whose_power_matters_writes_its_rating(self):
        # III level: 0603's weakest part 1/16 W × 0.5 × 0.8 = 0.025 W; 0.05 W matters and needs ≥ 0.0625 W written.
        self.add_resistor('1k/1%', 0.05)
        errors = [e for e in self.run_audit()['errors'] if e['code'] == 'resistor_power_rating_missing']
        self.assertEqual(1, len(errors), self.run_audit()['errors'])
        self.assertIn('0.0625 W', errors[0]['item'])

    def test_a_written_rating_or_a_small_power_needs_nothing(self):
        self.add_resistor('1k/1%/0.125W', 0.05)
        self.assertNotIn('resistor_power_rating_missing', self.codes())
        self.setUp()
        self.add_resistor('1k/1%', 0.02)          # below 0.025 W the weakest 0603 part is enough
        self.assertNotIn('resistor_power_rating_missing', self.codes())

    def test_without_a_level_the_power_rating_follows_level_i(self):
        # 2026-10-29 (user: 删掉 2 倍，按降额规范取): no level takes the spec's unset_level, I (RES-SMD-P 0.7):
        # 0603's weakest part 1/16 W × 0.5 × 0.7 = 0.021875 W < 0.023 W ≤ 0.025 W (level III)
        self.add_resistor('1k/1%', 0.023)
        self.assertNotIn('resistor_power_rating_missing', self.codes())
        self.record['derating'] = {}
        errors = [e for e in self.run_audit()['errors'] if e['code'] == 'resistor_power_rating_missing']
        self.assertEqual(1, len(errors))
        self.assertIn('0.03286 W', errors[0]['item'])
        self.assertIn('降额等级未定按 I 级', errors[0]['item'])

    def test_a_resistor_without_a_footprint_is_judged_as_0402(self):
        self.add_resistor('1k/1%', 0.03, footprint='')   # 0402 1/16 W too: 0.03 > 0.025
        self.assertIn('resistor_power_rating_missing', self.codes())
        self.setUp()
        self.add_resistor('1k/1%', 0.03, footprint='Resistor_SMD:R_1206_3216Metric')   # 0.125 × 0.5 × 0.8 = 0.05
        self.assertNotIn('resistor_power_rating_missing', self.codes())

    def test_the_floors_are_the_shared_layers(self):
        # 2026-11-02 (user: 最弱档收进共用层): the same file SR's passive_stress reads, no copy in either skill
        import guideline_criteria
        floors = guideline_criteria.commodity_floors()['chip_resistor']['packages']
        self.assertEqual({p: v['power_w_70c'] for p, v in floors.items()}, adc.RESISTOR_FLOORS)
        self.assertEqual((adc.WEAKEST_SHARE, adc.ASSUMED_PACKAGE),
                         (guideline_criteria.engineering_value('weakest_share'), guideline_criteria.engineering_value('assumed_resistor_package')))
        self.assertEqual(adc.WEAKEST_SHARE, 0.5)

    def test_derating_needs_a_layered_record(self):
        self.record['parameter_version'] = 1
        self.assertIn('schema', self.codes())


class SevereStressTests(unittest.TestCase):
    """Matrix R2 (2026-11-04): LM70880 estimated at 146 °C against 95 °C (level II IC-SW-TJ) and 150 °C absolute was only
    a pass with risk. Beyond the loosest level's value, or within est_junction_margin of the rating, needs an unclosed
    design/validation work item: P1 when the margin is short, P2 when only beyond every level."""

    def setUp(self):
        base = DeratingAuditTests('run_audit')
        base.setUp()
        self.addCleanup(base.tmp.cleanup)
        self.base = base
        base.intent.write_text(json.dumps({'components': [{'ref': 'U1', 'lib_id': 'MATRIX:LM70880-Q1', 'value': 'LM70880',
                                                            'mpn': 'LM70880QRRXRQ1'}]}))
        base.record['intent_sha256'] = sha256(base.intent)
        base.record['derating'] = {'level': 'II', 'source': 'req:R-DER'}
        base.record['requirements'][0]['refs'] = ['U1']
        calc = base.record['calculations'][0]
        calc.update(id='C-TJ', refs=['U1'])
        calc['checks'] = [{'name': 'U1 结温', 'value': 146.2, 'operator': '<=', 'limit': 95, 'unit': '℃', 'ref': 'U1',
                           'derating_rule': 'IC-SW-TJ', 'rating': 150, 'limit_basis': 'standard',
                           'limit_source': 'standard:derating-rules#IC-SW-TJ', 'improvement': '贴壳散热',
                           'rating_source': 'datasheet:Datasheet/08/TI - LM70880-Q1.pdf#p6'}]

    @property
    def check(self):
        return self.base.record['calculations'][0]['checks'][0]

    def item(self, **kw):
        row = {'id': 'W-TJ', 'stage': 'validation', 'status': 'handoff', 'requirements': ['R1'], 'evidence': ['E1'],
               'owner': '验证方', 'action': '样机测结温', 'consequence_class': 'damage', 'occurrence': 'fault'}
        row.update(kw)
        self.base.record['work_items'] = [row]
        self.base.record['requirements'][0]['depends_on'] = ['W-TJ']
        self.check['work_item'] = 'W-TJ'

    def codes(self):
        return {e['code'] for e in self.base.run_audit()['errors']}

    def test_near_the_rating_needs_a_p1_item(self):
        self.assertIn('severe_stress_without_work_item', self.codes())
        risk = self.base.run_audit()['derating']['stress_risks'][0]
        self.assertEqual(('P1', True, 105), (risk['required_severity'], risk['beyond_levels'], risk['loosest_limit']))
        self.item(consequence_class='margin', occurrence='normal')        # P2 is not enough
        self.assertIn('severe_stress_work_item_severity', self.codes())
        self.item()                                                       # damage, fault: P1
        self.assertEqual(set(), self.codes())
        self.item(status='closed')
        self.assertIn('severe_stress_work_item_not_open', self.codes())
        self.item(stage='external', status='open')
        self.assertIn('severe_stress_work_item_not_open', self.codes())

    def test_beyond_every_level_with_margin_needs_p2(self):
        self.check['value'] = 120                                         # R2 U401 short-circuit retry: 120 > 105, 30 °C left
        self.assertIn('severe_stress_without_work_item', self.codes())
        self.item(stage='design', status='open', consequence_class='margin', occurrence='condition')
        self.base.record['requirements'][0]['status'] = 'conditional'
        self.assertEqual(set(), self.codes())
        self.assertEqual('P2', self.base.run_audit()['derating']['stress_risks'][0]['required_severity'])

    def test_within_the_next_level_is_a_plain_risk(self):
        self.check['value'] = 100.1                                       # R2 U402: over 95, within III's 105, 50 °C left
        result = self.base.run_audit()
        self.assertEqual('PASS', result['status'], result['errors'])
        self.assertNotIn('required_severity', result['derating']['stress_risks'][0])

    def test_at_the_loosest_level_only_the_margin_counts(self):
        self.base.record['derating']['level'] = 'III'
        self.check.update(limit=105, value=120)
        self.assertEqual(set(), self.codes())
        self.check['value'] = 135
        self.assertIn('severe_stress_without_work_item', self.codes())

    def test_other_stresses_use_the_checks_uncertainty(self):
        self.base.intent.write_text(json.dumps({'components': [
            {'ref': 'U1', 'lib_id': 'Transistor_FET:Q_NMOS_GDS', 'value': 'NMOS', 'mpn': 'X650N'}]}))
        self.base.record['intent_sha256'] = sha256(self.base.intent)
        self.check.update(name='漏源电压', value=530, limit=520, unit='V', derating_rule='MOS-VDS-S', rating=650,
                          limit_source='standard:derating-rules#MOS-VDS-S')  # II 80 %: 520; III 90 %: 585
        self.assertEqual(set(), self.codes())
        self.check['uncertainty'] = 0.25                                   # 18 % left to the rating < 25 %
        self.assertIn('severe_stress_without_work_item', self.codes())


if __name__ == '__main__':
    unittest.main()
