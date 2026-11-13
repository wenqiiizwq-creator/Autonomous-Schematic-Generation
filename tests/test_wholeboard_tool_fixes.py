"""Tool issues from the whole-board baseline (ASG 128178e, 2026-11-07; runs in 评测记录/ASG/2026-11-07-wholeboard-128178e,
improvement 9 of 评测记录/ASG/2026-11-07-wholeboard-128178e/分析与改进方案.md in the 原理图设计规范 folder). One class per issue, each with the failing case it fixes."""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
import copy
import io
import json
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / 'scripts'
sys.path[:0] = [str(SCRIPTS), str(HERE), str(HERE / 'fixtures' / 'drawing')]
import audit_component_requirements  # noqa: E402
import deliver  # noqa: E402
import complete_pin_coverage  # noqa: E402
import guideline_criteria  # noqa: E402
import make_symbol  # noqa: E402
import operating_inputs  # noqa: E402
import select_guidelines  # noqa: E402
import test_deliver  # noqa: E402
from schematic_layout import component_requirements as cr  # noqa: E402
from schematic_layout.circuit_ir import expand_stacked_pins as expand, library_no_connects, stacked_groups  # noqa: E402
from schematic_layout.generate import Libraries, library_dirs  # noqa: E402
from schematic_layout.native import find_cli  # noqa: E402
from schematic_layout.part_classes import spec_text  # noqa: E402
from schematic_layout.recipes import Sheet  # noqa: E402
from schematic_layout.scene import physical_numbers, read_scene  # noqa: E402
from schematic_layout.sexpr import all_nodes, dump, parse  # noqa: E402
from schematic_layout.symbol_integrity import audit_symbols  # noqa: E402
from test_component_requirements import fixture  # noqa: E402


def kicad_libraries():
    try:
        Libraries(library_dirs()).load('Device:Crystal_GND24')
        return True
    except ValueError:
        return False


def output(fn, *args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = fn(*args)
    return code, out.getvalue(), err.getvalue()


class SelectManyValuesTests(unittest.TestCase):
    """Three boards: --circuit-type/--device-kind took one value per option, and a zsh "$TYPES" stayed one word."""

    def test_one_option_takes_several_values_and_matches_the_shared_cli(self):
        shared = output(guideline_criteria.main, ['select', '--circuit-type', 'POWER_PROTECTION', '--circuit-type', 'DC_24V',
                                                  '--device-kind', 'tvs', '--typed-only'])[1]
        self.assertTrue(shared.strip())
        for argv in (['--circuit-type', 'POWER_PROTECTION', 'DC_24V', '--device-kind', 'tvs', '--typed-only'],
                     ['--circuit-type', 'POWER_PROTECTION DC_24V', '--device-kind', 'tvs', '--typed-only'],   # zsh "$TYPES"
                     ['--circuit-type', 'POWER_PROTECTION,DC_24V', '--device-kind', 'tvs', '--typed-only']):
            with self.subTest(argv=argv):
                self.assertEqual((0, shared), output(select_guidelines.main, argv)[:2])

    def test_scope_reads_the_design_closure(self):
        with tempfile.TemporaryDirectory() as tmp:
            closure = Path(tmp) / 'design-closure.json'
            closure.write_text(json.dumps({'guideline_scope': {'baseline': 'industrial_telecom',
                                                               'circuit_types': ['POE_PD'], 'device_kinds': []}}))
            ids = lambda text: [line.split()[0] for line in text.splitlines()]
            got = output(select_guidelines.main, ['--scope', str(closure)])[1]
            expected = [r['id'] for r in guideline_criteria.select(guideline_criteria.load(),
                                                                   'industrial_telecom', ['POE_PD'], [])]
            self.assertEqual(expected, ids(got))


class DeterministicDrawingTests(unittest.TestCase):
    """Matrix #23: two exports differed with PYTHONHASHSEED. The cause was the runner's draw.py (a set sorted on one
    boolean key); ASG's own drawing must give the same sheet under any hash seed."""

    def test_recipe_sheet_is_the_same_under_different_hash_seeds(self):
        if not kicad_libraries():
            self.skipTest('KiCad symbol libraries are not installed')
        code = ('import sys, hashlib; sys.path[:0] = %r\n'
                'from recipe_board import draw\nfrom schematic_layout.sexpr import dump\n'
                'root, report = draw().build("recipe_board")\n'
                'print(hashlib.sha256((dump(root) + repr(sorted(report["readability"]["gate"].items()))).encode()).hexdigest())'
                % [str(SCRIPTS), str(HERE / 'fixtures' / 'drawing')])
        digests = {subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, check=True,
                                  env=dict(os.environ, PYTHONHASHSEED=seed)).stdout.strip() for seed in ('1', '2', '3')}
        self.assertEqual(1, len(digests), digests)


