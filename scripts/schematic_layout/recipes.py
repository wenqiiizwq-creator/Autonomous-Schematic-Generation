"""Pin-relative drawing recipes for readable native schematics.

The agent decides the drawing structure: where each anchor device sits, which
pins start a spine, which parts form a series chain, shunt, bank, divider or
repeated lane, which nets are rails, which leave the sheet and which local nets
carry a small name. This module derives every other position from real pin
geometry, writes explicit orthogonal wires, power symbols and labels, rejects
contacts between different nets, and places fields against the final drawing.
It is not a placement solver. With declared rails and external nets it also
proposes a role for every part (the outline rules in drawing-recipes.md) and
audits the drawing against them; a deviation needs a recorded reason.
"""

import copy
import math

from .component_role import is_connector
from .field_placer import FieldSpec, autoplace_fields
from .generate import Libraries, library_dirs, make_root, pin_clipped_body, pin_net_map
from .geometry import Box, TextField, text_extent
from .label_geometry import global_outline, DIRECTION_STYLE
from .readability import gate, measure
from .routing import on_segment, segment_hits_box, wire_box
from .scene import read_scene
from .sexpr import Atom, all_nodes, first, form, set_node, value

G = 1.27
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
ORIENTATIONS = [(0, ""), (90, ""), (180, ""), (270, ""), (0, "y"), (90, "y"), (180, "y"), (270, "y")]
UPRIGHT = [(0, ""), (0, "y")]
FLAG_SYMBOL = "power:PWR_FLAG"


def flag_value(symbol, net):
    """Value text of a power symbol: the net it names, or PWR_FLAG for a flag."""
    return "PWR_FLAG" if symbol == FLAG_SYMBOL else net


def pt(p):
    return (round(p[0], 4), round(p[1], 4))


def add(p, d, n=1):
    """Point ``n`` grid steps from ``p`` along unit direction ``d``."""
    return pt((p[0] + d[0] * n * G, p[1] + d[1] * n * G))


def label_geometry(kind, text, at, outward, font):
    """Native angle, justification and outline box of a label at a wire end.

    ``outward`` is the direction the label extends from its connection point.
    Verified by native render on KiCad 10.0.6: global labels extend left at
    0/right, right at 180/left, up at 90/left and down at 270/right; local
    label text is drawn readable, above a horizontal wire and left of a
    vertical one.
    """
    x, y = at
    if kind == "global":
        angle, just = DIRECTION_STYLE[outward]
        return angle, sorted(just), global_outline(text, at, outward, font).box
    angle, just = {RIGHT: (0, ["left", "bottom"]), LEFT: (180, ["right", "bottom"]),
                   UP: (90, ["left", "bottom"]), DOWN: (270, ["right", "bottom"])}[outward]
    w, h = text_extent(text, font)
    if outward in (LEFT, RIGHT):
        x0 = x if outward == RIGHT else x - w
        return angle, just, Box(x0, y - 0.3 - h, x0 + w, y - 0.3)
    return angle, just, (Box(x - 0.3 - h, y - w, x - 0.3, y) if outward == UP else Box(x - 0.3 - h, y, x - 0.3, y + w))


def select_local_names(intent, external=(), rails=(), min_pins=3):
    """Default naming rule: page-local nets touching a part with >= min_pins pins.

    Such nets are controller/transistor function nodes a reader looks up by
    name. Callers remove names the design never had and add documented ones.
    """
    counts = {}
    for net in intent["nets"]:
        for pid in net["pins"]:
            ref = pid.rsplit(".", 1)[0]
            counts[ref] = counts.get(ref, 0) + 1
    for pid in intent.get("no_connect", []):
        ref = pid.rsplit(".", 1)[0]
        counts[ref] = counts.get(ref, 0) + 1
    skip = set(external) | set(rails)
    return sorted(n["name"] for n in intent["nets"] if n["name"] not in skip and len(n["pins"]) > 1
                  and any(counts[p.rsplit(".", 1)[0]] >= min_pins for p in n["pins"]))


# Outline rules: which recipes may draw a part of each proposed role.
ALLOWED = {
    "anchor": {"place", "put"},
    "series": {"series"},
    "shunt": {"shunt", "bank", "series", "divider"},
    "decoupling": {"shunt", "bank"},
    "bank": {"bank"},
    "divider_upper": {"divider", "series"},
    "divider_lower": {"divider", "shunt"},
    "lane_series": {"series"},
    "lane_shunt": {"shunt"},
    "explicit": {"place", "put"},
}


