"""对全部对象核对的矩阵与保护逻辑状态表（整板评测 2026-11-07：复位门限只对 MCU、存储温度、低边防反接断开地回路、
软件正常关断误置锁）。行和格由设计网表列出，缺结论是设计没做完，结论与检查矛盾或检查没点名对象是记录错误。"""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import guideline_criteria  # noqa: E402
import object_matrices as om  # noqa: E402
from audit_design_closure import CURRENT_VERSIONS, audit as closure_audit, failing_checks, holds, sha256  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'object_matrices.py'
_env = None


def setUpModule():
    global _env
    from unittest import mock
    library = guideline_criteria.load()
    library.update(library_version='0.0.0', specs={}, criteria=[],
                   content_sha256=guideline_criteria.content_sha256([], library.get('engineering_values')))
    empty = Path(tempfile.gettempdir()) / 'asg-empty-guideline-criteria-matrices.json'
    empty.write_text(guideline_criteria.dump(library), encoding='utf-8')
    _env = mock.patch.dict('os.environ', {'HARDWARE_WIKI': str(Path(tempfile.gettempdir()) / 'asg-no-library'),
                                          'GUIDELINE_CRITERIA': str(empty), 'GUIDELINE_CRITERIA_TESTING': '1'})
    _env.start()


def tearDownModule():
    _env.stop()


def comp(ref, value, lib='Device:R', **fields):
    return {'ref': ref, 'lib_id': lib, 'value': value, 'mpn': value if lib.startswith('IC') else '', 'fields': fields}


# 一块小板：+3V3 由 U1（TPS3808）监控，U2 MCU 与 U3 交换芯片（经磁珠 FB1 派生的 AVDDH）是负载；
# J1 是 24 V 输入，回线 VIN_RTN 经低边 MOS Q1 才接 GND；J2 是 RS-485，SM712 D1 在端口上、经 R1 到收发器 U4；
# U5 是 eFuse，块 Ch 里有 CH_FLT。
INTENT = {
    'components': [
        comp('U1', 'TPS3808G33DBVR', 'IC:TPS3808', Circuit='MCU'), comp('U2', 'STM32F107VCT6', 'IC:STM32', Circuit='MCU'),
        comp('U3', 'YT9218MBH', 'IC:YT9218', Circuit='Switch'), comp('U4', 'ADM2561E', 'IC:ADM2561E', Circuit='RS485'),
        comp('U5', 'TPS26630RGER', 'IC:TPS2663', Circuit='Ch'),
        comp('FB1', '600R', 'Device:FerriteBead'), comp('R1', '10', 'Device:R'), comp('C1', '100n/50V/X7R', 'Device:C'),
        comp('C2', '100n/16V/X7R', 'Device:C'),
        comp('D1', 'CDSOT23-SM712', 'Device:D_TVS'), comp('Q1', 'PSMN1R4-100ASE', 'Device:Q_NMOS_GDS'),
        comp('J1', 'Conn', 'Connector_Generic:Conn_01x02'), comp('J2', 'Conn', 'Connector_Generic:Conn_01x03'),
        comp('TP1', 'TP', 'Connector:TestPoint')],
    'nets': {'+3V3': ['U1.1', 'U2.1', 'U3.1', 'FB1.1', 'C2.1', 'TP1.1'], 'AVDDH': ['FB1.2', 'U3.2'],
             'GND': ['U1.2', 'U2.2', 'U3.3', 'U4.2', 'U5.2', 'C1.2', 'C2.2', 'Q1.1', 'J2.3', 'D1.3'],
             'VIN_24V': ['J1.1', 'C1.1', 'U5.1'], 'VIN_RTN': ['J1.2', 'Q1.2'], 'Q1_G': ['Q1.3', 'U5.4'],
             'RS485_A': ['J2.1', 'D1.1', 'R1.1'], 'RS485_A_IC': ['R1.2', 'U4.1'], 'RS485_B': ['J2.2', 'D1.2', 'U4.3'],
             'CH_FLT': ['U5.3', 'U2.3'], 'MCU_NRST': ['U1.3', 'U2.4']},
    'net_roles': {'+3V3': 'power', 'AVDDH': 'power', 'VIN_24V': 'power', 'GND': 'return', 'VIN_RTN': 'return'},
    'filtered_supply': [{'net': 'AVDDH', 'from': '+3V3', 'via': 'FB1', 'reason': '磁珠滤波'}]}

