"""One-shot drawing gate runner on the recipe fixture pair."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / 'scripts'), str(HERE / 'fixtures' / 'drawing')]
from recipe_board import INTENT, draw
from schematic_layout.generate import Libraries, library_dirs
from schematic_layout.native import find_cli
from schematic_layout.sexpr import dump

RUNNER = HERE.parent / 'scripts' / 'verify_schematic.py'


class VerifySchematicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not find_cli():
            raise unittest.SkipTest('kicad-cli is not installed')
        try:
            Libraries(library_dirs()).load('Regulator_Switching:LM2596S-ADJ')
        except ValueError:
            raise unittest.SkipTest('KiCad symbol libraries are not installed')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        for name, bad in (('good', False), ('bad', True)):
            (cls.dir / name).mkdir()
            root, _ = draw(bad=bad).build('recipe_board')
            (cls.dir / name / 'recipe_board.kicad_sch').write_text(dump(root) + '\n')
        (cls.dir / 'intent.json').write_text(json.dumps(INTENT))
        cls.good = cls.run_gates('good', cls.dir / 'intent.json')
        cls.bad = cls.run_gates('bad', cls.dir / 'intent.json')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def run_gates(cls, name, intent, tag=''):
        out = cls.dir / f'run-{name}{tag}'
        r = subprocess.run([sys.executable, str(RUNNER), str(cls.dir / name / 'recipe_board.kicad_sch'),
                            '--intent', str(intent), '--out', str(out)], capture_output=True, text=True)
        summary = json.loads((out / 'summary.json').read_text())
        return r.returncode, summary

    def test_good_drawing_passes_drawing_gates(self):
        code, s = self.good
        for gate in ('intent_netlist', 'hierarchy', 'symbol_integrity', 'readability', 'geometry'):
            self.assertEqual('PASS', s['gates'][gate]['status'], gate)
        self.assertIn('schematic-review', ' '.join(s['pending']))

    def test_erc_is_reported_not_hidden(self):
        # A standalone fixture page has undriven power inputs and one-ended global labels.
        code, s = self.good
        self.assertEqual('FAIL', s['gates']['erc']['status'])
        self.assertEqual({'power_pin_not_driven': 2, 'isolated_pin_label': 3}, s['gates']['erc']['by_type'])
        self.assertEqual(('FAIL', 1), (s['status'], code))

    def test_bad_drawing_fails_readability(self):
        _, s = self.bad
        self.assertEqual('FAIL', s['gates']['readability']['status'])
        self.assertEqual('PASS', s['gates']['intent_netlist']['status'])

    def test_intent_mismatch_fails(self):
        intent = copy.deepcopy(INTENT)
        fb = next(n for n in intent['nets'] if n['name'] == 'FB')
        fb['pins'].remove('R2.1')
        intent['nets'].append({'name': 'SPLIT', 'pins': ['R2.1']})
        path = self.dir / 'wrong-intent.json'
        path.write_text(json.dumps(intent))
        _, s = self.run_gates('good', path, '-wrong')
        self.assertEqual('FAIL', s['gates']['intent_netlist']['status'])

    def test_board_intent_with_net_map_is_accepted(self):
        board = {**INTENT, 'nets': {n['name']: n['pins'] for n in INTENT['nets']}}
        board.pop('schema_version')
        path = self.dir / 'board-intent.json'
        path.write_text(json.dumps(board))
        _, s = self.run_gates('good', path, '-board')
        self.assertEqual('PASS', s['gates']['intent_netlist']['status'])

    def test_output_directory_must_be_fresh(self):
        r = subprocess.run([sys.executable, str(RUNNER), str(self.dir / 'good' / 'recipe_board.kicad_sch'),
                            '--intent', str(self.dir / 'intent.json'), '--out', str(self.dir / 'run-good')],
                           capture_output=True, text=True)
        self.assertNotEqual(0, r.returncode)
        self.assertIn('not empty', r.stderr)


if __name__ == '__main__':
    unittest.main()
