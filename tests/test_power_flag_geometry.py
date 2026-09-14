"""Power-source markers must attach legally without masking body traversal."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from schematic_layout.generate import Libraries, library_dirs
from schematic_layout.scene import read_scene
from schematic_layout.qa import check_scene
from schematic_layout.sexpr import form as f


class PowerFlagGeometryTests(unittest.TestCase):
    def findings(self, start, end):
        lib = Libraries(library_dirs()).load('power:PWR_FLAG')
        root = f('kicad_sch', f('paper', 'A4'), f('lib_symbols', lib),
                 f('symbol', f('lib_id', 'power:PWR_FLAG'), f('at', 50.8, 50.8, 0),
                   f('unit', 1), f('property', 'Reference', '#FLG01',
                                  f('effects', f('hide', 'yes')))),
                 f('wire', f('pts', f('xy', *start), f('xy', *end))))
        return [x for x in check_scene(read_scene(root))['findings'] if x['code']=='wire_body']

    def test_source_wire_leaves_body_from_its_terminal(self):
        self.assertEqual([], self.findings((50.8,50.8),(50.8,55.88)))

    def test_traversal_into_flag_remains_a_defect(self):
        self.assertTrue(self.findings((50.8,50.8),(50.8,45.72)))

    def test_foreign_wire_across_flag_remains_a_defect(self):
        self.assertTrue(self.findings((45.72,48.895),(55.88,48.895)))

    def test_wire_along_body_edge_is_not_point_contact(self):
        self.assertTrue(self.findings((50.8,50.8),(55.88,50.8)))


if __name__=='__main__':unittest.main()
