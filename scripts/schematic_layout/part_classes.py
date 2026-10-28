"""Which parts the design netlist must name exactly (references/part-roles.md section 1), aligned with schematic-review.

A part's class follows from its device kind and where it sits, never from a designer's choice. The kind is
declared from the part's own datasheet (``fields.Kind`` with ``KindSource`` and ``KindQuote``) or, for common
parts, read off the symbol and part number and only then the reference prefix (the weakest evidence, as in
schematic-review's ``part_words.classify``). Key parts (ICs, transistors, optocouplers, transformers, zeners,
TVS, bridge rectifiers, custom magnetics) and special parts (safety parts, connectors and relays on nets above
30 V, an NTC in the power path, any part a calculation cites a datasheet for) need an MPN and a datasheet;
common parts are fixed by value and specification, with every capacitor's voltage and every inductor's
current stated. A datasheet cited for a part in a calculation or a data gap must be the datasheet the design
netlist gives that part.
"""

import hashlib
import os
import re
from collections import OrderedDict, namedtuple
from pathlib import Path

from .citations import check, library_present, locate, page_text, parse
from .discrete_semantics import resolve

KEY, SPECIAL, COMMON = 'key', 'special', 'common'
CLASS_NAMES = {KEY: '关键器件', SPECIAL: '特殊器件', COMMON: '常规件'}

Kind = namedtuple('Kind', 'title prefixes words cues')

