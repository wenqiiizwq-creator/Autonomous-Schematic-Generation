"""Extract cached KiCad graphic bodies, active-unit pins, fields and wires.

Bodies exclude pin legs. Unsupported constructs remain coverage gaps, never an
invented fixed-size body or a PASS. This is a conservative AABB model, not the
native font renderer. Native export and visual review remain required.
"""

from dataclasses import dataclass, field, replace
import math
import re
from .sexpr import all_nodes, first, value
from .geometry import Box, TextField, union, parse_justify

Point = tuple[float, float]
PAPERS = {
    "A4": (297.0, 210.0),
    "A3": (420.0, 297.0),
    "A2": (594.0, 420.0),
    "A1": (841.0, 594.0),
    "A0": (1189.0, 841.0),
    "A": (279.4, 215.9),
    "B": (431.8, 279.4),
    "USLetter": (279.4, 215.9),
    "USLegal": (355.6, 215.9),
}


def xy(node, key="at"):
    n = first(node, key)
    if not n or len(n) < 3:
        raise ValueError(f"Missing {key} coordinates")
    return float(n[1]), float(n[2])


def transform(point, at, angle=0, mirror=""):
    x, y = point
    # Native KiCad applies the mirror to the rotated placement axes. Applying
    # it before rotation silently swaps numbered pins for 90/270-degree parts.
    a = math.radians(angle)
    c, s = round(math.cos(a), 12), round(math.sin(a), 12)
    rx, ry = x * c - y * s, x * s + y * c
    if mirror == "x":
        ry = -ry
    if mirror == "y":
        rx = -rx
    return round(at[0] + rx, 6), round(at[1] - ry, 6)


def points_box(points):
    return Box(
        min(p[0] for p in points),
        min(p[1] for p in points),
        max(p[0] for p in points),
        max(p[1] for p in points),
    )


def is_hidden(node):
    for holder in (node, first(node, "effects", [])):
        if "hide" in holder or value(holder, "hide") == "yes":
            return True
    return False


def text_field(node, text=None, label=False):
    x, y = xy(node)
    at = first(node, "at")
    angle = float(at[3]) if len(at) > 3 else 0.0
    effects = first(node, "effects", [])
    size = first(first(effects, "font", []), "size", [None, 1.27, 1.27])
    just = first(effects, "justify", [])[1:]
    if label and not just:
        just = ["left", "bottom"]
    return TextField(
        str(node[1] if text is None else text),
        x,
        y,
        angle,
        max(float(size[1]), float(size[2])),
        bold="bold" in first(effects, "font", []),
        justify=parse_justify(just),
    )


@dataclass
class Pin:
    id: str
    point: Point
    inner: Point
    direction: Point
    kind: str
    hidden: bool = False


@dataclass
class Symbol:
    ref: str
    lib_id: str
    unit: int
    node: list
    body: Box | None
    pins: list[Pin]
    fields: list[tuple[str, TextField]]


@dataclass
class Scene:
    page: Box
    symbols: list[Symbol] = field(default_factory=list)
    wires: list[tuple[Point, Point]] = field(default_factory=list)
    labels: list[tuple[str, TextField]] = field(default_factory=list)
    junctions: list[Point] = field(default_factory=list)
    no_connects: list[Point] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