class ProjectionKeepsRatingsTests(unittest.TestCase):
    """Matrix #24: projecting 220n/16V/X7R to its contract nominal 220nF dropped voltage and dielectric."""

    def test_the_rest_of_the_value_moves_to_the_specification(self):
        comp = {'ref': 'C1', 'value': '220n/16V/X7R'}
        cr.keep_ratings(comp, '220nF')
        self.assertEqual('16V X7R', comp['fields']['Specification'])
        comp = {'ref': 'C2', 'value': '10u 50V X7R 1206', 'fields': {'Specification': '50V'}}
        cr.keep_ratings(comp, '10uF')
        self.assertEqual('50V X7R 1206', comp['fields']['Specification'])
        comp = {'ref': 'C3', 'value': '100nF'}
        cr.keep_ratings(comp, '100nF')
        self.assertNotIn('fields', comp)

    def test_project_keeps_ratings_and_stays_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            intent, record = fixture(Path(tmp))
            req = dict(copy.deepcopy(record['components'][0]['requirements'][0]), parameter='resistance', op='eq',
                       value=100, unit='ohm')
            record['components'][0]['requirements'].append(req)
            record['components'][0]['required_parameters'].append('resistance')
            intent['components'][0]['value'] = '100R/1%/0.25W/1206'
            projected = cr.project(intent, record, Path(tmp))
            comp = projected['components'][0]
            self.assertEqual('100R', comp['value'])
            for rating in ('1%', '0.25W', '1206'):
                self.assertIn(rating, spec_text(comp))
            self.assertEqual(projected, cr.project(projected, record, Path(tmp)))


class ProjectionDoesNotStaleClosureTests(unittest.TestCase):
    """PoE #15: re-running the preparation rewrote electrical-intent.json and staled the closure's intent_sha256."""

    def run_cli(self, root):
        return output(audit_component_requirements.main, [
            str(root / 'cr.json'), '--intent', str(root / 'intent.json'), '--artifact-root', str(root),
            '--project-intent', str(root / 'intent.json'), '--out', str(root / 'out.json')])

    def test_an_unchanged_projection_leaves_the_file_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            intent, record = fixture(root)
            (root / 'cr.json').write_text(json.dumps(record))
            (root / 'intent.json').write_text(json.dumps(intent))
            first = self.run_cli(root)
            self.assertIn('PROJECTED', first[2])
            projected = (root / 'intent.json').read_bytes()
            # The runner's own formatting of the same content (compact JSON) must not be rewritten either.
            (root / 'intent.json').write_text(json.dumps(json.loads(projected)))
            compact = (root / 'intent.json').read_bytes()
            again = self.run_cli(root)
            self.assertNotIn('PROJECTED', again[2])
            self.assertEqual(compact, (root / 'intent.json').read_bytes())


