#!/usr/bin/env python3
"""核对设计目录中任务 C3.1（模块 C3）的方案准则记录。

只核对方案记录本身：留给任务 C4.2 的数值是否闭合由 C4 的关卡核对，方案与分页方案是否一致由 C6 的关卡核对
（`check_module.py`），整板报告两项都核对。"""
import argparse
from pathlib import Path

from render_design_report import check_scheme_criteria, load


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('design_root', type=Path, help='设计目录（含 record/）')
    args = parser.parse_args(argv)
    record = args.design_root / 'record'
    # The guideline scope is module C1's product (requirements.json); C3 does not read design-closure.json.
    closure, problem = load(record / 'requirements.json')
    problems = [problem] if problem else []
    if not problem and not isinstance(closure, dict):
        problems.append('record/requirements.json 要写 JSON 对象')
    scheme, problem = None, None
    if (record / 'scheme-criteria.json').exists():
        scheme, problem = load(record / 'scheme-criteria.json')
    if problem:
        problems.append(problem)
    if not problems:
        problems += check_scheme_criteria(scheme, closure, deferred=False)
    for problem in problems:
        print('PROBLEM:', problem)
    print('FAIL' if problems else 'PASS')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
