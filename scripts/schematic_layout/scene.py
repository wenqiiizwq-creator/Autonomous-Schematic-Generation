"""Extract cached KiCad graphic bodies, active-unit pins, fields and wires.

Bodies exclude pin legs. Unsupported constructs remain coverage gaps, never an
invented fixed-size body or a PASS. This is a conservative AABB model, not the
native font renderer. Native export and visual review remain required.
"""

from dataclasses import dataclass, field, replace
import math
import re
from .sexpr import all_nodes, first, value
from .geometry import Box, TextField, parse_justify, union
from .label_geometry import global_outline, STYLES

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
    sheet_pins: list[tuple[str, Point]] = field(default_factory=list)


# Global label styles whose native outline direction was verified by render
# (KiCad 10.0.6): (angle, justify) -> direction the outline extends.
GLOBAL_LABEL_STYLES = STYLES


@dataclass(frozen=True)
class GlobalLabelText(TextField):
    """Full native outline plus the style needed for precise cap contact."""

    outward: tuple = (1, 0)
    shape: str = "passive"
    italic: bool = False
    face: str | None = None
    size: tuple | None = None
    thickness: float | None = None
    native_justify: tuple | None = None

    def outline(self):
        return global_outline(self.text, (self.x, self.y), self.outward, self.font_mm,
                              shape=self.shape, bold=self.bold, italic=self.italic,
                              face=self.face, size=self.size, thickness=self.thickness,
                              angle=self.angle, justify=self.justify if self.native_justify is None else self.native_justify)

    def box(self) -> Box:
        return self.outline().box


@dataclass(frozen=True)
class HierarchicalLabelText(TextField):
    """Qualified text offset only; the electrical anchor remains unchanged."""
    outward: tuple = (1, 0)

    def box(self) -> Box:
        dx, dy = self.outward
        # Native default-font text starts 1.15*font beyond the anchor. The
        # contour and attached fields are deliberately still coverage gaps.
        return TextField(self.text, self.x + dx*self.font_mm*1.15,
                         self.y + dy*self.font_mm*1.15, self.angle % 180,
                         self.font_mm, self.bold, self.justify).box()


HIERARCHICAL_LABEL_STYLES = {
    (0, frozenset({"left"})): (1, 0),
    (90, frozenset({"left"})): (0, -1),
    (180, frozenset({"right"})): (-1, 0),
    (270, frozenset({"right"})): (0, 1),
}


TESTED_LOCAL_LABELS = {
    (0, frozenset({"left", "bottom"})),
    (180, frozenset({"right", "bottom"})),
    (90, frozenset({"left", "bottom"})),
    (270, frozenset({"right", "bottom"})),
}


