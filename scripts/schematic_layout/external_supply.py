"""Audit declared connector-fed supplies and native power-output markers.

The role/identity/type checks qualify declared structure only. Manufacturer
source interpretation, ratings and protection remain independent review work.
The probe mutates only marker Reference properties and instance references.
"""
import copy
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

from .component_role import is_connector
from . import circuit_supply
from .project_audit import properties
from .sexpr import all_nodes, first, parse, value, dump

ALIAS = "FLGX"


def declarations(intent):
    decls = intent.get("external_supply", [])
    if not isinstance(decls, list):
        raise ValueError("external_supply must be a list")
    nets = {n["name"]: set(n["pins"]) for n in intent.get("nets", [])}
    errors, seen = [], set()
    for d in decls:
        if (not isinstance(d, dict) or set(d) != {"net", "pin", "reason"}
                or not all(isinstance(d[k], str) and d[k].strip() for k in d)
                or not all(d["pin"].rsplit(".", 1)) or "." not in d["pin"]):
            raise ValueError("external_supply entries need nonempty net, REF.PIN pin and reason")
        if d["net"] in seen:
            raise ValueError(f"external_supply declares {d['net']} twice")
        seen.add(d["net"])
        if d["pin"] not in nets.get(d["net"], ()):
            errors.append({"kind": "declaration_not_in_intent", "net": d["net"], "pin": d["pin"]})
    return decls, errors



# Exact KiCad Device symbols only: Device:LED*, Device:Lamp and Device:R_Photo share prefixes.
SERIES_LIB = re.compile(r"^Device:(R|R_Small|R_US|R_Small_US|L|L_Small|L_Core_\w+|L_Iron\w*"
                        r"|FerriteBead|FerriteBead_Small|Fuse|Fuse_Small|Polyfuse|Polyfuse_Small)$")
SERIES_ROLES = {"series_resistor", "inductor", "ferrite_bead", "fuse"}  # MPN-named libraries only


def filtered_declarations(intent):
    """Supplies derived from a driven rail through one declared series passive.

    ``{"net", "from", "via", "reason"}``: the declared net is fed from ``from``
    only through the two-terminal part ``via`` (resistor, inductor, ferrite
    bead or fuse), e.g. an RC-filtered analog supply pin.
    """
    decls = intent.get("filtered_supply", [])
    if not isinstance(decls, list):
        raise ValueError("filtered_supply must be a list")
    nets = {n["name"]: set(n["pins"]) for n in intent.get("nets", [])}
    errors, seen = [], set()
    for d in decls:
        if (not isinstance(d, dict) or set(d) != {"net", "from", "via", "reason"}
                or not all(isinstance(d[k], str) and d[k].strip() for k in d)):
            raise ValueError("filtered_supply entries need nonempty net, from, via and reason")
        if d["net"] in seen:
            raise ValueError(f"filtered_supply declares {d['net']} twice")
        seen.add(d["net"])
        via = [p for pins in nets.values() for p in pins if p.rsplit(".", 1)[0] == d["via"]]
        if (len(via) != 2 or len(nets.get(d["net"], set()) & set(via)) != 1
                or len(nets.get(d["from"], set()) & set(via)) != 1):
            errors.append({"kind": "filtered_via_not_in_intent", "net": d["net"], "from": d["from"], "via": d["via"]})
    return decls, errors

def _refs(sym):
    found = {properties(sym).get("Reference", "")}
    found |= {str(value(p, "reference", "")) for inst in all_nodes(sym, "instances")
              for proj in all_nodes(inst, "project") for p in all_nodes(proj, "path")}
    return found - {""}


