#!/usr/bin/env python3
"""ASG 跑电路评测集。

prepare：把一个案例的需求摘录放进新工作目录，写好任务提示。案例只给需求，不给网表和测试点，设计完成前不要打开 case.json。
score：设计交付后，由 SR 或人对照测试点写 run.json（skill 写 ASG，variant 写交付名），打分时只算 asg 为 must 的测试点，期望一律是 pass。

    python3 evals/circuit_cases/run.py list
    python3 evals/circuit_cases/run.py prepare --case iio-can --out <新目录>
    python3 evals/circuit_cases/run.py score <run.json>
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'evals'))
import eval_set  # noqa: E402

PROMPT = """使用当前 autonomous-schematic-generation 技能，只读本目录的 需求.md，产品基线 {baseline}。
本任务只设计“{title}”这一个电路，电路类型至少包含 {types}。从任务 1.1 开始走完步骤①～⑤，交付到本目录。
未答复的澄清项不得当成已确认要求。不要读取评测集里的 case.json、网表或其他版本的设计。
技能提交：{commit}。
"""


def tool():
    if not eval_set.available():
        sys.exit(f'电路评测集不在 {eval_set.root()}；设 CIRCUIT_EVAL_SET 指向它')
    sys.path.insert(0, str(eval_set.root() / '工具'))
    import evalset
    return evalset


def cmd_prepare(args):
    evalset = tool()
    found = {c['id']: (p, c) for p, c in evalset.load_cases()}
    if args.case not in found or 'ASG' not in found[args.case][1]['skills']:
        sys.exit(f'{args.case} 不是 ASG 案例')
    path, case = found[args.case]
    if args.out.exists() and any(args.out.iterdir()):
        sys.exit(f'{args.out} 不是空目录')
    args.out.mkdir(parents=True, exist_ok=True)
    shutil.copy(path.parent / '需求.md', args.out / '需求.md')
    commit = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    (args.out / '任务.md').write_text(PROMPT.format(baseline='industrial_telecom', title=case['title'], types='、'.join(case['circuit_types']), commit=commit), encoding='utf-8')
    print(args.out / '任务.md')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    p = sub.add_parser('prepare')
    p.add_argument('--case', required=True)
    p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('score')
    p.add_argument('run')
    args = parser.parse_args()
    if args.command == 'prepare':
        return cmd_prepare(args) or 0
    if args.command == 'list':
        return tool().main(['list', '--skill', 'ASG'])
    return tool().main(['score', args.run, '--json'])


if __name__ == '__main__':
    sys.exit(main())
