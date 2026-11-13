"""Hierarchical root with the System_block cover: named, attached flow lines; rewritten instance paths; native pass."""
from framework_guard import skip_without_framework  # noqa: E402
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
from schematic_layout.native import find_cli
from schematic_layout.pages import page_intents
from schematic_layout.recipes import LEFT, RIGHT, UP, DOWN, Sheet, add
from schematic_layout.root import Root
from schematic_layout.project_audit import audit_project
from schematic_layout.qa import check_scene
from schematic_layout.scene import read_scene
from schematic_layout.sexpr import all_nodes, first, parse

VERIFY = HERE.parent / 'scripts' / 'verify_schematic.py'


def part(ref, lib, page):
    return {'ref': ref, 'lib_id': lib, 'value': ref, 'footprint': '', 'fields': {'Circuit': page}}


# Connector-fed input with a series resistor, then an LDO page; VIN_F crosses pages.
BOARD = {
    'schema_version': 1,
    'components': [part('J1', 'Connector_Generic:Conn_01x02', '01_in'), part('R1', 'Device:R', '01_in'),
                   part('U1', 'Regulator_Linear:AMS1117-3.3', '02_ldo'), part('C1', 'Device:C', '02_ldo')],
    'nets': {'VIN': ['J1.1', 'R1.1'], 'VIN_F': ['R1.2', 'U1.3', 'C1.1'], 'GND': ['J1.2', 'U1.1', 'C1.2'],
             '+3V3': ['U1.2']},
    'no_connect': [],
    'external_supply': [{'net': 'VIN', 'pin': 'J1.1', 'reason': 'test'}, {'net': 'GND', 'pin': 'J1.2', 'reason': 'test'}],
    'filtered_supply': [{'net': 'VIN_F', 'from': 'VIN', 'via': 'R1', 'reason': 'test'}],
}
RAILS = {'GND': 'power:GND', '+3V3': 'power:+3V3'}


def pages():
    p = page_intents(BOARD, rails=RAILS)
    s = Sheet(p['01_in']['intent'], rails=p['01_in']['rails'], external=p['01_in']['external'], power_ref_start=101)
    s.place('J1', (50.8, 76.2), rotation=0, mirror='y')
    g = s.stub('J1.2', 3)
    f = s.wire(g, add(g, DOWN, 7))
    s.power(s.wire(f, add(f, DOWN, 2)))
    s.power_flag(s.wire(f, add(f, RIGHT, 6)))
    a = s.stub('J1.1', 3)
    s.series(a, ['R1'], RIGHT, gap=max(3, s.name_run_steps('VIN')))
    s.name('VIN')
    s.power_flag(s.wire(a, add(a, UP, 2)))
    m = s.stub('R1.2', 3)
    s.label(s.wire(m, add(m, RIGHT, 2)), outward=RIGHT)
    s.power_flag(s.wire(m, add(m, UP, 2)))
    first_page = s.build('01_in')[0]
    s = Sheet(p['02_ldo']['intent'], rails=p['02_ldo']['rails'], external=p['02_ldo']['external'], power_ref_start=201)
    s.place('U1', (101.6, 76.2))
    s.power('U1.1')
    s.power('U1.2')
    s.label(s.bank('U1.3', ['C1'], LEFT), outward=LEFT)
    return first_page, s.build('02_ldo')[0]


def root(built, label_at=(107.95, 62.23)):
    r = Root('tiny', date='2026-10-23', rev='T1')
    r.page('01_in', built[0], (25.4, 50.8), note='输入 / 限流')
    r.page('02_ldo', built[1], (127.0, 50.8), note='LDO 3.3V')
    r.flow('VIN_F', '01_in', '02_ldo', label_at=label_at)
    r.isolation(x=114.3)
    return r


class RootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.built = pages()
        except ValueError as e:
            if 'Missing symbol' in str(e):
                raise unittest.SkipTest('KiCad symbol libraries are not installed')
            raise

    def test_cover_and_instance_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = root(self.built).write(Path(tmp) / 'p')
            self.assertEqual('PASS', result['system_block']['status'], result)
            cover = parse(result['root'].read_text(encoding='utf-8'))
            ru = first(cover, 'uuid')[1]
            self.assertEqual('System_block', first(first(cover, 'title_block'), 'title')[1])
            sheets = {next(p[2] for p in all_nodes(s, 'property') if p[1] == 'Sheetname'): first(s, 'uuid')[1]
                      for s in all_nodes(cover, 'sheet')}
            self.assertEqual(['01_in', '02_ldo'], sorted(sheets))
            child = parse((Path(tmp) / 'p' / '02_ldo.kicad_sch').read_text(encoding='utf-8'))
            for symbol in all_nodes(child, 'symbol'):
                project = first(first(symbol, 'instances'), 'project')
                self.assertEqual('tiny', project[1])
                self.assertEqual('/' + ru + '/' + sheets['02_ldo'], first(project, 'path')[1])
            for name in ('tiny.kicad_pro', '01_in.kicad_sch'):
                self.assertTrue((Path(tmp) / 'p' / name).is_file())

    def test_flow_needs_a_shared_band_or_via(self):
        r = Root('t')
        r.page('A', self.built[0], (25.4, 50.8))
        r.page('B', self.built[1], (127.0, 139.7))
        with self.assertRaisesRegex(ValueError, 'share no row or column'):
            r.flow('X', 'A', 'B')
        r.flow('X', 'A', 'B', via=[(63.5, 101.6), (165.1, 101.6)])
        kind, label, points, *_ = r.items[-1]
        self.assertEqual([(63.5, 81.28), (63.5, 101.6), (165.1, 101.6), (165.1, 139.7)], points)
        with self.assertRaisesRegex(ValueError, 'neither horizontal nor vertical'):
            r.flow('Y', 'A', 'B', via=[(63.5, 101.6), (165.1, 110.49)])

    def test_isolation_label_must_read_as_a_boundary(self):
        r = Root('t')
        r.page('A', self.built[0], (25.4, 50.8))
        with self.assertRaisesRegex(ValueError, 'must start with'):
            r.isolation(x=114.3, label='隔离电源')
        r.isolation(x=114.3, label='隔离 1500 Vrms')

    def test_label_on_another_line_and_bad_layout_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            # The geometry gate on the written cover reports the label sitting on the boundary.
            written = root(self.built, label_at=None).write(Path(tmp) / 'p')
            cover = check_scene(read_scene(parse(Path(written['root']).read_text())))
            self.assertIn('graphic_text', cover['counts'], cover)
        r = Root('t')
        r.page('A', self.built[0], (25.4, 50.8))
        with self.assertRaisesRegex(ValueError, 'closer than'):
            r.page('B', self.built[1], (101.6, 50.8))
        r.page('B', self.built[1], (127.0, 50.8))
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'no flow line reaches'):
                r.write(Path(tmp) / 'p')

    @skip_without_framework
    def test_native_project_passes_every_gate(self):
        cli = find_cli()
        if not cli:
            self.skipTest('kicad-cli is not installed')
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            result = root(self.built).write(tmp / 'p')
            (tmp / 'board.json').write_text(json.dumps(BOARD), encoding='utf-8')
            run = subprocess.run([sys.executable, str(VERIFY), str(result['root']), '--intent', str(tmp / 'board.json'),
                                  '--out', str(tmp / 'v'), '--expected-pages', '3', '--cli', cli],
                                 capture_output=True, text=True)
            summary = json.loads((tmp / 'v' / 'summary.json').read_text(encoding='utf-8'))
            self.assertEqual('AUTOMATED_PASS', summary['status'], run.stdout + run.stderr)
            self.assertEqual([], summary['gates']['erc']['ignored_rules'])   # the written project turns the rules on

    def test_kicad_10_saved_project_keeps_its_annotations(self):
        cli = find_cli()
        if not cli:
            self.skipTest('kicad-cli is not installed')
        with tempfile.TemporaryDirectory() as tmp:
            result = root(self.built).write(Path(tmp) / 'p')
            for sheet in sorted((Path(tmp) / 'p').glob('*.kicad_sch')):
                subprocess.run([cli, 'sch', 'upgrade', '--force', str(sheet)], capture_output=True, check=True)
            text = result['root'].read_text(encoding='utf-8')
            if '(version 20260306)' not in text:
                self.skipTest('this kicad-cli does not save format 20260306')
            audit = audit_project(result['root'])
            self.assertEqual('PASS', audit['status'], audit)
            self.assertFalse([g for g in audit['coverage_gaps'] if 'unsupported native annotation version' in g])
            self.assertEqual(3, audit['page_count'])


if __name__ == '__main__':
    unittest.main()
