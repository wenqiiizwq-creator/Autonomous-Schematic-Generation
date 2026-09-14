"""Stable-identity electrical diff and fail-closed protection of generated blocks."""

import copy
import hashlib
import json
from .generate import digest, pin_net_map
from .sexpr import parse, all_nodes, first, dump
from .scene import xy
from .geometry import Box
from .routing import segment_hits_box


def electrical_diff(before, after):
    def components(doc):
        return {c.get("stable_id", c["ref"]): c for c in doc["components"]}

    a, b = components(before), components(after)
    component_changes = [
        {"id": cid, "before": a.get(cid), "after": b.get(cid)}
        for cid in sorted(set(a) | set(b))
        if a.get(cid) != b.get(cid)
    ]
    an, bn = pin_net_map(before), pin_net_map(after)
    # Include explicit NC state so deleted NC markers are visible in the diff.
    an.update({p: "<NC>" for p in before.get("no_connect", [])})
    bn.update({p: "<NC>" for p in after.get("no_connect", [])})
    pin_changes = [
        {"pin": p, "before": an.get(p), "after": bn.get(p)}
        for p in sorted(set(an) | set(bn))
        if an.get(p) != bn.get(p)
    ]
    return {
        "status": "CHANGED" if component_changes or pin_changes else "UNCHANGED",
        "components": component_changes,
        "pins": pin_changes,
        "electrical_review": "PENDING"
        if component_changes or pin_changes
        else "UNCHANGED_INPUT_ONLY",
    }


def block_signature(intent, block):
    refs = {m["ref"] for m in block["members"]}
    return {
        "components": sorted(
            [c for c in intent["components"] if c["ref"] in refs],
            key=lambda c: c["ref"],
        ),
        "pins": {
            p: n
            for p, n in sorted(pin_net_map(intent).items())
            if p.rsplit(".", 1)[0] in refs
        },
        "no_connect": sorted(
            p for p in intent.get("no_connect", []) if p.rsplit(".", 1)[0] in refs
        ),
    }


def load_baseline(path, intent, compiled, locks):
    report = json.loads((path / "verification.json").read_text())
    if report["status"] != "AUTOMATED_PASS":
        raise ValueError("Baseline did not pass automated verification")
    old = json.loads((path / "electrical_intent.json").read_text())
    if old.get("design_id") != intent.get("design_id"):
        raise ValueError("Baseline design_id differs")
    sch = path / (intent["design_id"] + ".kicad_sch")
    sha = hashlib.sha256(sch.read_bytes()).hexdigest()
    if sha != report["native"]["schematic_sha256"]:
        raise ValueError("Baseline schematic changed since native verification")
    old_compiled = json.loads((path / "compiled.json").read_text())
    old_layout = json.loads((path / "layout_plan.json").read_text())
    old_generation = json.loads((path / "generation.json").read_text())
    if old_generation["intent_sha256"] != digest(old) or old_generation[
        "layout_sha256"
    ] != digest(old_layout):
        raise ValueError("Baseline intent/layout changed since generation")
    a = {b["id"]: b for b in old_compiled["blocks"]}
    b = {b["id"]: b for b in compiled["blocks"]}
    if set(locks) - (set(a) & set(b)):
        raise ValueError("Locked block is missing from baseline or candidate")
    for block in locks:
        if block_signature(old, a[block]) != block_signature(intent, b[block]):
            raise ValueError(f"Locked block electrical content changed: {block}")
        for member in b[block]["members"]:
            cid = member["id"]
            if (
                old_compiled["resolved_components"][cid]
                != compiled["resolved_components"][cid]
            ):
                raise ValueError(f"Locked block symbol/pin data changed: {cid}")
    return {
        "old_intent": old,
        "layout": old_layout,
        "planning": json.loads((path / "planning.json").read_text()),
        "root": parse(sch.read_text()),
        "blocks": a,
        "schematic_sha256": sha,
        "locks": list(locks),
    }


def retain_placements(layout, baseline, planning=None):
    if baseline["locks"] and layout["paper"] != baseline["layout"]["paper"]:
        raise ValueError("Locked blocks require the baseline paper size")
    for bid in baseline["locks"]:
        refs = {m["ref"] for m in baseline["blocks"][bid]["members"]}
        for key, placement in baseline["layout"]["placements"].items():
            if key.split(":")[0] in refs:
                layout["placements"][key] = copy.deepcopy(placement)
        if planning is not None:
            old_index = next(
                i
                for i, p in enumerate(baseline["planning"]["blocks"])
                if p["id"] == bid
            )
            new_index = next(
                i for i, p in enumerate(planning["blocks"]) if p["id"] == bid
            )
            planning["blocks"][new_index] = copy.deepcopy(
                baseline["planning"]["blocks"][old_index]
            )
            layout["annotations"][new_index] = copy.deepcopy(
                baseline["layout"]["annotations"][old_index]
            )


def drawing_signature(root, refs, bounds):
    box = Box(*bounds)
    selected = []
    for s in all_nodes(root, "symbol"):
        if (
            next((p[2] for p in all_nodes(s, "property") if p[1] == "Reference"), "")
            in refs
        ):
            selected.append(dump(s))
    for kind in ("wire", "junction", "no_connect", "label", "text"):
        for node in all_nodes(root, kind):
            if kind == "wire":
                pts = [
                    (float(p[1]), float(p[2]))
                    for p in all_nodes(first(node, "pts"), "xy")
                ]
                inside = segment_hits_box(*pts, box)
            else:
                inside = box.contains_point(*xy(node))
            if inside:
                # UUID remains part of the signature; unchanged geometry must
                # preserve object identity too, even when another net is added.
                selected.append(dump(node))
    return digest(sorted(selected))


def verify_locked_drawing(root, baseline):
    result = []
    plans = {b["id"]: b for b in baseline["planning"]["blocks"]}
    for bid in baseline["locks"]:
        refs = {m["ref"] for m in baseline["blocks"][bid]["members"]}
        bounds = plans[bid]["bounds"]
        old = drawing_signature(baseline["root"], refs, bounds)
        new = drawing_signature(root, refs, bounds)
        if old != new:
            raise ValueError(
                f"Locked block drawing changed (fields/wires/identity/annotations): {bid}"
            )
        result.append({"block": bid, "status": "UNCHANGED", "drawing_sha256": new})
    return result
