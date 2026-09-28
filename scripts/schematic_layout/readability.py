"""Wiring readability metrics and gate for one native sheet.

These are drawing-quality measures, not electrical evidence. Islands are
joined exactly as KiCad joins wires: at segment endpoints lying on another
segment and at explicit junctions; a bare perpendicular crossing stays apart.
"""

from .routing import on_segment
from .scene import read_scene
from .sexpr import all_nodes, first, value


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
    for kind, symbols in refs.items():
        for s in symbols:
            for p in s.pins:
                pt = tuple(round(v, 4) for v in p.point)
                for i, w in enumerate(wires):
                    if on_segment(pt, *w):
                        terminals.setdefault(island[i], set()).add((kind, s.ref, p.id))
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
    crossings = 0
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
                crossings += 1
    power_islands = {isl for isl, t in terminals.items() if any(k == "power" for k, *_ in t)}
    rail_mm = sum(length(w) for i, w in enumerate(wires) if island[i] in power_islands)
    two = [isl for isl, t in terminals.items() if len(t) == 2]
    tortuous = sorted(isl for isl in two if bends.get(isl, 0) >= 3)
    labels = [k for k, _ in scene.labels if k != "text"]
    return {
        "segments": len(wires),
        "wire_mm": round(sum(map(length, wires)), 1),
        "bends": sum(bends.values()),
        "cross_net_crossings": crossings,
        "junctions": len(junctions),
        "two_terminal_connections": len(two),
        "tortuous_connections": len(tortuous),
        "max_bends_in_connection": max(bends.values(), default=0),
        "rail_wire_mm": round(rail_mm, 1),
        "power_symbols": len(refs.get("power", [])),
        "labels_local": labels.count("label"),
        "labels_global": labels.count("global_label"),
        "power_libraries": sorted(p for p in power if p.startswith("power:")),
    }


def gate(metrics, max_crossings=0, max_tortuous=0):
    reasons = []
    if metrics["cross_net_crossings"] > max_crossings:
        reasons.append(f"{metrics['cross_net_crossings']} different-net wire crossings (limit {max_crossings})")
    if metrics["tortuous_connections"] > max_tortuous:
        reasons.append(f"{metrics['tortuous_connections']} two-terminal connections with >=3 bends (limit {max_tortuous})")
    return {"status": "FAIL" if reasons else "PASS", "reasons": reasons,
            "scope": "Drawing readability only; never electrical or datasheet evidence."}
