"""Read-only pin-to-ink and native physical-pin coverage checks.

An attachment candidate is a drawing defect candidate, not an electrical open.
No pin-tip coordinates, libraries or connections are changed by this module.
Manufacturer truth is a separate, externally authored evidence contract.
"""
import hashlib
import math
from pathlib import Path
import re

from .design_change import read_native
from .project_audit import audit_project, properties, _instance
from .scene import is_hidden, transform, xy
from .sexpr import all_nodes, dump, first, parse, value


def segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    squared = dx * dx + dy * dy
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / squared)) if squared else 0
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def arc_distance(p, start, mid, end):
    ax, ay = start
    bx, by = mid
    cx, cy = end
    det = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(det) < 1e-12:
        raise ValueError("Degenerate three-point arc")
    aa, bb, cc = ax * ax + ay * ay, bx * bx + by * by, cx * cx + cy * cy
    center = ((aa * (by - cy) + bb * (cy - ay) + cc * (ay - by)) / det,
              (aa * (cx - bx) + bb * (ax - cx) + cc * (bx - ax)) / det)
    angle = lambda q: math.atan2(q[1] - center[1], q[0] - center[0])
    a, b, c, query = map(angle, (start, mid, end, p))
    delta = lambda x, y: (y - x) % (2 * math.pi)
    # Choose the sweep containing mid; do not use the arc's full bounding circle.
    if delta(a, b) > delta(a, c):
        a, c = c, a
    if delta(a, query) <= delta(a, c) + 1e-10:
        return abs(math.dist(p, center) - math.dist(start, center))
    return min(math.dist(p, start), math.dist(p, end))


