"""SKILL.md 主流程: five steps of at most five numbered tasks, each ending with 做完的标志, matching the 架构 table (user:2026-10-26)."""
from pathlib import Path
import re
import unittest

SKILL = (Path(__file__).resolve().parents[1] / 'SKILL.md').read_text(encoding='utf-8')
STEP_MARKS = '①②③④⑤'


def body_steps():
    flow = SKILL.split('\n## 主流程\n', 1)[1].split('\n## ', 1)[0]
    steps = []
    for block in re.split(r'\n(?=### )', flow)[1:]:
        title = block.splitlines()[0][4:].strip()
        tasks = [(m.group(1), m.group(2).strip(), text)
                 for m, text in zip(re.finditer(r'^#### (\d+\.\d+) (.+)$', block, re.M),
                                    re.split(r'\n(?=#### )', block)[1:])]
        steps.append((title, tasks))
    return steps


def table_steps():
    arch = SKILL.split('\n### 架构\n', 1)[1].split('\n### ', 1)[0]
    rows = []
    for line in arch.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and cells[0][:1] in STEP_MARKS:
            rows.append((cells[0], [t.strip() for t in cells[1].split('·')]))
    return rows


class SkillStepTests(unittest.TestCase):
    def test_five_steps_of_one_to_five_numbered_tasks(self):
        steps = body_steps()
        self.assertEqual(list(STEP_MARKS), [title[0] for title, _ in steps])
        for n, (title, tasks) in enumerate(steps, 1):
            self.assertTrue(1 <= len(tasks) <= 5, title)
            self.assertEqual(['%d.%d' % (n, k) for k in range(1, len(tasks) + 1)], [num for num, _, _ in tasks], title)

    def test_every_task_ends_with_its_done_mark(self):
        for _, tasks in body_steps():
            for num, name, text in tasks:
                last = [p for p in re.split(r'\n\s*\n', text.strip()) if p.strip()][-1]
                self.assertTrue(last.startswith('做完的标志：'), '%s %s' % (num, name))

    def test_architecture_table_matches_the_body(self):
        body = [(title, ['%s %s' % (num, name) for num, name, _ in tasks]) for title, tasks in body_steps()]
        self.assertEqual(body, table_steps())

    def test_task_1_3_ends_with_the_scheme_record_check(self):
        task = next(text for _, tasks in body_steps() for num, _, text in tasks if num == '1.3')
        self.assertTrue(task.rstrip().endswith(
            '写完运行 `check_scheme_criteria.py <设计目录>`，无问题再结束任务 1.3。'))

    def test_design_steps_never_write_new_datasheets_into_the_library(self):
        # SKILL.md 2.1 资料规则 (2026-11-04); Matrix R3 S01: references and the cadence still said to file into HardwareWiki.
        root = Path(__file__).resolve().parents[1]
        docs = [root / 'SKILL.md'] + sorted((root / 'references').rglob('*.md'))
        stale = re.compile(r'同时存入\s*HardwareWiki|规则存入库里|读过的手册都在知识库里')
        found = ['%s:%d' % (p.relative_to(root), n) for p in docs
                 for n, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1) if stale.search(line)]
        self.assertEqual([], found)


if __name__ == '__main__':
    unittest.main()
