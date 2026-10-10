"""Explicit unfilled polyline ink, separate from electrical connectivity."""
import os,sys,unittest
from pathlib import Path
ROOT=Path(os.environ.get('ASG_ROOT',Path(__file__).resolve().parents[1]));sys.path.insert(0,str(ROOT/'scripts'))
from schematic_layout.scene import read_scene,Symbol,Pin
from schematic_layout.geometry import Box,TextField
from schematic_layout.sexpr import parse
from schematic_layout.qa import check_scene

def scene(points='(xy 20 20) (xy 60 20)', extras='',width='0.254',style='default'):
    return read_scene(parse(f'''(kicad_sch (paper "A4")
      (polyline (pts {points}) (stroke (width {width}) (type {style})) {extras}))'''))
def report(s):return check_scene(s,grid=1,reserved=[])
def codes(s):return {x['code'] for x in report(s)['findings']}

class SheetPolyline(unittest.TestCase):
    def test_clear_explicit_stroke_is_covered(self):
        r=report(scene());self.assertEqual(r['status'],'PASS');self.assertEqual(r['coverage']['graphic_segments'],1)
    def test_outline_empty_interior_not_a_solid_obstacle(self):
        s=scene('(xy 20 20) (xy 60 20) (xy 60 60) (xy 20 60) (xy 20 20)')
        s.labels=[('text',TextField('INSIDE',40,40))]
        self.assertEqual(report(s)['status'],'PASS')
    def test_text_crossing_graphic_ink(self):
        s=scene();s.labels=[('text',TextField('LABEL',40,20))]
        self.assertIn('graphic_text',codes(s))
    def test_symbol_body_crossing_graphic_ink(self):
        s=scene();s.symbols=[Symbol('U1','Test:X',1,[],Box(38,18,42,22),[],[])]
        self.assertIn('graphic_body',codes(s))
    def test_diagonal_ink_text_collision(self):
        s=scene('(xy 20 20) (xy 60 60)');s.labels=[('text',TextField('LABEL',40,40))]
        self.assertIn('graphic_text',codes(s))
    def test_diagonal_empty_aabb_not_a_collision(self):
        s=scene('(xy 20 20) (xy 60 60)');s.labels=[('text',TextField('LABEL',30,50))]
        self.assertEqual(report(s)['status'],'PASS')
    def test_graphic_wire_collision_does_not_create_net_contact(self):
        s=scene();s.wires=[((40,10),(40,30))]
        r=report(s);self.assertIn('graphic_wire',{x['code'] for x in r['findings']})
        self.assertEqual(len(s.wires),1);self.assertNotIn('different_net_contact',{x['code'] for x in r['findings']})
    def test_graphic_pin_leg_collision(self):
        s=scene();s.symbols=[Symbol('U1','Test:X',1,[],None,[Pin('U1.1',(40,18),(40,22),(0,-1),'passive')],[])]
        self.assertIn('graphic_pin',codes(s))
    def test_graphic_ink_off_page(self):
        self.assertIn('off_page',codes(scene('(xy 2 20) (xy 20 20)')))
    def test_title_region_ink_is_checked(self):
        r=check_scene(scene('(xy 190 180) (xy 200 180)'),grid=1)
        self.assertTrue(any(x['code']=='reserved_region' for x in r['findings']))
    def test_uncertified_native_forms_keep_coverage_gap(self):
        cases=[{'extras':'(fill (type background))'},{'style':'dash'}, {'width':'0'},
               {'points':'(xy 20 20)'},{'points':'(xy nan 20) (xy 60 20)'},
               {'points':'(xy 20 20) (xy 20 20)'},{'points':'(xy 20 20 5) (xy 60 20)'},
               {'extras':'(unknown yes)'},{'width':'-0.2'}]
        for c in cases:
            with self.subTest(c=c):self.assertEqual(report(scene(**c))['status'],'INSUFFICIENT')
    def test_other_unsupported_objects_keep_coverage_gap(self):
        s=read_scene(parse('(kicad_sch (paper "A4") (rectangle (start 20 20) (end 40 40)))'))
        self.assertEqual(report(s)['status'],'INSUFFICIENT')
    def test_native_stroke_half_width_at_frame_boundary(self):
        self.assertEqual(report(scene('(xy 5.2 20) (xy 20 20)'))['status'],'PASS')
        self.assertIn('off_page',codes(scene('(xy 5.1 20) (xy 20 20)')))
    def test_mixed_qualified_and_unknown_strokes_keep_gap(self):
        s=read_scene(parse('''(kicad_sch (paper "A4")
          (polyline (pts (xy 20 20) (xy 60 20)) (stroke (width 0.254) (type default)))
          (polyline (pts (xy 20 40) (xy 60 40)) (stroke (width 0) (type default))))'''))
        self.assertEqual(report(s)['status'],'INSUFFICIENT')
        self.assertEqual(report(s)['coverage']['graphic_segments'],1)
    def test_unknown_properties_and_duplicate_stroke_retain_gap(self):
        for extras in ['(stroke (width 0.254) (type default))','(pts (xy 20 20) (xy 60 20))']:
            with self.subTest(extras=extras):
                self.assertEqual(report(scene(extras=extras))['status'],'INSUFFICIENT')
    def test_graphic_crossing_is_review_warning_without_connectivity(self):
        s=scene();s.wires=[((40,10),(40,30))]
        r=report(s);hits=[f for f in r['findings']if f['code']=='graphic_wire']
        self.assertEqual([f['severity']for f in hits],['warning'])
    def test_conservative_text_collision_requires_review_not_pass(self):
        s=scene();s.labels=[('text',TextField('LABEL',40,20))]
        r=report(s);self.assertEqual(r['status'],'REVIEW')
        self.assertEqual([(f['code'],f['severity'])for f in r['findings']],[('graphic_text','warning')])
    def test_round_cap_clear_of_symbol_corner(self):
        s=scene('(xy 20 40) (xy 40 40)')
        s.symbols=[Symbol('U1','Test:X',1,[],Box(40.1,40.1,45,45),[],[])]
        self.assertNotIn('graphic_body',codes(s))
    def test_round_cap_touching_symbol_corner_is_collision(self):
        s=scene('(xy 20 40) (xy 40 40)')
        s.symbols=[Symbol('U1','Test:X',1,[],Box(40.08,40.08,45,45),[],[])]
        self.assertIn('graphic_body',codes(s))
    def test_round_cap_clear_of_reserved_corner(self):
        s=scene('(xy 30 49.2) (xy 49.2 49.2)',width='2')
        r=check_scene(s,grid=1,reserved=[Box(50,50,60,60)])
        self.assertFalse(any(f['code']=='reserved_region'for f in r['findings']))
    def test_round_cap_entering_reserved_corner_is_collision(self):
        s=scene('(xy 30 49.4) (xy 49.4 49.4)',width='2')
        r=check_scene(s,grid=1,reserved=[Box(50,50,60,60)])
        self.assertTrue(any(f['code']=='reserved_region'for f in r['findings']))
    def test_diagonal_stroke_clear_and_touching_corner(self):
        for offset,collision in [(1.6,False),(1.0,True)]:
            with self.subTest(offset=offset):
                s=scene('(xy 20 20) (xy 40 40)',width='2')
                # Use a small box wholly above y=x; its lower-right corner
                # must be more than the stroke radius from the centreline.
                s.symbols=[Symbol('U1','Test:X',1,[],Box(30,30+offset,30.1,30+offset+0.1),[],[])]
                self.assertEqual('graphic_body'in codes(s),collision)

if __name__=='__main__':unittest.main()