# The kind vocabulary of schematic-review's scripts/device_kinds.py (plus ASG's `mechanical`). Words are matched
# on "<lib_id> <value> <mpn>" in this order, the first kind wins; prefixes are the weakest evidence. Cues are what a
# datasheet quote must say, lowercase with spaces removed; they include schematic-review's cues for the kind.
# A part-number family (B) never starts inside a longer part number: PS2[5-9]xx is not the PS2663 in TPS26630.
B = r'(?<![A-Z0-9])'
KINDS = OrderedDict([
    ('relay', Kind('继电器', ('K',), (r'RELAY|继电器',), ('relay',))),
    ('varistor', Kind('压敏电阻', (), (r'VARISTOR|\bMOV\b|压敏',), ('varistor', 'siov', 'mov'))),
    ('ntc', Kind('热敏电阻', ('TH', 'RT', 'NTC'), (r'NTC|THERMISTOR',),
                 ('ntcthermistor', 'thermistor', 'inrushcurrentlimiter'))),
    ('opto', Kind('光耦', (), (r'OPTO|' + B + r'(?:PC81[07]|LTV-?\d|TLP\d|6N13[57]|HCPL|ACPL|FOD\d|CNY17|VO6\d|SFH6\d{2,3}|EL8\d\d|'
                             r'PS2[5-9]\d\d|TCMT\d|KPC\d|H11[A-Z]\d)|光耦',),
                  ('optocoupler', 'photocoupler', 'optoisolator', 'opticallycoupled', 'opticalisolator', 'opticalcoupler'))),
    ('tvs', Kind('TVS', ('TVS',), (r'TVS|POWER_PROTECTION:|' + B + r'(?:SMAJ|SMBJ|SMCJ|SMF\d|P6KE|1\.5KE|ESD\d|PESD|SM712)',),
                 ('tvs', 'esdprotection', 'transientvoltagesuppress', 'transientsuppress'))),
    ('zener', Kind('稳压管', ('ZD',), (r'ZENER|' + B + r'(?:BZX|BZT5\d|MMSZ|1N47\d)|稳压二极管',), ('zener',))),
    ('bjt', Kind('双极晶体管', (), (r'TRANSISTOR_BJT:|Q_NPN|Q_PNP|\bNPN\b|\bPNP\b|' + B + r'(?:BC[PXW]?\d{2,3}|2N\d{4}|MMBT|PBSS|S8050|S8550)|三极管',),
                 ('npn', 'pnp', 'bipolar'))),
    ('mosfet', Kind('MOSFET', ('Q',), (r'TRANSISTOR_FET:|TRANSISTOR_IGBT:|Q_NMOS|Q_PMOS|MOSFET|\bFET\b|NMOS|PMOS|IGBT|'
                                       + B + r'(?:IRF|IRLML|AO\d{4}|SI\d{4}|BSS\d|2N7002)',),
                   ('mosfet', 'nchannel', 'pchannel', 'superjunction', 'igbt'))),
    ('bridge_rectifier', Kind('整流桥', ('BR',), (r'BRIDGE|' + B + r'(?:GBU\d|KBP\d|DB10\d)',), ('bridgerectifier', 'bridge'))),
    ('diode', Kind('二极管', ('D', 'LED', 'CR'), (r':D(?:_|\s|$)|:LED|SCHOTTKY|DIODE|' + B + r'(?:SS\d{2}|BAT\d|1N4\d{3}|1N58\d)|二极管',),
                   ('rectifier', 'diode', 'schottky', 'led'))),
    # Multi-winding magnetics by what they do, above the CHOKE and ferrite words (schematic-review 2026-10-27 A1b).
    ('common_mode_choke', Kind('共模扼流圈', (), (r'COMMON[-_ ]?MODE|共模',),
                               ('commonmodechoke', 'commonmodefilter', 'commonmodeinductor', 'commonmodecoil'))),
    ('coupled_inductor', Kind('耦合电感', (), (r'COUPLED[-_ ]?INDUCTOR|耦合电感',), ('coupledinductor',))),
    ('ferrite', Kind('磁珠', ('FB',), (r'FERRITE|BEAD|' + B + r'(?:BLM\d|MPZ\d)|磁珠',), ('ferrite', 'bead'))),
    ('inductor', Kind('电感', ('L', 'FL'), (r':L(?:_|\s|$)|:CMC|INDUCTOR|CHOKE|电感',), ('inductor', 'choke'))),
    ('crystal', Kind('晶体', ('Y', 'X'), (r'CRYSTAL|XTAL|\bOSC(?:ILLATOR)?\b|晶振|晶体',), ('crystal', 'oscillator', 'resonator'))),
    ('transformer', Kind('变压器', ('T', 'TR'), (r'TRANSFORMER|变压器',), ('transformer',))),
    ('fuse', Kind('保险丝', ('F',), (r'FUSE|PTC|保险',), ('fuse', 'pptc', 'ptc', 'resettable', 'polyswitch'))),
    ('battery', Kind('电池', ('BT', 'BAT'), (r'(?:^|[\s:_])BATTERY|电池',), ('battery',))),
    ('testpoint', Kind('测试点', ('TP',), (r'TEST_?POINT|TEST-?PAD',), ('testpoint',))),
    ('connector', Kind('连接器', ('J', 'P', 'CN'), (r'CONNECTOR[A-Z_]*:|CONN_\d|USB_C_|RECEPTACLE|BARREL_?JACK|PINHEADER|'
                                               r'TERMINAL_?BLOCK|SCREW_TERMINAL',),
                       ('connector', 'receptacle', 'terminalblock', 'terminal', 'header', 'jack', 'plug', 'socket'))),
    ('switch', Kind('开关', ('SW', 'S'), (r':SW_|SWITCH:|KEYSW|:MX-',), ('switch',))),
    ('jumper', Kind('跳线', ('JP',), (r'JUMPER',), ('jumper',))),
    ('mechanical', Kind('机械件', ('H', 'MH', 'MB', 'FID', 'LOGO', 'HS'), (r'MOUNTINGHOLE|FIDUCIAL|HEATSINK|MECHANICAL:',), ())),
    ('capacitor', Kind('电容', ('C', 'CX', 'CY'), (r':C(?:_|\s|$)|:CP(?:_|\d*(?:\s|$))|CAPACITOR',),
                       ('capacitor', 'x1', 'x2', 'y1', 'y2'))),
    ('resistor', Kind('电阻', ('R', 'RN'), (r':R(?:_|\s|$)|RESISTOR|POTENTIOMETER',), ('resistor',))),
    ('ic', Kind('集成电路', ('U', 'M', 'IC', 'A', 'MODULE', 'REF'), (), ())),
])
KEY_KINDS = ('ic', 'mosfet', 'bjt', 'opto', 'transformer', 'zener', 'tvs', 'bridge_rectifier')
IC_PREFIXES = KINDS['ic'].prefixes
# A more specific declared kind than the symbol shows is not a conflict.
REFINES = {'diode': ('tvs', 'zener'), 'inductor': ('transformer', 'ferrite', 'common_mode_choke', 'coupled_inductor')}
MAGNETICS = ('inductor', 'transformer', 'common_mode_choke', 'coupled_inductor')
SAFETY_CLASS = re.compile(r'(?<![A-Za-z0-9])[XY][12](?![A-Za-z0-9])')
VOLTAGE = re.compile(r'\d\s*k?V(?![A-Za-z])|\d\s*k?V(?:ac|dc|AC|DC|rms)', re.I)
CURRENT = re.compile(r'\d\s*m?A(?![A-Za-z])|\d\s*m?A(?:rms|pk|dc)', re.I)


# Subcategories are the library's second level (raw/Datasheet/<category>/<subcategory>); only resistors and
# capacitors are subdivided for the level. Tiers are the commodity bounds of the catalogs checked on 2026-10-26
# (part-roles.md section 1): within a tier a part is common, beyond it special.
R_CAT, C_CAT = '22_电阻器/', '20_电容器/'
GENERAL_R, THIN_R, SENSE_R, POWER_R, POT_R, NETWORK_R = (R_CAT + n for n in (
    '厚膜贴片电阻 (通用)', '薄膜贴片电阻', '电流检测电阻 (分流)', '功率电阻 (线绕_金属板)', '电位器_微调', '电阻网络_分压器'))
MLCC, ALUMINUM, POLYMER, TANTALUM, FILM, SAFETY_C = (C_CAT + n for n in (
    'MLCC多层陶瓷电容', '铝电解电容', '聚合物电容', '钽电容', '薄膜电容', '安规电容(X_Y)'))
