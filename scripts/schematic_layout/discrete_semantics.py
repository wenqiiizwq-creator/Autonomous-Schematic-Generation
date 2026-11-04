"""Discrete-part symbol semantics against the exact part.

A two-terminal or three-terminal discrete symbol carries a meaning the netlist
cannot check: a bidirectional TVS drawn for a unidirectional part, an N-channel
MOSFET symbol for a P-channel part, NPN for PNP. Connectivity can match the
intent while the drawing tells the reader the wrong device.

For each intent component this compares what its placed symbol says (cached
library description and pin names) with what the part's own datasheet text or
standard MPN suffix says, or what the datasheet's own suffix legend (for example
"CA Bi-Directional" in a family ordering table) says about the part's suffix, or what the intent declares in fields.SymbolPolarity
with the page it was read from in fields.PolarityEvidence. A contradiction is FAIL.
Ambiguous evidence, and a symbol whose description states a polarity while no
evidence for the part could be read, are listed as unresolved (INSUFFICIENT)
with the reason. A polarity inferred only from K/A pin names is not applicable
without evidence. This is a semantic cross-check, not a pin map: the reference
contract still owns physical pin numbers.
"""
from pathlib import Path
import re
import shutil
import subprocess

from .sexpr import all_nodes, first, parse

PAGES = 3  # polarity is stated on the first pages: title, features, pinning
# Datasheets print N−Channel with U+2212 and other dash look-alikes; match them as '-'.
DASHES = re.compile('[\u00ad\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe58\ufe63\uff0d]')
# A family datasheet's suffix legend: "CA Bi-Directional (5% ...)", "C = bidirectional", "A: Uni-directional".
SUFFIX_LEGEND = re.compile(r'^[ \t]*(?:suffix[ \t]+)?["\'\u201c]?((?-i:[A-Z]{1,3}))["\'\u201d]?(?:[ \t]*[:=][ \t]*|[ \t]+-[ \t]+|[ \t]+)(bi|uni)-?directional\b',
                           re.I | re.M)

# Standard TVS families: "A" (or no letter) is unidirectional, "CA"/"C" bidirectional.
TVS_MPN = re.compile(r'^(?:SMAJ|SMBJ|SMCJ|SMDJ|SMF|SMLJ|P4KE|P4SMA|P6KE|P6SMB|1\.5KE|1\.5SMC|SM6T|SM15T|5KP|15KP|3\.0SMC)'
                     r'[0-9.]+(CA|C|A)?(?:[-/].*)?$', re.I)

FAMILIES = {
    'tvs_direction': {
        'symbol': [('bidirectional', re.compile(r'\bbidirectional\b', re.I)),
                   ('unidirectional', re.compile(r'\bunidirectional\b', re.I))],
        'datasheet': [('bidirectional', re.compile(r'\bbi-?directional\b', re.I)),
                      ('unidirectional', re.compile(r'\buni-?directional\b', re.I))],
    },
    'mos_channel': {
        'symbol': [('N-channel', re.compile(r'\bN-?(?:channel|MOSFET|MOS)\b|\bNMOS\b', re.I)),
                   ('P-channel', re.compile(r'\bP-?(?:channel|MOSFET|MOS)\b|\bPMOS\b', re.I))],
        'datasheet': [('N-channel', re.compile(r'\bN-?channel\b', re.I)),
                      ('P-channel', re.compile(r'\bP-?channel\b', re.I))],
    },
    'bjt_type': {
        'symbol': [('NPN', re.compile(r'\bNPN\b')), ('PNP', re.compile(r'\bPNP\b'))],
        'datasheet': [('NPN', re.compile(r'\bNPN\b')), ('PNP', re.compile(r'\bPNP\b'))],
    },
}
DOMINANCE = 3  # a datasheet that names the complement in passing still decides


def cached_symbols(sheets):
    """lib_id -> (description, pin names) from the schematics' own library caches."""
    found = {}
    for sheet in sheets:
        tree = parse(Path(sheet).read_text(encoding='utf-8'))
        for sym in all_nodes(first(tree, 'lib_symbols', []), 'symbol'):
            desc = ''
            for prop in all_nodes(sym, 'property'):
                if len(prop) > 2 and str(prop[1]) in ('Description', 'ki_description'):
                    desc = str(prop[2])
            pins = set()
            def walk(node):
                for child in node:
                    if isinstance(child, list) and child:
                        if child[0] == 'pin':
                            name = first(child, 'name')
                            if name and len(name) > 1:
                                pins.add(str(name[1]))
                        elif child[0] == 'symbol':
                            walk(child)
            walk(sym)
            found[str(sym[1])] = (desc, pins)
    return found


def normalize(text):
    return DASHES.sub('-', text or '')


def symbol_meaning(family, desc, pins):
    """(meaning, stated): stated is False when only the pin names imply it."""
    desc = normalize(desc)
    hits = {label for label, pattern in FAMILIES[family]['symbol'] if pattern.search(desc)}
    stated = bool(hits)
    if family == 'tvs_direction' and not hits:
        if pins == {'A1', 'A2'}:
            hits = {'bidirectional'}
        elif {'K', 'A'} <= pins and len(pins) == 2:
            hits = {'unidirectional'}
    return (hits.pop(), stated) if len(hits) == 1 else (None, False)


