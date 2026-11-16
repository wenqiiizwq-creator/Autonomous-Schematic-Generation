#!/usr/bin/env python3
"""知识必答清单：设计用到的知识条目里每一项，设计都要写处置（落实在哪，或不适用及理由）。

  python3 knowledge_checklist.py build <设计目录>     按当前记录重写 record/knowledge-checklist.json 的清单，保留已写的处置
  python3 knowledge_checklist.py check <设计目录> [--module C1|C4] [--block <块>]

清单不手抄，由本工具从知识框架（知识/）的条目里抽：
  C1  任务 C1.1 查到的需求要素条目（查阅记录里 `需求要素/端口/`、`需求要素/全板/` 下的）：每个条件一项
  C4  各功能块选定的典型电路实现方案（块文件 schemes[].selected.circuit）：必算项、必需外围、已知坑各一项；
      任务 C4.x 查到的计算方法条目：取值顺序整条一项（哪条计算照它算的）、算完之后的核对每条一项
每项写 `disposition`：`covered`（`where` 写落实在哪）或 `not_applicable`（`reason` 写理由）。`where` 是列表：
  条件 → 需求或澄清的编号；必算项、取值步骤、算完核对 → design-closure.json 的计算编号；
  必需外围 → 块设计里的位号；已知坑 → 怎样避开的说明。
只问与本板有关的：
  需求要素条目里标了“适用前提：X”的小节，只有清单顶层 `applies` 列了 X 才问（`build` 会列出条目里出现过哪些前提）。
  清单顶层 `groups`：[{"module", "entry", "group"（条目里的三级标题，不写就是整个条目）, "reason"}]，这一组的项整组不适用。
  条件项可写 `not_required`：需求没有要求这一条，本设计不做，`reason` 写一句为什么可以不做；不另提需求澄清。
选定方案自己的项（有 `scheme` 的）不筛、不成组、不能写 not_required。
条目改了（框架里的文字变了）对应项的编号就变，原处置作废，重跑 build 后补写。关卡是 check_module.py 的 C1、C4。
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import knowledge_source

FILE = 'knowledge-checklist.json'
SCHEMA_VERSION = 1
SCHEME_KINDS = ('必算项', '必需外围', '已知坑')
REQUIREMENT_FOLDERS = ('需求要素/端口/', '需求要素/全板/')
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')
# kind -> which ids `where` must name (None: free text saying how)
WHERE = {'条件': 'requirements', '必算项': 'calculations', '取值顺序': 'calculations', '算完核对': 'calculations',
         '必需外围': 'refs', '已知坑': None}
WHERE_WORDS = {'requirements': 'requirements.json 的需求或澄清编号', 'calculations': 'design-closure.json 的计算编号',
               'refs': '块设计里的位号'}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def clean(line):
    return LINK.sub(r'\1', line).strip()


def sections(body):
    found, current = {}, None
    for line in body.splitlines():
        if line.startswith('## '):
            current = found.setdefault(line[3:].strip(), [])
        elif current is not None:
            current.append(line)
    return found


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def tables(lines):
    """[(header cells, [row cells])] of the tables in these lines."""
    out, current = [], None
    for line in lines:
        if not line.startswith('|'):
            current = None
        elif current is None:
            current = (cells(line), [])
            out.append(current)
        elif not re.match(r'^\|\s*:?-{3}', line):
            current[1].append(cells(line))
    return out


PRECONDITION = re.compile(r'^适用前提[：:]\s*(\S.*?)\s*$')


def grouped(lines):
    """[(三级标题 or None, 适用前提 or None, lines)] of one section, split at its ### headings."""
    out = [[None, None, []]]
    for line in lines:
        if line.startswith('### '):
            out.append([line[4:].strip(), None, []])
            continue
        found = PRECONDITION.match(line)
        if found and not out[-1][2] and '（' not in found.group(1):      # the line right under the heading names it
            out[-1][1] = found.group(1)
        elif line.strip() or out[-1][2]:
            out[-1][2].append(line)
    return [tuple(g) for g in out]


