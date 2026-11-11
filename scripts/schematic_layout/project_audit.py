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
from .design_change import PINLESS_ROLES, native_inventory


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


def audit_project(root, pdf=None, project=None, expected_pages=None, *, context=None, netlist=None):
    root = Path(root).resolve()
    context = context or NativeHierarchy(root, project)
    project = context.project
    pages = context.pages
    errors, gaps = list(context.errors), list(context.coverage_gaps)
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
                # A mounting hole, logo or note: declared by its ComponentRole, and no unit or style of its
                # cached symbol has a pin. Anything else without active pins is a broken symbol.
                role = properties(symbol).get("ComponentRole")
                if not signature and role in PINLESS_ROLES:
                    pinless_objects.append({"reference": ref, "instance": page["instance"],
                                            "symbol_uuid": str(value(symbol, "uuid", "")), "role": role,
                                            "pin_integrity": "NA",
                                            "reason": "Declared ComponentRole; no cached unit/style has pins"})
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
            "pinless_objects": pinless_objects,
            "component_count_domain": "Unique references in exact selected-project annotation contexts, including virtual refs",
            "native_inventory": inventory, "native_inventory_reconciliation": reconciliation,
            "errors": errors, "coverage_gaps": sorted(set(gaps))}
