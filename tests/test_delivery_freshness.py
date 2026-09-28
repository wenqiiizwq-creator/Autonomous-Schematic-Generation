"""Evidence invalidation regressions from post-route drawing edits."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_delivery_freshness import check

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
    def test_missing_output_rejected(self):
        (self.base/'net.xml').unlink();self.assertNotEqual(self.result()['status'],'FRESH')

if __name__=='__main__':unittest.main()
