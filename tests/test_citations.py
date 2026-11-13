"""Datasheet citations are checked against the cited file and page; unshown values are listed, not blocking."""
from framework_guard import skip_without_framework  # noqa: E402
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from schematic_layout import citations


def pdf(pages):
    """A minimal text PDF, one page per string."""
    objs = ['<< /Type /Catalog /Pages 2 0 R >>', None, '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids = []
    for text in pages:
        stream = 'BT /F1 12 Tf 72 720 Td (%s) Tj ET' % text
        objs.append('<< /Length %d >>\nstream\n%s\nendstream' % (len(stream), stream))
        objs.append('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >>'
                    ' /Contents %d 0 R >>' % len(objs))
        kids.append(len(objs))
    objs[1] = '<< /Type /Pages /Kids [%s] /Count %d >>' % (' '.join('%d 0 R' % k for k in kids), len(kids))
    out, offsets = '%PDF-1.4\n', []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += '%d 0 obj\n%s\nendobj\n' % (i, body)
    xref = len(out)
    out += 'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1) + ''.join('%010d 00000 n \n' % o for o in offsets)
    return (out + 'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, xref)).encode()


@unittest.skipUnless(shutil.which('pdfinfo') and shutil.which('pdftotext'), 'poppler is not installed')
class CitationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.wiki = Path(tmp.name) / 'wiki'
        sheet = self.wiki / 'raw/Datasheet/08/Vendor - PART.pdf'
        sheet.parent.mkdir(parents=True)
        sheet.write_bytes(pdf(['Features 85 to 265 Vac', 'VCS 0.930 V  tDLY 200 ns  Vneg -0.9 V  tol 20 %']))
        env = mock.patch.dict(os.environ, {'HARDWARE_WIKI': str(self.wiki)})
        env.start()
        self.addCleanup(env.stop)
        citations._pages.clear(); citations._texts.clear()

    def test_file_and_page_are_checked(self):
        ok = citations.check_source('datasheet:Datasheet/08/Vendor - PART.pdf#p2')
        self.assertEqual('PASS', ok['status'])
        beyond = citations.check_source('datasheet:Datasheet/08/Vendor - PART.pdf#p3')
        self.assertEqual('FAIL', beyond['status'])
        self.assertIn('只有 2 页', beyond['reason'])
        missing = citations.check_source('datasheet:Datasheet/08/Other - PART.pdf#p1')
        self.assertEqual('FAIL', missing['status'])
        self.assertIsNone(citations.check_source('review:R5/W-3'))

    def test_values_in_another_prefix_or_layout_are_found_and_others_are_listed(self):
        r = citations.check_source('datasheet:Datasheet/08/Vendor - PART.pdf#p2', [0.93, 2e-7, -0.9, 0.2, 0.95, 20.0])
        self.assertEqual(('PASS', [0.95]), (r['status'], r['unshown']))
        r = citations.check_source('datasheet:Datasheet/08/Vendor - PART.pdf#p1', [[85, 265], 26])
        self.assertEqual([26], r['unshown'])          # 26 is not read out of 265
        self.assertTrue(citations._shown(-0.9, 'VZCD(MIN) \u22120.9 \u22120.7'))   # Unicode minus as printed

    def test_without_the_library_nothing_is_claimed(self):
        shutil.rmtree(self.wiki)
        r = citations.check_source('datasheet:Datasheet/08/Vendor - PART.pdf#p2')
        self.assertEqual('NOT_CHECKED', r['status'])
        self.assertIn('找不到知识库', r['reason'])

    @skip_without_framework
    def test_values_without_pdftotext_are_said_to_be_unchecked(self):
        from audit_design_closure import audit_citations
        real = shutil.which
        with mock.patch.object(citations.shutil, 'which', lambda tool: None if tool == 'pdftotext' else real(tool)):
            calc = {'C1': {'parameters': [{'name': 'VCS', 'basis': 'guaranteed', 'value': 0.93,
                                           'source': 'datasheet:Datasheet/08/Vendor - PART.pdf#p2'}]}}
            summary = audit_citations({}, calc, {}, [], lambda *a: self.fail(a))
        self.assertEqual(['没有 pdftotext，Datasheet/08/Vendor - PART.pdf 的数值没核对'], summary['not_checked'])

    @skip_without_framework
    def test_closure_audit_fails_a_wrong_page_and_lists_an_unshown_value(self):
        from audit_design_closure import audit_citations
        errors = []
        calc = {'C1': {'parameters': [
            {'name': 'VCS', 'basis': 'guaranteed', 'value': 0.93, 'source': 'datasheet:Datasheet/08/Vendor - PART.pdf#p2'},
            {'name': 'VX', 'basis': 'typical', 'value': 0.95, 'source': 'datasheet:Datasheet/08/Vendor - PART.pdf#p2'},
            {'name': 'VD', 'basis': 'derived', 'value': 1.7, 'source': 'datasheet:Datasheet/08/Vendor - PART.pdf#p2'},
            {'name': 'VZ', 'basis': 'guaranteed', 'value': 1, 'source': 'datasheet:Datasheet/08/Vendor - PART.pdf#p9'}]}}
        work = {'W1': {'missing': [{'source': 'datasheet:Datasheet/08/Gone.pdf#p1'}]}}
        summary = audit_citations({}, calc, work, [], lambda code, item: errors.append((code, item)))
        self.assertEqual(5, summary['checked'])
        self.assertEqual(['C1:VZ', 'W1:missing[0]'], [i.split(':', 2)[0] + ':' + i.split(':', 2)[1] for _, i in errors])
        self.assertEqual([{'item': 'C1:VX', 'source': 'datasheet:Datasheet/08/Vendor - PART.pdf#p2', 'values': [0.95]}],
                         summary['review'])


if __name__ == '__main__':
    unittest.main()
