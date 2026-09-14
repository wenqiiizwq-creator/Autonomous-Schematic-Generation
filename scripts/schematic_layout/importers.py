"""Data adapters for upstream circuit representations (no source execution).

The circuit-synth exporter loses local-vs-external net object identity. The
caller must resolve repeated names explicitly. Missing pins remain unassigned.
"""

import copy
from collections import Counter
from .circuit_ir import identifier
from .generate import digest


def skidl_to_ir(circuit, design_id, symbol_map):
    """Read an already-built SKiDL Circuit without mutating it or executing code.

    symbol_map must explicitly map every physical reference to a KiCad lib_id;
    an ad-hoc/backup-library Part name is not sufficient component identity.
    Node/Part tags are used as stable instance IDs. Actual connected-net objects
    supply cross-module membership; this preserves connectivity without guessing
    from net names. Call from the user's trusted SKiDL script and write the JSON.
    """
    parts = list(circuit.parts)
    if set(symbol_map) != {p.ref for p in parts}:
        raise ValueError("symbol_map must cover exactly all SKiDL physical references")
    net_members, aliases, pin_to_net = {}, {}, {}
    for net in circuit.get_nets():
        names = sorted({str(n.name) for n in net.get_nets()})
        name = identifier(
            names[0], "SKiDL net name (rename unsupported punctuation explicitly)"
        )
        if name in net_members:
            raise ValueError(
                f"Distinct SKiDL net objects share name {name}; rename explicitly"
            )
        members = sorted({(p.part.ref, str(p.num)) for p in net.get_pins()})
        net_members[name] = members
        aliases[name] = names
        for pin in members:
            if pin in pin_to_net:
                raise ValueError(f"SKiDL pin belongs to distinct nets: {pin}")
            pin_to_net[pin] = name
    nc = {(p.part.ref, str(p.num)) for p in circuit.NC.get_pins()}
    modules, references, visited_parts = {}, {}, set()
    counter = [0]

    def visit(node, path):
        module = {
            "components": [],
            "nets": [],
            "no_connect": [],
            "instances": [],
            "ports": [],
        }
        used_nets = set()
        local = {}
        for p in node.parts:
            cid = identifier(str(p.tag or p.ref), "SKiDL Part tag/ref")
            if cid in local or p.ref in visited_parts:
                raise ValueError("Duplicate SKiDL Part tag/reference")
            local[cid] = p
            visited_parts.add(p.ref)
            full = f"{path}/{cid}".strip("/")
            references[full] = p.ref
            c = {
                "id": cid,
                "lib_id": symbol_map[p.ref],
                "value": str(p.value),
                "footprint": str(getattr(p, "footprint", "") or ""),
                "fields": {"ImportedSKiDLTag": str(p.tag or "")},
            }
            # Preserve explicit procurement/assembly data too. The Part's live
            # ref/value/footprint take precedence over library template fields.
            source_fields = getattr(p, "fields", {})
            for field, item in source_fields.items():
                if field not in (
                    "Reference",
                    "Value",
                    "Footprint",
                    "Datasheet",
                    "MPN",
                    "DNP",
                ):
                    c["fields"][field] = copy.deepcopy(item)
            for attr, field in (("mpn", "MPN"), ("datasheet", "Datasheet")):
                item = getattr(p, attr, None) or source_fields.get(field)
                if item is not None:
                    c[attr] = str(item)
            dnp = getattr(p, "dnp", source_fields.get("DNP", False))
            if isinstance(dnp, str):
                flags = {
                    "true": True,
                    "yes": True,
                    "1": True,
                    "false": False,
                    "no": False,
                    "0": False,
                    "": False,
                }
                if dnp.lower() not in flags:
                    raise ValueError(f"{p.ref}: ambiguous SKiDL DNP state {dnp}")
                dnp = flags[dnp.lower()]
            if not isinstance(dnp, bool):
                raise ValueError(f"{p.ref}: invalid SKiDL DNP state")
            c["dnp"] = dnp
            if hasattr(p, "ratings"):
                c["ratings"] = copy.deepcopy(p.ratings)
            module["components"].append(c)
            for pin in p.pins:
                key = (p.ref, str(pin.num))
                if key in nc:
                    module["no_connect"].append(f"{cid}.{pin.num}")
                if key in pin_to_net:
                    used_nets.add(pin_to_net[key])
        child_ids = set()
        for child in node.children:
            iid = identifier(str(child.tag_or_name), "SKiDL Node tag/name")
            if iid in child_ids or iid in local:
                raise ValueError(
                    "Duplicate SKiDL Node tag/name; set stable tags explicitly"
                )
            child_ids.add(iid)
            child_module, child_nets = visit(child, f"{path}/{iid}".strip("/"))
            counter[0] += 1
            key = f"skidl_module_{counter[0]}"
            child_module["ports"] = sorted(child_nets)
            modules[key] = child_module
            module["instances"].append(
                {
                    "id": iid,
                    "module": key,
                    "bindings": {n: n for n in sorted(child_nets)},
                }
            )
            used_nets.update(child_nets)
        for name in sorted(used_nets):
            pins = [
                f"{cid}.{pin.num}"
                for cid, p in sorted(local.items())
                for pin in p.pins
                if pin_to_net.get((p.ref, str(pin.num))) == name
            ]
            module["nets"].append({"name": name, "pins": sorted(pins)})
        return module, used_nets

    root, _ = visit(circuit.root, "")
    if visited_parts != set(symbol_map):
        raise ValueError("SKiDL Node tree does not cover all circuit parts")
    return {
        "schema_version": 2,
        "design_id": identifier(design_id, "design_id"),
        "title": design_id,
        "modules": modules,
        "root": root,
        "references": references,
        "evidence": [
            {
                "source": "SKiDL Circuit objects",
                "net_aliases": aliases,
                "review": "PENDING",
            }
        ],
    }


