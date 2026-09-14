#!/usr/bin/env python3
"""Scoped execution evidence for pinned SKiDL objects and circuit-synth export.

Development-only: run with the project venv containing the pinned SKiDL checkout.
Does not run either upstream placement/router or claim their full test suites.
"""

import argparse
import ast
import json
import logging
import os
from pathlib import Path
import sys
from types import SimpleNamespace as NS
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.importers import skidl_to_ir, circuit_synth_to_ir
from schematic_layout.circuit_ir import compile_circuit


def skidl_probe(out):
    # Imports may create SKiDL diagnostics; keep them in the evidence directory.
    os.chdir(out)
    os.environ["MPLCONFIGDIR"] = str(out.parent / "upstream-cache/matplotlib")
    os.environ["XDG_CACHE_HOME"] = str(out / "cache")
    os.environ["XDG_DATA_HOME"] = str(out / "data")
    from skidl import Circuit, Part, Pin, Net, SKIDL, TEMPLATE
    from skidl.node import Node

    c = Circuit()
    c.no_files = True
    template = Part(name="R", tool=SKIDL, dest=TEMPLATE, ref_prefix="R")
    template += (
        Pin(num="1", func=Pin.funcs.PASSIVE),
        Pin(num="2", func=Pin.funcs.PASSIVE),
    )
    with c:
        vin, gnd = Net("VIN"), Net("GND")
        for tag, upper, lower in (("channel_a", "R1", "R2"), ("channel_b", "R3", "R4")):
            with Node("divider", tag=tag):
                top = template(ref=upper, tag="upper", value="10k", footprint="")
                bottom = template(ref=lower, tag="lower", value="10k", footprint="")
                if upper == "R1":
                    top.mpn = "FIXTURE_SKIDL_MPN"
                    top.dnp = True
                    top.ratings = {"Tolerance": "1%"}
                middle = Net("MID_" + tag[-1].upper())
                vin += top[1]
                middle += top[2], bottom[1]
                gnd += bottom[2]
    before = sorted(
        (n.name, sorted((p.part.ref, str(p.num)) for p in n.get_pins()))
        for n in c.get_nets()
    )
    document = skidl_to_ir(c, "skidl_import", {p.ref: "Device:R" for p in c.parts})
    intent, compiled = compile_circuit(document)
    sample = next(part for part in intent["components"] if part["ref"] == "R1")
    assert sample["mpn"] == "FIXTURE_SKIDL_MPN" and sample["dnp"] is True
    assert sample["ratings"]["Tolerance"] == "1%"
    expected = {frozenset(f"{r}.{p}" for r, p in pins) for _, pins in before}
    assert {frozenset(n["pins"]) for n in intent["nets"]} == expected
    assert before == sorted(
        (n.name, sorted((p.part.ref, str(p.num)) for p in n.get_pins()))
        for n in c.get_nets()
    )
    assert {b["id"] for b in compiled["blocks"]} == {"channel_a", "channel_b"}
    (out / "skidl.circuit.json").write_text(json.dumps(document, indent=2) + "\n")
    policy = {
        "schema_version": 2,
        "blocks": {b["id"]: {"template": "functional"} for b in compiled["blocks"]},
        "nets": {n["name"]: {"mode": "labels"} for n in intent["nets"]},
    }
    (out / "skidl.presentation.json").write_text(json.dumps(policy, indent=2) + "\n")
    return {
        "status": "PASS",
        "parts": len(intent["components"]),
        "nets": len(intent["nets"]),
        "blocks": [b["id"] for b in compiled["blocks"]],
        "source_objects_unchanged": True,
        "mpn_ratings_dnp_preserved": True,
    }


def synth_probe(out):
    # Execute the actual pure to_dict() method from the pinned source in a
    # deliberately small namespace. This isolates exporter semantics from MCP,
    # symbol caches, account services and unrelated upstream package imports.
    path = ROOT / "upstream/circuit-synth/src/circuit_synth/core/netlist_exporter.py"
    tree = ast.parse(path.read_text())
    cls = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "NetlistExporter"
    )
    methods = [
        n
        for n in cls.body
        if isinstance(n, ast.FunctionDef) and n.name in ("__init__", "to_dict")
    ]
    code = ast.fix_missing_locations(
        ast.Module(
            body=[
                ast.ClassDef(
                    name="NetlistExporter",
                    bases=[],
                    keywords=[],
                    body=methods,
                    decorator_list=[],
                )
            ],
            type_ignores=[],
        )
    )
    namespace = {
        "Dict": Dict,
        "Any": Any,
        "logger": logging.getLogger("upstream-export-probe"),
    }
    exec(compile(code, str(path), "exec"), namespace)

    class Component:
        def __init__(self, ref):
            self.ref = ref
            self._pins = {
                str(i): NS(num=str(i), name="~", func="passive", net=NS(name=n))
                for i, n in ((1, "VIN"), (2, "GND"))
            }

        def to_dict(self):
            return {
                "ref": self.ref,
                "symbol": "Device:R",
                "value": "1k",
                "footprint": "",
            }

    def circuit(name, ref):
        return NS(
            name=name,
            description="export probe",
            _components={ref: Component(ref)},
            _nets={
                "GND": NS(
                    is_power=True,
                    power_symbol=None,
                    trace_current=None,
                    impedance=None,
                    properties={},
                )
            },
            _subcircuits=[],
            _annotations=[],
        )

    root = circuit("root", "R1")
    root._subcircuits.append(circuit("child", "R2"))
    data = namespace["NetlistExporter"](root).to_dict()
    assert isinstance(data["nets"]["VIN"], list)
    assert isinstance(data["nets"]["GND"], dict)
    document, audit = circuit_synth_to_ir(
        data, "synth_import", shared_nets=["VIN", "GND"]
    )
    intent, _ = compile_circuit(document)
    assert {frozenset(n["pins"]) for n in intent["nets"]} == {
        frozenset(["R1.1", "R2.1"]),
        frozenset(["R1.2", "R2.2"]),
    }
    (out / "circuit-synth-export.json").write_text(json.dumps(data, indent=2) + "\n")
    (out / "circuit-synth-import.json").write_text(
        json.dumps(document, indent=2) + "\n"
    )
    (out / "circuit-synth-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    return {
        "status": "PASS",
        "method": "actual NetlistExporter.to_dict with fixture objects",
        "forms_tested": ["list", "nodes with metadata"],
        "recursive_subcircuits": True,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    result = {"skidl": skidl_probe(out), "circuit_synth": synth_probe(out)}
    (out / "probe-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
