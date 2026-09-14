"""Two related complete converters share a functional page; no count balancing."""
import argparse,copy
from pathlib import Path
from build_reference import buck,run

def power_pair():
 i,l=buck();d=copy.deepcopy(i);plan=copy.deepcopy(l)
 d['design_id']='ACU-Power-Pair-RevC';d['title']='ACU 12V to 5V to 3V3';plan['paper']='A3'
 def ref(r):return r.replace('201','202')
 def net(n):return {'ACU_12V':'ACU_5V','ACU_5V':'ACU_3V3'}.get(n,n.replace('ACU_5V_','ACU_3V3_'))
 def group(g):
  g={'pins':g} if isinstance(g,list) else copy.deepcopy(g)
  g['pins']=[ref(p) for p in g['pins']]
  if 'rail_y' in g:g['rail_y']+=91.44
  return g
 d['components'] += [dict(copy.deepcopy(c),ref=ref(c['ref'])) for c in i['components']]
 next(c for c in d['components'] if c['ref']=='R2020')['value']='312k / 0.1%'
 ns={n['name']:n['pins'] for n in d['nets']};policies={}
 for n in i['nets']:
  p=copy.deepcopy(l['nets'][n['name']]);policies[n['name']]={'mode':'wire','groups':p.pop('groups',[n['pins']]),'priority':p.get('priority',0)}
 for n in i['nets']:
  name=net(n['name']);ps=[ref(p) for p in n['pins']];ns.setdefault(name,[]).extend(ps)
  policy=l['nets'][n['name']]
  gs=[group(g) for g in policy.get('groups',[n['pins']])]
  policies.setdefault(name,{'mode':'wire','groups':[],'priority':policy.get('priority',0)})['groups']+=gs
 for name,p in policies.items():
  if len(p['groups'])==1 and len(p['groups'][0] if isinstance(p['groups'][0],list) else p['groups'][0]['pins'])==1:p['mode']='labels'
  p['label']=True
 d['nets']=[{'name':n,'pins':ps} for n,ps in ns.items()]
 for r,placement in l['placements'].items():
  p=copy.deepcopy(placement);p['at'][1]+=91.44
  for spec in p.get('fields',{}).values():spec['at'][1]+=91.44
  plan['placements'][ref(r)]=p
 plan['nets']=policies
 plan['annotations']=[
 {'text':'ACU / Two-stage power / 12 V to 5 V to 3.3 V','at':[15.24,17.78],'font_mm':2.032},
 {'text':'Rev C validation sample  |  Two complete related circuits on one functional page','at':[15.24,25.4],'font_mm':1.27},
 {'text':'5 V rail\nVOUT = 0.8 x (1 + 525k/100k)\nNominal 5.000 V\nPG pulled up to downstream 3.3 V','at':[254,76.2],'font_mm':1.27},
 {'text':'3.3 V rail\nVOUT = 0.8 x (1 + 312k/100k)\nNominal 3.296 V\nInput supplied by the 5 V stage above','at':[254,167.64],'font_mm':1.27},
 {'text':'Both stages: FSW=0 (2.5MHz), DEF=0; 10nF soft-start (~5ms typical).\nEach input: 10uF + 100nF local AVIN bypass. Each output: 2 x 22uF nominal.\nReference: TI SLVSAG7F Fig9-1 and sections9.2.2.2-9.2.2.8.\nMLCC MPN/DC-bias, actual loads, inductor hot loss and transient/thermal validation remain open.\nFull board integration and production release are not implied by this drawing sample.','at':[15.24,237.49],'font_mm':1.016}]
 return d,plan
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args();run(*power_pair(),args.out/'ACU-Power')
