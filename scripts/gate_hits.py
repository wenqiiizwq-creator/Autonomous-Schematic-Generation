#!/usr/bin/env python3
"""Which gate rules stopped these designs, and how often: gate_hits.py <设计目录> [<设计目录> ...] [--json].

Reads record/gate-log.jsonl (check_module.py writes one line per gate run). A problem is counted once per design and
module however many gate runs repeat it; `runs` is how many gate runs reported it. The rule is the audit code where
the problem carries one, else the problem text with its numbers and designators taken out.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CODE = re.compile(r'(?<![A-Za-z_])[a-z][a-z0-9]*(?:_[a-z0-9]+)+(?![A-Za-z_.])')
VARIABLE = re.compile(r'[A-Z]+\d+[A-Z]?(?:\.\w+)?|[A-Z]{1,4}-[\w-]+|\d+(?:\.\d+)?|[0-9a-f]{12,}')


def rule(problem):
    found = CODE.search(problem.split('：')[0])
    return found.group(0) if found else VARIABLE.sub('#', problem)[:48]


def tally(roots):
    hits = defaultdict(lambda: {'problems': set(), 'runs': 0, 'modules': set(), 'designs': set()})
    gates = failed = 0
    for root in roots:
        path = Path(root) / 'record' / 'gate-log.jsonl'
        if not path.is_file():
            print('没有 %s' % path, file=sys.stderr)
            continue
        for line in path.read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            gates += 1
            failed += bool(row['problems'])
            for name in {rule(p) for p in row['problems']}:
                hits[name]['runs'] += 1
            for problem in row['problems']:
                entry = hits[rule(problem)]
                entry['problems'].add((str(root), row['module'], problem))
                entry['modules'].add(row['module'])
                entry['designs'].add(str(root))
    return gates, failed, hits


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('designs', nargs='+', type=Path)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)
    gates, failed, hits = tally(args.designs)
    rows = sorted(({'rule': name, 'problems': len(h['problems']), 'runs': h['runs'], 'designs': len(h['designs']),
                    'modules': sorted(h['modules'])} for name, h in hits.items()), key=lambda r: (-r['problems'], r['rule']))
    if args.json:
        print(json.dumps({'gate_runs': gates, 'failed': failed, 'rules': rows}, ensure_ascii=False, indent=2))
        return 0
    print('关卡运行 %d 次，%d 次不通过；报过问题的规则 %d 条' % (gates, failed, len(rows)))
    print('| 规则 | 不同的问题 | 报出的关卡运行 | 设计数 | 模块 |\n|---|---|---|---|---|')
    for r in rows:
        print('| %s | %d | %d | %d | %s |' % (r['rule'], r['problems'], r['runs'], r['designs'], '、'.join(r['modules'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
