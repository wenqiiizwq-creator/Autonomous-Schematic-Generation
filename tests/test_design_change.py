"""Independent change-intent tests, including shorts, opens and assembly drift."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.design_change import read_native, verify_change
from schematic_layout.generate import generate, library_dirs
from schematic_layout.native import find_cli
from schematic_layout.sexpr import dump, first, all_nodes


def identity(value="1k", dnp=False):
    return {"value": value, "footprint": "", "datasheet": "", "lib_id": "Device:R", "dnp": dnp, "fields": {}}


def write_xml(path, components, groups):
    root = ET.Element("export"); cs = ET.SubElement(root, "components"); ns = ET.SubElement(root, "nets")
    for ref, data in components.items():
        c = ET.SubElement(cs, "comp", ref=ref)
        for key in ["value", "footprint", "datasheet"]:ET.SubElement(c, key).text = data[key]
        lib, part = data["lib_id"].split(":"); ET.SubElement(c, "libsource", lib=lib, part=part)
        if data["dnp"]:ET.SubElement(c, "property", name="dnp")
        fs = ET.SubElement(c, "fields")
        for k, v in data["fields"].items():ET.SubElement(fs, "field", name=k).text = v
    for i, pins in enumerate(groups):
        n = ET.SubElement(ns, "net", code=str(i), name=f"N{i}")
        for pin in pins:
            ref, num = pin.rsplit(".", 1); ET.SubElement(n, "node", ref=ref, pin=num)
    ET.ElementTree(root).write(path)


class ChangeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name); self.old = self.base / "before.xml"; self.new = self.base / "after.xml"
        self.comps = {"R1": identity(), "R2": identity("2k")}
        self.groups = [["R1.1", "R2.1"], ["R1.2"], ["R2.2"]]
        self.contract = {"schema_version": 1}
        write_xml(self.old, self.comps, self.groups); write_xml(self.new, self.comps, self.groups)

    def test_unchanged_baseline_passes_and_keeps_nc_singletons(self):
        self.assertEqual(verify_change(self.old, self.new, self.contract)["status"], "PASS")
        write_xml(self.new, self.comps, self.groups[:2])
        self.assertEqual(verify_change(self.old, self.new, self.contract)["status"], "FAIL")

    def test_add_component_and_replace_only_affected_partition(self):
        c = copy.deepcopy(self.contract)
        c["add_components"] = {"R3": {"identity": identity("10k", True), "pins": ["1", "2"]}}
        c["replace_partitions"] = [{"before": [self.groups[0]], "after": [["R1.1", "R2.1", "R3.1"], ["R3.2"]]}]
        write_xml(self.new, {**self.comps, "R3": identity("10k", True)}, [["R1.1", "R2.1", "R3.1"], ["R3.2"], *self.groups[1:]])
        self.assertEqual(verify_change(self.old, self.new, c)["status"], "PASS")
        c["add_components"]["R3"]["pins"].append("3")
        with self.assertRaisesRegex(ValueError, "physical pins"):verify_change(self.old, self.new, c)

    def test_remove_component_requires_complete_replacement(self):
        c = {"schema_version": 1, "remove_components": ["R2"], "replace_partitions": [{"before": [self.groups[0], self.groups[2]], "after": [["R1.1"]]}]}
        write_xml(self.new, {"R1": identity()}, [["R1.1"], ["R1.2"]])
        self.assertEqual(verify_change(self.old, self.new, c)["status"], "PASS")
        c.pop("replace_partitions")
        with self.assertRaises(ValueError):verify_change(self.old, self.new, c)

    def test_value_footprint_and_dnp_changes_need_before_after(self):
        for key, v in [("value", "9k"), ("footprint", "Resistor_SMD:R_0603_1608Metric"), ("dnp", True)]:
            with self.subTest(key=key):
                new = copy.deepcopy(self.comps); new["R1"][key] = v; write_xml(self.new, new, self.groups)
                self.assertEqual(verify_change(self.old, self.new, self.contract)["status"], "FAIL")
                c = {"schema_version": 1, "component_changes": {"R1": {key: {"before": self.comps["R1"][key], "after": v}}}}
                self.assertEqual(verify_change(self.old, self.new, c)["status"], "PASS")
                c["component_changes"]["R1"][key]["before"] = "wrong"
                with self.assertRaisesRegex(ValueError, "precondition"):verify_change(self.old, self.new, c)

    def test_unplanned_short_and_open_fail(self):
        for groups in [[["R1.1"], ["R2.1"], *self.groups[1:]], [self.groups[0], ["R1.2", "R2.2"]]]:
            write_xml(self.new, self.comps, groups)
            self.assertEqual(verify_change(self.old, self.new, self.contract)["status"], "FAIL")

    def test_pin_contracts_reject_unknown_pins(self):
        for key in ["same_net", "distinct_net"]:
            c = {"schema_version": 1, key: [["R1.1", "UNKNOWN.1"]]}
            with self.assertRaises(ValueError):verify_change(self.old, self.new, c)

    def test_pin_contracts_and_named_interfaces(self):
        c = {"schema_version": 1, "same_net": [["R1.1", "R2.1"]], "distinct_net": [["R1.1", "R1.2", "R2.2"]], "named_nets": {"N0": self.groups[0]}}
        self.assertEqual(verify_change(self.old, self.new, c)["status"], "PASS")
        c["named_nets"] = {"WRONG_NAME": self.groups[0]}
        self.assertEqual(verify_change(self.old, self.new, c)["status"], "FAIL")

    def test_partition_preconditions_and_duplicate_pin_rejected(self):
        cases = [
            [{"before": [["R1.1"]], "after": []}],
            [{"before": [self.groups[0], self.groups[0]], "after": []}],
            [{"before": [self.groups[0]], "after": [["R1.1", "R1.1", "R2.1"]]}],
            [{"before": [self.groups[0]], "after": [["R1.1", "R2.1", "R1.2"]]}],
        ]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                verify_change(self.old, self.new, {"schema_version": 1, "replace_partitions": changes})

    def test_native_duplicate_pin_is_rejected(self):
        write_xml(self.new, self.comps, [*self.groups, ["R1.1"]])
        with self.assertRaisesRegex(ValueError, "multiple nets"):read_native(self.new)

    def test_stale_baseline_and_malformed_xml_fail(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            verify_change(self.old, self.new, {"schema_version": 1, "baseline_sha256": "0" * 64})
        self.new.write_text("<export>")
        with self.assertRaisesRegex(ValueError, "Malformed"):read_native(self.new)

    def test_cli_invalid_input_returns_failure_report(self):
        contract = self.base / "contract.json"; report = self.base / "report.json"
        contract.write_text('{"schema_version": 999}')
        r = subprocess.run([sys.executable, str(ROOT / "scripts/verify_design_change.py"), str(self.old), str(self.new), str(contract), "--out", str(report)], capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(json.loads(report.read_text())["status"], "FAIL")

    def test_cli_does_not_overwrite_contract(self):
        contract = self.base / "contract.json"; contract.write_text(json.dumps(self.contract))
        before = contract.read_bytes()
        r = subprocess.run([sys.executable, str(ROOT / "scripts/verify_design_change.py"), str(self.old), str(self.new), str(contract), "--out", str(contract)], capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(contract.read_bytes(), before)

    def test_cli_preserves_input_via_hardlink_output(self):
        contract = self.base / "contract.json"; contract.write_text(json.dumps(self.contract))
        alias = self.base / "alias.json"; os.link(self.old, alias); before = self.old.read_bytes()
        r = subprocess.run([sys.executable, str(ROOT / "scripts/verify_design_change.py"), str(self.old), str(self.new), str(contract), "--out", str(alias)], capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.old.read_bytes(), before)

    def test_missing_native_pin_is_not_a_literal_none_pin(self):
        for path in [self.old, self.new]:
            tree = ET.parse(path); tree.find("nets/net/node").attrib.pop("pin"); tree.write(path)
        with self.assertRaisesRegex(ValueError, "missing reference or pin"):
            verify_change(self.old, self.new, self.contract)

    @unittest.skipUnless(find_cli() and library_dirs(), "native KiCad unavailable")
    def test_real_native_value_and_pin_change_match_independent_contract(self):
        fixture = ROOT / "tests/fixtures/generation"
        intent = json.loads((fixture / "rc_filter.intent.json").read_text())
        layout = json.loads((fixture / "rc_filter.layout.json").read_text())
        for name, value_ in [("before", "1k"), ("after", "2k")]:
            next(c for c in intent["components"] if c["ref"] == "R1")["value"] = value_
            tree, _ = generate(intent, layout, "board")
            if name == "after":
                resistor = next(s for s in all_nodes(tree, "symbol") if any(p[1:3] == ["Reference", "R1"] for p in all_nodes(s, "property")))
                at = first(resistor, "at"); at[3] = (float(at[3]) + 180) % 360
            path = self.base / (name + ".kicad_sch"); path.write_text(dump(tree) + "\n")
            r = subprocess.run([find_cli(), "sch", "export", "netlist", "--format", "kicadxml", "-o", str(self.base / (name + ".xml")), str(path)], capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
        c = {"schema_version": 1, "component_changes": {"R1": {"value": {"before": "1k", "after": "2k"}}},
             "replace_partitions": [{"before": [["J1.1", "R1.1"], ["R1.2", "C1.1", "J2.1"]],
                                      "after": [["J1.1", "R1.2"], ["R1.1", "C1.1", "J2.1"]]}]}
        self.assertEqual(verify_change(self.old, self.new, c)["status"], "PASS")
        self.assertEqual(verify_change(self.old, self.new, self.contract)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
