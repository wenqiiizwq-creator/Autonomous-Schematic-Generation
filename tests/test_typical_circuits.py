"""典型电路选择资料及来源检查；不以库声明强制设计准则范围。"""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import typical_circuits  # noqa: E402
import guideline_criteria  # noqa: E402
from audit_design_closure import audit, sha256  # noqa: E402
import find_parts  # noqa: E402

LIBRARY = guideline_criteria.load()
RULES = {r['id']: r for r in LIBRARY['criteria']}
CIRCUITS = typical_circuits.load()


class PatternFileTests(unittest.TestCase):
    def test_every_pattern_declares_vocabulary_circuit_types(self):
        names = set(guideline_criteria.vocabulary()['vocabulary']['circuit_types'])
        self.assertTrue(CIRCUITS)   # without README.md
        for pid, info in CIRCUITS.items():
            self.assertIsNotNone(info['circuit_types'], '%s 缺 电路类型： 一行（没有对应类型写 无）' % pid)
            self.assertEqual(set(), set(info['circuit_types']) - names, (pid, info['circuit_types']))

    def test_optional_rules_if_present_name_existing_active_rules(self):
        for pid, info in CIRCUITS.items():
            self.assertTrue(info['implementations'] or pid == 'reviewed-bias-and-latch', pid)   # a pointer entry
            for name, approach in info['implementations'].items():
                rules = approach['criteria'] or []
                self.assertEqual(len(rules), len(set(rules)), (pid, name))
                for gid in rules:
                    self.assertIn(gid, RULES, (pid, name, gid))
                    self.assertEqual(RULES[gid]['status'], 'active', (pid, name, gid))

    def test_the_swd_port_claims_the_g09_debug_rules_it_puts_into_practice(self):
        # G09 定稿接入项（2026-11-05）：swd-debug 的“落实规则：无”换成它真实做到的 G09 规则；上下拉（G09-011）、
        # 手接静电（G09-026）没有写进做法，不列。
        rules = CIRCUITS['swd-debug']['implementations']['10 针 1.27 mm 排针（SWD 引脚排列）']['criteria']
        self.assertTrue({'G09-010', 'G09-012', 'G09-013', 'G09-015'} <= set(rules), rules)

    def test_only_the_implementation_section_holds_implementations(self):
        # power-rail-test-break has ### headings under 「断点开路时的两类故障」; they are not approaches.
        names = CIRCUITS['power-rail-test-break']['implementations']
        self.assertTrue(names)
        self.assertFalse({'反馈丢失，输出升高', '使能脚悬空'} & set(names))
        self.assertNotIn('README', CIRCUITS)
        self.assertEqual(['ANALOG'], CIRCUITS['current-loop-4-20ma']['circuit_types'])

    def test_the_parser_agrees_with_find_parts_on_the_implementations(self):
        index = find_parts.circuit_index()
        self.assertEqual({pid: list(info['implementations']) for pid, info in CIRCUITS.items()},
                         {pid: info['implementations'] for pid, info in index.items()})

    def test_an_explicit_none_line_claims_no_rule_even_when_it_names_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'p.md').write_text('# 甲\n\n功能：x。\n\n电路类型：无\n\n## 实现方案\n\n### 做法一\n\n'
                                           '- **落实规则**：无（对应 G05-036，待规范放宽）\n- **已知坑**：\n', encoding='utf-8')
            info = typical_circuits.load(tmp)['p']
        self.assertEqual(info['circuit_types'], [])
        self.assertEqual(info['implementations']['做法一']['criteria'], [])



def card(rid, **changes):
    out = {'id': rid, 'title': '示例规则 ' + rid, 'spec': rid[:3], 'version': '0.1', 'status': 'active',
           'nature': 'shall', 'applies_when': {'board': True}, 'inputs': [], 'asg_action': '设计动作',
           'sr_check': '审查方法', 'source': [{'document': 'GB/T 17799.2', 'edition': '2023', 'clause': '表4', 'page': 9}],
           'closing_stage': 'schematic'}
    out.update(changes)
    return out


