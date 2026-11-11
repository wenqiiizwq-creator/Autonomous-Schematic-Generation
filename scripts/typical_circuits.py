#!/usr/bin/env python3
"""读取典型电路的选择资料及可选的落实规则。规则仅供参考，不决定本板准则适用范围。"""
import re
from pathlib import Path

CIRCUITS_DIR = Path(__file__).resolve().parent.parent / 'references' / 'knowledge' / '典型电路'
CIRCUIT_TYPES_LINE = '电路类型：'
IMPLEMENTATIONS = '## 实现方案'   # only the ### headings of this section are implementations
RULES_BULLET = re.compile(r'^- \*\*落实规则\*\*：(.*)$')
RULE_ID = re.compile(r'G0[1-9]-\d{3}')
NONE = '无'


def _names(rest):
    rest = re.sub(r'（[^）]*）', '', rest).strip()   # a note such as POWER_CONVERTER（电阻限流为 无） is not a name
    return [] if not rest or rest.startswith(NONE) else [n.strip() for n in re.split(r'[、,，]', rest) if n.strip()]


def load(circuits_dir=None):
    """{typical circuit id: {title, function, circuit_types: [..] | None, implementations: {name: {criteria: [..] | None}}}};
    None means the optional rule line is absent; an explicit 无 is an empty list."""
    circuits_dir = Path(CIRCUITS_DIR if circuits_dir is None else circuits_dir)   # resolved per call so tests can point elsewhere
    index = {}
    for md in sorted(circuits_dir.glob('*.md')) if circuits_dir.is_dir() else []:
        if md.name == 'README.md':
            continue
        info = {'title': '', 'function': '', 'circuit_types': None, 'implementations': {}}
        current, in_implementations = None, False
        for line in md.read_text(encoding='utf-8').splitlines():
            if line.startswith('# ') and not info['title']:
                info['title'] = line[2:].strip()
            elif line.startswith('功能：'):
                info['function'] = line[3:].strip()
            elif line.startswith(CIRCUIT_TYPES_LINE) and current is None:
                info['circuit_types'] = _names(line[len(CIRCUIT_TYPES_LINE):])
            elif line.startswith('## '):
                current, in_implementations = None, line.strip() == IMPLEMENTATIONS
            elif line.startswith('### ') and in_implementations:
                current = line[4:].strip()
                info['implementations'][current] = {'criteria': None}
            elif current is not None and RULES_BULLET.match(line):
                rest = RULES_BULLET.match(line).group(1).strip()
                info['implementations'][current]['criteria'] = [] if rest.startswith(NONE) else RULE_ID.findall(rest)
        index[md.stem] = info
    return index
