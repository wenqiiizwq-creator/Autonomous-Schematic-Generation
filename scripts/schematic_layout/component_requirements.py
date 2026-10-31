"""Performance contracts: calculation -> procurement -> IR/BOM -> native drawing.

The source record is deliberately separate from the selected part's guarantees.
Projection is explicit during preparation; checking never repairs stale outputs.
"""
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

VERSION = 1
FIELDS = ('RequirementSpec', 'ProcurementMode', 'SelectionStatus', 'SelectedSpec',
          'RequirementsSHA256', 'Performance')
OPS = {'eq': '=', 'le': '<=', 'ge': '>='}
DEFINITIONS = {'complete': '性能定义完整', 'pending': '性能待计算'}
SELECTIONS = {'not_selected': '型号未定', 'candidate': '候选待核', 'qualified': '型号已核准',
              'by_spec': '受控规格采购已核实', 'by_design_sheet': '设计单定制已核实',
              'by_bom_spec': 'BOM规格已写全'}
# Selections whose properties are checked one by one and that close the selection.
CLOSED = ('qualified', 'by_spec', 'by_design_sheet')
PARAMETERS = {'resistance': '阻值', 'tolerance': '容差', 'power': '连续额定功率',
              'rated_power': '额定功率', 'continuous_power': '连续额定功率',
              'pulse_energy': '单次脉冲耐受能量', 'pulse_power': '脉冲耐受功率',
              'pulse_voltage': '脉冲耐受电压', 'pulse_current': '脉冲耐受电流',
              'working_voltage': '工作耐压', 'overload_voltage': '过载耐压',
              'capacitance': '容量', 'effective_capacitance': '有效容量',
              'inductance': '电感量', 'current': '额定电流', 'drift': '漂移'}
# A spec-bought common part closes once each requirement is in its exported BOM/XML RequirementSpec; finding the part
# and checking its guarantees is handed to procurement (user 2026-10-28: 先改前四条; 同意按此做).
BOM_SPEC = 'by_bom_spec'
# Commodity chip-resistor floor voltages (V), mirroring schematic-review passive_stress RESISTOR_FLOORS: a working
# voltage within the package's weakest part derated by RES-SMD-V constrains nothing (SR passes it with no rating
# written). The record names no derating level, so the spec's unset_level (I, the strictest) applies (user 2026-10-29:
# 类似这种单一的规则，都先不要，全都并入到降额规范里面去).
RESISTOR_VOLTAGE_FLOORS = {'0201': 15.0, '0402': 25.0, '0603': 50.0, '0805': 100.0,
                           '1206': 150.0, '1210': 200.0, '2010': 200.0, '2512': 200.0}
ASSUMED_PACKAGE = '0402'
DERATING_RULES = Path(__file__).resolve().parents[2] / 'references' / 'derating-rules.json'


def voltage_share():
    """RES-SMD-V at the shared derating spec's unset_level."""
    spec = json.loads(DERATING_RULES.read_text(encoding='utf-8'))
    level = spec['engineering_values']['unset_level']['value']
    return next(r for r in spec['rules'] if r['id'] == 'RES-SMD-V')['values'][level]


