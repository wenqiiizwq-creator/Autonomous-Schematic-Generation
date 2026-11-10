#!/usr/bin/env python3
"""能力模块关卡与交接指纹（SKILL.md「架构」、P7；references/modules.md）。

  python3 check_module.py C3 <设计目录> [--given 文件 ...]   跑模块关卡；通过后把指纹记进 record/modules.json
  python3 check_module.py C4 <设计目录> --block PSU          只核一个块的块设计（不记指纹）
  python3 check_module.py return <设计目录> --from C4.2 --to C2.2 --reason … --evidence …
                                                             回到上游重做时在 record/modules.json 的 returns 记一条（P7）
  python3 check_module.py status <设计目录>                  列出已记模块：OK、STALE（上游变了）、MODIFIED（产出改过未重验）
  python3 check_module.py report <设计目录>                  单独运行（record/task.json 带 modules）时写 模块报告.md
  python3 check_module.py pack <设计目录>                    核对单独运行的交付目录

关卡调用现有检查，按模块只查它拥有的部分：
C1 requirements.json（audit_design_closure --module C1）；C2 architecture.json，C3 做完后加接口定稿 interfaces.json；
C3 方案记录与核心选型，
抽出并核对块文件 block-circuits/；C4 块设计 blocks/<块>.json 对架构的核对，再对已写的块设计做
audit_design_closure --module C4、器件性能要求、块文件里留给 C4.2 的数值；C5 先核 electrical-intent.json 是 blocks.py 合并
的结果，再做整板设计闭合审计；
C6 分页方案、图面审阅、KiCad 检查结果，以及块文件里的选定方案与分页方案一致（只读 C3 的产品，不读它的工作记录）。
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

import audit_design_closure as closure_audit
import architecture
from architecture import check_architecture
import block_circuits
import blocks
import render_design_report as report
from schematic_layout import component_requirements

MODULES = ('C1', 'C2', 'C3', 'C4', 'C5', 'C6')
# What each module writes (SKILL.md 架构). "file#a,b" is those top-level sections of a JSON file: design-closure.json is
# written by C4 and C5, each owning its sections; the shared ones (evidence, work_items, versions) are no module's.
# "dir/" is every JSON file in that folder; blocks/ leaves out BOARD.json, the board-level block module C5 writes.
OUTPUTS = {
    'C1': ('requirements.json',),
    'C2': ('architecture.json', architecture.INTERFACES),
    'C3': ('scheme-criteria.json', 'selection.json', block_circuits.DIR + '/'),
    'C4': ('design-closure.json#calculations,operating_points,pin_dispositions', 'component-requirements.json',
           'reference-input.json', blocks.DIR + '/'),
    'C5': ('electrical-intent.json', '%s/%s.json' % (blocks.DIR, blocks.BOARD),
           'design-closure.json#traceability,net_voltages,matrices'),
    'C6': ('page-plan.json', 'summary.json', 'visual-review.json'),
}
# C2 comes back after C3 for task C2.2 (interface freeze), which reads the block files; C3 reads only architecture.json,
# so writing interfaces.json does not make C3 stale. READS narrows what a module reads of an upstream one (default: all).
UPSTREAM = {'C1': (), 'C2': ('C1', 'C3'), 'C3': ('C1', 'C2'), 'C4': ('C1', 'C2', 'C3'), 'C5': ('C1', 'C2', 'C4'),
            'C6': ('C2', 'C3', 'C5')}
READS = {('C2', 'C3'): (block_circuits.DIR + '/',), ('C3', 'C2'): ('architecture.json',)}
TASK = re.compile(r'^C[1-6]\.[1-9]$')
MODULE_REPORT = '模块报告.md'
# What a module run delivers (workflow-handoff.md 角色): the drawing only when C6 ran.
MODULE_TOP = (MODULE_REPORT, 'record', '设计资料', '原理图')
SCHEMATIC_FILES = ('schematic.pdf', 'netlist.xml', 'BOM.csv')


def file_of(item):
    return item.partition('#')[0]


def scope_of(task):
    """(modules run, given) from task.json `modules` {from, to, given: {record file: {path, sha256}}}, or None for the
    whole flow. Raises ValueError when the field is malformed (workflow-handoff.md)."""
    spec = (task or {}).get('modules')
    if spec is None:
        return None
    if not isinstance(spec, dict) or spec.get('from') not in MODULES or spec.get('to') not in MODULES \
            or MODULES.index(spec['from']) > MODULES.index(spec['to']):
        raise ValueError('task.json modules 要写 from、to（C1–C6，from 不在 to 之后）')
    run = MODULES[MODULES.index(spec['from']):MODULES.index(spec['to']) + 1]
    given = spec.get('given', {})
    if not isinstance(given, dict) or any(not isinstance(v, dict) or not text(v.get('path')) or not text(v.get('sha256'))
                                          for v in given.values()):
        raise ValueError('task.json modules.given 每项写 {path, sha256}，键是 record/ 下的文件名')
    upstream = {file_of(i) for m in MODULES[:MODULES.index(spec['from'])] for i in OUTPUTS[m]}
    stray = sorted(k for k in given if k not in upstream and not any(u.endswith('/') and k.startswith(u) for u in upstream))
    if stray:
        raise ValueError('modules.given 的 %s 不是 %s 之前模块的产出' % ('、'.join(stray), spec['from']))
    return run, given


def given_problems(root, run, given):
    """P7: a given input is read only. For a file several modules write (design-closure.json) only the sections of
    the modules before the run are compared; the run adds its own sections."""
    record = root / 'record'
    problems = []
    for name, spec in sorted(given.items()):
        source = Path(spec['path'])
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != spec['sha256']:
            problems.append('给定输入 %s 的原件 %s 不在或哈希不符' % (name, spec['path']))
            continue
        owned = [i for m in MODULES[:MODULES.index(run[0])] for i in OUTPUTS[m] if file_of(i) == name]
        for item in owned or [name]:
            if fingerprint(record, item) != fingerprint(source.parent, item.replace(name, source.name, 1)):
                problems.append('给定输入 %s 被改动（%s）：单独运行时给定输入只读，问题登记成 input 待办（P7）' % (name, item))
    return problems


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def fingerprint(record, item):
    """SHA-256 of a record file, or of the named sections of a JSON record; 'absent' when the file is missing."""
    name, _, sections = item.partition('#')
    path = record / name
    if name.endswith('/'):
        files = sorted(f for f in path.glob('*.json') if not (name == blocks.DIR + '/' and f.stem == blocks.BOARD)) \
            if path.is_dir() else []
        return hashlib.sha256(canonical({f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files})).hexdigest() \
            if files else 'absent'
    if not path.is_file():
        return 'absent'
    if not sections:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except ValueError:
        return 'unreadable'
    data = data if isinstance(data, dict) else {}
    return hashlib.sha256(canonical({k: data.get(k) for k in sections.split(',')})).hexdigest()


def outputs_of(record, module):
    return {item: fingerprint(record, item) for item in OUTPUTS[module]}


def inputs_of(record, module, given=()):
    found = {'%s:%s' % (up, item): fingerprint(record, item) for up in UPSTREAM[module]
             for item in READS.get((module, up), OUTPUTS[up])}
    for path in given:
        found['given:%s' % path] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return found


def load(record, name):
    path = record / name
    if not path.is_file():
        return None, None
    data, problem = report.load(path)
    return data, problem


def text(value):
    return isinstance(value, str) and bool(value.strip())


def closure_problems(result, name='design-closure.json'):
    return ['%s %s：%s' % (name, e.get('code'), e.get('item')) for e in result.get('errors') or []]


def closure_for(closure, refs):
    """The C4 part of design-closure.json for one block (`check_module.py C4 --block`): its calculations, operating points
    and pin dispositions."""
    view = dict(closure)
    for key in ('calculations', 'operating_points'):
        if isinstance(closure.get(key), list):
            view[key] = [r for r in closure[key] if isinstance(r, dict) and set(r.get('refs') or ()) <= refs]
    kept = {r.get('id') for r in view.get('calculations') or []}
    if isinstance(closure.get('work_items'), list):      # shared rows: those about other blocks' calculations stay out
        rows = []
        for w in closure['work_items']:
            linked = w.get('calculations') if isinstance(w, dict) else None
            if isinstance(linked, list) and linked:
                if not set(linked) & kept:
                    continue
                w = dict(w, calculations=[c for c in linked if c in kept])
            rows.append(w)
        view['work_items'] = rows
    if isinstance(closure.get('pin_dispositions'), list):
        view['pin_dispositions'] = [r for r in closure['pin_dispositions'] if isinstance(r, dict)
                                    and str(r.get('pin', '')).rsplit('.', 1)[0] in refs]
    return view


def requirements_for(record, refs):
    """One block's part of record/component-requirements.json: its performance records and its screening rows."""
    view = dict(record, components=[e for e in record.get('components') or [] if isinstance(e, dict) and e.get('ref') in refs])
    view['screening'] = [dict(row, refs=[r for r in row.get('refs') or [] if r in refs])
                         for row in record.get('screening') or [] if isinstance(row, dict)
                         and set(row.get('refs') or ()) & refs]
    return view


