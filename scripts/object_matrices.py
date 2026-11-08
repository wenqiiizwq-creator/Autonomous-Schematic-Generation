#!/usr/bin/env python3
"""对全部对象核对的矩阵与保护逻辑状态表（design-closure.json 的 matrix_version 1，见 references/design-closure.md）。

整板评测 2026-11-07：6 个漏项里 3 个是同一条判据只核了一个对象（复位门限只对 MCU 核、温度只核工作范围、
防反接只看功率路径），1 个是保护逻辑的状态组合没列。表的行和格由本工具从设计网表列出，设计者逐格写结论：

- supervised_rails：受监督电源轨（电压监控器件接的电源轨，含经 filtered_supply 派生的轨）× 轨上每颗有源负载；
- temperature：每颗器件（测试点、机械件除外）的工作温度与存储温度 × 需求的两个温度范围；
- port_stress：每个连接器的每项外部应力 × 路径上每颗器件（端口网络上的、经串联电阻/磁珠/电感/保险丝一两跳到的），
  以及端口回线被开关器件（低边防反接 MOS 等）隔开时，与板地相连的其他端口（地回路的旁路）；
- protection_states：有 eFuse/热插拔、电压监控或故障/关断/复位网络的功能块 × 上电、正常开、正常关、短路、复位
  × 锁状态（清除/置位；块没有锁时只一列）。

结论只有三种来源：引用一条计算的检查（`calc` + `check`，结论由检查的数字推出，检查名或 `ref`/`objects` 要点名这个对象）、
温度格直接写手册数值（`source` 引手册页，或 `spec` 表示已写进该器件的采购规格）、`not_applicable` 加理由。
状态表的行另可引用证据条目（`evidence: "<证据编号>#<定位>"`）并写 `verdict`。缺结论记 `matrix_cell_missing`（设计没做完），
结论不满足记 `matrix_cell_failed`，结论与引用的检查矛盾或引用不存在记错误。

用法：
  python3 object_matrices.py skeleton --intent electrical-intent.json [--closure design-closure.json] --out matrices.json
列出全部行和格；已在 design-closure.json 写了结论的格原样带过来，其余结论为空，`candidates` 列出名字点到这个对象的现有检查，
只作提示：候选不是结论，要人判断它核的是不是这一格的判据。
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import operating_inputs  # noqa: E402
from schematic_layout import part_classes  # noqa: E402
from schematic_layout.citations import check_source  # noqa: E402

KEY = 'matrices'
VERSION_KEY = 'matrix_version'
TABLES = ('supervised_rails', 'temperature', 'port_stress', 'protection_states')

# 电压监控/复位芯片：按库目录、名字或系列认；别的器件（热插拔的欠压门限等）可以由设计者自己加一行。
SUPERVISOR_FOLDER = re.compile(r'Supervisor|电压监控|复位芯片', re.I)
SUPERVISOR_SERIES = re.compile(r'^(?:TPS3[0-9]{3}|TPS38\d\d|TLV8\d\d|MAX8\d\d|MAX6\d{3}|MAX16\d{3}|APX8\d\d|ADM8\d\d|'
                               r'STM8\d\d|LM8\d\d[A-Z]|MCP1[0-3]\d|NCP30\d|BD52|BD48|XC61|R3111|TCM8\d\d|LTC29\d\d|ISL880)', re.I)
LOAD_KINDS = ('ic', 'opto')
# 串联在信号路径上、应力沿它传到下一级的两端器件；电阻、磁珠、电感本身的应力由功耗与降额检查管，不进格。
SERIES_KINDS = ('resistor', 'ferrite', 'inductor', 'fuse')
NOT_STRESSED = ('connector', 'testpoint', 'mechanical', 'resistor', 'ferrite', 'inductor', 'jumper')
NO_TEMPERATURE = ('testpoint', 'mechanical')
SERIES_HOPS = 3    # 输入滤波链：保险丝→共模/差模电感→检流电阻，三跳内到保护与开关器件
BIG_NET = 25    # 走到这么多脚的网络（板上主电源轨）就不再往下走：应力在那里已由轨上的器件分担，另由电源轨的计算管
SWITCH_KINDS = ('mosfet', 'bjt', 'diode', 'relay')    # 隔离器跨两个地是隔离，不是开关
FAULT_NET = re.compile(r'(?:^|_)N?(?:FLT|FAULT|LATCH|SHDN|SHUTDOWN|RST|RESET|TRIP|KILL|OCP|OVP)(?:N|_?B)?(?:_|\d|$)', re.I)
STATES = ('power_up', 'normal_on', 'normal_off', 'short', 'reset')
STATE_NAMES = {'power_up': '上电', 'normal_on': '正常开', 'normal_off': '正常关', 'short': '短路', 'reset': '复位'}
LATCH_KINDS = ('hardware', 'firmware', 'none')
LATCH_STATES = ('clear', 'set')
VERDICTS = ('ok', 'fail', 'not_applicable')
EVIDENCE_REF = re.compile(r'^([^#\s]+)#(.+)$')
REQ_SOURCE = re.compile(r'^(req|clarification):(\S+)$')
TOKEN = re.compile(r'[A-Za-z][A-Za-z0-9]{3,}')
# 受监督轨的格核的是门限，不是稳压精度：“+3V3 下限 对 YT9218 3.135 V”不能顶“复位门限 对 YT9218”（Matrix 2026-11-07）。
THRESHOLD_WORDS = re.compile(r'门限|阈值|复位|欠压|掉电|threshold|\bV?IT\b|\bUV(?:LO)?\b|\bBOR\b|\bPOR\b|\bPVD\b|reset', re.I)
# 端口应力的种类与它的检查名里该有的词：钳位对总线脚额定、反接时的电压与回路……
# 回线被开关器件隔开时，经其他端口的地回路：检查要说的是回流或地电位（Matrix 2026-11-07 低边防反接断开地回路）。
RETURN_WORDS = re.compile(r'地回路|回流|回线|地电位|地偏移|反接|旁路|ground|return', re.I)
STRESS_KINDS = {
    'surge': re.compile(r'(?<!启动)(?<!合闸)浪涌|钳位|surge|clamp|8/20|10/700|1\.2/50', re.I),
    'esd': re.compile(r'ESD|静电|钳位|clamp', re.I),
    'eft': re.compile(r'EFT|脉冲群|钳位|clamp', re.I),
    'reverse_polarity': re.compile(r'反接|反向|反极性|reverse', re.I),
    'overvoltage': re.compile(r'过压|误接|钳位|overvoltage|clamp', re.I),
    'short': re.compile(r'短路|短接|short', re.I),
    'miswire': re.compile(r'误接|错接|miswir', re.I),
    'hot_plug': re.compile(r'热插拔|带电插拔|插拔|hot.?plug', re.I),
}


TEMPERATURE_RANGE = re.compile(r'([+\-−]?\s*\d+(?:\.\d+)?)\s*(?:℃|°C)?\s*[～~至到]\s*([+\-−]?\s*\d+(?:\.\d+)?)\s*(?:℃|°C)')


def temperature_ranges(words):
    """[(min, max)] 写成 “−40～+85 ℃” 的温度范围（带符号）。"""
    def num(x):
        return float(x.replace('−', '-').replace(' ', ''))
    return [(num(a), num(b)) for a, b in TEMPERATURE_RANGE.findall(str(words or '').replace('°C', '℃'))]


def states_range(words, lo, hi, covering=False):
    """文字写了这个温度范围（covering：写了一个不窄于它的范围）。"""
    for a, b in temperature_ranges(words):
        if (a <= lo and b >= hi) if covering else (a == lo and b == hi):
            return True
    return False


def text(value):
    return isinstance(value, str) and bool(value.strip())


def finite(x):
    return operating_inputs.finite(x)


def net_table(intent):
    nets = intent.get('nets') or {}
    if isinstance(nets, dict):
        return {k: [str(p) for p in v] for k, v in nets.items() if isinstance(v, list)}
    return {n['name']: [str(p) for p in n.get('pins') or []] for n in nets if isinstance(n, dict) and text(n.get('name'))}


class Board:
    """设计网表的查询：器件、类型、各网络上的引脚、网络角色。"""

    def __init__(self, intent):
        self.intent = intent
        self.comps = {c['ref']: c for c in intent.get('components') or [] if isinstance(c, dict) and text(c.get('ref'))}
        self.kinds = {ref: part_classes.kind_of(c)[0] for ref, c in self.comps.items()}
        self.nets = net_table(intent)
        self.roles = intent.get('net_roles') or {}
        self.of = {}
        for net, pins in self.nets.items():
            for pin in pins:
                ref, _, number = pin.rpartition('.')
                self.of.setdefault(ref, {}).setdefault(net, []).append(number)

    def role(self, net):
        role = self.roles.get(net)
        if role:
            return role
        return 'return' if re.search(r'(?:^|[/_])(?:[ADPS]?GND\w*|VSS\w*|RTN\w*|0V)$', net, re.I) else None

    def refs_on(self, net):
        found = {}
        for pin in self.nets.get(net, []):
            ref, _, number = pin.rpartition('.')
            found.setdefault(ref, []).append(number)
        return found

    def block(self, ref):
        return str(part_classes.fields(self.comps.get(ref, {})).get('Circuit') or '').strip()


def supervisor(comp):
    if part_classes.kind_of(comp)[0] != 'ic':
        return False
    f = part_classes.fields(comp)
    if str(f.get('ComponentRole') or f.get('Kind') or '').lower() == 'supervisor':
        return True
    parts = [str(comp.get(k) or '').split(':')[-1].strip() for k in ('value', 'mpn')]
    return bool(SUPERVISOR_FOLDER.search(str(comp.get('datasheet') or '')) or any(SUPERVISOR_SERIES.match(p) for p in parts))


def derived_rails(board, rail):
    """这条轨，以及经 filtered_supply（磁珠、滤波）从它派生的轨。"""
    found, todo = [rail], [rail]
    for _ in range(8):
        nxt = []
        for f in board.intent.get('filtered_supply') or []:
            if isinstance(f, dict) and f.get('from') in todo and f.get('net') not in found:
                found.append(f['net'])
                nxt.append(f['net'])
        todo = nxt
        if not todo:
            break
    return found


def supervised_rails(board):
    """{轨: {supervisors, loads: {位号: [经过的轨]}}}：监控器件接到的每条电源轨与其上的有源负载。"""
    out = {}
    for ref, comp in sorted(board.comps.items()):
        if not supervisor(comp):
            continue
        for net in sorted(board.of.get(ref, {})):
            if board.role(net) != 'power':
                continue
            row = out.setdefault(net, {'supervisors': [], 'loads': {}})
            row['supervisors'].append(ref)
    for rail, row in out.items():
        for net in derived_rails(board, rail):
            for ref in board.refs_on(net):
                if board.kinds.get(ref) in LOAD_KINDS and ref not in row['supervisors']:
                    row['loads'].setdefault(ref, []).append(net)
    return out


def temperature_objects(board):
    return sorted(ref for ref, kind in board.kinds.items() if kind not in NO_TEMPERATURE)


def ports(board):
    """{连接器: {nets, objects: {位号: [经过的网络]}, return_breaks: [{net, via, to, ports}]}}。"""
    out = {}
    for ref in sorted(board.comps):
        if board.kinds.get(ref) != 'connector':
            continue
        own = sorted(board.of.get(ref, {}))
        objects, breaks = {}, []
        for net in own:
            if board.role(net) == 'return':
                breaks.extend(return_breaks(board, ref, net))
                continue
            for r, nets in reach(board, net, SERIES_HOPS + 1, ref).items():
                objects.setdefault(r, [])
                objects[r] += [n for n in nets if n not in objects[r]]
        out[ref] = {'nets': own, 'objects': {r: v for r, v in sorted(objects.items()) if board.kinds.get(r) not in NOT_STRESSED},
                    'return_breaks': breaks}
    return out


def reach(board, start, depth, port):
    """{位号: [网络]}：端口网络上的器件，以及经串联两端器件（保险丝、检流电阻、磁珠）再走 depth−1 跳到的；
    不走进回流网络和板上主电源轨（BIG_NET 以上的网络）。"""
    found, frontier, seen = {}, [start], {start}
    for level in range(depth):
        nxt = []
        for net in frontier:
            for ref in board.refs_on(net):
                if ref == port:
                    continue
                found.setdefault(ref, [])
                if net not in found[ref]:
                    found[ref].append(net)
                others = [n for n in board.of.get(ref, {}) if n != net]
                if board.kinds.get(ref) in SERIES_KINDS and len(board.of.get(ref, {})) == 2 and level + 1 < depth:
                    for n in others:
                        if n not in seen and board.role(n) != 'return' and len(board.nets.get(n, [])) <= BIG_NET:
                            seen.add(n)
                            nxt.append(n)
        frontier = nxt
    return found


def return_breaks(board, port, net):
    """端口回线经开关器件（防反接 MOS、二极管）才接到另一回流网络时：那个回流网络上还有哪些端口（地回路的旁路）。"""
    out = []
    for ref, pins in board.refs_on(net).items():
        if ref == port or board.kinds.get(ref) not in SWITCH_KINDS:
            continue
        for other in board.of.get(ref, {}):
            if other == net or board.role(other) != 'return':
                continue
            if len(board.nets.get(other, [])) <= len(board.nets.get(net, [])):
                continue    # 只从被隔开的一侧（端口自己的回线）看；板地一侧看到的是同一个回路
            peers = sorted(r for r in board.refs_on(other) if r != port and board.kinds.get(r) == 'connector')
            if peers:
                out.append({'net': net, 'via': ref, 'to': other, 'ports': peers})
    return out


def protection_blocks(board):
    """{功能块: 为什么要列状态表}：块里有 eFuse/热插拔、电压监控，或接到故障/关断/复位网络。"""
    out = {}
    for ref, comp in sorted(board.comps.items()):
        block = board.block(ref)
        if not block:
            continue
        why = []
        if operating_inputs.hot_part(comp):
            why.append('%s 是 eFuse/热插拔/负载开关' % ref)
        if supervisor(comp):
            why.append('%s 是电压监控/复位器件' % ref)
        if board.kinds.get(ref) in ('ic', 'opto', 'mosfet', 'bjt'):
            nets = sorted(n for n in board.of.get(ref, {}) if FAULT_NET.search(n))
            if nets:
                why.append('%s 接 %s' % (ref, '、'.join(nets[:4])))
        if why:
            out.setdefault(block, []).extend(why)
    return out


def expected(intent):
    """本设计应有的行与格（不含结论）。"""
    board = Board(intent)
    return {'board': board, 'supervised_rails': supervised_rails(board), 'temperature': temperature_objects(board),
            'port_stress': ports(board), 'protection_states': protection_blocks(board)}


# ---------------------------------------------------------------- 结论

def mentions(check, ref, comp):
    """检查点名了这个对象：`ref`/`objects` 写了它，或名字里有位号、值、料号或其前段（STM32 之于 STM32F107VCT6）。"""
    if check.get('ref') == ref or ref in (check.get('objects') or []):
        return True
    name = str(check.get('name') or '')
    if re.search(r'(?<![A-Za-z0-9])%s(?![0-9])' % re.escape(ref), name):
        return True
    ids = [str(comp.get(k) or '').split(':')[-1].upper() for k in ('value', 'mpn')]
    for token in TOKEN.findall(name):
        t = token.upper()
        if any(i and (i.startswith(t) or t.startswith(i)) for i in ids) and not t.isalpha():
            return True
    return False


def candidates(calculations, ref, comp, words=None):
    found = []
    for cid, row in calculations.items():
        for c in row.get('checks') or []:
            if isinstance(c, dict) and mentions(c, ref, comp) and (words is None or words.search(str(c.get('name') or ''))):
                found.append({'calc': cid, 'check': c.get('name')})
    return found


def find_check(calculations, cid, name):
    for c in (calculations.get(cid) or {}).get('checks') or []:
        if isinstance(c, dict) and c.get('name') == name:
            return c
    return None


def cell_verdict(cell, where, calculations, holds, error, objects=(), board=None, about=None):
    """'ok'/'fail'/'not_applicable'，没写结论时 None。objects：这一格必须点名的位号。"""
    if not isinstance(cell, dict):
        return None
    verdict = cell.get('verdict')
    if verdict is not None and verdict not in VERDICTS:
        error('matrix_schema', '%s：verdict 只能是 ok、fail、not_applicable' % where)
        return None
    if verdict == 'not_applicable':
        if not text(cell.get('reason')):
            error('matrix_not_applicable_without_reason', where)
            return None
        return 'not_applicable'
    if text(cell.get('calc')) or text(cell.get('check')):
        check = find_check(calculations, cell.get('calc'), cell.get('check'))
        if check is None:
            error('matrix_check_unknown', '%s：%s 里没有检查“%s”' % (where, cell.get('calc'), cell.get('check')))
            return None
        for ref in objects:
            if board is not None and not mentions(check, ref, board.comps.get(ref, {})):
                error('matrix_check_not_about_object', '%s：检查“%s”没有点名 %s（在名字里写位号或型号，或在检查里写 objects）'
                      % (where, check.get('name'), ref))
                return None
        if about is not None and not about[1].search(str(check.get('name') or '')):
            error('matrix_check_not_about_criterion', '%s：检查“%s”核的不是%s（名字里没有对应的词）' % (where, check.get('name'), about[0]))
            return None
        derived = 'ok' if holds(check) else 'fail'
        if verdict is not None and verdict != derived:
            error('matrix_verdict_contradicts_check', '%s：写 %s，检查推出 %s' % (where, verdict, derived))
        return derived
    return None


def evidence_verdict(row, where, evidence, error):
    """状态表的行可以引用证据条目：evidence 写 '<证据编号>#<定位>'，verdict 写 ok/fail。"""
    m = EVIDENCE_REF.match(str(row.get('evidence') or ''))
    if not m:
        return None
    if m.group(1) not in evidence:
        error('matrix_evidence_unknown', '%s：%s' % (where, m.group(1)))
        return None
    if row.get('verdict') not in ('ok', 'fail'):
        error('matrix_schema', '%s：引用证据的行要写 verdict（ok/fail）' % where)
        return None
    return row['verdict']


# ---------------------------------------------------------------- 审计

def audit(record, intent, calculations, evidence, requirements, holds, error, need, extra=()):
    """核对 record['matrices']；返回审计结果里的 matrices 一节。"""
    exp = expected(intent)
    board = exp['board']
    tables = record.get(KEY)
    if not isinstance(tables, dict):
        error('matrix_schema', 'matrices 要是对象，含 %s' % '、'.join(TABLES))
        tables = {}
    summary = {}
    counters = {}

    def count(table, verdict, where):
        c = counters.setdefault(table, {'cells': 0, 'concluded': 0, 'missing': [], 'failed': []})
        c['cells'] += 1
        if verdict is None:
            c['missing'].append(where)
            need('matrix_cell_missing', where)
        else:
            c['concluded'] += 1
            if verdict == 'fail':
                c['failed'].append(where)
                need('matrix_cell_failed', where)

    # 受监督电源轨 × 每颗负载
    rows = {r.get('rail'): r for r in tables.get('supervised_rails') or [] if isinstance(r, dict)}
    for rail, info in exp['supervised_rails'].items():
        row = rows.get(rail) or {}
        if row.get('verdict') == 'not_applicable':
            count('supervised_rails', cell_verdict(row, '受监督轨 %s' % rail, calculations, holds, error), '受监督轨 %s' % rail)
            continue
        cells = {c.get('ref'): c for c in row.get('cells') or [] if isinstance(c, dict)}
        for ref in sorted(info['loads']):
            where = '受监督轨 %s（%s）的门限 × %s %s 最低工作电压' % (rail, '、'.join(info['supervisors']), ref,
                                                         board.comps[ref].get('value') or '')
            count('supervised_rails', cell_verdict(cells.get(ref), where, calculations, holds, error, (ref,), board,
                                                   ('门限', THRESHOLD_WORDS)), where)
        for ref in cells:
            if ref not in info['loads']:
                error('matrix_unknown_object', '受监督轨 %s：%s 不是这条轨上的负载' % (rail, ref))
    for rail in rows:
        if rail not in exp['supervised_rails']:
            for c in rows[rail].get('cells') or []:     # 设计者自己加的监督轨（热插拔欠压等）同样逐格核
                if isinstance(c, dict):
                    where = '受监督轨 %s × %s' % (rail, c.get('ref'))
                    if c.get('ref') not in board.comps:
                        error('matrix_unknown_object', where)
                        continue
                    count('supervised_rails', cell_verdict(c, where, calculations, holds, error, (c.get('ref'),), board,
                                                           ('门限', THRESHOLD_WORDS)), where)

    # 温度
    temp = tables.get('temperature') if isinstance(tables.get('temperature'), dict) else {}
    ranges = {}
    for key, title in (('operating', '工作温度'), ('storage', '存储温度')):
        r = temp.get(key)
        if not (isinstance(r, dict) and finite(r.get('min')) and finite(r.get('max'))):
            need('matrix_temperature_requirement_missing', '温度矩阵：写需求的%s范围 %s {min, max, source}' % (title, key))
            continue
        m = REQ_SOURCE.match(str(r.get('source') or ''))
        if not m:
            error('matrix_temperature_requirement_source', '%s：source 写 req:<需求编号> 或 clarification:<澄清编号>' % title)
        elif m.group(1) == 'req':
            req = requirements.get(m.group(2))
            if req is None:
                error('matrix_temperature_requirement_source', '%s：没有需求 %s' % (title, m.group(2)))
            elif text(req.get('text')) and not states_range(req['text'], r['min'], r['max']):
                error('matrix_temperature_requirement_source', '%s：需求 %s 的文字里没有 %g～%g ℃' % (title, m.group(2), r['min'], r['max']))
        ranges[key] = r
    seen = {}
    for i, row in enumerate(temp.get('rows') or []):
        if not isinstance(row, dict) or not isinstance(row.get('refs'), list):
            error('matrix_schema', '温度矩阵 rows[%d] 要写 refs' % i)
            continue
        for ref in row['refs']:
            if ref not in board.comps:
                error('matrix_unknown_object', '温度矩阵 rows[%d]：%s' % (i, ref))
            elif ref in seen:
                error('matrix_duplicate_object', '温度矩阵：%s 写在两行' % ref)
            else:
                seen[ref] = row
    for ref in exp['temperature']:
        row = seen.get(ref, {})
        for key, title in (('operating', '工作温度'), ('storage', '存储温度')):
            where = '%s %s 的%s' % (ref, board.comps[ref].get('value') or '', title)
            count('temperature', temperature_verdict(row, key, ranges.get(key), where, board, error, extra), where)

    # 端口应力
    rows = {r.get('port'): r for r in tables.get('port_stress') or [] if isinstance(r, dict)}
    for port, info in exp['port_stress'].items():
        row = rows.get(port) or {}
        where = '端口 %s' % port
        if text(row.get('no_stress_reason')):
            count('port_stress', 'not_applicable', where + ' 无外部应力')
            continue
        stresses = [s for s in row.get('stresses') or [] if isinstance(s, dict) and text(s.get('id'))]
        if not stresses:
            count('port_stress', None, where + '：写 stresses（浪涌、反接、过压、短路等，每项 {id, kind, source}）或 no_stress_reason')
        cells = {(c.get('stress'), c.get('ref')): c for c in row.get('cells') or [] if isinstance(c, dict)}
        for s in stresses:
            if not text(s.get('source')):
                error('matrix_stress_without_source', '%s 应力 %s' % (where, s['id']))
            if s.get('kind') not in STRESS_KINDS:
                error('matrix_schema', '%s 应力 %s：kind 取 %s' % (where, s['id'], '、'.join(STRESS_KINDS)))
                continue
            for ref, nets in info['objects'].items():
                w = '%s %s × %s %s（%s）' % (where, s['id'], ref, board.comps[ref].get('value') or '', '、'.join(nets))
                count('port_stress', cell_verdict(cells.get((s['id'], ref)), w, calculations, holds, error, (ref,), board,
                                                  (s['kind'], STRESS_KINDS[s['kind']])), w)
        breaks = {(b.get('via'), b.get('port')): b for b in row.get('return_paths') or [] if isinstance(b, dict)}
        for b in info['return_breaks']:
            for peer in b['ports']:
                w = '%s 回线 %s 经 %s 才接 %s：经 %s 的地回路' % (where, b['net'], b['via'], b['to'], peer)
                count('port_stress', cell_verdict(breaks.get((b['via'], peer)), w, calculations, holds, error, (peer,), board,
                                                  ('地回路', RETURN_WORDS)), w)
        for key in cells:
            if key[1] not in info['objects'] or key[0] not in {s['id'] for s in stresses}:
                error('matrix_unknown_object', '%s：格 %s × %s 不在矩阵里' % (where, key[0], key[1]))

    # 保护逻辑状态表
    rows = {r.get('block'): r for r in tables.get('protection_states') or [] if isinstance(r, dict)}
    for block, why in exp['protection_states'].items():
        row = rows.get(block) or {}
        latch = row.get('latch')
        if latch not in LATCH_KINDS:
            count('protection_states', None, '功能块 %s（%s）：写 latch（hardware/firmware/none）和状态表' % (block, '；'.join(why[:3])))
            continue
        states = {(r.get('state'), r.get('latch')): r for r in row.get('rows') or [] if isinstance(r, dict)}
        for state in STATES:
            for lock in (LATCH_STATES if latch != 'none' else ('none',)):
                where = '功能块 %s：%s × 锁%s' % (block, STATE_NAMES[state], {'clear': '清除', 'set': '置位', 'none': '（无锁）'}[lock])
                r = states.get((state, lock))
                verdict = None
                if isinstance(r, dict):
                    verdict = evidence_verdict(r, where, evidence, error) or cell_verdict(r, where, calculations, holds, error)
                    if verdict in ('ok', 'fail') and not text(r.get('outcome')):
                        error('matrix_state_without_outcome', where + '：写 outcome（各输出与锁在这一状态怎样变化）')
                        verdict = None
                count('protection_states', verdict, where)
    for table in TABLES:
        c = counters.get(table, {'cells': 0, 'concluded': 0, 'missing': [], 'failed': []})
        summary[table] = c
    return summary


def temperature_verdict(row, key, required, where, board, error, extra=()):
    r = row.get(key) if isinstance(row, dict) else None
    if not isinstance(r, dict):
        return None
    if r.get('verdict') == 'not_applicable':
        if not text(r.get('reason')):
            error('matrix_not_applicable_without_reason', where)
            return None
        return 'not_applicable'
    if not (finite(r.get('min')) and finite(r.get('max'))):
        return None
    source = str(r.get('source') or '')
    if source == 'spec':
        for ref in row['refs']:
            if not states_range(part_classes.spec_text(board.comps.get(ref, {})), r['min'], r['max'], covering=True):
                error('matrix_temperature_not_in_spec', '%s：source 写 spec，但 %s 的规格没写 %g～%g ℃' % (where, ref, r['min'], r['max']))
                return None
    else:
        cited = check_source(source, (abs(r['min']), abs(r['max'])), extra)
        if cited is None:
            error('matrix_temperature_without_source', '%s：source 写 datasheet:<库内路径>#p<页> 或 spec' % where)
            return None
        if cited['status'] == 'FAIL':
            error('matrix_temperature_citation', '%s：%s' % (where, cited['reason']))
            return None
    if required is None:
        return None
    return 'ok' if r['min'] <= required['min'] and r['max'] >= required['max'] else 'fail'


# ---------------------------------------------------------------- 骨架

def skeleton(intent, record=None):
    """全部行和格；record 里已有的结论带过来，其余空着并列候选检查。"""
    record = record or {}
    exp = expected(intent)
    board = exp['board']
    have = record.get(KEY) if isinstance(record.get(KEY), dict) else {}
    calculations = {r['id']: r for r in record.get('calculations') or [] if isinstance(r, dict) and text(r.get('id'))}

    def keep(old, new):
        return old if isinstance(old, dict) and (old.get('verdict') or old.get('calc') or old.get('evidence')) else new

    old_rails = {r.get('rail'): r for r in have.get('supervised_rails') or [] if isinstance(r, dict)}
    rails = []
    for rail, info in exp['supervised_rails'].items():
        old = {c.get('ref'): c for c in (old_rails.get(rail) or {}).get('cells') or [] if isinstance(c, dict)}
        cells = [keep(old.get(ref), {'ref': ref, 'value': board.comps[ref].get('value'), 'via': nets, 'calc': None, 'check': None,
                                     'candidates': candidates(calculations, ref, board.comps[ref], THRESHOLD_WORDS)})
                 for ref, nets in sorted(info['loads'].items())]
        rails.append({'rail': rail, 'supervisors': info['supervisors'], 'cells': cells})
    old_temp = have.get('temperature') if isinstance(have.get('temperature'), dict) else {}
    done = {ref for row in old_temp.get('rows') or [] if isinstance(row, dict) for ref in row.get('refs') or []}
    rows = [row for row in old_temp.get('rows') or [] if isinstance(row, dict)]
    ctx = part_classes.context(intent)
    groups = {}
    for ref in exp['temperature']:
        if ref in done:
            continue
        if part_classes.part_class(board.comps[ref], ctx) == part_classes.COMMON:
            groups.setdefault(board.kinds[ref], []).append(ref)     # 常规件按类型一行，可以再拆
        else:
            rows.append({'refs': [ref], 'value': board.comps[ref].get('value'), 'operating': None, 'storage': None})
    for kind, refs in sorted(groups.items()):
        rows.append({'refs': refs, 'kind': kind, 'operating': None, 'storage': None})
    temp = {'operating': old_temp.get('operating'), 'storage': old_temp.get('storage'), 'rows': rows}
    old_ports = {r.get('port'): r for r in have.get('port_stress') or [] if isinstance(r, dict)}
    port_rows = []
    for port, info in exp['port_stress'].items():
        old = old_ports.get(port) or {}
        stresses = old.get('stresses') or []
        cells_old = {(c.get('stress'), c.get('ref')): c for c in old.get('cells') or [] if isinstance(c, dict)}
        cells = [keep(cells_old.get((s.get('id'), ref)),
                      {'stress': s.get('id'), 'ref': ref, 'value': board.comps[ref].get('value'), 'nets': nets, 'calc': None, 'check': None,
                       'candidates': candidates(calculations, ref, board.comps[ref], STRESS_KINDS.get(s.get('kind')))})
                 for s in stresses if isinstance(s, dict) for ref, nets in info['objects'].items()]
        breaks_old = {(b.get('via'), b.get('port')): b for b in old.get('return_paths') or [] if isinstance(b, dict)}
        paths = [keep(breaks_old.get((b['via'], peer)), {'via': b['via'], 'net': b['net'], 'to': b['to'], 'port': peer, 'calc': None,
                                                          'check': None, 'candidates': candidates(calculations, peer, board.comps[peer], RETURN_WORDS)})
                 for b in info['return_breaks'] for peer in b['ports']]
        entry = {'port': port, 'nets': info['nets'], 'objects': {r: board.comps[r].get('value') for r in info['objects']},
                 'stresses': stresses, 'cells': cells, 'return_paths': paths}
        if text(old.get('no_stress_reason')):
            entry['no_stress_reason'] = old['no_stress_reason']
        port_rows.append(entry)
    old_blocks = {r.get('block'): r for r in have.get('protection_states') or [] if isinstance(r, dict)}
    blocks = []
    for block, why in exp['protection_states'].items():
        old = old_blocks.get(block) or {}
        latch = old.get('latch')
        locks = ('none',) if latch == 'none' else LATCH_STATES
        rows_old = {(r.get('state'), r.get('latch')): r for r in old.get('rows') or [] if isinstance(r, dict)}
        rows_ = [keep(rows_old.get((s, l)), {'state': s, 'latch': l, 'outcome': None, 'verdict': None}) for s in STATES for l in locks]
        blocks.append({'block': block, 'why': why, 'latch': latch, 'rows': rows_})
    return {VERSION_KEY: 1, KEY: {'supervised_rails': rails, 'temperature': temp, 'port_stress': port_rows,
                                  'protection_states': blocks}}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command', required=True)
    sk = sub.add_parser('skeleton', help='列出全部行和格')
    sk.add_argument('--intent', type=Path, required=True)
    sk.add_argument('--closure', type=Path)
    sk.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    intent = json.loads(args.intent.read_text(encoding='utf-8'))
    record = json.loads(args.closure.read_text(encoding='utf-8')) if args.closure else None
    out = skeleton(intent, record)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    m = out[KEY]
    print('受监督轨 %d 条（%d 格）；温度 %d 行；端口 %d 个（%d 格，地回路 %d 格）；状态表 %d 块' % (
        len(m['supervised_rails']), sum(len(r['cells']) for r in m['supervised_rails']), len(m['temperature']['rows']),
        len(m['port_stress']), sum(len(r['cells']) for r in m['port_stress']),
        sum(len(r['return_paths']) for r in m['port_stress']), len(m['protection_states'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
