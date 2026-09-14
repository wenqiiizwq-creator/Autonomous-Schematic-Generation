import copy,json,sys,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'examples/controller_reference';sys.path.insert(0,str(BASE))
from verify_peripherals import audit
class ReferencePeripheralTests(unittest.TestCase):
 def fixture(self):return json.loads((BASE/'phy_intent.json').read_text())
 def test_reference_candidate_has_all_contract_branches(self):self.assertEqual(audit(self.fixture())['status'],'REFERENCE_CHECKS_PASS')
 def test_removed_dnp_wrong_value_and_wrong_ground_fail(self):
  for mutation in ['removed','dnp','value','ground']:
   d=self.fixture();c=next(c for c in d['components'] if c['ref']=='C26012')
   if mutation=='removed':d['components'].remove(c)
   if mutation=='dnp':c['dnp']=True
   if mutation=='value':c['value']='1uF'
   if mutation=='ground':
    n=next(n for n in d['nets'] if 'C26012.2' in n['pins']);n['pins'].remove('C26012.2');d['nets'].append({'name':'WRONG_RETURN','pins':['C26012.2']})
   self.assertEqual(next(c['status'] for c in audit(d)['checks'] if c['id']=='core-bulk'),'FAIL',mutation)
 def test_bypassed_ferrite_fails_even_with_correct_capacitors(self):
  d=self.fixture();a=next(n for n in d['nets'] if n['name']=='TCU_PHY_AVDD');v=next(n for n in d['nets'] if n['name']=='TCU_3V3');v['pins']+=a['pins'];d['nets'].remove(a)
  self.assertEqual(next(c['status'] for c in audit(d)['checks'] if c['id']=='analog-ferrite'),'FAIL')

class ScopeTests(unittest.TestCase):
 def test_remote_supply_bulk_cannot_replace_local_pin_bypass(self):
  d=json.loads((BASE/'phy_intent.json').read_text())
  cap=next(c for c in d['components'] if c['ref']=='C26011');cap['value']='4.7uF'
  d['components'].append({'ref':'C9999','lib_id':'Device:C','value':'22uF'})
  next(n for n in d['nets'] if n['name']=='TCU_3V3')['pins'].append('C9999.1')
  next(n for n in d['nets'] if n['name']=='TCU_GND')['pins'].append('C9999.2')
  self.assertEqual(next(c['status'] for c in audit(d)['checks'] if c['id']=='io-bulk'),'FAIL')

if __name__=='__main__':unittest.main()
