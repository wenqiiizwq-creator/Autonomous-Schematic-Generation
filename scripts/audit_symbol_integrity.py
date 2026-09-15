#!/usr/bin/env python3
"""Audit active hierarchy symbols against body ink and native XML; never edit inputs."""
import argparse
import json
from pathlib import Path
from schematic_layout.symbol_integrity import audit_symbols


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("--netlist", type=Path)
    p.add_argument("--project")
    p.add_argument("--exceptions", type=Path)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if args.out.exists() or args.out.is_symlink():
        p.error("Report output already exists; use a fresh path")
    # Missing child inputs must not be replaced by an error report.
    if args.out.suffix.lower() != ".json":
        p.error("Report output must be a new .json file")
    protected = [args.root, args.netlist, args.exceptions]
    if args.out.resolve() in {x.resolve() for x in protected if x}:
        p.error("Report must not replace an input")
    try:
        report = audit_symbols(args.root, args.netlist, args.project,
                               json.loads(args.exceptions.read_text()) if args.exceptions else None)
        if args.out.resolve() in {args.root.resolve().parent / rel for rel in report["file_sha256"]}:
            p.error("Report must not replace a child sheet")
    except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
        report = {"status": "FAIL", "error": str(exc)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "graphics", "physical_pin_count", "error") if k in report}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
