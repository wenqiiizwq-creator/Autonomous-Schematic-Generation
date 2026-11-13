#!/usr/bin/env python3
"""Find candidate parts, reference designs and application notes in the local
source library (原件总库) before looking anywhere else.

The library lives outside the skill: the knowledge framework's 原件/ (it points
to HardwareWiki/raw), found through knowledge_source.raw_root(); --wiki names
another source library directory instead. Paths are relative to that directory.
Datasheets are indexed by Datasheet/catalog.json (vendor, model,
category, subcategory, facets, first pages of text); PDFs not yet in that
index are listed from the file system and marked 未入索引. Reference designs
(Designexample/<topology>/<board>/) and application notes are matched by
path. Every hit is a path to open and read; this tool proves nothing about a
part's suitability.

  find_parts.py --categories                      # what the library covers
  find_parts.py --category "USB PD" PD3.2 PPS     # datasheets, AND over terms
  find_parts.py --mpn NCP1343                     # exact model / alias lookup
  find_parts.py --designs flyback PD              # reference designs by topology
  find_parts.py --notes "Type-C"                  # application notes
  find_parts.py --roles-coverage                  # part-roles.md vs library subcategories
  find_parts.py --file <pdf>                      # where this file already is in the library, if anywhere
  find_parts.py --circuits 反激 隔离                # circuit patterns (知识框架 知识/典型电路/) by name, function, approach
"""

import argparse
import json
from pathlib import Path
import re
import sys

import knowledge_source

ROLES_MD = Path(__file__).resolve().parent.parent / "references" / "part-roles.md"


def old_wiki_problem(path):
    """The message for a --wiki that still names the HardwareWiki root (raw/ inside, no Datasheet/), else None."""
    path = Path(path).expanduser()
    if not (path / "Datasheet").is_dir() and (path / "raw").is_dir():
        return ("--wiki %s 是 HardwareWiki 根目录：现在要给原件目录本身（%s），默认取知识框架的原件"
                % (path, path / "raw"))
    return None


def norm(s):
    return re.sub(r"[\s\-_–—/]+", "", str(s or "")).lower()


def load_catalog(raw):
    path = raw / "Datasheet" / "catalog.json"
    if not path.is_file():
        return None, f"{path} not found; run the library's build_catalog.py or search by path only"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except ValueError as exc:
        return None, f"{path}: {exc}"


def archived(row):
    """A superseded datasheet kept under <category>/versions/<hash>/: not a subcategory, not a candidate."""
    return "versions" in row["path"].split("/")


def unindexed_pdfs(raw, indexed_paths):
    root = raw / "Datasheet"
    found = []
    for p in root.rglob("*.pdf"):
        rel = p.relative_to(root).as_posix()
        if rel not in indexed_paths:
            parts = rel.split("/")
            name = p.stem
            vendor, _, model = name.partition(" - ")
            found.append({"vendor": vendor if model else "", "model": model or name, "category": parts[0],
                          "subcategory": parts[1] if len(parts) > 2 else "", "path": rel, "pages": None,
                          "kind": "未入索引", "facets": [], "aliases": "", "first_page": ""})
    return found


def match_row(row, terms, category, with_text):
    hay = " ".join(str(row.get(k) or "") for k in ("vendor", "model", "category", "subcategory", "aliases", "path"))
    hay += " " + " ".join(row.get("facets") or [])
    if with_text:
        hay += " " + str(row.get("first_page") or "")
    hay_n = norm(hay)
    if category and norm(category) not in norm(row.get("category", "") + row.get("subcategory", "")):
        return False
    return all(norm(t) in hay_n for t in terms)


def search_datasheets(raw, terms, category=None, mpn=None, with_text=False, limit=40):
    catalog, problem = load_catalog(raw)
    rows = list((catalog or {}).get("rows") or [])
    rows += unindexed_pdfs(raw, {r["path"] for r in rows})
    rows = [r for r in rows if not archived(r)]
    if mpn:
        key = norm(mpn)
        hits = [r for r in rows if key in norm(r.get("model")) or key in norm(r.get("aliases"))]
    else:
        hits = [r for r in rows if match_row(r, terms, category, with_text)]
    hits.sort(key=lambda r: (r.get("category", ""), r.get("subcategory", ""), r.get("vendor", ""), r.get("model", "")))
    out = [{k: r.get(k) for k in ("vendor", "model", "category", "subcategory", "kind", "pages")}
           | {"path": "Datasheet/" + r["path"]} for r in hits[:limit]]
    return {"query": {"terms": terms, "category": category, "mpn": mpn, "text": with_text},
            "library": str(raw), "catalog_generated": (catalog or {}).get("generated"),
            "catalog_problem": problem, "total": len(hits), "shown": len(out), "results": out}


def categories(raw):
    catalog, problem = load_catalog(raw)
    counts = {}
    for r in (catalog or {}).get("rows") or []:
        if archived(r):
            continue
        counts.setdefault(r.get("category", ""), {}).setdefault(r.get("subcategory", ""), 0)
        counts[r["category"]][r.get("subcategory", "")] += 1
    return {"library": str(raw), "catalog_problem": problem, "categories": counts}


def roles_subcategories(path=ROLES_MD):
    """Subcategory names in the first column of every per-category table of part-roles.md."""
    names = set()
    for section in re.split(r"\n### ", path.read_text(encoding="utf-8"))[1:]:
        for line in section.splitlines()[1:]:
            if line.startswith("|") and not line.startswith("|---") and not line.startswith("| 二级类"):
                names.add(line.split("|")[1].strip())
    return names


