"""Single-sheet native KiCad writer driven by separate intent and layout JSON."""

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import uuid
from .sexpr import Atom, all_nodes, first, value, form, set_node, parse, dump
from .geometry import Box, TextField
from .scene import read_scene
from .field_placer import FieldSpec, autoplace_fields
from .routing import (
    route,
    wire_box,
    grid_point,
    manhattan_mst,
    normalize_wires,
    segment_hits_box,
)
from .qa import check_scene


def digest(data):
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def library_dirs(extra=()):
    candidates = list(extra)
    candidates += [
        v for k, v in os.environ.items() if re.fullmatch(r"KICAD(?:\d+)?_SYMBOL_DIR", k)
    ]
    candidates += [
        "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols",
        "/usr/share/kicad/symbols",
        "/usr/local/share/kicad/symbols",
    ]
    return [
        Path(p).expanduser().resolve()
        for p in candidates
        if Path(p).expanduser().is_dir()
    ]


class Libraries:
    def __init__(self, dirs):
        self.dirs = dirs
        self.cache = {}
        self.sources = {}

    def load(self, lib_id):
        if ":" not in lib_id:
            raise ValueError(f"Invalid library ID {lib_id}")
        library, name = lib_id.split(":", 1)
        if not re.fullmatch(r"[\w-]+", library):
            raise ValueError(f"Invalid library name {library}")
        if library not in self.cache:
            path = next(
                (
                    p / f"{library}.kicad_sym"
                    for p in self.dirs
                    if (p / f"{library}.kicad_sym").is_file()
                ),
                None,
            )
            if path is None:
                raise ValueError(f"Missing symbol library {library}; use --symbol-dir")
            raw = path.read_text(encoding="utf-8")
            root = parse(raw)
            self.cache[library] = {str(n[1]): n for n in all_nodes(root, "symbol")}
            self.sources[library] = {
                "path": str(path),
                "sha256": hashlib.sha256(raw.encode()).hexdigest(),
            }

        def resolve(name, seen=()):
            if name in seen:
                raise ValueError(f"Circular library inheritance {name}")
            if name not in self.cache[library]:
                raise ValueError(f"Missing symbol {lib_id}")
            n = copy.deepcopy(self.cache[library][name])
            base = value(n, "extends")
            if base:
                parent = resolve(str(base), (*seen, name))
                child_props = {p[1] for p in all_nodes(n, "property")}
                child_keys = {
                    str(c[0])
                    for c in n[2:]
                    if isinstance(c, list)
                    and c[0] not in ("extends", "property", "symbol")
                }
                n = [
                    n[0],
                    n[1],
                    *[
                        c
                        for c in n[2:]
                        if not (isinstance(c, list) and c[0] == "extends")
                    ],
                ]
                for c in parent[2:]:
                    if c[0] == "property" and c[1] in child_props:
                        continue
                    if c[0] in child_keys:
                        continue
                    n.append(c)
            for sub in all_nodes(n, "symbol"):
                suffix = re.search(r"_(\d+)_(\d+)$", str(sub[1]))
                if suffix:
                    sub[1] = name + suffix[0]
            return n

        n = resolve(name)
        n[1] = lib_id
        return n


def pin_net_map(intent):
    result = {}
    names = set()
    for net in intent["nets"]:
        name = net["name"]
        if not isinstance(name, str) or not name or any(c.isspace() for c in name):
            raise ValueError("Net names must be nonempty and contain no whitespace")
        if name in names:
            raise ValueError(f"Duplicate net name {name}")
        names.add(name)
        if not net["pins"]:
            raise ValueError(f"Empty net {name}")
        for pid in net["pins"]:
            if pid in result:
                raise ValueError(f"Pin assigned to multiple nets: {pid}")
            result[pid] = name
    return result


