"""The planning box of a text holds KiCad's ink (user 2026-11-11: 字宽估计比 KiCad 实际窄，这个做).

Third redraw of Matrix R2: a value with slashes on a body and a wire through a Chinese block title passed build() and
failed KiCad's geometry check. Measured on KiCad 10 SVG: Latin text was already estimated wide, but a CJK glyph is
about 1.47 font heights wide (estimated 1.3), a note and a local name sit above their anchor, and slashes, brackets
and descenders reach below the line. Each text is exported alone and its ink compared with the box.
"""
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
from schematic_layout.native import find_cli
from schematic_layout.native_geometry import SVG, bounds
from schematic_layout.recipes import RIGHT, UP, label_geometry
from schematic_layout.scene import read_scene
from schematic_layout.sexpr import parse

SHEET = ('(kicad_sch (version 20250114) (generator "eeschema") (uuid "%s") (paper "A4") (lib_symbols) %s '
         '(sheet_instances (path "/" (page "1"))))')
NOTE = '(text "%s" (at 100 100 %d) (effects (font (size %s %s)) (justify left)) (uuid "%s"))'
NAME = '(label "%s" (at 100 100 %d) (effects (font (size %s %s)) (justify left bottom)) (uuid "%s"))'
TEXTS = ('R1309', '270p/50V/C0G', 'abcdefgjpqy', 'ORIN_OV_FLT_N', '输入接口与机壳地', 'Orin 短路锁定（主路与 Orin）')


class TextInkTests(unittest.TestCase):
    def ink_and_box(self, tmp, item):
        path = Path(tmp) / 't.kicad_sch'
        path.write_text(SHEET % (uuid.uuid4(), item), encoding='utf-8')
        subprocess.run([self.cli, 'sch', 'export', 'svg', '--exclude-drawing-sheet', '--no-background-color',
                        '-o', tmp, str(path)], capture_output=True, check=True)
        ink = bounds(SVG((Path(tmp) / 't.svg').read_text(encoding='utf-8')).segments())
        return ink, read_scene(parse(path.read_text(encoding='utf-8'))).labels[0][1].box()

    def test_notes_and_local_names_hold_their_ink(self):
        self.cli = find_cli()
        if not self.cli:
            self.skipTest('kicad-cli is not installed')
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            for font in (1.0, 1.27):
                for form, angle in ((NOTE, 0), (NOTE, 90), (NAME, 0), (NAME, 90)):
                    for text in TEXTS:
                        if form is NAME and not text.isascii():
                            continue
                        ink, box = self.ink_and_box(tmp, form % (text, angle, font, font, uuid.uuid4()))
                        over = max(box.x_min - ink[0], box.y_min - ink[1], ink[2] - box.x_max, ink[3] - box.y_max)
                        if over > 0.02:
                            out.append((form.split()[0], angle, font, text, round(over, 2)))
                        if form is NAME:      # the box the recipes plan a name with
                            plan = label_geometry('local', text, (100, 100), RIGHT if angle == 0 else UP, font)[2]
                            side = plan.y_min - ink[1] if angle == 0 else plan.x_min - ink[0]
                            if side > 0.02:
                                out.append(('recipe name', angle, font, text, round(side, 2)))
        self.assertEqual([], out)

    def test_a_plain_field_keeps_its_line_and_a_slash_reaches_below(self):
        from schematic_layout.geometry import TextField
        plain, slashed = TextField('R1309', 0, 0).box(), TextField('270p/50V/C0G', 0, 0).box()
        self.assertEqual((-0.635, 0.635), (plain.y_min, plain.y_max))
        self.assertGreater(slashed.y_max, plain.y_max + 0.4)


if __name__ == '__main__':
    unittest.main()
