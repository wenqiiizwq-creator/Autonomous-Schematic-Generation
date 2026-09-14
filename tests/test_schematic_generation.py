"""Behavioral regressions: failure examples, native connectivity and rendering.

Run: python3 -m unittest discover -s tests -v
Native tests are explicit skips when KiCad/official symbol libraries are absent.
"""

import copy
import itertools
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.geometry import Box, TextField, text_extent
from schematic_layout.field_placer import FieldSpec, autoplace_fields
from schematic_layout.routing import (
    route,
    manhattan_mst,
    normalize_wires,
    segment_hits_box,
)
from schematic_layout.scene import Scene, Symbol, Pin, read_scene
from schematic_layout.qa import check_scene
from schematic_layout.sexpr import parse, dump, form, Atom, first, all_nodes, set_node
from schematic_layout.generate import generate, library_dirs
from schematic_layout.native import find_cli, compare_netlist

FIXTURES = ROOT / "tests/fixtures/generation"


def fixture():
    return (
        json.loads((FIXTURES / "rc_filter.intent.json").read_text()),
        json.loads((FIXTURES / "rc_filter.layout.json").read_text()),
    )


def codes(scene, **kwargs):
    return {f["code"] for f in check_scene(scene, **kwargs)["findings"]}


class GeometryTests(unittest.TestCase):
    def test_quoted_atoms_round_trip(self):
        text = (
            '(root (property "01" "a \\"quote\\" and \\\\ path") (x 1.27) (z "你好"))'
        )
        node = parse(text)
        self.assertEqual(parse(dump(node)), node)
        self.assertNotIsInstance(node[1][1], Atom)
        self.assertIsInstance(node[2][1], Atom)

    def test_malformed_sexpr_rejected(self):
        for raw in ("(a", "(a))", "(a)(b)", '(a "unfinished)', "(a) garbage"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse(raw)

    def test_multiline_and_cjk_extent(self):
        self.assertGreater(text_extent("电源")[0], text_extent("ab")[0])
        self.assertGreater(text_extent("10u\n50V")[1], text_extent("10u")[1])

    def test_rotated_justification_before_rotation(self):
        f = TextField("LONG", 10, 20, 90, 1, justify=frozenset({"left", "bottom"}))
        self.assertAlmostEqual(f.box().y_max, 20)
        self.assertAlmostEqual(f.box().x_max, 10)
        self.assertGreater(f.box().height, f.box().width)

    def test_placer_refuses_fully_blocked(self):
        with self.assertRaisesRegex(ValueError, "No collision-free"):
            autoplace_fields(
                Box(10, 10, 12, 15),
                [(11, 8), (11, 17)],
                [Box(0, 0, 100, 100)],
                [FieldSpec("Value", "10k")],
            )

    def test_placer_prefers_clear_pin_side_over_overlap(self):
        body = Box(10, 10, 12, 15)
        block = [Box(0, 10, 9.9, 15), Box(12.1, 10, 40, 15)]
        specs = [FieldSpec("Reference", "R1"), FieldSpec("Value", "10k")]
        placements = autoplace_fields(body, [(11, 8), (11, 17)], block, specs)
        for s, p in zip(specs, placements):
            self.assertFalse(
                any(
                    p.text_field(s.text, s.font_mm).box().overlaps(o)
                    for o in [body, *block]
                )
            )

    def test_same_symbol_reference_value_overlap_detected(self):
        scene = Scene(
            Box(0, 0, 297, 210),
            symbols=[
                Symbol(
                    "R1",
                    "Device:R",
                    1,
                    [],
                    Box(30, 30, 32, 34),
                    [],
                    [
                        ("Reference", TextField("R1", 40, 40)),
                        ("Value", TextField("10k", 40, 40)),
                    ],
                )
            ],
        )
        self.assertIn("text_overlap", codes(scene))

    def test_wire_body_and_text_crossings(self):
        scene = Scene(
            Box(0, 0, 297, 210),
            symbols=[
                Symbol(
                    "U1",
                    "Test:X",
                    1,
                    [],
                    Box(40, 40, 50, 50),
                    [],
                    [("Value", TextField("LONG", 60, 45))],
                )
            ],
            wires=[((30, 45), (70, 45))],
        )
        self.assertTrue({"wire_body", "wire_text"} <= codes(scene))

    def test_offsheet_extent_and_title_intrusion(self):
        scene = Scene(
            Box(0, 0, 297, 210),
            labels=[
                ("text", TextField("VERY_LONG_VALUE", 292, 50)),
                ("text", TextField("TITLE_COLLISION", 230, 185)),
            ],
        )
        self.assertTrue({"off_page", "reserved_region"} <= codes(scene))

    def test_missing_cache_cannot_pass(self):
        scene = read_scene(
            parse(
                '(kicad_sch (paper "A4") (symbol (lib_id "Missing:X") (at 50 50 0) (unit 1)))'
            )
        )
        self.assertEqual(check_scene(scene)["status"], "INSUFFICIENT")

    def test_different_net_t_contact(self):
        pins = [
            Pin("R1.1", (20, 20), (20, 18), (0, 1), "passive"),
            Pin("R2.1", (30, 30), (30, 32), (0, -1), "passive"),
        ]
        scene = Scene(
            Box(0, 0, 297, 210),
            symbols=[Symbol("X", "X:X", 1, [], None, pins, [])],
            wires=[((20, 20), (40, 20)), ((30, 20), (30, 30))],
        )
        self.assertIn(
            "different_net_contact",
            codes(scene, grid=1, pin_nets={"R1.1": "A", "R2.1": "B"}),
        )

    def test_undotted_crossing_is_not_declared_short(self):
        scene = Scene(
            Box(0, 0, 297, 210), wires=[((20, 30), (40, 30)), ((30, 20), (30, 40))]
        )
        found = codes(scene, grid=1)
        self.assertIn("wire_crossing", found)
        self.assertNotIn("different_net_contact", found)

    def test_straight_wire_between_pins_not_orphan(self):
        pins = [
            Pin("R1.1", (20, 20), (20, 18), (0, 1), "passive"),
            Pin("R2.1", (20, 30), (20, 32), (0, -1), "passive"),
        ]
        scene = Scene(
            Box(0, 0, 297, 210),
            symbols=[Symbol("X", "X:X", 1, [], None, pins, [])],
            wires=[((20, 20), (20, 30))],
        )
        self.assertNotIn("orphan_wire", codes(scene, grid=1))


class RoutingTests(unittest.TestCase):
    def test_mst_stable_and_minimum_cost_against_kruskal(self):
        rng = random.Random(1729)
        for _ in range(20):
            ps = [
                Pin(
                    str(i),
                    (rng.randrange(8), rng.randrange(8)),
                    (0, 0),
                    (1, 0),
                    "passive",
                )
                for i in range(8)
            ]
            result = manhattan_mst(ps)
            self.assertEqual(result, manhattan_mst(list(reversed(ps))))
            lookup = {p.id: p.point for p in ps}
            dist = lambda a, b: sum(abs(x - y) for x, y in zip(lookup[a], lookup[b]))
            parents = {p.id: p.id for p in ps}

            def root(a):
                while parents[a] != a:
                    a = parents[a]
                return a

            cost = 0
            for d, a, b in sorted(
                (dist(a, b), a, b) for a, b in itertools.combinations(lookup, 2)
            ):
                if root(a) != root(b):
                    parents[root(a)] = root(b)
                    cost += d
            self.assertEqual(sum(dist(a, b) for a, b in result), cost)
            self.assertEqual(len(result), len(ps) - 1)

    def test_duplicate_pin_id_rejected(self):
        p = Pin("A", (0, 0), (0, 0), (1, 0), "passive")
        with self.assertRaises(ValueError):
            manhattan_mst([p, p])

    def test_thin_obstacle_between_grid_nodes_is_avoided(self):
        box = Box(0.4, -0.1, 0.6, 0.1)
        path = route((0, 0), (2, 0), [box], Box(-2, -2, 4, 4), 1)
        self.assertTrue(
            all(not segment_hits_box(a, b, box) for a, b in zip(path, path[1:]))
        )
        self.assertGreater(len(path), 2)

    def test_terminal_not_snapped_or_exempted(self):
        with self.assertRaisesRegex(ValueError, "Off-grid"):
            route((0.1, 0), (2, 0), [], Box(-2, -2, 4, 4), 1)
        with self.assertRaisesRegex(ValueError, "obstructed"):
            route((0, 0), (2, 0), [Box(-1, -1, 1, 1)], Box(-2, -2, 4, 4), 1)

    def test_pin_exit_directions(self):
        path = route(
            (0, 0), (4, 0), [], Box(-3, -3, 8, 8), 1, start_dir=(0, -1), end_dir=(0, 1)
        )
        self.assertLess(path[1][1], path[0][1])
        self.assertGreater(path[-2][1], path[-1][1])

    def test_failed_route_is_bounded(self):
        with self.assertRaisesRegex(ValueError, "Unrouted"):
            route(
                (0, 0), (4, 0), [Box(1, -5, 3, 5)], Box(-1, -4, 5, 4), 1, max_states=100
            )

    def test_t_junction_normalization_and_same_net_dedup(self):
        wires = [("A", (0, 0), (10, 0)), ("A", (5, 0), (5, 5)), ("A", (0, 0), (5, 0))]
        segments, dots = normalize_wires(wires)
        self.assertEqual(len(segments), 3)
        self.assertEqual(dots, [(5, 0)])

    def test_cross_net_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError, "Different nets"):
            normalize_wires([("A", (0, 0), (10, 0)), ("B", (4, 0), (8, 0))])