def _scan(sheets):
    trees, markers, gaps, used = {}, {}, [], set()
    for sheet in sheets:
        key = str(Path(sheet).resolve())
        tree = parse(Path(sheet).read_text(encoding="utf-8")); trees[key] = tree
        caches = all_nodes(tree, "lib_symbols")
        cache = {}
        for c in caches:
            for lib in all_nodes(c, "symbol"):
                cache.setdefault(str(lib[1]), []).append(lib)

        def resolve(name, seen=()):
            matches = cache.get(name, [])
            if len(matches) != 1 or name in seen:
                raise ValueError(f"{key}: missing/duplicate/cyclic cached symbol {name}")
            lib = matches[0]
            parent = value(lib, "extends")
            if parent:
                # Resolve cached inheritance only; never borrow mutable installed libraries.
                base = resolve(str(parent), (*seen, name))
                if all_nodes(lib, "symbol"):
                    raise ValueError(f"{key}: unsupported inherited pin override {name}")
                lib = copy.deepcopy(lib)
                for node in base[2:]:
                    if node[0] in ("symbol", "power") and not all_nodes(lib, str(node[0])):
                        lib.extend(copy.deepcopy(all_nodes(base, str(node[0]))))
            return lib

        for sym in all_nodes(tree, "symbol"):
            used.update(_refs(sym))
            # The cache is keyed by lib_name when the placed symbol has one, as project_audit reads it.
            lib_id = str(value(sym, "lib_name", value(sym, "lib_id", "")))
            try:
                lib = resolve(lib_id)
                if first(lib, "power") is None:
                    continue
                # A cached output in an unused unit/style cannot qualify this
                # placed symbol. Common definitions apply to the current unit.
                if any(len(all_nodes(sym, field)) > 1 for field in ("unit", "body_style", "convert")):
                    raise ValueError(f"{key}: ambiguous placed unit/style for {lib_id}")
                if (first(sym, "body_style") is not None and first(sym, "convert") is not None
                        and value(sym, "body_style") != value(sym, "convert")):
                    raise ValueError(f"{key}: conflicting placed body_style/convert for {lib_id}")
                unit = int(value(sym, "unit", 1))
                style = int(value(sym, "body_style", value(sym, "convert", 1)))
                if unit < 1 or style < 1:
                    raise ValueError(f"{key}: invalid placed unit/style for {lib_id}")
                active, definitions = [], set()
                for sub in all_nodes(lib, "symbol"):
                    match = re.search(r"_(\d+)_(\d+)$", str(sub[1]))
                    if not match:
                        raise ValueError(f"{key}: unknown cached unit/style for {lib_id}")
                    pair = (int(match[1]), int(match[2]))
                    if pair in definitions:
                        raise ValueError(f"{key}: duplicate cached unit/style for {lib_id}")
                    definitions.add(pair)
                    if pair[0] in (0, unit) and pair[1] in (0, style):
                        active.append(sub)
                pins = [p for sub in active for p in all_nodes(sub, "pin")]
                if not pins:
                    gaps.append(f"{key}: cached power symbol {lib_id} lacks active pin metadata")
                    continue
                if any(str(p[1]) == "power_out" for p in pins):
                    markers.setdefault(key, []).append(sym)
                    if not _refs(sym):
                        gaps.append(f"{key}: power-output marker has no reference")
            except (ValueError, TypeError) as exc:
                gaps.append(str(exc))
    return trees, markers, gaps, used


def flag_references(sheets):
    """Marker refs are determined by cached native power/power_out, not namespace."""
    _, markers, _, _ = _scan(sheets)
    return {p: set().union(*(_refs(s) for s in symbols)) for p, symbols in markers.items()}


def renamed_copy(root, sheets, workdir):
    root, workdir = Path(root).resolve(), Path(workdir)
    base = root.parent
    trees, markers, _, used = _scan(sheets)
    aliases, counter = {}, 1
    for ref in sorted(set().union(*(_refs(s) for syms in markers.values() for s in syms)) if markers else ()):
        while f"{ALIAS}{counter}" in used:
            counter += 1
        aliases[ref] = f"{ALIAS}{counter}"; used.add(aliases[ref]); counter += 1
    for key, tree in trees.items():
        for sym in markers.get(key, []):
            for prop in all_nodes(sym, "property"):
                if len(prop) > 2 and prop[1] == "Reference" and str(prop[2]) in aliases:
                    prop[2] = aliases[str(prop[2])]
            for inst in all_nodes(sym, "instances"):
                for proj in all_nodes(inst, "project"):
                    for path in all_nodes(proj, "path"):
                        for node in all_nodes(path, "reference"):
                            if str(node[1]) in aliases:
                                node[1] = aliases[str(node[1])]
        target = workdir / Path(key).relative_to(base)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dump(tree) + "\n", encoding="utf-8")
    for name in (root.stem + ".kicad_pro", "sym-lib-table"):
        if (base / name).is_file():
            shutil.copy2(base / name, workdir / name)
    return workdir / root.name, {alias: ref for ref, alias in aliases.items()}