SUBCATEGORIES = {'resistor': (GENERAL_R, THIN_R, SENSE_R, POWER_R, POT_R, NETWORK_R),
                 'capacitor': (MLCC, ALUMINUM, POLYMER, TANTALUM, FILM, SAFETY_C)}
PULSE = re.compile(r'pulse|脉冲|浪涌|surge', re.I)
DV_DT = re.compile(r'dv/dt|snubber|吸收', re.I)
# Current-sense tiers: (lowest Ω, highest Ω, highest power W at 70 °C, weakest TCR ppm/K); ±1 % throughout.
# Vishay WSL p1-p2, Panasonic ERJ low resistance p2-p3, Bourns CRL p1 and CRA p1.
SENSE_TIERS = ((0.001, 0.0019999, 1.0, 275), (0.002, 0.0029999, 2.0, 275), (0.003, 0.0049999, 2.0, 150),
               (0.005, 0.0099999, 2.0, 300), (0.010, 0.100, 3.0, 300), (0.100001, 0.999999, 1.0, 300))
# Power-resistor tiers: (highest power W at 70 °C, lowest Ω, highest Ω, tightest tolerance %, weakest TCR ppm/K).
# Vishay PR01/PR02/PR03 p1-p2 (metal film, ±1 %) and AC01-AC10 p1 (wirewound, ±5 %).
POWER_TIERS = ((3.0, 0.22, 1e6, 1.0, 250), (3.0, 0.1, 27e3, 5.0, 250), (8.4, 0.1, 27e3, 5.0, 180))


def spec_text(comp):
    return '%s %s %s %s' % (comp.get('value') or '', fields(comp).get('Specification') or '',
                            fields(comp).get('Rating') or '', fields(comp).get('RequirementSpec') or '')


def ohms(value):
    """Resistance of a value such as 0R30, 4k7, R10, 10m, 0.10/1%/1W or 2.4k 1%; None when it is not one."""
    head = re.split(r'[/\s]', str(value or '').strip())[0].replace(',', '.').replace('Ω', '').replace('ohm', '')
    scale = {'R': 1, 'r': 1, '': 1, 'K': 1e3, 'k': 1e3, 'M': 1e6, 'm': 1e-3}
    m = re.fullmatch(r'(\d*)([RrKkMm])(\d+)', head)          # letter as the decimal point: 0R30, 4k7, R10
    if m:
        return float('%s.%s' % (m.group(1) or '0', m.group(3))) * scale[m.group(2)]
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([mkKM]?)[Rr]?', head)
    return float(m.group(1)) * scale[m.group(2)] if m else None


def watts(text_):
    found = [float(a) / float(b) if b else float(a) for a, b in re.findall(r'(\d+(?:\.\d+)?)(?:/(\d+))?\s*W(?![A-Za-z])', text_)]
    return max(found) if found else None


def tolerance(text_):
    found = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*%', text_)]
    return min(found) if found else None


def tcr(text_):
    found = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*ppm', text_, re.I)]
    return min(found) if found else None


def datasheet_category(comp):
    """The library subcategory a part's datasheet is filed under (…/Datasheet/<category>/<subcategory>/…)."""
    parts = Path(str(comp.get('datasheet') or '')).parts
    for i, part in enumerate(parts[:-3]):
        if part == 'Datasheet':
            return parts[i + 1] + '/' + parts[i + 2]
    return None


def category(comp, kind=None):
    """(subcategory, problem): declared, else the datasheet's library folder, else read off value and symbol."""
    kind = kind or kind_of(comp)[0]
    declared = fields(comp).get('Category')
    known = SUBCATEGORIES.get(kind, ())
    if text(declared):
        if known and declared not in known:
            return None, 'fields.Category 写的 %s 不是%s的子类（可选：%s）' % (declared, KINDS[kind].title, '、'.join(known))
        if ((declared.startswith(R_CAT) and kind != 'resistor')
                or (declared.startswith(C_CAT) and kind != 'capacitor')):
            return None, 'fields.Category 与实际器件类型 %s 不一致，不能按位号前缀套电阻/电容模板' % kind
        return declared, None
    filed = datasheet_category(comp)
    if filed and (not known or filed in known):
        return filed, None
    if not known:
        return None, None
    spec, lib = spec_text(comp), str(comp.get('lib_id', ''))
    if kind == 'resistor':
        r, w = ohms(comp.get('value')), watts(spec)
        if re.search(r'R_Potentiometer|POT', lib, re.I):
            return POT_R, None
        if re.search(r'R_Pack|R_Network', lib, re.I):
            return NETWORK_R, None
        if (r is not None and 0 < r < 1) or re.search(r'检流|分流|shunt|sense|开尔文|kelvin', spec, re.I):
            return SENSE_R, None
        if (w and w > 1) or re.search(r'线绕|wirewound|metal film power', spec, re.I):
            return POWER_R, None
        return (THIN_R if re.search(r'thin film|薄膜', spec, re.I) else GENERAL_R), None
    if prefix(comp) in ('CX', 'CY') or SAFETY_CLASS.search(spec):
        return SAFETY_C, None
    if re.search(r'polymer|固态|POSCAP|OS-CON', spec, re.I):
        return POLYMER, None
    if re.search(r'tantal|钽|TAJ', spec + ' ' + str(comp.get('mpn') or ''), re.I):
        return TANTALUM, None
    if re.search(r'film|薄膜|MKP|MKT|CBB', spec, re.I):
        return FILM, None
    return (ALUMINUM if re.search(r':C_Polarized|:CP', lib, re.I) else MLCC), None


