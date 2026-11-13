"""Condition inputs of a calculation have a source (user 2026-11-04; Matrix R2 CALC-CH-START's hidden 1 A)."""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import audit_design_closure as closure
from current_record import make_current  # noqa: E402
import guideline_criteria
import operating_inputs as oi
import render_design_report

REQ = 'D 口单路最大1.5 A，负载输入电容 ≤1500 µF'
SLEW = {'name': '最大输出斜率', 'value': 0.428519, 'unit': 'V/ms', 'basis': 'derived', 'source': 'calc:C1', 'derivation': '算式'}
CAP = {'name': '单路负载输入电容上限', 'value': 1500, 'unit': 'µF', 'basis': 'requirement', 'source': 'req:R1'}
LOAD = {'name': '启动期负载电流', 'value': 1.5, 'unit': 'A', 'basis': 'requirement', 'source': 'req:R1', 'input_role': 'startup_load'}


def surge(value=2.142778, expr='C*S*1e-3+I', **variables):
    variables = variables or {'C': CAP['name'], 'S': SLEW['name'], 'I': LOAD['name']}
    return {'name': '启动浪涌', 'value': value, 'unit': 'A', 'basis': 'derived', 'source': 'calc:C1', 'derivation': '算式',
            'formula': {'expr': expr, 'vars': variables}}


def calc(parameters, value=1.7, limit=1.8, refs=('U1',), guidelines=(), name='启动浪涌 vs I(OL) 下限'):
    return {'id': 'C1', 'requirements': ['R1'], 'refs': list(refs), 'evidence': [], 'guidelines': list(guidelines),
            'parameters': parameters, 'checks': [{'name': name, 'value': value, 'operator': '<=', 'limit': limit, 'unit': 'A'}]}


COMPONENTS = [{'ref': 'U1', 'lib_id': 'X:TPS2663', 'value': 'TPS26630RGER', 'mpn': 'TPS26630RGER'},
              {'ref': 'U2', 'lib_id': 'X:LM70880', 'value': 'LM70880QRRXRQ1', 'mpn': 'LM70880QRRXRQ1'},
              {'ref': 'J1', 'lib_id': 'Connector:Conn_01x02', 'value': 'Conn', 'fields': {}},
              {'ref': 'F1', 'lib_id': 'Device:Fuse', 'value': 'resettable fuse'}]


def run(row, clarifications=None, work=None, others=None):
    errors = []
    found = oi.audit_roles(dict({'C1': row}, **(others or {})), {'R1': {'id': 'R1', 'text': REQ}, 'CL-A': {'id': 'CL-A', 'text': '启动期负载 0.8 A'}},
                           clarifications or {}, work or {}, {'components': COMPONENTS},
                           lambda code, item: errors.append((code, item)), closure.shown)
    oi.audit_hidden_literals({'C1': row}, lambda code, item: errors.append((code, item)))
    return [e[0] for e in errors], found, errors


