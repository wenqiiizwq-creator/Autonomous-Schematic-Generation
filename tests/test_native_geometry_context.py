"""Finite same-job native controls: unique source causality, never visual guesses."""
import json
import subprocess
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from schematic_layout.scratch import scratch_base
from schematic_layout.native import find_cli
from unittest import mock
from schematic_layout import native_geometry_context as ngc
from schematic_layout.native_geometry_context import prepare_geometry_context,page_context_from_job,sha,spans,hidden,visible_name
from schematic_layout.sexpr import form as f,Atom as A,dump,parse,first,all_nodes
from schematic_layout.scene import read_scene
from schematic_layout.qa import check_scene

def uid(name): return str(uuid.uuid5(uuid.NAMESPACE_URL,'ASG-own-native-geometry/'+name))
def effects(angle=0): return f('effects',f('font',f('size',1.27,1.27)))
def fixture(kind):
    root=f('kicad_sch',f('version',20250114),f('generator','eeschema'),f('uuid',uid('root')),f('paper','A4'),f('lib_symbols'))
    x,y=(2.54,50.8) if kind=='offpage' else (50.8,50.8)
    name='${NAME}' if kind=='variable' else 'DUP'
    sh=f('sheet',f('at',x,y),f('size',76.2,38.1),f('stroke',f('width',0),f('type',A('default'))),f('fill',f('color',0,0,0,0)),f('uuid',uid('sheet')),
         f('property','Sheetname',name,f('at',x,y-2.54,0),effects()),
         f('property','Sheetfile','child.kicad_sch',f('at',x,y+40.64,0),effects()),
         f('instances',f('project','native',f('path','/'+uid('root'),f('page','2')))))
    if kind=='pins': sh.append(f('pin','PORT',A('input'),f('at',x,y+19.05,180),effects(),f('uuid',uid('pin'))))
    root.append(sh)
    root.append(f('text','DUP',f('at',x+38.1,y+19.05,0),effects(),f('uuid',uid('caption'))))
    if kind=='wire':
        for px in (x-10.16,x+10.16):
            root.append(f('label','N',f('at',px,y+19.05,0),effects(),f('uuid',uid(str(px)))))
        root.append(f('wire',f('pts',f('xy',x-10.16,y+19.05),f('xy',x+10.16,y+19.05)),f('stroke',f('width',0),f('type',A('default'))),f('uuid',uid('wire'))))
    if kind=='overlay': root.append(f('text','OVERLAY',f('at',x,y+40.64,0),effects(),f('uuid',uid('foreign-text'))))
    if kind=='identical': root.append(f('rectangle',f('start',x,y),f('end',x+76.2,y+38.1),f('stroke',f('width',.254),f('type',A('default'))),f('fill',f('type',A('none'))),f('uuid',uid('foreign-outline'))))
    if kind=='unknown-stroke': first(sh,'stroke').append(f('color',0,0,0,0))
    if kind=='extra-display': sh.append(f('dnp',A('yes')))
    if kind in ('cjk','rotate90','rotate180','bold','filledfont'):
        prop=all_nodes(sh,'property')[0]
        if kind=='cjk': prop[2]='重复 字段'
        if kind.startswith('rotate'): first(prop,'at')[3]=float(kind[6:])
        if kind=='bold': first(first(prop,'effects'),'font').append(A('bold'))
        if kind=='filledfont': first(first(prop,'effects'),'font').append(f('face','Arial'))
    if kind=='cachevar':
        # A library cache definition is not page ink, even with a variable in it.
        first(root,'lib_symbols').append(f('symbol','Cache:Part',f('property','Sim.Library','${KICAD9_SYMBOL_DIR}/x.sp',
            f('at',0,0,0),f('effects',f('font',f('size',1.27,1.27)),f('hide',A('yes'))))))
    root.append(f('sheet_instances',f('path','/',f('page','1'))))
    child=f('kicad_sch',f('version',20250114),f('generator','eeschema'),f('uuid',uid('child')),f('paper','A4'),f('lib_symbols'))
    return root,child

class SpanTests(unittest.TestCase):
    def test_exact_span_preserves_non_target_bytes_unicode_and_comments(self):
        src='(x ; comment\n (property "字段" "DUP" (effects (font (size 1 1)))))\n'
        ranges=spans(src);start,end=ranges[(1,3)]
        self.assertEqual('(effects (font (size 1 1)))',src[start:end])
        changed=src[:start]+src[start:end-1]+' (hide yes))'+src[end:]
        self.assertEqual(src[:start],changed[:start]);self.assertEqual('\n',changed[-1])

