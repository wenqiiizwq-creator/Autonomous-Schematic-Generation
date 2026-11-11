"""Independent geometry inspection, including same-owner fields and wires."""

from collections import Counter
from .geometry import Box, union
from .scene import GlobalLabelText
from .routing import on_segment, intersection, segment_hits_box, wire_box
from .native_geometry import ink_gap


def _round_stroke_hits_box(a, b, box, radius):
    """Intersect a round-capped segment capsule with axis-aligned bounds.

    Square expansion is only a broad-phase bound: it includes corner areas
    outside the circular cap. The shortest Euclidean distance is attained
    by a segment endpoint and the box, or a box corner and the segment.
    """
    if segment_hits_box(a, b, box):
        return True

    def point_box(p):
        dx = max(box.x_min - p[0], 0, p[0] - box.x_max)
        dy = max(box.y_min - p[1], 0, p[1] - box.y_max)
        return dx * dx + dy * dy

    dx, dy = b[0] - a[0], b[1] - a[1]
    length_sq = dx * dx + dy * dy

    def point_segment(p):
        t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length_sq)) if length_sq else 0
        return (p[0] - a[0] - t * dx) ** 2 + (p[1] - a[1] - t * dy) ** 2

    corners = ((x, y) for x in (box.x_min, box.x_max) for y in (box.y_min, box.y_max))
    distance_sq = min(point_box(a), point_box(b), *(point_segment(p) for p in corners))
    return distance_sq <= radius * radius


def body_terminal_contact(a, b, body, terminals):
    """Allow only a point contact at an explicit zero-length body terminal.

    Power flags have their pin on the boundary of the drawn stem's envelope.
    The scene's default 0.254 mm stroke pads the envelope by 0.127 mm. Allow
    only that terminal cap, in the declared outward pin direction. A traversal
    beyond the cap or a foreign contact remains a defect.
    """
    if a[1] == b[1] and body.y_min <= a[1] <= body.y_max:
        lo = max(min(a[0], b[0]), body.x_min)
        hi = min(max(a[0], b[0]), body.x_max)
    elif a[0] == b[0] and body.x_min <= a[0] <= body.x_max:
        lo = max(min(a[1], b[1]), body.y_min)
        hi = min(max(a[1], b[1]), body.y_max)
    else:
        return False
    if not -1e-8 <= hi - lo <= 0.127 + 1e-8:
        return False
    for point, other in ((a, b), (b, a)):
        if point not in terminals:
            continue
        dx, dy = terminals[point]
        vx, vy = other[0] - point[0], other[1] - point[1]
        if vx * dx + vy * dy > 0 and abs(vx * dy - vy * dx) < 1e-8:
            return True
    return False


def own_pin_exit(a, b, exits):
    """A wire leaving one of the symbol's own pin tips straight outward.

    Conservative graphic bounds (LED arrows, magnetics arcs) can reach past a
    pin tip; that pin's own outward wire is its intended exit, not a traversal.
    Any other wire through the same box remains a defect.
    """
    for point, other in ((a, b), (b, a)):
        d = exits.get(point)
        if d is None:
            continue
        vx, vy = other[0] - point[0], other[1] - point[1]
        if vx * d[0] + vy * d[1] > 0 and abs(vx * d[1] - vy * d[0]) < 1e-8:
            return True
    return False


FRAME_MARGIN_MM = 5.0   # drawn objects keep this clearance from the page edge


def title_block(page):
    """Default reserved region: the title block in the lower right corner of the page."""
    return Box(page.x_max - 120, page.y_max - 45, page.x_max - 5, page.y_max - 5)