def beyond_tier(comp, cat):
    """Why a sense or power resistor lies outside every commodity tier, or None when one tier holds it."""
    spec = spec_text(comp)
    r, w, tol, ppm = ohms(comp.get('value')), watts(spec), tolerance(spec), tcr(spec)
    if r is None:
        return None
    if cat == SENSE_R:
        tier = next((t for t in SENSE_TIERS if t[0] <= r <= t[1]), None)
        if tier is None:
            return '阻值 %g Ω 不在检流电阻档位内' % r
        if w and w > tier[2]:
            return '功率 %g W 超过该档上限 %g W' % (w, tier[2])
        if tol is not None and tol < 1:
            return '容差 ±%g%% 比档位的 ±1%% 更紧' % tol
        if ppm is not None and ppm < tier[3]:
            return 'TCR %g ppm/K 比档位最弱值 %g ppm/K 更严' % (ppm, tier[3])
        return None
    if cat == POWER_R:
        fits = [t for t in POWER_TIERS if (w or 0) <= t[0] and t[1] <= r <= t[2]
                and (tol is None or tol >= t[3]) and (ppm is None or ppm >= t[4])]
        return None if fits else '功率 %s W、阻值 %g Ω、容差 %s、TCR %s 不在功率电阻档位内' % (
            w, r, '±%g%%' % tol if tol is not None else '未写', '%g ppm/K' % ppm if ppm is not None else '未写')
    return None


def special_spec(comp, kind):
    """Why a resistor or capacitor's own specification makes it special, or None."""
    if kind not in SUBCATEGORIES:
        return None
    spec = spec_text(comp)
    cat, _ = category(comp, kind)
    if PULSE.search(spec):
        return '规格要求脉冲或浪涌能力'
    if cat == FILM and DV_DT.search(spec):
        return '薄膜电容用于吸收或承受 dv/dt'
    return beyond_tier(comp, cat)


def prefix(comp):
    return re.match(r'[A-Z]*', str(comp.get('ref', '')).upper()).group()


def fields(comp):
    return comp.get('fields') if isinstance(comp.get('fields'), dict) else {}


def inferred_kind(comp):
    """(kind, basis) from the symbol and part number ('symbol'), then the reference prefix ('prefix'); (None, None)."""
    blob = ' '.join(str(comp.get(k) or '') for k in ('lib_id', 'value', 'mpn')).upper()
    ic_ref = prefix(comp) in IC_PREFIXES
    named = [name for name, kind in KINDS.items() for w in kind.words if re.search(w, blob, re.I)]
    if {'bjt', 'mosfet'} <= set(named):
        named = [n for n in named if n not in ('bjt', 'mosfet')]
    for name in named:
        # An IC's text names other kinds ("charger with NTC input", CP2102): only a key kind re-identifies it.
        if not ic_ref or name in KEY_KINDS:
            return name, 'symbol'
    for name, kind in KINDS.items():
        if prefix(comp) in kind.prefixes:
            return name, 'prefix'
    return None, None


def kind_of(comp):
    """(kind, problem): the declared kind when it is a known kind and agrees with the symbol, else the inferred one."""
    declared = fields(comp).get('Kind')
    inferred, basis = inferred_kind(comp)
    if not text(declared):
        return inferred, None
    if declared not in KINDS:
        return inferred, 'fields.Kind 写的 %s 不是器件类型（可选：%s）' % (declared, '、'.join(KINDS))
    if basis == 'symbol' and inferred != declared and declared not in REFINES.get(inferred, ()):
        return declared, '类型声明 %s 与符号或型号 %s 推断的 %s 不一致（选错了符号或填错了型号）' % (
            declared, comp.get('lib_id') or comp.get('value'), inferred)
    return declared, None


def context(intent):
    """Nets of each part, the net roles and the declared high-voltage nets (None when not declared)."""
    nets = intent.get('nets') or []
    items = nets.items() if isinstance(nets, dict) else ((n.get('name'), n.get('pins')) for n in nets if isinstance(n, dict))
    pins = {}
    for name, members in items:
        for pin in members or []:
            pins.setdefault(str(pin).rsplit('.', 1)[0], set()).add(name)
    hv = intent.get('high_voltage_nets')
    return {'pins': pins, 'roles': intent.get('net_roles') or {}, 'hv': set(hv) if isinstance(hv, list) else None}