@unittest.skipUnless(library_dirs(), "KiCad symbol libraries unavailable")
class GenerationTests(unittest.TestCase):
    def test_empty_design_and_unknown_layout_policy_rejected(self):
        intent, layout = fixture()
        with self.assertRaisesRegex(ValueError, "nonempty"):
            generate(
                {"schema_version": 1, "components": [], "nets": []},
                {"schema_version": 1, "placements": {}},
                "bad",
            )
        layout["nets"]["GND"]["lable"] = True
        with self.assertRaisesRegex(ValueError, "unknown routing"):
            generate(intent, layout, "bad")

    def test_deterministic_generation_and_pin_coverage(self):
        intent, layout = fixture()
        root, a = generate(intent, layout, "probe")
        root2, b = generate(intent, layout, "probe")
        self.assertEqual(dump(root), dump(root2))
        self.assertEqual(a, b)
        self.assertEqual(a["geometry"]["status"], "PASS")
        del intent["nets"][0]["pins"][0]
        with self.assertRaisesRegex(ValueError, "Pin coverage"):
            generate(intent, layout, "bad")

    def test_overlap_layout_cannot_generate(self):
        intent, layout = fixture()
        layout["placements"]["R1"]["at"] = layout["placements"]["C1"]["at"]
        with self.assertRaisesRegex(ValueError, "overlap"):
            generate(intent, layout, "bad")

    def test_unsupported_multi_unit_not_flattened(self):
        intent = {
            "schema_version": 1,
            "components": [
                {"ref": "U1", "lib_id": "Amplifier_Operational:LM358", "value": "LM358"}
            ],
            "nets": [],
        }
        layout = {"schema_version": 1, "placements": {"U1": {"at": [50.8, 50.8]}}}
        with self.assertRaisesRegex(ValueError, "multi-unit"):
            generate(intent, layout, "bad")

    def test_explicit_label_connections(self):
        intent, layout = fixture()
        layout["nets"]["GND"] = {"mode": "labels"}
        root, report = generate(intent, layout, "labels")
        self.assertEqual(report["geometry"]["status"], "PASS")
        self.assertEqual(len([n for n in all_nodes(root, "label") if n[1] == "GND"]), 3)