def datasheet_text(path):
    """Whole datasheet text, pages separated by form feeds (pdftotext's page break)."""
    tool = shutil.which('pdftotext')
    if not tool or not path.is_file():
        return None
    r = subprocess.run([tool, '-q', str(path), '-'], capture_output=True, text=True, timeout=60)
    return r.stdout if r.returncode == 0 else None


def first_pages(text):
    return '\f'.join(text.split('\f')[:PAGES])


def mpn_suffix(mpn):
    """Letters after the last digit of the base part number: 30KPA28CA-B -> CA."""
    base = re.split(r'[-/,\s]', (mpn or '').strip())[0]
    m = re.search(r'\d([A-Z]*)$', base, re.I)
    return m.group(1).upper() if m else None


def legend_meaning(text, mpn):
    """TVS direction from the datasheet's suffix legend applied to the MPN suffix.

    Returns (meaning, page, sentence) or None when the suffix is absent from the
    legend or the legend contradicts itself for that suffix.
    """
    suffix = mpn_suffix(mpn)
    if not suffix:
        return None
    hits = []
    for page, body in enumerate(normalize(text).split('\f'), 1):
        for m in SUFFIX_LEGEND.finditer(body):
            if m.group(1).upper() == suffix:
                line = body[m.start():].lstrip().split('\n', 1)[0].strip()
                hits.append(('bidirectional' if m.group(2).lower() == 'bi' else 'unidirectional', page, line))
    if not hits or len({h[0] for h in hits}) > 1:
        return None
    return hits[0]


def datasheet_meaning(family, text):
    text = normalize(text)
    counts = {label: len(pattern.findall(text)) for label, pattern in FAMILIES[family]['datasheet']}
    present = {k: v for k, v in counts.items() if v}
    if not present:
        return None, counts
    if len(present) == 1:
        return next(iter(present)), counts
    (a, na), (b, nb) = sorted(present.items(), key=lambda kv: -kv[1])
    return (a if na >= DOMINANCE * nb else 'ambiguous'), counts


def mpn_meaning(mpn):
    m = TVS_MPN.match(mpn.strip()) if mpn else None
    if not m:
        return None
    return 'bidirectional' if (m.group(1) or '').upper() in ('CA', 'C') else 'unidirectional'


def resolve(path, bases):
    if not path:
        return None
    p = Path(path)
    if p.is_absolute():
        return p
    for base in bases:
        if (Path(base) / p).is_file():
            return Path(base) / p
    return None


def audit_discrete_semantics(sheets, intent, bases=()):
    cache = cached_symbols(sheets)
    errors, unresolved, checked = [], [], []
    for comp in intent.get('components', []):
        ref, lib_id = comp.get('ref'), str(comp.get('lib_id', ''))
        desc, pins = cache.get(lib_id, ('', set()))
        mpn = str(comp.get('mpn') or comp.get('value') or '')
        text = None
        path = resolve(comp.get('datasheet'), bases)
        fields = comp.get('fields') or {}
        for family in FAMILIES:
            drawn, stated = symbol_meaning(family, desc, pins)
            if drawn is None:
                continue
            labels = {label for label, _ in FAMILIES[family]['datasheet']}
            part, source, missing, located = None, None, None, {}
            if fields.get('SymbolPolarity') in labels and str(fields.get('PolarityEvidence', '')).strip():
                part, source = fields['SymbolPolarity'], 'declared: ' + str(fields['PolarityEvidence'])
            if part is None and family == 'tvs_direction':
                part = mpn_meaning(mpn)
                source = 'MPN suffix' if part else None
            if part is None:
                if path is None:
                    missing = 'datasheet path does not resolve'
                elif not shutil.which('pdftotext'):
                    missing = 'pdftotext not installed'
                else:
                    if text is None:
                        text = datasheet_text(path) or ''
                    legend = legend_meaning(text, mpn) if text and family == 'tvs_direction' else None
                    if legend:
                        part, page, sentence = legend
                        source = 'datasheet p%d suffix legend "%s" applied to MPN suffix %s' % (page, sentence, mpn_suffix(mpn))
                        located = {'evidence_page': page, 'evidence_text': sentence}
                    elif text:
                        part, counts = datasheet_meaning(family, first_pages(text))
                        source = 'datasheet first %d pages %s' % (PAGES, counts)
                    missing = None if part else 'datasheet first %d pages name no %s' % (PAGES, '/'.join(sorted(labels)))
            if part is None:
                if stated:
                    unresolved.append({'ref': ref, 'family': family, 'lib_id': lib_id, 'symbol': drawn, 'part': None,
                                       'mpn': mpn, 'evidence': None, 'reason': missing})
                continue  # a pin-name-only meaning without evidence is not applicable
            row = {'ref': ref, 'family': family, 'lib_id': lib_id, 'symbol': drawn, 'part': part,
                   'mpn': mpn, 'evidence': source, **located}
            if part == 'ambiguous':
                unresolved.append(row)
            elif part != drawn:
                errors.append({**row, 'code': 'symbol_semantics_mismatch',
                               'detail': f'{ref} {mpn}: symbol {lib_id} is {drawn}, part is {part}'})
            else:
                checked.append(row)
    status = 'FAIL' if errors else 'INSUFFICIENT' if unresolved else 'PASS' if checked else 'NOT_APPLICABLE'
    return {'status': status,
            'scope': 'Symbol meaning (TVS direction, MOSFET channel, BJT type) against datasheet text, the datasheet '
                     'suffix legend or MPN suffix; '
                     'not physical pin numbers, ratings or footprints.',
            'errors': errors, 'unresolved': unresolved, 'checked': checked}
