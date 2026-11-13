#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""设计准则库（G01–G09）：校验、汇编、按适用条件选出规则、统计覆盖；准则与降额数据的身份。

准则、词表、降额与常规件数据都直接读知识框架（位置见 scripts/knowledge_source.py），不在技能里留拷贝；准则登记在运行时
汇编成内存里的汇编文件（bundle）。本文件和 scripts/stress_check.py 是技能自己的代码，只用标准库，另外只导入 knowledge_source。

    python3 guideline_criteria.py check [BUNDLE]                      校验汇编结果（不给文件就校验框架里汇编出的）
    python3 guideline_criteria.py build --from DIR --vocabulary PATH [--library-version V] --out PATH
                                                                  只从 DIR 的直接子登记文件汇编（显式词表）
    python3 guideline_criteria.py select [BUNDLE] [--baseline B] [--circuit-type T ...] [--device-kind K ...]
                                                                  列出适用准则
    python3 guideline_criteria.py value NAME [BUNDLE]                 读一项工程取值
    python3 guideline_criteria.py shared                              准则与降额数据的指纹、逐文件 sha256
"""
import argparse
import copy
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import knowledge_source

BUNDLE_SCHEMA_VERSION = 1
SKILL_ROOT = Path(__file__).resolve().parent.parent
# 身份覆盖的技能自己的代码；其余文件在知识框架里，键是相对框架目录的路径。
SKILL_FILES = ('scripts/guideline_criteria.py', 'scripts/stress_check.py')
G10 = '知识/设计准则/' + knowledge_source.G10_DIR + '/'
FRAMEWORK_FILES = ('知识/设计准则/准则登记/词表.json', G10 + '降额值.json', G10 + '降额规范.md', G10 + '应力判法.md',
                   G10 + '常规件最弱档.json')
FINGERPRINT_FORMAT = 'framework-paths-sha256-v1'

RULE_ID = re.compile(r'^G0[1-9]-\d{3}$')
STATUSES = ('draft', 'active', 'retired')
NATURES = ('shall', 'should', 'method', 'project')
STAGES = ('schematic', 'pcb', 'simulation', 'prototype', 'production')
COVERAGES = ('item', 'project_input', 'handoff')   # how an applicable rule is covered; a rule without the field is item
TRIGGERS = ('baselines', 'circuit_types', 'device_kinds')
APPLIES_KEYS = set(TRIGGERS) | {'board', 'text'}
RELATION_KEYS = ('related', 'primary', 'reuses', 'conflicts')
RULE_KEYS = {'id', 'title', 'spec', 'version', 'status', 'nature', 'applies_when', 'not_applicable', 'tailoring',
             'inputs', 'asg_action', 'sr_check', 'source', 'relations', 'closing_stage', 'coverage'}
SOURCE_KEYS = ('document', 'edition', 'clause', 'page')
VALUE_NAME = re.compile(r'^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$')
VALUE_KEYS = {'spec', 'value', 'unit', 'applies', 'basis', 'confirmed'}
# 规则正文里点名工程取值的两种写法：反引号括住的蛇形名，或 G0x 前缀的裸名（如 g03_loop_pm_min）
VALUE_CITE = re.compile(r'`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`|\b(g0[1-9]_[a-z0-9_]*[a-z0-9])\b')
PREVIEW_WORDS = ('公开预览', '非全文', 'preview')   # 公开预览不能作规则依据


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def content_sha256(rules, values=None):
    """Hash of the rules, and of the engineering values when there are any (a bundle without values keeps the
    rules-only hash)."""
    content = {'criteria': rules, 'engineering_values': values} if values else rules
    return hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def cited_values(rule):
    """Engineering value names a rule's text cites."""
    text = ' '.join(str(rule.get(k) or '') for k in ('asg_action', 'sr_check', 'tailoring', 'not_applicable')) \
        + ' ' + ' '.join(str(x) for x in rule.get('inputs') or [])
    return {a or b for a, b in VALUE_CITE.findall(text)}


