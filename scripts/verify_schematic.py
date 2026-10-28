#!/usr/bin/env python3
"""Run every automated drawing gate on a saved KiCad schematic in one pass.

Exports native ERC, KiCad XML netlist and PDF from the root sheet, then runs:
intent partitions and component identity, hierarchy/PDF audit, symbol
integrity, discrete symbol semantics (TVS direction, MOSFET channel, BJT type)
against the part's datasheet or MPN suffix, the readability gate and geometry QA on every active sheet, the
declared external-supply/PWR_FLAG check when the intent declares one or a flag
is drawn, and optionally a reference contract and an electrical change contract. All reports
and ``summary.json`` go into a fresh output directory.

``AUTOMATED_PASS`` covers only these gates. Native render review of every page
remains pending, and none of this is an electrical design review.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from schematic_layout.external_supply import audit_external_supply  # noqa: E402
from schematic_layout.discrete_semantics import audit_discrete_semantics  # noqa: E402
from schematic_layout.native import compare_netlist, find_cli, ignored_erc_rules  # noqa: E402
from schematic_layout.pages import normalize  # noqa: E402
from schematic_layout.native_geometry_context import prepare_geometry_context, page_context_from_job  # noqa: E402
from schematic_layout.native_circle_contacts import refine_wire_contacts  # noqa: E402
from schematic_layout.sexpr import parse, all_nodes  # noqa: E402
from schematic_layout.scene import read_scene  # noqa: E402
from schematic_layout.qa import check_scene  # noqa: E402
from schematic_layout.system_block import audit_system_block  # noqa: E402
from schematic_layout.component_requirements import artifact_audit  # noqa: E402


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
    ap.add_argument("--baseline-xml", type=Path, help="baseline native XML for an electrical change")
    ap.add_argument("--change-contract", type=Path)
    ap.add_argument("--preflight", type=Path, help="design-preflight.json for an electrical change")
    ap.add_argument("--design-closure", type=Path, help="Evidence-bound end-to-end design review record")
    ap.add_argument("--input", action="append", default=[], metavar="NAME=PATH",
                    help="declared input for --design-closure evidence, as pack_design takes it")
    ap.add_argument("--artifact-root", type=Path, help="Evidence base for --design-closure, --preflight artifact bindings and reviewed_circuit_supply; defaults to root parent")
    ap.add_argument("--project", help="native project annotation name; defaults to the root file stem")
    ap.add_argument("--cli", help="kicad-cli path")
    ap.add_argument("--native-geometry", action="store_true", help="Also qualify native pin-name geometry on a standalone page; hierarchy roots enable the finite native channel automatically")
    ap.add_argument('--bom', type=Path, help='current canonical BOM; defaults to root schematic directory/BOM.csv')
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
        report = json.loads(erc.read_text())
        violations = [v for s in report.get("sheets", []) for v in s.get("violations", [])]
        by_type = {}
        for v in violations:
            by_type[v.get("type", "?")] = by_type.get(v.get("type", "?"), 0) + 1
        # A rule the project ignores is a rule nobody checked (P5); list it instead of passing.
        ignored = ignored_erc_rules(report)
        gates["erc"] = {"status": "FAIL" if violations or ignored else "PASS", "violations": len(violations),
                        "by_type": by_type, "ignored_rules": ignored}
    else:
        gates["erc"] = {"status": "INSUFFICIENT", "reason": "ERC report not written"}

    intent = normalize(json.loads(args.intent.read_text(encoding="utf-8")))
    artifact_root = args.artifact_root or args.root.parent
    performance = artifact_audit(artifact_root, intent, schematic=args.root, xml=xml, pdf=pdf,
                                 bom=args.bom or args.root.parent / 'BOM.csv', project_name=args.project,
                                 inputs=dict(item.split('=', 1) for item in args.input) if args.input else None)
    write(out / 'component-requirements-check.json', performance)
    if performance['status'] != 'NOT_CHECKED':
        gates['component_requirements'] = {'status': performance['status'],
                                          'errors': len(performance['errors']),
                                          'pending': len(performance['pending'])}
    if xml.is_file():
        try:
            result = compare_netlist(xml, intent)
        except (ValueError, ET.ParseError) as exc:   # an unreadable export says so; the other gates still run
            gates["intent_netlist"] = {"status": "INSUFFICIENT", "reason": "KiCad netlist cannot be read: %s" % exc}
        else:
            write(out / "intent-netlist.json", result)
            gates["intent_netlist"] = {"status": result["status"], "errors": len(result["errors"])}
    else:
        gates["intent_netlist"] = {"status": "INSUFFICIENT", "reason": "netlist export failed"}

    hierarchy = out / "hierarchy.json"
    extra = ["--expected-pages", args.expected_pages] if args.expected_pages else []
    project = ["--project", args.project] if args.project else []
    tool("audit_project.py", args.root, "--pdf", pdf, "--netlist", xml, *extra, *project, "--out", hierarchy)
    gates["hierarchy"] = {"status": status_of(hierarchy)}
    try:
        files = json.loads(hierarchy.read_text())["file_sha256"]
        sheets = [args.root.resolve().parent / f for f in files if f.endswith(".kicad_sch")]
    except (OSError, ValueError, KeyError):
        sheets = [args.root]

    root_node = parse(args.root.read_text(encoding="utf-8"))
    if all_nodes(root_node, "sheet"):
        # The cover page is graphics: flow lines must be labelled and attached, the
        # isolation boundary visible, no block left unconnected.
        block = audit_system_block(root_node)
        write(out / "system-block.json", block)
        gates["system_block"] = {"status": block["status"], "findings": len(block["findings"])}

    symbols = out / "symbol-integrity.json"
    extra = ["--exceptions", args.symbol_exceptions] if args.symbol_exceptions else []
    tool("audit_symbol_integrity.py", args.root, "--netlist", xml, *extra, *project, "--out", symbols)
    gates["symbol_integrity"] = {"status": status_of(symbols)}

    try:
        semantics = audit_discrete_semantics(sheets, json.loads(args.intent.read_text(encoding="utf-8")),
                                             [args.artifact_root or args.root.resolve().parent, args.intent.resolve().parent])
    except (ValueError, OSError, KeyError) as exc:
        semantics = {"status": "INSUFFICIENT", "reason": str(exc)}
    write(out / "discrete-semantics.json", semantics)
    if semantics["status"] != "NOT_APPLICABLE":
        gates["discrete_semantics"] = {"status": semantics["status"], "errors": len(semantics.get("errors", [])),
                                       "unresolved": len(semantics.get("unresolved", []))}

    readability = out / "readability.json"
    extra = ["--waivers", args.readability_waivers] if args.readability_waivers else []
    tool("check_schematic_readability.py", *sheets, *extra, "--out", readability)
    gates["readability"] = {"status": status_of(readability)}

    geometry, gaps, review = {}, {}, {}
    native = None
    if args.native_geometry or all_nodes(parse(args.root.read_text()), "sheet"):
        native = prepare_geometry_context(args.root, args.project, cli, out / "native-geometry")
        commands.extend(native["commands"])
    (out / "geometry").mkdir()
    for sheet in sheets:
        report = out / "geometry" / f"{sheet.stem}.json"
        if native is None:
            tool("check_schematic_geometry.py", sheet, "--output", report)
        else:
            context_gap = None
            try:
                page_context = page_context_from_job(native, sheet)
            except (ValueError, OSError, KeyError) as exc:
                page_context = None
                context_gap = "Fresh native geometry unavailable: " + str(exc)
            source_bytes = sheet.read_bytes()
            scene = read_scene(parse(source_bytes.decode('utf-8')), page_context)
            if context_gap:
                scene.gaps.append(context_gap)
            write(report, refine_wire_contacts(sheet, check_scene(scene), cli=cli,
                                               expected_source_sha256=hashlib.sha256(source_bytes).hexdigest()))
        geometry[sheet.name] = status_of(report)
        try:
            found = json.loads(report.read_text())["coverage"]["gaps"]
        except (OSError, ValueError, KeyError):
            found = []
        if found:
            gaps[sheet.name] = found
        try:
            items = json.loads(report.read_text())["coverage"].get("render_review_items", [])
        except (OSError, ValueError, KeyError):
            items = []
        if items:
            review[sheet.name] = items
    worst = [s for s in ("FAIL", "INSUFFICIENT") if s in geometry.values()]
    gates["geometry"] = {"status": worst[0] if worst else "PASS", "sheets": geometry}
    if gaps:
        gates["geometry"]["coverage_gaps"] = gaps
    if review:
        # Pin text the native channel cannot qualify; the render review must cover it.
        gates["geometry"]["render_review_items"] = review

    if xml.is_file():
        try:
            supply = audit_external_supply(args.root, sheets, intent, xml, cli, out / "external-supply", args.artifact_root)
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
        extra = ["--preflight", args.preflight, "--artifact-root", args.artifact_root or args.root.resolve().parent] if args.preflight else []
        tool("verify_design_change.py", args.baseline_xml, xml, args.change_contract, *extra, "--out", report)
        gates["design_change"] = {"status": status_of(report)}
        if not args.preflight:
            gates["design_change"]["note"] = "No --preflight: native delta only, not an electrical redesign closure"

    if args.design_closure:
        report = out / "design-closure.json"
        tool("audit_design_closure.py", args.design_closure, "--intent", args.intent,
             "--artifact-root", args.artifact_root or args.root.resolve().parent,
             *[a for v in args.input for a in ("--input", v)], "--out", report)
        gates["design_closure"] = {"status": status_of(report)}

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
        "design_closure": "checked" if args.design_closure else "NOT_CHECKED",
        "reference_contract": "checked" if args.reference_contract else "NOT_CHECKED",
        "pending": (["End-to-end design closure not checked"] if not args.design_closure else [])
                   + (["Core-part pin maps and peripherals not checked against datasheets (no --reference-contract)"]
                      if not args.reference_contract else []) + ["Native render review: trace each declared reading task on every page"]
                   + ([f"Native render review: check {sum(map(len, review.values()))} pin-text items listed in geometry.render_review_items"] if review else []),
        "commands": commands,
    }
    write(out / "summary.json", summary)
    for name, g in gates.items():
        print(f"{name:18} {g['status']}")
    print(f"{'overall':18} {overall}")
    return 0 if overall == "AUTOMATED_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
