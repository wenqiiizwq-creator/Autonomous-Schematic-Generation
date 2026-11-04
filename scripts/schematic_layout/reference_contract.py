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
from .component_role import is_connector
from .design_change import read_native, UnqualifiedPinlessObjects


def _field_path(context, key):
    # JSON pointer tokens keep identifiers containing '/' or '~' unambiguous.
    # Non-JSON keys are invalid schema fields; never print an arbitrary object.
    token = key if isinstance(key, str) else f"<{type(key).__name__} key>"
    return context + "/" + token.replace("~", "~0").replace("/", "~1")


def _keys(obj, required, optional=(), *, context):
    expected = f"Expected fields {sorted(required)}, optional {sorted(optional)}"
    if not isinstance(obj, dict):
        raise ValueError(f"{context}: Expected object; {expected}")
    missing = set(required) - set(obj)
    extra = set(obj) - set(required) - set(optional)
    if missing or extra:
        missing_paths = sorted(_field_path(context, key) for key in missing)
        extra_paths = sorted(_field_path(context, key) for key in extra)
        raise ValueError(f"{context}: {expected}; missing {missing_paths}; extra {extra_paths}")


def _text(s, context="text"):
    if not isinstance(s, str) or not s.strip():
        raise ValueError(f"{context}: Expected nonempty text")
    return s


