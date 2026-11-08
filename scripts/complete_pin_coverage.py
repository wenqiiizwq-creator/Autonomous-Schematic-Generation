#!/usr/bin/env python3
"""补全设计网表的逐脚覆盖：叠脚的其余物理脚、库里标为不连接（no_connect）的脚。

1. 叠脚（KiCad [17,18]，或 KiCad 库“一个可见脚 + 同点隐藏副本”的写法）：KiCad 把同一点的脚连成一个网络，导出 XML 时逐脚列出；
   设计网表只写了其中一个脚时，把同点的其余脚补进同一网络。同点的脚分在不同网络或标了不连接时报错。
2. 库里类型为 no_connect 的脚（TPS26630RGE NC 19–24）：设计网表没写的补进 `no_connect`；已接进网络的只列出，不改——
   KiCad ERC 会报接了线的 no_connect 脚，手册允许接时改项目符号把它设成 passive。

    python3 complete_pin_coverage.py record/electrical-intent.json [--symbol-dir 原理图] [--write]
"""
import argparse
import json
import sys
from pathlib import Path

from schematic_layout.circuit_ir import expand_stacked_pins, library_no_connects


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('intent', type=Path)
    ap.add_argument('--symbol-dir', action='append', default=[], help='项目符号库所在目录（可重复）')
    ap.add_argument('--write', action='store_true', help='写回设计网表；不写时只列出要补的脚')
    args = ap.parse_args(argv)
    try:
        intent = json.loads(args.intent.read_text(encoding='utf-8'))
        result, stacked = expand_stacked_pins(intent, args.symbol_dir)
        result, no_connect, connected = library_no_connects(result, args.symbol_dir)
    except (OSError, ValueError, KeyError) as exc:
        print('FAIL:', exc, file=sys.stderr)
        return 1
    for line in stacked:
        print('stacked', line)
    for pid in no_connect:
        print('no_connect', pid)
    for pid in connected:
        print('CONNECTED_NC %s：库里标不连接却接进了网络；手册允许接时把项目符号的这个脚改成 passive' % pid)
    added = len(stacked) + len(no_connect)
    if added and args.write:
        args.intent.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('%s: %d pad(s)%s' % ('WRITTEN' if added and args.write else 'OK' if not added else 'TO ADD', added,
                              '' if args.write or not added else '; rerun with --write'))
    return 1 if connected else 0


if __name__ == '__main__':
    sys.exit(main())
