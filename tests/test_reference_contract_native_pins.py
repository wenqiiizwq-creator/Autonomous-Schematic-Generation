"""Native library pin names are distinct from generated node identifiers."""
import copy
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


class NativeReferencePinTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        for p in (ROOT / "tests/fixtures/reference_contract").iterdir():
            shutil.copy2(p, self.base / p.name)
        self.net = self.base / "netlist.xml"
        self.contract = json.loads((self.base / "contract.json").read_text())
        self.tree = ET.parse(self.net)
        self.root = self.tree.getroot()
        old = self.root.find("libparts")
        if old is not None:
            self.root.remove(old)
        self.parts = ET.SubElement(self.root, "libparts")
        self.part = ET.SubElement(self.parts, "libpart", lib="Demo", part="Probe5")
        self.pins = ET.SubElement(self.part, "pins")
        for number, pin in self.contract["pin_maps"]["U1"]["pins"].items():
            ET.SubElement(self.pins, "pin", num=number,
                          name=pin["names"][0], type=pin["types"][0])
        self.comp = self.root.find("components/comp[@ref='U1']")

    def audit(self):
        self.tree.write(self.net)
        return verify_reference(self.net, self.contract, self.base)

    def node(self, number="5"):
        return self.root.find(f"nets/net/node[@ref='U1'][@pin='{number}']")

    def test_generated_node_identifier_does_not_change_library_pin_name(self):
        for node in self.root.findall("nets/net/node[@ref='U1']"):
            node.set("pinfunction", node.get("pinfunction") + "_" + node.get("pin"))
        self.assertEqual(self.audit()["status"], "PASS")

    def test_real_numbered_name_is_not_stripped(self):
        self.pins.find("pin[@num='5']").set("name", "Pin_1")
        self.node().set("pinfunction", "Pin_1_5")
        self.contract["pin_maps"]["U1"]["pins"]["5"]["names"] = ["Pin_1"]
        self.assertEqual(self.audit()["status"], "PASS")
        self.contract["pin_maps"]["U1"]["pins"]["5"]["names"] = ["Pin"]
        self.assertEqual(self.audit()["status"], "FAIL")

    def test_wrong_library_name_cannot_be_hidden_by_correct_node(self):
        self.pins.find("pin[@num='5']").set("name", "OTHER")
        self.assertEqual(self.audit()["status"], "FAIL")

    def test_wrong_library_type_cannot_be_hidden_by_correct_node(self):
        self.pins.find("pin[@num='5']").set("type", "output")
        self.assertEqual(self.audit()["status"], "FAIL")

    def test_node_type_mismatch_still_fails(self):
        self.node().set("pintype", "output")
        self.assertEqual(self.audit()["status"], "FAIL")

    def test_nc_node_type_suffix_is_not_a_library_type(self):
        self.node().set("pintype", "power_in+no_connect")
        self.assertEqual(self.audit()["status"], "PASS")

    def test_missing_libsource_is_insufficient(self):
        self.comp.remove(self.comp.find("libsource"))
        self.assertEqual(self.audit()["pin_maps"]["U1"]["status"], "FAIL")
        # Exact component identity is also contradicted; coverage must remain explicit.
        self.assertTrue(self.audit()["coverage_gaps"])

    def test_missing_libpart_does_not_fall_back_to_node(self):
        self.parts.remove(self.part)
        self.assertEqual(self.audit()["status"], "INSUFFICIENT")

    def test_duplicate_libpart_is_insufficient(self):
        self.parts.append(copy.deepcopy(self.part))
        self.assertEqual(self.audit()["status"], "INSUFFICIENT")

    def test_duplicate_physical_pin_number_is_insufficient(self):
        self.pins.append(copy.deepcopy(self.pins.find("pin[@num='5']")))
        self.assertEqual(self.audit()["status"], "INSUFFICIENT")

    def test_missing_library_pin_is_insufficient(self):
        self.pins.remove(self.pins.find("pin[@num='5']"))
        self.assertEqual(self.audit()["status"], "INSUFFICIENT")

    def test_missing_library_pin_metadata_is_insufficient(self):
        for field in ("name", "type"):
            with self.subTest(field=field):
                pin = self.pins.find("pin[@num='5']")
                original = pin.attrib.pop(field)
                self.assertEqual(self.audit()["status"], "INSUFFICIENT")
                pin.set(field, original)

    def test_library_pin_omitted_from_nodes_and_contract_cannot_pass(self):
        ET.SubElement(self.pins, "pin", num="6", name="NC", type="passive")
        self.assertEqual(self.audit()["pin_maps"]["U1"]["status"], "FAIL")

    def test_library_pin_without_physical_number_is_insufficient(self):
        ET.SubElement(self.pins, "pin", name="UNCERTAIN", type="passive")
        self.assertEqual(self.audit()["status"], "INSUFFICIENT")


if __name__ == "__main__":
    unittest.main()
