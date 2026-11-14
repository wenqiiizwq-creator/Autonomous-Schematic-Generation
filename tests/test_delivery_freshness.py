"""Evidence invalidation regressions from post-route drawing edits."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_delivery_freshness import check, evidence_sha256

class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        (self.base/'board.kicad_sch').write_text('(kicad_sch (uuid root) (sheet (property "Sheetfile" "child.kicad_sch")))')
        (self.base/'child.kicad_sch').write_text('(kicad_sch (uuid child))')
        for name in ('net.xml', 'erc.json', 'geometry.json', 'drawing.pdf'):
            (self.base/name).write_text('fixture evidence')
        sha = lambda name: hashlib.sha256((self.base/name).read_bytes()).hexdigest()
        self.m = {'schema_version': 1, 'root': 'board.kicad_sch',
                  'inputs': {n: sha(n) for n in ('board.kicad_sch','child.kicad_sch')},
                  'outputs': {n: sha(n) for n in ('net.xml','erc.json','geometry.json','drawing.pdf')},
                  'roles': {'netlist':['net.xml'],'erc':['erc.json'],'geometry':['geometry.json'],'render':['drawing.pdf']}}
        self.path = self.base/'delivery-evidence.json'
    def result(self):
        self.path.write_text(json.dumps(self.m))
        return check(self.path)
    def test_record_manifest_resolves_from_delivery_folder(self):
        sch=self.base/'设计方案';sch.mkdir();record=self.base/'record';record.mkdir()
        for n in list(self.m['inputs'])+list(self.m['outputs']):(self.base/n).rename(sch/n)
        self.m['root']='设计方案/board.kicad_sch'
        for section in ('inputs','outputs'):self.m[section]={'设计方案/'+k:v for k,v in self.m[section].items()}
        self.m['roles']={k:['设计方案/'+x for x in v] for k,v in self.m['roles'].items()}
        self.path=record/'delivery-evidence.json'
        self.assertEqual(self.result()['status'],'FRESH')
    def test_fresh_is_not_design_pass(self):
        r=self.result();self.assertEqual(r['status'],'FRESH');self.assertIn('no design acceptance',r['scope'])
    def test_postprocess_child_mutation_invalidates(self):
        (self.base/'child.kicad_sch').write_text('(kicad_sch (uuid edited))')
        self.assertNotEqual(self.result()['status'],'FRESH')
    def test_replaced_pdf_invalidates(self):
        (self.base/'drawing.pdf').write_text('different PDF')
        self.assertNotEqual(self.result()['status'],'FRESH')
    def test_missing_geometry_role_rejected(self):
        del self.m['roles']['geometry'];self.assertNotEqual(self.result()['status'],'FRESH')
    def test_omitted_child_rejected(self):
        del self.m['inputs']['child.kicad_sch'];self.assertNotEqual(self.result()['status'],'FRESH')
    def test_empty_render_role_rejected(self):
        self.m['roles']['render']=[];self.assertNotEqual(self.result()['status'],'FRESH')
    def test_path_escape_rejected(self):
        self.m['root']='../outside.kicad_sch';self.assertNotEqual(self.result()['status'],'FRESH')
    def test_local_library_omission_rejected(self):
        (self.base/'symbols').mkdir();(self.base/'symbols/Local.kicad_sym').write_text('library')
        self.assertNotEqual(self.result()['status'],'FRESH')
    def test_board_rules_in_the_shared_project_do_not_stale_the_schematic(self):
        # User 2026-11-13: schematic and board share the .kicad_pro in 设计方案/. Its board section is the board's own;
        # net classes are read by the schematic too.
        pro = self.base/'board.kicad_pro'
        pro.write_text(json.dumps({'meta': {}, 'board': {'rules': 1}, 'net_settings': {'classes': []}}))
        self.m['inputs']['board.kicad_pro'] = evidence_sha256(pro)
        self.assertEqual(self.result()['status'], 'FRESH')
        pro.write_text(json.dumps({'meta': {}, 'board': {'rules': 2, 'tracks': [0.2]}, 'net_settings': {'classes': []}}, indent=2))
        self.assertEqual(self.result()['status'], 'FRESH')
        pro.write_text(json.dumps({'meta': {}, 'board': {'rules': 2}, 'net_settings': {'classes': [{'name': 'RF50'}]}}))
        self.assertNotEqual(self.result()['status'], 'FRESH')
    def test_missing_output_rejected(self):
        (self.base/'net.xml').unlink();self.assertNotEqual(self.result()['status'],'FRESH')

if __name__=='__main__':unittest.main()