def placed_field(field, symbol_angle, mirror):
    """Native field anchors stay absolute; justification follows placement axes.

    KiCad keeps readable glyph orientation while its symbol transform changes
    the long and short justification axes. Verified against a native SVG
    matrix, not by reflecting the already-absolute field position.
    """
    total = (field.angle + symbol_angle) % 360
    angle = total % 180
    if total % 90 or mirror not in ("", "x", "y"):
        return replace(field, angle=angle)
    a, b = map(math.radians, (total, angle))
    long_axis = [round(math.cos(a)), -round(math.sin(a))]
    short_axis = [round(math.sin(a)), round(math.cos(a))]
    if mirror:
        axis = 1 if mirror == "x" else 0
        long_axis[axis] *= -1
        short_axis[axis] *= -1
    long_sign = long_axis[0]*round(math.cos(b)) - long_axis[1]*round(math.sin(b))
    short_sign = short_axis[0]*round(math.sin(b)) + short_axis[1]*round(math.cos(b))
    just = set(field.justify)
    for sign, tokens in ((long_sign, ("left", "right")), (short_sign, ("top", "bottom"))):
        if sign < 0:
            just = {tokens[1] if t == tokens[0] else tokens[0] if t == tokens[1] else t for t in just}
    return replace(field, angle=angle, justify=frozenset(just))


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
    # Native sheet terminals are explicit electrical anchors. Recognising
    # their coordinates does not qualify the sheet frame, text or pin outline.
    for si, sheet in enumerate(all_nodes(root, "sheet")):
        for pi, pin in enumerate(all_nodes(sheet, "pin")):
            try:
                at = first(pin, "at", [])
                if (len(pin) < 3 or not str(pin[1]).strip()
                        or pin[2] not in ("input", "output", "bidirectional", "tri_state", "passive")
                        or len(at) != 4):
                    raise ValueError("unsupported terminal form")
                x, y, angle = map(float, at[1:])
                if not all(map(math.isfinite, (x, y, angle))) or angle % 90:
                    raise ValueError("unsupported terminal coordinates/angle")
                scene.sheet_pins.append((f"sheet:{si}:pin:{pi}:{pin[1]}", (x, y)))
            except (ValueError, TypeError, IndexError) as exc:
                scene.gaps.append(f"sheet:{si}:pin:{pi}: {exc}")
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
                if (f.angle + angle) % 90 or mirror not in ("", "x", "y"):
                    scene.gaps.append(
                        f"{ref}: transformed non-centred field justification needs native review"
                    )
                f = placed_field(f, angle, mirror)
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
            f = text_field(n, label=kind != "text")
            if kind == "label":
                # KiCad draws local label text readable: 180 as 0 and 270 as 90,
                # keeping the justification (native render, KiCad 10.0.6).
                style = (round(f.angle) % 360, f.justify)
                f = replace(f, angle=f.angle % 180)
                if style not in TESTED_LOCAL_LABELS:
                    scene.gaps.append(
                        "Local label angle/justification outside the tested styles needs native review"
                    )
            scene.labels.append((kind, f))
            if kind == "global_label":
                style = (f.angle % 360, f.justify)
                if style not in GLOBAL_LABEL_STYLES:
                    font = first(first(n, "effects", []), "font", [])
                    size = first(font, "size", [None, 1.27, 1.27])
                    # Native 10.0.6 renders these default-font fallback styles
                    # readable, retaining justification (180->0, 270->90).
                    # This fixes text direction only; no outline is qualified.
                    if (f.angle in (180, 270) and f.justify in
                            (frozenset({"left"}), frozenset({"right"})) and
                            f.font_mm in (1.0, 1.27) and float(size[1]) == float(size[2]) and
                            not f.bold and "italic" not in font and value(font, "face") in (None, "") and
                            value(font, "thickness") in (None, "0", 0) and
                            str(value(n, "shape")) in ("input", "passive")):
                        scene.labels[-1] = (kind, replace(f, angle=f.angle % 180))
                    scene.gaps.append("Global label angle/justify direction needs native review")
                    continue
                outward = GLOBAL_LABEL_STYLES[style]
                font_node = first(first(n, "effects", []), "font", [])
                size = first(font_node, "size", [None, 1.27, 1.27])
                label = GlobalLabelText(f.text, f.x, f.y, f.angle, f.font_mm, f.bold,
                                        f.justify, outward, str(value(n, "shape", "unknown")),
                                        "italic" in font_node, value(font_node, "face"),
                                        (float(size[1]), float(size[2])),
                                        value(font_node, "thickness"),
                                        tuple(first(first(n, "effects", []), "justify", [])[1:]))
                scene.labels[-1] = (kind, label)
                if label.outline().gaps:
                    scene.gaps.append("Global label native coverage gap: " + ", ".join(label.outline().gaps))
            elif kind == "hierarchical_label":
                font = first(first(n, "effects", []), "font", [])
                size = first(font, "size", [None, 1.27, 1.27])
                style = (f.angle % 360, f.justify)
                if (style in HIERARCHICAL_LABEL_STYLES and f.font_mm in (.889, 1.0, 1.27)
                        and float(size[1]) == float(size[2]) and not f.bold
                        and "italic" not in font and value(font, "face") in (None, "")
                        and value(font, "thickness") in (None, "0", 0)
                        and f.text and all(32 <= ord(c) <= 126 for c in f.text)
                        and not any(c in f.text for c in '~{}^\\')
                        and str(value(n, "shape")) in ("input", "output", "bidirectional", "tri_state", "passive")):
                    scene.labels[-1] = (kind, HierarchicalLabelText(
                        f.text, f.x, f.y, f.angle, f.font_mm, f.bold, f.justify,
                        HIERARCHICAL_LABEL_STYLES[style]))
                else:
                    scene.gaps.append("Hierarchical label text style needs native review")
                scene.gaps.append(
                    f"{kind}: outline and attached fields need render review"
                )
    scene.junctions = [xy(n) for n in all_nodes(root, "junction")]
    scene.no_connects = [xy(n) for n in all_nodes(root, "no_connect")]
    return scene
