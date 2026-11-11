#!/usr/bin/env python3
"""知识缺口清单 record/knowledge-gaps.json（SKILL.md「能力目标」第 7 项、「报告与打包」）。

  python3 knowledge_gaps.py <交付目录> [--input datasheets=<资料目录>]

从各模块的产品里抽出设计中知识不够的地方，不手写：知识包（references/knowledge/）哪个组件查不到什么
（典型电路没有适用方案、modules.json 的 knowledge_lookups 里没查到的）、候选来源未证实、手册不在知识库、
计算依据是典型值或估计、外部资料待办、回到上游重做、用户没有采纳 ASG 的建议。清单只如实列出，不拦交付；
能力缺陷的归纳和改进在评测侧做。格式见 references/delivery-report.md。
"""
import argparse
import json
import sys
from pathlib import Path

FILE = 'knowledge-gaps.json'
SCHEMA_VERSION = 1
# signal → (label, the knowledge carrier it points at)
SIGNALS = {
    'no_typical_circuit': ('典型电路没有适用方案', '知识包/典型电路'),
    'knowledge_missing': ('知识包查不到', '知识包（组件见对象）'),
    'unverified_candidate': ('候选来源未证实', '知识包/典型电路'),
    'datasheet_not_in_library': ('手册不在知识库', '器件知识库'),
    'weak_basis': ('计算依据是典型值、估计或未规定', '知识包/器件参数'),
    'external_item': ('外部资料待办', '知识包/器件参数'),
    'returned_upstream': ('回到上游重做', '上游模块'),
    'user_overrode': ('用户没有采纳 ASG 的建议', '判断依据'),
}
WEAK_BASES = ('typical', 'model', 'unspecified')


def load(path):
    try:
        return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None
    except ValueError:
        return None


def rows(data, key):
    found = data.get(key) if isinstance(data, dict) else None
    return [r for r in found if isinstance(r, dict)] if isinstance(found, list) else []


def text(value):
    return isinstance(value, str) and bool(value.strip())


def extract(root, datasheets_to_file=()):
    """The knowledge-gap list of a design folder, from its records alone."""
    record = Path(root) / 'record'
    gaps = []
    def gap(signal, module, task, item, detail, source):
        gaps.append({'signal': signal, 'module': module, 'task': task, 'item': item, 'detail': detail, 'source': source})

    folder = record / 'block-circuits'
    for path in sorted(folder.glob('*.json')) if folder.is_dir() else []:
        for scheme in rows(load(path), 'schemes'):
            picked = scheme.get('selected')
            if isinstance(picked, dict) and not text(picked.get('circuit')):
                gap('no_typical_circuit', 'C3', 'C3.1', '%s：%s' % (path.stem, scheme.get('name')),
                    '选定方案“%s”没有对应的典型电路' % picked.get('name'), 'block-circuits/' + path.name)
    for block in rows(load(record / 'scheme-criteria.json'), 'blocks'):
        for candidate in rows(block, 'candidates'):
            if candidate.get('unverified') is True:
                gap('unverified_candidate', 'C3', 'C3.1', '%s：%s' % (block.get('block'), candidate.get('name')),
                    '候选由模型自身知识提出，当次没有查到来源', 'scheme-criteria.json')
    for name in datasheets_to_file:
        gap('datasheet_not_in_library', 'C4', 'C4.1', name, '本项目用到、知识库还没有的手册', 'manifest.json')

    closure = load(record / 'design-closure.json') or {}
    for calc in rows(closure, 'calculations'):
        for p in rows(calc, 'parameters'):
            if p.get('basis') in WEAK_BASES:
                gap('weak_basis', 'C4', 'C4.2', '%s：%s' % (calc.get('id'), p.get('name')),
                    '参数依据 %s' % p['basis'], 'design-closure.json')
        for c in rows(calc, 'checks'):
            if c.get('limit_basis') in WEAK_BASES:
                gap('weak_basis', 'C4', 'C4.2', '%s：%s' % (calc.get('id'), c.get('name')),
                    '门槛依据 %s' % c['limit_basis'], 'design-closure.json')
    for item in rows(closure, 'work_items'):
        if item.get('stage') == 'external' and item.get('status') == 'open':
            gap('external_item', 'C4', 'C4.3', str(item.get('id')), str(item.get('action') or ''), 'design-closure.json')

    modules = load(record / 'modules.json')
    for row in rows(modules, 'knowledge_lookups'):
        if row.get('found'):
            continue
        task = str(row.get('task') or '')
        gap('knowledge_missing', task.partition('.')[0], task, '%s：%s' % (row.get('component'), row.get('query')),
            str(row.get('detail') or '查不到'), 'modules.json')
    for row in rows(modules, 'returns'):
        source, target = str(row.get('from') or ''), str(row.get('to') or '')
        gap('returned_upstream', target.partition('.')[0], target, '%s → %s' % (source, target),
            '%s（依据：%s）' % (row.get('reason'), row.get('evidence')), 'modules.json')

    for c in rows(load(record / 'requirements.json'), 'clarifications'):
        answer = c.get('answer') if isinstance(c.get('answer'), dict) else {}
        if answer.get('decision') == 'DECIDED' and text(c.get('proposed_requirement')) \
                and answer.get('text') != c['proposed_requirement']:
            gap('user_overrode', 'C1', 'C1.1', str(c.get('id')), '用户给定的需求与建议条文不同', 'requirements.json')
    for role in rows(load(record / 'selection.json'), 'roles'):
        recommended = [o.get('name') for o in rows(role, 'options') if o.get('recommended') is True]
        chosen = (role.get('decision') or {}).get('option') if isinstance(role.get('decision'), dict) else None
        if recommended and text(chosen) and chosen not in recommended:
            gap('user_overrode', 'C3', 'C3.2', str(role.get('role')),
                '选定方案“%s”不是 ASG 推荐的“%s”' % (chosen, recommended[0]), 'selection.json')

    counts = {}
    for g in gaps:
        counts[g['signal']] = counts.get(g['signal'], 0) + 1
    return {'schema_version': SCHEMA_VERSION, 'counts': counts, 'gaps': gaps}


