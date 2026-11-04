import copy, hashlib, json, os, shutil, sys, tempfile, unittest
from unittest import mock
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from schematic_layout.external_supply import judge
from schematic_layout.circuit_supply import binding, declarations
from test_filtered_supply import xml
from schematic_layout.native import compare_netlist
from schematic_layout import citations
from test_citations import pdf

class ReviewedCircuitSupplyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
  self.ev=self.p/'review.md';self.ev.write_text('SRC1: connector, diode polarity and capacitor return reviewed. Scope: source semantics only.')
  self.i={'components':[{'ref':'D1','lib_id':'Device:D','value':'D'},{'ref':'C1','lib_id':'Device:C','value':'10u'}], 'nets':[{'name':'IN','pins':['D1.2']},{'name':'VCC','pins':['D1.1','C1.1']},{'name':'GND','pins':['C1.2']}], 'net_roles':{'VCC':'power'}}
  d={'net':'VCC','pin':'D1.1','refs':['D1','C1'],'reason':'diode supply reviewed','evidence':{'path':'review.md','sha256':hashlib.sha256(self.ev.read_bytes()).hexdigest(),'locator':'SRC1'},'binding_sha256':binding(self.i,['D1','C1'])}
  self.i['reviewed_circuit_supply']=[d]
  self.n={'IN':[('D1','2','passive')],'VCC':[('D1','1','passive'),('C1','1','passive'),('FLGX1','1','power_out')],'GND':[('C1','2','passive')]}
 def run_case(self):
  f=self.p/'n.xml';f.write_text(xml(self.n,{'D1':('Device','D','D'),'C1':('Device','C','10u')}))
  return judge(f,self.i,{'FLGX1':'#FLG1'})
 def test_bound_review_passes_without_changing_passive_pin_types(self):self.assertEqual(self.run_case()['status'],'PASS')
 def test_missing_review_fails(self):self.ev.unlink();self.assertEqual(self.run_case()['status'],'FAIL')
 def test_stale_document_fails(self):self.ev.write_text('changed');self.assertEqual(self.run_case()['status'],'FAIL')
 def test_locator_fails(self):self.i['reviewed_circuit_supply'][0]['evidence']['locator']='absent';self.assertEqual(self.run_case()['status'],'FAIL')
 def test_stale_parameter_fails(self):self.i['components'][1]['value']='22u';self.assertEqual(self.run_case()['status'],'FAIL')
 def test_reversed_native_diode_fails(self):self.n['IN'][0]=('D1','1','passive');self.n['VCC'][0]=('D1','2','passive');self.assertEqual(self.run_case()['status'],'FAIL')
 def test_disconnected_return_is_the_netlist_gates(self):
  self.n['IN']+=self.n.pop('GND');self.assert_netlist_gate_catches()
 def test_signal_flag_fails(self):self.i['net_roles']['VCC']='signal';self.assertEqual(self.run_case()['status'],'FAIL')
 def test_missing_role_fails(self):self.i['net_roles']={};self.assertEqual(self.run_case()['status'],'FAIL')
 def test_undeclared_flag_fails(self):self.i.pop('reviewed_circuit_supply');self.assertEqual(self.run_case()['status'],'FAIL')
 def test_duplicate_flag_fails(self):self.n['VCC'].append(('FLGX1','2','power_out'));self.assertEqual(self.run_case()['status'],'FAIL')
 def test_native_source_conflict_fails(self):self.n['VCC'].append(('U1','1','power_out'));self.assertEqual(self.run_case()['status'],'FAIL')
 def test_duplicate_declaration_rejected(self):self.i['reviewed_circuit_supply']*=2;self.assertRaises(ValueError,declarations,self.i)
 def test_review_path_escape_fails(self):self.i['reviewed_circuit_supply'][0]['evidence']['path']='../review.md';self.assertEqual(self.run_case()['status'],'FAIL')
 def test_review_kept_outside_schematic_folder_resolves_from_artifact_root(self):
  sch=self.p/'原理图';sch.mkdir();rec=self.p/'record'/'evidence';rec.mkdir(parents=True)
  self.ev.rename(rec/'review.md');self.i['reviewed_circuit_supply'][0]['evidence']['path']='record/evidence/review.md'
  f=sch/'n.xml';f.write_text(xml(self.n,{'D1':('Device','D','D'),'C1':('Device','C','10u')}))
  self.assertEqual(judge(f,self.i,{'FLGX1':'#FLG1'})['status'],'FAIL')
  self.assertEqual(judge(f,self.i,{'FLGX1':'#FLG1'},self.p)['status'],'PASS')
 def test_single_component_is_not_converter_review(self):self.i['reviewed_circuit_supply'][0]['refs']=['D1'];self.assertRaises(ValueError,declarations,self.i)

 def single_part(self,basis):
  # Matrix R2 SW_12: an IC switch node has one source part; the datasheet page says so instead of padded capacitors.
  wiki=self.p/'wiki';sheet=wiki/'raw/Datasheet/08/Vendor - D.pdf';sheet.parent.mkdir(parents=True,exist_ok=True)
  sheet.write_bytes(pdf(['SW switch node driven by internal switches','p2']))
  env=mock.patch.dict(os.environ,{'HARDWARE_WIKI':str(wiki)});env.start();self.addCleanup(env.stop)
  citations._pages.clear();citations._texts.clear()
  d=self.i['reviewed_circuit_supply'][0];d['refs']=['D1'];d['basis']=basis;d['binding_sha256']=binding(self.i,['D1'])
  return self.run_case()
 @unittest.skipUnless(shutil.which('pdfinfo'),'poppler is not installed')
 def test_single_component_with_datasheet_basis_passes(self):
  self.assertEqual(self.single_part('datasheet:Datasheet/08/Vendor - D.pdf#p1')['status'],'PASS')
 @unittest.skipUnless(shutil.which('pdfinfo'),'poppler is not installed')
 def test_single_component_basis_beyond_document_fails(self):
  r=self.single_part('datasheet:Datasheet/08/Vendor - D.pdf#p9')
  self.assertEqual(r['status'],'FAIL');self.assertIn('circuit_basis_citation',json.dumps(r))
 def test_basis_must_be_a_datasheet_citation(self):
  d=self.i['reviewed_circuit_supply'][0];d['refs']=['D1'];d['basis']='手册 p20'
  self.assertRaises(ValueError,declarations,self.i)

 def test_explicit_empty_mpn_remains_empty(self):
  for c in self.i['components']:c['mpn']=''
  d=self.i['reviewed_circuit_supply'][0];d['binding_sha256']=binding(self.i,d['refs'])
  text=xml(self.n,{'D1':('Device','D','D'),'C1':('Device','C','10u')}).replace('<libsource','<fields><field name="MPN"/></fields><libsource')
  f=self.p/'n.xml';f.write_text(text)
  self.assertEqual(judge(f,self.i,{'FLGX1':'#FLG1'})['status'],'PASS')

 def test_automatic_net_name_uses_complete_native_partition(self):
  self.n['Net-(D1-A)']=self.n.pop('IN')
  self.assertEqual(self.run_case()['status'],'PASS')
 def assert_netlist_gate_catches(self):
  # Pin topology is compared once, by intent_netlist; the supply gate checks the review binding and markers.
  self.assertEqual(self.run_case()['status'],'PASS')
  self.assertEqual(compare_netlist(self.p/'n.xml',self.i)['status'],'FAIL')
 def test_extra_native_short_is_the_netlist_gates(self):
  self.n['IN'].append(('C1','2','passive'));self.assert_netlist_gate_catches()
 def test_declared_nc_must_remain_singleton_with_native_nc_marker(self):
  self.i['no_connect']=['D1.3'];self.i['reviewed_circuit_supply'][0]['binding_sha256']=binding(self.i,['D1','C1'])
  self.n['unconnected-D1']=[('D1','3','passive+no_connect')]
  self.assertEqual(self.run_case()['status'],'PASS')
  self.n['unconnected-D1'].append(('U2','1','input'))
  self.assertEqual(compare_netlist(self.p/'n.xml',self.i)['status'],'FAIL')