RESISTOR_PACKAGE = re.compile(r'^Resistor_SMD:R_(0201|0402|0603|0805|1206|1210|2010|2512)_', re.I)
BOILERPLATE_REFS, TEMPLATE_CONDITIONS = 3, ('waveform', 'drift')
CONDITIONS = {'waveform': '波形', 'duration': '持续时间', 'repetition': '重复条件',
              'temperature': '温度', 'drift': '次数及允许漂移'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def compact(value):
    return re.sub(r'\s+', '', str(value))


def document_text(path):
    if path.suffix.lower() != '.pdf':
        try:
            return path.read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            return None
    cli = shutil.which('pdftotext')
    if not cli:
        return None
    result = subprocess.run([cli, '-layout', str(path), '-'], capture_output=True, timeout=60)
    return result.stdout.decode('utf-8', errors='replace') if result.returncode == 0 else None


def declared_inputs(root, inputs=None):
    if inputs is not None:
        return {k: Path(v).resolve() for k, v in inputs.items()}
    path = Path(root) / 'record' / 'deliver.json'
    if path.is_file():
        data = json.loads(path.read_text(encoding='utf-8')).get('inputs', {})
        return {k: (Path(root) / v).resolve() for k, v in data.items()}
    return {}


def source_errors(source, root, guaranteed=False, inputs=None):
    if not isinstance(source, dict) or not all(text(source.get(k)) for k in ('path', 'sha256', 'locator')):
        return ['source needs path, sha256 and locator']
    base = Path(root).resolve()
    raw = source['path']
    if raw.startswith('input:'):
        name, _, relative = raw[6:].partition('/')
        base = declared_inputs(root, inputs).get(name)
        if base is None:
            return ['undeclared evidence input: ' + name]
        path = (base / relative).resolve() if relative else base
        permitted = path == base if base.is_file() else path.is_relative_to(base)
    else:
        path = (base / raw).resolve()
        permitted = path.is_relative_to(base)
    if not permitted or not path.is_file():
        return ['source outside declared evidence roots or missing: ' + raw]
    if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
        return ['source changed: ' + source['path']]
    if guaranteed:
        if source.get('kind') not in ('manufacturer', 'controlled_standard') or not text(source.get('quote')):
            return ['guarantee needs manufacturer/controlled_standard evidence and an exact quote']
        body = document_text(path)
        if body is None:
            return ['guarantee source text cannot be checked; retain candidate status']
        if compact(source['quote']) not in compact(body):
            return ['guarantee quote not found in source']
        if re.search(r'\btypical\b|\btyp\.|典型|工程估计', source['quote'], re.I):
            return ['typical/model quote cannot establish a guaranteed limit']
    return []


def significant_digits(value):
    mantissa = f'{abs(value):.15g}'.split('e')[0].replace('.', '').strip('0')
    return len(mantissa)


def conservative(value, op, digits=3):
    """A bound rounded to ``digits`` significant digits in the safe direction: a lower bound up, an upper bound down."""
    if value == 0 or op == 'eq':
        return value
    scale = 10 ** (math.floor(math.log10(abs(value))) - digits + 1)
    step = math.ceil if op == 'ge' else math.floor
    return float(f'{step(round(value / scale, 9)) * scale:.{digits}g}')


def requirement_label(req):
    """The drawing shows only 参数 比较符 数值 单位; conditions stay in the record and the BOM RequirementSpec."""
    return f"{PARAMETERS.get(req['parameter'], req['parameter'])} {OPS[req['op']]} {req['value']:g} {req['unit']}"


def requirement_line(req):
    conditions = '; '.join(f'{CONDITIONS.get(k, k)}={v}' for k, v in sorted(req.get('conditions', {}).items()))
    name = PARAMETERS.get(req['parameter'], req['parameter'])
    return f"{name}要求: {req['parameter']}{OPS[req['op']]}{req['value']:g} {req['unit']} @ {conditions}"


def note_lines(entry):
    header = f"CR-{entry['ref']}: {entry['purpose']} [{DEFINITIONS[entry['definition_status']]}; {SELECTIONS[entry['selection']['status']]}]"
    lines = [header] + [requirement_label(r) for r in entry.get('requirements', [])]
    if entry['definition_status'] != 'complete':
        lines += ['PENDING / 待计算: ' + '; '.join(entry.get('gaps', []))]
    return lines


def fields_for(entry, record_hash):
    spec = ' | '.join(requirement_line(r) for r in entry.get('requirements', []))
    if entry['definition_status'] != 'complete':
        spec += ' | PENDING / 待计算: ' + '; '.join(entry.get('gaps', []))
    selected = entry.get('selection', {})
    actual = ' | '.join(f"{p['parameter']}={p['value']:g} {p['unit']}"
                        for p in selected.get('properties', [])) if selected.get('status') in CLOSED else ''
    labels = '; '.join(requirement_label(r) for r in entry.get('requirements', []))
    visible = (labels + f" [{SELECTIONS[selected['status']]}]" if entry.get('display') == 'inline'
               else f"要求见 CR-{entry['ref']}")
    return dict(zip(FIELDS, (spec, entry['procurement']['mode'], selected['status'], actual, record_hash, visible)))


def nominal_value(entry):
    """Project an exact electrical nominal when the contract defines one.

    Bounds on effective capacity, pulse capability, etc. do not rename the
    nominal. Designs without an exact nominal requirement retain their IR value.
    """
    parameters = {'resistor': 'resistance', 'capacitor': 'capacitance', 'inductor': 'inductance'}
    for req in entry.get('requirements', []):
        if req.get('parameter') != parameters.get(entry.get('kind')) or req.get('op') != 'eq':
            continue
        value, unit = req['value'], req['unit']
        if entry['kind'] == 'resistor':
            scales = {'ohm': 1, 'Ω': 1, 'kohm': 1000, 'kΩ': 1000, 'Mohm': 1e6, 'MΩ': 1e6,
                      'mohm': .001, 'mΩ': .001}
            if unit in scales:
                ohms = value * scales[unit]
                if abs(ohms) >= 1e6:
                    return f'{ohms / 1e6:g}M'
                if abs(ohms) >= 1000:
                    return f'{ohms / 1000:g}k'
                return format(ohms, '.12f').rstrip('0').rstrip('.') + 'R'
        elif ((entry['kind'] == 'capacitor' and unit in ('F', 'mF', 'uF', 'µF', 'nF', 'pF'))
              or (entry['kind'] == 'inductor' and unit in ('H', 'mH', 'uH', 'µH', 'nH'))):
            return f'{value:g}{unit}'
    return None


def entry_errors(entry, comp=None):
    """Structural validation only; evidence and pin/safety context are checked by audit()."""
    errors = []
    if not isinstance(entry, dict):
        return ['entry must be an object']
    if not all(text(entry.get(k)) for k in ('ref', 'purpose', 'kind')):
        errors.append('entry needs ref, purpose and kind')
    if entry.get('definition_status') not in ('complete', 'pending'):
        errors.append('definition_status must be complete/pending')
    if entry.get('display') not in ('inline', 'note'):
        errors.append('display must be inline/note')
    procurement = entry.get('procurement', {})
    selection = entry.get('selection', {})
    if not isinstance(procurement, dict) or not isinstance(selection, dict):
        return errors + ['procurement and selection must be objects']
    if procurement.get('mode') not in ('spec', 'mpn', 'design_sheet') or not text(procurement.get('reason')):
        errors.append('procurement needs spec/mpn/design_sheet mode and reason')
    if selection.get('status') not in SELECTIONS:
        errors.append('selection status must be not_selected/candidate/qualified/by_spec/by_design_sheet')
    if selection.get('status') in ('candidate', 'qualified') and not all(text(selection.get(k)) for k in ('mpn', 'route')):
        errors.append('selected/candidate part needs mpn and selection route')
    if selection.get('status') == 'by_spec' and (procurement.get('mode') != 'spec'
            or not all(text(selection.get(k)) for k in ('standard_id', 'route')) or text(selection.get('mpn'))):
        errors.append('by_spec requires controlled standard_id, route, spec procurement and no fixed mpn')
    # A custom magnetic is defined by its own design sheet (user 2026-10-28: 按 A 实施): the sheet closes the selection
    # and the sample acceptance stays an external item; a vendor approval sheet later qualifies it as an mpn part.
    if procurement.get('mode') == 'design_sheet' and selection.get('status') not in ('not_selected', 'by_design_sheet'):
        errors.append('design_sheet procurement is not_selected until its sheet is checked, then by_design_sheet')
    if selection.get('status') == 'by_design_sheet' and (procurement.get('mode') != 'design_sheet'
            or not text(selection.get('sheet_id')) or text(selection.get('mpn'))):
        errors.append('by_design_sheet requires design_sheet procurement, the sheet_id and no vendor mpn')
    if selection.get('status') == BOM_SPEC and (procurement.get('mode') != 'spec' or any(
            selection.get(k) for k in ('mpn', 'standard_id', 'properties'))):
        errors.append('by_bom_spec is a spec-bought part with no mpn, standard_id or properties: its BOM spec is the order')
    if selection.get('status') in CLOSED + (BOM_SPEC,) and entry.get('definition_status') != 'complete':
        errors.append('cannot qualify a part before all required performance is defined')
    requirements = entry.get('requirements', [])
    if not isinstance(requirements, list):
        return errors + ['requirements must be a list']
    if entry.get('definition_status') == 'complete' and not requirements:
        errors.append('complete definition needs finite requirements')
    if entry.get('definition_status') == 'pending' and not entry.get('gaps'):
        errors.append('pending definition needs explicit calculation gaps')
    seen = set()
    for req in requirements:
        if not isinstance(req, dict):
            errors.append('requirement must be an object')
            continue
        param = req.get('parameter')
        if not text(param) or param in seen:
            errors.append('requirement parameters must be nonempty and unique')
        if text(param):
            seen.add(param)
        if req.get('op') not in OPS or not finite(req.get('value')) or not text(req.get('unit')):
            errors.append(f'{param}: finite value, unit and eq/le/ge operator required')
        if not isinstance(req.get('conditions'), dict) or not req['conditions'] or any(not text(v) for v in req['conditions'].values()):
            errors.append(f'{param}: applicable conditions required')
        elif entry.get('definition_status') == 'complete' and any(
                re.search(r'\bTBD\b|\bunknown\b|待定|待计算|待确认', v, re.I) for v in req['conditions'].values()):
            errors.append(f'{param}: unresolved conditions cannot define a complete requirement')
        if req.get('op') in ('le', 'ge') and finite(req.get('value')) and significant_digits(req['value']) > 3:
            errors.append(f"{param}: 下限/上限取 2–3 位有效数字，按保守方向取整（下限向上、上限向下）："
                          f"{req['value']:g} 写成 {conservative(req['value'], req['op']):g}")
        if req.get('basis') not in ('calculation', 'requirement', 'standard', 'model'):
            errors.append(f'{param}: calculation/requirement/standard/model basis required')
        if text(param) and param.startswith('pulse_'):
            conditions = req.get('conditions') if isinstance(req.get('conditions'), dict) else {}
            missing = set(('waveform', 'duration', 'repetition', 'temperature', 'drift')) - set(conditions)
            if missing:
                errors.append(f'{param}: pulse conditions missing {sorted(missing)}')
    needed = entry.get('required_parameters')
    if not isinstance(needed, list) or not needed or any(not text(p) for p in needed):
        errors.append('required_parameters must list the purpose-driven calculation outputs')
    elif entry.get('definition_status') == 'complete' and set(needed) != seen:
        errors.append('complete definition must cover exactly required_parameters')
    if comp is not None:
        from .part_classes import kind_of, part_class, KEY, SAFETY_C, category, MAGNETICS, design_sheet
        kind, conflict = kind_of(comp)
        if conflict or kind != entry.get('kind'):
            errors.append('contract kind contradicts native part kind: ' + str(conflict or kind))
        trigger = ' '.join(str(x) for x in (entry.get('purpose', ''), comp.get('value', ''),
                                            comp.get('fields', {}).get('Specification', '')))
        if (entry.get('definition_status') == 'complete' and re.search(r'pulse|surge|脉冲|浪涌', trigger, re.I)
                and not any(text(p) and p.startswith('pulse_') for p in seen)):
            errors.append('pulse duty needs finite pulse requirement and applicable conditions')
        # Performance contracts never waive actual pin, safety, approval or curve binding.
        if procurement.get('mode') == 'spec' and (kind not in ('resistor', 'capacitor', 'inductor', 'ferrite')
                or part_class(comp) == KEY or (kind == 'capacitor' and category(comp, kind)[0] == SAFETY_C)
                or entry.get('binding_dependencies')):
            errors.append('pin/safety/approval/curve-dependent part needs mpn procurement')
        if procurement.get('mode') == 'design_sheet' and (kind not in MAGNETICS or not design_sheet(comp)):
            errors.append('design_sheet procurement is for a custom magnetic carrying fields.DesignSheet')
    return errors


def spec_procurement(comp):
    """Only R/C performance classification can be waived; safety checks remain earlier."""
    entry = comp.get('performance_contract')
    return bool(isinstance(entry, dict) and not entry_errors(entry)
                and entry.get('kind') in ('resistor', 'capacitor')
                and entry.get('procurement', {}).get('mode') == 'spec'
                and entry.get('definition_status') == 'complete'
                and not entry.get('binding_dependencies'))


MODES = {'spec': '按规格', 'mpn': '按型号', 'design_sheet': '按设计单定做'}


def property_errors(prop, req, quote, what):
    """The quoted value and unit, the conditions and the requirement comparison of one selected property."""
    errors = []
    number = re.escape(f"{prop['value']:g}")
    unit = str(prop.get('unit', ''))
    units = {'ohm': ('ohm', 'Ω'), 'degC': ('degC', '°C')}.get(unit, (unit,))
    pattern = r'(?<![\d.])' + number + r'(?:\.0+)?\s*(?:' + '|'.join(re.escape(u) for u in units) + r')(?![A-Za-z])'
    if not re.search(pattern, quote):
        errors.append(f'{what} value/unit not found together in quoted evidence')
    if prop.get('conditions') != req['conditions'] or prop.get('unit') != req['unit']:
        errors.append(f'{what} units/conditions do not match; qualification remains pending')
    actual_value, limit = prop['value'], req['value']
    if not {'eq': actual_value == limit, 'le': actual_value <= limit, 'ge': actual_value >= limit}[req['op']]:
        errors.append(f'selected {what} does not meet requirement')
    return errors


HEADING = re.compile(r'^(#{1,6})\s+(.*)$')


def sheet_section(body, names):
    """The Markdown section whose heading names the part (its ref or sheet id), up to the next heading of its level
    or higher; None when no heading names it. One 磁件设计单.md holds several parts, so a quote is read in its own."""
    lines, start, level = body.splitlines(), None, 0
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if not m:
            continue
        if start is not None and len(m.group(1)) <= level:
            return '\n'.join(lines[start:i])
        if start is None and any(re.search(r'(?<![A-Za-z0-9])' + re.escape(n) + r'(?![A-Za-z0-9])', m.group(2))
                                 for n in names):
            start, level = i, len(m.group(1))
    return '\n'.join(lines[start:]) if start is not None else None


def sheet_errors(ref, comp, selection, reqs, root, inputs=None):
    """by_design_sheet: each requirement is answered once by the part's own design sheet (fields.DesignSheet), in the
    section headed with its ref or sheet id, with the value and unit quoted, the requirement met under the same
    conditions and the sample acceptance method written. The sheet is a requirement on the vendor, not a guarantee."""
    from .part_classes import design_sheet
    errors = []
    properties = selection.get('properties', [])
    actual = {p.get('parameter'): p for p in properties if isinstance(p, dict)}
    if len(actual) != len(properties) or set(actual) != set(reqs):
        errors.append(f'{ref}: design sheet must answer each required property exactly once')
    sheet = Path(root, design_sheet(comp)).resolve()
    body = document_text(sheet) if sheet.is_file() else None
    section = sheet_section(body, (ref, selection['sheet_id'])) if body is not None else None
    if section is None:
        errors.append(f'{ref}: design sheet {design_sheet(comp)} has no section headed with {ref} or {selection["sheet_id"]}')
    for param, req in reqs.items():
        prop = actual.get(param, {})
        if prop.get('basis') != 'design_sheet' or not finite(prop.get('value')) or not text(prop.get('acceptance')):
            errors.append(f'{ref}/{param}: design sheet property needs basis design_sheet, a finite value and its acceptance test')
            continue
        source = prop.get('source') or {}
        errors += [f'{ref}/{param}: {e}' for e in source_errors(source, root, inputs=inputs)]
        if not isinstance(source, dict) or source.get('kind') != 'design_sheet' or not text(source.get('quote')) \
                or Path(root, str(source.get('path', ''))).resolve() != sheet:
            errors.append(f'{ref}/{param}: design sheet property cites the part\'s fields.DesignSheet with kind design_sheet and a quote')
            continue
        if section is not None and compact(source['quote']) not in compact(section):
            errors.append(f'{ref}/{param}: quote not found in the {ref} section of the design sheet')
        if re.search(r'\btypical\b|\btyp\.|典型|工程估计', source['quote'], re.I):
            errors.append(f'{ref}/{param}: a typical value is no acceptance limit')
        errors += [f'{ref}/{param}: {e}' for e in property_errors(prop, req, source['quote'], 'design sheet value')]
    return errors


def record_errors(record, intent, root, inputs=None):
    errors, pending = [], []
    if not isinstance(record, dict) or record.get('schema_version') != VERSION:
        return ['component-requirements schema_version must be 1'], []
    comps = {c['ref']: c for c in intent.get('components', [])}
    entries = record.get('components', [])
    if not isinstance(entries, list):
        return ['components must be a list'], []
    by_ref = {}
    for entry in entries:
        ref = entry.get('ref') if isinstance(entry, dict) else None
        if ref in by_ref or ref not in comps:
            errors.append(f'{ref}: duplicate or unknown requirement reference')
            continue
        by_ref[ref] = entry
        structural = entry_errors(entry, comps[ref])
        errors += [f'{ref}: {e}' for e in structural]
        if structural:
            continue
        if entry['definition_status'] != 'complete':
            pending.append(f'{ref}：性能计算未完成')
        reqs = {r['parameter']: r for r in entry.get('requirements', [])}
        for req in reqs.values():
            errors += [f"{ref}/{req['parameter']}: {e}" for e in source_errors(req.get('source'), root, inputs=inputs)]
            if req['basis'] == 'model':
                pending.append(f"{ref}/{req['parameter']}：依赖工程估计")
        selection = entry['selection']
        if selection['status'] == BOM_SPEC:
            pass  # closed by the exported BOM/XML in audit()
        elif selection['status'] not in CLOSED:
            pending.append(f"{ref}：{SELECTIONS[selection['status']]}，采购方式为" +
                           MODES[entry['procurement']['mode']])
        elif selection['status'] == 'by_design_sheet':
            errors += sheet_errors(ref, comps[ref], selection, reqs, root, inputs)
        else:
            properties = selection.get('properties', [])
            actual = {p.get('parameter'): p for p in properties if isinstance(p, dict)}
            if len(actual) != len(properties) or set(actual) != set(reqs):
                errors.append(f'{ref}: qualified part must cover each required property exactly once')
            for param, req in reqs.items():
                prop = actual.get(param, {})
                if prop.get('basis') != 'guaranteed' or not finite(prop.get('value')):
                    errors.append(f'{ref}/{param}: typical/model/missing property cannot qualify a part')
                    continue
                errors += [f'{ref}/{param}: {e}' for e in source_errors(prop.get('source'), root, guaranteed=True, inputs=inputs)]
                source = prop.get('source') or {}
                if selection['status'] == 'by_spec' and (not isinstance(source, dict) or source.get('kind') != 'controlled_standard'):
                    errors.append(f'{ref}/{param}: by_spec qualification needs controlled standard guarantees')
                quote = source.get('quote', '') if isinstance(source, dict) else ''
                errors += [f'{ref}/{param}: {e}' for e in property_errors(prop, req, quote, 'guarantee')]
    screened = set()
    for row in record.get('screening', []):
        if not isinstance(row, dict) or row.get('decision') not in ('standard', 'contract') or not text(row.get('reason')):
            errors.append('screening needs refs, standard/contract decision and engineering reason')
            continue
        refs = row.get('refs', [])
        if not isinstance(refs, list) or not refs:
            errors.append('screening refs must be a nonempty list')
            continue
        for ref in refs:
            if ref in screened or ref not in comps:
                errors.append(f'{ref}: duplicate/unknown screening reference')
            screened.add(ref)
            if (ref in by_ref) != (row['decision'] == 'contract'):
                errors.append(f'{ref}: screening decision contradicts performance contract')
            comp = comps.get(ref, {})
            trigger = ' '.join(str(x) for x in (comp.get('value', ''), comp.get('fields', {}).get('Specification', '')))
            if row['decision'] == 'standard' and re.search(r'pulse|surge|脉冲|浪涌', trigger, re.I):
                errors.append(f'{ref}: pulse duty cannot be screened out without a performance contract')
    if screened != set(comps):
        errors.append('purpose screening must cover every component: ' + str(sorted(set(comps) - screened)))
    return errors, pending


def spec_gaps(entry, spec):
    """The requirements whose parameter, direction and value a RequirementSpec text does not carry."""
    return [requirement_label(r) for r in entry.get('requirements', [])
            if compact(f"{r['parameter']}{OPS[r['op']]}{r['value']:g} {r['unit']}") not in compact(spec)]


def requirement_hints(record, intent):
    """Requirements that constrain nothing or repeat a template, written as review hints, not errors."""
    comps = {c['ref']: c for c in intent.get('components', [])}
    loose, shared, share = [], {}, voltage_share()
    for entry in record.get('components', []):
        for req in entry.get('requirements', []):
            if (entry.get('kind') == 'resistor' and req.get('parameter') == 'working_voltage' and req.get('op') == 'ge'
                    and finite(req.get('value')) and req.get('unit') == 'V'):
                m = RESISTOR_PACKAGE.match(str(comps.get(entry['ref'], {}).get('footprint') or ''))
                floor = RESISTOR_VOLTAGE_FLOORS[m.group(1) if m else ASSUMED_PACKAGE]
                if req['value'] <= floor * share:
                    loose.append(f"{entry['ref']}（{req['value']:g} V ≤ {floor * share:g} V）")
            if str(req.get('parameter', '')).startswith('pulse_') or req.get('parameter') == 'drift':
                for key, value in (req.get('conditions') or {}).items():
                    if key not in TEMPLATE_CONDITIONS:
                        continue   # a shared duration or temperature is a plain condition, not a copied sentence
                    shared.setdefault((key, ' '.join(str(value).split())), set()).add(entry['ref'])
    hints = []
    if loose:
        hints.append('%d 颗电阻的工作电压要求不超过封装最弱常用件耐压 × RES-SMD-V %g%%，不起约束作用，可以不写：%s'
                     % (len(loose), share * 100, '、'.join(loose[:6]) + ('等' if len(loose) > 6 else '')))
    for (key, value), refs in sorted(shared.items()):
        if len(refs) >= BOILERPLATE_REFS:
            hints.append('%d 颗器件的脉冲/漂移条件“%s”是同一句（%s）：按各自工况写，或确认确实相同'
                         % (len(refs), value[:40], CONDITIONS.get(key, key)))
    return hints


def project(intent, record, root, inputs=None):
    """Explicit preparation API. No checking path calls this function to repair outputs."""
    errors, _ = record_errors(record, intent, root, inputs)
    if errors:
        raise ValueError('; '.join(errors))
    result = copy.deepcopy(intent)
    result['component_requirements_version'] = VERSION
    sha = digest(record)
    entries = {e['ref']: e for e in record['components']}
    for comp in result['components']:
        if comp['ref'] not in entries:
            continue
        entry = entries[comp['ref']]
        comp['performance_contract'] = copy.deepcopy(entry)
        nominal = nominal_value(entry)
        if nominal is not None:
            comp['value'] = nominal
        comp.setdefault('fields', {}).update(fields_for(entry, sha))
        selection = entry['selection']
        if selection['status'] == 'qualified':
            comp['mpn'] = selection['mpn']
            if selection.get('datasheet'):
                comp['datasheet'] = selection['datasheet']
        elif selection['status'] == 'by_design_sheet':
            comp['mpn'] = selection['sheet_id']    # the sheet number is the order identity (part-roles.md)
            from .part_classes import design_sheet
            comp['datasheet'] = design_sheet(comp)
        else:
            comp.pop('mpn', None)  # candidate identity remains in the contract, never the orderable MPN
            comp.pop('datasheet', None)
    return result


def bom_rows(intent):
    """Canonical BOM fields; callers can append costing/supplier columns by Reference."""
    from .part_classes import kind_of, category
    rows = []
    for c in intent['components']:
        kind, conflict = kind_of(c)
        cat, cat_error = category(c, kind)
        if conflict or cat_error:
            raise ValueError(f"{c['ref']}: {conflict or cat_error}")
        rows.append(dict(Reference=c['ref'], Value=c['value'], MPN=c.get('mpn', ''),
                         Datasheet=c.get('datasheet', ''), Footprint=c.get('footprint', ''),
                         Kind=kind or '', Category=cat or '',
                         **{k: c.get('fields', {}).get(k, '') for k in FIELDS}))
    return rows


def write_bom(intent, path):
    rows = bom_rows(intent)
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else ['Reference', 'Value', 'MPN', *FIELDS])
    writer.writeheader()
    writer.writerows(rows)
    Path(path).write_text(stream.getvalue(), encoding='utf-8-sig')


