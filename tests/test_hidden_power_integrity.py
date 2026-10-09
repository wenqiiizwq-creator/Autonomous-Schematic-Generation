"""Synthetic physical hidden-power policy controls, separate from pin-to-ink.

No third-party board or pin coordinates are used in these minimal fixtures.
"""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from schematic_layout.sexpr import parse, dump
from schematic_layout.symbol_integrity import audit_symbols


class HiddenPowerIntegrityTests(unittest.TestCase):
    def audit(self, kind="power_in", *, hidden=True, length=2, peer=False,
              peer_name="SUPPLY", same_net=True, native=True, virtual=False,
              peer_kind="power_in"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "board.kicad_sch"
            marker = "(hide yes)" if hidden else ""
            peer_pin = (f'(pin {peer_kind} line (at -2 0 0) (length 2) '
                        f'(name "{peer_name}") (number "2"))') if peer else ""
            ref = "#PWR01" if virtual else "U1"
            root.write_text(dump(parse(f'''(kicad_sch (uuid "root")
              (lib_symbols (symbol "Demo:X" (symbol "X_1_1"
                (rectangle (start 0 -2) (end 4 2) (stroke (width 0.1)))
                (pin {kind} line (at -2 0 0) (length {length}) {marker}
                  (name "SUPPLY") (number "1")) {peer_pin})))
              (symbol (lib_id "Demo:X") (at 10 20 0) (unit 1)
                (property "Reference" "{ref}") (property "Value" "Probe")
                (instances (project "board" (path "/root"
                  (reference "{ref}") (unit 1))))))''')))
            xml = Path(tmp) / "native.xml"
            second = '<node ref="U1" pin="2"/>' if peer and same_net else ""
            other = ('<net name="OTHER"><node ref="U1" pin="2"/></net>'
                     if peer and not same_net else "")
            components = '<comp ref="U1"><value>Probe</value></comp>' if not virtual else ""
            nets = (f'<net name="N"><node ref="U1" pin="1"/>{second}</net>{other}'
                    if not virtual else "")
            xml.write_text(f'<export><components>{components}</components><nets>{nets}</nets></export>')
            before = root.read_bytes(), xml.read_bytes()
            report = audit_symbols(root, xml if native else None)
            self.assertEqual(before, (root.read_bytes(), xml.read_bytes()))
            return report

    def test_unrepresented_physical_hidden_power_is_failed(self):
        for kind in ("power_in", "power_out"):
            with self.subTest(kind=kind):
                report = self.audit(kind)
                self.assertEqual(report["status"], "FAIL")
                self.assertEqual(report["pins"][0]["attachment"], "NOT_APPLICABLE")
                self.assertEqual(report["graphics"]["status"], "PASS")
                self.assertEqual(report["native_pin_coverage"]["status"], "PASS")
                self.assertIn("unrepresented_hidden_power", {e["kind"] for e in report["errors"]})

    def test_zero_length_does_not_exempt_hidden_physical_power(self):
        self.assertEqual(self.audit(length=0)["status"], "FAIL")

    def test_hidden_signal_and_passive_keep_graphics_classification(self):
        for kind in ("input", "passive"):
            with self.subTest(kind=kind):
                self.assertEqual(self.audit(kind)["status"], "PASS")

    def test_visible_zero_length_physical_power_remains_accepted(self):
        self.assertEqual(self.audit(hidden=False, length=0)["status"], "PASS")

    def test_virtual_power_symbol_is_outside_physical_policy(self):
        self.assertEqual(self.audit(virtual=True)["status"], "PASS")

    def test_coincident_native_connected_hidden_power_is_not_qualified(self):
        report = self.audit(peer=True)
        self.assertEqual(report["status"], "INSUFFICIENT")
        self.assertEqual(report["hidden_power"]["status"], "INSUFFICIENT")
        self.assertEqual(report["native_pin_coverage"]["status"], "PASS")
        self.assertIn("unsupported coincident hidden power", " ".join(report["coverage_gaps"]))

    def test_wrong_visible_anchor_does_not_represent_hidden_supply(self):
        for kwargs in ({"peer_name": "RETURN"}, {"peer_kind": "passive"},
                       {"same_net": False}):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.audit(peer=True, **kwargs)["status"], "FAIL")

    def test_missing_native_evidence_cannot_qualify_coincident_power(self):
        self.assertEqual(self.audit(peer=True, native=False)["status"], "INSUFFICIENT")


if __name__ == "__main__":
    unittest.main()
