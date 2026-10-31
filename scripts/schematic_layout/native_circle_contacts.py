"""Finite zero-length ring terminals, qualified only by a fresh native job.

This refines existing wire_body findings. Unknown source/render profiles retain
the entire old finding and coverage, never becoming missing measurements.
No external sidecar, nearest-object identity or blanket owner exemption.
"""
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET

from .scratch import scratch_base
from .native import find_cli, QUALIFIED_VERSIONS
from .native_geometry import SVG, finite, linear_path, stroke_path, distance, point_segment, filled_arc_box
from .native_geometry_context import configuration_hashes, context_files, spans, paths, sha
from .native_hierarchy import NativeHierarchy
from .scene import read_scene, transform, is_hidden
from .sexpr import all_nodes, first, value

EPS = .0002  # conservative native four-decimal serialization envelope

def _keys(node, allowed, required=()):
    keys=[str(n[0]) for n in node[1:] if isinstance(n,list) and n]
    if len(keys)!=len(node)-1 or set(keys)-set(allowed) or len(keys)!=len(set(keys)):
        raise ValueError('unknown or duplicate primitive property')
    if set(required)-set(keys): raise ValueError('missing primitive property')

def _stroke(node, allow_solid=False):
    stroke=first(node,'stroke');_keys(stroke or [],{'width','type','color'},{'width','type'})
    if first(stroke,'type') not in ([['type','default'],['type','solid']] if allow_solid else [['type','default']]): raise ValueError('nondefault stroke')
    width=first(stroke,'width')
    if len(width)!=2 or finite(width[1])<0: raise ValueError('invalid source stroke')
    color=first(stroke,'color')
    if color is not None and (len(color)!=5 or any(finite(v)!=0 for v in color[1:])):
        raise ValueError('explicit colored stroke unsupported')

