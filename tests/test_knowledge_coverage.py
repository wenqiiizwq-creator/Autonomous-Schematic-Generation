"""对照表的条数从条目里数；docs/knowledge-coverage.md 与现装的知识一致（同步后要重写）。"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import knowledge_coverage as c
import knowledge_package

ENTRY = '''# 例

## 来源

| 编号 | 文件 |
|---|---|
| S1 | a.pdf |

## 取值顺序

| 步 | 定什么 |
|---|---|
| 1 | 甲 |
| 2 | 乙 |

## 算完之后的核对

- 一
- 二
- 三

## 实现方案

### 方案甲

- **必算项**：
  - 压差
  - 功耗
- **已知坑**：
  - 坑
### 方案乙

- **必算项**：
  - 电流
'''


def test_counts_come_from_the_entry_text():
    assert c.rows_in('取值顺序')(ENTRY) == 2
    assert c.rows_outside_sources(ENTRY) == 2          # the source table is not counted
    assert c.bullets_in('算完之后的核对')(ENTRY) == 3
    assert c.headings_in('实现方案')(ENTRY) == 2
    assert [c.checklist_items(k)(ENTRY) for k in ('必算项', '已知坑', '取值步骤', '算完核对')] == [3, 1, 2, 3]


def test_the_written_table_matches_the_installed_knowledge():
    rows = c.measure()
    assert all(entries and items for _, _, entries, items, *_ in rows)     # a kind that counts nothing has lost its format
    assert c.OUT.read_text(encoding='utf-8') == c.render(rows, knowledge_package.manifest()['knowledge_version'])
