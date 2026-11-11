"""references/knowledge/ 与 knowledge-release.json 一致；核对只读本技能，不读知识框架目录。"""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import knowledge_package as k


def test_the_installed_package_matches_its_manifest():
    assert k.problems() == []
    release = k.manifest()
    assert k.identity() == {'knowledge_version': release['knowledge_version'], 'fingerprint': release['fingerprint']}
    run = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'knowledge_package.py'), 'verify-installed'],
                         capture_output=True, text=True)
    assert run.returncode == 0 and 'PASS' in run.stdout


@pytest.fixture
def local_copy(tmp_path):
    shutil.copytree(ROOT / k.INSTALL_DIR, tmp_path / k.INSTALL_DIR)
    shutil.copyfile(ROOT / k.MANIFEST, tmp_path / k.MANIFEST)
    return tmp_path


def test_a_changed_missing_or_extra_file_is_found(local_copy):
    tree = local_copy / k.INSTALL_DIR
    (tree / 'README.md').write_text('改过', encoding='utf-8')
    (tree / '典型电路' / 'ldo.md').unlink()
    (tree / '典型电路' / 'extra.md').write_text('x', encoding='utf-8')
    found = k.problems(local_copy)
    assert 'README.md：内容与清单不符' in found
    assert '典型电路/ldo.md：缺失' in found
    assert '典型电路/extra.md：清单里没有' in found


def test_a_manifest_whose_fingerprint_does_not_match_its_files_is_found(local_copy):
    path = local_copy / k.MANIFEST
    data = json.loads(path.read_text(encoding='utf-8'))
    data['fingerprint'] = '0' * 64
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    assert k.problems(local_copy) == ['清单指纹不符']
