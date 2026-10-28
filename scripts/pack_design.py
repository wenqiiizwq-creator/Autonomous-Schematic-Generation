#!/usr/bin/env python3
"""Check a delivery folder has exactly the fixed shape, then write record/manifest.json.

    <delivery>/
      设计报告.md     render_design_report.py
      原理图/         KiCad project, schematic.pdf, netlist.xml, BOM.csv
      设计资料/       design documents that stay valid across versions
      record/         intent, design closure (+ audit), summary.json, visual review,
                      review responses, cited calculations and page scripts, manifest.json

Requirements, datasheets and the previous version are referenced by path + SHA-256, never
copied. Anything else at the top level, history snapshots and design
evidence that the closure record cites but the folder does not contain all fail the pack.
Design documents must also agree with the design: every part a 设计资料/ table or assembly file
names must exist in the electrical intent, with the same MPN and value where the table gives them.
Every PDF in the datasheets input must already be in the HardwareWiki library (same SHA-256 or
file name ignoring spaces, hyphens and case); packing lists the ones that are not and refuses until they are filed.
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
from audit_design_closure import audit  # noqa: E402
from find_parts import DEFAULT_WIKI, library_index, locate_file  # noqa: E402
from render_design_report import REPORT, render  # noqa: E402
from schematic_layout.component_requirements import package_audit  # noqa: E402

TOP = (REPORT, '原理图', '设计资料', 'record')
SCHEMATIC = ('schematic.pdf', 'netlist.xml', 'BOM.csv')
RECORD_DIRS = ('calculations', 'scripts', 'evidence')


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


def document_refs(root, intent):
    """Parts named in 设计资料/ tables and assembly files that the design does not have, or describes differently.

    Covers CSV tables with a reference column (and their mpn/value columns) and JSON values under
    ref/refs/fit/dnp keys. Free text is not parsed: a stale part mentioned only in prose is not found.
    """
    parts = {c.get('ref'): c for c in intent.get('components', []) if isinstance(c, dict)}
    errors = []
    docs = root / '设计资料'
    for path in sorted(docs.rglob('*')) if docs.is_dir() else []:
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() == '.csv':
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


def nets_of(intent):
    touched = {}
    nets = intent.get('nets') or []
    for n in (nets if isinstance(nets, list) else [{'name': k, 'pins': v} for k, v in nets.items()]):
        for pin in n.get('pins') or []:
            touched.setdefault(str(pin).rsplit('.', 1)[0], set()).add(n.get('name'))
    return touched


def check_against_previous(root, previous):
    """A 改图 response must have changed something in the intent since the previous
    delivery. The open work itself is not compared: each version lists only what
    its own design process confirmed is still to do."""
    root, previous = Path(root), Path(previous)
    errors = []
    responses = root / 'record' / 'review-responses.json'
    if responses.is_file():
        try:
            items = json.loads(responses.read_text(encoding='utf-8')).get('items') or []
            prev_intent = json.loads((previous / 'record' / 'electrical-intent.json').read_text(encoding='utf-8'))
            cur_intent = json.loads((root / 'record' / 'electrical-intent.json').read_text(encoding='utf-8'))
        except (OSError, ValueError) as error:
            return errors + ['previous: cannot compare intents: %s' % error]
        before = {c.get('ref'): c for c in prev_intent.get('components') or [] if isinstance(c, dict)}
        after = {c.get('ref'): c for c in cur_intent.get('components') or [] if isinstance(c, dict)}
        nets_before, nets_after = nets_of(prev_intent), nets_of(cur_intent)
        changed = {r for r in set(before) | set(after)
                   if before.get(r) != after.get(r) or nets_before.get(r, set()) != nets_after.get(r, set())}
        for item in items:
            if not isinstance(item, dict) or item.get('response') != 'REDESIGN':
                continue
            named = set()
            for c in item.get('changes') or []:
                named |= set(re.findall(r'(?<![A-Za-z0-9])[A-Z]{1,3}\d{1,4}(?![A-Za-z0-9])', str(c)))
            if named and not named & changed:
                errors.append('previous: %s 标为“改图”，但 %s 在设计网表里与上一版相同' % (item.get('id'), '、'.join(sorted(named))))
    return errors


def check(root, inputs=(), previous=None):
    root = Path(root)
    errors = []
    if previous:
        errors += check_against_previous(root, previous)
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
            result = audit(json.loads(closure.read_text(encoding='utf-8')), intent, root, inputs)
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append('design-closure.json cannot be audited: %s' % error)
        else:
            if result['status'] == 'FAIL':
                errors.append('design-closure.json fails inside the delivery (cited evidence must be in this folder, '
                              'paths relative to it, or in an --input): ' + '; '.join('%s %s' % (e['code'], e['item'])
                                                                    for e in result['errors'][:5]))
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
    errors = check(root, list(inputs.values()), inputs.get('previous'))
    declared = {}
    for name, path in inputs.items():
        if not Path(path).exists():
            errors.append('input %s does not exist: %s' % (name, path))
        else:
            declared[name] = fingerprint(path)
    if 'datasheets' in declared:
        missing = datasheets_not_in_library(inputs['datasheets'], Path(wiki))
        if missing:
            errors.append('%d datasheets are not in the library %s yet; file them per SKILL.md task 2.1 '
                          '(find_parts.py --file <pdf> shows where one already is): %s'
                          % (len(missing), wiki, ', '.join(missing[:8]) + ('…' if len(missing) > 8 else '')))
    if errors:
        return errors, None
    packed = {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob('*'))
              if p.is_file() and p.name != 'manifest.json'}
    manifest = {'schema_version': 1, 'skill_version': skill_version(), 'inputs': declared, 'packed': packed}
    (root / 'record' / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
                                                   encoding='utf-8')
    return [], manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('delivery')
    parser.add_argument('--input', action='append', default=[], metavar='NAME=PATH',
                        help='requirements, datasheets, previous version ... (referenced, not copied)')
    parser.add_argument('--wiki', type=Path, default=DEFAULT_WIKI, help='HardwareWiki root (env HARDWARE_WIKI)')
    args = parser.parse_args(argv)
    errors, _ = pack(args.delivery, dict(item.split('=', 1) for item in args.input), args.wiki)
    for e in errors:
        print('ERROR:', e)
    print('FAIL' if errors else 'PASS')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
