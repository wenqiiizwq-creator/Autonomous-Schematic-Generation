#!/usr/bin/env python3
"""块设计（任务 C4.4）与整板合并（任务 C5.1）；references/modules.md。

  python3 blocks.py merge <设计目录> [--out record/electrical-intent.json]
  python3 blocks.py roundtrip <electrical-intent.json> --plan record/page-plan.json [--by page] [--json]

块设计 `record/blocks/<块>.json`（C4 每块一个；整板层块 `BOARD.json` 由 C5 写）：
- block、components、nets、no_connect：只含本块的器件和它们的引脚。
- ports：本块里要和别的块接起来的网络，用 architecture.json 流向的 `nets` 或电压域的 `ground` 给的整板网络名；
  合并时同名端口接成一个网络。不在 ports 里的是块内网络，不能与整板网络或别的块的块内网络重名。
- net_roles、net_voltages、high_voltage_nets：本块网络上的标注；共享网络的标注各块都写，合并时必须一致。
- filtered_supply、external_supply、reviewed_circuit_supply：归 pin（或 via）所在的块。
- component_requirements_version：本块器件的性能记录版本（任务 C4.2）。
位号在 architecture.json 给本块的编号段 ref_range 内；合并时不改号，重号报错。
`BOARD.json` 可写 `header`（revision、title 等整板表头）。

roundtrip 只用于验证块格式：把已有整板网表按分页方案的功能块拆开，再合回去逐脚比对。
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from architecture import board_nets

SCHEMA = 1
DIR = 'blocks'
BOARD = 'BOARD'
INTENT_SCHEMA = 'project-hardware-intent-v1'
BODY = ('components', 'nets', 'no_connect', 'net_roles', 'net_voltages', 'high_voltage_nets',
        'filtered_supply', 'external_supply', 'reviewed_circuit_supply')
OWNED_LISTS = ('filtered_supply', 'external_supply', 'reviewed_circuit_supply')
SUPPLY_ROLES = ('power', 'return')
REF_NUMBER = re.compile(r'(\d+)$')


def ref_of(pin):
    return pin.rsplit('.', 1)[0]


def item_refs(item):
    refs = set(item.get('refs') or ())
    if item.get('pin'):
        refs.add(ref_of(item['pin']))
    if item.get('via'):
        refs.add(item['via'])
    return refs


def item_owner(item):
    if item.get('pin'):
        return ref_of(item['pin'])
    return item.get('via')


def read_dir(record):
    """({block id: block design}, problems) from record/blocks/."""
    folder = Path(record) / DIR
    found, problems = {}, []
    for path in sorted(folder.glob('*.json')) if folder.is_dir() else []:
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except ValueError as exc:
            problems.append('%s/%s 读不出来：%s' % (DIR, path.name, exc))
            continue
        key = data.get('block') if isinstance(data, dict) else None
        if key != path.stem:
            problems.append('%s/%s 的 block 要写 %s' % (DIR, path.name, path.stem))
            continue
        found[key] = data
    return found, problems


def check_block(block, architecture):
    """Problems of one block design against the architecture (task C4.4): its ports are board nets the flows touching
    it carry (or a domain ground), its internal nets are not board nets, its reference numbers sit in its range."""
    key = block.get('block') if isinstance(block, dict) else None
    where = '块 %s' % key
    if not isinstance(block, dict) or block.get('schema_version') != SCHEMA:
        return ['%s 要写 schema_version %d' % (where, SCHEMA)]
    problems = []
    for field, kind in (('components', list), ('nets', dict), ('ports', list), ('no_connect', list)):
        if not isinstance(block.get(field), kind):
            problems.append('%s 要写 %s' % (where, field))
    if problems:
        return problems
    arch_blocks = {b.get('id'): b for b in (architecture or {}).get('blocks') or [] if isinstance(b, dict)}
    if key != BOARD and key not in arch_blocks:
        return ['%s 不是 architecture.json 的功能块' % where]
    nets, grounds = board_nets(architecture)
    allowed = (set(nets) if key == BOARD else {n for n, ends in nets.items() if key in ends}) | grounds
    refs = {c.get('ref') for c in block['components'] if isinstance(c, dict)}
    for port in block['ports']:
        if port not in allowed:
            problems.append('%s 的端口 %s 不是与本块相连的流向给的网络名（或电压域的地）' % (where, port))
        if port not in block['nets']:
            problems.append('%s 的端口 %s 不是本块的网络' % (where, port))
    for net, pins in block['nets'].items():
        if net not in block['ports'] and (net in nets or net in grounds):
            problems.append('%s 的块内网络 %s 与整板网络重名：要接出去就写进 ports，否则改名' % (where, net))
        stray = [p for p in pins if ref_of(p) not in refs]
        if stray:
            problems.append('%s 的网络 %s 接到了不在本块的引脚：%s' % (where, net, '、'.join(stray)))
    span = (arch_blocks.get(key) or {}).get('ref_range')
    if key != BOARD and isinstance(span, list) and len(span) == 2:
        outside = sorted(r for r in refs if not (REF_NUMBER.search(r or '') and span[0] <= int(REF_NUMBER.search(r).group(1)) <= span[1]))
        if outside:
            problems.append('%s 的位号 %s 不在本块编号段 %d–%d 内' % (where, '、'.join(outside[:6]), span[0], span[1]))
    return problems


def merge(blocks, header=None, architecture=None, loose=False, circuit=True):
    """Whole-board design netlist from block designs (task C5.1). Returns (intent, problems).

    `architecture` checks each block against it; `loose` (the C4 gate's view of the blocks written so far) allows a
    port whose other end is not written yet; `circuit` writes each part's block into fields.Circuit."""
    problems, used = [], {}
    components, nets, no_connect = [], {}, []
    roles, voltages, high, owned = {}, [], [], {f: [] for f in OWNED_LISTS}
    net_block, port_users = {}, defaultdict(list)
    versions = set()
    for key in sorted(blocks):
        block = blocks[key]
        if not isinstance(block, dict) or block.get('schema_version') != SCHEMA:
            problems.append('块 %s 要写 schema_version %d' % (key, SCHEMA))
            continue
        if architecture is not None:
            problems += check_block(block, architecture)
        if 'component_requirements_version' in block:
            versions.add(block['component_requirements_version'])
        for comp in block.get('components') or []:
            ref = comp.get('ref')
            if ref in used:
                problems.append('位号 %s 在块 %s 与 %s 重复' % (ref, used[ref], key))
                continue
            used[ref] = key
            if circuit:
                comp = dict(comp, fields=dict(comp.get('fields') or {}, Circuit=key))
            components.append(comp)
        refs = {c.get('ref') for c in block.get('components') or []}
        ports = set(block.get('ports') or [])
        for net, pins in (block.get('nets') or {}).items():
            stray = [p for p in pins if ref_of(p) not in refs]
            if stray:
                problems.append('块 %s 的网络 %s 接到了不在本块的引脚：%s' % (key, net, '、'.join(stray)))
            if net in ports:
                port_users[net].append(key)
            elif net in net_block:
                problems.append('块 %s 与 %s 都有块内网络 %s；要接起来就写进两块的 ports，否则改名' % (net_block[net], key, net))
            net_block.setdefault(net, key)
            nets.setdefault(net, []).extend(pins)
        no_connect += list(block.get('no_connect') or [])
        for net, role in (block.get('net_roles') or {}).items():
            if roles.setdefault(net, role) != role:
                problems.append('网络 %s 的角色各块不一致：%s / %s' % (net, roles[net], role))
        for item in block.get('net_voltages') or []:
            same = [v for v in voltages if v.get('net') == item.get('net')]
            if same and item not in same:
                problems.append('网络 %s 的电压各块写得不一致' % item.get('net'))
            if item not in voltages:
                voltages.append(item)
        high += [n for n in block.get('high_voltage_nets') or [] if n not in high]
        for field in OWNED_LISTS:
            owned[field] += [i for i in block.get(field) or [] if i not in owned[field]]
    for net, keys in sorted(port_users.items()):
        if net in net_block and net_block[net] not in keys:
            problems.append('网络 %s 在块 %s 是块内网络，在 %s 是端口' % (net, net_block[net], '、'.join(keys)))
        elif len(keys) < 2 and not loose:
            problems.append('端口 %s 只有块 %s 用到，没有对端' % (net, keys[0]))
    if len(versions) > 1:
        problems.append('各块的 component_requirements_version 不一致：%s' % sorted(versions, key=str))
    intent = {'schema': INTENT_SCHEMA}
    intent.update(header or {})
    if versions:
        intent['component_requirements_version'] = versions.pop()
    intent.update({'components': components, 'nets': nets, 'no_connect': no_connect, 'net_roles': roles})
    if voltages:
        intent['net_voltages'] = voltages
    intent['high_voltage_nets'] = high
    intent.update({f: owned[f] for f in OWNED_LISTS})
    return intent, problems


def merge_record(root, loose=False, only=None):
    """Merge record/blocks/ against record/architecture.json. `only` limits it to those block ids (the C4 gate of one
    block). Returns (intent, problems)."""
    record = Path(root) / 'record'
    found, problems = read_dir(record)
    arch_path = record / 'architecture.json'
    if not arch_path.is_file():
        return None, problems + ['缺少 record/architecture.json（任务 C2.1）']
    architecture = json.loads(arch_path.read_text(encoding='utf-8'))
    if only:
        missing = sorted(set(only) - set(found))
        problems += ['缺少块设计 %s/%s.json（任务 C4.4）' % (DIR, k) for k in missing]
        found = {k: v for k, v in found.items() if k in only}
    if not found:
        return None, problems + ['%s/ 里没有块设计（任务 C4.4）' % DIR]
    header = (found.get(BOARD) or {}).get('header') or {}
    intent, more = merge(found, header, architecture, loose=loose)
    return intent, problems + more


# --- roundtrip: block format check on an existing whole-board netlist -------------------------------------------------

def assignment_from_plan(plan, by='block'):
    """{block id: [refs]} from the page plan. A page whose parts are all listed on other pages is an overview page."""
    pages = plan.get('pages') or []
    listed = [(p.get('file', ''), name, refs) for p in pages for name, refs in (p.get('blocks') or {}).items()]
    out = {}
    for page in pages:
        mine = {r for refs in (page.get('blocks') or {}).values() for r in refs}
        others = {r for f, _, refs in listed if f != page.get('file') for r in refs}
        if mine and mine <= others:
            continue
        stem = Path(page.get('file', '')).stem
        for name, refs in (page.get('blocks') or {}).items():
            key = stem if by == 'page' else '%s:%s' % (stem, name)
            out.setdefault(key, []).extend(refs)
    seen = defaultdict(list)
    for key, refs in out.items():
        for r in refs:
            seen[r].append(key)
    return out, ['器件 %s 同时归 %s' % (r, '、'.join(keys)) for r, keys in sorted(seen.items()) if len(keys) > 1]


def split(intent, assignment):
    """Block designs and board header from a whole-board design netlist. Returns (blocks, header, problems)."""
    owner, problems = {}, []
    for key, refs in assignment.items():
        for r in refs:
            if r in owner and owner[r] != key:
                problems.append('器件 %s 同时归 %s、%s' % (r, owner[r], key))
            owner.setdefault(r, key)
    refs = [c['ref'] for c in intent['components']]
    problems += ['器件 %s 不归任何块' % r for r in refs if r not in owner]
    problems += ['块里列的 %s 不在网表里' % r for r in sorted(set(owner) - set(refs))]
    if problems:
        return {}, {}, problems
    blocks = {key: {'schema_version': SCHEMA, 'block': key, 'components': [], 'nets': {}, 'ports': [],
                    'no_connect': []} for key in assignment}
    if 'component_requirements_version' in intent:
        for block in blocks.values():
            block['component_requirements_version'] = intent['component_requirements_version']
    for comp in intent['components']:
        blocks[owner[comp['ref']]]['components'].append(comp)
    users = {}
    for net, pins in (intent.get('nets') or {}).items():
        by_block = defaultdict(list)
        for pin in pins:
            by_block[owner[ref_of(pin)]].append(pin)
        users[net] = set(by_block)
        for key, own in by_block.items():
            blocks[key]['nets'][net] = own
            if len(by_block) > 1:
                blocks[key]['ports'].append(net)
    for pin in intent.get('no_connect') or []:
        blocks[owner[ref_of(pin)]]['no_connect'].append(pin)
    for net, role in (intent.get('net_roles') or {}).items():
        for key in users.get(net, ()):
            blocks[key].setdefault('net_roles', {})[net] = role
    for item in intent.get('net_voltages') or []:
        for key in users.get(item.get('net'), ()):
            blocks[key].setdefault('net_voltages', []).append(item)
    for net in intent.get('high_voltage_nets') or []:
        for key in users.get(net, ()):
            blocks[key].setdefault('high_voltage_nets', []).append(net)
    for field in OWNED_LISTS:
        for item in intent.get(field) or []:
            ref = item_owner(item)
            if ref not in owner:
                problems.append('%s 的 %s 找不到所属器件' % (field, item.get('net')))
                continue
            blocks[owner[ref]].setdefault(field, []).append(item)
    header = {k: v for k, v in intent.items() if k not in BODY + ('schema', 'component_requirements_version')}
    return blocks, header, problems


def canonical(intent):
    out = {k: v for k, v in intent.items() if k not in BODY}
    out['components'] = sorted(json.dumps(c, sort_keys=True, ensure_ascii=False) for c in intent.get('components') or [])
    out['nets'] = {n: sorted(p) for n, p in (intent.get('nets') or {}).items()}
    out['no_connect'] = sorted(intent.get('no_connect') or [])
    out['net_roles'] = dict(intent.get('net_roles') or {})
    for key in ('net_voltages', 'high_voltage_nets') + OWNED_LISTS:
        out[key] = sorted(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in intent.get(key) or [])
    return out


def compare(a, b):
    """Differences between two design netlists, pin by pin."""
    a, b = canonical(a), canonical(b)
    diff = []
    for key in sorted(set(a) | set(b)):
        if a.get(key) == b.get(key):
            continue
        if key == 'nets':
            for net in sorted(set(a['nets']) | set(b['nets'])):
                if a['nets'].get(net) != b['nets'].get(net):
                    diff.append('网络 %s：%s ≠ %s' % (net, a['nets'].get(net), b['nets'].get(net)))
        else:
            diff.append('%s 不一致' % key)
    return diff


def statistics(intent, blocks):
    roles = intent.get('net_roles') or {}
    shared = {n: [k for k, b in blocks.items() if n in b['ports']] for n in intent['nets']}
    shared = {n: ks for n, ks in shared.items() if len(ks) > 1}
    owner = {c['ref']: k for k, b in blocks.items() for c in b['components']}
    cross = []
    for field in OWNED_LISTS:
        for item in intent.get(field) or []:
            ks = sorted({owner[r] for r in item_refs(item) if r in owner})
            if len(ks) > 1:
                cross.append({'field': field, 'net': item.get('net'), 'blocks': ks})
    return {'components': len(intent['components']), 'nets': len(intent['nets']), 'blocks': len(blocks),
            'parts_per_block': {k: len(b['components']) for k, b in sorted(blocks.items())},
            'shared_supply_nets': {n: shared[n] for n in sorted(shared) if roles.get(n) in SUPPLY_ROLES},
            'shared_signal_nets': {n: shared[n] for n in sorted(shared) if roles.get(n) not in SUPPLY_ROLES},
            'ports_per_block': {k: len(b['ports']) for k, b in sorted(blocks.items())},
            'cross_block_annotations': cross}


def roundtrip(intent, plan, by='block'):
    assignment, problems = assignment_from_plan(plan, by)
    parts, header, more = split(intent, assignment) if not problems else ({}, {}, [])
    problems += more
    if problems:
        return {'problems': problems}
    merged, problems = merge(parts, header, circuit=False)
    intent = dict(intent, schema=intent.get('schema', INTENT_SCHEMA))
    stats = statistics(intent, parts)
    stats.update({'problems': problems, 'differences': compare(intent, merged) if not problems else []})
    return stats


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('merge')
    p.add_argument('design_root', type=Path, help='设计目录（含 record/blocks/ 与 record/architecture.json）')
    p.add_argument('--out', type=Path, help='默认 record/electrical-intent.json')
    p = sub.add_parser('roundtrip')
    p.add_argument('intent', type=Path)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--by', choices=('block', 'page'), default='block')
    p.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)

    if args.cmd == 'merge':
        intent, problems = merge_record(args.design_root)
        for problem in problems:
            print('FAIL:', problem)
        if problems:
            return 1
        out = args.out or args.design_root / 'record' / 'electrical-intent.json'
        out.write_text(json.dumps(intent, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('合并：器件 %d 个，网络 %d 个，写到 %s' % (len(intent['components']), len(intent['nets']), out))
        return 0

    stats = roundtrip(load(args.intent), load(args.plan), args.by)
    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    elif 'components' in stats:
        print('器件 %d、网络 %d、块 %d；共享电源/地网络 %d、共享信号网络 %d；跨块标注 %d' % (
            stats['components'], stats['nets'], stats['blocks'], len(stats['shared_supply_nets']),
            len(stats['shared_signal_nets']), len(stats['cross_block_annotations'])))
    bad = stats['problems'] + stats.get('differences', [])
    for problem in bad:
        print('FAIL:', problem)
    if not args.json:
        print('往返不一致' if bad else '往返一致')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
