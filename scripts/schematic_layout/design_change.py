"""Verify an explicit electrical-change contract against two native XML files.

Before/after partitions are authored from design intent, not learned from the
candidate. No implicit net-name union, blanket ignore list, or pin dropping.
Virtual refs beginning '#' are excluded consistently; physical singleton pins
remain significant. This does not calculate electrical performance.
"""
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET


FIELDS = {"value", "footprint", "datasheet", "lib_id", "dnp", "fields"}


def _partition(pins):
    if not isinstance(pins, list) or not pins or any(not isinstance(p, str) or "." not in p or p.startswith("#") for p in pins):
        raise ValueError("A partition must contain physical reference.pin strings")
    if len(pins) != len(set(pins)):
        raise ValueError("Duplicate pin in partition")
    if any(not all(p.rsplit(".", 1)) for p in pins):
        raise ValueError("Missing physical reference or pin number")
    return frozenset(pins)


def read_native(path):
    raw = Path(path).read_bytes()
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("Malformed native XML") from exc
    if root.tag != "export" or root.find("components") is None or root.find("nets") is None:
        raise ValueError("Expected a KiCad XML netlist")
    components = {}
    for c in root.findall("components/comp"):
        ref = c.get("ref", "")
        if ref.startswith("#"):
            continue
        if not ref or ref in components:
            raise ValueError("Missing or duplicate component reference")
        lib = c.find("libsource")
        fields = [(f.get("name"), f.text or "") for f in c.findall("fields/field")]
        if any(not name for name, _ in fields) or len(dict(fields)) != len(fields):
            raise ValueError("Missing or duplicate component field name")
        components[ref] = {"value": c.findtext("value") or "", "footprint": c.findtext("footprint") or "",
                           "datasheet": c.findtext("datasheet") or "",
                           "lib_id": f"{lib.get('lib')}:{lib.get('part')}" if lib is not None else "",
                           "dnp": c.find("property[@name='dnp']") is not None, "fields": dict(fields)}
    partitions, pin_nets, named = set(), {}, {}
    for net in root.findall("nets/net"):
        if any(not n.get("ref") or not n.get("pin") for n in net.findall("node")):
            raise ValueError("Native net node is missing reference or pin")
        pins = [f"{n.get('ref')}.{n.get('pin')}" for n in net.findall("node") if not n.get("ref", "").startswith("#")]
        if not pins:
            continue
        group = _partition(pins)
        for pin in group:
            if pin.rsplit(".", 1)[0] not in components:
                raise ValueError("Net pin references an absent physical component")
            if pin in pin_nets:
                raise ValueError("Physical pin appears in multiple nets")
            pin_nets[pin] = group
        partitions.add(group)
        name = net.get("name", "")
        if name in named:
            raise ValueError("Duplicate nonempty native net name")
        named[name] = group
    for ref in components:
        if not any(p.startswith(ref + ".") for p in pin_nets):
            raise ValueError(f"Component {ref} has no exported physical pins")
    return {"sha256": hashlib.sha256(raw).hexdigest(), "components": components,
            "partitions": partitions, "pin_nets": pin_nets, "named": named}


def _identity(descriptor):
    if not isinstance(descriptor, dict) or set(descriptor) != FIELDS:
        raise ValueError("Identity must specify exactly value, footprint, datasheet, lib_id, dnp and fields")
    if not isinstance(descriptor["dnp"], bool) or not isinstance(descriptor["fields"], dict):
        raise ValueError("Invalid identity dnp/fields")
    if any(not isinstance(descriptor[k], str) for k in FIELDS - {"dnp", "fields"}):
        raise ValueError("Identity text fields must be strings")
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in descriptor["fields"].items()):
        raise ValueError("Named field keys/values must be strings")
    return descriptor


