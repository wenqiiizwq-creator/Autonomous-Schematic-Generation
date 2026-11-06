"""Schema 2 gaps cannot inherit the historical global circuit waiver."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import render_design_report as report


def test_v2_event_cannot_waive_all_blocks():
    lessons = {'schema_version': 2, 'library_gaps': [], 'events': [
        {'source': 'user:2026-11-05', 'cause': 'knowledge_missing',
         'change': 'references/typical-circuits/new.md'}]}
    errors = report.check_block_circuits('a.kicad_sch', {'甲': ['R1'], '乙': ['R2']}, {}, {}, lessons)
    assert len(errors) == 2

import copy
import json
import pytest
from test_design_report import Delivery


def gap():
    return {'id': 'LG-1', 'page': 'a.kicad_sch', 'block': '甲',
            'reason': '检索 protection；方案甲的电压范围不适用', 'source': 'test:检索记录',
            'design_basis': 'basis.json#/items/0',
            'target': 'references/typical-circuits/new.md', 'status': 'open'}


def lessons(gaps=None, events=None):
    return {'schema_version': 2, 'library_gaps': [gap()] if gaps is None else gaps,
            'events': [] if events is None else events}


def event(impact='observed'):
    return {'source': 'review:SR/F-1', 'cause': 'knowledge_missing', 'knowledge_kind': 'criterion',
            'impact': impact, 'problem': '缺脉冲判据导致漏核', 'consequence': '审查证实漏核脉冲应力',
            'evidence': ['review:SR/F-1', 'user:2026-11-05'],
            'change': 'references/typical-circuits/new.md 必算项'}


def test_exact_binding_and_explicit_bad_circuit(tmp_path):
    (tmp_path / 'basis.json').write_text('{"items": [{"id": "B1"}]}')
    data = lessons()
    assert report.check_lessons(data) == ([], {})
    assert not report.check_block_circuits('a.kicad_sch', {'甲': ['R1']}, {}, {}, data, tmp_path)
    assert report.check_block_circuits('b.kicad_sch', {'甲': ['R1']}, {}, {}, data, tmp_path)
    assert report.check_block_circuits('a.kicad_sch', {'乙': ['R1']}, {}, {}, data, tmp_path)
    assert report.check_block_circuits('a.kicad_sch', {'甲': ['R1']}, {'甲': 'bad#x'}, {}, data, tmp_path)
    assert report.check_block_circuits('a.kicad_sch', {'甲': ['R1']}, {'甲': 'ok#bad'}, {'ok': {'x'}}, data, tmp_path)
    (tmp_path / 'basis.json').unlink()
    assert report.check_block_circuits('a.kicad_sch', {'甲': ['R1']}, {}, {}, data, tmp_path)


@pytest.mark.parametrize('field,value', [('id', ''), ('page', []), ('block', None), ('reason', ''),
    ('source', 'somewhere'), ('design_basis', ''), ('target', '../new.md'), ('status', 'done'), ('cause', 'none')])
def test_gap_schema_rejects_bad_fields(field, value):
    g = gap(); g[field] = value
    errors, _ = report.check_lessons(lessons([g]))
    assert errors


@pytest.mark.parametrize('gaps', [None, {}, 'bad', [42]])
def test_gap_list_required(gaps):
    data = lessons([]); data['library_gaps'] = gaps
    assert report.check_lessons(data)[0]


def test_duplicates_and_empty_records():
    assert report.check_lessons(lessons([gap(), gap()]))[0]
    g = gap(); g['id'] = 'LG-2'
    assert report.check_lessons(lessons([gap(), g]))[0]
    g['block'] = '乙'; g['id'] = 'LG-1'
    assert report.check_lessons(lessons([gap(), g]))[0]
    assert report.check_lessons(lessons([], []))[0]
    assert not report.check_lessons(lessons([], [{'source': 'user:2026-11-05', 'cause': 'none', 'why_none': '核对方案无新增内容'}]))[0]


def test_orphans_and_closed(tmp_path):
    circuits = tmp_path / 'references/typical-circuits'; circuits.mkdir(parents=True)
    (tmp_path / 'basis.json').write_text('{"items": [1]}')
    plan = {'pages': [{'file': 'a.kicad_sch', 'blocks': {'甲': ['R1']}, 'circuits': {}}]}
    assert not report.check_library_gaps(lessons(), plan, tmp_path, circuits)[0]
    g = gap(); g['page'] = 'other.kicad_sch'
    assert report.check_library_gaps(lessons([g]), plan, tmp_path, circuits)[0]
    g = gap(); g['block'] = '乙'
    assert report.check_library_gaps(lessons([g]), plan, tmp_path, circuits)[0]
    g = gap(); g.update(status='closed', resolution='references/typical-circuits/new.md#做法甲')
    assert report.check_library_gaps(lessons([g]), plan, tmp_path, circuits)[0]
    (circuits / 'new.md').write_text('# 电路\n功能：保护\n## 实现方案\n### 做法甲\n- 必算项：电流\n')
    assert report.check_library_gaps(lessons([g]), plan, tmp_path, circuits)[0]
    plan['pages'][0]['circuits']['甲'] = 'new#做法甲'
    assert not report.check_library_gaps(lessons([g]), plan, tmp_path, circuits)[0]
    assert not report.check_library_gaps(lessons([g]), plan, tmp_path, circuits)[1]
    g['resolution'] = 'references/typical-circuits/new.md#不存在'
    assert report.check_library_gaps(lessons([g]), plan, tmp_path, circuits)[0]


@pytest.mark.parametrize('value', [0, 3, '2', True, None])
def test_unknown_versions(value):
    data = lessons(); data['schema_version'] = value
    assert report.check_lessons(data)[0]


def test_legacy_compatibility():
    old = {'events': [{'source': 'user:2026-11-05', 'cause': 'knowledge_missing',
                       'change': 'references/typical-circuits/new.md'}]}
    for version in (None, 1):
        data = copy.deepcopy(old)
        if version: data['schema_version'] = version
        assert not report.check_lessons(data)[0]
        assert not report.check_block_circuits('any.kicad_sch', {'甲': [], '乙': []}, {}, {}, data)
    assert report.check_lessons({'schema_version': 1, 'events': []})[0]


@pytest.mark.parametrize('field', ['knowledge_kind', 'impact', 'problem', 'consequence', 'evidence'])
def test_observed_requires_evidence_and_consequence(field):
    e = event(); del e[field]
    assert report.check_lessons(lessons([], [e]))[0]


def test_uncertain_is_distinct_and_citations_scan_new_fields():
    e = event('uncertain'); e.pop('consequence'); e.pop('evidence')
    assert report.check_lessons(lessons([], [e]))[0]
    e.update(uncertainty='尚无独立复核', pending='核对当时运行包')
    assert not report.check_lessons(lessons([], [e]))[0]
    e['evidence'] = ['bad']
    assert report.check_lessons(lessons([], [e]))[0]


def test_locator_and_cross_record_report():
    d = Delivery()
    try:
        data = lessons()
        data['library_gaps'][0].update(page='board.kicad_sch', block='稳压', design_basis='record/evidence/design.md#regulator')
        d.write('lessons.json', data)
        plan = json.loads((d.record / 'page-plan.json').read_text()); plan['pages'][0]['circuits'] = {}
        d.write('page-plan.json', plan)
        output, errors = d.report()
        assert not errors, errors
        assert '共 1 项，独立于问题事件' in output
        assert '有证据后果 0；待核归因 0' in output
        e = event(); u = event('uncertain'); u.update(source='review:SR/F-2', uncertainty='尚无证据', pending='复核运行包')
        data['events'] = [e, u]; d.write('lessons.json', data)
        output, errors = d.report()
        assert not errors, errors
        assert '有证据后果 1；待核归因 1' in output
        e['evidence'] = ['datasheet:raw/Datasheet/08_电源管理/X - XYZ100.pdf#p999']
        data['library_gaps'][0]['source'] = e['evidence'][0]; d.write('lessons.json', data)
        _, errors = d.report()
        assert any('evidence' in p and '999' in p for p in errors)
        assert any('library_gaps' in p and '999' in p for p in errors)
        data['library_gaps'][0]['design_basis'] = 'record/evidence/design.md#不存在'; d.write('lessons.json', data)
        assert any('design_basis' in p for p in d.report()[1])
    finally:
        d.cleanup()


def test_gap_cannot_replace_review_event():
    d = Delivery()
    try:
        d.write('lessons.json', lessons())
        d.write('review-responses.json', {'schema_version': 1, 'sources': [], 'items': [
            {'id': 'F-1', 'cause': 'knowledge_missing', 'response': 'CALC_DOC', 'comment': '漏核', 'detail': '补核算', 'changes': ['核算']} ]})
        assert any('lessons.json' in p and 'F-1' in p for p in d.report()[1])
    finally:
        d.cleanup()


def test_closed_gap_allows_empty_events():
    g = gap()
    g.update(status='closed', target='references/typical-circuits/output-filter-storage.md',
             resolution='references/typical-circuits/output-filter-storage.md#实现方案')
    assert report.check_lessons(lessons([g])) == ([], {})


def test_locator_rejects_missing_entry_and_escape(tmp_path):
    (tmp_path / 'basis.json').write_text('{"items": [{"id": "B1"}]}')
    assert report.check_record_locator('basis.json#B1', tmp_path)
    assert not report.check_record_locator('basis.json#/items/9', tmp_path)
    assert not report.check_record_locator('basis.json# ', tmp_path)
    assert not report.check_record_locator('../basis.json#B1', tmp_path)
    assert not report.check_record_locator('basis.json', tmp_path)


@pytest.mark.parametrize('value', [None, {}, 3, 'bad'])
def test_v2_bad_event_list_is_reported(value):
    d = Delivery()
    try:
        data = lessons(); data['events'] = value; d.write('lessons.json', data)
        assert any('events' in p for p in d.report()[1])
    finally:
        d.cleanup()