def value_errors(name, entry):
    errors = []
    if not VALUE_NAME.match(str(name)):
        errors.append('engineering value %s: name must be snake_case' % name)
    if not isinstance(entry, dict):
        return errors + ['engineering value %s is not an object' % name]
    if set(entry) - VALUE_KEYS:
        errors.append('engineering value %s: unknown fields %s' % (name, sorted(set(entry) - VALUE_KEYS)))
    if not (isinstance(entry.get('spec'), str) and re.match(r'^G0[1-9]$', entry['spec'])):
        errors.append('engineering value %s: spec must look like G02' % name)
    if 'value' not in entry:
        errors.append('engineering value %s: value is required' % name)
    for key in ('applies', 'basis', 'confirmed'):
        if not _text(entry.get(key)):
            errors.append('engineering value %s: %s is required' % (name, key))
    if 'unit' in entry and not isinstance(entry['unit'], str):
        errors.append('engineering value %s: unit must be text' % name)
    return errors



_CACHE = {}


def _assembled():
    """Bundle assembled from the framework's registries; cached in the process until a registry or the vocabulary
    file changes. Returns a copy, so callers may edit it."""
    registry, vocab = knowledge_source.registry_dir(), knowledge_source.vocabulary_path()
    paths = sorted(registry.glob('G0*_准则登记.json')) + [vocab]
    key = (str(registry),) + tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths)
    if _CACHE.get('key') != key:
        bundle = build(registry, None, vocab)
        errors = bundle_errors(bundle, vocab)
        if errors:
            raise ValueError('知识框架的准则登记汇编不过：\n' + '\n'.join(errors))
        _CACHE.update(key=key, bundle=bundle)
    return copy.deepcopy(_CACHE['bundle'])


def load(path=None):
    """Explicit inspection path, or the bundle assembled from the framework's registries. Environment substitution
    requires explicit test mode."""
    override = os.environ.get('GUIDELINE_CRITERIA')
    if not path and override and os.environ.get('GUIDELINE_CRITERIA_TESTING') != '1':
        raise ValueError('GUIDELINE_CRITERIA is test-only; use an explicit path for inspection')
    if path or override:
        return json.loads(Path(path or override).read_text(encoding='utf-8'))
    return _assembled()


def vocabulary(path=None):
    """词表.json flattened to the bundle's form: {'default_baseline', 'vocabulary': {trigger: [names]}}.
    The file is the one place the names and titles live; SR's catalog and ASG's part classes are checked against it."""
    raw = json.loads(Path(path or knowledge_source.vocabulary_path()).read_text(encoding='utf-8'))
    return {'default_baseline': raw['default_baseline'],
            'vocabulary': {key: [item['name'] for item in raw[key]] for key in TRIGGERS}}


def vocabulary_titles(group, path=None):
    """Names/titles from the framework vocabulary; classifier order, cues and behavior stay with each consumer."""
    raw = json.loads(Path(path or knowledge_source.vocabulary_path()).read_text(encoding='utf-8'))
    return {item['name']: item['title'] for item in raw[group]}


def commodity_floors(path=None):
    """常规件最弱档.json: chip-resistor floors by package, orderable MLCC rows and contact floors, with their basis."""
    return json.loads(Path(path or knowledge_source.commodity_path()).read_text(encoding='utf-8'))


def coverage_class(rule):
    """How a rule is covered: item (each rule its own citation), project_input (one requirement baseline answers it)
    or handoff (one downstream handoff list carries it)."""
    return rule.get('coverage', 'item')


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
    if coverage_class(rule) not in COVERAGES:
        errors.append('%s: coverage must be one of %s' % (label, '/'.join(COVERAGES)))
    elif coverage_class(rule) == 'handoff' and rule.get('closing_stage') == 'schematic':
        errors.append('%s: a handoff rule closes after the schematic; closing_stage is schematic' % label)
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



def _framework_vocabulary_path():
    try:
        return knowledge_source.vocabulary_path()
    except knowledge_source.KnowledgeFrameworkNotFound:
        return None


