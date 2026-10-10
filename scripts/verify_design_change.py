#!/usr/bin/env python3
"""Compare native before/after XML against an independently authored contract."""
import argparse
import hashlib
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
    for prefix in ("baseline-", ""):
        p.add_argument("--" + prefix + "source-root", type=Path)
        p.add_argument("--" + prefix + "source-role-contract", type=Path)
        p.add_argument("--" + prefix + "project")
    a = p.parse_args()
    for prefix in ("baseline_", ""):
        root, roles, project = (getattr(a, prefix + key) for key in ("source_root", "source_role_contract", "project"))
        if bool(root) != bool(roles) or (project and not root):
            p.error("Each --source-root/--source-role-contract pair is independent; --project requires that pair")
    out = Path(a.out)
    if out.exists() or out.is_symlink():
        p.error("Report output already exists; choose a fresh path")
    protected = [a.baseline, a.candidate, a.contract, a.preflight, a.baseline_source_root,
                 a.source_root, a.baseline_source_role_contract, a.source_role_contract]
    if out.resolve() in {Path(x).resolve() for x in protected if x}:
        p.error("Report output must not overwrite an input")
    try:
        contract = json.loads(Path(a.contract).read_text())
        before_roles = json.loads(a.baseline_source_role_contract.read_text()) if a.baseline_source_role_contract else None
        after_roles = json.loads(a.source_role_contract.read_text()) if a.source_role_contract else None
        result = verify_change(a.baseline, a.candidate, contract,
                               before_source_root=a.baseline_source_root, before_source_roles=before_roles,
                               before_project=a.baseline_project, after_source_root=a.source_root,
                               after_source_roles=after_roles, after_project=a.project)
        if a.baseline_source_role_contract or a.source_role_contract:
            result["source_role_contracts"] = {key: {"path": str(path.resolve()),
                                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                                            for key, path in (("baseline", a.baseline_source_role_contract),
                                                              ("candidate", a.source_role_contract)) if path}
        if a.preflight:
            result['preflight'] = verify_preflight(json.loads(Path(a.preflight).read_text()),
                a.artifact_root or Path(a.preflight).parent, contract)
            if result['status'] != 'FAIL' and result['preflight']['status'] != 'PASS':
                result['status'] = 'FAIL' if result['preflight']['status'] == 'FAIL' else 'CONDITIONAL'
    except (ValueError, OSError, KeyError, TypeError) as exc:
        result = {"status": "FAIL", "error": str(exc)}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"]}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