def part_class(comp, ctx=None):
    """key / special / common for one design-netlist component, or None when its kind is not known."""
    ctx = ctx or {'pins': {}, 'roles': {}, 'hv': None}
    kind, _ = kind_of(comp)
    if kind is None:
        return None
    nets = ctx['pins'].get(comp.get('ref'), set())
    high = ctx['hv'] is None or bool(nets & ctx['hv'])
    if design_sheet(comp) and kind in MAGNETICS:
        return KEY
    if kind in KEY_KINDS:
        return KEY
    if kind in ('varistor', 'fuse'):
        return SPECIAL
    if kind == 'capacitor' and category(comp, kind)[0] == SAFETY_C:
        return SPECIAL
    from .component_requirements import spec_procurement
    if special_spec(comp, kind) and not spec_procurement(comp):
        return SPECIAL
    if kind in ('connector', 'relay') and high:
        return SPECIAL
    if kind == 'ntc' and (high or (nets and all(ctx['roles'].get(n) in ('power', 'return') for n in nets))):
        return SPECIAL
    return COMMON


def text(value):
    return isinstance(value, str) and bool(value.strip())


def find(path, bases):
    """A datasheet path from the design netlist or a citation: absolute, under the delivery, or in the library."""
    if not text(path):
        return None
    found = resolve(os.path.expanduser(path), bases)
    if found and Path(found).is_file():
        return Path(found)
    return locate(path, bases)


def _name(path):
    stem = Path(str(path)).stem.split(' - ')[-1]
    return re.sub(r'[^0-9a-z]', '', stem.lower())


def same_document(a, b, bases):
    """Two datasheet references name one document: equal bytes, or the same part name in the file names."""
    fa, fb = find(a, bases), find(b, bases)
    if fa and fb:
        digest = [hashlib.sha256(f.read_bytes()).hexdigest() for f in (fa, fb)]
        if digest[0] == digest[1]:
            return True
    na, nb = _name(a), _name(b)
    return bool(na) and bool(nb) and (na == nb or na.endswith(nb) or nb.endswith(na))


def design_sheet(comp):
    sheet = fields(comp).get('DesignSheet')
    return sheet if text(sheet) else None


def touched_refs(contract):
    """Parts this revision adds or changes, per record/change-contract.json; None for a new design."""
    if not isinstance(contract, dict):
        return None
    return set(contract.get('add_components') or {}) | set(contract.get('component_changes') or {})


def squash(value):
    return re.sub(r'[^0-9a-z]', '', str(value or '').lower())


SPECIFIC_DIODES = ('tvs', 'zener', 'bridge_rectifier')     # a quote naming these is not evidence for a plain diode
# Cues of schematic-review's integrated-circuit roles (catalog.DEVICE_ROLES). ASG declares no IC role; a text naming one
# describes an IC, and the discretes, fuses and relays it names are its load or its function ("Industrial eFuse" is a
# load switch, "relay driver" drives a coil). A kind is what the part does at its pins, not what is inside it.
IC_ROLE_CUES = (
    'pwmcontroller', 'pfccontroller', 'flybackcontroller', 'currentmodecontroller', 'voltagemodecontroller',
    'switchingcontroller', 'offlinecontroller', 'quasiresonantcontroller', 'boostcontroller', 'buckcontroller',
    'powerfactorcorrectioncontroller', 'powerfactorcontroller', 'resonantcontroller', 'llccontroller',
    'switchmodecontroller', 'pwmcontrol',
    'gatedriver', 'mosfetdriver', 'igbtdriver', 'bridgedriver', 'fetdriver',
    'synchronousrectif', 'srcontroller',
    'pdcontroller', 'powerdelivery', 'usbpd', 'typeccontroller', 'usbccontroller',
    'voltageregulator', 'linearregulator', 'lowdropout', 'ldoregulator', 'dcdcconverter', 'buckconverter', 'boostconverter',
    'switchingregulator', 'stepdownconverter', 'stepupconverter', 'powermanagementic', 'pmic', 'chargepump',
    'supervisor', 'supervisory', 'voltagemonitor', 'resetcircuit', 'resetic', 'watchdog',
    'operationalamplifier', 'opamp', 'comparator', 'erroramplifier', 'instrumentationamplifier',
    'currentsenseamplifier', 'currentshuntmonitor', 'differenceamplifier', 'audioamplifier',
    'shuntregulator', 'voltagereference', 'shuntreference',
    'microcontroller', 'microprocessor', 'systemonchip', 'mcu',
    'transceiver', 'ethernetphy', 'linedriver', 'busdriver',
    'digitalisolator', 'isolatedgatedriver', 'isolator',
    'loadswitch', 'hotswap', 'efuse', 'idealdiode', 'powerdistributionswitch', 'currentlimitswitch', 'highsideswitch',
    'batterycharger', 'chargecontroller', 'chargemanagement', 'switchingcharger', 'linearcharger', 'chargeric',
    'analogtodigital', 'digitaltoanalog', 'bitadc', 'bitdac', 'channeladc', 'channeldac', 'audiodac', 'audioadc',
    'sigmadeltaadc', 'deltasigmaadc',
    'crystaloscillator', 'clockgenerator', 'clockbuffer', 'clocksynthesizer', 'jittercleaner', 'oscillator',
    'clockdistribution', 'realtimeclock', 'clockmultiplier',
    'flashmemory', 'serialflash', 'spiflash', 'eeprom', 'sdram', 'lpddr', 'ddr2', 'ddr3', 'ddr4', 'ddr5', 'nandflash',
    'norflash', 'sram', 'emmc',
    'leveltranslat', 'levelshifter', 'voltagetranslat', 'voltageleveltranslat',
    'motordriver', 'steppermotor', 'brushlessdc', 'bldc', 'brusheddc', 'hbridgedriver', 'fullbridgedriver',
    'halfbridgedriver')
