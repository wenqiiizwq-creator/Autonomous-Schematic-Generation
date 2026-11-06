"""本地安装包的完整性检查不依赖对方仓库；合成副本故障有明确反例。"""
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import guideline_criteria as g


def test_local_installed_release_is_valid():
    manifest = g.verify_installed(ROOT)
    assert manifest['fingerprint'] == g.shared_digest(ROOT)
    assert manifest['library_version'] == g.load(ROOT / g.SHARED_FILES[1])['library_version']


@pytest.fixture
def local_copy(tmp_path):
    for name in g.SHARED_FILES + ('shared-release.json',):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    manifest = json.loads((tmp_path / 'shared-release.json').read_text())
    manifest['payload'] = g.shared_files(tmp_path)
    manifest['fingerprint'] = g.shared_digest(tmp_path)
    (tmp_path / 'shared-release.json').write_text(json.dumps(manifest))
    return tmp_path


@pytest.mark.parametrize('name', g.SHARED_FILES)
def test_every_damaged_local_payload_is_rejected(local_copy, name):
    (local_copy / name).write_bytes(b'controlled damage')
    with pytest.raises(ValueError, match='installed sha256 mismatch'):
        g.verify_installed(local_copy)


@pytest.mark.parametrize('key,value', [('manifest_version', 99), ('fingerprint_format', 'unknown'),
                                     ('fingerprint_order', []), ('payload', {}),
                                     ('fingerprint', '0' * 64), ('library_version', '0.0.0')])
def test_invalid_local_identity_is_rejected(local_copy, key, value):
    path = local_copy / 'shared-release.json'
    manifest = json.loads(path.read_text())
    manifest[key] = value
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        g.verify_installed(local_copy)


def test_explicit_local_check_does_not_use_test_substitute(local_copy, monkeypatch, tmp_path):
    monkeypatch.setenv('GUIDELINE_CRITERIA', str(tmp_path / 'nonexistent.json'))
    monkeypatch.setenv('GUIDELINE_CRITERIA_TESTING', '1')
    assert g.verify_installed(local_copy)['payload'] == g.shared_files(local_copy)


def test_manifest_rehash_cannot_hide_an_invalid_bundle(local_copy):
    path = local_copy / g.SHARED_FILES[1]
    data = json.loads(path.read_text())
    data['content_sha256'] = '0' * 64
    path.write_text(json.dumps(data))
    manifest_path = local_copy / 'shared-release.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['payload'] = g.shared_files(local_copy)
    manifest['fingerprint'] = g.shared_digest(local_copy)
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='invalid installed bundle'):
        g.verify_installed(local_copy)


def test_local_cli_validates_and_rejects_corruption(local_copy):
    import subprocess
    command = [sys.executable, '-B', str(local_copy / 'scripts/guideline_criteria.py'), 'verify-installed']
    assert subprocess.run(command, capture_output=True).returncode == 0
    (local_copy / g.SHARED_FILES[0]).write_bytes(b'damage')
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 1
    assert 'installed sha256 mismatch' in result.stderr