def wire_findings(scene, wires, reserved=None):
    """off_page, reserved_region and wire_body for named wires ``[(name, a, b)]``.

    Shared by Sheet.build (planned segments, before they are written) and the
    geometry gate (written wires), so both judge with the same numbers.
    """
    reserved = [title_block(scene.page)] if reserved is None else reserved
    findings = []
    def add(code, objects, detail):
        findings.append({"code": code, "objects": objects, "detail": detail, "severity": "error"})
    bodies = [(f"{s.ref}:unit{s.unit}", s.body, {p.point: p.direction for p in s.pins if p.point == p.inner},
               {p.point: p.direction for p in s.pins if p.point != p.inner}) for s in scene.symbols if s.body]
    for name, a, b in wires:
        box = wire_box(a, b, 0)
        if not box.inside(scene.page, margin_mm=FRAME_MARGIN_MM):
            add("off_page", [name], "Object outside page/frame clearance")
        if any(box.overlaps(r) for r in reserved):
            add("reserved_region", [name], "Object intrudes into reserved title/block region")
        for body_name, body, terminals, exits in bodies:
            if (segment_hits_box(a, b, body) and not body_terminal_contact(a, b, body, terminals)
                    and not own_pin_exit(a, b, exits)):
                add("wire_body", [name, body_name], "Wire passes through a symbol body")
    return findings


