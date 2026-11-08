#!/usr/bin/env python3
"""从手册引脚表生成 KiCad 矩形符号（缺符号时用；校准板、PoE 2026-11-07 都是手写生成脚本）。

输入 JSON 或 CSV，逐物理脚写，脚号、名字照手册：
  JSON {"name": "ADM2561E", "reference": "U", "description": "...", "datasheet": "...",
        "pins": [{"number": "1", "name": "VCC", "type": "PWR", "side": "T"}, ...]}
  CSV  表头 number,name,type[,side]
type 写手册类型（I/O/IO/OD/OS/PWR/PWR_OUT/GND/A/NC，与引脚表 datasheet_type 同一套）或 KiCad 电气类型；
side 写 L/R/T/B，不写时 PWR/PWR_OUT 在上、GND 在下、O/OD/OS/PWR_OUT 以外的输出在右、其余在左，各边按表内顺序排。
同名同类型的电源/地脚（PWR/PWR_OUT/GND）合成一个 KiCad 叠脚 [a,b]（--no-stack 不合）；NC 和信号脚从不合。

生成的符号满足 ASG 的符号完整性与引脚文字检查：2.54 mm 栅格；叠脚上方留出竖排脚号的空行；左右引脚名之间、
上下引脚与左右引脚名之间按文字宽度留空（Matrix 2026-11-07 #20：上下边引脚名在角上压到左右引脚名）。

    python3 make_symbol.py pins.json --out 原理图/项目.kicad_sym [--library 项目]
输出文件已存在时按符号名替换或追加，其余符号不动。设计网表里用 <library>:<name> 引用。
"""
import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

from schematic_layout.geometry import text_extent
from schematic_layout.scene import physical_numbers
from schematic_layout.sexpr import Atom, all_nodes, dump, form, parse

G = 2.54
PIN_LENGTH = 2.54
FONT = 1.27
NAME_OFFSET = 1.016
KICAD_TYPE = {'I': 'input', 'O': 'output', 'IO': 'bidirectional', 'OD': 'open_collector', 'OS': 'open_emitter',
              'PWR': 'power_in', 'PWR_OUT': 'power_out', 'GND': 'power_in', 'A': 'passive', 'NC': 'no_connect'}
KICAD_TYPES = set(KICAD_TYPE.values()) | {'tri_state', 'unspecified', 'free', 'power_in', 'power_out', 'passive'}
STACKABLE = {'PWR', 'PWR_OUT', 'GND'}


def snap_up(value):
    return G * math.ceil(round(value / G, 6))


def load_pins(path):
    if path.suffix.lower() == '.csv':
        with path.open(encoding='utf-8-sig', newline='') as stream:
            return {'pins': list(csv.DictReader(stream))}
    return json.loads(path.read_text(encoding='utf-8'))


def default_side(code):
    if code in ('PWR', 'PWR_OUT'):
        return 'T'
    if code == 'GND':
        return 'B'
    return 'R' if code in ('O', 'OD', 'OS') else 'L'


def pin_rows(rows, stack=True):
    """[{numbers, name, code, kicad, side}] in table order, same-name supply pins stacked."""
    out, seen = [], set()
    for row in rows:
        numbers = row['number'] if isinstance(row['number'], list) else re.split(r'[,\s]+', str(row['number']).strip())
        numbers = [n for item in numbers for n in physical_numbers(str(item).strip()) if n]
        name, code = str(row.get('name', '')).strip(), str(row.get('type', '')).strip()
        if not numbers or not name or not code:
            raise ValueError('every pin needs number, name and type: %s' % row)
        kicad = KICAD_TYPE.get(code.upper(), code if code in KICAD_TYPES else None)
        if kicad is None:
            raise ValueError('%s: type %s is neither a datasheet code (%s) nor a KiCad type' % (
                name, code, '/'.join(KICAD_TYPE)))
        code = code.upper() if code.upper() in KICAD_TYPE else code
        side = str(row.get('side') or '').strip().upper() or default_side(code)
        if side not in ('L', 'R', 'T', 'B'):
            raise ValueError('%s: side must be L/R/T/B' % name)
        for n in numbers:
            if n in seen:
                raise ValueError('pin %s listed twice' % n)
            seen.add(n)
        merge = next((p for p in out if stack and code in STACKABLE and p['code'] == code and p['name'] == name
                      and p['side'] == side), None)
        if merge:
            merge['numbers'] += numbers
        elif stack and code in STACKABLE or len(numbers) == 1:
            out.append({'numbers': numbers, 'name': name, 'code': code, 'kicad': kicad, 'side': side})
        else:   # several numbers on one signal row without stacking: one pin each
            out += [{'numbers': [n], 'name': name, 'code': code, 'kicad': kicad, 'side': side} for n in numbers]
    return out


def number_text(numbers):
    return numbers[0] if len(numbers) == 1 else '[' + ','.join(numbers) + ']'


def name_width(pin):
    return 0.0 if pin['name'] == '~' else text_extent(pin['name'], FONT)[0]


