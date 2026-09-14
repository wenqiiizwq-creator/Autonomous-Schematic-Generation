#!/usr/bin/env python3
"""Execute selected pinned upstream pure modules without installing MCP servers.

Optional source-comparison evidence. Requires downloaded upstream/ and Node
with TypeScript stripping (tested Node 24); does not claim full upstream suites.
"""

import argparse
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.scene import Pin
from schematic_layout.routing import manhattan_mst
from schematic_layout.geometry import Box
from schematic_layout.field_placer import FieldSpec, autoplace_fields


def load_pure(base, name):
    for package in ("upstream_probe", "upstream_probe.utils", "upstream_probe.models"):
        if package not in sys.modules:
            module = types.ModuleType(package)
            module.__path__ = []
            sys.modules[package] = module
    fullname = "upstream_probe." + name
    spec = importlib.util.spec_from_file_location(
        fullname, base / (name.replace(".", "/") + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = module
    spec.loader.exec_module(module)
    return module


def run():
    base = ROOT / "upstream/kicad-mcp-pro/src/kicad_mcp"
    g = load_pure(base, "utils.geometry")
    fp = load_pure(base, "utils.field_placer")
    router = load_pure(base, "utils.schematic_router")
    load_pure(base, "models.contract_verifier")
    qa = load_pure(base, "models.visual_qa")
    body = g.Box(10, 10, 12, 15)
    obstacle = g.Box(0, 0, 100, 100)
    placement = fp.autoplace_fields(
        body, [(11, 8), (11, 17)], [obstacle], [fp.FieldSpec("Value", "10k")]
    )[0]
    overlap = placement.text_field("10k", 1.27).box().overlaps(obstacle)
    local_refused = False
    try:
        autoplace_fields(
            Box(10, 10, 12, 15),
            [(11, 8), (11, 17)],
            [Box(0, 0, 100, 100)],
            [FieldSpec("Value", "10k")],
        )
    except ValueError:
        local_refused = True
    symbol = qa.PlacedSymbol(
        "R1",
        "Device:R",
        30,
        30,
        0,
        g.Box(30, 30, 32, 34),
        (g.TextField("R1", 40, 40), g.TextField("10k", 40, 40)),
    )
    same_owner = qa.detect_text_overlap([symbol], [])
    original_offgrid = router.SchematicRouter(grid_mm=1).route((0.1, 0), (2, 0))
    original_thin = router.SchematicRouter(
        grid_mm=1, obstacles=[router.RouterBBox(0.4, -0.1, 0.6, 0.1)]
    ).route((0, 0), (2, 0))
    rng = random.Random(1729)
    inputs = [
        [
            {"pinId": str(i), "x": rng.randrange(10), "y": rng.randrange(10)}
            for i in range(8)
        ]
        for _ in range(20)
    ]
    module = (
        ROOT
        / "upstream/schematic-trace-solver/lib/solvers/MspConnectionPairSolver/getMspConnectionPairsFromPins.ts"
    )
    source = (
        "import {getOrthogonalMinimumSpanningTree as mst} from "
        + json.dumps(module.as_uri())
        + ";\n"
    )
    source += "console.log(JSON.stringify(" + json.dumps(inputs) + ".map(p=>mst(p))));"
    output = subprocess.check_output(
        ["node", "--experimental-strip-types", "--input-type=module", "-"],
        input=source,
        text=True,
    )
    original = json.loads(output)
    matches = []
    for case, expected in zip(inputs, original):
        pins = [
            Pin(p["pinId"], (p["x"], p["y"]), (0, 0), (1, 0), "passive") for p in case
        ]
        normalize = lambda es: sorted(tuple(sorted(e)) for e in es)
        matches.append(normalize(expected) == normalize(manhattan_mst(pins)))
    assert all(matches) and overlap and local_refused and not same_owner
    return {
        "source_commits": {
            name: subprocess.check_output(
                ["git", "-C", str(ROOT / "upstream" / name), "rev-parse", "HEAD"],
                text=True,
            ).strip()
            for name in ("schematic-trace-solver", "kicad-mcp-pro")
        },
        "executed_scope": "Selected pure source modules only; full upstream pipelines/suites not executed",
        "mst_source_comparison": {"cases": len(matches), "matched": sum(matches)},
        "observed_upstream_boundaries": {
            "all_field_candidates_blocked_returns_overlap": overlap,
            "local_placer_rejects_same_case": local_refused,
            "same_owner_text_overlap_findings": len(same_owner),
            "off_grid_original_route": original_offgrid,
            "thin_obstacle_original_route": original_thin,
        },
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    report = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
