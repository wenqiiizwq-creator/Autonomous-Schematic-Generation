#!/usr/bin/env python3
"""本技能自带的知识：从硬件设计知识框架同步来的一份，运行时只读这一份，不读知识框架目录。

  python3 knowledge_package.py sync <知识框架目录> [--dry-run]
      取框架当前内容：知识组件换掉 references/knowledge/，设计准则汇编后换掉共用层（references/shared/ 和两个共用脚本），
      写清单 knowledge-sync.json、shared-release.json，并把与上一次同步的差异写进 docs/knowledge-sync/<框架版本>.md。
      --dry-run 只打印差异，不写文件。
  python3 knowledge_package.py verify-installed
      核对装的知识与清单一致（逐文件哈希、多出或缺少的文件、指纹）；不读知识框架目录。
"""
import datetime
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL_DIR = Path('references') / 'knowledge'
MANIFEST = 'knowledge-sync.json'
SHARED_MANIFEST = 'shared-release.json'
DIFF_DIR = Path('docs') / 'knowledge-sync'
# 同步进来的知识组件（框架里的目录名）和单个文件；设计实例是范例，不同步。
COMPONENTS = ('需求要素', '板级架构模式', '接口约定', '典型电路', '计算方法', '器件参数', '失效与故障分析')
SINGLE_FILES = ('索引/条目总表.md', '索引/准则支撑表.md', '原件勘误.md', '条目规范.md')
VERSION_LINE = re.compile(r'\*\*现行版本：(\d+\.\d+\.\d+)\*\*（(\d{4}-\d{2}-\d{2})）')
# 共用层：包内文件名 → 框架 设计准则/ 下的来源。guideline-criteria.json 由准则登记汇编，不在此表。
G10 = '规范正文/G10_元器件降额与应力规范/'
SHARED_SOURCES = {'references/shared/shared-layer.md': '工具/包说明/shared-layer.md',
                  'references/shared/guideline-criteria.md': '工具/包说明/guideline-criteria.md',
                  'references/shared/derating-rules.json': G10 + '降额值.json',
                  'references/shared/derating-rules.md': G10 + '降额规范.md',
                  'references/shared/stress-spec.md': G10 + '应力判法.md',
                  'references/shared/vocabulary.json': '准则登记/词表.json',
                  'references/shared/commodity-floors.json': G10 + '常规件最弱档.json',
                  'scripts/guideline_criteria.py': '工具/guideline_criteria.py',
                  'scripts/stress_check.py': '工具/stress_check.py'}
BUNDLE = 'references/shared/guideline-criteria.json'
# 降额规范、应力判法里的链接按框架的位置写，装进技能后改成包内文件名。
SHARED_LINKS = (('../../工具/包说明/shared-layer.md', 'shared-layer.md'), ('(应力判法.md)', '(stress-spec.md)'),
                ('(降额规范.md)', '(derating-rules.md)'))
README = '''# 本技能自带的知识

从硬件设计知识框架 %s（%s）同步，%s 取；逐文件哈希见技能根目录的 `knowledge-sync.json`。
不要在这里改条目：改在知识框架里，改完用 `python3 scripts/knowledge_package.py sync <知识框架目录>` 重新同步。

目录和框架里的同名：%s；`索引/条目总表.md` 列出全部条目，`索引/准则支撑表.md` 从准则编号反查支撑它的条目，
`原件勘误.md` 列出原件里的错误，`条目规范.md` 是条目的写法。设计实例没有同步，索引里列的设计实例条目这里没有。

条目里的来源路径相对知识框架的 `原件/`，指向 `设计准则/` 的链接在这里无效：准则正文和取值在技能的 `references/shared/`。
'''


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else Path(data).read_bytes()).hexdigest()


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def manifest(root=ROOT):
    return json.loads((Path(root) / MANIFEST).read_text(encoding='utf-8'))


def identity(root=ROOT):
    """What a delivery records: the framework version the knowledge was synced from, and its fingerprint."""
    m = manifest(root)
    return {'knowledge_version': m['knowledge_version'], 'fingerprint': m['fingerprint']}


def problems(root=ROOT):
    m, tree = manifest(root), Path(root) / INSTALL_DIR
    actual = {p.relative_to(tree).as_posix(): sha(p) for p in sorted(tree.rglob('*')) if p.is_file()} if tree.is_dir() else {}
    out = ['%s：%s' % (name, '缺失' if name not in actual else '内容与清单不符')
           for name, digest in m['files'].items() if actual.get(name) != digest]
    out += ['%s：清单里没有' % name for name in actual if name not in m['files']]
    if fingerprint(m['files']) != m['fingerprint']:
        out.append('清单指纹不符')
    return out


