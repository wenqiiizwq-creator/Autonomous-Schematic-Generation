#!/usr/bin/env python3
"""Check a component performance record; optionally prepare IR and canonical BOM.

Preparation is explicit (--project-intent/--write-bom) and precedes drawing and the design closure's intent_sha256.
It rewrites the IR only when the projection changes it; default operation only audits and writes nothing but --out.
"""
import argparse
import json
import sys
from pathlib import Path

from schematic_layout.component_requirements import audit, project, write_bom


def write_projection(intent, path):
    """Write the projected IR only when its content changes (PoE 2026-11-07 #15): re-running the preparation after the
    design closure was written must not touch the netlist and stale its intent_sha256. A real change says so."""
    try:
        if json.loads(path.read_text(encoding='utf-8')) == intent:
            return False
    except (OSError, ValueError):
        pass
    path.write_text(json.dumps(intent, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('PROJECTED: %s 已按性能要求改写；design-closure 的 intent_sha256 要按新文件重写后再跑闭环审计' % path,
          file=sys.stderr)
    return True


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
            write_projection(intent, args.project_intent)
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
