#!/usr/bin/env python3
"""Fill datasheet_name / datasheet_type in record/reference-input.json from each part's datasheet pin table.

binding_version 1 (references/design-closure.md) wants every pin of every pin map to say what the datasheet pin
table prints: the name and the type. Pin maps written from the project symbols carry only the symbol's names and
KiCad types (industrial I/O calibration board, 2026-11-02: 478 of 505 binding errors). For each pin map this script

  1. takes the part's datasheet from the design netlist (`datasheet`),
  2. finds the pin table pages (Pin Functions / Pin Configuration / Pin description / pin definitions ...),
  3. reads the table rows from `pdftotext -layout` (name, pin-number columns, type column),
  4. picks the number column that agrees with the symbol numbering (several packages or variants per table),
  5. writes `datasheet_name` (as printed, footnote marks dropped), `datasheet_type` (the vendor code translated
     by TYPE_CODES) and `datasheet_page` for each pin it can read, and points the pin map's `source`/`locator`
     at the datasheet.

Nothing is guessed: a pin whose number is not in the table, whose type column is empty or a dash, or whose rows
disagree stays unfilled and is listed with the reason. `name_note` and `type_note` are never written: where the printed name and
the symbol name differ, the audit asks the designer why (pin_name_differs_from_datasheet). Existing values are
kept unless --overwrite.

    python3 fill_pin_maps.py <delivery> [--intent record/electrical-intent.json]
        [--contract record/reference-input.json] [--pages U301=28-34 ...] [--write] [--overwrite] [--out report.json]
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schematic_layout import part_classes as pc  # noqa: E402

# Vendor type codes (TI "TYPE"/"I/O", ST "Type", NXP "Type") → binding_version 1 vocabulary (audit DATASHEET_PIN_TYPES).
# A dash, an empty column or "--" is not a type: such pins stay unfilled unless the printed name is NC.
TYPE_CODES = {
    'I': 'I', 'IN': 'I', 'INPUT': 'I', 'DIGITALINPUT': 'I', 'ANALOGINPUT': 'I', 'DI': 'I', 'LOGICINPUT': 'I',
    'O': 'O', 'OUT': 'O', 'OUTPUT': 'O', 'DIGITALOUTPUT': 'O', 'ANALOGOUTPUT': 'O', 'DO': 'O', 'LOGICOUTPUT': 'O',
    'IO': 'IO', 'B': 'IO', 'BIDIRECTIONAL': 'IO', 'BUSIO': 'IO', 'DIGITALIO': 'IO', 'INPUTOUTPUT': 'IO',
    'OD': 'OD', 'OPENDRAIN': 'OD', 'ODO': 'OD', 'OPENDRAINOUTPUT': 'OD', 'OUTPUTOPENDRAIN': 'OD', 'OOD': 'OD',
    'P': 'PWR', 'POWER': 'PWR', 'PWR': 'PWR', 'S': 'PWR', 'SUPPLY': 'PWR', 'POWERSUPPLY': 'PWR',
    'G': 'GND', 'GND': 'GND', 'GROUND': 'GND',
    'A': 'A', 'ANALOG': 'A', 'AI': 'A', 'AO': 'A', 'AIO': 'A',
    'NC': 'NC',
}
DASHES = {'-', '—', '–', '--', '−'}
NC_NAMES = {'nc', 'dnc', 'nic'}
PAGE_HEADER = re.compile(r'pin\s*(?:functions?|configurations?|descriptions?|definitions?|assignments?|out)\b|'
                         r'pinout|terminal\s+functions|pin\s+no\.?\s', re.I)
_N = r'\d{1,3}(?:\(\d+\))?(?:\s*(?:to|–|-)\s*\d{1,3})?'
NUMBER = re.compile(r'^%s(?:\s*,\s*%s)*$' % (_N, _N))      # 3 | 2, 8 | 11,12 | 1 to 12, 22 to 35, 48
BALL = re.compile(r'^[A-HJ-NP-Z]\d{1,2}(?:\(\d+\))?$')     # BGA ball (A3, K10); PA1 is a pin name
PAD = re.compile(r'thermal\s*pad|exposed\s*(?:thermal\s*)?pad|power\s*pad|^tab$', re.I)
NAME = re.compile(r'^[A-Za-z~][A-Za-z0-9_+\-–−/#~.]*(?:\(\d+\))?$')
FOOTNOTE = re.compile(r'\(\d+\)$')
TYPE_HEADER = re.compile(r'^(?:TYPE|Type|I/O)\s*(?:\(\d\))?$')
CELL = re.compile(r'\S+(?: \S+)*')                        # cells of a -layout line are separated by two or more spaces
DOCUMENT_ID = re.compile(r'\b(SL[A-Z]{2}[0-9A-Z]{2,4}|SN[A-Z]{2}[0-9A-Z]{2,4}|SBV[A-Z][0-9A-Z]{2,4}|SBAS[0-9A-Z]{2,4}|'
                         r'DS\d{4,6})\b')


def norm(name):
    """A pin name compared across symbol and datasheet (the audit's pin_name): overbar and punctuation dropped."""
    return re.sub(r'[^0-9a-z]', '', re.sub(r'~\{([^}]*)\}', r'\1', str(name)).lower())


def type_code(cell):
    """The binding vocabulary for a type cell (its first word decides: ST writes "I/O FT"), or None."""
    words = cell.split()
    for candidate in (cell, words[0] if words else ''):
        key = re.sub(r'[^A-Z]', '', candidate.upper())
        if key in TYPE_CODES and len(candidate) <= 24 and not re.search(r'\d', candidate):
            return TYPE_CODES[key], candidate
    return None


def numbers(cell):
    """2, 8 → [2, 8]; 1 to 12, 48 → [1..12, 48]; footnote marks (8) dropped."""
    out = []
    for part in re.sub(r'\(\d+\)', '', cell).split(','):
        m = re.match(r'\s*(\d+)\s*(?:(?:to|–|-)\s*(\d+))?\s*$', part)
        if m:
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            out += list(range(a, b + 1)) if b >= a else [a]
    return out


def positions_of(cell):
    """The pin-number tokens a cell holds: [[ints]], [None] for a dash or ball, ['pad'] for an exposed pad; else None."""
    cell = cell.strip()
    if NUMBER.match(cell):
        return [numbers(cell)]
    if cell in DASHES:
        return [None]
    if PAD.search(cell) and len(cell) <= 24:
        return ['pad']
    if all(BALL.match(t.strip()) for t in cell.split(',')) and ',' in cell:
        return [None]                                    # a list of BGA balls (B1, B2) in a ball column
    tokens = cell.split()
    if tokens and all(NUMBER.match(t) or BALL.match(t) or t in DASHES for t in tokens):
        return [numbers(t) if NUMBER.match(t) else None for t in tokens]
    return None


def type_span(text):
    """Where the type column of this page's pin table sits: the (start, end) of its TYPE / Type / I/O heading."""
    for line in text.splitlines():
        for m in CELL.finditer(line):
            if TYPE_HEADER.match(m.group()):
                return m.start(), m.end()
    return None


def parse_rows(text, page, span=None, sequential=False):
    """Pin-table rows of one page of `pdftotext -layout` text: {name, positions, type, raw_type, page}.

    The type is read only from the cell under the page's TYPE / I/O heading (`span`), so a pin-out drawing on the
    same page ("A  2 ... 17  NC") gives a name but no type. `sequential` reads the cell after the numbers instead,
    for a datasheet whose table has no heading the text keeps."""
    rows = []
    for line in text.splitlines():
        found_cells = list(CELL.finditer(line))
        cells = [m.group() for m in found_cells]
        if len(cells) < 2:
            continue
        lead, i = [], 0
        while i < len(cells) and positions_of(cells[i]) is not None:
            lead += positions_of(cells[i])
            i += 1
        if i >= len(cells) or not NAME.match(cells[i]) or len(cells[i]) > 24:
            continue
        if lead and type_code(cells[i]) and cells[i].upper() in ('I/O', 'I', 'O', 'S', 'P', 'G', 'IO'):
            continue      # the name column is empty on this line (STM32 PC13 wraps); the cell is the type
        name = FOOTNOTE.sub('', cells[i])
        i += 1
        trail = []
        if not lead:
            while i < len(cells) and positions_of(cells[i]) is not None:
                # A dash right before the description is the type column, not a number column, when numbers came first.
                if cells[i] in DASHES and trail and (
                        i + 1 >= len(cells) or positions_of(cells[i + 1]) is None):
                    break
                trail += positions_of(cells[i])
                i += 1
        positions = lead or trail
        numeric = [p for p in trail if isinstance(p, list)]
        if (not lead and len(trail) == 2 and len(numeric) == 2 and i < len(cells) and NAME.match(cells[i])
                and not type_code(cells[i])):
            # A pin-out drawing line: LEFT  n ... m  RIGHT, two pins, not one row of a table.
            rows.append({'name': name, 'positions': [numeric[0]], 'type': None, 'raw_type': None, 'page': page})
            rows.append({'name': FOOTNOTE.sub('', cells[i]), 'positions': [numeric[1]], 'type': None,
                         'raw_type': None, 'page': page})
            continue
        if not any(isinstance(p, list) or p == 'pad' for p in positions):
            if not (name.lower() in ('ep', 'pad', 'epad') and positions):
                continue
        cell = None
        if span:
            for m in found_cells[i:]:
                if m.start() <= span[1] + 3 and m.end() >= span[0] - 3:
                    cell = m.group()
                    break
                if m.start() > span[1] + 3:
                    break
        elif sequential and i < len(cells):
            cell = cells[i]
        found = type_code(cell) if cell else None
        rows.append({'name': name, 'positions': positions, 'type': found[0] if found else None,
                     'raw_type': cell if (found or (cell or '').strip() in DASHES) else None, 'page': page})
    return rows


def names_agree(row_name, symbol_names):
    """The printed name is the symbol's: equal, one '/'-segment of it (PA5/SPI1_SCK), or a numbered instance (VDD_1)."""
    printed = norm(row_name)
    base = norm(re.sub(r'_\d+$', '', row_name))
    for n in symbol_names:
        if printed == norm(n) or base == norm(n) or printed in {norm(s) for s in re.split(r'[/]', str(n))}:
            return True
    return False


def at(row, column):
    """The pin numbers a row gives in a column; a row with one number column gives it for every column."""
    numeric = [p for p in row['positions'] if p != 'pad']
    if len(row['positions']) == 1:
        return row['positions'][0] if isinstance(row['positions'][0], list) else []
    if column < len(row['positions']) and isinstance(row['positions'][column], list):
        return row['positions'][column]
    return [] if numeric else []


def choose_column(rows, pins):
    """The number column whose numbers carry the symbol's names for most rows (variants and packages per table)."""
    rows = [r for r in rows if r['type']] or rows        # table rows decide; pin-out drawings only fill names
    width = max((len(r['positions']) for r in rows), default=1)
    best, best_key = 0, (-1, -1)
    for column in range(width):
        hits = [(r, n) for r in rows for n in at(r, column) if str(n) in pins]
        key = (sum(1 for r, n in hits if names_agree(r['name'], pins[str(n)].get('names') or [])), len(hits))
        if key > best_key:      # names agreeing first; with no name agreeing, the column that numbers the most pins
            best, best_key = column, key
    return best, best_key[0]


def fill_map(spec, rows):
    """{pin: {datasheet_name, datasheet_type, datasheet_page}} and [{pin, reason, ...}] for one pin map."""
    pins = spec.get('pins') or {}
    column, score = choose_column(rows, pins)
    by_number = {}
    for r in rows:
        for n in at(r, column):
            by_number.setdefault(str(n), []).append(r)
    numbers = [int(n) for n in by_number if n.isdigit()]
    # The exposed pad's table row (it has a type cell, even a dash); "Thermal Pad" printed inside a pin-out drawing is not.
    pads = [r for r in rows if ('pad' in r['positions'] or r['name'].lower() in ('ep', 'pad', 'epad'))
            and r.get('raw_type') is not None]
    filled, missing = {}, []
    for number, pin in pins.items():
        candidates = by_number.get(number, [])
        if not candidates and pads and numbers and number.isdigit() and int(number) == max(numbers) + 1:
            candidates = pads[:1]   # the exposed pad is numbered after the last package pin
        if not candidates:
            missing.append({'pin': number, 'symbol_names': pin.get('names'), 'reason': 'not_in_table'})
            continue
        typed = [r for r in candidates if r['type']]
        names = {norm(r['name']) for r in (typed or candidates)}
        if len(names) > 1:
            missing.append({'pin': number, 'reason': 'rows_disagree',
                            'rows': sorted({r['name'] for r in candidates})})
            continue
        row = (typed or candidates)[0]
        entry = {'datasheet_name': row['name'], 'datasheet_page': row['page']}
        kinds = {r['type'] for r in typed}
        if len(kinds) == 1:
            entry['datasheet_type'] = kinds.pop()
        elif not typed and norm(row['name']) in NC_NAMES:
            entry['datasheet_type'] = 'NC'
        else:
            missing.append({'pin': number, 'reason': 'type_not_given' if not typed else 'types_disagree',
                            'datasheet_name': row['name'], 'raw_type': row.get('raw_type'), 'page': row['page']})
        filled[number] = entry
    return filled, missing, {'column': column, 'agreeing_rows': score}


def pdf_pages(pdf):
    tool = shutil.which('pdfinfo')
    info = subprocess.run([tool, str(pdf)], capture_output=True, text=True, timeout=60).stdout if tool else ''
    m = re.search(r'^Pages:\s+(\d+)', info, re.M)
    return int(m.group(1)) if m else 0


def layout_text(pdf, page):
    tool = shutil.which('pdftotext')
    if not tool:
        return ''
    return subprocess.run([tool, '-layout', '-q', '-f', str(page), '-l', str(page), str(pdf), '-'],
                          capture_output=True, text=True, timeout=60).stdout


def table_rows(pdf, pages=None):
    """Rows from the pin-table pages: the given page range, else every page whose text names a pin table. A page
    without a TYPE heading uses the last heading seen (continued tables); with no heading anywhere the cell after
    the numbers is read as the type."""
    texts = {}
    if pages:
        wanted = list(range(pages[0], pages[1] + 1))
    else:
        wanted = []
        for p in range(1, pdf_pages(pdf) + 1):
            texts[p] = layout_text(pdf, p)
            if PAGE_HEADER.search(texts[p]):
                wanted.append(p)
    spans = {p: type_span(texts.get(p) if p in texts else texts.setdefault(p, layout_text(pdf, p))) for p in wanted}
    sequential = not any(spans.values())
    rows = []
    for p in wanted:
        rows += parse_rows(texts[p], p, spans[p], sequential)
    return rows, wanted


def fill(root, intent_path, contract_path, pages=None, overwrite=False):
    root = Path(root)
    intent = json.loads((root / intent_path).read_text(encoding='utf-8'))
    contract = json.loads((root / contract_path).read_text(encoding='utf-8'))
    comps = {c.get('ref'): c for c in intent.get('components') or [] if isinstance(c, dict)}
    bases = [root, root / 'record']
    report = {'maps': {}, 'filled': 0, 'unfilled': 0, 'reasons': {}}
    for ref, spec in sorted((contract.get('pin_maps') or {}).items()):
        comp = comps.get(ref) or {}
        pdf = pc.find(comp.get('datasheet'), bases) if comp.get('datasheet') else None
        item = {'datasheet': comp.get('datasheet'), 'pins': len(spec.get('pins') or {})}
        report['maps'][ref] = item
        if pdf is None or pdf.suffix.lower() != '.pdf':
            item['missing'] = [{'pin': n, 'reason': 'no_datasheet'} for n in spec.get('pins') or {}]
        else:
            rows, read = table_rows(pdf, (pages or {}).get(ref))
            filled, missing, choice = fill_map(spec, rows)
            item.update(pages_read=read, rows=len(rows), **choice, missing=missing)
            changed = 0
            for number, entry in filled.items():
                pin = spec['pins'][number]
                for key, value in entry.items():
                    if overwrite or key not in pin:
                        pin[key] = value
                        changed += 1
            if filled:
                sid = 'DS-' + ref
                body = layout_text(pdf, 1)
                doc = DOCUMENT_ID.search(body or '')
                contract.setdefault('sources', {})[sid] = dict(
                    {'path': str(pdf), 'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(), 'url': 'file:' + str(pdf),
                     'document': pdf.name}, **({'revision': doc.group(1)} if doc else {}))
                used = sorted({e['datasheet_page'] for e in filled.values()})
                spec['source'], spec['locator'] = sid, '%s 引脚表 p%s' % (pdf.name, '、'.join(map(str, used)))
            item['written'] = changed
        complete = [n for n, p in (spec.get('pins') or {}).items() if p.get('datasheet_name') and p.get('datasheet_type')]
        item['complete'] = len(complete)
        report['filled'] += len(complete)
        for m in item.get('missing') or []:
            report['unfilled'] += 1
            report['reasons'][m['reason']] = report['reasons'].get(m['reason'], 0) + 1
    return contract, report


def parse_pages(values):
    out = {}
    for v in values or []:
        ref, _, span = v.partition('=')
        a, _, b = span.partition('-')
        out[ref] = (int(a), int(b or a))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('delivery', type=Path)
    ap.add_argument('--intent', default='record/electrical-intent.json')
    ap.add_argument('--contract', default='record/reference-input.json')
    ap.add_argument('--pages', nargs='*', help='REF=first-last: read only these pages for that part')
    ap.add_argument('--write', action='store_true', help='write the filled pin maps back into the contract')
    ap.add_argument('--overwrite', action='store_true', help='replace datasheet_name/type already written')
    ap.add_argument('--out', type=Path, help='full report (JSON); the summary goes to stdout')
    args = ap.parse_args(argv)
    contract, report = fill(args.delivery, args.intent, args.contract, parse_pages(args.pages), args.overwrite)
    if args.write:
        (args.delivery / args.contract).write_text(json.dumps(contract, ensure_ascii=False, indent=1), encoding='utf-8')
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    for ref, item in report['maps'].items():
        print('%-6s %3d/%-3d %s' % (ref, item.get('complete', 0), item['pins'],
                                    '; '.join('%s:%s' % (m['pin'], m['reason']) for m in item.get('missing') or [])[:200]))
    print('complete pins %d, unfilled %d %s' % (report['filled'], report['unfilled'], json.dumps(report['reasons'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
