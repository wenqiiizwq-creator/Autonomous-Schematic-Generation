#!/usr/bin/env python3
"""列出适用设计准则（技能侧包装，输出与 `guideline_criteria.py select` 相同）。

`guideline_criteria.py select` 的 --circuit-type/--device-kind 每个值要单独写一次选项；
这里一个选项可接多个值，逗号或空格分隔都行（zsh 里不分词的 "$TYPES" 也能用），也可直接读设计记录的 guideline_scope。

    python3 select_guidelines.py --circuit-type POWER_PROTECTION DC_24V --device-kind tvs,mosfet --typed-only
    python3 select_guidelines.py --scope DESIGN/record/requirements.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

import guideline_criteria


def split_values(values):
    out = []
    for value in values:
        out += [v for v in re.split(r'[,\s]+', value) if v]
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--bundle', default=None, help='准则汇编 JSON；不写则从知识框架的准则登记汇编')
    parser.add_argument('--scope', type=Path, help='requirements.json：取其 guideline_scope 的基线、电路类型、器件类别')
    parser.add_argument('--baseline')
    parser.add_argument('--circuit-type', nargs='+', action='extend', default=[])
    parser.add_argument('--device-kind', nargs='+', action='extend', default=[])
    parser.add_argument('--typed-only', action='store_true')
    parser.add_argument('--ports', action='store_true')
    args = parser.parse_args(argv)
    baseline, types, kinds = args.baseline, split_values(args.circuit_type), split_values(args.device_kind)
    if args.scope:
        scope = json.loads(args.scope.read_text(encoding='utf-8')).get('guideline_scope')
        if not isinstance(scope, dict):
            print('%s 没有 guideline_scope' % args.scope, file=sys.stderr)
            return 1
        baseline = baseline or scope.get('baseline')
        types += [t for t in scope.get('circuit_types') or [] if t not in types]
        kinds += [k for k in scope.get('device_kinds') or [] if k not in kinds]
    bundle = guideline_criteria.load(args.bundle)
    errors = guideline_criteria.bundle_errors(bundle)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    # guideline_criteria CLI 也只做 argparse 后转调 select；保持同一输出格式
    return guideline_criteria.main(['select'] + ([args.bundle] if args.bundle else []) + (['--baseline', baseline] if baseline else [])
                                   + sum((['--circuit-type', t] for t in types), [])
                                   + sum((['--device-kind', k] for k in kinds), [])
                                   + (['--typed-only'] if args.typed_only else [])
                                   + (['--ports'] if args.ports else []))


if __name__ == '__main__':
    sys.exit(main())
