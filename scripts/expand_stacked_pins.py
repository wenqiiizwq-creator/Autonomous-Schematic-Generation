#!/usr/bin/env python3
"""把叠脚的每个物理脚写进设计网表（KiCad 叠脚 [17,18]，或 KiCad 库“一个可见脚 + 同点隐藏副本”的写法）。

KiCad 把画在同一点的脚连成一个网络，导出 XML 时逐脚列出；ASG 的设计网表也逐脚写，网表核对才对得上。
设计网表只写了其中一个脚时，本脚本把同点的其余脚补进同一网络；同点的脚分在不同网络或标了不连接时报错。

    python3 expand_stacked_pins.py record/electrical-intent.json [--symbol-dir 原理图] [--write]
"""
import argparse
import json
import sys
from pathlib import Path

from schematic_layout.circuit_ir import expand_stacked_pins


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('intent', type=Path)
    ap.add_argument('--symbol-dir', action='append', default=[], help='项目符号库所在目录（可重复）')
    ap.add_argument('--write', action='store_true', help='写回设计网表；不写时只列出要补的脚')
    args = ap.parse_args(argv)
    try:
        intent = json.loads(args.intent.read_text(encoding='utf-8'))
        result, added = expand_stacked_pins(intent, args.symbol_dir)
    except (OSError, ValueError, KeyError) as exc:
        print('FAIL:', exc, file=sys.stderr)
        return 1
    for line in added:
        print(line)
    if added and args.write:
        args.intent.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('%s: %d pad(s)%s' % ('WRITTEN' if added and args.write else 'OK' if not added else 'TO ADD', len(added),
                              '' if args.write or not added else '; rerun with --write'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
