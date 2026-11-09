"""The newest row of docs/outline-approvals.md approves the outline as it is now."""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
import check_ledger  # noqa: E402


def record(rows):
    return '# 纲要确认记录\n\n| 确认 | 改了什么 | 纲要哈希 | 用户原话 |\n|---|---|---|---|\n' + ''.join(
        '| %s | %s | %s | %s |\n' % r for r in rows)


class OutlineApprovalTests(unittest.TestCase):
    def test_real_record_approves_the_current_outline(self):
        self.assertEqual([], check_ledger.check(check_ledger.RECORD.read_text(encoding='utf-8')))

    def test_only_the_newest_row_is_judged(self):
        current = check_ledger.outline_hash()
        good = record([('user:2026-11-08', '改了 1.3', current, '按草案改'), ('user:2026-10-23', '旧的', '0' * 16, '')])
        self.assertEqual([], check_ledger.check(good))

    def test_stale_hash_or_missing_approval_fails(self):
        current = check_ledger.outline_hash()
        stale = check_ledger.check(record([('user:2026-11-08', '改了 1.3', '0' * 16, '')]))
        self.assertTrue(any('不是当前纲要' in p for p in stale), stale)
        unapproved = check_ledger.check(record([('同意', '改了 1.3', current, '')]))
        self.assertTrue(any('user:<日期>' in p for p in unapproved), unapproved)
        self.assertTrue(check_ledger.check(record([('user:2026-11-08', '', current, '')])))
        self.assertTrue(check_ledger.check('# 纲要确认记录\n'))

    def test_outline_hash_follows_outline_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, _ in check_ledger.OUTLINE:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text((check_ledger.ROOT / name).read_text(encoding='utf-8'), encoding='utf-8')
            self.assertEqual(check_ledger.outline_hash(), check_ledger.outline_hash(root))
            skill = root / 'SKILL.md'
            skill.write_text(skill.read_text(encoding='utf-8').replace('P1 证据', 'P1 证据改'), encoding='utf-8')
            self.assertNotEqual(check_ledger.outline_hash(), check_ledger.outline_hash(root))

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'a.md'
            p.write_text(record([('user:2026-11-08', 'x', check_ledger.outline_hash(), '')]), encoding='utf-8')
            self.assertEqual(0, check_ledger.main([str(p)]))
            p.write_text(record([('user:2026-11-08', 'x', '0' * 16, '')]), encoding='utf-8')
            self.assertEqual(1, check_ledger.main([str(p)]))
            self.assertEqual(0, check_ledger.main(['--outline-hash']))


if __name__ == '__main__':
    unittest.main()