def block_view(root, only=None):
    """(path of a temporary design netlist merged from the C4 block designs written so far, their ports, problems)."""
    found, problems = blocks.read_dir(root / 'record')
    keys = set(only) if only else {k for k in found if k != blocks.BOARD}
    intent, more = blocks.merge_record(root, loose=True, only=keys)
    problems += more
    if intent is None:
        return None, set(), problems
    ports = {p for k in keys for p in (found.get(k) or {}).get('ports') or []}
    handle = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8')
    with handle:
        json.dump(intent, handle, ensure_ascii=False)
    return Path(handle.name), ports, problems


def gate(module, root, write=True, block=None):
    """Problems of the module's gate (empty when it passes) and notes (pending items that do not block). The C3 gate
    writes the block files when `write`; the report and the delivery check only compare them. `block` limits the C4
    gate to one block design."""
    record = root / 'record'
    closure, problem = load(record, 'design-closure.json')
    if problem:
        return [problem], []
    requirements, problem = load(record, closure_audit.REQUIREMENTS_FILE)
    if problem:
        return [problem], []
    intent_path = record / 'electrical-intent.json'
    problems, notes = [], []
    try:
        scope = scope_of(closure_audit.load_task(root))
    except ValueError as exc:
        return [str(exc)], []
    if scope:
        run, given = scope
        if module not in run:
            return ['%s 不在任务书 modules 指定的范围 %s–%s 内' % (module, run[0], run[-1])], []
        problems += given_problems(root, run, given)
    if module in ('C1', 'C4', 'C5'):
        if module == 'C1' and requirements is None:
            return ['缺少 record/requirements.json（模块 C1 的产品）'], []
        if module != 'C1' and closure is None:
            return ['缺少 record/design-closure.json'], []
        ports = ()
        if module == 'C4':
            intent_path, ports, found = block_view(root, [block] if block else None)
            problems += found
            if intent_path is None:
                return problems, notes
        elif module == 'C5':
            merged_intent, found = blocks.merge_record(root)
            problems += found
            if not intent_path.is_file():
                return problems + ['缺少 record/electrical-intent.json（任务 C5.1 用 blocks.py merge 生成）'], notes
            if merged_intent is not None and not found:
                current = json.loads(intent_path.read_text(encoding='utf-8'))
                problems += ['electrical-intent.json 与块设计的合并结果不一致（重跑 blocks.py merge）：%s' % d
                             for d in blocks.compare(merged_intent, current)[:6]]
        if module == 'C4' and block:
            intent = json.loads(intent_path.read_text(encoding='utf-8'))
            closure = closure_for(closure, {c.get('ref') for c in intent.get('components') or []})
        try:
            result = closure_audit.audit(requirements, None, root, module='C1') if module == 'C1' else \
                closure_audit.audit(closure, intent_path, root, module=module, requirements=requirements or {},
                                    open_ports=ports)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return ['%s 审计失败：%s' % ('requirements.json' if module == 'C1' else 'design-closure.json', exc)], []
        problems += closure_problems(result, 'requirements.json' if module == 'C1' else 'design-closure.json')
        notes += ['%s：%s' % (p.get('code'), p.get('item')) for p in result.get('pending') or []]
    if module == 'C2':
        data, problem = load(record, 'architecture.json')
        if problem or data is None:
            return [problem or '缺少 record/architecture.json（任务 C2.1）'], []
        ids = {r.get('id') for r in (requirements or {}).get('requirements') or [] if isinstance(r, dict)} \
            if requirements else None
        problems += check_architecture(data, ids)
        # Task C2.2 comes after C3: once the block files exist the interface freeze is part of the gate.
        files, _ = block_circuits.read_dir(record)
        frozen, problem = load(record, architecture.INTERFACES)
        if problem:
            problems.append(problem)
        elif frozen is None and files:
            problems.append('缺少 record/%s：C3 做完后做任务 C2.2 接口定稿' % architecture.INTERFACES)
        elif frozen is not None:
            found, more = architecture.check_interfaces(frozen, data, files)
            problems += found
            notes += more
    if module == 'C3':
        scheme, problem = load(record, 'scheme-criteria.json')
        if problem:
            problems.append(problem)
        else:
            problems += report.check_scheme_criteria(scheme, merged(closure, requirements), deferred=False)
            problems += report.unexplained_none(scheme)
    if module == 'C4':
        # Convention 1: C4 reads the C3 product (block files), not its working records.
        found, read_problems = block_circuits.read_dir(record)
        problems += read_problems
        if block:
            found = {k: v for k, v in found.items() if k == block}
        arch, _ = load(record, 'architecture.json')
        frozen, problem = load(record, architecture.INTERFACES)
        if problem or frozen is None:
            problems.append(problem or '缺少 record/%s：C4 按任务 C2.2 定稿的接口参数设计' % architecture.INTERFACES)
        else:
            keys = [block] if block else sorted(k for k in blocks.read_dir(record)[0] if k != blocks.BOARD)
            for key in keys:
                for row in architecture.block_interfaces(frozen, arch, key):
                    side = 'provides' if 'provides' in row else 'accepts'
                    if not isinstance(row[side], dict) or not row[side]:
                        problems.append('%s 的流向 %s 没有块 %s 这一头的 %s：回到任务 C2.2' % (
                            architecture.INTERFACES, row['name'], key, side))
        view = merged(closure, requirements)
        for name, data in sorted(found.items()):
            for scheme in (data.get('schemes') or []) if isinstance(data, dict) else []:
                for item in scheme.get('deferred') or [] if isinstance(scheme, dict) else []:
                    problems += report.check_deferred('%s/%s.json“%s”' % (block_circuits.DIR, name, scheme.get('name')),
                                                      item.get('rule'), item.get('values') or [], view)
    if module == 'C3':
        selection, problem = load(record, 'selection.json')
        if problem or selection is None:
            problems.append(problem or '缺少 record/selection.json（任务 C3.2 的核心器件选型）')
        else:
            evidence = {e.get('id'): e for e in merged(closure, requirements).get('evidence') or [] if isinstance(e, dict)}
            problems += report.check_selection(selection, {}, root, evidence)
        problems += block_circuits.run(root, write=write)
    if module == 'C4':
        requirements, problem = load(record, 'component-requirements.json')
        if problem or requirements is None:
            problems.append(problem or '缺少 record/component-requirements.json（任务 C4.2）')
        else:
            intent = json.loads(intent_path.read_text(encoding='utf-8'))
            digest = None
            if block:
                digest = component_requirements.projection_digest(requirements)
                requirements = requirements_for(requirements, {c.get('ref') for c in intent.get('components') or []})
            result = component_requirements.audit(intent, requirements, root, digest=digest)
            problems += ['component-requirements.json：%s' % e for e in result.get('errors') or []]
        intent_path.unlink(missing_ok=True)
    if module == 'C6':
        plan, problem = load(record, 'page-plan.json')
        visual, problem2 = load(record, 'visual-review.json')
        summary, problem3 = load(record, 'summary.json')
        problems += [p for p in (problem, problem2, problem3) if p]
        for name, data in (('page-plan.json', plan), ('visual-review.json', visual), ('summary.json', summary)):
            if data is None:
                problems.append('缺少 record/%s' % name)
        if problems:
            return problems, notes
        intent = json.loads(intent_path.read_text(encoding='utf-8')) if intent_path.is_file() else {}
        # Convention 1: C6 reads the C3 product (block files), not its working records.
        files, read_problems = block_circuits.read_dir(record)
        problems += read_problems
        scheme = {'blocks': [{'block': s.get('name'), 'candidates': [dict(s['selected'], status='selected')]}
                             for _, data in sorted(files.items()) for s in (data.get('schemes') or [])
                             if isinstance(s, dict) and isinstance(s.get('selected'), dict)]} if files else None
        problems += report.check_page_plan(plan, intent, visual, root=root, scheme=scheme, explain_none=False)
        problems += report.check_visual_items(root, visual, summary)
        if visual.get('status') != 'REVIEWED':
            problems.append('visual-review.json 的 status 不是 REVIEWED（任务 C6.5）')
        failed = [k for k, v in (summary.get('gates') or {}).items() if isinstance(v, dict) and v.get('status') == 'FAIL'
                  and k != 'design_closure']
        if failed:
            problems.append('summary.json 有 FAIL 的检查项：%s（任务 C6.4）' % '、'.join(failed))
        if scheme:
            problems += [p.replace('scheme-criteria.json', block_circuits.DIR + '/')
                         for p in report.scheme_against_plan(scheme, plan)]
    return problems, notes


