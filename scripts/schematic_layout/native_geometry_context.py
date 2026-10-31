"""Fresh full-project finite SVG qualification. All interventions are render-only.

No mutation of the delivered source, no number/physical-ID mask, no old cache.
Page identity is established by an added source-specific annotation intervention.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import uuid

from .native import QUALIFIED_VERSIONS
from .native_geometry import SVG, removal, finite, bounds
from .native_hierarchy import NativeHierarchy
from .sexpr import parse, all_nodes, first, value

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()

def configuration_hashes():
    config=os.environ.get('KICAD_CONFIG_HOME')
    dirs=[Path(config)] if config else [Path.home()/'Library/Preferences/kicad/10.0',Path.home()/'.config/kicad/10.0']
    extra=[Path(os.environ[k]) for k in ('FONTCONFIG_FILE','KICAD_FONTCONFIG_FILE') if os.environ.get(k)]
    return {str(p):sha(p) for p in [*extra,*[p for d in dirs if d.is_dir() for p in d.rglob('*') if p.is_file()]] if p.is_file()}

def producer_hashes():
    return {p.name:sha(p) for p in (Path(__file__),Path(__file__).with_name('native_geometry.py'))}

class FreshGeometryJob(dict):
    """Controller-only live receipt. The serialized form is audit evidence."""
    def digest(self):
        return hashlib.sha256(json.dumps(self,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def spans(text):
    """AST paths to exact character ranges; untouched source bytes are retained."""
    parse(text)  # use the shared grammar's validation before locating spans
    pattern=re.compile(r'\s+|;[^\n]*|\(|\)|"(?:\\.|[^"\\])*"|[^\s();"]+')
    ts=[m for m in pattern.finditer(text) if not m.group().isspace() and not m.group().startswith(';')]
    ranges={}; i=0
    def node(path):
        nonlocal i
        start=ts[i].start(); token=ts[i].group(); i+=1
        if token=='(':
            index=0
            while ts[i].group()!=')': node(path+(index,)); index+=1
            end=ts[i].end(); i+=1
        else: end=ts[i-1].end()
        ranges[path]=(start,end)
    node(())
    return ranges

def paths(tree):
    out={}
    def walk(node,path):
        if isinstance(node,list):
            out[id(node)]=path
            for i,n in enumerate(node): walk(n,path+(i,))
    walk(tree,()); return out

def context_files(root,hierarchy):
    """Only native inputs, never scan reports/calculations or unrelated tasks."""
    files={p for p in hierarchy.trees}
    for p in (root.with_suffix('.kicad_pro'),root.parent/'sym-lib-table',root.parent/'fp-lib-table'):
        if p.is_file(): files.add(p)
    table=root.parent/'sym-lib-table'
    if table.is_file():
        for lib in all_nodes(parse(table.read_text()),'lib'):
            raw=value(lib,'uri','').replace('${KIPRJMOD}',str(root.parent))
            if '${' in raw: raise ValueError('unbound library table variable')
            p=Path(raw)
            if not p.is_absolute(): p=root.parent/p
            p=p.resolve()
            if not p.is_relative_to(root.parent): raise ValueError('external library context not qualified')
            if p.is_file(): files.add(p)
    if any(p.is_symlink() for p in files): raise ValueError('symlink context input unsupported')
    return {p.relative_to(root.parent).as_posix():p for p in files}

def prepare_geometry_context(root, project, cli, workdir, pin_names=True):
    root=Path(root).resolve(); work=Path(workdir)
    if work.exists(): raise ValueError('native geometry output must be fresh')
    work.mkdir(parents=True); (work/'tmp').mkdir()
    result=FreshGeometryJob({'schema':'native-geometry-context-v1','root':str(root),'project':project or root.stem,
            'status':'INSUFFICIENT','commands':[],'pages':{},'gaps':[], 'started_utc':now()})
    h=NativeHierarchy(root,project)
    for page in h.pages:
        result['pages'].setdefault(page['path'],{'source_sha256':h.file_sha256.get(page['path']),
            'frames':[],'texts':[],'pin_texts':[],'owner_outlines':[],'gaps':[],'review':[], 'instance':page['instance']})
    source_files={}; env=dict(os.environ,TMPDIR=str(work/'tmp'),PYTHONDONTWRITEBYTECODE='1')
    def run(argv):
        before=configuration_hashes(); start=now()
        r=subprocess.run(list(map(str,argv)),capture_output=True,text=True,env=env,timeout=300)
        after=configuration_hashes()
        result['commands'].append({'argv':list(map(str,argv)),'start_utc':start,'end_utc':now(),
            'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,
            'config_before':before,'config_after':after})
        if before!=after: raise ValueError('renderer configuration changed during job')
        if r.returncode: raise ValueError('native SVG command failed')
        return r
    def clone_export(label, rel=None, replacement=None):
        folder=work/label; folder.mkdir(); src=folder/'source'; src.mkdir()
        for name,p in source_files.items():
            dest=src/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(p,dest)
        if rel is not None:
            target=src/rel; old=target.read_text(); start,end,new=replacement
            target.write_text(old[:start]+new+old[end:])
            if target.read_bytes() != (old[:start]+new+old[end:]).encode(): raise ValueError('source span mutation mismatch')
        before={name:sha(src/name) for name in source_files}
        run([cli,'sch','export','svg','--exclude-drawing-sheet','-o',folder/'svg',src/root.name])
        after={name:sha(src/name) for name in source_files}
        if before!=after: raise ValueError('native export modified source inputs')
        result.setdefault('exports',[]).append({'label':label,'input_sha256':before,
            'source_span':list(replacement[:2]) if replacement else None,
            'changed_file':rel,'svg_sha256':{p.name:sha(p) for p in (folder/'svg').glob('*.svg')}})
        out={p.name:SVG(p.read_text(),scoped=True) for p in (folder/'svg').glob('*.svg')}
        if not out: raise ValueError('no native SVG pages')
        return out
    def assert_other_pages(base,new,target):
        if set(base)!=set(new): raise ValueError('native page set changed')
        for name in base:
            if name!=target and (base[name].primitives!=new[name].primitives or base[name].texts!=new[name].texts):
                raise ValueError('non-target page changed')
    counter=0
    def change(rel,nodepath,edit):
        nonlocal counter
        counter+=1; text=source_files[rel].read_text(); span=spans(text)[nodepath]
        return clone_export('mask-%04d'%counter,rel,(*span,edit))
    def field_ink(rel,page_svg,node,nodepaths,ranges):
        if any('${' in str(n) for n in node) or '${' in str(node): raise ValueError('field variable unsupported')
        font=first(first(node,'effects',[]),'font',[])
        if first(font,'face') is not None or 'italic' in font: raise ValueError('external/italic font unsupported')
        if any(c in str(node[2]) for c in ('~{','^{','_{','\\')): raise ValueError('formatted field unsupported')
        effects=first(node,'effects')
        if effects is None: raise ValueError('missing field effects')
        hide=first(effects,'hide')
        if hide is not None or 'hide' in effects: raise ValueError('hidden field unsupported')
        path=nodepaths[id(effects)]; start,end=ranges[path]
        old=source_files[rel].read_text()[start:end]; edit=old[:-1]+' (hide yes))'
        new=change(rel,path,edit); assert_other_pages(baseline,new,page_svg)
        ink=removal(baseline[page_svg],new[page_svg]); ink['source_span']=[start,end]
        ink['witness']='mask-%04d'%counter
        return ink
    def frame_ink(rel,page_svg,node,nodepaths,ranges,placement=None):
        keys=[str(n[0]) for n in node[1:] if isinstance(n,list) and n]
        allowed=({'at','size','stroke','fill','uuid','property','instances'} if node[0]=='sheet'
                 else {'start','end','stroke','fill','uuid'})
        if len(keys)!=len(node)-1 or set(keys)-allowed:
            raise ValueError('unknown structural display/profile property')
        required={'at','size','stroke','fill','uuid'} if node[0]=='sheet' else {'start','end','stroke','fill'}
        if any(keys.count(k)!=1 for k in required): raise ValueError('duplicate/missing structural property')
        stroke=first(node,'stroke'); width=first(stroke or [],'width')
        if (width is None or len(width)!=2 or first(stroke,'type')!=['type','default']
                or len(stroke)!=3 or len(all_nodes(stroke,'type'))!=1):
            raise ValueError('unsupported frame stroke')
        original=finite(width[1])
        if original<0: raise ValueError('negative source frame width')
        if len(all_nodes(node,'stroke'))!=1: raise ValueError('duplicate frame stroke')
        if node[0]=='sheet':
            at=first(node,'at'); size=first(node,'size')
            if not at or len(at)!=3 or not size or len(size)!=3: raise ValueError('unsupported sheet shape')
            x,y=map(finite,at[1:]); w,hgt=map(finite,size[1:])
            fill=first(node,'fill')
            if fill!=['fill',['color','0','0','0','0']]: raise ValueError('nontransparent sheet fill unsupported')
        else:
            a,b=first(node,'start'),first(node,'end')
            if not a or not b or len(a)!=3 or len(b)!=3: raise ValueError('unsupported rectangle')
            x,y=map(finite,a[1:]); ex,ey=map(finite,b[1:]); x,y,w,hgt=min(x,ex),min(y,ey),abs(ex-x),abs(ey-y)
            if placement is None:
                if first(node,'fill')!=['fill',['type','none']]: raise ValueError('filled annotation rectangle unsupported')
            else:
                from .scene import transform
                if first(node,'fill') not in (['fill',['type','none']],['fill',['type','background']]): raise ValueError('unknown body fill')
                at=first(placement,'at'); mirror=value(placement,'mirror','')
                if not at or len(at)!=4 or finite(at[3]) not in (0,90,180,270) or mirror not in ('','x','y'): raise ValueError('unknown body placement')
                ps=[transform((px,py),(finite(at[1]),finite(at[2])),finite(at[3]),mirror) for px in (x,x+w) for py in (y,y+hgt)]
                x,y=min(p[0] for p in ps),min(p[1] for p in ps)
                w,hgt=max(p[0] for p in ps)-x,max(p[1] for p in ps)-y
        if min(w,hgt)<=0: raise ValueError('nonpositive frame size')
        new=change(rel,nodepaths[id(width)],'(width %.10g)'%(max(original,.1)+.137))
        assert_other_pages(baseline,new,page_svg)
        oldsvg,newsvg=baseline[page_svg],new[page_svg]
        deleted=oldsvg.primitives-newsvg.primitives; added=newsvg.primitives-oldsvg.primitives
        if sum(deleted.values())!=1 or sum(added.values())!=1 or oldsvg.texts!=newsvg.texts:
            if node[0]!='sheet': raise ValueError('frame intervention changed other primitives')
            # Sheet field pen can depend on the border pen. A fill-only probe
            # must leave all existing text/strokes invariant instead.
            fill=first(node,'fill')
            new=change(rel,nodepaths[id(fill)],'(fill (color 0 0 0 1))')
            assert_other_pages(baseline,new,page_svg)
            newsvg=new[page_svg]; deleted=oldsvg.primitives-newsvg.primitives; added=newsvg.primitives-oldsvg.primitives
            if oldsvg.texts!=newsvg.texts or sum(added.values())!=1 or sum(deleted.values())!=1:
                raise ValueError('frame fill probe changed other primitives')
            changed=newsvg.objects[next(iter(added))]
            if changed['tag']!='rect': raise ValueError('frame fill probe not rectangular')
            old=oldsvg.objects[next(iter(deleted))]
            if old['attrs']!=changed['attrs']: raise ValueError('frame fill changed geometry')
            actual=[finite(changed['attrs'].get(k,'0')) for k in ('x','y','width','height')]
            if any(abs(a-b)>0.0001 for a,b in zip(actual,(x,y,w,hgt))): raise ValueError('fill/native source rectangle mismatch')
            ink=oldsvg.segments(deleted)
            return {'segments':ink,'box':bounds(ink),'interior':[x,y,x+w,y+hgt],
                    'source_span':list(ranges[nodepaths[id(fill)]]),'witness':'mask-%04d'%counter,
                    'attribution':'single-fill-probe/one-complete-deleted-own-outline'}
        old=oldsvg.objects[next(iter(deleted))]; changed=newsvg.objects[next(iter(added))]
        if old['tag']!='rect' or old['attrs']!=changed['attrs']: raise ValueError('not unique native rectangular frame')
        if {k:v for k,v in old['style'].items() if k!='stroke-width'}!={k:v for k,v in changed['style'].items() if k!='stroke-width'}:
            raise ValueError('non-width frame style changed')
        actual=[finite(old['attrs'].get(k,'0')) for k in ('x','y','width','height')]
        if any(abs(a-b)>0.0001 for a,b in zip(actual,(x,y,w,hgt))):
            raise ValueError('native/source frame geometry differs beyond SVG serialization precision')
        ink=oldsvg.segments(deleted)
        return {'segments':ink,'box':bounds(ink),'interior':[x,y,x+w,y+hgt],
                'source_span':list(ranges[nodepaths[id(width)]]),'witness':'mask-%04d'%counter}
    try:
        if h.errors or h.coverage_gaps: raise ValueError('unbound native hierarchy/annotations')
        if result['project']!=root.stem: raise ValueError('CLI selected project mismatch')
        if any(sum(p['path']==page['path'] for p in h.pages)!=1 for page in h.pages):
            raise ValueError('reused hierarchical source instance unsupported')
        source_files=context_files(root,h)
        if any(b'\r' in p.read_bytes() for name,p in source_files.items() if name.endswith('.kicad_sch')):
            raise ValueError('non-LF source text profile unsupported; preserve exact source bytes')
        result['producer_sha256']=producer_hashes()
        result['configuration_sha256']=configuration_hashes()
        result['source_sha256']={name:sha(p) for name,p in source_files.items()}
        result['tool']={'path':str(Path(cli).resolve()),'sha256':sha(cli),'version':run([cli,'version']).stdout.strip()}
        if result['tool']['version'] not in QUALIFIED_VERSIONS: raise ValueError('native version profile not qualified')
        result['environment']={k:env.get(k) for k in ('KICAD_CONFIG_HOME','KICAD_FONTCONFIG_FILE','FONTCONFIG_FILE','FONTCONFIG_PATH','LANG','LC_ALL')}
        baseline=clone_export('baseline'); replica=clone_export('replica')
        if set(baseline)!=set(replica) or len(baseline)!=len(h.pages): raise ValueError('native page count/context mismatch')
        for name in baseline:
            if baseline[name].primitives!=replica[name].primitives or baseline[name].texts!=replica[name].texts:
                raise ValueError('fresh baseline not reproducible')
        mapping={}
        for page in h.pages:
            rel=page['path']; text=source_files[rel].read_text(); marker='ASG_GEOMETRY_'+uuid.uuid4().hex
            annotation=' (text '+json.dumps(marker)+' (at 10 10 0) (effects (font (size 1 1))) (uuid '+json.dumps(str(uuid.uuid4()))+'))'
            end=spans(text)[()][1]-1
            added=clone_export('page-binding-'+str(len(mapping)),rel,(end,end,annotation))
            if set(added)!=set(baseline): raise ValueError('marker changed native page set')
            candidates=[]
            for name,old in baseline.items():
                new=added[name]; dp=old.primitives-new.primitives; dt=old.texts-new.texts
                ap=new.primitives-old.primitives; at=new.texts-old.texts
                if dp or dt: raise ValueError('marker changed existing native objects')
                if ap or at:
                    if sum(at.values())!=1 or json.loads(next(iter(at)))['literal']!=marker: raise ValueError('marker not unique full literal')
                    new.segments(ap,glyph=True); candidates.append(name)
            if len(candidates)!=1 or candidates[0] in mapping.values(): raise ValueError('ambiguous native page/source binding')
            mapping[rel]=candidates[0]
            result['pages'][rel]['native_svg']=candidates[0]
        for page in h.pages:
            rel=page['path']; data=result['pages'][rel]; tree=h.trees[root.parent/rel]; nodepaths=paths(tree); ranges=spans(source_files[rel].read_text()); nativepage=mapping[rel]
            stroke_upper=max(finite(o['style'].get('stroke-width','0')) for o in baseline[nativepage].objects.values())
            data['stroke_upper_mm']=stroke_upper
            data['page_mm']=baseline[nativepage].page
            # Unsupported arc ink stays in equality; only its own page loses coverage.
            for key,reason in sorted(baseline[nativepage].unsupported.items()):
                data['gaps'].append('native arc ink unsupported: '+reason+': d='+baseline[nativepage].objects[key]['attrs'].get('d','')[:120])
            def unknown_display(n):
                if isinstance(n,list):
                    # Library caches are definitions, and hidden properties
                    # (e.g. KiCad's Intersheetrefs) produce no page ink.
                    if n and (n[0]=='lib_symbols' or (n[0]=='property' and hidden(n))): return
                    if n and n[0]=='font' and first(n,'face') is not None: data['gaps'].append('native display: external font face remains unsupported')
                    for child in n: unknown_display(child)
                elif isinstance(n,str) and '${' in n and n!='${KIPRJMOD}':
                    data['gaps'].append('native display: source variable conversion remains unsupported')
            unknown_display(tree)
            for tag in ('sheet','rectangle'):
                for node in all_nodes(tree,tag):
                    uid=value(node,'uuid'); record={'id':str(uid),'kind':tag,'qualified':False}
                    try:
                        if not uid or len([n for n in all_nodes(tree,tag) if value(n,'uuid')==uid])!=1: raise ValueError('ambiguous structural UUID')
                        record.update(frame_ink(rel,nativepage,node,nodepaths,ranges))
                        if tag=='sheet':
                            if all_nodes(node,'pin'): raise ValueError('sheet pin outline/text/normalized anchor not qualified')
                            props=all_nodes(node,'property')
                            if len(props)!=2 or set(str(p[1]) for p in props)!={'Sheetname','Sheetfile'}: raise ValueError('unsupported sheet property set')
                            for prop in props:
                                ink=field_ink(rel,nativepage,prop,nodepaths,ranges)
                                ink.update({'id':str(uid)+':'+str(prop[1]),'role':str(prop[1]),'property':prop})
                                data['texts'].append(ink)
                        record['qualified']=True
                    except (ValueError,KeyError,IndexError,TypeError) as exc:
                        data['gaps'].append(tag+':'+str(uid)+': '+str(exc))
                    data['frames'].append(record)
            # Unique cache + one placed instance only; number is never modified.
            libraries={n[1]:n for n in all_nodes(first(tree,'lib_symbols',[]),'symbol')}
            symbols=all_nodes(tree,'symbol')
            if not pin_names:
                if symbols: data['gaps'].append('pin-text native qualification not requested for this preparation job')
                continue
            for symbol in symbols:
                libid=value(symbol,'lib_id'); lib=libraries.get(libid); uid=value(symbol,'uuid'); unit=str(value(symbol,'unit',1))
                if not lib: continue
                active=[]
                for sub in all_nodes(lib,'symbol'):
                    match=re.search(r'_(\d+)_(\d+)$',str(sub[1]))
                    if match and match[1] in ('0',unit) and match[2]=='1': active+=all_nodes(sub,'pin')
                if not active: continue
                # Pin text the library hides draws no ink. Visible pin text that
                # this channel cannot qualify is a render-review item: the page
                # report already requires native review of pin names/numbers, so
                # it does not also make the page INSUFFICIENT.
                if not hidden(first(lib,'pin_numbers',[])):
                    data['review'].append('pin-number:'+str(uid)+': physical pin numbers need native render review')
                if hidden(first(lib,'pin_names',[])) or not any(visible_name(p) for p in active): continue
                nums=[str(value(p,'number','')) for p in active]
                if (not uid or first(lib,'extends') or first(lib,'power') is not None
                    or str(value(symbol,'dnp','no'))!='no'
                    or str(value(symbol,'convert',1))!='1'
                    or any(re.search(r'_(\d+)_[01]$',str(sub[1])) and int(re.search(r'_(\d+)_[01]$',str(sub[1]))[1])>1 for sub in all_nodes(lib,'symbol'))
                    or sum(value(s,'lib_id')==libid for s in symbols)!=1
                    or len(set(nums))!=len(nums) or '' in nums
                    or any(str(value(s,'lib_id'))==libid for path,t in h.trees.items() if path!=root.parent/rel for s in all_nodes(t,'symbol'))):
                    data['review'].append('pin-name:'+str(uid)+': ambiguous/shared/unsupported cache identity'); continue
                try:
                    graphics=[]
                    for sub in all_nodes(lib,'symbol'):
                        match=re.search(r'_(\d+)_(\d+)$',str(sub[1]))
                        if match and match[1] in ('0',unit) and match[2] in ('0','1'):
                            graphics += [n for n in sub[2:] if isinstance(n,list) and n and n[0]!='pin']
                    if not graphics or any(n[0]!='rectangle' for n in graphics): raise ValueError('only complete rectangular owner foreground supported')
                    for oi,graphic in enumerate(graphics):
                        outline=frame_ink(rel,nativepage,graphic,nodepaths,ranges,symbol)
                        outline.update({'id':str(uid)+':outline:'+str(oi),'symbol_uuid':str(uid)})
                        data['owner_outlines'].append(outline)
                except (ValueError,KeyError,TypeError,IndexError) as exc:
                    data['review'].append('pin-name:'+str(uid)+': own foreground outline incomplete: '+str(exc))
                for pin in active:
                    number=str(value(pin,'number')); name=first(pin,'name')
                    if not visible_name(pin): continue
                    try:
                        if first(first(first(name,'effects',[]),'font',[]),'face') is not None: raise ValueError('external pin font unsupported')
                        if any(c in str(name[1]) for c in ('${','~{','^{','_{','\\')): raise ValueError('formatted/variable pin name')
                        nodepath=nodepaths[id(name)]+(1,)
                        new=change(rel,nodepath,'""'); assert_other_pages(baseline,new,nativepage)
                        ink=removal(baseline[nativepage],new[nativepage])
                        if ink['literal']!=str(name[1]): raise ValueError('transformed pin shown literal unsupported')
                        ink.update({'id':str(uid)+':pin:'+number+':name','symbol_uuid':str(uid), 'lib_id':libid,
                            'unit':unit,'convert':1,'physical_pin':number,'role':'name', 'source_span':list(ranges[nodepath]),
                            'page_stroke_upper_mm':stroke_upper,'witness':'mask-%04d'%counter})
                        data['pin_texts'].append(ink)
                    except (ValueError,KeyError,IndexError,TypeError) as exc:
                        data['review'].append('pin-name:'+str(uid)+':'+number+': '+str(exc))
        if result['source_sha256']!={name:sha(p) for name,p in source_files.items()}: raise ValueError('original source changed during job')
        configs=[c['config_before'] for c in result['commands']]
        if any(c!=configs[0] for c in configs): raise ValueError('renderer configuration changed between exports')
        if result['producer_sha256']!=producer_hashes(): raise ValueError('geometry producer changed during job')
        if result['configuration_sha256']!=configuration_hashes(): raise ValueError('geometry configuration changed during job')
        result['status']='PASS'  # binding; per-object coverage is in pages/gaps
    except (ValueError,OSError,KeyError,IndexError,TypeError,subprocess.SubprocessError) as exc:
        result['gaps'].append('native geometry context: '+str(exc))
    result['finished_utc']=now()
    result['export_count']=sum('svg' in c['argv'] for c in result['commands'])
    (work/'context.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    result._workdir=str(work.resolve())
    result._sealed_sha256=result.digest()
    return result

def hidden(node):
    """True when a property/pin_names/pin_numbers node is hidden (KiCad 6-10 syntaxes)."""
    if not isinstance(node,list): return False
    for n in [node]+all_nodes(node,'effects'):
        if any(str(x)=='hide' for x in n[1:] if not isinstance(x,list)): return True
        h=first(n,'hide')
        if h is not None and (len(h)==1 or str(h[1])=='yes'): return True
    return False


def visible_name(pin):
    name=first(pin,'name')
    return bool(name and len(name)>1 and str(name[1]) not in ('','~')
                and not hidden(name) and not hidden(pin))


def page_context_from_job(job, schematic):
    if not isinstance(job, FreshGeometryJob) or job.digest()!=job._sealed_sha256:
        raise ValueError("Native geometry requires an unchanged live fresh-job object")
    if job["status"]!="PASS":
        raise ValueError("Native geometry binding unavailable: "+"; ".join(job["gaps"]))
    root=Path(job["root"]); source=Path(schematic).resolve()
    rel=source.relative_to(root.parent).as_posix()
    if any(sha(root.parent/name)!=digest for name,digest in job["source_sha256"].items()):
        raise ValueError("Native geometry original source binding changed")
    if job["producer_sha256"]!=producer_hashes() or job["configuration_sha256"]!=configuration_hashes():
        raise ValueError("Native geometry producer/configuration binding changed")
    if any(os.environ.get(k)!=v for k,v in job["environment"].items()):
        raise ValueError("Native geometry environment changed")
    if sha(job["tool"]["path"])!=job["tool"]["sha256"]:
        raise ValueError("Native geometry tool binding changed")
    work=Path(job._workdir)
    for export in job["exports"]:
        folder=work/export["label"]
        if any(sha(folder/"svg"/name)!=digest for name,digest in export["svg_sha256"].items()):
            raise ValueError("Native geometry raw SVG binding changed")
        if any(sha(folder/"source"/name)!=digest for name,digest in export["input_sha256"].items()):
            raise ValueError("Native geometry clone source binding changed")
    page=job["pages"][rel]
    if sha(source)!=page["source_sha256"]:
        raise ValueError("Native geometry page source binding changed")
    return page
