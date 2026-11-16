"""C4 gate: the three things later stages used to find first (H-001 rerun 2026-11-15)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_module


def comp(ref, lib_id):
    return {'ref': ref, 'lib_id': lib_id, 'value': lib_id.split(':')[1]}


INTENT = {'components': [comp('U101', 'ASG_Project:TPS26600'), comp('Q201', 'Transistor_FET:BSS138'),
                         comp('J101', 'Connector:Conn_01x02_Pin'), comp('D301', 'Device:LED')],
          'nets': {'GND': ['U101.9', 'J101.2', 'Q201.2'], 'PG': ['Q201.3', 'D301.1']}}
SCOPE = {'guideline_scope': {'device_kinds': ['ic', 'mosfet', 'connector', 'led']}}


class BoardConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.record = Path(self.tmp.name)
        self.write('reference-input.json', {'scope': {'core_refs': ['U101', 'Q201']}, 'pin_maps': {'U101': {}},
                                            'checks': [{'id': 'gnd', 'kind': 'same_net', 'pins': ['U101.9', 'J101.2']}],
                                            'features': [{'id': 'f', 'stages': [{'refs': ['U101']}]}]})
        self.write('selection.json', {'roles': [{'role': 'a', 'refs': ['U101']}, {'role': 'b', 'refs': ['Q201']}]})

    def write(self, name, data):
        (self.record / name).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def problems(self, requirements=SCOPE):
        return check_module.board_consistency(self.record, INTENT, requirements)

    def test_a_consistent_board_passes_in_both_net_forms(self):
        self.assertEqual(self.problems(), [])
        listed = dict(INTENT, nets=[[k, v] for k, v in INTENT['nets'].items()])
        self.assertEqual(check_module.board_consistency(self.record, listed, SCOPE), [])

    def test_a_table_citing_an_old_designator_is_named(self):
        self.write('reference-input.json', {'checks': [{'id': 'gnd', 'kind': 'same_net', 'pins': ['U101.9', 'J1.2']}],
                                            'features': [{'id': 'f', 'stages': [{'refs': ['J1']}]}]})
        found = self.problems()
        self.assertEqual(len(found), 1)
        self.assertIn('J1.2（checks gnd）', found[0])
        self.assertIn('J1（features f）', found[0])

    def test_a_core_part_without_a_selection_role_is_named(self):
        self.write('selection.json', {'roles': [{'role': 'a', 'refs': ['U101']}]})
        self.assertEqual([p for p in self.problems() if '选型角色' in p and 'Q201' in p and 'U101' not in p][:1],
                         self.problems())

    def test_a_device_kind_outside_the_guideline_scope_is_named(self):
        found = self.problems({'guideline_scope': {'device_kinds': ['ic', 'connector', 'led']}})
        self.assertEqual(len(found), 1)
        self.assertIn('mosfet（Q201）', found[0])

    def test_missing_records_are_left_to_their_own_checks(self):
        for name in ('reference-input.json', 'selection.json'):
            (self.record / name).unlink()
        self.assertEqual(self.problems({}), [])


if __name__ == '__main__':
    unittest.main()
