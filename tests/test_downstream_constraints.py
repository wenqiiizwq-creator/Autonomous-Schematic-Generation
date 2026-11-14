"""downstream_version 1 (user 2026-11-13: 照草案写入, docs/草案-下游约束表.md). AD9361 board: U301 at an estimated
104 °C junction against 85 °C derated carried a heat sink only in an `improvement` cell and a validation item "measure it on
the sample"; PCB and the enclosure were never told, and the rules closing after the schematic were handed to no one.
Every board carries 设计资料/下游约束表.md: a temperature stress risk, or any severe stress, not fixed in the schematic names
the rows that carry its boundary; every applicable rule closing after the schematic has a row or a not-applicable reason."""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_design_closure import markdown_table_rows, sha256  # noqa: E402
import test_derating_audit as derating  # noqa: E402
import test_guideline_closure as base  # noqa: E402
from test_design_report import Delivery  # noqa: E402

setUpModule, tearDownModule = derating.setUpModule, derating.tearDownModule

HEAD = '| 编号 | 接收方 | 对象 | 约束 | 依据 | 验收 |\n|---|---|---|---|---|---|\n'
TJ_ROW = ('| D-1 | 结构、PCB | U1 | 结到环境热阻 ≤ 21.9 ℃/W；顶面散热片接壳，U1 地脚下打满过孔 | C-TJ、G08-047 | '
          '45 ℃ 满载实测壳温换算结温 ≤ 85 ℃ |\n')


def write_table(root, record, body, name='下游约束表.md'):
    (root / name).write_text('# 下游约束表\n\n' + HEAD + body, encoding='utf-8')
    record['evidence'] = [e for e in record['evidence'] if e.get('carrier') != 'DOWNSTREAM'] + [
        {'id': 'E-DS', 'path': name, 'sha256': sha256(root / name), 'locator': '全表', 'carrier': 'DOWNSTREAM'}]


class StressRiskTests(unittest.TestCase):
    """The severe junction-temperature case of test_derating_audit (146 °C against 95 °C, 150 °C absolute)."""

    def setUp(self):
        case = derating.SevereStressTests('test_near_the_rating_needs_a_p1_item')
        case.setUp()
        self.addCleanup(case.doCleanups)
        self.case, self.base = case, case.base
        case.item()                                    # validation item, damage, fault: P1 — enough before this change
        self.base.record['downstream_version'] = 1

    @property
    def check(self):
        return self.case.check

    def result(self):
        return self.base.run_audit()

    def codes(self):
        r = self.result()
        return {e['code'] for e in r['errors']} | {p['code'] for p in r['pending']}

    def test_an_undeclared_record_is_unchanged(self):
        del self.base.record['downstream_version']
        result = self.result()
        self.assertEqual(set(), {e['code'] for e in result['errors']})
        self.assertEqual({'status': 'NOT_DECLARED'}, result['downstream'])

    def test_a_validation_item_alone_does_not_hand_the_boundary_on(self):
        self.assertIn('stress_risk_without_downstream', self.codes())

    def test_a_design_item_fixes_it_in_the_schematic(self):
        self.case.item(stage='design', status='open')
        self.base.record['requirements'][0]['status'] = 'conditional'
        self.assertNotIn('stress_risk_without_downstream', self.codes())

    def test_the_named_row_carries_the_calculation(self):
        self.check['downstream'] = ['D-1']
        codes = self.codes()
        self.assertIn('downstream_unknown_row', codes)
        self.assertIn('design_document_incomplete', codes)
        write_table(self.base.root, self.base.record, TJ_ROW)
        result = self.result()
        self.assertEqual(set(), {e['code'] for e in result['errors']}, result['errors'])
        self.assertEqual('PASS', result['downstream']['status'])
        self.assertEqual(['D-1'], result['derating']['stress_risks'][0]['downstream'])
        self.assertEqual(['结构', 'PCB'], result['downstream']['rows'][0]['receivers'])
        write_table(self.base.root, self.base.record, TJ_ROW.replace('C-TJ、', ''))
        self.assertIn('downstream_row_not_citing', self.codes())

    def test_a_plain_temperature_risk_is_handed_on_too(self):
        self.check['value'] = 100.1                    # over 95, within III's 105: no work item needed, still a boundary
        self.base.record['work_items'] = []
        self.base.record['requirements'][0]['depends_on'] = []
        self.check.pop('work_item')
        self.assertIn('stress_risk_without_downstream', self.codes())

    def test_a_row_is_complete(self):
        self.check['downstream'] = ['D-1']
        for row, word in ((TJ_ROW.replace('45 ℃ 满载实测壳温换算结温 ≤ 85 ℃', ''), '缺 验收'),
                          (TJ_ROW.replace('结构、PCB', '散热组'), '散热组'),
                          (TJ_ROW.replace('D-1', 'X1'), 'D-<序号>')):
            with self.subTest(word=word):
                write_table(self.base.root, self.base.record, row)
                items = [e['item'] for e in self.result()['errors'] if e['code'] == 'downstream_row_incomplete']
                self.assertTrue(items and word in items[0], items)

    def test_markdown_table_rows(self):
        lines = (HEAD + TJ_ROW + '| | | | | | |\n').splitlines() + ['']
        rows = markdown_table_rows(lines, ('编号', '验收'))
        self.assertEqual([{'编号': 'D-1', '验收': '45 ℃ 满载实测壳温换算结温 ≤ 85 ℃'}], rows)


