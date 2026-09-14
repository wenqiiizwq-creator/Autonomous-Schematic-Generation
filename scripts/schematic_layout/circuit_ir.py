"""Circuit IR v2: reusable modules, explicit ports, stable identity and real pins.

Inspired by SKiDL Part/Net/Node/tags and circuit-synth's hierarchical JSON.
This is an independent implementation, not a compatible Python interpreter.
Presentation is a separate document. No implicit same-name merging or NC fill.
"""

import copy
import re
from .generate import Libraries, library_dirs, digest, pin_net_map
from .sexpr import all_nodes, value, dump


def keys(obj, allowed, context):
    if not isinstance(obj, dict):
        raise ValueError(f"{context}: expected an object")
    unknown = set(obj) - set(allowed.split())
    if unknown:
        raise ValueError(f"{context}: unknown fields {sorted(unknown)}")


def identifier(s, context):
    if not isinstance(s, str) or not re.fullmatch(r"[A-Za-z0-9_+-]+", s):
        raise ValueError(f"{context}: use letters, digits, _, +, -")
    return s


def symbol_catalog(lib):
    """Pin numbers are strings; names may resolve to several physical pins."""
    pins = {}
    for sub in all_nodes(lib, "symbol"):
        m = re.search(r"_(\d+)_(\d+)$", str(sub[1]))
        if not m or int(m[2]) not in (0, 1):
            continue
        for p in all_nodes(sub, "pin"):
            number = str(value(p, "number"))
            item = {
                "number": number,
                "name": str(value(p, "name", "")),
                "unit": int(m[1]),
                "type": str(p[1]),
            }
            if number in pins and pins[number] != item:
                raise ValueError(f"Stacked/duplicate physical pin {number}")
            pins[number] = item
    if not pins:
        raise ValueError("Symbol has no physical pin data")
    return pins


def substitute(obj, parameters):
    if isinstance(obj, dict):
        if set(obj) == {"param"}:
            if obj["param"] not in parameters:
                raise ValueError(f"Missing parameter {obj['param']}")
            return copy.deepcopy(parameters[obj["param"]])
        return {k: substitute(v, parameters) for k, v in obj.items()}
    if isinstance(obj, list):
        return [substitute(v, parameters) for v in obj]
    return obj


