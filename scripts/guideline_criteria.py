#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""共用设计准则库（G01–G09）：校验、汇编、按适用条件选出规则、统计覆盖；共用层指纹。

本文件、scripts/stress_check.py（共用应力核对）和 references/shared/ 下的文件是 ASG 与 SR 的共用层，两个技能里是同一份字节，
由硬件设计规范统一维护和发布；技能内不得编辑（见 references/shared/shared-layer.md）。只用标准库，不导入任一技能的模块。

    python3 guideline_criteria.py check BUNDLE                       校验汇编文件
    python3 guideline_criteria.py build --from DIR --vocabulary PATH --library-version V --out PATH
                                                                  只从 DIR 的直接子登记文件汇编（显式词表）
    python3 guideline_criteria.py select BUNDLE [--baseline B] [--circuit-type T ...] [--device-kind K ...]
                                                                  列出适用准则
    python3 guideline_criteria.py value NAME [BUNDLE]                 读一项工程取值
    python3 guideline_criteria.py release --help                    确定性发布（保存输入快照）
    python3 guideline_criteria.py verify-release DIR                校验正式发布目录
    python3 guideline_criteria.py install DIR --target SKILL         核清单后整批安装
    python3 guideline_criteria.py shared                              共用层指纹与逐文件 sha256
