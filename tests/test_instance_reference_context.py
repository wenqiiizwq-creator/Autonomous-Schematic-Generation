"""Synthetic annotation context regressions; no public circuit copied."""
import os, sys, unittest
from pathlib import Path
ROOT=Path(os.environ.get('ASG_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
from schematic_layout.scene import read_scene
from schematic_layout.sexpr import parse

def scene(entries='', root_uuid='CURRENT', property_ref='R100', unit=1):
    instances=f'(instances {entries})' if entries else ''
    return read_scene(parse(f'''(kicad_sch (uuid "{root_uuid}") (paper "A4")
      (lib_symbols (symbol "Synthetic:Probe"
        (symbol "Probe_0_1" (rectangle (start 0 -1) (end 2 1) (stroke (width 0.254)))
          (pin passive line (at -2.54 0 0) (length 2.54) (name "A") (number "1")))))
      (symbol (lib_id "Synthetic:Probe") (at 50.8 50.8 0) (unit {unit})
        (property "Reference" "{property_ref}" (at 50.8 45.72 0)
          (effects (font (size 1.27 1.27)))) {instances}))'''))

def entry(project, path, ref, unit=1):
    return f'(project "{project}" (path "{path}" (reference "{ref}") (unit {unit})))'

class InstanceReferenceContext(unittest.TestCase):
    def test_unique_current_root_context_selects_native_reference(self):
        s=scene(entry('OLD','/OLD','R100')+entry('CURRENT','/CURRENT','R2'))
        self.assertEqual(s.symbols[0].ref,'R2')
        self.assertEqual(s.symbols[0].pins[0].id,'R2.1')
        self.assertEqual(dict(s.symbols[0].fields)['Reference'].text,'R2')
    def test_no_instances_preserves_property(self):
        self.assertEqual(scene().symbols[0].ref,'R100')
    def test_same_reference_instances_are_compatible(self):
        s=scene(entry('A','/OTHER_A','R100')+entry('B','/OTHER_B','R100'))
        self.assertEqual(s.symbols[0].ref,'R100')
        self.assertFalse(s.gaps)
    def test_same_path_conflicting_projects_remains_insufficient(self):
        s=scene(entry('A','/CURRENT','R2')+entry('B','/CURRENT','R3'))
        self.assertTrue(s.gaps)
    def test_unbound_reused_sheet_conflict_remains_insufficient(self):
        s=scene(entry('A','/ROOT/ONE','R2')+entry('A','/ROOT/TWO','R3'))
        self.assertTrue(s.gaps)
    def test_annotation_unit_conflict_is_not_silently_remapped(self):
        s=scene(entry('CURRENT','/CURRENT','R2',2))
        self.assertTrue(s.gaps)
    def test_ambiguous_context_never_arbitrarily_selects_an_instance(self):
        s=scene(entry('A','/CURRENT','R2')+entry('B','/CURRENT','R3'))
        self.assertEqual(s.symbols[0].ref,'R100')
    def test_missing_annotation_unit_is_not_inferred_from_symbol(self):
        s=scene('(project "CURRENT" (path "/CURRENT" (reference "R2")))')
        self.assertTrue(s.gaps)
        self.assertEqual(s.symbols[0].ref,'R100')
    def test_empty_project_identity_is_incomplete(self):
        self.assertTrue(scene(entry('','/CURRENT','R2')).gaps)
    def test_empty_path_is_incomplete_even_with_matching_reference(self):
        self.assertTrue(scene(entry('CURRENT','','R100')).gaps)
    def test_missing_root_uuid_does_not_qualify_instance_consensus(self):
        self.assertTrue(scene(entry('CURRENT','/OTHER','R100'),root_uuid='').gaps)
    def test_nonpositive_annotation_unit_is_incomplete(self):
        self.assertTrue(scene(entry('CURRENT','/CURRENT','R2',0)).gaps)

if __name__=='__main__':unittest.main()
