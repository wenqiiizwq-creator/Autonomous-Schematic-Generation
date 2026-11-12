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
from render_design_report import check_selection, num, render, render_sha256, REPORT
from pack_design import pack
import knowledge_gaps
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_citations import pdf
from current_record import make_current, write_record

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
                                                                   'datasheet': '设计资料/X - XYZ100.pdf'}, {'ref': 'R1', 'value': '10k'}]})
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
                  'reason': '最大 2 A 不满足', 'values': {'输出电流': {'value': 2, 'page': 1}}}],
             'decision': {'source': 'user:2026-10-24', 'locator': '对话记录 2026-10-24 选型确认'}}]}
        self.write('selection.json', self.selection)
        self.closure = {
            'schema_version': 1, 'coverage': 'complete',
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
                              'needed': '全温过压门限与关断时延', 'kind': 'firmware'}],
                 'why_external': '过压动作由固件配置决定，手册没有公开', 'calculations': ['C1'],
                 'consequence': '过压时输出电容过充，负载损坏', 'questions': ['全温下过压门限的范围', '从检测到关断的最大时延']},
                {'id': 'W-TEST', 'stage': 'validation', 'status': 'handoff', 'requirements': ['R-OUT'],
                 'evidence': ['E1'], 'owner': '样机验证', 'action': '满载温升测试'}],
            'calculations': [{'id': 'C1', 'requirements': ['R-OUT'], 'evidence': ['E1'], 'refs': ['U1'],
                              'coverage': 'bounded', 'conclusion': 'conditional', 'rests_on': 'vendor_data', 'omitted_terms': [],
                              'parameters': [{'name': 'IOUT', 'ref': 'U1', 'value': 3.5, 'unit': 'A', 'basis': 'guaranteed',
                                              'source': 'datasheet:设计资料/X - XYZ100.pdf#p1', 'locator': '电气特性表 IOUT'}],
                              'checks': [{'name': '输出纹波', 'value': 18, 'operator': '<=', 'limit': 30, 'unit': 'mV'}]}]}
        make_current(self.closure, self.record / 'electrical-intent.json', self.root)
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
             'circuits': {'稳压': 'output-filter-storage#电解/聚合物 + MLCC 并联'}}]})
        self.write('delivery-evidence.json', {'schema_version': 1})
        self.write('architecture.json', {'schema_version': 1, 'domains': [{'name': '主电源'}], 'blocks': [
            {'id': 'REG', 'name': '稳压', 'domain': '主电源', 'inputs': ['VIN'], 'outputs': ['VOUT'], 'ref_range': [1, 999],
             'spec': {'text': '9～14 V 输入，输出 3 A', 'requirements': ['R-OUT']}}],
            'flows': [], 'boundaries': [], 'interfaces': []})

    def cleanup(self):
        self.env.stop()
        self.tmp.cleanup()

    def write(self, name, value):
        if name == 'design-closure.json':
            write_record(value, self.record / name)     # trace_version 1: requirements.json next to it
            return
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
        self.assertEqual(lines[3], '- **图纸自动检查**：共 4 项。通过（PASS） 2 项，没通过（FAIL） 0 项，资料不足（INSUFFICIENT） 1 项，'
                                   '未完成（INCOMPLETE） 1 项。')
        self.assertIn('- **需求**：共 1 条。有设计依据 0 条，有条件成立 1 条，还没有设计 0 条（有条件成立的需求中依赖厂家资料 1 条）。', text)
        self.assertIn('- **计算**：共 1 项。设计成立 0 项，依赖工程估计 0 项，依赖厂家资料 1 项，不满足 0 项。', text)
        self.assertIn('- **设计完成状态**：未完成。未完成项：', text)
        self.assertIn('2 项图纸自动检查资料不足或未执行：图面几何（重叠、穿线）、设计记录闭合审计', text)
        self.assertIn('2 件未关闭项（设计未完成 1 件，外部资料缺口 1 件）', text)

    def test_twelve_gates_with_mixed_states_are_all_counted(self):
        """Matrix R3 S35: the summary had 12 gates (design_closure FAIL, component_requirements INCOMPLETE); the report
        said 11 with 0 failed."""
        states = dict.fromkeys(('erc', 'intent_netlist', 'hierarchy', 'system_block', 'symbol_integrity', 'readability',
                                'geometry', 'external_supply', 'reference_contract'), 'PASS')
        states.update(component_requirements='INCOMPLETE', discrete_semantics='INSUFFICIENT', design_closure='FAIL')
        self.d.write('summary.json', {'status': 'FAIL', 'sheets': ['a', 'b'],
                                      'gates': {k: {'status': v} for k, v in states.items()}})
        text, _ = self.d.report()
        self.assertIn('- **图纸自动检查**：共 12 项。通过（PASS） 9 项，没通过（FAIL） 1 项，资料不足（INSUFFICIENT） 1 项，'
                      '未完成（INCOMPLETE） 1 项。', text)
        self.assertIn('| 设计记录闭合审计 | 没通过（FAIL） |', text)

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
        self.assertIn('  - C1：依赖 待办 W-FW', section)
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

    def test_small_values_are_not_shown_as_zero(self):
        # R8 showed a 379 ns > 343 ns check as "0 > 0 s".
        self.assertEqual('3.79e-07', num(3.7914e-07))
        self.assertEqual('0.000275', num(0.0002748))
        self.assertEqual('144', num(144.4))

    def estimate_case(self):
        c1 = self.d.closure['calculations'][0]
        c1.update(coverage='bounded', conclusion='conditional', rests_on='estimate', omitted_terms=[], parameters=[
            {'name': 'eta', 'value': 0.9, 'unit': '1', 'basis': 'model', 'reason': '满载效率工程包络'}],
            checks=[{'name': '空载功耗', 'value': 0.1445, 'operator': '<=', 'limit': 0.15, 'unit': 'W'},
                    {'name': '输出纹波', 'value': 18, 'operator': '<=', 'limit': 30, 'unit': 'mV'},
                    {'name': '每日能量配对', 'value': 217.5, 'operator': '==', 'limit': 217.5, 'unit': 'Wh'}])
        make_current(self.d.closure)
        self.d.write('design-closure.json', self.d.closure)
        return c1

    def test_an_older_closure_record_is_refused(self):
        # user 2026-11-08: only the current versions are read; an older record is rewritten, not reported version by version.
        self.d.closure['parameter_version'] = 2
        del self.d.closure['matrix_version']
        self.d.write('design-closure.json', self.d.closure)
        text, problems = self.d.report()
        self.assertTrue(any(p.startswith('design-closure.json 是旧版本记录（parameter_version 2、matrix_version 缺）') for p in problems),
                        problems)
        self.assertNotIn('记录版本', text)

    def test_the_rule_by_rule_tables_stay_in_the_record(self):
        # user 2026-11-08: the report keeps the decisions; each rule's citation stays in design-closure-audit.json.
        audit_out = json.loads((self.d.record / 'design-closure-audit.json').read_text())
        audit_out['guidelines'] = {'library_version': '1.9.8', 'applicable': ['G01-001', 'G07-001'],
                                   'covered': {'G01-001': ['calc:C1'], 'G07-001': ['work:W-TEST']}, 'not_applicable': {},
                                   'uncovered': [], 'downstream': ['G07-001'],
                                   'identity': {}}
        self.d.write('design-closure-audit.json', audit_out)
        with mock.patch('render_design_report.guideline_criteria.identity_errors', lambda found: []), \
                mock.patch('render_design_report.guideline_criteria.shared_label', lambda identity=None: '共用层 x'):
            text, _ = self.d.report()
        self.assertIn('- **共用规范**：共用层 x，适用 2 条，其中计算、选型、待办或证据引用 2 条，写明不适用 0 条；'
                      '只有淘汰候选方案、改变选型或进入计算的准则逐条落实。', text)
        self.assertIn('逐条在 record/design-closure-audit.json 的 guidelines', text)
        for heading in ('## 共用设计准则覆盖', '## 下游约束', '## 由自动检查覆盖', '## 由设计文档整组覆盖'):
            self.assertNotIn(heading, text)

    def test_estimates_each_say_why(self):
        c1 = self.estimate_case()
        c1['parameters'] = [{'name': 'p%d' % i, 'value': 1, 'unit': '1', 'basis': 'model',
                             'reason': '本版工程模型；见设计计算及可复算脚本'} for i in range(4)]
        self.d.write('design-closure.json', self.d.closure)
        text, problems = self.d.report()
        self.assertTrue(any(p.startswith('4 个工程估计参数共用同一句理由') for p in problems), problems)
        c1['parameters'] = c1['parameters'][:3]
        self.d.write('design-closure.json', self.d.closure)
        self.assertFalse(any('共用同一句理由' in p for p in self.d.report()[1]))

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
        self.assertIn('| C1 | Q1 | MOS-VDS-S | 560 / 520 / 650 V | 换 700 V 管 | — |', section)

    def test_severe_stress_threshold_and_work_item_are_reported(self):
        # Matrix R2 (2026-11-04): the stress-risk section says when a risk needs a work item and which one it names.
        audit_result = json.loads((self.d.record / 'design-closure-audit.json').read_text(encoding='utf-8'))
        audit_result['derating'] = {'level': 'II', 'source': 'req:R-DER', 'hints': [],
                                    'severe_thresholds': {'loosest_level': 'III', 'junction_margin_c': 20, 'other_margin': 'uncertainty'},
                                    'stress_risks': [
            {'calculation': 'C-TJ', 'check': 'U701 结温', 'ref': 'U701', 'rule': 'IC-SW-TJ', 'value': 146.2, 'limit': 95,
             'rating': 150, 'unit': '℃', 'improvement': '贴壳散热', 'required_severity': 'P1', 'work_item': 'W-TJ'}]}
        self.d.write('design-closure-audit.json', audit_result)
        section = self.d.report()[0].split('## 应力风险')[1].split('\n## ')[0]
        self.assertIn('应力超过 III 级的降额值至少 P2', section)
        self.assertIn('温度类 20 ℃', section)
        self.assertIn('| C-TJ | U701 | IC-SW-TJ | 146 / 95 / 150 ℃ | 贴壳散热 | W-TJ 要求 P1 |', section)

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
        text, problems = self.d.report()
        self.assertEqual(['候选 ABC200 的“输出电流”：手册引用不对，设计资料/Y - ABC200.pdf 只有 1 页，引用了第 4 页'],
                         problems)
        self.assertIn('## 引用待人工核对', text)
        self.assertIn('| 候选 XYZ100 的“输出电流” | 设计资料/X - XYZ100.pdf#p1 | 3.8 |', text)

    def test_unnamed_core_part_is_a_record_problem(self):
        self.d.write('electrical-intent.json', {'components': [{'ref': 'U1', 'value': 'XYZ100'}, {'ref': 'R1'}]})
        text, problems = self.d.report()
        self.assertTrue(any(p.startswith('关键器件和特殊器件要写确切料号、数据手册和类型声明') and 'U1' in p for p in problems), problems)

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

    def test_architecture_is_required_and_checked(self):
        # SKILL.md task C2.1, module C2 (user 2026-11-09 “确认写入”).
        arch = json.loads((self.d.record / 'architecture.json').read_text())
        (self.d.record / 'architecture.json').unlink()
        _, problems = self.d.report()
        self.assertTrue(any('缺少 record/architecture.json' in p for p in problems), problems)
        arch['blocks'][0]['spec'] = {}
        self.d.write('architecture.json', arch)
        _, problems = self.d.report()
        self.assertTrue(any('块规格' in p for p in problems), problems)

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
        role['decision'] = {'option': 'XYZ100 单芯片', 'source': 'user:2026-10-24', 'locator': '对话记录 选型确认'}
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
        role['decision'] = {'option': 'ABC200 加外置过压', 'source': 'user:2026-10-24', 'locator': '对话记录 选型确认'}
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('不在你选的方案' in p for p in problems), problems)
        role['decision'] = {'option': 'XYZ100 单芯片', 'source': 'user:2026-10-24', 'locator': '对话记录 选型确认'}
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

    def test_every_core_role_has_a_confirmation(self):
        # 整板评测 2026-11-07 A2: roles without options had decision null and passed; A6: user:<date> written by the runner.
        sel = json.loads(json.dumps(self.d.selection))
        role = sel['roles'][0]
        del role['decision']
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('稳压器”还没有确认记录' in p for p in problems), problems)
        role['decision'] = {'source': 'user:2026-11-07', 'basis': 'eval-run:auto（无用户，按技能推荐）'}
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('运行者自拟' in p for p in problems), problems)
        role['decision'] = {'source': 'user:2026-11-07'}
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('用户确认要写 locator' in p for p in problems), problems)
        role['decision'] = {'source': 'user:2026-11-07', 'locator': '对话记录 选型确认清单'}
        self.d.write('selection.json', sel)
        text, problems = self.d.report()
        self.assertEqual([], problems)
        self.assertIn('| user:2026-11-07 对话记录 选型确认清单 |', text)

    def test_confirmation_delegated_by_the_task_file(self):
        # 改进 7: an unattended run confirms through the task file's delegation, adopting ASG's recommendation only.
        sel, role = self.options_role()
        role['decision'] = {'option': 'XYZ100 单芯片', 'source': 'delegate:eval-wholeboard:2026-11-07'}
        self.d.write('selection.json', sel)
        _, problems = self.d.report()
        self.assertTrue(any('delegate_without_task' in p for p in problems), problems)
        task = {'schema_version': 1, 'id': 'T7', 'delegation': {
            'by': 'eval-wholeboard', 'date': '2026-11-07', 'scope': ['clarification', 'selection'],
            'rule': 'adopt_recommendation', 'text': '本次评测没有用户可问，采纳 ASG 的推荐。'}}
        self.d.write('task.json', task)
        text, problems = self.d.report()
        self.assertEqual([], problems)
        self.assertIn('- **任务书代答**：以下 1 处无人当场答复，由任务书代答（eval-wholeboard，授权原文：本次评测没有用户可问，采纳 ASG 的推荐。）：选型“稳压器”。', text)
        role['decision']['source'] = 'delegate:eval-wholeboard:2026-11-06'
        self.d.write('selection.json', sel)
        self.assertTrue(any('代答人或日期' in p for p in self.d.report()[1]))
        role['decision'] = {'option': 'ABC200 加外置过压', 'source': 'delegate:eval-wholeboard:2026-11-07'}
        self.d.write('selection.json', sel)
        self.assertTrue(any('只能采纳 ASG 推荐的方案' in p for p in self.d.report()[1]))
        task['delegation']['scope'] = ['clarification']
        role['decision'] = {'option': 'XYZ100 单芯片', 'source': 'delegate:eval-wholeboard:2026-11-07'}
        self.d.write('selection.json', sel)
        self.d.write('task.json', task)
        self.assertTrue(any('scope 不含 selection' in p for p in self.d.report()[1]))

    def test_confirmation_from_the_users_scheme_document(self):
        req = self.d.root / '需求' / '方案.md'
        req.parent.mkdir()
        req.write_text('## 决定表\n\n| D-04 | 稳压器用 XYZ100（用户 2026-10-20 确认） |\n', encoding='utf-8')
        self.d.closure['evidence'].append({'id': 'E-REQ', 'path': '需求/方案.md', 'sha256': sha256(req), 'locator': '决定表'})
        self.d.write('design-closure.json', self.d.closure)
        sel = json.loads(json.dumps(self.d.selection))
        role = sel['roles'][0]
        def problems_with(decision):
            role['decision'] = decision
            self.d.write('selection.json', sel)
            return self.d.report()[1]
        ok = {'source': 'scheme:E-REQ', 'locator': '决定表 D-04', 'quote': '稳压器用 XYZ100（用户 2026-10-20 确认）'}
        self.assertEqual([], problems_with(ok))
        self.assertTrue(any('原文在' in p for p in problems_with(dict(ok, quote='稳压器用 XYZ100（已确认）'))))
        self.assertTrue(any('不含选定型号' in p for p in problems_with(dict(ok, quote='用户 2026-10-20 确认'))))
        self.assertTrue(any('不在 design-closure.json 的 evidence' in p for p in problems_with(dict(ok, source='scheme:E-X'))))
        self.assertTrue(any('ASG 自己写的' in p for p in problems_with(dict(ok, source='scheme:E1'))))

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

    def test_selection_checked_at_task_1_4_before_the_design_netlist_exists(self):
        # Matrix R3 S06: the design netlist is written in task C5.1, so the C3.2 check cannot require its refs;
        # once the netlist exists the binding is checked in full.
        sel = json.loads(json.dumps(self.d.selection))
        sel['roles'][0]['refs'] = ['U9']
        self.assertEqual([], check_selection(json.loads(json.dumps(sel)), {}, self.d.root))
        sel['roles'][0]['candidates'][0]['reason'] = ''
        self.assertIn('候选 XYZ100 没有写选中或淘汰的理由', check_selection(json.loads(json.dumps(sel)), {}, self.d.root))
        sel['roles'][0]['candidates'][0]['reason'] = 'x'
        intent = {'components': [{'ref': 'U1', 'value': 'XYZ100'}]}
        self.assertIn('选型角色“稳压器”的位号 U9 不在设计网表里', check_selection(sel, intent, self.d.root))

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

    def test_blocks_name_a_pattern_approach_or_none(self):
        plan = json.loads((self.d.record / 'page-plan.json').read_text())
        page = plan['pages'][0]
        page['circuits'] = {}
        page['key_blocks'] = ['稳压']
        self.d.write('page-plan.json', plan)
        _, problems = self.d.report()
        self.assertIn('board.kicad_sch：关键功能块“稳压”要标注典型电路与实现方案，库里没有适用的写 none', problems)
        self.assertTrue(any('scheme-criteria.json' in p for p in problems), problems)
        page['circuits'] = {'稳压': 'no-such#做法'}
        self.d.write('page-plan.json', plan)
        _, problems = self.d.report()
        self.assertIn('board.kicad_sch：功能块“稳压”标注的典型电路 no-such 在 references/knowledge/典型电路/ 里不存在', problems)
        page['circuits'] = {'稳压': 'output-filter-storage#不存在的做法'}
        self.d.write('page-plan.json', plan)
        _, problems = self.d.report()
        self.assertTrue(any(p.startswith('board.kicad_sch：功能块“稳压”标注的实现方案“不存在的做法”不在典型电路 output-filter-storage 里') for p in problems), problems)
        plan['pages'].insert(0, {'file': 'PD_root.kicad_sch', 'reader_tasks': ['看流向'], 'blocks': {'能量链': ['U1']}})
        self.d.write('page-plan.json', plan)
        self.d.write('visual-review.json', {'status': 'REVIEWED', 'pdf_sha256': self.d.pdf, 'pages': [
            {'page': 1, 'file': 'board.kicad_sch', 'paths': ['VIN to VOUT'], 'problems': []},
            {'page': 0, 'file': 'PD_root.kicad_sch', 'paths': ['flow'], 'problems': []}]})
        page['circuits'] = {'稳压': 'output-filter-storage#电解/聚合物 + MLCC 并联'}
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
        # Pin text is the library symbol's: one item per symbol, naming the parts drawn with it (2026-11-11).
        listed = ['pin-number:Device/R:unit1: physical pin numbers need native render review',
                  'pin-name:Device/R:unit1: nonunique/noncausal text removal',
                  'hierarchical_label: outline and attached fields need render review']
        summary = json.loads((self.d.record / 'summary.json').read_text())
        summary['gates']['geometry']['render_review_items'] = {'board.kicad_sch': listed, 'other.kicad_sch': listed[:1]}
        summary['gates']['geometry']['render_review_refs'] = {'board.kicad_sch': {k: ['R1', 'U1'] for k in listed[:2]},
                                                              'other.kicad_sch': {listed[0]: ['R7']}}
        self.d.write('summary.json', summary)
        same = '在 R1 上看：引脚号和引脚名清楚，互不相压。'
        def review(items, paths=('VIN to VOUT',)):
            self.d.write('visual-review.json', {'status': 'REVIEWED', 'pdf_sha256': self.d.pdf, 'pages': [
                {'page': 1, 'file': 'board.kicad_sch', 'paths': list(paths), 'problems': [], 'render_review_items': items}]})
            return self.d.report()[1]
        # One sentence may describe several symbols; what matters is that every listed object was looked at.
        self.assertEqual([], review([{'item': k, 'disposition': same} for k in listed]))
        problems = review([{'item': listed[0], 'disposition': same}, {'item': 'pin-name:Device/C:unit1: x', 'disposition': 'C9 看过'}])
        self.assertIn('board.kicad_sch：条目“pin-name:Device/C:unit1: x”不在本版的图面待审对象里', problems)
        self.assertIn('board.kicad_sch：2 个图面待审对象在 visual-review.json 里没有处置（如 %s）' % listed[1][:48],
                      problems)
        # The symbol was read once, on this page: the other page drawing it needs no second disposition.
        self.assertFalse([p for p in problems if p.startswith('other.kicad_sch')], problems)
        problems = review([{'item': listed[0], 'disposition': ''}] + [{'item': k, 'disposition': same} for k in listed[1:]])
        self.assertIn('board.kicad_sch：1 个图面待审对象在 visual-review.json 里没有处置（如 %s）' % listed[0][:48],
                      problems)
        # A disposition says which part it was read on; a sentence that names none could be written without looking.
        problems = review([{'item': k, 'disposition': '引脚号和引脚名都没有被压住。'} for k in listed])
        self.assertIn('board.kicad_sch：条目“%s”的处置要写明看的是哪一只（R1、U1 之一）' % listed[0][:48], problems)
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

    def test_numbers_use_three_significant_digits(self):
        from render_design_report import num
        self.assertEqual(['0.426', '145000', '18', '0.00199', '1.04', '264', '2.67'],
                         [num(v) for v in (0.42632428, 144700.68310544, 18, 0.0019886243943543296, 1.0392525, 264, 2.6666667)])

