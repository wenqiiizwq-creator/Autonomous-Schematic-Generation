#!/usr/bin/env python3
"""Check a source-bound reference contract against a fresh KiCad XML netlist."""
import argparse
import hashlib
import json
from pathlib import Path
from schematic_layout.reference_contract import verify_reference


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("netlist", type=Path)
    p.add_argument("contract", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--source-root", type=Path, help="Native source bound by the reviewed role contract")
    p.add_argument("--source-role-contract", type=Path, help="Reviewed hash-bound pinless roles; no automatic classification")
    p.add_argument("--project", help="Selected native annotation project")
    a = p.parse_args()
    if bool(a.source_root) != bool(a.source_role_contract) or (a.project and not a.source_root):
        p.error("--source-root and --source-role-contract go together; --project requires them")
    if a.out.exists() or a.out.is_symlink() or a.out.suffix.lower() != ".json":
        p.error("Use a fresh .json report path")
    protected = {p.resolve() for p in (a.netlist, a.contract, a.source_root, a.source_role_contract) if p}
    if a.out.resolve() in protected:
        p.error("Report must not replace an input")
    try:
        c = json.loads(a.contract.read_text())
        source_paths = {(a.contract.parent / s["path"]).resolve() for s in c.get("sources", {}).values()}
        if a.out.resolve() in source_paths:
            p.error("Report must not replace a source document")
        roles = json.loads(a.source_role_contract.read_text()) if a.source_role_contract else None
        r = verify_reference(a.netlist, c, a.contract.parent, source_root=a.source_root,
                             source_roles=roles, project=a.project)
        if a.source_role_contract:
            r["source_role_contract"] = {"path": str(a.source_role_contract.resolve()),
                                         "sha256": hashlib.sha256(a.source_role_contract.read_bytes()).hexdigest()}
    except (ValueError, OSError, KeyError, IndexError, TypeError) as e:
        r = {"status": "FAIL", "error": str(e)}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("x", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: r[k] for k in ("status", "coverage_gaps", "error") if k in r}))
    return 0 if r["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
