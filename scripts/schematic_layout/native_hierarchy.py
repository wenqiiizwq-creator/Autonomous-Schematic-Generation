"""Read-only native file graph and selected-project annotation context.

Cache files, not page instances. Legacy root tables use root-relative UUID
chains; modern per-entity records use complete page paths. No Reference
property fallback, cross-project borrowing, or electrical acceptance.
"""
import hashlib
from pathlib import Path
import re

from .sexpr import all_nodes, first, value
from .sexpr import parse


# Native formats whose instance semantics are supported here. A missing version
# permits small API fixtures; unknown declared formats remain coverage gaps.
SUPPORTED_VERSIONS = {"20211123", "20230121", "20231120", "20250114"}


def sheet_properties(sheet):
    """Return canonical aliases plus errors, without silently picking a winner.

    Sheetname is optional for file-coverage fixtures. When present it has the
    same duplicate/conflict rules as Sheetfile. Sheetfile must be usable.
    """
    props, errors = {}, []
    for canonical, aliases in (("Sheetname", ("Sheetname", "Sheet name")),
                               ("Sheetfile", ("Sheetfile", "Sheet file"))):
        nodes = [p for p in all_nodes(sheet, "property") if len(p) > 1 and p[1] in aliases]
        for alias in aliases:
            if sum(p[1] == alias for p in nodes) > 1:
                errors.append({"kind": "duplicate_sheet_property", "property": alias})
        values = [str(p[2]) for p in nodes if len(p) > 2]
        if len(values) != len(nodes):
            errors.append({"kind": "invalid_sheet_property", "property": canonical})
        if len(set(values)) > 1:
            errors.append({"kind": "conflicting_sheet_property", "property": canonical})
        if values and len(set(values)) == 1:
            props[canonical] = values[0]
    if not any(len(p) > 2 and p[1] in ("Sheetfile", "Sheet file") and str(p[2])
               for p in all_nodes(sheet, "property")):
        errors.append({"kind": "missing_sheetfile_property"})
    return props, errors


