"""Drawing recipes, local-name policy and the mandatory readability gate."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / 'scripts'), str(HERE / 'fixtures' / 'drawing')]
from recipe_board import EXTERNAL, INTENT, RAILS, draw
from schematic_layout.generate import Libraries, library_dirs
from schematic_layout.native import compare_netlist, find_cli
from schematic_layout.qa import check_scene
from schematic_layout.recipes import DOWN, RIGHT, UP, Sheet, add, select_local_names
from schematic_layout.scene import read_scene
from schematic_layout.sexpr import all_nodes, dump, first, parse

CLI = HERE.parent / 'scripts' / 'check_schematic_readability.py'


def pins(root):
    return {p.id: p for s in read_scene(root).symbols for p in s.pins}


class RecipeBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            Libraries(library_dirs()).load('Regulator_Switching:LM2596S-ADJ')
        except ValueError:
            raise unittest.SkipTest('KiCad symbol libraries are not installed')
        cls.good, cls.report = draw().build('recipe_board')
        cls.bad, cls.bad_report = draw(bad=True).build('recipe_board')
        cls.pins = pins(parse(dump(cls.good)))

    def test_build_is_deterministic(self):
        again, _ = draw().build('recipe_board')
        self.assertEqual(dump(self.good), dump(again))

    def test_good_drawing_passes_the_gate(self):
        r = self.report['readability']
        self.assertEqual('PASS', r['gate']['status'], r)
        self.assertEqual([], self.report['crossings'])
        self.assertEqual([], r['tortuous'])

    def test_bad_drawing_fails_with_locations(self):
        r = self.bad_report['readability']
        self.assertEqual('FAIL', r['gate']['status'])
        self.assertEqual(['+5V', 'FB'], self.bad_report['crossings'][0]['nets'])
        self.assertEqual([['D3.2', 'R3.2']], r['tortuous'])

    def test_series_chain_is_collinear_and_in_order(self):
        y = self.pins['J1.1'].point[1]
        xs = [self.pins[p].point[0] for p in ('J1.1', 'F1.1', 'F1.2', 'D1.2', 'D1.1')]
        self.assertTrue(all(self.pins[p].point[1] == y for p in ('F1.1', 'F1.2', 'D1.2', 'D1.1')))
        self.assertEqual(sorted(xs), xs)

    def test_bank_shares_a_straight_return(self):
        c3, c4 = self.pins['C3.2'].point, self.pins['C4.2'].point
        self.assertEqual(self.pins['C3.1'].point[1], self.pins['C4.1'].point[1])
        self.assertLess(c3[0], c4[0])
        decision = next(d for d in self.report['decisions'] if d['recipe'] == 'bank' and d['parts'] == ['C3', 'C4'])
        self.assertTrue(decision['common_return'])

    def test_repeated_lanes_use_the_same_arrangement(self):
        for a, b in (('R5', 'R4'), ('D5', 'D4')):
            self.assertEqual(self.pins[f'{a}.1'].point[0], self.pins[f'{b}.1'].point[0])

    def test_rails_are_power_symbols_named_by_net(self):
        self.assertEqual(['+3V3', '+5V', 'GND'], self.report['rails'])
        self.assertEqual(0, len([n for n in self.report['layout']['nets'] if n == 'GND' and
                                 self.report['layout']['nets'][n].get('label')]))

    def test_label_policy(self):
        labels = self.report['labels']
        self.assertEqual(['MCU_DN', 'MCU_DP', 'USB_VBUS'], labels['global'])
        self.assertEqual(['FB', 'SW', 'USB_DN', 'USB_DP', 'VIN'], labels['local'])
        small = [n for n in self.good if isinstance(n, list) and n and n[0] == 'label']
        self.assertTrue(all(float(n[3][1][1][1]) == 1.0 for n in small))
        # Unselected local nets stay unnamed.
        self.assertNotIn('LED_A', labels['local'])
        self.assertNotIn('VIN_F', labels['local'])

    def test_default_local_name_selection(self):
        names = select_local_names(INTENT, external=['MCU_DP', 'MCU_DN', 'USB_VBUS'], rails=['GND', '+5V', '+3V3'])
        self.assertEqual(['FB', 'SW', 'USB_DN', 'USB_DP', 'VIN'], names)

    def test_geometry_qa_has_no_errors(self):
        # Device:LED arrows reach past its cathode tip; the cathode's own exit
        # wire is not a body traversal.
        report = check_scene(read_scene(parse(dump(self.good))), reserved=[])
        self.assertEqual([], [f for f in report['findings'] if f['severity'] == 'error'])

    def test_qa_still_flags_a_foreign_wire_through_the_overhang(self):
        root = parse(dump(self.good))
        led = next(x for x in read_scene(root).symbols if x.ref == 'D3')
        x = round(led.body.center[0], 2)
        root.append(['wire', ['pts', ['xy', x, led.body.y_min - 5], ['xy', x, led.body.y_max + 5]]])
        errors = check_scene(read_scene(root), reserved=[])['findings']
        self.assertIn('D3:unit1', {o for f in errors if f['code'] == 'wire_body' for o in f['objects']})

    def test_plan_proposes_roles_from_connectivity(self):
        roles = {r: p['role'] for r, p in self.report['structure']['plan']['parts'].items()}
        self.assertEqual('anchor', roles['U1'])
        self.assertEqual('anchor', roles['J1'])
        self.assertEqual(('bank', 'bank'), (roles['C1'], roles['C2']))
        self.assertEqual(('divider_upper', 'divider_lower'), (roles['R1'], roles['R2']))
        self.assertEqual({'lane_series'}, {roles['R4'], roles['R5']})
        self.assertEqual({'lane_shunt'}, {roles['D4'], roles['D5']})
        self.assertEqual(('series', 'shunt'), (roles['F1'], roles['D2']))

    def test_structure_audit(self):
        self.assertEqual('PASS', self.report['structure']['status'], self.report['structure']['findings'])
        bad = self.bad_report['structure']
        self.assertEqual('FAIL', bad['status'])
        self.assertEqual([('recipe', 'D3')], [(f['rule'], f['subject']) for f in bad['findings']])

    def test_a_reason_turns_a_finding_into_a_deviation(self):
        sheet = draw(bad=True)
        sheet.justify('D3', 'regression fixture keeps the reversed LED')
        _, report = sheet.build('recipe_board')
        self.assertEqual('PASS', report['structure']['status'])
        self.assertEqual(['D3'], [d['subject'] for d in report['structure']['deviations']])

    def test_good_and_bad_are_electrically_identical(self):
        cli = find_cli()
        if not cli:
            self.skipTest('kicad-cli is not installed')
        with tempfile.TemporaryDirectory() as tmp:
            for root, report in ((self.good, self.report), (self.bad, self.bad_report)):
                sch, xml = Path(tmp) / 'board.kicad_sch', Path(tmp) / 'board.xml'
                sch.write_text(dump(root) + '\n')
                subprocess.run([cli, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(xml), str(sch)],
                               check=True, capture_output=True)
                result = compare_netlist(xml, INTENT, report['layout'])
                self.assertEqual('PASS', result['status'], result['errors'])

    def test_gate_cli_requires_reasoned_waivers(self):
        with tempfile.TemporaryDirectory() as tmp:
            sch = Path(tmp) / 'bad.kicad_sch'
            sch.write_text(dump(self.bad) + '\n')
            run = lambda *a: subprocess.run([sys.executable, str(CLI), str(sch), *a], capture_output=True, text=True)
            self.assertEqual(2, run().returncode)
            waivers = Path(tmp) / 'waivers.json'
            waivers.write_text(json.dumps({'bad.kicad_sch': {'cross_net_crossings': 1, 'tortuous_connections': 1}}))
            self.assertNotEqual(0, run('--waivers', str(waivers)).returncode)
            waivers.write_text(json.dumps({'bad.kicad_sch': {'cross_net_crossings': 1, 'tortuous_connections': 1,
                                                             'reason': 'regression fixture'}}))
            done = run('--waivers', str(waivers))
            self.assertEqual(0, done.returncode, done.stdout)
            self.assertIn('waiver', json.loads(done.stdout)['sheets']['bad.kicad_sch']['gate'])


class VerticalLabelTests(unittest.TestCase):
    """Labels on vertical wire ends and names on vertical-only nets."""

    @classmethod
    def setUpClass(cls):
        try:
            Libraries(library_dirs()).load('Device:R')
        except ValueError:
            raise unittest.SkipTest('KiCad symbol libraries are not installed')
        cls.intent = {'schema_version': 1, 'design_id': 'vertical-labels', 'title': 'vertical labels', 'components': [
            {'ref': 'R1', 'lib_id': 'Device:R', 'value': '10k', 'footprint': ''},
            {'ref': 'R2', 'lib_id': 'Device:R', 'value': '1k', 'footprint': ''}],
            'nets': [{'name': 'TOP_OUT', 'pins': ['R1.1']}, {'name': 'MID', 'pins': ['R1.2', 'R2.1']},
                     {'name': 'LOW_JOIN', 'pins': ['R2.2']}], 'no_connect': []}
        s = Sheet(cls.intent, rails={}, external=['TOP_OUT'])
        s.put('R1', '1', (50.8, 50.8), DOWN)
        s.justify('R1', 'first part of a vertical chain')
        s.label('R1.1', 'global', length=2)
        s.series('R1.2', ['R2'], DOWN, gap=8)
        s.label('R2.2', 'local', length=2, reason='joins the sense block')
        s.justify('MID', 'test name on a vertical-only net')
        s.name('MID')
        cls.root, cls.report = s.build('vertical')

    def labels(self, kind):
        return {n[1]: (float(first(n, 'at')[3]), [str(t) for t in first(first(n, 'effects'), 'justify')[1:]])
                for n in all_nodes(self.root, kind)}

    def test_native_styles(self):
        self.assertEqual({'TOP_OUT': (90.0, ['left'])}, self.labels('global_label'))
        self.assertEqual({'LOW_JOIN': (270.0, ['right', 'bottom']), 'MID': (90.0, ['left', 'bottom'])},
                         self.labels('label'))

    def test_scene_reads_them_without_review_gaps(self):
        scene = read_scene(parse(dump(self.root)))
        self.assertFalse([g for g in scene.gaps if 'Local label' in g])
        self.assertEqual([], [f for f in check_scene(scene, reserved=[])['findings'] if f['severity'] == 'error'])
        self.assertEqual('PASS', self.report['structure']['status'], self.report['structure'])

    def test_native_names(self):
        cli = find_cli()
        if not cli:
            self.skipTest('kicad-cli is not installed')
        with tempfile.TemporaryDirectory() as tmp:
            sch, xml = Path(tmp) / 'v.kicad_sch', Path(tmp) / 'v.xml'
            sch.write_text(dump(self.root) + '\n')
            subprocess.run([cli, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(xml), str(sch)],
                           check=True, capture_output=True)
            result = compare_netlist(xml, self.intent, self.report['layout'])
        self.assertEqual('PASS', result['status'], result['errors'])

    def test_local_join_label_needs_a_reason(self):
        s = Sheet(self.intent)
        s.put('R1', '1', (50.8, 50.8), DOWN)
        with self.assertRaisesRegex(ValueError, 'reason'):
            s.label('R1.1', 'local')


class RecipeRefinementTests(unittest.TestCase):
    """Behaviour added while redrawing a nine-page charger with recipes."""

    @classmethod
    def setUpClass(cls):
        try:
            Libraries(library_dirs()).load('Connector:USB_C_Receptacle_USB2.0_16P')
        except ValueError:
            raise unittest.SkipTest('KiCad symbol libraries are not installed')

    def test_global_label_outlines_follow_native_directions(self):
        from schematic_layout.sexpr import form, Atom
        root = form('kicad_sch', form('paper', 'A4'), form('lib_symbols'))
        for i, (angle, just) in enumerate(((0, 'right'), (180, 'left'), (90, 'left'), (270, 'right'))):
            root.append(form('global_label', f'N{i}', form('shape', Atom('passive')), form('at', 100, 100, angle),
                             form('effects', form('font', form('size', 1.27, 1.27)), form('justify', Atom(just)))))
        boxes = [f.box() for _, f in read_scene(root).labels]
        self.assertLess(boxes[0].x_max, 100)      # extends left
        self.assertGreater(boxes[1].x_min, 100)   # extends right
        self.assertLess(boxes[2].y_max, 100)      # extends up
        self.assertGreater(boxes[3].y_min, 100)   # extends down
        self.assertFalse(read_scene(root).gaps)

    def test_a_part_between_two_candidate_lanes_is_a_rung(self):
        intent = {'schema_version': 1, 'design_id': 'rung', 'components': [
            {'ref': 'J1', 'lib_id': 'Connector_Generic:Conn_01x03', 'value': 'J', 'footprint': ''},
            {'ref': 'C1', 'lib_id': 'Device:C', 'value': '4n7', 'footprint': ''},
            {'ref': 'R1', 'lib_id': 'Device:R', 'value': '100', 'footprint': ''},
            {'ref': 'R2', 'lib_id': 'Device:R', 'value': '100', 'footprint': ''}],
            'nets': [{'name': 'P', 'pins': ['J1.1', 'C1.1', 'R1.2']}, {'name': 'N', 'pins': ['J1.2', 'C1.2', 'R2.2']},
                     {'name': 'GND', 'pins': ['J1.3', 'R1.1', 'R2.1']}], 'no_connect': []}
        roles = {r: p['role'] for r, p in Sheet(intent, rails={'GND': 'power:GND'}).plan['parts'].items()}
        self.assertEqual(('series', 'shunt', 'shunt'), (roles['C1'], roles['R1'], roles['R2']))

    def test_bank_lead_zero_puts_the_first_part_at_the_start(self):
        s = Sheet(INTENT, rails=RAILS, external=EXTERNAL)
        s.place('D1', (50.8, 50.8))
        start = s.stub('D1.1', 4)
        s.bank(start, ['C1', 'C2'], RIGHT, lead=0)
        self.assertEqual(start[0], s.point('C1.1')[0])

    def test_draft_records_what_strict_mode_rejects(self):
        def sheet():
            s = draw()
            s.name('LED_A')     # R3 -> D3 is too short for this name
            return s
        with self.assertRaisesRegex(ValueError, 'LED_A'):
            sheet().build('recipe_board')
        _, report = sheet().build('recipe_board', draft=True)
        self.assertIn('name LED_A', report['draft_failures'])

    def test_coincident_pads_do_not_add_a_junction(self):
        others = ['J1.A5', 'J1.B5', 'J1.A6', 'J1.B6', 'J1.A7', 'J1.B7', 'J1.A8', 'J1.B8', 'J1.SH']
        intent = {'schema_version': 1, 'design_id': 'pads', 'components': [
            {'ref': 'J1', 'lib_id': 'Connector:USB_C_Receptacle_USB2.0_16P', 'value': 'USB-C', 'footprint': ''}],
            'nets': [{'name': 'GND', 'pins': ['J1.A1', 'J1.A12', 'J1.B1', 'J1.B12']},
                     {'name': 'VBUS', 'pins': ['J1.A4', 'J1.A9', 'J1.B4', 'J1.B9']}],
            'no_connect': others}
        s = Sheet(intent, rails={'GND': 'power:GND'}, external=['VBUS'])
        s.place('J1', (101.6, 76.2))
        s.power('J1.A1')
        s.label('J1.A4', 'global', length=4)
        root, _ = s.build('pads')
        self.assertEqual([], all_nodes(root, 'junction'))


class RecipeRejectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            Libraries(library_dirs()).load('Device:R')
        except ValueError:
            raise unittest.SkipTest('KiCad symbol libraries are not installed')

    def sheet(self):
        intent = copy.deepcopy(INTENT)
        return Sheet(intent)

    def test_pin_cannot_face_an_impossible_direction(self):
        s = self.sheet()
        s.place('U1', (101.6, 50.8))
        with self.assertRaises(ValueError):
            s.series('U1.1', ['C2'], RIGHT)

    def test_rail_symbol_must_not_face_back_into_its_pin(self):
        s = self.sheet()
        s.put('C2', '2', (50.8, 50.8), DOWN)
        with self.assertRaises(ValueError):
            s.power('C2.2')

    def test_different_nets_may_not_touch(self):
        s = self.sheet()
        s.place('J1', (20.32, 50.8))
        s.stub('J1.1', 4)
        s.wire('J1.2', add(s.point('J1.2'), RIGHT, 2), add(add(s.point('J1.2'), RIGHT, 2), (0, -1), 4))
        with self.assertRaisesRegex(ValueError, 'touch'):
            s._segments()

    def test_unplaced_parts_block_the_build(self):
        s = self.sheet()
        s.place('J1', (20.32, 50.8))
        with self.assertRaisesRegex(ValueError, 'Unplaced parts'):
            s.build()

    def test_diagonal_wires_are_rejected(self):
        s = self.sheet()
        s.place('J1', (20.32, 50.8))
        with self.assertRaises(ValueError):
            s.wire('J1.1', (40.64, 40.64))


if __name__ == '__main__':
    unittest.main()
