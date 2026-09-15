#!/usr/bin/env python3
"""Generate a bounded single-sheet draft from separate intent/layout JSON.

Zero exit means automated gates passed; native visual review and datasheet
review are still required. Failed runs retain diagnostics and never overwrite
an existing output directory. See references/schematic-generation.md.
"""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from schematic_layout.generate import generate
from schematic_layout.sexpr import dump, form
from schematic_layout.native import verify


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("intent", type=Path)
    ap.add_argument("layout", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--name", default="generated")
    ap.add_argument("--symbol-dir", action="append", default=[])
    ap.add_argument("--kicad-cli")
    ap.add_argument("--reference-contract", type=Path, help="Externally authored source/pin/peripheral contract")
    args = ap.parse_args()
    if not args.name.replace("_", "").replace("-", "").isalnum():
        ap.error("name must be alphanumeric with hyphens/underscores")
    out = args.output_dir.resolve()
    if out.exists():
        ap.error("output directory already exists; choose a new run directory")
    out.mkdir(parents=True)
    result = {
        "status": "INSUFFICIENT",
        "native_render_review": "PENDING",
        "datasheet_review": "PENDING",
    }
    try:
        intent = json.loads(args.intent.read_text())
        layout = json.loads(args.layout.read_text())
        shutil.copyfile(args.intent, out / "electrical_intent.json")
        shutil.copyfile(args.layout, out / "layout_plan.json")
        root, manifest = generate(intent, layout, args.name, args.symbol_dir)
        path = out / (args.name + ".kicad_sch")
        path.write_text(dump(root) + "\n", encoding="utf-8")
        # Bind this project to the exact libraries read, avoiding stale global
        # KiCad path mappings. This changes only the new output project.
        table = form("sym_lib_table", form("version", 7))
        for name, source in manifest["library_sources"].items():
            table.append(
                form(
                    "lib",
                    form("name", name),
                    form("type", "KiCad"),
                    form("uri", source["path"]),
                    form("options", ""),
                    form("descr", ""),
                )
            )
        (out / "sym-lib-table").write_text(dump(table) + "\n")
        (out / (args.name + ".kicad_pro")).write_text("{}\n")
        (out / "generation.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        )
        result["geometry"] = manifest["geometry"]
        result["native"] = verify(path, intent, layout, out / "native", args.kicad_cli, args.reference_contract)
        result["status"] = (
            "AUTOMATED_PASS"
            if result["geometry"]["status"] == result["native"]["status"] == "PASS"
            else "FAIL"
        )
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as e:
        result["status"] = "FAIL"
        result["error"] = str(e)
    (out / "verification.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "report": str(out / "verification.json"),
                "native_render_review": result["native_render_review"],
                "error": result.get("error"),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "AUTOMATED_PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