def attachment_rows(lib, unit, style, tolerance=0.16):
    """Distances use local coordinates and half stroke width, never body AABBs."""
    if not math.isfinite(tolerance) or not 0 <= tolerance <= 0.25:
        raise ValueError("Attachment tolerance must be between 0 and 0.25 mm")
    if first(lib, "extends"):
        return [], ["Unresolved symbol inheritance"]
    active, gaps = [], []
    for sub in all_nodes(lib, "symbol"):
        match = re.search(r"_(\d+)_(\d+)$", str(sub[1]))
        if not match:
            gaps.append("Unrecognized symbol unit/style")
        elif int(match[1]) in (0, unit) and int(match[2]) in (0, style):
            active.append(sub)
    segments, circles, arcs, unsupported = [], [], [], set()
    for sub in active:
        for g in sub[2:]:
            if not isinstance(g, list) or not g:
                continue
            half = float(value(first(g, "stroke", []), "width", 0)) / 2
            if not math.isfinite(half) or half < 0:
                raise ValueError("Invalid symbol stroke width")
            if g[0] == "rectangle":
                a, b = xy(g, "start"), xy(g, "end")
                corners = [a, (a[0], b[1]), b, (b[0], a[1]), a]
                segments.extend((a, b, half) for a, b in zip(corners, corners[1:]))
            elif g[0] == "polyline":
                points = [tuple(map(float, p[1:3])) for p in all_nodes(first(g, "pts", []), "xy")]
                if len(points) < 2:
                    gaps.append("Polyline has fewer than two points")
                segments.extend((a, b, half) for a, b in zip(points, points[1:]))
            elif g[0] == "circle":
                radius = float(value(g, "radius"))
                if not math.isfinite(radius) or radius <= 0:
                    raise ValueError("Invalid symbol circle radius")
                circles.append((xy(g, "center"), radius, half))
            elif g[0] == "arc":
                points = [xy(g, key) for key in ("start", "mid", "end")]
                try:
                    arc_distance(points[0], *points)
                    arcs.append((*points, half))
                except ValueError:
                    unsupported.add("degenerate_arc")
            elif g[0] != "pin":
                # Text, Beziers and future primitives cannot prove attachment.
                unsupported.add(str(g[0]))
    points = [p for a, b, _ in segments for p in (a, b)] + [c for c, _, _ in circles] + [p for a, b, c, _ in arcs for p in (a, b, c)]
    if any(not math.isfinite(x) for p in points for x in p):
        raise ValueError("Nonfinite symbol artwork coordinates")
    active_pins = [p for s in active for p in all_nodes(s, "pin")]
    # Standard op-amp libraries may put only supply pins in a separate unit.
    # This classification is not available to a single-unit IC with missing art.
    bodyless_power_unit = (unit > 1 and not (segments or circles or arcs or unsupported)
                          and bool(active_pins) and all(p[1] in ("power_in", "power_out") for p in active_pins)
                          and any(g[0] in ("polyline", "rectangle", "circle", "arc")
                                  for s in all_nodes(lib, "symbol") for g in s[2:] if isinstance(g, list) and g))
    rows = []
    for sub in active:
        for pin in all_nodes(sub, "pin"):
            at = first(pin, "at")
            tip = xy(pin)
            angle = float(at[3])
            length = float(value(pin, "length"))
            if not all(math.isfinite(x) for x in (*tip, angle, length)) or length < 0:
                raise ValueError("Invalid pin geometry")
            inner = (tip[0] + length * math.cos(math.radians(angle)),
                     tip[1] + length * math.sin(math.radians(angle)))
            distances = [max(0, segment_distance(inner, a, b) - half) for a, b, half in segments]
            distances += [max(0, abs(math.dist(inner, c) - r) - half) for c, r, half in circles]
            distances += [max(0, arc_distance(inner, a, b, c) - half) for a, b, c, half in arcs]
            distance = min(distances) if distances else None
            hidden = is_hidden(pin)
            if hidden or length == 0 or bodyless_power_unit:
                status = "NOT_APPLICABLE"
            elif distance is not None and distance <= tolerance + 1e-9:
                status = "PASS"
            elif unsupported or distance is None:
                status = "INSUFFICIENT"
            else:
                status = "CANDIDATE"
            rows.append({"pin": str(value(pin, "number", "")), "name": str(value(pin, "name", "")),
                         "electrical_type": str(pin[1]), "hidden": hidden, "length_mm": length,
                         "tip_local": tip, "inner_local": inner, "angle": angle,
                         "distance_to_ink_mm": round(distance, 6) if distance is not None else None,
                         "unsupported_primitives": sorted(unsupported), "attachment": status})
            if status == "NOT_APPLICABLE":
                rows[-1]["reason"] = "hidden pin" if hidden else "zero-length pin" if length == 0 else "bodyless separate power unit"
    return rows, gaps


