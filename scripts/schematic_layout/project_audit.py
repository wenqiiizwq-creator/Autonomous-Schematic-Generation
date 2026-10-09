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


def audit_project(root, pdf=None, project=None, expected_pages=None, *, context=None):
    root = Path(root).resolve()
    context = context or NativeHierarchy(root, project)
    project = context.project
    pages = context.pages
    errors, gaps = list(context.errors), list(context.coverage_gaps)
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
    return {"status": "FAIL" if errors else "INSUFFICIENT" if gaps else "PASS",
            "scope": "Hierarchy, annotation, cached symbol consistency and PDF count only; not electrical or production approval.",
            "root": root.name, "project": project, "page_count": len(pages),
            "component_count": len({r for r, _ in refs}), "pages": pages,
            "pin_signature_sha256": {r: hashlib.sha256(repr(s).encode()).hexdigest()
                                     for r, s in sorted(definitions.items()) if not r.startswith("#")},
            "file_sha256": file_hashes, "pdf": pdf_result,
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