def _origin(root, intent, pin):
    ref, number = pin.rsplit(".", 1)
    components = intent.get("components", [])
    if isinstance(components, dict):
        components = [{"ref": r, **c} for r, c in components.items()]
    expected = [c for c in components if c.get("ref") == ref]
    actual = root.findall(f"components/comp[@ref='{ref}']")
    if len(expected) != 1 or len(actual) != 1:
        return "FAIL", "origin needs one intent and one native component"
    # Identity against the intent is the intent_netlist gate's; this checks the connector contact itself.
    c, x = expected[0], actual[0]
    lib = x.find("libsource")
    if lib is None:
        return "INSUFFICIENT", "native component has no library source"
    native_fields = {f.get("name"): f.text or "" for f in x.findall("fields/field")}
    if not is_connector(c) or not is_connector({"lib_id": f"{lib.get('lib')}:{lib.get('part')}", "fields": native_fields}):
        return "FAIL", "origin lacks an explicit connector role"
    parts = [p for p in root.findall("libparts/libpart") if p.get("lib") == lib.get("lib") and p.get("part") == lib.get("part")]
    if len(parts) != 1 or not parts[0].findall("pins/pin"):
        return "INSUFFICIENT", "complete connector library pin metadata unavailable"
    pins = parts[0].findall("pins/pin")
    numbers = [p.get("num") for p in pins]
    if any(not n for n in numbers) or len(set(numbers)) != len(numbers) or number not in numbers:
        return "INSUFFICIENT", "missing/duplicate connector contact definition"
    if x.find("property[@name='dnp']") is not None:
        return "FAIL", "connector must be fitted"
    nodes = root.findall(f"nets/net/node[@ref='{ref}'][@pin='{number}']")
    if len(nodes) != 1 or nodes[0].get("pintype") != "passive":
        return "FAIL", "declared physical contact must have exact passive native type"
    return "PASS", "explicit connector role and native passive contact; mechanical semantics require source review"


def _via(root, intent, ref):
    """A fitted two-pin passive series part whose intent role is a resistor, inductor, bead or fuse."""
    components = intent.get("components", [])
    if isinstance(components, dict):
        components = [{"ref": r, **c} for r, c in components.items()]
    expected = [c for c in components if c.get("ref") == ref]
    actual = root.findall(f"components/comp[@ref='{ref}']")
    if len(expected) != 1 or len(actual) != 1:
        return "FAIL", "via needs one intent and one native component"
    c, comp = expected[0], actual[0]
    role, lib_id = c.get("fields", {}).get("ComponentRole"), str(c.get("lib_id", ""))
    if not (SERIES_LIB.match(lib_id) or (not lib_id.startswith("Device:") and role in SERIES_ROLES)):
        return "FAIL", ("via must be a series resistor, inductor, ferrite bead or fuse: a Device:R/L/FerriteBead/Fuse/"
                        "Polyfuse symbol, or an MPN-named library part with fields.ComponentRole "
                        + "/".join(sorted(SERIES_ROLES)))
    lib = comp.find("libsource")
    if comp.find("property[@name='dnp']") is not None or c.get("dnp", False):
        return "FAIL", "via must be fitted"
    parts = [p for p in root.findall("libparts/libpart") if lib is not None
             and p.get("lib") == lib.get("lib") and p.get("part") == lib.get("part")]
    if len(parts) != 1:
        return "INSUFFICIENT", "via library pin metadata unavailable"
    pins = parts[0].findall("pins/pin")
    if len(pins) != 2 or any(p.get("type") != "passive" for p in pins):
        return "FAIL", "via must have exactly two passive pins"
    numbers = [p.get("num") for p in pins]
    if any(not n for n in numbers) or len(set(numbers)) != 2:
        return "INSUFFICIENT", "via library pin numbers are missing or ambiguous"
    nodes = root.findall(f"nets/net/node[@ref='{ref}']")
    actual_numbers = [p.get("pin") for p in nodes]
    if len(nodes) != 2 or set(actual_numbers) != set(numbers):
        return "FAIL", "via needs exactly one native node for each physical pin"
    if any(not p.get("pintype") for p in nodes):
        return "INSUFFICIENT", "via actual native pin type unavailable"
    if any(p.get("pintype") != "passive" for p in nodes):
        return "FAIL", "via actual native pins must both be passive"
    return "PASS", "fitted two-pin passive series part with matching identity"


