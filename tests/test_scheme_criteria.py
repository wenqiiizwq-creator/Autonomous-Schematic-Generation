"""Task 1.3: key functional blocks list the rules that can exclude a candidate scheme (record/scheme-criteria.json)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import guideline_criteria  # noqa: E402
import render_design_report as report  # noqa: E402

BUNDLE = guideline_criteria.load()


def closure(types=('POWER_PROTECTION', 'DC_24V'), kinds=('tvs', 'mosfet')):
    return {'guideline_scope': {'library_version': BUNDLE['library_version'], 'baseline': 'industrial_telecom',
                                'circuit_types': list(types), 'device_kinds': list(kinds)}}


def criterion(gid='G07-023', basis='standard'):
    return {'id': gid, 'excludes': '只在输入侧做保护的方案', 'basis': basis,
            'how': 'OUT 口加负向钳位与反灌阻断', 'defer': ['负向浪涌残压']}


def record(*criteria, ports=True, searched=''):
    return {'version': 1, 'blocks': [{'block': '24 V 入口与输出保护', 'circuit_types': ['POWER_PROTECTION', 'DC_24V'],
                                      'device_kinds': ['tvs'], 'ports': ports, 'searched': searched,
                                      'criteria': list(criteria)}]}


def check(data, c=None):
    return report.check_scheme_criteria(data, closure() if c is None else c, BUNDLE)


def test_typed_only_drops_board_wide_rules_and_ports_adds_g07():
    every = guideline_criteria.select(BUNDLE, None, ['POWER_PROTECTION', 'DC_24V'], ['tvs'])
    typed = guideline_criteria.select(BUNDLE, None, ['POWER_PROTECTION', 'DC_24V'], ['tvs'], typed_only=True)
    ported = guideline_criteria.select(BUNDLE, None, ['POWER_PROTECTION', 'DC_24V'], ['tvs'], typed_only=True, ports=True)
    assert all(not r['applies_when'].get('board') for r in typed)
    assert len(typed) < len(ported) < len(every)
    extra = {r['id'] for r in ported} - {r['id'] for r in typed}
    assert extra and all(i.startswith('G07') for i in extra)
    assert 'G07-022' in extra and 'G07-023' in {r['id'] for r in typed}


def test_a_well_formed_record_passes():
    assert check(record(criterion(), criterion('G07-022', 'inference'))) == []


def test_missing_record_is_required_only_for_key_circuit_types():
    assert check(None) and 'scheme-criteria.json' in check(None)[0]
    assert check(None, closure(types=('I2C',), kinds=())) == []
    assert check(None, {}) == []


def test_every_key_circuit_type_needs_a_block():
    problems = check(record(criterion()), closure(types=('POWER_PROTECTION', 'DC_24V', 'ANALOG')))
    assert any('ANALOG' in p for p in problems)


def test_port_rules_need_a_block_with_ports():
    assert any('G07-022' in p for p in check(record(criterion('G07-022'), ports=False)))


def test_a_rule_the_block_does_not_trigger_is_refused():
    assert any('G01-001' in p for p in check(record(criterion('G01-001'))))
    assert any('G99-999' in p for p in check(record(criterion('G99-999'))))


def test_an_empty_block_says_what_it_searched():
    assert any('searched' in p for p in check(record()))
    assert check(record(searched='select --typed-only POWER_PROTECTION DC_24V tvs，84 条标题')) == []


def test_each_rule_says_what_it_excludes_how_and_on_what_basis():
    bare = {'id': 'G07-023'}
    problems = check(record(bare))
    assert any('excludes' in p for p in problems) and any('basis' in p for p in problems)
    assert any('basis' in p for p in check(record(criterion(basis='engineering'))))


def test_block_types_must_be_in_the_scope():
    data = record(criterion())
    data['blocks'][0]['device_kinds'] = ['varistor']
    assert any('varistor' in p for p in check(data))


def test_report_marks_inference_as_not_a_hard_exclusion():
    lines = '\n'.join(report.render_scheme_criteria(record(criterion('G07-022', 'inference'))))
    assert '方案阶段对照的规则' in lines and '工程推论，不作硬排除' in lines
    assert report.render_scheme_criteria(None) == []