def merged(closure, requirements):
    """design-closure.json and requirements.json as one view (audit_design_closure.merge_requirements)."""
    return closure_audit.merge_requirements(closure or {}, requirements or {})[0]


def record_module(root, module, given):
    record = root / 'record'
    path = record / 'modules.json'
    data = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {'schema_version': 1, 'modules': {}}
    data['modules'][module] = {'gate': 'PASS', 'checked': datetime.date.today().isoformat(),
                               'inputs': inputs_of(record, module, given), 'outputs': outputs_of(record, module)}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def record_return(root, source, target, reason, evidence):
    """P7: going back to an upstream module is recorded in record/modules.json `returns`. Returns the problems."""
    problems = [] if TASK.match(source or '') and TASK.match(target or '') and source != target else \
        ['--from、--to 写两项不同的任务编号，例如 C4.2、C2.2']
    problems += ['--reason、--evidence 都要写'] if not (text(reason) and text(evidence)) else []
    if problems:
        return problems
    path = root / 'record' / 'modules.json'
    data = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {'schema_version': 1, 'modules': {}}
    data.setdefault('returns', []).append({'date': datetime.date.today().isoformat(), 'from': source, 'to': target,
                                           'reason': reason, 'evidence': evidence})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return []


def status(root):
    """{module: OK | STALE | MODIFIED} for every module recorded in record/modules.json."""
    record = root / 'record'
    path = record / 'modules.json'
    data = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {'modules': {}}
    out = {}
    for module, row in sorted(data.get('modules', {}).items()):
        given = [k.split(':', 1)[1] for k in row.get('inputs', {}) if k.startswith('given:')]
        if row.get('outputs') != outputs_of(record, module):
            out[module] = 'MODIFIED'
        elif row.get('inputs') != inputs_of(record, module, given):
            out[module] = 'STALE'
        else:
            out[module] = 'OK'
    return out


