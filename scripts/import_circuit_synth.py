#!/usr/bin/env python3
"""Convert an exported circuit-synth JSON into Circuit IR v2 for review."""

import argparse
import json
from pathlib import Path
import sys
from schematic_layout.importers import circuit_synth_to_ir


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("--design-id", required=True)
    ap.add_argument("--shared-net", action="append", default=[])
    ap.add_argument("--local-net", action="append", default=[])
    ap.add_argument("--no-connect", action="append", default=[])
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    if args.output_dir.exists():
        ap.error("output directory exists")
    try:
        doc, audit = circuit_synth_to_ir(
            json.loads(args.source.read_text()),
            args.design_id,
            args.shared_net,
            args.local_net,
            args.no_connect,
        )
        args.output_dir.mkdir(parents=True)
        for filename, content in (("circuit.json", doc), ("import-audit.json", audit)):
            (args.output_dir / filename).write_text(
                json.dumps(content, indent=2, ensure_ascii=False) + "\n"
            )
        print(
            json.dumps(
                {
                    "status": "IMPORTED_FOR_REVIEW",
                    "output": str(args.output_dir.resolve()),
                }
            )
        )
        return 0
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({"status": "FAIL", "error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