def make_root(intent, layout, name, dirs=()):
    if intent.get("schema_version") != 1 or layout.get("schema_version") != 1:
        raise ValueError("Expected schema_version 1 in intent and layout")
    components = intent["components"]
    placements = layout["placements"]
    if not isinstance(components, list) or not components:
        raise ValueError("A nonempty component list is required")
    unknown = set(layout) - {
        "schema_version",
        "paper",
        "grid_mm",
        "placements",
        "nets",
        "reserved",
        "max_route_states",
        "annotations",
    }
    if unknown:
        raise ValueError(f"Unknown layout options: {sorted(unknown)}")
    for ref, placement in placements.items():
        unknown = set(placement) - {"at", "rotation", "mirror", "fields"}
        if unknown:
            raise ValueError(f"{ref}: unknown placement options {sorted(unknown)}")
        if len(placement.get("at", [])) != 2:
            raise ValueError(f"{ref}: at must contain x and y")
    for region in layout.get("reserved", []):
        if (
            len(region) != 4
            or not all(math.isfinite(x) for x in region)
            or region[0] >= region[2]
            or region[1] >= region[3]
        ):
            raise ValueError("Reserved region must have finite ordered bounds")
    if not 1 <= int(layout.get("max_route_states", 150000)) <= 1000000:
        raise ValueError("max_route_states must be between 1 and 1000000")
    refs = [c["ref"] for c in components]
    if len(set(refs)) != len(refs):
        raise ValueError(
            "Duplicate reference; multi-unit generation is not supported yet"
        )
    if any(not re.fullmatch(r"[A-Za-z#][A-Za-z0-9_#]*", r) for r in refs):
        raise ValueError("Invalid reference")
    view_keys = {view_key(c, unit) for c in components for unit in c.get("units", [1])}
    if set(placements) != view_keys:
        raise ValueError(
            "Placements must cover exactly the intent component references"
        )
    if layout.get("paper", "A4") not in ("A4", "A3", "A2", "A1", "A0"):
        raise ValueError("Generation supports landscape ISO A sheets only")
    grid = float(layout.get("grid_mm", 1.27))
    sid = intent.get("design_id") or digest(intent)
    uid = lambda key: str(
        uuid.uuid5(uuid.NAMESPACE_URL, "kicad-skill:" + sid + ":" + key)
    )
    root = [
        Atom("kicad_sch"),
        form("version", 20250114),
        form("generator", "eeschema"),
        form("uuid", uid("root")),
        form("paper", layout.get("paper", "A4")),
        form(
            "title_block",
            form("title", intent.get("title", name)),
            form("rev", intent.get("revision", "draft")),
        ),
        form("lib_symbols"),
    ]
    for i, annotation in enumerate(layout.get("annotations", [])):
        if set(annotation) - {"text", "at", "font_mm"}:
            raise ValueError("Unknown annotation options")
        root.append(
            form(
                "text",
                annotation["text"],
                form("at", *annotation["at"], 0),
                form(
                    "effects",
                    form(
                        "font",
                        form(
                            "size",
                            annotation.get("font_mm", 1.8),
                            annotation.get("font_mm", 1.8),
                        ),
                    ),
                    form("justify", Atom("left")),
                ),
                form("uuid", uid("annotation:" + digest(annotation))),
            )
        )
    libraries = Libraries(library_dirs(dirs))
    added = set()
    views = [(c, u) for c in components for u in c.get("units", [1])]
    for component, unit in views:
        ref = component["ref"]
        lib_id = component["lib_id"]
        vkey = view_key(component, unit)
        placement = placements[vkey]
        at = placement["at"]
        angle = placement.get("rotation", 0)
        mirror = placement.get("mirror", "")
        grid_point(at, grid)
        if angle not in (0, 90, 180, 270) or mirror not in ("", "x", "y"):
            raise ValueError(
                f"{ref}: only orthogonal rotations and single-axis mirrors supported"
            )
        lib = libraries.load(lib_id)
        units = {
            int(m[1])
            for sub in all_nodes(lib, "symbol")
            if (m := re.search(r"_(\d+)_(\d+)$", str(sub[1]))) and int(m[1]) > 0
        }
        if set(component.get("units", [1])) != units or unit not in units:
            raise ValueError(
                f"{ref}: multi-unit symbol requires explicit, complete units {sorted(units)}"
            )
        if lib_id not in added:
            first(root, "lib_symbols").append(lib)
            added.add(lib_id)
        sym = [
            Atom("symbol"),
            form("lib_id", lib_id),
            form("at", *at, angle),
            form("unit", unit),
            form("in_bom", Atom("yes")),
            form("on_board", Atom("yes")),
            form("dnp", Atom("yes" if component.get("dnp") else "no")),
            form("uuid", uid(component.get("stable_id", ref) + f":unit:{unit}")),
        ]
        if mirror:
            sym.append(form("mirror", Atom(mirror)))
        lib_props = {p[1]: p[2] for p in all_nodes(lib, "property")}
        props = {
            "Reference": ref,
            "Value": component["value"],
            "Footprint": component.get("footprint", lib_props.get("Footprint", "")),
            "Datasheet": component.get("datasheet", lib_props.get("Datasheet", "")),
        }
        if "mpn" in component:
            props["MPN"] = component["mpn"]
        if "hierarchy" in component:
            props["CircuitPath"] = component["hierarchy"]
        for group in ("fields", "ratings"):
            for field, text in component.get(group, {}).items():
                if field in props:
                    raise ValueError(
                        f"{ref}: custom field overrides identity field {field}"
                    )
                props[field] = str(text)
        for field, text in props.items():
            effects = form("effects", form("font", form("size", 1.27, 1.27)))
            if field not in ("Reference", "Value"):
                effects.append(form("hide", Atom("yes")))
            sym.append(form("property", field, text, form("at", *at, 0), effects))
        sym.append(
            form(
                "instances",
                form(
                    "project",
                    name,
                    form(
                        "path",
                        "/" + uid("root"),
                        form("reference", ref),
                        form("unit", unit),
                    ),
                ),
            )
        )
        root.append(sym)
    scene = read_scene(root)
    if scene.gaps:
        raise ValueError(
            "Unsupported generation geometry: " + "; ".join(sorted(set(scene.gaps)))
        )
    pins = [p for s in scene.symbols for p in s.pins]
    if len({p.id for p in pins}) != len(pins):
        raise ValueError("Stacked/duplicate numbered pins need explicit symbol support")
    mapping = pin_net_map(intent)
    nc = intent.get("no_connect", [])
    if len(set(nc)) != len(nc) or set(nc) & set(mapping):
        raise ValueError("Duplicate NC or connected pin also marked NC")
    if any(p.kind == "no_connect" and p.id not in nc for p in pins):
        raise ValueError("Library no_connect pins require explicit NC assignment")
    actual = {p.id for p in pins}
    if actual != set(mapping) | set(nc):
        raise ValueError(
            f"Pin coverage mismatch: unassigned={sorted(actual - set(mapping) - set(nc))}; unknown={sorted((set(mapping) | set(nc)) - actual)}"
        )
    for p in pins:
        grid_point(p.point, grid)
    coords = {}
    for p in pins:
        if p.point in coords:
            q = coords[p.point]
            if (p.id.rsplit('.', 1)[0] != q.id.rsplit('.', 1)[0]
                    or p.inner != q.inner or p.direction != q.direction
                    or p.id not in mapping or mapping.get(p.id) != mapping.get(q.id)):
                raise ValueError(
                    f"Coincident terminals must belong to the same symbol and connected net: {p.id}, {q.id}"
                )
        coords[p.point] = p
    for s in scene.symbols:
        for p in s.pins:
            s.node.append(
                form("pin", p.id.split(".")[-1], form("uuid", uid("pin:" + p.id)))
            )
    # Make geometry obstacles before adding fields or wires.
    page = scene.page.expanded(-5.0)
    reserved = [
        Box(*b)
        for b in layout.get(
            "reserved",
            [
                [
                    scene.page.x_max - 120,
                    scene.page.y_max - 45,
                    scene.page.x_max - 5,
                    scene.page.y_max - 5,
                ]
            ],
        )
    ]
    bodies = [s.body for s in scene.symbols]
    if any(
        a.overlaps(b, gap_mm=1.27 - 1e-6)
        for i, a in enumerate(bodies)
        for b in bodies[i + 1 :]
    ):
        raise ValueError(
            "Symbol body overlap/clearance failure; recompute layout before routing"
        )
    obstacles = [
        *bodies,
        *reserved,
        *[f.box() for _, f in scene.labels],
        *[wire_box(p.point, p.inner, 0.3) for p in pins if p.point != p.inner],
    ]
    # Explicit presentation fields are reserved first, so automatic fields and
    # routes cannot displace a reviewed capacitor-bank or control-band style.
    explicit = set()
    for s in scene.symbols:
        key = s.ref if s.ref in placements else f"{s.ref}:{s.unit}"
        fields = placements[key].get("fields", {})
        if set(fields) - {n for n, _ in s.fields}:
            raise ValueError(f"{key}: only visible fields can be positioned")
        for n, field in s.fields:
            if n not in fields:
                continue
            spec = fields[n]
            at = spec.get("at", [])
            angle = spec.get("angle", 0)
            font = spec.get("font_mm", field.font_mm)
            if (set(spec) - {"at", "angle", "font_mm"} or len(at) != 2
                    or not all(math.isfinite(v) for v in at)
                    or angle not in (0, 90) or not 1 <= font <= 5):
                raise ValueError(f"{key}.{n}: invalid field presentation")
            box = TextField(field.text, *at, angle, font).box()
            if not box.inside(page) or any(box.overlaps(o, gap_mm=0.3) for o in obstacles):
                raise ValueError(f"{key}.{n}: explicit field collides; move the field/block")
            prop = next(p for p in all_nodes(s.node, "property") if p[1] == n)
            set_node(prop, "at", *at, (angle - float(first(s.node, "at")[3])) % 180)
            set_node(first(first(prop, "effects"), "font"), "size", font, font)
            obstacles.append(box)
            explicit.add((key, n))
    for s in sorted(scene.symbols, key=lambda s: s.ref):
        key = s.ref if s.ref in placements else f"{s.ref}:{s.unit}"
        specs = [FieldSpec(n, f.text, f.font_mm) for n, f in s.fields if (key, n) not in explicit]
        placed = autoplace_fields(
            s.body, [p.point for p in s.pins], obstacles, specs, page=page
        )
        for spec, pl in zip(specs, placed):
            prop = next(p for p in all_nodes(s.node, "property") if p[1] == spec.name)
            symbol_angle = float(first(s.node, "at")[3])
            # Native rotations/mirrors can flip side justification. Encode the
            # intended world box as a centred field for an unambiguous anchor.
            field_box = pl.text_field(spec.text, spec.font_mm).box()
            cx, cy = field_box.center
            set_node(prop, "at", cx, cy, (pl.angle - symbol_angle) % 180)
            effects = first(prop, "effects")
            old = first(effects, "justify")
            if old:
                effects.remove(old)
            obstacles.append(field_box)
    return (
        root,
        {
            "schema_version": 1,
            "intent_sha256": digest(intent),
            "layout_sha256": digest(layout),
            "library_sources": libraries.sources,
            "grid_mm": grid,
            "shared_terminals": [sorted(p.id for p in pins if p.point == point)
                                 for point in coords
                                 if sum(p.point == point for p in pins) > 1],
        },
        uid,
        reserved,
    )


