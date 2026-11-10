#!/usr/bin/env python3
"""把一份 KiCad XML 网表转成设计网表，供单独运行 C6 时用（SKILL.md 任务 C6.1，references/modules.md）。

  python3 import_netlist.py <netlist.xml> --out record/electrical-intent.json \\
      [--source-schematic 根图.kicad_sch --library-dir 设计资料/symbols]

- 器件：位号、lib_id、Value、封装、手册和其余字段原样带过来；电源符号（# 开头的位号）不进网表。
- 网络：每个网络列出 `位号.引脚`；KiCad 给单脚未接网络起的 `unconnected-…` 名字归入 no_connect。
- 符号：给了源原理图时，把根图和各子页里内嵌的 lib_symbols 抽成项目符号库（每个库一个 .kicad_sym），
  库名里 KiCad 允许而布图库不收的字符换成 `_`，lib_id 一并改写；工程内改过的符号（没有库名）放进 `local` 库。
  画图时用 `--symbol-dir` 指向这个目录。
- 电源轨角色（net_roles）、网络电压等不在网表里的信息不猜，导入后由任务 C6.1 按需要补写。
"""
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from schematic_layout.sexpr import Atom, all_nodes, dump, first, parse, value

NICK = re.compile(r'[^\w-]')
UNCONNECTED = re.compile(r'^unconnected-', re.I)
LOCAL = 'local'


def nickname(library):
    return NICK.sub('_', library)


def components(root):
    out = []
    for comp in root.iter('comp'):
        ref = comp.get('ref')
        if not ref or ref.startswith('#'):
            continue
        source = comp.find('libsource')
        lib, part = (source.get('lib'), source.get('part')) if source is not None else ('', '')
        fields = {f.get('name'): (f.text or '') for f in comp.iter('field') if f.get('name')}
        # A symbol edited inside the project has no library (KiCad lib_name); it goes to the `local` library.
        item = {'ref': ref, 'lib_id': '%s:%s' % (nickname(lib) if lib else LOCAL, part),
                'value': comp.findtext('value') or '', 'footprint': comp.findtext('footprint') or ''}
        sheet = comp.find('sheetpath')
        extra = {k: v for k, v in fields.items() if v and k not in ('Footprint', 'Datasheet', 'Value', 'Reference')}
        if sheet is not None and sheet.get('names') not in (None, '/'):
            extra['Sheet'] = sheet.get('names')
        if extra:
            item['fields'] = extra
        datasheet = comp.findtext('datasheet') or fields.get('Datasheet') or ''
        if datasheet and datasheet != '~':
            item['datasheet'] = datasheet
        mpn = next((fields[k] for k in ('MPN', 'Manufacturer_Part_Number', 'MFR_PN', 'PartNumber', 'Part Number') if fields.get(k)), '')
        if mpn:
            item['mpn'] = mpn
        if comp.find("property[@name='dnp']") is not None:
            item['dnp'] = True
        out.append(item)
    return out


def nets(root, refs):
    dotted = sorted({'%s.%s' % (n.get('ref'), n.get('pin')) for n in root.iter('node')
                     if n.get('ref') in refs and '.' in (n.get('pin') or '')})
    if dotted:
        # `位号.引脚` is split at the last dot, so a pin number with a dot cannot be written (SparkFun GNSSDO 39.1).
        raise ValueError('引脚号带“.”，设计网表的“位号.引脚”写法表达不了：%s%s' % (
            '、'.join(dotted[:5]), ' 等 %d 个' % len(dotted) if len(dotted) > 5 else ''))
    named, no_connect = {}, []
    for net in root.iter('net'):
        pins = ['%s.%s' % (n.get('ref'), n.get('pin')) for n in net.iter('node') if n.get('ref') in refs]
        if not pins:
            continue
        name = net.get('name') or 'NET%s' % net.get('code')
        if UNCONNECTED.match(name) and len(pins) == 1:
            no_connect += pins
        else:
            named[name.lstrip('/') if name.startswith('/') and name.count('/') == 1 else name] = pins
    return named, sorted(no_connect)


def sheet_files(root_file):
    """The root sheet and every sub-sheet file it references, recursively."""
    seen, todo = [], [Path(root_file)]
    while todo:
        path = todo.pop()
        if path in seen or not path.is_file():
            continue
        seen.append(path)
        tree = parse(path.read_text(encoding='utf-8'))
        for sheet in all_nodes(tree, 'sheet'):
            for prop in all_nodes(sheet, 'property'):
                if len(prop) > 2 and prop[1] in ('Sheetfile', 'Sheet file'):
                    todo.append(path.parent / prop[2])
    return seen


def extract_libraries(root_file, out_dir):
    """{nickname: path} of project libraries holding the symbols embedded in the source sheets."""
    libraries = {}
    for path in sheet_files(root_file):
        tree = parse(path.read_text(encoding='utf-8'))
        for symbol in all_nodes(first(tree, 'lib_symbols') or [], 'symbol'):
            lib, _, name = str(symbol[1]).rpartition(':')
            lib = lib or LOCAL
            copy = [symbol[0], name] + symbol[2:]
            libraries.setdefault(nickname(lib), {})[name] = copy
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for nick, symbols in sorted(libraries.items()):
        target = out_dir / (nick + '.kicad_sym')
        body = [Atom('kicad_symbol_lib'), [Atom('version'), Atom('20231120')], [Atom('generator'), 'asg_import_netlist']]
        body += [symbols[n] for n in sorted(symbols)]
        target.write_text(dump(body) + '\n', encoding='utf-8')
        written[nick] = str(target)
    return written


def convert(netlist, source_schematic=None, library_dir=None):
    raw = Path(netlist).read_bytes()
    root = ET.fromstring(raw)
    comps = components(root)
    named, no_connect = nets(root, {c['ref'] for c in comps})
    intent = {'schema': 'project-hardware-intent-v1', 'revision': 'imported', 'components': comps, 'nets': named,
              'no_connect': no_connect, 'net_roles': {},
              'source_netlist': {'path': str(netlist), 'sha256': hashlib.sha256(raw).hexdigest()}}
    libraries = extract_libraries(Path(source_schematic), Path(library_dir)) if source_schematic else {}
    if libraries:
        intent['source_netlist']['symbol_libraries'] = libraries
    return intent


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('netlist', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--source-schematic', type=Path, help='源工程的根 .kicad_sch，用来抽出内嵌符号')
    ap.add_argument('--library-dir', type=Path, help='抽出的项目符号库写到这里（与 --source-schematic 一起给）')
    args = ap.parse_args(argv)
    if bool(args.source_schematic) != bool(args.library_dir):
        ap.error('--source-schematic 与 --library-dir 要一起给')
    try:
        intent = convert(args.netlist, args.source_schematic, args.library_dir)
    except ValueError as exc:
        print('FAIL:', exc)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(intent, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('器件 %d 个，网络 %d 个，未接脚 %d 个，符号库 %d 个' % (
        len(intent['components']), len(intent['nets']), len(intent['no_connect']),
        len(intent['source_netlist'].get('symbol_libraries') or {})))
    return 0


if __name__ == '__main__':
    sys.exit(main())