class RequirementNumberMatchTests(unittest.TestCase):
    """Matrix #14: a requirement writing 1 kV and 30 cm had to be quoted as 1 kV and 30 cm, not 1000 V and 0.3 m."""

    def test_values_match_by_quantity_and_unit(self):
        shown = lambda value, words: False
        for value, unit, words in [(1000, 'V', '差模 ±1 kV/2 Ω'), (1, 'kV', '共模 ±1kV'), (0.3, 'm', '每段均不超过 30 cm'),
                                   (300, 'mm', '线长 30 cm'), (30, 'cm', '30 cm'), (1.2, 'm', '0.6～1.2 m')]:
            with self.subTest(words=words, value=value, unit=unit):
                self.assertTrue(operating_inputs.written_with_unit(value, unit, words, shown))
        for value, unit, words in [(5, 'A', '5 mA'), (30, 'cm', '30 min'), (0.3, 'm', '30 mm')]:
            with self.subTest(words=words, value=value, unit=unit):
                self.assertFalse(operating_inputs.written_with_unit(value, unit, words, shown))


@unittest.skipUnless(kicad_libraries(), 'KiCad symbol libraries are not installed')
class StackedPadsTests(unittest.TestCase):
    """Calibration #9, Matrix #7: KiCad's own symbols draw same-net pads as one visible pin with hidden copies on its
    point; the design netlist must name every pad, and the drawing error now says which pads those are."""

    INTENT = {'schema_version': 1, 'design_id': 's', 'no_connect': [],
              'components': [{'ref': 'Y1', 'lib_id': 'Device:Crystal_GND24', 'value': '25MHz', 'footprint': ''},
                             {'ref': 'U1', 'lib_id': 'Regulator_Switching:TPS62130', 'value': 'TPS62130', 'footprint': ''}],
              'nets': [{'name': 'X1', 'pins': ['Y1.1']}, {'name': 'X2', 'pins': ['Y1.3']},
                       {'name': 'GND', 'pins': ['Y1.2', 'U1.6']}, {'name': 'SW', 'pins': ['U1.1']}]}

    def test_groups_cover_stacked_numbers_and_hidden_copies(self):
        libs = Libraries(library_dirs())
        self.assertEqual([('2', '4')], stacked_groups(libs.load('Device:Crystal_GND24')))
        self.assertIn(('1', '2', '3'), stacked_groups(libs.load('Regulator_Switching:TPS62130')))
        self.assertEqual([], stacked_groups(libs.load('Device:R')))

    def test_expansion_writes_each_pad_into_the_named_net(self):
        result, added = expand(self.INTENT)
        nets = {n['name']: n['pins'] for n in result['nets']}
        self.assertIn('Y1.4', nets['GND'])
        self.assertTrue({'U1.2', 'U1.3'} <= set(nets['SW']))
        self.assertIn('Y1.4 -> GND', added)
        self.assertEqual([], expand(result)[1])          # idempotent

    def test_pads_of_one_point_in_two_nets_are_rejected(self):
        intent = copy.deepcopy(self.INTENT)
        intent['nets'].append({'name': 'OTHER', 'pins': ['Y1.4']})
        with self.assertRaisesRegex(ValueError, 'one point'):
            expand(intent)

    def test_cli_lists_then_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'intent.json'
            path.write_text(json.dumps(self.INTENT))
            code, out, _ = output(complete_pin_coverage.main, [str(path)])
            self.assertEqual(0, code)
            self.assertIn('TO ADD', out)
            self.assertEqual(self.INTENT, json.loads(path.read_text()))
            output(complete_pin_coverage.main, [str(path), '--write'])
            self.assertIn('Y1.4', json.loads(path.read_text())['nets'][2]['pins'])

    def test_drawing_error_names_the_stacked_pad(self):
        intent = {'schema_version': 1, 'design_id': 's', 'no_connect': [],
                  'components': [{'ref': 'Y1', 'lib_id': 'Device:Crystal_GND24', 'value': 'x', 'footprint': ''}],
                  'nets': [{'name': 'X1', 'pins': ['Y1.1']}, {'name': 'X2', 'pins': ['Y1.3']}, {'name': 'G', 'pins': ['Y1.2']}]}
        sheet = Sheet(intent, rails={}, external=[])
        sheet.place('Y1', (101.6, 101.6))
        for pin in ('Y1.1', 'Y1.3', 'Y1.2'):
            sheet.label(pin, 'global', length=5)
        with self.assertRaisesRegex(ValueError, r"Y1\.4->G.*complete_pin_coverage"):
            sheet.build('s', draft=True)