@unittest.skipUnless(
    find_cli() and library_dirs(), "Native KiCad CLI/libraries unavailable"
)
class NativeTests(unittest.TestCase):
    def run_generator(self, intent, layout, folder, name):
        ip = folder / (name + ".intent.json")
        lp = folder / (name + ".layout.json")
        ip.write_text(json.dumps(intent))
        lp.write_text(json.dumps(layout))
        output = folder / name
        p = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/generate_schematic.py"),
                str(ip),
                str(lp),
                "--output-dir",
                str(output),
                "--name",
                name,
            ],
            capture_output=True,
            text=True,
            timeout=90,
        )
        report = json.loads((output / "verification.json").read_text())
        compact = {k: v for k, v in report.items() if k != "native"}
        compact["native"] = {
            k: v for k, v in report.get("native", {}).items() if k != "commands"
        }
        self.assertEqual(
            p.returncode, 0, json.dumps(compact, ensure_ascii=False)[:6000]
        )
        self.assertEqual(report["native"]["netlist"]["status"], "PASS")
        self.assertEqual(report["native"]["erc"]["violations"], [])
        return output

    def test_native_rc_and_remote_label_topologies(self):
        with tempfile.TemporaryDirectory() as td:
            intent, layout = fixture()
            folder = Path(td)
            out = self.run_generator(intent, layout, folder, "rc")
            # Native verifier must reject an open and a short in the intended
            # partitions, even when all references and pin counts stay equal.
            broken = copy.deepcopy(intent)
            broken["nets"][0]["pins"], broken["nets"][1]["pins"] = (
                broken["nets"][0]["pins"] + ["C1.1"],
                ["R1.2", "J2.1"],
            )
            self.assertEqual(
                compare_netlist(out / "native/netlist.xml", broken, layout)["status"],
                "FAIL",
            )
            layout["nets"]["GND"] = {"mode": "labels"}
            self.run_generator(intent, layout, folder, "labels")

    def test_native_unnamed_direct_wire_and_unsplit_t(self):
        with tempfile.TemporaryDirectory() as td:
            intent, layout = fixture()
            out = self.run_generator(intent, layout, Path(td), "plain")
            path = out / "plain.kicad_sch"
            root = parse(path.read_text())
            root[:] = [n for n in root if not (isinstance(n, list) and n[0] == "label")]
            # Collapse the split horizontal output rail around its capacitor T
            # while retaining the junction and the branch.
            wires = all_nodes(root, "wire")
            pair = []
            for w in wires:
                pts = all_nodes(first(w, "pts"), "xy")
                if (
                    all(abs(float(p[2]) - 63.5) < 1e-6 for p in pts)
                    and min(float(p[1]) for p in pts) > 70
                ):
                    pair.append(w)
            # Labels may add split points. The connectivity probe requires a
            # contiguous rail with a T, not a particular label segmentation.
            self.assertGreaterEqual(len(pair), 2)
            intervals = sorted(sorted(float(p[1]) for p in all_nodes(first(w, "pts"), "xy")) for w in pair)
            for a, b in zip(intervals, intervals[1:]):
                self.assertAlmostEqual(a[1], b[0])
            xs = [float(p[1]) for w in pair for p in all_nodes(first(w, "pts"), "xy")]
            set_node(
                pair[0], "pts", form("xy", min(xs), 63.5), form("xy", max(xs), 63.5)
            )
            for segment in pair[1:]:
                root.remove(segment)
            path.write_text(dump(root))
            xml = out / "unnamed.xml"
            p = subprocess.run(
                [
                    find_cli(),
                    "sch",
                    "export",
                    "netlist",
                    "--format",
                    "kicadxml",
                    "-o",
                    str(xml),
                    str(path),
                ],
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(p.returncode, 0)
            self.assertEqual(compare_netlist(xml, intent)["status"], "PASS")

    def test_native_rotations_and_mirrors_preserve_pin_numbers(self):
        with tempfile.TemporaryDirectory() as td:
            intent = {
                "schema_version": 1,
                "title": "Rotation and mirror native probe",
                "components": [],
                "nets": [],
            }
            layout = {"schema_version": 1, "paper": "A3", "placements": {}, "nets": {}}
            for i, (angle, mirror) in enumerate(
                itertools.product((0, 90, 180, 270), ("", "x", "y")), 1
            ):
                ref = f"R{i}"
                intent["components"].append(
                    {
                        "ref": ref,
                        "lib_id": "Device:R",
                        "value": "TEST_VALUE_100k",
                        "footprint": "",
                    }
                )
                layout["placements"][ref] = {
                    "at": [50.8 + ((i - 1) % 4) * 76.2, 50.8 + ((i - 1) // 4) * 63.5],
                    "rotation": angle,
                    "mirror": mirror,
                }
                name = f"N{i}"
                intent["nets"].append(
                    {"name": name, "pins": [f"{ref}.1", f"R{(i % 12) + 1}.2"]}
                )
                layout["nets"][name] = {"mode": "labels"}
            out = self.run_generator(intent, layout, Path(td), "transforms")
            # Inspect actual native PDF text bounds, not just stored field
            # angles. This catches the rotated/mirrored justification failure
            # that a model-only geometry checker can otherwise miss.
            if shutil.which("pdftotext"):
                bbox = out / "native/bbox.html"
                subprocess.run(
                    [
                        "pdftotext",
                        "-bbox",
                        str(out / "native/schematic.pdf"),
                        str(bbox),
                    ],
                    check=True,
                    capture_output=True,
                )
                words = [
                    w
                    for w in ET.parse(bbox).getroot().iter()
                    if w.tag.endswith("word") and w.text == "TEST_VALUE_100k"
                ]
                self.assertEqual(len(words), 12)
                boxes = [
                    Box(
                        *(
                            float(w.attrib[k]) * 25.4 / 72
                            for k in ("xMin", "yMin", "xMax", "yMax")
                        )
                    )
                    for w in words
                ]
                for box in boxes:
                    self.assertGreater(
                        box.width, box.height, "Value rendered vertically"
                    )
                scene = read_scene(parse((out / "transforms.kicad_sch").read_text()))
                for symbol in scene.symbols:
                    value_field = next(
                        f for name, f in symbol.fields if name == "Value"
                    )
                    actual = min(
                        boxes,
                        key=lambda b: (
                            (b.center[0] - value_field.x) ** 2
                            + (b.center[1] - value_field.y) ** 2
                        ),
                    )
                    if (
                        value_field.y > symbol.body.y_min
                        and value_field.y < symbol.body.y_max
                        and value_field.x > symbol.body.x_max
                    ):
                        self.assertGreater(
                            actual.x_min,
                            symbol.body.x_max,
                            "Mirrored value intrudes into body",
                        )


if __name__ == "__main__":
    unittest.main()
