"""Hierarchy and cache regressions derived from real multi-page delivery faults."""
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.project_audit import audit_project, compare_projects, symbol_pin_signature
from schematic_layout.sexpr import parse, dump, form, first, all_nodes, set_node


def library():
    return parse('(symbol "Demo:Dual" (symbol "Dual_1_1" (rectangle (start 0 0) (end 2 2)) (pin passive line (at 0 0 0) (length 2) (name "A") (number "1"))) (symbol "Dual_2_1" (pin passive line (at 0 0 0) (length 2) (name "B") (number "2"))))')


def symbol(ref, unit, path):
    return form("symbol", form("lib_id", "Demo:Dual"), form("unit", unit),
                form("property", "Reference", ref), form("instances", form("project", "board",
                     form("path", path, form("reference", ref), form("unit", unit)))))


def sheet(uid, filename, page, parent="/root"):
    return form("sheet", form("uuid", uid), form("property", "Sheetname", uid),
                form("property", "Sheetfile", filename), form("instances", form("project", "board",
                     form("path", parent, form("page", page)))))


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "board.kicad_sch"
        self.write(self.root, form("kicad_sch", form("uuid", "root"), sheet("one", "a.kicad_sch", "2"), sheet("two", "b.kicad_sch", "3")))
        for file, uid, unit in [("a", "one", 1), ("b", "two", 2)]:
            self.write(self.base / (file + ".kicad_sch"), form("kicad_sch", form("uuid", file),
                       form("lib_symbols", library()), symbol("U1", unit, "/root/" + uid)))

    def write(self, path, tree):
        path.write_text(dump(tree) + "\n")

    def mutate(self, path, change):
        tree = parse(path.read_text())
        change(tree)
        self.write(path, tree)

    def kinds(self, report):
        return {e["kind"] for e in report["errors"]}

    def test_valid_multiunit_hierarchy_counts_physical_components(self):
        r = audit_project(self.root, expected_pages=3)
        self.assertEqual(r["status"], "PASS", r)
        self.assertEqual(r["component_count"], 1)
        self.assertEqual(r["page_count"], 3)

    def test_missing_child_and_cycle_fail(self):
        (self.base / "a.kicad_sch").unlink()
        self.assertIn("missing_sheet", self.kinds(audit_project(self.root)))
        self.write(self.base / "a.kicad_sch", form("kicad_sch", sheet("loop", "board.kicad_sch", "4", "/root/one")))
        self.assertIn("hierarchy_cycle", self.kinds(audit_project(self.root)))

    def test_parent_escape_is_not_portable(self):
        self.mutate(self.root, lambda t: t.append(sheet("escape", "../outside.kicad_sch", "4")))
        self.assertIn("nonportable_sheet_path", self.kinds(audit_project(self.root)))

    def test_absolute_child_inside_current_folder_is_still_nonportable(self):
        self.mutate(self.root, lambda t: t.append(sheet("absolute", str(self.base / "a.kicad_sch"), "4")))
        self.assertIn("nonportable_absolute_sheet_path", self.kinds(audit_project(self.root)))

    def test_cli_does_not_overwrite_child_with_report(self):
        child = self.base / "a.kicad_sch"; before = child.read_bytes()
        r = subprocess.run([sys.executable, str(ROOT / "scripts/audit_project.py"), str(self.root), "--out", str(child)], capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(child.read_bytes(), before)

    def test_cli_preserves_truncated_or_unparseable_children(self):
        child = self.base / "a.kicad_sch"
        for raw in ['(kicad_sch', child.read_text().replace('(unit 1)', '(unit bad)')]:
            child.write_text(raw)
            r = subprocess.run([sys.executable, str(ROOT / "scripts/audit_project.py"), str(self.root), "--out", str(child)], capture_output=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(child.read_text(), raw)

    def test_selected_unit_must_have_actual_pins(self):
        def change(t):
            s = first(t, "symbol"); set_node(s, "unit", 99)
            set_node(first(first(first(s, "instances"), "project"), "path"), "unit", 99)
        self.mutate(self.base / "a.kicad_sch", change)
        self.assertIn("missing_active_unit_pins", self.kinds(audit_project(self.root)))

    def test_instance_unit_must_agree_with_displayed_unit(self):
        self.mutate(self.base / "a.kicad_sch", lambda t: set_node(first(t, "symbol"), "unit", 2))
        self.assertIn("instance_unit_mismatch", self.kinds(audit_project(self.root)))

    def test_same_lib_id_different_artwork_fails(self):
        def change(t):
            lib = first(first(t, "lib_symbols"), "symbol")
            set_node(first(first(lib, "symbol"), "rectangle"), "end", 9, 9)
        self.mutate(self.base / "b.kicad_sch", change)
        r = audit_project(self.root)
        self.assertIn("cached_library_conflict", self.kinds(r))
        self.assertNotIn("multiunit_pin_definition_conflict", self.kinds(r))

    def test_physical_pin_identity_cannot_change_with_artwork(self):
        lib = library()
        sig = symbol_pin_signature(lib)
        set_node(first(first(lib, "symbol"), "pin"), "at", 100, 100, 90)
        self.assertEqual(sig, symbol_pin_signature(lib))
        set_node(first(first(lib, "symbol"), "pin"), "number", "99")
        self.assertNotEqual(sig, symbol_pin_signature(lib))

    def test_hidden_pin_and_unit_changes_are_detected(self):
        lib = library(); sig = symbol_pin_signature(lib)
        first(first(lib, "symbol"), "pin").append("hide")
        self.assertNotEqual(sig, symbol_pin_signature(lib))
        lib = library(); first(lib, "symbol")[1] = "Dual_3_1"
        self.assertNotEqual(sig, symbol_pin_signature(lib))

    def test_pdf_count_mismatch_cannot_pass(self):
        pdf = self.base / "old.pdf"; pdf.write_bytes(b"fixture")
        with patch("schematic_layout.project_audit.pdf_page_count", return_value=2):
            r = audit_project(self.root, pdf)
        self.assertIn("pdf_page_count_mismatch", self.kinds(r))

    def test_missing_pdf_tool_is_insufficient(self):
        with patch("schematic_layout.project_audit.pdf_page_count", side_effect=RuntimeError("pdfinfo absent")):
            self.assertEqual(audit_project(self.root, "missing.pdf")["status"], "INSUFFICIENT")

    def test_removed_instance_report_even_when_file_still_exists(self):
        old = audit_project(self.root)
        self.mutate(self.root, lambda t: t.remove(all_nodes(t, "sheet")[-1]))
        new = audit_project(self.root)
        diff = compare_projects(old, new)
        self.assertEqual(len(diff["removed_instances"]), 1)
        self.assertEqual(diff["removed_files"], ["b.kicad_sch"])
        self.assertIn("unexpected_page_count", self.kinds(audit_project(self.root, expected_pages=3)))

    def test_shared_child_count_uses_instances_and_resolves_annotation(self):
        t = parse((self.base / "a.kicad_sch").read_text())
        s = first(t, "symbol")
        pr = first(first(s, "instances"), "project")
        pr.append(form("path", "/root/two", form("reference", "U2"), form("unit", 1)))
        self.write(self.base / "a.kicad_sch", t)
        root = parse(self.root.read_text())
        second = all_nodes(root, "sheet")[1]
        next(p for p in all_nodes(second, "property") if p[1] == "Sheetfile")[2] = "a.kicad_sch"
        self.write(self.root, root)
        r = audit_project(self.root)
        self.assertEqual(r["status"], "PASS", r)
        self.assertEqual(r["page_count"], 3)
        self.assertEqual(len(r["file_sha256"]), 2)
        self.assertEqual(r["component_count"], 2)

    def test_missing_annotation_does_not_claim_pass(self):
        self.mutate(self.base / "a.kicad_sch", lambda t: first(t, "symbol").remove(first(first(t, "symbol"), "instances")))
        self.assertEqual(audit_project(self.root)["status"], "INSUFFICIENT")

    def test_page_identifiers_may_have_gaps_but_not_duplicates(self):
        t = parse(self.root.read_text()); sh = all_nodes(t, "sheet")[1]
        pa = first(first(first(sh, "instances"), "project"), "path")
        set_node(pa, "page", "12"); self.write(self.root, t)
        self.assertEqual(audit_project(self.root)["status"], "PASS")
        set_node(pa, "page", "2"); self.write(self.root, t)
        self.assertIn("duplicate_page_number", self.kinds(audit_project(self.root)))


if __name__ == "__main__":
    unittest.main()