def tps26630(nc=()):
    """TPS26630RGE wired on every pin but its library-NC pins 19-24."""
    nets = {'IN': ['U1.1', 'U1.2'], 'GND': ['U1.8', 'U1.25'], 'OUT': ['U1.17', 'U1.18']}
    for n in (3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16):
        nets['N%d' % n] = ['U1.%d' % n]
    return {'schema_version': 1, 'design_id': 'nc', 'no_connect': list(nc),
            'components': [{'ref': 'U1', 'lib_id': 'Power_Management:TPS26630RGE', 'value': 'TPS26630', 'footprint': ''}],
            'nets': [{'name': k, 'pins': v} for k, v in nets.items()]}


@unittest.skipUnless(kicad_libraries(), 'KiCad symbol libraries are not installed')
class LibraryNoConnectTests(unittest.TestCase):
    """Matrix #7 (TPS26630RGE NC 19-24): the error only said NC pins needed an assignment; nothing wrote them."""
    NC = ['U1.%d' % n for n in range(19, 25)]

    def test_error_names_the_pins_and_the_tool(self):
        sheet = Sheet(tps26630(), rails={}, external=[])
        sheet.place('U1', (127, 101.6))
        with self.assertRaisesRegex(ValueError, r"U1\.19.*U1\.24.*complete_pin_coverage"):
            sheet.build('nc', draft=True)

    def test_tool_writes_unwired_nc_pins_and_lists_wired_ones(self):
        result, added, connected = library_no_connects(tps26630())
        self.assertEqual((self.NC, self.NC, []), (result['no_connect'], added, connected))
        self.assertEqual([], library_no_connects(result)[1])
        wired = tps26630(self.NC[1:])
        wired['nets'].append({'name': 'GND2', 'pins': ['U1.19']})
        self.assertEqual(([], ['U1.19']), library_no_connects(wired)[1:])

    def test_cli_writes_and_fails_on_a_wired_nc_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'intent.json'
            path.write_text(json.dumps(tps26630()))
            self.assertEqual(0, output(complete_pin_coverage.main, [str(path), '--write'])[0])
            self.assertEqual(self.NC, json.loads(path.read_text())['no_connect'])
            wired = tps26630(self.NC[1:])
            wired['nets'].append({'name': 'GND2', 'pins': ['U1.19']})
            path.write_text(json.dumps(wired))
            code, out, _ = output(complete_pin_coverage.main, [str(path)])
            self.assertEqual(1, code)
            self.assertIn('CONNECTED_NC U1.19', out)

    def test_written_nc_pins_draw(self):
        from schematic_layout.generate import make_root
        result = library_no_connects(tps26630())[0]
        layout = {'schema_version': 1, 'paper': 'A4', 'placements': {'U1': {'at': [127, 101.6], 'rotation': 0}},
                  'defer_fields': True}
        root = make_root(result, layout, 'nc')[0]       # raised the NC error before the pins were written
        self.assertEqual(1, len([s for s in all_nodes(root, 'symbol') if s[1][1] == 'Power_Management:TPS26630RGE']))
        with self.assertRaisesRegex(ValueError, 'no_connect'):
            make_root(tps26630(), layout, 'nc')


GATE_NETS = {'A1': 'U1.1', 'Y1': 'U1.7', 'A2': 'U1.6', 'Y2': 'U1.2', 'A3': 'U1.3', 'Y3': 'U1.5', 'GND': 'U1.4', '+3V3': 'U1.8'}


def gate_intent(**extra):
    return {'schema_version': 1, 'design_id': 'mu', 'no_connect': [],
            'components': [dict({'ref': 'U1', 'lib_id': '74xGxx:74LVC3G17', 'value': '74LVC3G17', 'footprint': ''}, **extra)],
            'nets': [{'name': n, 'pins': [p]} for n, p in GATE_NETS.items()]}


