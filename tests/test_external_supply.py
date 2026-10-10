"""Declared external supplies, PWR_FLAG placement and partially unnamed symbols."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.external_supply import declarations, judge  # noqa: E402
from schematic_layout.pages import page_intents  # noqa: E402
from schematic_layout.symbol_integrity import unnamed_pin_rows  # noqa: E402

INTENT = {
    "components": [{"ref": "J1", "lib_id": "Connector_Generic:Conn_01x03", "value": "HEADER"}],
    "nets": [{"name": "VCC", "pins": ["J1.3", "U1.7"]}, {"name": "GND", "pins": ["J1.2", "U1.3"]}],
    "external_supply": [{"net": "VCC", "pin": "J1.3", "reason": "host header supply"}],
}


def xml(nets):
    body = "".join(f'<net code="{i}" name="{name}">'
                   + "".join(f'<node ref="{r}" pin="{p}" pintype="{t}"/>' for r, p, t in nodes)
                   + "</net>" for i, (name, nodes) in enumerate(nets.items(), 1))
    return f'<export version="E"><components><comp ref="J1"><value>HEADER</value><libsource lib="Connector_Generic" part="Conn_01x03"/></comp></components><libparts><libpart lib="Connector_Generic" part="Conn_01x03"><pins><pin num="1" name="Pin_1" type="passive"/><pin num="2" name="Pin_2" type="passive"/><pin num="3" name="Pin_3" type="passive"/></pins></libpart></libparts><nets>{body}</nets></export>'


class ExternalSupplyTests(unittest.TestCase):
    def run_judge(self, nets, intent=INTENT, aliases=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "n.xml"
            path.write_text(xml(nets), encoding="utf-8")
            return judge(path, intent, aliases if aliases is not None else {"FLGX1": "#FLG1"})

    def test_declared_flag_passes(self):
        r = self.run_judge({"VCC": [("J1", "3", "passive"), ("U1", "7", "power_in"), ("FLGX1", "1", "power_out")],
                            "GND": [("J1", "2", "passive"), ("U1", "3", "power_in")]})
        self.assertEqual(r["status"], "PASS", r)
        self.assertEqual(r["flags"], ["#FLG1"])

    def test_flag_on_undeclared_net_fails(self):
        r = self.run_judge({"VCC": [("J1", "3", "passive"), ("U1", "7", "power_in")],
                            "GND": [("J1", "2", "passive"), ("U1", "3", "power_in"), ("FLGX1", "1", "power_out")]})
        kinds = {e["kind"] for e in r["errors"]}
        self.assertEqual(r["status"], "FAIL")
        self.assertEqual(kinds, {"undeclared_pwr_flag", "missing_pwr_flag"})

    def test_board_power_output_on_declared_net_fails(self):
        r = self.run_judge({"VCC": [("J1", "3", "passive"), ("U1", "7", "power_in"),
                                    ("U9", "2", "power_out"), ("FLGX1", "1", "power_out")]})
        self.assertIn({"kind": "net_has_power_source", "net": "VCC", "sources": ["U9.2"]}, r["errors"])

    def test_duplicate_flags_fail(self):
        r = self.run_judge({"VCC": [("J1", "3", "passive"), ("FLGX1", "1", "power_out"), ("FLGX2", "1", "power_out")]},
                           aliases={"FLGX1": "#FLG1", "FLGX2": "#FLG2"})
        self.assertIn("duplicate_pwr_flag", {e["kind"] for e in r["errors"]})

    def test_no_declaration_and_no_flag_is_not_applicable(self):
        r = self.run_judge({"VCC": [("J1", "3", "passive")]}, intent={"nets": INTENT["nets"]}, aliases={})
        self.assertEqual(r["status"], "NOT_APPLICABLE")

    def test_declaration_must_match_intent_net(self):
        intent = dict(INTENT, external_supply=[{"net": "VCC", "pin": "J1.2", "reason": "wrong pin"}])
        self.assertEqual(declarations(intent)[1][0]["kind"], "declaration_not_in_intent")
        for bad in ([{"net": "VCC", "pin": "J1.3"}], [{"net": "VCC", "pin": "J1.3", "reason": " "}],
                    INTENT["external_supply"] * 2):
            with self.assertRaises(ValueError):
                declarations(dict(INTENT, external_supply=bad))

    def test_page_intent_keeps_declaration_on_connector_page(self):
        board = {"components": [{"ref": "J1", "fields": {"Circuit": "io"}}, {"ref": "U1", "fields": {"Circuit": "amp"}}],
                 "nets": INTENT["nets"], "external_supply": INTENT["external_supply"]}
        pages = page_intents(board, rails=("VCC", "GND"))
        self.assertEqual(pages["io"]["intent"]["external_supply"], INTENT["external_supply"])
        self.assertNotIn("external_supply", pages["amp"]["intent"])


class UnnamedPinTests(unittest.TestCase):
    def rows(self, ref, names):
        return [{"reference": ref, "pin": str(i), "name": n} for i, n in enumerate(names, 1)]

    def test_one_blank_pin_in_named_symbol_is_diagnostic(self):
        # KiCad's AD8494 symbol leaves OUT (pin 6) blank.
        rows = self.rows("U1", ["-IN", "REF", "-VS", "NC", "SENSE", "", "+VS", "+IN"])
        self.assertEqual([(e["reference"], e["pin"]) for e in unnamed_pin_rows(rows)], [("U1", "6")])
        rows[5]["name"] = "~"
        self.assertEqual(len(unnamed_pin_rows(rows)), 1)

    def test_fully_unnamed_and_fully_named_symbols_pass(self):
        rows = self.rows("R1", ["~", "~"]) + self.rows("C1", ["", ""]) + self.rows("J1", ["Pin_1", "Pin_2"])
        self.assertEqual(unnamed_pin_rows(rows), [])


if __name__ == "__main__":
    unittest.main()
