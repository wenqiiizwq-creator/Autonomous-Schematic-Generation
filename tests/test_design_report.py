"""One generated report plus a small fixed folder; numbers come only from the records."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_design_closure import audit, sha256
from render_design_report import num, render, render_sha256, REPORT
from pack_design import pack
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_citations import pdf

JARGON = ('合同', '冻结', '门禁', '原生', '闭环', '移交', 'SR', 'schematic-review', 'design_supported', 'handoff')


class Delivery:
    """Synthetic delivery folder in the fixed layout."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'v1'
        # Cited datasheets are real PDFs in a private library, so citations are checked page by page.
        wiki = Path(self.tmp.name) / 'library'
        self.env = mock.patch.dict(os.environ, {'HARDWARE_WIKI': str(wiki)})
        self.env.start()
        (wiki / 'raw/Datasheet/08_电源管理').mkdir(parents=True)
        (wiki / 'raw/Datasheet/08_电源管理/X - XYZ100.pdf').write_bytes(pdf(['VIN 4.5 V to 18 V', 'SOIC-8', 'COUT']))
        self.record = self.root / 'record'
        for d in ('原理图', '设计资料', 'record/evidence'):
            (self.root / d).mkdir(parents=True)
        for name in ('board.kicad_pro', 'board.kicad_sch', 'schematic.pdf', 'netlist.xml', 'BOM.csv'):
            (self.root / '原理图' / name).write_text('x')
        (self.root / '设计资料' / '方案与选型依据.md').write_text('# basis')
        (self.record / 'evidence' / 'design.md').write_text('regulator design basis')
        self.write('electrical-intent.json', {'components': [{'ref': 'U1', 'value': 'XYZ100', 'mpn': 'XYZ100',
                                                                   'datasheet': '设计资料/X - XYZ100.pdf'}, {'ref': 'R1'}]})
        (self.root / '设计资料' / 'X - XYZ100.pdf').write_bytes(pdf(['VIN 4.5 V to 18 V  IOUT 3.5 A  EN', 'SOIC-8  OVP 25 C']))
        (self.root / '设计资料' / 'Y - ABC200.pdf').write_bytes(pdf(['IOUT 2 A']))
        self.selection = {'schema_version': 1, 'library_root': str(self.root), 'roles': [
            {'role': '稳压器', 'refs': ['U1'], 'requirements': ['R-OUT'], 'decisive': [
                {'param': '输入电压范围', 'op': 'covers', 'limit': [9, 14], 'unit': 'V', 'requirement': 'R-OUT'},
                {'param': '输出电流', 'op': '>=', 'limit': 3, 'unit': 'A'},
                {'param': '封装', 'op': 'equals', 'limit': 'SOIC-8'},
                {'param': '使能引脚', 'op': 'has', 'limit': True}],
             'sources': ['catalog:08_电源管理/DC-DC 降压转换器 (Buck)'], 'candidates': [
                 {'mpn': 'XYZ100', 'vendor': 'X', 'status': 'selected', 'datasheet': '设计资料/X - XYZ100.pdf',
                  'reason': '电流裕量够，库里资料全', 'external_dependencies': [], 'values': {
                      '输入电压范围': {'value': [4.5, 18], 'page': 1}, '输出电流': {'value': 3.5, 'page': 1},
                      '封装': {'value': 'soic8', 'page': 2}, '使能引脚': {'value': True, 'page': 1}}},
                 {'mpn': 'ABC200', 'vendor': 'Y', 'status': 'rejected', 'datasheet': '设计资料/Y - ABC200.pdf',
                  'reason': '最大 2 A 不满足', 'values': {'输出电流': {'value': 2, 'page': 1}}}]}]}
        self.write('selection.json', self.selection)
        self.closure = {
            'schema_version': 1, 'parameter_version': 1, 'gap_version': 1, 'coverage': 'complete',
            'intent_sha256': sha256(self.record / 'electrical-intent.json'),
            'evidence': [{'id': 'E1', 'path': 'record/evidence/design.md',
                          'sha256': sha256(self.record / 'evidence' / 'design.md'), 'locator': 'section 1'}],
            'requirements': [{'id': 'R-OUT', 'status': 'conditional', 'refs': ['U1'], 'evidence': ['E1'],
                              'implementation': 'U1 output path', 'depends_on': ['W-FW', 'W-CALC', 'W-TEST']}],
            'work_items': [
                {'id': 'W-CALC', 'stage': 'design', 'status': 'open', 'consequence_class': 'margin', 'occurrence': 'normal', 'requirements': ['R-OUT'],
                 'evidence': [], 'owner': '设计', 'action': '补算输出电容纹波电流'},
                {'id': 'W-FW', 'stage': 'external', 'status': 'open', 'consequence_class': 'damage', 'occurrence': 'normal', 'requirements': ['R-OUT'],
                 'evidence': [], 'owner': 'X 公司应用支持', 'action': '取得过压保护配置表后重算 C1', 'fallback': '评估独立硬件过压关断',
                 'missing': [{'source': 'datasheet:设计资料/X - XYZ100.pdf#p2', 'given': '过压门限只在 25°C 规定',
                              'needed': '全温过压门限与关断时延'}],
                 'why_external': '过压动作由固件配置决定，手册没有公开', 'calculations': ['C1'],
                 'consequence': '过压时输出电容过充，负载损坏', 'questions': ['全温下过压门限的范围', '从检测到关断的最大时延']},
                {'id': 'W-TEST', 'stage': 'validation', 'status': 'handoff', 'requirements': ['R-OUT'],
                 'evidence': ['E1'], 'owner': '样机验证', 'action': '满载温升测试'}],
            'calculations': [{'id': 'C1', 'requirements': ['R-OUT'], 'evidence': ['E1'], 'refs': ['U1'],
                              'coverage': 'partial', 'conclusion': 'conditional', 'omitted_terms': ['ripple'],
                              'missing_guarantee': '纹波电流在 105°C 的额定',
                              'parameters': [{'name': 'IOUT', 'ref': 'U1', 'value': 3.5, 'unit': 'A', 'basis': 'guaranteed',
                                              'source': 'datasheet:设计资料/X - XYZ100.pdf#p1', 'locator': '电气特性表 IOUT'}],
                              'checks': [{'name': '输出纹波', 'value': 18, 'operator': '<=', 'limit': 30, 'unit': 'mV'}]}]}
        self.write('design-closure.json', self.closure)
        self.write('design-closure-audit.json', audit(self.closure, self.record / 'electrical-intent.json', self.root))
        self.write('summary.json', {'status': 'INCOMPLETE', 'sheets': ['a', 'b'], 'gates': {
            'erc': {'status': 'PASS', 'violations': 0}, 'intent_netlist': {'status': 'PASS', 'errors': 0},
            'geometry': {'status': 'INSUFFICIENT'}, 'design_closure': {'status': 'INCOMPLETE'}}})
        self.pdf = render_sha256(self.root / '原理图' / 'schematic.pdf')
        self.write('visual-review.json', {'status': 'REVIEWED', 'pdf_sha256': self.pdf, 'pages': [
            {'page': 1, 'file': 'board.kicad_sch', 'paths': ['VIN to VOUT'], 'problems': []}]})
        self.write('page-plan.json', {'schema_version': 1, 'pages': [
            {'file': 'board.kicad_sch', 'reader_tasks': ['跟随 VIN 到 VOUT 的能量流'], 'blocks': {'稳压': ['U1', 'R1']},
             'patterns': {'稳压': 'output-filter-storage#电解/聚合物 + MLCC 并联'}}]})
        self.write('lessons.json', {'schema_version': 1, 'events': [
            {'source': 'datasheet:raw/Datasheet/08_电源管理/X - XYZ100.pdf#p3', 'cause': 'none',
             'why_none': 'p.3 的输出电容要求与 part-roles.md 降压转换器行一致'}]})
        self.write('delivery-evidence.json', {'schema_version': 1})

    def cleanup(self):
        self.env.stop()
        self.tmp.cleanup()

    def write(self, name, value):
        (self.record / name).write_text(json.dumps(value, ensure_ascii=False))

    def report(self, notes=None):
        return render(self.root, notes)


