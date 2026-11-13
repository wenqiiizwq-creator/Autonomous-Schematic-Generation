"""A fact is written in one place, and nothing is left behind unused (user 2026-11-11: 都进行改动).

The stale text found on 2026-11-11 was all of three kinds: a numbered range repeated outside the file that owns it
(绘图纲要 O1–O8 written six times, missed when H1–H8 was added), the README copying SKILL.md's module table, and a
module nobody imported any more (placement.py).
"""
import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
# Used by both skills, byte-identical; some of their functions are only the other skill's.
SHARED = {'guideline_criteria.py', 'stress_check.py', 'knowledge_source.py'}
# A range of rule numbers starts at 1 (P0–P3 is the work-item priority scale, not the principles).
RANGE = re.compile(r'(?<![\w-])(?:[OHP]1|HR-01)\s*[–-]\s*(?:[OHP]|HR-)?\d+')
OWNERS = {'O': 'references/drawing-recipes.md', 'H': 'references/drawing-recipes.md',
          'HR': 'references/human-readable-routing.md', 'P': 'SKILL.md'}


def docs():
    return [ROOT / 'README.md', ROOT / 'SKILL.md', SCRIPTS / 'README.md'] + sorted((ROOT / 'references').rglob('*.md'))


def sources():
    return sorted(p for p in SCRIPTS.rglob('*.py') if '__pycache__' not in p.parts)


class SingleSourceTests(unittest.TestCase):
    def test_a_rule_range_is_written_only_in_the_file_that_owns_the_rules(self):
        found = []
        for path in docs():
            name = str(path.relative_to(ROOT))
            for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                for hit in RANGE.findall(line):
                    if OWNERS[re.match(r'HR|[OHP]', hit).group()] != name:
                        found.append('%s:%d %s' % (name, n, hit))
        self.assertEqual([], found, '编号范围只写在定义它的文件里，别处写“绘图纲要”“核心原则”“HR 规则”')

    def test_the_range_pattern_catches_the_repeats_it_was_written_for(self):
        self.assertTrue(RANGE.search('按绘图纲要 O1–O8 决定'))
        self.assertTrue(RANGE.search('HR-01–HR-11'))
        self.assertFalse(RANGE.search('C1–C6'))

    def test_the_readme_does_not_restate_the_module_table(self):
        text = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertEqual([], re.findall(r'C[1-6] [一-鿿]+', text), '模块名和入口只写在 SKILL.md')

    def test_every_script_is_imported_or_documented(self):
        text = ''.join(p.read_text(encoding='utf-8') for p in docs())
        code = {p: p.read_text(encoding='utf-8') for p in sources() + sorted((ROOT / 'tests').glob('*.py'))}
        unused = []
        for path in sources():
            if path.name == '__init__.py':
                continue
            word = re.compile(r'(?<!\w)%s(?!\w)' % re.escape(path.stem))
            if path.name not in text and not any(word.search(src) for other, src in code.items() if other != path):
                unused.append(str(path.relative_to(ROOT)))
        self.assertEqual([], unused, '没有脚本导入、文档也没提到的模块：删掉，或写明谁用它')

    def test_every_top_level_name_is_used_somewhere(self):
        code = {p: p.read_text(encoding='utf-8') for p in sources()}
        tests = ''.join(p.read_text(encoding='utf-8') for p in (ROOT / 'tests').glob('*.py'))
        unused = []
        for path, src in code.items():
            if path.name in SHARED:
                continue
            for node in ast.parse(src).body:
                names = []
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    names = [node.name]
                elif isinstance(node, ast.Assign):
                    names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                for name in names:
                    word = re.compile(r'(?<!\w)%s(?!\w)' % re.escape(name))
                    if name != 'main' and sum(len(word.findall(s)) for s in code.values()) <= 1 and not word.search(tests):
                        unused.append('%s %s' % (path.relative_to(ROOT), name))
        self.assertEqual([], unused, '只定义、没有任何脚本或测试用到的函数或常量')


if __name__ == '__main__':
    unittest.main()
