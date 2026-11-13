"""A part the datasheet lists as discontinued is not used in a new design (R5 review F-D201: MUR550APFG)."""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
from pathlib import Path
import shutil
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from schematic_layout.lifecycle import flagged
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_design_report import Delivery

# Layout text of the ordering table in onsemi MUR550/D Rev. 12, p.1-2, shortened.
MUR550 = """
NOTE: Some of the devices on this data sheet have been
DISCONTINUED. Please refer to the table on page 2.

        MUR550APFG, MURD550PFG, MUR550PFG
 ORDERING INFORMATION
 MUR550APFRLG                Axial          1,500 Tape & Reel
 MURD550PFT4G                DPAK           2,500 Tape & Reel


 DISCONTINUED (Note 1)

 MUR550APFG                  Axial          500 Units/Bag
 MUR550PFG                   TO-220AC       50 Units/Rail
† For information on tape and reel specifications, refer to BRD8011/D.
1. DISCONTINUED: These devices are not recommended for new design.
 MAXIMUM RATINGS   MURD550PFT4G
"""


def lines_pdf(lines):
    """A one-page PDF with one text line per entry."""
    body = ' '.join('(%s) Tj 0 -16 Td' % l for l in lines)
    stream = 'BT /F1 10 Tf 72 740 Td %s ET' % body
    objs = ['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [4 0 R] /Count 1 >>',
            '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
            '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents 5 0 R >>',
            '<< /Length %d >>\nstream\n%s\nendstream' % (len(stream), stream)]
    out, offsets = '%PDF-1.4\n', []
    for i, b in enumerate(objs, 1):
        offsets.append(len(out))
        out += '%d 0 obj\n%s\nendobj\n' % (i, b)
    xref = len(out)
    out += 'xref\n0 6\n0000000000 65535 f \n' + ''.join('%010d 00000 n \n' % o for o in offsets)
    return (out + 'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % xref).encode()


class OrderingTableTests(unittest.TestCase):
    def test_the_discontinued_block_flags_only_the_parts_listed_in_it(self):
        self.assertEqual('DISCONTINUED (Note 1)', flagged('MUR550APFG', MUR550))
        self.assertEqual('DISCONTINUED (Note 1)', flagged('MUR550PFG', MUR550))
        self.assertIsNone(flagged('MUR550APFRLG', MUR550))   # the orderable axial part
        self.assertIsNone(flagged('MURD550PFT4G', MUR550))   # after the footnote the block has ended

    def test_a_suffix_variant_is_another_part(self):
        self.assertIsNone(flagged('ABC100', 'ORDERING\nABC100-TR  SOT-23\nOBSOLETE\nABC100-TR  SOT-23\n'))

    def test_a_marker_on_the_part_line_flags_it(self):
        self.assertTrue(flagged('XYZ1', 'XYZ1   SOT-23   Last Time Buy\n'))


@unittest.skipUnless(shutil.which('pdftotext'), 'poppler is not installed')
class ReportTests(unittest.TestCase):
    def setUp(self):
        self.d = Delivery()
        self.addCleanup(self.d.cleanup)
        (self.d.root / 'ABC100.pdf').write_bytes(lines_pdf(
            ['ORDERING INFORMATION', 'ABC100-TR    SOT-23', 'DISCONTINUED (Note 1)', 'ABC100    SOT-23',
             '1. DISCONTINUED: not recommended for new design.']))

    def report(self, mpn, **extra):
        self.d.write('electrical-intent.json', {'components': [
            {'ref': 'U1', 'value': 'XYZ100'}, dict({'ref': 'D1', 'mpn': mpn, 'datasheet': 'ABC100.pdf'}, **extra)]})
        return self.d.report()

    def test_a_discontinued_part_is_a_record_problem_unless_a_reason_keeps_it(self):
        _, problems = self.report('ABC100')
        self.assertTrue(any('位号 D1 的料号 ABC100' in p and '停产' in p for p in problems), problems)
        text, problems = self.report('ABC100', lifecycle_reason='用户指定，已有 2000 只库存')
        self.assertFalse(any('位号 D1' in p for p in problems), problems)
        self.assertIn('- D1 ABC100：手册列在“DISCONTINUED (Note 1)”下，保留理由：用户指定，已有 2000 只库存', text)

    def test_the_orderable_part_passes(self):
        _, problems = self.report('ABC100-TR')
        self.assertFalse(any('位号 D1' in p for p in problems), problems)


if __name__ == '__main__':
    unittest.main()
