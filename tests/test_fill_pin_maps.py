"""fill_pin_maps.py reads datasheet pin tables (pdftotext -layout text) into datasheet_name / datasheet_type.

Industrial I/O calibration board, 2026-11-03 (user: 按建议执行): binding_version 1 reported 478 of 505 errors as pin maps
without the datasheet name and type. The rows below are shaped like the TI, ST and pin-out text that board's
datasheets give; nothing is filled from the symbol, and a pin the table does not type stays unfilled.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import fill_pin_maps as F  # noqa: E402

TI_NAME_FIRST = """
                                 Table 5-1. Pin Functions
 NAME                      NO.        TYPE(1)             DESCRIPTION
 DGATE                      1            O         Diode controller gate drive output.
 A                          2            I         Anode of the ideal diode.
 NC                         8            —         No connect.
 GND                       13            G         Connect to the system ground plane.
 VS                        22            P         Input power supply to the IC.
 RTN                   Thermal Pad       —         Leave exposed pad floating.
 (1)  I = input, O = output, I/O = input and output, P = power, G = ground
"""

TI_NUMBER_FIRST = """
NO.          NAME        I/O (1)                     DESCRIPTION
1            AGND           —       Analog Ground.
2            PGND           P       Power Ground.
11,12        SW             P       Switch node.
—            EP             —       Exposed Pad.
"""

VARIANTS = """
                    ISO6440 ,           ISO6441 ,        ISO6442 ,     Type(1)          DESCRIPTION
 EN1                     -                 7                  7           I      Enable 1
 IND                    6                  11                11           I      Input, channel D
 OUTD                   11                 6                  6           O      Output, channel D
 NC                     7                   -                 -                  Not connected
"""

PINOUT = """
     VCC1       1                                16        VCC2
     GND1       8                                 9        GND2
"""

ST_RANGES = """
                           Pin             Name              Type                                  Description
                           TAB             VCC               Supply        IC supply voltage.
                   1 to 12, 22 to 35, 48    NC                  -
                            14             STAT1       Output/Open drain   Channel 1 status (active low).
"""


def pin(*names, kind='passive'):
    return {'names': list(names), 'types': [kind]}


class ParseRows(unittest.TestCase):
    def test_ti_name_first_reads_type_under_heading(self):
        rows = F.parse_rows(TI_NAME_FIRST, 3, F.type_span(TI_NAME_FIRST))
        got = {r['name']: (r['positions'], r['type']) for r in rows}
        self.assertEqual(got['DGATE'], ([[1]], 'O'))
        self.assertEqual(got['VS'], ([[22]], 'PWR'))
        self.assertEqual(got['GND'], ([[13]], 'GND'))
        self.assertIsNone(got['NC'][1])                  # a dash is no type
        self.assertEqual(got['RTN'][0], ['pad'])

    def test_number_first_layout_and_stacked_pins(self):
        rows = F.parse_rows(TI_NUMBER_FIRST, 4, F.type_span(TI_NUMBER_FIRST))
        got = {r['name']: r for r in rows}
        self.assertEqual(got['SW']['positions'], [[11, 12]])
        self.assertEqual(got['SW']['type'], 'PWR')
        self.assertIsNone(got['AGND']['type'])
        self.assertEqual(got['EP']['raw_type'], '—')

    def test_pinout_drawing_line_is_two_pins_without_type(self):
        rows = F.parse_rows(PINOUT, 4, None)
        self.assertEqual([(r['name'], r['positions'], r['type']) for r in rows],
                         [('VCC1', [[1]], None), ('VCC2', [[16]], None), ('GND1', [[8]], None), ('GND2', [[9]], None)])

    def test_ranges_tab_and_open_drain(self):
        rows = F.parse_rows(ST_RANGES, 3, F.type_span(ST_RANGES))
        got = {r['name']: r for r in rows}
        self.assertEqual(got['NC']['positions'], [list(range(1, 13)) + list(range(22, 36)) + [48]])
        self.assertEqual(got['VCC']['positions'], ['pad'])
        self.assertEqual(got['VCC']['type'], 'PWR')
        self.assertEqual(got['STAT1']['type'], 'OD')

    def test_pin_names_with_digits_are_not_types(self):
        self.assertIsNone(F.type_code('GND2'))
        self.assertEqual(F.type_code('I/O FT')[0], 'IO')        # ST writes type and I/O level in one cell


class FillMap(unittest.TestCase):
    def test_variant_column_follows_symbol_numbering(self):
        rows = F.parse_rows(VARIANTS, 5, F.type_span(VARIANTS)) + F.parse_rows(PINOUT, 4, None)
        spec = {'pins': {'7': pin('EN1', kind='input'), '11': pin('IND', kind='input'), '6': pin('OUTD', kind='output'),
                         '16': pin('VCC2', kind='power_in')}}
        filled, missing, choice = F.fill_map(spec, rows)
        self.assertEqual(choice['column'], 1)            # the ISO6441 column, not ISO6440
        self.assertEqual(filled['7'], {'datasheet_name': 'EN1', 'datasheet_page': 5, 'datasheet_type': 'I'})
        self.assertEqual(filled['11']['datasheet_name'], 'IND')
        self.assertEqual(filled['6']['datasheet_type'], 'O')
        # VCC2 is only in the pin-out drawing: the name is read, the type is not, and the pin is listed.
        self.assertEqual(filled['16']['datasheet_name'], 'VCC2')
        self.assertNotIn('datasheet_type', filled['16'])
        self.assertEqual([m['reason'] for m in missing], ['type_not_given'])

    def test_exposed_pad_is_numbered_after_the_last_pin_and_nc_typed_by_name(self):
        rows = F.parse_rows(TI_NAME_FIRST, 3, F.type_span(TI_NAME_FIRST))
        spec = {'pins': {'1': pin('DGATE', kind='output'), '8': pin('NC', kind='no_connect'),
                         '22': pin('VS', kind='power_in'), '23': pin('NC', kind='no_connect'), '99': pin('X')}}
        filled, missing, _ = F.fill_map(spec, rows)
        self.assertEqual(filled['23']['datasheet_name'], 'RTN')       # 22 is the last numbered pin
        self.assertEqual(filled['8']['datasheet_type'], 'NC')
        reasons = {m['pin']: m['reason'] for m in missing}
        self.assertEqual(reasons, {'23': 'type_not_given', '99': 'not_in_table'})

    def test_never_writes_name_note_or_copies_symbol_names(self):
        rows = F.parse_rows(ST_RANGES, 3, F.type_span(ST_RANGES))
        spec = {'pins': {'14': pin('STATUS1', kind='output')}}
        filled, _, _ = F.fill_map(spec, rows)
        self.assertEqual(filled['14'], {'datasheet_name': 'STAT1', 'datasheet_page': 3, 'datasheet_type': 'OD'})

    def test_disagreeing_untyped_rows_stay_unfilled(self):
        rows = [{'name': 'NRST', 'positions': [[4]], 'type': None, 'raw_type': None, 'page': 2},
                {'name': 'PC15', 'positions': [[4]], 'type': None, 'raw_type': None, 'page': 3}]
        filled, missing, _ = F.fill_map({'pins': {'4': pin('PC15')}}, rows)
        self.assertEqual(filled, {})
        self.assertEqual(missing[0]['reason'], 'rows_disagree')


if __name__ == '__main__':
    unittest.main()