def extra(group, precondition=None, unwritten=None):
    return {k: v for k, v in (('group', group), ('precondition', precondition), ('unwritten', unwritten)) if v}


def requirement_rows(body):
    """(kind, text, {group, precondition, unwritten}) per row of every table whose first column is 条件."""
    out = []
    for name, lines in sections(body).items():
        if name.startswith('来源'):
            continue
        for group, precondition, part in grouped(lines):
            for header, rows in tables(part):
                if not header or header[0] != '条件':
                    continue
                column = header.index('没写时') if '没写时' in header else None
                out += [('条件', clean(row[0]), extra(group, precondition, clean(row[column]) if column is not None and len(row) > column else None))
                        for row in rows if row and row[0]]
    return out


def requirement_items(body):
    """One item per row of every table whose first column is 条件."""
    return [row[:2] for row in requirement_rows(body)]


def unnumbered(title):
    """A scheme title without its ordinal: the block file may name 「2. 集成 eFuse」 as 「集成 eFuse」 (H-001 rerun
    2026-11-15: the missing ordinal sent C4 back to C3)."""
    return re.sub(r'^\d+[.、．]\s*', '', title.strip())


def scheme_items(body, scheme):
    """The second-level bullets under 必算项 / 必需外围 / 已知坑 of one 「### scheme」 of a typical circuit; None when
    the entry has no such implementation."""
    out, inside, kind = [], False, None
    seen = False
    for line in sections(body).get('实现方案', []):
        if line.startswith('### '):
            inside, kind = unnumbered(line[4:]) == unnumbered(scheme), None
            seen = seen or inside
        elif inside and line.startswith('- **'):
            kind = next((k for k in SCHEME_KINDS if line.startswith('- **%s**' % k)), None)
            rest = line.partition('：')[2].strip()
            if kind and rest and not rest.startswith('无'):      # the item written on the bullet's own line
                out.append((kind, clean(rest)))
        elif inside and kind and line.startswith('  - '):
            out.append((kind, clean(line[4:])))
    return out if seen else None


def method_rows(body):
    parts = sections(body)
    steps = [('取值步骤', clean('第 %s 步：%s' % (row[0], row[1])), extra(group))
             for group, _, part in grouped(parts.get('取值顺序', [])) for header, rows in tables(part) for row in rows if len(row) > 1]
    return steps + [('算完核对', clean(line[2:]), {}) for line in parts.get('算完之后的核对', []) if line.startswith('- ')]


def method_items(body):
    return [row[:2] for row in method_rows(body)]


def method_checklist(body):
    """What a calculation method asks of the design: one item for its 取值顺序 as a whole (which calculation followed
    it), one per line of 算完之后的核对. The steps themselves are how to calculate, not separate obligations: asked one
    by one they were 63 of 211 items on a 20-part board, 34 of them answered not applicable (H-001 2026-11-16)."""
    rows = method_rows(body)
    whole = [('取值顺序', '按本条目的取值顺序算（%d 步）' % sum(r[0] == '取值步骤' for r in rows), {})] \
        if any(r[0] == '取值步骤' for r in rows) else []
    return whole + [r for r in rows if r[0] == '算完核对']


def keyed(source, pairs):
    """Checklist rows of one source: the id is a hash of kind and text, numbered when an entry repeats a line."""
    rows, seen = [], {}
    for kind, words, *more in pairs:
        digest = hashlib.sha256(('%s\n%s' % (kind, words)).encode('utf-8')).hexdigest()[:10]
        seen[digest] = seen.get(digest, 0) + 1
        rows.append(dict(source, kind=kind, id=digest if seen[digest] == 1 else '%s-%d' % (digest, seen[digest]), text=words,
                         **(more[0] if more else {})))
    return rows


def load(path):
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def lookups(record, module, component):
    rows = load(record / 'modules.json').get('knowledge_lookups') or []
    found = [e for r in rows if isinstance(r, dict) and str(r.get('task') or '').startswith(module + '.')
             and r.get('component') == component for e in r.get('found') or [] if isinstance(e, str)]
    return sorted(set(e for e in found if Path(e).name != 'README.md' and (knowledge_source.knowledge_dir() / e).is_file()))