def view_key(component, unit):
    return (
        component["ref"]
        if component.get("units", [1]) == [1]
        else f"{component['ref']}:{unit}"
    )


def routing_groups(intent, layout):
    """Expand explicit local wire groups without changing electrical intent.

    Every terminal must occur exactly once. Display names remain the original
    net names; internal group keys must never leak into the native schematic.
    """
    work = copy.deepcopy(intent)
    plan = copy.deepcopy(layout)
    work["nets"] = []
    plan["nets"] = {}
    aliases = {}
    original_names = {n["name"] for n in intent["nets"]}
    if set(layout.get("nets", {})) - original_names:
        raise ValueError("Unknown net in layout policies")
    for net in intent["nets"]:
        name = net["name"]
        policy = dict(layout.get("nets", {}).get(name, {}))
        groups = policy.pop("groups", None)
        if groups is None:
            groups = [net["pins"]]
        if not isinstance(groups, list) or not groups:
            raise ValueError(f"{name}: groups must partition every net pin exactly once")
        normalized = []
        for group in groups:
            spec = {"pins": group} if isinstance(group, list) else group
            if (not isinstance(spec, dict) or set(spec) - {"pins", "mode", "rail_y", "priority"}
                    or not isinstance(spec.get("pins"), list) or not spec["pins"]):
                raise ValueError(f"{name}: groups must partition every net pin exactly once")
            normalized.append(spec)
        if sorted(p for g in normalized for p in g["pins"]) != sorted(net["pins"]):
            raise ValueError(f"{name}: groups must partition every net pin exactly once")
        for i, group in enumerate(normalized):
            pins = group["pins"]
            key = name if len(groups) == 1 else f"{name}__route_group_{i}"
            if key != name and key in original_names:
                raise ValueError(f"Routing group name collision: {key}")
            aliases[key] = name
            work["nets"].append({"name": key, "pins": pins})
            plan["nets"][key] = dict(policy)
            plan["nets"][key].update({k: v for k, v in group.items() if k != "pins"})
            if len(groups) > 1:
                plan["nets"][key]["label"] = True
                if len(pins) == 1:
                    plan["nets"][key]["mode"] = "labels"
                    plan["nets"][key].pop("rail_y", None)
    return work, plan, aliases