ROLE_LOADS = {'mosfet', 'bjt', 'diode', 'zener', 'tvs', 'bridge_rectifier', 'fuse', 'relay'}
WORD_CUES = ('fuse',)   # squashed, "Littelfuse" (a maker's name) holds fuse: read as a word too


def named_by(cue, value, flat):
    """As schematic-review's datasheet_kinds.named_by: a long cue anywhere in the squashed text, a cue of three letters
    or fewer (or a word cue) as a word of its own; a lowercase-to-capital join counts as a space and a plural s is
    allowed."""
    if len(cue) > 3 and cue not in WORD_CUES:
        return cue in flat
    spaced = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', str(value or ''))
    return re.search(r'(?<![A-Za-z0-9])(?:%s(?![0-9])|(?i:%s)s?(?![a-z0-9]))' % (cue.upper(), cue), spaced) is not None


def cues(value, specific=True):
    """Kinds a datasheet text names, as schematic-review's datasheet_kinds.cues (extraction drops spaces, so long cues
    are looked for in the squashed text)."""
    flat = squash(value)
    found = {kind for kind, k in KINDS.items() for cue in k.cues if named_by(cue, value, flat)}
    if specific and found & set(SPECIFIC_DIODES):
        found.discard('diode')
    if specific and found & {'common_mode_choke', 'coupled_inductor'}:
        found.discard('inductor')       # "coupled inductor", "common mode choke": the specific magnetic is the kind
    if specific and 'opto' in found:
        found -= {'diode', 'bjt'}       # an optocoupler names its emitter diode and phototransistor too
    if specific and any(named_by(cue, value, flat) for cue in IC_ROLE_CUES):
        found -= ROLE_LOADS
    if specific and found & {'ntc', 'varistor'}:
        found.discard('fuse')           # a thermistor or varistor datasheet names its thermally fused (ThermoFuse) types
    if specific and 'relaydriver' in flat:
        found.discard('relay')          # a relay driver drives the coil
    return found


def verify_declaration(comp, kind, bases, check_files):
    """(status, detail) of a kind declaration, with schematic-review's statuses: VERIFIED, QUOTE_NOT_FOUND,
    QUOTE_LACKS_TYPE, QUOTE_CONFLICT, NO_DOCUMENT, NO_TEXT; ('MISSING', what) when a field is not written."""
    f = fields(comp)
    if not text(f.get('Kind')):
        return 'MISSING', '类型声明（fields.Kind、KindSource、KindQuote，按本器件手册；propose_part_kinds.py 给候选）'
    cited = parse(f.get('KindSource'))
    if not cited:
        return 'MISSING', '类型声明的手册页（fields.KindSource 写 datasheet:<库内路径>#p<页>）'
    if not text(f.get('KindQuote')):
        return 'MISSING', '类型声明的手册原文（fields.KindQuote）'
    if text(comp.get('datasheet')) and not same_document(comp['datasheet'], cited[0], bases):
        return 'NO_DOCUMENT', 'KindSource %s 与 datasheet %s 不是同一份手册' % (cited[0], comp['datasheet'])
    quote = f['KindQuote']
    if check_files:
        result = check(cited[0], cited[1], (), bases)
        if result['status'] == 'FAIL':
            return 'NO_DOCUMENT', result['reason']
        pdf = locate(cited[0], bases)
        page = page_text(pdf, cited[1]) if pdf else None
        if pdf is None or result['status'] == 'NOT_CHECKED' or len(squash(page)) < 20:
            return 'NO_TEXT', '%s 第 %d 页取不出文字（%s）' % (cited[0], cited[1], result['reason'] or '扫描版或没有 pdftotext')
        if squash(quote) not in squash(page):
            return 'QUOTE_NOT_FOUND', 'KindQuote 不在 %s 第 %d 页' % (cited[0], cited[1])
    else:
        return 'NO_TEXT', '找不到知识库，%s 没核对' % cited[0]
    named = cues(quote)
    if kind not in cues(quote, specific=False):
        return 'QUOTE_LACKS_TYPE', 'KindQuote 没有说出 %s（说的是 %s）' % (kind, '、'.join(sorted(named)) or '无器件类型')
    if named - {kind}:
        return 'QUOTE_CONFLICT', 'KindQuote 还说出了 %s' % '、'.join(sorted(named - {kind}))
    return 'VERIFIED', ''


def needs_declaration(comp, kind, level):
    return level in (KEY, SPECIAL) and kind not in (None, 'ic') and not design_sheet(comp)


