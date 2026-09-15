"""Verify externally authored source/pin/peripheral facts against native XML.

This deliberately does not infer transfer functions, current paths through ICs,
or circuit completeness from net names. Coverage is relative to the authored
scope, whose adequacy still requires engineering review.
"""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from .design_change import read_native


def _keys(obj, required, optional=()):
    if not isinstance(obj, dict) or set(obj) - set(required) - set(optional) or set(required) - set(obj):
        raise ValueError(f"Expected fields {sorted(required)}, optional {sorted(optional)}")


def _text(s):
    if not isinstance(s, str) or not s.strip():
        raise ValueError("Expected nonempty text")
    return s


def verify_reference(netlist, contract, base):
    _keys(contract, {"schema_version", "scope", "sources", "pin_maps", "checks", "features"})
    if contract["schema_version"] != 1:
        raise ValueError("Unsupported reference contract version")
    scope = contract["scope"]
    _keys(scope, {"core_refs", "feature_ids"})
    for values in scope.values():
        if not isinstance(values, list) or not values or any(not isinstance(x, str) or not x for x in values) or len(set(values)) != len(values):
            raise ValueError("Scope must declare nonempty unique core_refs and feature_ids")
    if not isinstance(contract["sources"], dict) or not isinstance(contract["pin_maps"], dict) or not isinstance(contract["checks"], list) or not isinstance(contract["features"], list):
        raise ValueError("Invalid reference contract collections")
    native = read_native(netlist)
    root = ET.parse(netlist).getroot()
    metadata = {f'{n.get("ref")}.{n.get("pin")}': {"name": n.get("pinfunction", ""), "type": n.get("pintype", "").removesuffix("+no_connect")}
                for net in root.findall("nets/net") for n in net.findall("node") if not n.get("ref", "").startswith("#")}
    sources, checks, errors, gaps = {}, {}, [], []
    base = Path(base).resolve()
    for sid, s in contract["sources"].items():
        _text(sid)
        _keys(s, {"path", "sha256", "url", "document", "revision"})
        for v in s.values():
            _text(v)
        if not re.fullmatch(r"[0-9a-f]{64}", s["sha256"]):
            raise ValueError("Source SHA256 must be a lowercase 64-digit digest")
        path = (base / s["path"]).resolve()
        record = {k: s[k] for k in ("sha256", "url", "document", "revision")}
        if not path.is_file():
            record.update(status="INSUFFICIENT", reason="Source file missing")
        else:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            record.update(status="PASS" if actual == s["sha256"] else "FAIL", actual_sha256=actual)
        sources[sid] = record

    def evidence(item):
        _text(item["locator"])
        if item["source"] not in sources:
            raise ValueError("Unknown source ID")
        return sources[item["source"]]["status"]

    pin_results = {}
    for ref, spec in contract["pin_maps"].items():
        _keys(spec, {"identity", "source", "locator", "pins"})
        _keys(spec["identity"], {"value", "mpn", "footprint", "lib_id"})
        for v in spec["identity"].values():
            _text(v)
        if not isinstance(spec["pins"], dict) or not spec["pins"]:
            raise ValueError("Pin map must enumerate every physical pin, including NC/EP")
        failures = []
        basis = evidence(spec)
        component = native["components"].get(ref)
        if component is None:
            failures.append("Component absent")
        elif any((component["fields"].get("MPN") or component["value"] if k == "mpn" else component[k]) != v for k, v in spec["identity"].items()):
            failures.append("Exact part/package/library identity mismatch")
        actual = {p.rsplit(".", 1)[1] for p in native["pin_nets"] if p.rsplit(".", 1)[0] == ref}
        if actual != set(spec["pins"]):
            failures.append({"missing_from_contract": sorted(actual - spec["pins"].keys()),
                             "missing_from_native": sorted(spec["pins"].keys() - actual)})
        for number, expected in spec["pins"].items():
            _text(number)
            _keys(expected, {"names", "types"})
            for field, aliases in expected.items():
                if not isinstance(aliases, list) or not aliases or any(not isinstance(x, str) for x in aliases) or len(set(aliases)) != len(aliases):
                    raise ValueError("Pin names/types must be explicit nonempty alias lists")
                if field == "types" and any(not x for x in aliases):
                    raise ValueError("Pin electrical types cannot be blank")
            observed = metadata.get(ref + "." + number)
            if observed and (observed["name"] not in expected["names"] or observed["type"] not in expected["types"]):
                failures.append({"pin": number, "actual": observed, "expected": expected})
        pin_results[ref] = {"status": "FAIL" if failures or basis == "FAIL" else basis,
                            "source": spec["source"], "locator": spec["locator"], "failures": failures}
    if set(scope["core_refs"]) != set(pin_results):
        gaps.append({"kind": "core_scope_mismatch", "missing": sorted(set(scope["core_refs"]) - pin_results.keys()),
                     "undeclared": sorted(pin_results.keys() - set(scope["core_refs"]))})

    for c in contract["checks"]:
        common = {"id", "kind", "source", "locator"}
        if not isinstance(c, dict) or c.get("kind") not in {"component", "same_net", "distinct_nets"}:
            raise ValueError("Unknown peripheral check kind")
        _keys(c, common | ({"ref", "expected"} if c["kind"] == "component" else {"pins"}))
        cid = _text(c["id"])
        if cid in checks:
            raise ValueError("Duplicate check ID")
        basis = evidence(c)
        failures = []
        if c["kind"] == "component":
            _keys(c["expected"], {"value", "footprint", "lib_id", "dnp"})
            if type(c["expected"]["dnp"]) is not bool or any(not isinstance(c["expected"][k], str) for k in ("value", "footprint", "lib_id")):
                raise ValueError("Invalid component expectation")
            comp = native["components"].get(c["ref"])
            if comp is None or any(comp[k] != v for k, v in c["expected"].items()):
                failures.append("Component value/footprint/library/population mismatch or absent")
        else:
            pins = c["pins"]
            if not isinstance(pins, list) or len(pins) < 2 or any(not isinstance(p, str) or "." not in p for p in pins) or len(set(pins)) != len(pins):
                raise ValueError("Net check needs at least two unique physical pins")
            missing = [p for p in pins if p not in native["pin_nets"]]
            dnp = [p for p in pins if native["components"].get(p.rsplit(".", 1)[0], {}).get("dnp")]
            if missing or dnp:
                failures.append({"absent_pins": missing, "unfitted_endpoints": dnp})
            else:
                groups = {native["pin_nets"][p] for p in pins}
                wanted = 1 if c["kind"] == "same_net" else len(pins)
                if len(groups) != wanted:
                    failures.append("Native pin partition mismatch")
        checks[cid] = {"status": "FAIL" if failures or basis == "FAIL" else basis, "kind": c["kind"],
                       "source": c["source"], "locator": c["locator"], "failures": failures}

    features = {}
    for f in contract["features"]:
        _keys(f, {"id", "boundary", "source", "locator", "stages"})
        fid = _text(f["id"])
        _text(f["boundary"])
        if fid in features or not isinstance(f["stages"], list) or not f["stages"]:
            raise ValueError("Duplicate feature or empty stages")
        basis = evidence(f)
        stage_ids, stage_results = set(), []
        for stage in f["stages"]:
            _keys(stage, {"id", "role", "refs", "checks"})
            sid = _text(stage["id"])
            _text(stage["role"])
            if sid in stage_ids or any(not isinstance(stage[k], list) or not stage[k] or any(not isinstance(x, str) or not x for x in stage[k]) or len(set(stage[k])) != len(stage[k]) for k in ("refs", "checks")):
                raise ValueError("Stage needs unique ID and nonempty refs/checks")
            stage_ids.add(sid)
            missing = [r for r in stage["refs"] if r not in native["components"] or native["components"][r]["dnp"]]
            unknown = set(stage["checks"]) - checks.keys()
            if unknown:
                raise ValueError("Stage refers to an unknown check ID")
            statuses = [checks[k]["status"] for k in stage["checks"]] + [basis]
            status = "FAIL" if missing or "FAIL" in statuses else "INSUFFICIENT" if "INSUFFICIENT" in statuses else "PASS"
            stage_results.append({"id": sid, "role": stage["role"], "status": status, "absent_or_unfitted_refs": missing})
        statuses = [s["status"] for s in stage_results]
        features[fid] = {"status": "FAIL" if "FAIL" in statuses else "INSUFFICIENT" if "INSUFFICIENT" in statuses else "PASS",
                         "boundary": f["boundary"], "stages": stage_results}
    if set(scope["feature_ids"]) != set(features):
        gaps.append({"kind": "feature_scope_mismatch", "missing": sorted(set(scope["feature_ids"]) - features.keys()),
                     "undeclared": sorted(features.keys() - set(scope["feature_ids"]))})
    if not checks:
        gaps.append({"kind": "no_peripheral_checks"})
    statuses = [r["status"] for collection in (sources, pin_results, checks, features) for r in collection.values()]
    status = "FAIL" if errors or "FAIL" in statuses else "INSUFFICIENT" if gaps or "INSUFFICIENT" in statuses else "PASS"
    return {"schema_version": 1, "status": status,
            "scope": "Declared source hashes, full pin maps and native topology/population facts only; stage semantics and scope completeness require independent review.",
            "netlist_sha256": native["sha256"], "contract_sha256": hashlib.sha256(json.dumps(contract, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            "sources": sources, "pin_maps": pin_results, "checks": checks, "features": features, "errors": errors, "coverage_gaps": gaps,
            "unverified": ["Manufacturer authority and interpretation of source text", "Adequacy of declared core/feature scope and stages", "Footprint mechanical dimensions", "Transfer functions, load and transient margins", "DNP alternatives and fitted zero-ohm graph equivalence", "Native visual review and physical validation"]}