def layout(pins):
    """Pin positions and the body half-sizes, all on the 2.54 mm grid."""
    sides = {s: [p for p in pins if p['side'] == s] for s in 'LRTB'}
    wl = max([name_width(p) for p in sides['L']] or [0]) + NAME_OFFSET
    wr = max([name_width(p) for p in sides['R']] or [0]) + NAME_OFFSET
    wt = max([name_width(p) for p in sides['T']] or [0]) + NAME_OFFSET
    wb = max([name_width(p) for p in sides['B']] or [0]) + NAME_OFFSET
    # Left/right rows: a stacked pin prints its numbers upwards, one row each, so it gets empty rows above it.
    def column(items):
        ys, y = [], 0
        for p in items:
            y += G * (len(p['numbers']) - 1)
            ys.append(y)
            y += G
        return ys, y
    left, hl = column(sides['L'])
    right, hr = column(sides['R'])
    # Top/bottom pins sit between the side name zones, 2 grids apart (a power symbol's text clears its neighbour);
    # their vertical names start at the edge, so the body is wide enough that they never reach a side pin's name.
    n_tb = max(len(sides['T']), len(sides['B']))
    tb_half = G * (n_tb - 1)
    hw = snap_up(max((wl + wr + G) / 2, max(wl, wr) + tb_half + G if n_tb else 0, 2 * G))
    # Height: the side rows, and the top and bottom names end to end (a top and a bottom pin share an x).
    side_height = max(hl, hr)
    hh = snap_up(max(side_height + G, wt + wb + G if sides['T'] and sides['B'] else max(wt, wb) + G, 2 * G) / 2)
    place = []
    first = hh - G
    for items, ys, x, angle in ((sides['L'], left, -hw - PIN_LENGTH, 0), (sides['R'], right, hw + PIN_LENGTH, 180)):
        for p, y in zip(items, ys):
            place.append((p, x, first - y, angle))
    for items, y, angle in ((sides['T'], hh + PIN_LENGTH, 270), (sides['B'], -hh - PIN_LENGTH, 90)):
        x0 = -G * (len(items) - 1)
        for i, p in enumerate(items):
            place.append((p, round(x0 + 2 * G * i, 4), y, angle))
    return hw, hh, place


def fmt(value):
    value = round(value, 4)
    return int(value) if value == int(value) else value


def effects(*extra):
    return form('effects', form('font', form('size', FONT, FONT)), *extra)


def prop(key, text, x, y, hide=False, justify=None):
    extra = ([form('justify', Atom(justify))] if justify else []) + ([form('hide', Atom('yes'))] if hide else [])
    return form('property', key, text, form('at', fmt(x), fmt(y), 0), effects(*extra))


def symbol(spec, stack=True):
    name = str(spec.get('name') or '').strip()
    if not re.fullmatch(r'[A-Za-z0-9_.+\-]+', name):
        raise ValueError('symbol name must be letters, digits, _ . + -: %r' % name)
    pins = pin_rows(spec.get('pins') or [], stack)
    if not pins:
        raise ValueError('no pins')
    hw, hh, place = layout(pins)
    top = hh + (PIN_LENGTH + G * max([len(p['numbers']) for p, *_ in place if p['side'] == 'T'] or [0]) + G
                if any(p['side'] == 'T' for p, *_ in place) else G)
    node = form('symbol', name, form('pin_names', form('offset', NAME_OFFSET)), form('exclude_from_sim', Atom('no')),
                form('in_bom', Atom('yes')), form('on_board', Atom('yes')),
                prop('Reference', spec.get('reference', 'U'), -hw, top, justify='left'),
                prop('Value', name, hw, top, justify='right'),
                prop('Footprint', spec.get('footprint', ''), 0, 0, hide=True),
                prop('Datasheet', spec.get('datasheet', ''), 0, 0, hide=True),
                prop('Description', spec.get('description', ''), 0, 0, hide=True),
                form('symbol', name + '_0_1', form('rectangle', form('start', fmt(-hw), fmt(hh)), form('end', fmt(hw), fmt(-hh)),
                                                   form('stroke', form('width', 0.254), form('type', Atom('default'))),
                                                   form('fill', form('type', Atom('background'))))),
                form('symbol', name + '_1_1', *[
                    form('pin', Atom(p['kicad']), Atom('line'), form('at', fmt(x), fmt(y), angle), form('length', PIN_LENGTH),
                         form('name', p['name'], effects()), form('number', number_text(p['numbers']), effects()))
                    for p, x, y, angle in place]))
    return node


def write_library(nodes, out):
    if out.exists():
        root = parse(out.read_text(encoding='utf-8'))
    else:
        root = form('kicad_symbol_lib', form('version', 20241209), form('generator', 'asg_make_symbol'))
    for node in nodes:
        old = next((i for i, n in enumerate(root) if isinstance(n, list) and n and n[0] == 'symbol' and n[1] == node[1]), None)
        if old is None:
            root.append(node)
        else:
            root[old] = node
    out.write_text(dump(root) + '\n', encoding='utf-8')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pins', type=Path, help='引脚表 JSON 或 CSV')
    ap.add_argument('--out', type=Path, required=True, help='.kicad_sym（已有时按符号名替换或追加）')
    ap.add_argument('--name', help='符号名（CSV 必填，JSON 可覆盖 name）')
    ap.add_argument('--reference', help='位号前缀，默认 U')
    ap.add_argument('--no-stack', action='store_true', help='同名电源/地脚不合成叠脚')
    args = ap.parse_args(argv)
    try:
        spec = load_pins(args.pins)
        for key in ('name', 'reference'):
            if getattr(args, key):
                spec[key] = getattr(args, key)
        node = symbol(spec, stack=not args.no_stack)
        write_library([node], args.out)
    except (OSError, ValueError, KeyError) as exc:
        print('FAIL:', exc, file=sys.stderr)
        return 1
    pins = [p for sub in all_nodes(node, 'symbol') for p in all_nodes(sub, 'pin')]
    print('%s: %d pins (%d pads) -> %s' % (node[1], len(pins),
                                          sum(len(physical_numbers(str(p[-1][1]))) for p in pins), args.out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
