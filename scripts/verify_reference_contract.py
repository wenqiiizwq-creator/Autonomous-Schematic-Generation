#!/usr/bin/env python3
"""Check a source-bound reference contract against a fresh KiCad XML netlist."""
import argparse
import json
from pathlib import Path
from schematic_layout.reference_contract import verify_reference


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("netlist", type=Path)
    p.add_argument("contract", type=Path)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    if a.out.exists() or a.out.is_symlink() or a.out.suffix.lower() != ".json":
        p.error("Use a fresh .json report path")
    if a.out.resolve() in {a.netlist.resolve(), a.contract.resolve()}:
        p.error("Report must not replace an input")
    try:
        c = json.loads(a.contract.read_text())
        source_paths = {(a.contract.parent / s["path"]).resolve() for s in c.get("sources", {}).values()}
        if a.out.resolve() in source_paths:
            p.error("Report must not replace a source document")
        r = verify_reference(a.netlist, c, a.contract.parent)
    except (ValueError, OSError, KeyError, IndexError, TypeError) as e:
        r = {"status": "FAIL", "error": str(e)}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("x", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: r[k] for k in ("status", "coverage_gaps", "error") if k in r}))
    return 0 if r["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
