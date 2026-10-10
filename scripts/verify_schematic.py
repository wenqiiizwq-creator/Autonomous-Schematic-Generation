#!/usr/bin/env python3
"""Run every automated drawing gate on a saved KiCad schematic in one pass.

Exports native ERC, KiCad XML netlist and PDF from the root sheet, then runs:
intent partitions and component identity, hierarchy/PDF audit, symbol
integrity, the readability gate and geometry QA on every active sheet, the
declared external-supply/PWR_FLAG check when the intent declares one or a flag
is drawn, and optionally a reference contract and an electrical change contract. All reports
and ``summary.json`` go into a fresh output directory.

``AUTOMATED_PASS`` covers only these gates. Native render review of every page
and the full electrical review (schematic-review) remain pending.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from schematic_layout.external_supply import audit_external_supply  # noqa: E402
from schematic_layout.native import compare_netlist, find_cli  # noqa: E402
from schematic_layout.pages import normalize  # noqa: E402


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tool(name, *args):
    """Run a sibling checker CLI; its own report file carries the result."""
    r = subprocess.run([sys.executable, "-B", str(HERE / name), *map(str, args)],
                       capture_output=True, text=True, timeout=600)
    return {"returncode": r.returncode, "stderr": r.stderr[-2000:]}


def status_of(path, fallback="INSUFFICIENT"):
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("status", fallback)
    except (OSError, ValueError):
        return fallback


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="root .kicad_sch (single page or hierarchy)")
    ap.add_argument("--intent", type=Path, required=True,
                    help="board or page electrical intent (nets as a list or {name: pins})")
    ap.add_argument("--out", type=Path, required=True, help="fresh output directory")
    ap.add_argument("--expected-pages", type=int)
    ap.add_argument("--symbol-exceptions", type=Path)
    ap.add_argument("--readability-waivers", type=Path)
    ap.add_argument("--reference-contract", type=Path)
    ap.add_argument("--source-role-contract", type=Path, help="Reviewed hash-bound pinless mechanical/documentation roles")
    ap.add_argument("--baseline-xml", type=Path, help="baseline native XML for an electrical change")
    ap.add_argument("--change-contract", type=Path)
    ap.add_argument("--preflight", type=Path, help="design-preflight.json for an electrical change")
    ap.add_argument("--project", help="native project annotation name; defaults to the root file stem")
    ap.add_argument("--cli", help="kicad-cli path")
    args = ap.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        ap.error("Output directory is not empty; use a fresh run directory")
    if bool(args.baseline_xml) != bool(args.change_contract):
        ap.error("--baseline-xml and --change-contract go together")
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    gates, commands = {}, []

    cli = find_cli(args.cli)
    if not cli:
        write(out / "summary.json", {"status": "INSUFFICIENT", "reason": "kicad-cli not found"})
        print("INSUFFICIENT: kicad-cli not found")
        return 1

    def kicad(*a):
        r = subprocess.run([cli, *map(str, a)], capture_output=True, text=True, timeout=300)
        commands.append({"argv": [cli, *map(str, a)], "returncode": r.returncode, "stderr": r.stderr[-2000:]})
        return r

    version = kicad("version").stdout.strip()
    erc, xml, pdf = out / "erc.json", out / "netlist.xml", out / "schematic.pdf"
    kicad("sch", "erc", "--format", "json", "--severity-all", "-o", erc, args.root)
    kicad("sch", "export", "netlist", "--format", "kicadxml", "-o", xml, args.root)
    kicad("sch", "export", "pdf", "-o", pdf, args.root)

    if erc.is_file():
        violations = [v for s in json.loads(erc.read_text()).get("sheets", []) for v in s.get("violations", [])]
        by_type = {}
        for v in violations:
            by_type[v.get("type", "?")] = by_type.get(v.get("type", "?"), 0) + 1
        gates["erc"] = {"status": "FAIL" if violations else "PASS", "violations": len(violations), "by_type": by_type}
    else:
        gates["erc"] = {"status": "INSUFFICIENT", "reason": "ERC report not written"}

    if xml.is_file():
        intent = normalize(json.loads(args.intent.read_text(encoding="utf-8")))
        result = compare_netlist(xml, intent)
        write(out / "intent-netlist.json", result)
        gates["intent_netlist"] = {"status": result["status"], "errors": len(result["errors"])}
    else:
        gates["intent_netlist"] = {"status": "INSUFFICIENT", "reason": "netlist export failed"}

    hierarchy = out / "hierarchy.json"
    extra = ["--expected-pages", args.expected_pages] if args.expected_pages else []
    project = ["--project", args.project] if args.project else []
    roles = ["--source-role-contract", args.source_role_contract] if args.source_role_contract else []
    tool("audit_project.py", args.root, "--pdf", pdf, "--netlist", xml, *extra, *project, *roles, "--out", hierarchy)
    gates["hierarchy"] = {"status": status_of(hierarchy)}
    try:
        files = json.loads(hierarchy.read_text())["file_sha256"]
        sheets = [args.root.resolve().parent / f for f in files if f.endswith(".kicad_sch")]
    except (OSError, ValueError, KeyError):
        sheets = [args.root]

    symbols = out / "symbol-integrity.json"
    extra = ["--exceptions", args.symbol_exceptions] if args.symbol_exceptions else []
    tool("audit_symbol_integrity.py", args.root, "--netlist", xml, *extra, *project, *roles, "--out", symbols)
    gates["symbol_integrity"] = {"status": status_of(symbols)}

    readability = out / "readability.json"
    extra = ["--waivers", args.readability_waivers] if args.readability_waivers else []
    tool("check_schematic_readability.py", *sheets, *extra, "--out", readability)
    gates["readability"] = {"status": status_of(readability)}

    geometry, gaps = {}, {}
    (out / "geometry").mkdir()
    for sheet in sheets:
        report = out / "geometry" / f"{sheet.stem}.json"
        tool("check_schematic_geometry.py", sheet, "--output", report)
        geometry[sheet.name] = status_of(report)
        try:
            found = json.loads(report.read_text())["coverage"]["gaps"]
        except (OSError, ValueError, KeyError):
            found = []
        if found:
            gaps[sheet.name] = found
    worst = [s for s in ("FAIL", "INSUFFICIENT", "REVIEW") if s in geometry.values()]
    gates["geometry"] = {"status": worst[0] if worst else "PASS", "sheets": geometry}
    if gaps:
        gates["geometry"]["coverage_gaps"] = gaps

    if xml.is_file():
        try:
            supply = audit_external_supply(args.root, sheets, intent, xml, cli, out / "external-supply")
        except (ValueError, OSError) as exc:
            supply = {"status": "FAIL", "error": str(exc)}
        if supply["status"] != "NOT_APPLICABLE":
            write(out / "external-supply.json", supply)
            gates["external_supply"] = {"status": supply["status"], "errors": len(supply.get("errors", []))}

    if args.reference_contract:
        report = out / "reference-contract.json"
        tool("verify_reference_contract.py", xml, args.reference_contract, "--out", report)
        gates["reference_contract"] = {"status": status_of(report)}

    if args.change_contract:
        report = out / "design-change.json"
        extra = ["--preflight", args.preflight, "--artifact-root", args.root.resolve().parent] if args.preflight else []
        tool("verify_design_change.py", args.baseline_xml, xml, args.change_contract, *extra, "--out", report)
        gates["design_change"] = {"status": status_of(report)}
        if not args.preflight:
            gates["design_change"]["note"] = "No --preflight: native delta only, not an electrical redesign closure"

    states = {g["status"] for g in gates.values()}
    overall = "FAIL" if "FAIL" in states else "AUTOMATED_PASS" if states == {"PASS"} else "INCOMPLETE"
    summary = {
        "status": overall,
        "root": str(args.root),
        "intent": str(args.intent),
        "kicad_version": version,
        "gates": gates,
        "sheets": [str(s) for s in sheets],
        "render": str(pdf) if pdf.is_file() else None,
        "pending": ["Native render review: trace each declared reading task on every page",
                    "Full electrical review: hand off to schematic-review"],
        "commands": commands,
    }
    write(out / "summary.json", summary)
    for name, g in gates.items():
        print(f"{name:18} {g['status']}")
    print(f"{'overall':18} {overall}")
    return 0 if overall == "AUTOMATED_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