def bundle_errors(bundle, vocabulary_path=None):
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
    vocabulary_path = vocabulary_path or _framework_vocabulary_path()
    if vocabulary_path and Path(vocabulary_path).is_file():   # the bundle carries a copy of the framework vocabulary; a changed 词表.json needs a rebuild
        shared = globals()['vocabulary'](vocabulary_path)
        if vocabulary != shared['vocabulary'] or default != shared['default_baseline']:
            errors.append('vocabulary or default_baseline differs from the framework 词表.json: rebuild the bundle')
    rules = bundle.get('criteria')
    if not isinstance(rules, list):
        return errors + ['rules must be a list']
    ids = [r.get('id') for r in rules if isinstance(r, dict)]
    for rid in sorted({i for i in ids if ids.count(i) > 1}, key=str):
        errors.append('%s: duplicate id' % rid)
    if ids != sorted(ids, key=str):
        errors.append('rules must be sorted by id')
    known = set(ids)
    errors.extend(relation_shape_errors(rules))
    values = bundle.get('engineering_values', {})
    if not isinstance(values, dict):
        return errors + ['engineering_values must be an object']
    for name, entry in values.items():
        errors.extend(value_errors(name, entry))
    for rule in rules:
        errors.extend(rule_errors(rule, vocabulary, default))
        for key, targets in (rule.get('relations') or {}).items() if isinstance(rule, dict) else ():
            for target in targets if isinstance(targets, list) else ():
                if target not in known:
                    errors.append('%s: relations.%s names unknown rule %s' % (rule.get('id'), key, target))
        if isinstance(rule, dict):
            for name in sorted(cited_values(rule) - set(values)):
                errors.append('%s: cites engineering value %s, which the bundle does not hold' % (rule.get('id'), name))
    if bundle.get('content_sha256') != content_sha256(rules, values):
        errors.append('content_sha256 does not match the rules')
    return errors


def relation_shape_errors(rules):
    """related 必须双向；一条规则不能指向自己，也不能把同一条既标主判又标复用。"""
    errors = []
    related = {r.get('id'): set((r.get('relations') or {}).get('related') or ())
               for r in rules if isinstance(r, dict) and isinstance(r.get('relations') or {}, dict)}
    for rule in rules:
        if not isinstance(rule, dict) or not isinstance(rule.get('relations') or {}, dict):
            continue
        rid, rel = rule.get('id'), rule.get('relations') or {}
        if any(rid in (v if isinstance(v, list) else ()) for v in rel.values()):
            errors.append('%s: relations name the rule itself' % rid)
        both = set(rel.get('primary') or ()) & set(rel.get('reuses') or ())
        if both:
            errors.append('%s: %s is both primary and reuses' % (rid, '、'.join(sorted(both))))
        for target in sorted(related.get(rid, ())):
            if target in related and rid not in related[target]:
                errors.append('%s: related %s, but %s does not list it back' % (rid, target, target))
    return errors


def engineering_value(name, bundle=None):
    """The value of one engineering value (raises KeyError when the bundle does not hold it)."""
    return (bundle if bundle is not None else load())['engineering_values'][name]['value']


def shared_files():
    """{path relative to the framework: sha256} of the guideline and derating data in the framework (the registries,
    the vocabulary, the derating values and spec, the stress rule, the commodity floors) plus the skill's own
    scripts/ files (keyed scripts/...)."""
    root = knowledge_source.framework_root()
    registries = sorted((root / '知识/设计准则/准则登记').glob('G0*_准则登记.json'))
    names = [p.relative_to(root).as_posix() for p in registries] + list(FRAMEWORK_FILES)
    files = {name: _sha(root / name) for name in names}
    files.update({name: _sha(SKILL_ROOT / name) for name in SKILL_FILES})
    return files


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _digest(files):
    """Canonical relative-path -> file SHA-256 map; input enumeration order has no meaning."""
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def shared_digest():
    return _digest(shared_files())


def shared_versions(bundle=None):
    """Identity of the data actually consumed; alternate data never borrows the framework fingerprint."""
    assembled = _assembled()
    library = bundle if bundle is not None else load()
    derating = json.loads(Path(knowledge_source.derating_path()).read_text(encoding='utf-8'))
    files = shared_files()
    override = os.environ.get('GUIDELINE_CRITERIA')
    input_identity = None
    if override or library != assembled:
        # Explicit in-memory test inputs use canonical JSON; environment inputs bind their real bytes.
        raw = dump(library).encode('utf-8')
        if override:
            alternate = Path(override).read_bytes()
            if json.loads(alternate) != library:
                raise ValueError('alternate guideline input changed during identity binding')
            raw = alternate
        input_identity = {'kind': 'alternate', 'sha256': hashlib.sha256(raw).hexdigest()}
        files['guideline_input'] = input_identity['sha256']
    identity = {'shared_sha256': _digest(files), 'fingerprint_format': FINGERPRINT_FORMAT,
                'library_version': library['library_version'], 'content_sha256': library['content_sha256'],
                'derating_version': derating['version'], 'read_date': datetime.date.today().isoformat()}
    if input_identity:
        identity['guideline_input'] = input_identity
    return identity


