#!/usr/bin/env python3
"""本技能装的知识包 references/knowledge/ 与根目录 knowledge-release.json 是否一致（逐文件哈希、多出或缺少的文件、指纹）。

  python3 knowledge_package.py verify-installed

只读本技能里的文件，不读知识框架目录；核法与知识框架 工具/knowledge_package.py 的 verify-installed 相同。
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL_DIR = Path('references') / 'knowledge'
MANIFEST = 'knowledge-release.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def manifest(root=ROOT):
    return json.loads((Path(root) / MANIFEST).read_text(encoding='utf-8'))


def identity(root=ROOT):
    """What a delivery records: the knowledge package version and fingerprint."""
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


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv != ['verify-installed']:
        print(__doc__)
        return 2
    found = problems()
    m = manifest()
    print('\n'.join(found) if found else '知识包 %s %s' % (m['knowledge_version'], m['fingerprint']))
    print('FAIL' if found else 'PASS')
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
