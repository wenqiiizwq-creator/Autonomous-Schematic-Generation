"""Default-font fallback orientation, calibrated with 32 native 10.0.6 SVGs."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from schematic_layout.scene import GlobalLabelText, read_scene
from schematic_layout.sexpr import parse, first, all_nodes
from schematic_layout.qa import check_scene

FIX = ROOT / 'tests/fixtures/drawing/global_label_fallback'


class GlobalLabelFallbackTests(unittest.TestCase):
    def test_native_32_directions_and_unsupported_outline_gaps_remain(self):
        rows = json.loads((FIX / 'native-bounds.json').read_text())['cases']
        self.assertEqual(len(rows), 32)
        fallback = 0
        for row in rows:
            with self.subTest(case=row['case']):
                directory = FIX / row['case']
                self.assertEqual(hashlib.sha256((directory / 'specimen.svg').read_bytes()).hexdigest(), row['svg_sha256'])
                scene = read_scene(parse((directory / 'specimen.kicad_sch').read_text()))
                label = scene.labels[0][1]
                center = label.box().center
                if row['native_outward'][0]:
                    self.assertGreater((center[0] - label.x) * row['native_outward'][0], 0)
                else:
                    self.assertGreater((center[1] - label.y) * row['native_outward'][1], 0)
                if not isinstance(label, GlobalLabelText):
                    fallback += 1
                    self.assertTrue(scene.gaps)
                    result = check_scene(scene, grid=.01, reserved=[])
                    # The native calibration fragment intentionally has no
                    # connection. Preserve that real fault as well as gaps.
                    self.assertEqual(result['status'], 'FAIL')
                    self.assertEqual([f['code'] for f in result['findings']], ['floating_label'])
        self.assertGreater(fallback, 0)

    def test_actual_fallback_text_traversal_is_still_fail(self):
        for row in json.loads((FIX / 'native-bounds.json').read_text())['cases']:
            scene = read_scene(parse((FIX / row['case'] / 'specimen.kicad_sch').read_text()))
            label = scene.labels[0][1]
            if isinstance(label, GlobalLabelText):
                continue  # Qualified outlines already have their own cap tests.
            with self.subTest(case=row['case']):
                box = label.box()
                cx, cy = box.center
                scene.wires = [((box.x_min - 1, cy), (box.x_max + 1, cy))]
                result = check_scene(scene, grid=.01, reserved=[])
                self.assertEqual(result['status'], 'FAIL')
                self.assertTrue(any(f['code'] == 'wire_text' for f in result['findings']), result)

    def test_unmeasured_fonts_and_shapes_are_not_newly_qualified(self):
        rows = json.loads((FIX / 'native-bounds.json').read_text())['cases']
        row = next(x for x in rows if x['angle'] == 180 and x['justify'] == 'right')
        tree = parse((FIX / row['case'] / 'specimen.kicad_sch').read_text())
        for shape, font in [('unknown', None), ('input', 'OtherFont')]:
            candidate = copy.deepcopy(tree)
            label = all_nodes(candidate, 'global_label')[0]
            first(label, 'shape')[1] = shape
            if font:
                first(first(label, 'effects'), 'font').append(['face', font])
            scene = read_scene(candidate)
            self.assertTrue(scene.gaps)
            self.assertEqual(scene.labels[0][1].angle, 180)


if __name__ == '__main__':
    unittest.main()
