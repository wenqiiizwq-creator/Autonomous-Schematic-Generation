#!/usr/bin/env python3
"""ASG 跑电路评测集。

prepare：把一个案例的需求摘录放进新工作目录，写好任务提示。案例只给需求，不给网表和测试点，设计完成前不要打开 case.json。
score：设计交付后，由 SR 或人对照测试点写 run.json（skill 写 ASG，variant 写交付名），打分时只算 asg 为 must 的测试点，期望一律是 pass。

    python3 evals/circuit_cases/run.py list
    python3 evals/circuit_cases/run.py prepare --case iio-can --out <新目录> --guideline-release <发布包>
    python3 evals/circuit_cases/run.py score <run.json> --guideline-release <发布包>
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'evals'))
import eval_set  # noqa: E402

PROMPT = """使用当前 autonomous-schematic-generation 技能，只读本目录的 需求.md，产品基线 {baseline}。
本任务只设计“{title}”这一个电路，电路类型至少包含 {types}。{scope}
未答复的澄清项不得当成已确认要求。不要读取评测集里的 case.json、网表或其他版本的设计。
技能提交：{commit}。
"""


def tool():
    return eval_set.tool()

def cmd_prepare(args):
    evalset = tool()
    context = eval_set.context(args.guideline_release, ROOT)
    found = {c['id']: (p, c) for p, c in evalset.load_cases()}
    if args.case not in found or 'ASG' not in found[args.case][1]['skills']:
        sys.exit(f'{args.case} 不是 ASG 案例')
    path, case = found[args.case]
    criteria, _ = evalset.binding.release_context(args.guideline_release)
    errors = evalset.check_case(path, case, criteria)
    if errors:
        raise ValueError('; '.join(errors))
    context['case_inputs'] = evalset.binding.case_inputs(path)
    if args.out.exists() and any(args.out.iterdir()):
        sys.exit(f'{args.out} 不是空目录')
    args.out.mkdir(parents=True, exist_ok=True)
    shutil.copy(path.parent / '需求.md', args.out / '需求.md')
    commit = context['skill']['head']
    (args.out / 'run-context.json').write_text(json.dumps(dict(skill='ASG', skill_commit=commit, case=args.case,
                                                               evaluation=context), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.out / '任务.md').write_text(PROMPT.format(baseline='industrial_telecom', title=case['title'], types='、'.join(case['circuit_types']), commit=commit,
        scope='本案例只评步骤①的方案选择，写出方案和决定条件，不生成原理图。' if case.get('test_points') and all(p['kind'] == 'route' for p in case['test_points']) else '从任务 1.1 开始走完步骤①～⑤，交付到本目录。'), encoding='utf-8')
    print(args.out / '任务.md')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    p = sub.add_parser('prepare')
    p.add_argument('--case', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--guideline-release', type=Path, required=True)
    p = sub.add_parser('score')
    p.add_argument('run')
    p.add_argument('--guideline-release', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        return cmd_prepare(args) or 0
    if args.command == 'list':
        return tool().main(['list', '--skill', 'ASG'])
    return tool().main(['score', args.run, '--json', '--guideline-release', str(args.guideline_release), '--skill-root', str(ROOT)])


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
