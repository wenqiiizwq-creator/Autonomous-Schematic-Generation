"""Unassigned schematic footprints remain exact identity facts, not wildcards."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.reference_contract import verify_reference


class ReferenceContractStageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        for path in (ROOT / "tests/fixtures/reference_contract").iterdir():
            shutil.copy2(path, self.base / path.name)
        self.net = self.base / "netlist.xml"
        self.contract = json.loads((self.base / "contract.json").read_text())

    def audit(self):
        return verify_reference(self.net, self.contract, self.base)

    def native_footprint(self, text):
        tree = ET.parse(self.net)
        tree.getroot().find("components/comp[@ref='U1']/footprint").text = text
        tree.write(self.net)

    def test_explicit_unassigned_footprints_pass(self):
        self.native_footprint("")
        self.contract["pin_maps"]["U1"]["identity"]["footprint"] = ""
        result = self.audit()
        self.assertEqual(result["status"], "PASS", result)
        self.assertTrue(result["unverified"])

    def test_absent_native_footprint_matches_explicit_unassigned(self):
        tree = ET.parse(self.net)
        comp = tree.getroot().find("components/comp[@ref='U1']")
        comp.remove(comp.find("footprint"))
        tree.write(self.net)
        self.contract["pin_maps"]["U1"]["identity"]["footprint"] = ""
        self.assertEqual(self.audit()["status"], "PASS")

    def test_unassigned_contract_does_not_match_assigned_native(self):
        self.contract["pin_maps"]["U1"]["identity"]["footprint"] = ""
        self.assertEqual(self.audit()["pin_maps"]["U1"]["status"], "FAIL")

    def test_assigned_contract_does_not_match_unassigned_native(self):
        self.native_footprint("")
        self.assertEqual(self.audit()["pin_maps"]["U1"]["status"], "FAIL")

    def test_assigned_footprint_mismatch_still_fails(self):
        self.native_footprint("Demo:OTHER-5")
        self.assertEqual(self.audit()["pin_maps"]["U1"]["status"], "FAIL")

    def test_other_identity_fields_cannot_be_blank(self):
        identity = self.contract["pin_maps"]["U1"]["identity"]
        for field in ("value", "mpn", "lib_id"):
            with self.subTest(field=field):
                original = identity[field]
                identity[field] = ""
                with self.assertRaises(ValueError):
                    self.audit()
                identity[field] = original

    def test_footprint_must_still_be_text(self):
        for value in (None, 0, False, [], {}):
            with self.subTest(value=value):
                self.contract["pin_maps"]["U1"]["identity"]["footprint"] = value
                with self.assertRaises(ValueError):
                    self.audit()

    def test_whitespace_is_not_an_unassigned_footprint(self):
        self.contract["pin_maps"]["U1"]["identity"]["footprint"] = "  "
        with self.assertRaises(ValueError):
            self.audit()


if __name__ == "__main__":
    unittest.main()
