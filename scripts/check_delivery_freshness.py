#!/usr/bin/env python3
"""Read-only hash/coverage gate for a saved KiCad evidence snapshot.

FRESH means the declared inputs and outputs are unchanged; it does NOT mean
ERC, geometry, visual review or electrical qualification passed.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from schematic_layout.native_hierarchy import NativeHierarchy

REQUIRED_ROLES = {'netlist', 'erc', 'geometry', 'render'}
# The KiCad project file is shared by the schematic and the board in 设计方案/ (user 2026-11-13). Its `board` section holds
# only the board's design rules, so the evidence hashes the project without it: a board-rule edit leaves the schematic
# evidence fresh, while net classes and everything else the schematic reads still count.
BOARD_ONLY = ('board',)
# A project's frozen library copy lives in 库快照/ (Hardware-Library tools/project_snapshot.py, user 2026-11-13) and its
# rows in sym-lib-table point there. The schematic embeds its symbols, so those rows are not schematic evidence.
SNAPSHOT_DIR = '库快照'
LIB_ROW = re.compile(r'\(lib \(name "[^"]*"\).*?\(uri "([^"]*)"\).*?\)\s*(?=\(lib |\)\s*$)', re.S)


def snapshot_rows(text):
    """The rows of a library table that point into the project's 库快照/."""
    return [m.group(0).strip() for m in LIB_ROW.finditer(text) if '/%s/' % SNAPSHOT_DIR in m.group(1)]


def evidence_sha256(path):
    """SHA-256 a delivery's evidence records for one file: a .kicad_pro without its board-only sections, a sym-lib-table
    by its library rows without the ones pointing into 库快照/."""
    path = Path(path)
    if path.suffix == '.kicad_pro':
        try:
            project = json.loads(path.read_text(encoding='utf-8'))
        except ValueError:
            project = None
        if isinstance(project, dict):
            shared = {k: v for k, v in project.items() if k not in BOARD_ONLY}
            return hashlib.sha256(json.dumps(shared, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
    if path.name == 'sym-lib-table':
        text = path.read_text(encoding='utf-8')
        rows = [m.group(0).strip() for m in LIB_ROW.finditer(text) if m.group(0).strip() not in snapshot_rows(text)]
        return hashlib.sha256('\n'.join(rows).encode('utf-8')).hexdigest()
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    base = manifest_path.parent
    if base.name == 'record':  # delivery folder layout: paths are relative to the folder holding record/
        base = base.parent
    errors = []
    def local(name):
        if not isinstance(name, str) or not name or Path(name).is_absolute():
            raise ValueError('Expected a nonempty relative path')
        path = (base / name).resolve()
        if not path.is_relative_to(base):
            raise ValueError('Path escapes the delivery root: ' + name)
        return path
    try:
        m = json.loads(manifest_path.read_text())
        if set(m) != {'schema_version', 'root', 'inputs', 'outputs', 'roles'} or m['schema_version'] != 1:
            raise ValueError('Invalid manifest schema')
        for section in ('inputs', 'outputs'):
            if not isinstance(m[section], dict) or not m[section]:
                raise ValueError(section + ' must contain path-to-SHA256 entries')
            for name, expected in m[section].items():
                path = local(name)
                if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
                    raise ValueError('Invalid SHA256 for ' + name)
                if not path.is_file():
                    errors.append({'kind': 'missing_file', 'path': name})
                elif evidence_sha256(path) != expected:
                    errors.append({'kind': 'changed_' + section, 'path': name})
        if not isinstance(m['roles'], dict):
            raise ValueError('roles must be an object')
        for role in REQUIRED_ROLES | set(m['roles']):
            paths = m['roles'].get(role)
            if not isinstance(paths, list) or not paths or not all(isinstance(p, str) and p in m['outputs'] for p in paths):
                errors.append({'kind': 'missing_role_evidence', 'role': role})
        # Derive active hierarchy coverage independently of the manifest list.
        context = NativeHierarchy(local(m['root']), base=base, annotations=False)
        errors.extend(context.file_errors)
        for relative in context.file_sha256:
            if relative not in m['inputs']:
                errors.append({'kind': 'untracked_active_sheet', 'path': relative})
        root = local(m['root'])
        ancillary = [root.with_suffix('.kicad_pro'), root.parent / 'sym-lib-table']
        ancillary += list((root.parent / 'symbols').glob('*.kicad_sym'))
        for path in ancillary:
            if path.name == 'sym-lib-table' and path.is_file() and not [  # only 库快照 rows: nothing the schematic evidence covers
                    r for r in LIB_ROW.finditer(path.read_text(encoding='utf-8')) if '/%s/' % SNAPSHOT_DIR not in r.group(1)]:
                continue
            if path.is_file() and path.relative_to(base).as_posix() not in m['inputs']:
                errors.append({'kind': 'untracked_project_input', 'path': path.relative_to(base).as_posix()})
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        errors.append({'kind': 'invalid_manifest_or_input', 'detail': str(exc)})
    return {'status': 'STALE_OR_INVALID' if errors else 'FRESH',
            'scope': 'Hash integrity and declared evidence coverage only; no design acceptance.',
            'errors': errors}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    result = check(args.manifest)
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'FRESH' else 2

if __name__ == '__main__':
    raise SystemExit(main())
