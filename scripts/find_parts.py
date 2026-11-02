#!/usr/bin/env python3
"""Find candidate parts, reference designs and application notes in the local
HardwareWiki raw library before looking anywhere else.

The library lives outside the skill (default ~/Documents/知识库/HardwareWiki).
Datasheets are indexed by raw/Datasheet/catalog.json (vendor, model,
category, subcategory, facets, first pages of text); PDFs not yet in that
index are listed from the file system and marked 未入索引. Reference designs
(raw/Designexample/<topology>/<board>/) and application notes are matched by
path. Every hit is a path to open and read; this tool proves nothing about a
part's suitability.

  find_parts.py --categories                      # what the library covers
  find_parts.py --category "USB PD" PD3.2 PPS     # datasheets, AND over terms
  find_parts.py --mpn NCP1343                     # exact model / alias lookup
  find_parts.py --designs flyback PD              # reference designs by topology
  find_parts.py --notes "Type-C"                  # application notes
  find_parts.py --roles-coverage                  # part-roles.md vs library subcategories
  find_parts.py --file <pdf>                      # where this file already is in the library, if anywhere
  find_parts.py --circuits 反激 隔离                # circuit patterns (references/typical-circuits/) by name, function, approach
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys

ROLES_MD = Path(__file__).resolve().parent.parent / "references" / "part-roles.md"
CIRCUITS_DIR = Path(__file__).resolve().parent.parent / "references" / "typical-circuits"
DEFAULT_WIKI = Path(os.environ.get("HARDWARE_WIKI", Path.home() / "Documents" / "知识库" / "HardwareWiki"))


def norm(s):
    return re.sub(r"[\s\-_–—/]+", "", str(s or "")).lower()


def load_catalog(wiki):
    path = wiki / "raw" / "Datasheet" / "catalog.json"
    if not path.is_file():
        return None, f"{path} not found; run the library's build_catalog.py or search by path only"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except ValueError as exc:
        return None, f"{path}: {exc}"


def archived(row):
    """A superseded datasheet kept under <category>/versions/<hash>/: not a subcategory, not a candidate."""
    return "versions" in row["path"].split("/")


def unindexed_pdfs(wiki, indexed_paths):
    root = wiki / "raw" / "Datasheet"
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


def search_datasheets(wiki, terms, category=None, mpn=None, with_text=False, limit=40):
    catalog, problem = load_catalog(wiki)
    rows = list((catalog or {}).get("rows") or [])
    rows += unindexed_pdfs(wiki, {r["path"] for r in rows})
    rows = [r for r in rows if not archived(r)]
    if mpn:
        key = norm(mpn)
        hits = [r for r in rows if key in norm(r.get("model")) or key in norm(r.get("aliases"))]
    else:
        hits = [r for r in rows if match_row(r, terms, category, with_text)]
    hits.sort(key=lambda r: (r.get("category", ""), r.get("subcategory", ""), r.get("vendor", ""), r.get("model", "")))
    out = [{k: r.get(k) for k in ("vendor", "model", "category", "subcategory", "kind", "pages")}
           | {"path": "raw/Datasheet/" + r["path"]} for r in hits[:limit]]
    return {"query": {"terms": terms, "category": category, "mpn": mpn, "text": with_text},
            "library": str(wiki), "catalog_generated": (catalog or {}).get("generated"),
            "catalog_problem": problem, "total": len(hits), "shown": len(out), "results": out}


def categories(wiki):
    catalog, problem = load_catalog(wiki)
    counts = {}
    for r in (catalog or {}).get("rows") or []:
        if archived(r):
            continue
        counts.setdefault(r.get("category", ""), {}).setdefault(r.get("subcategory", ""), 0)
        counts[r["category"]][r.get("subcategory", "")] += 1
    return {"library": str(wiki), "catalog_problem": problem, "categories": counts}


def roles_subcategories(path=ROLES_MD):
    """Subcategory names in the first column of every per-category table of part-roles.md."""
    names = set()
    for section in re.split(r"\n### ", path.read_text(encoding="utf-8"))[1:]:
        for line in section.splitlines()[1:]:
            if line.startswith("|") and not line.startswith("|---") and not line.startswith("| 二级类"):
                names.add(line.split("|")[1].strip())
    return names


def roles_coverage(wiki, path=ROLES_MD):
    cats = categories(wiki)
    library = {s for subs in cats["categories"].values() for s in subs}
    table = roles_subcategories(path)
    return {"library": str(wiki), "roles": str(path), "catalog_problem": cats["catalog_problem"],
            "missing_in_table": sorted(library - table), "not_in_library": sorted(table - library),
            "status": "PASS" if library and library <= table else "FAIL"}


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def library_index(wiki):
    """One walk of raw/: catalog SHA-256 -> path, normalised file name -> path, byte size -> paths."""
    catalog, _ = load_catalog(wiki)
    by_hash = {row["sha256"]: "raw/Datasheet/" + row["path"] for row in (catalog or {}).get("rows") or [] if row.get("sha256")}
    by_name, by_size = {}, {}
    raw = wiki / "raw"
    for p in raw.rglob("*.pdf") if raw.is_dir() else []:
        by_name.setdefault(norm(p.stem), p)
        by_size.setdefault(p.stat().st_size, []).append(p)
    return {"wiki": wiki, "by_hash": by_hash, "by_name": by_name, "by_size": by_size}


def locate_file(wiki, path, index=None):
    """Library-relative path of a file already in raw/, or None.

    Matched by catalog SHA-256, then by normalised file name, then by hashing the
    library files of the same byte size (a renamed copy whose catalog entry is stale).
    Pass the same library_index() when locating many files.
    """
    path = Path(path)
    index = index or library_index(wiki)
    digest = sha256(path)
    if digest in index["by_hash"]:
        return index["by_hash"][digest]
    hit = index["by_name"].get(norm(path.stem))
    if hit is not None:
        return hit.relative_to(wiki).as_posix()
    for p in index["by_size"].get(path.stat().st_size, []):
        if sha256(p) == digest:
            return p.relative_to(wiki).as_posix()
    return None


def circuit_index(path=CIRCUITS_DIR):
    """{pattern id: {"title", "function", "implementations": [...]}} from references/typical-circuits/*.md."""
    index = {}
    for md in sorted(path.glob("*.md")) if path.is_dir() else []:
        title, function, implementations = "", "", []
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.startswith("# ") and not title:
                title = line[2:].strip()
            elif line.startswith("功能："):
                function = line[3:].strip()
            elif line.startswith("### "):
                implementations.append(line[4:].strip())
        index[md.stem] = {"title": title, "function": function, "implementations": implementations}
    return index


def search_circuits(terms, path=CIRCUITS_DIR):
    hits = []
    for pid, info in circuit_index(path).items():
        hay = norm(" ".join([pid, info["title"], info["function"]] + info["implementations"]))
        if all(norm(t) in hay for t in terms):
            hits.append({"id": pid, "file": "references/typical-circuits/%s.md" % pid, **info})
    return {"terms": terms, "total": len(hits), "results": hits}


def search_paths(wiki, kind, terms, limit=40):
    root = wiki / "raw" / kind
    if not root.is_dir():
        return {"library": str(wiki), "problem": f"{root} not found", "results": []}
    hits = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in (".pdf", ".txt", ".zip", ".md"):
            rel = p.relative_to(wiki).as_posix()
            if all(norm(t) in norm(rel) for t in terms):
                hits.append(rel)
    boards = sorted({h.rsplit("/", 1)[0] for h in hits})
    return {"library": str(wiki), "kind": kind, "terms": terms, "total": len(hits),
            "folders": boards[:limit], "files": hits[:limit]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="*", help="search terms, all must match (case/hyphen insensitive)")
    ap.add_argument("--wiki", type=Path, default=DEFAULT_WIKI, help="HardwareWiki root (env HARDWARE_WIKI)")
    ap.add_argument("--categories", action="store_true", help="list datasheet categories and counts")
    ap.add_argument("--category", help="restrict datasheets to a category or subcategory substring")
    ap.add_argument("--mpn", help="exact-ish model lookup (substring of model or alias)")
    ap.add_argument("--text", action="store_true", help="also match the indexed first pages of each datasheet")
    ap.add_argument("--designs", action="store_true", help="search raw/Designexample by path")
    ap.add_argument("--notes", action="store_true", help="search raw/Applicationnote by path")
    ap.add_argument("--circuits", action="store_true", help="search circuit patterns in references/typical-circuits/")
    ap.add_argument("--file", type=Path, help="report where this local file already is in the library")
    ap.add_argument("--roles-coverage", action="store_true", help="compare references/part-roles.md with the library")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
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
