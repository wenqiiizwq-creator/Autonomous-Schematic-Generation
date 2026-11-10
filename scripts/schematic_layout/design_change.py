"""Read a KiCad-exported native XML netlist: components, pin partitions and pinless objects.

Virtual refs beginning '#' are excluded consistently; physical singleton pins
remain significant. This does not calculate electrical performance.
"""
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET


PINLESS_ROLES = ("mechanical", "documentation")


class UnqualifiedPinlessObjects(ValueError):
    """Strict rejection with structurally parsed facts for local diagnostics only.

    Consumers must retain FAIL, never accept these facts as qualified
    connectivity or infer object roles.
    """
    def __init__(self, references, diagnostic_native):
        self.references = tuple(references)
        self.diagnostic_native = diagnostic_native
        super().__init__(f"Component {self.references[0]} has no exported physical pins")


def native_inventory(path):
    """Independent export diagnostics, never electrical qualification.

    Counts are XML element occurrences, not inferred physical parts/pins. They
    remain available when the stricter partition/identity reader rejects XML.
    """
    raw = Path(path).read_bytes()
    result = {"status": "INSUFFICIENT", "qualification": "NOT_EVALUATED",
              "sha256": hashlib.sha256(raw).hexdigest(),
              "count_domain": "Native XML component/node element occurrences"}
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return {**result, "reason": "Malformed native XML"}
    if root.tag != "export" or root.find("components") is None or root.find("nets") is None:
        return {**result, "reason": "Expected a KiCad XML netlist"}
    comps, nodes = root.findall("components/comp"), root.findall("nets/net/node")
    physical = [c for c in comps if not c.get("ref", "").startswith("#")]
    endpoints = [n for n in nodes if not n.get("ref", "").startswith("#")]
    connected = {n.get("ref") for n in endpoints}
    return {**result, "status": "DIAGNOSTIC_ONLY", "export_component_count": len(comps),
            "export_endpoint_count": len(nodes), "physical_component_count": len(physical),
            "physical_endpoint_count": len(endpoints),
            "physical_unique_endpoint_count": len({(n.get("ref"), n.get("pin")) for n in endpoints}),
            "physical_references": sorted({c.get("ref", "") for c in physical}),
            "zero_endpoint_references": sorted(c.get("ref", "") for c in physical if c.get("ref") not in connected)}


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
    # A part with no exported pins is a mounting hole, logo or note only when the drawing says so
    # (ComponentRole, checked against the intent by intent_netlist) and its library part has no pins at all.
    libpart_pins = {(lp.get("lib"), lp.get("part")): bool(lp.findall("pins/pin")) for lp in root.findall("libparts/libpart")}
    pinless = {}
    for c in root.findall("components/comp"):
        ref, lib = c.get("ref", ""), c.find("libsource")
        if ref not in components or any(p.startswith(ref + ".") for p in pin_nets) or lib is None:
            continue
        role = components[ref]["fields"].get("ComponentRole")
        if role in PINLESS_ROLES and libpart_pins.get((lib.get("lib"), lib.get("part"))) is False:
            pinless[ref] = {"status": "NA", "role": role, "reason": "Declared ComponentRole; library part has no pins"}
    unqualified = [ref for ref in components
                   if not any(p.startswith(ref + ".") for p in pin_nets)
                   and ref not in pinless]
    native = {"sha256": hashlib.sha256(raw).hexdigest(), "components": components,
              "partitions": partitions, "pin_nets": pin_nets, "named": named,
              "pinless_objects": pinless, "native_inventory": native_inventory(path)}
    if unqualified:
        raise UnqualifiedPinlessObjects(unqualified, native)
    return native
