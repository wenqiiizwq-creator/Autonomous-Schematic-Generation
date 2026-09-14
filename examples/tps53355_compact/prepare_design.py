"""Create explicit, datasheet-derived inputs for the TPS53355 drawing test."""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SKILL = next(p for p in [*BASE.parents, Path.home()/'.codex/skills/kicad'] if (p/'scripts/schematic_layout').is_dir())
sys.path.insert(0, str(SKILL / 'scripts'))
from schematic_layout.sexpr import form as f, Atom as A, dump
from schematic_layout.circuit_ir import compile_circuit

DS = 'https://www.ti.com/lit/ds/symlink/tps53355.pdf'
LIB = BASE / 'libraries'
LIB.mkdir(exist_ok=True)
def save(name, value):
    (BASE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

# A project symbol, not a substituted device. Every lead is separately visible.
# EP is our explicit name for the unnumbered GND PowerPAD in TI Table 5-1.
pins = []
def pin(num, name, kind, x, y, angle):
    pins.append(f('pin', A(kind), A('line'), f('at',x,y,angle), f('length',5.08),
                  f('name',name,f('effects',f('font',f('size',1.27,1.27)))),
                  f('number',str(num),f('effects',f('font',f('size',1.0,1.0))))))
for i,n in enumerate(range(12,18)):
    pin(n,'VIN','power_in',-17.78,round(-2.54-i*2.54,2),0)
for i,n in enumerate(range(6,12)):
    pin(n,'LL','bidirectional',17.78,round(-2.54-i*2.54,2),180)
for n,name,typ,y in [(19,'VDD','power_in',22.86),(22,'RF','input',17.78),
                      (21,'TRIP','input',12.7),(20,'MODE','input',7.62),
                      (18,'VREG','power_out',2.54),('EP','GND','power_in',-20.32)]:
    pin(n,name,typ,-17.78,y,0)
for n,name,typ,y in [(1,'VFB','input',22.86),(2,'EN','input',17.78),
                      (3,'PGOOD','open_collector',12.7),(4,'VBST','power_in',7.62),
                      (5,'NC','no_connect',-20.32)]:
    pin(n,name,typ,17.78,y,180)
sym=f('symbol','TPS53355DQP',f('pin_names',f('offset',0.8)),f('in_bom',A('yes')),f('on_board',A('yes')),
      f('property','Reference','U',f('at',0,29.21,0),f('effects',f('font',f('size',1.27,1.27)))),
      f('property','Value','TPS53355DQP',f('at',0,26.67,0),f('effects',f('font',f('size',1.27,1.27)))),
      f('property','Datasheet',DS,f('at',0,0,0),f('effects',f('font',f('size',1.27,1.27)),f('hide',A('yes')))),
      f('symbol','TPS53355DQP_0_1',f('rectangle',f('start',-12.7,25.4),f('end',12.7,-25.4),f('stroke',f('width',0.254),f('type',A('default'))),f('fill',f('type',A('background'))))),
      f('symbol','TPS53355DQP_1_1',*pins))
(LIB/'TPS53355_Test.kicad_sym').write_text(dump(f('kicad_symbol_lib',f('version',20241209),f('generator','kicad_symbol_editor'),sym))+'\n')
save('symbol-pin-audit.json', {'source':DS,'section':'Table 5-1, page 4','ep_convention':'EP = unnumbered GND PowerPAD, not physical lead 23',
    'pin_map':{'1':'VFB','2':'EN','3':'PGOOD','4':'VBST','5':'NC',**{str(i):'LL' for i in range(6,12)},**{str(i):'VIN' for i in range(12,18)},'18':'VREG','19':'VDD','20':'MODE','21':'TRIP','22':'RF','EP':'GND'},'electrical_types':{'VIN/VDD/GND/VBST':'power_in','VREG':'power_out','LL':'bidirectional','PGOOD':'open_collector','NC':'no_connect','others':'input'},
    'all_leads_visible':True,'footprint_status':'Not assigned: schematic-only test, DQP package must not be replaced by generic DFN-22'})

comps=[]; refs={}; nets={}; nc=[]
def part(ref,lib,value,role='',mpn='',footprint='',ratings=None,source=''):
    refs[ref]=ref
    c={'id':ref,'lib_id':lib,'value':value,'footprint':footprint,'role':role or 'control'}
    if mpn: c['mpn']=mpn
    if ratings:c['ratings']=ratings
    if source:c['datasheet']=source
    comps.append(c)
def net(name,*pins): nets.setdefault(name,[]).extend(pins)
RFP='Resistor_SMD:R_0603_1608Metric'
CFP='Capacitor_SMD:C_0603_1608Metric'
part('U1','TPS53355_Test:TPS53355DQP','TPS53355DQP','regulator','TPS53355DQPR',ratings={'Package':'DQP 22-lead + GND PowerPAD'},source=DS)
part('L1','Device:L','0.47uH','inductor','XGL7030-471MEC',ratings={'DCR_max_25C':'2.3mOhm','Isat20_25C':'21.5A','Isat30_25C':'32A','Irms40K_reference':'29.4A'},source='https://www.coilcraft.com/getmedia/63e6e233-cff1-40b9-9e5d-f0f490094f44/xgl7030.pdf')
part('J1','Connector_Generic:Conn_01x02','5V INPUT','input')
part('J2','Connector_Generic:Conn_01x02','0.85V / 15A','output')
for i in range(1,5):
    part(f'C{i}','Device:C','22uF / 16V','input_cap',footprint='Capacitor_SMD:C_1210_3225Metric',ratings={'Dielectric':'X7R','Requirement':'6 x 22uF: Ceff >= 66uF at 5V; bank ripple >= 6Arms at application temperature'})
for i in range(5,9):
    part(f'C{i}','Device:C','100uF / 6.3V','output_cap','GRM32ER60J107ME20L','Capacitor_SMD:C_1210_3225Metric',ratings={'Dielectric':'X5R','Tolerance':'+/-20%','Requirement':'6 x 100uF: combined effective COUT >= 300uF including bias, temperature and aging'},source='https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/dynamic-model/component-list-d-mlcc-2504.ashx')
for ref,val,role in [('C9','4.7uF / 10V','input_cap'),('C10','1uF / 10V','input_cap'),('C11','100nF / 16V','bootstrap'),('C12','100nF / 16V','compensation'),('C13','1nF / 50V','compensation')]:
    part(ref,'Device:C',val,role,footprint=CFP,ratings={'Dielectric':'C0G' if ref=='C13' else 'X7R'})
for ref,val,role in [('R1','3.97k 0.1%','feedback'),('R2','10k 0.1%','feedback'),('R3','1k 1%','compensation'),('R4','100k 1%','control'),('R5','100k 1%','control'),('R6','10k 1%','control'),('R7','10k 1%','control'),('R8','2R 1%','bootstrap')]:
    part(ref,'Device:R',val,role,footprint=RFP)
# Preserve the original references; additional bank members have new references.
for ref in ('C16','C17'):
    part(ref,'Device:C','22uF / 16V','input_cap',footprint='Capacitor_SMD:C_1210_3225Metric',ratings={'Dielectric':'X7R','Requirement':'Ceff bank >= 66uF; ripple >= 6Arms'})
for ref in ('C18','C19'):
    part(ref,'Device:C','100uF / 6.3V','output_cap','GRM32ER60J107ME20L','Capacitor_SMD:C_1210_3225Metric',ratings={'Dielectric':'X5R','Requirement':'Ceff bank >= 300uF'},source='https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/dynamic-model/component-list-d-mlcc-2504.ashx')
part('C14','Device:C','100nF/16V','control',footprint=CFP,ratings={'Voltage':'16V','Dielectric':'X7R'})
part('C15','Device:C','1nF/50V DNP','snubber',footprint=CFP,ratings={'Voltage':'50V','Dielectric':'C0G'})
part('R9','Device:R','0R DNP','control',footprint=RFP)
part('R11','Device:R','100R DNP','snubber',footprint='Resistor_SMD:R_1206_3216Metric',ratings={'Power':'0.25W; tuning only'})
part('R12','Device:R','100R DNP','output',footprint='Resistor_SMD:R_1206_3216Metric')
for ref,val in [('TP1','VOUT'),('TP2','EN_SEQ'),('TP3','PGOOD')]:
    part(ref,'Connector:TestPoint',val,'testpoint',footprint='TestPoint:TestPoint_Pad_D1.5mm')
# Retain meaningful engineering options, with explicit default population.
for ref,val,role in [('R10','0R','pg_isolation'),('R13','866k DNP','rf_option'),
                      ('R14','187k DNP','rf_option'),('R15','100k DNP','mode_option'),
                      ('R16','0R','vdd_filter_link'),('R17','0R','external_vreg_link')]:
    part(ref,'Device:R',val,role,footprint=RFP,ratings={'Tolerance':'1%','Purpose':role})
for ref,val,role,diel in [('C20','100nF/16V','vin_hf_bypass','X7R'),('C21','1nF/50V','vin_hf_bypass','C0G'),
                         ('C22','10uF/6.3V','load_local_bypass','X5R'),('C23','100nF/16V','load_local_bypass','X7R')]:
    part(ref,'Device:C',val,role,footprint=CFP,ratings={'Dielectric':diel,'Purpose':role})
for c in comps:
    if c['id'] in ('C15','R9','R11','R12','R13','R14','R15'): c['dnp']=True
    # Keep the canvas concise; full ratings/MPN remain in independent metadata.
    if c['id'].startswith('R') and '1%' in c['value']:
        c.setdefault('ratings',{})['Tolerance']='0.1%' if '0.1%' in c['value'] else '1%'
    c['value']=c['value'].replace(' / ','/').replace(' 1%','').replace(' 0.1%',' 0.1%')
cin=['C1','C2','C3','C4','C16','C17']; cout=['C5','C6','C7','C8','C18','C19']
net('VIN_5V','J1.1',*[f'U1.{i}' for i in range(12,18)],*[f'{r}.1' for r in cin],'R7.1','R16.1','R17.1','C20.1','C21.1')
net('GND','J1.2','J2.2','U1.EP',*[f'{r}.2' for r in cin+cout], 'C9.2','C10.2','C14.2','R2.2','R4.2','R5.2','R11.2','R12.2','R14.2','C20.2','C21.2','C22.2','C23.2')
net('SW',*[f'U1.{i}' for i in range(6,12)],'L1.1','C11.2','R3.1','C15.1')
net('VOUT_0V85','L1.2','J2.1',*[f'{r}.1' for r in cout],'R1.1','C12.2','R12.1','TP1.1','C22.1','C23.1')
net('VFB','U1.1','R1.2','R2.1','C13.2')
net('RIPPLE','R3.2','C12.1','C13.1')
net('BOOT','U1.4','R8.1')
net('BOOT_CAP','R8.2','C11.1')
net('TRIP','U1.21','R4.1')
net('MODE','U1.20','R5.1','R15.1')
net('PGOOD_IC','U1.3','R10.1')
net('PGOOD','R10.2','R6.2','TP3.1','R15.2')
net('EN','U1.2','R7.2','C14.1','R9.1')
net('EN_SEQ','R9.2','TP2.1')
net('SNUBBER','C15.2','R11.1')
net('RF','U1.22','R13.2','R14.1')
net('VDD_5V','R16.2','U1.19','C9.1')
net('VREG_5V','R17.2','U1.18','C10.1','R13.1','R6.1')
nc=['U1.5']
doc={'schema_version':2,'design_id':'TPS53355-Test','title':'TPS53355 5V to 0.85V / 15A','revision':'C',
     'references':refs,'root':{'components':comps,'nets':[{'name':n,'pins':p} for n,p in nets.items()],'no_connect':nc},
     'evidence':[{'source':DS,'status':'CALCULATED_DRAFT','load_current':'15A comparison assumption from engineer image; not a confirmed production load',
     'bias':'R16=0 to VDD_5V, R17=0 to VREG_5V; preserve external regulated 5V bias, add isolation/tuning footprints; no unreviewed 10ohm filter' ,
     'frequency':'R13/R14 DNP: RF electrically open at default population, 500kHz nominal CCM; R13=866k to VREG for 650kHz option, R14=187k to GND for 300kHz option; never fit both' ,
     'mode':'R5=100k fitted to GND, R15=100k to PG DNP; auto-skip/1.4ms. For FCCM swap population; never fit both' ,
     'variant':'Default R7 installed, R9 DNP: automatic enable. External sequencing: R7 DNP, R9 installed; never combine without interface review.'}]}
save('circuit.json',doc)
intent,compiled=compile_circuit(doc,[str(LIB)])
# Published evidence uses portable library locations, never a developer's
# private checkout path. The runtime writer resolves its own actual sources.
for source in compiled['library_sources'].values():
    source_path = Path(source['path'])
    if source_path.is_relative_to(BASE):
        source['path'] = source_path.relative_to(BASE).as_posix()
        source['path_base'] = 'example_directory'
    else:
        source['path'] = source_path.name
        source['path_base'] = 'kicad_symbol_directory'
save('electrical_intent.json',intent);save('compiled.json',compiled)
print(f'Prepared {len(comps)} components, {len(nets)} nets, {sum(map(len,nets.values()))} connected physical pins')