def audit_identity(intent, bases, touched=None):
    """(problems, inherited, unchecked): parts whose kind or subcategory is unknown or contradicted, key and special
    parts lacking an MPN, a datasheet or a verified kind declaration, and common parts without their ratings;
    unchecked lists kind declarations whose page text could not be read (NO_TEXT), which do not block.

    With a change contract only parts the revision adds or changes are problems; parts kept from the
    baseline are listed as inherited."""
    problems, inherited, unchecked = [], [], []
    check_files = library_present()
    ctx = context(intent)
    for comp in intent.get('components') or []:
        if not isinstance(comp, dict):
            continue
        ref = comp.get('ref')
        kind, conflict = kind_of(comp)
        conflict = conflict or (category(comp, kind)[1] if kind else None)
        kind_cls = part_class(comp, ctx)
        lack = [conflict] if conflict else []
        if kind is None:
            lack.append('器件类型（认不出，写 fields.Kind：%s）' % '、'.join(KINDS))
        elif kind_cls in (KEY, SPECIAL):
            sheet = design_sheet(comp) or comp.get('datasheet')
            magnetic = kind in MAGNETICS
            if not text(comp.get('mpn')):
                lack.append('料号（mpn）')
            if not text(sheet):
                lack.append('数据手册（datasheet%s）' % ('；定制磁件写 fields.DesignSheet' if magnetic else ''))
            elif check_files and not find(sheet, bases):
                lack.append('能找到的数据手册（%s 不在交付目录或知识库里）' % sheet)
            if needs_declaration(comp, kind, kind_cls):
                status, detail = verify_declaration(comp, kind, bases, check_files)
                if status == 'NO_TEXT':
                    unchecked.append('%s：%s' % (ref, detail))
                elif status != 'VERIFIED':
                    lack.append(detail if status == 'MISSING' else '核对通过的类型声明（%s：%s）' % (status, detail))
        else:
            rating = spec_text(comp)
            if kind == 'capacitor' and not VOLTAGE.search(rating):
                lack.append('耐压（写在值或 fields.Specification 里）')
            if kind in ('inductor', 'common_mode_choke', 'coupled_inductor') and not CURRENT.search(rating):
                lack.append('额定电流（写在值或 fields.Specification 里）')
            cat = category(comp, kind)[0]
            if cat in (SENSE_R, POWER_R):
                need = (('阻值', ohms(comp.get('value')) is not None),) if cat == SENSE_R else ()
                need += (('容差', tolerance(rating) is not None), ('功率', watts(rating) is not None))
                lack += ['%s（%s要写）' % (name, cat.split('/')[1]) for name, ok in need if not ok]
        if not lack:
            continue
        lack = [x for x in lack if x != conflict]
        said = ([conflict] if conflict else []) + (['缺' + '、'.join(lack)] if lack else [])
        why = special_spec(comp, kind) if kind_cls == SPECIAL else None
        line = '%s %s（%s%s）%s' % (CLASS_NAMES.get(kind_cls, '器件'), ref, comp.get('value', ''),
                                  '；升为特殊器件：' + why if why else '', '；'.join(said))
        (problems if touched is None or ref in touched else inherited).append(line)
    return problems, inherited, unchecked


def audit_citations(intent, closure, bases):
    """Each datasheet cited in a calculation parameter or a data gap names its parts, and they carry that datasheet."""
    comps = {c.get('ref'): c for c in intent.get('components') or [] if isinstance(c, dict)}
    problems = []

    def bound(where, source, refs):
        cited = parse(source)
        # Only a part's datasheet binds to a part; standards and application notes do not.
        if not cited or not cited[0].startswith('Datasheet/'):
            return
        if not refs:
            problems.append('%s 引用了手册 %s，要写明它说的是哪个位号' % (where, cited[0]))
            return
        for ref in refs:
            comp = comps.get(ref)
            if comp is None:
                problems.append('%s 引用手册的位号 %s 不在设计网表里' % (where, ref))
            elif design_sheet(comp):
                continue        # a custom magnetic's design sheet names its core and material datasheets
            elif not text(comp.get('datasheet')):
                problems.append('%s 引用了手册 %s，但设计网表里 %s 没有写 datasheet' % (where, cited[0], ref))
            elif not text(comp.get('mpn')):
                problems.append('%s 引用了手册 %s，%s 因此是特殊器件，设计网表里要写它的 mpn' % (where, cited[0], ref))
            elif not same_document(comp['datasheet'], cited[0], bases):
                problems.append('%s 引用的手册 %s 与设计网表里 %s 的 datasheet %s 不是同一份'
                                % (where, cited[0], ref, comp['datasheet']))

    for calc in closure.get('calculations') or []:
        for p in (calc.get('parameters') or []) if isinstance(calc, dict) else []:
            if isinstance(p, dict):
                bound('计算 %s 的参数“%s”' % (calc.get('id'), p.get('name')), p.get('source'),
                      [p['ref']] if text(p.get('ref')) else [])
    for item in closure.get('work_items') or []:
        for i, gap in enumerate((item.get('missing') or []) if isinstance(item, dict) else [], 1):
            if isinstance(gap, dict):
                refs = gap.get('refs') if isinstance(gap.get('refs'), list) else []
                bound('待办 %s 的第 %d 项资料缺口' % (item.get('id'), i), gap.get('source'), [r for r in refs if text(r)])
    return problems


