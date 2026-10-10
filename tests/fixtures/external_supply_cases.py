"""Small, self-authored synthetic native fixtures; no third-party board data."""
from pathlib import Path
import json,subprocess
from schematic_layout.generate import make_root,Libraries,library_dirs
from schematic_layout.scene import read_scene
from schematic_layout.sexpr import all_nodes,first,form,value,dump,Atom
from schematic_layout.native import find_cli
from schematic_layout.external_supply import audit_external_supply,renamed_copy,flag_references
from schematic_layout.project_audit import properties
def build(base, name,kind='Connector_Generic:Conn_01x02',role=None,flags=1,flagnet='VCC',customflag=False):
    cli=find_cli();out=base/name;out.mkdir()
    load_ref='FLGX1' if name=='alias_collision' else 'R1'
    comps=[{'ref':'J1','lib_id':kind,'value':'synthetic-origin','mpn':'synthetic-origin','footprint':'','datasheet':'','fields':{}}, {'ref':load_ref,'lib_id':'Device:R','value':'1k','mpn':'1k','footprint':'','datasheet':''}]
    if role:comps[0]['fields']['ComponentRole']=role
    intent={'schema_version':1,'design_id':'synthetic-'+name,'components':comps,'nets':[{'name':'VCC','pins':['J1.1',load_ref+'.1']},{'name':'GND','pins':['J1.2',load_ref+'.2']}], 'external_supply':[{'net':'VCC','pin':'J1.1','reason':'Synthetic unit fixture only'}]}
    layout={'schema_version':1,'placements':{'J1':{'at':[50.8,50.8]},load_ref:{'at':[76.2,76.2]}}}
    root,_,uid,_=make_root(intent,layout,name)
    if name == 'role_type_conflict':
        for lib in all_nodes(first(root,'lib_symbols'),'symbol'):
            if lib[1] == kind:
                for sub in all_nodes(lib,'symbol'):
                    for pin in all_nodes(sub,'pin'):
                        if str(value(pin,'number')) == '1':pin[1]=Atom('input')
    if name == 'custom_undeclared':intent['external_supply']=[]
    # Connect each pin with an explicit local label, then place markers on that same label.
    for sym in read_scene(root).symbols:
        for pin in sym.pins:
            net=next(n['name'] for n in intent['nets'] if pin.id in n['pins'])
            root.append(form('label',net,form('at',*pin.point,0),form('effects',form('font',form('size',1,1))),form('uuid',uid('label:'+pin.id))))
    lib=Libraries(library_dirs()).load('power:PWR_FLAG')
    if customflag:
        lib[1]='Custom:SourceMarker'
        for sub in all_nodes(lib,'symbol'):sub[1]=str(sub[1]).replace('PWR_FLAG_','SourceMarker_')
    first(root,'lib_symbols').append(lib)
    for i in range(flags):
        at=[101.6+12.7*i,101.6];ref=f'#FLG{i+1}'
        root.append(form('symbol',form('lib_id',lib[1]),form('at',*at,0),form('unit',1),form('in_bom',Atom('no')),form('on_board',Atom('no')),form('dnp',Atom('no')),form('uuid',uid(ref)),form('property','Reference',ref,form('at',*at,0),form('effects',form('font',form('size',1,1)))),form('property','Value','PWR_FLAG',form('at',*at,0),form('effects',form('font',form('size',1,1)))),form('pin','1',form('uuid',uid(ref+'pin'))),form('instances',form('project',name,form('path','/'+uid('root'),form('reference',ref),form('unit',1))))))
        root.append(form('label',flagnet,form('at',*at,0),form('effects',form('font',form('size',1,1))),form('uuid',uid(ref+'label'))))
    # Literal marker-reference text must not be rewritten by the probe.
    root.append(form('text','#FLG1',form('at',127,127,0),form('effects',form('font',form('size',1,1))),form('uuid',uid('text'))))
    sch=out/(name+'.kicad_sch');sch.write_text(dump(root)+'\n');(out/'intent.json').write_text(json.dumps(intent,indent=2)+'\n')
    xml=out/'native.xml';cmd=[cli,'sch','export','netlist','--format','kicadxml','-o',str(xml),str(sch)]
    r=subprocess.run(cmd,capture_output=True,text=True);(out/'export.log').write_text(r.stdout+r.stderr)
    result=audit_external_supply(sch,[sch],intent,xml,cli,out/'probe')
    aliases={};text_kept=None
    if flags and any(flag_references([sch]).values()):
        probe,aliases=renamed_copy(sch,[sch],out/'rename-check')
        text_kept=any(x[1]=='#FLG1' for x in all_nodes(__import__('schematic_layout.sexpr',fromlist=['parse']).parse(probe.read_text()),'text'))
    rec={'name':name,'export_returncode':r.returncode,'result':result,'aliases':aliases,'text_preserved':text_kept}
    return root,intent,sch,xml,rec
