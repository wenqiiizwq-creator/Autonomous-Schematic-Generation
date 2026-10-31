#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""共用规范规则库（G01–G09）：校验、汇编、按适用条件选出规则、统计覆盖。

本文件与 references/guideline-rules.json、references/guideline-rules.md 在 ASG 与 SR 两个技能里是同一份字节，
改动时两边一起改（SR 的 test_guideline_rules.py 在两边都装了时逐字节比对）。只用标准库，不导入任一技能的模块。

    python3 guideline_rules.py check BUNDLE                       校验汇编文件
    python3 guideline_rules.py build --from DIR --base BUNDLE --library-version V --out PATH
                                                                  从 DIR 下各 G0x_规则登记.json 汇编（词表取自 BASE）
    python3 guideline_rules.py select BUNDLE [--baseline B] [--circuit-type T ...] [--device-kind K ...]
                                                                  列出适用规则
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

BUNDLE_SCHEMA_VERSION = 1
BUNDLE_PATH = Path(__file__).resolve().parent.parent / 'references' / 'guideline-rules.json'
RULE_ID = re.compile(r'^G0[1-9]-\d{3}$')
STATUSES = ('draft', 'active', 'retired')
NATURES = ('shall', 'should', 'method', 'project')
STAGES = ('schematic', 'pcb', 'simulation', 'prototype', 'production')
TRIGGERS = ('baselines', 'circuit_types', 'device_kinds')
APPLIES_KEYS = set(TRIGGERS) | {'board', 'text'}
RELATION_KEYS = ('related', 'primary', 'reuses', 'conflicts')
RULE_KEYS = {'id', 'title', 'spec', 'version', 'status', 'nature', 'applies_when', 'not_applicable', 'tailoring',
             'inputs', 'asg_action', 'sr_check', 'source', 'relations', 'closing_stage'}
