"""Audit declared connector-fed supplies and native power-output markers.

The role/identity/type checks qualify declared structure only. Manufacturer
source interpretation, ratings and protection remain independent review work.
The probe mutates only marker Reference properties and instance references.
"""
import copy
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from .component_role import is_connector
from .project_audit import properties
from .sexpr import all_nodes, first, parse, value, dump

FLAG_LIB = "power:PWR_FLAG"
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
            lib_id = str(value(sym, "lib_id", ""))
            try:
                lib = resolve(lib_id)
                pins = [p for sub in all_nodes(lib, "symbol") for p in all_nodes(sub, "pin")]
                if not pins:
                    if first(lib, "power") is not None:
                        gaps.append(f"{key}: cached power symbol {lib_id} lacks pin metadata")
                    # Non-power pinless symbols are outside this gate.
                    continue
                if first(lib, "power") is not None and any(str(p[1]) == "power_out" for p in pins):
                    markers.setdefault(key, []).append(sym)
                    if not _refs(sym):
                        gaps.append(f"{key}: power-output marker has no reference")
            except ValueError as exc:
                gaps.append(str(exc))
    return trees, markers, gaps, used


def flag_references(sheets):
    """Marker refs are determined by cached native power/power_out, not namespace."""
    _, markers, _, _ = _scan(sheets)
    return {p: set().union(*(_refs(s) for s in symbols)) for p, symbols in markers.items()}


def renamed_copy(root, sheets, workdir):
    root, workdir = Path(root).resolve(), Path(workdir)
    base = root.parent
    trees, markers, gaps, used = _scan(sheets)
    if gaps:
        raise ValueError("; ".join(gaps))
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
    c, x = expected[0], actual[0]
    libs = x.findall("libsource")
    fields = [(f.get("name"), f.text or "") for f in x.findall("fields/field")]
    if len(libs) != 1 or len(fields) != len(dict(fields)):
        return "INSUFFICIENT", "ambiguous native component metadata"
    lib = libs[0]; native_fields = dict(fields)
    observed = {"lib_id": f"{lib.get('lib')}:{lib.get('part')}", "value": x.findtext("value") or "",
                "footprint": x.findtext("footprint") or "", "datasheet": x.findtext("datasheet") or "",
                "mpn": native_fields.get("MPN") or x.findtext("value") or "",
                "dnp": x.find("property[@name='dnp']") is not None}
    if any(observed[k] != c.get(k, False if k == "dnp" else c.get("value", "") if k == "mpn" else "") for k in observed):
        return "FAIL", "exact intent/native identity mismatch"
    if not is_connector(c) or not is_connector({"lib_id": observed["lib_id"], "fields": native_fields}):
        return "FAIL", "origin lacks an explicit connector role"
    if c.get("fields", {}).get("ComponentRole") != native_fields.get("ComponentRole"):
        return "FAIL", "intent/native ComponentRole mismatch"
    parts = [p for p in root.findall("libparts/libpart") if p.get("lib") == lib.get("lib") and p.get("part") == lib.get("part")]
    if len(parts) != 1 or not parts[0].findall("pins/pin"):
        return "INSUFFICIENT", "complete connector library pin metadata unavailable"
    pins = parts[0].findall("pins/pin")
    numbers = [p.get("num") for p in pins]
    if any(not n for n in numbers) or len(set(numbers)) != len(numbers) or number not in numbers:
        return "INSUFFICIENT", "missing/duplicate connector contact definition"
    if any(p.get("type") != "passive" for p in pins) or observed["dnp"]:
        return "FAIL", "connector must be fitted and every contact must be passive"
    nodes = root.findall(f"nets/net/node[@ref='{ref}'][@pin='{number}']")
    if len(nodes) != 1 or nodes[0].get("pintype") != "passive":
        return "FAIL", "declared physical contact must have exact passive native type"
    return "PASS", "explicit role, exact identity and native passive contacts; mechanical semantics require source review"


def judge(xml_path, intent, aliases):
    decls, errors = declarations(intent)
    root = ET.parse(xml_path).getroot()
    gaps, origins = [], []
    nets = [{"name": n.get("name"), "nodes": [(p.get("ref"), p.get("pin"), p.get("pintype", "")) for p in n.findall("node")]}
            for n in root.findall("nets/net")]
    by_pin = {f"{r}.{p}": net for net in nets for r, p, _ in net["nodes"]}
    flags = [(aliases[r], net) for net in nets for r, _, _ in net["nodes"] if r in aliases]
    for alias, ref in aliases.items():
        count = sum(r == alias for net in nets for r, _, _ in net["nodes"])
        if count != 1:
            errors.append({"kind": "marker_native_coverage", "flag": ref, "nodes": count})
    for flag, net in flags:
        pins = {f"{r}.{p}" for r, p, _ in net["nodes"]}
        owners = [d for d in decls if d["pin"] in pins]
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
    status = "FAIL" if errors else "INSUFFICIENT" if gaps else "PASS" if decls or flags else "NOT_APPLICABLE"
    return {"status": status, "scope": "Declared connector structure and native markers only; source semantics, supply ratings and protection require review.",
            "declarations": decls, "flags": sorted(f for f, _ in flags), "origins": origins, "errors": errors, "coverage_gaps": gaps}


def audit_external_supply(root, sheets, intent, xml_path, cli, workdir):
    _, markers, gaps, _ = _scan(sheets)
    if gaps:
        return {"status": "INSUFFICIENT", "coverage_gaps": gaps}
    if not markers:
        return judge(xml_path, intent, {})
    copy_root, aliases = renamed_copy(root, sheets, workdir)
    probe = Path(workdir) / "external-supply-netlist.xml"
    r = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(probe), str(copy_root)], capture_output=True, text=True, timeout=300)
    if r.returncode or not probe.is_file():
        return {"status": "INSUFFICIENT", "reason": "marker-renamed native export failed", "stderr": r.stderr[-2000:]}
    return judge(probe, intent, aliases)
