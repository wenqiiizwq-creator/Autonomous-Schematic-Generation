"""Generation-side guards for the defect classes SR found on 86 open boards (user 2026-11-02: 把这86块板子上找到的问题，
在规则库、ASG和SR技能中进行改进). Each check has a failing case taken from a board finding and a passing case.

Part numbers and file names below come from the board findings; the files are synthetic stand-ins, not datasheets.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import guideline_criteria  # noqa: E402
from audit_design_closure import audit, sha256  # noqa: E402
from schematic_layout import component_requirements as cr  # noqa: E402
from schematic_layout.reference_contract import verify_reference  # noqa: E402

_env = None


def setUpModule():
    global _env
    library = guideline_criteria.load(guideline_criteria.BUNDLE_PATH)
    library.update(library_version='0.0.0', specs={}, criteria=[],
                   content_sha256=guideline_criteria.content_sha256([], library.get('engineering_values')))
    empty = Path(tempfile.gettempdir()) / 'asg-empty-guideline-criteria-boards.json'
    empty.write_text(guideline_criteria.dump(library), encoding='utf-8')
    _env = mock.patch.dict('os.environ', {'HARDWARE_WIKI': str(Path(tempfile.gettempdir()) / 'asg-no-library'),
                                          'GUIDELINE_CRITERIA': str(empty)})
    _env.start()


def tearDownModule():
    _env.stop()


DS = 'datasheet:Datasheet/08_电源管理/TI - TPS709.pdf#p3'


class BindingTests(unittest.TestCase):
    """binding_version 1 of design-closure.json."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'record').mkdir()
        (self.root / 'design.txt').write_text('evidence\n')
        (self.root / 'TI - TPS709.txt').write_text('TPS709 150-mA LDO; ordering TPS70933DBVR\n')
        self.components = [
            {'ref': 'U1', 'lib_id': 'Regulator_Linear:TPS709', 'value': 'TPS70933', 'mpn': 'TPS70933DBVR',
             'datasheet': 'TI - TPS709.txt'},
            {'ref': 'C1', 'lib_id': 'Device:C', 'value': '1uF/50V'},
            {'ref': 'D1', 'lib_id': 'Device:D_TVS', 'value': 'SMBJ40A', 'mpn': 'SMBJ40A',
             'datasheet': 'Littelfuse - SMBJ.txt'}]
        (self.root / 'Littelfuse - SMBJ.txt').write_text('SMBJ series\n')
        self.nets = {'VIN': ['U1.1', 'C1.1', 'D1.1'], 'GND': ['U1.2', 'C1.2', 'D1.2'], 'VOUT': ['U1.5', 'U1.3']}
        self.no_connect = ['U1.4']
        self.boundary = []
        self.record = {
            'schema_version': 1, 'coverage': 'complete', 'binding_version': 1,
            'evidence': [{'id': 'E1', 'path': 'design.txt', 'sha256': sha256(self.root / 'design.txt'), 'locator': 'l1'}],
            'requirements': [{'id': 'R1', 'status': 'design_supported', 'refs': ['U1'], 'evidence': ['E1'],
                              'implementation': '24 V 输入稳压', 'depends_on': []}],
            'work_items': [],
            'calculations': [{'id': 'C1', 'requirements': ['R1'], 'evidence': ['E1'], 'refs': ['U1', 'D1'],
                              'coverage': 'bounded', 'conclusion': 'supported', 'omitted_terms': [], 'kind': 'threshold',
                              'checks': [{'name': 'VIN 最高 对 VRWM', 'side': 'no_false_trip', 'value': 30, 'operator': '<=',
                                          'limit': 40, 'unit': 'V'},
                                         {'name': '钳位 对 U1 绝对最大', 'side': 'protection', 'value': 64.5, 'operator': '<=',
                                          'limit': 65, 'unit': 'V'}]}],
            'pin_dispositions': [{'pin': 'U1.4', 'disposition': 'open', 'source': DS, 'locator': '表 4-1 NC：可悬空'}],
            'net_voltages': [{'net': 'VIN', 'max': 30, 'unit': 'V', 'source': 'req:R1'},
                             {'net': 'VOUT', 'max': 3.4, 'unit': 'V', 'source': 'calc:C1'}]}
        self.pins = {'1': {'names': ['IN'], 'types': ['power_in'], 'datasheet_type': 'PWR', 'datasheet_name': 'IN'},
                     '2': {'names': ['GND'], 'types': ['power_in'], 'datasheet_type': 'GND', 'datasheet_name': 'GND'},
                     '3': {'names': ['~{EN}'], 'types': ['input'], 'datasheet_type': 'I', 'datasheet_name': 'EN'},
                     '4': {'names': ['NC'], 'types': ['no_connect'], 'datasheet_type': 'NC', 'datasheet_name': 'NC'},
                     '5': {'names': ['OUT'], 'types': ['power_out'], 'datasheet_type': 'PWR_OUT', 'datasheet_name': 'OUT'}}
        self.contract = {'sources': {'ds': {'path': '../TI - TPS709.txt', 'sha256': '0' * 64}},
                         'pin_maps': {'U1': {'identity': {}, 'source': 'ds', 'locator': 'p3 表 4-1', 'pins': self.pins}}}

    def run_audit(self):
        intent = self.root / 'intent.json'
        intent.write_text(json.dumps({'components': self.components, 'nets': self.nets, 'no_connect': self.no_connect,
                                      'net_roles': {'VIN': 'power', 'VOUT': 'power', 'GND': 'return'},
                                      'boundary_nets': self.boundary}))
        (self.root / 'record' / 'reference-input.json').write_text(json.dumps(self.contract))
        record = dict(self.record, intent_sha256=sha256(intent))
        return audit(record, intent, self.root)

    def codes(self):
        return {e['code'] for e in self.run_audit()['errors']}

    def part(self, ref):
        return next(c for c in self.components if c['ref'] == ref)

    def test_the_bound_record_passes(self):
        result = self.run_audit()
        self.assertEqual([], result['errors'])
        self.assertEqual({'VIN': 30, 'VOUT': 3.4}, result['binding']['net_voltages'])

    # --- placeholders (DOC-D01 chlinknet R_Small/C, greenmobi-bms BZT52Bxx; DOC-Q01 gnss K?) ---
    def test_a_library_default_value_does_not_ship(self):
        self.part('C1')['value'] = 'C'
        self.assertIn('placeholder_value', self.codes())

    def test_a_wildcard_part_number_does_not_ship(self):
        self.components.append({'ref': 'D2', 'lib_id': 'Device:D_Zener', 'value': 'BZT52Bxx'})
        self.nets['VOUT'].append('D2.1')
        self.nets['GND'].append('D2.2')
        self.assertIn('placeholder_value', self.codes())

    def test_a_value_equal_to_its_symbol_name_is_a_placeholder(self):
        self.components.append({'ref': 'Y1', 'lib_id': 'Device:Crystal_GND24', 'value': 'Crystal_GND24'})
        self.assertIn('placeholder_value', self.codes())

    def test_an_unannotated_reference_does_not_ship(self):
        self.part('C1')['ref'] = 'C?'
        self.nets = {k: [p.replace('C1.', 'C?.') for p in v] for k, v in self.nets.items()}
        self.assertIn('unannotated_reference', self.codes())

    def test_placeholders_are_checked_without_binding_version(self):
        del self.record['binding_version']
        self.part('C1')['value'] = 'R_Small'
        self.assertIn('placeholder_value', self.codes())

    # --- identity (DEV-D01 greenmobi-bms LM5163/LM5164, protocentral TCR2EF33 vs AP2112; CLK-C01 16 vs 24 MHz) ---
    def test_value_and_part_number_name_one_part(self):
        self.part('U1').update(value='TPS79333', mpn='TPS70933DBVR')
        self.assertIn('part_value_contradicts_mpn', self.codes())

    def test_the_datasheet_is_the_parts_own(self):
        (self.root / 'Diodes - AP2112.txt').write_text('AP2112 600mA CMOS LDO\n')
        self.part('U1').update(value='TCR2EF33', mpn='TCR2EF33', datasheet='Diodes - AP2112.txt')
        self.assertIn('part_datasheet_contradicts_mpn', self.codes())

    def test_a_family_datasheet_covers_its_members(self):
        (self.root / 'Vishay - SiC47x.txt').write_text('SiC47x family\n')
        self.part('U1').update(value='SIC477ED', mpn='SIC477ED-T1-GE3', datasheet='Vishay - SiC47x.txt')
        self.contract['sources']['ds']['path'] = '../Vishay - SiC47x.txt'
        self.assertNotIn('part_datasheet_contradicts_mpn', self.codes())

    def test_a_crystal_value_and_part_number_give_one_frequency(self):
        self.components.append({'ref': 'Y1', 'lib_id': 'Device:Crystal', 'value': '16MHz',
                                'mpn': 'ABM8-24.000MHZ-10-B1U-T'})
        self.assertIn('crystal_frequency_contradicts_mpn', self.codes())
        self.components[-1]['value'] = '24MHz'
        self.assertNotIn('crystal_frequency_contradicts_mpn', self.codes())

    # --- pin maps (DEV-D02 hdmi-mipi-bridge HWSON read as SO8, flatmcu outputs declared IN) ---
    def test_the_pin_map_reads_the_selected_parts_datasheet(self):
        (self.root / 'TI - TPS79333.txt').write_text('TPS793\n')
        self.contract['sources']['ds']['path'] = '../TI - TPS79333.txt'
        self.assertIn('pin_map_datasheet_mismatch', self.codes())

    def test_each_pin_writes_its_datasheet_type(self):
        del self.pins['3']['datasheet_type']
        self.assertIn('pin_map_without_datasheet_type', self.codes())

    def test_an_output_cannot_be_drawn_as_an_input(self):
        self.pins['5'].update(types=['input'])
        self.assertIn('pin_type_contradicts_datasheet', self.codes())

    def test_each_pin_writes_the_name_the_datasheet_prints(self):
        del self.pins['1']['datasheet_name']
        self.assertIn('pin_map_without_datasheet_name', self.codes())

    def test_a_symbol_name_unlike_the_datasheet_needs_a_note(self):
        self.pins['5']['datasheet_name'] = 'VOUT'
        self.assertIn('pin_name_differs_from_datasheet', self.codes())
        self.pins['5']['name_note'] = '手册表 4-1 写 VOUT，符号沿用库名 OUT，同一物理脚 5'
        self.assertNotIn('pin_name_differs_from_datasheet', self.codes())

    def test_the_reference_contract_accepts_the_datasheet_type(self):
        base = Path(self.tmp.name) / 'rc'
        shutil.copytree(ROOT / 'tests/fixtures/reference_contract', base)
        contract = json.loads((base / 'contract.json').read_text())
        for pin in contract['pin_maps']['U1']['pins'].values():
            pin['datasheet_type'] = 'A'
        self.assertEqual('PASS', verify_reference(base / 'netlist.xml', contract, base)['status'])

    def test_the_reference_contract_carries_the_type_note_into_its_report(self):
        # Matrix R2 (2026-11-04): TI's P read as PWR_OUT could only be written in 外围电路核对表.md.
        base = Path(self.tmp.name) / 'rc'
        shutil.copytree(ROOT / 'tests/fixtures/reference_contract', base)
        contract = json.loads((base / 'contract.json').read_text())
        number, pin = next(iter(contract['pin_maps']['U1']['pins'].items()))
        pin['type_note'] = '手册类型列印 P，功能栏写器件输出的开关节点，按 PWR_OUT 记'
        result = verify_reference(base / 'netlist.xml', contract, base)
        self.assertEqual('PASS', result['status'])
        self.assertEqual({number: pin['type_note']}, result['pin_maps']['U1']['type_notes'])
        pin['type_note'] = ' '
        with self.assertRaises(ValueError):
            verify_reference(base / 'netlist.xml', contract, base)

    def test_the_audit_accepts_a_type_note_but_it_waives_nothing(self):
        self.pins['5']['type_note'] = '手册印 P，功能栏写输出，按 PWR_OUT 记'
        self.assertNotIn('schema', self.codes())
        self.pins['5']['datasheet_type'] = 'I'
        self.assertIn('pin_type_contradicts_datasheet', self.codes())
        self.pins['5']['type_note'] = ''
        self.assertIn('schema', self.codes())

    # --- unused pins (NET-A07 eegfrontier DAISY_IN, nixie SN74HC595; NET-A01 rs485-spy CC on a one-node net) ---
    def test_an_open_pin_needs_its_datasheet_disposition(self):
        self.record['pin_dispositions'] = []
        self.assertIn('no_connect_without_disposition', self.codes())

    def test_the_disposition_is_what_the_netlist_does(self):
        self.record['pin_dispositions'][0].update(disposition='tie_low', net='GND')
        self.assertIn('disposition_contradicts_netlist', self.codes())

    def test_a_disposition_cites_the_datasheet_page(self):
        self.record['pin_dispositions'][0].pop('source')
        self.assertIn('disposition_without_source', self.codes())

    def test_a_pull_down_needs_a_resistor_on_the_net(self):
        self.no_connect = []
        self.nets['DAISY'] = ['U1.4', 'R1.1']
        self.components.append({'ref': 'R1', 'lib_id': 'Device:R', 'value': '10k'})
        self.nets['GND'].append('R1.2')
        self.record['pin_dispositions'][0].update(disposition='pull_down')
        self.assertNotIn('disposition_contradicts_netlist', self.codes())
        self.nets['DAISY'] = ['U1.4', 'C1.1']
        self.nets['VIN'].remove('C1.1')
        self.assertIn('disposition_contradicts_netlist', self.codes())

    def test_a_one_endpoint_net_is_an_open_pin(self):
        self.components.append({'ref': 'J1', 'lib_id': 'Connector:USB_C_Receptacle_USB2.0', 'value': 'USB_C'})
        self.nets['CC1'] = ['J1.A5']
        self.assertIn('single_endpoint_net', self.codes())

    # --- a net that leaves the board (Matrix R3 S25: PPS_OUT_1..6 on one connector pin, buffer on another board) ---
    def pps_net(self, contract_row='| PPS_OUT_1 | 输出 |'):
        self.components.append({'ref': 'J1', 'lib_id': 'Connector_Generic:Conn_01x03', 'value': 'PPS'})
        self.nets['PPS_OUT_1'] = ['J1.3']
        doc = self.root / '设计资料' / 'MCU与固件接口.md'
        doc.parent.mkdir(exist_ok=True)
        doc.write_text('| 网络 | 方向 |\n|---|---|\n%s\n' % contract_row, encoding='utf-8')
        self.boundary = [{'net': 'PPS_OUT_1', 'to': 'PPS缓冲分图', 'contract': '设计资料/MCU与固件接口.md'}]

    def test_a_declared_boundary_net_with_its_contract_row_may_have_one_pin(self):
        self.pps_net()
        result = self.run_audit()
        self.assertEqual([], result['errors'])
        self.assertEqual(['PPS_OUT_1'], result['boundary_nets'])

    def test_an_undeclared_one_endpoint_net_still_fails(self):
        self.pps_net()
        self.boundary = []
        self.assertIn('single_endpoint_net', self.codes())

    def test_a_boundary_net_whose_contract_has_no_row_is_not_waived(self):
        self.pps_net(contract_row='| PPS_OUT_10 | 输出 |')
        codes = self.codes()
        self.assertIn('boundary_net_not_in_contract', codes)
        self.assertIn('single_endpoint_net', codes)
        self.boundary[0]['contract'] = '设计资料/不存在.md'
        codes = self.codes()
        self.assertIn('boundary_contract_missing', codes)
        self.assertIn('single_endpoint_net', codes)

    def test_a_real_open_pin_beside_a_boundary_net_still_fails(self):
        self.pps_net()
        self.nets['VOUT'] = ['U1.5']
        self.nets['SENSE'] = ['U1.3']
        errors = self.run_audit()['errors']
        self.assertEqual(['U1.3', 'U1.5'], sorted(e['item'].split('只接 ')[1].split(' ')[0] for e in errors
                                                  if e['code'] == 'single_endpoint_net'))

    # --- rail voltages (DEV-C01 neotron 25 V on 30 V; PRO-E02 jetson SMBJ33A on 36 V, hv-flyback PESD5V0 on 6 V) ---
    def test_each_rail_writes_its_highest_voltage(self):
        self.record['net_voltages'].pop()
        self.assertIn('net_voltage_missing', self.codes())

    def test_the_rail_voltage_has_a_source(self):
        self.record['net_voltages'][0]['source'] = 'req:R9'
        self.assertIn('net_voltage_without_source', self.codes())

    def test_a_capacitor_rated_below_its_rail_fails(self):
        self.part('C1')['value'] = '10uF/25V'
        self.assertIn('capacitor_rating_below_net_voltage', self.codes())

    def test_a_tvs_standing_off_below_its_rail_fails(self):
        self.record['net_voltages'][0]['max'] = 36
        self.part('D1').update(value='SMBJ33A', mpn='SMBJ33A')
        self.assertIn('tvs_vrwm_below_net_voltage', self.codes())
        self.part('D1').update(value='PESD5V0L1BSL', mpn='PESD5V0L1BSL', datasheet='Nexperia - PESD5V0L1BSL.txt')
        (self.root / 'Nexperia - PESD5V0L1BSL.txt').write_text('PESD5V0L1BSL\n')
        self.record['net_voltages'][0]['max'] = 6
        self.assertIn('tvs_vrwm_below_net_voltage', self.codes())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ComponentRequirementGuards(unittest.TestCase):
    """component-requirements.json: capacitor and TVS voltages, datasheet minimums (PWR-D02/C04/C09, DEV-C01, PRO-E02)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        calc = self.root / 'calc.txt'
        calc.write_text('synthetic: VIN max 30 V; datasheet asks COUT >= 1 uF effective\n')
        self.source = {'path': 'calc.txt', 'sha256': digest(calc), 'locator': 'line 1'}
        self.entry = {'ref': 'C1', 'kind': 'capacitor', 'purpose': 'LDO 输出电容', 'definition_status': 'complete',
                      'display': 'note', 'required_parameters': ['capacitance', 'effective_capacitance', 'working_voltage'],
                      'procurement': {'mode': 'spec', 'reason': 'MLCC 按规格采购'}, 'selection': {'status': 'not_selected'},
                      'requirements': [
                          {'parameter': 'capacitance', 'op': 'eq', 'value': 2.2, 'unit': 'uF',
                           'conditions': {'temperature': '25 degC'}, 'basis': 'calculation', 'source': self.source},
                          {'parameter': 'effective_capacitance', 'op': 'ge', 'value': 1, 'unit': 'uF',
                           'conditions': {'bias': '3.3 V'}, 'basis': 'datasheet',
                           'source': dict(self.source, kind='manufacturer')},
                          {'parameter': 'working_voltage', 'op': 'ge', 'value': 10, 'unit': 'V',
                           'conditions': {'node': 'VOUT 最高 3.4 V'}, 'basis': 'calculation', 'source': self.source}]}

    def errors(self):
        return cr.entry_errors(self.entry)

    def test_the_complete_contract_passes(self):
        self.assertEqual([], self.errors())

    def test_a_capacitor_writes_its_voltage(self):
        self.entry['requirements'].pop()
        self.entry['required_parameters'].pop()
        self.assertTrue(any('working_voltage' in e for e in self.errors()))

    def test_a_tvs_writes_its_stand_off_voltage(self):
        self.entry.update(kind='tvs', required_parameters=['capacitance', 'effective_capacitance'],
                          requirements=self.entry['requirements'][:2])
        self.assertTrue(any('tvs needs a working_voltage' in e for e in self.errors()))

    def test_the_nominal_meets_the_datasheet_minimum(self):
        self.entry['requirements'][0]['value'] = 100
        self.entry['requirements'][0]['unit'] = 'nF'
        self.assertTrue(any('nominal capacitance 100 nF does not meet effective_capacitance >= 1 uF' in e for e in self.errors()))

    def test_a_datasheet_requirement_cites_the_manufacturer(self):
        self.entry['requirements'][1]['source'] = self.source
        self.assertTrue(any('source kind manufacturer' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
