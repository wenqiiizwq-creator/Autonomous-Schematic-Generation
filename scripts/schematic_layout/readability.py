"""Wiring readability metrics and gate for one native sheet.

These are drawing-quality measures, not electrical evidence. Islands are
joined exactly as KiCad joins wires: at segment endpoints lying on another
segment and at explicit junctions; a bare perpendicular crossing stays apart.
"""

from .geometry import Box
from .qa import FRAME_MARGIN_MM
from .routing import on_segment
from .scene import PAPERS, read_scene
from .sexpr import all_nodes, first, value

FRAME_MM = FRAME_MARGIN_MM  # content stays this far inside the sheet frame (Sheet.build and the geometry gate)
# Standard papers a page may shrink to, smallest first; only the metric sizes
# the recipes use. A page whose content fits a smaller one is oversized (HR-11).
PAPER_ORDER = ("A4", "A3", "A2", "A1", "A0")


CELL_MM = 25.4
# Drawing habit H3 (drawing-recipes.md): engineers' direct two-pin wires are at most 1.5 times the Manhattan distance of
# their pins in 96 % of 4191 connections of the public KiCad projects census; shorter runs than this are not judged.
DETOUR_RATIO = 1.5
DETOUR_MIN_MM = 25.4


def _object_boxes(scene, root=None):
    boxes = []
    for s in scene.symbols:
        if s.body is not None:
            boxes.append(s.body)
        boxes += [f.box() for _, f in s.fields]
        boxes += [Box(p.point[0], p.point[1], p.point[0], p.point[1]) for p in s.pins if not p.hidden]
    boxes += [f.box() for _, f in scene.labels]
    boxes += [Box(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for a, b in scene.wires]
    boxes += [Box(x, y, x, y) for x, y in scene.junctions]
    # Cover flow lines and page frames are drawn content too.
    boxes += [Box(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])).expanded(w / 2)
              for _, a, b, w in scene.graphic_segments]
    for node in all_nodes(root, "sheet") if root is not None else []:
        (x, y), (w, h) = first(node, "at")[1:3], first(node, "size")[1:3]
        boxes.append(Box(float(x), float(y), float(x) + float(w), float(y) + float(h)))
    for node in all_nodes(root, "rectangle") if root is not None else []:
        (ax, ay), (bx, by) = first(node, "start")[1:3], first(node, "end")[1:3]
        boxes.append(Box(min(float(ax), float(bx)), min(float(ay), float(by)), max(float(ax), float(bx)), max(float(ay), float(by))))
    return boxes


def content_box(scene, root=None):
    """Bounding box of every drawn object: bodies, visible fields, wires, labels, junctions, graphics, frames."""
    boxes = _object_boxes(scene, root)
    if not boxes:
        return None
    return Box(min(b.x_min for b in boxes), min(b.y_min for b in boxes),
               max(b.x_max for b in boxes), max(b.y_max for b in boxes))


def paper_fit(scene, content):
    """Current paper name and the smallest standard paper the content fits with the frame margin."""
    dims = (scene.page.width, scene.page.height)
    current = next((n for n in PAPER_ORDER if PAPERS[n] == dims), None)
    if content is None:
        return current, None
    for name in PAPER_ORDER:
        w, h = PAPERS[name]
        if content.width <= w - 2 * FRAME_MM and content.height <= h - 2 * FRAME_MM:
            return current, name
    return current, None