def route_root(root, intent, layout, uid, reserved):
    intent, layout, aliases = routing_groups(intent, layout)
    scene = read_scene(root)
    grid = float(layout.get("grid_mm", 1.27))
    page = scene.page.expanded(-5.0)
    pinmap = {p.id: p for s in scene.symbols for p in s.pins}
    mapping = pin_net_map(intent)
    # A visual grouping cannot split an electrically shared physical terminal.
    terminal_groups = {}
    for pid, p in pinmap.items():
        if p.point in terminal_groups and terminal_groups[p.point] != mapping.get(pid):
            raise ValueError(f"Shared terminal split across routing groups: {pid}")
        terminal_groups[p.point] = mapping.get(pid)
    policies = layout.get("nets", {})
    if set(policies) - {n["name"] for n in intent["nets"]}:
        raise ValueError("Unknown net in layout policies")
    for name, policy in policies.items():
        unknown = set(policy) - {"mode", "rail_y", "label", "priority"}
        if unknown:
            raise ValueError(f"{name}: unknown routing options {sorted(unknown)}")
        if policy.get("mode") == "labels" and "rail_y" in policy:
            raise ValueError(f"{name}: labels mode cannot also specify rail_y")
        if not isinstance(policy.get("label", False), bool):
            raise ValueError(f"{name}: label must be a boolean")
    base = [s.body.expanded(0.3) for s in scene.symbols] + list(reserved)
    base += [f.box().expanded(0.3) for s in scene.symbols for _, f in s.fields]
    base += [f.box().expanded(0.3) for _, f in scene.labels]
    attempts = []
    orders = [
        sorted(
            intent["nets"],
            key=lambda n: (policies.get(n["name"], {}).get("priority", 0), n["name"]),
        )
    ]
    orders.append(list(reversed(orders[0])))
    for order in orders:
        wires = []
        labels = []
        stage = []
        try:
            for net in order:
                name = net["name"]
                policy = policies.get(name, {})
                mode = policy.get("mode", "wire")
                if mode not in ("wire", "labels"):
                    raise ValueError(f"Unknown routing mode {mode}")
                selected = list({pinmap[pid].point: pinmap[pid]
                                 for pid in sorted(net["pins"])}.values())
                if mode == "wire" and len(selected) == 1 and len(net["pins"]) > 1 and policy.get("label") and "rail_y" not in policy:
                    # An explicitly labelled local group of shared pads has
                    # one geometric endpoint. Draw one stem, retaining all pads.
                    mode = "labels"
                forbidden = base + [
                    wire_box(a, b, 0.35) for other, a, b in wires if other != name
                ]
                forbidden += [
                    wire_box(p.point, p.inner, 0.35)
                    for pid, p in pinmap.items()
                    if mapping.get(pid) != name
                ]
                forbidden += [f.box().expanded(0.3) for _, f in labels]
                if mode == "labels":
                    # Explicit remote-label topology, never an automatic escape
                    # hatch for a failed visible connection.
                    for p in selected:
                        label = None
                        # Left-facing labels still use KiCad's tested left
                        # justification, so the stem must clear their real
                        # estimated width, not a fixed ten-millimetre limit.
                        text_width = TextField(aliases[name], 0, 0, 0, 1.27).box().width
                        long_stem = math.ceil(text_width / grid) + 2
                        for steps in sorted(set((2, 4, 6, 8, long_stem, long_stem + 4))):
                            end = (
                                round(p.point[0] + steps * grid * p.direction[0], 6),
                                round(p.point[1] + steps * grid * p.direction[1], 6),
                            )
                            if not page.contains_point(*end) or any(
                                segment_hits_box(p.point, end, o) for o in forbidden
                            ):
                                continue
                            try:
                                label = place_net_label(
                                    aliases[name],
                                    [end],
                                    forbidden
                                    + [wire_box(a, b, 0.04) for _, a, b in wires]
                                    + [
                                        wire_box(pin.point, pin.inner, 0.5)
                                        for pin in pinmap.values()
                                    ],
                                    page,
                                )
                                break
                            except ValueError:
                                continue
                        if label is None:
                            raise ValueError(
                                f"No clear label stub for {p.id} on {name}; expand the block"
                            )
                        wires.append((name, p.point, end))
                        labels.append((name, label))
                        forbidden.append(label.box().expanded(0.3))
                    stage.append(
                        {"net": name, "mode": mode, "terminals": len(selected)}
                    )
                    continue
                if "rail_y" in policy:
                    y = float(policy["rail_y"])
                    grid_point((0.0, y), grid)
                    y = round(y, 6)
                    targets = {
                        p.id: (
                            round(
                                p.point[0]
                                + (grid * p.direction[0] if p.direction[0] else 0),
                                6,
                            ),
                            y,
                        )
                        for p in selected
                    }
                    xs = [t[0] for t in targets.values()]
                    a, b = (min(xs), y), (max(xs), y)
                    if a != b:
                        if any(segment_hits_box(a, b, o) for o in forbidden):
                            raise ValueError(f"Fixed rail {name} obstructed")
                        wires.append((name, a, b))
                    pairs = [(p.id, None) for p in selected]
                else:
                    pairs = manhattan_mst(selected)
                    targets = {}
                for aid, bid in pairs:
                    a = pinmap[aid]
                    b = pinmap[bid] if bid else None
                    end = b.point if b else targets[aid]
                    points = route(
                        a.point,
                        end,
                        forbidden,
                        page,
                        grid,
                        start_dir=a.direction,
                        end_dir=b.direction if b else None,
                        max_states=int(layout.get("max_route_states", 150000)),
                    )
                    wires.extend((name, x, y) for x, y in zip(points, points[1:]))
                if len(selected) == 1 and "rail_y" not in policy:
                    raise ValueError(
                        f"One-pin net {name} needs explicit labels mode, or no_connect instead"
                    )
                if policy.get("label", False):
                    segments = [(a, b) for n, a, b in wires if n == name]
                    if not segments:
                        raise ValueError(f"No segment available for label on {name}")
                    label_obstacles = forbidden + [
                        wire_box(a, b, 0.04) for _, a, b in wires
                    ] + [wire_box(p.point, p.inner, 0.5) for p in pinmap.values()]
                    placed = None
                    for a, b in sorted(
                        segments,
                        key=lambda w: (
                            -(abs(w[1][0] - w[0][0]) + abs(w[1][1] - w[0][1]))
                        ),
                    ):
                        try:
                            # Try interior grid points as well as endpoints,
                            # which may lie next to the IC's pin text.
                            length = abs(b[0]-a[0])+abs(b[1]-a[1])
                            count = round(length/grid)
                            candidates = [a, b]
                            if count > 1:
                                candidates += [(round(a[0]+(b[0]-a[0])*j/count,6),
                                                round(a[1]+(b[1]-a[1])*j/count,6))
                                               for j in range(1,count)]
                            placed = place_net_label(
                                aliases[name], candidates, label_obstacles, page
                            )
                            break
                        except ValueError:
                            pass
                    if placed is None:
                        raise ValueError(f"No clear label location on {name}")
                    labels.append((name, placed))
                stage.append({"net": name, "mode": mode, "pairs": pairs})
            wires, dots = normalize_wires(
                [(aliases[n], a, b) for n, a, b in wires],
                [p.point for p in pinmap.values()] + [(f.x, f.y) for _, f in labels],
            )
            break
        except ValueError as e:
            attempts.append({"order": [n["name"] for n in order], "failure": str(e)})
    else:
        raise ValueError(
            "Routing failed after bounded order retries: " + json.dumps(attempts)
        )
    for i, (net, a, b) in enumerate(wires):
        root.append(
            form(
                "wire",
                form("pts", form("xy", *a), form("xy", *b)),
                form("stroke", form("width", 0), form("type", Atom("default"))),
                form("uuid", uid("wire:" + net + ":" + repr(sorted([a, b])))),
            )
        )
    for i, p in enumerate(dots):
        root.append(
            form(
                "junction",
                form("at", *p),
                form("diameter", 0),
                form("color", 0, 0, 0, 0),
                form("uuid", uid("dot:" + repr(p))),
            )
        )
    for i, (name, f) in enumerate(labels):
        root.append(
            form(
                "label",
                aliases[name],
                form("at", f.x, f.y, f.angle),
                form(
                    "effects",
                    form("font", form("size", f.font_mm, f.font_mm)),
                    form("justify", *[Atom(j) for j in sorted(f.justify)]),
                ),
                form("uuid", uid("label:" + name + ":" + repr((f.x, f.y)))),
            )
        )
    for pid in intent.get("no_connect", []):
        root.append(
            form(
                "no_connect",
                form("at", *pinmap[pid].point),
                form("uuid", uid("nc:" + pid)),
            )
        )
    return {
        "attempts": attempts,
        "stages": stage,
        "wire_count": len(wires),
        "junction_count": len(dots),
    }


