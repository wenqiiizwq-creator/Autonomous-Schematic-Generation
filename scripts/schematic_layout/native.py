"""Native KiCad verification: exact pin partitions and component identity."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


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
    nets = [
        (
            n.attrib["name"],
            frozenset(
                f"{p.attrib['ref']}.{p.attrib['pin']}" for p in n.findall("node")
            ),
        )
        for n in root.findall("nets/net")
    ]
    actual_sets = {s for _, s in nets if s}
    expected_sets = {frozenset(n["pins"]) for n in intent["nets"]}
    nc = set(intent.get("no_connect", []))
    errors = []
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
    for n in intent["nets"]:
        policy = (layout or {}).get("nets", {}).get(n["name"], {})
        if policy.get("mode") == "labels" or policy.get("label") or len(policy.get("groups", [])) > 1:
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
        if "units" in c:
            native_units = native.findall("units/unit")
            if len(native_units) != len(c["units"]):
                errors.append(
                    {
                        "kind": "unit_coverage_mismatch",
                        "ref": c["ref"],
                        "expected": c["units"],
                        "actual_count": len(native_units),
                    }
                )
            expected_pins = {
                p.rsplit(".", 1)[1]
                for n in intent["nets"]
                for p in n["pins"]
                if p.rsplit(".", 1)[0] == c["ref"]
            }
            expected_pins.update(
                p.rsplit(".", 1)[1]
                for p in intent.get("no_connect", [])
                if p.rsplit(".", 1)[0] == c["ref"]
            )
            actual_pins = {p.get("num") for p in native.findall("units/unit/pins/pin")}
            if actual_pins != expected_pins:
                errors.append(
                    {
                        "kind": "physical_pin_coverage_mismatch",
                        "ref": c["ref"],
                        "expected": sorted(expected_pins),
                        "actual": sorted(actual_pins),
                    }
                )
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
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "expected_connected_pins": sum(len(s) for s in expected_sets),
        "expected_nets": len(expected_sets),
        "actual_nets": len(actual_sets),
        "no_connect_pins": sorted(nc),
    }


def verify(schematic, intent, layout, output, cli=None):
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
        result["erc"] = {
            "status": "PASS" if erc_run.returncode == 0 and not violations else "FAIL",
            "violations": violations,
            "ignored_checks": report.get("ignored_checks", []),
        }
        if "sheets" not in report:
            result["erc"]["status"] = "INSUFFICIENT"
    else:
        result["erc"] = {"status": "INSUFFICIENT"}
    result["netlist"] = (
        compare_netlist(netlist, intent, layout)
        if net_run.returncode == 0 and netlist.is_file()
        else {"status": "INSUFFICIENT"}
    )
    result["status"] = (
        "PASS"
        if (
            result["erc"]["status"] == result["netlist"]["status"] == "PASS"
            and pdf_run.returncode == 0
            and pdf.is_file()
        )
        else "FAIL"
    )
    return result
