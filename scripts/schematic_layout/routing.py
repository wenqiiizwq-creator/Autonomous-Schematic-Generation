"""Deterministic Manhattan MST + bounded obstacle-aware orthogonal routing.

MST port adapted from tscircuit getMspConnectionPairsFromPins.ts (MIT, 2024
tscircuit Inc.). A* architecture informed by kicad-mcp-pro schematic_router.py
(MIT, 2026 Osman Aslan). Local implementation retains heading in search state,
checks complete edges, rejects off-grid pins, and never bypasses obstacles at
terminals. See references/upstream-integration.md and upstream-licenses/.
"""

import heapq
import itertools
import math
from .geometry import Box

EPS = 1e-6


def on_segment(p, a, b):
    cross = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    return (
        abs(cross) < EPS
        and min(a[0], b[0]) - EPS <= p[0] <= max(a[0], b[0]) + EPS
        and min(a[1], b[1]) - EPS <= p[1] <= max(a[1], b[1]) + EPS
    )


def segment_hits_box(a, b, box):
    # Liang-Barsky clipping also catches thin obstacles between grid nodes.
    lo, hi = 0.0, 1.0
    for p, d, mn, mx in (
        (a[0], b[0] - a[0], box.x_min, box.x_max),
        (a[1], b[1] - a[1], box.y_min, box.y_max),
    ):
        if abs(d) < EPS:
            if p < mn - EPS or p > mx + EPS:
                return False
        else:
            x, y = (mn - p) / d, (mx - p) / d
            lo = max(lo, min(x, y))
            hi = min(hi, max(x, y))
            if lo > hi + EPS:
                return False
    return True


def intersection(a, b, c, d):
    """Orthogonal segment intersection: point or collinear overlap endpoints."""
    ah = abs(a[1] - b[1]) < EPS
    ch = abs(c[1] - d[1]) < EPS
    if ah != ch:
        p = (c[0], a[1]) if ah else (a[0], c[1])
        return [p] if on_segment(p, a, b) and on_segment(p, c, d) else []
    candidates = sorted(
        set(p for p in (a, b, c, d) if on_segment(p, a, b) and on_segment(p, c, d))
    )
    return candidates


def manhattan_mst(pins):
    """Prim with stable IDs; never pair pins from different nets at the caller."""
    pins = sorted(pins, key=lambda p: p.id)
    if len({p.id for p in pins}) != len(pins):
        raise ValueError("Duplicate pin ID")
    if len(pins) < 2:
        return []
    remaining = {p.id: p for p in pins}
    tree = []
    best = {pins[0].id: (0.0, "")}
    result = []
    while remaining:
        pid = min(remaining, key=lambda p: (best.get(p, (math.inf, ""))[0], p))
        p = remaining.pop(pid)
        _, parent = best[pid]
        if parent:
            result.append((parent, pid))
        tree.append(pid)
        for other in remaining.values():
            dist = abs(p.point[0] - other.point[0]) + abs(p.point[1] - other.point[1])
            candidate = (dist, pid)
            if candidate < best.get(other.id, (math.inf, "")):
                best[other.id] = candidate
    return result


def grid_point(point, grid):
    if grid <= 0 or not math.isfinite(grid):
        raise ValueError("Grid must be finite and positive")
    if not all(math.isfinite(x) for x in point):
        raise ValueError("Non-finite coordinate")
    node = tuple(round(x / grid) for x in point)
    if any(abs(x - n * grid) > EPS for x, n in zip(point, node)):
        raise ValueError(
            f"Off-grid terminal {point}; choose a compatible grid, never silently snap"
        )
    return node


def simplify(points):
    result = []
    for p in points:
        if result and p == result[-1]:
            continue
        while len(result) > 1 and on_segment(result[-1], result[-2], p):
            result.pop()
        result.append(p)
    return result