def framework_version(framework):
    found = VERSION_LINE.search((Path(framework) / '版本记录.md').read_text(encoding='utf-8'))
    if not found:
        raise ValueError('版本记录.md 里没有“**现行版本：X.Y.Z**（日期）”一行')
    return found.group(1), found.group(2)


def collect(framework, version, date, today):
    """{path under references/knowledge/: bytes} of what a sync installs."""
    framework = Path(framework)
    missing = [name for name in COMPONENTS if not (framework / name).is_dir()] + \
              [name for name in SINGLE_FILES if not (framework / name).is_file()]
    if missing:
        raise ValueError('知识框架里没有：%s（目录改了名就先改本脚本的 COMPONENTS、SINGLE_FILES 和读它们的代码）' % '、'.join(missing))
    files = {p.relative_to(framework).as_posix(): p.read_bytes()
             for name in COMPONENTS for p in sorted((framework / name).rglob('*.md'))}
    files.update({name: (framework / name).read_bytes() for name in SINGLE_FILES})
    stems = [Path(name).stem for name in files if name.startswith('典型电路/') and Path(name).name != 'README.md']
    twice = sorted({s for s in stems if stems.count(s) > 1})
    if twice:   # a typical circuit is named by its file name alone (page plan, scheme records)
        raise ValueError('典型电路里文件名重复：%s' % '、'.join(twice))
    files['README.md'] = (README % (version, date, today, '、'.join('`%s/`' % c for c in COMPONENTS))).encode('utf-8')
    return files


def collect_shared(framework, version):
    """({shared-layer path: bytes}, {registry file: sha256}) built with the framework's own guideline tool."""
    source = Path(framework) / '设计准则'
    spec = importlib.util.spec_from_file_location('framework_guideline_criteria', source / SHARED_SOURCES['scripts/guideline_criteria.py'])
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    registries = sorted((source / '准则登记').glob('G0*_准则登记.json'))
    vocabulary = source / '准则登记/词表.json'
    bundle = tool.build(source / '准则登记', version, vocabulary)
    errors = tool.bundle_errors(bundle, vocabulary)
    if errors or len(registries) != 9:
        raise ValueError('准则登记汇编不过：%s' % (errors or '应有 G01–G09 九份登记'))
    files = {name: (source / origin).read_bytes() for name, origin in SHARED_SOURCES.items()}
    for name in ('references/shared/derating-rules.md', 'references/shared/stress-spec.md'):
        text = files[name].decode('utf-8')
        for old, new in SHARED_LINKS:
            text = text.replace(old, new)
        files[name] = text.encode('utf-8')
    files[BUNDLE] = tool.dump(bundle).encode('utf-8')
    if set(files) != set(tool.SHARED_FILES):
        raise ValueError('共用层文件名单与准则工具的 SHARED_FILES 不一致，先改本脚本的 SHARED_SOURCES')
    return files, {'准则登记/' + p.name: sha(p) for p in registries}


