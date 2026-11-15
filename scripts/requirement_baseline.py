#!/usr/bin/env python3
"""Write 设计资料/需求基线.md from record/requirements.json: requirement_baseline.py <交付目录> [--check].

The requirement baseline is what the design was made against: the original requirement clauses plus the
clauses the user (or the delegate named in the task) decided in clarification. It is the one requirement
file a delivery hands to later stages (independent review, PCB): they do not read record/. Generated, never
hand-written; --check exits 1 when the file is missing or differs from a fresh rendering.
"""
import argparse
import json
import sys
from pathlib import Path

NAME = '设计资料/需求基线.md'
DECISIONS = {'DECIDED': '用户给定', 'ADOPTED_PROPOSAL': '采纳建议'}


def cell(text):
    return str(text or '').replace('|', '\\|').replace('\n', ' ')


def render(requirements):
    sources = {e.get('id'): e for e in requirements.get('evidence') or [] if isinstance(e, dict)}
    asked = {q.get('id'): q for q in requirements.get('clarifications') or [] if isinstance(q, dict)}
    derating = requirements.get('derating') or {}
    out = ['# 需求基线', '',
           '本文件由 `requirement_baseline.py` 从 `record/requirements.json` 生成，不手改。它是本设计所依据的全部需求：'
           '原始需求条文，加上设计过程中由用户（或任务书授权的代答人）在需求澄清中定下的条文。'
           '澄清条文与原始需求文件有出入时，以澄清条文为准。', '',
           '降额等级：%s 级（依据 %s）。' % (derating.get('level', '未定'), str(derating.get('source') or '未写').replace('req:', '')), '',
           '## 需求条文', '', '| 编号 | 条文 | 来源 |', '|---|---|---|']
    for r in requirements.get('requirements') or []:
        answer = (asked.get(r.get('id')) or {}).get('answer') or {}
        if answer.get('decision') in DECISIONS:
            q = asked[r['id']]
            source = '需求澄清（涉及 %s）：%s，%s %s' % (
                '、'.join(q.get('requirement_ids') or []) or '原需求未提及', DECISIONS[answer['decision']],
                answer.get('by', ''), answer.get('date', ''))
        else:
            source = '；'.join('%s（%s）' % (sources[e].get('path', ''), sources[e].get('locator', ''))
                              for e in r.get('evidence') or [] if e in sources)
        out.append('| %s | %s | %s |' % (r.get('id'), cell(r.get('text')), cell(source)))
    deferred = [q for q in asked.values() if (q.get('answer') or {}).get('decision') == 'DEFERRED']
    if deferred:
        out += ['', '## 用户暂缓的澄清', '',
                # Not an id column (编号): a tool that transcribes requirement tables must not take these as clauses.
                '下面各项用户明确暂缓，还不是需求；设计按建议条文作为假设，定下之前不作为验收依据。', '',
                '| 澄清项 | 涉及的需求 | 问题 | 设计暂按的假设 |', '|---|---|---|---|']
        out += ['| %s | %s | %s | %s |' % (q.get('id'), '、'.join(q.get('requirement_ids') or []), cell(q.get('question')),
                                         cell(q.get('proposed_requirement'))) for q in deferred]
    out += ['', '## 原始需求文件', '', '| 文件 | 位置 | SHA-256 |', '|---|---|---|']
    out += ['| %s | %s | %s |' % (cell(e.get('path')), cell(e.get('locator')), e.get('sha256', ''))
            for e in sources.values()]
    return '\n'.join(out) + '\n'


def problem(root):
    """Why 设计资料/需求基线.md is not this record's baseline, or None."""
    root = Path(root)
    path = root / NAME
    if not path.is_file():
        return '缺少 %s：交给后续环节的需求基线，由 requirement_baseline.py 从 record/requirements.json 生成' % NAME
    source = root / 'record' / 'requirements.json'
    if path.read_text(encoding='utf-8') != render(json.loads(source.read_text(encoding='utf-8'))):
        return '%s 与 record/requirements.json 重新生成的不一致：重新生成，不手改' % NAME
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('delivery', type=Path)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args(argv)
    if args.check:
        found = problem(args.delivery)
        print(found or 'PASS')
        return 1 if found else 0
    target = args.delivery / NAME
    target.parent.mkdir(exist_ok=True)
    target.write_text(render(json.loads((args.delivery / 'record' / 'requirements.json').read_text(encoding='utf-8'))),
                      encoding='utf-8')
    print(target)
    return 0


if __name__ == '__main__':
    sys.exit(main())
