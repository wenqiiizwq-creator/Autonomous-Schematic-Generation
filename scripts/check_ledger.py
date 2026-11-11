#!/usr/bin/env python3
"""The ASG outline changes only with a person's approval.

The 纲要 (SKILL.md 「ASG 纲要（核心标准）」 and 「主流程」, references/drawing-recipes.md 「绘图纲要」) is
hashed; the newest row of docs/outline-approvals.md must carry the current hash and a `user:<date>`.
"""

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / 'docs' / 'outline-approvals.md'
# (file, heading) of each outline section; a section runs to the next level-2 heading.
OUTLINE = (('SKILL.md', '## ASG 纲要（核心标准）'), ('SKILL.md', '## 主流程'),
           ('references/drawing-recipes.md', '## 绘图纲要（怎样决定结构）'))
APPROVED = re.compile(r'^user:\d{4}-\d{2}-\d{2}$')


def outline_hash(root=ROOT):
    digest = hashlib.sha256()
    for name, heading in OUTLINE:
        text = (root / name).read_text(encoding='utf-8')
        start = text.find('\n' + heading + '\n')
        if start < 0:
            raise ValueError('%s: heading %r not found' % (name, heading))
        end = text.find('\n## ', start + len(heading) + 2)
        digest.update(text[start:end if end >= 0 else len(text)].strip().encode('utf-8'))
    return digest.hexdigest()[:16]


def rows(text):
    """Data rows of the approval table: [approved, what, hash, quote]."""
    out = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')] if line.startswith('|') else []
        if len(cells) == 4 and cells[0] != '确认' and not set(cells[0]) <= set('-: '):
            out.append(cells)
    return out


def check(text, root=ROOT):
    table = rows(text)
    if not table:
        return ['docs/outline-approvals.md 没有纲要确认记录']
    approved, what, recorded, _ = table[0]
    problems = []
    if not APPROVED.match(approved):
        problems.append('第一行的确认要写 user:<日期>（现在是 %r）' % approved)
    if not what:
        problems.append('第一行要写改了什么')
    current = outline_hash(root)
    if recorded != current:
        problems.append('第一行的纲要哈希 %s 不是当前纲要 %s：纲要改动须先经人确认，再在最上面加一行' % (recorded, current))
    return problems


def main(argv=None):
    argv = list(argv or [])
    if argv[:1] == ['--outline-hash']:
        print(outline_hash())
        return 0
    path = Path(argv[0]) if argv else RECORD
    problems = check(path.read_text(encoding='utf-8'))
    for p in problems:
        print('PROBLEM:', p)
    print('FAIL' if problems else 'PASS')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