def place_net_label(name, segment, obstacles, page):
    from .geometry import TextField

    # Anchors stay at segment endpoints. Text remains horizontal and uses an
    # explicit native KiCad anchor/justify; no tscircuit SVG-only text surrogate.
    for p in reversed(segment):
        # Local labels use angle/spin for native alignment. Emit the tested
        # 0-degree style and extend left-facing stubs instead of falsifying
        # bounds with property-field justification that KiCad will ignore.
        for just in (frozenset({"left", "bottom"}),):
            f = TextField(name, *p, 0.0, 1.27, justify=just)
            box = f.box()
            if box.inside(page) and not any(
                box.expanded(-0.06).overlaps(o) for o in obstacles
            ):
                return f
    raise ValueError(f"No clear label placement for {name}")


def generate(intent, layout, name, dirs=()):
    root, manifest, uid, reserved = make_root(intent, layout, name, dirs)
    # Save stage facts separately from the final KiCad result; neither is an
    # electrical PASS. The CLI re-reads the serialized file and uses native CLI.
    manifest["routing"] = route_root(root, intent, layout, uid, reserved)
    scene = read_scene(parse(dump(root)))
    report = check_scene(
        scene, grid=manifest["grid_mm"], reserved=reserved, pin_nets=pin_net_map(intent)
    )
    manifest["geometry"] = report
    manifest["resolved_placements"] = [
        {
            "ref": s.ref,
            "body": s.body.__dict__
            if hasattr(s.body, "__dict__")
            else [s.body.x_min, s.body.y_min, s.body.x_max, s.body.y_max],
            "pins": {p.id: list(p.point) for p in s.pins},
            "fields": {
                n: {
                    "at": [f.x, f.y, f.angle],
                    "text": f.text,
                    "justify": sorted(f.justify),
                }
                for n, f in s.fields
            },
        }
        for s in scene.symbols
    ]
    return root, manifest