def verify_change(before_path, after_path, contract):
    allowed = {"schema_version", "baseline_sha256", "remove_components", "add_components", "component_changes", "replace_partitions", "named_nets", "same_net", "distinct_net"}
    if not isinstance(contract, dict) or set(contract) - allowed or contract.get("schema_version") != 1:
        raise ValueError("Unknown contract field or unsupported schema_version")
    for key in ["add_components", "component_changes", "named_nets"]:
        if not isinstance(contract.get(key, {}), dict):
            raise ValueError(f"{key} must be an object")
    for key in ["remove_components", "replace_partitions", "same_net", "distinct_net"]:
        if not isinstance(contract.get(key, []), list):
            raise ValueError(f"{key} must be a list")
    old, new = read_native(before_path), read_native(after_path)
    if "baseline_sha256" in contract and contract["baseline_sha256"] != old["sha256"]:
        raise ValueError("Baseline SHA256 does not match the frozen contract")
    expected_components = {r: dict(v) for r, v in old["components"].items()}
    removed = contract.get("remove_components", [])
    if not isinstance(removed, list) or len(removed) != len(set(removed)):
        raise ValueError("Duplicate/invalid remove_components")
    for ref in removed:
        if ref not in expected_components:
            raise ValueError("Removed reference absent from baseline")
        del expected_components[ref]
    added_pins = set()
    for ref, data in contract.get("add_components", {}).items():
        if ref in old["components"] or ref.startswith("#") or set(data) != {"identity", "pins"}:
            raise ValueError("Invalid added component")
        expected_components[ref] = _identity(data["identity"])
        pins = data["pins"]
        if not isinstance(pins, list) or not pins or len(pins) != len(set(pins)) or any(not isinstance(p, str) or not p or "." in p for p in pins):
            raise ValueError("Added component requires every physical pin number")
        added_pins.update(ref + "." + p for p in pins)
    for ref, changes in contract.get("component_changes", {}).items():
        if ref not in old["components"] or ref in removed or not isinstance(changes, dict) or not changes or set(changes) - FIELDS:
            raise ValueError("Invalid component change")
        for key, change in changes.items():
            if set(change) != {"before", "after"} or old["components"][ref][key] != change["before"]:
                raise ValueError("Component change precondition does not match baseline")
            expected_components[ref][key] = change["after"]
        _identity(expected_components[ref])
    expected_partitions = set(old["partitions"])
    consumed, produced = set(), set()
    for change in contract.get("replace_partitions", []):
        if set(change) != {"before", "after"}:
            raise ValueError("Partition replacement needs before and after")
        for pins in change["before"]:
            group = _partition(pins)
            if group not in old["partitions"] or group in consumed:
                raise ValueError("Partition precondition absent or used twice")
            consumed.add(group)
            expected_partitions.remove(group)
        for pins in change["after"]:
            group = _partition(pins)
            if group in produced:
                raise ValueError("Duplicate expected partition")
            produced.add(group)
    if expected_partitions & produced:
        raise ValueError("Replacement repeats an untouched partition")
    expected_partitions |= produced
    expected_pins = {p for p in old["pin_nets"] if p.rsplit(".", 1)[0] not in removed} | added_pins
    declared = [p for group in expected_partitions for p in group]
    if len(declared) != len(set(declared)) or set(declared) != expected_pins:
        raise ValueError("Contract loses, invents or multiply assigns physical pins")
    errors = []
    if expected_components != new["components"]:
        errors.append({"kind": "component_identity_or_set_mismatch",
                       "references": sorted(r for r in expected_components.keys() | new["components"].keys()
                                            if expected_components.get(r) != new["components"].get(r))})
    if expected_partitions != new["partitions"]:
        errors.append({"kind": "pin_partition_mismatch",
                       "missing": sorted(sorted(s) for s in expected_partitions - new["partitions"]),
                       "unexpected": sorted(sorted(s) for s in new["partitions"] - expected_partitions)})
    for name, pins in contract.get("named_nets", {}).items():
        group = _partition(pins)
        if not group <= expected_pins:
            raise ValueError("Named net contains unknown physical pins")
        if new["named"].get(name) != group:
            errors.append({"kind": "named_interface_mismatch", "name": name})
    for key in ["same_net", "distinct_net"]:
        for pins in contract.get(key, []):
            group = _partition(pins)
            if len(group) < 2 or not group <= expected_pins:
                raise ValueError("Pin contract needs at least two known physical pins")
            found = [new["pin_nets"].get(pin) for pin in group]
            valid = None not in found and (len(set(found)) == 1 if key == "same_net" else len(set(found)) == len(group))
            if not valid:
                errors.append({"kind": key + "_mismatch", "pins": sorted(group)})
    return {"status": "FAIL" if errors else "PASS", "errors": errors,
            "baseline_sha256": old["sha256"], "candidate_sha256": new["sha256"],
            "old_components": len(old["components"]), "new_components": len(new["components"]),
            "expected_partitions": len(expected_partitions), "actual_partitions": len(new["partitions"]),
            "scope": "Explicit physical connectivity, component identity, named interfaces and pin contracts only; not electrical performance or release."}
