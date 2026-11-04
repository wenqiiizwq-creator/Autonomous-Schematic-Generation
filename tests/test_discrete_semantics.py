"""Discrete symbol meaning must match the exact part, not only its pin numbers."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from schematic_layout import discrete_semantics as ds
from schematic_layout.discrete_semantics import audit_discrete_semantics, mpn_meaning

LIBRARY = Path.home() / 'Documents' / '知识库' / 'HardwareWiki' / 'raw' / 'Datasheet'

SYMBOLS = {
    'Device:D_TVS': ('Bidirectional transient-voltage-suppression diode', ('A1', 'A2')),
    'Device:D_Zener': ('Zener diode', ('K', 'A')),
    'Test:TVS_Uni': ('', ('K', 'A')),
    'Device:Q_PMOS': ('P-MOSFET transistor, gate/source/drain', ('G', 'S', 'D')),
    'Device:Q_NMOS': ('N-MOSFET transistor, gate/source/drain', ('G', 'S', 'D')),
    'Device:Q_NPN': ('NPN transistor, base/emitter/collector', ('B', 'E', 'C')),
}


def cache(lib_ids):
    out = []
    for lib in lib_ids:
        desc, pins = SYMBOLS[lib]
        body = ' '.join('(pin passive line (at 0 0 0) (length 2.54) (name "%s") (number "%d"))' % (p, i + 1)
                        for i, p in enumerate(pins))
        out.append('(symbol "%s" (property "Description" "%s") (symbol "x_1_1" %s))' % (lib, desc, body))
    return '(kicad_sch (version 20250114) (lib_symbols %s))' % ' '.join(out)


class DiscreteSemanticsTests(unittest.TestCase):
    def run_case(self, parts, text=None, fields=None, pdftotext='/usr/bin/pdftotext'):
        """parts: [(ref, lib_id, mpn)]; text: datasheet first-pages text for every part."""
        with tempfile.TemporaryDirectory() as tmp:
            sheet = Path(tmp) / 'page.kicad_sch'
            sheet.write_text(cache({lib for _, lib, _ in parts}))
            pdf = Path(tmp) / 'part.pdf'
            pdf.write_text('stub')
            intent = {'components': [{'ref': r, 'lib_id': lib, 'mpn': mpn, 'datasheet': str(pdf) if text is not None else '',
                                      'fields': fields or {}} for r, lib, mpn in parts]}
            with mock.patch.object(ds, 'datasheet_text', return_value=text), \
                    mock.patch.object(ds.shutil, 'which', return_value=pdftotext):
                return audit_discrete_semantics([sheet], intent, [tmp])

    def test_bidirectional_symbol_for_unidirectional_datasheet_fails(self):
        r = self.run_case([('D702', 'Device:D_TVS', 'PESD5V0L1UA')],
                          'Low capacitance unidirectional ESD protection diode. Unidirectional ESD protection of one line')
        self.assertEqual('FAIL', r['status'])
        self.assertEqual('symbol_semantics_mismatch', r['errors'][0]['code'])
        self.assertIn('bidirectional', r['errors'][0]['detail'])

    def test_unidirectional_ka_symbol_passes(self):
        r = self.run_case([('D702', 'Test:TVS_Uni', 'PESD5V0L1UA')], 'Low capacitance unidirectional ESD protection diode')
        self.assertEqual('PASS', r['status'], r)

    def test_tvs_mpn_suffix_decides_family_datasheets(self):
        self.assertEqual('unidirectional', mpn_meaning('SMBJ24A-E3/52'))
        self.assertEqual('bidirectional', mpn_meaning('SMBJ24CA-E3/52'))
        self.assertEqual('unidirectional', mpn_meaning('P6KE33A'))
        self.assertIsNone(mpn_meaning('PESD5V0L1UA'))
        family_sheet = 'Available in unidirectional and bidirectional. VBR (bidirectional) 6.4 V to 231 V'
        self.assertEqual('FAIL', self.run_case([('D706', 'Device:D_TVS', 'SMBJ24A-E3/52')], family_sheet)['status'])
        self.assertEqual('PASS', self.run_case([('D706', 'Device:D_TVS', 'SMBJ24CA-E3/52')], family_sheet)['status'])
        self.assertEqual('FAIL', self.run_case([('D706', 'Device:D_Zener', 'SMBJ24CA')], family_sheet)['status'])

    def test_mosfet_channel_mismatch_fails(self):
        r = self.run_case([('Q701', 'Device:Q_PMOS', 'NTMFS5C604NL')], 'Power MOSFET 60 V, single N-Channel. N-Channel')
        self.assertEqual('FAIL', r['status'])
        self.assertEqual('PASS', self.run_case([('Q701', 'Device:Q_NMOS', 'NTMFS5C604NL')], 'single N-Channel')['status'])

    def test_complement_named_in_passing_still_decides(self):
        text = 'NPN switching transistor. NPN general purpose. NPN. PNP complement: MMBT3906'
        self.assertEqual('PASS', self.run_case([('Q302', 'Device:Q_NPN', 'MMBT3904')], text)['status'])

    def test_ambiguous_datasheet_is_unresolved_not_pass(self):
        r = self.run_case([('Q1', 'Device:Q_NMOS', 'DUAL')], 'N-channel and P-channel pair. N-channel. P-channel')
        self.assertEqual('INSUFFICIENT', r['status'])
        self.assertEqual('Q1', r['unresolved'][0]['ref'])

    def test_pin_name_polarity_without_evidence_is_not_applicable(self):
        r = self.run_case([('D303', 'Device:D_Zener', 'BZT52H-C5V1')], 'Single Zener diodes in a SOD123F package')
        self.assertEqual('NOT_APPLICABLE', r['status'])

    def test_stated_polarity_without_readable_evidence_says_why(self):
        r = self.run_case([('D1', 'Device:D_TVS', '')])
        self.assertEqual(('INSUFFICIENT', 'datasheet path does not resolve'), (r['status'], r['unresolved'][0]['reason']))
        r = self.run_case([('Q1', 'Device:Q_NMOS', 'X')], 'single N-Channel', pdftotext=None)
        self.assertEqual(('INSUFFICIENT', 'pdftotext not installed'), (r['status'], r['unresolved'][0]['reason']))
        r = self.run_case([('Q1', 'Device:Q_NMOS', 'X')], 'Power MOSFET 60 V')
        self.assertIn('name no', r['unresolved'][0]['reason'])

    def test_declared_polarity_decides(self):
        declared = {'SymbolPolarity': 'N-channel', 'PolarityEvidence': 'datasheet:Q.pdf#p1'}
        self.assertEqual('PASS', self.run_case([('Q1', 'Device:Q_NMOS', 'X')], 'N-channel and P-channel pair. N-channel. P-channel',
                                               fields=declared)['status'])
        self.assertEqual('FAIL', self.run_case([('Q1', 'Device:Q_PMOS', 'X')], None, fields=declared)['status'])
        self.assertEqual('INSUFFICIENT', self.run_case([('Q1', 'Device:Q_NMOS', 'X')], None,
                                                       fields={'SymbolPolarity': 'N-channel'})['status'])

    def test_unicode_dash_channel_is_read(self):
        # onsemi BSS123LT1 prints "N\u2212Channel" (U+2212 minus sign)
        for dash in ('\u2212', '\u2010', '\u2013', '-'):
            text = 'Power MOSFET 170 mA, 100 V N%sChannel SOT%s23' % (dash, dash)
            self.assertEqual('PASS', self.run_case([('Q902', 'Device:Q_NMOS', 'BSS123LT1G')], text)['status'], dash)
            self.assertEqual('FAIL', self.run_case([('Q902', 'Device:Q_PMOS', 'BSS123LT1G')], text)['status'], dash)
        self.assertEqual('PASS', self.run_case([('Q1', 'Device:Q_PMOS', 'X')], 'p\u2212channel enhancement')['status'])

    def test_family_suffix_legend_decides_mixed_tvs_datasheet(self):
        mixed = ('Uni-directional\nBi-directional\nUnidirectional only. Bi-directional. Uni-directional\n'
                 '\f\fPart numbering\nType Code:\nA Uni-Directional (5 % VBR Voltage Tolerance)\n'
                 'CA Bi-Directional (5% VBR Voltage Tolerance)\n')
        r = self.run_case([('D201', 'Device:D_TVS', '30KPA28CA')], mixed)
        self.assertEqual('PASS', r['status'], r)
        row = r['checked'][0]
        self.assertEqual((3, 'CA Bi-Directional (5% VBR Voltage Tolerance)'), (row['evidence_page'], row['evidence_text']))
        self.assertIn('MPN suffix CA', row['evidence'])
        self.assertEqual('FAIL', self.run_case([('D201', 'Device:D_TVS', '30KPA28A-B')], mixed)['status'])
        # suffix not in the legend: fall back to the first-pages count, still ambiguous
        self.assertEqual('INSUFFICIENT', self.run_case([('D201', 'Device:D_TVS', '30KPA28')], mixed)['status'])
        # a legend that contradicts itself for the suffix decides nothing
        self.assertIsNone(ds.legend_meaning('C = bidirectional\nC = unidirectional\n', 'XYZ12C'))
        self.assertIsNone(ds.legend_meaning('For bidirectional types the IR limit is double\n', 'XYZ12For'))
        self.assertEqual('CA', ds.mpn_suffix('30KPA28CA-B'))

    @unittest.skipUnless(LIBRARY.is_dir() and ds.shutil.which('pdftotext'), 'HardwareWiki or pdftotext not installed')
    def test_real_datasheets_from_matrix_r2(self):
        """R2 had 17 INSUFFICIENT false alarms from these two datasheets."""
        with tempfile.TemporaryDirectory() as tmp:
            sheet = Path(tmp) / 'page.kicad_sch'
            sheet.write_text(cache(['Device:D_TVS', 'Device:Q_NMOS']))
            intent = {'components': [
                {'ref': 'D201', 'lib_id': 'Device:D_TVS', 'mpn': '30KPA28CA',
                 'datasheet': str(LIBRARY / '28_保护器件/TVS_ESD保护器件/Littelfuse - 30KPA.pdf')},
                {'ref': 'Q902', 'lib_id': 'Device:Q_NMOS', 'mpn': 'BSS123LT1G',
                 'datasheet': str(LIBRARY / '09_功率半导体/MOSFET/onsemi - BSS123LT1.pdf')}]}
            r = audit_discrete_semantics([sheet], intent, [tmp])
        self.assertEqual(('PASS', []), (r['status'], r['unresolved']), r)
        tvs = next(row for row in r['checked'] if row['ref'] == 'D201')
        self.assertEqual(('bidirectional', 6), (tvs['part'], tvs['evidence_page']))
        self.assertIn('CA Bi-Directional', tvs['evidence_text'])


if __name__ == '__main__':
    unittest.main()
