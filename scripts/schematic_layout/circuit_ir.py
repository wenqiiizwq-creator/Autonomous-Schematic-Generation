"""Small helpers on design netlists and symbol libraries: field checks, stacked pins, library NC pins."""

import copy
import re
from .generate import Libraries, library_dirs, pin_net_map
from .scene import physical_numbers
from .sexpr import all_nodes, value


def keys(obj, allowed, context):
    if not isinstance(obj, dict):
        raise ValueError(f"{context}: expected an object")
    unknown = set(obj) - set(allowed.split())
    if unknown:
        raise ValueError(f"{context}: unknown fields {sorted(unknown)}")


def stacked_groups(lib):
    """Physical pads one drawn pin stands for: a KiCad stacked number [17,18], or KiCad's library convention of
    one visible pin with hidden copies on the same point (TPS26630RGE OUT 17/18, Crystal_GND24 G 2/4).
    Returns [(pad, ...)] with two or more pads each, in symbol order."""
    groups = {}
    for sub in all_nodes(lib, "symbol"):
        m = re.search(r"_(\d+)_(\d+)$", str(sub[1]))
        if not m or int(m[2]) not in (0, 1):
            continue
        for p in all_nodes(sub, "pin"):
            at = next((n for n in p if isinstance(n, list) and n and str(n[0]) == "at"), None)
            key = (int(m[1]), str(at[1]), str(at[2])) if at else id(p)
            groups.setdefault(key, []).extend(n for n in physical_numbers(value(p, "number"))
                                              if n not in groups.get(key, []))
    return [tuple(g) for g in groups.values() if len(g) > 1]


def expand_stacked_pins(intent, dirs=()):
    """Write every pad of a stacked pin into the net that names one of them (calibration board 2026-11-07 #9):
    KiCad joins pads drawn on one point and its XML lists each, so the design netlist names each pad too.
    Returns (new intent, ["U1.18 -> OUT", ...]). Pads of one point in different nets, or one in a net and another
    marked no-connect, are a ValueError: the symbol and the netlist disagree."""
    result = copy.deepcopy(intent)
    nets = pin_net_map(result)
    by_name = {n["name"]: n for n in result["nets"]}
    nc = set(result.get("no_connect", []))
    libraries = Libraries(library_dirs(dirs))
    added = []
    for comp in result["components"]:
        ref = comp["ref"]
        for group in stacked_groups(libraries.load(comp["lib_id"])):
            ids = ["%s.%s" % (ref, n) for n in group]
            named = sorted({nets[i] for i in ids if i in nets})
            if len(named) > 1 or (named and any(i in nc for i in ids)):
                raise ValueError("%s are drawn on one point but the netlist puts them in %s" % (
                    "/".join(ids), ", ".join(named + (["no_connect"] if any(i in nc for i in ids) else []))))
            if not named:
                continue
            for i in ids:
                if i not in nets:
                    by_name[named[0]]["pins"].append(i)
                    nets[i] = named[0]
                    added.append("%s -> %s" % (i, named[0]))
    return result, added


def library_no_connects(intent, dirs=()):
    """Pins a library marks no_connect (TPS26630RGE NC 19-24) that the design netlist leaves out: the native writer
    wants each in ``no_connect``. Returns (new intent, added ids, connected ids); connected ones are not changed
    (KiCad ERC flags a wired no_connect pin: a datasheet that allows tying it needs a passive project pin)."""
    result = copy.deepcopy(intent)
    nets = pin_net_map(result)
    nc = result.setdefault("no_connect", [])
    libraries = Libraries(library_dirs(dirs))
    added, connected = [], []
    for comp in result["components"]:
        lib = libraries.load(comp["lib_id"])
        for sub in all_nodes(lib, "symbol"):
            for p in all_nodes(sub, "pin"):
                if str(p[1]) != "no_connect":
                    continue
                for n in physical_numbers(value(p, "number")):
                    pid = "%s.%s" % (comp["ref"], n)
                    if pid in nets:
                        connected.append(pid)
                    elif pid not in nc:
                        nc.append(pid)
                        added.append(pid)
    return result, added, connected