class DesignReportTests(unittest.TestCase):
    def setUp(self):
        self.d = Delivery()
        self.addCleanup(self.d.cleanup)

    def test_conclusion_counts_and_what_is_missing(self):
        text, problems = self.d.report()
        self.assertEqual(problems, [])
        lines = [l for l in text.splitlines() if l.strip()]
        self.assertEqual(lines[1], '## 结论')
        self.assertEqual(lines[2], '- **规模**：器件 2 个，图纸 2 页。')
        self.assertEqual(lines[3], '- **图纸自动检查**：共 3 项。通过（PASS） 2 项，没通过（FAIL） 0 项，资料不足（INSUFFICIENT） 1 项。')
        self.assertIn('- **需求**：共 1 条。有设计依据 0 条，有条件成立 1 条，还没有设计 0 条。', text)
        self.assertIn('- **设计完成状态**：未完成。未完成项：', text)
        self.assertIn('1 项图纸自动检查资料不足或未执行：图面几何（重叠、穿线）', text)
        self.assertIn('2 件未关闭项（设计未完成 1 件，外部资料缺口 1 件）', text)

    def test_design_sheet_acceptance_is_listed_apart(self):
        # A custom magnetic closed on its design sheet (user 2026-10-28: 按 A 实施): its sample acceptance is shown, not pending.
        result = {'status': 'PASS', 'errors': [], 'pending': [], 'acceptance': ['L1：样件按设计单 MS-L1-01 验收'],
                  'definition': {'L1': 'complete'}, 'selection': {'L1': 'by_design_sheet'}}
        with mock.patch('render_design_report.package_audit', return_value=result):
            text, _ = self.d.report()
        self.assertIn('- **器件性能流程**：通过；性能定义完整 1 项；设计单定制已核实 1 项。', text)
        self.assertIn('- **样件验收（外部，不挡交付，未定型）**：L1：样件按设计单 MS-L1-01 验收。', text)
        self.assertNotIn('器件性能定义、选型或原生图面核对尚未完成', text)

    def test_one_todo_list_ordered_by_consequence(self):
        text, _ = self.d.report({'items': {'W-FW': '固件过压保护配置还没拿到。'}})
        section = text.split('## 未关闭项')[1].split('\n## ')[0]
        self.assertLess(section.index('W-FW（P0：可能损坏器件或危及安全；器件损坏，正常工作）'), section.index('W-CALC（P2'))
        self.assertIn('- **替代方案**：评估独立硬件过压关断', section)
        self.assertIn('固件过压保护配置还没拿到。', section)
        self.assertNotIn('W-TEST', section)

    def test_external_gap_shows_what_is_missing_and_what_to_ask(self):
        text, problems = self.d.report()
        self.assertEqual([], problems)
        self.assertIn('- **外部资料缺口**：1 件（X 公司应用支持 1 件），影响有条件成立的计算 1 项。', text)
        section = text.split('## 未关闭项')[1].split('\n## ')[0]
        self.assertIn('  - 手册已给出：过压门限只在 25°C 规定；设计所需：全温过压门限与关断时延'
                      '（datasheet:设计资料/X - XYZ100.pdf#p2）', section)
        self.assertIn('  - C1：纹波电流在 105°C 的额定', section)
        self.assertIn('- **外部依赖原因**：过压动作由固件配置决定，手册没有公开', section)
        self.assertIn('- **关闭方式**：取得过压保护配置表后重算 C1', section)
        self.assertIn('  2. 从检测到关断的最大时延', section)
        asks = text.split('## 外部资料需求')[1].split('\n## ')[0]
        self.assertIn('### X 公司应用支持', asks)
        self.assertIn('1. 全温下过压门限的范围（W-FW）', asks)

    def test_external_item_without_gap_record_is_a_problem(self):
        del self.d.closure['gap_version']
        self.d.write('design-closure.json', self.d.closure)
        _, problems = self.d.report()
        self.assertTrue(any('gap_version 2' in p for p in problems), problems)

    def ask_user(self, decision='DEFERRED'):
        c = self.d.closure
        proposal = '待机功耗 ≤0.1 W（230 Vac 空载）'
        c['clarifications'] = [{'id': 'CL-STBY', 'requirement_ids': ['R-OUT'], 'found_in': '2.2',
                                'question': '待机功耗上限没给，启动电阻取值没有依据', 'requirement_text': '需求规格 §3：未提及待机功耗',
                                'proposed_requirement': proposal}]
        if decision:
            c['clarifications'][0]['answer'] = {'decision': decision, 'text': '先按建议设计，量产前再定', 'by': '产品负责人',
                                                'date': '2026-10-27', 'source': {'source': '对话记录', 'locator': '2026-10-27 第 1 问'}}
        c['work_items'].append({'id': 'W-STBY', 'stage': 'requirement', 'status': 'open', 'consequence_class': 'optimization', 'occurrence': 'normal',
                                'requirements': ['R-OUT'], 'evidence': [], 'owner': '产品负责人', 'clarification': 'CL-STBY',
                                'action': '确定待机功耗上限', 'assumption': proposal})
        c['requirements'][0]['depends_on'].append('W-STBY')
        self.d.write('design-closure.json', c)
        self.d.write('design-closure-audit.json',
                     audit(c, self.d.record / 'electrical-intent.json', self.d.root))

    def test_requirement_questions_called_out_and_listed_first(self):
        self.ask_user()
        text, problems = self.d.report()
        self.assertEqual(problems, [])
        conclusion = text.split('## 结论')[1].split('\n## ')[0]
        self.assertIn('- **用户暂缓的需求**：1 件（W-STBY）。本版按建议条文设计', conclusion)
        self.assertIn('3 件未关闭项（用户暂缓的需求 1 件，设计未完成 1 件，外部资料缺口 1 件）', conclusion)
        self.assertIn('用户暂缓的需求排最前', conclusion)
        self.assertIn('- **需求澄清**：问过用户 1 个问题。用户暂缓 1 个。', conclusion)
        section = text.split('## 未关闭项')[1].split('\n## ')[0]
        self.assertLess(section.index('W-STBY（P3'), section.index('W-FW（P0'))
        self.assertIn('- **类型**：用户暂缓的需求', section)
        self.assertIn('- **需求澄清**：CL-STBY', section)
        self.assertIn('- **设计假设**：待机功耗 ≤0.1 W（230 Vac 空载）', section)
        self.assertIn('| 未关闭项：用户暂缓的需求 | 1 |', text)
        record = text.split('## 需求澄清记录')[1].split('\n## ')[0]
        self.assertIn('| CL-STBY | 需求规格 §3：未提及待机功耗 | 待机功耗上限没给，启动电阻取值没有依据 | 待机功耗 ≤0.1 W（230 Vac 空载） '
                      '| 用户暂缓：先按建议设计，量产前再定 | 产品负责人 2026-10-27 | R-OUT |', record)

    def test_calculation_on_a_deferred_requirement_has_its_own_tier(self):
        self.ask_user()
        c1 = self.d.closure['calculations'][0]
        c4 = dict(c1, id='C4', coverage='bounded', conclusion='conditional', rests_on='user_deferred', omitted_terms=[], parameters=[
            {'name': 'P_stby', 'value': 0.1, 'unit': 'W', 'basis': 'requirement', 'source': 'req:R-OUT'}])
        self.d.closure.update(parameter_version=2, calculations=[c4])
        self.d.closure['work_items'][-1]['calculations'] = ['C4']
        self.d.write('design-closure.json', self.d.closure)
        self.d.write('design-closure-audit.json', audit(self.d.closure, self.d.record / 'electrical-intent.json', self.d.root))
        text, problems = self.d.report()
        self.assertEqual([], [p for p in problems if '计算' in p], problems)
        self.assertIn('依赖暂缓的需求 1 项', text.split('## 结论')[1].split('\n## ')[0])
        section = text.split('## 依赖暂缓的需求的计算')[1].split('\n## ')[0]
        self.assertIn('用户定下需求后按定下的数值复算', section)
        self.assertIn('| C4 | R-OUT | 输出纹波：18 ≤ 30 mV | 待办 W-STBY | W-STBY |', section)

    def test_clarification_record_shows_whether_requirement_files_were_changed(self):
        self.ask_user()
        c = self.d.closure
        c['clarifications'][0]['answer'].update(decision='ADOPTED_PROPOSAL', text=c['clarifications'][0]['proposed_requirement'],
                                                requirement_files={'decision': 'UPDATED', 'files': ['需求/工程规格.md']})
        self.d.write('design-closure.json', c)
        record = self.d.report()[0].split('## 需求澄清记录')[1].split('\n## ')[0]
        self.assertIn('| 原始需求文件 |', record)
        self.assertIn('| R-OUT | 已改：需求/工程规格.md |', record)
        c['clarifications'][0]['answer']['requirement_files'] = {'decision': 'KEPT'}
        self.d.write('design-closure.json', c)
        self.assertIn('| R-OUT | 用户不让改 |', self.d.report()[0])

    def test_unanswered_clarification_is_a_problem(self):
        self.ask_user(decision=None)
        text, problems = self.d.report()
        self.assertIn('需求澄清 CL-STBY 还没有答复：要当场问用户，答复写回需求清单后再往下设计（见 requirement-clarifications.md）', problems)
        self.assertIn('| 还没有答复 |', text.split('## 需求澄清记录')[1].split('\n## ')[0])

    def test_ask_user_response_must_point_at_clarifications(self):
        self.ask_user()
        self.d.write('review-responses.json', {'schema_version': 1,
            'sources': [{'id': 'S1', 'path': '/x', 'sha256': '0' * 64}],
            'items': [{'id': 'RC1', 'source': 'S1', 'locator': '1', 'comment': 'c', 'cause': 'none', 'response': 'ASK_USER',
                       'detail': '待机功耗上限要产品定', 'clarifications': ['CL-STBY']},
                      {'id': 'RC2', 'source': 'S1', 'locator': '2', 'comment': 'c', 'cause': 'none', 'response': 'ASK_USER',
                       'detail': 'd', 'clarifications': ['CL-LOAD']},
                      {'id': 'RC3', 'source': 'S1', 'locator': '3', 'comment': 'c', 'cause': 'none', 'response': 'ASK_USER',
                       'detail': 'e', 'work_items': ['W-STBY']}]})
        _, problems = self.d.report()
        self.assertEqual(problems, ['RC2：引用的需求澄清 CL-LOAD 不在 design-closure.json 里',
                                    'RC3：处理方式为“请用户定需求”时必须填 clarifications'])

    def test_conditional_calculations_listed_with_assumptions(self):
        text, _ = self.d.report()
        section = text.split('## 有条件成立的计算')[1].split('## ')[0]
        self.assertIn('| C1 | R-OUT | 输出纹波：18 ≤ 30 mV | ripple | W-FW |', section)
        self.assertIn('不阻塞出图', section)

    def test_calculations_without_parameter_sources_are_a_problem(self):
        del self.d.closure['parameter_version']
        self.d.write('design-closure.json', self.d.closure)
        _, problems = self.d.report()
        self.assertTrue(any('parameter_version 3' in p for p in problems), problems)

    def test_version_2_reports_what_each_calculation_rests_on(self):
        c1 = self.d.closure['calculations'][0]
        c1.update(rests_on='vendor_data', omitted_terms=[{'term': '纹波电流', 'kind': 'not_calculated', 'work_item': 'W-CALC'}])
        c2 = dict(c1, id='C2', coverage='bounded', conclusion='conditional', rests_on='estimate', omitted_terms=[], parameters=[
            {'name': 'eta', 'value': 0.9, 'unit': '1', 'basis': 'model', 'reason': '满载效率工程包络'}])
        c3 = dict(c1, id='C3', coverage='bounded', conclusion='supported', omitted_terms=[
            {'term': '满载温升', 'kind': 'verify_by_test', 'work_item': 'W-TEST'}], parameters=[
            {'name': 'P_out', 'value': 30, 'unit': 'W', 'basis': 'requirement', 'source': 'req:R-OUT'}])
        del c3['rests_on']
        self.d.closure.update(parameter_version=2, calculations=[c1, c2, c3])
        self.d.write('design-closure.json', self.d.closure)
        self.d.write('design-closure-audit.json', audit(self.d.closure, self.d.record / 'electrical-intent.json', self.d.root))
        text, problems = self.d.report()
        self.assertEqual([], [p for p in problems if '计算' in p], problems)
        self.assertIn('- **计算**：共 3 项。设计成立 1 项，依赖工程估计 1 项，依赖厂家资料 1 项，不满足 0 项。', text)
        self.assertIn('（有条件成立的需求中依赖厂家资料 1 条）', text)
        vendor = text.split('## 依赖厂家资料的计算')[1].split('\n## ')[0]
        self.assertIn('| C1 | R-OUT | 输出纹波：18 ≤ 30 mV | 待办 W-FW、没算：纹波电流 | W-FW、W-CALC |', vendor)
        self.assertIn('| C2 |', text.split('## 依赖工程估计的计算')[1].split('\n## ')[0])
        self.assertNotIn('## 有条件成立的计算', text)
        self.assertIn('  - C1：依赖 待办 W-FW、没算：纹波电流', text)
        self.assertIn('| 计算结论：设计成立 / 依赖工程估计 / 依赖厂家资料 / 不满足 | 1 / 1 / 1 / 0 |', text)

    def test_a_failed_calculation_leads_the_tables_with_its_terms_and_candidate(self):
        # R10 ENERGY failed in every best case yet appeared only as a work item (user 2026-10-28: 先改前四条).
        c1 = self.d.closure['calculations'][0]
        c1.update(conclusion='failed', coverage='bounded', omitted_terms=[], contributors=[
            {'name': '限流电阻', 'value': 6.4, 'unit': 'W'}, {'name': '检流电阻', 'value': 0.2, 'unit': 'W'},
            {'name': '钳位电阻', 'value': 2.4, 'unit': 'W'}])
        c1['checks'] = [{'name': '低损耗情景效率', 'value': 0.82, 'operator': '>=', 'limit': 0.835, 'unit': '1',
                         'scenario': 'best'}, {'name': '输出纹波', 'value': 18, 'operator': '<=', 'limit': 30, 'unit': 'mV'}]
        c2 = dict(c1, id='C2', conclusion='conditional', rests_on='estimate', contributors=None, checks=c1['checks'][1:],
                  parameters=[{'name': 'eta', 'value': 0.9, 'unit': '1', 'basis': 'model', 'reason': '满载效率工程包络'}])
        del c2['contributors']
        self.d.closure['work_items'][0].update(calculations=['C1'], redesign='限流电阻启动后旁路，预计减少 6 W')
        self.d.closure.update(parameter_version=2, calculations=[c1, c2])
        self.d.write('design-closure.json', self.d.closure)
        self.d.write('design-closure-audit.json', audit(self.d.closure, self.d.record / 'electrical-intent.json', self.d.root))
        text, _ = self.d.report()
        failed = text.split('## 不满足的计算')[1].split('\n## ')[0]
        self.assertLess(text.index('## 不满足的计算'), text.index('## 依赖工程估计的计算'))
        self.assertIn('| C1 | R-OUT | 低损耗情景效率：0.82 ≥ 0.835 1（最好情景） | 限流电阻 6.4 W；钳位电阻 2.4 W；检流电阻 0.2 W '
                      '| 限流电阻启动后旁路，预计减少 6 W | W-CALC、W-FW |', failed)
        self.assertIn('- **改设计候选（须用户批准后实施）**：限流电阻启动后旁路，预计减少 6 W', text)

    def test_margin_risks_bom_spec_handoff_and_requirement_hints_are_one_line_each(self):
        self.d.write('design-closure-audit.json', dict(audit(
            self.d.closure, self.d.record / 'electrical-intent.json', self.d.root), estimate_margins=[
                {'calculation': 'C1', 'check': '正常峰值不误触发', 'value': 96.9, 'limit': 97.6, 'against': 'limit',
                 'unit': 'V', 'margin': 0.0072, 'uncertainty': 0.1, 'improvement': '提高门槛'}]))
        performance = {'status': 'PASS', 'errors': [], 'pending': [], 'native': 'CHECKED', 'procurement': ['R1', 'R2'],
                       'hints': ['2 颗电阻的工作电压要求不到封装最弱常用件耐压的一半'], 'definition': {}, 'selection': {}}
        with mock.patch('render_design_report.package_audit', return_value=performance):
            text, _ = self.d.report()
        self.assertIn('- **按 BOM 规格转交采购（外部，不挡交付）**：2 颗，采购按 BOM 的 RequirementSpec 找料并核对保证值。', text)
        self.assertIn('- **性能要求提示**：2 颗电阻的工作电压要求不到封装最弱常用件耐压的一半。', text)
        self.assertIn('- **估计余量**：1 处检查', text)
        self.assertIn('| C1 | 正常峰值不误触发 | 96.9 / 97.6 V | 0.72% / 10% | 提高门槛 |',
                      text.split('## 余量不足以覆盖估计误差')[1])

    def test_version_1_says_its_conclusions_are_not_layered(self):
        text, _ = self.d.report()
        self.assertIn('记录是 parameter_version 1，结论没有按依据分层', text)

    def test_small_values_are_not_shown_as_zero(self):
        # R8 showed a 379 ns > 343 ns check as "0 > 0 s".
        self.assertEqual('3.79e-07', num(3.7914e-07))
        self.assertEqual('0.000275', num(0.0002748))
        self.assertEqual('144', num(144.4))

    def estimate_case(self, version=2):
        c1 = self.d.closure['calculations'][0]
        c1.update(coverage='bounded', conclusion='conditional', rests_on='estimate', omitted_terms=[], parameters=[
            {'name': 'eta', 'value': 0.9, 'unit': '1', 'basis': 'model', 'reason': '满载效率工程包络'}],
            checks=[{'name': '空载功耗', 'value': 0.1445, 'operator': '<=', 'limit': 0.15, 'unit': 'W'},
                    {'name': '输出纹波', 'value': 18, 'operator': '<=', 'limit': 30, 'unit': 'mV'},
                    {'name': '每日能量配对', 'value': 217.5, 'operator': '==', 'limit': 217.5, 'unit': 'Wh'}])
        self.d.closure.update(parameter_version=version)
        self.d.write('design-closure.json', self.d.closure)
        return c1

    def test_a_version_2_record_and_a_consistency_check_are_shown(self):
        self.estimate_case()
        text, _ = self.d.report()
        self.assertIn('每日能量配对：218 = 218 Wh', text)
        self.assertIn('- **记录版本**：parameter_version 2（检查门槛的出处、每条需求有没有检查没核对）', text)

    def test_version_3_estimates_each_say_why(self):
        c1 = self.estimate_case(3)
        c1['parameters'] = [{'name': 'p%d' % i, 'value': 1, 'unit': '1', 'basis': 'model',
                             'reason': '本版工程模型；见设计计算及可复算脚本'} for i in range(4)]
        self.d.write('design-closure.json', self.d.closure)
        text, problems = self.d.report()
        self.assertTrue(any(p.startswith('4 个工程估计参数共用同一句理由') for p in problems), problems)
        self.assertNotIn('parameter_version 2（', text)
        self.assertIn('没有 derating_version（器件应力没有按降额等级核对）', text)
        c1['parameters'] = c1['parameters'][:3]
        self.d.write('design-closure.json', self.d.closure)
        self.assertFalse(any('共用同一句理由' in p for p in self.d.report()[1]))

    def test_an_old_gap_record_is_named_in_the_conclusion(self):
        text, _ = self.d.report()
        self.assertIn('- **记录版本**：gap_version 1（外部资料缺口没有分类）。新设计按 parameter_version 3、gap_version 2、derating_version 1、uncertainty_version 1 写。', text)

    def test_derating_level_and_stress_risks_are_reported(self):
        # stress-spec.md (user 2026-10-27): the level and every stress risk with its improvement are in the report.
        audit_result = json.loads((self.d.record / 'design-closure-audit.json').read_text(encoding='utf-8'))
        audit_result['derating'] = {'level': 'II', 'source': 'req:R-DER', 'hints': ['derating_rule_available C2:x'],
                                    'stress_risks': [
            {'calculation': 'C1', 'check': '漏源电压', 'ref': 'Q1', 'rule': 'MOS-VDS-S', 'value': 560, 'limit': 520,
             'rating': 650, 'unit': 'V', 'improvement': '换 700 V 管'}]}
        self.d.write('design-closure-audit.json', audit_result)
        text, _ = self.d.report()
        self.assertIn('- **降额等级**：II 级（req:R-DER，见 stress-spec.md）。合格但有风险（应力）1 处，见“应力风险”。'
                      '另有 1 处应力比较没点名降额规则（提示）。', text)
        self.assertNotIn('降额偏离', text)
        section = text.split('## 应力风险')[1].split('\n## ')[0]
        self.assertIn('| C1 | Q1 | MOS-VDS-S | 560 / 520 / 650 V | 换 700 V 管 |', section)

    def test_kept_unspecified_operating_point_is_listed(self):
        c = self.d.closure
        c['operating_points'] = [{'id': 'OP-EN', 'refs': ['U1'], 'pins': ['EN'], 'mode': '开漏灌电流驱动光耦 LED',
                                  'specified': False, 'source': 'datasheet:设计资料/X - XYZ100.pdf#p2', 'locator': 'EN 一节',
                                  'work_item': 'W-FW', 'alternatives': [
                                      {'approach': '小信号 MOS 缓冲', 'specified': True, 'feasible': False, 'reason': '板面不够'}]}]
        self.d.write('design-closure.json', c)
        self.d.write('design-closure-audit.json', audit(c, self.d.record / 'electrical-intent.json', self.d.root))
        text, problems = self.d.report()
        self.assertEqual([], problems)
        section = text.split('## 手册未规定的工作点')[1].split('\n## ')[0]
        self.assertIn('| U1 EN | 开漏灌电流驱动光耦 LED | 小信号 MOS 缓冲：板面不够 | W-FW |', section)

    def test_english_prose_in_records_is_a_problem(self):
        self.d.closure['calculations'][0]['assumptions'] = [
            'Transformer temperature, fringing and leakage require construction verification.']
        self.d.write('design-closure.json', self.d.closure)
        self.d.write('design-closure-audit.json', audit(self.d.closure, self.d.record / 'electrical-intent.json', self.d.root))
        _, problems = self.d.report()
        self.assertTrue(any('要改成中文' in p and 'C1' in p for p in problems), problems)

    def test_chinese_prose_with_part_numbers_and_acronyms_is_fine(self):
        from render_design_report import english_sentence
        self.assertFalse(english_sentence('NCP1343的FAULT脚经BZT52H-B68检测辅助绕组过压，PFC关断后VCC由HV维持'))
        self.assertFalse(english_sentence('Kelvin回路按TDK ETD39 p2-4核对'))
        self.assertTrue(english_sentence('Only NCP1343 remains on VCC after auxiliary dies'))

    def test_failed_drawing_gate_is_a_problem(self):
        self.d.write('summary.json', {'status': 'FAIL', 'sheets': ['a', 'b'], 'gates': {
            'erc': {'status': 'PASS', 'violations': 0}, 'geometry': {'status': 'FAIL'}}})
        text, problems = self.d.report()
        self.assertTrue(any('图面几何' in p and '改图' in p for p in problems), problems)
        self.assertIn('没通过（FAIL） 1 项', text)
        self.assertNotIn('REVIEW', text)

    def test_geometry_detail_counts_gaps_and_render_review_items(self):
        self.d.write('summary.json', {'status': 'INCOMPLETE', 'sheets': ['a', 'b'], 'gates': {
            'erc': {'status': 'PASS', 'violations': 0},
            'geometry': {'status': 'PASS', 'render_review_items': {'a': ['x', 'y']}}}})
        text, _ = self.d.report()
        self.assertIn('2 个对象交图面审阅', text)

    def test_page_plan_is_required_and_checked(self):
        (self.d.record / 'page-plan.json').unlink()
        _, problems = self.d.report()
        self.assertIn('缺少 record/page-plan.json', problems)
        self.d.write('page-plan.json', {'schema_version': 1, 'pages': [
            {'file': 'board.kicad_sch', 'reader_tasks': ['任务一', '任务二'], 'blocks': {'a': ['U1', 'R9'], 'b': ['U1']}},
            {'file': 'other.kicad_sch', 'reader_tasks': [], 'blocks': {}}]})
        _, problems = self.d.report()
        self.assertIn('board.kicad_sch：功能块“a”里的 R9 不在设计网表里', problems)
        self.assertIn('board.kicad_sch：U1 同时在功能块“a”和“b”里', problems)
        self.assertIn('board.kicad_sch：读者任务 2 条，图面审阅只追了 1 条路径', problems)
        self.assertIn('other.kicad_sch：要写明读者任务（reader_tasks）', problems)
        self.assertIn('other.kicad_sch：要按功能块列出器件（blocks）', problems)

    def test_datasheet_citations_are_checked_against_the_page(self):
        text, problems = self.d.report()
        self.assertEqual([], problems)
        self.assertNotIn('## 引用待人工核对', text)
        role = self.d.selection['roles'][0]
        role['candidates'][0]['values']['输出电流'] = {'value': 3.8, 'page': 1}    # not what page 1 shows
        role['candidates'][1]['values']['输出电流'] = {'value': 2, 'page': 4}      # the PDF has one page
        self.d.write('selection.json', self.d.selection)
        lessons = json.loads((self.d.record / 'lessons.json').read_text())
        lessons['events'][0]['source'] = 'datasheet:raw/Datasheet/08_电源管理/X - XYZ100.pdf#p7'
        self.d.write('lessons.json', lessons)
        text, problems = self.d.report()
        self.assertEqual(['候选 ABC200 的“输出电流”：手册引用不对，设计资料/Y - ABC200.pdf 只有 1 页，引用了第 4 页',
                          'lessons.json 第 1 条：手册引用不对，raw/Datasheet/08_电源管理/X - XYZ100.pdf 只有 3 页，引用了第 7 页'],
                         problems)
        self.assertIn('## 引用待人工核对', text)
        self.assertIn('| 候选 XYZ100 的“输出电流” | 设计资料/X - XYZ100.pdf#p1 | 3.8 |', text)

    def test_unnamed_core_part_is_a_record_problem_unless_kept_from_the_baseline(self):
        self.d.write('electrical-intent.json', {'components': [{'ref': 'U1', 'value': 'XYZ100'}, {'ref': 'R1'}]})
        text, problems = self.d.report()
        self.assertTrue(any(p.startswith('关键器件和特殊器件要写确切料号、数据手册和类型声明') and 'U1' in p for p in problems), problems)
        self.d.write('change-contract.json', {'schema_version': 1, 'add_components': {}, 'component_changes': {}})
        text, problems = self.d.report()
        self.assertFalse(any('关键器件和特殊器件' in p for p in problems), problems)
        self.assertIn('1 个沿用基线的器件缺确切料号、数据手册、类型声明或规格：U1', text)

    def test_protection_and_safety_positions_are_report_problems(self):
        self.d.write('electrical-intent.json', {
            'nets': {'L_IN': ['F1.1'], 'L_F': ['F1.2', 'U1.1']}, 'high_voltage_nets': ['L_IN', 'L_F'],
            'components': [{'ref': 'U1', 'value': 'XYZ100', 'mpn': 'XYZ100', 'datasheet': '设计资料/X - XYZ100.pdf'},
                           {'ref': 'F1', 'lib_id': 'Device:Fuse', 'value': 'T2A/250Vac'}]})
        text, problems = self.d.report()
        found = [p for p in problems if p.startswith('保护器件与安全防护位置')]
        self.assertTrue(found, problems)
        self.assertIn('保护器件 F1', found[0])
        self.assertIn('市电/高压侧的安规件 F1', found[0])

    def test_selection_is_required_and_checked(self):
        (self.d.record / 'selection.json').unlink()
        _, problems = self.d.report()
        self.assertIn('缺少 record/selection.json', problems)
        self.d.write('selection.json', self.d.selection)
        text, problems = self.d.report()
        self.assertEqual([], problems)
        self.assertIn('## 核心器件选型', text)
        self.assertIn('| 稳压器 | U1 | XYZ100 | 2 | 电流裕量够，库里资料全 | ABC200：输出电流 2 >= 3 A |', text)
        self.d.write('selection.json', {'schema_version': 1, 'roles': []})
        _, problems = self.d.report()
        self.assertTrue(any('没有 roles' in p for p in problems), problems)

    def options_role(self):
        sel = json.loads(json.dumps(self.d.selection))
        role = sel['roles'][0]
        role['candidates'][0]['external_dependencies'] = ['过压保护配置表未公开（p2 只有功能描述）']
        role['options'] = [
            {'name': 'XYZ100 单芯片', 'parts': ['XYZ100'], 'external_dependencies': ['过压保护配置表'],
             'cost': '器件最少', 'pros': '集成度高', 'cons': '过压行为要原厂答复', 'recommended': True},
            {'name': 'ABC200 加外置过压', 'parts': ['ABC200', 'TL431'], 'external_dependencies': [],
             'cost': '增加 4 个器件', 'pros': '过压可按手册算', 'cons': '电流只有 2A', 'recommended': False}]
        role['recommendation'] = '推荐方案 1：电流满足需求，过压另有硬件后备'
        role['decision'] = {'option': 'XYZ100 单芯片', 'source': 'user:2026-10-24'}
        return sel, role

    def test_uncertain_selection_lists_options_and_the_users_choice(self):
        sel, _ = self.options_role()
        self.d.write('selection.json', sel)
        text, problems = self.d.report()
        self.assertEqual([], problems)
        self.assertIn('- **外部条件不确定的选型**：1 个角色（稳压器→XYZ100 单芯片）', text)
        section = text.split('## 外部条件不确定的选型')[1].split('\n## ')[0]
        self.assertIn('| XYZ100 单芯片（ASG 推荐） | XYZ100 | 1 项：过压保护配置表 | 器件最少 | 集成度高 | 过压行为要原厂答复 |', section)
        self.assertIn('- **用户决定**：XYZ100 单芯片（user:2026-10-24）', section)

    def test_uncertain_selection_needs_options_recommendation_and_decision(self):
        sel, role = self.options_role()
        del role['decision']
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('还没有你的决定' in p for p in problems), problems)
        role['decision'] = {'option': 'ABC200 加外置过压', 'source': 'user:2026-10-24'}
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('不在你选的方案' in p for p in problems), problems)
        role['decision'] = {'option': 'XYZ100 单芯片', 'source': 'user:2026-10-24'}
        role['options'][1]['cons'] = role['options'][0]['cons']
        role['options'][1]['recommended'] = True
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('一字不差' in p for p in problems), problems)
        self.assertTrue(any('恰好一个推荐方案' in p for p in problems), problems)
        role['options'] = role['options'][:1]
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('要列 2–3 个选型方案' in p for p in problems), problems)

    def test_selected_candidate_declares_external_dependencies(self):
        sel = json.loads(json.dumps(self.d.selection))
        del sel['roles'][0]['candidates'][0]['external_dependencies']
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('没有写 external_dependencies' in p for p in problems), problems)

    def test_selection_candidates_are_compared_and_traceable(self):
        sel = json.loads(json.dumps(self.d.selection))
        role = sel['roles'][0]
        role['candidates'][1]['status'] = 'selected'
        role['candidates'][1]['reason'] = ''
        role['candidates'][0]['datasheet'] = '设计资料/missing.pdf'
        role['decisive'] = []
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertIn('选型角色“稳压器”没有写决定性条件', problems)
        self.assertIn('选型角色“稳压器”要恰好一个 selected 候选，现在 2 个', problems)
        self.assertIn('候选 ABC200 没有写选中或淘汰的理由', problems)
        self.assertTrue(any(p.startswith('候选 XYZ100 的资料 设计资料/missing.pdf 不在知识库') for p in problems), problems)
        role['candidates'][1] = {'mpn': 'ABC200', 'status': 'rejected', 'datasheet': '设计资料/Y - ABC200.pdf', 'reason': 'x'}
        role['candidates'][0]['datasheet'] = '设计资料/X - XYZ100.pdf'
        role['decisive'] = [{'param': 'x', 'op': 'has', 'limit': True}]
        role['candidates'][0]['values'] = {'x': {'value': True, 'page': 1}}
        del role['candidates'][1]
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertIn('选型角色“稳压器”只有 1 个候选又没写 single_candidate_reason', problems)
        role['single_candidate_reason'] = '用户指定'
        role['refs'] = ['U1', 'U9']
        self.d.write('selection.json', sel)
        self.d.write('electrical-intent.json', {'components': [{'ref': 'U1', 'value': 'OTHER'}, {'ref': 'Q1', 'value': 'M'}]})
        _, problems = self.d.report()
        self.assertIn('选型角色“稳压器”的位号 U9 不在设计网表里', problems)
        self.assertIn('位号 U1 的 value/mpn “OTHER” 都不含选定型号 XYZ100', problems)
        self.assertIn('核心器件没有选型记录：Q1', problems)

    def test_lessons_are_required_and_checked(self):
        (self.d.record / 'lessons.json').unlink()
        _, problems = self.d.report()
        self.assertIn('缺少 record/lessons.json', problems)
        self.d.write('lessons.json', {'schema_version': 1, 'events': []})
        _, problems = self.d.report()
        self.assertTrue(any('没有 events' in p for p in problems), problems)
        self.d.write('lessons.json', {'schema_version': 1, 'events': [
            {'source': 'SR-R3/W-1', 'cause': 'rule_missing', 'change': 'scripts/x.py'},
            {'source': 'review:SR-R3/W-2', 'cause': 'knowledge_missing', 'change': 'scripts/x.py'},
            {'source': 'review:SR-R3/W-3', 'cause': 'judgment', 'change': 'SKILL.md 任务 2.1'},
            {'source': 'review:SR-R3/W-4', 'cause': 'none', 'why_none': '看过了'},
            {'source': 'review:SR-R3/W-5', 'cause': 'oops'}]})
        text, problems = self.d.report()
        self.assertIn('lessons.json 第 1 条的 source 要写成 review:<审查目录>/<待办编号>、datasheet:<库内路径>#p<页>、test:<记录> 或 user:<日期>', problems)
        self.assertIn('lessons.json 第 2 条归因 knowledge_missing，change 要指向 references//wiki//raw/ 下的具体文件', problems)
        self.assertIn('lessons.json 第 3 条归因 judgment 要写 why_not_rule：为什么规则和知识都拦不住', problems)
        self.assertFalse(any(p.startswith('lessons.json 第 4 条') for p in problems), problems)
        self.assertIn('lessons.json 第 5 条的 cause 必须是 rule_missing/rule_not_enforced/knowledge_missing/knowledge_wrong/judgment 或 none', problems)
        self.assertIn('## 改进记录', text)
        self.assertIn('| review:SR-R3/W-2 | 缺知识 | scripts/x.py |', text)

    def test_a_lesson_changed_in_the_delivery_is_not_a_skill_change(self):
        # R8 wrote its new circuit patterns into 设计资料/references/circuit-patterns/, so the skill learned nothing.
        self.d.write('lessons.json', {'schema_version': 1, 'events': [
            {'source': 'user:2026-10-27', 'cause': 'knowledge_missing',
             'change': '设计资料/references/circuit-patterns/ac-indicator.md：补一次侧 VCC 供电 LED 做法'},
            {'source': 'user:2026-10-27', 'cause': 'knowledge_missing',
             'change': 'references/circuit-patterns/ac-indicator.md：补一次侧 VCC 供电 LED 做法'}]})
        _, problems = self.d.report()
        self.assertTrue(any(p.startswith('lessons.json 第 1 条的 change 写在交付目录里') for p in problems), problems)
        self.assertFalse(any(p.startswith('lessons.json 第 2 条') for p in problems), problems)

    def test_a_deferred_comment_is_still_attributed(self):
        # R6 marked nine deferred review comments cause=none "下一轮处理时再归因", among them the P1 F-SR-TONMIN.
        self.d.write('lessons.json', {'schema_version': 1, 'events': [
            {'source': 'review:SR-R5/F-SR-TONMIN', 'cause': 'none',
             'why_none': '本版范围外暂缓，未做根因归类；已读该意见原文，下一轮处理时再归因。'},
            {'source': 'review:SR-R5/W-REQ', 'cause': 'none', 'why_none': '需求取舍，用户决定本版暂缓；不反映技能缺口。'}]})
        _, problems = self.d.report()
        self.assertTrue(any(p.startswith('lessons.json 第 1 条 cause=none 只用于') for p in problems), problems)
        self.assertFalse(any(p.startswith('lessons.json 第 2 条') for p in problems), problems)

    def test_review_comments_must_be_attributed_to_a_cause(self):
        self.d.write('review-responses.json', {'schema_version': 1, 'sources': [
            {'id': 'SR', 'path': 'r.md', 'sha256': 'x'}], 'items': [
            {'id': 'W-A', 'source': 'SR', 'locator': 'W-A', 'comment': 'a', 'response': 'DECLINE', 'detail': '不采纳 a', 'evidence': ['E1']},
            {'id': 'W-B', 'source': 'SR', 'locator': 'W-B', 'comment': 'b', 'response': 'DECLINE', 'detail': '不采纳 b', 'evidence': ['E1'], 'cause': 'rule_missing'},
            {'id': 'W-C', 'source': 'SR', 'locator': 'W-C', 'comment': 'c', 'response': 'DECLINE', 'detail': '不采纳 c', 'evidence': ['E1'], 'cause': 'knowledge_wrong'},
            {'id': 'W-D', 'source': 'SR', 'locator': 'W-D', 'comment': 'd', 'response': 'DECLINE', 'detail': '不采纳 d', 'evidence': ['E1'], 'cause': 'none'}]})
        self.d.write('lessons.json', {'schema_version': 1, 'events': [
            {'source': 'review:SR-R3/W-C', 'cause': 'knowledge_missing', 'change': 'references/part-roles.md 光耦行'}]})
        _, problems = self.d.report()
        self.assertIn('W-A：要归因（cause）：rule_missing/rule_not_enforced/knowledge_missing/knowledge_wrong/judgment 或 none', problems)
        self.assertIn('W-B：归因 rule_missing，lessons.json 里要有 source 以 /W-B 结尾的事件写明改了什么', problems)
        self.assertIn('W-C：review-responses 归因 knowledge_wrong，lessons.json 同一事件归因 knowledge_missing，要一致', problems)
        self.assertFalse(any(p.startswith('W-D') for p in problems), problems)

    def test_a_recurring_comment_is_not_a_judgment_slip(self):
        item = {'id': 'W-A', 'source': 'SR', 'locator': 'W-A', 'comment': 'a', 'response': 'DECLINE', 'detail': '不采纳 a',
                'evidence': ['E1'], 'cause': 'judgment', 'recurs_from': 'review:SR-R4/W-7'}
        self.d.write('lessons.json', {'schema_version': 1, 'events': [
            {'source': 'review:SR-R5/W-A', 'cause': 'judgment', 'change': 'SKILL.md 任务 2.3', 'why_not_rule': 'x'}]})
        self.d.write('review-responses.json', {'schema_version': 1, 'sources': [{'id': 'SR', 'path': 'r.md', 'sha256': 'x'}],
                                               'items': [item]})
        text, problems = self.d.report()
        self.assertIn('W-A：意见复发自 review:SR-R4/W-7，不能归因为判断失误（judgment）：复发说明规则或知识没有拦住', problems)
        self.assertIn('| W-A | a | 不采纳 | 不采纳 a（复发自 review:SR-R4/W-7） |', text)
        item['recurs_from'] = 'R4 第 7 条'
        self.d.write('review-responses.json', {'schema_version': 1, 'sources': [{'id': 'SR', 'path': 'r.md', 'sha256': 'x'}],
                                               'items': [item]})
        _, problems = self.d.report()
        self.assertIn('W-A：recurs_from 要写成 review:<上一轮审查目录>/<意见编号>', problems)

    def test_decisive_conditions_are_judged_from_recorded_values(self):
        sel = json.loads(json.dumps(self.d.selection))
        role = sel['roles'][0]
        role['decisive'][0] = '输入 12 V'
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertIn('选型角色“稳压器”的决定性条件要写成 {param, op, limit[, unit, requirement]}，op 取 <=/>=/covers/equals/has', problems)
        sel = json.loads(json.dumps(self.d.selection))
        role = sel['roles'][0]
        chosen, rejected = role['candidates']
        chosen['values']['输出电流']['value'] = 2.5                       # fails >= 3
        del chosen['values']['封装']                                      # missing
        chosen['values']['使能引脚']['value'] = False
        rejected['values'] = {}                                           # no failed condition, no kind
        role['candidates'].append({'mpn': 'DEF300', 'status': 'rejected', 'datasheet': '设计资料/Y - ABC200.pdf',
                                   'reason': '只有简介', 'reject_kind': 'data'})
        role['candidates'].append({'mpn': 'GHI400', 'status': 'alternate', 'datasheet': '设计资料/Y - ABC200.pdf',
                                   'reason': '可替代', 'values': {
                                       '输入电压范围': {'value': [10, 12], 'page': 1}, '输出电流': {'value': 3, 'page': 1},
                                       '封装': {'value': 'SOIC-8', 'page': 1}, '使能引脚': {'value': True, 'page': 1}}})
        self.d.write('selection.json', sel)
        text, problems = self.d.report()
        self.assertIn('选型角色“稳压器”候选 XYZ100 不满足条件“输出电流”（2.5 >= 3 A）却被选定', problems)
        self.assertIn('选型角色“稳压器”候选 XYZ100 没有给出条件“封装”的值和页码（没有值或页码）', problems)
        self.assertIn('选型角色“稳压器”候选 XYZ100 不满足条件“使能引脚”（无）却被选定', problems)
        self.assertIn('选型角色“稳压器”淘汰候选 ABC200 没有一条决定性条件判定不满足，也没写 reject_kind（dependency/data/availability/cost/preference）', problems)
        self.assertIn('选型角色“稳压器”候选 GHI400 不满足条件“输入电压范围”（10–12 覆盖 9–14 V）却被列为备选', problems)
        self.assertIn('DEF300：资料不足', text)

    def test_blocks_name_a_pattern_approach_or_register_the_gap(self):
        plan = json.loads((self.d.record / 'page-plan.json').read_text())
        page = plan['pages'][0]
        page['patterns'] = {}
        self.d.write('page-plan.json', plan)
        _, problems = self.d.report()
        self.assertIn('board.kicad_sch：功能块“稳压”没有标注电路模式（patterns），没有合适模式时在 lessons.json 登记 knowledge_missing 并补写 references/circuit-patterns/', problems)
        self.d.write('lessons.json', {'schema_version': 1, 'events': [
            {'source': 'user:2026-10-19', 'cause': 'knowledge_missing', 'change': 'references/circuit-patterns/ldo-regulator.md 新增'}]})
        _, problems = self.d.report()
        self.assertEqual([], problems)
        page['patterns'] = {'稳压': 'no-such#做法'}
        self.d.write('page-plan.json', plan)
        _, problems = self.d.report()
        self.assertIn('board.kicad_sch：功能块“稳压”标注的模式 no-such 在 references/circuit-patterns/ 里不存在', problems)
        page['patterns'] = {'稳压': 'output-filter-storage#不存在的做法'}
        self.d.write('page-plan.json', plan)
        _, problems = self.d.report()
        self.assertTrue(any(p.startswith('board.kicad_sch：功能块“稳压”标注的做法“不存在的做法”不在模式 output-filter-storage 里') for p in problems), problems)
        plan['pages'].insert(0, {'file': 'PD_root.kicad_sch', 'reader_tasks': ['看流向'], 'blocks': {'能量链': ['U1']}})
        self.d.write('page-plan.json', plan)
        self.d.write('visual-review.json', {'status': 'REVIEWED', 'pdf_sha256': self.d.pdf, 'pages': [
            {'page': 1, 'file': 'board.kicad_sch', 'paths': ['VIN to VOUT'], 'problems': []},
            {'page': 0, 'file': 'PD_root.kicad_sch', 'paths': ['flow'], 'problems': []}]})
        page['patterns'] = {'稳压': 'output-filter-storage#电解/聚合物 + MLCC 并联'}
        self.d.write('page-plan.json', plan)
        _, problems = self.d.report()
        self.assertFalse(any('PD_root' in p for p in problems), problems)

    def test_parts_on_a_page_must_belong_to_a_block(self):
        self.d.write('electrical-intent.json', {'components': [
            {'ref': 'U1', 'fields': {'Circuit': 'board'}}, {'ref': 'R1', 'fields': {'Circuit': 'board'}},
            {'ref': 'C1', 'fields': {'Circuit': 'board'}}]})
        _, problems = self.d.report()
        self.assertIn('board.kicad_sch：这些器件不属于任何功能块：C1', problems)

    def test_a_finished_review_names_this_versions_pdf(self):
        """R6 redraw: a review made on the previous export read as finished; KiCad's export time does not count."""
        pdf = self.d.root / '原理图' / 'schematic.pdf'
        pdf.write_bytes(b'%PDF-1.5 /CreationDate (D:2026:10:23:10:00:00) page')
        review = json.loads((self.d.record / 'visual-review.json').read_text())
        review['pdf_sha256'] = render_sha256(pdf)
        self.d.write('visual-review.json', review)
        pdf.write_bytes(b'%PDF-1.5 /CreationDate (D:2026:10:24:00:02:15) page')
        self.assertEqual([], self.d.report()[1])
        pdf.write_bytes(b'%PDF-1.5 /CreationDate (D:2026:10:24:00:02:15) moved page')
        stale = [p for p in self.d.report()[1] if 'pdf_sha256' in p]
        self.assertEqual(1, len(stale), stale)
        review['status'] = 'REVIEW_PENDING'
        self.d.write('visual-review.json', review)
        self.assertFalse(any('pdf_sha256' in p for p in self.d.report()[1]))
        review.update(status='REVIEWED', pdf_sha256=render_sha256(pdf), method='未改页与 R5 同图，逐项处置按位号沿用')
        self.d.write('visual-review.json', review)
        self.assertIn('visual-review.json 的 method 写了沿用上一版：没改动的页面也要按本版 PDF 重新看', self.d.report()[1])

    def test_every_render_review_item_is_dispositioned_from_this_pdf(self):
        (self.d.root / '原理图' / 'board.kicad_sch').write_text(
            '(kicad_sch (version 20250114) (generator "t") (uuid "r") (paper "A4") (lib_symbols)\n'
            '(symbol (lib_id "Device:R") (at 0 0 0) (uuid "aaa") (property "Reference" "R1" (at 0 0 0)))\n'
            '(symbol (lib_id "Device:R") (at 0 10 0) (uuid "bbb") (property "Reference" "U1" (at 0 0 0))))\n')
        listed = ['pin-number:aaa: physical pin numbers need native render review', 'pin-name:bbb:1: nonunique/noncausal text removal',
                  'hierarchical_label: outline and attached fields need render review']
        summary = json.loads((self.d.record / 'summary.json').read_text())
        summary['gates']['geometry']['render_review_items'] = {'board.kicad_sch': listed}
        self.d.write('summary.json', summary)
        same = '本页 PDF 上可见的引脚号和引脚名都没有被导线或文字压住。'
        def review(items, paths=('VIN to VOUT',)):
            self.d.write('visual-review.json', {'status': 'REVIEWED', 'pdf_sha256': self.d.pdf, 'pages': [
                {'page': 1, 'file': 'board.kicad_sch', 'paths': list(paths), 'problems': [], 'render_review_items': items}]})
            return self.d.report()[1]
        # One sentence may describe several symbols; what matters is that every listed object was looked at.
        self.assertEqual([], review([{'item': k, 'disposition': same} for k in listed]))
        problems = review([{'item': listed[0], 'disposition': same}, {'item': 'pin-name:ccc:1: x', 'disposition': 'C9 看过'}])
        self.assertIn('board.kicad_sch：条目“pin-name:ccc:1: x”的符号在图里找不到', problems)
        self.assertIn('board.kicad_sch：2 个图面待审对象在 visual-review.json 里没有处置（如 pin-name:bbb:1: nonunique/noncausal text removal）',
                      problems)
        problems = review([{'item': listed[0], 'disposition': ''}] + [{'item': k, 'disposition': same} for k in listed[1:]])
        self.assertIn('board.kicad_sch：1 个图面待审对象在 visual-review.json 里没有处置（如 pin-number:aaa: physical pin numbers need native）',
                      problems)
        problems = review([{'item': k, 'disposition': '沿用上一版的处置'} for k in listed])
        self.assertIn('board.kicad_sch：处置“沿用上一版的处置”沿用上一版：没改动的页面也要按本版 PDF 重新看', problems)
        problems = review([{'item': k, 'disposition': same} for k in listed], paths=['本页未改，同上一版'])
        self.assertTrue(any('同上一版' in p for p in problems), problems)

    def test_records_and_notes_use_the_terminology_table(self):
        _, problems = self.d.report({'summary': '本版原生网表与设计网表一致，可以定稿。', 'items': {'W-FW': '过压配置待厂家交接。'}})
        self.assertEqual(1, len(problems), problems)
        self.assertIn('notes summary：“本版原生网表与设计网表一致，可以定稿。”（定稿、原生）', problems[0])
        self.assertIn('notes 待办 W-FW：“过压配置待厂家交接。”（交接）', problems[0])
        self.assertEqual([], self.d.report({'summary': '电压环为闭环控制，KiCad 导出网表与设计网表一致。'})[1])

    def test_written_totals_match_the_records(self):
        notes = {'summary': '共 2 个器件，共 2 页；全部 1 项计算，共 2 件未关闭项，共 1 条需求。其中 1 条需求有条件成立。'}
        self.assertEqual([], self.d.report(notes)[1])
        notes = {'summary': '共 3 个器件，全部 2 项计算。', 'highlights': ['共 4 页']}
        self.assertEqual(['notes summary 写“共 3 个器件”，记录里是 2', 'notes summary 写“全部 2 项计算”，记录里是 1',
                          'notes 关键依据 1 写“共 4 页”，记录里是 2'], self.d.report(notes)[1])

    def test_handoffs_listed_apart(self):
        text, _ = self.d.report()
        self.assertIn('| 样机验证 | 样机或试验验证 | 满载温升测试 |', text.split('## 技术转交要求')[1])

    def test_plain_words_only(self):
        text, _ = self.d.report()
        for word in JARGON:
            self.assertNotIn(word, text, word)

    def test_review_responses_are_checked_and_listed(self):
        self.d.write('review-responses.json', {'schema_version': 1,
            'sources': [{'id': 'S1', 'path': '/x/审查报告.md', 'sha256': '0' * 64, 'from': '审查方 v0'}],
            'items': [{'id': 'RC1', 'source': 'S1', 'locator': '待办 1', 'comment': '过压保护配置没依据',
                       'cause': 'none', 'response': 'OBTAIN_DATA', 'detail': '向固件供应方要配置表', 'work_items': ['W-FW']},
                      {'id': 'RC2', 'source': 'S1', 'locator': '待办 2', 'comment': '缺满载温升',
                       'cause': 'none', 'response': 'DECLINE', 'detail': '只能样机测'}]})
        text, problems = self.d.report()
        self.assertIn('RC2：处理方式为“不采纳”时必须填 evidence', problems)
        self.assertIn('- **收到的审查意见**：2 条。补资料 1 条，不采纳 1 条。', text)
        self.assertIn('| RC1 | 过压保护配置没依据 | 补资料 | 向固件供应方要配置表 |', text)
        self.assertIn('设计记录本身有问题', text.splitlines()[2])

    def responses(self, items):
        self.d.write('review-responses.json', {'schema_version': 1,
            'sources': [{'id': 'S1', 'path': '/x', 'sha256': '0' * 64}], 'items': items})
        _, problems = self.d.report()
        return problems

    def test_same_detail_on_several_comments_is_a_problem(self):
        same = '本次未宣称关闭；已复核现有条件计算并保留原任务。'
        problems = self.responses([
            {'id': 'RC1', 'source': 'S1', 'locator': '1', 'comment': 'a', 'cause': 'none', 'response': 'OBTAIN_DATA', 'detail': same, 'work_items': ['W-FW']},
            {'id': 'RC2', 'source': 'S1', 'locator': '2', 'comment': 'b', 'cause': 'none', 'response': 'OBTAIN_DATA', 'detail': same, 'work_items': ['W-FW']}])
        self.assertTrue(any(p.startswith('处理说明“本次未宣称关闭') and '2 条意见里重复' in p for p in problems), problems)

    def test_design_response_needs_this_versions_progress(self):
        item = {'id': 'RC1', 'source': 'S1', 'locator': '1', 'comment': 'c', 'cause': 'none', 'response': 'DESIGN',
                'detail': '自己算完', 'work_items': ['W-CALC']}
        problems = self.responses([item])
        self.assertIn('RC1：“补设计”引用的待办 W-CALC 没有写本版进展（progress）', problems)
        self.d.closure['work_items'][0]['progress'] = '已按 105°C 额定算出 2.67A，待核均流'
        self.d.write('design-closure.json', self.d.closure)
        self.d.write('design-closure-audit.json', audit(self.d.closure, self.d.record / 'electrical-intent.json', self.d.root))
        self.assertEqual([], self.responses([item]))
        text, _ = self.d.report()
        self.assertIn('- **本版进展**：已按 105°C 额定算出 2.67A，待核均流', text)

    def test_peripheral_check_not_done_leaves_the_design_unfinished(self):
        summary = json.loads((self.d.record / 'summary.json').read_text())
        summary['reference_contract'] = 'NOT_CHECKED'
        summary['gates']['erc']['ignored_rules'] = ['single_global_label']
        self.d.write('summary.json', summary)
        text, _ = self.d.report()
        self.assertIn('外围电路按手册核对：未执行', text)
        self.assertIn('| 外围电路按手册核对 | 未执行 |', text)
        self.assertIn('工程设为忽略的规则：single_global_label', text)
        summary['reference_contract'] = 'checked'
        self.d.write('summary.json', summary)
        self.assertNotIn('外围电路按手册核对：未执行', self.d.report()[0])

    def test_selected_part_matches_value_or_mpn_and_sources_are_optional(self):
        del self.d.selection['roles'][0]['sources']
        self.d.write('selection.json', self.d.selection)
        self.d.write('electrical-intent.json', {'components': [{'ref': 'U1', 'value': '3.3V/3A', 'mpn': 'XYZ100-DR'}, {'ref': 'R1'}]})
        _, problems = self.d.report()
        self.assertFalse(any('选定型号' in p or '候选来源' in p for p in problems), problems)
        del self.d.selection['roles'][0]['candidates'][0]['mpn']
        self.d.write('selection.json', self.d.selection)
        _, problems = self.d.report()
        self.assertIn('选型角色“稳压器”的选定候选没有写 mpn', problems)

    def test_review_source_is_hashed_when_readable_and_marked_unverified_otherwise(self):
        source = self.d.root / '审查报告.md'
        source.write_text('意见原文')
        item = {'id': 'RC1', 'source': 'S1', 'locator': '1', 'comment': 'c', 'cause': 'none', 'response': 'ASK_USER', 'detail': 'd',
                'work_items': ['W-FW']}
        def write(path, digest):
            self.d.write('review-responses.json', {'schema_version': 1, 'sources': [{'id': 'S1', 'path': path, 'sha256': digest}],
                                                   'items': [item]})
            return self.d.report()
        _, problems = write(str(source), '0' * 64)
        self.assertTrue(any('S1 的文件与登记的 sha256 不一致' in p for p in problems), problems)
        text, problems = write(str(source), sha256(source))
        self.assertFalse(any('sha256 不一致' in p for p in problems), problems)
        self.assertNotIn('来源未核对', text)
        text, problems = write('/does/not/exist.md', '0' * 64)
        self.assertFalse(any('sha256 不一致' in p for p in problems), problems)
        self.assertIn('意见来源 S1 的原文读不到，来源未核对', text)

    def test_redesign_names_a_part_or_page_and_calc_doc_names_its_target(self):
        base = {'source': 'S1', 'locator': '1', 'comment': 'c', 'detail': 'd'}
        problems = self.responses([
            {'id': 'RC1', 'cause': 'none', 'response': 'REDESIGN', 'changes': ['三只旁路升为2.2uF'], **base},
            {'id': 'RC2', 'cause': 'none', 'response': 'REDESIGN', 'changes': ['R1 改 470Ω'], **{**base, 'detail': 'e'}},
            {'id': 'RC3', 'cause': 'none', 'response': 'REDESIGN', 'changes': ['System_block 流向标名'], **{**base, 'detail': 'f'}},
            {'id': 'RC4', 'cause': 'none', 'response': 'CALC_DOC', 'changes': ['C1', '方案与选型依据.md', '不存在.md'], **{**base, 'detail': 'g'}}])
        self.assertIn('RC1：“改图”的 changes 没有点名改了哪个位号或哪一页', problems)
        self.assertFalse(any(p.startswith('RC2') or p.startswith('RC3') for p in problems), problems)
        self.assertIn('RC4：“补计算/补文档”的 changes 项“不存在.md”既不是计算编号也不是设计资料文件', problems)
        self.assertEqual(1, sum(p.startswith('RC4') for p in problems), problems)

    def test_highlight_wording_is_not_judged_and_response_tally(self):
        text, problems = self.d.report({'highlights': ['第一轮审查已锁定，第二轮将逐件核销', '120Hz 纹波按 0.66A 额定核过']})
        self.assertFalse(any('关键设计依据' in p for p in problems), problems)
        self.d.write('review-responses.json', {'schema_version': 1,
            'sources': [{'id': 'S1', 'path': '/x', 'sha256': '0' * 64}],
            'items': [{'id': 'RC1', 'source': 'S1', 'locator': '1', 'comment': 'c', 'cause': 'none', 'response': 'OBTAIN_DATA',
                       'detail': 'x', 'work_items': ['W-FW']},
                      {'id': 'RC2', 'source': 'S1', 'locator': '2', 'comment': 'c', 'cause': 'none', 'response': 'REDESIGN',
                       'detail': 'y', 'changes': ['R1 改值']}]})
        text, _ = self.d.report()
        self.assertIn('本版共收到 2 条审查意见：改图或补计算/补文档 1 条，其余 1 条登记为待办、技术转交或不采纳。', text)

    def test_numbers_use_three_significant_digits(self):
        from render_design_report import num
        self.assertEqual(['0.426', '145000', '18', '0.00199', '1.04', '264', '2.67'],
                         [num(v) for v in (0.42632428, 144700.68310544, 18, 0.0019886243943543296, 1.0392525, 264, 2.6666667)])

    def test_response_stage_must_match_work_item(self):
        self.d.write('review-responses.json', {'schema_version': 1,
            'sources': [{'id': 'S1', 'path': '/x', 'sha256': '0' * 64}],
            'items': [{'id': 'RC1', 'source': 'S1', 'locator': '1', 'comment': 'c', 'cause': 'none', 'response': 'HANDOFF',
                       'detail': 'd', 'work_items': ['W-CALC']}]})
        _, problems = self.d.report()
        self.assertIn('RC1：待办 W-CALC 的阶段与处理方式“技术转交”不符', problems)