@unittest.skipUnless(kicad_libraries(), 'KiCad symbol libraries are not installed')
class MultiUnitTests(unittest.TestCase):
    """Matrix #7: 74LVC3G17 is a multi-unit symbol and recipes only drew single-unit parts."""

    def sheet(self, intent=None):
        return Sheet(intent or gate_intent(), rails={'GND': 'power:GND', '+3V3': 'power:+3V3'},
                     external=[n for n in GATE_NETS if n not in ('GND', '+3V3')])

    def draw(self, sheet):
        for unit, y in ((1, 50.8), (2, 76.2), (3, 101.6)):
            sheet.place('U1', (101.6, y), unit=unit)
        self.assertEqual('U1:4', sheet.place('U1', (160.02, 76.2), pin='8'))     # the supply unit, implied by its pin
        for pid, net in sheet.nets.items():
            sheet.power(pid) if net in sheet.rails else sheet.label(pid, 'global', length=4)
        return sheet.build('mu')

    def test_every_unit_is_placed_and_drawn(self):
        sheet = self.sheet()
        self.assertEqual([1, 2, 3, 4], sheet.units('U1'))
        self.assertEqual(2, sheet.unit_of('U1', '6'))
        root, report = self.draw(sheet)
        self.assertEqual('PASS', report['readability']['gate']['status'])
        units = sorted(int(next(n for n in s if isinstance(n, list) and n[0] == 'unit')[1]) for s in all_nodes(root, 'symbol')
                       if any(isinstance(n, list) and n[0] == 'lib_id' and n[1] == '74xGxx:74LVC3G17' for n in s))
        self.assertEqual([1, 2, 3, 4], units)
        cli = find_cli()
        if cli is None:
            self.skipTest('kicad-cli not installed: native netlist not checked')
        from schematic_layout.native import compare_netlist
        with tempfile.TemporaryDirectory() as tmp:
            sch, xml = Path(tmp) / 'mu.kicad_sch', Path(tmp) / 'mu.xml'
            sch.write_text(dump(root) + '\n')
            subprocess.run([cli, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(xml), str(sch)],
                           check=True, capture_output=True)
            result = compare_netlist(xml, gate_intent(units=[1, 2, 3, 4]), report['layout'])
            self.assertEqual('PASS', result['status'], result['errors'])
            self.assertEqual('PASS', audit_symbols(sch, xml)['status'])

    def test_unit_is_required_and_every_unit_must_be_placed(self):
        sheet = self.sheet()
        with self.assertRaisesRegex(ValueError, 'unit='):
            sheet.place('U1', (101.6, 50.8))
        sheet.place('U1', (101.6, 50.8), unit=1)
        with self.assertRaisesRegex(ValueError, 'already placed'):
            sheet.place('U1', (101.6, 76.2), unit=1)
        with self.assertRaisesRegex(ValueError, r"Unplaced parts: \['U1:2', 'U1:3', 'U1:4'\]"):
            sheet.build('mu')

    def test_declared_units_must_match_the_library(self):
        with self.assertRaisesRegex(ValueError, 'do not match'):
            self.sheet(gate_intent(units=[1, 2]))