CALCS = {'C-RST': {'id': 'C-RST', 'checks': [
            {'name': '复位门限下限 对 STM32 VDD 下限 2.0 V', 'value': 2.9, 'operator': '>', 'limit': 2.0, 'unit': 'V'},
            {'name': '复位门限下限 对 YT9218 最低 3.135 V', 'value': 3.02, 'operator': '>=', 'limit': 3.135, 'unit': 'V'},
            {'name': '+3V3 下限 对 YT9218 3.135 V', 'value': 3.2, 'operator': '>=', 'limit': 3.135, 'unit': 'V'}]},
         'C-485': {'id': 'C-485', 'checks': [
            {'name': 'SM712 钳位 对 ADM2561E 总线脚绝对最大', 'value': 14, 'operator': '<', 'limit': 18, 'unit': 'V'},
            {'name': 'R501 功耗 对 额定', 'value': 0.1, 'operator': '<', 'limit': 0.5, 'unit': 'W'}]},
         'C-RTN': {'id': 'C-RTN', 'checks': [
            {'name': '反接时经 J2 地回流 对 U4 GND 脚负压绝对最大', 'value': 0.3, 'operator': '<', 'limit': 0.5, 'unit': 'V'}]}}


def passes(c):
    return holds(c) is not None and not failing_checks({'checks': [c]})


def run(matrices, calculations=CALCS, evidence=('E1',), requirements=None):
    errors, pending = [], []
    reqs = requirements if requirements is not None else {
        'REQ-T': {'id': 'REQ-T', 'text': '工作 −40～+85 ℃，存储 −45～+70 ℃'}, 'REQ-S': {'id': 'REQ-S', 'text': '浪涌 ±1 kV'}}
    summary = om.audit({'matrices': matrices}, INTENT, calculations, {e: {} for e in evidence}, reqs, passes,
                       lambda c, i: errors.append((c, i)), lambda c, i: pending.append((c, i)))
    return summary, errors, pending


def codes(items):
    return {c for c, _ in items}


class ExpectedRowsTests(unittest.TestCase):
    def test_rows_come_from_the_design_netlist(self):
        exp = om.expected(INTENT)
        self.assertEqual({'+3V3': {'supervisors': ['U1'], 'loads': {'U2': ['+3V3'], 'U3': ['+3V3', 'AVDDH']}}},
                         exp['supervised_rails'])
        self.assertNotIn('TP1', exp['temperature'])
        self.assertIn('C1', exp['temperature'])
        j2 = exp['port_stress']['J2']
        self.assertEqual(['D1', 'U4'], sorted(j2['objects']))     # U4 经串联 R1 也在路径上，R1 本身不进格
        self.assertEqual(['RS485_A_IC', 'RS485_B'], sorted(j2['objects']['U4']))
        j1 = exp['port_stress']['J1']
        self.assertEqual([{'net': 'VIN_RTN', 'via': 'Q1', 'to': 'GND', 'ports': ['J2']}], j1['return_breaks'])
        self.assertEqual([], j2['return_breaks'])              # 板地一侧看到的是同一个回路，只从被隔开的一侧列
        self.assertIn('Ch', exp['protection_states'])
        self.assertIn('MCU', exp['protection_states'])          # 监控器件与 MCU_NRST

    def test_a_regulator_is_not_a_supervisor(self):
        intent = copy.deepcopy(INTENT)
        intent['components'][0].update(value='TLV74333P', mpn='TLV74333P')
        self.assertEqual({}, om.expected(intent)['supervised_rails'])

    def test_skeleton_lists_every_cell_and_keeps_written_conclusions(self):
        record = {'calculations': list(CALCS.values()), 'matrices': {'supervised_rails': [
            {'rail': '+3V3', 'cells': [{'ref': 'U2', 'calc': 'C-RST', 'check': '复位门限下限 对 STM32 VDD 下限 2.0 V'}]}]}}
        sk = om.skeleton(INTENT, record)['matrices']
        cells = {c['ref']: c for c in sk['supervised_rails'][0]['cells']}
        self.assertEqual('C-RST', cells['U2']['calc'])
        self.assertIsNone(cells['U3']['calc'])
        # 候选只列核门限的检查：“+3V3 下限 对 YT9218”核的是稳压精度
        self.assertEqual(['复位门限下限 对 YT9218 最低 3.135 V'], [c['check'] for c in cells['U3']['candidates']])
        blocks = {b['block']: b for b in sk['protection_states']}
        self.assertEqual(10, len(blocks['Ch']['rows']))         # 5 个状态 × 锁清除/置位

    def test_cli_writes_a_skeleton(self):
        with tempfile.TemporaryDirectory() as tmp:
            intent, out = Path(tmp) / 'intent.json', Path(tmp) / 'm.json'
            intent.write_text(json.dumps(INTENT), encoding='utf-8')
            done = subprocess.run([sys.executable, str(SCRIPT), 'skeleton', '--intent', str(intent), '--out', str(out)],
                                  capture_output=True, text=True)
            self.assertEqual(0, done.returncode, done.stderr)
            self.assertIn('supervised_rails', json.loads(out.read_text(encoding='utf-8'))['matrices'])


