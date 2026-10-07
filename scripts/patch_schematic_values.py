#!/usr/bin/env python3
"""Create a native-verified candidate with byte-preserving Value-only edits."""
import argparse
import json
from pathlib import Path
from schematic_layout.value_patch import apply

if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('root', type=Path)
    cli.add_argument('--contract', type=Path, required=True)
    cli.add_argument('--out', type=Path, required=True)
    cli.add_argument('--kicad-cli')
    args = cli.parse_args()
    try:
        result = apply(args.root, json.loads(args.contract.read_text()), args.out, args.kicad_cli)
    except (ValueError, OSError) as exc:
        cli.exit(2, str(exc) + '\n')
    print(result['status'])
    raise SystemExit(0 if result['status'] == 'PATCH_VERIFIED' else 3)
