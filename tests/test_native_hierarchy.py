"""Synthetic regressions for native legacy/modern instance coverage; no design data."""
from pathlib import Path
import copy, hashlib, json, os, sys, tempfile, unittest
ROOT=Path(os.environ.get('ASG_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
from schematic_layout.project_audit import audit_project
from schematic_layout.symbol_integrity import audit_symbols
from schematic_layout.sexpr import parse, dump, form, first, all_nodes, set_node
from check_delivery_freshness import check

def library():
    return parse('''(symbol "Audit:X" (symbol "X_0_0" (rectangle (start 0 -2) (end 4 2) (stroke (width 0.1))))
      (symbol "X_1_1" (pin passive line (at -2 0 0) (length 2) (name "A") (number "1")))
      (symbol "X_2_1" (pin passive line (at 6 0 180) (length 2) (name "B") (number "2")))
      (symbol "X_1_2" (pin passive line (at -2 0 0) (length 2) (name "C") (number "3"))))''')
def symbol(uid,ref,unit=1):
    return form('symbol',form('uuid',uid),form('lib_id','Audit:X'),form('at',20,20,0),form('unit',unit),form('property','Reference',ref),form('property','Value','X'))
def sheet(uid,file,name=None):
    return form('sheet',form('uuid',uid),form('property','Sheet name',name or uid),form('property','Sheet file',file))
def spath(path,page):return form('path',path,form('page',page))
def annotation(path,ref,unit=1):return form('path',path,form('reference',ref),form('unit',unit))

class HierarchyRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.root=self.base/'board.kicad_sch'
        self.root_tree=form('kicad_sch',form('version',20211123),form('uuid','root'),form('lib_symbols',library()),symbol('r','R1'),sheet('a','child.kicad_sch'),form('sheet_instances',spath('/','1'),spath('/a','2')),form('symbol_instances',annotation('/r','R1'),annotation('/a/c','R2')))
        self.child=form('kicad_sch',form('version',20211123),form('uuid','child'),form('lib_symbols',library()),symbol('c','R2'))
        self.save()
    def save(self):
        self.root.write_text(dump(self.root_tree));(self.base/'child.kicad_sch').write_text(dump(self.child))
        for p in self.base.glob('*.kicad_sch'):self.assertLess(p.stat().st_size,200000)
    def kinds(self):return {e['kind'] for e in audit_project(self.root)['errors']}
    def xml(self,pins):
        p=self.base/'net.xml';refs=sorted({r for r,_ in pins})
        p.write_text('<export><components>'+''.join(f'<comp ref="{r}"><value>X</value></comp>' for r in refs)+'</components><nets><net name="N">'+''.join(f'<node ref="{r}" pin="{n}"/>' for r,n in pins)+'</net></nets></export>');return p
    def freshness(self,omit=None):
        outs={}
        for name in ('net.xml','erc.json','geometry.json','drawing.pdf'):
            p=self.base/name
            if not p.exists():p.write_text('hash fixture only')
            outs[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        ins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.base.glob('*.kicad_sch') if p.name!=omit}
        m={'schema_version':1,'root':self.root.name,'inputs':ins,'outputs':outs,'roles':dict(zip(('netlist','erc','geometry','render'),([n] for n in outs)))}
        p=self.base/'manifest.json';p.write_text(json.dumps(m));return check(p)
    def modern(self):
        for tree,parent,ref in [(self.root_tree,'/root','R1'),(self.child,'/root/a','R2')]:
            first(tree,'symbol').append(form('instances',form('project','board',annotation(parent,ref))))
        sh=first(self.root_tree,'sheet');sh.append(form('instances',form('project','board',spath('/root','2'))))
        for p in all_nodes(sh,'property'):p[1]=str(p[1]).replace(' ','')
    def test_legacy_two_resolves_globals_and_native_pins(self):
        r=audit_project(self.root);self.assertEqual(r['status'],'PASS',r);self.assertEqual(r['page_count'],2)
        s=audit_symbols(self.root,self.xml([('R1','1'),('R2','1')]));self.assertEqual(s['status'],'PASS',s);self.assertEqual(s['physical_pin_count'],2)
        self.assertEqual(self.freshness()['status'],'FRESH')
    def test_shared_child_counts_instances_not_files(self):
        self.root_tree.append(sheet('b','child.kicad_sch'));first(self.root_tree,'sheet_instances').append(spath('/b','3'));first(self.root_tree,'symbol_instances').append(annotation('/b/c','R3'));self.save()
        r=audit_project(self.root);self.assertEqual((r['status'],r['page_count'],len(r['file_sha256'])),('PASS',3,2),r)
        s=audit_symbols(self.root,self.xml([('R1','1'),('R2','1'),('R3','1')]));self.assertEqual(s['status'],'PASS',s);self.assertEqual(s['physical_pin_count'],3)
    def test_consistent_modern_and_global_annotations_pass(self):
        self.modern();self.save();self.assertEqual(audit_symbols(self.root,self.xml([('R1','1'),('R2','1')]))['status'],'PASS')
    def test_equal_aliases_pass_and_track_child(self):
        sh=first(self.root_tree,'sheet');sh.append(form('property','Sheetname','a'));sh.append(form('property','Sheetfile','child.kicad_sch'));self.save()
        self.assertEqual(audit_project(self.root)['status'],'PASS');self.assertEqual(self.freshness()['status'],'FRESH')
    def test_conflicting_file_alias_is_rejected_by_all_consumers(self):
        first(self.root_tree,'sheet').append(form('property','Sheetfile','decoy.kicad_sch'));(self.base/'decoy.kicad_sch').write_text(dump(self.child));self.save()
        self.assertIn('conflicting_sheet_property',self.kinds());self.assertNotEqual(self.freshness()['status'],'FRESH');self.assertEqual(audit_symbols(self.root)['status'],'FAIL')
    def test_conflicting_name_alias_is_rejected(self):
        first(self.root_tree,'sheet').append(form('property','Sheetname','wrong'));self.save();self.assertIn('conflicting_sheet_property',self.kinds());self.assertNotEqual(self.freshness()['status'],'FRESH')
    def test_duplicate_property_is_rejected(self):
        first(self.root_tree,'sheet').append(form('property','Sheet file','child.kicad_sch'));self.save();self.assertIn('duplicate_sheet_property',self.kinds());self.assertNotEqual(self.freshness()['status'],'FRESH')
    def test_missing_file_has_precise_error(self):
        (self.base/'child.kicad_sch').unlink();self.assertIn('missing_sheet',self.kinds());self.assertNotEqual(self.freshness()['status'],'FRESH')
    def test_omitted_existing_child_manifest_is_rejected(self):
        self.assertIn('untracked_active_sheet',{e['kind'] for e in self.freshness('child.kicad_sch')['errors']})
    def test_parent_escape_is_rejected(self):
        next(p for p in all_nodes(first(self.root_tree,'sheet'),'property') if p[1]=='Sheet file')[2]='../outside.kicad_sch';self.save();self.assertIn('nonportable_sheet_path',self.kinds());self.assertNotEqual(self.freshness()['status'],'FRESH')
    def test_duplicate_global_symbol_context_is_rejected(self):
        first(self.root_tree,'symbol_instances').append(annotation('/a/c','R2'));self.save();self.assertIn('duplicate_annotation_context',self.kinds())
    def test_duplicate_global_sheet_context_is_rejected(self):
        first(self.root_tree,'sheet_instances').append(spath('/a','2'));self.save();self.assertIn('duplicate_annotation_context',self.kinds())
    def test_conflicting_global_local_symbol_is_rejected(self):
        self.modern();set_node(first(first(first(first(self.child,'symbol'),'instances'),'project'),'path'),'reference','R9');self.save();self.assertIn('conflicting_annotation_context',self.kinds())
    def test_conflicting_global_local_page_is_rejected(self):
        self.modern();set_node(first(first(first(first(self.root_tree,'sheet'),'instances'),'project'),'path'),'page','9');self.save();self.assertIn('conflicting_annotation_context',self.kinds())
    def test_dangling_global_context_is_rejected(self):
        first(self.root_tree,'symbol_instances').append(annotation('/not-active/c','R9'));self.save();self.assertIn('dangling_annotation_context',self.kinds())
    def test_missing_annotation_does_not_use_reference_property(self):
        first(self.root_tree,'symbol_instances').pop();self.save();r=audit_project(self.root);self.assertEqual(r['status'],'INSUFFICIENT',r);s=audit_symbols(self.root);self.assertEqual({p['reference'] for p in s['pins']},{'R1'})
    def test_cross_project_context_is_not_borrowed(self):
        self.modern();self.root_tree.remove(first(self.root_tree,'symbol_instances'));first(first(first(self.child,'symbol'),'instances'),'project')[1]='other';self.save();s=audit_symbols(self.root);self.assertEqual({p['reference'] for p in s['pins']},{'R1'});self.assertEqual(s['status'],'INSUFFICIENT')
    def test_global_unit_two_is_used_and_checked(self):
        set_node(first(self.child,'symbol'),'unit',2);set_node(all_nodes(first(self.root_tree,'symbol_instances'),'path')[1],'unit',2);self.save();s=audit_symbols(self.root,self.xml([('R1','1'),('R2','2')]));self.assertEqual(s['status'],'PASS',s);self.assertEqual(next(p['unit'] for p in s['pins'] if p['reference']=='R2'),2)
        set_node(first(self.child,'symbol'),'unit',1);self.save();self.assertIn('instance_unit_mismatch',self.kinds())
    def test_legacy_style_selection_is_not_merged(self):
        set_node(first(self.child,'symbol'),'convert',2);self.save();s=audit_symbols(self.root,self.xml([('R1','1'),('R2','3')]));self.assertEqual(s['status'],'PASS',s);self.assertEqual({p['pin'] for p in s['pins'] if p['reference']=='R2'},{'3'})
    def test_nested_legacy_instances_resolve_relative_to_parent_file(self):
        (self.base/'sub').mkdir();sh=first(self.root_tree,'sheet');next(p for p in all_nodes(sh,'property') if p[1]=='Sheet file')[2]='sub/child.kicad_sch'
        self.child.append(sheet('b','../grand.kicad_sch'));first(self.root_tree,'sheet_instances').append(spath('/a/b','3'));first(self.root_tree,'symbol_instances').append(annotation('/a/b/g','R3'))
        self.save();(self.base/'sub/child.kicad_sch').write_text(dump(self.child));(self.base/'grand.kicad_sch').write_text(dump(form('kicad_sch',form('uuid','grand'),form('lib_symbols',library()),symbol('g','R3'))))
        r=audit_project(self.root);self.assertEqual((r['status'],r['page_count']),('PASS',3),r);self.assertEqual(audit_symbols(self.root,self.xml([('R1','1'),('R2','1'),('R3','1')]))['status'],'PASS')

    def test_symlink_escape_rejected_after_resolve(self):
        other=tempfile.TemporaryDirectory();self.addCleanup(other.cleanup)
        external=Path(other.name)/'outside.kicad_sch';external.write_text(dump(self.child))
        (self.base/'child.kicad_sch').unlink();(self.base/'child.kicad_sch').symlink_to(external)
        self.assertIn('nonportable_sheet_path',self.kinds());self.assertNotEqual(self.freshness()['status'],'FRESH')
    def test_legacy_cycle_is_rejected_without_infinite_walk(self):
        self.child.append(sheet('loop','board.kicad_sch'));self.save();self.assertIn('hierarchy_cycle',self.kinds());self.assertNotEqual(self.freshness()['status'],'FRESH')
    def test_unresolved_variable_rejected(self):
        next(p for p in all_nodes(first(self.root_tree,'sheet'),'property') if p[1]=='Sheet file')[2]='${UNKNOWN}/child.kicad_sch';self.save();self.assertIn('unresolved_sheet_path',self.kinds());self.assertNotEqual(self.freshness()['status'],'FRESH')
    def test_hidden_pin_still_has_native_physical_coverage(self):
        pin=first(all_nodes(first(first(self.child,'lib_symbols'),'symbol'),'symbol')[1],'pin');pin.append('hide')
        # Both pages use the identical changed cache; cached conflicts remain real errors.
        first(self.root_tree,'lib_symbols')[1]=copy.deepcopy(first(first(self.child,'lib_symbols'),'symbol'));self.save()
        s=audit_symbols(self.root,self.xml([('R1','1'),('R2','1')]));self.assertEqual(s['status'],'PASS',s);self.assertEqual(s['physical_pin_count'],2);self.assertTrue(all(p['hidden'] for p in s['pins']))
    def test_zero_length_pin_still_has_native_physical_coverage(self):
        lib=first(first(self.child,'lib_symbols'),'symbol');pin=first(all_nodes(lib,'symbol')[1],'pin');set_node(pin,'length',0);set_node(pin,'at',0,0,0)
        first(self.root_tree,'lib_symbols')[1]=copy.deepcopy(lib);self.save();s=audit_symbols(self.root,self.xml([('R1','1'),('R2','1')]));self.assertEqual(s['status'],'PASS',s);self.assertEqual(s['physical_pin_count'],2);self.assertTrue(all(p['reason']=='zero-length pin' for p in s['pins']))
    def test_zero_pin_entity_is_not_silently_ignored(self):
        lib=first(first(self.child,'lib_symbols'),'symbol');sub=all_nodes(lib,'symbol')[1];sub.remove(first(sub,'pin'));first(self.root_tree,'lib_symbols')[1]=copy.deepcopy(lib);self.save()
        self.assertIn('missing_active_unit_pins',self.kinds());self.assertEqual(audit_symbols(self.root)['status'],'FAIL')


    def test_unknown_declared_annotation_version_is_insufficient(self):
        set_node(self.root_tree, 'version', 99999999)
        self.modern(); self.save()
        report = audit_project(self.root)
        self.assertEqual(report['status'], 'INSUFFICIENT', report)
        self.assertTrue(any('unsupported native annotation version' in gap for gap in report['coverage_gaps']))
        self.assertEqual(self.freshness()['status'], 'FRESH')

    def test_missing_sheetname_does_not_block_filename_coverage(self):
        sh = first(self.root_tree, 'sheet')
        sh.remove(next(p for p in all_nodes(sh, 'property') if p[1] == 'Sheet name'))
        self.save()
        self.assertEqual(audit_project(self.root)['status'], 'PASS')
        self.assertEqual(self.freshness()['status'], 'FRESH')

    def test_duplicate_name_alias_is_rejected(self):
        first(self.root_tree, 'sheet').append(form('property', 'Sheet name', 'a'))
        self.save()
        self.assertIn('duplicate_sheet_property', self.kinds())
        self.assertNotEqual(self.freshness()['status'], 'FRESH')

    def test_modern_symbol_path_must_be_complete_and_active(self):
        self.modern()
        self.root_tree.remove(first(self.root_tree, 'symbol_instances'))
        ctx = first(first(first(first(self.child, 'symbol'), 'instances'), 'project'), 'path')
        ctx[1] = '/a'
        self.save()
        self.assertIn('dangling_annotation_context', self.kinds())
        self.assertEqual({p['reference'] for p in audit_symbols(self.root)['pins']}, {'R1'})

    def test_modern_sheet_path_is_parent_instance_not_child_instance(self):
        self.modern()
        ctx = first(first(first(first(self.root_tree, 'sheet'), 'instances'), 'project'), 'path')
        ctx[1] = '/root/a'
        self.save()
        self.assertIn('dangling_annotation_context', self.kinds())

    def test_duplicate_modern_symbol_context_is_rejected(self):
        self.modern()
        pr = first(first(first(self.child, 'symbol'), 'instances'), 'project')
        pr.append(copy.deepcopy(first(pr, 'path')))
        self.save()
        self.assertIn('duplicate_annotation_context', self.kinds())

    def test_modern_global_unit_conflict_is_rejected(self):
        self.modern()
        ctx = first(first(first(first(self.child, 'symbol'), 'instances'), 'project'), 'path')
        set_node(ctx, 'unit', 2)
        self.save()
        self.assertIn('conflicting_annotation_context', self.kinds())

    def test_dangling_global_page_context_is_rejected(self):
        first(self.root_tree, 'sheet_instances').append(spath('/inactive', '9'))
        self.save()
        self.assertIn('dangling_annotation_context', self.kinds())

    def test_duplicate_symbol_uuid_is_rejected(self):
        self.child.append(symbol('c', 'R9'))
        self.save()
        self.assertIn('missing_or_duplicate_symbol_uuid', self.kinds())

    def test_global_unit_must_be_present_not_inferred_from_display(self):
        ctx = all_nodes(first(self.root_tree, 'symbol_instances'), 'path')[1]
        ctx.remove(first(ctx, 'unit'))
        self.save()
        report = audit_project(self.root)
        self.assertEqual(report['status'], 'INSUFFICIENT', report)
        self.assertEqual({p['reference'] for p in audit_symbols(self.root)['pins']}, {'R1'})

    def test_annotation_gap_does_not_fail_hash_coverage(self):
        self.root_tree.remove(first(self.root_tree, 'symbol_instances'))
        self.save()
        self.assertEqual(audit_project(self.root)['status'], 'INSUFFICIENT')
        self.assertEqual(self.freshness()['status'], 'FRESH')


    def test_declared_modern_native_symbol_requires_uuid(self):
        # Real UUIDs and modern-only instance data: no legacy table can mask loss.
        self.modern()
        self.root_tree.remove(first(self.root_tree, 'symbol_instances'))
        root_uuid = 'f0000000-0000-0000-0000-000000000001'
        child_uuid = 'f0000000-0000-0000-0000-000000000002'
        symbol_uuid = 'f0000000-0000-0000-0000-000000000003'
        set_node(self.root_tree, 'uuid', root_uuid)
        for tree, ctx_path in ((self.root_tree, '/' + root_uuid), (self.child, '/' + root_uuid + '/a')):
            sym = first(tree, 'symbol')
            set_node(sym, 'uuid', symbol_uuid if tree is self.root_tree else child_uuid)
            first(first(first(sym, 'instances'), 'project'), 'path')[1] = ctx_path
        first(first(first(first(self.root_tree, 'sheet'), 'instances'), 'project'), 'path')[1] = '/' + root_uuid
        self.save()
        self.assertEqual(audit_project(self.root)['status'], 'PASS')
        sym = first(self.child, 'symbol'); sym.remove(first(sym, 'uuid')); self.save()
        report = audit_project(self.root)
        self.assertEqual(report['status'], 'INSUFFICIENT', report)
        self.assertTrue(any('missing native symbol UUID' in g for g in report['coverage_gaps']))
        self.assertEqual({p['reference'] for p in audit_symbols(self.root)['pins']}, {'R1'})
        self.assertEqual(self.freshness()['status'], 'FRESH')

    def test_duplicate_symbol_uuid_field_is_rejected(self):
        first(self.child, 'symbol').append(form('uuid', 'other'))
        self.save()
        self.assertIn('invalid_symbol_uuid', self.kinds())

    def test_uuid_with_path_separator_or_whitespace_is_rejected(self):
        for uid in ('a/b', ' a ', ''):
            with self.subTest(uid=uid):
                set_node(first(self.child, 'symbol'), 'uuid', uid)
                self.save()
                self.assertIn('invalid_symbol_uuid', self.kinds())


    def test_blank_global_reference_or_page_is_not_complete_annotation(self):
        for field in ('reference', 'page'):
            for blank in ('', '   '):
                with self.subTest(field=field, blank=blank):
                    if field == 'reference':
                        ctx = all_nodes(first(self.root_tree, 'symbol_instances'), 'path')[1]
                    else:
                        ctx = all_nodes(first(self.root_tree, 'sheet_instances'), 'path')[1]
                    original = copy.deepcopy(first(ctx, field))
                    set_node(ctx, field, blank); self.save()
                    self.assertEqual(audit_project(self.root)['status'], 'INSUFFICIENT')
                    ctx.remove(first(ctx, field)); ctx.append(original)
                    self.save()

if __name__=='__main__':unittest.main()
