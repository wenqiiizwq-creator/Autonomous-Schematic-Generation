#!/usr/bin/env python3
"""Read-only KiCad geometry gate. Unsupported objects remain INSUFFICIENT."""

import argparse
import json
from pathlib import Path
from schematic_layout.sexpr import parse
from schematic_layout.scene import read_scene
from schematic_layout.qa import check_scene
from schematic_layout.generate import pin_net_map
from schematic_layout.geometry import Box


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("schematic", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--intent", type=Path)
    ap.add_argument("--layout", type=Path)
    ap.add_argument("--grid-mm", type=float, default=1.27)
    args = ap.parse_args()
    layout = json.loads(args.layout.read_text()) if args.layout else {}
    report = check_scene(
        read_scene(parse(args.schematic.read_text())),
        grid=layout.get("grid_mm", args.grid_mm),
        reserved=[Box(*b) for b in layout["reserved"]]
        if "reserved" in layout
        else None,
        pin_nets=pin_net_map(json.loads(args.intent.read_text()))
        if args.intent
        else None,
    )
    result = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end="")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
