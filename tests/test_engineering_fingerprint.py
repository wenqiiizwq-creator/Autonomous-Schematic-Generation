"""Guideline identity: what the fingerprint covers, that a non-current record is rejected, and that an actual alternate
input binds its real bytes. Tests that change files use a small framework copied from the configured one."""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
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
import knowledge_source as ks


@pytest.fixture
def package(tmp_path, monkeypatch):
    """A framework holding only the files the identity covers, and a skill folder holding the two scripts it covers."""
    framework, skill = tmp_path / 'framework', tmp_path / 'skill'
    real = ks.framework_root()
    for name in g.shared_files():
        source = ROOT / name if name.startswith('scripts/') else real / name
        dest = (skill if name.startswith('scripts/') else framework) / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    for name in ('知识', '索引'):
        (framework / name).mkdir(exist_ok=True)
    monkeypatch.setenv(ks.ENV_VAR, str(framework))
    monkeypatch.setattr(g, 'SKILL_ROOT', skill)
    return framework


def test_only_prose_outside_the_controlled_files_changes_nothing(package):
    before = g.shared_versions()
    (package / '知识/设计准则/维护').mkdir(parents=True)
    (package / '知识/设计准则/维护/说明.md').write_text('合成维护历史补充。\n')
    (package / '知识/设计准则/README.md').write_text('合成说明。\n')
    assert g.shared_versions() == before
    assert g.identity_errors(before) == []


def test_each_controlled_input_changes_the_fingerprint(package):
    names = sorted(g.shared_files())
    assert any(n.endswith('降额值.json') for n in names) and any(n.endswith('应力判法.md') for n in names)
    for name in names:
        path = (g.SKILL_ROOT if name.startswith('scripts/') else package) / name
        before_bytes = path.read_bytes()
        before = g.shared_digest()
        path.write_bytes(before_bytes + b'\n')      # JSON stays valid; scripts and prose just end with a blank line
        try:
            assert g.shared_digest() != before, name
        finally:
            path.write_bytes(before_bytes)
        assert g.shared_digest() == before, name


def test_the_fingerprint_is_a_sorted_relative_path_hash_map(package):
    files = g.shared_files()
    assert all(not Path(n).is_absolute() for n in files)
    expected = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert g.shared_digest() == expected
    # Path names themselves bind the file role (even if the multiset of hashes is unchanged).
    swapped = dict(files)
    swapped['scripts/guideline_criteria.py'], swapped['scripts/stress_check.py'] = files['scripts/stress_check.py'], files['scripts/guideline_criteria.py']
    assert g._digest(swapped) != expected


def test_old_format_records_are_rejected_not_promoted(package):
    """Any non-current record must be regenerated, never migrated."""
    current = g.shared_versions()
    for fmt in (None, 'shared-paths-sha256-v2'):
        old = dict(current)
        old.pop('fingerprint_format')
        if fmt:
            old['fingerprint_format'] = fmt
        original = copy.deepcopy(old)
        assert any('fingerprint format' in e for e in g.identity_errors(old))
        assert old == original


@pytest.mark.parametrize('field,value', [('fingerprint_format', None), ('fingerprint_format', 'unknown'),
                                       ('shared_sha256', '0'*64), ('library_version', '0.0.0')])
def test_new_identity_requires_version_digest_and_explicit_format(package, field, value):
    record = g.shared_versions()
    if value is None:
        record.pop(field)
    else:
        record[field] = value
    assert g.identity_errors(record)


def test_the_read_date_is_recorded_and_not_compared(package):
    record = g.shared_versions()
    assert record['read_date']
    record['read_date'] = '2000-01-01'
    assert g.identity_errors(record) == []


def test_alternate_input_binds_real_bytes_even_when_test_mode_is_explicit(tmp_path, monkeypatch):
    installed = g.shared_versions()
    library = g.load()
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
    assert label.startswith('设计准则 111111111111（') and '日期未记录' in label
    assert g.shared_versions()['read_date'] not in label


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
