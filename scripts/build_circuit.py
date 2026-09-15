#!/usr/bin/env python3
"""Compile Circuit IR v2, automatically place functional blocks and verify KiCad.

Input is JSON, never executed as Python. Every attempt and the original inputs
are retained. Use a new output directory; see references/circuit-ir.md.
"""

import argparse
import json
from pathlib import Path
import sys
from schematic_layout.circuit_ir import compile_circuit
from schematic_layout.placement import plan_layout
from schematic_layout.generate import generate
from schematic_layout.native import verify
from schematic_layout.sexpr import dump, form
from schematic_layout.change_control import (
    load_baseline,
    electrical_diff,
    retain_placements,
    verify_locked_drawing,
)


def write_json(path, data):
    Path(path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def write_project(out, name, root, libraries):
    path = out / (name + ".kicad_sch")
    path.write_text(dump(root) + "\n", encoding="utf-8")
    (out / (name + ".kicad_pro")).write_text("{}\n")
    table = form("sym_lib_table", form("version", 7))
    for lib, source in sorted(libraries.items()):
        table.append(
            form(
                "lib",
                form("name", lib),
                form("type", "KiCad"),
                form("uri", source["path"]),
                form("options", ""),
                form("descr", ""),
            )
        )
    (out / "sym-lib-table").write_text(dump(table) + "\n")
    return path


def build(document, policy, out, dirs=(), cli=None, baseline_path=None, locks=(), reference_contract=None):
    result = {
        "status": "FAIL",
        "native_render_review": "PENDING",
        "datasheet_review": "PENDING",
        "attempts": [],
    }
    write_json(out / "circuit.json", document)
    write_json(out / "presentation.json", policy)
    intent, compiled = compile_circuit(document, dirs)
    write_json(out / "electrical_intent.json", intent)
    write_json(out / "compiled.json", compiled)
    baseline = None
    if locks and not baseline_path:
        raise ValueError("--lock-block requires --baseline")
    if baseline_path:
        write_json(
            out / "electrical-diff.json",
            electrical_diff(
                json.loads((baseline_path / "electrical_intent.json").read_text()),
                intent,
            ),
        )
        baseline = load_baseline(baseline_path, intent, compiled, locks)
        old_policy = json.loads((baseline_path / "presentation.json").read_text())
        if any(
            old_policy.get("blocks", {}).get(b, {})
            != policy.get("blocks", {}).get(b, {})
            for b in locks
        ):
            raise ValueError("Locked block presentation settings changed")
    attempts = policy.get("max_attempts", 3)
    if not isinstance(attempts, int) or not 1 <= attempts <= 5:
        raise ValueError("max_attempts must be between 1 and 5")
    if policy.get("page_mode", "pack") != "pack":
        raise ValueError("This build entry currently expects page_mode pack")
    for attempt in range(attempts):
        attempt_dir = out / f"attempt-{attempt + 1}"
        attempt_dir.mkdir()
        try:
            layout, planning = plan_layout(intent, compiled, policy, attempt)
            if baseline:
                retain_placements(layout, baseline, planning)
            write_json(attempt_dir / "layout_plan.json", layout)
            write_json(attempt_dir / "planning.json", planning)
            root, manifest = generate(intent, layout, document["design_id"], dirs)
            write_json(attempt_dir / "generation.json", manifest)
            (attempt_dir / "candidate.kicad_sch").write_text(dump(root) + "\n")
            if manifest["geometry"]["status"] != "PASS":
                raise ValueError(
                    "Geometry rejected candidate: "
                    + json.dumps(manifest["geometry"]["findings"])
                )
            if baseline:
                result["locked_blocks"] = verify_locked_drawing(root, baseline)
        except ValueError as e:
            result["attempts"].append(
                {"attempt": attempt + 1, "status": "FAIL", "error": str(e)}
            )
            write_json(attempt_dir / "failure.json", result["attempts"][-1])
            continue
        result["attempts"].append({"attempt": attempt + 1, "status": "GEOMETRY_PASS"})
        path = write_project(
            out, document["design_id"], root, manifest["library_sources"]
        )
        write_json(out / "layout_plan.json", layout)
        write_json(out / "planning.json", planning)
        write_json(out / "generation.json", manifest)
        result["geometry"] = manifest["geometry"]
        result["native"] = verify(path, intent, layout, out / "native", cli, reference_contract)
        result["status"] = (
            "AUTOMATED_PASS" if result["native"]["status"] == "PASS" else "FAIL"
        )
        break
    write_json(out / "verification.json", result)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("circuit", type=Path)
    ap.add_argument("presentation", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--symbol-dir", action="append", default=[])
    ap.add_argument("--kicad-cli")
    ap.add_argument("--reference-contract", type=Path, help="Externally authored source/pin/peripheral contract; failure blocks automated acceptance")
    ap.add_argument("--baseline", type=Path)
    ap.add_argument("--lock-block", action="append", default=[])
    args = ap.parse_args()
    out = args.output_dir.resolve()
    if out.exists():
        ap.error("output directory exists; choose a new directory")
    out.mkdir(parents=True)
    try:
        result = build(
            json.loads(args.circuit.read_text()),
            json.loads(args.presentation.read_text()),
            out,
            args.symbol_dir,
            args.kicad_cli,
            args.baseline,
            args.lock_block,
            args.reference_contract,
        )
    except (ValueError, KeyError, TypeError, OSError) as e:
        result = {
            "status": "FAIL",
            "error": str(e),
            "native_render_review": "PENDING",
            "datasheet_review": "PENDING",
        }
    write_json(out / "verification.json", result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "report": str(out / "verification.json"),
                "error": result.get("error"),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "AUTOMATED_PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
