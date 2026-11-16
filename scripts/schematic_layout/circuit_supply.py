"""Evidence-bound manual qualification of discrete-converter supply markers.

This checks review freshness and native topology, NOT converter feasibility.
A converter's diode/transformer/pass-transistor pins must keep their real types.
A source path is at least two parts; a net one part drives by itself (an IC switch node)
names that part alone and the datasheet page that says so (``basis``, Matrix R2 SW_12).
"""
import json
from pathlib import Path

from .citations import CITATION, check_source

KEY = 'reviewed_circuit_supply'
REQUIRED = {'net','pin','refs','reason','evidence'}

def declarations(intent):
    ds=intent.get(KEY,[])
    if not isinstance(ds,list): raise ValueError(KEY+' must be a list')
    names=set(); errors=[]
    comps={c['ref']:c for c in intent.get('components',[])}
    nets={n['name']:set(n['pins']) for n in intent.get('nets',[])}
    for d in ds:
        # binding_sha256 and evidence.sha256 are accepted and not read: records written before they were dropped.
        if not isinstance(d,dict) or not REQUIRED<=set(d)<=REQUIRED|{'basis','binding_sha256'}:
            raise ValueError(KEY+' requires net, pin, refs, reason and evidence (basis optional)')
        if any(not isinstance(d[k],str) or not d[k].strip() for k in ('net','pin','reason')):
            raise ValueError('empty circuit-supply declaration')
        if 'basis' in d and not (isinstance(d['basis'],str) and CITATION.match(d['basis'])):
            raise ValueError('circuit supply basis is datasheet:<path>#p<page>')
        if not isinstance(d['refs'],list) or not d['refs'] or len(set(d['refs']))!=len(d['refs']) or any(r not in comps for r in d['refs']):
            raise ValueError('circuit supply needs distinct, existing source-path components')
        if len(d['refs'])<2 and 'basis' not in d:
            raise ValueError('a one-part circuit supply cites the datasheet page that makes the part the source (basis)')
        ev=d['evidence']
        if not isinstance(ev,dict) or not {'path','locator'}<=set(ev)<={'path','sha256','locator'} or any(not isinstance(v,str) or not v.strip() for v in ev.values()):
            raise ValueError('circuit supply needs a review document and locator')
        if d['net'] in names: raise ValueError('duplicate circuit supply '+d['net'])
        names.add(d['net'])
        if d['pin'] not in nets.get(d['net'],set()) or d['pin'].rsplit('.',1)[0] not in d['refs']:
            errors.append({'kind':'circuit_output_not_bound','net':d['net']})
        if intent.get('net_roles',{}).get(d['net']) not in ('power','return'):
            errors.append({'kind':'circuit_supply_not_power_or_return','net':d['net']})
    return ds,errors

def judge(root,intent,decls,by_pin,flags,aliases,artifact_root):
    errors=[]
    sheets={s.get('name','') for s in root.findall('design/sheet')}|{'/'}
    def named(a,b):return a==b or (not b.startswith('/') and any(a==p+b for p in sheets))
    for d in decls:
        net=by_pin.get(d['pin']); prefix={'net':d['net']}
        if net is None or not named(net['name'],d['net']):
            errors.append(dict(prefix,kind='circuit_output_native_missing'));continue
        if sum(n is net for _,n in flags)!=1:
            errors.append(dict(prefix,kind='circuit_marker_count'))
        if any(r not in aliases and t.split('+')[0]=='power_out' for r,p,t in net['nodes']):
            errors.append(dict(prefix,kind='circuit_has_native_source'))
        ev=d['evidence']; base=Path(artifact_root).resolve(); path=(base/ev['path']).resolve()
        if not path.is_relative_to(base) or not path.is_file():
            errors.append(dict(prefix,kind='circuit_evidence_missing'))
        else:
            try: present=ev['locator'] in path.read_text(encoding='utf-8')
            except (UnicodeError,OSError):present=False
            if not present:errors.append(dict(prefix,kind='circuit_evidence_locator_missing'))
        if 'basis' in d:
            cited=check_source(d['basis'],(),[base])
            if cited and cited['status']=='FAIL':
                errors.append(dict(prefix,kind='circuit_basis_citation',reason=cited['reason']))
        # Identity and pin topology are the intent_netlist gate's; a reviewed supply part must still be fitted.
        for ref in d['refs']:
            if any(c.find("property[@name='dnp']") is not None for c in root.findall(f"components/comp[@ref='{ref}']")):
                errors.append(dict(prefix,kind='circuit_component_not_fitted',ref=ref))
    return errors
