"""Synthetic guarantees only, not production component specifications."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] if HERE.parents[1].name == 'scripts' else HERE.parents[1] / 'scripts'))
from design_preflight import calculate, validate_calculations

E = [{'source': 'synthetic-datasheet', 'locator': 'stipulated test limits'}]


def calculation():
    return {'id': 'BIAS', 'model': 'Synthetic source current; Vz guaranteed only at 5 mA',
            'expression': '(vin - vz) / r', 'output_unit': 'mA', 'assumptions': [], 'claim': 'SUPPORTED',
            'acceptance': {'operator': '>=', 'value': 5, 'unit': 'mA'},
            'inputs': {key: {'value': value, 'unit': unit, 'basis': 'GUARANTEED', 'evidence': E,
                            'conditions': {}, 'operating_conditions': {},
                            'unconditional_basis': 'Synthetic fixed test conditions'}
                       for key, value, unit in [('vin', 12, 'V'), ('vz', 7, 'V'), ('r', 1, 'kohm')]}}


class CalculationPreflightTests(unittest.TestCase):
    def test_supported_arithmetic(self):
        errors, out = validate_calculations([calculation()])
        self.assertEqual(errors, [])
        self.assertEqual(out['BIAS']['value'], 5)
        self.assertEqual(out['BIAS']['status'], 'SUPPORTED')

    def test_zener_guarantee_at_5ma_not_available_at_0123ma(self):
        row = calculation()
        row['inputs']['vz'].update(conditions={'IZ': {'min': 5, 'max': 5, 'unit': 'mA'}},
            operating_conditions={'IZ': {'min': .123, 'max': .123, 'unit': 'mA'}})
        errors, result = validate_calculations([row])
        self.assertTrue(errors)
        self.assertEqual(result['BIAS']['status'], 'CONDITIONAL')
        row.update(claim='CONDITIONAL', closure='Obtain voltage bounds at the actual bias current')
        self.assertEqual(validate_calculations([row])[0], [])

    def test_ntc_extrapolation_and_runtime_switching_stay_conditional(self):
        row = calculation()
        row['inputs']['r']['basis'] = 'ASSUMED'
        row.update(assumptions=['B25/50 extrapolated outside characterized range',
                               'Runtime bias switching not yet evidenced'], claim='CONDITIONAL',
                   closure='Get full RT curve and verify firmware register transitions')
        self.assertEqual(validate_calculations([row])[0], [])
        row['claim'] = 'SUPPORTED'
        self.assertTrue(validate_calculations([row])[0])

    def test_temperature_condition_must_cover_operating_range(self):
        row = calculation()
        row['inputs']['vz'].update(conditions={'T': {'min': 25, 'max': 25, 'unit': 'C'}},
                                  operating_conditions={'T': {'min': -10, 'max': 100, 'unit': 'C'}})
        self.assertEqual(validate_calculations([row])[1]['BIAS']['status'], 'CONDITIONAL')

    def test_arithmetic_failure_is_not_ready(self):
        row = calculation(); row['inputs']['vin']['value'] = 8
        errors, result = validate_calculations([row])
        self.assertTrue(errors)
        self.assertEqual(result['BIAS']['status'], 'FAIL')

    def test_no_code_execution_and_no_nonfinite_values(self):
        for expr in ["__import__('os').getcwd()", 'r ** 100000000', '1 / 0', 'unknown + 1']:
            with self.subTest(expr=expr), self.assertRaises(ValueError):
                calculate(expr, {'r': 1})
        row = calculation(); row['inputs']['r']['value'] = float('nan')
        self.assertTrue(validate_calculations([row])[0])

    def test_unit_mismatch_missing_condition_duplicate_ids(self):
        row = calculation(); row['inputs']['vz'].update(
            conditions={'T': {'min': 20, 'max': 30, 'unit': 'C'}},
            operating_conditions={'T': {'min': 20, 'max': 30, 'unit': 'K'}})
        self.assertTrue(validate_calculations([row])[0])
        self.assertTrue(validate_calculations([calculation(), calculation()])[0])


if __name__ == '__main__':
    unittest.main()
