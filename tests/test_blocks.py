"""blocks.py: block designs (task C4.4) merge by board net name into the whole-board design netlist (task C5.1); the
ports come from the architecture's flows, reference numbers from each block's range (user 2026-11-09 “按草案写入”)."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import blocks

INTENT = {
    'schema': 'project-hardware-intent-v1', 'revision': 'v1',
    'components': [{'ref': 'U1', 'lib_id': 'Reg:LDO', 'value': 'LDO'}, {'ref': 'C1', 'lib_id': 'Device:C', 'value': '1u'},
                   {'ref': 'U2', 'lib_id': 'MCU:M', 'value': 'MCU'}, {'ref': 'C2', 'lib_id': 'Device:C', 'value': '100n'},
                   {'ref': 'R1', 'lib_id': 'Device:R', 'value': '10k'}],
    'nets': {'VIN': ['U1.1', 'C1.1'], '+3V3': ['U1.2', 'U2.1', 'C2.1'], 'GND': ['U1.3', 'C1.2', 'U2.2', 'C2.2'],
             'NRST': ['U2.3', 'R1.1'], 'PULL': ['R1.2']},
    'no_connect': ['U2.4'], 'net_roles': {'VIN': 'power', '+3V3': 'power', 'GND': 'return', 'NRST': 'signal'},
    'net_voltages': [{'net': '+3V3', 'max': 3.6, 'unit': 'V', 'source': 'calc:C1'}], 'high_voltage_nets': [],
    'filtered_supply': [], 'external_supply': [{'net': 'VIN', 'pin': 'C1.1', 'reason': 'x'}],
    'reviewed_circuit_supply': [{'net': '+3V3', 'pin': 'U1.2', 'refs': ['U1', 'C2'], 'reason': 'y'}],
}
PLAN = {'pages': [
    {'file': 'root.kicad_sch', 'blocks': {'总览': ['U1', 'U2']}},
    {'file': '02_power.kicad_sch', 'blocks': {'LDO': ['U1', 'C1']}},
    {'file': '03_mcu.kicad_sch', 'blocks': {'主控': ['U2', 'C2'], '复位': ['R1']}},
]}
ARCH = {'schema_version': 1, 'domains': [{'name': '主电源', 'ground': 'GND'}],
        'blocks': [{'id': 'PSU', 'ref_range': [1, 99]}, {'id': 'MCU', 'ref_range': [100, 199]}],
        'flows': [{'name': '+3V3', 'kind': 'power', 'from': 'PSU', 'to': 'MCU', 'nets': ['+3V3'],
                   'params': {'voltage': '3.3 V ±3 %', 'current_max': '0.2 A'}}]}


def block(key, comps, nets, ports, **extra):
    return {'schema_version': 1, 'block': key, 'components': [{'ref': r, 'value': v} for r, v in comps],
            'nets': nets, 'ports': ports, 'no_connect': [], **extra}


PSU = block('PSU', [('U1', 'LDO'), ('C1', '1u')], {'VIN': ['U1.1', 'C1.1'], '+3V3': ['U1.2'], 'GND': ['U1.3', 'C1.2']},
            ['+3V3', 'GND'], net_roles={'+3V3': 'power', 'GND': 'return'})
MCU = block('MCU', [('U101', 'MCU'), ('C101', '100n')], {'+3V3': ['U101.1', 'C101.1'], 'GND': ['U101.2', 'C101.2']},
            ['+3V3', 'GND'], net_roles={'+3V3': 'power', 'GND': 'return'})


class RoundtripTest(unittest.TestCase):
    def test_overview_page_is_skipped_and_parts_have_one_owner(self):
        assignment, problems = blocks.assignment_from_plan(PLAN)
        self.assertEqual(problems, [])
        self.assertEqual(set(assignment), {'02_power:LDO', '03_mcu:主控', '03_mcu:复位'})
        self.assertEqual(set(blocks.assignment_from_plan(PLAN, 'page')[0]), {'02_power', '03_mcu'})

    def test_roundtrip_is_pin_for_pin(self):
        for by in ('block', 'page'):
            stats = blocks.roundtrip(copy.deepcopy(INTENT), PLAN, by)
            self.assertEqual(([], []), (stats['problems'], stats['differences']), by)
        stats = blocks.roundtrip(copy.deepcopy(INTENT), PLAN)
        self.assertEqual(sorted(stats['shared_supply_nets']), ['+3V3', 'GND'])
        self.assertEqual(stats['shared_signal_nets'], {'NRST': ['03_mcu:主控', '03_mcu:复位']})
        self.assertEqual(len(stats['cross_block_annotations']), 1)

    def test_unassigned_and_doubly_assigned_parts_fail(self):
        _, _, problems = blocks.split(INTENT, {'A': ['U1', 'C1', 'U2'], 'B': ['C2', 'U2']})
        self.assertTrue(any('R1 不归任何块' in p for p in problems))
        self.assertTrue(any('U2 同时归' in p for p in problems))


class MergeTest(unittest.TestCase):
    def test_blocks_merge_by_port_name_and_each_part_names_its_block(self):
        intent, problems = blocks.merge({'PSU': PSU, 'MCU': MCU}, {'revision': 'v2'}, ARCH)
        self.assertEqual([], problems)
        self.assertEqual(sorted(intent['nets']['+3V3']), ['C101.1', 'U1.2', 'U101.1'])
        self.assertEqual({'PSU', 'MCU'}, {c['fields']['Circuit'] for c in intent['components']})
        self.assertEqual(('project-hardware-intent-v1', 'v2'), (intent['schema'], intent['revision']))

    def test_reference_numbers_are_never_changed_and_a_repeat_fails(self):
        mcu = copy.deepcopy(MCU)
        mcu['components'][0]['ref'] = 'U1'
        mcu['nets'] = {'+3V3': ['U1.1', 'C101.1'], 'GND': ['U1.2', 'C101.2']}
        _, problems = blocks.merge({'PSU': PSU, 'MCU': mcu})
        self.assertIn('位号 U1 在块 MCU 与 PSU 重复', problems)
        _, problems = blocks.merge({'PSU': PSU, 'MCU': mcu}, None, ARCH)
        self.assertTrue(any('U1 不在本块编号段 100–199' in p for p in problems), problems)

    def test_ports_come_from_the_flows_and_internal_nets_keep_off_board_names(self):
        psu = copy.deepcopy(PSU)
        psu['ports'].append('VIN')
        self.assertTrue(any('端口 VIN 不是与本块相连的流向' in p for p in blocks.check_block(psu, ARCH)))
        mcu = copy.deepcopy(MCU)
        mcu['ports'] = ['GND']
        self.assertTrue(any('块内网络 +3V3 与整板网络重名' in p for p in blocks.check_block(mcu, ARCH)))
        self.assertTrue(any('不是 architecture.json 的功能块' in p for p in blocks.check_block(block('PFC', [], {}, []), ARCH)))

    def test_lonely_port_fails_unless_the_other_blocks_are_not_written_yet(self):
        _, problems = blocks.merge({'PSU': PSU})
        self.assertIn('端口 +3V3 只有块 PSU 用到，没有对端', problems)
        self.assertEqual([], blocks.merge({'PSU': PSU}, loose=True)[1])

    def test_internal_name_clash_and_conflicting_role_fail(self):
        a = block('A', [('R1', '1k')], {'MID': ['R1.1']}, [])
        b = block('B', [('R2', '1k')], {'MID': ['R2.1']}, [])
        self.assertTrue(any('块内网络 MID' in p for p in blocks.merge({'A': a, 'B': b})[1]))
        mcu = copy.deepcopy(MCU)
        mcu['net_roles']['GND'] = 'signal'
        self.assertTrue(any('GND 的角色' in p for p in blocks.merge({'PSU': PSU, 'MCU': mcu})[1]))

    def test_merge_record_reads_the_folder_and_the_board_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = Path(tmp) / 'record'
            (record / 'blocks').mkdir(parents=True)
            (record / 'architecture.json').write_text(json.dumps(ARCH), encoding='utf-8')
            for data in (PSU, MCU, block('BOARD', [], {}, [], header={'title': '样板'})):
                (record / 'blocks' / (data['block'] + '.json')).write_text(json.dumps(data, ensure_ascii=False),
                                                                          encoding='utf-8')
            intent, problems = blocks.merge_record(tmp)
            self.assertEqual([], problems)
            self.assertEqual('样板', intent['title'])
            self.assertEqual(0, blocks.main(['merge', tmp]))
            self.assertTrue((record / 'electrical-intent.json').is_file())
            _, problems = blocks.merge_record(tmp, loose=True, only={'MCU', 'PFC'})
            self.assertIn('缺少块设计 blocks/PFC.json（任务 C4.4）', problems)


if __name__ == '__main__':
    unittest.main()
