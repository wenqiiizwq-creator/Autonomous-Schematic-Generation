"""Improvement 8 (user 2026-11-07: 按推荐实施): rules an audit check proves are covered by the check passing, and the
board-wide method and document rules by one design document whose sections and objects are all there, instead of one
hand-written citation each. A declared document that falls short leaves its rules uncovered."""
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import guideline_criteria
import render_design_report
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


setUpModule, tearDownModule = base.setUpModule, base.tearDownModule


class EvidenceGroupTests(unittest.TestCase):
    """The record of test_guideline_closure, with a connector J1 added."""
    run_audit, codes = base.GuidelineClosureTests.run_audit, base.GuidelineClosureTests.codes

    def setUp(self):
        base.GuidelineClosureTests.setUp(self)
        self.intent.write_text(json.dumps({'components': [
            {'ref': 'U1', 'lib_id': 'Interface:RS485', 'value': 'X'},
            {'ref': 'J1', 'lib_id': 'Connector:Conn_01x02', 'value': 'Conn_01x02'}]}))
        self.record['intent_sha256'] = sha256(self.intent)
        self.record['calculations'][0]['guidelines'] = ['G01-001', 'G04-001']

    def run_groups(self):
        return self.run_audit(LIB)

    def write_fmea(self, body=FMEA, carrier='FMEA'):
        (self.root / 'fmea.md').write_text(body, encoding='utf-8')
        self.record['evidence'].append({'id': 'E-FMEA', 'path': 'fmea.md', 'sha256': sha256(self.root / 'fmea.md'),
                                        'locator': '全文', 'carrier': carrier})

    def test_the_groups_name_item_rules_of_the_installed_library_once(self):
        groups, lib = load_guideline_groups(), {r['id']: r for r in guideline_criteria.load()['criteria']}
        named = list(groups['checks']) + [g for c in groups['carriers'].values() for g in c['rules']]
        self.assertEqual(len(named), len(set(named)))
        for gid in named:
            self.assertEqual(guideline_criteria.coverage_class(lib[gid]), 'item', gid)
            self.assertEqual(lib[gid]['closing_stage'], 'schematic', gid)
            self.assertEqual(lib[gid]['status'], 'active', gid)
        for name, c in groups['carriers'].items():
            self.assertTrue(c['sections'] and all(s['match'] for s in c['sections']), name)

    def test_a_passing_check_covers_its_rule_and_a_failing_one_does_not(self):
        self.write_fmea()
        result = self.run_groups()
        self.assertEqual(result['guidelines']['covered']['G09-018'], ['check:装配状态独立字段'])
        self.assertEqual(result['guidelines']['by_group']['check'], {'G09-018': '装配状态独立字段'})
        components = json.loads(self.intent.read_text())['components'] + [{'ref': 'R1', 'lib_id': 'Device:R', 'value': '10k DNP'}]
        self.intent.write_text(json.dumps({'components': components}))
        self.record['intent_sha256'] = sha256(self.intent)
        result = self.run_groups()
        self.assertIn('G09-018', result['guidelines']['uncovered'])
        self.assertTrue(any('G09-018' in p['item'] and 'dnp_in_value' in p['item'] for p in result['pending']), result['pending'])

    def test_a_check_that_did_not_run_covers_nothing(self):
        lib = library(card('G01-001'), card('G04-001', applies_when={'circuit_types': ['RS485']}), card('G02-038'))
        result = self.run_audit(lib)   # G02-038 needs binding_version 1
        self.assertIn('G02-038', result['guidelines']['uncovered'])
        self.assertTrue(any('binding_version' in p['item'] for p in result['pending'] if p['code'] == 'guideline_uncovered'))

    def test_a_complete_document_covers_its_group(self):
        self.write_fmea()
        result = self.run_groups()
        found = result['guidelines']
        self.assertNotIn('guideline_carrier_incomplete', self.codes(result))
        self.assertEqual(found['covered']['G05-001'], ['carrier:E-FMEA'])
        self.assertEqual(found['covered']['G05-002'], ['carrier:E-FMEA'])
        self.assertEqual(found['by_group']['carrier']['FMEA'], {'evidence': ['E-FMEA'], 'rules': ['G05-001', 'G05-002'],
                                                                'problems': []})
        self.assertNotIn('guideline_uncovered', self.codes(result))

    def test_a_missing_or_empty_section_or_object_leaves_the_group_uncovered(self):
        for broken, word in ((FMEA.replace('## 潜伏故障\nTVS 开路无告警，登记待测。\n', ''), '缺“潜伏故障”'),
                             (FMEA.replace('TVS 开路无告警，登记待测。', ''), '“潜伏故障”是空的'),
                             (FMEA.replace('J1', 'J10'), '没写到 J1')):
            with self.subTest(word=word):
                self.record['evidence'] = self.record['evidence'][:1]
                self.write_fmea(broken)
                result = self.run_groups()
                problem = [p['item'] for p in result['pending'] if p['code'] == 'guideline_carrier_incomplete']
                self.assertEqual(len(problem), 1, result['pending'])
                self.assertIn(word, problem[0])
                self.assertIn('G05-001', result['guidelines']['uncovered'])

    def test_a_declared_group_is_not_rescued_by_a_stray_citation(self):
        self.write_fmea(FMEA.replace('## 关键项', '## 别的'))
        self.record['calculations'][0]['guidelines'] = ['G01-001', 'G04-001', 'G05-001', 'G05-002']
        self.assertIn('G05-001', self.run_groups()['guidelines']['uncovered'])

    def test_an_undeclared_group_still_counts_its_citations(self):
        self.record['calculations'][0]['guidelines'] = ['G01-001', 'G04-001', 'G05-001', 'G05-002']
        result = self.run_groups()
        self.assertEqual(result['guidelines']['covered']['G05-001'], ['calc:C1'])
        self.assertEqual(result['guidelines']['by_group']['carrier'], {})

    def test_an_unknown_group_name_is_an_error(self):
        self.write_fmea(carrier='失效分析')
        self.assertIn('guideline_carrier_unknown', self.codes(self.run_groups()))

    def test_the_report_lists_the_groups_apart(self):
        self.write_fmea()
        found = self.run_groups()['guidelines']
        with mock.patch.object(guideline_criteria, 'load', lambda *args: LIB):
            text = '\n'.join(render_design_report.render_guidelines(found))
        self.assertIn('| G09-018 | 示例规则 G09-018 | 装配状态独立字段 |', text)
        self.assertIn('| FMEA | E-FMEA | G05-001、G05-002 | 齐全 |', text)
        main = text.split('## 由自动检查覆盖')[0]
        self.assertNotIn('G05-001', main)
        self.assertIn('G04-001', main)

    def test_markdown_sections_and_mentions(self):
        lines = ['# A', '', '## B', '', '## C', 'text', '| x | y |', '|---|---|', '| | |']
        self.assertEqual(markdown_sections(lines), [('A', True), ('B', False), ('C', True), ('| x | y |', False)])
        self.assertTrue(mentions('见 J1。', 'J1'))
        self.assertFalse(mentions('见 J10', 'J1'))
        self.assertTrue(mentions('J1-3 脚', 'J1'))
        self.assertFalse(mentions('CALC-IN-SURGE', 'CALC-IN'))


if __name__ == '__main__':
    unittest.main()
