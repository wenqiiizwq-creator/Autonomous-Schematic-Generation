#!/usr/bin/env python3
"""核对设计目录中任务 1.3 的方案准则记录。"""
import argparse
from pathlib import Path

from render_design_report import check_scheme_criteria, load


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('design_root', type=Path, help='设计目录（含 record/）')
    args = parser.parse_args(argv)
    record = args.design_root / 'record'
    closure, problem = load(record / 'design-closure.json')
    problems = [problem] if problem else []
    if not problem and not isinstance(closure, dict):
        problems.append('record/design-closure.json 要写 JSON 对象')
    scheme, problem = None, None
    if (record / 'scheme-criteria.json').exists():
        scheme, problem = load(record / 'scheme-criteria.json')
    if problem:
        problems.append(problem)
    plan = None
    if (record / 'page-plan.json').exists():
        plan, problem = load(record / 'page-plan.json')
        if problem:
            problems.append(problem)
        elif not isinstance(plan, dict) or not isinstance(plan.get('pages'), list):
            problems.append('record/page-plan.json 要写带 pages 列表的对象')
    if not problems:
        problems += check_scheme_criteria(scheme, closure, plan=plan)
    for problem in problems:
        print('PROBLEM:', problem)
    print('FAIL' if problems else 'PASS')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
