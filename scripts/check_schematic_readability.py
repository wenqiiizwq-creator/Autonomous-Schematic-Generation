#!/usr/bin/env python3
"""Measure wiring readability of native .kicad_sch sheets and apply the gate.

Reports segments, bends, different-net crossings, tortuous two-terminal
connections, remaining rail wiring, power symbols and labels per sheet. The
gate covers drawing quality only; it never replaces ERC, netlist identity or
native visual review. See references/human-readable-routing.md.
"""

import argparse
import json
from pathlib import Path
import sys

from schematic_layout.readability import gate, measure
from schematic_layout.sexpr import parse


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sheets", nargs="+", type=Path)
    ap.add_argument("--max-crossings", type=int, default=0)
    ap.add_argument("--max-tortuous", type=int, default=0)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    report = {"sheets": {}}
    for path in args.sheets:
        metrics = measure(parse(path.read_text(encoding="utf-8")))
        report["sheets"][path.name] = {**metrics, "gate": gate(metrics, args.max_crossings, args.max_tortuous)}
    report["status"] = "FAIL" if any(s["gate"]["status"] == "FAIL" for s in report["sheets"].values()) else "PASS"
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
