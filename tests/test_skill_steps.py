"""SKILL.md 主流程: the six capability modules C1–C6 and then 交付, each module's tasks numbered Cn.1, Cn.2 … and each
task ending with 做完的标志, matching the 架构 module table (user:2026-10-26; modules user:2026-11-09 “确认写入”)."""
from pathlib import Path
import re
import unittest

SKILL = (Path(__file__).resolve().parents[1] / 'SKILL.md').read_text(encoding='utf-8')
MODULES = ['C%d' % k for k in range(1, 7)]


def body_sections():
    """[(section title, [(task number or None, task name, text)])] of 主流程."""
    flow = SKILL.split('\n## 主流程\n', 1)[1].split('\n## ', 1)[0]
    sections = []
    for block in re.split(r'\n(?=### )', flow)[1:]:
        title = block.splitlines()[0][4:].strip()
        tasks = []
        for text in re.split(r'\n(?=#### )', block)[1:]:
            head = text.splitlines()[0][5:].strip()
            m = re.match(r'^(C\d\.\d+) (.+)$', head)
            tasks.append((m.group(1), m.group(2), text) if m else (None, head, text))
        sections.append((title, tasks))
    return sections


def table_modules():
    """架构 module table: [(module, [task numbers])]; 'C6.1–C6.5' expands."""
    arch = SKILL.split('\n### 架构\n', 1)[1].split('\n### ', 1)[0]
    rows = []
    for line in arch.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and re.match(r'^C\d ', cells[0]):
            tasks = []
            for item in cells[1].split('·'):
                item = item.strip()
                span = re.match(r'^(C\d)\.(\d)–\1\.(\d)$', item)
                if span:
                    tasks += ['%s.%d' % (span.group(1), k) for k in range(int(span.group(2)), int(span.group(3)) + 1)]
                elif re.match(r'^C\d\.\d$', item):
                    tasks.append(item)
            rows.append((cells[0].split()[0], tasks))
    return rows


class SkillStepTests(unittest.TestCase):
    def test_six_modules_then_delivery(self):
        titles = [title for title, _ in body_sections()]
        self.assertEqual(MODULES + ['交付'], [t.split()[0] for t in titles])

    def test_module_tasks_are_numbered_in_order(self):
        for title, tasks in body_sections()[:6]:
            module = title.split()[0]
            self.assertTrue(1 <= len(tasks) <= 5, title)
            self.assertEqual(['%s.%d' % (module, k) for k in range(1, len(tasks) + 1)], [num for num, _, _ in tasks], title)

    def test_every_task_ends_with_its_done_mark(self):
        for _, tasks in body_sections():
            for num, name, text in tasks:
                last = [p for p in re.split(r'\n\s*\n', text.strip()) if p.strip()][-1]
                self.assertTrue(last.startswith('做完的标志：'), '%s %s' % (num, name))

    def test_architecture_table_matches_the_body(self):
        body = [(title.split()[0], [num for num, _, _ in tasks]) for title, tasks in body_sections()[:6]]
        self.assertEqual(body, table_modules())

    def test_task_c3_1_ends_with_the_scheme_record_check(self):
        task = next(text for _, tasks in body_sections() for num, _, text in tasks if num == 'C3.1')
        self.assertTrue(task.rstrip().endswith(
            '写完运行 `check_scheme_criteria.py <设计目录>`，无问题再结束任务 C3.1。'))

    def test_design_steps_never_write_new_datasheets_into_the_library(self):
        # SKILL.md C4.1 资料规则 (2026-11-04); Matrix R3 S01: references and the cadence still said to file into HardwareWiki.
        root = Path(__file__).resolve().parents[1]
        docs = [root / 'SKILL.md'] + sorted((root / 'references').rglob('*.md'))
        stale = re.compile(r'同时存入\s*HardwareWiki|规则存入库里|读过的手册都在知识库里')
        found = ['%s:%d' % (p.relative_to(root), n) for p in docs
                 for n, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1) if stale.search(line)]
        self.assertEqual([], found)


if __name__ == '__main__':
    unittest.main()