def stale(root):
    """Why record/knowledge-gaps.json is not the list of the current records, or None. The datasheet rows depend on the
    library outside the delivery (a datasheet filed later leaves the list), so they are not compared."""
    path = Path(root) / 'record' / FILE
    if not path.is_file():
        return 'record/%s 缺失：运行 knowledge_gaps.py <交付目录>' % FILE
    def kept(data):
        return [g for g in rows(data, 'gaps') if g.get('signal') != 'datasheet_not_in_library']
    if kept(load(path)) != kept(extract(root)):
        return 'record/%s 与当前记录不一致：重跑 knowledge_gaps.py，不手改' % FILE
    return None


def render(data):
    """The report section: how many of each signal, then the list."""
    gaps = rows(data, 'gaps')
    out = ['## 知识缺口', '', '设计中知识不够的地方，由 `knowledge_gaps.py` 从记录抽出，如实列出，不影响交付结论。', '']
    if not gaps:
        return out + ['本版没有抽出知识缺口。', '']
    out += ['| 信号 | 指向 | 数量 |', '|---|---|---|']
    out += ['| %s | %s | %d |' % (SIGNALS[k][0], SIGNALS[k][1], n) for k, n in sorted((data.get('counts') or {}).items())
            if k in SIGNALS]
    out += ['', '| 模块 | 任务 | 信号 | 对象 | 说明 |', '|---|---|---|---|---|']
    out += ['| %s | %s | %s | %s | %s |' % (g.get('module'), g.get('task'), SIGNALS.get(g.get('signal'), ('',))[0],
                                         str(g.get('item')).replace('|', '／'), str(g.get('detail')).replace('|', '／').replace('\n', ' '))
            for g in gaps]
    return out + ['']


def datasheets_of(inputs):
    """Datasheets of the `datasheets` input that the library does not hold (the list pack_design.py prints)."""
    folder = dict(i.split('=', 1) for i in inputs if '=' in i).get('datasheets')
    if not folder:
        return []
    import pack_design
    return pack_design.datasheets_not_in_library(folder, pack_design.DEFAULT_WIKI)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('design_root', type=Path, help='交付目录（含 record/）')
    ap.add_argument('--input', action='append', default=[], help='datasheets=<资料目录>：核对哪些手册不在知识库')
    args = ap.parse_args(argv)
    data = extract(args.design_root, datasheets_of(args.input))
    path = args.design_root / 'record' / FILE
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for key, count in sorted(data['counts'].items()):
        print('%s：%d' % (SIGNALS[key][0], count))
    print('wrote %s（%d 条）' % (path, len(data['gaps'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