# Parts that do not conduct DC between their pins when nets are grouped into DC domains (schematic-review
# checkers/domains.py); an unknown part merges nothing.
NON_CONDUCTING = ('capacitor', 'transformer', 'opto', 'relay', 'crystal', 'connector', 'testpoint', 'battery', None)
PROTECTION_KINDS = ('fuse', 'varistor', 'tvs', 'zener')
MAINS_SIDE_KINDS = ('fuse', 'varistor', 'connector', 'relay')
APPROVAL = re.compile(r'IEC|EN\s?\d|UL|GB|CQC|VDE|T[ÜU]V|CSA|ENEC|CCC|datasheet:.+#p\d+')
SAFETY_RELEVANT = ('fuse', 'varistor', 'transformer', 'opto')


def domains(intent, ctx=None):
    """{net: domain root}: nets joined through every part that conducts DC between its pins."""
    ctx = ctx or context(intent)
    parent = {}

    def root(n):
        parent.setdefault(n, n)
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    for comp in intent.get('components') or []:
        nets = sorted(n for n in ctx['pins'].get(comp.get('ref'), ()) if n)
        for n in nets:
            root(n)
        if isinstance(comp, dict) and kind_of(comp)[0] not in NON_CONDUCTING:
            for n in nets[1:]:
                parent[root(n)] = root(nets[0])
    return {n: root(n) for n in list(parent)}


def safety_positions(intent, ctx=None):
    """{ref: 'isolation' | 'mains'}: parts bridging a hazardous-voltage domain and another, and safety parts on
    high_voltage_nets. Empty when high_voltage_nets is not declared."""
    ctx = ctx or context(intent)
    if ctx['hv'] is None:
        return {}
    dom = domains(intent, ctx)
    hazardous = {dom[n] for n in ctx['hv'] if n in dom}
    out = {}
    for comp in intent.get('components') or []:
        if not isinstance(comp, dict):
            continue
        nets = ctx['pins'].get(comp.get('ref'), set())
        groups = {dom[n] for n in nets if n in dom}
        kind = kind_of(comp)[0]
        if groups & hazardous and groups - hazardous:
            out[comp['ref']] = 'isolation'
        elif nets & ctx['hv'] and (kind in MAINS_SIDE_KINDS or (kind == 'capacitor' and category(comp, kind)[0] == SAFETY_C)):
            out[comp['ref']] = 'mains'
    return out


def protection_part(comp, ctx):
    kind = kind_of(comp)[0]
    return kind in PROTECTION_KINDS or (kind == 'ntc' and part_class(comp, ctx) == SPECIAL)


def audit_safety(intent, closure, touched=None):
    """(problems, inherited): protection parts without a two-sided threshold calculation, parts at safety positions
    without an approval, safety capacitors without their discharge or touch-current calculation, and a design with
    safety parts but no high_voltage_nets."""
    ctx = context(intent)
    calcs = [c for c in (closure or {}).get('calculations') or [] if isinstance(c, dict)]
    in_calc = {r for c in calcs for r in c.get('refs') or []}
    in_threshold = {r for c in calcs if c.get('kind') == 'threshold' for r in c.get('refs') or []}
    positions = safety_positions(intent, ctx)
    problems, inherited = [], []

    def add(ref, line):
        (problems if touched is None or ref in touched else inherited).append(line)

    comps = [c for c in intent.get('components') or [] if isinstance(c, dict)]
    if ctx['hv'] is None and any(kind_of(c)[0] in SAFETY_RELEVANT or category(c)[0] == SAFETY_C for c in comps):
        line = '设计网表没写 high_voltage_nets（工作电压高于 30 V 或接市电的网络），判不出安全防护位置'
        (problems if touched is None else inherited).append(line)
    for comp in comps:
        ref, value = comp.get('ref'), comp.get('value', '')
        if protection_part(comp, ctx) and ref not in in_threshold:
            add(ref, '保护器件 %s（%s）要进一条两侧都算的阈值计算（kind: threshold，含 no_false_trip 与 protection）' % (ref, value))
        where = positions.get(ref)
        if where and not APPROVAL.search(str(fields(comp).get('Approval') or '')):
            add(ref, '%s %s（%s）缺认证（fields.Approval：认证标准与证书号，或手册认证页 datasheet:<路径>#p<页>）' % (
                '跨隔离的器件' if where == 'isolation' else '市电/高压侧的安规件', ref, value))
        if category(comp)[0] == SAFETY_C and ref not in in_calc:
            y = where == 'isolation' or prefix(comp) == 'CY' or re.search(r'(?<![A-Za-z0-9])Y[12]', spec_text(comp))
            add(ref, '%s %s（%s）要进%s计算的 refs' % ('Y 电容' if y else 'X 电容', ref, value, '接触电流' if y else '放电'))
    return problems, inherited
