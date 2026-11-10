"""A part with no pins (mounting hole, logo, note) passes only when its ComponentRole says so and no unit has pins."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.design_change import read_native
from schematic_layout.native import find_cli
from schematic_layout.project_audit import audit_project
from schematic_layout.reference_contract import verify_reference
from schematic_layout.sexpr import parse, dump

SOURCE = ('(kicad_sch (uuid root) (lib_symbols (symbol "Example:Marker" (symbol "Marker_1_1" (circle (center 0 0) (radius 1)))'
          '{extra_unit})) (symbol (lib_id "Example:Marker") (uuid obj) (at 10 10 0) (unit 1) (property "Reference" "Z7")'
          ' (property "Value" "Mounting hole"){role} (instances (project "board" (path "/root" (reference "Z7") (unit 1))))))')
XML = ('<export><components><comp ref="Z7"><value>Mounting hole</value><fields>{field}</fields><libsource lib="Example" part="Marker"/>'
       '<sheetpath tstamps="/"/><tstamps>obj</tstamps></comp></components><libparts><libpart lib="Example" part="Marker">{pins}'
       '</libpart></libparts><nets/></export>')


class PinlessEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root, self.xml = self.base / "board.kicad_sch", self.base / "native.xml"

    def write(self, role="mechanical", unit_pin=False, libpart_pin=False):
        extra = ' (symbol "Marker_2_1" (pin passive line (at 0 0 0) (length 2.54) (name "A") (number "1")))' if unit_pin else ""
        prop = f' (property "ComponentRole" "{role}")' if role else ""
        self.root.write_text(SOURCE.format(extra_unit=extra, role=prop))
        field = f'<field name="ComponentRole">{role}</field>' if role else ""
        pins = '<pins><pin num="1" name="A" type="passive"/></pins>' if libpart_pin else ""
        self.xml.write_text(XML.format(field=field, pins=pins))

    def test_declared_role_and_pinless_cache_qualify(self):
        for role in ("mechanical", "documentation"):
            with self.subTest(role=role):
                self.write(role)
                native = read_native(self.xml)
                self.assertEqual(("NA", role), (native["pinless_objects"]["Z7"]["status"], native["pinless_objects"]["Z7"]["role"]))
                audit = audit_project(self.root)
                self.assertEqual("PASS", audit["status"], audit)
                self.assertEqual(["Z7"], [o["reference"] for o in audit["pinless_objects"]])

    def test_no_role_or_another_role_still_fails(self):
        for role in (None, "connector", "resistor"):
            with self.subTest(role=role):
                self.write(role)
                with self.assertRaisesRegex(ValueError, "no exported physical pins"):
                    read_native(self.xml)
                self.assertIn("missing_active_unit_pins", {e["kind"] for e in audit_project(self.root)["errors"]})

    def test_a_pin_in_any_unit_disqualifies_the_role(self):
        self.write(unit_pin=True, libpart_pin=True)
        with self.assertRaisesRegex(ValueError, "no exported physical pins"):
            read_native(self.xml)
        self.assertEqual("FAIL", audit_project(self.root)["status"])

    def test_consumers_take_the_role_from_the_netlist(self):
        self.write()
        reference = {"schema_version": 1, "scope": {"feature_ids": ["f"]}, "sources": {}, "pin_maps": {}, "checks": [],
                     "features": [{"id": "f", "boundary": "b", "stages": []}]}
        try:
            result = verify_reference(self.xml, reference, self.base)
        except ValueError as exc:      # a contract this small may be rejected for its own shape, never for Z7
            self.assertNotIn("Z7", str(exc))
        else:
            self.assertNotIn("Z7", str(result.get("errors")))

    def test_kicad_export_of_a_declared_marker(self):
        cli = find_cli()
        if not cli:
            self.skipTest("kicad-cli is not installed")
        specimen = self.base / "specimen.kicad_sch"
        shutil.copy2(ROOT / "tests/fixtures/pinless_marker/specimen.kicad_sch", specimen)
        tree = parse(specimen.read_text())
        symbol = next(n for n in tree if isinstance(n, list) and n and n[0] == "symbol")
        symbol.append(parse('(property "ComponentRole" "mechanical" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))'))
        specimen.write_text(dump(tree) + "\n")
        xml = self.base / "specimen.xml"
        subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(xml), str(specimen)],
                       capture_output=True, check=True)
        self.assertEqual("NA", read_native(xml)["pinless_objects"]["Z7"]["status"])
        self.assertEqual("PASS", audit_project(specimen)["status"])


if __name__ == "__main__":
    unittest.main()
