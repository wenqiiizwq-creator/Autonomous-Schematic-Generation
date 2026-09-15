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

from .sexpr import all_nodes, first, value, parse, dump


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


def audit_project(root, pdf=None, project=None, expected_pages=None):
    root = Path(root).resolve()
    base = root.parent
    project = project or root.stem
    pages, errors, gaps, caches, definitions, refs = [], [], [], {}, {}, {}
    file_hashes = {}

    def visit(path, uuid_path=None, page="1", ancestors=()):
        try:
            relative = str(path.relative_to(base))
        except ValueError:
            errors.append({"kind": "nonportable_sheet_path"})
            return
        if path in ancestors:
            errors.append({"kind": "hierarchy_cycle", "path": relative})
            return
        if not path.is_file():
            errors.append({"kind": "missing_sheet", "path": relative})
            return
        try:
            data = path.read_bytes()
            tree = parse(data.decode("utf-8"))
            if tree[0] != "kicad_sch":
                raise ValueError("Expected kicad_sch")
        except (ValueError, UnicodeError) as exc:
            errors.append({"kind": "invalid_sheet", "path": relative, "reason": str(exc)})
            return
        file_hashes[relative] = hashlib.sha256(data).hexdigest()
        if uuid_path is None:
            uid = value(tree, "uuid")
            if not uid:
                errors.append({"kind": "missing_root_uuid"})
                return
            uuid_path = "/" + str(uid)
            root_pages = [value(p, "page") for p in all_nodes(first(tree, "sheet_instances", []), "path") if p[1] == "/"]
            if len(root_pages) > 1:
                errors.append({"kind": "duplicate_root_page_annotation"})
            if root_pages:
                page = root_pages[0]
        pages.append({"path": relative, "instance": uuid_path, "page": page})
        libs = {str(n[1]): n for n in all_nodes(first(tree, "lib_symbols", []), "symbol")}
        for symbol in all_nodes(tree, "symbol"):
            props = properties(symbol)
            ctx = _instance(symbol, project, uuid_path)
            if ctx is None:
                gaps.append(f"{relative}: missing symbol annotation for {project}:{uuid_path}")
            ref = str(value(ctx or [], "reference", props.get("Reference", "?")))
            unit = int(value(ctx or [], "unit", value(symbol, "unit", 1)))
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
        child_ids = set()
        for sheet in all_nodes(tree, "sheet"):
            props = properties(sheet)
            uid = value(sheet, "uuid")
            if not uid or uid in child_ids:
                errors.append({"kind": "missing_or_duplicate_sheet_uuid", "path": relative})
                continue
            child_ids.add(uid)
            ctx = _instance(sheet, project, uuid_path)
            child_page = value(ctx or [], "page")
            if child_page is None:
                gaps.append(f"{relative}: missing child page annotation for {project}:{uuid_path}")
            raw = props.get("Sheetfile", "")
            if not raw:
                errors.append({"kind": "missing_sheetfile_property", "path": relative})
                continue
            if Path(raw).is_absolute():
                errors.append({"kind": "nonportable_absolute_sheet_path", "path": relative})
                continue
            raw = raw.replace("${KIPRJMOD}", str(base))
            if "${" in raw or re.match(r"^[A-Za-z]:", raw):
                errors.append({"kind": "unresolved_sheet_path", "path": relative})
                continue
            visit((path.parent / raw).resolve(), uuid_path + "/" + str(uid),
                  str(child_page) if child_page is not None else None, ancestors + (path,))

    visit(root)
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
