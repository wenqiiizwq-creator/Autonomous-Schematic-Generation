"""KiCad stacked pin numbers ([17,18]): one drawn pin for several same-net pads.

Matrix R2 (2026-11-04): TPS26630 OUT 17/18 could only be drawn as two visible
pins on one point (numbers overprinted) and LM70880 SW1-SW4 only as power_in
plus a PWR_FLAG, because hidden copies had to be passive. A stacked pin keeps
the datasheet type, KiCad's XML lists every pad and ERC sees one pin.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from schematic_layout.generate import Libraries, library_dirs
from schematic_layout.native import find_cli
from schematic_layout.recipes import RIGHT, Sheet
from schematic_layout.scene import physical_numbers, read_scene
from schematic_layout.sexpr import all_nodes, dump, parse
from schematic_layout.symbol_integrity import audit_symbols

DEMO = '''(kicad_symbol_lib (version 20231120) (generator "test")
  (symbol "EF" (pin_names (offset 0.762)) {numbers} (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "EF" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (symbol "EF_0_1" (rectangle (start -5.08 5.08) (end 5.08 -5.08) (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "EF_1_1"
      (pin power_in line (at -7.62 0 0) (length 2.54) (name "IN" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      (pin power_in line (at -7.62 -2.54 0) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      {out})))'''
STACKED = '(pin power_out line (at 7.62 0 180) (length 2.54) (name "OUT" (effects (font (size 1.27 1.27)))) (number "[17,18]" (effects (font (size 1.27 1.27)))))'
SEPARATE = STACKED.replace('"[17,18]"', '"17"') + ' ' + STACKED.replace('"[17,18]"', '"18"')


def library(out=STACKED, numbers=""):
    return DEMO.format(out=out, numbers=numbers)


class PhysicalNumberTests(unittest.TestCase):
    def test_kicad_stacked_notation(self):
        self.assertEqual(["17", "18"], physical_numbers("[17,18]"))
        self.assertEqual(["20", "21", "22", "5"], physical_numbers("[20-22,5]"))
        self.assertEqual(["A1", "A2", "A3"], physical_numbers("[A1-A3]"))
        self.assertEqual(["5"], physical_numbers("5"))
        self.assertEqual(["A-1"], physical_numbers("A-1"))

    def test_malformed_stacks_are_rejected(self):
        for text in ("[17, 18]", "[]", "[3-1]", "[1,1]", "[1,,2]"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                physical_numbers(text)


def board(tmp, out=STACKED, numbers=""):
    lib = parse(library(out, numbers))
    sym = next(s for s in all_nodes(lib, "symbol") if s[1] == "EF")
    sym[1] = "Demo:EF"
    root = Path(tmp) / "board.kicad_sch"
    root.write_text(dump(parse(f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid "root") (paper "A4")
      (lib_symbols {dump(sym)})
      (symbol (lib_id "Demo:EF") (at 100 100 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "u1")
        (property "Reference" "U1" (at 100 92 0)) (property "Value" "EF" (at 100 108 0))
        (instances (project "board" (path "/root" (reference "U1") (unit 1))))))''')) + "\n")
    return root


def xml(tmp, pins):
    path = Path(tmp) / "native.xml"
    nodes = "".join(f'<node ref="U1" pin="{p}"/>' for p in pins if p in ("17", "18"))
    rest = "".join(f'<net name="N{p}"><node ref="U1" pin="{p}"/></net>' for p in pins if p not in ("17", "18"))
    path.write_text(f'<export><components><comp ref="U1"><value>EF</value></comp></components>'
                    f'<nets><net name="OUT">{nodes}</net>{rest}</nets></export>')
    return path


class StackedSceneAndIntegrityTests(unittest.TestCase):
    def test_scene_expands_a_stacked_pin_on_one_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            scene = read_scene(parse(board(tmp).read_text()))
        pins = {p.id: p for p in scene.symbols[0].pins}
        self.assertEqual({"U1.1", "U1.2", "U1.17", "U1.18"}, set(pins))
        self.assertEqual(pins["U1.17"].point, pins["U1.18"].point)
        self.assertEqual("[17,18]", pins["U1.18"].number)
        self.assertEqual([], scene.gaps)

    def test_stacked_power_output_passes_integrity_and_native_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = audit_symbols(board(tmp), xml(tmp, ["1", "2", "17", "18"]))
        self.assertEqual("PASS", report["status"], report["errors"] + report["coverage_gaps"])
        rows = {r["pin"]: r for r in report["pins"]}
        self.assertEqual("[17,18]", rows["18"]["stacked_number"])
        self.assertEqual("power_out", rows["17"]["electrical_type"])
        self.assertEqual([], report["hidden_power"]["pins"])
        self.assertEqual("PASS", report["native_pin_coverage"]["status"])

    def test_xml_missing_a_stacked_pad_fails_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = audit_symbols(board(tmp), xml(tmp, ["1", "2", "17"]))
        self.assertEqual(["U1.18"], report["native_pin_coverage"]["source_pins_missing_from_xml"])

    def test_visible_pins_on_one_point_overprint_their_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = audit_symbols(board(tmp, SEPARATE), xml(tmp, ["1", "2", "17", "18"]))
        self.assertEqual("FAIL", report["status"])
        found = [e for e in report["errors"] if e["kind"] == "overprinted_pin_numbers"]
        self.assertEqual([["17", "18"]], [e["pins"] for e in found])

    def test_hidden_pin_numbers_do_not_overprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = audit_symbols(board(tmp, SEPARATE, "(pin_numbers hide)"), xml(tmp, ["1", "2", "17", "18"]))
        self.assertNotIn("overprinted_pin_numbers", {e["kind"] for e in report["errors"]})


class StackedDrawingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            Libraries(library_dirs()).load("Device:R")
        except ValueError:
            raise unittest.SkipTest("KiCad symbol libraries are not installed")

    def test_sheet_wires_a_stacked_pin_once_and_kicad_lists_every_pad(self):
        intent = {"schema_version": 1, "design_id": "stacked", "components": [
            {"ref": "U1", "lib_id": "Demo:EF", "value": "EF", "footprint": ""},
            {"ref": "R1", "lib_id": "Device:R", "value": "1k", "footprint": ""}],
            "nets": [{"name": "VIN", "pins": ["U1.1"]}, {"name": "GND", "pins": ["U1.2", "R1.2"]},
                     {"name": "VOUT", "pins": ["U1.17", "U1.18", "R1.1"]}]}
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "Demo.kicad_sym").write_text(library() + "\n")
            s = Sheet(intent, rails={"VIN": "power:+24V", "GND": "power:GND"}, external=[], dirs=[Path(tmp)])
            s.place("U1", (101.6, 101.6))
            s.power("U1.1"); s.power("U1.2")
            out = s.stub("U1.17", 4)
            s.shunt(out, "R1", RIGHT, gap=4)
            root, _ = s.build("stacked")
            text = dump(root)
            self.assertIn('(number "[17,18]"', text)
            cli = find_cli()
            if cli is None:
                self.skipTest("kicad-cli is not installed")
            sch = Path(tmp) / "stacked.kicad_sch"
            sch.write_text(text + "\n")
            subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(Path(tmp) / "n.xml"), str(sch)],
                           check=True, capture_output=True)
            nets = {n.get("name"): {(x.get("ref"), x.get("pin"), x.get("pintype")) for x in n.iter("node")}
                    for n in ET.parse(Path(tmp) / "n.xml").getroot().iter("net")}
            out_net = next(v for v in nets.values() if ("R1", "1", "passive") in v)
            self.assertLessEqual({("U1", "17", "power_out"), ("U1", "18", "power_out")}, out_net)


if __name__ == "__main__":
    unittest.main()
