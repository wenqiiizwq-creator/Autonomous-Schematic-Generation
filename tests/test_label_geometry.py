"""Native-calibrated label bounds and narrowly attached cap regression.

Fixtures are independently hand-authored KiCad 10.0.6 synthetic geometry,
not third-party circuits. Their four-direction contours/net partitions were
checked in native PDF/XML. Native font universality is not claimed.
"""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
from schematic_layout.generate import global_label_box
from schematic_layout.geometry import Box
from schematic_layout.label_geometry import CAP_MM, DIRECTION_STYLE, global_outline
from schematic_layout.qa import check_scene
from schematic_layout.recipes import Sheet, label_geometry
from schematic_layout.scene import GlobalLabelText, Pin, Scene, Symbol, read_scene
from schematic_layout.sexpr import Atom, all_nodes, dump, first, form, parse
FIXTURES = HERE / 'fixtures' / 'drawing' / 'label_geometry'
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def field(direction=(1, 0), font=1.0, **kwargs):
    angle, just = DIRECTION_STYLE[direction]
    return GlobalLabelText('NET_A', 80, 50, angle, font, False, just, direction, **kwargs)


def qa(label, wire=None, pin=None):
    scene = Scene(Box(0, 0, 297, 210), labels=[('global_label', label)])
    if wire: scene.wires = [wire]
    if pin:
        scene.symbols = [Symbol('P1', 'Audit:Pin', 1, [], None,
                                [Pin('P1.1', *pin, (1, 0), 'passive')], [])]
    return check_scene(scene, grid=.01, reserved=[])


