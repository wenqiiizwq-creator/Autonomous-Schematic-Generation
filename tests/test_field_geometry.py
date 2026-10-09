"""Compare field anchor transforms with independent native stroke bounds."""
import json,os,sys,unittest
from pathlib import Path
ROOT=Path(os.environ.get('ASG_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
from schematic_layout.scene import read_scene
from schematic_layout.sexpr import parse
from schematic_layout.qa import check_scene
FIX=Path(__file__).resolve().parent/'fixtures/drawing/field_geometry'


class FieldGeometryTests(unittest.TestCase):
    def test_all_96_native_anchor_and_rotation_cases(self):
        scene=read_scene(parse((FIX/'field-matrix.kicad_sch').read_text()))
        fields={s.ref:dict(s.fields)['Reference'] for s in scene.symbols}
        for r in json.loads((FIX/'native-matrix.json').read_text()):
            with self.subTest(style={k:r[k] for k in ('symbol_angle','mirror','field_angle','justify')}):
                b=fields[r['ref']].box().expanded(.16)
                x0,y0,x1,y1=r['native_ink_box']
                self.assertTrue(b.contains_point(x0,y0) and b.contains_point(x1,y1),
                                (r,b))
                self.assertEqual(r['native_long_axis'],'x' if b.width>b.height else 'y')
    def test_native_clear_mirrored_field_does_not_hit_own_body(self):
        r=check_scene(read_scene(parse((FIX/'mirrored-field-positive.kicad_sch').read_text())))
        self.assertFalse([x for x in r['findings'] if x['code'] in ('text_body_overlap','text_pin_overlap')])
    def test_foreign_wire_crossing_actual_mirrored_text_is_caught(self):
        r=check_scene(read_scene(parse((FIX/'mirrored-field-negative.kicad_sch').read_text())))
        self.assertTrue([x for x in r['findings'] if x['code']=='wire_text' and any('Reference' in n for n in x['objects'])])


if __name__=='__main__':unittest.main()
