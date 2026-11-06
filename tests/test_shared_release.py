"""发布入口的可复现、拒绝损坏和整批安装回滚；合成输入，不读取规范工作目录。"""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if ROOT.name == 'scripts':
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import guideline_criteria as g


@pytest.fixture
def source(tmp_path):
    registry, shared, tools = [tmp_path / n for n in ('registry', 'shared', 'tools')]
    for path in (registry, shared, tools):
        path.mkdir()
    for name in g.SHARED_FILES:
        if name == 'references/shared/guideline-criteria.json':
            continue
        shutil.copyfile(ROOT / name, (shared if name.startswith('references/') else tools) / Path(name).name)
    rule = {'id': 'G01-001', 'spec': 'G01', 'version': '1.0', 'title': '合成设计准则',
            'status': 'active', 'nature': 'shall', 'applies_when': {'board': True},
            'inputs': [], 'asg_action': '核对合成输入', 'sr_check': '独立核对合成输入',
            'source': [{'document': 'Synthetic test source', 'edition': '1', 'clause': '1', 'page': '1'}],
            'closing_stage': 'schematic'}
    for n in range(1, 10):
        spec = 'G0%d' % n
        (registry / (spec + '_准则登记.json')).write_text(g.dump(
            {'spec': spec, 'version': '1.0', 'criteria': [rule] if n == 1 else []}), encoding='utf-8')
    def publish(destination='releases', version='2.0.0'):
        return g.publish(registry, shared, tools, shared / 'vocabulary.json', version,
                         tmp_path / destination, tmp_path / 'scratch')
    return registry, shared, tools, publish


def test_build_reads_only_direct_children_and_rejects_duplicate_specs(source):
    registry, _, _, _ = source
    nested = registry / 'history'
    nested.mkdir()
    shutil.copyfile(registry / 'G01_准则登记.json', nested / 'G01_准则登记.json')
    assert len(g.build(registry, '2.0.0')['criteria']) == 1
    shutil.copyfile(registry / 'G09_准则登记.json', registry / 'G09_copy_准则登记.json')
    with pytest.raises(ValueError, match='duplicate spec'):
        g.build(registry, '2.0.0')


def test_release_requires_exactly_nine_distinct_specs(source):
    registry, _, _, publish = source
    path = registry / 'G09_准则登记.json'
    path.unlink()
    with pytest.raises(ValueError, match='nine direct'):
        publish()
    path.write_text(g.dump({'spec': 'G08', 'version': '1.0', 'criteria': []}))
    with pytest.raises(ValueError, match='duplicate spec'):
        publish()


@pytest.mark.parametrize('fault', ['id', 'reference', 'vocabulary', 'preview', 'value'])
def test_release_rejects_invalid_source_metadata(source, fault):
    registry, _, _, publish = source
    path = registry / 'G01_准则登记.json'
    data = json.loads(path.read_text())
    rule = data['criteria'][0]
    if fault == 'id':
        data['criteria'].append(copy.deepcopy(rule))
    elif fault == 'reference':
        rule['relations'] = {'related': ['G09-999']}
    elif fault == 'vocabulary':
        rule['applies_when'] = {'circuit_types': ['UNKNOWN_TEST_TYPE']}
    elif fault == 'preview':
        rule['source'][0]['document'] = '公开预览 Synthetic source'
    else:
        rule['asg_action'] = '核对 `missing_engineering_value`'
    path.write_text(g.dump(data))
    with pytest.raises(ValueError):
        publish()


def test_explicit_vocabulary_is_used_in_build_and_validation(source):
    registry, shared, _, publish = source
    vocabulary = shared / 'vocabulary.json'
    data = json.loads(vocabulary.read_text())
    data['circuit_types'].append({'name': 'SYNTHETIC_NEW', 'title': '合成电路'})
    vocabulary.write_text(g.dump(data))
    path = registry / 'G01_准则登记.json'
    data = json.loads(path.read_text())
    data['criteria'][0]['applies_when'] = {'circuit_types': ['SYNTHETIC_NEW']}
    path.write_text(g.dump(data))
    release = publish()
    assert 'SYNTHETIC_NEW' in g.load(release / g.SHARED_FILES[1])['vocabulary']['circuit_types']
    assert not g.bundle_errors(g.load(release / g.SHARED_FILES[1]), vocabulary)


