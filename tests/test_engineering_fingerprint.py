"""M4: engineering identity, document integrity, historical semantics and actual alternate input."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if ROOT.name == 'scripts':
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import guideline_criteria as g


@pytest.fixture
def package(tmp_path):
    for name in g.SHARED_FILES + ('shared-release.json',):
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    manifest_path = tmp_path / 'shared-release.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['payload'] = g.shared_files(tmp_path)
    manifest['fingerprint'] = g.shared_digest(tmp_path, manifest['fingerprint_format'])
    manifest_path.write_text(g.dump(manifest))
    return tmp_path


def test_only_maintenance_prose_changes_neither_engineering_identity_nor_version(package):
    before = g.shared_versions(package)
    for name in ('shared-layer.md', 'guideline-criteria.md'):
        path = package / 'references/shared' / name
        path.write_text(path.read_text() + '\n合成维护历史补充。\n')
    assert g.shared_versions(package) == before
    assert g.identity_errors(before, package) == []
    # Excluded prose is still protected by the full manifest, independently of engineering identity.
    with pytest.raises(ValueError, match='installed sha256 mismatch'):
        g.verify_installed(package)


@pytest.mark.parametrize('name', [
    'references/shared/guideline-criteria.json', 'references/shared/vocabulary.json',
    'references/shared/derating-rules.json', 'references/shared/derating-rules.md',
    'references/shared/commodity-floors.json', 'references/shared/stress-spec.md',
    'scripts/guideline_criteria.py', 'scripts/stress_check.py'])
def test_each_controlled_engineering_input_changes_fingerprint(package, name):
    before = g.shared_digest(package)
    path = package / name
    if name.endswith('guideline-criteria.json'):
        library = json.loads(path.read_text())
        library['engineering_values']['assumed_resistor_package']['value'] = '0201'
        path.write_text(g.dump(library))
    elif name.endswith('stress-spec.md'):
        path.write_text(path.read_text() + '\n合成判法变化：边界相等也记失败。\n')
    elif name.endswith('.py'):
        path.write_text(path.read_text() + '\nSYNTHETIC_ALGORITHM = lambda value: value + 1\n')
    else:
        path.write_bytes(path.read_bytes() + b'\ncontrolled change')
    assert g.shared_digest(package) != before


def test_v2_is_a_sorted_relative_path_hash_map_not_implicit_list_order(package, monkeypatch):
    files = g.shared_files(package)
    names = {'references/shared/guideline-criteria.json', 'references/shared/vocabulary.json',
             'references/shared/derating-rules.json', 'references/shared/derating-rules.md',
             'references/shared/commodity-floors.json', 'references/shared/stress-spec.md',
             'scripts/guideline_criteria.py', 'scripts/stress_check.py'}
    expected = hashlib.sha256(json.dumps({n: files[n] for n in names}, sort_keys=True,
                                         separators=(',', ':')).encode()).hexdigest()
    assert g.shared_digest(package) == expected
    monkeypatch.setattr(g, 'SHARED_FILES', tuple(reversed(g.SHARED_FILES)))
    monkeypatch.setattr(g, 'ENGINEERING_FILES', tuple(reversed(g.ENGINEERING_FILES)))
    assert g.shared_digest(package) == expected
    # Path names themselves bind the file role (even if the multiset of hashes is unchanged).
    files['scripts/guideline_criteria.py'], files['scripts/stress_check.py'] = files['scripts/stress_check.py'], files['scripts/guideline_criteria.py']
    assert g._engineering_digest(files) != expected


def test_legacy_algorithm_and_records_are_preserved_and_never_promoted(package):
    hashes = g.shared_files(package)
    expected = hashlib.sha256('\n'.join(hashes[n] for n in g.SHARED_FILES).encode()).hexdigest()
    assert g.shared_digest(package, 'shared-files-sha256-lines-v1') == expected
    manifest_path = package / 'shared-release.json'
    manifest = json.loads(manifest_path.read_text())
    current = g.shared_versions(package)
    old = dict(current, shared_sha256=expected)
    old.pop('fingerprint_format')
    original = copy.deepcopy(old)
    assert g.identity_errors(old, package)
    manifest.update(fingerprint_format='shared-files-sha256-lines-v1',
                    fingerprint_order=list(g.SHARED_FILES), fingerprint=expected)
    manifest_path.write_text(g.dump(manifest))
    assert g.verify_installed(package)['fingerprint'] == expected
    assert g.identity_errors(old, package) == []   # Only the v1 installation can validate historical semantics.
    assert old == original
    path = package / 'references/shared/shared-layer.md'
    path.write_text(path.read_text() + '\n旧算法仍绑定说明。\n')
    assert g.identity_errors(old, package)  # v1 did not lose its old identity check.


@pytest.mark.parametrize('field,value', [('fingerprint_format', None), ('fingerprint_format', 'unknown'),
                                       ('shared_sha256', '0'*64), ('library_version', '0.0.0')])
def test_new_identity_requires_version_digest_and_explicit_format(package, field, value):
    record = g.shared_versions(package)
    if value is None:
        record.pop(field)
    else:
        record[field] = value
    assert g.identity_errors(record, package)


def test_alternate_input_binds_real_bytes_even_when_test_mode_is_explicit(tmp_path, monkeypatch):
    installed = g.shared_versions()
    library = g.load(g.BUNDLE_PATH)
    library['engineering_values']['assumed_resistor_package']['value'] = '0201'
    override = tmp_path / 'alternate.json'
    raw = json.dumps(library, ensure_ascii=False).encode()
    override.write_bytes(raw)
    monkeypatch.setenv('GUIDELINE_CRITERIA', str(override))
    monkeypatch.setenv('GUIDELINE_CRITERIA_TESTING', '1')
    effective = g.shared_versions(bundle=g.load())
    assert effective['shared_sha256'] != installed['shared_sha256']
    assert effective['guideline_input'] == {'kind': 'alternate', 'sha256': hashlib.sha256(raw).hexdigest()}
    assert g.identity_errors(installed)
    assert g.identity_errors(effective) == []
    override.write_bytes(raw + b'\n')
    assert g.shared_versions()['shared_sha256'] != effective['shared_sha256']
    with pytest.raises(ValueError, match='changed during identity'):
        stale = copy.deepcopy(library)
        stale['library_version'] = 'stale-input'
        g.shared_versions(bundle=stale)


def test_recorded_label_never_prints_the_current_identity_for_old_records():
    record = {'library_version': 'historical', 'shared_sha256': '1'*64}
    label = g.shared_label(identity=record)
    assert '111111111111 [shared-files-sha256-lines-v1]' in label
    assert '设计准则库 historical' in label


def test_asg_report_rejects_old_audit_identity_without_rewriting_it():
    from test_design_report import Delivery
    delivery = Delivery()
    try:
        path = delivery.record / 'design-closure-audit.json'
        data = json.loads(path.read_text())
        data['guidelines'] = dict(g.shared_versions(), applicable=[])
        data['guidelines'].pop('fingerprint_format')
        path.write_text(json.dumps(data))
        original = path.read_bytes()
        _, problems = delivery.report()
        assert any('fingerprint format changed' in problem for problem in problems)
        assert path.read_bytes() == original
    finally:
        delivery.cleanup()
