"""Documents of the skill never tell the designer to file new datasheets into the library."""
from pathlib import Path
import re
import unittest


class SkillStepTests(unittest.TestCase):
    def test_design_steps_never_write_new_datasheets_into_the_library(self):
        # 资料规则 (2026-11-04); Matrix R3 S01: references and the cadence still said to file into HardwareWiki.
        root = Path(__file__).resolve().parents[1]
        docs = [root / 'SKILL.md'] + sorted((root / 'references').rglob('*.md'))
        stale = re.compile(r'同时存入\s*HardwareWiki|规则存入库里|读过的手册都在知识库里')
        found = ['%s:%d' % (p.relative_to(root), n) for p in docs
                 for n, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1) if stale.search(line)]
        self.assertEqual([], found)


if __name__ == '__main__':
    unittest.main()
