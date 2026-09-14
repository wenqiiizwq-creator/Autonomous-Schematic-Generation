"""Functional templates, measured symbol/field envelopes and bounded page packing.

Templates express drawing roles only. They never add components, select values,
remap pins, or infer a regulator's internal topology. Source ideas: SKiDL's
subcircuit partitioning and circuit-synth's connection-aware placement.
"""

import math
import re
from .circuit_ir import keys
from .generate import Libraries, library_dirs, view_key
from .scene import read_scene, PAPERS, points_box
from .sexpr import form, Atom
from .geometry import Box, union, text_extent
from .field_placer import FieldSpec, autoplace_fields
from .routing import wire_box, grid_point

# Role -> (column, row, native rotation). Multiple parts in a role get distinct
# cells, never a shared origin. These are presentation templates, not circuits.
TEMPLATES = {
    "rc_filter": {
        "input": (0, 1, 0),
        "series": (1, 1, 90),
        "shunt": (2, 2, 0),
        "output": (3, 1, 0),
    },
    "divider": {
        "input": (0, 0, 0),
        "upper": (1, 1, 0),
        "lower": (1, 2, 0),
        "output": (2, 1, 0),
    },
    "ldo": {
        "input": (0, 1, 0),
        "input_cap": (1, 2, 0),
        "regulator": (2, 1, 0),
        "output_cap": (3, 2, 0),
        "output": (4, 1, 0),
        "control": (1, 0, 0),
        "feedback": (3, 3, 0),
    },
    "buck_async": {
        "input": (0, 1, 0),
        "input_cap": (1, 2, 0),
        "regulator": (2, 1, 0),
        "diode": (3, 2, 0),
        "inductor": (4, 1, 90),
        "output_cap": (5, 2, 0),
        "output": (6, 1, 0),
        "bootstrap": (3, 0, 90),
        "feedback": (5, 3, 0),
        "compensation": (1, 3, 0),
        "control": (1, 0, 0),
    },
    "integrated_power": {
        "input": (0, 1, 0),
        "input_cap": (1, 2, 0),
        "regulator": (2, 1, 0),
        "output_cap": (3, 2, 0),
        "output": (4, 1, 0),
        "feedback": (3, 3, 0),
        "control": (1, 0, 0),
    },
}


def snap_up(v, grid):
    return round(math.ceil((v - 1e-8) / grid) * grid, 6)


def natural_key(text):
    return tuple(
        (1, int(s)) if s.isdigit() else (0, s) for s in re.split(r"(\d+)", text)
    )


def measure(component, unit, rotation, mirror, libraries):
    lib = libraries.load(component["lib_id"])
    symbol = form(
        "symbol",
        form("lib_id", component["lib_id"]),
        form("unit", unit),
        form("at", 0, 0, rotation),
        form(
            "property",
            "Reference",
            component["ref"],
            form("effects", form("hide", Atom("yes"))),
        ),
    )
    if mirror:
        symbol.append(form("mirror", Atom(mirror)))
    scene = read_scene(
        form("kicad_sch", form("paper", "A4"), form("lib_symbols", lib), symbol)
    )
    if scene.gaps:
        raise ValueError("Unsupported placement geometry: " + "; ".join(scene.gaps))
    s = scene.symbols[0]
    specs = [
        FieldSpec(
            "Reference",
            component["ref"] + ("A" if len(component.get("units", [1])) > 1 else ""),
        ),
        FieldSpec("Value", component["value"]),
    ]
    obstacles = [s.body, *[wire_box(p.point, p.inner, 0.3) for p in s.pins]]
    fields = autoplace_fields(s.body, [p.point for p in s.pins], obstacles, specs)
    bounds = [s.body, points_box([p.point for p in s.pins])]
    bounds += [
        f.text_field(spec.text, spec.font_mm).box() for f, spec in zip(fields, specs)
    ]
    return union(bounds), s.pins