def library(*cards):
    out = copy.deepcopy(LIBRARY)
    out['criteria'] = sorted(cards, key=lambda r: r['id'])
    out['content_sha256'] = guideline_criteria.content_sha256(out['criteria'])
    return out


TEST_LIBRARY = library(card('G01-001'), card('G03-001', applies_when={'circuit_types': ['POWER_CONVERTER']}),
                       card('G05-001', applies_when={'device_kinds': ['fuse']}))
PATTERN_MD = ('# 测试模式\n\n功能：x。\n\n适用范围：y。\n\n电路类型：POWER_CONVERTER\n\n## 实现方案\n\n### 做法甲\n\n'
              '- **必算项**：z\n- **落实规则**：G03-001、G05-001\n- **已知坑**：\n- **来源**：\n')


class PatternClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.patterns = self.root / 'circuits'
        self.patterns.mkdir()
        (self.patterns / 'test-pattern.md').write_text(PATTERN_MD, encoding='utf-8')
        (self.root / 'record').mkdir()
        (self.root / 'record' / 'page-plan.json').write_text(json.dumps(
            {'schema_version': 1, 'pages': [{'file': 'a.kicad_sch', 'circuits': {'电源': 'test-pattern#做法甲'}}]}))
        self.intent = self.root / 'intent.json'
        self.intent.write_text(json.dumps({'components': [{'ref': 'U1', 'lib_id': 'Regulator:X', 'value': 'X'}]}))
        (self.root / 'design.txt').write_text('evidence\n')
        self.record = {
            'schema_version': 1, 'coverage': 'complete', 'intent_sha256': sha256(self.intent), 'guideline_version': 1,
            'guideline_scope': {'library_version': TEST_LIBRARY['library_version'], 'baseline': 'industrial_telecom',
                                'circuit_types': ['POWER_CONVERTER'], 'device_kinds': ['fuse'], 'not_applicable': []},
            'evidence': [{'id': 'E1', 'path': 'design.txt', 'sha256': sha256(self.root / 'design.txt'), 'locator': 'l1'}],
            'requirements': [{'id': 'R1', 'status': 'design_supported', 'refs': ['U1'], 'evidence': ['E1'],
                              'implementation': '电源', 'depends_on': []}],
            'work_items': [],
            'calculations': [{'id': 'C1', 'requirements': ['R1'], 'evidence': ['E1'], 'refs': ['U1'],
                              'coverage': 'bounded', 'conclusion': 'supported', 'assumptions': [],
                              'omitted_terms': [], 'guidelines': ['G01-001', 'G03-001', 'G05-001']}]}

    def run_audit(self):
        with mock.patch.object(guideline_criteria, 'load', lambda *args: TEST_LIBRARY), \
                mock.patch.object(typical_circuits, 'default_circuits_dir', lambda: self.patterns):
            return audit(self.record, self.intent, self.root)

    def codes(self, result):
        return {e['code'] for e in result['errors']} | {p['code'] for p in result['pending']}

    def test_pattern_metadata_does_not_expand_board_scope(self):
        self.record['guideline_scope']['circuit_types'] = []
        self.record['guideline_scope']['device_kinds'] = []
        self.record['calculations'][0]['guidelines'] = ['G01-001']
        result = self.run_audit()
        self.assertFalse({c for c in self.codes(result) if c.startswith('guideline')}, result)

    def test_board_applicable_rules_are_listed_by_the_board_scope(self):
        # The pattern does not narrow the board's scope; an uncited rule is listed, not pending (user 2026-11-08: 按草案实施).
        self.record['calculations'][0]['guidelines'] = ['G01-001']
        result = self.run_audit()
        self.assertIn('G03-001', result['guidelines']['uncited'])
        self.assertNotIn('guideline_uncovered', self.codes(result))


if __name__ == '__main__':
    unittest.main()
