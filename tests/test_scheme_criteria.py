"""Task C3.1: key functional blocks list the rules that can exclude a candidate scheme (record/scheme-criteria.json)."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import guideline_criteria  # noqa: E402
import render_design_report as report  # noqa: E402

BUNDLE = guideline_criteria.load()


def closing_check(name):
    return {'name': name, 'value': 30, 'operator': '<=', 'limit': 36, 'unit': 'V'}


def closure(types=('POWER_PROTECTION', 'DC_24V'), kinds=('tvs', 'mosfet'), calculations=None):
    # The values the records below leave to task C4.2 are closed by a calculation citing their rules (A4).
    if calculations is None:
        calculations = [{'id': 'CALC-CLAMP', 'guidelines': ['G07-022', 'G07-023', 'G07-030'],
                         'checks': [closing_check(n + ' 对 下游绝对最大值') for n in ('负向浪涌残压', '负向残压', '钳位器件脉冲能量')]}]
    return {'guideline_scope': {'library_version': BUNDLE['library_version'], 'baseline': 'industrial_telecom',
                                'circuit_types': list(types), 'device_kinds': list(kinds)},
            'calculations': calculations}


def criterion(gid='G07-023', basis='standard'):
    return {'id': gid, 'excludes': '只在输入侧做保护的方案', 'basis': basis,
            'how': 'OUT 口加负向钳位与反灌阻断', 'defer': ['负向浪涌残压']}


def record(*criteria, ports=True, searched=''):
    return {'version': 1, 'blocks': [{'block': '24 V 入口与输出保护', 'circuit_types': ['POWER_PROTECTION', 'DC_24V'],
                                      'device_kinds': ['tvs'], 'ports': ports, 'searched': searched,
                                      'decisive': [{'condition': '现场口是否可能反接', 'value': '可能'}],
                                      'candidates': [{'name': '输出钳位', 'source': ['user:2026-11-07'], 'status': 'selected', 'reason': '覆盖输出口'},
                                                     {'name': '只保护输入', 'source': ['user:2026-11-07'], 'status': 'rejected', 'reason': '不覆盖输出口'}],
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


def test_the_example_in_knowledge_package_passes_the_check():
    assert check(document_example()) == []


def document_example():
    doc = (ROOT / 'references' / 'knowledge-package.md').read_text(encoding='utf-8')
    return json.loads(re.search(r'```json\n(.*?)```', doc, re.S).group(1))


def run_cli(root):
    return subprocess.run([sys.executable, str(ROOT / 'scripts' / 'check_scheme_criteria.py'), str(root)],
                          capture_output=True, text=True)


def write_records(root, scheme):
    records = root / 'record'
    records.mkdir()
    (records / 'scheme-criteria.json').write_text(json.dumps(scheme), encoding='utf-8')
    (records / 'requirements.json').write_text(json.dumps({'schema_version': 1, 'guideline_scope': closure()['guideline_scope']}),
                                               encoding='utf-8')
    return records


def test_cli_rejects_the_pt100_rerun_record(tmp_path):
    # Verbatim evalset record: schema_version/rules/candidate_effect instead of the documented fields.
    fixture = ROOT / 'tests' / 'fixtures' / 'scheme-criteria' / 'rt-afe-pt100.json'
    write_records(tmp_path, json.loads(fixture.read_text(encoding='utf-8')))
    result = run_cli(tmp_path)
    assert result.returncode != 0
    assert 'version 1' in result.stdout and 'FAIL' in result.stdout


def test_cli_accepts_the_documented_example(tmp_path):
    write_records(tmp_path, document_example())
    result = run_cli(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS' in result.stdout


@pytest.mark.parametrize('filename,content', [
    ('scheme-criteria.json', None), ('scheme-criteria.json', '{'),
    ('requirements.json', None), ('requirements.json', '{'), ('requirements.json', 'null'),
])
def test_cli_reports_unreadable_or_missing_records(tmp_path, filename, content):
    records = write_records(tmp_path, document_example())
    if content is None:
        (records / filename).unlink()
    else:
        (records / filename).write_text(content, encoding='utf-8')
    result = run_cli(tmp_path)
    assert result.returncode != 0
    assert filename in result.stdout and 'FAIL' in result.stdout
    assert 'Traceback' not in result.stderr


@pytest.mark.parametrize('nature', ['method', 'project', None])
def test_standard_basis_requires_shall_or_should(nature):
    # Method/project cards cannot acquire standard authority through the record's basis field.
    from copy import deepcopy
    bundle = deepcopy(BUNDLE)
    card = next(r for r in bundle['criteria'] if r['id'] == 'G07-023')
    card['nature'] = nature
    problems = report.check_scheme_criteria(record(criterion()), closure(), bundle)
    assert len(problems) == 1
    assert all(word in problems[0] for word in ('G07-023', 'standard', 'nature', 'requirement', 'inference'))
    for basis in ('requirement', 'inference'):
        assert report.check_scheme_criteria(record(criterion(basis=basis)), closure(), bundle) == []


@pytest.mark.parametrize('gid', ['G07-022', 'G07-023'])
def test_standard_basis_accepts_shall_and_should(gid):
    assert check(record(criterion(gid))) == []


def test_cli_rejects_a_method_rule_marked_as_standard(tmp_path):
    assert next(r for r in BUNDLE['criteria'] if r['id'] == 'G07-030')['nature'] == 'method'
    write_records(tmp_path, record(criterion('G07-030')))
    result = run_cli(tmp_path)
    assert result.returncode != 0
    assert all(word in result.stdout for word in ('G07-030', 'standard', 'requirement', 'inference', 'FAIL'))


def test_scheme_format_explains_basis_limits_and_nonexcluding_rules():
    doc = (ROOT / 'references' / 'knowledge-package.md').read_text(encoding='utf-8')
    assert '`standard` 只用于 `nature` 为 `shall`/`should` 的规则' in doc
    assert '`datasheet_abs_max` 只指器件手册 Absolute Maximum Ratings 表里的值，推荐工作条件不算' in doc
    assert '没有排除候选的规则不写进 `criteria`，放 `searched`' in doc


def test_candidates_require_decisive_values_sources_and_reasons():
    data = record(criterion())
    b = data['blocks'][0]
    b.pop('decisive')
    b['candidates'][0]['source'] = []
    b['candidates'][1].pop('reason')
    problems = check(data)
    assert any('decisive' in p for p in problems)
    assert any('source' in p for p in problems)
    assert any('reason' in p for p in problems)


@pytest.mark.parametrize('candidates', [None, [], ['甲'], [{'name': '甲', 'source': ['wiki:线索']}],
    [{'name': '甲', 'source': ['user:2026-11-07'], 'status': 'alternate', 'reason': '备选'}]])
def test_incomplete_comparison_is_rejected(candidates):
    data = record(criterion())
    data['blocks'][0]['candidates'] = candidates
    assert check(data)


def test_only_one_viable_requires_search_explanation():
    data = record(criterion())
    b = data['blocks'][0]
    b['candidates'] = b['candidates'][:1]
    assert any('only_viable' in p for p in check(data))
    b['only_viable'] = '查过两种控制器手册和反激参考设计，其余不能满足输入电压'
    assert check(data) == []


@pytest.mark.parametrize('unverified', [True, '未证实', 'false'])
def test_unverified_candidate_cannot_be_selected(unverified):
    data = record(criterion())
    data['blocks'][0]['candidates'][0]['unverified'] = unverified
    assert any('未证实' in p for p in check(data))


def test_unverified_rejected_candidate_is_allowed_with_source():
    data = record(criterion())
    data['blocks'][0]['candidates'][1]['unverified'] = True
    assert check(data) == []


@pytest.mark.parametrize('statuses', [('selected', 'selected'), ('rejected', 'rejected')])
def test_exactly_one_selected_candidate(statuses):
    data = record(criterion())
    for c, status in zip(data['blocks'][0]['candidates'], statuses):
        c['status'] = status
    assert any('只有一个 selected' in p for p in check(data))


def test_cli_is_the_c3_gate_and_leaves_the_page_plan_to_c6(tmp_path):
    # SKILL.md 架构 (user 2026-11-09): the task C3.1 gate reads no page plan; check_module.py C6 compares them.
    data = record(criterion())
    b = data['blocks'][0]
    b['candidates'][0]['circuit'] = 'dc-reverse-protection#甲'
    records = write_records(tmp_path, data)
    assert run_cli(tmp_path).returncode == 0
    plan = {'schema_version': 1, 'pages': [{'file': 'a.kicad_sch', 'blocks': {b['block']: ['U1']},
                                          'key_blocks': [b['block']], 'circuits': {b['block']: 'dc-reverse-protection#乙'}}]}
    (records / 'page-plan.json').write_text(json.dumps(plan))
    assert run_cli(tmp_path).returncode == 0


def test_scheme_against_plan_is_the_c6_cross_check():
    data = record(criterion())
    b = data['blocks'][0]
    b['candidates'][0]['circuit'] = 'dc-reverse-protection#甲'
    plan = {'schema_version': 1, 'pages': [{'file': 'a.kicad_sch', 'blocks': {b['block']: ['U1']},
                                          'key_blocks': [b['block']], 'circuits': {b['block']: 'dc-reverse-protection#乙'}}]}
    assert any('circuits 不一致' in p for p in report.scheme_against_plan(data, plan))
    plan['pages'][0]['circuits'][b['block']] = 'dc-reverse-protection#甲'
    assert report.scheme_against_plan(data, plan) == []
    plan['pages'][0]['blocks'] = {'别的块': ['U1']}
    plan['pages'][0]['key_blocks'] = ['别的块']
    problems = report.scheme_against_plan(data, plan)
    assert any('没有对应功能块' in p for p in problems) and any('别的块' in p for p in problems)
    # The whole-board report still makes the same cross-check.
    assert any('没有对应功能块' in p for p in report.check_scheme_criteria(data, closure(), plan=plan))


def test_key_page_block_requires_comparison_even_without_key_scope_type():
    plan = {'pages': [{'key_blocks': ['对外接口']}]}
    assert report.check_scheme_criteria(None, {}, plan=plan)
    assert any('对外接口' in p for p in report.check_scheme_criteria(record(criterion()), closure(), plan=plan))


def test_comparison_is_in_the_report():
    data = record(criterion())
    rendered = '\n'.join(report.render_scheme_criteria(data))
    for value in ('功能块方案比较', '现场口是否可能反接', '输出钳位', '只保护输入', 'user:2026-11-07', '选定', '淘汰'):
        assert value in rendered


# A4 (whole-board baseline 2026-11-07): the calibration board left "SM712 钳位对收发器总线额定" to task C4.2; CALC-RS485
# cited G05-033 and G04-005 but compared no clamp voltage with the transceiver's bus rating.
def test_a_deferred_value_no_calculation_computes_is_not_closed():
    problems = check(record(criterion()), closure(calculations=[]))
    assert len(problems) == 1 and '负向浪涌残压' in problems[0] and '没有闭合' in problems[0]


def test_a_rule_cited_by_a_calculation_that_skips_the_value_is_covered_in_form_only():
    rs485 = {'id': 'CALC-RS485', 'guidelines': ['G07-023'],
             'checks': [closing_check('D501 反向工作电压 对 总线共模下限幅值 7 V')]}
    problems = check(record(criterion()), closure(calculations=[rs485]))
    assert len(problems) == 1 and 'calc:CALC-RS485' in problems[0] and '形式覆盖' in problems[0]


def test_the_closing_check_must_be_in_a_calculation_citing_the_rule():
    other = {'id': 'CALC-OTHER', 'guidelines': ['G07-022'], 'checks': [closing_check('负向浪涌残压 对 36 V')]}
    assert check(record(criterion()), closure(calculations=[other]))


def test_a_check_without_a_conclusion_does_not_close_the_value():
    bare = {'id': 'CALC-CLAMP', 'guidelines': ['G07-023'], 'checks': [{'name': '负向浪涌残压', 'value': 30}]}
    assert check(record(criterion()), closure(calculations=[bare]))


def test_a_check_named_otherwise_closes_the_value_through_its_defer_field():
    named = closing_check('D501 钳位 对 U501 A/B 绝对最大 14 V')
    calc = {'id': 'CALC-RS485', 'guidelines': ['G07-023'], 'checks': [named]}
    assert check(record(criterion()), closure(calculations=[calc]))
    named['defer'] = '负向浪涌残压'
    assert check(record(criterion()), closure(calculations=[calc])) == []
    named['defer'] = ['别的数值', '负向 浪涌残压']
    assert check(record(criterion()), closure(calculations=[calc])) == []