class PackDesignTests(unittest.TestCase):
    def setUp(self):
        self.d = Delivery()
        self.addCleanup(self.d.cleanup)
        text, _ = self.d.report()
        (self.d.root / REPORT).write_text(text)
        self.inputs = Path(self.d.tmp.name) / 'req'
        self.inputs.mkdir()
        (self.inputs / 'spec.md').write_text('spec')

    def gaps(self):
        knowledge_gaps.main([str(self.d.root)])

    def run_pack(self):
        self.gaps()
        return pack(self.d.root, {'requirements': str(self.inputs)})

    def test_the_knowledge_gap_list_is_extracted_not_written(self):
        path = self.d.root / 'record' / knowledge_gaps.FILE
        path.unlink(missing_ok=True)
        errors, _ = pack(self.d.root, {'requirements': str(self.inputs)})
        self.assertTrue(any('knowledge-gaps.json 缺失' in e for e in errors), errors)
        self.gaps()
        data = json.loads(path.read_text(encoding='utf-8'))
        data['gaps'].append({'signal': 'weak_basis', 'module': 'C4', 'task': 'C4.2', 'item': 'x', 'detail': 'y', 'source': 'z'})
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        errors, _ = pack(self.d.root, {'requirements': str(self.inputs)})
        self.assertTrue(any('与当前记录不一致' in e for e in errors), errors)

    def test_datasheets_not_in_the_library_are_listed_not_rejected(self):
        # 2026-11-04 (user): project datasheets stay in the project; filing them into HardwareWiki is prompted after delivery
        wiki = Path(self.d.tmp.name) / 'wiki'
        (wiki / 'raw' / 'Datasheet' / '08_电源管理' / 'X').mkdir(parents=True)
        (wiki / 'raw' / 'Datasheet' / '08_电源管理' / 'X' / 'X - XYZ100.pdf').write_bytes(b'%PDF-lib')
        sheets = Path(self.d.tmp.name) / 'sheets'
        sheets.mkdir()
        (sheets / 'X - XYZ100.pdf').write_bytes(b'%PDF-copy')
        (sheets / 'Y - ABC200.pdf').write_bytes(b'%PDF-new')
        self.gaps()
        errors, manifest = pack(self.d.root, {'requirements': str(self.inputs), 'datasheets': str(sheets)}, wiki)
        self.assertEqual([], errors)
        self.assertEqual(['Y - ABC200.pdf'], manifest['datasheets_to_file'])
        self.assertIn('datasheets', manifest['inputs'])
        (wiki / 'raw' / 'Datasheet' / '08_电源管理' / 'X' / 'Y - ABC200.pdf').write_bytes(b'%PDF-new')
        errors, manifest = pack(self.d.root, {'requirements': str(self.inputs), 'datasheets': str(sheets)}, wiki)
        self.assertEqual(([], []), (errors, manifest['datasheets_to_file']))

    def test_failed_drawing_gate_cannot_be_packed(self):
        self.d.write('summary.json', {'status': 'FAIL', 'sheets': ['a', 'b'], 'gates': {
            'erc': {'status': 'PASS', 'violations': 0}, 'geometry': {'status': 'FAIL'}}})
        text, _ = self.d.report()
        (self.d.root / REPORT).write_text(text)
        errors, _ = self.run_pack()
        self.assertTrue(any('图面几何' in e for e in errors), errors)

    def test_uncited_guidelines_do_not_block_but_missing_port_documents_do(self):
        # user 2026-11-08 (按草案实施): A1 is gone; a board with external connectors carries FMEA and the EMC port matrix.
        import guideline_criteria
        library = guideline_criteria.load()
        scope = {'library_version': library['library_version'], 'baseline': 'industrial_telecom',
                 'circuit_types': ['I2C'], 'device_kinds': ['resistor'], 'not_applicable': []}

        def repack():
            self.d.closure.update(guideline_version=1, guideline_scope=scope)
            make_current(self.d.closure, self.d.record / 'electrical-intent.json', self.d.root)
            self.d.write('design-closure.json', self.d.closure)
            result = audit(self.d.closure, self.d.record / 'electrical-intent.json', self.d.root)
            self.d.write('design-closure-audit.json', result)
            (self.d.root / REPORT).write_text(self.d.report()[0])
            return result, [e for e in self.run_pack()[0] if '准则' in e or '必写的设计文档' in e]

        result, errors = repack()
        self.assertTrue(result['guidelines']['uncited'])
        self.assertEqual([], errors)
        intent = json.loads((self.d.record / 'electrical-intent.json').read_text())
        intent['components'].append({'ref': 'J1', 'lib_id': 'Connector:Conn_01x02', 'value': 'Conn_01x02'})
        self.d.write('electrical-intent.json', intent)
        self.d.closure['intent_sha256'] = sha256(self.d.record / 'electrical-intent.json')
        _, errors = repack()
        self.assertEqual(1, len(errors), errors)
        self.assertIn('FMEA（FMEA）：有对外连接器 J1', errors[0])
        self.assertIn('EMC（EMC 端口矩阵）', errors[0])

    def test_matrix_cells_without_conclusion_cannot_be_packed(self):
        # SKILL.md C5.2 done mark: no matrix or state-table cell is missing or failing; the audit only marks it pending.
        import pack_design
        real = pack_design.audit

        def with_cells(*args, **kwargs):
            result = real(*args, **kwargs)
            result['pending'] = list(result.get('pending', [])) + [
                {'code': 'matrix_cell_missing', 'item': '受监督轨 +3V3 × U2 最低工作电压'},
                {'code': 'matrix_cell_failed', 'item': '温度 × U3 存储下限'}]
            return result

        with mock.patch.object(pack_design, 'audit', with_cells):
            errors = [e for e in self.run_pack()[0] if '矩阵与状态表' in e]
        self.assertEqual(1, len(errors), errors)
        self.assertIn('2 格缺结论或不满足', errors[0])
        self.assertEqual([], [e for e in self.run_pack()[0] if '矩阵与状态表' in e])

    def test_clean_delivery_packs_with_manifest(self):
        errors, manifest = self.run_pack()
        self.assertEqual(errors, [])
        self.assertEqual(manifest['inputs']['requirements']['kind'], 'directory')
        self.assertIn('原理图/schematic.pdf', manifest['packed'])
        self.assertTrue((self.d.record / 'manifest.json').is_file())
        release = json.loads((Path(__file__).resolve().parents[1] / 'knowledge-sync.json').read_text(encoding='utf-8'))
        self.assertEqual({'knowledge_version': release['knowledge_version'], 'fingerprint': release['fingerprint']},
                         manifest['knowledge_release'])

    def test_extra_files_and_history_fail_but_a_log_does_not(self):
        (self.d.root / 'README.md').write_text('x')
        (self.d.record / 'baseline-v05').mkdir()
        (self.d.record / 'run.log').write_text('x')
        errors, _ = self.run_pack()
        self.assertTrue(any('README.md' in e for e in errors))
        self.assertTrue(any('record/baseline-v05/' in e for e in errors))
        self.assertFalse(any('run.log' in e for e in errors), errors)

    def test_an_sr_review_folder_is_a_delivery_folder(self):
        # Industrial I/O calibration board 2026-11-03: the SR run of this version sits in record/sr-review/.
        (self.d.record / 'sr-review').mkdir()
        (self.d.record / 'sr-review' / 'findings.json').write_text('{}')
        errors, _ = self.run_pack()
        self.assertFalse(any('sr-review' in e for e in errors), errors)

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

    def test_design_document_prose_names_the_parts_the_design_has(self):
        # Matrix R2 (2026-11-04): 供电路径复核.md kept "U801 LM5060" after U801 became an LTC4367.
        self.d.write('electrical-intent.json', {'components': [
            {'ref': 'U1', 'mpn': 'LTC4367HMS8#PBF', 'value': 'LTC4367HMS8'},
            {'ref': 'U2', 'mpn': 'LM5069MM-1/NOPB', 'value': 'LM5069MM-1'},
            {'ref': 'U3', 'mpn': 'SN74LVC07APWR', 'value': 'SN74LVC07APWR'},
            {'ref': 'J1', 'mpn': '3915-P04-1ZW4WDBR1', 'value': '3915-P04'}, {'ref': 'R1', 'value': '10k'}]})
        self.d.closure['intent_sha256'] = sha256(self.d.record / 'electrical-intent.json')
        self.d.write('design-closure.json', self.d.closure)
        (self.d.root / '设计资料' / '供电路径复核.md').write_text('\n'.join([
            '# 复核',
            'U1 LM5060 的 OV 门限按 Rev D p4 取。',             # line 2: stale part number
            'U1 LTC4367 关断 ≤16 µs；U2 LM5069-1 限流；U3 LVC07A 缓冲。',  # base, variant and family prefix agree
            'J1 Pin3/4 接 24 V，R1 10kΩ，C7 ~100uF，CR-R301: 检流，TPS62903 SW 开关节点。',  # not part numbers / not refs
            '| U1 | LM5060 | 表格行按列核 |',
            '```', 'U1 LM5060', '```',
            'U9 TPS259814 已删除。']), encoding='utf-8')   # line 9: not in the design
        errors, _ = self.run_pack()
        prose = [e for e in errors if '供电路径复核.md' in e]
        self.assertEqual(2, len(prose), prose)
        self.assertTrue(any('供电路径复核.md line 2: text says U1 LM5060, the design has U1 LTC4367HMS8#PBF' in e
                            for e in prose), prose)
        self.assertTrue(any('供电路径复核.md line 9: U9 TPS259814 is not in the design' in e for e in prose), prose)

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
