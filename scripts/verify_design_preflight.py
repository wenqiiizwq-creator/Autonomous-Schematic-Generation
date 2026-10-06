#!/usr/bin/env python3
"""Check explicit change impact and current-design artifact bindings before delivery.

This checks declared coverage and arithmetic; it cannot discover every electrical
coupling or read unstructured prose semantically. Review the impact declaration.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from design_preflight import validate_calculations, text, evidence

DOMAINS = ('supply', 'drive', 'voltage_stress', 'current_power', 'protection', 'temperature', 'documentation')


def contract_objects(contract):
    refs = set(contract.get('remove_components', []))
    refs.update(contract.get('add_components', {}))
    refs.update(contract.get('component_changes', {}))
    for replacement in contract.get('replace_partitions', []):
        for side in ('before', 'after'):
            for group in replacement.get(side, []):
                refs.update(pin.rsplit('.', 1)[0] for pin in group)
    return refs


def read_binding(path, binding):
    kind = binding.get('format')
    if kind == 'json':
        value = json.loads(path.read_text())
        pointer = binding.get('pointer')
        if not isinstance(pointer, str) or not pointer.startswith('/'):
            raise ValueError('JSON binding requires a non-root pointer')
        for token in pointer[1:].split('/'):
            token = token.replace('~1', '/').replace('~0', '~')
            value = value[int(token)] if isinstance(value, list) else value[token]
        return value
    if kind == 'csv':
        with path.open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        selected = [r for r in rows if r.get(binding['key_column']) == binding['key']]
        if len(selected) != 1:
            raise ValueError('CSV binding must identify exactly one row')
        return selected[0][binding['column']]
    if kind == 'text':
        pattern = binding.get('pattern')
        if not text(pattern):
            raise ValueError('text binding needs a pattern with one capture group')
        compiled = re.compile(pattern, re.MULTILINE)
        matches = list(compiled.finditer(path.read_text()))
        if compiled.groups != 1 or len(matches) != 1:
            raise ValueError('text binding must match exactly once with one capture group')
        return matches[0].group(1)
    raise ValueError('binding format must be text/csv/json')


def verify_preflight(manifest, root, contract=None, artifacts=True):
    errors, pending = [], []
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
        return {'status': 'FAIL', 'errors': ['preflight schema_version must be 1']}
    if not text(manifest.get('revision')):
        errors.append('revision required')
    changed = manifest.get('changed_objects')
    if not isinstance(changed, list) or not changed or not all(text(x) for x in changed) or len(set(changed)) != len(changed):
        errors.append('changed_objects must be nonempty unique strings'); changed = []
    if contract is not None:
        if manifest.get('baseline_sha256') != contract.get('baseline_sha256') or not text(manifest.get('baseline_sha256')):
            errors.append('preflight and design contract must bind the same baseline SHA256')
        try:
            missing = contract_objects(contract) - set(changed)
            if missing:
                errors.append('contract changes missing from preflight: ' + ', '.join(sorted(missing)))
        except (TypeError, AttributeError):
            errors.append('invalid design contract change objects')
    calculation_errors, calculations = validate_calculations(manifest.get('calculations'))
    errors.extend(calculation_errors)
    impacts = manifest.get('impacts')
    if not isinstance(impacts, list):
        errors.append('impacts must be an array'); impacts = []
    covered = set()
    for impact in impacts:
        if not isinstance(impact, dict) or impact.get('trigger') not in changed:
            errors.append('impact needs a declared changed trigger'); continue
        trigger = impact['trigger']
        if trigger in covered:
            errors.append('duplicate impact trigger: ' + trigger)
        covered.add(trigger)
        affected = impact.get('affected_objects')
        if not isinstance(affected, list) or not affected or not all(text(x) for x in affected):
            errors.append(trigger + ': affected_objects required (include electrically dependent unchanged parts)')
        checks = impact.get('checks')
        if not isinstance(checks, dict) or set(checks) != set(DOMAINS):
            errors.append(trigger + ': classify all impact domains: ' + '/'.join(DOMAINS)); continue
        for domain, check in checks.items():
            label = trigger + '/' + domain
            if not isinstance(check, dict) or not text(check.get('reason')):
                errors.append(label + ': reason required'); continue
            disposition = check.get('disposition')
            if disposition == 'NOT_APPLICABLE':
                if not evidence(check.get('evidence')):
                    errors.append(label + ': exclusion requires evidence')
            elif disposition == 'OPEN':
                if not text(check.get('closure')):
                    errors.append(label + ': open impact needs closure method')
                pending.append(label)
            elif disposition == 'CALCULATED':
                links = check.get('calculation_ids')
                if not isinstance(links, list) or not links or not all(text(k) and k in calculations for k in links):
                    errors.append(label + ': link known calculations'); continue
                if any(calculations[k]['status'] != 'SUPPORTED' for k in links):
                    pending.append(label)
            elif disposition == 'DOCUMENTED' and domain == 'documentation':
                if not evidence(check.get('evidence')):
                    errors.append(label + ': documentation needs current source')
            else:
                errors.append(label + ': invalid disposition')
    if set(changed) != covered:
        errors.append('every changed object needs impact coverage')
    facts, bindings = manifest.get('facts'), manifest.get('artifact_bindings')
    if not isinstance(facts, dict) or not facts:
        errors.append('facts must be a nonempty current-design map'); facts = {}
    for key, fact in facts.items():
        if not isinstance(fact, dict) or not text(fact.get('value')) or not evidence(fact.get('evidence')):
            errors.append(key + ': fact requires canonical string value and evidence')
    if not isinstance(bindings, list) or not bindings:
        errors.append('artifact_bindings must cover current facts'); bindings = []
    bound, hashes = set(), {}
    for binding in bindings:
        if not isinstance(binding, dict) or not text(binding.get('fact')) or binding['fact'] not in facts or not text(binding.get('path')):
            errors.append('artifact binding requires known fact and path'); continue
        bound.add(binding['fact'])
        if not artifacts:
            continue
        path = Path(root) / binding['path']
        try:
            hashes[str(path.resolve())] = hashlib.sha256(path.read_bytes()).hexdigest()
            actual = read_binding(path, binding)
            if str(actual) != facts[binding['fact']].get('value'):
                errors.append(binding['path'] + ': stale/conflicting ' + binding['fact'] + ': ' + repr(actual))
        except (OSError, ValueError, TypeError, KeyError, IndexError, re.error) as exc:
            errors.append(binding['path'] + ': ' + str(exc))
    if set(facts) != bound:
        errors.append('facts without artifact bindings: ' + ', '.join(sorted(set(facts) - bound)))
    return {'status': 'FAIL' if errors else ('CONDITIONAL' if pending else 'PASS'),
            'phase': 'delivery' if artifacts else 'before_generation', 'errors': errors,
            'open_impacts': sorted(set(pending)), 'calculations': calculations, 'artifact_sha256': hashes,
            'scope': 'Declared impact, arithmetic and artifact consistency only; not electrical approval.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--contract')
    parser.add_argument('--root', help='artifact root, defaults to manifest parent')
    parser.add_argument('--before-generation', action='store_true', help='validate impact before output artifacts exist')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    target = Path(args.out)
    if target.exists() or target.is_symlink():
        parser.error('report exists; choose a fresh output')
    try:
        source = Path(args.manifest)
        result = verify_preflight(json.loads(source.read_text()), args.root or source.parent,
                                  json.loads(Path(args.contract).read_text()) if args.contract else None,
                                  artifacts=not args.before_generation)
    except (ValueError, OSError, TypeError) as exc:
        result = {'status': 'FAIL', 'errors': [str(exc)]}
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'errors': result.get('errors', [])}, ensure_ascii=False))
    return {'PASS': 0, 'CONDITIONAL': 2, 'FAIL': 1}[result['status']]


if __name__ == '__main__':
    raise SystemExit(main())