class StartupLoadTests(unittest.TestCase):
    def test_the_matrix_r2_form_is_reported_three_ways(self):
        hidden = dict(surge(1.642778), name='启动浪涌（负载电容上限 + 1 A）')
        del hidden['formula']
        codes = run(calc([CAP, SLEW, hidden], 1.64278))[0]
        self.assertEqual(['startup_load_undeclared', 'startup_surge_without_formula', 'hidden_literal_in_name'], codes)

    def test_declared_load_from_a_requirement_passes_and_the_value_flows(self):
        self.assertEqual([], run(calc([CAP, SLEW, LOAD, surge()], 2.14278, 2.2))[0])

    def test_startup_calculation_found_without_citing_the_rule(self):
        _, found, _ = run(calc([LOAD], 1.5, name='软启动电流 vs I(OL)'))
        self.assertEqual({'C1': 'U1'}, found['startup_calculations'])
        self.assertEqual({'C1': 'G03-017'}, run(calc([LOAD], 1.5, refs=(), guidelines=['G03-017'], name='别的'))[1]['startup_calculations'])

    def test_not_a_startup_calculation(self):
        self.assertEqual({}, run(calc([CAP], 1.0, name='D902 8/20 µs 浪涌电流'))[1]['startup_calculations'])
        self.assertEqual({}, run(calc([CAP], 1.0, name='主路电流 vs 门限'))[1]['startup_calculations'])
        self.assertEqual({}, run(calc([CAP], 1.0, refs=('U2',), name='启动电流 vs 限流'))[1]['startup_calculations'], 'a Buck is not a switch part')

    def test_a_fuse_or_a_buck_is_not_a_switch_part(self):
        self.assertEqual(['U1'], run(calc([CAP], 1.0, name='别的'))[1]['hot_parts'])

    def test_number_a_requirement_does_not_show_is_rejected(self):
        codes, _, errors = run(calc([dict(LOAD, value=0.7)], 0.7))
        self.assertEqual(['operating_input_without_source'], codes)
        self.assertIn('没有 0.7', errors[0][1])

    def test_requirement_number_is_compared_with_its_unit(self):
        only_amps, millifarad = {'text': '单路最大1.5 A'}, {'text': '负载输入电容 ≤1.5 mF'}
        written = lambda value, unit, req: oi.written_with_unit(value, unit, req['text'], closure.shown)
        self.assertFalse(written(1500, 'µF', only_amps), '量纲不同，1.5 不算写明')
        self.assertTrue(written(1.5, 'A', only_amps))
        self.assertTrue(written(1500, 'mA', only_amps))
        self.assertTrue(written(1500, 'µF', millifarad))
        self.assertFalse(written(1.5, 'A', {'text': '数字 1.5 没有单位'}))
        self.assertTrue(written(20.4, 'V', {'text': '连续输入 20.4～28.8 V'}), '范围下端取上端的单位')
        self.assertTrue(written(1000, 'Ω', {'text': '1～2 kΩ'}))
        self.assertTrue(written(85, '℃', {'text': '−40～+85 °C'}))
        self.assertTrue(written(32, '', {'text': '不超过 32 单位负载'}), '没有单位的只比数')
        self.assertTrue(written(100, 'kbit/s', {'text': '速率 100 kbit/s'}))
        self.assertFalse(written(100, 'kbit/s', {'text': '速率 200 kbit/s，长 100 m'}))

    def test_whole_check_on_units(self):
        role_cap = dict(CAP, input_role='load_capacitance')
        amps = {'R1': {'id': 'R1', 'text': '单路最大1.5 A'}}

        def codes(p, reqs):
            errors = []
            oi.audit_roles({'C1': calc([p, LOAD], 1.5)}, reqs, {}, {}, {'components': COMPONENTS}, lambda c, i: errors.append(c), closure.shown)
            return errors
        self.assertEqual(['operating_input_without_source'], codes(role_cap, amps))
        self.assertEqual(['operating_input_without_source'], codes(CAP, amps), '没写 input_role 的负载电容在启动计算里一样核')
        self.assertEqual([], codes(role_cap, {'R1': {'id': 'R1', 'text': '单路最大1.5 A，负载输入电容 ≤1.5 mF'}}))

    def test_other_values_the_requirement_writes_are_listed_not_judged(self):
        row = calc([dict(LOAD, value=1)], 1.0)
        reqs = {'R1': {'text': '单路最大1.5 A，预算各路1 A，输入 24 V'}}
        listed = oi.checklist({'C1': row}, reqs, guideline_criteria.load(), [], set(), {})['multiple_candidates']
        self.assertEqual([1.5], listed[0]['others'])
        self.assertEqual([], oi.checklist({'C1': calc([LOAD], 1.5)}, {'R1': {'text': '单路最大1.5 A'}}, guideline_criteria.load(), [], set(), {})['multiple_candidates'])

    def test_sources_that_are_accepted(self):
        for p in (dict(LOAD, value=0.8, source='req:CL-A'),
                  dict(LOAD, basis='guaranteed', ref='U2', source='datasheet:x.pdf#p3', locator='表 1'),
                  dict(LOAD, basis='model', source=None, reason='算', uncertainty=0.2, load_refs=['U2']),
                  dict(LOAD, basis='derived', source='calc:C9', derivation='见 C9')):
            with self.subTest(p=p):
                self.assertEqual([], run(calc([p], p['value']), others={'C9': {'parameters': [LOAD], 'refs': [], 'checks': []}})[0])

    def test_estimate_of_an_external_load_is_rejected(self):
        for p, word in ((dict(LOAD, basis='model', source=None, reason='工程经验'), '不能由 ASG 自定'),
                        (dict(LOAD, basis='design_choice', source=None, ref='U1'), '不能由 ASG 自定'),
                        (dict(LOAD, basis='model', source=None, load_refs=['U1']), '不是本板上的负载'),
                        (dict(LOAD, basis='model', source=None, load_refs=['J1']), '不是本板上的负载'),
                        (dict(LOAD, basis='derived', source='calc:C1'), '写 formula'),
                        (dict(LOAD, basis='derived', source='calc:C9'), 'C9 没有声明'),
                        (dict(LOAD, basis='constant', source=None), '不能作工况来源')):
            with self.subTest(p=p):
                codes, _, errors = run(calc([p], p['value']))
                self.assertEqual(['operating_input_without_source'], codes)
                self.assertIn(word, errors[0][1])

    def test_a_derived_load_rests_on_inputs_that_have_sources(self):
        power = {'name': '恒功率负载', 'value': 30, 'unit': 'W', 'basis': 'model', 'reason': '估'}
        volts = {'name': 'UVLO', 'value': 20, 'unit': 'V', 'basis': 'guaranteed', 'source': 'datasheet:x.pdf#p3', 'locator': 't'}
        load = dict(LOAD, basis='derived', source='calc:C1', formula={'expr': 'P/V', 'vars': {'P': power['name'], 'V': volts['name']}})
        codes, _, errors = run(calc([power, volts, load], 1.5))
        self.assertEqual(['operating_input_without_source'], codes)
        self.assertIn('恒功率负载', errors[0][1])
        self.assertEqual([], run(calc([dict(power, basis='requirement', source='req:CL-P'), volts, load], 1.5))[0][1:])

    def test_a_deferred_question_carries_the_load(self):
        cl = {'CL-X': {'id': 'CL-X', 'answer': {'decision': 'DEFERRED'}}}
        p = dict(LOAD, basis='model', source=None, reason='建议值', clarification='CL-X')
        self.assertEqual(['operating_input_without_source'], run(calc([p], 1.5), cl)[0])
        work = {'W': {'stage': 'requirement', 'status': 'open', 'clarification': 'CL-X', 'calculations': ['C1']}}
        self.assertEqual([], run(calc([p], 1.5), cl, work)[0])
        self.assertEqual(['operating_input_without_source'], run(calc([p], 1.5), {'CL-X': {'answer': {'decision': 'DECIDED'}}}, work)[0])

    def test_surge_value_must_be_a_parameter_and_use_the_load(self):
        self.assertEqual(['startup_surge_unbound'], run(calc([LOAD], 1.29))[0])
        cap_only = surge(0.642778, 'C*S*1e-3', C=CAP['name'], S=SLEW['name'])
        self.assertEqual(['startup_surge_ignores_load'], run(calc([CAP, SLEW, LOAD, cap_only], 0.642778))[0])
        no_load = dict(LOAD, value=0, basis='guaranteed', source='datasheet:x.pdf#p3', locator='后级 UVLO')
        self.assertEqual([], run(calc([CAP, SLEW, no_load, cap_only], 0.642778))[0], 'a load of zero with a source need not be added')

    def test_an_undocumented_current_in_the_surge_formula_is_not_enough(self):
        inner = {'name': '电容电流', 'value': 1.642778, 'unit': 'A', 'basis': 'derived', 'source': 'calc:C1', 'derivation': '藏了 1 A'}
        hiding = surge(3.142778, 'A+I', A=inner['name'], I=LOAD['name'])
        self.assertEqual(['startup_surge_without_formula'], run(calc([LOAD, inner, hiding], 3.142778, 4))[0])

    def test_estimated_capacitance_of_the_load_needs_a_source_in_a_startup_calculation(self):
        wrong = dict(CAP, basis='model', source=None, reason='接口表写入的设计约束')
        self.assertIn('operating_input_without_source', run(calc([wrong, LOAD], 1.5))[0])
        self.assertEqual([], run(calc([wrong], 1.0, refs=('U2',), name='别的'))[0], 'outside a startup calculation it is only listed')


