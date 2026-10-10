"""Synthetic source-role evidence regressions; no third-party circuit fixtures."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.design_change import read_native
from schematic_layout.project_audit import audit_project, properties
from schematic_layout.symbol_integrity import audit_symbols
from schematic_layout.native_hierarchy import NativeHierarchy
from schematic_layout.sexpr import parse, dump, first, all_nodes, set_node


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PinlessEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root, self.xml = self.base / "board.kicad_sch", self.base / "native.xml"
        self.tree = parse('(kicad_sch (uuid root) (lib_symbols (symbol "Example:Marker" (symbol "Marker_1_1" (circle (center 0 0) (radius 1))))) (symbol (lib_id "Example:Marker") (uuid obj) (at 10 10 0) (unit 1) (exclude_from_sim yes) (in_bom no) (on_board yes) (property "Reference" "Z7") (property "Value" "Reviewed marker") (instances (project "board" (path "/root" (reference "Z7") (unit 1))))))')
        self.save()
        self.xml.write_text('<export><components><comp ref="Z7"><value>Reviewed marker</value><libsource lib="Example" part="Marker"/><sheetpath tstamps="/"/><tstamps>obj</tstamps><units><unit><pins/></unit></units></comp></components><nets/></export>')
        self.contract = self.make_contract()

    def save(self):
        self.root.write_text(dump(self.tree))

    def make_contract(self):
        context = NativeHierarchy(self.root)
        lib = first(first(self.tree, "lib_symbols"), "symbol")
        sym = first(self.tree, "symbol")
        return {"schema_version": 1, "project": "board", "file_sha256": context.file_sha256,
            "native_xml_sha256": sha(self.xml), "objects": [{"reference": "Z7", "instance": "/root", "symbol_uuid": "obj",
            "lib_id": "Example:Marker", "lib_sha256": hashlib.sha256(dump(lib).encode()).hexdigest(),
            "source_properties": properties(sym), "source_flags": {"exclude_from_sim": "yes", "in_bom": "no", "on_board": "yes", "dnp": "unspecified"},
            "role": "mechanical", "native_identity": {"value": "Reviewed marker", "footprint": "", "datasheet": "", "lib_id": "Example:Marker", "dnp": False, "fields": {}}}]}

    def read(self, contract=None):
        return read_native(self.xml, source_root=self.root, source_roles=self.contract if contract is None else contract)

    def test_mechanical_documentation_preserved_after_evidence_before_strict_failure(self):
        with self.assertRaisesRegex(ValueError, "no exported physical pins"):
            read_native(self.xml)
        self.assertEqual(audit_project(self.root)["status"], "FAIL")
        for role in ("mechanical", "documentation"):
            self.contract["objects"][0]["role"] = role
            native = self.read()
            self.assertEqual(set(native["components"]), {"Z7"})
            self.assertEqual(native["components"]["Z7"], self.contract["objects"][0]["native_identity"])
            self.assertEqual(native["pinless_objects"]["Z7"]["status"], "NA")
            self.assertFalse(native["pin_nets"])
            report = audit_symbols(self.root, self.xml, source_roles=self.contract)
            self.assertEqual(report["status"], "PASS", report)
            self.assertEqual(report["pinless_objects"][0]["pin_integrity"], "NA")
            self.assertEqual(report["physical_pin_count"], 0)
            self.assertEqual(report["native_pin_coverage"]["xml_only_references"], [])

    def test_no_role_electrical_zero_pins_rejected_even_with_flags(self):
        with self.assertRaisesRegex(ValueError, "no exported physical pins"):
            read_native(self.xml)
        self.assertEqual(audit_symbols(self.root, self.xml)["status"], "FAIL")
        contract = copy.deepcopy(self.contract); contract["objects"] = []
        with self.assertRaisesRegex(ValueError, "no exported physical pins"):
            self.read(contract)

    def test_cache_pin_in_any_unit_or_hidden_style_disallows_role(self):
        for unit in (0, 1, 2, 99):
            with self.subTest(unit=unit):
                lib = first(first(self.tree, "lib_symbols"), "symbol")
                pinunit = parse(f'(symbol "Marker_{unit}_2" (pin passive line hide (at 0 0 0) (length 0) (name "X") (number "3")))')
                lib.append(pinunit); self.save(); self.contract = self.make_contract()
                with self.assertRaisesRegex(ValueError, "cached physical pins"):
                    self.read()
                self.assertEqual(audit_project(self.root, source_roles=self.contract)["status"], "FAIL")
                lib.remove(pinunit)

    def test_unresolved_extends_is_insufficient_never_qualified(self):
        first(first(self.tree, "lib_symbols"), "symbol").append(parse('(extends "Unknown")'))
        self.save(); self.contract = self.make_contract()
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            self.read()
        report = audit_symbols(self.root, self.xml, source_roles=self.contract)
        self.assertEqual(report["status"], "INSUFFICIENT", report)
        self.assertFalse(report["pinless_objects"])

    def test_unresolved_object_does_not_mask_electrical_zero_pin_failure(self):
        first(first(self.tree, "lib_symbols"), "symbol").append(parse('(extends "Unknown")'))
        self.save()
        self.xml.write_text(self.xml.read_text().replace('</components>', '<comp ref="E1"><value>Electrical</value></comp></components>'))
        self.contract = self.make_contract()
        self.assertEqual(audit_symbols(self.root, self.xml, source_roles=self.contract)["native_pin_coverage"]["status"], "FAIL")
        with self.assertRaisesRegex(ValueError, "E1 has no exported physical pins"):
            self.read()

    def test_undefined_pinless_unit_and_duplicate_reference_cannot_qualify(self):
        sym = first(self.tree, "symbol")
        set_node(sym, 'unit', 99)
        set_node(first(first(first(sym, 'instances'), 'project'), 'path'), 'unit', 99)
        self.save(); self.contract = self.make_contract()
        with self.assertRaisesRegex(ValueError, "unit/style"): self.read()
        self.tree = parse(self.root.read_text().replace('(unit 99)', '(unit 1)'))
        self.save(); self.contract = self.make_contract()
        self.contract['objects'].append(copy.deepcopy(self.contract['objects'][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"): self.read()

    def test_stale_source_cache_xml_hash_and_wrong_identity_fail(self):
        for mutation in (lambda c: c["file_sha256"].update({self.root.name: "0" * 64}),
                         lambda c: c.update(native_xml_sha256="0" * 64),
                         lambda c: c["objects"][0].update(lib_sha256="0" * 64),
                         lambda c: c["objects"][0]["native_identity"].update(value="Different"),
                         lambda c: c["objects"][0].update(symbol_uuid="wrong"),
                         lambda c: c["objects"][0]["source_flags"].update(in_bom="yes")):
            c = copy.deepcopy(self.contract); mutation(c)
            with self.assertRaises(ValueError): self.read(c)
        self.xml.write_text(self.xml.read_text().replace('tstamps="/"', 'tstamps="/wrong/"'))
        self.contract["native_xml_sha256"] = sha(self.xml)
        with self.assertRaisesRegex(ValueError, "identity/instance mismatch"): self.read()

    def test_other_project_reference_and_property_cannot_be_borrowed(self):
        first(first(first(self.tree, "symbol"), "instances"), "project")[1] = "old-project"
        self.save(); self.contract = self.make_contract()
        report = audit_symbols(self.root, self.xml, source_roles=self.contract)
        self.assertEqual(report["status"], "INSUFFICIENT", report)
        self.assertFalse(report["pinless_objects"])
        self.assertEqual(report["native_inventory"]["export_component_count"], 1)
        self.assertEqual(len(report["missing_symbol_annotations"]), 1)
        self.assertEqual(report["native_inventory_reconciliation"]["selected_context_reference_count"], 0)

    def test_inventory_113_518_retained_on_strict_failure_and_never_qualifies(self):
        comps = ''.join(f'<comp ref="X{i}"/>' for i in range(113))
        nodes = ''.join(f'<node ref="X{i % 105}" pin="{i + 1}"/>' for i in range(518))
        self.xml.write_text(f'<export><components>{comps}</components><nets><net name="N">{nodes}</net></nets></export>')
        report = audit_symbols(self.root, self.xml)
        self.assertEqual(report["status"], "FAIL")
        diag = report["native_inventory"]
        self.assertEqual((diag["export_component_count"], diag["export_endpoint_count"]), (113, 518))
        self.assertEqual(set(diag["zero_endpoint_references"]), {f"X{i}" for i in range(105,113)})
        self.assertEqual(diag["qualification"], "NOT_EVALUATED")
        self.assertEqual(report["native_pin_coverage"]["status"], "FAIL")

    def test_cli_contract_forwarded_hash_reported_and_electrical_zero_rejected(self):
        contractfile = self.base / "roles.json"; contractfile.write_text(json.dumps(self.contract))
        for name in ("audit_project.py", "audit_symbol_integrity.py"):
            out = self.base / (name + '.json')
            argv = [sys.executable, '-B', str(ROOT / 'scripts' / name), str(self.root), '--netlist', str(self.xml),
                    '--source-role-contract', str(contractfile), '--out', str(out)]
            r = subprocess.run(argv, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(json.loads(out.read_text())["source_role_contract"]["sha256"], sha(contractfile))
            out.unlink(); contractfile.write_text(json.dumps({**self.contract, 'objects': []}))
            self.assertNotEqual(subprocess.run(argv, capture_output=True).returncode, 0)
            contractfile.write_text(json.dumps(self.contract))

    def test_one_shot_cli_forwards_explicit_roles_without_rebinding(self):
        spec = importlib.util.spec_from_file_location('pinless_verify_cli', ROOT / 'scripts/verify_schematic.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        calls = []
        def tool(name, *args):
            calls.append((name, [str(x) for x in args]))
            output = Path(args[-1]); output.write_text(json.dumps({'status': 'PASS', 'file_sha256': {self.root.name: sha(self.root)}}))
        argv = ['verify_schematic.py', str(self.root), '--intent', str(self.base / 'intent.json'),
                '--source-role-contract', str(self.base / 'roles.json'),
                '--reference-contract', str(self.base / 'reference.json'),
                '--baseline-xml', str(self.xml), '--change-contract', str(self.base / 'change.json'),
                '--baseline-source-root', str(self.root),
                '--baseline-source-role-contract', str(self.base / 'baseline-roles.json'),
                '--baseline-project', 'board', '--out', str(self.base / 'run')]
        with patch.object(sys, 'argv', argv), patch.object(module, 'find_cli', return_value='fake-kicad'), patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '10.0.6', '')), patch.object(module, 'tool', side_effect=tool):
            module.main()
        recipients = {name for name, args in calls if '--source-role-contract' in args}
        self.assertEqual(recipients, {'audit_project.py', 'audit_symbol_integrity.py',
                                     'verify_reference_contract.py', 'verify_design_change.py'})
        change_args = next(args for name, args in calls if name == 'verify_design_change.py')
        self.assertIn('--baseline-source-role-contract', change_args)
        self.assertIn(str(self.base / 'baseline-roles.json'), change_args)
        self.assertIn(str(self.base / 'roles.json'), change_args)
        self.assertFalse((self.base / 'roles.json').exists())  # CLI never creates/rebinds roles.


if __name__ == '__main__':
    unittest.main()