PINS = {'name': 'DEMO_PHY', 'reference': 'U', 'pins': [
    {'number': '1', 'name': 'VDDIO', 'type': 'PWR'}, {'number': '2', 'name': 'VDDIO', 'type': 'PWR'},
    {'number': '3', 'name': 'AVDD33', 'type': 'PWR'}, {'number': '4', 'name': 'GND', 'type': 'GND'},
    {'number': '5', 'name': 'GND', 'type': 'GND'}, {'number': '6', 'name': 'EPAD', 'type': 'GND'},
    {'number': '7', 'name': 'RXD0/PHYAD0', 'type': 'O'}, {'number': '8', 'name': 'RXD1/PHYAD1', 'type': 'O'},
    {'number': '9', 'name': 'CRS_DV/MODE2', 'type': 'IO'}, {'number': '10', 'name': 'MDIO', 'type': 'IO'},
    {'number': '11', 'name': 'MDC', 'type': 'I'}, {'number': '12', 'name': 'nINT/REFCLKO', 'type': 'OD'},
    {'number': '13', 'name': 'TXP', 'type': 'A', 'side': 'R'}, {'number': '14', 'name': 'TXN', 'type': 'A', 'side': 'R'},
    {'number': '15', 'name': 'NC', 'type': 'NC'}, {'number': '16', 'name': 'NC', 'type': 'NC'},
    {'number': '17', 'name': 'VOUT_1V2', 'type': 'PWR_OUT', 'side': 'R'},
    {'number': '18', 'name': 'VOUT_1V2', 'type': 'PWR_OUT', 'side': 'R'}]}