class HiddenTextTests(unittest.TestCase):
    """Hidden pin text and properties draw no ink, in old and new KiCad syntax."""
    def test_hidden_flags(self):
        self.assertTrue(hidden(parse('(pin_numbers (hide yes))')))
        self.assertTrue(hidden(parse('(pin_names (offset 0) hide)')))
        self.assertTrue(hidden(parse('(property "Intersheetrefs" "${INTERSHEET_REFS}" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))')))
        self.assertTrue(hidden(parse('(property "Intersheetrefs" "${INTERSHEET_REFS}" (at 0 0 0) (hide yes) (effects (font (size 1 1))))')))
        self.assertFalse(hidden(parse('(pin_names (offset 1.016))')))
        self.assertFalse(hidden(parse('(property "Value" "10k" (at 0 0 0) (effects (font (size 1 1))))')))
        self.assertFalse(hidden(parse('(pin_numbers (hide no))')))
    def test_visible_pin_names(self):
        pin=lambda body: parse('(pin passive line (at 0 0 0) (length 2.54) '+body+' (number "1" (effects (font (size 1 1)))))')
        self.assertTrue(visible_name(pin('(name "FAULT" (effects (font (size 1 1))))')))
        self.assertFalse(visible_name(pin('(name "~" (effects (font (size 1 1))))')))
        self.assertFalse(visible_name(pin('(name "" (effects (font (size 1 1))))')))
        self.assertFalse(visible_name(pin('(hide yes) (name "VCC" (effects (font (size 1 1))))')))

class NativeContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli=find_cli()
        if not cls.cli: raise unittest.SkipTest('KiCad native tool missing')
        tempbase=scratch_base()/'native-geometry-tests';tempbase.mkdir(parents=True,exist_ok=True)
        cls.temp=tempfile.TemporaryDirectory(prefix='asg-native-geometry-',dir=tempbase);cls.base=Path(cls.temp.name);cls.rows={}
        for kind in ('clear','wire','overlay','offpage','pins','variable','cachevar'):
            folder=cls.base/kind;folder.mkdir();a,b=fixture(kind)
            (folder/'native.kicad_sch').write_text(dump(a)+'\n');(folder/'child.kicad_sch').write_text(dump(b)+'\n')
            (folder/'native.kicad_pro').write_text(json.dumps({'meta':{'filename':'native.kicad_pro','version':1},'text_variables':{'NAME':'NativeVariable'}}))
            before={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
            ctx=prepare_geometry_context(folder/'native.kicad_sch',None,cls.cli,folder/'context')
            after={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
            if before!=after: raise AssertionError('native tool modified original source')
            page=page_context_from_job(ctx,folder/'native.kicad_sch') if ctx['status']=='PASS' else {'gaps':ctx['gaps']}
            report=check_scene(read_scene(parse((folder/'native.kicad_sch').read_text()),page),reserved=[])
            cls.rows[kind]=(ctx,report)
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def test_clear_caption_same_literal_inside_frame_qualified(self):
        ctx,report=self.rows['clear'];self.assertEqual('PASS',report['status'],report)
        self.assertEqual(2,report['coverage']['native_sheet_fields'])
    def test_true_foreign_wire_crossing_caught(self):
        self.assertIn('wire_sheet_frame',self.rows['wire'][1]['counts'])
    def test_real_sheet_field_overlay_caught(self):
        self.assertIn('native_sheet_text_overlap',self.rows['overlay'][1]['counts'])
    def test_native_extents_off_page_caught(self):
        self.assertIn('off_page',self.rows['offpage'][1]['counts'])
    def test_outline_or_variable_unknown_not_pass(self):
        for kind in ('pins','variable'):
            self.assertEqual('INSUFFICIENT',self.rows[kind][1]['status'])
            self.assertIn('Unsupported sheet object: sheet',self.rows[kind][1]['coverage']['gaps'])
    def test_cached_or_hidden_variable_is_not_a_display_gap(self):
        ctx,report=self.rows['cachevar']
        self.assertFalse([g for g in report['coverage']['gaps'] if 'source variable' in g],report['coverage']['gaps'])
        self.assertEqual('PASS',report['status'],report)
    def test_sidecar_sha_and_original_input_drift_rejected(self):
        folder=self.base/'clear';p=folder/'context/context.json'
        child=folder/'child.kicad_sch';old=child.read_bytes();child.write_bytes(old+b'\n')
        with self.assertRaises(ValueError):page_context_from_job(self.rows['clear'][0],folder/'native.kicad_sch')
        child.write_bytes(old)
    def test_bound_native_svg_tamper_rejected(self):
        folder=self.base/'clear';p=folder/'context/context.json';svg=next((folder/'context/baseline/svg').glob('*.svg'));old=svg.read_bytes();svg.write_bytes(old+b'\n')
        with self.assertRaises(ValueError):page_context_from_job(self.rows['clear'][0],folder/'native.kicad_sch')
        svg.write_bytes(old)
    def test_geometry_cli_takes_no_serialized_context(self):
        cli=[sys.executable,str(Path(__file__).resolve().parents[1]/'scripts/check_schematic_geometry.py'),
             str(self.base/'clear/native.kicad_sch'),'--native-context',str(self.base/'clear/context/context.json')]
        self.assertEqual(2,subprocess.run(cli,capture_output=True).returncode)
    def test_live_job_derived_lists_and_gaps_cannot_be_modified(self):
        ctx=self.rows['clear'][0];page=ctx['pages']['native.kicad_sch'];original=page['texts'];page['texts']=[]
        with self.assertRaises(ValueError):page_context_from_job(ctx,self.base/'clear/native.kicad_sch')
        page['texts']=original

if __name__=='__main__': unittest.main()

class RenderReviewItemTests(unittest.TestCase):
    """Unqualified visible pin text is listed for render review; it is not a coverage gap."""
    def test_review_items_do_not_make_page_insufficient(self):
        root=f('kicad_sch',f('version',20250114),f('generator','eeschema'),f('uuid',uid('review')),f('paper','A4'),f('lib_symbols'))
        scene=read_scene(root,{'gaps':[],'review':['pin-number:x: physical pin numbers need native render review']})
        report=check_scene(scene,reserved=[])
        self.assertEqual('PASS',report['status'],report)
        self.assertEqual(['pin-number:x: physical pin numbers need native render review'],report['coverage']['render_review_items'])
        self.assertEqual([],report['coverage']['gaps'])

class ConfigurationHashTests(unittest.TestCase):
    def test_working_dir_written_by_every_kicad_launch_is_not_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'kicad_common.json'
            def h(data):
                p.write_text(json.dumps(data))
                with mock.patch.dict(os.environ,{'KICAD_CONFIG_HOME':tmp}):
                    return ngc.configuration_hashes()[str(p)]
            base=h({'system':{'working_dir':'/a','text_editor':'x'},'graphics':{'canvas_type':1}})
            self.assertEqual(base,h({'graphics':{'canvas_type':1},'system':{'text_editor':'x','working_dir':'/b'}}))
            self.assertNotEqual(base,h({'system':{'working_dir':'/a','text_editor':'x'},'graphics':{'canvas_type':2}}))

class ConcurrentConfigurationRetryTests(unittest.TestCase):
    """Another session's KiCad rewriting the renderer configuration mid-job is waited out, not reported."""
    @classmethod
    def setUpClass(cls):
        cls.cli=find_cli()
        if not cls.cli: raise unittest.SkipTest('KiCad native tool missing')
        tempbase=scratch_base()/'native-geometry-tests';tempbase.mkdir(parents=True,exist_ok=True)
        cls.temp=tempfile.TemporaryDirectory(prefix='asg-native-retry-',dir=tempbase);cls.base=Path(cls.temp.name)
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def run_with(self,hashes,name):
        folder=self.base/name;folder.mkdir();a,b=fixture('clear')
        (folder/'native.kicad_sch').write_text(dump(a)+'\n');(folder/'child.kicad_sch').write_text(dump(b)+'\n')
        (folder/'native.kicad_pro').write_text(json.dumps({'meta':{'filename':'native.kicad_pro','version':1}}))
        waits=[]
        with mock.patch.object(ngc,'configuration_hashes',side_effect=hashes),mock.patch.object(ngc.time,'sleep',side_effect=waits.append):
            ctx=prepare_geometry_context(folder/'native.kicad_sch',None,self.cli,folder/'context')
            page=page_context_from_job(ctx,folder/'native.kicad_sch') if ctx['status']=='PASS' else None
        return ctx,page,waits,folder
    def test_change_during_first_attempt_is_retried_and_recorded(self):
        calls=[0]
        def hashes():
            calls[0]+=1  # the 3rd read (after the version command) sees another session's rewrite
            return {'kicad_common.json':'old' if calls[0]<=2 else 'new'}
        ctx,page,waits,folder=self.run_with(hashes,'once')
        self.assertEqual('PASS',ctx['status'],ctx['gaps'])
        self.assertIsNotNone(page)
        self.assertEqual([30],waits)
        self.assertEqual(1,len(ctx['retries']))
        self.assertIn('renderer configuration changed during job',ctx['retries'][0]['reason'])
        self.assertEqual(['kicad_common.json'],ctx['retries'][0]['changed_files'])
        self.assertEqual(ctx['retries'],json.loads((folder/'context/context.json').read_text())['retries'])
    def test_change_between_exports_is_retried(self):
        calls=[0]
        def hashes():
            calls[0]+=1  # changes between commands, never inside one
            return {'kicad_common.json':'old' if calls[0]<=3 else 'new'}
        ctx,page,waits,_=self.run_with(hashes,'between')
        self.assertEqual('PASS',ctx['status'],ctx['gaps'])
        self.assertEqual([30],waits)
        self.assertTrue(any(r in ctx['retries'][0]['reason'] for r in ('between exports','geometry configuration changed')),ctx['retries'])
    def test_configuration_that_keeps_changing_stays_insufficient(self):
        calls=[0]
        def hashes():
            calls[0]+=1
            return {'kicad_common.json':str(calls[0])}
        ctx,page,waits,_=self.run_with(hashes,'always')
        self.assertEqual('INSUFFICIENT',ctx['status'])
        self.assertEqual([30,60,90],waits)
        self.assertEqual(3,len(ctx['retries']))
        self.assertIn('still changing after 3 retries',ctx['gaps'][-1])
