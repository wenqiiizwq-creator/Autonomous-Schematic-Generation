"""find_parts.py searches the HardwareWiki raw library: catalog rows, unindexed PDFs, design examples."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
import find_parts

CLI = HERE.parent / 'scripts' / 'find_parts.py'


def make_wiki(tmp):
    wiki = Path(tmp) / 'HardwareWiki'
    ds = wiki / 'raw' / 'Datasheet'
    rows = [
        {'path': '08_电源管理/USB PD 控制器/Richtek - RT7209.pdf', 'vendor': 'Richtek', 'model': 'RT7209',
         'category': '08_电源管理', 'subcategory': 'USB PD 控制器', 'kind': '器件资料', 'facets': ['电源转换'],
         'aliases': 'RT7209GQW', 'pages': 30, 'first_page': 'USB PD 3.1 PPS controller with optocoupler drive'},
        {'path': '08_电源管理/AC-DC 转换器/onsemi - NCP1343.pdf', 'vendor': 'onsemi', 'model': 'NCP1343',
         'category': '08_电源管理', 'subcategory': 'AC-DC 转换器', 'kind': '器件资料', 'facets': ['电源转换', '隔离'],
         'aliases': '', 'pages': 40, 'first_page': 'Quasi-resonant flyback controller'}]
    for r in rows:
        p = ds / r['path']
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'%PDF')
    (ds / 'catalog.json').write_text(json.dumps({'generated': '2026-10-19', 'count': 2, 'rows': rows}), encoding='utf-8')
    extra = ds / '09_功率半导体' / 'MOSFET' / 'Infineon - IPA60R180P7.pdf'
    extra.parent.mkdir(parents=True)
    extra.write_bytes(b'%PDF')
    board = wiki / 'raw' / 'Designexample' / 'USB-PD' / 'NCP1343PD100WGEVB'
    board.mkdir(parents=True)
    (board / 'onsemi - NCP1343PD100WGEVB - 100 W PD charger.pdf').write_bytes(b'%PDF')
    note = wiki / 'raw' / 'Applicationnote' / 'TI - SLVA123 - Type-C sink design.pdf'
    note.parent.mkdir(parents=True)
    note.write_bytes(b'%PDF')
    return wiki


class FindPartsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.wiki = make_wiki(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_terms_match_any_indexed_field_and_ignore_case_and_hyphens(self):
        r = find_parts.search_datasheets(self.wiki, ['usb-pd'])
        self.assertEqual(['RT7209'], [x['model'] for x in r['results']])
        self.assertEqual('raw/Datasheet/08_电源管理/USB PD 控制器/Richtek - RT7209.pdf', r['results'][0]['path'])
        self.assertEqual(0, find_parts.search_datasheets(self.wiki, ['PPS'])['total'])       # body text is opt-in
        self.assertEqual(1, find_parts.search_datasheets(self.wiki, ['PPS'], with_text=True)['total'])
        self.assertEqual(1, find_parts.search_datasheets(self.wiki, ['电源转换'], category='AC-DC')['total'])

    def test_mpn_matches_model_or_alias(self):
        self.assertEqual(1, find_parts.search_datasheets(self.wiki, [], mpn='rt7209gqw')['total'])
        self.assertEqual(0, find_parts.search_datasheets(self.wiki, [], mpn='NCP1623')['total'])

    def test_pdf_missing_from_catalog_is_listed_as_unindexed(self):
        r = find_parts.search_datasheets(self.wiki, ['MOSFET'])
        self.assertEqual([('IPA60R180P7', '未入索引', 'Infineon')],
                         [(x['model'], x['kind'], x['vendor']) for x in r['results']])

    def test_missing_catalog_is_reported_not_fatal(self):
        (self.wiki / 'raw' / 'Datasheet' / 'catalog.json').unlink()
        r = find_parts.search_datasheets(self.wiki, ['NCP1343'])
        self.assertIn('catalog.json not found', r['catalog_problem'])
        self.assertEqual(1, r['total'])

    def test_designs_and_notes_by_path(self):
        r = find_parts.search_paths(self.wiki, 'Designexample', ['pd', '100w'])
        self.assertEqual(['raw/Designexample/USB-PD/NCP1343PD100WGEVB'], r['folders'])
        self.assertEqual(0, find_parts.search_paths(self.wiki, 'Designexample', ['flyback'])['total'])
        self.assertEqual(1, find_parts.search_paths(self.wiki, 'Applicationnote', ['type-c'])['total'])

    def test_categories_and_cli(self):
        cats = find_parts.categories(self.wiki)['categories']
        self.assertEqual({'USB PD 控制器': 1, 'AC-DC 转换器': 1}, cats['08_电源管理'])
        r = subprocess.run([sys.executable, str(CLI), '--wiki', str(self.wiki), '--category', 'USB PD'],
                           capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual(1, json.loads(r.stdout)['total'])
        r = subprocess.run([sys.executable, str(CLI), '--wiki', str(self.wiki)], capture_output=True, text=True)
        self.assertEqual(2, r.returncode)

    def test_locate_file_by_hash_then_by_name(self):
        ds = self.wiki / 'raw' / 'Datasheet'
        rows = json.loads((ds / 'catalog.json').read_text())['rows']
        rows[0]['sha256'] = find_parts.sha256(ds / rows[0]['path'])
        (ds / 'catalog.json').write_text(json.dumps({'rows': rows}))
        with tempfile.TemporaryDirectory() as tmp:
            same = Path(tmp) / 'renamed.pdf'
            same.write_bytes((ds / rows[0]['path']).read_bytes())
            self.assertEqual('raw/Datasheet/' + rows[0]['path'], find_parts.locate_file(self.wiki, same))
            by_name = Path(tmp) / 'infineon-IPA60R180P7.pdf'
            by_name.write_bytes(b'%PDF-other')
            self.assertEqual('raw/Datasheet/09_功率半导体/MOSFET/Infineon - IPA60R180P7.pdf', find_parts.locate_file(self.wiki, by_name))
            renamed_in_library = Path(tmp) / 'onsemi-NCP1343-old-name.pdf'       # same bytes, stale catalog, other name
            renamed_in_library.write_bytes((ds / rows[1]['path']).read_bytes() + b'')
            (ds / rows[1]['path']).write_bytes(b'%PDF-ncp1343-unique')
            renamed_in_library.write_bytes(b'%PDF-ncp1343-unique')
            self.assertEqual('raw/Datasheet/' + rows[1]['path'], find_parts.locate_file(self.wiki, renamed_in_library))
            other = Path(tmp) / 'TI - TPS1234.pdf'
            other.write_bytes(b'%PDF-x')
            self.assertIsNone(find_parts.locate_file(self.wiki, other))
            r = subprocess.run([sys.executable, str(CLI), '--wiki', str(self.wiki), '--file', str(other)], capture_output=True, text=True)
            self.assertEqual(1, r.returncode)

    def test_patterns_are_searchable_and_each_approach_has_sources_and_pitfalls(self):
        r = find_parts.search_circuits(['反激'])
        self.assertIn('qr-flyback', [x['id'] for x in r['results']])
        self.assertEqual(0, find_parts.search_circuits(['不存在的功能'])['total'])
        index = find_parts.circuit_index()
        self.assertGreaterEqual(len(index), 16)
        self.assertNotIn('README', index)
        # knowledge package format (references/knowledge/典型电路/README.md): only the ### headings under 「## 实现方案」
        # are approaches; sources are 「## 来源清单」 numbers (S1 p4). The pointer entry has no approach.
        self.assertEqual(['反馈丢失，输出升高', '使能脚悬空'],
                         [h for h in ('反馈丢失，输出升高', '使能脚悬空') if h not in index['power-rail-test-break']['implementations']])
        for pid, info in index.items():
            self.assertTrue(info['title'] and info['function'], pid)
            if not info['implementations']:
                self.assertEqual('reviewed-bias-and-latch', pid)
                continue
            body = (find_parts.CIRCUITS_DIR.parents[2] / info['file']).read_text(encoding='utf-8')
            self.assertIn('\n## 来源清单\n', body, pid)
            section_text = body.split('\n## 实现方案\n', 1)[1].split('\n## ', 1)[0]
            for section in section_text.split('\n### ')[1:]:
                if '所有方案' in section.splitlines()[0]:   # a note common to every approach
                    continue
                self.assertIn('**适用范围**', section, '%s: %s' % (pid, section[:40]))
                self.assertRegex(section, r'来源\*\*：[\s\S]*S\d+', '%s: %s' % (pid, section[:40]))

    def test_roles_table_covers_library_subcategories(self):
        r = find_parts.roles_coverage(self.wiki)
        self.assertEqual('PASS', r['status'], r)
        extra = self.wiki / 'raw' / 'Datasheet' / 'catalog.json'
        data = json.loads(extra.read_text())
        data['rows'].append(dict(data['rows'][0], path='08_电源管理/新子类/X - Y.pdf', subcategory='新子类'))
        extra.write_text(json.dumps(data))
        r = find_parts.roles_coverage(self.wiki)
        self.assertEqual(('FAIL', ['新子类']), (r['status'], r['missing_in_table']))
        r = subprocess.run([sys.executable, str(CLI), '--wiki', str(self.wiki), '--roles-coverage'],
                           capture_output=True, text=True)
        self.assertEqual(1, r.returncode)

    def test_archived_versions_are_neither_candidates_nor_a_subcategory(self):
        path = self.wiki / 'raw' / 'Datasheet' / 'catalog.json'
        data = json.loads(path.read_text())
        old = '08_电源管理/versions/abc123/Richtek - RT7209.pdf'
        (path.parent / old).parent.mkdir(parents=True)
        (path.parent / old).write_bytes(b'%PDF')
        data['rows'].append(dict(data['rows'][0], path=old, subcategory='versions'))
        path.write_text(json.dumps(data))
        r = find_parts.search_datasheets(self.wiki, [], mpn='RT7209')
        self.assertEqual(['raw/Datasheet/08_电源管理/USB PD 控制器/Richtek - RT7209.pdf'], [x['path'] for x in r['results']])
        self.assertNotIn('versions', find_parts.categories(self.wiki)['categories']['08_电源管理'])

    def test_roles_table_matches_the_real_library_when_present(self):
        if not (find_parts.DEFAULT_WIKI / 'raw' / 'Datasheet' / 'catalog.json').is_file():
            raise unittest.SkipTest('HardwareWiki library is not on this machine')
        r = find_parts.roles_coverage(find_parts.DEFAULT_WIKI)
        self.assertEqual([], r['missing_in_table'], r)


if __name__ == '__main__':
    unittest.main()