class GuidelineTests(unittest.TestCase):
    """The record of test_guideline_closure: G07-001 applies and closes at PCB."""
    run_audit = base.GuidelineClosureTests.run_audit

    def setUp(self):
        env = mock.patch.dict(os.environ)          # this class brings its own library, as test_guideline_closure does
        env.start()
        self.addCleanup(env.stop)
        for key in ('GUIDELINE_CRITERIA', 'GUIDELINE_CRITERIA_TESTING'):
            os.environ.pop(key, None)
        base.GuidelineClosureTests.setUp(self)
        self.record['downstream_version'] = 1

    def pending(self, result=None):
        return [p['item'] for p in (result or self.run_audit())['pending'] if p['code'] == 'downstream_constraint_missing']

    def test_a_rule_closing_downstream_needs_a_row(self):
        write_table(self.root, self.record, TJ_ROW.replace('C-TJ、G08-047', 'G01-001'))
        missing = self.pending()
        self.assertEqual(1, len(missing), missing)
        self.assertTrue(missing[0].startswith('G07-001'), missing)
        write_table(self.root, self.record, TJ_ROW.replace('C-TJ、G08-047', 'G07-001'))
        self.assertEqual([], self.pending())

    def test_a_reason_holds_it_not_applicable(self):
        write_table(self.root, self.record, TJ_ROW.replace('C-TJ、G08-047', 'G01-001'))
        self.record['work_items'][0]['guidelines'] = []
        self.record['guideline_scope']['not_applicable'] = [{'id': 'G07-001', 'reason': '本板没有对外端口'}]
        self.assertEqual([], self.pending())

    def test_a_row_hands_a_cited_rule_on_without_a_work_item(self):
        self.record['work_items'][0]['guidelines'] = []
        self.record['calculations'][0]['guidelines'].append('G07-001')
        codes = {e['code'] for e in self.run_audit()['errors']}
        self.assertIn('guideline_downstream_without_work_item', codes)
        write_table(self.root, self.record, TJ_ROW.replace('C-TJ、G08-047', 'G07-001'))
        codes = {e['code'] for e in self.run_audit()['errors']}
        self.assertNotIn('guideline_downstream_without_work_item', codes)

    def test_the_table_is_required(self):
        result = self.run_audit()
        self.assertTrue(any(p['code'] == 'design_document_incomplete' and p['item'].startswith('DOWNSTREAM')
                            for p in result['pending']), result['pending'])
        self.assertEqual('INCOMPLETE', result['downstream']['status'])


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.d = Delivery()
        self.addCleanup(self.d.cleanup)

    def test_handoff_section_groups_by_receiver_and_leads_with_severe_rows(self):
        audit_result = json.loads((self.d.record / 'design-closure-audit.json').read_text(encoding='utf-8'))
        audit_result['derating'] = {'level': 'III', 'source': 'req:R-DER', 'hints': [], 'stress_risks': [
            {'calculation': 'C1', 'check': 'U1 结温', 'ref': 'U1', 'rule': 'IC-OTH-TJ', 'value': 104, 'limit': 85,
             'rating': 110, 'unit': '℃', 'improvement': '散热片', 'required_severity': 'P1', 'work_item': 'W-TEST',
             'downstream': ['D-2']}]}
        row = lambda rid, who, what, basis: {'编号': rid, '接收方': who, '对象': 'U1', '约束': what, '依据': basis,  # noqa: E731
                                             '验收': '实测', 'receivers': who.split('、'), 'cites': []}
        audit_result['downstream'] = {'status': 'PASS', 'evidence': ['E-DS'], 'missing_guidelines': [], 'rows': [
            row('D-1', 'PCB', '爬电 ≥ 2.5 mm', 'G06-024'), row('D-2', '结构、PCB', '热阻 ≤ 21.9 ℃/W', 'C1、G08-047')]}
        self.d.write('design-closure-audit.json', audit_result)
        text, _ = self.d.report()
        self.assertIn('- **技术转交**：下游约束表 2 行（PCB 2、结构 1），其中挂在应力超幅上的 1 行；另有转交待办 1 件。', text)
        section = text.split('## 技术转交要求')[1].split('\n## ')[0]
        pcb = section.split('### PCB（2 条）')[1].split('###')[0]
        self.assertLess(pcb.index('D-2'), pcb.index('D-1'))
        self.assertIn('| D-2 | U1 | **应力超幅 P1** 热阻 ≤ 21.9 ℃/W | C1、G08-047 | 实测 |', pcb)
        self.assertIn('### 结构（1 条）', section)
        self.assertIn('### 样机与 PCB 的转交待办', section)
        risks = text.split('## 应力风险')[1].split('\n## ')[0]
        self.assertIn('| 散热片 | W-TEST 要求 P1 | D-2 |', risks)


if __name__ == '__main__':
    unittest.main()
