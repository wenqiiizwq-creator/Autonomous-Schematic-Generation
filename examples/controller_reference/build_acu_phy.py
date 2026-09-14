"""Instantiate the same tested PHY contract for the isolated ACU control domain."""
import argparse,copy
from pathlib import Path
from build_phy import phy
from build_reference import run

def acu_phy():
 i,l=phy();d=copy.deepcopy(i);p=copy.deepcopy(l)
 refs={c['ref']:c['ref'].replace('260','120').replace('2651','1251') for c in i['components']}
 def pin(s):r,n=s.rsplit('.',1);return refs[r]+'.'+n
 for c in d['components']:c['ref']=refs[c['ref']]
 for n in d['nets']:n['name']=n['name'].replace('TCU_','ACU_');n['pins']=[pin(x) for x in n['pins']]
 d['no_connect']=[pin(x) for x in d['no_connect']]
 d['design_id']='ACU-Ethernet-RevC';d['title']='ACU KSZ8081RNA reference-driven redraw'
 p['placements']={refs[r]:v for r,v in p['placements'].items()}
 for policy in p['nets'].values():
  for g in policy.get('groups',[]):
   if isinstance(g,list):g[:]=[pin(x) for x in g]
   else:g['pins']=[pin(x) for x in g['pins']]
 p['nets']={n.replace('TCU_','ACU_'):v for n,v in p['nets'].items()}
 for a in p['annotations']:a['text']=a['text'].replace('TCU','ACU')
 return d,p
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args();run(*acu_phy(),args.out/'ACU-Ethernet')
