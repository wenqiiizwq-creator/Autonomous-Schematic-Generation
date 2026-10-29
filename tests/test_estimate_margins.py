"""Task 2.2 (user 2026-10-28: 先改前四条; 判风险): an engineering estimate says how far it may be off, and a check resting
on it whose margin is smaller than that passes with a margin risk and an improvement, like a stress risk; a derating
check's margin is taken to its rating (R12). A calculation that fails even in its best case carries a design change
candidate for the user to approve, and may list what the result is the sum of."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_design_closure import audit, sha256


def setUpModule():
    global _env
    _env = mock.patch.dict('os.environ', {'HARDWARE_WIKI': str(Path(tempfile.gettempdir()) / 'asg-no-library')})
    _env.start()


def tearDownModule():
    _env.stop()


ESTIMATE = {'name': '漏感尖峰', 'value': 40, 'unit': 'V', 'basis': 'model', 'reason': '按同类变压器漏感比例估计',
            'uncertainty': 0.1}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.intent = self.root / 'intent.json'
        self.intent.write_text(json.dumps({'components': [
            {'ref': 'Q1', 'lib_id': 'Transistor_FET:Q_NMOS_GDS', 'value': 'NMOS', 'mpn': 'X650N'}]}))
        (self.root / 'design.txt').write_text('evidence\n')
        self.record = {
            'schema_version': 1, 'coverage': 'complete', 'intent_sha256': sha256(self.intent),
            'parameter_version': 3, 'derating_version': 1, 'uncertainty_version': 1,
            'derating': {'level': 'III', 'source': 'req:R-DER'},
            'evidence': [{'id': 'E1', 'path': 'design.txt', 'sha256': sha256(self.root / 'design.txt'), 'locator': 'l1'}],
            'requirements': [
                {'id': 'R1', 'status': 'conditional', 'refs': ['Q1'], 'evidence': ['E1'], 'implementation': '反激主开关',
                 'depends_on': []},
                {'id': 'R-DER', 'status': 'design_supported', 'refs': [], 'evidence': ['E1'], 'implementation': '降额 III 级',
                 'depends_on': [], 'no_check_reason': '降额等级本身不对应电路'}],
            'work_items': [],
            'calculations': [{
                'id': 'C-VDS', 'requirements': ['R1'], 'evidence': ['E1'], 'refs': ['Q1'], 'coverage': 'bounded',
                'conclusion': 'conditional', 'rests_on': 'estimate', 'omitted_terms': [],
                'parameters': [{'name': 'Vin', 'value': 373, 'unit': 'V', 'basis': 'requirement', 'source': 'req:R1'},
                               dict(ESTIMATE)],
                'checks': [{'name': '漏源电压', 'value': 560, 'operator': '<=', 'limit': 585, 'unit': 'V',
                            'derating_rule': 'MOS-VDS-S', 'ref': 'Q1', 'rating': 650,
                            'rating_source': 'datasheet:Datasheet/09_MOSFET/X - X650N.pdf#p2',
                            'limit_basis': 'standard', 'limit_source': 'standard:derating-rules#MOS-VDS-S'},
                           {'name': '正常峰值不误触发过压', 'value': 80, 'operator': '<', 'limit': 97.6, 'unit': 'V',
                            'limit_basis': 'requirement', 'limit_source': 'req:R1'}]}]}

    def run_audit(self):
        return audit(self.record, self.intent, self.root)

    def codes(self):
        return {e['code'] for e in self.run_audit()['errors']}

    @property
    def calc(self):
        return self.record['calculations'][0]


class EstimateMarginTests(Fixture):
    def test_margins_wider_than_the_estimate_pass(self):
        result = self.run_audit()
        self.assertEqual([], result['errors'])
        self.assertEqual([], result['estimate_margins'])

    def test_an_estimate_says_how_far_it_may_be_off(self):
        del self.calc['parameters'][1]['uncertainty']
        self.assertIn('model_without_uncertainty', self.codes())
        self.calc['parameters'][1]['uncertainty'] = 1.5
        self.assertIn('model_without_uncertainty', self.codes())
        del self.record['uncertainty_version'], self.calc['parameters'][1]['uncertainty']
        result = self.run_audit()
        self.assertEqual(([], 'NOT_CHECKED'), (result['errors'], result['estimate_margins']))

    def test_a_margin_inside_the_estimate_is_a_risk_with_an_improvement(self):
        self.calc['checks'][1]['value'] = 96.9            # 0.7 % short of the limit against a ±10 % estimate
        self.assertIn('estimate_margin_risk_without_improvement', self.codes())
        self.calc['checks'][1]['improvement'] = '提高过压门槛或减小漏感尖峰'
        result = self.run_audit()
        self.assertEqual([], result['errors'])
        risk, = result['estimate_margins']
        self.assertEqual(('C-VDS', '正常峰值不误触发过压', 'limit', 0.1), (risk['calculation'], risk['check'], risk['against'],
                                                                     risk['uncertainty']))
        self.assertAlmostEqual(0.7 / 97.6, risk['margin'])
        self.assertEqual('conditional', result['calculation_basis']['C-VDS']['conclusion'])   # a risk, not a failure

    def test_a_check_may_carry_its_own_propagated_uncertainty(self):
        self.calc['checks'][1].update(value=96.9, uncertainty=0.005)
        self.assertEqual([], self.run_audit()['estimate_margins'])

    def test_a_derating_checks_margin_is_taken_to_its_rating(self):
        # 560 V is 4 % under the derated 585 V but 14 % under the 650 V rating: one allowance only (R12).
        self.assertEqual([], self.run_audit()['estimate_margins'])
        self.calc['parameters'][1]['uncertainty'] = 0.2
        self.calc['checks'][0]['improvement'] = '换 800 V 器件'
        self.calc['checks'][1]['value'] = 70              # 28 % margin: clear of a ±20 % estimate
        risk, = self.run_audit()['estimate_margins']
        self.assertEqual(('漏源电压', 'rating', 650), (risk['check'], risk['against'], risk['limit']))


class BestCaseFailureTests(Fixture):
    def setUp(self):
        super().setUp()
        del self.record['uncertainty_version']
        self.calc.update(conclusion='failed', rests_on=None)
        self.calc['checks'][1].update(name='低损耗情景效率', value=0.819, operator='>=', limit=0.835, unit='1',
                                      scenario='best')

    def design_item(self, **extra):
        self.record['work_items'] = [dict({
            'id': 'W-EFF', 'stage': 'design', 'status': 'open', 'requirements': ['R1'], 'evidence': ['E1'], 'owner': 'ASG',
            'action': '降低主要损耗', 'consequence_class': 'function', 'occurrence': 'normal', 'calculations': ['C-VDS']},
            **extra)]

    def test_a_best_case_failure_carries_a_design_change_candidate(self):
        self.assertIn('best_case_failed_without_redesign', self.codes())
        self.design_item()
        self.assertIn('best_case_failed_without_redesign', self.codes())
        self.design_item(redesign='限流电阻改为启动后旁路，预计满载损耗减少约 6 W')
        self.assertNotIn('best_case_failed_without_redesign', self.codes())

    def test_a_failure_not_in_its_best_case_needs_no_candidate(self):
        self.calc['checks'][1]['scenario'] = 'worst'
        self.assertNotIn('best_case_failed_without_redesign', self.codes())
        self.calc['checks'][1]['scenario'] = 'typical'
        self.assertIn('schema', self.codes())

    def test_contributors_are_named_values(self):
        self.calc['contributors'] = [{'name': '限流电阻', 'value': 6.38, 'unit': 'W'}]
        self.assertNotIn('schema', self.codes())
        self.calc['contributors'] = [{'name': '限流电阻', 'value': 'large'}]
        self.assertIn('schema', self.codes())


if __name__ == '__main__':
    unittest.main()