def roles_coverage(raw, path=ROLES_MD):
    cats = categories(raw)
    library = {s for subs in cats["categories"].values() for s in subs}
    table = roles_subcategories(path)
    return {"library": str(raw), "roles": str(path), "catalog_problem": cats["catalog_problem"],
            "missing_in_table": sorted(library - table), "not_in_library": sorted(table - library),
            "status": "PASS" if library and library <= table else "FAIL"}


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def library_index(raw):
    """One walk of the source library: catalog SHA-256 -> path, normalised file name -> path, byte size -> paths."""
    catalog, _ = load_catalog(raw)
    by_hash = {row["sha256"]: "Datasheet/" + row["path"] for row in (catalog or {}).get("rows") or [] if row.get("sha256")}
    by_name, by_size = {}, {}
    for p in raw.rglob("*.pdf") if raw.is_dir() else []:
        by_name.setdefault(norm(p.stem), p)
        by_size.setdefault(p.stat().st_size, []).append(p)
    return {"raw": raw, "by_hash": by_hash, "by_name": by_name, "by_size": by_size}


def locate_file(raw, path, index=None):
    """Library-relative path of a file already in the source library, or None.

    Matched by catalog SHA-256, then by normalised file name, then by hashing the
    library files of the same byte size (a renamed copy whose catalog entry is stale).
    Pass the same library_index() when locating many files.
    """
    path = Path(path)
    index = index or library_index(raw)
    digest = sha256(path)
    if digest in index["by_hash"]:
        return index["by_hash"][digest]
    hit = index["by_name"].get(norm(path.stem))
    if hit is not None:
        return hit.relative_to(raw).as_posix()
    for p in index["by_size"].get(path.stat().st_size, []):
        if sha256(p) == digest:
            return p.relative_to(raw).as_posix()
    return None


def circuit_index(path=None):
    """{pattern id: {"title", "function", "implementations": [...]}} from the framework's 知识/典型电路/<知识域>/*.md;
    implementations are the ### headings under 「## 实现方案」 only; "file" is relative to 知识/."""
    path = Path(path) if path else knowledge_source.knowledge_dir() / "典型电路"
    index = {}
    for md in sorted(path.rglob("*.md")) if path.is_dir() else []:
        if md.name == "README.md":
            continue
        title, function, implementations, in_implementations = "", "", [], False
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.startswith("# ") and not title:
                title = line[2:].strip()
            elif line.startswith("功能："):
                function = line[3:].strip()
            elif line.startswith("## "):
                in_implementations = line.strip() == "## 实现方案"
            elif line.startswith("### ") and in_implementations:
                implementations.append(line[4:].strip())
        index[md.stem] = {"title": title, "function": function, "implementations": implementations,
                          "file": "典型电路/" + md.relative_to(path).as_posix()}
    return index


def search_circuits(terms, path=None):
    hits = []
    for pid, info in circuit_index(path).items():
        hay = norm(" ".join([pid, info["title"], info["function"]] + info["implementations"]))
        if all(norm(t) in hay for t in terms):
            hits.append({"id": pid, **info})
    return {"terms": terms, "total": len(hits), "results": hits}


def search_paths(raw, kind, terms, limit=40):
    root = raw / kind
    if not root.is_dir():
        return {"library": str(raw), "problem": f"{root} not found", "results": []}
    hits = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in (".pdf", ".txt", ".zip", ".md"):
            rel = p.relative_to(raw).as_posix()
            if all(norm(t) in norm(rel) for t in terms):
                hits.append(rel)
    boards = sorted({h.rsplit("/", 1)[0] for h in hits})
    return {"library": str(raw), "kind": kind, "terms": terms, "total": len(hits),
            "folders": boards[:limit], "files": hits[:limit]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="*", help="search terms, all must match (case/hyphen insensitive)")
    ap.add_argument("--wiki", type=Path, help="source library directory (the one holding Datasheet/); default: the "
                    "knowledge framework's 原件/, which points to HardwareWiki/raw")
    ap.add_argument("--categories", action="store_true", help="list datasheet categories and counts")
    ap.add_argument("--category", help="restrict datasheets to a category or subcategory substring")
    ap.add_argument("--mpn", help="exact-ish model lookup (substring of model or alias)")
    ap.add_argument("--text", action="store_true", help="also match the indexed first pages of each datasheet")
    ap.add_argument("--designs", action="store_true", help="search Designexample/ by path")
    ap.add_argument("--notes", action="store_true", help="search Applicationnote/ by path")
    ap.add_argument("--circuits", action="store_true", help="search circuit patterns in the knowledge framework's 知识/典型电路/")
    ap.add_argument("--file", type=Path, help="report where this local file already is in the library")
    ap.add_argument("--roles-coverage", action="store_true", help="compare references/part-roles.md with the library")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    if not args.circuits and args.wiki is None:
        try:
            args.wiki = knowledge_source.raw_root()
        except knowledge_source.KnowledgeFrameworkNotFound as exc:
            ap.error(str(exc))
    elif not args.circuits and old_wiki_problem(args.wiki):
        ap.error(old_wiki_problem(args.wiki))
    if args.circuits:
        report = search_circuits(args.terms)
    elif args.file:
        where = locate_file(args.wiki, args.file)
        report = {"library": str(args.wiki), "file": str(args.file), "in_library": where,
                  "status": "PASS" if where else "FAIL"}
    elif args.roles_coverage:
        report = roles_coverage(args.wiki)
    elif args.categories:
        report = categories(args.wiki)
    elif args.designs:
        report = search_paths(args.wiki, "Designexample", args.terms, args.limit)
    elif args.notes:
        report = search_paths(args.wiki, "Applicationnote", args.terms, args.limit)
    elif args.mpn or args.terms or args.category:
        report = search_datasheets(args.wiki, args.terms, args.category, args.mpn, args.text, args.limit)
    else:
        ap.error("give search terms, --mpn, --category, --designs, --notes or --categories")
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if report.get("status") == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