def circuit_file(stem):
    hits = sorted((knowledge_source.knowledge_dir() / '典型电路').rglob(stem + '.md'))
    return hits[0] if len(hits) == 1 else None


def required(record, module, block=None):
    """(checklist rows the design has to answer, problems reading what they come from)."""
    rows, problems = [], []
    if module == 'C1':
        for entry in lookups(record, 'C1', '需求要素'):
            if entry.startswith(REQUIREMENT_FOLDERS):
                rows += keyed({'entry': entry}, requirement_rows((knowledge_source.knowledge_dir() / entry).read_text(encoding='utf-8')))
        return rows, problems
    folder = record / 'block-circuits'
    for path in sorted(folder.glob('*.json')) if folder.is_dir() else []:
        if block and path.stem != block:
            continue
        for scheme in load(path).get('schemes') or []:
            circuit = ((scheme or {}).get('selected') or {}).get('circuit')
            if not text(circuit) or '#' not in circuit:
                continue
            stem, _, name = circuit.partition('#')
            md = circuit_file(stem)
            pairs = scheme_items(md.read_text(encoding='utf-8'), name) if md else None
            if pairs is None:
                problems.append('块 %s 选定的 %s 在知识框架的典型电路里找不到' % (path.stem, circuit))
                continue
            rows += keyed({'block': path.stem, 'entry': md.relative_to(knowledge_source.knowledge_dir()).as_posix(), 'scheme': name}, pairs)
    if not block:
        for entry in lookups(record, 'C4', '计算方法'):
            rows += keyed({'entry': entry}, method_checklist((knowledge_source.knowledge_dir() / entry).read_text(encoding='utf-8')))
    return rows, problems


def key(row):
    return tuple(row.get(k) for k in ('block', 'entry', 'scheme', 'kind', 'id'))


def label(row):
    where = '块 %s ' % row['block'] if row.get('block') else ''
    return '%s%s%s 的%s“%s”' % (where, row['entry'], '#' + row['scheme'] if row.get('scheme') else '', row['kind'],
                               row['text'] if len(row['text']) <= 40 else row['text'][:40] + '…')


def known_ids(record):
    requirements = load(record / 'requirements.json')
    closure = load(record / 'design-closure.json')
    ids = lambda rows: {r.get('id') for r in rows or [] if isinstance(r, dict) and text(r.get('id'))}
    refs = set()
    for path in sorted((record / 'blocks').glob('*.json')) if (record / 'blocks').is_dir() else []:
        refs |= {c.get('ref') for c in load(path).get('components') or [] if isinstance(c, dict) and text(c.get('ref'))}
    return {'requirements': ids(requirements.get('requirements')) | ids(requirements.get('clarifications')),
            'calculations': ids(closure.get('calculations')), 'refs': refs}


def group_answers(data, module):
    """(适用前提 the board declares, {(entry, group or None)} answered not applicable as a whole, problems)."""
    found = []
    applies = data.get('applies') if isinstance(data.get('applies'), list) else []
    groups = set()
    for row in data.get('groups') or []:
        if not isinstance(row, dict) or row.get('module') != module:
            continue
        if not text(row.get('entry')) or not text(row.get('reason')):
            found.append('必答清单 groups：每条写 module、entry、reason，只对条目里的一组时另写 group')
            continue
        groups.add((row['entry'], row.get('group') or None))
    return {a for a in applies if text(a)}, groups, found


def answered_as_a_group(row, applies, groups):
    """Not asked of this board: under a 适用前提 the board does not declare, or in a group answered as a whole.
    A selected scheme's own items are always asked: the scheme was chosen for this board."""
    if row.get('scheme'):
        return False
    return (row.get('precondition') and row['precondition'] not in applies) or (row['entry'], None) in groups \
        or bool(row.get('group') and (row['entry'], row['group']) in groups)