def audit(intent, record, root, bom=None, xml=None, schematic=None, pdf=None, project_name=None, inputs=None):
    """Recompute from source and actual artifacts; missing native evidence is never PASS."""
    if record is None:
        required = intent.get('component_requirements_version') or any(
            c.get('performance_contract') or c.get('fields', {}).get('RequirementsSHA256')
            for c in intent.get('components', []))
        return {'status': 'FAIL' if required else 'NOT_CHECKED',
                'errors': ['component-requirements.json missing'], 'pending': [], 'native': 'NOT_CHECKED'}
    errors, pending = record_errors(record, intent, root, inputs)
    if intent.get('component_requirements_version') != VERSION:
        errors.append('IR must opt into component_requirements_version 1')
    if errors:
        return {'status': 'FAIL', 'errors': errors, 'pending': pending, 'native': 'NOT_CHECKED'}
    sha = digest(record)
    entries = {e['ref']: e for e in record['components']}
    comps = {c['ref']: c for c in intent['components']}
    expected = {}
    for ref, entry in entries.items():
        comp = comps[ref]
        fields = fields_for(entry, sha)
        expected[ref] = fields
        if comp.get('performance_contract') != entry:
            errors.append(f'{ref}: stale/missing projected performance contract')
        nominal = nominal_value(entry)
        if nominal is not None and comp.get('value') != nominal:
            errors.append(f'{ref}: nominal Value differs from exact performance requirement')
        for k, v in fields.items():
            if str(comp.get('fields', {}).get(k, '')) != v:
                errors.append(f'{ref}: stale IR field {k}')
        selected = entry['selection']
        expected_mpn = {'qualified': selected.get('mpn', ''), 'by_design_sheet': selected.get('sheet_id', '')}.get(
            selected['status'], '')
        if (comp.get('mpn') or '') != expected_mpn:
            errors.append(f'{ref}: candidate is not a qualified BOM MPN, or selected MPN mismatch')
        # Legacy ambiguous tolerance columns must be resolved, not copied with a default.
        if any(k.lower() in ('tolerance', '公差', '精度') for k in comp.get('fields', {})):
            errors.append(f'{ref}: ambiguous tolerance field; use RequirementSpec and SelectedSpec')
        if selected['status'] == 'qualified' and entry['kind'] == 'resistor':
            from .part_classes import tolerance
            actual = {p['parameter']: p['value'] for p in selected.get('properties', [])}
            label = tolerance(comp.get('value', ''))
            if label is not None and 'tolerance' in actual and label != actual['tolerance']:
                errors.append(f'{ref}: value tolerance disagrees with selected part')
    native, bom_checked = 'NOT_CHECKED', False
    if any(v is not None for v in (bom, xml, schematic, pdf)):
        native = 'CHECKED'
        if not all(v is not None and Path(v).is_file() for v in (bom, xml, schematic, pdf)):
            pending.append('缺少本次BOM、XML、原理图或PDF，图面性能未核实')
            native = 'INSUFFICIENT'
        else:
            try:
                rows = list(csv.DictReader(Path(bom).read_text(encoding='utf-8-sig').splitlines()))
                refs = [r.get('Reference') for r in rows]
                if len(refs) != len(set(refs)) or set(refs) != set(comps):
                    errors.append('BOM must cover each component exactly once')
                by_ref = {r.get('Reference'): r for r in rows}
                for canonical in bom_rows(intent):
                    ref = canonical['Reference']
                    for key, value in canonical.items():
                        if by_ref.get(ref, {}).get(key, '') != value:
                            errors.append(f'{ref}: BOM {key} differs from contract/IR')
                tree = ET.parse(xml)
                xcomps = tree.findall('.//components/comp')
                xrefs = [c.get('ref') for c in xcomps]
                if len(xrefs) != len(set(xrefs)):
                    errors.append('duplicate native XML component references')
                by_xml = {c.get('ref'): c for c in xcomps}
                for ref, fields in expected.items():
                    if any(k.lower() in ('tolerance', '公差', '精度') and text(v)
                           for k, v in by_ref.get(ref, {}).items() if isinstance(k, str)):
                        errors.append(f'{ref}: BOM ambiguous tolerance field; separate requirement and selected values')
                    node = by_xml.get(ref)
                    xf = {n.get('name'): n.text or '' for n in node.findall('./fields/field')} if node is not None else {}
                    for k, v in dict(MPN=comps[ref].get('mpn', ''), **fields).items():
                        if xf.get(k, '') != v:
                            errors.append(f'{ref}: native XML {k} differs from contract')
                    if entries[ref]['selection']['status'] == BOM_SPEC:
                        for where, spec in (('BOM', by_ref.get(ref, {}).get('RequirementSpec', '')),
                                            ('XML', xf.get('RequirementSpec', ''))):
                            errors += [f'{ref}: {where} 规格没写出要求“{label}”' for label in spec_gaps(entries[ref], spec)]
                bom_checked = True
                errors2, gaps = drawing_errors(entries, expected, schematic, pdf, project_name)
                errors += errors2
                pending += gaps
                if gaps:
                    native = 'INSUFFICIENT'
            except (OSError, ValueError, ET.ParseError) as exc:
                errors.append('native comparison could not read artifacts: ' + str(exc))
    # Sample acceptance against a design sheet is the vendor's and the pilot run's, outside ASG's self-check: listed, not
    # pending (user 2026-10-28: 按 A 实施).
    acceptance = [f"{ref}：样件按设计单 {e['selection']['sheet_id']} 验收" for ref, e in entries.items()
                  if e['selection']['status'] == 'by_design_sheet']
    # Finding a part to the BOM spec and checking its guarantees is procurement's: handed over, not pending.
    procurement = sorted(ref for ref, e in entries.items() if e['selection']['status'] == BOM_SPEC)
    if procurement and not bom_checked:
        pending.append(f'{len(procurement)} 颗按 BOM 规格采购的器件，规格未在本次导出的 BOM/XML 核实')
    return {'schema_version': VERSION, 'status': 'FAIL' if errors else 'INCOMPLETE' if pending else 'PASS',
            'errors': errors, 'pending': pending, 'acceptance': acceptance, 'procurement': procurement,
            'hints': requirement_hints(record, intent), 'native': native, 'record_sha256': sha,
            'definition': {r: e['definition_status'] for r, e in entries.items()},
            'selection': {r: e['selection']['status'] for r, e in entries.items()}}