class SupervisedRailTests(unittest.TestCase):
    def rails(self, cells):
        return {'supervised_rails': [{'rail': '+3V3', 'cells': cells}]}

    def test_threshold_checked_against_the_mcu_only_leaves_the_switch_missing(self):
        summary, errors, pending = run(self.rails([{'ref': 'U2', 'calc': 'C-RST', 'check': '复位门限下限 对 STM32 VDD 下限 2.0 V'}]))
        self.assertEqual([], [e for e in errors if e[0].startswith('matrix_check')])
        missing = [i for c, i in pending if c == 'matrix_cell_missing' and '受监督轨' in i]
        self.assertEqual(1, len(missing))
        self.assertIn('U3 YT9218MBH', missing[0])

    def test_failed_threshold_is_a_failed_cell(self):
        summary, errors, pending = run(self.rails([
            {'ref': 'U2', 'calc': 'C-RST', 'check': '复位门限下限 对 STM32 VDD 下限 2.0 V'},
            {'ref': 'U3', 'calc': 'C-RST', 'check': '复位门限下限 对 YT9218 最低 3.135 V'}]))
        self.assertIn('matrix_cell_failed', codes(pending))
        self.assertEqual(1, len(summary['supervised_rails']['failed']))

    def test_the_mcu_check_cannot_stand_for_another_load(self):
        _, errors, _ = run(self.rails([{'ref': 'U3', 'calc': 'C-RST', 'check': '复位门限下限 对 STM32 VDD 下限 2.0 V'}]))
        self.assertIn('matrix_check_not_about_object', codes(errors))

    def test_a_regulation_check_is_not_a_threshold_check(self):
        _, errors, _ = run(self.rails([{'ref': 'U3', 'calc': 'C-RST', 'check': '+3V3 下限 对 YT9218 3.135 V'}]))
        self.assertIn('matrix_check_not_about_criterion', codes(errors))

    def test_written_verdict_must_follow_the_check(self):
        _, errors, _ = run(self.rails([{'ref': 'U3', 'calc': 'C-RST', 'check': '复位门限下限 对 YT9218 最低 3.135 V', 'verdict': 'ok'}]))
        self.assertIn('matrix_verdict_contradicts_check', codes(errors))

    def test_unknown_check_and_bare_not_applicable_are_errors(self):
        _, errors, _ = run(self.rails([{'ref': 'U2', 'calc': 'C-RST', 'check': '不存在'}, {'ref': 'U3', 'verdict': 'not_applicable'}]))
        self.assertTrue({'matrix_check_unknown', 'matrix_not_applicable_without_reason'} <= codes(errors))