def compile_circuit(document, dirs=()):
    keys(
        document,
        "schema_version design_id title revision modules root references evidence",
        "circuit",
    )
    if document.get("schema_version") != 2:
        raise ValueError("Circuit IR requires schema_version 2")
    design_id = identifier(document["design_id"], "design_id")
    libraries = Libraries(library_dirs(dirs))
    intent = {
        "schema_version": 1,
        "design_id": design_id,
        "title": document.get("title", design_id),
        "revision": document.get("revision", "draft"),
        "components": [],
        "nets": [],
        "no_connect": [],
    }
    refs = document["references"]
    modules = document.get("modules", {})
    netpins, netmeta, blocks, resolved, used_refs = {}, {}, [], {}, set()
    canonical_names = {}
    pin_audit = []
    hierarchy = []

    def net_key(path, name):
        identifier(name, "net")
        key = (path, name)
        label = "__".join([*(path.split("/") if path else []), name])
        if label in canonical_names and canonical_names[label] != key:
            raise ValueError(f"Qualified net-name collision: {label}")
        canonical_names[label] = key
        return label

    def visit(module, path, bindings, parameters, stack):
        keys(
            module,
            "ports parameters components nets no_connect instances buses evidence",
            path or "root",
        )
        defaults = module.get("parameters", {})
        if set(parameters) - set(defaults):
            raise ValueError(f"{path}: unknown parameters")
        module = substitute(module, {**defaults, **parameters})
        ports = module.get("ports", [])
        if len(set(ports)) != len(ports) or set(bindings) != set(ports):
            raise ValueError(f"{path}: ports must be bound exactly once")
        local_nets = {}
        for n in module.get("nets", []):
            keys(n, "name pins class constraints evidence", "net")
            name = identifier(n["name"], "net")
            if name in local_nets:
                raise ValueError(f"{path}: duplicate net {name}")
            target = bindings[name] if name in bindings else net_key(path, name)
            local_nets[name] = target
            netpins.setdefault(target, [])
            netmeta.setdefault(target, []).append({"path": path, **copy.deepcopy(n)})
        if set(ports) - set(local_nets):
            raise ValueError(f"{path}: port lacks a declared net")
        members, local = [], {}
        for c in module.get("components", []):
            keys(
                c,
                "id lib_id value footprint mpn datasheet dnp fields ratings evidence role symbol_sha256",
                "component",
            )
            cid = identifier(c["id"], "component id")
            full = f"{path}/{cid}" if path else cid
            if cid in local or full not in refs:
                raise ValueError(
                    f"Duplicate component or missing reference mapping: {full}"
                )
            ref = refs[full]
            if (
                not isinstance(ref, str)
                or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", ref)
                or ref in used_refs
            ):
                raise ValueError(f"Duplicate/invalid physical reference {ref}")
            used_refs.add(ref)
            lib = libraries.load(c["lib_id"])
            sha = digest(dump(lib))
            if c.get("symbol_sha256", sha) != sha:
                raise ValueError(f"{full}: locked symbol hash changed")
            pins = symbol_catalog(lib)
            comp = {
                k: copy.deepcopy(v)
                for k, v in c.items()
                if k not in ("id", "role", "symbol_sha256")
            }
            if not isinstance(comp.get("value"), str) or not isinstance(
                comp.get("footprint"), str
            ):
                raise ValueError(
                    f"{full}: explicit string value and footprint required (empty allowed for drafts)"
                )
            for k in ("mpn", "datasheet"):
                if k in comp and not isinstance(comp[k], str):
                    raise ValueError(f"{full}: {k} must be a string")
            if not isinstance(comp.get("dnp", False), bool):
                raise ValueError(f"{full}: dnp must be boolean")
            comp.update(
                ref=ref,
                stable_id=full,
                hierarchy=path,
                units=sorted({p["unit"] for p in pins.values() if p["unit"] > 0}),
            )
            intent["components"].append(comp)
            local[cid] = (ref, pins)
            members.append({"id": full, "ref": ref, "role": c.get("role", "support")})
            resolved[full] = {
                "ref": ref,
                "lib_id": c["lib_id"],
                "symbol_sha256": sha,
                "pins": pins,
            }

        def endpoints(ep):
            if isinstance(ep, str):
                if "." not in ep:
                    raise ValueError(f"{path}: use component.physical_pin_number")
                cid, number = ep.rsplit(".", 1)
                selector = {"component": cid, "pin": number}
            else:
                selector = ep
                keys(selector, "component pin pin_name all", "pin selector")
            cid = selector["component"]
            if cid not in local:
                raise ValueError(
                    f"{path}: unknown local component {cid}; connect instances through ports"
                )
            ref, pins = local[cid]
            if ("pin" in selector) == ("pin_name" in selector):
                raise ValueError(
                    "Select either a physical pin number or an exact pin name"
                )
            if "pin" in selector:
                matches = [str(selector["pin"])] if str(selector["pin"]) in pins else []
            else:
                matches = sorted(
                    n for n, p in pins.items() if p["name"] == selector["pin_name"]
                )
                if len(matches) > 1 and selector.get("all") is not True:
                    raise ValueError(
                        f"{ref}: ambiguous pin name {selector['pin_name']}; use numbers or all:true"
                    )
            if not matches:
                raise ValueError(f"{ref}: nonexistent pin selector {selector}")
            result = [f"{ref}.{n}" for n in matches]
            pin_audit.append({"path": path, "selector": selector, "resolved": result})
            return result

        for n in module.get("nets", []):
            for ep in n.get("pins", []):
                netpins[local_nets[n["name"]]].extend(endpoints(ep))
        for ep in module.get("no_connect", []):
            intent["no_connect"].extend(endpoints(ep))
        # Buses are ordered scalar-net interfaces, not inferred graphical wires.
        buses = []
        for bus in module.get("buses", []):
            keys(bus, "name members", "bus")
            if not bus["members"] or len(set(bus["members"])) != len(bus["members"]):
                raise ValueError("Bus members must be nonempty and distinct")
            if set(bus["members"]) - set(local_nets):
                raise ValueError("Bus references undeclared scalar nets")
            buses.append(
                {
                    "name": bus["name"],
                    "members": [local_nets[n] for n in bus["members"]],
                }
            )
        if members:
            blocks.append(
                {
                    "id": path or "root",
                    "members": members,
                    "ports": {p: local_nets[p] for p in ports},
                    "buses": buses,
                }
            )
        hierarchy.append(
            {
                "path": path,
                "parent": path.rsplit("/", 1)[0] if "/" in path else "",
                "ports": {p: local_nets[p] for p in ports},
                "buses": buses,
                "members": [m["id"] for m in members],
            }
        )
        instance_ids = set()
        for inst in module.get("instances", []):
            keys(inst, "id module bindings parameters", "instance")
            iid = identifier(inst["id"], "instance")
            target = inst["module"]
            if iid in instance_ids or iid in local:
                raise ValueError(f"{path}: duplicate instance/component id {iid}")
            instance_ids.add(iid)
            if target in stack or target not in modules:
                raise ValueError(f"Unknown/recursive module {target}")
            binding = inst.get("bindings", {})
            if set(binding.values()) - set(local_nets):
                raise ValueError(
                    f"{path}/{iid}: binding references undeclared parent net"
                )
            visit(
                modules[target],
                f"{path}/{iid}".strip("/"),
                {p: local_nets[n] for p, n in binding.items()},
                inst.get("parameters", {}),
                (*stack, target),
            )

    visit(document["root"], "", {}, {}, ())
    if set(refs) != set(resolved):
        raise ValueError(
            f"Unused reference mappings: {sorted(set(refs) - set(resolved))}"
        )
    intent["components"].sort(key=lambda c: c["stable_id"])
    intent["nets"] = [
        {"name": n, "pins": sorted(p)} for n, p in sorted(netpins.items())
    ]
    intent["no_connect"].sort()
    mapping = pin_net_map(intent)
    nc = intent["no_connect"]
    actual = {f"{c['ref']}.{p}" for c in resolved.values() for p in c["pins"]}
    if len(set(nc)) != len(nc) or set(nc) & set(mapping):
        raise ValueError("Duplicate NC or NC also connected")
    if actual != set(mapping) | set(nc):
        raise ValueError(
            f"Unassigned pins {sorted(actual - set(mapping) - set(nc))}; unknown {sorted((set(mapping) | set(nc)) - actual)}"
        )
    return intent, {
        "schema_version": 2,
        "design_id": design_id,
        "input_sha256": digest(document),
        "blocks": sorted(blocks, key=lambda b: b["id"]),
        "resolved_components": resolved,
        "pin_resolution": pin_audit,
        "hierarchy": hierarchy,
        "net_sources": netmeta,
        "library_sources": libraries.sources,
        "evidence": document.get("evidence", []),
        "electrical_review": "PENDING",
    }
