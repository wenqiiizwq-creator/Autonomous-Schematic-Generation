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


class GradeReasonTests(unittest.TestCase):
    """G08-006 (user 2026-11-15): an MLCC dielectric above the lowest stable code covering the requirement states why."""
    BOARD = {'CL-ENV': {'text': '工作环境温度 0～+45 ℃；贮存和运输 −40～+85 ℃'}}      # the AD9361 board

    def codes(self, value, requirements=None, **extra):
        found = []
        intent = {'components': [dict({'ref': 'C1', 'lib_id': 'Device:C', 'value': value}, **extra)]}
        audit.audit_grade_reasons(intent, self.BOARD if requirements is None else requirements, lambda code, item: found.append(code))
        return found

    def test_x7r_where_x5r_covers_the_requirement_needs_a_reason(self):
        self.assertEqual(['grade_above_requirement_without_reason'], self.codes('100nF/10V/X7R'))
        self.assertEqual([], self.codes('100nF/10V/X7R', grade_reason='与 X5R 同价同供货'))
        self.assertEqual([], self.codes('22uF/6.3V/X5R'))
        self.assertEqual([], self.codes('1nF/50V/C0G'))      # class I is chosen for stability, not by temperature

    def test_the_needed_grade_follows_the_requirement(self):
        hot = {'R1': {'text': '工作环境温度 −40～+105 ℃'}}
        self.assertEqual([], self.codes('100nF/10V/X7R', hot))
        self.assertEqual(['grade_above_requirement_without_reason'], self.codes('100nF/10V/X8R', hot))
        self.assertEqual([], self.codes('100nF/10V/X7R', {}))   # no range in the requirements: nothing to compare


class RatingAboveNeedTests(unittest.TestCase):
    """降额规范 R13 (user 2026-11-15): an MLCC of 1 µF or more two standard steps above the derated need states why."""
    def codes(self, value, top=7.0, level='III', **extra):
        found = []
        comp = dict({'ref': 'C1', 'lib_id': 'Device:C', 'value': value}, **extra)
        audit.audit_rating_above_need({'derating': {'level': level}}, comp, audit.rated_volts(comp), '+5V', top,
                                      lambda code, item: found.append(code))
        return found

    def test_the_ad9361_parts(self):
        # +5 V rail, worst 7 V, level III (0.95): 10 V is enough
        self.assertEqual(['capacitor_rating_above_need_without_reason'], self.codes('10uF/25V/X7R'))
        self.assertEqual(['capacitor_rating_above_need_without_reason'], self.codes('1uF/25V/X7R'))
        self.assertEqual([], self.codes('10uF/16V/X7R'))                     # one step above: not reported
        self.assertEqual([], self.codes('10uF/10V/X5R'))
        self.assertEqual([], self.codes('100nF/25V/X7R'))                    # below 1 µF the rating costs nothing
        self.assertEqual([], self.codes('1uF/50V/X7R', top=25.2))            # 26.5 V needed: 35 V, 50 V is one step
        self.assertEqual([], self.codes('2.2uF/10V/X7R', top=1.4))           # 6.3 V is the lowest step
        self.assertEqual([], self.codes('10uF/25V/X7R', grade_reason='偏压后有效容量按 G03-010 算，10 V 件不够'))

    def test_the_level_sets_the_need(self):
        # level I (0.8): 7 V needs 8.75 V, so 10 V; 25 V is two steps above
        self.assertEqual(['capacitor_rating_above_need_without_reason'], self.codes('10uF/25V/X7R', level='I'))
        self.assertEqual([], self.codes('10uF/25V/X7R', top=12.0))           # 12.6 V needed: 16 V, 25 V is one step


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