"""
import argparse
import hashlib
import json
import os
import re
import sys
import shutil
import tempfile
from pathlib import Path

BUNDLE_SCHEMA_VERSION = 1
SKILL_ROOT = Path(__file__).resolve().parent.parent
SHARED_DIR = SKILL_ROOT / 'references' / 'shared'
BUNDLE_PATH = SHARED_DIR / 'guideline-criteria.json'
DERATING_PATH = SHARED_DIR / 'derating-rules.json'
VOCABULARY_PATH = SHARED_DIR / 'vocabulary.json'       # 词表的唯一出处：基线、电路类型、器件类别（名字与标题）
COMMODITY_PATH = SHARED_DIR / 'commodity-floors.json'  # 常规件最弱档：片式电阻、MLCC 可订购档、触点（厂家目录给的数）
# 共用层的全部文件（相对技能根目录）：references/shared/ 里的每一份加本脚本。两技能同字节，指纹由它们现算。
SHARED_FILES = ('references/shared/shared-layer.md', 'references/shared/guideline-criteria.json',
                'references/shared/guideline-criteria.md', 'references/shared/derating-rules.json',
                'references/shared/derating-rules.md', 'references/shared/stress-spec.md',
                'references/shared/vocabulary.json', 'references/shared/commodity-floors.json',
                'scripts/guideline_criteria.py', 'scripts/stress_check.py')
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


def load(path=None):
    """Explicit inspection path, or the installed bundle. Environment substitution requires explicit test mode."""
    override = os.environ.get('GUIDELINE_CRITERIA')
    if not path and override and os.environ.get('GUIDELINE_CRITERIA_TESTING') != '1':
        raise ValueError('GUIDELINE_CRITERIA is test-only; use an explicit path for inspection, or install a release')
    return json.loads(Path(path or override or BUNDLE_PATH).read_text(encoding='utf-8'))


def vocabulary(path=None):
    """vocabulary.json flattened to the bundle's form: {'default_baseline', 'vocabulary': {trigger: [names]}}.
    The file is the one place the names and titles live; SR's catalog and ASG's part classes are checked against it."""
    raw = json.loads(Path(path or VOCABULARY_PATH).read_text(encoding='utf-8'))
    return {'default_baseline': raw['default_baseline'],
            'vocabulary': {key: [item['name'] for item in raw[key]] for key in TRIGGERS}}


def commodity_floors(path=None):
    """commodity-floors.json: chip-resistor floors by package, orderable MLCC rows and contact floors, with their basis."""
    return json.loads(Path(path or COMMODITY_PATH).read_text(encoding='utf-8'))


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
    if Path(vocabulary_path or VOCABULARY_PATH).is_file():   # the bundle carries a copy of the shared vocabulary; a changed vocabulary.json needs a rebuild
        shared = globals()['vocabulary'](vocabulary_path)
        if vocabulary != shared['vocabulary'] or default != shared['default_baseline']:
            errors.append('vocabulary or default_baseline differs from references/shared/vocabulary.json: rebuild the bundle')
    rules = bundle.get('criteria')
    if not isinstance(rules, list):
        return errors + ['rules must be a list']
    ids = [r.get('id') for r in rules if isinstance(r, dict)]
    for rid in sorted({i for i in ids if ids.count(i) > 1}, key=str):
        errors.append('%s: duplicate id' % rid)
    if ids != sorted(ids, key=str):
        errors.append('rules must be sorted by id')
    known = set(ids)
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


def engineering_value(name, bundle=None):
    """The value of one engineering value (raises KeyError when the bundle does not hold it)."""
    return (bundle if bundle is not None else load())['engineering_values'][name]['value']


def shared_files(root=SKILL_ROOT):
    """{relative path: sha256} of every shared-layer file installed under root."""
    return {name: hashlib.sha256((Path(root) / name).read_bytes()).hexdigest() for name in SHARED_FILES}


def shared_digest(root=SKILL_ROOT):
    """One fingerprint of the whole shared layer: the sha256 of its files' sha256 list in SHARED_FILES order.
    Reports bind to it; a plan or audit written against another digest is stale."""
    return hashlib.sha256('\n'.join(shared_files(root)[n] for n in SHARED_FILES).encode('utf-8')).hexdigest()


def shared_versions(root=SKILL_ROOT):
    """The versions the shared layer carries: the rule library's and the derating table's."""
    root = Path(root)
    library = json.loads((root / SHARED_FILES[1]).read_text(encoding='utf-8'))
    derating = json.loads((root / SHARED_FILES[3]).read_text(encoding='utf-8'))
    return {'shared_sha256': shared_digest(root), 'library_version': library['library_version'],
            'derating_version': derating['version']}


def shared_label(root=SKILL_ROOT):
    """共用层 <指纹前 12 位>，设计准则库 <版本>，降额 v<版本> — the one line both reports print."""
    v = shared_versions(root)
    return '共用层 %s，设计准则库 %s，降额 v%s' % (v['shared_sha256'][:12], v['library_version'], v['derating_version'])


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


def build(registry_dir, library_version, vocabulary_path=None):
    """Build direct child registries only; release requires all nine, tests may build a subset.
    Existing import callers may omit vocabulary_path; the publishing CLI always supplies it."""
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
    bundle = {'schema_version': BUNDLE_SCHEMA_VERSION, 'library_version': library_version,
              'default_baseline': base['default_baseline'], 'vocabulary': base['vocabulary'], 'specs': specs,
              'content_sha256': content_sha256(rules, values), 'criteria': rules}
    if values:
        bundle['engineering_values'] = values
    return bundle


def dump(bundle):
    return json.dumps(bundle, ensure_ascii=False, indent=2) + '\n'


# 发布源由规范维护；此处函数随同一文件安装，运行时装载路径保持不变。
FINGERPRINT_FORMAT = 'shared-files-sha256-lines-v1'


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inventory(root):
    root = Path(root)
    return {p.relative_to(root).as_posix(): _sha(p) for p in sorted(root.rglob('*')) if p.is_file()}


def _safe_file(root, name):
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts or relative.as_posix() != name:
        raise ValueError('unsafe manifest path: %s' % name)
    root = Path(root).resolve()
    path = root / relative
    if any(p.is_symlink() for p in (path, *path.parents) if p != root and root in p.parents):
        raise ValueError('symlink is not a controlled file: %s' % name)
    return path


def verify_release(release):
    """校验完整发布目录；清单覆盖载荷、持久输入与附加身份记录。"""
    release = Path(release)
    manifest = json.loads((release / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('manifest_version') != 1 or manifest.get('fingerprint_format') != FINGERPRINT_FORMAT:
        raise ValueError('unsupported manifest or fingerprint format')
    if manifest.get('fingerprint_order') != list(SHARED_FILES) or set(manifest.get('payload', {})) != set(SHARED_FILES):
        raise ValueError('manifest must name exactly the ten controlled payload files')
    expected = dict(manifest['payload'])
    expected.update({'inputs/' + name: digest for name, digest in manifest['inputs'].items()})
    expected.update(manifest.get('auxiliary', {}))
    for name, digest in expected.items():
        if _sha(_safe_file(release, name)) != digest:
            raise ValueError('sha256 mismatch: %s' % name)
    actual = set(_inventory(release))
    if actual != set(expected) | {'manifest.json'}:
        raise ValueError('unlisted or missing release files')
    if shared_digest(release) != manifest['fingerprint']:
        raise ValueError('fingerprint mismatch')
    bundle = load(release / SHARED_FILES[1])  # 明确路径，不使用测试替代输入
    errors = bundle_errors(bundle, release / 'references/shared/vocabulary.json')
    if errors or bundle['library_version'] != manifest['library_version']:
        raise ValueError('invalid release bundle: %s' % errors)
    return manifest


def publish(registry_dir, shared_source, tools_source, vocabulary_path, library_version, releases_dir,
            scratch_root='/tmp/codex-work/shared-release'):
    """从显式源构建确定性包；正式版本只增不改，快照是复现输入。"""
    registry_dir, shared_source, tools_source = map(Path, (registry_dir, shared_source, tools_source))
    names = sorted(registry_dir.glob('G0*_准则登记.json'))
    if len(names) != 9:
        raise ValueError('release requires nine direct registry files')
    bundle = build(registry_dir, library_version, vocabulary_path)
    if set(bundle['specs']) != {'G0%d' % n for n in range(1, 10)}:
        raise ValueError('release requires G01 through G09 exactly once')
    errors = bundle_errors(bundle, vocabulary_path)
    if errors:
        raise ValueError('\n'.join(errors))
    if not re.fullmatch(r'\d+\.\d+\.\d+', library_version):
        raise ValueError('library version must be X.Y.Z')
    if (tools_source / 'guideline_criteria.py').read_bytes() != Path(__file__).read_bytes():
        raise ValueError('builder source differs from the executing publisher')
    scratch_root = Path(scratch_root)
    scratch_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='publish-', dir=scratch_root) as tmp:
        candidate = Path(tmp) / library_version
        candidate.mkdir()
        inputs = candidate / 'inputs'
        for source in names:
            dest = inputs / '准则登记' / source.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        for name in SHARED_FILES:
            dest = candidate / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if name == 'references/shared/guideline-criteria.json':
                dest.write_text(dump(bundle), encoding='utf-8')
                continue
            source = (Path(vocabulary_path) if name == 'references/shared/vocabulary.json' else
                      shared_source / Path(name).name if name.startswith('references/') else tools_source / Path(name).name)
            shutil.copyfile(source, dest)
            snapshot = inputs / name
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(dest, snapshot)
        # 从已固定的输入再构建，拒绝构建期间发生的源变化。
        rebuilt = build(inputs / '准则登记', library_version, inputs / 'references/shared/vocabulary.json')
        if dump(rebuilt) != dump(bundle):
            raise ValueError('inputs changed during publication')
        manifest = {'manifest_version': 1, 'library_version': library_version,
                    'fingerprint_format': FINGERPRINT_FORMAT,
                    'fingerprint_algorithm': 'SHA-256 of lowercase file SHA-256 digests joined by LF, no trailing LF; fingerprint_order is authoritative.',
                    'fingerprint_order': list(SHARED_FILES), 'fingerprint': shared_digest(candidate),
                    'payload': shared_files(candidate), 'inputs': _inventory(inputs), 'auxiliary': {}}
        (candidate / 'manifest.json').write_text(dump(manifest), encoding='utf-8')
        verify_release(candidate)
        target = Path(releases_dir) / library_version
        if target.exists():
            verify_release(target)
            if _inventory(target) != _inventory(candidate):
                raise ValueError('immutable release already exists with different bytes: %s' % library_version)
            return target
        target.parent.mkdir(parents=True, exist_ok=True)
        # 临时文件只在 /tmp/codex-work；跨文件系统时明确失败，不留下半包。
        candidate.rename(target)
        return target


def install_release(release, target, scratch_root='/tmp/codex-work/shared-release'):
    """临时副本先核全清单；作为一批替换十个受控文件及清单，异常恢复原文件。"""
    target = Path(target)
    if not target.is_dir():
        raise ValueError('explicit installation target must already exist')
    scratch_root = Path(scratch_root)
    scratch_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='install-', dir=scratch_root) as tmp:
        staged = Path(tmp) / 'release'
        shutil.copytree(release, staged, symlinks=True)
        manifest = verify_release(staged)  # 所有验证发生在目标第一次写入之前
        replacements = {name: (staged / name).read_bytes() for name in SHARED_FILES}
        replacements['shared-release.json'] = (staged / 'manifest.json').read_bytes()
        paths = {name: _safe_file(target, name) for name in replacements}
        original = {name: path.read_bytes() if path.exists() else None for name, path in paths.items()}
        modes = {name: path.stat().st_mode & 0o777 if path.exists() else 0o644 for name, path in paths.items()}
        changed = []
        try:
            for name, data in replacements.items():
                path = paths[name]
                path.parent.mkdir(parents=True, exist_ok=True)
                # 每文件同文件系统原子替换；批次失败则回滚全部已替换文件。
                with tempfile.NamedTemporaryFile(dir=tmp, prefix='shared-', delete=False) as stream:
                    temporary = Path(stream.name)
                    try:
                        stream.write(data)
                        stream.flush()
                        temporary.chmod(modes[name])
                        os.replace(temporary, path)
                    finally:
                        temporary.unlink(missing_ok=True)
                changed.append(name)
            if shared_files(target) != manifest['payload'] or shared_digest(target) != manifest['fingerprint']:
                raise ValueError('installed payload differs from the verified release')
        except BaseException:
            for name in reversed(changed):
                path, data = paths[name], original[name]
                if data is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(data)
                    path.chmod(modes[name])
            raise
    return manifest



def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('check')
    check.add_argument('bundle', nargs='?', default=str(BUNDLE_PATH))
    make = sub.add_parser('build')
    make.add_argument('--from', dest='source', required=True)
    make.add_argument('--vocabulary', required=True)
    make.add_argument('--library-version', required=True)
    make.add_argument('--out', required=True)
    pick = sub.add_parser('select')
    pick.add_argument('bundle', nargs='?', default=str(BUNDLE_PATH))
    pick.add_argument('--baseline')
    pick.add_argument('--circuit-type', action='append', default=[])
    pick.add_argument('--device-kind', action='append', default=[])
    pick.add_argument('--typed-only', action='store_true', help='only rules a circuit type or device kind triggers')
    pick.add_argument('--ports', action='store_true', help='with --typed-only, add the board-wide G07 port rules')
    read = sub.add_parser('value')
    read.add_argument('name')
    read.add_argument('bundle', nargs='?', default=str(BUNDLE_PATH))
    sub.add_parser('shared')
    release = sub.add_parser('release')
    release.add_argument('--from', dest='source', required=True)
    release.add_argument('--shared-source', required=True)
    release.add_argument('--tools-source', required=True)
    release.add_argument('--vocabulary', required=True)
    release.add_argument('--library-version', required=True)
    release.add_argument('--releases', required=True)
    release.add_argument('--scratch-root', default='/tmp/codex-work/shared-release')
    verify = sub.add_parser('verify-release')
    verify.add_argument('release')
    install = sub.add_parser('install')
    install.add_argument('release')
    install.add_argument('--target', required=True)
    install.add_argument('--scratch-root', default='/tmp/codex-work/shared-release')
    args = parser.parse_args(argv)
    if args.command in ('release', 'verify-release', 'install'):
        try:
            if args.command == 'release':
                result = publish(args.source, args.shared_source, args.tools_source, args.vocabulary,
                                 args.library_version, args.releases, args.scratch_root)
            elif args.command == 'verify-release':
                result = verify_release(args.release)['fingerprint']
            else:
                result = install_release(args.release, args.target, args.scratch_root)['fingerprint']
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(result)
        return 0
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
        errors = bundle_errors(bundle)
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
