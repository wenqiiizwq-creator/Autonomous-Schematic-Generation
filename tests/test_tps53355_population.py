"""Assembly faults which an all-pads KiCad netlist/ERC cannot detect."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'examples/tps53355_compact'
spec = importlib.util.spec_from_file_location('tps_population', EXAMPLE / 'verify_population.py')
pop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pop)


class PopulationTests(unittest.TestCase):
    def setUp(self):
        self.c = json.loads((EXAMPLE / 'electrical_intent.json').read_text())
        self.b = json.loads((ROOT / 'tests/fixtures/generation/tps53355_rev_b.intent.json').read_text())

    def move(self, pin, destination):
        for net in self.c['nets']:
            if pin in net['pins']:
                net['pins'].remove(pin)
        next(n for n in self.c['nets'] if n['name'] == destination)['pins'].append(pin)

    def test_default_rf_is_open_despite_drawn_resistors(self):
        result = pop.audit(self.c)
        self.assertEqual(result['status'], 'CONFIGURATION_PASS')
        self.assertEqual(result['rf_active_pin_island'], ['U1.22'])
        self.assertEqual(result['frequency_nominal_kHz'], 500)
        self.assertEqual((result['fitted_count'], result['dnp_count']), (40, 7))

    def test_legal_rf_codes_do_not_release_alternate_design(self):
        for ref, freq in [('R13', 650), ('R14', 300)]:
            with self.subTest(ref=ref):
                result = pop.audit(self.c, {ref: True})
                self.assertEqual(result['frequency_nominal_kHz'], freq)
                self.assertEqual(result['status'], 'REVIEW_REQUIRED')
                self.assertTrue(result['review_required'])

    def test_two_rf_resistors_are_invalid_not_a_frequency(self):
        result = pop.audit(self.c, {'R13': True, 'R14': True})
        self.assertEqual(result['status'], 'FAIL')
        self.assertIsNone(result['frequency_nominal_kHz'])

    def test_dnp_does_not_hide_wrong_option_pad_or_value(self):
        saved = copy.deepcopy(self.c)
        self.move('R13.1', 'GND')
        self.assertEqual(pop.audit(self.c)['status'], 'FAIL')
        self.c = saved
        next(c for c in self.c['components'] if c['ref'] == 'R13')['value'] = '100k 1% DNP'
        self.assertEqual(pop.audit(self.c)['status'], 'FAIL')

    def test_mode_exclusivity_and_fccm_review(self):
        for changes in [{'R15': True}, {'R5': False}]:
            result = pop.audit(self.c, changes)
            self.assertEqual(result['status'], 'FAIL')
            self.assertIsNone(result['mode'])
        result = pop.audit(self.c, {'R5': False, 'R15': True})
        self.assertEqual(result['status'], 'REVIEW_REQUIRED')
        self.assertEqual(result['mode'], 'FCCM_AFTER_PG')

    def test_external_bias_links_cannot_silently_be_removed_or_filtered(self):
        self.assertEqual(pop.audit(self.c, {'R17': False})['status'], 'FAIL')
        next(c for c in self.c['components'] if c['ref'] == 'R16')['value'] = '10 1%'
        self.assertEqual(pop.audit(self.c)['status'], 'FAIL')

    def test_incomplete_snubber_conflicting_en_and_unknown_override(self):
        for changes in [{'C15': True}, {'R9': True}, {'R7': False}, {'R999': True}, {'R9': 'FIT'}]:
            with self.subTest(changes=changes):
                self.assertEqual(pop.audit(self.c, changes)['status'], 'FAIL')
        self.assertEqual(pop.audit(self.c, {'R7': False, 'R9': True})['status'], 'REVIEW_REQUIRED')

    def test_baseline_active_connectivity_survives_added_zero_links(self):
        result = pop.compare_existing_pins(self.b, self.c)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['retained_active_pins'], 84)
        self.move('R5.2', 'PGOOD')
        self.assertEqual(pop.compare_existing_pins(self.b, self.c)['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
