"""Reference-driven controller repair samples using the installed skill API."""
import argparse,hashlib,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from schematic_layout.generate import generate
from schematic_layout.native import verify
from build_circuit import write_project

def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def run(intent,layout,out):
 out.mkdir(parents=True,exist_ok=True)
 baseline=out/'generation-baseline.json'
 if baseline.exists():
  for name,expected in json.loads(baseline.read_text()).items():
   path=out/name
   if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
    raise ValueError(f'Protected generated file changed: {path}; choose a new output directory')
 save(out/'electrical_intent.json',intent);save(out/'layout_plan.json',layout)
 try:
  root,m=generate(intent,layout,intent['design_id'])
  sch=write_project(out,intent['design_id'],root,m['library_sources'])
  save(out/'generation.json',m)
  result={'geometry':m['geometry'],'native':verify(sch,intent,layout,out/'native')}
  result['status']='REVIEW_ONLY' if result['geometry']['status']==result['native']['netlist']['status']=='PASS' else 'FAIL'
  result['runtime']={'skill_root':str(ROOT.resolve()),'files_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'scripts/schematic_layout/generate.py',ROOT/'scripts/schematic_layout/scene.py',ROOT/'scripts/schematic_layout/qa.py',ROOT/'scripts/schematic_layout/native.py',*BASE.glob('*.py'),*BASE.glob('*.json')]}}
  save(out/'verification.json',result)
  save(baseline,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.kicad_*')})
  (out/'failure.json').unlink(missing_ok=True)
  print(out.name,result['geometry']['status'],result['native']['netlist']['status'],result['native']['erc']['status'])
  if result['status']=='FAIL':raise SystemExit(1)
 except Exception as e:
  save(out/'failure.json',{'error':str(e)});print(out.name,str(e));raise SystemExit(1)

def buck():
 intent=json.loads((BASE/'buck_intent.json').read_text())
 p={}
 def place(ref,x,y,r=0,bank=False):
  p[ref]={'at':[x,y],'rotation':r}
  if bank:p[ref]['fields']={'Reference':{'at':[x+3.81,y],'angle':90,'font_mm':1.016},'Value':{'at':[x+5.588,y],'angle':90,'font_mm':1.016}}
 place('U201',101.6,76.2)
 p['U201']['fields']={'Reference':{'at':[119.38,55.88],'font_mm':1.016},'Value':{'at':[119.38,58.42],'font_mm':1.016}}
 place('L201',158.75,71.12,90)
 p['L201']['fields']={'Reference':{'at':[158.75,65.405],'font_mm':1.016},'Value':{'at':[158.75,67.945],'font_mm':1.016}}
 for ref,x in [('C2010',50.8),('C2011',63.5)]:place(ref,x,58.42,bank=True)
 for ref,x in [('C2012',208.28),('C2013',220.98)]:place(ref,x,86.36,bank=True)
 place('C2014',73.66,87.63,bank=True)
 place('R2010',187.96,90.17);place('R2011',187.96,110.49)
 place('R2012',133.35,78.74,270)
 p['R2012']['fields']={'Reference':{'at':[133.35,82.55],'font_mm':1.016},'Value':{'at':[133.35,85.09],'font_mm':1.016}}
 nets={n['name']:{'mode':'wire'} for n in intent['nets']}
 nets['ACU_12V'].update(label=True,priority=-5)
 nets['ACU_3V3']={'mode':'labels'}
 nets['ACU_5V'].update(label=True,priority=-3)
 nets['ACU_5V_SW']['priority']=-10
 nets['ACU_5V_PG'].update(priority=-7)
 nets['ACU_GND']['groups']=[{'pins':['C2010.2','C2011.2'],'rail_y':66.04},['C2014.2'],['U201.6','U201.7','U201.8','U201.15','U201.16','U201.17'],['R2011.2'],{'pins':['C2012.2','C2013.2'],'rail_y':96.52}]
 layout={'schema_version':1,'paper':'A4','grid_mm':1.27,'placements':p,'nets':nets,'max_route_states':300000,'annotations':[
 {'text':'ACU / 12 V to 5 V / TPS62130','at':[15.24,17.78],'font_mm':2.032},
 {'text':'Rev C validation sample  |  Native stock symbol / complete physical pin coverage','at':[15.24,25.4],'font_mm':1.27},
 {'text':'VIN bypass: 10uF + 100nF\nPlace 100nF at AVIN pin 10 on PCB','at':[25.4,111.76],'font_mm':1.016},
 {'text':'FSW=0: 2.5 MHz; DEF=0\nSS 10nF: ~5ms typical','at':[25.4,127],'font_mm':1.016},
 {'text':'VOUT = 0.8 x (1 + 525k/100k) = 5.000 V\nVOS senses output; FB is the divider midpoint','at':[151.13,133.35],'font_mm':1.016},
 {'text':'Reference: TI SLVSAG7F, Fig 9-1 and sections 9.2.2.2-9.2.2.8.\nInput/output MLCC MPN and DC-bias curves, actual load/thermal/transient limits remain open.\nPG pulls up to ACU_3V3 supplied by the next converter. This is a review sample, not production release.','at':[15.24,161.29],'font_mm':1.016}]}
 return intent,layout
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();run(*buck(),a.out/'ACU-Power')