class FormulaTests(unittest.TestCase):
    def test_hidden_constants_are_rejected_wherever_they_sit(self):
        for expr in ('C*S*1e-3+1', '1+C*S*1e-3', 'C*S*1e-3-0.5', '(C*S+1)*1e-3', 'C*S*1.2', 'max(C*S,1)', '(C*S*1e-3+0.5+0.5)'):
            with self.subTest(expr=expr):
                self.assertTrue(oi.literal_problems(ast.parse(expr, mode='eval').body))

    def test_textbook_forms_are_allowed(self):
        for expr in ('C*S*1e-3+I', '0.5*C*V**2', 'V*(1+R1/R2)', 'V*(1-R1/R2)', 'I/1000', 'sqrt(I**2+V**2)', 'C*S/1e3'):
            with self.subTest(expr=expr):
                self.assertEqual([], oi.literal_problems(ast.parse(expr, mode='eval').body))

    def test_recomputed_from_declared_parameters(self):
        self.assertEqual(['formula_mismatch'], run(calc([CAP, SLEW, LOAD, surge(2.5)], 2.5, 2.6))[0], '差的部分没声明')
        self.assertEqual(['formula_schema'], run(calc([CAP, SLEW, LOAD, surge(C='没有这个', S=SLEW['name'], I=LOAD['name'])], 2.14278, 2.2))[0])
        self.assertIn('formula_schema', run(calc([LOAD, dict(surge(), formula={'expr': 'I', 'vars': []})], 2.14278, 2.2))[0])
        self.assertEqual(['formula_schema'], run(calc([LOAD, surge(expr='__import__("os")', I=LOAD['name'])], 2.14278, 2.2))[0])
        self.assertEqual(['formula_schema'], run(calc([LOAD, surge(-1, '(0-I)**0.5', I=LOAD['name'])], -1, 2.2))[0])

    def test_any_calculation_may_write_a_formula(self):
        bad = {'name': '输出', 'value': 3, 'unit': 'V', 'basis': 'derived', 'source': 'calc:C1', 'derivation': 'x',
               'formula': {'expr': 'A+1', 'vars': {'A': '输入'}}}
        codes = run(calc([{'name': '输入', 'value': 2, 'unit': 'V', 'basis': 'requirement', 'source': 'req:R1'}, bad], 1.0, refs=(), name='别的'))[0]
        self.assertEqual(['formula_hidden_literal'], [c for c in codes if c.startswith('formula')])