def identity_errors(record, bundle=None):
    """Any record not in the current format must be regenerated; an old PASS never migrates. read_date is not compared."""
    if not isinstance(record, dict):
        return ['missing shared identity: regenerate the plan/audit']
    current = shared_versions(bundle)
    if record.get('fingerprint_format') != current['fingerprint_format']:
        return ['shared fingerprint format changed/missing: regenerate the plan/audit']
    errors = []
    for key in ('library_version', 'shared_sha256'):
        if record.get(key) != current[key]:
            errors.append('shared %s changed: regenerate the plan/audit' % key)
    if record.get('guideline_input') != current.get('guideline_input'):
        errors.append('shared guideline input changed: regenerate the plan/audit')
    return errors


def shared_label(identity=None):
    """Print recorded identity when supplied; a missing read date is shown as such, never as today's."""
    v = shared_versions() if identity is None else identity
    label = '设计准则 %s（%s 读取）' % (v['shared_sha256'][:12], v.get('read_date', '日期未记录'))
    return label + ('，降额 v%s' % v['derating_version'] if 'derating_version' in v else '')


def select(bundle, baseline=None, circuit_types=(), device_kinds=(), typed_only=False, ports=False):
    """Active rules whose conditions hold: the baseline matches (an empty list is every baseline) and the rule is
    board-wide or names one of the circuit types or device kinds present. typed_only drops the board-wide rules and
    keeps those a circuit type or device kind triggers (ASG task 1.3, one functional block); ports adds back the
    board-wide G07 rules, the port matrix of a block with external ports."""
    baseline = baseline or bundle['default_baseline']
    circuits, kinds = set(circuit_types), set(device_kinds)
    out = []
    for rule in bundle['criteria']:
        when = rule['applies_when']
        if rule['status'] != 'active' or (when.get('baselines') and baseline not in when['baselines']):
            continue
        typed = circuits & set(when.get('circuit_types', ())) or kinds & set(when.get('device_kinds', ()))
        board = when.get('board') and (not typed_only or (ports and rule['spec'] == 'G07'))
        if typed or board:
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
        errors.append('scope library_version %s is not the current %s'
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
    known = {r['id'] for r in bundle['criteria']}
    for item in scope.get('not_applicable', []):
        if not (isinstance(item, dict) and item.get('id') in known and _text(item.get('reason'))):
            errors.append('scope not_applicable entries are {id, reason} naming a rule in the bundle')
    return errors


def coverage(bundle, applicable, cited, not_applicable=None, answered=None):
    """cited: {rule id: [where it is cited]}; not_applicable: {rule id: reason}; answered: {rule id: the baseline item
    that answers it}. An applicable rule is covered when cited or held not applicable with a reason; a project_input
    rule is covered by its answer, not by a citation. The rest are uncovered. Rules closing after the schematic are
    listed as downstream whether covered or not. by_coverage lists the three classes when a rule is not item, and is
    absent otherwise."""
    not_applicable, answered = not_applicable or {}, answered or {}
    known = {r['id'] for r in bundle['criteria']}
    ids = [r['id'] for r in applicable]
    classes = {r['id']: coverage_class(r) for r in applicable}
    where = {i: (['baseline:' + answered[i]] if i in answered else []) if classes[i] == 'project_input' else cited.get(i)
             for i in ids}
    found = {
        'library_version': bundle['library_version'],
        'content_sha256': bundle['content_sha256'],
        'applicable': ids,
        'covered': {i: sorted(where[i]) for i in ids if where[i]},
        'not_applicable': {i: not_applicable[i] for i in ids if i in not_applicable and not where[i]},
        'uncovered': [i for i in ids if not where[i] and i not in not_applicable],
        'downstream': [r['id'] for r in applicable if r['closing_stage'] != 'schematic'],
        'unknown_cited': sorted(i for i in cited if i not in known),
    }
    if set(classes.values()) - {'item'}:
        found['by_coverage'] = {c: [i for i in ids if classes[i] == c] for c in COVERAGES}
    return found


def build(registry_dir, library_version=None, vocabulary_path=None):
    """Build direct child registries only (tests may build a subset). library_version defaults to
    'framework-' + the first 12 hex digits of content_sha256, so it follows the content and nothing else.
    Existing import callers may omit vocabulary_path; the framework vocabulary is then used."""

    base = vocabulary(vocabulary_path)
    rules, specs, values = [], {}, {}
    for path in sorted(Path(registry_dir).glob('G0*_准则登记.json')):
        registry = json.loads(path.read_text(encoding='utf-8'))
        if registry['spec'] in specs:
            raise ValueError('duplicate spec: %s' % registry['spec'])
        if not re.fullmatch(r'G0[1-9]', str(registry['spec'])):
            raise ValueError('unknown spec: %s' % registry['spec'])
        if any(rule.get('spec') != registry['spec'] for rule in registry['criteria']):
            raise ValueError('rule spec differs from its registry')
        specs[registry['spec']] = registry['version']
        rules.extend(registry['criteria'])
        for name, entry in (registry.get('engineering_values') or {}).items():
            if name in values:
                raise ValueError('engineering value %s is defined by both %s and %s'
                                 % (name, values[name].get('spec'), registry['spec']))
            values[name] = dict(entry, spec=registry['spec'])
    rules.sort(key=lambda r: str(r.get('id')))
    values = dict(sorted(values.items()))
    digest = content_sha256(rules, values)
    bundle = {'schema_version': BUNDLE_SCHEMA_VERSION, 'library_version': library_version or 'framework-' + digest[:12],
              'default_baseline': base['default_baseline'], 'vocabulary': base['vocabulary'], 'specs': specs,
              'content_sha256': digest, 'criteria': rules}
    if values:
        bundle['engineering_values'] = values
    return bundle


def dump(bundle):
    return json.dumps(bundle, ensure_ascii=False, indent=2) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('check')
    check.add_argument('bundle', nargs='?')
    make = sub.add_parser('build')
    make.add_argument('--from', dest='source', required=True)
    make.add_argument('--vocabulary', required=True)
    make.add_argument('--library-version')
    make.add_argument('--out', required=True)
    pick = sub.add_parser('select')
    pick.add_argument('bundle', nargs='?')
    pick.add_argument('--baseline')
    pick.add_argument('--circuit-type', action='append', default=[])
    pick.add_argument('--device-kind', action='append', default=[])
    pick.add_argument('--typed-only', action='store_true', help='only rules a circuit type or device kind triggers')
    pick.add_argument('--ports', action='store_true', help='with --typed-only, add the board-wide G07 port rules')
    read = sub.add_parser('value')
    read.add_argument('name')
    read.add_argument('bundle', nargs='?')
    sub.add_parser('shared')
    args = parser.parse_args(argv)
    try:
        if args.command == 'shared':
            for name, digest in shared_files().items():
                print('%s  %s' % (digest, name))
            print(shared_label())
            return 0
        if args.command == 'build':
            bundle = build(args.source, args.library_version, args.vocabulary)
            errors = bundle_errors(bundle, args.vocabulary)
            if not errors:
                Path(args.out).write_text(dump(bundle), encoding='utf-8')
        else:
            bundle = load(args.bundle)
            errors = bundle_errors(bundle) if args.bundle else []   # an assembled bundle was checked on assembly
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    if args.command == 'value':
        if args.name not in bundle.get('engineering_values', {}):
            print('no engineering value %s' % args.name, file=sys.stderr)
            return 1
        print(json.dumps(bundle['engineering_values'][args.name], ensure_ascii=False))
    elif args.command == 'select':
        for rule in select(bundle, args.baseline, args.circuit_type, args.device_kind, args.typed_only, args.ports):
            kind = coverage_class(rule)
            print('%s  %s  [%s]%s' % (rule['id'], rule['title'], rule['closing_stage'], '' if kind == 'item' else '  coverage=' + kind))
    else:
        print('%s: %d criteria, library %s' % (args.command, len(bundle['criteria']), bundle['library_version']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
