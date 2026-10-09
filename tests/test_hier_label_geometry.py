"""Native-calibrated hierarchical text bounds retain real crossings and gaps."""
import json,os,sys,unittest
from pathlib import Path
ROOT=Path(os.environ.get('ASG_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
from schematic_layout.scene import read_scene,HierarchicalLabelText
from schematic_layout.sexpr import parse,first,set_node
from schematic_layout.qa import check_scene
FIX=Path(__file__).resolve().parent/'fixtures/drawing/hier_label_geometry'


class HierLabelGeometryTests(unittest.TestCase):
    def test_all_60_native_text_bounds_and_unchanged_anchors(self):
        scene=read_scene(parse((FIX/'hier-matrix.kicad_sch').read_text()))
        labels={f.text:f for _,f in scene.labels}
        for r in json.loads((FIX/'native-matrix.json').read_text()):
            with self.subTest(angle=r['angle'],shape=r['shape'],font=r['font']):
                field=labels[r['ref']];self.assertEqual(tuple(r['at']),(field.x,field.y))
                b=field.box().expanded(.16);x0,y0,x1,y1=r['native_ink_box']
                self.assertTrue(b.contains_point(x0,y0) and b.contains_point(x1,y1),(r,b))
    def test_wire_exits_opposite_label_text_without_false_crossing(self):
        r=check_scene(read_scene(parse((FIX/'positive.kicad_sch').read_text())))
        self.assertFalse([x for x in r['findings'] if x['code']=='wire_text'])
        self.assertTrue(any('hierarchical_label' in g for g in r['coverage']['gaps']))
        self.assertNotEqual('PASS',r['status'])
    def test_foreign_wire_crossing_real_label_text_still_fails(self):
        r=check_scene(read_scene(parse((FIX/'negative.kicad_sch').read_text())))
        self.assertTrue([x for x in r['findings'] if x['code']=='wire_text'])
    def test_untested_font_and_text_do_not_claim_calibrated_bounds(self):
        for mode in ('font','escaped_text','angle'):
            root=parse((FIX/'positive.kicad_sch').read_text());label=first(root,'hierarchical_label')
            if mode=='font':set_node(first(first(label,'effects'),'font'),'face','Other font')
            if mode=='escaped_text':label[1]='N_{SUBSCRIPT}'
            if mode=='angle':first(label,'at')[3]='45'
            scene=read_scene(root)
            self.assertFalse(isinstance(scene.labels[0][1],HierarchicalLabelText))
            self.assertIn('Hierarchical label text style needs native review',scene.gaps)


if __name__=='__main__':unittest.main()