def _islands(wires, junctions):
    parent = list(range(len(wires)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, (a, b) in enumerate(wires):
        for j in range(i):
            c, d = wires[j]
            if (any(on_segment(p, c, d) for p in (a, b)) or any(on_segment(p, a, b) for p in (c, d))
                    or any(on_segment(p, a, b) and on_segment(p, c, d) for p in junctions)):
                parent[find(i)] = find(j)
    return [find(i) for i in range(len(wires))]


def measure(root):
    scene = read_scene(root)
    wires = [tuple(tuple(round(v, 4) for v in p) for p in w) for w in scene.wires]
    junctions = [tuple(round(v, 4) for v in p) for p in scene.junctions]
    island = _islands(wires, junctions)
    power = {str(value(n, "lib_id", "")) for n in all_nodes(root, "symbol")}
    refs = {}
    for s in scene.symbols:
        refs.setdefault("power" if s.ref.startswith("#") else "part", []).append(s)
    terminals = {}
    pin_points = {}
    for kind, symbols in refs.items():
        for s in symbols:
            for p in s.pins:
                pt = tuple(round(v, 4) for v in p.point)
                for i, w in enumerate(wires):
                    if on_segment(pt, *w):
                        terminals.setdefault(island[i], set()).add((kind, s.ref, p.id))
                        pin_points.setdefault(island[i], []).append(pt)
                        break
    for kind, f in scene.labels:
        if kind == "text":
            continue
        pt = (round(f.x, 4), round(f.y, 4))
        for i, w in enumerate(wires):
            if on_segment(pt, *w):
                terminals.setdefault(island[i], set()).add((kind, f.text, pt))
                break
    length = lambda w: abs(w[0][0] - w[1][0]) + abs(w[0][1] - w[1][1])
    ends = {}
    for i, w in enumerate(wires):
        for p in w:
            ends.setdefault((island[i], p), []).append(i)
    bends = {}
    for (isl, p), segs in ends.items():
        if len(segs) == 2:
            (a, b), (c, d) = wires[segs[0]], wires[segs[1]]
            if (a[1] == b[1]) != (c[1] == d[1]):
                bends[isl] = bends.get(isl, 0) + 1
    crossings = []
    for i, (a, b) in enumerate(wires):
        for j in range(i):
            if island[i] == island[j]:
                continue
            c, d = wires[j]
            ah, ch = a[1] == b[1], c[1] == d[1]
            if ah == ch:
                continue
            p = (c[0], a[1]) if ah else (a[0], c[1])
            if on_segment(p, a, b) and on_segment(p, c, d):
                crossings.append(list(p))
    power_islands = {isl for isl, t in terminals.items() if any(k == "power" for k, *_ in t)}
    rail_mm = sum(length(w) for i, w in enumerate(wires) if island[i] in power_islands)
    two = [isl for isl, t in terminals.items() if len(t) == 2]
    tortuous = sorted(isl for isl in two if bends.get(isl, 0) >= 3)
    # A direct two-pin wire much longer than the distance between its pins goes the long way round (H3).
    island_mm = {}
    for i, w in enumerate(wires):
        island_mm[island[i]] = island_mm.get(island[i], 0) + length(w)
    detours = []
    for isl in two:
        pts = pin_points.get(isl, [])
        if len(pts) == 2 and all(k == "part" for k, *_ in terminals[isl]):
            direct = abs(pts[0][0] - pts[1][0]) + abs(pts[0][1] - pts[1][1])
            if direct and island_mm[isl] > DETOUR_MIN_MM and island_mm[isl] / direct > DETOUR_RATIO:
                detours.append(sorted(t[2] for t in terminals[isl]) + [round(island_mm[isl] / direct, 2)])
    labels = [k for k, _ in scene.labels if k != "text"]
    # Parts joined only through labels or rail symbols are separate groups: a
    # page made of such islands shows no path, whatever its crossing count.
    part_parent = {}

    def part_find(r):
        while part_parent.setdefault(r, r) != r:
            part_parent[r] = part_parent[part_parent[r]]
            r = part_parent[r]
        return r

    for s in refs.get("part", []):
        part_find(s.ref)
    for t in terminals.values():
        parts = sorted(ref for kind, ref, *_ in t if kind == "part")
        for ref in parts[1:]:
            part_parent[part_find(ref)] = part_find(parts[0])
    groups = {}
    for ref in part_parent:
        groups.setdefault(part_find(ref), []).append(ref)
    part_groups = sorted((sorted(g) for g in groups.values()), key=lambda g: (-len(g), g))
    content = content_box(scene, root)
    paper, fits = paper_fit(scene, content)
    drawing = scene.page.expanded(-FRAME_MM)
    # Share of 25.4 mm cells of the drawing area that hold any object: a sparse
    # page with notes in its corners has a large bounding box but few inked cells.
    cells = set()
    for box in _object_boxes(scene, root):
        for cx in range(int((box.x_min - drawing.x_min) // CELL_MM), int((box.x_max - drawing.x_min) // CELL_MM) + 1):
            for cy in range(int((box.y_min - drawing.y_min) // CELL_MM), int((box.y_max - drawing.y_min) // CELL_MM) + 1):
                cells.add((cx, cy))
    total = max(1, int(drawing.width // CELL_MM) * int(drawing.height // CELL_MM))
    return {
        "paper": paper,
        "content_box_mm": [round(v, 1) for v in (content.x_min, content.y_min, content.x_max, content.y_max)] if content else None,
        "content_size_mm": [round(content.width, 1), round(content.height, 1)] if content else None,
        # Share of the drawing area's width and height the content spans: a page drawn as one strip leaves a low value.
        "content_span": [round(content.width / drawing.width, 2), round(content.height / drawing.height, 2)]
        if content and drawing.area else None,
        "occupancy": round(content.area / drawing.area, 3) if content and drawing.area else 0.0,
        "cell_coverage": round(len(cells) / total, 3),
        "fits_paper": fits,
        "oversized_paper": bool(paper and fits and PAPER_ORDER.index(fits) < PAPER_ORDER.index(paper)),
        "part_groups": len(part_groups),
        "part_group_refs": part_groups,
        "longest_segment_mm": round(max(map(length, wires), default=0), 1),
        "segments": len(wires),
        "wire_mm": round(sum(map(length, wires)), 1),
        "bends": sum(bends.values()),
        "cross_net_crossings": len(crossings),
        "junctions": len(junctions),
        "two_terminal_connections": len(two),
        "tortuous_connections": len(tortuous),
        "detour_connections": len(detours),
        "detours": sorted(detours),
        "max_bends_in_connection": max(bends.values(), default=0),
        "rail_wire_mm": round(rail_mm, 1),
        "power_symbols": len(refs.get("power", [])),
        "labels_local": labels.count("label"),
        "labels_global": labels.count("global_label"),
        "power_libraries": sorted(p for p in power if p.startswith("power:")),
        # Locations, so a failure names what to redraw.
        "crossing_points": sorted(crossings),
        "tortuous": [sorted(t[2] if t[0] in ("part", "power") else f"{t[0]}:{t[1]}" for t in terminals[isl])
                     for isl in tortuous],
    }


def gate(metrics, max_crossings=0, max_tortuous=0, allow_oversized_paper=False):
    """Hard drawing gate. Raise a limit only through a reasoned waiver."""
    reasons = []
    if metrics["cross_net_crossings"] > max_crossings:
        reasons.append(f"{metrics['cross_net_crossings']} different-net wire crossings (limit {max_crossings})")
    if metrics["tortuous_connections"] > max_tortuous:
        reasons.append(f"{metrics['tortuous_connections']} two-terminal connections with >=3 bends (limit {max_tortuous})")
    if metrics.get("oversized_paper") and not allow_oversized_paper:
        w, h = metrics["content_size_mm"]
        reasons.append(f"content {w}x{h} mm fits {metrics['fits_paper']} but the sheet is {metrics['paper']}: "
                       f"use {metrics['fits_paper']} or bring this page's other blocks onto it (HR-11)")
    return {"status": "FAIL" if reasons else "PASS", "reasons": reasons,
            "scope": "Drawing readability only; never electrical or datasheet evidence."}