def check_scene(scene, reserved=None, body_clearance=1.27):
    findings = []

    def add(code, objects, detail):
        findings.append(
            {"code": code, "objects": objects, "detail": detail, "severity": "error"}
        )

    bodies = [(f"{s.ref}:unit{s.unit}", s.body) for s in scene.symbols if s.body]
    fields = [
        (f"{s.ref}:unit{s.unit}:{name}", f.box())
        for s in scene.symbols
        for name, f in s.fields
    ]
    fields += [
        (f"{kind}:{i}:{f.text}", f.box()) for i, (kind, f) in enumerate(scene.labels)
    ]
    global_labels = {f"{kind}:{i}:{f.text}": f.outline()
                     for i, (kind, f) in enumerate(scene.labels) if isinstance(f, GlobalLabelText)}
    gaps = list(scene.gaps)
    gaps += ["Global label native coverage gap: " + ", ".join(outline.gaps)
             for outline in global_labels.values() if outline.gaps]
    pins = [p for s in scene.symbols for p in s.pins]
    if reserved is None:
        reserved = [title_block(scene.page)]
    findings += wire_findings(scene, [(f"wire:{i}", a, b) for i, (a, b) in enumerate(scene.wires)], reserved)
    for i, (a, box) in enumerate(bodies):
        for b, other in bodies[i + 1 :]:
            if box.overlaps(other):
                add("body_overlap", [a, b], "Symbol body bounds overlap")
            elif box.overlaps(other, gap_mm=body_clearance - 1e-6):
                findings.append({"code": "body_clearance", "objects": [a, b],
                                 "detail": f"Separated bodies have less than {body_clearance:g} mm clearance; inspect in native render",
                                 "severity": "error"})
    for i, (a, box) in enumerate(fields):
        # Reference and Value on the SAME component are checked as well.
        for b, other in fields[i + 1 :]:
            if box.overlaps(other, gap_mm=0.15):
                add("text_overlap", [a, b], "Visible field/label boxes collide")
        for b, body in bodies:
            if box.overlaps(body):
                add("text_body_overlap", [a, b], "Visible text overlaps a symbol body")
        for pin in pins:
            if pin.point != pin.inner and segment_hits_box(
                pin.point, pin.inner, box if a in global_labels else box.expanded(-0.04)
            ) and not (a in global_labels and global_labels[a].terminal_contact(pin.point, pin.inner)):
                add("text_pin_overlap", [a, pin.id], "Visible text crosses a pin leg")
    # A pin number is drawn above a horizontal pin leg and left of a vertical one, centred on the leg and reaching
    # 1.87 mm from it at 1.27 mm (KiCad 10 SVG, 2026-11-11). Whatever else is drawn there hides it; this is checked
    # for every part, so the render review reads each library symbol's pin text once.
    justified = {f"{s.ref}:unit{s.unit}:{name}": (f.justify, round(f.angle) % 180 == 0 and f.text.isascii())
                 for s in scene.symbols for name, f in s.fields}
    justified.update({f"{kind}:{i}:{f.text}": (f.justify, round(f.angle) % 180 == 0 and f.text.isascii())
                      for i, (kind, f) in enumerate(scene.labels)})
    for s_ in scene.symbols:
        seen = set()
        for pin in s_.pins if s_.numbers_shown else ():
            if pin.hidden or pin.point == pin.inner or not pin.number:
                continue
            (x0, y0), (x1, y1) = pin.point, pin.inner
            if (pin.point, pin.inner) in seen:      # stacked pads share one leg and one drawn number
                continue
            seen.add((pin.point, pin.inner))
            half = 0.4 * 1.27 * min(len(pin.number), 3)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            box = Box(mx - half, y0 - 1.9, mx + half, y0 - 0.4) if y0 == y1 else Box(x0 - 1.9, my - half, x0 - 0.4, my + half)
            name = f"pin-number:{pin.id}"
            for b, other in fields:
                # Latin text is estimated about 13 % wide, on the side away from its anchor; left as it is, that
                # would report a clear number as covered.
                just, flat = justified.get(b, (frozenset(), False))
                spare = 0.13 * other.width if flat else 0.0
                left = 0.0 if "left" in just else spare if "right" in just else spare / 2
                right = 0.0 if "right" in just else spare if "left" in just else spare / 2
                if box.overlaps(Box(other.x_min + left, other.y_min, other.x_max - right, other.y_max), gap_mm=0.3):
                    add("pin_number_text", [name, b], "Visible text covers a pin number")
            for i, (a, b) in enumerate(scene.wires):
                if segment_hits_box(a, b, box.expanded(-0.05)):
                    add("pin_number_wire", [name, f"wire:{i}"], "Wire passes through a pin number")
    extents = bodies + fields      # wires are judged by wire_findings above
    extents += [(f"pin:{p.id}", wire_box(p.point, p.inner, 0)) for p in pins]
    extents += [
        (f"junction:{i}", Box.from_center(*p, 0.8, 0.8))
        for i, p in enumerate(scene.junctions)
    ]
    extents += [
        (f"nc:{i}", Box.from_center(*p, 1.27, 1.27))
        for i, p in enumerate(scene.no_connects)
    ]
    for name, box in extents:
        if not box.inside(scene.page, margin_mm=FRAME_MARGIN_MM):
            add("off_page", [name], "Object outside page/frame clearance")
        if any(box.overlaps(r) for r in reserved):
            add(
                "reserved_region",
                [name],
                "Object intrudes into reserved title/block region",
            )
    # Native default polyline ink has round caps/joins. Clip each real
    # capsule against actual bounds rather than treating an outline's
    # interior (or a diagonal's entire AABB) as opaque. Annotation crossings
    # with conductors are visual warnings, never electrical contacts.
    graphic_extents = []
    for name, a, b, width in scene.graphic_segments:
        radius = width / 2
        extent = wire_box(a, b, radius)
        graphic_extents.append((name, extent))
        if not extent.inside(scene.page, margin_mm=FRAME_MARGIN_MM):
            add("off_page", [name], "Graphic ink outside page/frame clearance")
        if any(_round_stroke_hits_box(a, b, r, radius) for r in reserved):
            add("reserved_region", [name], "Graphic ink enters reserved title/block region")
        for target, box in fields:
            if _round_stroke_hits_box(a, b, box, radius):
                findings.append({"code": "graphic_text", "objects": [name, target],
                                 "detail": "Annotation ink intersects conservative text bounds; inspect actual glyphs in native render",
                                 "severity": "error"})
        for target, box in bodies:
            if _round_stroke_hits_box(a, b, box, radius):
                add("graphic_body", [name, target], "Annotation ink crosses symbol body bounds")
        for target, c, d in (
            [(f"wire:{i}", *wire) for i, wire in enumerate(scene.wires)]
            + [(p.id, p.point, p.inner) for p in pins if p.point != p.inner]
        ):
            if _round_stroke_hits_box(a, b, wire_box(c, d, 0), radius):
                findings.append({"code": "graphic_wire" if target.startswith("wire:") else "graphic_pin",
                                 "objects": [name, target],
                                 "detail": "Annotation ink crosses a conductor; inspect native render, no electrical contact inferred",
                                 "severity": "error"})
    for i, (a, b) in enumerate(scene.wires):
        if a == b:
            add("zero_wire", [f"wire:{i}"], "Zero-length wire")
        if a[0] != b[0] and a[1] != b[1]:
            add("diagonal_wire", [f"wire:{i}"], "Non-orthogonal wire")
        for name, box in fields:
            if (segment_hits_box(a, b, box if name in global_labels else box.expanded(-0.04))
                    and not (name in global_labels and global_labels[name].terminal_contact(a, b))):
                add(
                    "wire_text", [f"wire:{i}", name], "Wire passes through visible text"
                )
    for i, p in enumerate(scene.junctions):
        if sum(on_segment(p, *w) for w in scene.wires) < 2:
            add(
                "orphan_junction",
                [f"junction:{i}"],
                "Junction does not join at least two segments",
            )
    for i, (a, b) in enumerate(scene.wires):
        for j, (c, d) in enumerate(scene.wires[i + 1 :], i + 1):
            hits = intersection(a, b, c, d)
            if len(hits) > 1:
                add(
                    "collinear_overlap",
                    [f"wire:{i}", f"wire:{j}"],
                    "Duplicate/overlapping segments must be normalized",
                )
    # Native channels are independent of Sheet.build's existing estimates.
    # Frames protect edges/structure, not an opaque box against architecture text.
    native_extents = []
    for i, frame in enumerate(scene.native_frames):
        if not frame.get("segments"): continue
        for other in scene.native_frames[i+1:]:
            if not other.get("segments"): continue
            if (ink_gap(frame["segments"],other["segments"])<=0
                    or (frame["kind"]==other["kind"]=="sheet"
                        and Box(*frame["interior"]).overlaps(Box(*other["interior"])) )):
                add("native_frame_overlap",[frame["id"],other["id"]],"Native structural outlines/overlapping sheets collide")
    for frame in scene.native_frames:
        if not frame.get("segments"):
            continue
        name = frame["kind"] + ":" + frame["id"]
        native_extents.append((name, Box(*frame["box"])))
        for target, box in fields + bodies:
            if any(_round_stroke_hits_box(a, b, box, w / 2) for a, b, w in frame["segments"]):
                add("native_frame_object", [name, target], "Native structural edge intersects visible object bounds")
        for i, (a, b) in enumerate(scene.wires):
            if (any(_round_stroke_hits_box(c, d, wire_box(a, b, 0), (w + scene.native_stroke_upper_mm) / 2)
                    for c, d, w in frame["segments"])
                    or (frame["kind"] == "sheet" and _round_stroke_hits_box(a,b,Box(*frame["interior"]),scene.native_stroke_upper_mm/2))):
                add("wire_sheet_frame", [f"wire:{i}", name], "Electrical wire crosses native frame/structural footprint")
    native_fields = [(f["id"], f["conservative_box"]) for f in scene.native_texts]
    for i, (name, box) in enumerate(native_fields):
        native_extents.append((name, box))
        for target, other in fields + native_fields[i + 1:]:
            if box.overlaps(other, gap_mm=.15):
                add("native_sheet_text_overlap", [name, target], "Complete shown sheet text conservative envelopes collide")
        for target, other in bodies:
            if box.overlaps(other): add("native_sheet_text_body", [name, target], "Sheet field intersects foreign symbol body")
        for frame in scene.native_frames:
            if any(_round_stroke_hits_box(a, b, box, w / 2) for a, b, w in frame.get("segments", [])):
                add("native_sheet_text_frame", [name, frame["id"]], "Complete sheet field envelope intersects native frame ink")
        for pin in pins:
            if pin.point != pin.inner and segment_hits_box(pin.point, pin.inner, box):
                add("native_sheet_text_pin", [name, pin.id], "Sheet field crosses pin leg")
        for wi, (a, b) in enumerate(scene.wires):
            if _round_stroke_hits_box(a,b,box,scene.native_stroke_upper_mm/2): add("native_sheet_wire_text", [f"wire:{wi}", name], "Wire crosses full sheet field envelope")
    for i, item in enumerate(scene.native_pin_texts):
        name=item["id"]; ink=item["segments"]; box=Box(*item["box"])
        native_extents.append((name, box))
        for other in scene.native_pin_texts[i + 1:]:
            if ink_gap(ink, other["segments"]) <= 0:
                add("native_pin_text_overlap", [name, other["id"]], "Different native pin-name strokes intersect")
        for outline in scene.native_owner_outlines:
            if ink_gap(ink,outline["segments"])<=0:
                add("native_pin_text_outline",[name,outline["id"]],"Pin-name ink crosses actual symbol foreground outline")
        for target, field_box in fields + native_fields:
            if any(_round_stroke_hits_box(a, b, field_box, w / 2) for a,b,w in ink):
                add("native_pin_text_field", [name, target], "Native pin-name ink intersects field envelope")
        for symbol in scene.symbols:
            if str(next((n[1] for n in symbol.node if isinstance(n,list) and n and n[0]=='uuid'),'')) == item["symbol_uuid"]:
                # Background fill intentionally contains pin names. Foreground
                # outline uncertainty is an explicit context gap, not PASS.
                continue
            if symbol.body and any(_round_stroke_hits_box(a,b,symbol.body,w/2) for a,b,w in ink):
                add("native_pin_text_body", [name, symbol.ref], "Pin-name crosses foreign symbol body")
        for wi,(a,b) in enumerate(scene.wires):
            # Upper bound is taken from ALL visible same-page native strokes.
            width=item["page_stroke_upper_mm"]
            if ink_gap(ink, [[a,b,width]]) <= 0:
                add("native_pin_wire_text", [name,f"wire:{wi}"], "Wire intersects native pin-name ink")
    for name,box in native_extents:
        if not box.inside(scene.page,margin_mm=FRAME_MARGIN_MM): add("off_page",[name],"Native geometry outside page/frame clearance")
        if any(box.overlaps(r) for r in reserved): add("reserved_region",[name],"Native geometry enters reserved region")
    extents += native_extents
    content = union(box for name, box in extents + graphic_extents)
    counts = Counter(f["code"] for f in findings)
    status = (
        "FAIL"
        if any(f["severity"] == "error" for f in findings)
        else ("INSUFFICIENT" if gaps else "PASS")
    )
    return {
        "status": status,
        "findings": findings,
        "counts": dict(counts),
        "coverage": {
            "symbols": len(scene.symbols),
            "bodies": len(bodies),
            "visible_texts": len(fields),
            "wires": len(scene.wires),
            "pins": len(pins),
            "sheet_pins": len(scene.sheet_pins),
            "graphic_segments": len(scene.graphic_segments),
            "native_frames": len(scene.native_frames),
            "native_sheet_fields": len(scene.native_texts),
            "native_pin_names": len(scene.native_pin_texts),
            "native_owner_outlines": len(scene.native_owner_outlines),
            "gaps": sorted(set(gaps)),
            "render_review_items": sorted(set(scene.review)),
            "render_review_refs": {k: sorted(v) for k, v in sorted(scene.review_refs.items())},
            "checks": [
                "body_overlap",
                "body_clearance",
                "wire_body",
                "text_overlap_including_same_owner",
                "text_body",
                "wire_text",
                "text_pin",
                "page_frame",
                "reserved_region",
                "orphan_junction",
                "collinear_overlap",
                "explicit_unfilled_polyline_ink",
            ],
            "limitations": [
                "AABB bounds; arc full-circle bounds may over-report",
                "Text widths are conservative estimates, not native glyph metrics",
                "Pin names/numbers and custom drawing sheets require native render review",
                "Native exported netlist is the electrical authority",
            ],
        },
        "page_mm": [scene.page.x_max, scene.page.y_max],
        "content_bounds": (
            [content.x_min, content.y_min, content.x_max, content.y_max]
            if content
            else None
        ),
        "native_render_review_required": True,
    }