def candidate_profiles(tree, scene):
    """Only source eligibility. It never authorizes an exemption by itself."""
    libs={str(n[1]):n for n in all_nodes(first(tree,'lib_symbols',[]),'symbol')}
    profiles=[]
    for symbol in scene.symbols:
        try:
            node=symbol.node
            allowed={'lib_id','lib_name','at','unit','mirror','in_bom','on_board','dnp','uuid','property','instances','pin'}
            children=[n for n in node[1:] if isinstance(n,list) and n]
            if len(children)!=len(node)-1 or any(n[0] not in allowed for n in children): raise ValueError('unknown placed display flag')
            for key in allowed-{'property','pin'}:
                if len(all_nodes(node,key))>1: raise ValueError('duplicate placement property')
            uid=value(node,'uuid');at=first(node,'at');mirror=str(value(node,'mirror',''))
            if not uid or not at or len(at)!=4 or finite(at[3]) not in (0,90,180,270) or mirror not in ('','x','y'):
                raise ValueError('unsupported placement')
            if str(value(node,'dnp','no'))!='no' or symbol.unit!=1: raise ValueError('unsupported instance')
            lib=libs[str(value(node,'lib_name',symbol.lib_id))]
            if any(not isinstance(n,list) or not n or n[0] not in {'pin_names','pin_numbers','in_bom','on_board','property','symbol'} for n in lib[2:]):raise ValueError('unknown cached display profile')
            if any(len(all_nodes(lib,k))>1 for k in ('pin_names','pin_numbers','in_bom','on_board')):raise ValueError('ambiguous cached display profile')
            if first(lib,'extends') or first(lib,'power') is not None: raise ValueError('unsupported library')
            if first(lib,'pin_names')!=['pin_names','hide'] or first(lib,'pin_numbers')!=['pin_numbers','hide']:
                raise ValueError('displayed pin text')
            graphics=[];pins=[]
            for sub in all_nodes(lib,'symbol'):
                m=re.search(r'_(\d+)_(\d+)$',str(sub[1]))
                if not m or m[1] not in ('0','1') or m[2]!='1': raise ValueError('multiunit or alternate body')
                for item in sub[2:]:
                    if not isinstance(item,list) or not item: raise ValueError('invalid sub-symbol')
                    if item[0]=='pin':pins.append(item)
                    elif item[0] in ('rectangle','circle'):graphics.append(item)
                    else:raise ValueError('mixed foreground')
            rectangles=[g for g in graphics if g[0]=='rectangle'];rings=[g for g in graphics if g[0]=='circle']
            if len(rectangles)!=1 or len(rings)<2 or len(rings)!=len(pins): raise ValueError('not ring terminals')
            rect=rectangles[0];_keys(rect,{'start','end','stroke','fill'},{'start','end','stroke','fill'});_stroke(rect)
            if first(rect,'fill')!=['fill',['type','background']]: raise ValueError('not background frame')
            start,end=first(rect,'start'),first(rect,'end')
            if len(start)!=3 or len(end)!=3: raise ValueError('invalid frame')
            x1,y1=map(finite,start[1:]);x2,y2=map(finite,end[1:]);lo,hi=min(x1,x2),max(x1,x2);bottom,top=min(y1,y2),max(y1,y2)
            if not 0<hi-lo<top-bottom: raise ValueError('not a finite single-column frame')
            pose=lambda p:transform(p,tuple(map(finite,at[1:3])),finite(at[3]),mirror)
            circles=[];local=[]
            for ring in rings:
                _keys(ring,{'center','radius','stroke','fill'},{'center','radius','stroke','fill'});_stroke(ring)
                if first(ring,'fill')!=['fill',['type','none']]: raise ValueError('filled circle')
                center=first(ring,'center');rn=first(ring,'radius')
                if len(center)!=3 or len(rn)!=2: raise ValueError('invalid circle')
                x,y=map(finite,center[1:]);r=finite(rn[1])
                if r<=0 or x!=(lo+hi)/2 or not (lo<x-r<x+r<hi and bottom<y-r<y+r<top):
                    raise ValueError('circle not inside own frame')
                local.append((x,y));circles.append({'center':pose((x,y)),'radius':r})
            numbers=[];centers=[]
            for pin in pins:
                if len(pin)<3 or pin[1:3]!=['passive','line']: raise ValueError('not passive line')
                children=pin[3:]
                if any(not isinstance(n,list) or not n or n[0] not in {'at','length','name','number'} for n in children): raise ValueError('unknown pin display')
                if any(len(all_nodes(pin,k))!=1 for k in ('at','length','name','number')): raise ValueError('ambiguous pin')
                pa=first(pin,'at');length=first(pin,'length');num=first(pin,'number')
                if len(pa)!=4 or finite(pa[3]) not in (0,180) or len(length)!=2 or finite(length[1])!=0 or len(num)!=3:
                    raise ValueError('unsupported pin anchor')
                numbers.append(str(num[1]));centers.append(tuple(map(finite,pa[1:3])))
            if len(set(numbers))!=len(numbers) or '' in numbers or Counter(local)!=Counter(centers): raise ValueError('pin-circle identity differs')
            placed_pins=all_nodes(node,'pin')
            if placed_pins:
                if any(len(p)!=3 or not isinstance(p[2],list) or p[2][0]!='uuid' or len(p[2])!=2 or not p[2][1] for p in placed_pins):raise ValueError('unknown placed pin identity')
                if Counter(str(p[1]) for p in placed_pins)!=Counter(numbers) or len(set(str(p[2][1]) for p in placed_pins))!=len(placed_pins):raise ValueError('placed physical pins differ')
            if len(set(local))!=len(local): raise ValueError('duplicate circle')
            if len(symbol.pins)!=len(pins) or any(p.kind!='passive' or p.point!=p.inner for p in symbol.pins): raise ValueError('scene pin mismatch')
            corners=[pose((x,y)) for x in (lo,hi) for y in (bottom,top)]
            interior=[min(p[0] for p in corners),min(p[1] for p in corners),max(p[0] for p in corners),max(p[1] for p in corners)]
            profiles.append({'object':f'{symbol.ref}:unit{symbol.unit}','uuid':str(uid),'unit':symbol.unit,'lib_id':symbol.lib_id,'library':lib,'graphics':graphics,'pin_nodes':pins,'circles':circles,'pins':{p.point:p.id for p in symbol.pins},'pin_numbers':{pose(c):n for c,n in zip(centers,numbers)},'interior':interior,'axis':transform((1,0),(0,0),finite(at[3]),mirror),'placement':node})
        except (ValueError,KeyError,IndexError,TypeError):continue
    return profiles

