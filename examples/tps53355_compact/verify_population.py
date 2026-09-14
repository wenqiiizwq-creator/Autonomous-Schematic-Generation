"""TPS53355 recipe population audit; not a universal analog circuit simulator.

Checks actual pin endpoints, removes DNP parts, collapses FIT 0-ohm links and
separates a legal frequency code from a qualified converter configuration.
"""
import argparse
import copy
import json
import re
from pathlib import Path


def resistance(value):
    match=re.fullmatch(r'\s*([0-9]+(?:\.[0-9]+)?)([RrKkMm]?)(?:\s.*)?',value)
    if not match: raise ValueError('Unsupported resistance value: '+value)
    return float(match[1])*{'':1,'r':1,'k':1e3,'m':1e6}[match[2].lower()]


def active_groups(intent):
    comps={c['ref']:c for c in intent['components']}
    active=lambda p:not comps[p.rsplit('.',1)[0]].get('dnp',False)
    parent={}
    def find(p):
        parent.setdefault(p,p)
        if parent[p]!=p:parent[p]=find(parent[p])
        return parent[p]
    def join(p,q):parent[find(p)]=find(q)
    for net in intent['nets']:
        pins=[p for p in net['pins'] if active(p)]
        for p in pins:join(p,pins[0])
    for p in intent.get('no_connect',[]):
        if active(p):find(p)
    for ref,c in comps.items():
        if c.get('dnp') or c['lib_id']!='Device:R':continue
        if resistance(c['value'])==0:
            join(ref+'.1',ref+'.2')
    groups={}
    for p in list(parent):groups.setdefault(find(p),set()).add(p)
    return list(groups.values())


def audit(intent, overrides=None):
    doc=copy.deepcopy(intent);comps={c['ref']:c for c in doc['components']}
    required=['U1','R5','R6','R7','R9','R10','R13','R14','R15','R16','R17','C15','R11']
    missing=set(required)-set(comps)
    if missing: return {'status':'FAIL','errors':['Missing required references: '+str(sorted(missing))]}
    for ref,state in (overrides or {}).items():
        if ref not in comps or type(state) is not bool:
            return {'status':'FAIL','errors':['Unknown reference or non-boolean population override: '+ref]}
        comps[ref]['dnp']=not state
    fit=lambda r:not comps[r].get('dnp',False)
    errors=[]; review=[]
    if fit('R13') and fit('R14'):errors.append('RF upper and lower options must not both be fitted')
    if fit('R5')==fit('R15'):errors.append('Fit exactly one MODE resistor: R5 or R15')
    if fit('R7')==fit('R9'):errors.append('This recipe supports exactly one EN path: R7 or R9')
    if fit('C15')!=fit('R11'):errors.append('Fit snubber C15 and R11 together')
    for r in ['R10','R16','R17']:
        if not fit(r) or resistance(comps[r]['value'])!=0:
            errors.append(r+' must remain a fitted 0-ohm link in supported external-5V profiles')
    # Validate even the unpopulated option pads, using the declaration graph plus
    # only the intended fitted zero links. Wrong pins cannot pass from DNP alone.
    declared={p:n['name'] for n in doc['nets'] for p in n['pins']}
    # Explicit zero-link pairs provide intended aliases without turning ordinary
    # 100k resistors, capacitors, or the IC into conductive net equivalences.
    parent={n['name']:n['name'] for n in doc['nets']}
    def find(n):
        while parent[n]!=n:n=parent[n]
        return n
    for r in ['R10','R16','R17']:
        if fit(r) and resistance(comps[r]['value'])==0:
            parent[find(declared[r+'.1'])]=find(declared[r+'.2'])
    def endpoints(r):return {find(declared[r+'.1']),find(declared[r+'.2'])}
    def target(a,b):return {find(declared[a]),find(declared[b])}
    for r,a,b in [('R13','U1.22','U1.18'),('R14','U1.22','U1.EP'),('R5','U1.20','U1.EP'),('R15','U1.20','U1.3'),('R6','U1.3','U1.18')]:
        if endpoints(r)!=target(a,b):errors.append(r+' endpoints do not match the datasheet role')
    for r,ohms in [('R13',866000),('R14',187000),('R5',100000),('R15',100000)]:
        if resistance(comps[r]['value'])!=ohms:errors.append(r+' has an unsupported option value')
    frequency=None if fit('R13') and fit('R14') else 650 if fit('R13') else 300 if fit('R14') else 500
    mode=None if fit('R5')==fit('R15') else 'AUTO_SKIP' if fit('R5') else 'FCCM_AFTER_PG'
    if frequency!=500:review.append('Changing RF requires frequency-dependent ripple/FB/OCP/thermal/transient recalculation; this is not a released alternate design')
    if fit('R15'):review.append('FCCM assembly is electrically documented; verify light-load/negative-current behavior before release')
    if fit('R9'):review.append('External EN requires a defined 3.3V/5V drive or pull-up; check thresholds and sequencing')
    if fit('C15'):review.append('Snubber values require measured ringing and dissipation')
    groups=active_groups(doc);rf=next((g for g in groups if 'U1.22' in g),set())
    if frequency==500 and rf!={'U1.22'}:errors.append('Default RF is not electrically open after DNP removal')
    return {'status':'FAIL' if errors else 'REVIEW_REQUIRED' if review else 'CONFIGURATION_PASS',
      'errors':errors,'review_required':review,'frequency_nominal_kHz':frequency,'mode':mode,'rf_active_pin_island':sorted(rf),
      'rf_default_open':rf=={'U1.22'},'fitted_count':sum(fit(r) for r in comps),'dnp_count':sum(not fit(r) for r in comps),
      'scope':'Pin/option population check only, not converter performance acceptance'}


def compare_existing_pins(before,after):
    a=active_groups(before);common=set().union(*a);b=[g&common for g in active_groups(after) if g&common]
    aa={frozenset(g) for g in a};bb={frozenset(g) for g in b}
    return {'status':'PASS' if aa==bb else 'FAIL','retained_active_pins':len(common),
      'before_groups':len(aa),'after_projected_groups':len(bb),
      'missing_groups':[sorted(g) for g in aa-bb],'unexpected_groups':[sorted(g) for g in bb-aa],
      'method':'Remove DNP components, collapse fitted Device:R zero links, include open/NC IC terminals, project onto baseline active pins. Extra capacitors remain extra components, not an equivalence of frequency response.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('intent',type=Path);ap.add_argument('--baseline',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    doc=json.loads(a.intent.read_text());result={'default':audit(doc),'options':{name:audit(doc,override) for name,override in {
      '650kHz':{'R13':True},'300kHz':{'R14':True},'FCCM':{'R5':False,'R15':True},'external_EN':{'R7':False,'R9':True},'invalid_RF_both':{'R13':True,'R14':True}}.items()}}
    if a.baseline:result['baseline_active_pin_equivalence']=compare_existing_pins(json.loads(a.baseline.read_text()),doc)
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
