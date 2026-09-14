"""Bounded reference contract; consumes Circuit IR or native KiCad XML.

PASS means only these enumerated topology/value rules pass. It says nothing
about load, transient, EMC, clock margin, timing, footprint or production status.
"""
import argparse,json,math,re,xml.etree.ElementTree as ET
from pathlib import Path
DOC='Microchip DS00002199D (2020)'
def number(value):
 m=re.match(r'\s*([0-9]+(?:\.[0-9]*)?)\s*([pnuµmkM]?)(?:[FHRΩ]|ohm)?',value)
 if not m:return None
 return float(m[1])*{'':1,'p':1e-12,'n':1e-9,'u':1e-6,'µ':1e-6,'m':1e-3,'k':1e3,'M':1e6}[m[2]]
def native(path):
 r=ET.parse(path).getroot()
 return {'components':[{'ref':c.get('ref'),'value':c.findtext('value',''),'lib_id':c.find('libsource').get('lib')+':'+c.find('libsource').get('part'),'dnp':c.find("property[@name='dnp']") is not None} for c in r.findall('components/comp')],
 'nets':[{'name':n.get('name'),'pins':[p.get('ref')+'.'+p.get('pin') for p in n.findall('node')]} for n in r.findall('nets/net')]}
def audit(d,ic='U2601',jack='J2601'):
 nets={p:n['name'] for n in d['nets'] for p in n['pins']};cs={c['ref']:c for c in d['components']};checks=[]
 def pin(n):return nets.get(ic+'.'+str(n))
 ground=pin(22);supply=pin(14)
 def branch(kind,a,b,v=None,allowed=None):
  if a is None or b is None or a==b:return []
  return [c['ref'] for c in cs.values() if (allowed is None or c['ref'] in allowed) and not c.get('dnp') and c['lib_id']==kind and
          {nets.get(c['ref']+'.1'),nets.get(c['ref']+'.2')}=={a,b} and
          (v is None or number(c['value']) is not None and math.isclose(number(c['value']),v,rel_tol=1e-8))]
 def record(id,passed,basis,evidence=None):checks.append({'id':id,'status':'PASS' if passed else 'FAIL','basis':f'{DOC}, {basis}','evidence':evidence or []})
 record('ground-pad',ground is not None and ground==pin(25),'pp5,23')
 local_caps=json.loads((Path(__file__).parent/'reference_roles.json').read_text())['instances'][ic]['capacitors']
 for label,pnum,cap in [('core-bulk',1,2.2e-6),('core-hf',1,1e-7),('analog-bulk',2,22e-6),('analog-hf',2,1e-7),('io-bulk',14,22e-6),('io-hf',14,1e-7)]:
  evidence=branch('Device:C',pin(pnum),ground,cap,local_caps[label]);record(label,bool(evidence),'p24 table3-6',evidence)
 b=branch('Device:FerriteBead',supply,pin(2));record('analog-ferrite',bool(b),'pp23-24',b)
 for label,pnum,rval in [('mdio-pullup',10,1000),('irq-pullup',18,1000)]:
  b=branch('Device:R',pin(pnum),supply,rval);record(label,bool(b),'pp6-7',b)
 b=branch('Device:R',pin(9),ground,6490);record('rext',bool(b),'p6',b)
 for label,pnum in [('address-low-15',15),('address-low-16',16)]:
  b=branch('Device:R',pin(pnum),ground,1000);record(label,bool(b),'p9 external pull-down for address 0',b)
 b=branch('Device:R',pin(17),ground);record('rxer-low',bool(b),'p7; external pull-down selected for host reset robustness',b)
 tx=nets.get(jack+'.2');rx=nets.get(jack+'.5')
 record('separate-centre-taps',None not in (tx,rx,supply,ground) and len({tx,rx,supply,ground})==4,'p44')
 for label,n in [('tx-ct-cap',tx),('rx-ct-cap',rx)]:
  b=branch('Device:C',n,ground,1e-7);record(label,bool(b),'p44',b)
 return {'status':'REFERENCE_CHECKS_PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','scope':'17 explicit topology/value checks; not complete IC qualification','ic':ic,'checks':checks,'unverified':['MLCC effective capacitance and ratings','ferrite MPN and impedance versus bias','crystal CL/ESR/drive and frequency across temperature','reset/strap timing with host','full board power/EMC/isolation','PCB layout and manufacturing readiness']}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('input',type=Path);a.add_argument('--ic',default='U2601');a.add_argument('--jack',default='J2601');a.add_argument('--out',type=Path);args=a.parse_args()
 d=native(args.input) if args.input.suffix=='.xml' else json.loads(args.input.read_text());r=audit(d,args.ic,args.jack);s=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
 if args.out:args.out.write_text(s)
 else:print(s)
 raise SystemExit(0 if r['status']=='REFERENCE_CHECKS_PASS' else 1)