def contact_corridor(profile,a,b,wire_width,circles):
    """Own local exit only, keeping every other ring's entire ink disk."""
    try:
        if wire_width<=0 or not math.isfinite(wire_width) or len(circles)!=len(profile['circles']):return False
        if Counter(tuple(c['center']) for c in circles)!=Counter(tuple(c['center']) for c in profile['circles']):return False
        x1,y1,x2,y2=profile['interior'];dx,dy=profile['axis']
        pad=profile.get('native_frame_width',0)/2+wire_width/2+EPS
        for p,other in ((a,b),(b,a)):
            if p not in profile['pins'] or other in profile['pins']:continue
            vx,vy=other[0]-p[0],other[1]-p[1]
            if not (vx or vy) or abs(vx*dy-vy*dx)>1e-8:continue
            if x1-pad<=other[0]<=x2+pad and y1-pad<=other[1]<=y2+pad:continue
            contact=next(c for c in circles if tuple(c['center'])==p)
            inner=contact['radius']-contact['width']/2
            if inner<=0 or wire_width/2+EPS>=inner:continue
            if any(tuple(c['center'])!=p and point_segment(tuple(c['center']),p,other)<=c['radius']+(wire_width+c['width'])/2+EPS for c in circles):continue
            return True
    except (ValueError,KeyError,TypeError):pass
    return False

def _opaque_page(text):
    root=ET.fromstring(text)
    for node in list(root):
        if node.tag.rsplit('}',1)[-1]=='title':root.remove(node)
    return ET.tostring(root,encoding='utf-8')

def _locate_root(source):
    # Only this source's directory/project; no ancestor or unrelated-tree scan.
    roots=[]
    for p in source.parent.glob('*.kicad_sch'):
        if p.is_symlink() or not p.with_suffix('.kicad_pro').is_file():continue
        h=NativeHierarchy(p)
        if source in h.trees:roots.append(h)
    if len(roots)!=1:raise ValueError('unique bound project root unavailable')
    h=roots[0]
    if h.errors or h.coverage_gaps or any(sum(p['path']==q['path'] for q in h.pages)!=1 for p in h.pages):raise ValueError('unbound or repeated native context')
    return h

def _paint(o, foreign=False):
    st=o['style']
    dash=st.get('stroke-dasharray','none')
    if dash!='none':
        # Foreign dashed ink is protected by its entire continuous capsule
        # union. This is an upper bound for finite round dash caps/joins, not
        # a dash-gap permission. Owned artwork and conductors remain solid.
        if not foreign or not re.fullmatch(r'[\d.eE+\-\s,]+',dash):raise ValueError('unsupported native dash paint')
        values=[finite(v) for v in re.split(r'[\s,]+',dash.strip())]
        if len(values)<2 or any(v<=0 for v in values):raise ValueError('unsupported native dash pattern')
    if o['opacity']!=1 or finite(st.get('stroke-opacity',1))!=1 or finite(st['fill-opacity'])!=1 or st.get('stroke-linecap')!='round' or st.get('stroke-linejoin')!='round':
        raise ValueError('unsupported native paint')
    width=finite(st.get('stroke-width',0))
    if width<=0:raise ValueError('unbound native stroke')
    return width

def _geometry(o):
    a=o['attrs'];tag=o['tag']
    if tag=='circle':return ('circle',*[round(finite(a[k]),4) for k in ('cx','cy','r')])
    if tag=='rect' and finite(a.get('rx',0))==0:return ('rect',*[round(finite(a[k]),4) for k in ('x','y','width','height')])
    raise ValueError('not target native geometry')

