"""Native KiCad export and role qualification regressions."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/fixtures')]
from external_supply_cases import build
from schematic_layout.native import find_cli
from schematic_layout.external_supply import audit_external_supply,judge,flag_references
from schematic_layout.generate import Libraries,library_dirs
from schematic_layout.sexpr import all_nodes,first,dump,Atom,form,parse
from schematic_layout.recipes import Sheet
from schematic_layout.project_audit import properties

class NativeExternalSupplyTests(unittest.TestCase):
    def setUp(self):
        if not find_cli():self.skipTest('kicad-cli unavailable')
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
    def case(self,name,expected,**kw):
        root,intent,sch,xml,record=build(self.base,name,**kw)
        self.assertEqual(record['export_returncode'],0,record)
        self.assertEqual(record['result']['status'],expected,record)
        return root,intent,sch,xml,record
    def test_native_standard_marker_and_literal_reference_text(self):
        *_,r=self.case('positive','PASS');self.assertTrue(r['text_preserved'])
    def test_native_custom_namespace_marker_and_undeclared_control(self):
        self.case('custom_flag','PASS',customflag=True)
        self.case('custom_undeclared','FAIL',customflag=True)
    def test_native_alias_avoids_real_component_reference(self):
        *_,r=self.case('alias_collision','PASS')
        self.assertNotIn('FLGX1',r['aliases']);self.assertTrue(r['text_preserved'])
    def test_native_missing_duplicate_and_wrong_net_markers(self):
        self.case('missing','FAIL',flags=0)
        self.case('duplicate','FAIL',flags=2)
        self.case('undeclared','FAIL',flagnet='GND')
    def test_native_nonconnector_and_role_type_contradiction(self):
        self.case('nonconnector','FAIL',kind='Device:R')
        self.case('role_type_conflict','FAIL',role='connector')
    def test_native_board_power_output_cannot_be_justified_by_flag(self):
        root,intent,sch,xml,_=self.case('board_source','PASS')
        from schematic_layout.sexpr import value
        import subprocess
        for lib in all_nodes(first(root,'lib_symbols'),'symbol'):
            if lib[1]=='Device:R':
                for sub in all_nodes(lib,'symbol'):
                    for pin in all_nodes(sub,'pin'):
                        if str(value(pin,'number'))=='1':pin[1]=Atom('power_out')
        sch.write_text(dump(root)+'\n')
        r=subprocess.run([find_cli(),'sch','export','netlist','--format','kicadxml','-o',str(xml),str(sch)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        result=audit_external_supply(sch,[sch],intent,xml,find_cli(),self.base/'board-source-probe')
        self.assertEqual(result['status'],'FAIL',result)
        self.assertIn('net_has_power_source',{e['kind'] for e in result['errors']})

    def test_missing_cache_cannot_pass(self):
        root,intent,sch,xml,_=self.case('missing_cache','PASS')
        root.remove(first(root,'lib_symbols'));sch.write_text(dump(root)+'\n')
        self.assertEqual(audit_external_supply(sch,[sch],intent,xml,find_cli(),self.base/'unknown')['status'],'INSUFFICIENT')
    def test_resolved_cached_inheritance_marker_is_detected(self):
        root,intent,sch,xml,_=self.case('inheritance','PASS')
        cache=first(root,'lib_symbols');base=next(s for s in all_nodes(cache,'symbol') if s[1]=='power:PWR_FLAG')
        base[1]='Custom:Base'
        cache.append(form('symbol','Custom:Inherited',form('extends','Custom:Base')))
        marker=next(s for s in all_nodes(root,'symbol') if properties(s).get('Reference')=='#FLG1')
        first(marker,'lib_id')[1]='Custom:Inherited';sch.write_text(dump(root)+'\n')
        self.assertEqual(flag_references([sch]),{str(sch.resolve()):{'#FLG1'}})
        # Missing cached parent must stay insufficient; installed libraries cannot fill it.
        cache.remove(base);sch.write_text(dump(root)+'\n')
        self.assertEqual(audit_external_supply(sch,[sch],intent,xml,find_cli(),self.base/'missing-parent')['status'],'INSUFFICIENT')
    def test_identity_and_role_are_bound_to_native_component(self):
        _,intent,_,xml,_=self.case('identity','PASS')
        probe=self.base/'identity/probe/external-supply-netlist.xml'
        aliases={'FLGX1':'#FLG1'}
        wrong=copy.deepcopy(intent);wrong['components'][0]['value']='different'
        self.assertEqual(judge(probe,wrong,aliases)['status'],'FAIL')
        wrong=copy.deepcopy(intent);wrong['components'][0]['fields']['ComponentRole']='connector'
        self.assertEqual(judge(probe,wrong,aliases)['status'],'FAIL')
    def test_custom_two_contact_connector_role_and_ordinary_rc(self):
        lib=Libraries(library_dirs()).load('Connector_Generic:Conn_01x02')
        lib[1]='Port'
        for s in all_nodes(lib,'symbol'):s[1]=str(s[1]).replace('Conn_01x02_','Port_')
        (self.base/'Synthetic.kicad_sym').write_text(dump(form('kicad_symbol_lib',form('version',20241209),form('generator','kicad_symbol_editor'),lib))+'\n')
        def intent(role=None):
            c={'ref':'J1','lib_id':'Synthetic:Port','value':'port','fields':{'ComponentRole':role} if role else {}}
            return {'schema_version':1,'components':[c], 'nets':[{'name':'VCC','pins':['J1.1']},{'name':'GND','pins':['J1.2']}]}
        s=Sheet(intent('connector'),rails={'GND':'power:GND'},dirs=[self.base])
        self.assertTrue(s._is_anchor('J1'));self.assertEqual(s.plan['parts']['J1']['role'],'anchor')
        s=Sheet(intent(),rails={'GND':'power:GND'},dirs=[self.base]);self.assertFalse(s._is_anchor('J1'))
        for name in ('R','C'):
            board=intent();board['components'][0]['lib_id']='Device:'+name
            self.assertFalse(Sheet(board,rails={'GND':'power:GND'})._is_anchor('J1'))

if __name__=='__main__':unittest.main()
