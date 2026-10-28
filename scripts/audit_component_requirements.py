#!/usr/bin/env python3
"""Check a component performance record; optionally prepare IR and canonical BOM.

Preparation is explicit (--project-intent/--write-bom) and precedes drawing.
Default operation only audits; it never repairs an exported schematic or BOM.
"""
import argparse
import json
from pathlib import Path

from schematic_layout.component_requirements import audit, project, write_bom


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('record', type=Path)
    ap.add_argument('--intent', type=Path, required=True)
    ap.add_argument('--artifact-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--project-intent', type=Path)
    ap.add_argument('--write-bom', type=Path)
    ap.add_argument('--input', action='append', default=[], metavar='NAME=PATH')
    for name in ('bom', 'xml', 'schematic', 'pdf'):
        ap.add_argument('--' + name, type=Path)
    args = ap.parse_args(argv)
    try:
        record = json.loads(args.record.read_text(encoding='utf-8'))
        intent = json.loads(args.intent.read_text(encoding='utf-8'))
        inputs = dict(item.split('=', 1) for item in args.input) if args.input else None
        if args.project_intent:
            intent = project(intent, record, args.artifact_root, inputs)
            args.project_intent.write_text(json.dumps(intent, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if args.write_bom:
            if not args.project_intent:
                ap.error('--write-bom requires --project-intent; avoid generating from stale IR')
            write_bom(intent, args.write_bom)
        result = audit(intent, record, args.artifact_root, inputs=inputs,
                       **{k: getattr(args, k) for k in ('bom', 'xml', 'schematic', 'pdf')})
    except (ValueError, OSError, TypeError, KeyError) as exc:
        result = {'status': 'FAIL', 'errors': [str(exc)], 'pending': []}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(result['status'])
    return 1 if result['status'] == 'FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())