def place_symbol(folder, library, name):
    """A page with the symbol alone and a KiCad-style XML naming each of its pads."""
    sym = next(s for s in all_nodes(parse(library.read_text()), 'symbol') if s[1] == name)
    sym[1] = 'Demo:' + name
    root = folder / 'board.kicad_sch'
    root.write_text(dump(parse(f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid "root") (paper "A3")
      (lib_symbols {dump(sym)})
      (symbol (lib_id "Demo:{name}") (at 152.4 152.4 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "u1")
        (property "Reference" "U1" (at 152.4 60 0)) (property "Value" "{name}" (at 152.4 250 0))
        (instances (project "board" (path "/root" (reference "U1") (unit 1))))))''')) + '\n')
    pads = [n for sub in all_nodes(sym, 'symbol') for p in all_nodes(sub, 'pin') for n in physical_numbers(str(p[-1][1]))]
    xml = folder / 'native.xml'
    xml.write_text('<export><components><comp ref="U1"><value>%s</value></comp></components><nets>%s</nets></export>' % (
        name, ''.join(f'<net name="N{n}"><node ref="U1" pin="{n}"/></net>' for n in pads)))
    return root, xml, pads


class SymbolFromPinTableTests(unittest.TestCase):
    """Calibration #9 and PoE: no script made a symbol from a datasheet pin table; Matrix #20: top/bottom pin names
    crossed the side pin names at the corners."""

    def make(self, folder, spec=PINS, fmt='json'):
        source = folder / ('pins.' + fmt)
        if fmt == 'json':
            source.write_text(json.dumps(spec))
        else:
            source.write_text('number,name,type,side\n' + ''.join(
                '%s,%s,%s,%s\n' % (p['number'], p['name'], p['type'], p.get('side', '')) for p in spec['pins']))
        out = folder / 'Demo.kicad_sym'
        args = [str(source), '--out', str(out)] + (['--name', spec['name']] if fmt == 'csv' else [])
        self.assertEqual(0, output(make_symbol.main, args)[0])
        return out

    def test_pins_stack_supplies_only_and_keep_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.make(Path(tmp), fmt='csv')
            sym = next(s for s in all_nodes(parse(out.read_text()), 'symbol') if s[1] == 'DEMO_PHY')
            pins = {str(p[-1][1]): str(p[1]) for sub in all_nodes(sym, 'symbol') for p in all_nodes(sub, 'pin')}
            self.assertEqual('power_in', pins['[1,2]'])
            self.assertEqual(('power_in', 'power_in'), (pins['[4,5]'], pins['6']))    # EPAD has its own name
            self.assertEqual('power_out', pins['[17,18]'])
            self.assertEqual(('no_connect', 'no_connect'), (pins['15'], pins['16']))     # NC never stacks
            self.assertEqual('open_collector', pins['12'])
            on_grid = [p for sub in all_nodes(sym, 'symbol') for p in all_nodes(sub, 'pin')]
            for pin in on_grid:
                at = next(n for n in pin if isinstance(n, list) and n[0] == 'at')
                self.assertTrue(all(abs(float(v) / 2.54 - round(float(v) / 2.54)) < 1e-6 for v in at[1:3]), at)

    def test_rewriting_replaces_the_symbol_and_keeps_others(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.make(folder)
            other = dict(PINS, name='OTHER')
            self.make(folder, other)
            self.make(folder)
            names = [s[1] for s in all_nodes(parse((folder / 'Demo.kicad_sym').read_text()), 'symbol')]
            self.assertEqual(['DEMO_PHY', 'OTHER'], names)

    def test_bad_rows_are_rejected(self):
        for pins, message in [([{'number': '1', 'name': 'A', 'type': 'Q'}], 'neither'),
                              ([{'number': '1', 'name': 'A', 'type': 'I'}, {'number': '1', 'name': 'B', 'type': 'I'}], 'twice'),
                              ([{'number': '1', 'name': 'A', 'type': 'I', 'side': 'X'}], 'L/R/T/B')]:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                make_symbol.symbol({'name': 'X', 'pins': pins})

    def test_generated_symbol_passes_integrity_and_native_pin_text(self):
        cli = find_cli()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, xml, pads = place_symbol(folder, self.make(folder), 'DEMO_PHY')
            self.assertEqual(sorted(str(n) for n in range(1, 19)), sorted(pads))
            report = audit_symbols(root, xml)
            self.assertEqual('PASS', report['status'], report['errors'] + report['coverage_gaps'])
            if cli is None:
                self.skipTest('kicad-cli not installed: native pin-name geometry not checked')
            from schematic_layout.native_geometry_context import page_context_from_job, prepare_geometry_context
            from schematic_layout.qa import check_scene
            context = prepare_geometry_context(root, None, cli, folder / 'context')
            self.assertEqual('PASS', context['status'], context['gaps'])
            found = check_scene(read_scene(parse(root.read_text()), page_context_from_job(context, root)))
            self.assertEqual(15, found['coverage']['native_pin_names'])
            self.assertEqual([], [f for f in found['findings'] if f['code'].startswith('native_pin')])


class OnePassDeliveryTests(unittest.TestCase):
    """Calibration board: delivery took two full runs (review needs the PDF, the report needs the review); Matrix #25:
    the reminder about datasheets to file made a packed delivery exit 1."""
    setUp = test_deliver.DeliverTests.setUp
    write_config = test_deliver.DeliverTests.write_config
    run_deliver = test_deliver.DeliverTests.run_deliver

    def test_a_review_of_the_same_pdf_delivers_in_one_run(self):
        code, steps, failure = self.run_deliver()
        self.assertEqual((0, None, '打包'), (code, failure, steps[-1]['step']))

    def test_without_a_matching_review_the_run_stops_at_the_review(self):
        for review in (None, {'status': 'REVIEW_PENDING'}, {'status': 'REVIEWED', 'pdf_sha256': '0' * 64}):
            with self.subTest(review=review):
                path = self.root / 'record' / 'visual-review.json'
                path.unlink(missing_ok=True)
                (self.root / '设计报告.md').unlink(missing_ok=True)
                if review:
                    path.write_text(json.dumps(review))
                code, steps, failure = self.run_deliver()
                self.assertEqual((2, None), (code, failure))
                self.assertEqual(('自动检查', '图面审阅'), (steps[-2]['step'], steps[-1]['step']))
                self.assertFalse((self.root / '设计报告.md').exists())

    def test_datasheets_to_file_do_not_fail_a_packed_delivery(self):
        stub = self.stubs / 'pack_design.py'
        stub.write_text(stub.read_text().replace("elif name == 'pack_design':\n",
                                                 "elif name == 'pack_design':\n    print('TO_FILE: 设计资料/datasheets/x.pdf')\n"))
        code, steps, failure = self.run_deliver()
        self.assertEqual((0, None), (code, failure))
        self.assertEqual({'step': '手册待入库', 'status': '1 份'}, steps[-1])


if __name__ == '__main__':
    unittest.main()