def read_scene(root):
    if root[0] != "kicad_sch":
        raise ValueError("Expected kicad_sch")
    paper = first(root, "paper", [None, "A4"])
    gaps = []
    if paper[1] == "User":
        dims = (float(paper[2]), float(paper[3]))
    elif paper[1] in PAPERS:
        dims = PAPERS[paper[1]]
    else:
        dims = PAPERS["A4"]
        gaps.append(f"Unknown paper: {paper[1]}")
    if "portrait" in paper:
        dims = dims[::-1]
    scene = Scene(Box(0, 0, *dims), gaps=gaps)
    for key in (
        "sheet",
        "bus",
        "bus_entry",
        "image",
        "text_box",
        "polyline",
        "rectangle",
        "arc",
        "circle",
        "embedded_files",
    ):
        if all_nodes(root, key):
            scene.gaps.append(f"Unsupported sheet object: {key}")
    libs = {n[1]: n for n in all_nodes(first(root, "lib_symbols", []), "symbol")}
    for node in all_nodes(root, "symbol"):
        lib_id = value(node, "lib_id", "")
        ref = next(
            (str(p[2]) for p in all_nodes(node, "property") if p[1] == "Reference"), "?"
        )
        unit = int(value(node, "unit", 1))
        body_style = int(value(node, "body_style", value(node, "convert", 1)))
        at = xy(node)
        angle = float(first(node, "at")[3])
        mirror = value(node, "mirror", "")
        if angle % 90 or mirror not in ("", "x", "y"):
            scene.gaps.append(f"{ref}: unsupported rotation/mirror")
        lib = libs.get(value(node, "lib_name", lib_id))
        if lib is None:
            scene.gaps.append(f"{ref}: missing cached library {lib_id}")
            lib = []
        if first(lib, "extends"):
            scene.gaps.append(f"{ref}: unresolved library inheritance")
        trans = lambda p: transform(p, at, angle, mirror)
        graphics, pins = [], []
        for sub in all_nodes(lib, "symbol"):
            match = re.search(r"_(\d+)_(\d+)$", str(sub[1]))
            if not match:
                scene.gaps.append(f"{ref}: unknown sub-symbol {sub[1]}")
                continue
            if int(match[1]) not in (0, unit) or int(match[2]) not in (0, body_style):
                continue
            for item in sub[2:]:
                if not isinstance(item, list) or not item:
                    continue
                kind = item[0]
                points = []
                if kind == "rectangle":
                    a, b = xy(item, "start"), xy(item, "end")
                    points = [(x, y) for x in (a[0], b[0]) for y in (a[1], b[1])]
                elif kind in ("polyline", "bezier"):
                    points = [
                        (float(p[1]), float(p[2]))
                        for p in all_nodes(first(item, "pts", []), "xy")
                    ]
                    if kind == "bezier":
                        scene.gaps.append(f"{ref}: bezier bounded by control hull")
                elif kind == "circle":
                    x, y = xy(item, "center")
                    r = float(value(item, "radius"))
                    points = [
                        (x - r, y - r),
                        (x - r, y + r),
                        (x + r, y - r),
                        (x + r, y + r),
                    ]
                elif kind == "arc":
                    # Full circle is a conservative bounding box for a 3-point arc.
                    a, b, c = xy(item, "start"), xy(item, "mid"), xy(item, "end")
                    d = 2 * (
                        a[0] * (b[1] - c[1])
                        + b[0] * (c[1] - a[1])
                        + c[0] * (a[1] - b[1])
                    )
                    if abs(d) < 1e-9:
                        points = [a, b, c]
                        scene.gaps.append(f"{ref}: degenerate arc")
                    else:
                        s = [p[0] ** 2 + p[1] ** 2 for p in (a, b, c)]
                        cx = (
                            s[0] * (b[1] - c[1])
                            + s[1] * (c[1] - a[1])
                            + s[2] * (a[1] - b[1])
                        ) / d
                        cy = (
                            s[0] * (c[0] - b[0])
                            + s[1] * (a[0] - c[0])
                            + s[2] * (b[0] - a[0])
                        ) / d
                        r = math.hypot(a[0] - cx, a[1] - cy)
                        points = [
                            (cx - r, cy - r),
                            (cx - r, cy + r),
                            (cx + r, cy - r),
                            (cx + r, cy + r),
                        ]
                elif kind == "pin":
                    p = xy(item)
                    pa = float(first(item, "at")[3])
                    length = float(value(item, "length", 0))
                    inward = (
                        round(math.cos(math.radians(pa)), 12),
                        round(math.sin(math.radians(pa)), 12),
                    )
                    inner = (p[0] + length * inward[0], p[1] + length * inward[1])
                    tip = trans(p)
                    ip = trans(inner)
                    # Direction away from body, including zero-length pin orientation.
                    out = trans((p[0] - inward[0], p[1] - inward[1]))
                    direction = (round(out[0] - tip[0]), round(out[1] - tip[1]))
                    number = str(value(item, "number", ""))
                    pins.append(
                        Pin(
                            f"{ref}.{number}",
                            tip,
                            ip,
                            direction,
                            str(item[1]),
                            is_hidden(item),
                        )
                    )
                elif kind == "text":
                    # Treat library legends as protected symbol graphics. They
                    # retain their native text and expand the routing obstacle.
                    if not is_hidden(item):
                        box = text_field(item).box()
                        points = [(box.x_min, box.y_min), (box.x_min, box.y_max),
                                  (box.x_max, box.y_min), (box.x_max, box.y_max)]
                elif kind not in ("property",):
                    scene.gaps.append(f"{ref}: unsupported symbol graphic {kind}")
                if points:
                    width = (
                        float(value(first(item, "stroke", []), "width", 0.254)) or 0.254
                    )
                    graphics.append(
                        points_box(list(map(trans, points))).expanded(width / 2)
                    )
        fields = []
        for p in all_nodes(node, "property"):
            if not is_hidden(p) and p[2]:
                f = text_field(p, text=str(p[2]))
                # KiCad field stored orientation is combined with the symbol's
                # rotation. Horizontal fields on a 90/270-degree symbol must
                # be written at 90 degrees (native-render regression).
                f = replace(f, angle=(f.angle + angle) % 180)
                if f.justify and (angle != 0 or mirror):
                    scene.gaps.append(
                        f"{ref}: transformed non-centred field justification needs native review"
                    )
                fields.append((str(p[1]), f))
        # Some official multi-unit ICs draw their separate power unit using
        # pins only. Its interior envelope is derived from actual inner pin
        # coordinates, never substituted for missing library graphics.
        library_units = {
            int(m[1])
            for sub in all_nodes(lib, "symbol")
            if (m := re.search(r"_(\d+)_(\d+)$", str(sub[1]))) and int(m[1]) > 0
        }
        if (
            not graphics
            and len(library_units) > 1
            and pins
            and all(p.kind in ("power_in", "power_out") for p in pins)
        ):
            graphics.append(points_box([p.inner for p in pins]).expanded(0.635))
        if not graphics:
            scene.gaps.append(
                f"{ref}: body geometry absent (power/graphic-only symbols need explicit review)"
            )
        # Official libraries hide passive copies of an explicitly drawn terminal
        # (e.g. several QFN ground pads). Keep every physical pin in the scene.
        # A hidden terminal elsewhere still has no supported visible geometry.
        if any(p.hidden and p.kind != "no_connect" and not any(
            not q.hidden and p.point == q.point and p.inner == q.inner
            and p.direction == q.direction and p.kind == "passive"
            for q in pins
        ) for p in pins):
            scene.gaps.append(f"{ref}: hidden pins require native connectivity review")
        scene.symbols.append(
            Symbol(ref, str(lib_id), unit, node, union(graphics), pins, fields)
        )
    for wire in all_nodes(root, "wire"):
        points = all_nodes(first(wire, "pts", []), "xy")
        if len(points) != 2:
            raise ValueError("Wire must have exactly two endpoints")
        scene.wires.append(tuple((float(p[1]), float(p[2])) for p in points))
    for kind in ("label", "global_label", "hierarchical_label", "text"):
        for n in all_nodes(root, kind):
            scene.labels.append((kind, text_field(n, label=kind != "text")))
            if kind == "label" and (
                float(first(n, "at")[3]) != 0
                or "right" in first(first(n, "effects", []), "justify", [])
            ):
                scene.gaps.append(
                    "Local label angle/justification outside tested 0-degree style needs native review"
                )
            if kind in ("global_label", "hierarchical_label"):
                scene.gaps.append(
                    f"{kind}: outline and attached fields need render review"
                )
    scene.junctions = [xy(n) for n in all_nodes(root, "junction")]
    scene.no_connects = [xy(n) for n in all_nodes(root, "no_connect")]
    return scene
