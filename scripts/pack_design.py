#!/usr/bin/env python3
"""Check a delivery folder has exactly the fixed shape, then write record/manifest.json.

    <delivery>/
      设计报告.md     render_design_report.py
      原理图/         KiCad project, schematic.pdf, netlist.xml, BOM.csv
      设计资料/       design documents that stay valid across versions
      record/         intent, design closure (+ audit), summary.json, visual review,
                      cited calculations and page scripts, manifest.json

Requirements and datasheets are referenced by path + SHA-256, never
copied. Anything else at the top level, history snapshots and design
evidence that the closure record cites but the folder does not contain all fail the pack.
Design documents must also agree with the design: every part a 设计资料/ table or assembly file
names must exist in the electrical intent, with the same MPN and value where the table gives them.
PDFs in the datasheets input that the HardwareWiki library does not hold yet (same SHA-256 or
file name ignoring spaces, hyphens and case) do not block packing: they are listed in the manifest's
``datasheets_to_file`` and printed, so the user can file them into the library after delivery.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_design_closure import audit, load_task, read_requirements  # noqa: E402
import check_module  # noqa: E402
import knowledge_gaps  # noqa: E402
from find_parts import DEFAULT_WIKI, library_index, locate_file  # noqa: E402
from render_design_report import REPORT, render  # noqa: E402
from schematic_layout.component_requirements import package_audit  # noqa: E402

TOP = (REPORT, '原理图', '设计资料', 'record')
SCHEMATIC = ('schematic.pdf', 'netlist.xml', 'BOM.csv')
# sr-review: an independent schematic-review run of this version kept with the records it reviewed
# (industrial I/O calibration board 2026-11-03: the SR report lives in record/sr-review/ and packing refused it).
RECORD_DIRS = ('calculations', 'scripts', 'evidence', 'sr-review', 'block-circuits')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def fingerprint(path):
    path = Path(path).resolve()
    if path.is_file():
        return {'path': str(path), 'kind': 'file', 'sha256': sha256(path)}
    files = sorted(p for p in path.rglob('*') if p.is_file() and not p.name.startswith('.'))
    tree = hashlib.sha256()
    for p in files:
        tree.update(('%s\0%s\n' % (p.relative_to(path).as_posix(), sha256(p))).encode())
    return {'path': str(path), 'kind': 'directory', 'files': len(files), 'tree_sha256': tree.hexdigest()}


def skill_version():
    try:
        return subprocess.run(['git', '-C', str(Path(__file__).resolve().parents[1]), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


REF_COLUMNS = ('ref', 'refs', 'reference', '位号')
REF_KEYS = ('ref', 'refs', 'fit', 'dnp')
SAME_FIELDS = ('mpn', 'value')


def _refs(value):
    """Parts named by one cell or JSON value: 'R1', 'R1, R2' or a list of them."""
    items = value if isinstance(value, list) else [value]
    return [r for item in items if isinstance(item, str) for r in re.split(r'[,;\s]+', item.strip()) if r]


# Prose "<ref> <part number>" in 设计资料/*.md (Matrix R2, 2026-11-04: 供电路径复核.md kept "U801 LM5060" after U801
# became an LTC4367). The ref is a reference-like word not glued to a longer name (CR-R301, TPS62903 are not refs);
# the next word looks like a part number: a digit and an uppercase letter, four characters or more, not a value with
# a unit (100uF, 4.7UH) and not a capitalised word with a number (Pin3/4, Rev2).
PROSE_PART = re.compile(r'(?<![A-Za-z0-9_\-./#])([A-Z]{1,3})(\d{1,4})(?![A-Za-z0-9_\-])\s+([A-Za-z0-9][A-Za-z0-9\-#/.+]*)')
VALUE_WITH_UNIT = re.compile(r'\d+(?:\.\d+)?[A-Za-zµμΩ]*')


def _part_like(token):
    token = token.rstrip('.')
    return (len(token) >= 4 and re.search(r'\d', token) and re.search(r'[A-Z]', token)
            and not VALUE_WITH_UNIT.fullmatch(token) and not re.match(r'[A-Z][a-z]', token))


def _same_part(written, mpn):
    """The written part number names the design's mpn: ignoring case, hyphens and other punctuation, it is a
    piece of the mpn or the mpn of it, or its base (letters and the first run of digits: LM5069 of LM5069-1,
    LVC07 of LVC07A) is; package/variant suffixes and family prefixes such as SN74 do not matter."""
    flat = lambda s: re.sub(r'[^0-9A-Z]', '', s.upper())
    w, m = flat(written), flat(mpn)
    base = re.match(r'[A-Z]*\d+', written.upper())
    base = flat(base.group(0)) if base and re.search(r'[A-Z]', base.group(0)) and len(base.group(0)) >= 4 else w
    return bool(w and m) and (w in m or m in w or base in m)


def prose_parts(path, rel, parts):
    """"<ref> <part number>" in a Markdown file's prose against the design netlist. Table rows and code blocks
    are skipped (tables are read by their columns); a ref whose letters no part of the design uses (LM, TPS) is
    a part name, not a ref."""
    prefixes = {re.match(r'[A-Z]*', r).group(0) for r in parts if isinstance(r, str)}
    errors, fenced = [], False
    for number, line in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if line.lstrip().startswith(('```', '~~~')):
            fenced = not fenced
            continue
        if fenced or line.lstrip().startswith('|'):
            continue
        for match in PROSE_PART.finditer(line):
            letters, digits, token = match.groups()
            ref, token = letters + digits, token.rstrip('.')
            if letters not in prefixes or not _part_like(token):
                continue
            part = parts.get(ref)
            if part is None:
                errors.append('%s line %d: %s %s is not in the design' % (rel, number, ref, token))
                continue
            mpn = str(part.get('mpn') or part.get('value') or '').strip()
            if mpn and not _same_part(token, mpn):
                errors.append('%s line %d: text says %s %s, the design has %s %s' % (rel, number, ref, token, ref, mpn))
    return errors


def document_refs(root, intent):
    """Parts named in 设计资料/ tables, assembly files and prose that the design does not have, or describes differently.

    Covers CSV tables with a reference column (and their mpn/value columns), JSON values under
    ref/refs/fit/dnp keys, and "<ref> <part number>" in Markdown prose (prose_parts). Other prose is not parsed.
    """
    parts = {c.get('ref'): c for c in intent.get('components', []) if isinstance(c, dict)}
    errors = []
    docs = root / '设计资料'
    for path in sorted(docs.rglob('*')) if docs.is_dir() else []:
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() == '.md':
            errors += prose_parts(path, rel, parts)
        elif path.suffix.lower() == '.csv':
            with open(path, encoding='utf-8-sig', newline='') as f:
                rows = csv.DictReader(f)
                columns = {c.strip().lower(): c for c in rows.fieldnames or [] if c}
                ref_col = next((columns[c] for c in REF_COLUMNS if c in columns), None)
                if not ref_col:
                    continue
                for line, row in enumerate(rows, 2):
                    for ref in _refs(row.get(ref_col) or ''):
                        part = parts.get(ref)
                        if part is None:
                            errors.append('%s line %d: %s is not in the design' % (rel, line, ref))
                            continue
                        for field in SAME_FIELDS:
                            given = (row.get(columns.get(field, '')) or '').strip()
                            expected = str(part.get(field) or '').strip()
                            if given and expected and given != expected:
                                errors.append('%s line %d: %s %s is %r, the design has %r' % (rel, line, ref, field, given, expected))
        elif path.suffix.lower() == '.json':
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, ValueError) as error:
                errors.append('%s cannot be read: %s' % (rel, error))
                continue
            stack = [data]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    for key, value in node.items():
                        if key in REF_KEYS:
                            errors += ['%s: %s %s is not in the design' % (rel, key, r) for r in _refs(value) if r not in parts]
                        else:
                            stack.append(value)
                elif isinstance(node, list):
                    stack.extend(node)
    return errors


def check(root, inputs=()):
    root = Path(root)
    # A module run (task.json `modules`, SKILL.md 架构) delivers a module report and its records, not a whole board.
    if (load_task(root) or {}).get('modules'):
        return check_module.check_delivery(root)
    errors = []
    present = {p.name for p in root.iterdir() if not p.name.startswith('.')} if root.is_dir() else set()
    extra = sorted(present - set(TOP))
    if extra:
        errors.append('only %s belong at the top level; move these to the work directory or reference them '
                      'with --input: %s' % (', '.join(TOP), ', '.join(extra)))
    for name in TOP:
        if name not in present:
            errors.append('missing %s%s' % (name, '; run render_design_report.py' if name == REPORT else ''))
    sch = root / '原理图'
    if sch.is_dir():
        if not list(sch.glob('*.kicad_pro')):
            errors.append('原理图/ has no .kicad_pro')
        for name in SCHEMATIC:
            if not (sch / name).is_file():
                errors.append('原理图/%s is missing' % name)
    record = root / 'record'
    if record.is_dir():
        # The other records are the report's to require; it names each one missing.
        if not (record / 'delivery-evidence.json').is_file():
            errors.append('record/delivery-evidence.json is missing')
        for p in record.iterdir():
            if p.is_dir() and p.name not in RECORD_DIRS:
                errors.append('record/%s/ is not a delivery folder (allowed: %s)' % (p.name, ', '.join(RECORD_DIRS)))
    intent, closure = record / 'electrical-intent.json', record / 'design-closure.json'
    if intent.is_file():
        try:
            intent_data = json.loads(intent.read_text(encoding='utf-8'))
            errors += ['design documents: ' + e for e in document_refs(root, intent_data)]
            performance = package_audit(root, intent_data)
            if performance['status'] == 'FAIL':
                errors += ['component requirements: ' + e for e in performance['errors']]
        except ValueError as error:
            errors.append('electrical-intent.json cannot be read: %s' % error)
    if intent.is_file() and closure.is_file():
        try:
            result = audit(json.loads(closure.read_text(encoding='utf-8')), intent, root, inputs,
                           requirements=read_requirements(closure))
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append('design-closure.json cannot be audited: %s' % error)
        else:
            if result['status'] == 'FAIL':
                errors.append('design-closure.json fails inside the delivery (cited evidence must be in this folder, '
                              'paths relative to it, or in an --input): ' + '; '.join('%s %s' % (e['code'], e['item'])
                                                                    for e in result['errors'][:5]))
            # SKILL.md C5.2 (user 2026-11-08: 按草案实施): an uncited rule no longer blocks; a board with external connectors
            # carries its FMEA and EMC port matrix with every section and connector.
            docs = [p['item'] for p in result.get('pending', []) if p.get('code') == 'design_document_incomplete']
            if docs:
                errors.append('design-closure.json: 必写的设计文档不齐（%s）；见 references/guideline-evidence-groups.md' % '；'.join(docs))
            # SKILL.md C5.2: the matrices and state tables have no cell without a conclusion or failing (2026-11-07).
            cells = [p['item'] for p in result.get('pending', []) if p.get('code') in ('matrix_cell_missing', 'matrix_cell_failed')]
            if cells:
                errors.append('design-closure.json: 矩阵与状态表有 %d 格缺结论或不满足（%s%s）；按 object_matrices.py 列出的格逐格写结论，'
                              '不满足的改设计' % (len(cells), '；'.join(cells[:5]), ' 等' if len(cells) > 5 else ''))
    if (root / REPORT).is_file() and record.is_dir():
        _, problems = render(root)
        errors += ['report records: ' + p for p in problems]
    return errors


def datasheets_not_in_library(folder, wiki):
    """PDFs under the datasheets input that the HardwareWiki library does not hold yet."""
    folder = Path(folder)
    pdfs = sorted(p for p in folder.rglob('*.pdf') if p.is_file()) if folder.is_dir() else []
    index = library_index(Path(wiki)) if pdfs else None
    return [p.relative_to(folder).as_posix() for p in pdfs if locate_file(wiki, p, index) is None]


def pack(root, inputs, wiki=DEFAULT_WIKI):
    root = Path(root)
    errors = check(root, list(inputs.values()))
    declared = {}
    for name, path in inputs.items():
        if not Path(path).exists():
            errors.append('input %s does not exist: %s' % (name, path))
        else:
            declared[name] = fingerprint(path)
    to_file = datasheets_not_in_library(inputs['datasheets'], Path(wiki)) if 'datasheets' in declared else []
    if not (load_task(root) or {}).get('modules'):      # a whole-board delivery carries its knowledge-gap list
        problem = knowledge_gaps.stale(root)
        errors += [problem] if problem else []
    if errors:
        return errors, None
    packed = {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob('*'))
              if p.is_file() and p.name != 'manifest.json'}
    manifest = {'schema_version': 1, 'skill_version': skill_version(), 'inputs': declared, 'packed': packed,
                'datasheets_to_file': to_file}
    (root / 'record' / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
                                                   encoding='utf-8')
    return [], manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('delivery')
    parser.add_argument('--input', action='append', default=[], metavar='NAME=PATH',
                        help='requirements, datasheets ... (referenced, not copied)')
    parser.add_argument('--wiki', type=Path, default=DEFAULT_WIKI, help='HardwareWiki root (env HARDWARE_WIKI)')
    args = parser.parse_args(argv)
    errors, manifest = pack(args.delivery, dict(item.split('=', 1) for item in args.input), args.wiki)
    for e in errors:
        print('ERROR:', e)
    for pdf in (manifest or {}).get('datasheets_to_file') or []:
        print('TO_FILE:', pdf, '(not in the library %s yet; copy it there after delivery, SKILL.md task C4.1)' % args.wiki)
    print('FAIL' if errors else 'PASS')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
