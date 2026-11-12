#!/usr/bin/env python3
"""知识到关卡的对照表：知识包里每类可核对的内容有多少项，C1–C5 的关卡现在核对到哪一步，还差什么。

  python3 knowledge_coverage.py            打印对照表
  python3 knowledge_coverage.py --write    写进 docs/knowledge-coverage.md（每次同步知识后重写）

条数从 references/knowledge/ 的条目里数出来；“关卡现在核对什么”一列是本文件的 KINDS 表，按关卡代码的实际行为写：
给某类内容加了关卡，就改这里的 checked，对照表里它就不再算缺口。
"""
import re
import sys
from pathlib import Path

import knowledge_checklist as checklist

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / 'references' / 'knowledge'
OUT = ROOT / 'docs' / 'knowledge-coverage.md'
ROW = re.compile(r'^\|(?!\s*-{3})')            # a table line that is not the |---| separator
LOOKUP = '只核对查过这个组件（`knowledge_lookups` 有记录、所记条目存在）'
ANSWERED = '必答清单：设计用到的条目，这类内容逐项写处置，%s（`knowledge_checklist.py`，%s 关卡）'


def sections(text):
    """{## heading: [lines]} of one entry."""
    found, current = {}, None
    for line in text.splitlines():
        if line.startswith('## '):
            current = found.setdefault(line[3:].strip(), [])
        elif current is not None:
            current.append(line)
    return found


def table_rows(lines):
    """Data rows of the tables in these lines (each table's header row is not counted)."""
    count, in_table = 0, False
    for line in lines:
        if ROW.match(line):
            count += in_table
            in_table = True
        elif not line.startswith('|'):
            in_table = False
    return count


def rows_outside_sources(text):
    return sum(table_rows(lines) for name, lines in sections(text).items() if not name.startswith('来源'))


def rows_in(*names):
    return lambda text: sum(table_rows(lines) for name, lines in sections(text).items() if name in names)


def bullets_in(name):
    return lambda text: sum(line.startswith('- ') for line in sections(text).get(name, []))


def headings_in(name):
    return lambda text: sum(line.startswith('### ') for line in sections(text).get(name, []))


def checklist_items(kind):
    """How many checklist items of this kind knowledge_checklist.py draws from one entry."""
    def count(body):
        if kind == '条件':
            return len(checklist.requirement_items(body))
        if kind in checklist.SCHEME_KINDS:
            names = [line[4:].strip() for line in sections(body).get('实现方案', []) if line.startswith('### ')]
            return sum(k == kind for name in names for k, _ in checklist.scheme_items(body, name) or [])
        return sum(k == kind for k, _ in checklist.method_items(body))
    return count


# (组件下的目录, 这类内容, 怎么数, 哪项任务用, 关卡现在核对什么, 是否核对到内容)
KINDS = (
    ('需求要素/端口', '端口要给定的条件', checklist_items('条件'), 'C1.1', ANSWERED % ('落实处写需求或澄清编号', 'C1'), True),
    ('需求要素/全板', '全板要给定的条件', checklist_items('条件'), 'C1.1', ANSWERED % ('落实处写需求或澄清编号', 'C1'), True),
    ('需求要素/环境与电磁等级', '标准等级对应的波形和数值', rows_outside_sources, 'C4.2、C5.2', LOOKUP, False),
    ('板级架构模式', '结构问题的做法', headings_in('做法'), 'C2.1', LOOKUP, False),
    ('板级架构模式', '块之间由此要交代的参数', lambda t: rows_in('块之间由此要交代的参数')(t) or bullets_in('块之间由此要交代的参数')(t),
     'C2.1', LOOKUP, False),
    ('接口约定/参数模板', '接口两端要交代的量', rows_outside_sources, 'C2.1、C3.3',
     LOOKUP + '；每条跨块流向只要求 `params` 非空，不对照模板的量', False),
    ('接口约定/总线与电平', '总线和电平的电气约定', rows_outside_sources, 'C2.1、C3.3', LOOKUP, False),
    ('典型电路', '实现方案', headings_in('实现方案'), 'C3.1',
     '关键功能块要有候选比较、恰好选定一个方案，标注的文件和方案名存在（`scheme-criteria.json`、分页方案）', True),
    ('典型电路', '实现方案的必算项', checklist_items('必算项'), 'C4.2', ANSWERED % ('落实处写计算编号', 'C4'), True),
    ('典型电路', '实现方案的必需外围', checklist_items('必需外围'), 'C4', ANSWERED % ('落实处写位号', 'C4'), True),
    ('典型电路', '实现方案的已知坑', checklist_items('已知坑'), 'C4', ANSWERED % ('落实处写怎样避开', 'C4'), True),
    ('计算方法', '取值步骤', checklist_items('取值步骤'), 'C4.2', ANSWERED % ('落实处写计算编号', 'C4'), True),
    ('计算方法', '算完之后的核对', checklist_items('算完核对'), 'C4.2', ANSWERED % ('落实处写计算编号', 'C4'), True),
    ('器件参数', '器件条目（保证值与页码）', lambda t: 1, 'C4.1、C4.3', LOOKUP + '；计算里用的保证值不对照条目', False),
    ('失效与故障分析/器件失效方式', '失效方式', rows_in('失效方式与比例'), 'C5.2', LOOKUP + '；FMEA 的行不对照失效方式', False),
    ('失效与故障分析/分析步骤', '分析步骤条目', lambda t: 1, 'C5.2', LOOKUP, False),
)


def entries(folder):
    return [p for p in sorted((KNOWLEDGE / folder).rglob('*.md')) if p.name != 'README.md']


def measure():
    """[(folder, kind, entries, items, task, gate, checked)] in KINDS order."""
    out = []
    for folder, kind, count, task, gate, checked in KINDS:
        files = entries(folder)
        out.append((folder, kind, len(files), sum(count(p.read_text(encoding='utf-8')) for p in files), task, gate, checked))
    return out


def render(rows, version):
    open_items = sum(r[3] for r in rows if not r[6])
    lines = ['# 知识到关卡的对照表', '',
             '由 `scripts/knowledge_coverage.py --write` 生成，依据知识框架 %s。每次同步知识后重写；给某类内容加了关卡，改脚本里的 `KINDS`。' % version, '',
             '“项数”是知识包里这类内容的条数（从条目的表格行、列表项、小标题数出来）。“核对到内容”为“否”的，'
             '关卡只知道设计时查过这个组件，不知道查到的内容有没有用上：这些就是技能还没吃进去的知识，共 %d 项（%d 类里的 %d 类）。'
             % (open_items, len(rows), sum(not r[6] for r in rows)), '',
             '| 组件 | 内容 | 条目数 | 项数 | 哪项任务用 | 关卡现在核对什么 | 核对到内容 |', '|---|---|---|---|---|---|---|']
    lines += ['| `%s/` | %s | %d | %d | %s | %s | %s |' % (r[0], r[1], r[2], r[3], r[4], r[5], '是' if r[6] else '否') for r in rows]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv not in ([], ['--write']):
        print(__doc__)
        return 2
    import knowledge_package
    text = render(measure(), knowledge_package.manifest()['knowledge_version'])
    if argv:
        OUT.write_text(text, encoding='utf-8')
    print(text, end='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