def verify_reference(netlist, contract, base):
    _keys(contract, {"schema_version", "scope", "sources", "pin_maps", "checks", "features"}, context="contract")
    if contract["schema_version"] != 1:
        raise ValueError("Unsupported reference contract version")
    scope = contract["scope"]
    # Which parts need a pin map follows from the netlist; core_refs is accepted but no longer decides it.
    _keys(scope, {"feature_ids"}, {"core_refs"}, context="contract/scope")
    for values in scope.values():
        if not isinstance(values, list) or not values or any(not isinstance(x, str) or not x for x in values) or len(set(values)) != len(values):
            raise ValueError("Scope must declare nonempty unique feature_ids (and core_refs when given)")
    if not isinstance(contract["sources"], dict) or not isinstance(contract["pin_maps"], dict) or not isinstance(contract["checks"], list) or not isinstance(contract["features"], list):
        raise ValueError("Invalid reference contract collections")
    native_errors = []
    unqualified = []
    try:
        native = read_native(netlist)
    except UnqualifiedPinlessObjects as exc:
        # All structural/identity/role-evidence checks ran before this exception.
        # Keep whole-input FAIL; local source-bound diagnostics cannot qualify it.
        native = exc.diagnostic_native
        unqualified = list(exc.references)
        native_errors = [f"Component {ref} has no exported physical pins" for ref in unqualified]
    root = ET.parse(netlist).getroot()
    # KiCad node pinfunction may be a generated identifier (e.g. STAT_1).
    # Resolve the physical name from the exact library definition, never by
    # removing punctuation or a numeric suffix from that identifier.
    components_xml = {c.get("ref"): c for c in root.findall("components/comp")}
    library_parts = {}
    for part in root.findall("libparts/libpart"):
        library_parts.setdefault((part.get("lib"), part.get("part")), []).append(part)
    node_types = {f'{n.get("ref")}.{n.get("pin")}': n.get("pintype", "").removesuffix("+no_connect")
                  for net in root.findall("nets/net") for n in net.findall("node")}
    sources, checks, errors, gaps = {}, {}, native_errors, []
    base = Path(base).resolve()
    for sid, s in contract["sources"].items():
        _text(sid, "sources ID")
        _keys(s, {"path", "sha256"}, {"url", "document", "revision"}, context=_field_path("contract/sources", sid))
        for key, v in s.items():
            _text(v, f"source {sid}.{key}")
        if not re.fullmatch(r"[0-9a-f]{64}", s["sha256"]):
            raise ValueError("Source SHA256 must be a lowercase 64-digit digest")
        path = (base / s["path"]).resolve()
        record = {k: s[k] for k in ("sha256", "url", "document", "revision") if k in s}
        if not path.is_file():
            record.update(status="INSUFFICIENT", reason="Source file missing")
        else:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            record.update(status="PASS" if actual == s["sha256"] else "FAIL", actual_sha256=actual)
        sources[sid] = record

    def evidence(item, context):
        _text(item["locator"], f"{context}.locator")
        _text(item["source"], f"{context}.source")
        if item["source"] not in sources:
            raise ValueError(f"{context}.source: Unknown source ID {item['source']}")
        return sources[item["source"]]["status"]

    pin_results = {}
    for ref, spec in contract["pin_maps"].items():
        pin_map_context = _field_path("contract/pin_maps", ref)
        _keys(spec, {"identity", "source", "locator", "pins"}, context=pin_map_context)
        _keys(spec["identity"], {"value", "mpn", "footprint", "lib_id"}, context=pin_map_context + "/identity")
        for key, v in spec["identity"].items():
            if key == "footprint" and v == "":
                continue  # Explicitly unassigned at schematic stage; still compared exactly below.
            _text(v, f"{ref}.identity.{key}")
        if not isinstance(spec["pins"], dict) or not spec["pins"]:
            raise ValueError("Pin map must enumerate every physical pin, including NC/EP")
        failures = []
        pin_gaps = []
        type_notes = {}
        basis = evidence(spec, ref)
        component = native["components"].get(ref)
        if component is None:
            failures.append("Component absent")
        elif any((component["fields"].get("MPN") or component["value"] if k == "mpn" else component[k]) != v for k, v in spec["identity"].items()):
            failures.append("Exact part/package/library identity mismatch")
        actual = {p.rsplit(".", 1)[1] for p in native["pin_nets"] if p.rsplit(".", 1)[0] == ref}
        if actual != set(spec["pins"]):
            failures.append({"missing_from_contract": sorted(actual - spec["pins"].keys()),
                             "missing_from_native": sorted(spec["pins"].keys() - actual)})
        definitions = {}
        comp_xml = components_xml.get(ref)
        libsources = comp_xml.findall("libsource") if comp_xml is not None else []
        parts = library_parts.get((libsources[0].get("lib"), libsources[0].get("part")), []) if len(libsources) == 1 else []
        if len(libsources) != 1 or len(parts) != 1:
            pin_gaps.append("Pin metadata requires one libsource and one matching libpart")
        else:
            for pin in parts[0].findall("pins/pin"):
                number = pin.get("num")
                if not number:
                    pin_gaps.append("Library pin lacks its physical number")
                    continue
                definitions.setdefault(number, []).append(pin)
            unmapped = set(definitions) - spec["pins"].keys()
            if unmapped:
                failures.append({"library_pins_missing_from_contract": sorted(unmapped)})
        for number, expected in spec["pins"].items():
            _text(number, f"{ref}.physical pin")
            # datasheet_type: what the datasheet pin table says the pin is; audit_design_closure (binding_version 1) holds types to it.
            # datasheet_page: the page fill_pin_maps.py read the name and type from.
            # type_note: how the datasheet's type code was read, or why the symbol type differs (Matrix R2, 2026-11-04:
            # TI's P read as PWR_OUT was written only in 设计资料/外围电路核对表.md); carried into the report as written.
            note_keys = ("datasheet_name", "datasheet_type", "name_note", "type_note", "datasheet_page")
            _keys(expected, {"names", "types"}, set(note_keys), context=_field_path(pin_map_context + "/pins", number))
            if "type_note" in expected:
                type_notes[number] = _text(expected["type_note"], f"{ref} physical pin {number} type_note")
            for field, aliases in ((k, v) for k, v in expected.items() if k not in note_keys):
                if not isinstance(aliases, list) or not aliases or any(not isinstance(x, str) for x in aliases) or len(set(aliases)) != len(aliases):
                    raise ValueError(f"{ref} physical pin {number} {field}: explicit nonempty unique alias list required")
                if any(not x.strip() or x.strip() == "~" for x in aliases):
                    raise ValueError(f"{ref} physical pin {number} {field}: blank or tilde alias forbidden")
            pins = definitions.get(number, [])
            if len(pins) != 1 or "name" not in pins[0].attrib or not pins[0].get("type"):
                pin_gaps.append({"pin": number, "reason": "Missing, duplicate or incomplete library pin definition"})
                continue
            observed = {"name": pins[0].get("name"), "type": pins[0].get("type")}
            # A library pin left unnamed (~) is matched by the datasheet's name for it, written separately.
            unnamed = observed["name"] in ("", "~")
            if unnamed and not (isinstance(expected.get("datasheet_name"), str) and expected["datasheet_name"].strip()
                                and expected["datasheet_name"].strip() != "~"):
                failures.append({"pin": number, "actual": observed, "reason": "unnamed library pin needs datasheet_name"})
            elif (not unnamed and observed["name"] not in expected["names"]) or observed["type"] not in expected["types"]:
                failures.append({"pin": number, "actual": observed, "expected": expected})
            node_type = node_types.get(ref + "." + number)
            if not node_type:
                pin_gaps.append({"pin": number, "reason": "Missing native node electrical type"})
            elif node_type != observed["type"]:
                failures.append({"pin": number, "node_type": node_type, "library_type": observed["type"]})
        if pin_gaps:
            gaps.append({"kind": "native_pin_metadata", "reference": ref, "details": pin_gaps})
        pin_results[ref] = {"status": "FAIL" if failures or basis == "FAIL" else "INSUFFICIENT" if pin_gaps else basis,
                            "source": spec["source"], "locator": spec["locator"], "failures": failures,
                            "coverage_gaps": pin_gaps}
        if type_notes:
            pin_results[ref]["type_notes"] = type_notes
    # Every part with three or more pins needs a pin map, apart from connectors and pinless objects.
    pin_counts = {}
    for p in native["pin_nets"]:
        pin_counts[p.rsplit(".", 1)[0]] = pin_counts.get(p.rsplit(".", 1)[0], 0) + 1
    core = {r for r, n in pin_counts.items() if n >= 3 and not is_connector(native["components"][r])
            and r not in native["pinless_objects"]}
    if core - set(pin_results):
        gaps.append({"kind": "core_scope_mismatch", "missing": sorted(core - set(pin_results))})

    for check_index, c in enumerate(contract["checks"]):
        check_context = f"contract/checks/{check_index}"
        common = {"id", "kind", "source", "locator"}
        if not isinstance(c, dict) or c.get("kind") not in {"component", "same_net", "distinct_nets"}:
            raise ValueError(f"{check_context}/kind: Unknown peripheral check kind")
        _keys(c, common | ({"ref", "expected"} if c["kind"] == "component" else {"pins"}), context=check_context)
        cid = _text(c["id"], "check.id")
        if cid in checks:
            raise ValueError("Duplicate check ID")
        basis = evidence(c, f"check {cid}")
        failures = []
        if c["kind"] == "component":
            _keys(c["expected"], {"value", "footprint", "lib_id", "dnp"}, context=check_context + "/expected")
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
    for feature_index, f in enumerate(contract["features"]):
        feature_context = f"contract/features/{feature_index}"
        _keys(f, {"id", "boundary", "source", "locator", "stages"}, context=feature_context)
        fid = _text(f["id"], "feature.id")
        _text(f["boundary"], f"feature {fid}.boundary")
        if fid in features or not isinstance(f["stages"], list) or not f["stages"]:
            raise ValueError("Duplicate feature or empty stages")
        basis = evidence(f, f"feature {fid}")
        stage_ids, stage_results = set(), []
        for stage_index, stage in enumerate(f["stages"]):
            _keys(stage, {"id", "role", "refs", "checks"}, context=f"{feature_context}/stages/{stage_index}")
            sid = _text(stage["id"], f"feature {fid}.stage.id")
            _text(stage["role"], f"feature {fid}.stage {sid}.role")
            if sid in stage_ids or any(not isinstance(stage[k], list) or (k == "refs" and not stage[k]) or any(not isinstance(x, str) or not x for x in stage[k]) or len(set(stage[k])) != len(stage[k]) for k in ("refs", "checks")):
                raise ValueError("Stage needs unique ID, nonempty refs and a checks list")
            # A stage proven by its parts' pin maps alone (an MCU or driver page) may list no peripheral check
            # (calibration board #17, 2026-11-02); then every ref needs a pin map, whose status the stage takes.
            if not stage["checks"] and not set(stage["refs"]) <= set(pin_results):
                raise ValueError(f"Stage {sid} has no checks: every ref needs a pin map, or name a peripheral check")
            stage_ids.add(sid)
            missing = [r for r in stage["refs"] if r not in native["components"] or native["components"][r]["dnp"]]
            unknown = set(stage["checks"]) - checks.keys()
            if unknown:
                raise ValueError("Stage refers to an unknown check ID")
            statuses = [checks[k]["status"] for k in stage["checks"]] + [basis]
            if not stage["checks"]:
                statuses += [pin_results[r]["status"] for r in stage["refs"]]
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
            "native_qualification": {"status": "FAIL" if native_errors else "PASS",
                                     "unqualified_zero_pin_objects": unqualified,
                                     "scope": "Whole-native qualification remains failed when objects are unqualified; local fact results are diagnostics only in that case."},
            "unverified": ["Manufacturer authority and interpretation of source text", "Adequacy of declared core/feature scope and stages", "Footprint mechanical dimensions", "Transfer functions, load and transient margins", "DNP alternatives and fitted zero-ohm graph equivalence", "Native visual review and physical validation"]}