class TemperatureTests(unittest.TestCase):
    HEADER = {'operating': {'min': -40, 'max': 85, 'source': 'req:REQ-T'}, 'storage': {'min': -45, 'max': 70, 'source': 'req:REQ-T'}}

    def table(self, rows, header=None):
        return {'temperature': dict(header or self.HEADER, rows=rows)}

    def test_storage_left_to_device_ratings_is_missing(self):
        rows = [{'refs': ['U2'], 'operating': {'min': -40, 'max': 105, 'source': 'datasheet:Datasheet/x/ST - STM32F107VC.pdf#p1'}}]
        _, _, pending = run(self.table(rows))
        missing = [i for c, i in pending if c == 'matrix_cell_missing']
        self.assertIn('U2 STM32F107VCT6 的存储温度', missing)
        self.assertNotIn('U2 STM32F107VCT6 的工作温度', missing)

    def test_storage_range_short_of_the_requirement_fails(self):
        rows = [{'refs': ['U2'], 'storage': {'min': -40, 'max': 125, 'source': 'datasheet:Datasheet/x/ST - STM32F107VC.pdf#p1'}}]
        summary, _, pending = run(self.table(rows))
        self.assertEqual(['U2 STM32F107VCT6 的存储温度'], summary['temperature']['failed'])

    def test_spec_source_must_be_written_into_every_part_spec(self):
        rows = [{'refs': ['C1', 'C2'], 'storage': {'min': -55, 'max': 125, 'source': 'spec'}}]
        _, errors, _ = run(self.table(rows))
        self.assertIn('matrix_temperature_not_in_spec', codes(errors))

    def test_spec_source_written_into_the_part_spec_concludes(self):
        intent = copy.deepcopy(INTENT)
        for c in intent['components']:
            if c['ref'] in ('C1', 'C2'):
                c['fields']['Specification'] = 'X7R，−55 ℃～+125 ℃'
        errors, pending = [], []
        rows = [{'refs': ['C1', 'C2'], 'storage': {'min': -55, 'max': 125, 'source': 'spec'}}]
        summary = om.audit({'matrices': self.table(rows)}, intent, CALCS, {}, {'REQ-T': {'text': '工作 −40～+85 ℃，存储 −45～+70 ℃'}},
                           passes, lambda c, i: errors.append(c), lambda c, i: pending.append(i))
        self.assertEqual([], errors)
        self.assertNotIn('C1 100n/50V/X7R 的存储温度', summary['temperature']['missing'])

    def test_requirement_range_must_be_the_requirement_text(self):
        header = {'operating': {'min': -40, 'max': 85, 'source': 'req:REQ-T'}, 'storage': {'min': -40, 'max': 70, 'source': 'req:REQ-T'}}
        _, errors, _ = run(self.table([], header))
        self.assertIn('matrix_temperature_requirement_source', codes(errors))
        _, _, pending = run({'temperature': {'rows': []}})
        self.assertIn('matrix_temperature_requirement_missing', codes(pending))

    def test_a_part_written_twice_is_an_error(self):
        _, errors, _ = run(self.table([{'refs': ['U2']}, {'refs': ['U2']}]))
        self.assertIn('matrix_duplicate_object', codes(errors))


class PortStressTests(unittest.TestCase):
    def ports(self, j2_cells=(), j1=None, j2_extra=None):
        j2 = {'port': 'J2', 'stresses': [{'id': '浪涌', 'kind': 'surge', 'source': 'req:REQ-S'}], 'cells': list(j2_cells)}
        j2.update(j2_extra or {})
        return {'port_stress': [j1 or {'port': 'J1', 'no_stress_reason': 'x'}, j2]}

    def test_clamp_checked_against_the_bus_pin_concludes_its_cell(self):
        summary, errors, pending = run(self.ports([{'stress': '浪涌', 'ref': 'U4', 'calc': 'C-485', 'check': 'SM712 钳位 对 ADM2561E 总线脚绝对最大'}]))
        self.assertEqual([], [e for e in errors if e[0].startswith('matrix')])
        missing = [i for c, i in pending if c == 'matrix_cell_missing' and '端口 J2' in i]
        self.assertEqual(1, len(missing))           # 只剩 D1 自己的浪涌电流
        self.assertIn('D1', missing[0])

    def test_charge_check_does_not_close_the_clamp_cell(self):
        _, errors, _ = run(self.ports([{'stress': '浪涌', 'ref': 'U4', 'calc': 'C-485', 'check': 'R501 功耗 对 额定'}]))
        self.assertIn('matrix_check_not_about_object', codes(errors))

    def test_port_without_stresses_or_reason_is_missing(self):
        _, _, pending = run({'port_stress': []})
        self.assertTrue(any('端口 J2' in i and 'stresses' in i for c, i in pending if c == 'matrix_cell_missing'))

    def test_unknown_stress_kind_is_an_error(self):
        _, errors, _ = run(self.ports(j2_extra={'stresses': [{'id': 'x', 'kind': 'lightning', 'source': 'req:REQ-S'}]}))
        self.assertIn('matrix_schema', codes(errors))

    def test_low_side_reverse_mos_asks_for_each_other_port_ground_path(self):
        j1 = {'port': 'J1', 'stresses': [{'id': '反接', 'kind': 'reverse_polarity', 'source': 'req:REQ-S'}], 'cells': []}
        _, _, pending = run(self.ports(j1=j1))
        self.assertTrue(any('回线 VIN_RTN 经 Q1 才接 GND：经 J2 的地回路' in i for c, i in pending if c == 'matrix_cell_missing'))
        j1['return_paths'] = [{'via': 'Q1', 'port': 'J2', 'calc': 'C-RTN', 'check': '反接时经 J2 地回流 对 U4 GND 脚负压绝对最大'}]
        _, errors, pending = run(self.ports(j1=j1))
        self.assertFalse(any('地回路' in i for c, i in pending if c == 'matrix_cell_missing'))
        self.assertEqual([], [e for e in errors if e[0].startswith('matrix')])


