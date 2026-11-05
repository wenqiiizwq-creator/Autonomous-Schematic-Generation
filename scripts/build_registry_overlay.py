#!/usr/bin/env python3
"""只读登记 + 受控覆盖层，在 /tmp/codex-work 下生成临时登记并调用原汇编器。"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def materialize(source, overlay, target):
    source, target = Path(source), Path(target)
    paths = sorted(source.rglob('G0*_准则登记.json'))
    hashes = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if hashes != overlay['sources']:
        raise ValueError('登记源指纹变化，请复核覆盖层；不自动吸收并行会话改动')
    seen, patched = set(), set()
    for path in paths:
        registry = json.loads(path.read_text(encoding='utf-8'))
        kept = []
        for rule in registry['criteria']:
            rid = rule['id']
            if rid in seen:
                raise ValueError('duplicate id: ' + rid)
            seen.add(rid)
            if rid in overlay['exclude']:
                continue
            if rid in overlay['patches']:
                rule.update(overlay['patches'][rid]['set'])
                patched.add(rid)
            kept.append(rule)
        registry['criteria'] = kept
        out = target / path.relative_to(source)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    missing = set(overlay['patches']) - patched
    if missing:
        raise ValueError('覆盖层指向不存在的规则: ' + ', '.join(sorted(missing)))
    if len(seen) != overlay['source_count'] or len(seen - set(overlay['exclude'])) != overlay['expected_count']:
        raise ValueError('规则数量与覆盖层不一致')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path)
    parser.add_argument('--overlay', type=Path, default=ROOT / 'docs/registry-overlay-2026-11-05.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'references/shared/guideline-criteria.json')
    args = parser.parse_args()
    overlay = json.loads(args.overlay.read_text(encoding='utf-8'))
    scratch = Path('/tmp/codex-work/g01-g09')
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='registry-', dir=scratch) as directory:
        materialize(args.registry or Path(overlay['registry']), overlay, directory)
        return subprocess.call([sys.executable, str(ROOT / 'scripts/guideline_criteria.py'), 'build',
                                '--from', directory, '--library-version', overlay['library_version'],
                                '--out', str(args.out)])


if __name__ == '__main__':
    sys.exit(main())
