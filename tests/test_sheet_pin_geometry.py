"""Synthetic native sheet terminal contacts; the sheet outline stays unqualified."""
import os, sys, unittest
from pathlib import Path
ROOT = Path(os.environ.get('ASG_ROOT', Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT/'scripts'))
from schematic_layout.sexpr import form as f
from schematic_layout.scene import read_scene
from schematic_layout.qa import check_scene


def schematic(pin=None, end=(50.8, 50.8), label=None):
    sheet = f('sheet', f('at',50.8,40.64),f('size',25.4,25.4))
    if pin is not None:
        sheet.append(pin)
    root = f('kicad_sch',f('paper','A4'),sheet,
             f('wire',f('pts',f('xy',40.64,50.8),f('xy',*end))),
             f('label','SOURCE',f('at',40.64,50.8,0),
               f('effects',f('font',f('size',1.27,1.27)))))
    if label:
        root.append(label)
    return root


def terminal(point=(50.8,50.8), angle=180):
    return f('pin','PORT','input',f('at',*point,angle),
             f('effects',f('font',f('size',1.27,1.27))))


class SheetPinGeometryTests(unittest.TestCase):
    def report(self, root):
        return check_scene(read_scene(root))
    def orphan(self, root):
        return [x for x in self.report(root)['findings'] if x['code']=='orphan_wire']
    def test_wire_ending_at_explicit_sheet_pin_is_attached(self):
        self.assertEqual([],self.orphan(schematic(terminal())))
    def test_sheet_frame_without_terminal_does_not_attach(self):
        self.assertEqual(1,len(self.orphan(schematic())))
    def test_nearby_terminal_does_not_attach_wire(self):
        self.assertEqual(1,len(self.orphan(schematic(terminal((50.8,52.07))))))
    def test_unknown_pin_shape_stays_unqualified(self):
        p=terminal();p[2]='mystery'
        self.assertEqual(1,len(self.orphan(schematic(p))))
    def test_missing_terminal_coordinates_do_not_attach(self):
        p=f('pin','PORT','input')
        self.assertEqual(1,len(self.orphan(schematic(p))))
    def test_outline_gap_is_retained_after_valid_terminal_contact(self):
        report=self.report(schematic(terminal()))
        self.assertEqual('INSUFFICIENT',report['status'])
        self.assertIn('Unsupported sheet object: sheet',report['coverage']['gaps'])
        self.assertEqual(1,report['coverage']['sheet_pins'])
    def test_off_grid_terminal_is_reported(self):
        report=self.report(schematic(terminal((50.9,50.8)),end=(50.9,50.8)))
        self.assertTrue(any(x['code']=='off_grid' and x['objects'][0].startswith('sheet:') for x in report['findings']))
    def test_label_at_sheet_terminal_is_not_floating(self):
        root=schematic(terminal())
        root=[x for x in root if not isinstance(x,list) or x[0] not in ('wire','label')]
        root.append(f('label','PORT_NET',f('at',50.8,50.8,0),f('effects',f('font',f('size',1.27,1.27)))))
        self.assertFalse(any(x['code']=='floating_label' for x in self.report(root)['findings']))
    def test_invalid_angle_stays_unqualified(self):
        self.assertEqual(1,len(self.orphan(schematic(terminal(angle=45)))))
    def test_non_finite_coordinate_stays_unqualified(self):
        self.assertEqual(1,len(self.orphan(schematic(terminal((float('nan'),50.8))))))


if __name__=='__main__':
    unittest.main()