def filled_arc(o):
    """A filled path in the qualified circular-A profile (never a filled glyph)."""
    if 'A' not in o['attrs'].get('d','') or 'stroked-text' in o['classes']:
        return False
    try:
        filled_arc_box(o['attrs']['d'],finite(o['style'].get('stroke-width',0)),o['style'],o['opacity'])
    except ValueError:
        return False
    return True

def _hits(o,a,b,wire_width):
    st=o['style'];attrs=o['attrs'];tag=o['tag'];w=finite(st.get('stroke-width',0));radius=(wire_width+w)/2+EPS
    if tag=='circle':return point_segment((finite(attrs['cx']),finite(attrs['cy'])),a,b)<=finite(attrs['r'])+radius
    if tag=='rect':
        x,y,ww,hh=(finite(attrs[k]) for k in ('x','y','width','height'))
        if st.get('fill','none')!='none':
            from .qa import _round_stroke_hits_box
            from .geometry import Box
            return _round_stroke_hits_box(a,b,Box(x,y,x+ww,y+hh),radius)
        pts=[(x,y),(x+ww,y),(x+ww,y+hh),(x,y+hh),(x,y)]
        return any(distance(a,b,c,d)<=radius for c,d in zip(pts,pts[1:]))
    if tag=='path' and st.get('fill','none')!='none' and filled_arc(o):
        # Filled circular-A region: its conservative bounding box (native_geometry.filled_arc_box).
        from .qa import _round_stroke_hits_box
        from .geometry import Box
        return _round_stroke_hits_box(a,b,Box(*filled_arc_box(attrs['d'],w,st,o['opacity'])),(wire_width)/2+EPS)
    if tag=='path' and st.get('fill','none')=='none':
        # Arc capsules already include their own sagitta/serialization/numeric
        # envelope. Physical pin caps/legs and source-wire identity below still
        # require strict MLZ, never an approximated circular path.
        return any(distance(a,b,c,d)<=(wire_width+v)/2+EPS for c,d,v in stroke_path(attrs['d'],w))
    raise ValueError('unsupported foreground; retain old finding')

def _validate_foreground(native):
    for o in native.objects.values():
        st=o['style']
        if o['opacity']!=1 or finite(st.get('stroke-opacity',1))!=1 or finite(st['fill-opacity'])!=1:
            raise ValueError('unknown foreground transparency')
        if o['tag'] not in ('path','rect','circle'):raise ValueError('unsupported foreground shape')
        if st.get('stroke','none')!='none':_paint(o,foreign=True)
        if st.get('fill','none')!='none':
            if (o['tag']=='path' and not filled_arc(o)) or not re.fullmatch(r'#[0-9a-fA-F]{6}',st['fill']):raise ValueError('filled font or unknown foreground paint')
        if o['tag']=='rect' and finite(o['attrs'].get('rx',0))!=0:raise ValueError('rounded foreground rectangle')

