"""Native KiCad verification: exact pin partitions and component identity."""

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

# KiCad automatic names; the pin names inside may themselves contain "/".
AUTO_NET_NAME = re.compile(r"(?:^|/)(?:Net|unconnected)-\(")
# kicad-cli versions whose SVG export the native geometry controls were run on (10.0.7: 2026-10-30, every
# native test passes unchanged). Add a version only after that check.
QUALIFIED_VERSIONS = ("10.0.6", "10.0.7")
# ERC rules KiCad 10 ignores by default that a generated project turns on, and the only
# rules a project may leave ignored (they concern simulation models and footprint filters).
ERC_RULES_ON = {"single_global_label": "error", "four_way_junction": "error"}
ERC_MAY_IGNORE = {"simulation_model_issue", "footprint_filter"}


def project_settings():
    """The .kicad_pro content a generated project starts from."""
    return {"erc": {"rule_severities": dict(ERC_RULES_ON)}}


def ignored_erc_rules(report):
    """Rules an ERC report says were not checked, apart from the ones a project may ignore."""
    return sorted(c.get("key", "?") for c in report.get("ignored_checks", []) if c.get("key") not in ERC_MAY_IGNORE)


def find_cli(explicit=None):
    candidates = [
        explicit,
        shutil.which("kicad-cli"),
        "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    ]
    return next((str(p) for p in candidates if p and Path(p).is_file()), None)


def compare_netlist(xml_path, intent, layout=None):
    root = ET.parse(xml_path).getroot()
    if (
        root.tag != "export"
        or root.find("nets") is None
        or root.find("components") is None
    ):
        raise ValueError("Not a KiCad XML netlist")
    # Power symbols (#PWR...) are virtual net-name carriers, not physical pins.
    nets = [
        (
            n.attrib["name"],
            frozenset(
                f"{p.attrib['ref']}.{p.attrib['pin']}" for p in n.findall("node")
                if not p.attrib["ref"].startswith("#")
            ),
        )
        for n in root.findall("nets/net")
    ]
    actual_sets = {s for _, s in nets if s}
    expected_sets = {frozenset(n["pins"]) for n in intent["nets"]}
    nc = set(intent.get("no_connect", []))
    errors = []
    coverage_gaps = []
    for expected in expected_sets:
        if expected not in actual_sets:
            errors.append(
                {
                    "kind": "pin_partition_mismatch",
                    "expected": sorted(expected),
                    "actual": [sorted(s) for s in actual_sets if s & expected],
                }
            )
    for actual in actual_sets:
        if actual not in expected_sets and not (len(actual) == 1 and actual <= nc):
            errors.append({"kind": "unexpected_net_partition", "pins": sorted(actual)})
    if layout is None:
        # Board level: a drawn net name must be the intent name of the same pin
        # partition (e.g. two swapped single-use name labels). A name KiCad made up
        # (Net-(...), unconnected-(...)) is not compared. A local
        # name may carry only its own sheet path as a prefix; intent names that
        # start with "/" must match exactly.
        sheets = {s.attrib.get("name", "") for s in root.findall("design/sheet")} | {"/"}
        by_pins = {frozenset(n["pins"]): n["name"] for n in intent["nets"]}
        for name, pins in nets:
            expected = by_pins.get(pins)
            if expected is None:
                continue
            allowed = {expected} if expected.startswith("/") else {expected} | {p + expected for p in sheets}
            if name not in allowed and AUTO_NET_NAME.search(name):
                continue
            if name not in allowed:
                errors.append(
                    {
                        "kind": "net_name_mismatch",
                        "expected": expected,
                        "actual": [name],
                    }
                )
    for n in intent["nets"]:
        policy = (layout or {}).get("nets", {}).get(n["name"], {})
        if (policy.get("mode") in ("labels", "power") or policy.get("label")
                or len(policy.get("groups", [])) > 1):
            found = [name for name, s in nets if s == frozenset(n["pins"])]
            # Local labels are qualified by the root sheet path in native XML.
            if len(found) != 1 or found[0] not in (n["name"], "/" + n["name"]):
                errors.append(
                    {
                        "kind": "net_name_mismatch",
                        "expected": n["name"],
                        "actual": found,
                    }
                )
    components = {c.attrib["ref"]: c for c in root.findall("components/comp")}
    if set(components) != {c["ref"] for c in intent["components"]}:
        errors.append({"kind": "component_set_mismatch", "actual": sorted(components)})
    for c in intent["components"]:
        if c["ref"] not in components:
            continue
        native = components[c["ref"]]
        for key in ("value", "footprint"):
            if key in c and (native.findtext(key) or "") != c[key]:
                errors.append(
                    {
                        "kind": "component_identity_mismatch",
                        "ref": c["ref"],
                        "field": key,
                        "expected": c[key],
                        "actual": native.findtext(key),
                    }
                )
        native_fields = {
            f.get("name"): f.text or "" for f in native.findall("fields/field")
        }
        expected_fields = {**c.get("fields", {}), **c.get("ratings", {})}
        for key, field in (
            ("mpn", "MPN"),
            ("datasheet", "Datasheet"),
            ("hierarchy", "CircuitPath"),
        ):
            if key in c:
                expected_fields[field] = c[key]
        for field, expected in expected_fields.items():
            if native_fields.get(field) != str(expected):
                errors.append(
                    {
                        "kind": "component_identity_mismatch",
                        "ref": c["ref"],
                        "field": field,
                        "expected": str(expected),
                        "actual": native_fields.get(field),
                    }
                )
        if (native.find("property[@name='dnp']") is not None) != c.get("dnp", False):
            errors.append({"kind": "assembly_state_mismatch", "ref": c["ref"]})
        source = native.find("libsource")
        if source is None or f"{source.get('lib')}:{source.get('part')}" != c["lib_id"]:
            errors.append(
                {
                    "kind": "symbol_identity_mismatch",
                    "ref": c["ref"],
                    "expected": c["lib_id"],
                }
            )
    return {
        "status": "FAIL" if errors else "INSUFFICIENT" if coverage_gaps else "PASS",
        "errors": errors,
        **({"coverage_gaps": coverage_gaps} if coverage_gaps else {}),
        "expected_connected_pins": sum(len(s) for s in expected_sets),
        "expected_nets": len(expected_sets),
        "actual_nets": len(actual_sets),
        "no_connect_pins": sorted(nc),
    }


def verify(schematic, intent, layout, output, cli=None, reference_contract=None):
    cli = find_cli(cli)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if not cli:
        return {
            "status": "INSUFFICIENT",
            "reason": "kicad-cli not found",
            "render_review_required": True,
        }
    records = []

    def run(args):
        result = subprocess.run(
            [cli, *args], text=True, capture_output=True, timeout=120
        )
        record = {
            "argv": [cli, *args],
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        records.append(record)
        return result

    version = run(["version"]).stdout.strip()
    erc = output / "erc.json"
    netlist = output / "netlist.xml"
    pdf = output / "schematic.pdf"
    erc_run = run(
        [
            "sch",
            "erc",
            "--format",
            "json",
            "--severity-all",
            "--exit-code-violations",
            "-o",
            str(erc),
            str(schematic),
        ]
    )
    net_run = run(
        [
            "sch",
            "export",
            "netlist",
            "--format",
            "kicadxml",
            "-o",
            str(netlist),
            str(schematic),
        ]
    )
    pdf_run = run(["sch", "export", "pdf", "-o", str(pdf), str(schematic)])
    result = {
        "kicad_version": version,
        "commands": records,
        "schematic_sha256": hashlib.sha256(Path(schematic).read_bytes()).hexdigest(),
        "render_review_required": True,
        "render": str(pdf) if pdf.is_file() else None,
    }
    if erc.is_file():
        report = json.loads(erc.read_text())
        violations = [
            v for s in report.get("sheets", []) for v in s.get("violations", [])
        ]
        ignored = ignored_erc_rules(report)
        result["erc"] = {
            "status": "PASS" if erc_run.returncode == 0 and not violations and not ignored else "FAIL",
            "violations": violations,
            "ignored_checks": report.get("ignored_checks", []),
            "ignored_rules": ignored,
        }
        if "sheets" not in report:
            result["erc"]["status"] = "INSUFFICIENT"
    else:
        result["erc"] = {"status": "INSUFFICIENT"}
    if net_run.returncode == 0 and netlist.is_file():
        if layout is None:
            result["netlist"] = compare_netlist(netlist, intent)
        else:
            result["netlist"] = compare_netlist(netlist, intent, layout)
    else:
        result["netlist"] = {"status": "INSUFFICIENT"}
    # Run on the saved hierarchy and native export, including custom library ink.
    # An ERC/netlist match alone cannot detect a shortened internal pin leg.
    from .symbol_integrity import audit_symbols
    result["symbol_integrity"] = audit_symbols(
        schematic, netlist if net_run.returncode == 0 and netlist.is_file() else None
    )
    (output / "symbol-integrity.json").write_text(
        json.dumps(result["symbol_integrity"], ensure_ascii=False, indent=2) + "\n"
    )
    if reference_contract is not None:
        from .reference_contract import verify_reference
        contract_path = Path(reference_contract)
        result["reference_contract"] = (
            verify_reference(netlist, json.loads(contract_path.read_text()), contract_path.parent)
            if net_run.returncode == 0 and netlist.is_file()
            else {"status": "INSUFFICIENT", "reason": "Native netlist export unavailable"}
        )
        (output / "reference-contract.json").write_text(
            json.dumps(result["reference_contract"], ensure_ascii=False, indent=2) + "\n"
        )
    result["status"] = (
        "PASS"
        if (
            result["erc"]["status"] == result["netlist"]["status"] == "PASS"
            and result["symbol_integrity"]["status"] == "PASS"
            and result.get("reference_contract", {"status": "PASS"})["status"] == "PASS"
            and pdf_run.returncode == 0
            and pdf.is_file()
        )
        else "FAIL"
    )
    return result