SOURCE_KEYS = ('document', 'edition', 'clause', 'page')
PREVIEW_WORDS = ('公开预览', '非全文', 'preview')   # 公开预览不能作规则依据


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def content_sha256(rules):
    return hashlib.sha256(json.dumps(rules, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def load(path=BUNDLE_PATH):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def rule_errors(rule, vocabulary, default_baseline):
    if not isinstance(rule, dict):
        return ['rule is not an object']
    rid = rule.get('id')
    label = str(rid)
    errors = []
    if not (isinstance(rid, str) and RULE_ID.match(rid)):
        errors.append('%s: id must look like G03-005' % label)
    elif rule.get('spec') != rid[:3]:
        errors.append('%s: spec must be %s' % (label, rid[:3]))
    extra = set(rule) - RULE_KEYS
    if extra:
        errors.append('%s: unknown fields %s' % (label, sorted(extra)))
    for key in ('title', 'version', 'asg_action', 'sr_check'):
        if not _text(rule.get(key)):
            errors.append('%s: %s is required' % (label, key))
    for key in ('not_applicable', 'tailoring'):
        if key in rule and not isinstance(rule[key], str):
            errors.append('%s: %s must be text' % (label, key))
    for key, allowed in (('status', STATUSES), ('nature', NATURES), ('closing_stage', STAGES)):
        if rule.get(key) not in allowed:
            errors.append('%s: %s must be one of %s' % (label, key, '/'.join(allowed)))
    if not (isinstance(rule.get('inputs', []), list) and all(_text(x) for x in rule.get('inputs', []))):
        errors.append('%s: inputs must be a list of text' % label)
    when = rule.get('applies_when')
    if not isinstance(when, dict):
        errors.append('%s: applies_when is required' % label)
    else:
        if set(when) - APPLIES_KEYS:
            errors.append('%s: applies_when has unknown keys %s' % (label, sorted(set(when) - APPLIES_KEYS)))
        for key in TRIGGERS:
            values = when.get(key, [])
            if not isinstance(values, list):
                errors.append('%s: applies_when.%s must be a list' % (label, key))
                continue
            unknown = [v for v in values if v not in vocabulary.get(key, ())]
            if unknown:
                errors.append('%s: applies_when.%s not in vocabulary: %s' % (label, key, unknown))
        if when.get('board') not in (None, True, False):
            errors.append('%s: applies_when.board must be true or false' % label)
        if not (when.get('board') or when.get('circuit_types') or when.get('device_kinds')):
            errors.append('%s: applies_when needs board: true or a circuit type or device kind' % label)
        if rule.get('nature') == 'project' and (not when.get('baselines') or default_baseline in when['baselines']):
            errors.append('%s: a project-specific rule names its baselines and not the default %s'
                          % (label, default_baseline))
    sources = rule.get('source')
    if not (isinstance(sources, list) and sources):
        errors.append('%s: source needs at least one entry' % label)
    else:
        for item in sources:
            if not (isinstance(item, dict) and all(_text(str(item.get(k) or '')) for k in SOURCE_KEYS)):
                errors.append('%s: each source names %s' % (label, '/'.join(SOURCE_KEYS)))
            elif any(w in str(item['document']).lower() for w in PREVIEW_WORDS):
                errors.append('%s: a public preview is not a source: %s' % (label, item['document']))
    relations = rule.get('relations', {})
    if not (isinstance(relations, dict) and set(relations) <= set(RELATION_KEYS)
            and all(isinstance(v, list) for v in relations.values())):
        errors.append('%s: relations holds lists under %s' % (label, '/'.join(RELATION_KEYS)))
    return errors


def bundle_errors(bundle):
    if not isinstance(bundle, dict):
        return ['bundle is not an object']
    errors = []
    if bundle.get('schema_version') != BUNDLE_SCHEMA_VERSION:
        errors.append('schema_version must be %d' % BUNDLE_SCHEMA_VERSION)
    if not _text(bundle.get('library_version')):
        errors.append('library_version is required')
    vocabulary = bundle.get('vocabulary')
    if not (isinstance(vocabulary, dict) and all(isinstance(vocabulary.get(k), list) for k in TRIGGERS)):
        return errors + ['vocabulary lists %s' % '/'.join(TRIGGERS)]
    default = bundle.get('default_baseline')
    if default not in vocabulary['baselines']:
        errors.append('default_baseline must be in vocabulary.baselines')
    rules = bundle.get('rules')
    if not isinstance(rules, list):
        return errors + ['rules must be a list']
    ids = [r.get('id') for r in rules if isinstance(r, dict)]
    for rid in sorted({i for i in ids if ids.count(i) > 1}, key=str):
        errors.append('%s: duplicate id' % rid)
    if ids != sorted(ids, key=str):
        errors.append('rules must be sorted by id')
    known = set(ids)
    for rule in rules:
        errors.extend(rule_errors(rule, vocabulary, default))
        for key, targets in (rule.get('relations') or {}).items() if isinstance(rule, dict) else ():
            for target in targets if isinstance(targets, list) else ():
                if target not in known:
                    errors.append('%s: relations.%s names unknown rule %s' % (rule.get('id'), key, target))
    if bundle.get('content_sha256') != content_sha256(rules):
        errors.append('content_sha256 does not match the rules')
    return errors


def select(bundle, baseline=None, circuit_types=(), device_kinds=()):
    """Active rules whose conditions hold: the baseline matches (an empty list is every baseline) and the rule is
    board-wide or names one of the circuit types or device kinds present."""
    baseline = baseline or bundle['default_baseline']
    circuits, kinds = set(circuit_types), set(device_kinds)
    out = []
    for rule in bundle['rules']:
        when = rule['applies_when']
        if rule['status'] != 'active' or (when.get('baselines') and baseline not in when['baselines']):
            continue
        if when.get('board') or circuits & set(when.get('circuit_types', ())) or kinds & set(when.get('device_kinds', ())):
            out.append(rule)
    return out


def scope_errors(scope, bundle):
    """A design's declared scope (ASG design-closure.json guideline_scope): the library version it was written
    against, its baseline and the circuit types and device kinds it has, in the bundle's vocabulary, and the rules
    it holds not applicable with a reason."""
    if not isinstance(scope, dict):
        return ['scope is not an object']
    errors = []
    extra = set(scope) - {'library_version', 'baseline', 'circuit_types', 'device_kinds', 'not_applicable'}
    if extra:
        errors.append('scope has unknown fields %s' % sorted(extra))
    if scope.get('library_version') != bundle['library_version']:
        errors.append('scope library_version %s is not the installed %s'
                      % (scope.get('library_version'), bundle['library_version']))
    vocabulary = bundle['vocabulary']
    if scope.get('baseline') not in vocabulary['baselines']:
        errors.append('scope baseline must be one of %s' % '/'.join(vocabulary['baselines']))
    for key in ('circuit_types', 'device_kinds'):
        values = scope.get(key)
        if not isinstance(values, list):
            errors.append('scope %s must be a list' % key)
        elif [v for v in values if v not in vocabulary[key]]:
            errors.append('scope %s not in vocabulary: %s' % (key, [v for v in values if v not in vocabulary[key]]))
    known = {r['id'] for r in bundle['rules']}
    for item in scope.get('not_applicable', []):
        if not (isinstance(item, dict) and item.get('id') in known and _text(item.get('reason'))):
            errors.append('scope not_applicable entries are {id, reason} naming a rule in the bundle')
    return errors


def coverage(bundle, applicable, cited, not_applicable=None):
    """cited: {rule id: [where it is cited]}; not_applicable: {rule id: reason}. An applicable rule is covered when
    cited or held not applicable with a reason; the rest are uncovered. Rules closing after the schematic are listed
    as downstream whether covered or not."""
    not_applicable = not_applicable or {}
    known = {r['id'] for r in bundle['rules']}
    ids = [r['id'] for r in applicable]
    return {
        'library_version': bundle['library_version'],
        'content_sha256': bundle['content_sha256'],
        'applicable': ids,
        'covered': {i: sorted(cited[i]) for i in ids if cited.get(i)},
        'not_applicable': {i: not_applicable[i] for i in ids if i in not_applicable and not cited.get(i)},
        'uncovered': [i for i in ids if not cited.get(i) and i not in not_applicable],
        'downstream': [r['id'] for r in applicable if r['closing_stage'] != 'schematic'],
        'unknown_cited': sorted(i for i in cited if i not in known),
    }


def build(registry_dir, base, library_version):
    """Gather the rules of every G0x_规则登记.json under registry_dir into one bundle; the vocabulary and default
    baseline come from the installed bundle (base)."""
    rules, specs = [], {}
    for path in sorted(Path(registry_dir).rglob('G0*_规则登记.json')):
        registry = json.loads(path.read_text(encoding='utf-8'))
        specs[registry['spec']] = registry['version']
        rules.extend(registry['rules'])
    rules.sort(key=lambda r: str(r.get('id')))
    return {'schema_version': BUNDLE_SCHEMA_VERSION, 'library_version': library_version,
            'default_baseline': base['default_baseline'], 'vocabulary': base['vocabulary'], 'specs': specs,
            'content_sha256': content_sha256(rules), 'rules': rules}


def dump(bundle):
    return json.dumps(bundle, ensure_ascii=False, indent=2) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('check')
    check.add_argument('bundle', nargs='?', default=str(BUNDLE_PATH))
    make = sub.add_parser('build')
    make.add_argument('--from', dest='source', required=True)
    make.add_argument('--base', default=str(BUNDLE_PATH))
    make.add_argument('--library-version', required=True)
    make.add_argument('--out', required=True)
    pick = sub.add_parser('select')
    pick.add_argument('bundle', nargs='?', default=str(BUNDLE_PATH))
    pick.add_argument('--baseline')
    pick.add_argument('--circuit-type', action='append', default=[])
    pick.add_argument('--device-kind', action='append', default=[])
    args = parser.parse_args(argv)
    if args.command == 'build':
        bundle = build(args.source, load(args.base), args.library_version)
        errors = bundle_errors(bundle)
        if not errors:
            Path(args.out).write_text(dump(bundle), encoding='utf-8')
    else:
        bundle = load(args.bundle)
        errors = bundle_errors(bundle)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    if args.command == 'select':
        for rule in select(bundle, args.baseline, args.circuit_type, args.device_kind):
            print('%s  %s  [%s]' % (rule['id'], rule['title'], rule['closing_stage']))
    else:
        print('%s: %d rules, library %s' % (args.command, len(bundle['rules']), bundle['library_version']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
