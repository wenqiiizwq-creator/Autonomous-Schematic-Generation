"""SKILL.md and references use one word per concept (references/terminology.md, 技能文档用词; user:2026-10-26)."""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import render_design_report

TERMS = ROOT / 'references' / 'terminology.md'


def doc_banned_words():
    table = TERMS.read_text(encoding='utf-8').split('## 技能文档用词', 1)[1].split('\n## ', 1)[0]
    words = []
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and len(cells) == 3 and not set(cells[2]) <= set('-') and cells[2] != '不用的词':
            words += [w for w in re.split(r'[、,，]', cells[2]) if w.strip()]
    return words


def pattern(word):
    # 脚号 inside 引脚号 is the unified term, not the banned one.
    return re.compile(('(?<!引)' if word.startswith('脚') else '') + re.escape(word))


def skill_docs():
    return [ROOT / 'SKILL.md'] + sorted(p for p in (ROOT / 'references').rglob('*.md') if p != TERMS)


class TerminologyTests(unittest.TestCase):
    def test_table_lists_the_replaced_words(self):
        self.assertIn('设计要求表', doc_banned_words())
        self.assertIn('脚号', doc_banned_words())

    def test_skill_docs_use_the_unified_words(self):
        found = []
        for path in skill_docs():
            for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                found += ['%s:%d %s' % (path.relative_to(ROOT), n, w) for w in doc_banned_words() if pattern(w).search(line)]
        self.assertEqual([], found)

    def test_a_replaced_word_is_caught(self):
        self.assertTrue(pattern('脚号').search('物理脚号'))
        self.assertFalse(pattern('脚号').search('物理引脚号'))

    def test_report_table_still_parses_alone(self):
        words = render_design_report.banned_terms()
        self.assertIn('门禁', words)
        self.assertNotIn('设计要求表', words)

    def test_a_markdown_table_in_notes_is_not_a_banned_word(self):
        # Matrix R3 S30: the table's header and |---| delimiter row were read as banned words.
        words = render_design_report.banned_terms()
        self.assertNotIn('---', words)
        self.assertNotIn('不用的词', words)
        table = '| 项 | R2 | R3 |\n|---|---|---|\n| 入口 | A | B |'
        self.assertEqual([], render_design_report.check_terms([('notes.json differences', table)]))
        self.assertTrue(render_design_report.check_terms([('notes.json summary', '门禁全部通过')]))


if __name__ == '__main__':
    unittest.main()