def module_report(root):
    """模块报告.md for a module run: scope, given inputs, each module's gate and what it produced, open items."""
    record = root / 'record'
    task = closure_audit.load_task(root)
    scope = scope_of(task)
    if not scope:
        raise ValueError('record/task.json 没有 modules：整板交付用 render_design_report.py')
    run, given = scope
    closure = load(record, 'design-closure.json')[0] or {}
    requirements = load(record, closure_audit.REQUIREMENTS_FILE)[0] or {}
    states = status(root)
    out = ['# 模块报告：%s' % ('、'.join(run)), '',
           '任务 %s 只运行 %s（SKILL.md「架构」、P7）。给定输入只读，问题登记为 input 待办。' % (
               (task or {}).get('id', ''), '–'.join((run[0], run[-1])) if len(run) > 1 else run[0]), '',
           '## 给定输入', '']
    out += ['| 文件 | 原件 | SHA-256 |', '|---|---|---|'] + [
        '| %s | %s | %s |' % (n, s['path'], s['sha256'][:16]) for n, s in sorted(given.items())] if given else ['无（从 C1 开始）']
    out += ['', '## 模块关卡', '', '| 模块 | 关卡 | 指纹状态 | 待办 |', '|---|---|---|---|']
    problems = []
    for module in run:
        found, notes = gate(module, root, write=False)
        problems += ['%s：%s' % (module, p) for p in found]
        out.append('| %s | %s | %s | %d |' % (module, 'FAIL' if found else 'PASS', states.get(module, '未记录'), len(notes)))
    out += ['', '## 产出', '']
    if 'C1' in run:
        reqs = requirements.get('requirements') or []
        out.append('- C1：需求 %d 条，需求澄清 %d 个，降额等级 %s' % (
            len(reqs), len(requirements.get('clarifications') or []), (requirements.get('derating') or {}).get('level', '未定')))
    if 'C2' in run:
        arch = load(record, 'architecture.json')[0] or {}
        out.append('- C2：功能块 %d 个，跨块流向 %d 条，隔离边界 %d 条' % tuple(
            len(arch.get(k) or []) for k in ('blocks', 'flows', 'boundaries')))
    if 'C3' in run:
        out += ['- C3：块文件 %d 个（%s/），方案比较与核心选型见下表' % (len(block_circuits.read_dir(record)[0]), block_circuits.DIR),
                ''] + report.render_scheme_criteria(load(record, 'scheme-criteria.json')[0] or {})
    if 'C4' in run:
        calcs = closure.get('calculations') or []
        tally = {}
        for c in calcs:
            tally[c.get('conclusion')] = tally.get(c.get('conclusion'), 0) + 1
        out.append('- C4：计算 %d 项（%s）' % (len(calcs), '，'.join('%s %d' % kv for kv in sorted(tally.items(), key=str))))
    if 'C5' in run or 'C6' in run:
        intent = load(record, 'electrical-intent.json')[0] or {}
        out.append('- 设计网表：器件 %d 个，网络 %d 个' % (len(intent.get('components') or []), len(intent.get('nets') or {})))
    if 'C6' in run:
        plan = load(record, 'page-plan.json')[0] or {}
        out.append('- C6：图页 %d 页，原理图在 原理图/' % len(plan.get('pages') or []))
    work = [w for w in closure.get('work_items') or [] if isinstance(w, dict) and w.get('status') == 'open']
    inputs = [w for w in work if w.get('stage') == 'input']
    out += ['', '## 给定输入的问题（input 待办）', '']
    out += ['| 编号 | 上游模块 | 文件 | 问题与建议 |', '|---|---|---|---|'] + [
        '| %s | %s | %s | %s |' % (w.get('id'), w.get('upstream'), w.get('given'), report.cell(w.get('action'))) for w in inputs] \
        if inputs else ['无']
    out += ['', '## 其余未关闭待办', '']
    rest = [w for w in work if w.get('stage') != 'input']
    out += ['| 编号 | 阶段 | 动作 |', '|---|---|---|'] + [
        '| %s | %s | %s |' % (w.get('id'), report.STAGES.get(w.get('stage'), w.get('stage')), report.cell(w.get('action')))
        for w in rest] if rest else ['无']
    return '\n'.join(out) + '\n', problems


