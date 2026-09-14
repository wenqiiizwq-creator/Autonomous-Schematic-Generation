"""Electrical and geometry checks for explicit local groups and bank fields."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from schematic_layout.generate import generate, routing_groups, make_root
from schematic_layout.native import verify, find_cli
from schematic_layout.sexpr import dump, all_nodes

class CompactPresentationTests(unittest.TestCase):
    def fixture(self):
        intent={'schema_version':1,'design_id':'compact-fields-test','components':[
            {'ref':f'C{i}','lib_id':'Device:C','value':'100uF/6.3V','footprint':''} for i in (1,2)],
            'nets':[{'name':'VOUT','pins':['C1.1','C2.1']},{'name':'GND','pins':['C1.2','C2.2']}], 'no_connect':[]}
        layout={'schema_version':1,'paper':'A4','placements':{},'nets':{'VOUT':{'groups':[{'pins':['C1.1']},['C2.1']]},'GND':{'groups':[{'pins':['C1.2','C2.2'],'rail_y':76.2}],'label':True}}}
        for i,x in [(1,50.8),(2,88.9)]:
            layout['placements'][f'C{i}']={'at':[x,63.5],'fields':{
              'Reference':{'at':[x+3.81,63.5],'angle':90,'font_mm':1.016},
              'Value':{'at':[x+5.588,63.5],'angle':90,'font_mm':1.016}}}
        return intent,layout
    def test_rail_float_noise_does_not_create_zero_length_serialized_wires(self):
        from schematic_layout.sexpr import parse, dump
        from schematic_layout.scene import read_scene
        from schematic_layout.qa import check_scene
        intent,layout=self.fixture()
        layout['nets']['GND']['groups'][0]['rail_y']=76.2+1e-12
        root,manifest=generate(intent,layout,'compact')
        report=check_scene(read_scene(parse(dump(root))))
        self.assertNotIn('zero_wire',report['counts'])

    def test_partial_duplicate_foreign_or_empty_groups_are_rejected(self):
        for groups in [[['C1.1']],[['C1.1'],['C1.1','C2.1']],[['C1.1'],['C9.1']],[[],['C1.1','C2.1']]]:
            intent,layout=self.fixture();layout['nets']['VOUT']['groups']=groups
            with self.assertRaisesRegex(ValueError,'partition'):
                routing_groups(intent,layout)
    def test_colliding_fields_cannot_bypass_qa(self):
        intent,layout=self.fixture()
        layout['placements']['C1']['fields']['Value']['at']=[50.8,63.5]
        with self.assertRaisesRegex(ValueError,'collides'):
            make_root(intent,layout,'compact')
    def test_groups_do_not_mutate_ir_or_leak_internal_names(self):
        intent,layout=self.fixture();original=copy.deepcopy((intent,layout))
        root,manifest=generate(intent,layout,'compact')
        self.assertEqual(original,(intent,layout))
        self.assertEqual(manifest['geometry']['status'],'PASS')
        self.assertEqual({str(n[1]) for n in all_nodes(root,'label')},{'VOUT','GND'})
        self.assertNotIn('__route_group_',dump(root))
    @unittest.skipUnless(find_cli(),'KiCad CLI absent')
    def test_native_groups_and_rotated_fields_preserve_physical_circuit(self):
        intent,layout=self.fixture();root,manifest=generate(intent,layout,'compact')
        with tempfile.TemporaryDirectory() as folder:
            from build_circuit import write_project
            path=write_project(Path(folder),'compact',root,manifest['library_sources'])
            report=verify(path,intent,layout,Path(folder)/'native')
            self.assertEqual(report['status'],'PASS',json.dumps(report))

if __name__=='__main__':unittest.main()