def problems(root, module, block=None):
    """What keeps the module's checklist from being answered (empty when every item has a valid disposition)."""
    record = Path(root) / 'record'
    wanted, found = required(record, module, block)
    if not wanted:
        return found
    data = load(record / FILE)
    written = {key(r): r for r in data.get(module) or [] if isinstance(r, dict)}
    applies, groups, trouble = group_answers(data, module)
    found += trouble
    known = known_ids(record)
    missing = 0
    for row in wanted:
        answer, name = written.get(key(row)), label(row)
        if answered_as_a_group(row, applies, groups):
            continue
        if answer is None:
            missing += 1
        elif answer.get('disposition') == 'not_required':
            if row['kind'] != '条件' or row.get('scheme'):
                found.append('必答清单 %s：not_required 只用于需求要素的条件' % name)
            elif not text(answer.get('reason')):
                found.append('必答清单 %s：not_required 要在 reason 写为什么可以不做' % name)
        elif answer.get('disposition') == 'not_applicable':
            if not text(answer.get('reason')):
                found.append('必答清单 %s：不适用要在 reason 写理由' % name)
        elif answer.get('disposition') == 'covered':
            where = answer.get('where')
            if not (isinstance(where, list) and where and all(text(w) for w in where)):
                found.append('必答清单 %s：covered 要在 where 列出落实在哪' % name)
            elif WHERE[row['kind']]:
                unknown = [w for w in where if w not in known[WHERE[row['kind']]]]
                if unknown:
                    found.append('必答清单 %s：where 的 %s 不是%s' % (name, '、'.join(unknown), WHERE_WORDS[WHERE[row['kind']]]))
        else:
            found.append('必答清单 %s：还没有写处置（disposition 写 covered、not_applicable，条件项还可写 not_required）' % name)
    if missing:
        found.append('record/%s 的 %s 缺 %d 项（知识条目或选定方案变了）：重跑 knowledge_checklist.py build 后补写处置' % (FILE, module, missing))
    return found


def build(root):
    """Rewrite the checklist from the current records; dispositions already written stay with their items."""
    record = Path(root) / 'record'
    old = load(record / FILE)
    data, found = {'schema_version': SCHEMA_VERSION}, []
    for name in ('applies', 'groups'):
        if old.get(name):
            data[name] = old[name]
    for module in ('C1', 'C4'):
        written = {key(r): r for r in old.get(module) or [] if isinstance(r, dict)}
        rows, read_problems = required(record, module)
        found += read_problems
        data[module] = [dict(row, **{k: written.get(key(row), {}).get(k, default)
                                     for k, default in (('disposition', ''), ('where', []), ('reason', ''))}) for row in rows]
    record.mkdir(parents=True, exist_ok=True)
    (record / FILE).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data, found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('command', choices=('build', 'check'))
    ap.add_argument('root', type=Path)
    ap.add_argument('--module', choices=('C1', 'C4'))
    ap.add_argument('--block')
    args = ap.parse_args(argv)
    if args.command == 'build':
        data, found = build(args.root)
        for module in ('C1', 'C4'):
            applies, groups, _ = group_answers(data, module)
            skipped = sum(1 for r in data[module] if answered_as_a_group(r, applies, groups))
            todo = sum(1 for r in data[module] if r['disposition'] not in ('covered', 'not_applicable', 'not_required')
                       and not answered_as_a_group(r, applies, groups))
            print('%s：%d 项，其中 %d 项不问（适用前提没有声明，或成组不适用），%d 项还没有处置' % (module, len(data[module]), skipped, todo))
        seen = sorted({r['precondition'] for r in data['C1'] if r.get('precondition')})
        if seen:
            declared = group_answers(data, 'C1')[0]
            print('条目里的适用前提：%s；本板声明的（清单顶层 applies）：%s' % ('、'.join(seen), '、'.join(sorted(declared)) or '无'))
    else:
        found = [p for m in ([args.module] if args.module else ['C1', 'C4']) for p in problems(args.root, m, args.block if m == 'C4' else None)]
    print('\n'.join(found + ['FAIL' if found else 'PASS']))
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
