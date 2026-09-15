"""Independent regressions for inner-leg geometry, hierarchy and native gates."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.symbol_integrity import attachment_rows, arc_distance, audit_symbols
from schematic_layout.sexpr import parse, dump, form, first, all_nodes, set_node
from schematic_layout.generate import generate, library_dirs
from schematic_layout.native import find_cli, verify


def lib(length=2, kind="input"):
    return parse(f'''(symbol "Demo:X" (symbol "X_1_1"
      (rectangle (start 0 -2) (end 4 2) (stroke (width 0.1)))
      (pin {kind} line (at -2 0 0) (length {length}) (name "IN") (number "1"))))''')


def sym(ref="U1", path="/root"):
    return parse(f'''(symbol (lib_id "Demo:X") (at 10 20 0) (unit 1)
      (property "Reference" "{ref}") (property "Value" "Probe")
      (instances (project "board" (path "{path}" (reference "{ref}") (unit 1)))))''')


def sheet(uid, number):
    return parse(f'''(sheet (uuid "{uid}") (property "Sheetfile" "child.kicad_sch")
      (instances (project "board" (path "/root" (page "{number}")))))''')


class AttachmentTests(unittest.TestCase):
    def test_short_leg_and_inside_bounding_box_are_candidates(self):
        for length in (1, 4):
            r, _ = attachment_rows(lib(length), 1, 1)
            self.assertEqual(r[0]["attachment"], "CANDIDATE")
        r, _ = attachment_rows(lib(), 1, 1)
        self.assertEqual(r[0]["attachment"], "PASS")

    def test_thick_capacitor_plate_is_not_a_gap(self):
        l = parse('''(symbol "D:C" (symbol "C_1_1"
          (polyline (pts (xy -2 0) (xy 2 0)) (stroke (width 0.508)))
          (pin passive line (at 0 2.54 270) (length 2.286) (name "~") (number "1"))))''')
        self.assertEqual(attachment_rows(l, 1, 1)[0][0]["attachment"], "PASS")
        set_node(first(first(l, "symbol"), "polyline")[2], "width", 0)
        self.assertEqual(attachment_rows(l, 1, 1)[0][0]["attachment"], "CANDIDATE")

    def test_supply_leg_meets_sloped_triangle_at_inner_end(self):
        l = parse('''(symbol "D:A" (symbol "A_1_1"
          (polyline (pts (xy -3 -3) (xy 3 0) (xy -3 3) (xy -3 -3)) (stroke (width 0.1)))
          (pin power_in line (at 0 5 270) (length 3.5) (name "V+") (number "5"))))''')
        self.assertEqual(attachment_rows(l, 1, 1)[0][0]["attachment"], "PASS")
        set_node(first(first(l, "symbol"), "pin"), "length", 2)
        self.assertEqual(attachment_rows(l, 1, 1)[0][0]["attachment"], "CANDIDATE")

    def test_nc_is_not_a_blanket_graphics_exception(self):
        self.assertEqual(attachment_rows(lib(1, "no_connect"), 1, 1)[0][0]["attachment"], "CANDIDATE")

    def test_hidden_and_zero_length_are_classified_not_verified(self):
        l = lib(0)
        r, _ = attachment_rows(l, 1, 1)
        self.assertEqual((r[0]["attachment"], r[0]["reason"]), ("NOT_APPLICABLE", "zero-length pin"))
        set_node(first(first(l, "symbol"), "pin"), "hide", "yes")
        self.assertEqual(attachment_rows(l, 1, 1)[0][0]["reason"], "hidden pin")

    def test_arc_distance_respects_sweep_and_endpoints(self):
        self.assertAlmostEqual(arc_distance((0, 1), (1, 0), (0, 1), (-1, 0)), 0)
        self.assertGreater(arc_distance((0, -1), (1, 0), (0, 1), (-1, 0)), 1)
        self.assertAlmostEqual(arc_distance((0, -1), (1, 0), (0, -1), (-1, 0)), 0)
        self.assertAlmostEqual(arc_distance((1.2, 0), (1, 0), (0, 1), (-1, 0)), .2)

    def test_unsupported_and_degenerate_geometry_remains_insufficient(self):
        for shape in ('(bezier (pts (xy 0 0) (xy 1 1)))', '(arc (start 0 0) (mid 1 0) (end 2 0))'):
            l = lib(1); sub = first(l, "symbol"); sub.remove(first(sub, "rectangle")); sub.append(parse(shape))
            self.assertEqual(attachment_rows(l, 1, 1)[0][0]["attachment"], "INSUFFICIENT")
        l = lib(); l.append(form("extends", "Unknown"))
        self.assertTrue(attachment_rows(l, 1, 1)[1])

    def test_units_styles_common_pins_and_bodyless_supply_unit(self):
        l = lib(); l.append(parse('(symbol "X_2_1" (pin power_in line (at 0 2 270) (length 1) (name "V+") (number "2")))'))
        r, _ = attachment_rows(l, 2, 1)
        self.assertEqual(r[0]["reason"], "bodyless separate power unit")
        l.append(parse('(symbol "X_0_1" (pin power_in line (at 0 0 0) (length 0) (name "EP") (number "3")))'))
        self.assertEqual({p["pin"] for p in attachment_rows(l, 1, 1)[0]}, {"1", "3"})
        self.assertEqual({p["pin"] for p in attachment_rows(l, 1, 2)[0]}, set())
        l = lib(); sub = first(l, "symbol"); sub.remove(first(sub, "rectangle"))
        self.assertEqual(attachment_rows(l, 1, 1)[0][0]["attachment"], "INSUFFICIENT")

    def test_nonfinite_coordinates_and_large_tolerance_rejected(self):
        l = lib(); set_node(first(first(l, "symbol"), "pin"), "length", float("nan"))
        with self.assertRaises(ValueError): attachment_rows(l, 1, 1)
        with self.assertRaises(ValueError): attachment_rows(lib(), 1, 1, 20)


class ProjectSymbolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name); self.root = self.base / "board.kicad_sch"
        self.tree = form("kicad_sch", form("uuid", "root"), form("lib_symbols", lib()), sym())
        self.save()
        self.xml = self.base / "native.xml"
        self.xml.write_text('<export><components><comp ref="U1"><value>Probe</value></comp></components><nets><net name="N"><node ref="U1" pin="1"/></net></nets></export>')

    def save(self): self.root.write_text(dump(self.tree))

    def test_native_physical_pins_are_checked_in_both_directions(self):
        self.assertEqual(audit_symbols(self.root, self.xml)["status"], "PASS")
        self.xml.write_text(self.xml.read_text().replace('pin="1"', 'pin="2"'))
        r = audit_symbols(self.root, self.xml)
        self.assertEqual(r["status"], "FAIL")
        self.assertEqual(r["native_pin_coverage"]["source_pins_missing_from_xml"], ["U1.1"])
        self.assertEqual(r["native_pin_coverage"]["xml_pins_missing_from_source"], ["U1.2"])

    def test_native_coverage_absence_never_overall_passes(self):
        r = audit_symbols(self.root)
        self.assertEqual(r["status"], "INSUFFICIENT")
        self.assertEqual(r["graphics"]["status"], "PASS")

    def test_shared_child_uses_each_selected_instance_annotation(self):
        child = form("kicad_sch", form("uuid", "child"), form("lib_symbols", lib()), sym("U1", "/root/a"))
        project = first(first(first(child, "symbol"), "instances"), "project")
        project.append(parse('(path "/root/b" (reference "U2") (unit 1))'))
        (self.base / "child.kicad_sch").write_text(dump(child))
        self.tree = form("kicad_sch", form("uuid", "root"), sheet("a", 2), sheet("b", 3)); self.save()
        r = audit_symbols(self.root)
        self.assertEqual(r["component_count"], 2)
        self.assertEqual({(p["reference"], p["instance"]) for p in r["pins"]}, {("U1", "/root/a"), ("U2", "/root/b")})

    def test_missing_project_annotation_never_uses_display_ref(self):
        first(first(first(self.tree, "symbol"), "instances"), "project")[1] = "elsewhere"
        self.save(); r = audit_symbols(self.root, self.xml)
        self.assertNotEqual(r["status"], "PASS")
        self.assertEqual(r["pins"], [])

    def test_exception_binds_library_hash_and_cannot_hide_change(self):
        l = first(first(self.tree, "lib_symbols"), "symbol")
        set_node(first(first(l, "symbol"), "pin"), "length", 1)
        self.save(); r = audit_symbols(self.root, self.xml); p = r["pins"][0]
        e = {"schema_version": 1, "exceptions": [{"instance": "/root", "reference": "U1", "unit": 1, "pin": "1", "lib_sha256": p["lib_sha256"], "reason": "Synthetic isolated terminal", "evidence": "fixture review record 1"}]}
        self.assertEqual(audit_symbols(self.root, self.xml, exceptions=e)["status"], "PASS")
        set_node(first(first(l, "symbol"), "pin"), "length", .5); self.save()
        self.assertEqual(audit_symbols(self.root, self.xml, exceptions=e)["status"], "FAIL")
        e["exceptions"][0]["pin"] = "99"
        self.assertEqual(audit_symbols(self.root, self.xml, exceptions=e)["status"], "FAIL")

    def test_rotation_mirror_changes_only_sheet_tip_not_attachment(self):
        s = first(self.tree, "symbol"); set_node(s, "at", 10, 20, 90); set_node(s, "mirror", "x"); self.save()
        r = audit_symbols(self.root, self.xml)
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["pins"][0]["tip_sheet"], (10, 18))

    def test_cli_preserves_input_and_hardlink(self):
        before = self.root.read_bytes(); alias = self.base / "alias.json"; alias.hardlink_to(self.root)
        for out in (self.root, alias):
            r = subprocess.run([sys.executable, str(ROOT / "scripts/audit_symbol_integrity.py"), str(self.root), "--out", str(out)], capture_output=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(self.root.read_bytes(), before)


class NativeAttachmentTests(unittest.TestCase):
    @unittest.skipUnless(find_cli() and library_dirs(), "KiCad CLI/libraries unavailable")
    def test_native_connectivity_passes_but_detached_leg_blocks_generation(self):
        fixtures = ROOT / "tests/fixtures/generation"
        intent = json.loads((fixtures / "rc_filter.intent.json").read_text())
        layout = json.loads((fixtures / "rc_filter.layout.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); root, _ = generate(intent, layout, "board")
            # Keep external tip and all wiring fixed; damage only the internal leg.
            cached = first(root, "lib_symbols")
            resistor = next(l for l in all_nodes(cached, "symbol") if l[1] == "Device:R")
            pin = next(p for s in all_nodes(resistor, "symbol") for p in all_nodes(s, "pin"))
            old_at = copy.deepcopy(first(pin, "at")); set_node(pin, "length", .2)
            path = base / "board.kicad_sch"; path.write_text(dump(root))
            (base / "board.kicad_pro").write_text('{}')
            result = verify(path, intent, layout, base / "native")
            self.assertEqual(first(pin, "at"), old_at)
            self.assertEqual(result["netlist"]["status"], "PASS")
            # KiCad may emit a library-cache mismatch warning for intentional art damage.
            self.assertEqual(result["symbol_integrity"]["graphics"]["counts"]["CANDIDATE"], 1)
            self.assertEqual(result["status"], "FAIL")

    @unittest.skipUnless(find_cli() and library_dirs(), "KiCad CLI/libraries unavailable")
    def test_supplied_reference_contract_is_a_required_generation_gate(self):
        fixtures = ROOT / "tests/fixtures/generation"
        intent = json.loads((fixtures / "rc_filter.intent.json").read_text())
        layout = json.loads((fixtures / "rc_filter.layout.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); root, _ = generate(intent, layout, "board")
            path = base / "board.kicad_sch"; path.write_text(dump(root))
            (base / "board.kicad_pro").write_text('{}')
            result = verify(path, intent, layout, base / "native", reference_contract=ROOT / "tests/fixtures/reference_contract/contract.json")
            self.assertEqual(result["netlist"]["status"], "PASS")
            self.assertEqual(result["symbol_integrity"]["status"], "PASS")
            self.assertEqual(result["reference_contract"]["status"], "FAIL")
            self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__": unittest.main()