def audit_symbols(root, netlist=None, project=None, exceptions=None, tolerance=0.16):
    root = Path(root).resolve()
    hierarchy = audit_project(root, project=project)
    rows, errors, gaps, used = [], [], [], set()
    exceptions = exceptions or {"schema_version": 1, "exceptions": []}
    if set(exceptions) != {"schema_version", "exceptions"} or exceptions["schema_version"] != 1 or not isinstance(exceptions["exceptions"], list):
        raise ValueError("Invalid symbol exception document")
    allowed = {}
    for e in exceptions["exceptions"]:
        if set(e) != {"instance", "reference", "unit", "pin", "lib_sha256", "reason", "evidence"} or not all(isinstance(e[k], str) and e[k].strip() for k in set(e) - {"unit"}) or type(e["unit"]) is not int:
            raise ValueError("Exception needs exact instance/reference/unit/pin/library hash, reason and evidence")
        key = (e["instance"], e["reference"], e["unit"], e["pin"])
        if key in allowed:
            raise ValueError("Duplicate pin exception")
        allowed[key] = e
    errors.extend(hierarchy["errors"])
    gaps.extend(hierarchy["coverage_gaps"])
    for page in hierarchy["pages"]:
        path = root.parent / page["path"]
        tree = parse(path.read_text())
        libs = {str(l[1]): l for l in all_nodes(first(tree, "lib_symbols", []), "symbol")}
        for sym in all_nodes(tree, "symbol"):
            props = properties(sym)
            ctx = _instance(sym, hierarchy["project"], page["instance"])
            if ctx is None:  # Never borrow the reference from a different project/instance.
                continue
            ref = str(value(ctx, "reference", ""))
            if ref.startswith("#"):
                continue
            unit = int(value(ctx, "unit", value(sym, "unit", 1)))
            style = int(value(sym, "body_style", value(sym, "convert", 1)))
            lid = str(value(sym, "lib_name", value(sym, "lib_id", "")))
            lib = libs.get(lid)
            if lib is None:
                continue
            digest = hashlib.sha256(dump(lib).encode()).hexdigest()
            pins, pin_gaps = attachment_rows(lib, unit, style, tolerance)
            gaps.extend(f"{ref} unit {unit}: {g}" for g in pin_gaps)
            if not pins:
                gaps.append(f"{ref} unit {unit}: no resolved active pins")
            for p in pins:
                if not p["pin"]:
                    errors.append({"kind": "empty_pin_number", "reference": ref})
                key = (page["instance"], ref, unit, p["pin"])
                if key in allowed:
                    used.add(key)
                    e = allowed[key]
                    if e["lib_sha256"] != digest or p["attachment"] != "CANDIDATE":
                        errors.append({"kind": "stale_or_inapplicable_exception", "reference": ref, "pin": p["pin"]})
                    else:
                        p["attachment"] = "REVIEWED_EXCEPTION"
                        p["disposition"] = {k: e[k] for k in ("reason", "evidence")}
                p.update({"reference": ref, "unit": unit, "style": style, "page": page["path"],
                          "instance": page["instance"], "value": props.get("Value", ""),
                          "footprint": props.get("Footprint", ""), "lib_id": lid, "lib_sha256": digest,
                          "dnp": value(sym, "dnp", "no") == "yes"})
                at = first(sym, "at")
                p["tip_sheet"] = transform(p["tip_local"], xy(sym), float(at[3]) if len(at) > 3 else 0, str(value(sym, "mirror", "")))
                rows.append(p)
    if allowed.keys() - used:
        errors.append({"kind": "unused_exceptions", "pins": [list(k) for k in sorted(allowed.keys() - used)]})
    counts = {s: sum(r["attachment"] == s for r in rows) for s in ("PASS", "CANDIDATE", "INSUFFICIENT", "NOT_APPLICABLE", "REVIEWED_EXCEPTION")}
    graphics_status = "FAIL" if counts["CANDIDATE"] else "INSUFFICIENT" if counts["INSUFFICIENT"] else "PASS"
    physical = {f'{r["reference"]}.{r["pin"]}' for r in rows}
    native_result = {"status": "INSUFFICIENT", "reason": "Native KiCad XML not supplied"}
    if netlist is not None:
        native = read_native(netlist)
        exported = set(native["pin_nets"])
        missing, extra = sorted(physical - exported), sorted(exported - physical)
        source_refs = {r["reference"] for r in rows}
        native_result = {"status": "FAIL" if missing or extra or source_refs != set(native["components"]) else "PASS",
                         "sha256": native["sha256"], "source_pins_missing_from_xml": missing,
                         "xml_pins_missing_from_source": extra,
                         "source_only_references": sorted(source_refs - native["components"].keys()),
                         "xml_only_references": sorted(native["components"].keys() - source_refs)}
    axes = [hierarchy["status"], graphics_status, native_result["status"]]
    status = "FAIL" if errors or "FAIL" in axes else "INSUFFICIENT" if gaps or "INSUFFICIENT" in axes else "PASS"
    return {"schema_version": 1, "status": status,
            "scope": "Pin-to-ink candidates and native physical pin coverage only. No manufacturer, pad geometry, peripheral or electrical approval.",
            "hierarchy_status": hierarchy["status"], "page_count": hierarchy["page_count"],
            "component_count": len({r["reference"] for r in rows}), "physical_pin_count": len(physical),
            "file_sha256": hierarchy["file_sha256"], "graphics": {"status": graphics_status, "tolerance_mm": tolerance, "counts": counts},
            "native_pin_coverage": native_result, "errors": errors, "coverage_gaps": sorted(set(gaps)), "pins": rows}