def circuit_synth_to_ir(data, design_id, shared_nets=(), local_nets=(), no_connect=()):
    """Adapt NetlistExporter.to_dict() list/nodes forms, with audited net scopes.

    shared_nets are names intentionally shared across ALL occurrences; local_nets
    are repeated names explicitly confirmed independent. Mixed scopes need an
    edited IR with explicit module bindings; guessing is forbidden.
    """
    shared, local = set(shared_nets), set(local_nets)
    if shared & local:
        raise ValueError("A name cannot be both shared and local")
    nodes = []

    def scan(node, path):
        nodes.append((path, node))
        siblings = set()
        for child in node.get("subcircuits", []):
            name = identifier(child["name"], "circuit-synth subcircuit name")
            if name in siblings:
                raise ValueError(
                    "Duplicate subcircuit names require explicit stable renaming"
                )
            siblings.add(name)
            scan(child, f"{path}/{name}".strip("/"))

    scan(data, "")
    counts = Counter(name for _, n in nodes for name in n.get("nets", {}))
    ambiguous = {n for n, count in counts.items() if count > 1} - shared - local
    if ambiguous:
        raise ValueError(
            f"Ambiguous circuit-synth net scope: {sorted(ambiguous)}; declare shared_nets or local_nets"
        )
    if (shared | local) - set(counts):
        raise ValueError("Scope policy references absent net names")
    modules, references, instances, source_records = {}, {}, [], []
    root = {"components": [], "nets": [], "instances": instances}
    root_nets = {name: {"name": name, "pins": []} for name in shared}
    nc_remaining = set(no_connect)
    for i, (path, node) in enumerate(nodes):
        # Preserve hierarchy in stable IDs even though this import creates a
        # leaf-module presentation of each source sheet. Source path is retained.
        instance = path.replace("/", "__") if path else "source_root"
        identifier(instance, "source path")
        if any(x["id"] == instance for x in instances):
            raise ValueError("Imported source paths collide after qualification")
        module = {"components": [], "nets": [], "no_connect": [], "ports": []}
        for ref, c in node.get("components", {}).items():
            if c.get("ref", c.get("reference", ref)) != ref:
                raise ValueError(f"Inconsistent component reference {ref}")
            if not c.get("symbol"):
                raise ValueError(
                    f"{ref}: missing library symbol; cannot reconstruct it from value"
                )
            comp = {
                "id": ref,
                "lib_id": c["symbol"],
                "value": c.get("value", ""),
                "footprint": c.get("footprint", ""),
                "datasheet": c.get("datasheet", ""),
                "fields": {"ImportedSourcePath": path},
            }
            for field in ("mpn", "dnp"):
                if field in c:
                    comp[field] = c[field]
            # Preserve procurement and other upstream properties as hidden data.
            for group in ("properties", "_extra_fields"):
                for field, val in c.get(group, {}).items():
                    if field in (
                        "Reference",
                        "Value",
                        "Footprint",
                        "Datasheet",
                        "CircuitPath",
                        "MPN",
                    ):
                        raise ValueError(
                            f"{ref}: conflicting imported identity property {field}"
                        )
                    comp["fields"][field] = val
            module["components"].append(comp)
            references[f"{instance}/{ref}"] = ref
            nc = sorted(p for p in nc_remaining if p.rsplit(".", 1)[0] == ref)
            module["no_connect"].extend(nc)
            nc_remaining.difference_update(nc)
        for name, raw in node.get("nets", {}).items():
            identifier(name, "imported net")
            connections = raw.get("nodes") if isinstance(raw, dict) else raw
            if not isinstance(connections, list):
                raise ValueError(f"Unsupported net encoding: {name}")
            pins = []
            for connection in connections:
                number = connection.get("pin", {}).get("number")
                if number is None or str(number) == "":
                    raise ValueError(f"{name}: missing physical pin number")
                pins.append(f"{connection['component']}.{number}")
            module["nets"].append({"name": name, "pins": pins})
            if name in shared:
                module["ports"].append(name)
        if module["components"]:
            modname = f"imported_{i}"
            modules[modname] = module
            instances.append(
                {
                    "id": instance,
                    "module": modname,
                    "bindings": {n: n for n in module["ports"]},
                }
            )
        elif node.get("nets"):
            if any(
                (r.get("nodes", []) if isinstance(r, dict) else r)
                for r in node["nets"].values()
            ):
                raise ValueError(
                    "Connections on an empty source sheet require explicit port reconstruction"
                )
        source_records.append({"path": path, "source": copy.deepcopy(node)})
    if nc_remaining:
        raise ValueError(
            f"NC pins reference unknown components: {sorted(nc_remaining)}"
        )
    root["nets"] = list(root_nets.values())
    return {
        "schema_version": 2,
        "design_id": identifier(design_id, "design_id"),
        "title": data.get("name", design_id),
        "modules": modules,
        "root": root,
        "references": references,
        "evidence": [
            {
                "kind": "upstream_import",
                "source": "circuit-synth",
                "source_sha256": digest(data),
                "review": "PENDING",
            }
        ],
    }, {
        "source_sha256": digest(data),
        "source_records": source_records,
        "shared_nets": sorted(shared),
        "local_nets": sorted(local),
        "notes": [
            "Source annotations/coordinates are preserved here as evidence, not imported as layout.",
            "Unassigned pins are not converted to no-connect; compile against the actual library.",
            "is_power/trace_current/impedance metadata is evidence, not proof or an ERC override.",
        ],
    }
