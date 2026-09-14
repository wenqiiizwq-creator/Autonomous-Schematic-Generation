"""Independent geometry inspection, including same-owner fields and wires."""

from collections import Counter
from .geometry import Box, union
from .routing import on_segment, intersection, segment_hits_box, wire_box, grid_point


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


def check_scene(scene, grid=1.27, reserved=None, body_clearance=1.27, pin_nets=None):
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
    pins = [p for s in scene.symbols for p in s.pins]
    body_terminals = {
        f"{s.ref}:unit{s.unit}": {
            p.point: p.direction for p in s.pins if p.point == p.inner
        }
        for s in scene.symbols
    }
    if reserved is None:
        reserved = [
            Box(
                scene.page.x_max - 120,
                scene.page.y_max - 45,
                scene.page.x_max - 5,
                scene.page.y_max - 5,
            )
        ]
    for i, (a, box) in enumerate(bodies):
        for b, other in bodies[i + 1 :]:
            if box.overlaps(other, gap_mm=body_clearance - 1e-6):
                add("body_overlap", [a, b], "Body overlap or insufficient clearance")
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
                pin.point, pin.inner, box.expanded(-0.04)
            ):
                add("text_pin_overlap", [a, pin.id], "Visible text crosses a pin leg")
    extents = bodies + fields
    extents += [
        (f"wire:{i}", wire_box(a, b, 0)) for i, (a, b) in enumerate(scene.wires)
    ]
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
        if not box.inside(scene.page, margin_mm=5):
            add("off_page", [name], "Object outside page/frame clearance")
        if any(box.overlaps(r) for r in reserved):
            add(
                "reserved_region",
                [name],
                "Object intrudes into reserved title/block region",
            )
    for i, (a, b) in enumerate(scene.wires):
        if a == b:
            add("zero_wire", [f"wire:{i}"], "Zero-length wire")
        if a[0] != b[0] and a[1] != b[1]:
            add("diagonal_wire", [f"wire:{i}"], "Non-orthogonal wire")
        for name, box in bodies:
            if segment_hits_box(a, b, box) and not body_terminal_contact(
                a, b, box, body_terminals[name]
            ):
                add(
                    "wire_body",
                    [f"wire:{i}", name],
                    "Wire passes through a symbol body",
                )
        for name, box in fields:
            if segment_hits_box(a, b, box.expanded(-0.04)):
                add(
                    "wire_text", [f"wire:{i}", name], "Wire passes through visible text"
                )
    anchors = [(p.id, p.point) for p in pins]
    anchors += [(f"wire:{i}", p) for i, w in enumerate(scene.wires) for p in w]
    anchors += [
        (f"{kind}:{f.text}", (f.x, f.y)) for kind, f in scene.labels if kind != "text"
    ]
    anchors += [("junction", p) for p in scene.junctions] + [
        ("nc", p) for p in scene.no_connects
    ]
    for name, point in anchors:
        try:
            grid_point(point, grid)
        except ValueError as e:
            add("off_grid", [name], str(e))
    # Detect wire ends without a pin, label, or another segment; corners count
    # as connected segments and need no spurious junction dot.
    attached = {p.point for p in pins} | {
        (f.x, f.y) for k, f in scene.labels if k != "text"
    }
    for i, w in enumerate(scene.wires):
        for p in w:
            if p not in attached and not any(
                on_segment(p, *other) for j, other in enumerate(scene.wires) if i != j
            ):
                add("orphan_wire", [f"wire:{i}"], f"Unattached endpoint {p}")
    for kind, f in scene.labels:
        if (
            kind != "text"
            and (f.x, f.y) not in {p.point for p in pins}
            and not any(on_segment((f.x, f.y), *w) for w in scene.wires)
        ):
            add(
                "floating_label",
                [f"{kind}:{f.text}"],
                "Label is not attached to a pin or wire",
            )
    for i, p in enumerate(scene.junctions):
        if sum(on_segment(p, *w) for w in scene.wires) < 2:
            add(
                "orphan_junction",
                [f"junction:{i}"],
                "Junction does not join at least two segments",
            )
    for i, p in enumerate(scene.no_connects):
        if p not in {pin.point for pin in pins}:
            add("orphan_nc", [f"nc:{i}"], "NC marker not on pin")
    # Build connectivity from endpoints, pin contacts and explicit junctions;
    # naked mid-segment crossings stay separate, matching the schematic model.
    parent = list(range(len(scene.wires)))

    def root(i):
        while parent[i] != i:
            i = parent[i]
        return i

    def join(i, j):
        parent[root(j)] = root(i)

    for i, (a, b) in enumerate(scene.wires):
        for j, (c, d) in enumerate(scene.wires[i + 1 :], i + 1):
            hits = intersection(a, b, c, d)
            if hits and (
                len(hits) > 1
                or any(p in (a, b, c, d) or p in scene.junctions for p in hits)
            ):
                join(i, j)
    label_groups = {}
    for kind, f in scene.labels:
        if kind == "text":
            continue
        indices = [i for i, w in enumerate(scene.wires) if on_segment((f.x, f.y), *w)]
        label_groups.setdefault((kind, f.text), []).extend(indices)
    for indices in label_groups.values():
        for i in indices[1:]:
            join(indices[0], i)
    owners = {}
    if pin_nets:
        for pin in pins:
            for i, w in enumerate(scene.wires):
                if on_segment(pin.point, *w) and pin.id in pin_nets:
                    owners.setdefault(root(i), set()).add(pin_nets[pin.id])
        for r, nets in owners.items():
            if len(nets) > 1:
                add(
                    "different_net_contact",
                    [str(x) for x in sorted(nets)],
                    "Wire geometry joins distinct intended nets",
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
            elif hits and root(i) != root(j):
                # Legitimate undotted crossings are visible review items, not
                # automatically called electrical shorts.
                findings.append(
                    {
                        "code": "wire_crossing",
                        "objects": [f"wire:{i}", f"wire:{j}"],
                        "detail": "Undotted crossing: inspect in native render",
                        "severity": "warning",
                    }
                )
    content = union(box for name, box in extents)
    counts = Counter(f["code"] for f in findings)
    status = (
        "FAIL"
        if any(f["severity"] == "error" for f in findings)
        else ("INSUFFICIENT" if scene.gaps else ("REVIEW" if findings else "PASS"))
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
            "gaps": sorted(set(scene.gaps)),
            "checks": [
                "body_overlap",
                "wire_body",
                "text_overlap_including_same_owner",
                "text_body",
                "wire_text",
                "text_pin",
                "page_frame",
                "reserved_region",
                "off_grid",
                "orphan_wire",
                "floating_label",
                "orphan_junction",
                "orphan_nc",
                "collinear_overlap",
                "wire_crossing",
            ],
            "pin_net_intent_checked": bool(pin_nets),
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