class LabelGeometryTests(unittest.TestCase):
    def test_native_fixture_pairs_and_own_wire_contacts(self):
        scene = read_scene(parse((FIXTURES / 'audit.kicad_sch').read_text()))
        report = check_scene(scene, grid=.01, reserved=[])
        pairs = [f for f in report['findings'] if f['code'] == 'text_overlap']
        self.assertEqual(len(pairs), 8, pairs)
        wire_hits = [f for f in report['findings'] if f['code'] == 'wire_text']
        self.assertEqual(len(wire_hits), 8, wire_hits)
        self.assertTrue(all('3_SIG_' in f['objects'][1] for f in wire_hits), wire_hits)
        # Group 2 is font1.0/pitch2.54 and must have no pair findings.
        self.assertFalse([f for f in pairs if any('_SIG_' in o and '2_' in o for o in f['objects'])])

    def test_actual_four_direction_sheet_build_pass_and_fail(self):
        root = parse((FIXTURES / 'audit.kicad_sch').read_text())
        lib = copy.deepcopy(all_nodes(first(root, 'lib_symbols'), 'symbol')[0])
        lib[1] = 'Boundary8'
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, 'Audit.kicad_sym').write_text(dump(form('kicad_symbol_lib', form('version', 20231120),
                                      form('generator', 'kicad_symbol_editor'), lib)) + '\n')
            for direction, pins in zip(DIRECTIONS, [(1, 2), (3, 4), (5, 6), (7, 8)]):
                for font, pitch in ((1.0, 2.54), (1.27, 2.54), (1.0, 1.0)):
                    with self.subTest(direction=direction, font=font, pitch=pitch):
                        names = ['SIGNAL_A', 'SIGNAL_B']
                        intent = {'schema_version': 1, 'components': [{'ref': 'U1', 'lib_id': 'Audit:Boundary8', 'value': 'Boundary8'}],
                                  'nets': [{'name': name, 'pins': [f'U1.{pin}']} for name, pin in zip(names, pins)],
                                  'no_connect': [f'U1.{i}' for i in range(1, 9) if i not in pins]}
                        sheet = Sheet(intent, rails={}, external=names, dirs=[temp])
                        sheet.place('U1', (63.5, 50.8))
                        if pitch == 2.54:
                            for pin in pins: sheet.label(f'U1.{pin}', font=font, length=4)
                        else:
                            axis = 1 if direction[0] else 0
                            center = sum(sheet.point(f'U1.{pin}')[axis] for pin in pins) / 2
                            for pin, offset in zip(pins, (-.5, .5)):
                                tip = sheet.point(f'U1.{pin}')
                                bend = (tip[0] + direction[0] * 3.81, tip[1] + direction[1] * 3.81)
                                corner = list(bend); corner[axis] = center + offset
                                anchor = (corner[0] + direction[0] * 1.27, corner[1] + direction[1] * 1.27)
                                sheet.wire(f'U1.{pin}', bend, tuple(corner), anchor)
                                sheet.label(anchor, net=sheet.nets[f'U1.{pin}'], outward=direction, font=font)
                        if font == 1.27 or pitch == 1.0:
                            with self.assertRaisesRegex(ValueError, 'collides'): sheet.build('label-test')
                        else:
                            built, _ = sheet.build('label-test')
                            self.assertEqual(qa_status := check_scene(read_scene(built), reserved=[])['status'], 'PASS', qa_status)

    def test_true_collision_pitch_one_preserved_in_all_directions(self):
        for direction in DIRECTIONS:
            a = global_outline('N_A', (80, 50), direction, 1.0).box
            at = (80, 51) if direction[0] else (81, 50)
            b = global_outline('N_B', at, direction, 1.0).box
            self.assertTrue(a.overlaps(b, gap_mm=.2))

    def test_shared_model_and_complete_anchor(self):
        for font in (1.0, 1.27):
            for direction in DIRECTIONS:
                label = field(direction, font)
                recipe = label_geometry('global', label.text, (80, 50), direction, font)[2]
                self.assertEqual(recipe, label.box())
                self.assertTrue(recipe.contains_point(80, 50))
                self.assertAlmostEqual(recipe.height if direction[0] else recipe.width, 2 * font + .1524 + .002)
                if direction[0]: self.assertEqual(recipe, global_label_box(label.text, (80, 50), 'right' if direction[0] > 0 else 'left', font))

    def test_cap_positive_for_own_wire_and_pin(self):
        for d in DIRECTIONS:
            anchor = (80, 50)
            outside = (80 - d[0] * 5, 50 - d[1] * 5)
            label = field(d)
            for wire in [(anchor, outside), (outside, anchor)]:
                self.assertTrue(label.outline().terminal_contact(*wire))
                self.assertNotIn('wire_text', qa(label, wire)['counts'])
            self.assertNotIn('text_pin_overlap', qa(label, pin=(anchor, outside))['counts'])

    def test_foreign_and_same_net_traversals_not_waived(self):
        for dx, dy in DIRECTIONS:
            label = field((dx, dy))
            a = (80, 50)
            away = (80 - dx * 5, 50 - dy * 5)
            inside = (80 + dx * 5, 50 + dy * 5)
            perpendicular = (-dy, dx)
            near = (80 - dx * .02, 50 - dy * .02)
            for wire in [(away, inside), (a, inside),
                         ((80 - perpendicular[0] * 2, 50 - perpendicular[1] * 2),
                          (80 + perpendicular[0] * 2, 50 + perpendicular[1] * 2)),
                         (near, away), (a, (80 - dx * .02, 50 - dy * .02)),
                         ((80 + dx * .25 - perpendicular[0] * 2, 50 + dy * .25 - perpendicular[1] * 2),
                          (80 + dx * .25 + perpendicular[0] * 2, 50 + dy * .25 + perpendicular[1] * 2))]:
                with self.subTest(direction=(dx, dy), wire=wire):
                    self.assertFalse(label.outline().terminal_contact(*wire))
                    self.assertIn('wire_text', qa(label, wire)['counts'])
                    self.assertIn('text_pin_overlap', qa(label, pin=wire)['counts'])

    def test_native_perpendicular_endpoint_connection_boundary(self):
        # Native MCU/clock crops show the legal endpoint on a passive label's
        # near edge. Rotate that geometry; complete traversals remain errors.
        for d in DIRECTIONS:
            for font in (1.0, 1.27):
                label = field(d, font)
                anchor = (80, 50)
                perpendicular = (-d[1], d[0])
                for sign in (-1, 1):
                    outside = (80 + sign * perpendicular[0] * 4,
                               50 + sign * perpendicular[1] * 4)
                    for segment in ((anchor, outside), (outside, anchor)):
                        self.assertNotIn('wire_text', qa(label, segment)['counts'])
                        self.assertNotIn('text_pin_overlap', qa(label, pin=segment)['counts'])
                near = (80 + perpendicular[0] * .02, 50 + perpendicular[1] * .02)
                self.assertIn('wire_text', qa(label, (anchor, near))['counts'])

    def test_connected_anchor_pass_regression_is_fail_wire_text(self):
        report = check_scene(read_scene(parse((FIXTURES / 'connected-anchor.kicad_sch').read_text())),
                             grid=.01, reserved=[], pin_nets={'P1.1': 'NET_A', 'P2.1': 'NET_B', 'P3.1': 'NET_B'})
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['counts'], {'wire_text': 1})
        self.assertFalse(report['coverage']['gaps'])

    def test_unknown_styles_keep_legacy_envelope_and_coverage_gap(self):
        styles = [dict(shape='input'), dict(bold=True), dict(italic=True), dict(face='Arial'),
                  dict(thickness=.2), dict(size=(1, .8)), dict(font_mm=1.5), dict(text='中文'),
                  dict(text='A\nB'), dict(text='~{A}'), dict(justify=frozenset({'left', 'bottom'})), dict(native_justify=('left', 'mirror')), dict(angle=179.9)]
        for style in styles:
            from dataclasses import replace
            label = replace(field(), **style)
            with self.subTest(style=style):
                self.assertTrue(label.outline().gaps)
                box = label.box()
                self.assertTrue(box.contains_point(80, 50))
                self.assertGreaterEqual(box.height, max(3.0, 3.0 * label.font_mm / 1.27))
                self.assertEqual(label.outline().terminal_contact((80, 50), (75, 50)),
                                 style == dict(shape='input'))
                result = qa(label, wire=((70, 50), (80, 50)))
                self.assertNotEqual('PASS', result['status'])
                self.assertTrue(result['coverage']['gaps'])

    def test_parsed_unknown_native_style_is_insufficient_without_collision(self):
        root = form('kicad_sch', form('paper', 'A4'), form('lib_symbols'),
                    form('global_label', 'N', form('shape', Atom('passive')), form('at', 80, 50, 180),
                         form('effects', form('font', form('size', 1, 1), Atom('italic')), form('justify', Atom('left')))))
        scene = read_scene(root)
        # Exact own pin point attaches it without a rendered pin leg.
        scene.symbols = [Symbol('P1', 'Audit:Pin', 1, [], None,
                                [Pin('P1.1', (80, 50), (80, 50), (1, 0), 'passive')], [])]
        self.assertEqual(check_scene(scene, grid=.01, reserved=[])['status'], 'INSUFFICIENT')
        # parse_justify drops unknown tokens for ordinary TextField callers;
        # global-label native coverage must retain and reject them.
        font = first(first(all_nodes(root, 'global_label')[0], 'effects'), 'font')
        font.remove(Atom('italic'))
        first(first(all_nodes(root, 'global_label')[0], 'effects'), 'justify').append(Atom('mirror'))
        scene = read_scene(root)
        self.assertTrue(scene.labels[0][1].outline().gaps)
        self.assertIn('justify', scene.labels[0][1].outline().gaps)

    def test_unknown_orientation_preserves_text_estimate_without_acceptance(self):
        from schematic_layout.scene import text_field
        node = form('global_label', 'LONG_SIGNAL', form('shape', Atom('passive')),
                    form('at', 80, 50, 0),
                    form('effects', form('font', form('size', 1, 1)),
                         form('justify', Atom('left'))))
        root = form('kicad_sch', form('paper', 'A4'), form('lib_symbols'), node)
        scene = read_scene(root)
        field = scene.labels[0][1]
        self.assertNotIsInstance(field, GlobalLabelText)
        self.assertEqual(field.box(), text_field(node, label=True).box())
        scene.symbols = [Symbol('P1', 'Audit:Pin', 1, [], None,
                                [Pin('P1.1', (80, 50), (80, 50), (1, 0), 'passive')], [])]
        self.assertEqual(check_scene(scene, grid=.01, reserved=[])['status'], 'INSUFFICIENT')
        box = field.box()
        mid_y = (box.y_min + box.y_max) / 2
        scene.wires = [((box.x_min - 2, mid_y), (box.x_max + 2, mid_y))]
        report = check_scene(scene, grid=.01, reserved=[])
        self.assertEqual(report['status'], 'FAIL')
        self.assertIn('wire_text', report['counts'])
        self.assertTrue(report['coverage']['gaps'])

    def test_input_tip_attachment_does_not_qualify_unknown_outline(self):
        from dataclasses import replace
        for direction in DIRECTIONS:
            for font in (1.0, 1.27):
                label = replace(field(direction, font), shape='input', text='STAT{slash}EN')
                outside = (80 - direction[0] * 4, 50 - direction[1] * 4)
                self.assertTrue(label.outline().terminal_contact((80, 50), outside))
                report = qa(label, ((80, 50), outside), pin=(outside, outside))
                self.assertNotIn('wire_text', report['counts'])
                self.assertEqual(report['status'], 'INSUFFICIENT')
                self.assertTrue(report['coverage']['gaps'])
                perp = (-direction[1], direction[0])
                self.assertIn('wire_text', qa(label, ((80, 50), (80 + perp[0] * 4, 50 + perp[1] * 4)))['counts'])
                wrong = (80 + direction[0] * 4, 50 + direction[1] * 4)
                self.assertIn('wire_text', qa(label, ((80, 50), wrong))['counts'])
                for bad in (replace(label, bold=True), replace(label, text='A{unknown}B'),
                            replace(label, text='中文'), replace(label, face='Arial')):
                    self.assertFalse(bad.outline().terminal_contact((80, 50), outside))



if __name__ == '__main__': unittest.main()
