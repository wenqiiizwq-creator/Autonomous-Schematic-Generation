#!/usr/bin/env python3
"""典型电路库（references/typical-circuits/*.md）的读取：每个典型电路声明的电路类型、每种实现方案落实的共用设计准则。

典型电路文件头部一行 `电路类型：<词表名>[、<词表名>…]`（没有对应类型写 `无`），每种实现方案一条 `- **落实规则**：G0x-nnn[、…]`（写 `无` 时可带括号说明）。
这是 ASG 一侧的典型电路→准则映射，与 SR 的 `catalog.BASIS`（SR 规则→设计准则）对称；分页方案用了哪个做法，
设计完成核对就要求它落实的规则被引用（audit_design_closure.audit_guidelines）。
"""
import re
from pathlib import Path

CIRCUITS_DIR = Path(__file__).resolve().parent.parent / 'references' / 'typical-circuits'
CIRCUIT_TYPES_LINE = '电路类型：'
RULES_BULLET = re.compile(r'^- \*\*落实规则\*\*：(.*)$')
RULE_ID = re.compile(r'G0[1-9]-\d{3}')
NONE = '无'


def _names(rest):
    rest = rest.strip()
    return [] if not rest or rest.startswith(NONE) else [n.strip() for n in re.split(r'[、,，]', rest) if n.strip()]


def load(circuits_dir=None):
    """{typical circuit id: {title, function, circuit_types: [..] | None, implementations: {name: {criteria: [..] | None}}}};
    None means the line is missing (the tests and the audit tell that apart from an explicit 无)."""
    circuits_dir = Path(CIRCUITS_DIR if circuits_dir is None else circuits_dir)   # resolved per call so tests can point elsewhere
    index = {}
    for md in sorted(circuits_dir.glob('*.md')) if circuits_dir.is_dir() else []:
        info = {'title': '', 'function': '', 'circuit_types': None, 'implementations': {}}
        current = None
        for line in md.read_text(encoding='utf-8').splitlines():
            if line.startswith('# ') and not info['title']:
                info['title'] = line[2:].strip()
            elif line.startswith('功能：'):
                info['function'] = line[3:].strip()
            elif line.startswith(CIRCUIT_TYPES_LINE) and current is None:
                info['circuit_types'] = _names(line[len(CIRCUIT_TYPES_LINE):])
            elif line.startswith('### '):
                current = line[4:].strip()
                info['implementations'][current] = {'criteria': None}
            elif current is not None and RULES_BULLET.match(line):
                rest = RULES_BULLET.match(line).group(1).strip()
                info['implementations'][current]['criteria'] = [] if rest.startswith(NONE) else RULE_ID.findall(rest)
        index[md.stem] = info
    return index


def claimed(references, patterns=None):
    """What the pattern implementations a page plan names (`<模式>#<做法>` strings) declare: {'circuit_types': {type: [ref..]},
    'criteria': {criterion id: [ref..]}}. Unknown circuits or implementations are skipped (render_design_report reports them)."""
    patterns = load() if patterns is None else patterns
    out = {'circuit_types': {}, 'criteria': {}}
    for ref in sorted(set(references)):
        pid, _, approach = str(ref).partition('#')
        info = patterns.get(pid)
        if not info or approach not in info['implementations']:
            continue
        for t in info['circuit_types'] or []:
            out['circuit_types'].setdefault(t, []).append(ref)
        for gid in info['implementations'][approach]['criteria'] or []:
            out['criteria'].setdefault(gid, []).append(ref)
    return out