class ProtectionStateTests(unittest.TestCase):
    def block(self, rows, latch='firmware'):
        return {'protection_states': [{'block': 'Ch', 'latch': latch, 'rows': rows}]}

    def test_block_without_latch_declaration_is_missing(self):
        _, _, pending = run({'protection_states': []})
        self.assertTrue(any('功能块 Ch' in i and 'latch' in i for c, i in pending if c == 'matrix_cell_missing'))

    def test_normal_off_with_latch_clear_must_be_a_row(self):
        rows = [{'state': s, 'latch': l, 'outcome': 'x', 'evidence': 'E1#表 3', 'verdict': 'ok'}
                for s in om.STATES for l in om.LATCH_STATES if (s, l) != ('normal_off', 'clear')]
        summary, errors, pending = run(self.block(rows))
        self.assertEqual(['功能块 Ch：正常关 × 锁清除'], summary['protection_states']['missing'][-1:])
        self.assertEqual(1, len([i for c, i in pending if c == 'matrix_cell_missing' and '功能块 Ch' in i]))

    def test_row_needs_outcome_and_known_evidence(self):
        rows = [{'state': 'normal_off', 'latch': 'clear', 'evidence': 'E1#表 3', 'verdict': 'ok'},
                {'state': 'short', 'latch': 'clear', 'outcome': 'x', 'evidence': 'E9#表 3', 'verdict': 'ok'}]
        _, errors, _ = run(self.block(rows))
        self.assertTrue({'matrix_state_without_outcome', 'matrix_evidence_unknown'} <= codes(errors))

    def test_block_without_latch_has_one_column(self):
        summary, _, _ = run(self.block([], latch='none'))
        self.assertEqual(5, len([m for m in summary['protection_states']['missing'] if '功能块 Ch' in m]))


class ClosureIntegrationTests(unittest.TestCase):
    def test_matrices_are_audited_and_missing_cells_keep_the_record_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            intent = root / 'intent.json'
            intent.write_text(json.dumps(INTENT), encoding='utf-8')
            (root / 'design.txt').write_text('evidence\n')
            record = {'schema_version': 1, 'coverage': 'complete', 'intent_sha256': sha256(intent),
                      'evidence': [{'id': 'E1', 'path': 'design.txt', 'sha256': sha256(root / 'design.txt'), 'locator': 'line 1'}],
                      'requirements': [{'id': 'R1', 'status': 'design_supported', 'refs': ['U2'], 'evidence': ['E1'],
                                        'implementation': 'MCU', 'depends_on': []}],
                      'work_items': [],
                      'calculations': [dict(CALCS['C-RST'], requirements=['R1'], evidence=['E1'], refs=['U1'], coverage='bounded',
                                            conclusion='supported', omitted_terms=[])]}
            record.update(CURRENT_VERSIONS)
            self.assertIn('matrix_schema', {e['code'] for e in closure_audit(record, intent, root)['errors']})
            record.update(matrices={})
            result = closure_audit(record, intent, root)
            self.assertIn('matrix_cell_missing', {p['code'] for p in result['pending']})
            self.assertIn('supervised_rails', result['matrices'])
            record['matrix_version'] = 2
            self.assertIn('outdated_record', {e['code'] for e in closure_audit(record, intent, root)['errors']})


if __name__ == '__main__':
    unittest.main()
