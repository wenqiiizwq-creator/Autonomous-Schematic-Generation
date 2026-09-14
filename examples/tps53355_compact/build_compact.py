"""Compact synchronous-buck template using the skill's field and group APIs."""
import argparse, hashlib, json, shutil, sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
SKILL=next(p for p in [*BASE.parents, Path.home()/'.codex/skills/kicad'] if (p/'scripts/schematic_layout').is_dir())
sys.path.insert(0,str(SKILL/'scripts'))
from schematic_layout.generate import make_root, route_root, pin_net_map, Libraries, library_dirs
from schematic_layout.scene import read_scene
from schematic_layout.qa import check_scene
from schematic_layout.native import verify
from schematic_layout.sexpr import form as f, Atom as A, first, all_nodes, value, dump, parse
from build_circuit import write_project

def save(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--unrouted',action='store_true');args=ap.parse_args()
out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
intent=json.loads((BASE/'electrical_intent.json').read_text())
from verify_population import audit
population=audit(intent)
save(out/'population-default.json',population)
if population['status']!='CONFIGURATION_PASS':
    raise SystemExit('Default population rejected: '+json.dumps(population))
placements={}
def place(ref,x,y,r=0,mirror=None,style=None):
    p={'at':[x,y],'rotation':r}; placements[ref]=p
    if mirror:p['mirror']=mirror
    if style=='bank':p['fields']={'Reference':{'at':[x+3.81,y],'angle':90,'font_mm':1.016},'Value':{'at':[x+5.588,y],'angle':90,'font_mm':1.016}}
    if style=='h':p['fields']={'Reference':{'at':[x,y-3.81],'font_mm':1.016},'Value':{'at':[x,y+3.81],'font_mm':1.016}}
    return p
place('U1',114.3,101.6)['fields']={'Reference':{'at':[114.3,71.12],'font_mm':1.27},'Value':{'at':[114.3,73.66],'font_mm':1.27}}
place('J1',25.4,104.14,0,'y');place('J2',271.78,104.14)['fields']={'Reference':{'at':[271.78,90.17],'font_mm':1.016},'Value':{'at':[269.24,93.98],'font_mm':1.016}}
place('L1',175.26,104.14,90,'', 'h')
cin=['C1','C2','C3','C4','C16','C17'];cout=['C5','C6','C7','C8','C18','C19']
for ref,x in zip(cin,[38.1,46.99,55.88,64.77,73.66,82.55]):place(ref,x,111.76,style='bank')
for ref,x in zip(cout,[193.04,201.93,210.82,219.71,228.6,237.49]):place(ref,x,114.3,style='bank')
place('C9',81.28,78.74,270,style='h');place('C10',81.28,99.06,270,style='h')
place('R4',82.55,88.9,270,style='h');place('R5',50.8,93.98,270,style='h')
place('R8',146.05,93.98,90,style='h');place('C11',163.83,93.98,90,style='h')
place('R3',153.67,130.81,90,style='h');place('C12',180.34,130.81,90,style='h')
place('C13',168.91,140.97)
place('R1',215.9,139.7);place('R2',215.9,156.21)
place('R7',198.12,45.72);place('C14',198.12,66.04)
place('R9',223.52,53.34,90,style='h');place('TP2',240.03,53.34)
place('R6',254,45.72);place('TP3',269.24,53.34)
place('C15',160.02,46.99);place('R11',160.02,60.96)
place('R12',254,114.3,style='bank')
place('TP1',256.54,99.06)
place('R13',73.66,43.18);place('R14',73.66,62.23)
place('R15',116.84,46.99)
place('R16',100.33,60.96);place('R17',38.1,73.66)
place('R10',154.94,83.82,90,style='h')
place('C20',76.2,146.05,style='bank');place('C21',93.98,146.05,style='bank')
place('C22',254,143.51,style='bank');place('C23',271.78,143.51,style='bank')
partitions={
 'VIN_5V':[['J1.1',*[f'U1.{i}' for i in range(12,18)],*[f'{r}.1' for r in cin]],['R7.1'],['R16.1'],['R17.1'],['C20.1','C21.1']],
 'VDD_5V':[['R16.2'],['U1.19','C9.1']],
 'VREG_5V':[['R17.2'],['U1.18','C10.1'],['R13.1'],['R6.1']],
 'GND':[['J1.2','U1.EP',*[f'{r}.2' for r in cin]],['J2.2',*[f'{r}.2' for r in cout],'R12.2'],['C9.2'],['C10.2'],['R2.2'],['R4.2'],['R5.2'],['R11.2'],['C14.2'],['R14.2'],['C20.2','C21.2'],['C22.2','C23.2']],
 'SW':[[*[f'U1.{i}' for i in range(6,12)],'L1.1','C11.2','R3.1'],['C15.1']],
 'VOUT_0V85':[['L1.2','J2.1',*[f'{r}.1' for r in cout],'TP1.1','R12.1','R1.1','C12.2'],['C22.1','C23.1']],
 'RF':[['U1.22'],['R13.2','R14.1']],
 'MODE':[['U1.20','R5.1'],['R15.1']],
 'PGOOD':[['R10.2'],['R6.2','TP3.1'],['R15.2']],
 'EN':[['U1.2'],['R7.2','C14.1','R9.1']],
 'VFB':[['U1.1'],['R1.2','R2.1','C13.2']]
}
priorities={'RF':-35,'TRIP':-34,'MODE':-33,'PGOOD':-32,'PGOOD_IC':-31,'EN':-27,'EN_SEQ':-26,'SW':-20,'BOOT':-19,'BOOT_CAP':-18,'VIN_5V':-10,'VDD_5V':-8,'VREG_5V':-9,'VOUT_0V85':-7,'RIPPLE':3,'VFB':4,'GND':10}
policies={n['name']:{'mode':'wire','priority':priorities.get(n['name'],0),'label':n['name']=='BOOT'} for n in intent['nets']}
for name,groups in partitions.items():policies[name]['groups']=groups
for name,index,y in [('VIN_5V',0,104.14),('VIN_5V',4,137.16),('GND',0,121.92),('GND',1,124.46),('GND',10,154.94),('GND',11,153.67),('VOUT_0V85',0,104.14),('VOUT_0V85',1,134.62)]:
    policies[name]['groups'][index]={'pins':partitions[name][index],'rail_y':y}
# Only the continuous capacitor bank rails are fixed; local configuration and
# feedback are allowed to route orthogonally around measured field obstacles.
layout={'schema_version':1,'paper':'A4','grid_mm':1.27,'placements':placements,'nets':policies,'max_route_states':300000,
 'annotations':[
 {'text':'RF options: revalidate before fitting\nR13: 650 kHz / R14: 300 kHz','at':[53.34,29.21],'font_mm':1.016},
 {'text':'MODE: R5 FIT / R15 DNP\nFCCM: fit R15, remove R5','at':[104.14,31.75],'font_mm':1.016},
 {'text':'TPS53355-Test   |   5 V to 0.85 V / 15 A','at':[15.24,17.78],'font_mm':2.032},
 {'text':'REV C  /  ENGINEERING OPTIONS  /  500 kHz nominal in CCM  /  AUTO-SKIP','at':[15.24,24.13],'font_mm':1.27},
 {'text':'DNP: snubber tuning','at':[143.51,32.004],'font_mm':1.016},
 {'text':'EN: auto-start by default\nSequencing: R7 DNP, fit R9','at':[187.96,30.48],'font_mm':1.016},
 {'text':'Open-drain PG','at':[251.46,32.004],'font_mm':1.016},
 {'text':'Input: 4.75-5.25 V\nR16/R17: 0R default\nExternal 5 V bias','at':[15.24,36.83],'font_mm':1.016},
 {'text':'RF: R13 / R14 DNP\nDefault = 500 kHz\nFit only one to retune','at':[15.24,54.61],'font_mm':1.016},
 {'text':'CIN: 6 x 22uF / 16V; Ceff >= 66uF','at':[30.48,130.175],'font_mm':1.016},
 {'text':'COUT: 6 x 100uF / 6.3V; Ceff >= 300uF\nC20/C21: local VIN bypass; C22/C23: load bypass','at':[22.86,165.1],'font_mm':1.016},
 {'text':'D-CAP ripple injection\nKeep R3/C12/C13 and FB local on PCB','at':[119.38,155.575],'font_mm':1.016},
 {'text':'MPNs, tolerance calculations and assembly variants: see BOM + design report.\n15 A is a comparison target. PCB, thermal and load-transient validation pending.','at':[15.24,179.07],'font_mm':1.016}
 ]}
save(out/'electrical_intent.json',intent);save(out/'layout_plan.json',layout)
shutil.copy(BASE/'circuit.json',out/'circuit.json');shutil.copy(BASE/'compiled.json',out/'compiled.json')
result={'status':'FAIL','datasheet_review':'PENDING','native_render_review':'PENDING'}
try:
    root,manifest,uid,reserved=make_root(intent,layout,'TPS53355-Test',[str(BASE/'libraries')])
    if args.unrouted:
        write_project(out,'TPS53355-Test',root,manifest['library_sources']); print('unrouted');sys.exit(0)
    manifest['routing']=route_root(root,intent,layout,uid,reserved)
    powerlibs=Libraries(library_dirs());flag=powerlibs.load('power:PWR_FLAG');first(root,'lib_symbols').append(flag)
    manifest['library_sources'].update(powerlibs.sources)
    fp={}
    for i,(net,x,y) in enumerate([('GND',25.4,128.27),('BOOT',22.86,147.32),('VIN_5V',43.18,147.32),('VDD_5V',63.5,147.32)],1):
        ref=f'#FLG0{i:02d}';fp[ref+'.1']=net
        s=f('symbol',f('lib_id','power:PWR_FLAG'),f('at',x,y,0),f('unit',1),f('in_bom',A('no')),f('on_board',A('no')),f('dnp',A('no')),f('uuid',uid(ref)),
              f('property','Reference',ref,f('at',x,y,0),f('effects',f('font',f('size',1.27,1.27)),f('hide',A('yes')))),
              f('property','Value','PWR_FLAG',f('at',x,y-3.81,0),f('effects',f('font',f('size',1.27,1.27)),f('hide',A('yes')))),
              f('instances',f('project','TPS53355-Test',f('path','/'+str(value(root,'uuid')),f('reference',ref),f('unit',1)))))
        root.append(s)
        root.append(f('wire',f('pts',f('xy',x,y),f('xy',x,y+5.08)),f('stroke',f('width',0),f('type',A('default'))),f('uuid',uid(ref+':wire'))))
        root.append(f('label',net,f('at',x,y+5.08,0),f('effects',f('font',f('size',1.27,1.27)),f('justify',A('left'),A('bottom'))),f('uuid',uid(ref+':label'))))
    root=parse(dump(root))
    geometry=check_scene(read_scene(root),grid=1.27,reserved=reserved,pin_nets={**pin_net_map(intent),**fp})
    manifest['geometry']=geometry;result['geometry']=geometry
    path=write_project(out,'TPS53355-Test',root,manifest['library_sources']);save(out/'generation.json',manifest)
    # Keep the custom pin-audited symbol with the delivered project.
    (out/'libraries').mkdir(exist_ok=True)
    shutil.copy2(BASE/'libraries/TPS53355_Test.kicad_sym',out/'libraries/TPS53355_Test.kicad_sym')
    table=out/'sym-lib-table'
    table.write_text(table.read_text().replace(str(BASE/'libraries/TPS53355_Test.kicad_sym'),'${KIPRJMOD}/libraries/TPS53355_Test.kicad_sym'))
    result['native']=verify(path,intent,layout,out/'native')
    result['status']='AUTOMATED_PASS' if geometry['status']==result['native']['status']=='PASS' else 'FAIL'
except Exception as e:
    result['error']=str(e)
save(out/'verification.json',result)
print(json.dumps({'status':result['status'],'error':result.get('error'),'geometry':result.get('geometry',{}).get('status'),'native':result.get('native',{}).get('status'),'report':str(out/'verification.json')}))
