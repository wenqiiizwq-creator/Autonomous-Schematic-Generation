#!/usr/bin/env python3
"""任务 C3.2（模块 C3）的产品：每块一个 record/block-circuits/<块>.json（SKILL.md「架构」、references/modules.md）。

  python3 block_circuits.py <设计目录>     抽出块文件，再核对它们与工作记录一致

块文件不手写，从 C3 的两份工作记录确定性地抽出：scheme-criteria.json 的每块、selection.json 的每个核心角色都写
block_id（architecture.json 的 blocks[].id）。每个功能块一个文件，内容是选定方案、核心器件与角色、决定条件的本板取值、
核心器件的端口限值（port_limits，供任务 C3.3 定接口参数）、留给任务 C4.2 核算的数值；不含外围器件和数值。C4 只读块文件，不读这两份工作记录。
"""
import argparse
import json
import sys
from pathlib import Path

DIR = 'block-circuits'
SCHEMA_VERSION = 1


def text(value):
    return isinstance(value, str) and bool(value.strip())


def items(data, key):
    rows = data.get(key) if isinstance(data, dict) else None
    return [r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []


def selected(rows):
    chosen = [c for c in rows if isinstance(c, dict) and c.get('status') == 'selected']
    return chosen[0] if len(chosen) == 1 else None


def scheme_entry(block):
    pick = selected(block.get('candidates') or [])
    return {'name': block.get('block'),
            'circuit_types': block.get('circuit_types', []), 'device_kinds': block.get('device_kinds', []),
            'ports': block.get('ports') is True,
            'selected': {k: pick[k] for k in ('name', 'circuit', 'reason', 'source') if k in pick} if pick else None,
            'decisive': [{'condition': d.get('condition'), 'value': d.get('value')}
                         for d in block.get('decisive') or [] if isinstance(d, dict)],
            'deferred': [{'rule': c.get('id'), 'values': c['defer']} for c in block.get('criteria') or []
                         if isinstance(c, dict) and isinstance(c.get('defer'), list) and c['defer']]}


def part_entry(role):
    pick = selected(role.get('candidates') or [])
    out = {'role': role.get('role'), 'refs': role.get('refs', []),
           'decisive': [d for d in role.get('decisive') or [] if isinstance(d, dict)]}
    for key in ('mpn', 'vendor', 'datasheet', 'values', 'port_limits', 'external_dependencies'):
        if pick and key in pick:
            out[key] = pick[key]
    return out


def port_limit_problems(arch, selection):
    """Task C3.2: the selected part of every core role lists its limits on the block's ports (`port_limits`: board net
    and datasheet page, plus the numbers), an empty list when it touches none."""
    touching = {}
    for flow in items(arch, 'flows'):
        for block in (flow.get('from'), flow.get('to')):
            touching.setdefault(block, set()).update(n for n in flow.get('nets') or [] if text(n))
    problems = []
    for role in items(selection, 'roles'):
        pick = selected(role.get('candidates') or [])
        if pick is None:
            continue
        where = 'selection.json 角色“%s”' % role.get('role')
        rows = pick.get('port_limits')
        if not isinstance(rows, list):
            problems.append(where + ' 的选定候选要写 port_limits：它在本块各端口上的限值和手册页码，不接端口的写空列表（任务 C3.2）')
            continue
        for row in rows:
            if not isinstance(row, dict) or not text(row.get('net')) or not (text(row.get('page')) or isinstance(row.get('page'), int)):
                problems.append(where + ' 的 port_limits 每项写 net（整板网络名）和 page（手册页码）')
            elif row['net'] not in touching.get(role.get('block_id'), set()):
                problems.append('%s 的 port_limits 的 %s 不是与块 %s 相连的流向的网络' % (where, row['net'], role.get('block_id')))
            elif len(row) < 3:
                problems.append('%s 的 port_limits 的 %s 没有写限值' % (where, row['net']))
    return problems


def extract(arch, scheme, selection):
    """({block id: block file}, problems). Every scheme block and core role names an architecture block in block_id."""
    blocks = items(arch, 'blocks')
    ids = [b.get('id') for b in blocks if text(b.get('id'))]
    problems = []
    if not ids:
        return {}, ['architecture.json 没有功能块：块文件按 architecture.json 的 blocks[].id 分（任务 C2.1）']
    files = {b['id']: {'schema_version': SCHEMA_VERSION, 'block': b['id'], 'name': b.get('name'),
                       'library_root': (selection or {}).get('library_root') if isinstance(selection, dict) else None,
                       'schemes': [], 'core_parts': []} for b in blocks if text(b.get('id'))}
    for i, block in enumerate(items(scheme, 'blocks'), 1):
        if block.get('block_id') not in files:
            problems.append('scheme-criteria.json“%s”的 block_id 要是 architecture.json 的功能块 id（%s）' % (
                block.get('block') or '第 %d 块' % i, '、'.join(ids)))
            continue
        files[block['block_id']]['schemes'].append(scheme_entry(block))
    for i, role in enumerate(items(selection, 'roles'), 1):
        if role.get('block_id') not in files:
            problems.append('selection.json 角色“%s”的 block_id 要是 architecture.json 的功能块 id（%s）' % (
                role.get('role') or '第 %d 个' % i, '、'.join(ids)))
            continue
        files[role['block_id']]['core_parts'].append(part_entry(role))
    return files, problems


def read_dir(record):
    folder = record / DIR
    found, problems = {}, []
    for path in sorted(folder.glob('*.json')) if folder.is_dir() else []:
        try:
            found[path.stem] = json.loads(path.read_text(encoding='utf-8'))
        except ValueError as exc:
            problems.append('%s/%s 不是合法 JSON：%s' % (DIR, path.name, exc))
    return found, problems


def verify(found, scheme, selection, arch):
    """Problems where the block files on disk and the working records disagree: one file per architecture block, each
    scheme block and each core role in its own block's file with the same selected scheme or part."""
    ids = {b.get('id') for b in items(arch, 'blocks') if text(b.get('id'))}
    problems = []
    for name in sorted(ids - set(found)):
        problems.append('缺少 %s/%s.json' % (DIR, name))
    for name in sorted(set(found) - ids):
        problems.append('%s/%s.json 不是 architecture.json 的功能块' % (DIR, name))
    for block in items(scheme, 'blocks'):
        data = found.get(block.get('block_id')) or {}
        pick = selected(block.get('candidates') or []) or {}
        rows = [s for s in data.get('schemes') or [] if isinstance(s, dict) and s.get('name') == block.get('block')]
        if len(rows) != 1 or (rows[0].get('selected') or {}).get('name') != pick.get('name'):
            problems.append('%s/%s.json 与 scheme-criteria.json“%s”的选定方案不一致' % (DIR, block.get('block_id'), block.get('block')))
    for role in items(selection, 'roles'):
        data = found.get(role.get('block_id')) or {}
        pick = selected(role.get('candidates') or []) or {}
        rows = [p for p in data.get('core_parts') or [] if isinstance(p, dict) and p.get('role') == role.get('role')]
        if len(rows) != 1 or rows[0].get('mpn') != pick.get('mpn') or rows[0].get('refs') != role.get('refs', []):
            problems.append('%s/%s.json 与 selection.json 角色“%s”的选定器件或位号不一致' % (DIR, role.get('block_id'), role.get('role')))
    listed = sum(len(d.get('schemes') or []) for d in found.values() if isinstance(d, dict))
    parts = sum(len(d.get('core_parts') or []) for d in found.values() if isinstance(d, dict))
    if listed != len(items(scheme, 'blocks')) or parts != len(items(selection, 'roles')):
        problems.append('块文件里的方案或核心器件比工作记录多：块文件只能由 block_circuits.py 抽出')
    return problems


def load(path):
    if not path.is_file():
        return None, '缺少 record/%s' % path.name
    try:
        return json.loads(path.read_text(encoding='utf-8')), None
    except ValueError as exc:
        return None, 'record/%s 不是合法 JSON：%s' % (path.name, exc)


def run(root, write=True):
    """Module C3 gate part: extract the block files (written when `write`, else compared with the files on disk), then
    check them against the working records. Returns the problems."""
    record = Path(root) / 'record'
    loaded = {}
    problems = []
    for name in ('architecture.json', 'scheme-criteria.json', 'selection.json'):
        loaded[name], problem = load(record / name)
        if problem:
            problems.append(problem)
    if problems:
        return problems
    arch, scheme, selection = (loaded[n] for n in ('architecture.json', 'scheme-criteria.json', 'selection.json'))
    files, problems = extract(arch, scheme, selection)
    if problems:
        return problems
    problems = port_limit_problems(arch, selection)
    rendered = {k: json.dumps(v, ensure_ascii=False, indent=2) + '\n' for k, v in files.items()}
    folder = record / DIR
    if write:
        folder.mkdir(exist_ok=True)
        for old in folder.glob('*.json'):
            if old.stem not in rendered:
                old.unlink()
        for name, body in rendered.items():
            (folder / (name + '.json')).write_text(body, encoding='utf-8')
    else:
        for name, body in sorted(rendered.items()):
            path = folder / (name + '.json')
            if path.is_file() and path.read_text(encoding='utf-8') != body:
                problems.append('%s/%s.json 与工作记录抽出的结果不同：重跑 block_circuits.py，不手改块文件' % (DIR, name))
    found, read_problems = read_dir(record)
    return problems + read_problems + verify(found, scheme, selection, arch)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('design_root', type=Path, help='设计目录（含 record/）')
    args = ap.parse_args(argv)
    problems = run(args.design_root)
    for problem in problems:
        print('PROBLEM:', problem)
    print('FAIL' if problems else 'PASS')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