class PackDesignTests(unittest.TestCase):
    def setUp(self):
        self.d = Delivery()
        self.addCleanup(self.d.cleanup)
        text, _ = self.d.report()
        (self.d.root / REPORT).write_text(text)
        self.inputs = Path(self.d.tmp.name) / 'req'
        self.inputs.mkdir()
        (self.inputs / 'spec.md').write_text('spec')

    def run_pack(self):
        return pack(self.d.root, {'requirements': str(self.inputs)})

    def test_datasheets_input_must_be_in_the_library(self):
        wiki = Path(self.d.tmp.name) / 'wiki'
        (wiki / 'raw' / 'Datasheet' / '08_电源管理' / 'X').mkdir(parents=True)
        (wiki / 'raw' / 'Datasheet' / '08_电源管理' / 'X' / 'X - XYZ100.pdf').write_bytes(b'%PDF-lib')
        sheets = Path(self.d.tmp.name) / 'sheets'
        sheets.mkdir()
        (sheets / 'X - XYZ100.pdf').write_bytes(b'%PDF-copy')
        (sheets / 'Y - ABC200.pdf').write_bytes(b'%PDF-new')
        errors, _ = pack(self.d.root, {'requirements': str(self.inputs), 'datasheets': str(sheets)}, wiki)
        self.assertEqual(1, len(errors), errors)
        self.assertIn('1 datasheets are not in the library', errors[0])
        self.assertIn('Y - ABC200.pdf', errors[0])
        (wiki / 'raw' / 'Datasheet' / '08_电源管理' / 'X' / 'Y - ABC200.pdf').write_bytes(b'%PDF-new')
        errors, manifest = pack(self.d.root, {'requirements': str(self.inputs), 'datasheets': str(sheets)}, wiki)
        self.assertEqual([], errors)
        self.assertIn('datasheets', manifest['inputs'])

    def test_failed_drawing_gate_cannot_be_packed(self):
        self.d.write('summary.json', {'status': 'FAIL', 'sheets': ['a', 'b'], 'gates': {
            'erc': {'status': 'PASS', 'violations': 0}, 'geometry': {'status': 'FAIL'}}})
        text, _ = self.d.report()
        (self.d.root / REPORT).write_text(text)
        errors, _ = self.run_pack()
        self.assertTrue(any('图面几何' in e for e in errors), errors)

    def previous(self, closure_changes=None, intent=None):
        prev = Path(self.d.tmp.name) / 'v0'
        (prev / 'record').mkdir(parents=True)
        closure = json.loads(json.dumps(self.d.closure))
        for change in closure_changes or []:
            change(closure)
        (prev / 'record' / 'design-closure.json').write_text(json.dumps(closure, ensure_ascii=False))
        (prev / 'record' / 'electrical-intent.json').write_text(json.dumps(
            intent if intent is not None else json.loads((self.d.record / 'electrical-intent.json').read_text())))
        return prev

    def test_open_work_is_not_compared_with_previous(self):
        prev = self.previous([lambda c: c['work_items'][0].update(status='closed'),
                              lambda c: c['requirements'][0].update(status='design_supported')])
        errors, _ = pack(self.d.root, {'requirements': str(self.inputs), 'previous': str(prev)})
        self.assertFalse(any(e.startswith('previous:') for e in errors), errors)

    def test_redesign_must_change_the_named_part_since_previous(self):
        prev = self.previous(intent={'components': [{'ref': 'U1'}, {'ref': 'R1'}]})
        self.d.write('review-responses.json', {'schema_version': 1,
            'sources': [{'id': 'S1', 'path': '/x', 'sha256': '0' * 64}],
            'items': [{'id': 'RC1', 'source': 'S1', 'locator': '1', 'comment': 'c', 'cause': 'none', 'response': 'REDESIGN',
                       'detail': 'R1 改 470Ω', 'changes': ['R1 改 470Ω']}]})
        errors, _ = pack(self.d.root, {'requirements': str(self.inputs), 'previous': str(prev)})
        self.assertIn('previous: RC1 标为“改图”，但 R1 在设计网表里与上一版相同', errors)
        self.d.write('electrical-intent.json', {'components': [{'ref': 'U1'}, {'ref': 'R1', 'value': '470R'}]})
        self.d.closure['intent_sha256'] = sha256(self.d.record / 'electrical-intent.json')
        self.d.write('design-closure.json', self.d.closure)
        self.d.write('design-closure-audit.json', audit(self.d.closure, self.d.record / 'electrical-intent.json', self.d.root))
        errors, _ = pack(self.d.root, {'requirements': str(self.inputs), 'previous': str(prev)})
        self.assertFalse(any('与上一版相同' in e for e in errors), errors)

    def test_clean_delivery_packs_with_manifest(self):
        errors, manifest = self.run_pack()
        self.assertEqual(errors, [])
        self.assertEqual(manifest['inputs']['requirements']['kind'], 'directory')
        self.assertIn('原理图/schematic.pdf', manifest['packed'])
        self.assertTrue((self.d.record / 'manifest.json').is_file())

    def test_extra_files_and_history_fail_but_a_log_does_not(self):
        (self.d.root / 'README.md').write_text('x')
        (self.d.record / 'baseline-v05').mkdir()
        (self.d.record / 'run.log').write_text('x')
        errors, _ = self.run_pack()
        self.assertTrue(any('README.md' in e for e in errors))
        self.assertTrue(any('record/baseline-v05/' in e for e in errors))
        self.assertFalse(any('run.log' in e for e in errors), errors)

    def test_a_missing_record_is_reported_once(self):
        (self.d.record / 'page-plan.json').unlink()
        errors, _ = self.run_pack()
        self.assertEqual(1, sum('page-plan.json' in e for e in errors), errors)

    def test_cited_evidence_must_be_inside(self):
        (self.d.record / 'evidence' / 'design.md').unlink()
        errors, _ = self.run_pack()
        self.assertTrue(any('evidence_missing_or_outside_root' in e for e in errors), errors)

    def test_requirement_evidence_may_stay_in_declared_input(self):
        spec = self.inputs / 'spec.md'
        self.d.closure['evidence'].append({'id': 'E2', 'path': 'requirements/spec.md', 'sha256': sha256(spec),
                                           'locator': 'REQ-1'})
        self.d.closure['requirements'][0]['evidence'].append('E2')
        self.d.write('design-closure.json', self.d.closure)
        errors, manifest = self.run_pack()
        self.assertEqual(errors, [])
        self.assertNotIn('requirements/spec.md', manifest['packed'])
        spec.write_text('changed')
        errors, _ = self.run_pack()
        self.assertTrue(any('stale_evidence E2' in e for e in errors), errors)

    def test_design_documents_must_name_parts_the_design_has(self):
        docs = self.d.root / '设计资料'
        (docs / '装配配置.json').write_text(json.dumps({'assemblies': [{'fit': ['U1', 'U9'], 'dnp': []}]}))
        (docs / 'BOM约束.csv').write_text('ref,value,mpn,note\nR1,10k,,ok\nC7,1u,,removed part\n', encoding='utf-8')
        errors, _ = self.run_pack()
        self.assertTrue(any('装配配置.json: fit U9 is not in the design' in e for e in errors), errors)
        self.assertTrue(any('BOM约束.csv line 3: C7 is not in the design' in e for e in errors), errors)
        self.assertFalse(any(' U1 ' in e or ' R1 ' in e for e in errors), errors)

    def test_design_document_mpn_and_value_must_match(self):
        self.d.write('electrical-intent.json', {'components': [{'ref': 'U1', 'mpn': 'TPS7A4001DGNR', 'value': 'TPS7A4001DGNR'},
                                                               {'ref': 'R1', 'value': '10k'}]})
        self.d.closure['intent_sha256'] = sha256(self.d.record / 'electrical-intent.json')
        self.d.write('design-closure.json', self.d.closure)
        (self.d.root / '设计资料' / 'BOM约束.csv').write_text('位号,value,mpn\nU1,TPS7A4001DGNR,TPS7A16DGNR\nR1,10k,\n', encoding='utf-8')
        errors, _ = self.run_pack()
        self.assertTrue(any("U1 mpn is 'TPS7A16DGNR', the design has 'TPS7A4001DGNR'" in e for e in errors), errors)
        self.assertFalse(any('R1' in e for e in errors), errors)

    def test_missing_schematic_outputs_fail(self):
        (self.d.root / '原理图' / 'BOM.csv').unlink()
        errors, _ = self.run_pack()
        self.assertIn('原理图/BOM.csv is missing', errors)


if __name__ == '__main__':
    unittest.main()
