#!/usr/bin/env python3
"""Bring the derived parts of a design's records up to date: refresh.py <设计目录> [--module C4|C5].

What follows from other records by rule is written here, not by hand, and a module gate (check_module.py C4, C5)
runs this first; the audits then judge what the designer wrote. Derived, by module:

  C4  the performance contract and its fields on each part of the block designs (or of the design netlist when the
      design has no block designs), from record/component-requirements.json;
      each calculation's conclusion, rests_on and coverage, from its checks, parameters, omitted terms and work items.
  C5  record/electrical-intent.json, merged from the block designs once C5 has written it;
      design-closure.json intent_sha256;
      a traced requirement written design_supported that rests on a calculation not supported becomes conditional.

Not derived, never touched: the visual review's PDF hash. Without --module both parts run.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import audit_design_closure as closure_audit
import blocks
from schematic_layout import component_requirements


def load(path):
    try:
        data = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def write(path, data, old, done, what):
    if data != old:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        done.append(what)


def project_contracts(root, done, skipped):
    record = root / 'record'
    import check_module     # it runs this module before its gates
    requirements = load(record / 'component-requirements.json')
    if requirements is None:
        return
    digest = component_requirements.projection_digest(requirements)
    found, _ = blocks.read_dir(record)
    targets = [(record / blocks.DIR / (key + '.json'), data) for key, data in sorted(found.items()) if key != blocks.BOARD]
    if not targets and load(record / 'electrical-intent.json') is not None:
        targets = [(record / 'electrical-intent.json', load(record / 'electrical-intent.json'))]
    for path, design in targets:
        refs = {c.get('ref') for c in design.get('components') or [] if isinstance(c, dict)}
        part = check_module.requirements_for(requirements, refs)
        if not part['components']:
            continue
        try:
            projected = component_requirements.project(design, part, root, digest=digest)
        except (ValueError, KeyError, TypeError) as exc:
            skipped.append('%s 的性能要求没有投影（记录有错，关卡会列出）：%s' % (path.name, str(exc)[:200]))
            continue
        write(path, projected, design, done, '%s：器件的性能合同与字段' % path.relative_to(root))


def derive_calculations(root, done):
    path = root / 'record' / 'design-closure.json'
    closure = load(path)
    if closure is None:
        return
    new = json.loads(json.dumps(closure))
    derived = closure_audit.derived_calculations(new)
    for row in new.get('calculations') or []:
        found = derived.get(row.get('id')) if isinstance(row, dict) else None
        if not found:
            continue
        row['conclusion'], row['coverage'] = found['conclusion'], found['coverage']
        if found['rests_on'] is None:
            row.pop('rests_on', None)
        else:
            row['rests_on'] = found['rests_on']
    write(path, new, closure, done, 'record/design-closure.json：计算的 conclusion、rests_on、coverage')


def merge_board(root, done, skipped):
    record = root / 'record'
    path = record / 'electrical-intent.json'
    found, _ = blocks.read_dir(record)
    if path.is_file() and any(key != blocks.BOARD for key in found):
        intent, problems = blocks.merge_record(root)
        if problems or intent is None:
            skipped.append('electrical-intent.json 没有重新合并（块设计合并有错，关卡会列出）')
        else:
            write(path, intent, load(path), done, 'record/electrical-intent.json：由块设计合并')
    closure = load(record / 'design-closure.json')
    if closure is None:
        return
    new = json.loads(json.dumps(closure))
    if path.is_file():
        new['intent_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    derived = closure_audit.derived_calculations(new)
    for row in new.get('traceability') or []:
        if isinstance(row, dict) and row.get('status') == 'design_supported' and any(
                row.get('requirement') in (c.get('requirements') or [])
                and derived.get(c.get('id'), {}).get('conclusion') != 'supported'
                for c in new.get('calculations') or [] if isinstance(c, dict)):
            row['status'] = 'conditional'
    write(record / 'design-closure.json', new, closure, done, 'record/design-closure.json：intent_sha256、需求追溯的状态')


def refresh(root, module=None):
    """(what was rewritten, what could not be derived). Writes a file only when its content changes."""
    root = Path(root)
    done, skipped = [], []
    if module in (None, 'C4'):
        project_contracts(root, done, skipped)
        derive_calculations(root, done)
    if module in (None, 'C5'):
        merge_board(root, done, skipped)
    return done, skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('design_root', type=Path)
    ap.add_argument('--module', choices=('C4', 'C5'))
    args = ap.parse_args(argv)
    done, skipped = refresh(args.design_root, args.module)
    for line in done:
        print('REFRESHED:', line)
    for line in skipped:
        print('SKIPPED:', line)
    if not done and not skipped:
        print('派生量都是最新的')
    return 0


if __name__ == '__main__':
    sys.exit(main())
