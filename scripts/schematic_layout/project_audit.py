"""Read-only hierarchy, cached-symbol and delivery checks for native projects.

This does not infer electrical connectivity, qualify a design, or edit files.
Instances of a shared child file count separately. Paths escaping the delivery
root are rejected; unresolved variables and annotation context remain gaps.
"""

import hashlib
from pathlib import Path
import re
import shutil
import subprocess

from .sexpr import all_nodes, first, value, dump
from .native_hierarchy import NativeHierarchy
from .design_change import _identity, native_inventory


def properties(node):
    return {str(p[1]): str(p[2]) for p in all_nodes(node, "property")}


def symbol_pin_signature(lib):
    """Physical identity independent of artwork and library name, with units."""
    result = []
    if first(lib, "extends"):
        raise ValueError("Unresolved symbol inheritance")
    for sub in all_nodes(lib, "symbol"):
        match = re.search(r"_(\d+)_(\d+)$", str(sub[1]))
        if not match:
            raise ValueError("Unrecognized symbol unit")
        for pin in all_nodes(sub, "pin"):
            if len(pin) < 3 or value(pin, "number") is None or value(pin, "name") is None:
                raise ValueError("Incomplete physical pin definition")
            result.append((int(match[1]), int(match[2]), str(value(pin, "number")),
                           str(value(pin, "name")), str(pin[1]), str(pin[2]),
                           "hide" in pin or value(pin, "hide") == "yes"))
    return sorted(result)


def source_flags(symbol):
    return {key: str(value(symbol, key, "unspecified")) for key in
            ("exclude_from_sim", "in_bom", "on_board", "dnp")}


def _descendants(node):
    for child in node:
        if isinstance(child, list):
            yield child
            yield from _descendants(child)


def validate_pinless_roles(context, contract):
    """Validate externally reviewed roles against exact native source identity.

    A role asserts mechanical/documentation intent; the cache proves absence
    of pins in *every* unit/style. Neither statement is a BOM qualification.
    Missing selected annotation or unresolved inheritance is a coverage gap.
    """
    keys = {"schema_version", "project", "file_sha256", "native_xml_sha256", "objects"}
    fields = {"reference", "instance", "symbol_uuid", "lib_id", "lib_sha256",
              "source_properties", "source_flags", "role", "native_identity"}
    if (not isinstance(contract, dict) or set(contract) != keys or contract["schema_version"] != 1 or
            not isinstance(contract["objects"], list) or not isinstance(contract["native_xml_sha256"], str) or
            not re.fullmatch(r"[0-9a-f]{64}", contract["native_xml_sha256"])):
        raise ValueError("Invalid pinless source-role contract schema")
    errors, objects = [], []
    if context.errors:
        errors.append("Source native hierarchy has structural/annotation errors")
    if contract["project"] != context.project or contract["file_sha256"] != context.file_sha256:
        errors.append("Source-role project or native file SHA256 binding mismatch")
    seen, seen_refs = set(), set()
    for item in contract["objects"]:
        if (not isinstance(item, dict) or set(item) != fields or
                item["role"] not in ("mechanical", "documentation") or
                any(not isinstance(item[k], str) or not item[k] for k in
                    ("reference", "instance", "symbol_uuid", "lib_id", "lib_sha256")) or
                not re.fullmatch(r"[0-9a-f]{64}", item["lib_sha256"]) or
                not isinstance(item["source_properties"], dict) or not isinstance(item["source_flags"], dict)):
            raise ValueError("Invalid pinless source-role object")
        _identity(item["native_identity"])
        key = (item["instance"], item["symbol_uuid"])
        if key in seen or item["reference"] in seen_refs or item["reference"].startswith("#"):
            errors.append("Duplicate or virtual source-role object")
        seen.add(key)
        seen_refs.add(item["reference"])
        matches = [(p, s) for p in context.pages if p["instance"] == item["instance"]
                   for s in all_nodes(context.tree_for(p), "symbol") if value(s, "uuid") == item["symbol_uuid"]]
        row = {**item, "status": "INSUFFICIENT", "reason": "Source object or selected annotation unavailable"}
        objects.append(row)
        if len(matches) != 1:
            errors.append(f"Source-role object identity absent/ambiguous: {item['reference']}")
            continue
        page, sym = matches[0]
        ctx = context.symbol_context(page, sym)
        if ctx is None:
            continue  # No Reference-property or other-project fallback.
        lid = str(value(sym, "lib_name", value(sym, "lib_id", "")))
        propnodes = all_nodes(sym, "property")
        if (ctx["reference"] != item["reference"] or lid != item["lib_id"] or
                properties(sym) != item["source_properties"] or len(properties(sym)) != len(propnodes) or
                source_flags(sym) != item["source_flags"] or
                any(len(all_nodes(sym, key)) > 1 for key in source_flags(sym))):
            errors.append(f"Source-role native identity/properties mismatch: {item['reference']}")
            continue
        identity, props = item["native_identity"], properties(sym)
        # KiCad exports an exact '~' as empty in named fields, but preserves
        # Reference/Value literally. Only these standard fields have native
        # empty defaults; an absent custom field is never an empty assertion.
        exported_props = {k: ("" if v == "~" and k not in ("Reference", "Value") else v)
                          for k, v in props.items()}
        for standard in ("Footprint", "Datasheet", "Description"):
            exported_props.setdefault(standard, "")
        if (any(identity[k] != exported_props.get(p, "") for k, p in
                (("value", "Value"), ("footprint", "Footprint"), ("datasheet", "Datasheet"))) or
                identity["lib_id"] != lid or identity["dnp"] != (value(sym, "dnp", "no") == "yes") or
                any(exported_props.get(k) != v for k, v in identity["fields"].items())):
            errors.append(f"Source-role export identity contradicts source: {item['reference']}")
            continue
        libs = [l for l in all_nodes(first(context.tree_for(page), "lib_symbols", []), "symbol") if str(l[1]) == lid]
        if len(libs) != 1:
            row["reason"] = "Missing/ambiguous cached symbol"
            continue
        lib = libs[0]
        if hashlib.sha256(dump(lib).encode()).hexdigest() != item["lib_sha256"]:
            errors.append(f"Source-role cached symbol SHA256 mismatch: {item['reference']}")
            continue
        try:
            if any(n[0] == "extends" for n in _descendants(lib)):
                raise ValueError("Unresolved symbol inheritance")
            signature = symbol_pin_signature(lib)
            if not all_nodes(lib, "symbol"):
                raise ValueError("No resolved cache unit definitions")
            style = int(value(sym, "body_style", value(sym, "convert", 1)))
            units = [tuple(map(int, re.search(r"_(\d+)_(\d+)$", str(sub[1])).groups()))
                     for sub in all_nodes(lib, "symbol")]
            if len(units) != len(set(units)):
                raise ValueError("Ambiguous cached unit/style definitions")
            if (ctx["unit"] != int(value(sym, "unit", 1)) or
                    not any(u in (0, ctx["unit"]) and s in (0, style) for u, s in units)):
                errors.append(f"Source-role active unit/style is not defined: {item['reference']}")
                continue
            if signature or any(n[0] == "pin" for n in _descendants(lib)):
                errors.append(f"Source-role object has cached physical pins: {item['reference']}")
                continue
        except ValueError as exc:
            row["reason"] = str(exc)
            continue
        row.update(status="NA", reason="Externally reviewed role; all resolved cached units/styles are pinless")
    return {"status": "FAIL" if errors else "INSUFFICIENT" if any(r["status"] != "NA" for r in objects) else "PASS",
            "errors": errors, "objects": objects}