def judge(xml_path, intent, aliases, artifact_root=None):
    decls, errors = declarations(intent)
    filtered, filtered_errors = filtered_declarations(intent)
    errors += filtered_errors
    reviewed, review_errors = circuit_supply.declarations(intent)
    errors += review_errors
    root = ET.parse(xml_path).getroot()
    gaps, origins = [], []
    nets = [{"name": n.get("name"), "nodes": [(p.get("ref"), p.get("pin"), p.get("pintype", "")) for p in n.findall("node")]}
            for n in root.findall("nets/net")]
    by_pin = {f"{r}.{p}": net for net in nets for r, p, _ in net["nodes"]}
    flags = [(aliases[r], net) for net in nets for r, _, _ in net["nodes"] if r in aliases]
    for alias, ref in aliases.items():
        marker_nodes = [t for net in nets for r, _, t in net["nodes"] if r == alias]
        count = len(marker_nodes)
        if count != 1:
            errors.append({"kind": "marker_native_coverage", "flag": ref, "nodes": count})
        elif not marker_nodes[0]:
            gaps.append({"kind": "marker_native_type", "flag": ref, "reason": "native pin type unavailable"})
        elif marker_nodes[0] != "power_out":
            errors.append({"kind": "marker_native_type", "flag": ref, "actual": marker_nodes[0]})
        elif any(not p.get("pin") for p in root.findall(f"nets/net/node[@ref='{alias}']")):
            gaps.append({"kind": "marker_native_coverage", "flag": ref, "reason": "native pin number unavailable"})
    intent_pins = {n["name"]: set(n["pins"]) for n in intent.get("nets", [])}
    derived = {}  # declared net name -> native net on the declared side of the via
    for d in filtered:
        side = sorted(intent_pins.get(d["net"], set()) & {p for p in by_pin if p.rsplit(".", 1)[0] == d["via"]})
        if len(side) == 1:
            derived[d["net"]] = by_pin[side[0]]
    for flag, net in flags:
        pins = {f"{r}.{p}" for r, p, _ in net["nodes"]}
        owners = [d for d in decls if d["pin"] in pins] + [d for d in filtered if derived.get(d["net"]) is net] + [d for d in reviewed if by_pin.get(d["pin"]) is net]
        if len(owners) != 1:
            errors.append({"kind": "undeclared_pwr_flag" if not owners else "ambiguous_pwr_flag",
                           "flag": flag, "net": net["name"], "declarations": [d["net"] for d in owners]})
    for d in decls:
        origin_status, reason = _origin(root, intent, d["pin"])
        origins.append({"pin": d["pin"], "status": origin_status, "reason": reason})
        if origin_status != "PASS":
            (errors if origin_status == "FAIL" else gaps).append({"kind": "connector_origin", "pin": d["pin"], "reason": reason})
        net = by_pin.get(d["pin"])
        if net is None:
            errors.append({"kind": "declared_pin_missing", "net": d["net"], "pin": d["pin"]}); continue
        count = sum(n is net for _, n in flags)
        if count != 1:
            errors.append({"kind": "missing_pwr_flag" if not count else "duplicate_pwr_flag", "net": d["net"], "pin": d["pin"], "flags": count})
        sources = sorted(f"{r}.{p}" for r, p, t in net["nodes"] if r not in aliases and t.split("+", 1)[0] == "power_out")
        if sources:
            errors.append({"kind": "net_has_power_source", "net": d["net"], "sources": sources})
    errors += circuit_supply.judge(root, intent, reviewed, by_pin, flags, aliases, artifact_root or Path(xml_path).parent)
    unfitted = {c.get("ref") for c in root.findall("components/comp") if c.find("property[@name='dnp']") is not None}

    def has_source(net):
        return any(r not in aliases and r not in unfitted and t.split("+", 1)[0] == "power_out"
                   for r, _, t in net["nodes"])

    roles = intent.get("net_roles", {})
    unchecked = []

    sheets = {s.get("name", "") for s in root.findall("design/sheet")} | {"/"}

    def named(native, wanted):
        """Native name equals the declared name, allowing only a listed sheet-path prefix."""
        return native == wanted or (not wanted.startswith("/") and any(native == p + wanted for p in sheets))

    far = {}
    for d in filtered:
        net = derived.get(d["net"])
        ends = [by_pin[p] for p in by_pin if p.rsplit(".", 1)[0] == d["via"] and by_pin[p] is not net]
        if net is not None and len(ends) == 1:
            far[d["net"]] = ends[0]
    # Qualify by native net objects: board-driven or connector-fed, then through qualified vias.
    qualified = {id(n) for n in nets if has_source(n)} | {id(by_pin[d["pin"]]) for d in decls + reviewed if d["pin"] in by_pin}
    pending = [d for d in filtered if d["net"] in derived and d["net"] in far]
    while True:
        done = [d for d in pending if id(far[d["net"]]) in qualified]
        if not done:
            break
        qualified.update(id(derived[d["net"]]) for d in done)
        pending = [d for d in pending if d not in done]
    for d in filtered:
        via_status, reason = _via(root, intent, d["via"])
        if via_status != "PASS":
            (errors if via_status == "FAIL" else gaps).append({"kind": "filtered_via", "net": d["net"], "via": d["via"], "reason": reason})
        net = derived.get(d["net"])
        if net is None:
            errors.append({"kind": "declared_pin_missing", "net": d["net"], "via": d["via"]}); continue
        if not named(net["name"], d["net"]):
            errors.append({"kind": "filtered_net_name_mismatch", "net": d["net"], "actual": net["name"]})
        if d["net"] not in far or not named(far[d["net"]]["name"], d["from"]):
            errors.append({"kind": "filtered_via_not_between_nets", "net": d["net"], "from": d["from"], "via": d["via"]})
        elif d in pending:
            errors.append({"kind": "filtered_source_not_driven", "net": d["net"], "from": d["from"]})
        if not any(r not in aliases and t.split("+", 1)[0] == "power_in" for r, _, t in net["nodes"]):
            errors.append({"kind": "filtered_net_without_power_input", "net": d["net"]})
        # A filtered net and its source are both power or both return, as the intent declares them.
        ends = (roles.get(d["net"]), roles.get(d["from"]))
        if not all(r in ("power", "return") for r in ends):
            unchecked.append({"net": d["net"], "from": d["from"], "reason": "未核对：缺 net_roles"})
        elif ends[0] != ends[1]:
            errors.append({"kind": "filtered_return_from_supply", "net": d["net"], "from": d["from"]})
        count = sum(n is net for _, n in flags)
        if count != 1:
            errors.append({"kind": "missing_pwr_flag" if not count else "duplicate_pwr_flag", "net": d["net"], "via": d["via"], "flags": count})
        if has_source(net):
            errors.append({"kind": "net_has_power_source", "net": d["net"]})
    status = ("FAIL" if errors else "INSUFFICIENT" if gaps
              else "PASS" if decls or filtered or reviewed or flags else "NOT_APPLICABLE")
    return {"status": status, "scope": ("Declared connector, filtered and manually reviewed discrete-circuit supply structure, evidence freshness and native markers only; source semantics, filter values, "
                      "series drop at the pin's maximum current, supply ratings and protection require review."),
            "reviewed_circuit_declarations": reviewed, "declarations": decls, "filtered_declarations": filtered, "flags": sorted(f for f, _ in flags), "origins": origins, "errors": errors, "coverage_gaps": gaps,
            "return_class_unchecked": unchecked}


def audit_external_supply(root, sheets, intent, xml_path, cli, workdir, artifact_root=None):
    base = artifact_root or Path(root).parent
    _, markers, gaps, _ = _scan(sheets)
    if gaps:
        return {"status": "INSUFFICIENT", "coverage_gaps": gaps}
    if not markers:
        return judge(xml_path, intent, {}, base)
    copy_root, aliases = renamed_copy(root, sheets, workdir)
    probe = Path(workdir) / "external-supply-netlist.xml"
    r = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(probe), str(copy_root)], capture_output=True, text=True, timeout=300)
    if r.returncode or not probe.is_file():
        return {"status": "INSUFFICIENT", "reason": "marker-renamed native export failed", "stderr": r.stderr[-2000:]}
    return judge(probe, intent, aliases, base)