class HiddenLiteralTests(unittest.TestCase):
    def found(self, words, *params):
        row = {'parameters': list(params), 'checks': [{'name': words}]}
        errors = []
        oi.audit_hidden_literals({'C': row}, lambda code, item: errors.append(item))
        return errors

    def test_added_numbers_in_names(self):
        for words in ('负载电容上限 + 1 A', 'VIN+5 V 耐压', 'VBR 上限＋1 V 动态', 'VIN − 0.7 V'):
            self.assertTrue(self.found(words), words)

    def test_signs_rails_and_declared_numbers_are_not_flagged(self):
        for words in ('+5V 轨总电流', '共模 +7 V vs 接收共模', '+30 V 下 IP 电压', '24V+5V 轨负载', '20-30 V', '（+5 V）'):
            self.assertEqual([], self.found(words), words)
        self.assertEqual([], self.found('负载电容上限 + 1 A', {'name': '负载', 'value': 1000, 'unit': 'mA'}))
        self.assertTrue(self.found('负载电容上限 + 1 A', {'name': '负载', 'value': 1, 'unit': 'V'}))


class ChecklistTests(unittest.TestCase):
    library = guideline_criteria.load()

    def test_classifier_keeps_datasheet_data_out(self):
        self.assertEqual(['startup_load'], oi.classify_input('启动期间负载特性（阻性 / 恒流 / 恒功率；后级 UVLO 开启点）'))
        self.assertEqual([], oi.classify_input('运放手册保证值（共模范围、输出摆幅、输出电流、GBW、SR、失调、偏置、噪声）'))
        self.assertEqual(['source_impedance', 'input_window'], oi.classify_input('G01 电源输入工况：输入电压上升斜率范围（含慢上电）与源阻抗'))
        self.assertEqual([], oi.classify_input('变压器线缆侧中心抽头'))

    def test_library_coverage_is_pinned_so_a_rebuilt_library_shows_up(self):
        stats = oi.library_stats(self.library)
        self.assertIn('G03-017', stats['startup_load'] + stats['load_capacitance'])
        self.assertIn('G03-013', stats['startup_load'])
        self.assertIn('G03-019', stats['startup_load'])
        self.assertIn('G02-006', stats['ambient_temperature'])
        self.assertIn('G03-011', stats['source_impedance'])
        rules = {i for ids in stats.values() for i in ids}
        self.assertGreaterEqual(len(rules), 100)
        self.assertLess(len(rules), 140, 'broader than this reads every rule as a condition')

    def test_list_names_weak_parameters_and_what_is_not_declared(self):
        row = calc([dict(CAP, basis='model', source=None), {'name': '组合波源阻抗', 'value': 2, 'unit': 'Ω', 'basis': 'constant', 'reason': '标准'}], 1.0, refs=(), name='别的')
        row['guidelines'] = ['G03-018']
        listed = oi.checklist({'C1': row}, {'R1': {'text': '输入 20～30 V'}}, self.library, ['G03-018', 'G02-006'], {'U1'}, {})
        self.assertEqual([('C1', '单路负载输入电容上限')], [(w['calculation'], w['parameter']) for w in listed['weak_sources']])
        self.assertEqual(['U1'], listed['switch_parts_without_startup_calculation'])
        self.assertEqual({'input_window': ['G03-018']}, listed['calculations'][0]['missing'], '名字里有源阻抗的算声明了')
        by_role = {r['role']: r for r in listed['roles']}
        self.assertEqual(['R1'], by_role['input_window']['requirements'])
        self.assertFalse(by_role['ambient_temperature']['sourced'])

    def test_report_section(self):
        found = {'declared': [{'calculation': 'C1', 'parameter': '启动期负载电流', 'role': 'startup_load', 'basis': 'requirement', 'value': 1.5, 'unit': 'A', 'source': 'req:R1'}],
                 'checklist': {'weak_sources': [{'calculation': 'C2', 'parameter': '负载电容', 'value': 1, 'unit': 'µF', 'basis': 'model'}],
                               'switch_parts_without_startup_calculation': ['U9'],
                               'calculations': [{'calculation': 'C3', 'missing': {'ambient_temperature': ['G02-006']}}],
                               'roles': [{'role': 'ambient_temperature', 'title': '环境温度', 'rules': 3, 'requirements': []}]}}
        words = '\n'.join(render_design_report.render_operating_inputs(found))
        found['checklist']['multiple_candidates'] = [{'calculation': 'C1', 'parameter': '启动期负载电流', 'value': 1, 'unit': 'A', 'requirement': 'R1', 'others': [1.5]}]
        self.assertIn('不利值', '\n'.join(render_design_report.render_operating_inputs(found)))
        for piece in ('启动期负载电流', 'req:R1', '负载电容', 'U9', '环境温度', '**没有**', 'C3'):
            self.assertIn(piece, words)
        self.assertEqual([], render_design_report.render_operating_inputs(None))


