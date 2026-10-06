#!/usr/bin/env python3
"""Compare native before/after XML against an independently authored contract."""
import argparse
import json
from pathlib import Path
from schematic_layout.design_change import verify_change
from verify_design_preflight import verify_preflight


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("baseline")
    p.add_argument("candidate")
    p.add_argument("contract")
    p.add_argument("--out", required=True)
    p.add_argument("--preflight", help="required by the electrical redesign workflow")
    p.add_argument("--artifact-root", help="defaults to preflight manifest parent")
    a = p.parse_args()
    out = Path(a.out)
    if out.exists() or out.is_symlink():
        p.error("Report output already exists; choose a fresh path")
    try:
        contract = json.loads(Path(a.contract).read_text())
        result = verify_change(a.baseline, a.candidate, contract)
        if a.preflight:
            result['preflight'] = verify_preflight(json.loads(Path(a.preflight).read_text()),
                a.artifact_root or Path(a.preflight).parent, contract)
            if result['status'] != 'FAIL' and result['preflight']['status'] != 'PASS':
                result['status'] = 'FAIL' if result['preflight']['status'] == 'FAIL' else 'CONDITIONAL'
    except (ValueError, OSError, KeyError, TypeError) as exc:
        result = {"status": "FAIL", "error": str(exc)}
    if out.resolve() in {Path(x).resolve() for x in [a.baseline, a.candidate, a.contract] + ([a.preflight] if a.preflight else [])}:
        p.error("Report output must not overwrite an input")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"]}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