def shared_manifest(files, version, inputs, tool_files):
    """shared-release.json in the format scripts/guideline_criteria.py verifies (verify-installed)."""
    engineering = sorted(n for n in files if n not in ('references/shared/shared-layer.md', 'references/shared/guideline-criteria.md'))
    digests = {name: sha(files[name]) for name in tool_files}
    controlled = {name: digests[name] for name in engineering}
    return {'manifest_version': 1, 'library_version': version, 'fingerprint_format': 'shared-paths-sha256-v2',
            'fingerprint_algorithm': 'SHA-256 of UTF-8 canonical JSON mapping relative paths to lowercase file SHA-256 digests; '
                                     'sorted keys, compact separators, no trailing LF. fingerprint_order declares the controlled scope only.',
            'fingerprint_order': engineering,
            'fingerprint': hashlib.sha256(json.dumps(controlled, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest(),
            'payload': digests, 'inputs': inputs, 'auxiliary': {}}


def file_changes(old, new):
    """Compare two {path: sha256}: {added, removed, changed, moved: [(old path, new path, content changed)]}.
    A file that left one path and appeared at another with the same name (the only one of that name on both sides) moved."""
    added, removed = sorted(set(new) - set(old)), sorted(set(old) - set(new))
    by_name = lambda paths: {n: [p for p in paths if Path(p).name == n] for n in {Path(p).name for p in paths}}
    gone, came = by_name(removed), by_name(added)
    moved = sorted((gone[n][0], came[n][0], old[gone[n][0]] != new[came[n][0]])
                   for n in gone if n != 'README.md' and len(gone[n]) == 1 and len(came.get(n, ())) == 1)
    return {'added': [p for p in added if p not in {m[1] for m in moved}],
            'removed': [p for p in removed if p not in {m[0] for m in moved}],
            'changed': sorted(p for p in set(old) & set(new) if old[p] != new[p]), 'moved': moved}


def criteria_changes(old, new):
    """Compare two guideline bundles by criterion id and engineering value name."""
    def part(key, index):
        a, b = index(old.get(key, [])), index(new.get(key, []))
        return {'added': sorted(set(b) - set(a)), 'removed': sorted(set(a) - set(b)),
                'changed': sorted(k for k in set(a) & set(b) if a[k] != b[k])}
    return {'criteria': part('criteria', lambda rows: {r['id']: r for r in rows}),
            'engineering_values': part('engineering_values', dict)}


def report(before, after, files, criteria, shared_files):
    lines = ['# 知识同步差异：%s → %s' % (before or '（首次同步）', after), '',
             '由 `scripts/knowledge_package.py sync` 生成。这是本技能要消化的清单：新增和改了的条目、准则，'
             '逐条看技能里对应的关卡、查阅表和说明要不要跟着改。', '']

    def section(title, rows):
        lines.extend(['## %s（%d）' % (title, len(rows)), ''] + (['- ' + r for r in rows] or ['无']) + [''])
    section('新增的条目', files['added'])
    section('内容改了的条目', files['changed'] + ['%s（由 %s 搬来）' % (new, old) for old, new, changed in files['moved'] if changed])
    section('删除的条目', files['removed'])
    section('只搬了位置的条目', ['%s → %s' % (old, new) for old, new, changed in files['moved'] if not changed])
    for key, title in (('criteria', '准则'), ('engineering_values', '工程取值')):
        for kind, word in (('added', '新增'), ('changed', '改了'), ('removed', '删除')):
            section('%s的%s' % (word, title), criteria[key][kind])
    section('共用层里变了的其他文件', shared_files)
    return '\n'.join(lines)


def sync(framework, root=ROOT, dry_run=False, today=None):
    """Install the framework's current content into root; returns the difference report text."""
    root, today = Path(root), today or datetime.date.today().isoformat()
    version, date = framework_version(framework)
    knowledge = collect(framework, version, date, today)
    shared, inputs = collect_shared(framework, version)
    old = manifest(root) if (root / MANIFEST).is_file() else {}
    tree = root / INSTALL_DIR
    old_files = {p.relative_to(tree).as_posix(): sha(p) for p in tree.rglob('*') if p.is_file()} if tree.is_dir() else {}
    old_bundle = json.loads((root / BUNDLE).read_text(encoding='utf-8')) if (root / BUNDLE).is_file() else {}
    new_bundle = json.loads(shared[BUNDLE])
    new_files = {name: sha(data) for name, data in knowledge.items()}
    strip = lambda files: {k: v for k, v in files.items() if k != 'README.md'}   # the README carries the sync date
    other = sorted(name for name, data in shared.items()
                   if name != BUNDLE and (not (root / name).is_file() or sha(root / name) != sha(data)))
    text = report(old.get('knowledge_version'), version, file_changes(strip(old_files), strip(new_files)),
                  criteria_changes(old_bundle, new_bundle), other)
    if dry_run:
        return text
    if tree.is_dir():
        shutil.rmtree(tree)
    for name, data in knowledge.items():
        (tree / name).parent.mkdir(parents=True, exist_ok=True)
        (tree / name).write_bytes(data)
    for name, data in shared.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_bytes(data)
    order = [n for n in shared if n != BUNDLE][:1] + [BUNDLE] + [n for n in shared if n != BUNDLE][1:]
    dump = lambda data: json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    (root / SHARED_MANIFEST).write_text(dump(shared_manifest(shared, version, inputs, order)), encoding='utf-8')
    (root / MANIFEST).write_text(dump({
        'manifest_version': 2, 'source': '硬件设计知识框架', 'knowledge_version': version, 'framework_date': date,
        'synced': today, 'components': list(COMPONENTS), 'fingerprint': fingerprint(new_files),
        'fingerprint_algorithm': 'SHA-256 of UTF-8 canonical JSON mapping relative paths to file SHA-256; sorted keys, compact separators',
        'files': dict(sorted(new_files.items()))}), encoding='utf-8')
    (root / DIFF_DIR).mkdir(parents=True, exist_ok=True)
    (root / DIFF_DIR / ('%s.md' % version)).write_text(text + '\n', encoding='utf-8')
    return text


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ['sync'] and len([a for a in argv[1:] if a != '--dry-run']) == 1:
        try:
            print(sync(next(a for a in argv[1:] if a != '--dry-run'), dry_run='--dry-run' in argv))
        except (OSError, ValueError) as error:
            print('FAIL：%s' % error)
            return 1
        return 0
    if argv != ['verify-installed']:
        print(__doc__)
        return 2
    found = problems()
    m = manifest()
    print('\n'.join(found) if found else '知识框架 %s（%s 同步） %s' % (m['knowledge_version'], m['synced'], m['fingerprint']))
    print('FAIL' if found else 'PASS')
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