def route(
    start,
    end,
    obstacles,
    page,
    grid=1.27,
    start_dir=None,
    end_dir=None,
    max_states=150000,
    bend_cost=4.0,
):
    """Find a path within page; end_dir is the terminal's OUTWARD direction.

    Heading belongs to the state because a future bend cost depends on it.
    All obstacle edges are checked; terminals inside obstacles are errors.
    """
    sn, en = grid_point(start, grid), grid_point(end, grid)
    world = lambda n: (round(n[0] * grid, 6), round(n[1] * grid, 6))
    if not page.contains_point(*start) or not page.contains_point(*end):
        raise ValueError("Routing endpoint outside usable page")
    if any(o.contains_point(*p) for p in (start, end) for o in obstacles):
        raise ValueError(f"Routing terminal is obstructed: {start} -> {end}")
    if sn == en:
        return [start]
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
    initial = (sn, None)
    costs = {initial: 0.0}
    prev = {initial: None}
    counter = itertools.count()
    queue = [(abs(sn[0] - en[0]) + abs(sn[1] - en[1]), 0.0, next(counter), initial)]
    edge_cache = {}
    explored = 0
    while queue and explored < max_states:
        _, g, _, state = heapq.heappop(queue)
        if g != costs.get(state):
            continue
        node, heading = state
        explored += 1
        if node == en:
            points = []
            while state is not None:
                points.append(world(state[0]))
                state = prev[state]
            return simplify(points[::-1])
        for direction in dirs:
            if node == sn and start_dir and direction != tuple(start_dir):
                continue
            nxt = (node[0] + direction[0], node[1] + direction[1])
            if nxt == en and end_dir and direction != (-end_dir[0], -end_dir[1]):
                continue
            a, b = world(node), world(nxt)
            if not page.contains_point(*b):
                continue
            edge = tuple(sorted((node, nxt)))
            if edge not in edge_cache:
                edge_cache[edge] = any(segment_hits_box(a, b, o) for o in obstacles)
            if edge_cache[edge]:
                continue
            cost = g + 1 + (bend_cost if heading and heading != direction else 0)
            ns = (nxt, direction)
            if cost >= costs.get(ns, math.inf):
                continue
            costs[ns] = cost
            prev[ns] = state
            h = abs(nxt[0] - en[0]) + abs(nxt[1] - en[1])
            heapq.heappush(queue, (cost + h, cost, next(counter), ns))
    raise ValueError(
        f"Unrouted {start} -> {end}; explored {explored} states (limit {max_states})"
    )


def wire_box(a, b, clearance=0.3):
    return Box(
        min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])
    ).expanded(clearance)


def normalize_wires(wires, extra_points=()):
    """Split at same-net branches/contacts, deduplicate, add degree>=3 dots.

    wires: [(net,a,b)]. Different-net contact is always rejected by this
    generation engine (explicit remote labels can avoid such crossings).
    """
    points = {i: {a, b} for i, (_, a, b) in enumerate(wires)}
    for i, (net, a, b) in enumerate(wires):
        if a == b:
            raise ValueError("Zero-length wire")
        if a[0] != b[0] and a[1] != b[1]:
            raise ValueError("Diagonal wire")
        points[i].update(p for p in extra_points if on_segment(p, a, b))
        for j, (other, c, d) in enumerate(wires[i + 1 :], i + 1):
            hits = intersection(a, b, c, d)
            if hits and net != other:
                raise ValueError(f"Different nets touch: {net}, {other}")
            points[i].update(hits)
            points[j].update(hits)
    segments = set()
    for i, (net, _, _) in enumerate(wires):
        coords = sorted(points[i])
        for a, b in zip(coords, coords[1:]):
            segments.add((net, a, b))
    degrees = {}
    for net, a, b in segments:
        for p in (a, b):
            degrees[(net, p)] = degrees.get((net, p), 0) + 1
    return sorted(segments), sorted(
        p for (net, p), degree in degrees.items() if degree >= 3
    )