class Sheet:
    """Structured drawing of one sheet; see the module docstring.

    ``rails`` maps rail/return nets to their ``power:`` symbol; ``external``
    lists nets that leave the sheet. Declaring both enables ``plan`` and the
    structure audit in the build report.
    """

    def __init__(self, intent, rails=None, external=(), paper="A4", dirs=(), power_ref_start=1):
        self.intent = intent
        self.nets = pin_net_map(intent)
        self.components = {c["ref"]: c for c in intent["components"]}
        self.libraries = Libraries(library_dirs(dirs))
        self.dirs = tuple(dirs)
        self.paper = paper
        self.power_ref_start = power_ref_start
        self.placements = {}
        self.pins = {}
        self.segments = []
        self.powers = []
        self.flags = []
        self.labels = []
        self.names = []
        self.notes = []
        self.decisions = []
        self.reasons = {}
        self._shapes = {}
        self.rails = dict(rails or {})
        self.external = sorted(external)
        unknown = (set(self.rails) | set(self.external)) - {n["name"] for n in intent["nets"]}
        if unknown:
            raise ValueError(f"Unknown rail/external nets: {sorted(unknown)}")
        self.plan = self._suggest() if rails is not None else None

    # ----- outline rules --------------------------------------------------
    def _is_anchor(self, ref):
        return len(self._shape(ref)[0]) >= 3 or is_connector(self.components[ref])

    def _suggest(self):
        """Propose a role for every part and a label role for every net."""
        returns = {n for n, sym in self.rails.items() if self._power_shape(sym)[2]}
        roles, two = {}, {}
        for ref in sorted(self.components):
            nums = sorted(self._shape(ref)[0])
            if self._is_anchor(ref):
                roles[ref] = {"role": "anchor", "why": "three or more pins, or a connector"}
            elif len(nums) != 2 or any(f"{ref}.{n}" not in self.nets for n in nums):
                roles[ref] = {"role": "explicit", "why": "not a connected two-pin part"}
            else:
                two[ref] = tuple(self.nets[f"{ref}.{n}"] for n in nums)
        at_anchor = {}
        for pid, net in self.nets.items():
            if roles.get(pid.rsplit(".", 1)[0], {}).get("role") == "anchor":
                at_anchor.setdefault(net, set()).add(pid.rsplit(".", 1)[0])
        groups = {}
        for ref, pair in two.items():
            if set(pair) - set(self.rails):
                groups.setdefault(frozenset(pair), []).append(ref)
        for refs in groups.values():
            if len(refs) > 1:
                for r in refs:
                    roles[r] = {"role": "bank", "group": sorted(refs), "why": "parallel parts on the same two nets"}
        for m in sorted(at_anchor):
            if m in self.rails:
                continue
            legs = [r for r, pair in two.items() if m in pair and r not in roles
                    and self.components[r]["lib_id"].startswith("Device:R")]
            low = [r for r in legs if set(two[r]) - {m} <= returns]
            up = [r for r in legs if r not in low]
            if len(low) == 1 and len(up) == 1:
                why = f"resistor pair with its midpoint {m} on an anchor pin"
                roles[up[0]] = {"role": "divider_upper", "tap": m, "why": why}
                roles[low[0]] = {"role": "divider_lower", "tap": m, "why": why}
        lanes = {}
        for s_ref, pair in two.items():
            if s_ref in roles or set(pair) & set(self.rails):
                continue
            for m in pair:
                shunts = [d for d, q in two.items() if d not in roles and d != s_ref and m in q
                          and set(q) - {m} <= returns]
                if m in at_anchor and len(shunts) == 1:
                    anchor = sorted(at_anchor[m])[0]
                    key = (anchor, self.components[s_ref]["lib_id"], self.components[shunts[0]]["lib_id"])
                    lanes.setdefault(key, []).append((s_ref, shunts[0]))
        for (anchor, _, _), pairs in lanes.items():
            # A part shared by two candidate lanes is a rung between them, not a lane.
            if len(pairs) > 1 and len({p[0] for p in pairs}) == len(pairs) == len({p[1] for p in pairs}):
                for s_ref, d_ref in pairs:
                    why = f"one of {len(pairs)} repeated series+shunt lanes into {anchor}"
                    roles[s_ref] = {"role": "lane_series", "lane": d_ref, "why": why}
                    roles[d_ref] = {"role": "lane_shunt", "lane": s_ref, "why": why}
        for ref, pair in two.items():
            if ref not in roles:
                on_rails = sum(n in self.rails for n in pair)
                role = ("series", "shunt", "decoupling")[on_rails]
                roles[ref] = {"role": role, "why": ("between two signal nets", "one pin on a rail",
                                                    "both pins on rails")[on_rails]}
        names = select_local_names(self.intent, self.external, self.rails)
        nets = {}
        for n in sorted(x["name"] for x in self.intent["nets"]):
            nets[n] = ("power" if n in self.rails else "global" if n in self.external
                       else "name" if n in names else None)
        return {"parts": roles, "nets": nets}

    def justify(self, subject, reason):
        """Record why a part or net deviates from the outline rules."""
        if not str(reason).strip():
            raise ValueError("A deviation needs a reason")
        self.reasons[subject] = reason

    # ----- geometry -------------------------------------------------------
    def _shape(self, ref, rotation=0, mirror=""):
        lib_id = self.components[ref]["lib_id"]
        key = (lib_id, rotation, mirror)
        if key not in self._shapes:
            lib = self.libraries.load(lib_id)
            sym = form("symbol", form("lib_id", lib_id), form("at", 0, 0, rotation), form("unit", 1))
            if mirror:
                sym.append(form("mirror", Atom(mirror)))
            sym.append(form("property", "Reference", "X", form("at", 0, 0, 0),
                            form("effects", form("hide", Atom("yes")))))
            s = read_scene(form("kicad_sch", form("paper", "A4"), form("lib_symbols", lib), sym)).symbols[0]
            self._shapes[key] = ({p.id.split(".", 1)[1]: (pt(p.point), tuple(p.direction)) for p in s.pins}, s.body)
        return self._shapes[key]

    def point(self, target):
        if isinstance(target, str):
            if target not in self.pins:
                raise ValueError(f"{target} is not a pin of a placed part")
            return self.pins[target][0]
        return pt(target)

    def net_at(self, p):
        p = pt(p)
        found = {n for n, a, b in self.segments if on_segment(p, a, b)}
        found |= {self.nets[pid] for pid, (q, _) in self.pins.items() if q == p and pid in self.nets}
        if len(found) != 1:
            raise ValueError(f"Expected one net at {p}, found {sorted(found)}")
        return found.pop()

    def _net(self, target):
        return self.nets.get(target) if isinstance(target, str) else self.net_at(target)

    # ----- placement ------------------------------------------------------
    def orient(self, ref, facing, order=None):
        """First (rotation, mirror) in which each pin of ``facing`` ({pin: direction}) exits that way.

        ``order=(a, b, axis)`` also keeps pin ``a`` before pin ``b`` along x (0) or y (1).
        """
        if ref not in self.components:
            raise ValueError(f"Unknown reference {ref}")
        for rot, mir in ORIENTATIONS:
            pins, _ = self._shape(ref, rot, mir)
            missing = [str(k) for k in facing if str(k) not in pins]
            if missing:
                raise ValueError(f"{ref} has no pins {missing}")
            if all(pins[str(k)][1] == tuple(d) for k, d in facing.items()) and (
                    order is None or pins[str(order[0])][0][order[2]] < pins[str(order[1])][0][order[2]]):
                return rot, mir
        raise ValueError(f"{ref}: no orientation gives pin exits {facing}; change the requested sides")

    def place(self, ref, at, rotation=0, mirror="", pin=None, facing=None, order=None):
        """Place an anchor device explicitly (controllers, connectors, magnetics).

        ``facing`` ({pin: direction}, optional ``order``) chooses rotation and
        mirror from the required pin exits; see ``orient``. With ``pin``, ``at``
        is where that pin's tip lands instead of the symbol origin.
        """
        if facing:
            rotation, mirror = self.orient(ref, facing, order)
        if pin is not None:
            pins, _ = self._shape(ref, rotation, mirror)
            if str(pin) not in pins:
                raise ValueError(f"{ref} has no pin {pin}")
            q = pins[str(pin)][0]
            at = (at[0] - q[0], at[1] - q[1])
        self.decisions.append({"recipe": "place", "parts": [ref]})
        return self._place(ref, at, rotation, mirror)

    def _place(self, ref, at, rotation=0, mirror=""):
        if ref not in self.components:
            raise ValueError(f"Unknown reference {ref}")
        if ref in self.placements:
            raise ValueError(f"{ref} is already placed")
        at = pt(at)
        pins, _ = self._shape(ref, rotation, mirror)
        self.placements[ref] = {"at": list(at), "rotation": rotation, "mirror": mirror}
        for num, (q, d) in pins.items():
            self.pins[f"{ref}.{num}"] = (pt((at[0] + q[0], at[1] + q[1])), d)
        return ref

    def put(self, ref, num, at, toward, orientations=None):
        """Place ``ref`` so pin ``num`` lands on ``at`` and the part extends along ``toward``.

        The pin faces back against ``toward``. Parts with more than two pins stay
        upright (rotation 0, optionally mirrored) unless orientations are given.
        """
        self.decisions.append({"recipe": "put", "parts": [ref]})
        return self._put(ref, num, at, toward, orientations)

    def _put(self, ref, num, at, toward, orientations=None):
        pins, _ = self._shape(ref)
        options = orientations or (ORIENTATIONS if len(pins) <= 2 else UPRIGHT)
        back = (-toward[0], -toward[1])
        for rot, mir in options:
            shape, _ = self._shape(ref, rot, mir)
            q, d = shape[str(num)]
            if d == back:
                return self._place(ref, (at[0] - q[0], at[1] - q[1]), rot, mir)
        raise ValueError(f"{ref}.{num} cannot face {back}; change the recipe direction or anchor")

    def _pair(self, ref, net):
        nums = sorted(self._shape(ref)[0])
        on = [n for n in nums if self.nets.get(f"{ref}.{n}") == net]
        if len(nums) != 2 or len(on) != 1:
            raise ValueError(f"{ref} is not a two-pin part with exactly one pin on {net}")
        return on[0], next(n for n in nums if n != on[0])

    # ----- wiring ---------------------------------------------------------
    def wire(self, *points, net=None):
        """Orthogonal polyline through pins (``REF.NUM``) and points; returns its end."""
        ids = [p for p in points if isinstance(p, str)]
        pts = [self.point(p) for p in points]
        if net is None:
            if ids:
                net = self.nets.get(ids[0])
            else:
                try:
                    net = self.net_at(pts[0])
                except ValueError:
                    net = self.net_at(pts[-1])
        if net is None:
            raise ValueError(f"No net for wire {points}")
        for pid in ids:
            if self.nets.get(pid) != net:
                raise ValueError(f"{pid} is on {self.nets.get(pid)}, not {net}")
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            if a[0] != b[0] and a[1] != b[1]:
                raise ValueError(f"Diagonal wire {a} -> {b} on {net}; add a corner")
            self.segments.append((net, a, b))
        return pts[-1]

    def stub(self, pid, n=2):
        """Leave a pin along its outward direction; returns the stub end."""
        end = add(self.point(pid), self.pins[pid][1], n)
        return self.wire(pid, end)

    def connect(self, a, b, first="h", x=None, y=None):
        """L (``first`` h/v) or Z (middle leg at ``x`` or ``y``) connection."""
        pa, pb = self.point(a), self.point(b)
        if x is not None:
            mid = [(x, pa[1]), (x, pb[1])]
        elif y is not None:
            mid = [(pa[0], y), (pb[0], y)]
        else:
            mid = [(pb[0], pa[1])] if first == "h" else [(pa[0], pb[1])]
        return self.wire(a, *[pt(m) for m in mid], b)

    def _origin(self, start, toward, net=None):
        """Start point for a recipe; a pin is left along its own direction first."""
        if not isinstance(start, str):
            return self.point(start), net or self.net_at(start)
        d = self.pins[start][1]
        if d == (-toward[0], -toward[1]):
            raise ValueError(f"{start} faces away from {toward}; start from the other side")
        if d == toward:
            return self.point(start), self.nets[start]
        return self.stub(start), self.nets[start]

    # ----- recipes --------------------------------------------------------
    def series(self, start, refs, toward, gap=2, net=None):
        """Series chain on one axis, in circuit order; returns each far-pin point.

        ``net`` names the start point's net when no wire reaches it yet.
        """
        if gap < 1:
            raise ValueError("Series gap must be at least one grid step")
        cur, net = self._origin(start, toward, net)
        nodes = []
        for ref in refs:
            near, far = self._pair(ref, net)
            target = add(cur, toward, gap)
            self._put(ref, near, target, toward)
            self.wire(cur, target, net=net)
            cur, net = self.pins[f"{ref}.{far}"][0], self.nets.get(f"{ref}.{far}")
            nodes.append(cur)
        self.decisions.append({"recipe": "series", "parts": list(refs), "toward": list(toward)})
        return nodes

    def _rail(self, target, rail):
        """``rail``: True uses the declared symbol, a string names one, False skips."""
        if rail is True:
            return self.power(target)
        return self.power(target, rail) if rail else self.point(target)

    def shunt(self, node, ref, toward=DOWN, gap=2, rail=True):
        """Two-pin part branching off a node; its far pin gets its rail symbol (``rail=False``: returned)."""
        p, net = self._origin(node, toward)
        near, far = self._pair(ref, net)
        target = add(p, toward, gap)
        self._put(ref, near, target, toward)
        self.wire(p, target, net=net)
        pid = f"{ref}.{far}"
        self.decisions.append({"recipe": "shunt", "parts": [ref], "toward": list(toward)})
        return self._rail(pid, rail)

    def pitch_for(self, refs):
        """Grid steps between banked parts: body, beside-field text and clearance."""
        width = 0
        for ref in refs:
            body_w = max(b.x_max - b.x_min for b in (self._shape(ref, r)[1] for r in (0, 90)))
            c = self.components[ref]
            text = max(TextField(t, 0, 0, 0, 1.27).box().width for t in (ref, c["value"]))
            width = max(width, body_w + text + 1.27)
        return max(4, math.ceil((width + 2 * G) / G))

    def bank(self, start, refs, toward=RIGHT, hang=DOWN, pitch=None, gap=2, rail=True, common=True, depth=None,
             lead=None):
        """Parallel parts hanging from a spine at a regular pitch.

        With ``common`` the far pins share one straight return rail and a single
        rail symbol; otherwise each part gets its own. ``depth`` puts the common
        rail that many grid steps from the spine (a second line, e.g. N between
        L and N). ``rail=False`` draws the common line without a symbol.
        ``lead`` is the grid distance to the first part (default one pitch; 0
        puts it at ``start``, e.g. inline with a pin). Returns the spine end.
        """
        p, net = self._origin(start, toward)
        pitch = pitch or self.pitch_for(refs)
        lead = pitch if lead is None else lead
        nodes = [add(p, toward, lead + i * pitch) for i in range(len(refs))]
        if nodes[-1] != p:
            self.wire(p, nodes[-1], net=net)
        fars = []
        for node, ref in zip(nodes, refs):
            near, far = self._pair(ref, net)
            target = add(node, hang, gap)
            self._put(ref, near, target, hang)
            self.wire(node, target, net=net)
            fars.append(f"{ref}.{far}")
        if len({self.nets.get(f) for f in fars}) != 1:
            raise ValueError(f"Bank {refs} does not share one far net")
        if rail and not common:
            for f in fars:
                self._rail(f, rail)
        elif fars:
            deepest = max(self.point(f)[1] * hang[1] + self.point(f)[0] * hang[0] for f in fars) / G
            level = (p[1] * hang[1] + p[0] * hang[0]) / G
            if depth is not None and level + depth < deepest + 1:
                raise ValueError(f"Bank {refs}: depth {depth} does not clear the parts")
            depth = level + depth if depth is not None else deepest + 2
            ends = []
            for f in fars:
                q = self.point(f)
                steps = round(depth - (q[1] * hang[1] + q[0] * hang[0]) / G)
                ends.append(self.wire(f, add(q, hang, steps)))
            self.wire(ends[0], ends[-1], net=self.nets.get(fars[0]))
            if rail:
                self._rail(ends[-1], rail)
        self.decisions.append({"recipe": "bank", "parts": list(refs), "pitch_grid": pitch, "common_return": common})
        return nodes[-1]

    def divider(self, top, upper, lower, toward=DOWN, gap=2, rail=True):
        """Stacked divider; returns the tap point on the midpoint wire."""
        nodes = self.series(top, [upper, lower], toward, gap)
        far = next(f"{lower}.{n}" for n in self._shape(lower)[0] if self.pins[f"{lower}.{n}"][0] == nodes[-1])
        self._rail(far, rail)
        self.decisions[-1]["recipe"] = "divider"
        return add(nodes[0], toward, gap // 2 or 1)

    # ----- rails and labels -----------------------------------------------
    def _power_shape(self, symbol):
        lib = self.libraries.load(symbol)
        sym = form("symbol", form("lib_id", symbol), form("at", 0, 0, 0), form("unit", 1),
                   form("property", "Reference", "#PWR", form("at", 0, 0, 0), form("effects", form("hide", Atom("yes")))))
        s = read_scene(form("kicad_sch", form("paper", "A4"), form("lib_symbols", lib), sym)).symbols[0]
        return lib, s.body, s.body.center[1] > 0

    @staticmethod
    def _moved(box, at):
        return Box(box.x_min + at[0], box.y_min + at[1], box.x_max + at[0], box.y_max + at[1])

    def power(self, target, symbol=None, net=None, length=2):
        """Rail symbol whose Value is the net name (KiCad 10 names the net from it).

        Without ``symbol`` the declared rail symbol for the net is used.
        """
        net = net or self._net(target)
        symbol = symbol or self.rails.get(net) or "power:GND"
        if not symbol.startswith("power:"):
            raise ValueError(
                f"{target!r} on {net}: invalid rail symbol {symbol!r}. "
                "Rail symbols must come from the power library; use rail=True "
                "for the declared rail, or a full power: library identifier."
            )
        _, shape, down = self._power_shape(symbol)
        d = DOWN if down else UP
        start = self.point(target)
        if isinstance(target, str):
            pd = self.pins[target][1]
            if pd == (-d[0], -d[1]):
                raise ValueError(f"{target} faces away from its {net} symbol; flip the part or recipe")
            if pd != d:
                # Leave the pin sideways far enough that the symbol clears the whole body.
                ref = target.rsplit(".", 1)[0]
                place = self.placements[ref]
                _, body = self._shape(ref, place["rotation"], place["mirror"])
                body = Box(body.x_min + place["at"][0], body.y_min + place["at"][1],
                           body.x_max + place["at"][0], body.y_max + place["at"][1])
                n = next(k for k in range(2, 9) if not body.overlaps(
                    self._moved(shape, add(add(start, pd, k), d, length)), gap_mm=1.27 - 1e-6))
                start = self.wire(target, add(start, pd, n))
        end = add(start, d, length)
        self.wire(start, end, net=net)
        if symbol == FLAG_SYMBOL:
            self.flags.append((net, symbol, end))
        else:
            self.powers.append((net, symbol, end))
        return end

    def power_flag(self, target, length=2):
        """PWR_FLAG on a connector-fed supply declared in ``intent["external_supply"]``.

        The flag names no net and is checked by the external-supply gate; put it
        on the declared connector pin's net, once per declared net.
        """
        net = self._net(target)
        declared = {d.get("net") for d in self.intent.get("external_supply", [])}
        if net not in declared:
            raise ValueError(f"{net} is not declared in external_supply; PWR_FLAG only marks declared connector-fed nets")
        return self.power(target, symbol=FLAG_SYMBOL, net=net, length=length)

    def label(self, target, kind="global", length=3, outward=None, net=None, font=None, reason=None):
        """Label at a wire end extending ``outward`` (a pin's own direction by default).

        Global where the net leaves the sheet; a local join label needs the
        declared boundary as ``reason``.
        """
        if kind not in ("global", "local"):
            raise ValueError("Label kind must be global or local")
        if kind == "local" and not reason:
            raise ValueError("A local join label needs the declared block boundary as its reason")
        p = self.point(target)
        if isinstance(target, str):
            net, outward = self.nets[target], self.pins[target][1]
            if length:
                p = self.wire(target, add(p, outward, length))
        else:
            net = net or self.net_at(p)
        if tuple(outward or ()) not in (LEFT, RIGHT, UP, DOWN):
            raise ValueError(f"{net}: a label needs an outward unit direction")
        font = font or (1.27 if kind == "global" else 1.0)
        self.labels.append({"net": net, "kind": kind, "at": p, "outward": tuple(outward), "font": font})
        if reason:
            self.reasons[f"label:{net}"] = reason
        return p

    def name(self, net, at=None, font=1.0):
        """Small local name on the net's own visible wire (placed at build time)."""
        if at is not None and not any(n == net and on_segment(pt(at), a, b) for n, a, b in self.segments):
            raise ValueError(f"{net}: name position is not on its wire")
        self.names.append({"net": net, "at": pt(at) if at else None, "font": font})

    def text(self, text, at, font=1.27):
        self.notes.append({"text": text, "at": list(pt(at)), "font_mm": font})

    # ----- build ----------------------------------------------------------
    def _segments(self):
        """Split same-net branches; reject any contact between different nets."""
        raw = sorted(set((n, *sorted((a, b))) for n, a, b in self.segments))
        pins = [(self.nets.get(pid), q) for pid, (q, _) in self.pins.items()]
        anchors = (pins + [(l["net"], l["at"]) for l in self.labels]
                   + [(n, e) for n, _, e in self.powers + self.flags])
        crossings = []
        for i, (n, a, b) in enumerate(raw):
            for m, c, d in raw[:i]:
                if n == m:
                    continue
                if (a[1] == b[1]) != (c[1] == d[1]):
                    x = (c[0], a[1]) if a[1] == b[1] else (a[0], c[1])
                    if on_segment(x, a, b) and on_segment(x, c, d):
                        if x in (a, b, c, d):
                            raise ValueError(f"{n} and {m} touch at {x}")
                        crossings.append({"nets": sorted([n, m]), "at": list(x)})
                elif any(on_segment(q, a, b) for q in (c, d)) or any(on_segment(q, c, d) for q in (a, b)):
                    raise ValueError(f"{n} and {m} overlap along {a}-{b}")
            for m, q in anchors:
                if m != n and on_segment(q, a, b):
                    raise ValueError(f"{n} wire {a}-{b} runs over a {m} terminal at {q}")
        split = set()
        for n, a, b in raw:
            cuts = {a, b}
            cuts |= {q for m, c, d in raw if m == n for q in (c, d) if on_segment(q, a, b)}
            cuts |= {q for m, q in anchors if m == n and on_segment(q, a, b)}
            seq = sorted(cuts)
            split |= {(n, u, v) for u, v in zip(seq, seq[1:]) if u != v}
        return sorted(split), crossings

    def _check_connected(self, segments):
        """Every connected pin is wired; a net's separate pieces must carry its name."""
        wired = {q for _, a, b in segments for q in (a, b)}
        loose = [pid for pid, (q, _) in self.pins.items() if pid in self.nets and q not in wired]
        if loose:
            raise ValueError(f"Unwired pins: {sorted(loose)}")
        parent = list(range(len(segments)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for i, (n, a, b) in enumerate(segments):
            for j, (m, c, d) in enumerate(segments[:i]):
                if n == m and {a, b} & {c, d}:
                    parent[find(i)] = find(j)
        named = {l["net"] for l in self.labels} | {n for n, _, _ in self.powers}
        pieces = {}
        for i, (n, _, _) in enumerate(segments):
            pieces.setdefault(n, set()).add(find(i))
        def locations(net, roots):
            result = []
            for piece in sorted(roots):
                lines = [(a, b) for i, (n, a, b) in enumerate(segments)
                         if n == net and find(i) == piece]
                points = sorted({q for line in lines for q in line})
                pins = sorted(pid for pid, (q, _) in self.pins.items()
                              if self.nets.get(pid) == net
                              and any(on_segment(q, a, b) for a, b in lines))
                result.append({"pins": pins, "endpoints": points})
            return result
        broken = sorted(n for n, s in pieces.items() if len(s) > 1 and n not in named)
        if broken:
            detail = {n: locations(n, pieces[n]) for n in broken}
            raise ValueError(f"Nets drawn in separate pieces without a label or rail: {broken}; "
                             f"pieces={detail}. Join intended endpoints or name each piece with its net label/rail.")
        # A labelled net with separate pieces needs its name on every piece.
        for n, s in pieces.items():
            if len(s) > 1:
                ends = [l["at"] for l in self.labels if l["net"] == n] + [e for m, _, e in self.powers if m == n]
                marked = {find(i) for i, (m, a, b) in enumerate(segments) if m == n
                          and any(on_segment(q, a, b) for q in ends)}
                if marked != s:
                    raise ValueError(f"{n}: a separate piece carries no label or rail symbol; "
                                     f"unmarked pieces={locations(n, s - marked)}. "
                                     "Join intended endpoints or name each piece with its net label/rail.")

    def build(self, name="sheet", draft=False):
        """Native sheet root and a report (decisions, crossings, readability).

        ``draft=True`` records name and field placement failures in the report
        instead of raising, so the page can be rendered while it is revised.
        A draft is never a deliverable.
        """
        failures = []
        missing = sorted(set(self.components) - set(self.placements))
        if missing:
            raise ValueError(f"Unplaced parts: {missing}")
        boxes = {r: self._moved(self._shape(r, p["rotation"], p["mirror"])[1], p["at"]) for r, p in self.placements.items()}
        refs = sorted(boxes)
        clash = [(a, b) for i, a in enumerate(refs) for b in refs[i + 1:]
                 if boxes[a].overlaps(boxes[b], gap_mm=1.27 - 1e-6)]
        if clash:
            raise ValueError(f"Part bodies closer than 1.27 mm: {clash}; widen a gap or pitch")
        layout = {"schema_version": 1, "paper": self.paper, "placements": self.placements,
                  "annotations": self.notes, "defer_fields": True}
        root, meta, uid, reserved = make_root(self.intent, layout, name, self.dirs)
        segments, crossings = self._segments()
        self._check_connected(segments)
        scene = read_scene(root)
        page = scene.page.expanded(-12.0)  # inside the drawing-sheet frame
        bodies = {s.ref: pin_clipped_body(s.body, [p for p in s.pins if p.point != p.inner]) for s in scene.symbols}
        for n, a, b in segments:
            if not (page.contains_point(*a) and page.contains_point(*b)):
                raise ValueError(f"{n} wire {a}-{b} leaves the drawing area")
            for box in reserved:
                if segment_hits_box(a, b, box):
                    raise ValueError(f"{n} wire {a}-{b} enters the title block")
            for ref, box in bodies.items():
                if segment_hits_box(a, b, box.expanded(-0.05)):
                    raise ValueError(f"{n} wire {a}-{b} crosses the body of {ref}")
        obstacles = [b.expanded(0.2) for b in bodies.values()] + list(reserved)
        label_pin_obstacles = [(p, wire_box(p.point, p.inner, 0.25))
                               for s in scene.symbols for p in s.pins]
        obstacles += [box for _, box in label_pin_obstacles]
        obstacles += [t.box() for kind, t in scene.labels if kind == "text"]
        wires = {n: [] for n, _, _ in segments}
        for n, a, b in segments:
            wires[n].append((a, b))

        def foreign(box, net):
            return any(segment_hits_box(a, b, box) for n, a, b in segments if n != net)

        # Junctions: three or more wire ends and pins meet.
        degree = {}
        for n, a, b in segments:
            for q in (a, b):
                degree[(n, q)] = degree.get((n, q), 0) + 1
        # Coincident pads of one symbol meet the wire once.
        for n, q in {(self.nets.get(pid), q) for pid, (q, _) in self.pins.items()}:
            if (n, q) in degree:
                degree[(n, q)] += 1
        dots = sorted(q for (n, q), k in degree.items() if k >= 3)
        spots = [Box(q[0] - 0.8, q[1] - 0.8, q[0] + 0.8, q[1] + 0.8)
                 for q in set(dots) | {q for q, _ in self.pins.values()}]
        # Power symbols: body plus Value field.
        powers = []
        for net, symbol, end in self.powers + self.flags:
            lib, body, down = self._power_shape(symbol)
            b = Box(body.x_min + end[0], body.y_min + end[1], body.x_max + end[0], body.y_max + end[1])
            value_at = pt((end[0], b.y_max + 0.9 if down else b.y_min - 0.9))
            vbox = TextField(flag_value(symbol, net), *value_at, 0, 1.0).box()
            for box in (b, vbox):
                if foreign(box, net) or any(box.overlaps(o) for o in obstacles) or not box.inside(page):
                    raise ValueError(f"{net} rail symbol at {end} collides; change the recipe direction or length")
            obstacles += [b.expanded(0.2), vbox.expanded(0.2)]
            powers.append((net, symbol, end, lib, value_at))
        labels = []
        for l in self.labels:
            box = label_geometry(l["kind"], l["net"], l["at"], l["outward"], l["font"])[2]
            outline = (global_outline(l["net"], l["at"], l["outward"], l["font"])
                       if l["kind"] == "global" else None)
            # A same-net segment elsewhere in the body still collides. Only
            # the native connection cap can touch an attached wire or pin.
            if outline:
                pin_boxes = {id(o) for _, o in label_pin_obstacles}
                blockers = [o for o in obstacles if id(o) not in pin_boxes]
                pin_collision = any(box.overlaps(o) and not outline.terminal_contact(p.point, p.inner)
                                    for p, o in label_pin_obstacles)
                wire_collision = any(segment_hits_box(a, b, box) and not outline.terminal_contact(a, b)
                                     for _, a, b in segments)
            else:
                blockers = obstacles
                pin_collision = False
                wire_collision = foreign(box, l["net"])
            if wire_collision or pin_collision or any(box.overlaps(o) for o in blockers) or not box.inside(page):
                raise ValueError(f"{l['net']} label at {l['at']} collides; move its anchor or increase label pitch")
            obstacles.append(box.expanded(0.2))
            labels.append(dict(l))
        for spec in self.names:
            net = spec["net"]
            if net not in wires:
                raise ValueError(f"{net} has no wire to carry its name")
            candidates = []
            if spec["at"]:
                horizontal = any(a[1] == b[1] and on_segment(spec["at"], a, b) for a, b in wires[net])
                candidates = [(spec["at"], RIGHT if horizontal else UP)]
            else:
                # Horizontal wires first (text above), then vertical (text beside);
                # longest segment and mid-segment first, clear of pins and dots.
                for a, b in sorted(wires[net], key=lambda w: (w[0][1] != w[1][1], -abs(w[1][0] - w[0][0])
                                                             - abs(w[1][1] - w[0][1]))):
                    axis = 0 if a[1] == b[1] else 1
                    steps = round(abs(b[axis] - a[axis]) / G)
                    lo = min(a, b, key=lambda q: q[axis])
                    ks = sorted(range(1, steps - 1), key=lambda k: (abs(k - (steps - 1) / 2), k))
                    if axis == 0:
                        candidates += [(pt((lo[0] + k * G, lo[1])), RIGHT) for k in ks]
                    else:
                        candidates += [(pt((lo[0], lo[1] + (k + 1) * G)), UP) for k in ks]
            own = [wire_box(a, b, 0.0) for a, b in wires[net] if a[0] == b[0]] + spots
            for at, outward in candidates:
                box = label_geometry("local", net, at, outward, spec["font"])[2]
                blockers = obstacles + [o for o in own if not (outward == UP and o.x_min == o.x_max == at[0])]
                if (not foreign(box, net) and not any(box.overlaps(o) for o in blockers)
                        and box.inside(page)):
                    labels.append({"net": net, "kind": "local", "at": at, "outward": outward, "font": spec["font"]})
                    obstacles.append(box.expanded(0.2))
                    break
            else:
                if not draft:
                    raise ValueError(f"No clear spot for the {net} name; give it a longer straight wire")
                failures.append(f"name {net}")
        # Emit wires, junctions, NC markers, rails and labels.
        for n, a, b in segments:
            root.append(form("wire", form("pts", form("xy", *a), form("xy", *b)),
                             form("stroke", form("width", 0), form("type", Atom("default"))),
                             form("uuid", uid("wire:" + n + ":" + repr((a, b))))))
        for q in dots:
            root.append(form("junction", form("at", *q), form("diameter", 0), form("color", 0, 0, 0, 0),
                             form("uuid", uid("dot:" + repr(q)))))
        pinmap = {p.id: p for s in scene.symbols for p in s.pins}
        for pid in self.intent.get("no_connect", []):
            root.append(form("no_connect", form("at", *pinmap[pid].point), form("uuid", uid("nc:" + pid))))
        for l in labels:
            key = uid("label:" + l["net"] + ":" + repr(l["at"]))
            angle, just, _ = label_geometry(l["kind"], l["net"], l["at"], l["outward"], l["font"])
            effects = form("effects", form("font", form("size", l["font"], l["font"])),
                           form("justify", *[Atom(j) for j in just]))
            if l["kind"] == "global":
                root.append(form("global_label", l["net"], form("shape", Atom("passive")), form("at", *l["at"], angle),
                                 effects, form("uuid", key),
                                 form("property", "Intersheetrefs", "${INTERSHEET_REFS}", form("at", *l["at"], angle),
                                      form("effects", form("font", form("size", 1, 1)), form("hide", Atom("yes"))))))
            else:
                root.append(form("label", l["net"], form("at", *l["at"], angle), effects, form("uuid", key)))
        cache = first(root, "lib_symbols")
        present = {str(n[1]) for n in all_nodes(cache, "symbol")}
        template = next((first(s, "instances") for s in all_nodes(root, "symbol") if first(s, "instances")), None)
        hidden = lambda: form("effects", form("font", form("size", 1.27, 1.27)), form("hide", Atom("yes")))
        flag_count = 0
        for k, (net, symbol, end, lib, value_at) in enumerate(powers):
            if symbol not in present:
                cache.append(copy.deepcopy(lib))
                present.add(symbol)
            if symbol == FLAG_SYMBOL:
                flag_count += 1
                ref = "#FLG" + uid("flag-reference:" + name + ":" + net + ":" + repr(end)).replace("-", "")
                if ref in self.components:
                    raise ValueError(f"Power flag reference collides with component {ref}")
            else:
                ref = f"#PWR{self.power_ref_start + k - flag_count:03d}"
            numbers = [str(value(p, "number")) for s in all_nodes(lib, "symbol") for p in all_nodes(s, "pin")]
            sym = [Atom("symbol"), form("lib_id", symbol), form("at", *end, 0), form("unit", 1),
                   form("in_bom", Atom("no")), form("on_board", Atom("no")), form("dnp", Atom("no")),
                   form("uuid", uid("power:" + net + ":" + repr(end))),
                   form("property", "Reference", ref, form("at", *end, 0), hidden()),
                   form("property", "Value", flag_value(symbol, net), form("at", *value_at, 0),
                        form("effects", form("font", form("size", 1.0, 1.0)))),
                   form("property", "Footprint", "", form("at", *end, 0), hidden()),
                   form("property", "Datasheet", "", form("at", *end, 0), hidden()),
                   *[form("pin", n, form("uuid", uid("power-pin:" + ref + ":" + n))) for n in numbers]]
            if template is not None:
                instances = copy.deepcopy(template)
                for path in all_nodes(first(instances, "project") or [], "path"):
                    set_node(path, "reference", ref)
                    set_node(path, "unit", 1)
                sym.append(instances)
            root.append(sym)
        # Fields last, against every wire, label and rail symbol actually drawn.
        obstacles += [wire_box(a, b, 0.25) for _, a, b in segments]
        for s in sorted(scene.symbols, key=lambda s: s.ref):
            specs = [FieldSpec(n, f.text, f.font_mm) for n, f in s.fields]
            try:
                placed = autoplace_fields(s.body, [p.point for p in s.pins], obstacles, specs, page=page)
                boxes = [pl.text_field(spec.text, spec.font_mm).box() for spec, pl in zip(specs, placed)]
            except ValueError:
                # Parts wired on all four sides (bridges, transistors) take a corner.
                boxes = self._corner_fields(s.body, specs, obstacles, page)
                if boxes is None:
                    if not draft:
                        raise ValueError(f"{s.ref}: no clear Reference/Value position; give the part more room")
                    failures.append(f"fields {s.ref}")
                    continue
            angle = float(first(s.node, "at")[3])
            for spec, box in zip(specs, boxes):
                prop = next(p for p in all_nodes(s.node, "property") if p[1] == spec.name)
                set_node(prop, "at", *pt(box.center), (0 - angle) % 180)
                effects = first(prop, "effects")
                if first(effects, "justify"):
                    effects.remove(first(effects, "justify"))
                obstacles.append(box)
        metrics = measure(root)
        nets = {n: {"mode": "power", "symbol": s} for n, s, _ in self.powers}
        nets.update({l["net"]: {"label": True} for l in labels})
        report = {
            "schema_version": 1,
            "draft_failures": failures,
            "decisions": self.decisions,
            "crossings": crossings,
            "labels": {k: sorted({l["net"] for l in labels if l["kind"] == k}) for k in ("global", "local")},
            "rails": sorted({n for n, _, _ in self.powers}),
            "readability": {**metrics, "gate": gate(metrics)},
            "structure": self._audit(labels),
            "layout": {**layout, "nets": nets},
            "meta": meta,
        }
        return root, report

    @staticmethod
    def _corner_fields(body, specs, obstacles, page):
        """Stacked fields beside a body corner, clear of every obstacle."""
        sizes = [text_extent(sp.text, sp.font_mm) for sp in specs]
        width, pitch = max(w for w, _ in sizes), max(h for _, h in sizes) + 0.4
        height = pitch * len(specs)
        for margin in (0.8, 2.0, 3.2):
            for right, below in ((True, False), (False, False), (True, True), (False, True)):
                x0 = body.x_max + margin if right else body.x_min - margin - width
                y0 = body.y_max + margin if below else body.y_min - margin - height
                boxes = [Box(x0, y0 + i * pitch, x0 + w, y0 + i * pitch + h) for i, (w, h) in enumerate(sizes)]
                if all(b.inside(page) and not any(b.overlaps(o, gap_mm=0.3) for o in obstacles) for b in boxes):
                    return boxes
        return None

    def _audit(self, labels):
        """Check the drawing against the outline rules; reasons turn findings into deviations."""
        if self.plan is None:
            return {"status": "UNPLANNED", "findings": [], "deviations": [],
                    "note": "Declare rails and external nets to enable the outline audit."}
        found = []
        used = {}
        for d in self.decisions:
            for r in d["parts"]:
                used.setdefault(r, d["recipe"])
        for ref, s in self.plan["parts"].items():
            if used.get(ref) not in ALLOWED[s["role"]]:
                found.append({"rule": "recipe", "subject": ref, "detail":
                              f"proposed {s['role']} ({s['why']}), drawn with {used.get(ref)}"})
        banks = [set(d["parts"]) for d in self.decisions if d["recipe"] == "bank"]
        for ref, s in self.plan["parts"].items():
            if s["role"] == "bank" and not any(set(s["group"]) <= b for b in banks):
                found.append({"rule": "bank", "subject": ref, "detail": f"bank {s['group']} is not drawn as one bank"})
        offsets = {}
        for ref, s in self.plan["parts"].items():
            if s["role"] == "lane_series":
                a, b = self.placements[ref], self.placements[s["lane"]]
                offsets[ref] = (round(b["at"][0] - a["at"][0], 3), round(b["at"][1] - a["at"][1], 3),
                                a["rotation"], b["rotation"])
        if len(set(offsets.values())) > 1:
            found += [{"rule": "lanes", "subject": ref, "detail": "repeated lanes use different arrangements"}
                      for ref in sorted(offsets)]
        kinds = {}
        for l in labels:
            kinds.setdefault(l["net"], set()).add(l["kind"])
        powered = {n for n, _, _ in self.powers}
        for net, role in self.plan["nets"].items():
            k = kinds.get(net, set())
            if "global" in k and role != "global":
                found.append({"rule": "label", "subject": net, "detail": "global label on a net that stays on the sheet"})
            if role == "global" and "global" not in k:
                found.append({"rule": "label", "subject": net, "detail": "net leaves the sheet without a global label"})
            if net in powered and role != "power":
                found.append({"rule": "rail", "subject": net, "detail": "power symbol on an undeclared rail"})
            if role == "power" and (net not in powered or k):
                found.append({"rule": "rail", "subject": net, "detail": "rail not drawn with power symbols only"})
            if role == "name" and "local" not in k:
                found.append({"rule": "name", "subject": net, "detail": "selected local net carries no small name"})
            if role is None and "local" in k and f"label:{net}" not in self.reasons:
                found.append({"rule": "name", "subject": net, "detail": "local label on an unselected net"})
        findings = [f for f in found if f["subject"] not in self.reasons]
        deviations = [{**f, "reason": self.reasons[f["subject"]]} for f in found if f["subject"] in self.reasons]
        return {"status": "FAIL" if findings else "PASS", "findings": findings, "deviations": deviations,
                "plan": self.plan}
