"""Pin text is read once per library symbol; what covers a pin number is found by the gate (user 2026-11-11:
C6.5请按照推荐改).

Third redraw of Matrix R2: 427 pin-text items, one per part, were dispositioned with one template sentence, and a value
drawn against a pin number (U701 pin 17) was not noticed. A pin name or number is the library symbol's and is the same
on every part drawn with it; what differs from part to part is what else is drawn over it, which the gate can check.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
from schematic_layout.qa import check_scene
from schematic_layout.scene import read_scene
from schematic_layout.sexpr import parse

LIB = ('(symbol "t:IC" (pin_names (offset 1.016)) (symbol "IC_1_1" (rectangle (start 0 -5.08) (end 10.16 5.08))'
       ' (pin input line (at -2.54 0 0) (length 2.54) (name "IN" (effects (font (size 1.27 1.27))))'
       ' (number "17" (effects (font (size 1.27 1.27)))))))')
PART = ('(symbol (lib_id "t:IC") (at %s %s 0) (unit 1) (uuid "%s") (property "Reference" "%s" (at %s %s 0)'
        ' (effects (font (size 1.27 1.27)))) (property "Value" "IC" (at %s %s 0) (effects (font (size 1.27 1.27))))'
        ' (pin "17" (uuid "p-%s")))')
NOTE = '(text "270p/50V/C0G" (at %s %s 0) (effects (font (size 1.27 1.27)) (justify right)))'


def sheet(*extra):
    parts = [PART % (100, y, uid, ref, 105, y - 8, 105, y + 8, uid) for y, uid, ref in ((100, 'u-1', 'U1'), (140, 'u-2', 'U2'))]
    return parse('(kicad_sch (version 20250114) (generator "t") (uuid "r") (paper "A4") (lib_symbols %s) %s)'
                 % (LIB, ' '.join(parts + list(extra))))


class PinTextReviewTests(unittest.TestCase):
    def test_one_item_per_library_symbol_names_the_parts_drawn_with_it(self):
        native = {'gaps': [], 'review': ['pin-number:u-1: physical pin numbers need native render review',
                                         'pin-number:u-2: physical pin numbers need native render review',
                                         'pin-name:u-1:17: nonunique/noncausal text removal',
                                         'pin-name:u-2: ambiguous/shared/unsupported cache identity']}
        coverage = check_scene(read_scene(sheet(), native), reserved=[])['coverage']
        number = 'pin-number:t/IC:unit1: physical pin numbers need native render review'
        self.assertEqual(3, len(coverage['render_review_items']), coverage['render_review_items'])
        self.assertIn(number, coverage['render_review_items'])
        self.assertEqual(['U1', 'U2'], coverage['render_review_refs'][number])

    def test_a_text_drawn_against_a_pin_number_is_found(self):
        codes = lambda root: [(f['code'], f['objects']) for f in check_scene(read_scene(root), reserved=[])['findings']
                              if f['code'].startswith('pin_number')]
        self.assertEqual([], codes(sheet()))
        self.assertEqual([], codes(sheet(NOTE % (96.5, 98.5))))          # ends a millimetre short of the number
        found = codes(sheet(NOTE % (97.8, 98.5)))                        # ends against it, as C703's value did
        self.assertEqual([('pin_number_text', 'pin-number:U1.17')], [(c, o[0]) for c, o in found])

    def test_a_wire_through_a_pin_number_is_found(self):
        wire = '(wire (pts (xy 98.7 90) (xy 98.7 99)))'
        found = [f for f in check_scene(read_scene(sheet(wire)), reserved=[])['findings'] if f['code'] == 'pin_number_wire']
        self.assertEqual(['pin-number:U1.17'], [f['objects'][0] for f in found])


if __name__ == '__main__':
    unittest.main()
