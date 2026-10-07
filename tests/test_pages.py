"""Board intent to per-page drawing intents."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
from schematic_layout.pages import normalize, page_intents


def part(ref, lib, page):
    return {'ref': ref, 'lib_id': lib, 'value': ref, 'footprint': '', 'mpn': 'X-' + ref,
            'fields': {'Circuit': page, 'Evidence': 'test'}}


BOARD = {
    'schema': 'project-hardware-intent-v1', 'revision': 'v1',
    'components': [part('J1', 'Connector:Conn_01x02', '01_in'), part('R1', 'Device:R', '01_in'),
                   part('U1', 'Regulator_Linear:AMS1117-3.3', '02_ldo'), part('C1', 'Device:C', '02_ldo')],
    'nets': {'VIN': ['J1.1', 'R1.1'], 'VIN_F': ['R1.2', 'U1.3', 'C1.1'], 'GND': ['J1.2', 'U1.1', 'C1.2'],
             '+3V3': ['U1.2']},
    'no_connect': ['U1.4'],
}


class PageIntentTests(unittest.TestCase):
    def test_pages_keep_components_and_local_pins(self):
        pages = page_intents(BOARD, rails=['GND'])
        self.assertEqual(['01_in', '02_ldo'], list(pages))
        ldo = pages['02_ldo']['intent']
        self.assertEqual(1, ldo['schema_version'])
        self.assertEqual(['U1', 'C1'], [c['ref'] for c in ldo['components']])
        self.assertEqual('X-U1', ldo['components'][0]['mpn'])
        self.assertEqual({'VIN_F': ['U1.3', 'C1.1'], 'GND': ['U1.1', 'C1.2'], '+3V3': ['U1.2']},
                         {n['name']: n['pins'] for n in ldo['nets']})
        self.assertEqual(['U1.4'], ldo['no_connect'])

    def test_external_nets_cross_pages_and_exclude_rails(self):
        pages = page_intents(BOARD, rails=['GND'])
        self.assertEqual(['VIN_F'], pages['01_in']['external'])
        self.assertEqual(['VIN_F'], pages['02_ldo']['external'])
        self.assertEqual(['GND', 'VIN_F'], page_intents(BOARD)['01_in']['external'])

    def test_rails_are_restricted_to_each_page(self):
        pages = page_intents(BOARD, rails={'GND': 'power:GND', '+3V3': 'power:+3V3'})
        self.assertEqual({'GND': 'power:GND'}, pages['01_in']['rails'])
        self.assertEqual({'GND': 'power:GND', '+3V3': 'power:+3V3'}, pages['02_ldo']['rails'])
        self.assertEqual(['GND'], page_intents(BOARD, rails=['GND', 'VBAT'])['01_in']['rails'])

    def test_page_override_and_missing_page(self):
        pages = page_intents(BOARD, page_of={'R1': '02_ldo'})
        self.assertEqual(['VIN'], pages['01_in']['external'][1:])
        board = {**BOARD, 'components': BOARD['components'] + [{'ref': 'R9', 'lib_id': 'Device:R', 'value': '1k'}]}
        with self.assertRaisesRegex(ValueError, 'R9 has no page'):
            page_intents(board)

    def test_pins_must_belong_to_components(self):
        board = {**BOARD, 'nets': {**BOARD['nets'], 'X': ['Q9.1']}}
        with self.assertRaisesRegex(ValueError, 'Q9.1'):
            page_intents(board)

    def test_normalize_lists_nets(self):
        intent = normalize(BOARD)
        self.assertNotIn('schema', intent)
        self.assertEqual(1, intent['schema_version'])
        self.assertIn({'name': 'VIN', 'pins': ['J1.1', 'R1.1']}, intent['nets'])
        self.assertEqual(normalize(intent)['nets'], intent['nets'])


if __name__ == '__main__':
    unittest.main()