def refine_wire_contacts(schematic,report,cli=None,workdir=None,expected_source_sha256=None):
    """Fresh controlled refinement; returned diagnostics cannot authorize reuse."""
    out=copy.deepcopy(report);errors=[f for f in report['findings'] if f['code']=='wire_body']
    if not errors:return out
    source=Path(schematic).resolve()
    from .sexpr import parse
    if expected_source_sha256 is not None and sha(source)!=expected_source_sha256:
        out['native_contact_qualification']={'status':'FALLBACK','reason':'source changed since geometry inspection','removed':[]}
        return out
    initial_source=sha(source)
    tree=parse(source.read_text());scene=read_scene(tree);profiles=candidate_profiles(tree,scene)
    wanted={o for f in errors for o in f['objects'] if not o.startswith('wire:')}
    profiles=[p for p in profiles if p['object'] in wanted]
    if not profiles:return out
    evidence={'status':'FALLBACK','removed':[],'commands':[],'exports':[]};tick=time.monotonic()
    try:
        def unknown(n):
            if isinstance(n,list):
                # Explicitly hidden source properties are not a displayed
                # literal. Every actual native glyph still participates in
                # the foreground union, even if a project override shows one.
                if n and n[0]=='property' and is_hidden(n):return
                if n and n[0]=='font' and (first(n,'face') is not None or 'italic' in n):raise ValueError('unknown target font profile')
                for v in n:unknown(v)
            elif isinstance(n,str) and '${' in n:raise ValueError('unknown target display variable')
        unknown(tree)
        h=_locate_root(source);root=h.root;page=next(p for p in h.pages if h.base/p['path']==source);rel=page['path']
        # Keep exact legacy object names only when the active native instance agrees.
        for p in profiles:
            node=next(s for s in all_nodes(h.trees[source],'symbol') if str(value(s,'uuid'))==p['uuid'])
            active=h.symbol_contexts.get((page['instance'],id(node)))
            if active!={'reference':p['object'].split(':unit')[0],'unit':p['unit']}:raise ValueError('native/source reference or unit mismatch')
        files=context_files(root,h)
        original={n:sha(p) for n,p in files.items()};config=configuration_hashes();cli=cli or find_cli()
        if original[rel]!=initial_source:raise ValueError('source changed during candidate inspection')
        if not cli:raise ValueError('native tool unavailable')
        tool_hash=sha(Path(cli));producer={p.name:sha(p) for p in (Path(__file__),Path(__file__).with_name('native_geometry.py'),Path(__file__).with_name('native_geometry_context.py'))}
        environment={k:os.environ.get(k) for k in ('KICAD_CONFIG_HOME','KICAD_FONTCONFIG_FILE','FONTCONFIG_FILE','FONTCONFIG_PATH','LANG','LC_ALL')}
        if workdir is None:
            base=scratch_base()/'asg-native-contacts'
            base.mkdir(parents=True,exist_ok=True);work=Path(tempfile.mkdtemp(prefix='fresh-',dir=base))
        else:
            work=Path(workdir);work.mkdir(exist_ok=False,parents=True)
        (work/'tmp').mkdir();env=dict(os.environ,TMPDIR=str(work/'tmp'),PYTHONDONTWRITEBYTECODE='1')
        evidence.update({'root':str(root),'source_sha256':original,'configuration_sha256':config,'tool_sha256':tool_hash,'producer_sha256':producer,'workdir':str(work),'source_instance':page['instance']})
        def run(cmd):
            before=configuration_hashes();t=time.monotonic();start=datetime.now(timezone.utc).isoformat();r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,env=env,timeout=300)
            evidence['commands'].append({'argv':list(map(str,cmd)),'start_utc':start,'seconds':time.monotonic()-t,'rc':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
            if r.returncode or before!=config or configuration_hashes()!=config:raise ValueError('native command/configuration changed')
            return r
        if run([cli,'version']).stdout.strip() not in QUALIFIED_VERSIONS:raise ValueError('unsupported native version')
        raw=files[rel].read_bytes().decode('utf-8');ranges=spans(raw);nodepaths=paths(tree)
        def export(label,edits=()):
            folder=work/label;folder.mkdir();clone=folder/'source';clone.mkdir()
            for n,p in files.items():dest=clone/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
            altered=raw
            for a,b,new in sorted(edits,reverse=True):altered=altered[:a]+new+altered[b:]
            if edits:(clone/rel).write_bytes(altered.encode('utf-8'))
            # Page canvas paint is not source foreground. Native graphic
            # background fills remain present and must still be attributed.
            before={n:sha(clone/n) for n in files};run([cli,'sch','export','svg','--exclude-drawing-sheet','--no-background-color','-o',folder/'svg',clone/root.name])
            if before!={n:sha(clone/n) for n in files}:raise ValueError('native modified clone source')
            svg={p.name:p.read_text() for p in (folder/'svg').glob('*.svg')}
            evidence['exports'].append({'label':label,'input_sha256':before,'svg_sha256':{p.name:sha(p) for p in (folder/'svg').glob('*.svg')},'source_spans':[[a,b] for a,b,_ in edits],'source_edits':[[a,b,new] for a,b,new in edits],'changed_file':rel if edits else None})
            return svg
        base=export('baseline');replica=export('replica')
        if set(base)!=set(replica) or len(base)!=len(h.pages) or any(_opaque_page(base[n])!=_opaque_page(replica[n]) for n in base):raise ValueError('non-reproducible full native project')
        marker='ASG_CONTACT_'+uuid.uuid4().hex;end=ranges[()][1]-1
        marked=export('page-binding',[(end,end,' (text '+json.dumps(marker)+' (at 10 10 0) (effects (font (size 1 1))) (uuid '+json.dumps(str(uuid.uuid4()))+'))')])
        names=[n for n in base if _opaque_page(base[n])!=_opaque_page(marked[n])]
        if set(base)!=set(marked) or len(names)!=1:raise ValueError('ambiguous native source page')
        name=names[0];native=SVG(base[name]);added=SVG(marked[name])
        _validate_foreground(native)
        dp=native.primitives-added.primitives;dt=native.texts-added.texts;ap=added.primitives-native.primitives;at=added.texts-native.texts
        if dp or dt or sum(at.values())!=1 or json.loads(next(iter(at)))['literal']!=marker:raise ValueError('page marker changed existing native objects')
        added.segments(ap,glyph=True)
        def difference(label,edits):
            changed=export(label,edits)
            if set(changed)!=set(base) or any(_opaque_page(base[n])!=_opaque_page(changed[n]) for n in base if n!=name):raise ValueError('non-target native page changed')
            other=SVG(changed[name]);deleted=native.primitives-other.primitives
            added=other.primitives-native.primitives
            if native.texts!=other.texts or not deleted:raise ValueError('causal mask changed non-target foreground')
            return deleted,added,other
        def mask(label,nodes):
            deleted,added,_=difference(label,[(*ranges[nodepaths[id(n)]],'') for n in nodes])
            if added:raise ValueError('mask added foreground')
            return deleted
        owned={};groups={}
        for p in profiles:groups.setdefault(p['lib_id'],[]).append(p)
        for libid,targets in groups.items():
            # Every placed use of the deleted cached group must be represented.
            allprofiles=[p for p in candidate_profiles(tree,scene) if p['lib_id']==libid]
            if len(allprofiles)!=sum(str(value(s,'lib_id'))==libid for s in all_nodes(tree,'symbol')):raise ValueError('unknown cached group owner')
            deleted=mask('group-'+str(len(owned)),targets[0]['graphics']);expected=Counter();mapping={}
            for p in allprofiles:
                x1,y1,x2,y2=p['interior'];geoms=[('rect',round(x1,4),round(y1,4),round(x2-x1,4),round(y2-y1,4))]+[('circle',round(c['center'][0],4),round(c['center'][1],4),round(c['radius'],4)) for c in p['circles']]
                for g in geoms:expected[g]+=1;mapping[g]=p['uuid']
            if any(n!=1 for n in expected.values()):raise ValueError('overlapping cached owners unsupported')
            actual=Counter();witness={};background=Counter();background_keys={}
            for k,n in deleted.items():
                o=native.objects[k];g=_geometry(o)
                st=o['style']
                if o['tag']=='rect' and st.get('stroke','none')=='none':
                    if o['opacity']!=1 or finite(st['fill-opacity'])!=1 or not re.fullmatch(r'#[0-9a-fA-F]{6}',st.get('fill','')) or set(st)-{'fill','fill-opacity','stroke'}:
                        raise ValueError('unknown native background fill')
                    background[g]+=n;background_keys[g]=k;continue
                w=_paint(o)
                if o['tag']=='circle' and o['style'].get('fill','none')!='none':raise ValueError('filled native contact circle')
                actual[g]+=n;witness[g]=(k,w)
            if actual!=expected:raise ValueError('incomplete source/native body group')
            if any(g not in expected or g[0]!='rect' or n!=1 for g,n in background.items()):raise ValueError('unbound background fill')
            # A zero-length passive line still plots a round native point cap.
            # Change only cached leg length, never number/UUID/unit/anchor/name,
            # and require the complete old/new cap/leg multiset to match every
            # source pin of this group. No nearest-point or owner inference.
            probe=.137
            cap_deleted,leg_added,leg_svg=difference('pin-cap-'+str(len(owned)),[(*ranges[nodepaths[id(first(pin,'length'))]],'(length %.10g)'%probe) for pin in targets[0]['pin_nodes']])
            cap_expected=Counter();leg_expected=Counter();pinowner={}
            pairkey=lambda a,b:tuple(sorted((tuple(round(v,4) for v in a),tuple(round(v,4) for v in b))))
            for p in allprofiles:
                at=first(p['placement'],'at');mirror=str(value(p['placement'],'mirror',''));pose=lambda q:transform(q,tuple(map(finite,at[1:3])),finite(at[3]),mirror)
                for pin in p['pin_nodes']:
                    pa=first(pin,'at');x,y,angle=map(finite,pa[1:]);tip=pose((x,y));inside=pose((x+probe*round(math.cos(math.radians(angle))),y+probe*round(math.sin(math.radians(angle)))))
                    cap_expected[pairkey(tip,tip)]+=1;leg_expected[pairkey(tip,inside)]+=1;pinowner[pairkey(tip,tip)]=p['uuid']
            def pin_pairs(svg,keys):
                found=Counter();witness={}
                for k,n in keys.items():
                    o=svg.objects[k];w=_paint(o)
                    if o['tag']!='path' or o['classes'] or o['style'].get('fill','none')!='none':raise ValueError('unbound native pin leg')
                    lines=linear_path(o['attrs'].get('d',''))
                    if len(lines)!=1:raise ValueError('ambiguous native pin cap')
                    key=pairkey(*lines[0]);found[key]+=n;witness[key]=(k,w)
                return found,witness
            caps,cap_witness=pin_pairs(native,cap_deleted);legs,_=pin_pairs(leg_svg,leg_added)
            if caps!=cap_expected or legs!=leg_expected or any(n!=1 for n in cap_expected.values()):raise ValueError('pin cap intervention changed other foreground')
            for p in targets:
                keys=Counter();circles=[];x1,y1,x2,y2=p['interior'];g=('rect',round(x1,4),round(y1,4),round(x2-x1,4),round(y2-y1,4));key,rw=witness[g];keys[key]+=1
                if g in background_keys:keys[background_keys[g]]+=1
                for c in p['circles']:
                    g=('circle',round(c['center'][0],4),round(c['center'][1],4),round(c['radius'],4));key,cw=witness[g];keys[key]+=1
                    if c['radius']+(cw+rw)/2+EPS>=min(c['center'][0]-x1,x2-c['center'][0],c['center'][1]-y1,y2-c['center'][1]):raise ValueError('native ring exceeds own local frame')
                    circles.append({**c,'width':cw})
                    cap_key,cap_width=cap_witness[pairkey(c['center'],c['center'])]
                    if cap_width/2+EPS>=c['radius']-cw/2:raise ValueError('native cap exceeds contact circle inner aperture')
                    keys[cap_key]+=1
                owned[p['uuid']]=(keys,circles,rw)
        evidence['bindings']=[{'object':p['object'],'source_uuid':p['uuid'],'unit':p['unit'],'convert':1,'lib_id':p['lib_id'],'pins':[{'physical_pin':v,'anchor':list(k)} for k,v in p['pin_numbers'].items()],'native_circles':owned[p['uuid']][1],'native_frame_width':owned[p['uuid']][2]} for p in profiles]
        wires=all_nodes(tree,'wire')
        for wire in wires:
            _keys(wire,{'pts','stroke','uuid'},{'pts','stroke'});_stroke(wire,allow_solid=True)
            if len(first(wire,'pts'))!=3:raise ValueError('unknown wire source path')
        wire_deleted=mask('all-wires',wires)
        pairkey=lambda a,b:tuple(sorted((tuple(round(v,4) for v in a),tuple(round(v,4) for v in b))))
        expected=Counter(pairkey(a,b) for a,b in scene.wires);actual=Counter();wire_widths={}
        for k,n in wire_deleted.items():
            o=native.objects[k];w=_paint(o)
            if o['tag']!='path' or o['style'].get('fill','none')!='none' or o['classes']:raise ValueError('not complete wire stroke')
            segments=linear_path(o['attrs'].get('d',''))
            if len(segments)!=1:raise ValueError('native wire segmentation unsupported')
            key=pairkey(*segments[0]);actual[key]+=n;wire_widths[key]=max(w,wire_widths.get(key,0))
        if actual!=expected or any(n!=1 for n in actual.values()):raise ValueError('source/native wire identity mismatch')
        # All actual visible foreground is protected; only the own group and
        # causally attributed conductor paths may be removed from this union.
        upper=max(finite(o['style'].get('stroke-width',0)) for o in native.objects.values())
        removable=[]
        for f in errors:
            obj=next((x for x in f['objects'] if not x.startswith('wire:')),None);ps=[p for p in profiles if p['object']==obj]
            if len(ps)!=1:continue
            p=ps[0];wi=int(next(x for x in f['objects'] if x.startswith('wire:')).split(':')[1]);a,b=scene.wires[wi];keys,circles,rw=owned[p['uuid']];width=wire_widths[pairkey(a,b)]
            if not contact_corridor({**p,'native_frame_width':rw},a,b,max(width,upper),circles):continue
            # A field's legacy estimate may be absent or too narrow. Preserve
            # the old rejection if any actual glyph touches this entire wire,
            # including portions beyond the owner's local contact corridor.
            if any('stroked-text' in native.objects[k]['classes'] and _hits(native.objects[k],a,b,max(width,upper)) for k in native.primitives):continue
            point=a if a in p['pins'] else b;other=b if point==a else a;x1,y1,x2,y2=p['interior']
            exitpoint=(x2+rw/2+EPS,point[1]) if other[0]>point[0] else (x1-rw/2-EPS,point[1]) if other[0]<point[0] else (point[0],y2+rw/2+EPS) if other[1]>point[1] else (point[0],y1-rw/2-EPS)
            rest=native.primitives-keys-wire_deleted
            if any(_hits(native.objects[k],point,exitpoint,max(width,upper)) for k in rest):continue
            removable.append(f)
        kept=[f for f in report['findings'] if f not in removable]
        if removable and not any(f['severity']=='error' for f in kept) and (report['coverage']['gaps'] or kept):
            raise ValueError('refinement would hide measured findings behind existing coverage gaps')
        if original!={n:sha(p) for n,p in files.items()} or config!=configuration_hashes() or sha(Path(cli))!=tool_hash or producer!={p.name:sha(p) for p in (Path(__file__),Path(__file__).with_name('native_geometry.py'),Path(__file__).with_name('native_geometry_context.py'))} or environment!={k:os.environ.get(k) for k in environment}:
            raise ValueError('fresh source/tool/producer/config/environment binding drift')
        for record in evidence['exports']:
            folder=work/record['label']
            if any(sha(folder/'source'/n)!=v for n,v in record['input_sha256'].items()) or any(sha(folder/'svg'/n)!=v for n,v in record['svg_sha256'].items()):raise ValueError('fresh raw witness binding drift')
        out['findings']=kept;out['counts']=dict(Counter(f['code'] for f in kept))
        out['status']='FAIL' if kept else 'INSUFFICIENT' if out['coverage']['gaps'] else 'PASS'
        evidence['status']='QUALIFIED';evidence['removed']=[{'code':f['code'],'objects':f['objects']} for f in removable]
    except (ValueError,OSError,KeyError,TypeError,IndexError,StopIteration,subprocess.SubprocessError) as exc:
        evidence['reason']=str(exc)
    evidence['seconds']=time.monotonic()-tick;out['native_contact_qualification']=evidence
    if 'workdir' in evidence:(Path(evidence['workdir'])/'qualification.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    return out
