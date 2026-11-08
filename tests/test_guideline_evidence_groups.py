"""User 2026-11-08 (按草案实施): only the guideline rules that rule out a scheme candidate, change a selection or enter a
calculation are implemented one by one; an uncited rule raises nothing. A board with external connectors carries the FMEA
and the EMC port matrix, each with all its sections and every connector (references/guideline-evidence-groups.md)."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_design_closure import load_guideline_groups, markdown_sections, mentions, sha256
import test_guideline_closure as base
from test_guideline_closure import card, library

LIB = library(card('G01-001'), card('G04-001', applies_when={'circuit_types': ['RS485']}),
              card('G05-001'), card('G05-002'), card('G09-018'))

FMEA = '''# FMEA

## 范围与判定准则
只看电源入口与 J1。

## 条目
| 对象 | 失效模式 | 传播 | 严重度 | 检测 | 处置 |
|---|---|---|---|---|---|
| J1 | 对地短路 | 不传到 U1 | 3 | 无 | 加限流 |

## 覆盖表
J1 → 条目 1。

## 关键项
无单点关键项：J1 短路只丢通信。

## 潜伏故障
TVS 开路无告警，登记待测。

## 共同原因
限流与被保护器件不共用基准。

## 软件响应
无软件参与。

## 版本
对应原理图 v1。
'''

EMC = '''# EMC 端口矩阵

| 端口 | 归类 | 判据 | 浪涌 | 耦合 | 源阻抗 | 波形 | 极性 | 屏蔽 | 泄放 | 机壳 | 跨端口 | 静电 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| J1 | 信号端口 | B | 1 kV 线对地 | 线对地 | 42 Ω | 1.2/50 µs | 正负 | 非屏蔽 | 经 TVS 到 PE | 单点 | 无 | 接触 4 kV |
'''


setUpModule, tearDownModule = base.setUpModule, base.tearDownModule


class DesignDocumentTests(unittest.TestCase):
    """The record of test_guideline_closure, with a connector J1 added."""
    run_audit, codes = base.GuidelineClosureTests.run_audit, base.GuidelineClosureTests.codes

    def setUp(self):
        base.GuidelineClosureTests.setUp(self)
        self.intent.write_text(json.dumps({'components': [
            {'ref': 'U1', 'lib_id': 'Interface:RS485', 'value': 'X'},
            {'ref': 'J1', 'lib_id': 'Connector:Conn_01x02', 'value': 'Conn_01x02'}]}))
        self.record['intent_sha256'] = sha256(self.intent)
        self.record['calculations'][0]['guidelines'] = ['G01-001', 'G04-001']

    def run_docs(self):
        return self.run_audit(LIB)

    def write_doc(self, name, body, carrier):
        (self.root / name).write_text(body, encoding='utf-8')
        self.record['evidence'].append({'id': 'E-' + carrier, 'path': name, 'sha256': sha256(self.root / name),
                                        'locator': '全文', 'carrier': carrier})

    def incomplete(self, result):
        return [p['item'] for p in result['pending'] if p['code'] == 'design_document_incomplete']

    def test_only_fmea_and_the_emc_port_matrix_are_required(self):
        groups = load_guideline_groups()
        self.assertEqual(sorted(groups['carriers']), ['EMC', 'FMEA'])
        self.assertNotIn('checks', groups)
        for name, c in groups['carriers'].items():
            self.assertEqual(c['objects'], 'connectors', name)
            self.assertTrue(c['sections'] and all(s['match'] for s in c['sections']), name)

    def test_an_uncited_rule_raises_nothing(self):
        self.record['work_items'][0]['guidelines'] = []     # G07-001 is not in this library
        self.write_doc('fmea.md', FMEA, 'FMEA')
        self.write_doc('emc.md', EMC, 'EMC')
        result = self.run_docs()
        self.assertFalse({c for c in self.codes(result) if c.startswith(('guideline', 'design_document'))}, result)
        self.assertEqual(result['guidelines']['uncited'], ['G05-001', 'G05-002', 'G09-018'])
        self.assertEqual(result['guidelines']['documents']['FMEA'], {'evidence': ['E-FMEA'], 'objects': ['J1'], 'problems': []})

    def test_a_board_with_a_connector_carries_both_documents(self):
        missing = self.incomplete(self.run_docs())
        self.assertEqual(2, len(missing), missing)
        self.assertTrue(missing[0].startswith('FMEA（FMEA）：有对外连接器 J1，没有登记这份文档'), missing)
        self.write_doc('fmea.md', FMEA, 'FMEA')
        missing = self.incomplete(self.run_docs())
        self.assertEqual(1, len(missing), missing)
        self.assertTrue(missing[0].startswith('EMC（EMC 端口矩阵）'), missing)

    def test_a_board_without_connectors_needs_neither(self):
        self.intent.write_text(json.dumps({'components': [{'ref': 'U1', 'lib_id': 'Interface:RS485', 'value': 'X'}]}))
        self.record['intent_sha256'] = sha256(self.intent)
        self.assertEqual([], self.incomplete(self.run_docs()))

    def test_a_missing_or_empty_section_or_connector_is_named(self):
        for broken, word in ((FMEA.replace('## 潜伏故障\nTVS 开路无告警，登记待测。\n', ''), '缺“潜伏故障”'),
                             (FMEA.replace('TVS 开路无告警，登记待测。', ''), '“潜伏故障”是空的'),
                             (FMEA.replace('J1', 'J10'), '没写到 J1')):
            with self.subTest(word=word):
                self.record['evidence'] = self.record['evidence'][:1]
                self.write_doc('fmea.md', broken, 'FMEA')
                self.write_doc('emc.md', EMC, 'EMC')
                problem = self.incomplete(self.run_docs())
                self.assertEqual(len(problem), 1, problem)
                self.assertIn(word, problem[0])

    def test_an_unknown_document_name_is_an_error(self):
        self.write_doc('fmea.md', FMEA, '失效分析')
        self.assertIn('guideline_carrier_unknown', self.codes(self.run_docs()))

    def test_markdown_sections_and_mentions(self):
        lines = ['# A', '', '## B', '', '## C', 'text', '| x | y |', '|---|---|', '| | |']
        self.assertEqual(markdown_sections(lines), [('A', True), ('B', False), ('C', True), ('| x | y |', False)])
        self.assertTrue(mentions('见 J1。', 'J1'))
        self.assertFalse(mentions('见 J10', 'J1'))
        self.assertTrue(mentions('J1-3 脚', 'J1'))
        self.assertFalse(mentions('CALC-IN-SURGE', 'CALC-IN'))


if __name__ == '__main__':
    unittest.main()