def cells_for(block, template, intent):
    members = sorted(block["members"], key=lambda m: (natural_key(m["id"]), m["id"]))
    if template in TEMPLATES:
        roles = TEMPLATES[template]
        missing = {m["role"] for m in members} - set(roles)
        if missing:
            raise ValueError(
                f"{block['id']}: roles {sorted(missing)} unsupported by {template}"
            )
        # Prevent use of a Buck layout for an LDO or integrated-inductor module.
        required = {
            "rc_filter": {"series", "shunt"},
            "divider": {"upper", "lower"},
            "ldo": {"regulator"},
            "buck_async": {"regulator", "inductor", "diode"},
            "integrated_power": {"regulator"},
        }[template]
        if required - {m["role"] for m in members}:
            raise ValueError(
                f"{block['id']}: {template} missing required roles {sorted(required)}"
            )
        result = {m["ref"]: roles[m["role"]] for m in members}
    elif template == "capacitor_bank":
        if any(m["role"] != "capacitor" for m in members):
            raise ValueError("capacitor_bank accepts only the capacitor role")
        result = {m["ref"]: (i % 4, i // 4, 0) for i, m in enumerate(members)}
    elif template == "functional":
        # Traverse actual connectivity starting at declared inputs (otherwise
        # the most connected member); high-fanout rails do not dominate order.
        refs = {m["ref"] for m in members}
        adjacency = {r: set() for r in refs}
        for net in intent["nets"]:
            connected = {p.rsplit(".", 1)[0] for p in net["pins"]} & refs
            if len(connected) > 4:
                continue
            for r in connected:
                adjacency[r].update(connected - {r})
        roots = [m["ref"] for m in members if m["role"] == "input"]
        queue = roots or sorted(refs, key=lambda r: (-len(adjacency[r]), r))[:1]
        ordered = []
        while queue:
            r = queue.pop(0)
            if r not in ordered:
                ordered.append(r)
                queue.extend(sorted(adjacency[r] - set(ordered)))
        ordered.extend(sorted(refs - set(ordered)))
        result = {r: (i % 4, i // 4, 0) for i, r in enumerate(ordered)}
    else:
        raise ValueError(f"Unknown layout template {template}")
    occupied, unique = set(), {}
    components = {c["ref"]: c for c in intent["components"]}
    for m in members:
        col, row, angle = result[m["ref"]]
        for unit in components[m["ref"]].get("units", [1]):
            y = row
            while (col, y) in occupied:
                y += 1
            occupied.add((col, y))
            unique[view_key(components[m["ref"]], unit)] = (col, y, angle, unit)
    return unique


def block_layout(block, config, intent, libraries, grid, gap):
    keys(config, "template orientations title", f"block {block['id']}")
    cells = cells_for(block, config.get("template", "functional"), intent)
    components = {c["ref"]: c for c in intent["components"]}
    orientations = config.get("orientations", {})
    if set(orientations) - set(cells):
        raise ValueError(f"{block['id']}: unknown orientation view")
    measured, rotations = {}, {}
    for key, (col, row, angle, unit) in cells.items():
        orient = orientations.get(key, {})
        keys(orient, "rotation mirror", "orientation")
        angle, mirror = orient.get("rotation", angle), orient.get("mirror", "")
        if angle not in (0, 90, 180, 270) or mirror not in ("", "x", "y"):
            raise ValueError("Invalid orientation")
        c = components[key.split(":")[0]]
        box, pins = measure(c, unit, angle, mirror, libraries)
        for p in pins:
            grid_point(p.point, grid)
        measured[key] = box.expanded(gap / 2)
        rotations[key] = (angle, mirror)

    def axis_centres(axis):
        centres, cursor = {}, 0.0
        for index in sorted({v[axis] for v in cells.values()}):
            boxes = [measured[k] for k, cell in cells.items() if cell[axis] == index]
            low = min(b.x_min if axis == 0 else b.y_min for b in boxes)
            high = max(b.x_max if axis == 0 else b.y_max for b in boxes)
            centres[index] = snap_up(cursor - low, grid)
            cursor = centres[index] + high
        return centres

    xs, ys = axis_centres(0), axis_centres(1)
    placements, bounds = {}, []
    for key, (col, row, _, _) in cells.items():
        x, y = xs[col], ys[row]
        angle, mirror = rotations[key]
        placements[key] = {
            "at": [x, y],
            "rotation": angle,
            **({"mirror": mirror} if mirror else {}),
        }
        b = measured[key]
        bounds.append(Box(b.x_min + x, b.y_min + y, b.x_max + x, b.y_max + y))
    extent = union(bounds)
    title = config.get("title", block["id"])
    w, _ = text_extent(title, 1.8)
    return placements, Box(0, 0, max(extent.x_max, w) + gap, extent.y_max + gap), title


def plan_layout(intent, compiled, policy, attempt=0, only_block=None):
    keys(
        policy,
        "schema_version papers grid_mm blocks nets gap_mm block_gap_mm max_attempts page_mode",
        "presentation",
    )
    if policy.get("schema_version") != 2:
        raise ValueError("Presentation requires schema_version 2")
    if set(policy.get("nets", {})) - {n["name"] for n in intent["nets"]}:
        raise ValueError("Presentation contains unknown net names")
    grid = float(policy.get("grid_mm", 1.27))
    if not math.isfinite(grid) or grid <= 0:
        raise ValueError("Invalid grid")
    gap = float(policy.get("gap_mm", 12.7)) * (1 + attempt * 0.4)
    block_gap = float(policy.get("block_gap_mm", 10.16))
    if not 5 <= gap <= 100 or not 5 <= block_gap <= 100:
        raise ValueError("Layout gaps must be between 5 and 100 mm")
    blocks = [b for b in compiled["blocks"] if only_block in (None, b["id"])]
    configs = policy.get("blocks", {})
    if set(configs) - {b["id"] for b in compiled["blocks"]}:
        raise ValueError("Presentation references unknown blocks")
    papers = policy.get("papers", ["A4", "A3"])
    if not papers or any(p not in ("A4", "A3", "A2", "A1", "A0") for p in papers):
        raise ValueError("Expected a nonempty list of landscape ISO papers")
    libraries = Libraries(
        library_dirs(
            [s["path"].rsplit("/", 1)[0] for s in compiled["library_sources"].values()]
        )
    )
    shapes = [
        (b, *block_layout(b, configs.get(b["id"], {}), intent, libraries, grid, gap))
        for b in blocks
    ]
    for paper in papers:
        width, height = PAPERS[paper]
        title_keepout = Box(width - 120, height - 45, width - 5, height - 5)
        page = Box(10, 10, width - 10, height - 10)
        placed, placements, manifest, annotations, strips = [], {}, [], [], []
        for b, positions, extent, title in shapes:
            # Candidate corners derive from existing envelopes: compact rows
            # with a hard title keepout, rather than fixed per-part coordinates.
            candidates = {(snap_up(12.7, grid), snap_up(12.7, grid))}
            for other in placed:
                candidates.add((snap_up(other.x_max + block_gap, grid), other.y_min))
                candidates.add(
                    (snap_up(12.7, grid), snap_up(other.y_max + block_gap, grid))
                )
            valid = []
            for x, y in candidates:
                box = Box(x, y, x + extent.width, y + extent.height + 7.62)
                if (
                    box.inside(page)
                    and not box.overlaps(title_keepout)
                    and not any(
                        box.overlaps(o, gap_mm=block_gap - 0.01) for o in placed
                    )
                ):
                    valid.append(box)
            if not valid:
                break
            box = min(valid, key=lambda r: (r.y_max, r.x_min))
            placed.append(box)
            for key, placement in positions.items():
                x, y = placement["at"]
                placements[key] = {
                    **placement,
                    "at": [round(x + box.x_min, 6), round(y + box.y_min + 7.62, 6)],
                }
            annotations.append(
                {"text": title, "at": [box.x_min, box.y_min + 2.54], "font_mm": 1.8}
            )
            strips.append([box.x_min, box.y_min, box.x_max, box.y_min + 6.35])
            manifest.append(
                {
                    "id": b["id"],
                    "template": configs.get(b["id"], {}).get("template", "functional"),
                    "bounds": [box.x_min, box.y_min, box.x_max, box.y_max],
                }
            )
        else:
            nets = {
                n: dict(p)
                for n, p in policy.get("nets", {}).items()
                if n in {n["name"] for n in intent["nets"]}
            }
            return {
                "schema_version": 1,
                "paper": paper,
                "grid_mm": grid,
                "placements": placements,
                "nets": nets,
                "annotations": annotations,
                "reserved": [
                    [
                        title_keepout.x_min,
                        title_keepout.y_min,
                        title_keepout.x_max,
                        title_keepout.y_max,
                    ]
                ],
            }, {
                "blocks": manifest,
                "paper": paper,
                "attempt": attempt,
                "occupied_envelope_area_mm2": sum(b.width * b.height for b in placed),
                "gap_mm": gap,
            }
    raise ValueError(
        "Functional blocks do not fit allowed pages; allow a larger paper or reduce/split the input block set. Native multi-page writing is not supported by this backend."
    )