def check_delivery(root):
    """A module run's delivery folder (workflow-handoff.md): the module report, record/, datasheets, and the drawing only
    when C6 ran; every module of the run passes its gate and is recorded fresh."""
    root = Path(root)
    errors = []
    try:
        scope = scope_of(closure_audit.load_task(root))
    except ValueError as exc:
        return [str(exc)]
    if not scope:
        return ['record/task.json 没有 modules：整板交付用 pack_design.py']
    run, _ = scope
    present = {p.name for p in root.iterdir() if not p.name.startswith('.')}
    allowed = set(MODULE_TOP) if 'C6' in run else set(MODULE_TOP) - {'原理图'}
    extra = sorted(present - allowed)
    if extra:
        errors.append('单独运行 %s 的交付目录只放 %s：%s 不该在这里' % ('–'.join((run[0], run[-1])), '、'.join(sorted(allowed)), '、'.join(extra)))
    for name in (MODULE_REPORT, 'record') + (('原理图',) if 'C6' in run else ()):
        if name not in present:
            errors.append('缺少 %s' % name)
    if 'C6' in run:
        for name in SCHEMATIC_FILES:
            if not (root / '原理图' / name).is_file():
                errors.append('原理图/%s 缺失' % name)
    states = status(root)
    for module in run:
        found, _ = gate(module, root, write=False)
        errors += ['%s 关卡：%s' % (module, p) for p in found]
        if states.get(module) != 'OK':
            errors.append('%s 在 record/modules.json 里是 %s：重跑 check_module.py %s' % (module, states.get(module, '未记录'), module))
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('module', choices=MODULES + ('status', 'report', 'pack', 'return'))
    ap.add_argument('design_root', type=Path, help='设计目录（含 record/）')
    ap.add_argument('--given', action='append', default=[], help='单独运行时任务书给定的输入文件（记入指纹）')
    ap.add_argument('--block', help='C4：只核这个块的块设计（architecture.json 的块 id），不记入 modules.json')
    ap.add_argument('--from', dest='source', help='return：发现问题的任务，如 C4.2')
    ap.add_argument('--to', dest='target', help='return：回到的任务，如 C2.2')
    ap.add_argument('--reason', help='return：原因')
    ap.add_argument('--evidence', help='return：依据（计算编号、手册页码、检查输出）')
    args = ap.parse_args(argv)
    if args.block and args.module != 'C4':
        ap.error('--block 只用于 C4')
    if args.module == 'return':
        problems = record_return(args.design_root, args.source, args.target, args.reason, args.evidence)
        for problem in problems:
            print('PROBLEM:', problem)
        print('FAIL' if problems else 'recorded')
        return 1 if problems else 0
    if args.module == 'status':
        found = status(args.design_root)
        for module, state in found.items():
            print('%s %s' % (module, state))
        return 0 if all(s == 'OK' for s in found.values()) else 1
    if args.module == 'report':
        text_, problems = module_report(args.design_root)
        (args.design_root / MODULE_REPORT).write_text(text_, encoding='utf-8')
        print('wrote', args.design_root / MODULE_REPORT)
        for problem in problems:
            print('PROBLEM:', problem)
        return 1 if problems else 0
    if args.module == 'pack':
        errors = check_delivery(args.design_root)
        for error in errors:
            print('ERROR:', error)
        print('FAIL' if errors else 'PASS')
        return 1 if errors else 0
    problems, notes = gate(args.module, args.design_root, block=args.block)
    for note in notes:
        print('PENDING:', note)
    for problem in problems:
        print('PROBLEM:', problem)
    if problems:
        print('FAIL')
        return 1
    if args.block:
        print('PASS（只核了块 %s，没有记入 modules.json；全部块写完后不带 --block 再跑一次）' % args.block)
        return 0
    record_module(args.design_root, args.module, args.given)
    print('PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
