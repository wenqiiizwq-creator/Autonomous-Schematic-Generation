#!/usr/bin/env python3
"""知识必答清单：设计用到的知识条目里每一项，设计都要写处置（落实在哪，或不适用及理由）。

  python3 knowledge_checklist.py build <设计目录>     按当前记录重写 record/knowledge-checklist.json 的清单，保留已写的处置
  python3 knowledge_checklist.py check <设计目录> [--module C1|C4] [--block <块>]

清单不手抄，由本工具从知识包（references/knowledge/）的条目里抽：
  C1  任务 C1.1 查到的需求要素条目（查阅记录里 `需求要素/端口/`、`需求要素/全板/` 下的）：每个条件一项
  C4  各功能块选定的典型电路实现方案（块文件 schemes[].selected.circuit）：必算项、必需外围、已知坑各一项；
      任务 C4.x 查到的计算方法条目：取值顺序每步一项、算完之后的核对每条一项
每项写 `disposition`：`covered`（`where` 写落实在哪）或 `not_applicable`（`reason` 写理由）。`where` 是列表：
  条件 → 需求或澄清的编号；必算项、取值步骤、算完核对 → design-closure.json 的计算编号；
  必需外围 → 块设计里的位号；已知坑 → 怎样避开的说明。
条目改了（知识同步后文字变了）对应项的编号就变，原处置作废，重跑 build 后补写。关卡是 check_module.py 的 C1、C4。
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

KNOWLEDGE = Path(__file__).resolve().parent.parent / 'references' / 'knowledge'
FILE = 'knowledge-checklist.json'
SCHEMA_VERSION = 1
SCHEME_KINDS = ('必算项', '必需外围', '已知坑')
REQUIREMENT_FOLDERS = ('需求要素/端口/', '需求要素/全板/')
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')
# kind -> which ids `where` must name (None: free text saying how)
WHERE = {'条件': 'requirements', '必算项': 'calculations', '取值步骤': 'calculations', '算完核对': 'calculations',
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


def requirement_items(body):
    """One item per row of every table whose first column is 条件."""
    return [('条件', clean(row[0])) for name, lines in sections(body).items() if not name.startswith('来源')
            for header, rows in tables(lines) if header and header[0] == '条件' for row in rows if row and row[0]]


def scheme_items(body, scheme):
    """The second-level bullets under 必算项 / 必需外围 / 已知坑 of one 「### scheme」 of a typical circuit; None when
    the entry has no such implementation."""
    out, inside, kind = [], False, None
    seen = False
    for line in sections(body).get('实现方案', []):
        if line.startswith('### '):
            inside, kind = line[4:].strip() == scheme, None
            seen = seen or inside
        elif inside and line.startswith('- **'):
            kind = next((k for k in SCHEME_KINDS if line.startswith('- **%s**' % k)), None)
            rest = line.partition('：')[2].strip()
            if kind and rest and not rest.startswith('无'):      # the item written on the bullet's own line
                out.append((kind, clean(rest)))
        elif inside and kind and line.startswith('  - '):
            out.append((kind, clean(line[4:])))
    return out if seen else None


def method_items(body):
    parts = sections(body)
    steps = [('取值步骤', clean('第 %s 步：%s' % (row[0], row[1]))) for header, rows in tables(parts.get('取值顺序', []))
             for row in rows if len(row) > 1]
    return steps + [('算完核对', clean(line[2:])) for line in parts.get('算完之后的核对', []) if line.startswith('- ')]


def keyed(source, pairs):
    """Checklist rows of one source: the id is a hash of kind and text, numbered when an entry repeats a line."""
    rows, seen = [], {}
    for kind, words in pairs:
        digest = hashlib.sha256(('%s\n%s' % (kind, words)).encode('utf-8')).hexdigest()[:10]
        seen[digest] = seen.get(digest, 0) + 1
        rows.append(dict(source, kind=kind, id=digest if seen[digest] == 1 else '%s-%d' % (digest, seen[digest]), text=words))
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
    return sorted(set(e for e in found if Path(e).name != 'README.md' and (KNOWLEDGE / e).is_file()))


def circuit_file(stem):
    hits = sorted((KNOWLEDGE / '典型电路').rglob(stem + '.md'))
    return hits[0] if len(hits) == 1 else None


def required(record, module, block=None):
    """(checklist rows the design has to answer, problems reading what they come from)."""
    rows, problems = [], []
    if module == 'C1':
        for entry in lookups(record, 'C1', '需求要素'):
            if entry.startswith(REQUIREMENT_FOLDERS):
                rows += keyed({'entry': entry}, requirement_items((KNOWLEDGE / entry).read_text(encoding='utf-8')))
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
                problems.append('块 %s 选定的 %s 在知识包的典型电路里找不到' % (path.stem, circuit))
                continue
            rows += keyed({'block': path.stem, 'entry': md.relative_to(KNOWLEDGE).as_posix(), 'scheme': name}, pairs)
    if not block:
        for entry in lookups(record, 'C4', '计算方法'):
            rows += keyed({'entry': entry}, method_items((KNOWLEDGE / entry).read_text(encoding='utf-8')))
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


def problems(root, module, block=None):
    """What keeps the module's checklist from being answered (empty when every item has a valid disposition)."""
    record = Path(root) / 'record'
    wanted, found = required(record, module, block)
    if not wanted:
        return found
    written = {key(r): r for r in load(record / FILE).get(module) or [] if isinstance(r, dict)}
    known = known_ids(record)
    missing = 0
    for row in wanted:
        answer, name = written.get(key(row)), label(row)
        if answer is None:
            missing += 1
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
            found.append('必答清单 %s：还没有写处置（disposition 写 covered 或 not_applicable）' % name)
    if missing:
        found.append('record/%s 的 %s 缺 %d 项（知识条目或选定方案变了）：重跑 knowledge_checklist.py build 后补写处置' % (FILE, module, missing))
    return found


def build(root):
    """Rewrite the checklist from the current records; dispositions already written stay with their items."""
    record = Path(root) / 'record'
    old = load(record / FILE)
    data, found = {'schema_version': SCHEMA_VERSION}, []
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
            todo = sum(1 for r in data[module] if r['disposition'] not in ('covered', 'not_applicable'))
            print('%s：%d 项，其中 %d 项还没有处置' % (module, len(data[module]), todo))
    else:
        found = [p for m in ([args.module] if args.module else ['C1', 'C4']) for p in problems(args.root, m, args.block if m == 'C4' else None)]
    print('\n'.join(found + ['FAIL' if found else 'PASS']))
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
