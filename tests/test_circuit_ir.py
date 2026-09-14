"""IR/compiler, automatic placement, imports and protected regeneration regressions."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.circuit_ir import compile_circuit
from schematic_layout.placement import plan_layout
from schematic_layout.generate import generate, library_dirs
from schematic_layout.native import find_cli, compare_netlist
from schematic_layout.sexpr import all_nodes, value, dump
from schematic_layout.importers import circuit_synth_to_ir
from schematic_layout.change_control import electrical_diff, load_baseline
from build_circuit import build

FIX = ROOT / "tests/fixtures/generation"


def fixture(name="dual_filter"):
    return tuple(
        json.loads((FIX / f"{name}.{kind}.json").read_text())
        for kind in ("circuit", "presentation")
    )


@unittest.skipUnless(library_dirs(), "KiCad symbol libraries absent")
class CircuitIRTests(unittest.TestCase):
    def test_reuse_parameters_ports_and_input_order(self):
        doc, policy = fixture()
        doc["root"]["instances"][1]["parameters"] = {"resistance": "22k"}
        intent, compiled = compile_circuit(doc)
        self.assertEqual(
            {c["ref"]: c["value"] for c in intent["components"]}["R2"], "22k"
        )
        self.assertEqual(
            next(n["pins"] for n in intent["nets"] if n["name"] == "GND"),
            ["C1.2", "C2.2"],
        )
        a, _ = plan_layout(intent, compiled, policy)
        doc["root"]["instances"].reverse()
        doc["modules"]["rc"]["components"].reverse()
        doc["modules"]["rc"]["nets"].reverse()
        other, compilation = compile_circuit(doc)
        b, _ = plan_layout(other, compilation, policy)
        self.assertEqual(intent, other)
        self.assertEqual(a, b)
        self.assertEqual(
            dump(generate(intent, a, doc["design_id"])[0]),
            dump(generate(other, b, doc["design_id"])[0]),
        )

    def test_local_nets_do_not_merge_between_instances(self):
        doc, _ = fixture()
        doc["modules"]["rc"]["ports"].remove("OUT")
        doc["root"]["nets"] = [
            n for n in doc["root"]["nets"] if not n["name"].startswith("OUT")
        ]
        for inst in doc["root"]["instances"]:
            del inst["bindings"]["OUT"]
        intent, _ = compile_circuit(doc)
        nets = {n["name"]: n["pins"] for n in intent["nets"]}
        self.assertIn("filter_a__OUT", nets)
        self.assertFalse(set(nets["filter_a__OUT"]) & set(nets["filter_b__OUT"]))

    def test_bad_port_pin_duplicate_reference_and_unknown_options(self):
        mutations = [
            lambda d: d["root"]["instances"][0]["bindings"].pop("OUT"),
            lambda d: d["root"]["instances"][0]["bindings"].update(OUT="TYPO"),
            lambda d: d["modules"]["rc"]["nets"][0]["pins"].append("series.99"),
            lambda d: d["references"].update({"filter_b/series": "R1"}),
            lambda d: d["modules"]["rc"]["components"][0].update(footprit="typo"),
            lambda d: d["modules"]["rc"]["nets"][0]["pins"].append("series.1"),
            lambda d: d["root"]["instances"][0].update(parameters={"unknown": 42}),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                doc, _ = fixture()
                mutation(doc)
                with self.assertRaises(ValueError):
                    compile_circuit(doc)

    def test_unassigned_pin_is_not_automatically_nc(self):
        doc, _ = fixture()
        doc["modules"]["rc"]["nets"][0]["pins"].remove("series.1")
        with self.assertRaisesRegex(ValueError, "Unassigned pins"):
            compile_circuit(doc)

    def test_recursive_module_and_namespace_collision_rejected(self):
        doc, _ = fixture()
        doc["modules"]["rc"]["instances"] = [
            {
                "id": "again",
                "module": "rc",
                "bindings": {n: n for n in ("IN", "OUT", "GND")},
            }
        ]
        with self.assertRaisesRegex(ValueError, "recursive"):
            compile_circuit(doc)
        doc, _ = fixture()
        doc["modules"]["rc"]["ports"].remove("OUT")
        doc["root"]["nets"] = [
            n for n in doc["root"]["nets"] if not n["name"].startswith("OUT")
        ]
        doc["root"]["nets"].append({"name": "filter_a__OUT", "pins": []})
        for inst in doc["root"]["instances"]:
            del inst["bindings"]["OUT"]
        with self.assertRaisesRegex(ValueError, "collision"):
            compile_circuit(doc)

    def test_exact_pin_names_require_explicit_ambiguous_group(self):
        doc, _ = fixture("multiunit")
        doc["root"]["no_connect"] = [
            p for p in doc["root"]["no_connect"] if p not in ("amp.3", "amp.5")
        ]
        doc["root"]["nets"] = [
            {"name": "PLUS", "pins": [{"component": "amp", "pin_name": "+"}]}
        ]
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            compile_circuit(doc)
        doc["root"]["nets"][0]["pins"][0]["all"] = True
        intent, _ = compile_circuit(doc)
        self.assertEqual(intent["nets"][0]["pins"], ["U1.3", "U1.5"])

    def test_symbol_lock_and_bus_members(self):
        doc, _ = fixture()
        doc["root"]["buses"] = [{"name": "CHANNEL_IN", "members": ["IN_A", "IN_B"]}]
        _, compiled = compile_circuit(doc)
        self.assertEqual(
            next(h for h in compiled["hierarchy"] if h["path"] == "")["buses"][0][
                "members"
            ],
            ["IN_A", "IN_B"],
        )
        doc["modules"]["rc"]["components"][0]["symbol_sha256"] = "bad"
        with self.assertRaisesRegex(ValueError, "symbol hash changed"):
            compile_circuit(doc)
        self.assertIn("filter_a/input", compiled["resolved_components"])
        doc, _ = fixture()
        doc["root"]["buses"] = [{"name": "DATA", "members": ["IN_A", "TYPO"]}]
        with self.assertRaisesRegex(ValueError, "undeclared scalar"):
            compile_circuit(doc)

    def test_automatic_field_budget_grows_and_packing_fails_safely(self):
        doc, policy = fixture("capacitor_bank")
        intent, compiled = compile_circuit(doc)
        layout, _ = plan_layout(intent, compiled, policy)
        self.assertLess(
            layout["placements"]["C2"]["at"][0], layout["placements"]["C3"]["at"][0]
        )
        self.assertGreater(
            layout["placements"]["C5"]["at"][1], layout["placements"]["C4"]["at"][1]
        )
        doc["root"]["components"][0]["value"] = "VeryLongCapacitorValue_10u_50V_X7R"
        longer, comp2 = compile_circuit(doc)
        wider, _ = plan_layout(longer, comp2, policy)
        self.assertGreater(
            max(p["at"][0] for p in wider["placements"].values()),
            max(p["at"][0] for p in layout["placements"].values()),
        )
        for c in doc["root"]["components"]:
            c["value"] = "W" * 2000
        huge, comp3 = compile_circuit(doc)
        with self.assertRaisesRegex(ValueError, "do not fit"):
            plan_layout(huge, comp3, {**policy, "papers": ["A4"]})

    def test_multiunit_views_and_template_contracts(self):
        doc, policy = fixture("multiunit")
        intent, compiled = compile_circuit(doc)
        self.assertEqual(intent["components"][0]["units"], [1, 2, 3])
        layout, _ = plan_layout(intent, compiled, policy)
        self.assertEqual(set(layout["placements"]), {"U1:1", "U1:2", "U1:3"})
        _, manifest = generate(intent, layout, doc["design_id"])
        self.assertEqual(manifest["geometry"]["status"], "PASS")
        doc, policy = fixture()
        intent, compiled = compile_circuit(doc)
        policy["blocks"]["filter_a"]["template"] = "ldo"
        with self.assertRaisesRegex(ValueError, "unsupported"):
            plan_layout(intent, compiled, policy)
        policy["nets"]["TYPO"] = {"label": True}
        with self.assertRaisesRegex(ValueError, "unknown net"):
            plan_layout(intent, compiled, policy)

    def test_stable_uuid_and_electrical_diff_on_parameter_change(self):
        doc, policy = fixture()
        before, c1 = compile_circuit(doc)
        l1, _ = plan_layout(before, c1, policy)
        root1, _ = generate(before, l1, doc["design_id"])
        doc["root"]["instances"][1]["parameters"] = {"resistance": "2k"}
        after, c2 = compile_circuit(doc)
        l2, _ = plan_layout(after, c2, policy)
        root2, _ = generate(after, l2, doc["design_id"])
        self.assertEqual(
            [value(s, "uuid") for s in all_nodes(root1, "symbol")],
            [value(s, "uuid") for s in all_nodes(root2, "symbol")],
        )
        diff = electrical_diff(before, after)
        self.assertEqual([c["id"] for c in diff["components"]], ["filter_b/series"])
        self.assertEqual(diff["pins"], [])


class ImportTests(unittest.TestCase):
    def test_circuit_synth_formats_scopes_and_missing_symbol(self):
        source = {"name": "root", "components": {}, "nets": {}, "subcircuits": []}
        for name, ref in (("a", "R1"), ("b", "R2")):
            source["subcircuits"].append(
                {
                    "name": name,
                    "components": {
                        ref: {"symbol": "Device:R", "value": "1k", "footprint": ""}
                    },
                    "nets": {
                        "TOP": [{"component": ref, "pin": {"number": "1"}}],
                        "BOTTOM": {
                            "nodes": [{"component": ref, "pin": {"number": "2"}}],
                            "is_power": True,
                        },
                    },
                }
            )
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            circuit_synth_to_ir(source, "imported")
        doc, audit = circuit_synth_to_ir(
            source, "imported", shared_nets=["BOTTOM"], local_nets=["TOP"]
        )
        self.assertEqual(audit["shared_nets"], ["BOTTOM"])
        if library_dirs():
            intent, _ = compile_circuit(doc)
            self.assertEqual(
                next(n["pins"] for n in intent["nets"] if n["name"] == "BOTTOM"),
                ["R1.2", "R2.2"],
            )
            self.assertEqual(len(intent["nets"]), 3)
        source["subcircuits"][0]["components"]["R1"]["symbol"] = ""
        with self.assertRaisesRegex(ValueError, "missing library"):
            circuit_synth_to_ir(
                source, "imported", shared_nets=["BOTTOM"], local_nets=["TOP"]
            )


@unittest.skipUnless(find_cli() and library_dirs(), "Native KiCad unavailable")
class NativeCircuitTests(unittest.TestCase):
    def test_templates_native_identity_and_mutated_dnp_mpn_rejected(self):
        for name in ("dual_filter", "multiunit", "capacitor_bank"):
            with self.subTest(fixture=name), tempfile.TemporaryDirectory() as tmp:
                doc, policy = fixture(name)
                out = Path(tmp)
                result = build(doc, policy, out)
                self.assertEqual(result["status"], "AUTOMATED_PASS", result)
                if name == "capacitor_bank":
                    intent = json.loads((out / "electrical_intent.json").read_text())
                    intent["components"][0]["mpn"] = "WRONG_PART"
                    intent["components"][-1]["dnp"] = not intent["components"][-1][
                        "dnp"
                    ]
                    comparison = compare_netlist(out / "native/netlist.xml", intent)
                    self.assertEqual(comparison["status"], "FAIL")
                    self.assertIn(
                        "assembly_state_mismatch",
                        {e["kind"] for e in comparison["errors"]},
                    )

    def test_protected_regeneration_and_baseline_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, new = Path(tmp) / "baseline", Path(tmp) / "new"
            base.mkdir()
            new.mkdir()
            doc, policy = fixture()
            first = build(doc, policy, base)
            self.assertEqual(first["status"], "AUTOMATED_PASS", first)
            doc["root"]["instances"][1]["parameters"] = {"resistance": "2k"}
            result = build(doc, policy, new, baseline_path=base, locks=["filter_a"])
            self.assertEqual(result["status"], "AUTOMATED_PASS", result)
            self.assertEqual(result["locked_blocks"][0]["status"], "UNCHANGED")
            intent, compiled = compile_circuit(doc)
            doc["root"]["instances"][0]["parameters"] = {"resistance": "3k"}
            altered, compilation = compile_circuit(doc)
            with self.assertRaisesRegex(ValueError, "electrical content changed"):
                load_baseline(base, altered, compilation, ["filter_a"])
            schematic = base / (doc["design_id"] + ".kicad_sch")
            schematic.write_text(schematic.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "changed since native"):
                load_baseline(base, intent, compiled, ["filter_a"])


if __name__ == "__main__":
    unittest.main()
