"""Stock hidden pad copies retain physical connectivity in native KiCad."""
import copy, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from schematic_layout.generate import generate, make_root, route_root
from schematic_layout.native import verify, find_cli
from schematic_layout.scene import read_scene
from build_circuit import write_project

class SharedTerminalTests(unittest.TestCase):
    def fixture(self):
        nets={'SW':[1,2,3], 'VIN':[10,11,12,13], 'GND':[6,7,8,15,16,17], 'PG':[4], 'FB':[5], 'SS':[9], 'VOUT':[14]}
        intent={'schema_version':1,'design_id':'pads','components':[{'ref':'U1','lib_id':'Regulator_Switching:TPS62130','value':'TPS62130','units':[1]}], 'nets':[{'name':n,'pins':[f'U1.{p}' for p in ps]} for n,ps in nets.items()], 'no_connect':[]}
        layout={'schema_version':1,'placements':{'U1':{'at':[101.6,76.2],'fields':{'Reference':{'at':[101.6,50.8]},'Value':{'at':[101.6,53.34]}}}},'nets':{n:{'mode':'labels'} for n in nets}}
        return intent,layout
    def test_shared_tips_keep_every_physical_pin(self):
        intent,layout=self.fixture();root,m=generate(intent,layout,'pads')
        self.assertEqual(len([p for s in read_scene(root).symbols for p in s.pins]),17)
        self.assertEqual(len(m['shared_terminals']),3)
        self.assertEqual(m['geometry']['status'],'PASS')
    def test_different_nets_or_nc_on_shared_pad_rejected(self):
        for use_nc in (False,True):
            intent,layout=self.fixture();intent['nets'][0]['pins'].remove('U1.2')
            if use_nc:intent['no_connect'].append('U1.2')
            else:intent['nets'].append({'name':'BAD','pins':['U1.2']})
            with self.assertRaisesRegex(ValueError,'Coincident'):make_root(intent,layout,'pads')
    def test_visual_partition_cannot_split_shared_terminal(self):
        intent,layout=self.fixture();layout['nets']['SW']['groups']=[['U1.1'],['U1.2','U1.3']]
        root,_,uid,res=make_root(intent,layout,'pads')
        with self.assertRaisesRegex(ValueError,'Shared terminal split'):route_root(root,intent,layout,uid,res)
    @unittest.skipUnless(find_cli(),'KiCad CLI absent')
    def test_native_export_retains_all_seventeen_pads(self):
        intent,layout=self.fixture();root,m=generate(intent,layout,'pads')
        with tempfile.TemporaryDirectory() as d:
            path=write_project(Path(d),'pads',root,m['library_sources'])
            report=verify(path,intent,layout,Path(d)/'native')
            self.assertEqual(report['netlist']['status'],'PASS',json.dumps(report['netlist']))
            # This isolated IC has no external power source; ERC must stay separate.
            self.assertEqual(report['erc']['status'],'FAIL')

class LibraryPresentationTests(unittest.TestCase):
    def test_hidden_nc_cannot_be_wired(self):
        intent={'schema_version':1,'design_id':'jack','components':[{'ref':'J1','lib_id':'Connector:RJ45_Wuerth_7499010121A','value':'7499010121A'}], 'nets':[{'name':f'N{x}','pins':[f'J1.{x}']} for x in [1,2,3,4,5,6,7,8,9,10,11,12,'SH']], 'no_connect':[]}
        layout={'schema_version':1,'placements':{'J1':{'at':[127,101.6]}}}
        with self.assertRaisesRegex(ValueError,'Library no_connect'):make_root(intent,layout,'jack')
        intent['nets']=[n for n in intent['nets'] if n['pins']!=['J1.7']];intent['no_connect']=['J1.7']
        root,_,_,_=make_root(intent,layout,'jack')
        self.assertFalse(read_scene(root).gaps)
    def test_long_left_facing_label_expands_without_erasing_physical_pins(self):
        intent={'schema_version':1,'design_id':'longlabel','components':[{'ref':'R1','lib_id':'Device:R','value':'1k'}], 'nets':[{'name':'LONG_INTERFACE_NET_NAME','pins':['R1.1']},{'name':'GND','pins':['R1.2']}], 'no_connect':[]}
        layout={'schema_version':1,'placements':{'R1':{'at':[127,76.2],'rotation':90}},'nets':{n['name']:{'mode':'labels'} for n in intent['nets']}}
        root,m=generate(intent,layout,'longlabel');self.assertEqual(m['geometry']['status'],'PASS')

if __name__=='__main__':unittest.main()
