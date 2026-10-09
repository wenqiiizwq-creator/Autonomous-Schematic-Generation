#!/usr/bin/env python3
"""Read-only hash/coverage gate for a saved KiCad evidence snapshot.

FRESH means the declared inputs and outputs are unchanged; it does NOT mean
ERC, geometry, visual review or electrical qualification passed.
"""
import argparse
import hashlib
import json
from pathlib import Path
from schematic_layout.native_hierarchy import NativeHierarchy

REQUIRED_ROLES = {'netlist', 'erc', 'geometry', 'render'}

def check(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    base = manifest_path.parent
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
                elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
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
        ancillary = [root.with_suffix('.kicad_pro'), base / 'sym-lib-table']
        ancillary += list((base / 'symbols').glob('*.kicad_sym'))
        for path in ancillary:
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