def test_repeated_publication_and_snapshot_rebuild_are_byte_identical(source, tmp_path):
    _, _, _, publish = source
    left, right = publish('left'), publish('right')
    assert g._inventory(left) == g._inventory(right)
    assert publish('left') == left  # 同版同字节幂等
    rebuilt = tmp_path / 'rebuilt.json'
    subprocess.run([sys.executable, '-B', str(left / 'inputs/scripts/guideline_criteria.py'),
                    'build', '--from', str(left / 'inputs/准则登记'), '--vocabulary',
                    str(left / 'inputs/references/shared/vocabulary.json'), '--library-version', '2.0.0',
                    '--out', str(rebuilt)], check=True, capture_output=True)
    assert rebuilt.read_bytes() == (left / g.SHARED_FILES[1]).read_bytes()
    manifest = g.verify_release(left)
    assert manifest['fingerprint'] == g.shared_digest(left)
    assert not any(str(tmp_path) in name for name in manifest['inputs'])


def test_published_version_cannot_be_overwritten_with_different_bytes(source):
    _, shared, _, publish = source
    release = publish()
    before = g._inventory(release)
    path = shared / 'shared-layer.md'
    path.write_text(path.read_text() + '\n合成维护说明变化。\n')
    with pytest.raises(ValueError, match='immutable release'):
        publish()
    assert before == g._inventory(release)


@pytest.mark.parametrize('fault', ['payload', 'input', 'unlisted', 'format', 'order', 'fingerprint', 'version'])
def test_damaged_release_is_rejected_before_target_changes(source, tmp_path, fault):
    _, _, _, publish = source
    release = publish()
    if fault in ('payload', 'input', 'unlisted'):
        path = release / {'payload': g.SHARED_FILES[0],
                          'input': 'inputs/准则登记/G01_准则登记.json', 'unlisted': 'extra.txt'}[fault]
        path.write_text('damage')
    else:
        path = release / 'manifest.json'
        data = json.loads(path.read_text())
        key = {'format': 'fingerprint_format', 'order': 'fingerprint_order',
               'fingerprint': 'fingerprint', 'version': 'library_version'}[fault]
        data[key] = [] if fault == 'order' else 'invalid'
        path.write_text(g.dump(data))
    target = tmp_path / 'consumer'
    target.mkdir()
    (target / 'keep.txt').write_text('untouched')
    before = g._inventory(target)
    with mock.patch.object(g.os, 'replace', wraps=g.os.replace) as replace:
        with pytest.raises((ValueError, OSError)):
            g.install_release(release, target, tmp_path / 'scratch')
        replace.assert_not_called()
    assert before == g._inventory(target)


def test_installs_exact_payload_preserves_other_files_and_rolls_back(source, tmp_path):
    _, shared, _, publish = source
    release = publish()
    target = tmp_path / 'consumer'
    target.mkdir()
    (target / 'keep.txt').write_text('untouched')
    manifest = g.install_release(release, target, tmp_path / 'scratch')
    assert g.shared_files(target) == manifest['payload']
    assert (target / 'shared-release.json').read_bytes() == (release / 'manifest.json').read_bytes()
    assert (target / 'keep.txt').read_text() == 'untouched'
    before = g._inventory(target)
    path = shared / 'shared-layer.md'
    path.write_text(path.read_text() + '\n合成新版本。\n')
    next_release = publish(version='2.0.1')
    original_replace = g.os.replace
    calls = []
    def fail_second(src, dst):
        calls.append(dst)
        if len(calls) == 2:
            raise OSError('synthetic replacement failure')
        return original_replace(src, dst)
    with mock.patch.object(g.os, 'replace', side_effect=fail_second):
        with pytest.raises(OSError, match='synthetic replacement'):
            g.install_release(next_release, target, tmp_path / 'scratch')
    assert len(calls) == 2
    assert before == g._inventory(target)


def test_manifest_paths_cannot_escape_or_follow_symlinks(source, tmp_path):
    _, _, _, publish = source
    release = publish()
    outside = tmp_path / 'outside'
    outside.write_text('untouched')
    target = tmp_path / 'consumer'
    target.mkdir()
    (target / 'references').symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        g.install_release(release, target, tmp_path / 'scratch')
    with pytest.raises(ValueError, match='unsafe'):
        g._safe_file(target, '../outside')
    assert outside.read_text() == 'untouched'


def test_production_load_does_not_silently_bind_test_data_to_installed_identity(tmp_path, monkeypatch):
    custom = tmp_path / 'test-bundle.json'
    library = g.load(g.BUNDLE_PATH)
    library['library_version'] = 'synthetic-test-data'
    custom.write_text(g.dump(library))
    monkeypatch.setenv('GUIDELINE_CRITERIA', str(custom))
    monkeypatch.delenv('GUIDELINE_CRITERIA_TESTING', raising=False)
    with pytest.raises(ValueError, match='test-only'):
        g.load()
    assert g.load(custom)['library_version'] == 'synthetic-test-data'  # 显式文件检查
    monkeypatch.setenv('GUIDELINE_CRITERIA_TESTING', '1')
    assert g.load()['library_version'] == 'synthetic-test-data'