def drawing_errors(entries, expected, schematic, pdf, project_name=None):
    from .native_hierarchy import NativeHierarchy
    from .sexpr import all_nodes, first
    hierarchy = NativeHierarchy(schematic, project=project_name)
    errors = [str(e) for e in hierarchy.errors]
    gaps = list(hierarchy.coverage_gaps)
    body = document_text(Path(pdf))
    if body is None:
        gaps.append('PDF 文字读不出：图面性能标注要人工对照原生图核实')
    pdf_pages = body.split('\f') if body is not None else []
    found = set()
    for page in hierarchy.pages:
        tree = hierarchy.tree_for(page)
        annotations = [str(n[1]) for n in all_nodes(tree, 'text') if len(n) > 1]
        visible = []
        for sym in all_nodes(tree, 'symbol'):
            ctx = hierarchy.symbol_context(page, sym)
            ref = ctx.get('reference') if ctx else None
            if ref not in entries:
                continue
            found.add(ref)
            props = [p for p in all_nodes(sym, 'property') if p[1] == 'Performance']
            if len(props) != 1 or str(props[0][2]) != expected[ref]['Performance']:
                errors.append(f'{ref}: native visible Performance property missing/stale')
                continue
            effects = first(props[0], 'effects')
            if effects is None or all_nodes(effects, 'hide'):
                errors.append(f'{ref}: hidden property is not visible performance information')
                continue
            visible.append(expected[ref]['Performance'])
            if entries[ref]['display'] == 'note':
                note = compact('\n'.join(annotations))
                for line in note_lines(entries[ref]):
                    if compact(line) not in note:
                        errors.append(f'{ref}: same-page technical note missing/stale: {line}')
                    visible.append(line)
        number = str(page.get('page') or '')
        if body is None:
            continue  # native visibility/notes above remain checked without PDF text
        if not number.isdigit() or not 1 <= int(number) <= len(pdf_pages):
            gaps.append(f"{page['path']}：原生图页对不上 PDF 页")
        else:
            rendered = compact(pdf_pages[int(number) - 1])
            for label in visible:
                if compact(label) not in rendered:
                    gaps.append(f"{page['path']}：PDF 第 {number} 页没找到图面性能标注“{label}”")
    if found != set(entries):
        errors.append('performance references missing from active native hierarchy: ' + str(sorted(set(entries) - found)))
    return errors, gaps


def artifact_audit(root, intent, schematic=None, pdf=None, xml=None, bom=None, project_name=None, inputs=None):
    root = Path(root)
    path = root / 'record' / 'component-requirements.json'
    try:
        record = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None
        return audit(intent, record, root, schematic=schematic, pdf=pdf, xml=xml, bom=bom,
                     project_name=project_name, inputs=inputs)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {'status': 'FAIL', 'errors': ['invalid component-requirements record: ' + str(exc)], 'pending': [], 'native': 'NOT_CHECKED'}


def package_audit(root, intent):
    root = Path(root)
    folder = root / '原理图'
    config_path = root / 'record' / 'deliver.json'
    native = None
    if config_path.is_file():
        try:
            native = root / json.loads(config_path.read_text(encoding='utf-8'))['root']
        except (ValueError, KeyError):
            pass
    if native is None:
        candidates = sorted(folder.glob('*.kicad_sch'))
        native = candidates[0] if len(candidates) == 1 else folder / 'unresolved-root.kicad_sch'
    return artifact_audit(root, intent, schematic=native, xml=folder / 'netlist.xml',
                          pdf=folder / 'schematic.pdf', bom=folder / 'BOM.csv')