class NativeHierarchy:
    """Parse once and resolve an active hierarchy without modifying any input."""
    def __init__(self, root, project=None, base=None, annotations=True):
        self.root = Path(root).resolve()
        self.base = Path(base).resolve() if base else self.root.parent
        self.project = project or self.root.stem
        self.pages, self.errors, self.coverage_gaps = [], [], []
        self.file_errors, self.file_sha256, self.trees = [], {}, {}
        self.symbol_contexts = {}
        self._visit(self.root, None, ())
        if annotations and self.pages:
            self._annotations()

    def _file_error(self, kind, **details):
        entry = {"kind": kind, **details}
        self.file_errors.append(entry)
        self.errors.append(entry)

    def _visit(self, path, instance, ancestors):
        try:
            relative = path.relative_to(self.base).as_posix()
        except ValueError:
            self._file_error("nonportable_sheet_path")
            return
        if path in ancestors:
            self._file_error("hierarchy_cycle", path=relative)
            return
        if not path.is_file():
            self._file_error("missing_sheet", path=relative)
            return
        if path not in self.trees:
            try:
                data = path.read_bytes()
                tree = parse(data.decode("utf-8"))
                if not tree or tree[0] != "kicad_sch":
                    raise ValueError("Expected kicad_sch")
            except (OSError, ValueError, UnicodeError, IndexError) as exc:
                self._file_error("invalid_sheet", path=relative, reason=str(exc))
                return
            self.trees[path] = tree
            self.file_sha256[relative] = hashlib.sha256(data).hexdigest()
        tree = self.trees[path]
        if instance is None:
            uid = value(tree, "uuid")
            if not uid:
                self.errors.append({"kind": "missing_root_uuid"})
            instance = "/" + str(uid or "")
        self.pages.append({"path": relative, "instance": instance, "page": None})
        ids = set()
        for ordinal, sheet in enumerate(all_nodes(tree, "sheet")):
            props, errs = sheet_properties(sheet)
            for e in errs:
                self._file_error(e["kind"], path=relative, **{k: v for k, v in e.items() if k != "kind"})
            uid = value(sheet, "uuid")
            if not uid or uid in ids:
                self.errors.append({"kind": "missing_or_duplicate_sheet_uuid", "path": relative})
            if uid:
                ids.add(uid)
            # File coverage remains meaningful even if instance UUIDs are absent.
            child_instance = instance + "/" + str(uid or ("@missing-" + str(ordinal)))
            if errs:
                continue
            raw = props["Sheetfile"]
            if Path(raw).is_absolute():
                self._file_error("nonportable_absolute_sheet_path", path=relative)
                continue
            raw = raw.replace("${KIPRJMOD}", str(self.base))
            if "${" in raw or re.match(r"^[A-Za-z]:", raw):
                self._file_error("unresolved_sheet_path", path=relative)
                continue
            self._visit((path.parent / raw).resolve(), child_instance, ancestors + (path,))

    def _annotation_error(self, kind, **details):
        self.errors.append({"kind": kind, **details})

    def _record(self, node, fields, location):
        record = {}
        for field in fields:
            nodes = all_nodes(node, field)
            if len(nodes) > 1:
                self._annotation_error("duplicate_annotation_context", path=location, field=field)
                return None
            if len(nodes) != 1 or len(nodes[0]) != 2 or not str(nodes[0][1]).strip():
                self.coverage_gaps.append(f"{location}: incomplete annotation field {field}")
                return None
            record[field] = str(nodes[0][1])
        if "unit" in record:
            try:
                record["unit"] = int(record["unit"])
                if record["unit"] < 1:
                    raise ValueError("nonpositive unit")
            except ValueError:
                self._annotation_error("invalid_annotation_context", path=location, field="unit")
                return None
        return record

    def _path(self, raw, legacy=False):
        if not isinstance(raw, str) or not raw.startswith("/") or "//" in raw or (raw != "/" and raw.endswith("/")):
            self.coverage_gaps.append(f"unsupported annotation path: {raw!r}")
            return None
        if legacy:
            return self.pages[0]["instance"] + ("" if raw == "/" else raw)
        return raw

    def _global(self, tree, tag, fields):
        result = {}
        tables = all_nodes(tree, tag)
        if len(tables) > 1:
            self._annotation_error("duplicate_annotation_context", table=tag)
        for table in tables:
            for node in all_nodes(table, "path"):
                path = self._path(node[1] if len(node) > 1 else None, legacy=True)
                if path is None:
                    continue
                if path in result:
                    self._annotation_error("duplicate_annotation_context", path=path, table=tag)
                    continue
                result[path] = self._record(node, fields, path)
        return result

    def _locals(self, tree, path):
        """Index entity-local records once per file, retaining full UUID paths."""
        result = {}
        for tag, fields in (("symbol", ("reference", "unit")), ("sheet", ("page",))):
            for entity in all_nodes(tree, tag):
                records = {}
                containers = all_nodes(entity, "instances")
                if len(containers) > 1:
                    self._annotation_error("duplicate_annotation_context", path=str(path))
                projects = [pr for c in containers for pr in all_nodes(c, "project")
                            if len(pr) > 1 and str(pr[1]) == self.project]
                if len(projects) > 1:
                    self._annotation_error("duplicate_annotation_context", path=str(path), project=self.project)
                for pr in projects:
                    for node in all_nodes(pr, "path"):
                        full = self._path(node[1] if len(node) > 1 else None)
                        if full is None:
                            continue
                        if full in records:
                            self._annotation_error("duplicate_annotation_context", path=full)
                            continue
                        records[full] = self._record(node, fields, full)
                result[id(entity)] = records
        return result

    def _merge(self, global_record, local_record, location):
        if global_record is not None and local_record is not None and global_record != local_record:
            self._annotation_error("conflicting_annotation_context", path=location)
            return None
        return global_record if global_record is not None else local_record

    def _annotations(self):
        root_tree = self.trees[self.root]
        unsupported = set()
        for path, tree in self.trees.items():
            version = value(tree, "version")
            if version is not None and str(version) not in SUPPORTED_VERSIONS:
                unsupported.add(path)
                self.coverage_gaps.append(f"{path.relative_to(self.base)}: unsupported native annotation version {version}")
        global_sheets = self._global(root_tree, "sheet_instances", ("page",)) if self.root not in unsupported else {}
        global_symbols = self._global(root_tree, "symbol_instances", ("reference", "unit")) if self.root not in unsupported else {}
        local = {path: self._locals(tree, path.relative_to(self.base)) if path not in unsupported else {}
                 for path, tree in self.trees.items()}
        active_sheets, active_symbols, active_local = set(), set(), {}
        for page in self.pages:
            file = self.base / page["path"]
            tree, chain = self.trees[file], page["instance"]
            active_sheets.add(chain)
            root_page = global_sheets.get(chain) if file == self.root and chain == self.pages[0]["instance"] else None
            if chain == self.pages[0]["instance"]:
                # Modern files conventionally start at page 1; legacy explicit
                # tables, if supplied, remain authoritative rather than guessed.
                page["page"] = root_page["page"] if root_page else "1" if not all_nodes(root_tree, "sheet_instances") and file not in unsupported else None
                if page["page"] is None:
                    self.coverage_gaps.append(f"{page['path']}: missing root page annotation")
            symbols = all_nodes(tree, "symbol")
            uids = [value(s, "uuid") for s in symbols if value(s, "uuid")]
            if len(uids) != len(set(uids)):
                self._annotation_error("missing_or_duplicate_symbol_uuid", path=page["path"])
            for symbol in symbols:
                active_local.setdefault((file, id(symbol)), set()).add(chain)
                uuid_nodes = all_nodes(symbol, "uuid")
                uid = value(symbol, "uuid")
                declared = str(value(tree, "version")) in SUPPORTED_VERSIONS
                if not uuid_nodes and declared:
                    self.coverage_gaps.append(f"{page['path']}: missing native symbol UUID for {chain}")
                    continue
                if uuid_nodes and (len(uuid_nodes) != 1 or len(uuid_nodes[0]) != 2
                                   or not str(uid or "").strip() or re.search(r"[\s/]", str(uid))):
                    self._annotation_error("invalid_symbol_uuid", path=page["path"])
                    continue
                full = chain + "/" + str(uid) if uid else None
                if full:
                    active_symbols.add(full)
                global_record = global_symbols.get(full) if file not in unsupported else None
                local_record = local[file].get(id(symbol), {}).get(chain)
                record = self._merge(global_record, local_record, full or chain)
                if record is None:
                    self.coverage_gaps.append(f"{page['path']}: missing symbol annotation for {self.project}:{chain}")
                else:
                    self.symbol_contexts[(chain, id(symbol))] = record
            for sheet in all_nodes(tree, "sheet"):
                active_local.setdefault((file, id(sheet)), set()).add(chain)
                child_chain = chain + "/" + str(value(sheet, "uuid"))
                record = self._merge(global_sheets.get(child_chain) if file not in unsupported else None,
                                     local[file].get(id(sheet), {}).get(chain), child_chain)
                if record is None:
                    self.coverage_gaps.append(f"{page['path']}: missing child page annotation for {self.project}:{chain}")
                else:
                    for child in self.pages:
                        if child["instance"] == child_chain:
                            child["page"] = record["page"]
        for table, active in ((global_sheets, active_sheets), (global_symbols, active_symbols)):
            for path in table.keys() - active:
                self._annotation_error("dangling_annotation_context", path=path)
        for file, records in local.items():
            for entity, annotations in records.items():
                for path in annotations.keys() - active_local.get((file, entity), set()):
                    self._annotation_error("dangling_annotation_context", path=path, file=file.relative_to(self.base).as_posix())

    def tree_for(self, page):
        return self.trees[self.base / page["path"]]

    def symbol_context(self, page, symbol):
        return self.symbol_contexts.get((page["instance"], id(symbol)))