def _instance(node, project, path):
    matches = [p for pr in all_nodes(first(node, "instances", []), "project")
               if pr[1] == project for p in all_nodes(pr, "path") if p[1] == path]
    if len(matches) > 1:
        raise ValueError("Duplicate annotation context")
    return matches[0] if matches else None


def pdf_page_count(path):
    cli = shutil.which("pdfinfo")
    if not cli:
        raise RuntimeError("pdfinfo is required to check the actual PDF page count")
    result = subprocess.run([cli, str(Path(path).resolve())], capture_output=True,
                            text=True, timeout=30)
    if result.returncode:
        raise ValueError("pdfinfo could not read the PDF")
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        raise ValueError("pdfinfo returned no page count")
    return int(match[1])


def audit_project(root, pdf=None, project=None, expected_pages=None, *, context=None, source_roles=None, netlist=None):
    root = Path(root).resolve()
    context = context or NativeHierarchy(root, project)
    project = context.project
    pages = context.pages
    errors, gaps = list(context.errors), list(context.coverage_gaps)
    roles = validate_pinless_roles(context, source_roles) if source_roles is not None else None
    role_objects = {(r["instance"], r["symbol_uuid"]): r for r in roles["objects"]} if roles else {}
    if roles:
        errors.extend({"kind": "invalid_source_role_evidence", "reason": e} for e in roles["errors"])
        gaps.extend(r["reason"] for r in roles["objects"] if r["status"] != "NA")
    pinless_objects = []
    caches, definitions, refs = {}, {}, {}
    file_hashes = context.file_sha256
    for page in pages:
        relative = page["path"]
        tree = context.tree_for(page)
        libs = {str(n[1]): n for n in all_nodes(first(tree, "lib_symbols", []), "symbol")}
        for symbol in all_nodes(tree, "symbol"):
            ctx = context.symbol_context(page, symbol)
            if ctx is None:
                continue
            ref, unit = ctx["reference"], ctx["unit"]
            if not ref.startswith("#"):
                if (ref, unit) in refs:
                    errors.append({"kind": "duplicate_reference_unit", "ref": ref, "unit": unit})
                refs[(ref, unit)] = relative
            lid = str(value(symbol, "lib_name", value(symbol, "lib_id", "")))
            lib = libs.get(lid)
            if lib is None:
                errors.append({"kind": "missing_cached_symbol", "path": relative, "lib_id": lid})
                continue
            digest = hashlib.sha256(dump(lib).encode()).hexdigest()
            if lid in caches and caches[lid] != digest:
                errors.append({"kind": "cached_library_conflict", "path": relative, "lib_id": lid})
            caches[lid] = digest
            try:
                signature = symbol_pin_signature(lib)
            except ValueError as exc:
                gaps.append(f"{relative}: {lid}: {exc}")
                continue
            style = int(value(symbol, "body_style", value(symbol, "convert", 1)))
            if not any(p[0] in (0, unit) and p[1] in (0, style) for p in signature):
                role = role_objects.get((page["instance"], str(value(symbol, "uuid", ""))))
                if not signature and role and role["status"] == "NA":
                    pinless_objects.append({"reference": ref, "instance": page["instance"],
                                            "symbol_uuid": role["symbol_uuid"], "role": role["role"],
                                            "pin_integrity": "NA", "reason": role["reason"]})
                elif not signature and role and role["status"] == "INSUFFICIENT":
                    gaps.append(f"{ref}: {role['reason']}")
                else:
                    errors.append({"kind": "missing_active_unit_pins", "ref": ref, "unit": unit, "style": style})
            if unit != int(value(symbol, "unit", 1)):
                errors.append({"kind": "instance_unit_mismatch", "ref": ref, "unit": unit})
            if ref in definitions and definitions[ref] != signature:
                errors.append({"kind": "multiunit_pin_definition_conflict", "ref": ref})
            definitions[ref] = signature
    numbers = [p["page"] for p in pages if p["page"] is not None]
    if len(numbers) != len(set(numbers)):
        errors.append({"kind": "duplicate_page_number"})
    # Nonconsecutive page identifiers are legal. Count instances, not max(page).
    if expected_pages is not None and len(pages) != expected_pages:
        errors.append({"kind": "unexpected_page_count", "expected": expected_pages, "actual": len(pages)})
    pdf_result = None
    if pdf is not None:
        try:
            count = pdf_page_count(pdf)
            pdf_result = {"name": Path(pdf).name, "pages": count,
                          "sha256": hashlib.sha256(Path(pdf).read_bytes()).hexdigest()}
            if count != len(pages):
                errors.append({"kind": "pdf_page_count_mismatch", "expected": len(pages), "actual": count})
        except (RuntimeError, ValueError, OSError, subprocess.SubprocessError) as exc:
            gaps.append(str(exc))
    inventory = native_inventory(netlist) if netlist is not None else None
    selected_refs = {r for r, _ in refs if not r.startswith("#")}
    reconciliation = None
    if inventory:
        reconciliation = {"qualification": "NOT_EVALUATED", "selected_project": project,
                          "selected_context_physical_reference_count": len(selected_refs),
                          "missing_selected_context_count": len(context.missing_symbol_annotations),
                          "native_export_physical_reference_count": inventory.get("physical_component_count"),
                          "xml_references_without_selected_source_identity": sorted(set(inventory.get("physical_references", [])) - selected_refs)}
    return {"status": "FAIL" if errors else "INSUFFICIENT" if gaps else "PASS",
            "scope": "Hierarchy, annotation, cached symbol consistency and PDF count only; not electrical or production approval.",
            "root": root.name, "project": project, "page_count": len(pages),
            "component_count": len({r for r, _ in refs}), "pages": pages,
            "pin_signature_sha256": {r: hashlib.sha256(repr(s).encode()).hexdigest()
                                     for r, s in sorted(definitions.items()) if not r.startswith("#")},
            "file_sha256": file_hashes, "pdf": pdf_result,
            "missing_symbol_annotations": context.missing_symbol_annotations,
            "pinless_objects": pinless_objects, "source_role_evidence": roles,
            "component_count_domain": "Unique references in exact selected-project annotation contexts, including virtual refs",
            "native_inventory": inventory, "native_inventory_reconciliation": reconciliation,
            "errors": errors, "coverage_gaps": sorted(set(gaps))}


def compare_projects(before, after):
    old, new = before["file_sha256"], after["file_sha256"]
    def instances(report):
        return {(p["instance"], p["path"]) for p in report["pages"]}
    pins_old, pins_new = before["pin_signature_sha256"], after["pin_signature_sha256"]
    return {"removed_files": sorted(old.keys() - new.keys()),
            "added_files": sorted(new.keys() - old.keys()),
            "changed_files": sorted(p for p in old.keys() & new.keys() if old[p] != new[p]),
            "removed_instances": sorted(instances(before) - instances(after)),
            "added_instances": sorted(instances(after) - instances(before)),
            "removed_references": sorted(pins_old.keys() - pins_new.keys()),
            "added_references": sorted(pins_new.keys() - pins_old.keys()),
            "changed_pin_or_unit_signatures": sorted(r for r in pins_old.keys() & pins_new.keys() if pins_old[r] != pins_new[r])}
