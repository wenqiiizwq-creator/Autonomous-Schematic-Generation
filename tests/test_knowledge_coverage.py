"""对照表的条数从条目里数；docs/knowledge-coverage.md 的内容类别、关卡列与脚本的 KINDS 一致（条数随知识框架变，不比较）。"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import knowledge_coverage as c
import knowledge_source

import pytest

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


def test_the_written_table_has_the_kinds_and_gates_of_the_script():
    try:
        knowledge_source.framework_root()
    except knowledge_source.KnowledgeFrameworkNotFound as exc:
        pytest.skip('没有配置知识框架：%s' % exc)
    rows = c.measure()
    assert all(entries and items for _, _, entries, items, *_ in rows)     # a kind that counts nothing has lost its format
    written = [line.split('|')[1:-1] for line in c.OUT.read_text(encoding='utf-8').splitlines() if c.ROW.match(line)][1:]
    # columns: 组件, 内容, 条目数, 项数, 哪项任务用, 关卡现在核对什么, 核对到内容 (the two counts follow the framework)
    keep = lambda cells: [cells[0].strip(), cells[1].strip(), cells[4].strip(), cells[5].strip(), cells[6].strip()]
    expected = [keep(['`%s/`' % r[0], r[1], r[2], r[3], r[4], r[5], '是' if r[6] else '否']) for r in rows]
    assert [keep(cells) for cells in written] == expected