class WholeAuditTests(unittest.TestCase):
    def record(self, d, parameter, check_value=1.5):
        intent = Path(d) / 'electrical-intent.json'
        intent.write_text(json.dumps({'schema_version': 1, 'components': COMPONENTS, 'nets': [], 'no_connect': []}), encoding='utf-8')
        return intent, {'schema_version': 1, 'parameter_version': 3, 'intent_sha256': closure.sha256(intent), 'coverage': 'complete',
                        'evidence': [], 'work_items': [],
                        'requirements': [{'id': 'R1', 'status': 'design_supported', 'implementation': 'U1', 'refs': ['U1'], 'evidence': [], 'text': REQ}],
                        'calculations': [{'id': 'C1', 'requirements': ['R1'], 'evidence': [], 'refs': ['U1'], 'coverage': 'bounded', 'conclusion': 'supported',
                                          'parameters': [parameter],
                                          'checks': [{'name': '启动电流 vs 限流', 'value': check_value, 'operator': '<=', 'limit': 1.8, 'unit': 'A',
                                                      'limit_basis': 'requirement', 'limit_source': 'req:R1'}]}]}

    def codes(self, parameter):
        with tempfile.TemporaryDirectory() as d:
            intent, record = self.record(d, parameter)
            out = closure.audit(make_current(record, intent, Path(d)), intent, Path(d))
        return {e['code'] for e in out['errors']}, out

    def test_audit_runs_the_check_and_reports_the_list(self):
        unmarked = {k: v for k, v in LOAD.items() if k != 'input_role'}
        self.assertIn('startup_load_undeclared', self.codes(unmarked)[0])
        codes, out = self.codes(LOAD)
        self.assertFalse(codes & {'startup_load_undeclared', 'operating_input_without_source'}, codes)
        self.assertEqual('startup_load', out['operating_inputs']['declared'][0]['role'])
        self.assertIn('checklist', out['operating_inputs'])

    def test_a_declared_load_above_the_limit_fails_the_calculation(self):
        with tempfile.TemporaryDirectory() as d:
            intent, record = self.record(d, LOAD, 2.0)
            record['calculations'][0]['conclusion'] = 'failed'
            out = closure.audit(record, intent, Path(d))
        self.assertIn('calculation_failed', {p['code'] for p in out['pending']})


if __name__ == '__main__':
    unittest.main()
