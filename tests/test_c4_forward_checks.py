"""C4 finds what C5's temperature matrix and C6's ERC used to send back (handoff run H-001, 2026-11-14)."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import audit_design_closure as audit


def part(ref, lib_id, spec, datasheet=None):
    comp = {'ref': ref, 'lib_id': lib_id, 'value': 'x', 'fields': {'Specification': spec}}
    if datasheet:
        comp['datasheet'] = datasheet
    return comp


class SpecTemperatureTests(unittest.TestCase):
    REQUIREMENTS = {'R10': {'text': '环境温度 −20 ℃ 到 +70 ℃，自然散热。'},
                    'CL-ENV': {'text': '贮存运输温度 −40 ℃ 到 +85 ℃。'},
                    'R3': {'text': '结温不超过 −40～150 ℃ 的器件额定'}}      # not an ambient clause: not read

    def codes(self, spec, datasheet=None):
        found = []
        intent = {'components': [part('R1', 'Device:R', spec, datasheet)], 'nets': {'A': ['R1.1'], 'B': ['R1.2']}}
        audit.audit_spec_temperature(intent, self.REQUIREMENTS, lambda code, item: found.append(code))
        return found

    def test_a_specification_part_states_a_rated_range_covering_the_requirement(self):
        self.assertEqual([], self.codes('10 kohm，工作及存储温度 -55～+125 ℃'))
        self.assertEqual(['spec_temperature_missing'], self.codes('10 kohm，0402'))
        # the first H-001 design wrote the condition of use, which C5's matrix refused
        self.assertEqual(['spec_temperature_narrower_than_requirement'], self.codes('10 kohm，-20～70 ℃'))

    def test_a_part_with_a_datasheet_is_not_read_from_its_specification(self):
        self.assertEqual([], self.codes('10 kohm', datasheet='Datasheet/x.pdf'))


class PowerSourceTests(unittest.TestCase):
    def codes(self, **supplies):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'record').mkdir()
            (root / 'record' / 'reference-input.json').write_text(json.dumps({'pin_maps': {
                'U1': {'pins': {'1': {'types': ['power_in']}, '2': {'types': ['power_out']}, '3': {'types': ['power_in']}}},
                'Q1': {'pins': {'1': {'types': ['passive']}, '2': {'types': ['passive']}}}}}))
            intent = dict({'nets': {'VIN': ['J1.1', 'Q1.2'], 'VIN_P': ['Q1.1', 'U1.1'], 'VOUT': ['U1.2', 'C1.1'],
                                    'GND': ['U1.3', 'J1.2']}}, **supplies)
            found = []
            audit.audit_power_sources(intent, root, lambda code, item: found.append((code, item.split('：')[0])))
            return found

    def test_a_power_input_behind_a_discrete_switch_needs_a_supply_declaration(self):
        self.assertEqual([('power_pin_without_source', 'GND'), ('power_pin_without_source', 'VIN_P')], self.codes())
        self.assertEqual([], self.codes(external_supply=[{'net': 'GND', 'pin': 'J1.2'}],
                                        reviewed_circuit_supply=[{'net': 'VIN_P', 'pin': 'Q1.1'}]))


if __name__ == '__main__':
    unittest.main()
