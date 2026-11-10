"""import_netlist.py: a KiCad XML netlist becomes a design netlist for a C6-only run (references/modules.md)."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import import_netlist
from schematic_layout.generate import Libraries

XML = '''<?xml version="1.0" encoding="UTF-8"?>
<export version="E"><components>
  <comp ref="R1"><value>10k</value><footprint>R_0603</footprint>
    <fields><field name="MPN">RC0603FR-0710KL</field></fields>
    <libsource lib="my lib.v2" part="R" description=""/><sheetpath names="/" tstamps="/"/></comp>
  <comp ref="U1"><value>OPA</value><footprint></footprint><libsource lib="" part="OPA_1" description=""/>
    <sheetpath names="/AFE/" tstamps="/x/"/></comp>
  <comp ref="#PWR01"><value>GND</value><libsource lib="power" part="GND" description=""/></comp>
</components><nets>
  <net code="1" name="GND"><node ref="R1" pin="2"/><node ref="U1" pin="2"/><node ref="#PWR01" pin="1"/></net>
  <net code="2" name="/IN"><node ref="R1" pin="1"/><node ref="U1" pin="1"/></net>
  <net code="3" name="unconnected-(U1-NC-Pad3)"><node ref="U1" pin="3"/></net>
</nets></export>
'''
SCH = '''(kicad_sch (version 20231120) (lib_symbols
  (symbol "my lib.v2:R" (symbol "R_1_1" (pin passive line (at 0 0 0) (length 1) (name "~") (number "1")) (pin passive line (at 0 2 0) (length 1) (name "~") (number "2"))))
  (symbol "OPA_1" (symbol "OPA_1_1_1" (pin input line (at 0 0 0) (length 1) (name "IN") (number "1")) (pin power_in line (at 0 2 0) (length 1) (name "V-") (number "2")) (pin no_connect line (at 0 4 0) (length 1) (name "NC") (number "3")))))
)
'''


class ImportNetlistTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        (self.dir / 'n.xml').write_text(XML, encoding='utf-8')
        (self.dir / 'root.kicad_sch').write_text(SCH, encoding='utf-8')

    def test_parts_nets_and_unconnected_pins(self):
        intent = import_netlist.convert(self.dir / 'n.xml', self.dir / 'root.kicad_sch', self.dir / 'sym')
        parts = {c['ref']: c for c in intent['components']}
        self.assertEqual({'R1', 'U1'}, set(parts))                       # power symbols stay out
        self.assertEqual('my_lib_v2:R', parts['R1']['lib_id'])           # nickname the layout library accepts
        self.assertEqual('local:OPA_1', parts['U1']['lib_id'])           # a symbol edited inside the project
        self.assertEqual('RC0603FR-0710KL', parts['R1']['mpn'])
        self.assertEqual({'GND': ['R1.2', 'U1.2'], 'IN': ['R1.1', 'U1.1']}, intent['nets'])
        self.assertEqual(['U1.3'], intent['no_connect'])
        libraries = Libraries([self.dir / 'sym'])
        for comp in intent['components']:
            libraries.load(comp['lib_id'])

    def test_a_pin_number_with_a_dot_cannot_be_written(self):
        (self.dir / 'n.xml').write_text(XML.replace('pin="2"/><node ref="U1" pin="2"', 'pin="2"/><node ref="U1" pin="39.1"'),
                                        encoding='utf-8')
        with self.assertRaises(ValueError):
            import_netlist.convert(self.dir / 'n.xml')
        self.assertEqual(1, import_netlist.main([str(self.dir / 'n.xml'), '--out', str(self.dir / 'o.json')]))


if __name__ == '__main__':
    unittest.main()
