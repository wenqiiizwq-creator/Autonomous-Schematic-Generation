"""只读覆盖层重建；冻结源漂移必须失败，不静默改规则。"""
import copy
import hashlib
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_registry_overlay as overlay
import guideline_criteria as g


def test_overlay_is_reproducible_and_does_not_write_source(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    card = copy.deepcopy(g.load()['criteria'][0])
    registry = {'spec': card['spec'], 'version': '1', 'criteria': [card]}
    path = source / 'G01_准则登记.json'
    path.write_text(json.dumps(registry))
    original = path.read_bytes()
    change = {'sources': {path.name: hashlib.sha256(original).hexdigest()}, 'source_count': 1,
              'expected_count': 1, 'exclude': {}, 'patches': {card['id']: {'set': {'coverage': 'project_input'}}}}
    for name in ('a', 'b'):
        overlay.materialize(source, change, tmp_path / name)
    assert path.read_bytes() == original
    assert (tmp_path / 'a' / path.name).read_bytes() == (tmp_path / 'b' / path.name).read_bytes()
    assert json.loads((tmp_path / 'a' / path.name).read_text())['criteria'][0]['coverage'] == 'project_input'
    path.write_text('{}')
    with pytest.raises(ValueError, match='指纹变化'):
        overlay.materialize(source, change, tmp_path / 'bad')


def test_runtime_overlay_matches_approved_action_and_exclusions():
    change = json.loads((overlay.ROOT / 'docs/registry-overlay-2026-11-05.json').read_text())
    library = g.load()
    cards = {r['id']: r for r in library['criteria']}
    assert not (set(cards) & set(change['exclude']))
    assert len(cards) == change['expected_count']
    assert library['library_version'] == '1.9.0'
    for rid, patch in change['patches'].items():
        for field, value in patch['set'].items():
            assert cards[rid][field] == value
    assert set(library['specs']) == {'G%02d' % n for n in range(1, 10)}
    assert g.bundle_errors(library) == []
