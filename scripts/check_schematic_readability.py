#!/usr/bin/env python3
"""Measure wiring readability of native .kicad_sch sheets and apply the gate.

Reports segments, bends, different-net crossings, tortuous two-terminal
connections (with their locations), remaining rail wiring, power symbols and
labels per sheet. The gate is mandatory for generated or redrawn sheets: zero
crossings and zero two-terminal connections with three or more bends, unless a
waiver file names the sheet, the allowed count and a reason. It covers drawing
quality only; it never replaces ERC, netlist identity or native visual review.
See references/human-readable-routing.md.
"""

import argparse
import json
from pathlib import Path
import sys

from schematic_layout.readability import gate, measure
from schematic_layout.sexpr import parse


def load_waivers(path):
    """{"sheet.kicad_sch": {"cross_net_crossings": 1, "reason": "..."}}"""
    waivers = json.loads(path.read_text(encoding="utf-8")) if path else {}
    for sheet, w in waivers.items():
        if set(w) - {"cross_net_crossings", "tortuous_connections", "reason"} or not str(w.get("reason", "")).strip():
            raise SystemExit(f"{sheet}: a waiver needs allowed counts and a nonempty reason")
    return waivers


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sheets", nargs="+", type=Path)
    ap.add_argument("--max-crossings", type=int, default=0)
    ap.add_argument("--max-tortuous", type=int, default=0)
    ap.add_argument("--waivers", type=Path, help="JSON: per-sheet allowed counts with a reason")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    waivers = load_waivers(args.waivers)
    report = {"sheets": {}}
    for path in args.sheets:
        metrics = measure(parse(path.read_text(encoding="utf-8")))
        w = waivers.get(path.name, {})
        result = gate(metrics, w.get("cross_net_crossings", args.max_crossings),
                      w.get("tortuous_connections", args.max_tortuous))
        if w:
            result["waiver"] = w
        report["sheets"][path.name] = {**metrics, "gate": result}
    unused = sorted(set(waivers) - {p.name for p in args.sheets})
    if unused:
        report["unused_waivers"] = unused
    report["status"] = "FAIL" if any(s["gate"]["status"] == "FAIL" for s in report["sheets"].values()) else "PASS"
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
