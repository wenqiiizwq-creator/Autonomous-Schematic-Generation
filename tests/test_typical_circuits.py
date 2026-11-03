"""The circuit-pattern library maps its implementations to shared guideline rules (typical_circuits.py): every pattern declares
its vocabulary circuit types, every approach lists the active rules it puts into practice, and the closure audit holds a
design to what the page plan's patterns claim."""
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
        self.assertEqual(len(CIRCUITS), 19)
        for pid, info in CIRCUITS.items():
            self.assertIsNotNone(info['circuit_types'], '%s 缺 电路类型： 一行（没有对应类型写 无）' % pid)
            self.assertTrue(set(info['circuit_types']) <= names, (pid, info['circuit_types']))

    def test_every_approach_lists_its_rules_and_they_fit(self):
        for pid, info in CIRCUITS.items():
            self.assertTrue(info['implementations'], pid)
            for name, approach in info['implementations'].items():
                rules = approach['criteria']
                self.assertIsNotNone(rules, '%s#%s 缺 落实规则 一行（没有写 无）' % (pid, name))
                self.assertEqual(len(rules), len(set(rules)), (pid, name))
                for gid in rules:
                    self.assertIn(gid, RULES, (pid, name, gid))
                    rule = RULES[gid]
                    self.assertEqual(rule['status'], 'active', (pid, name, gid))
                    baselines = rule['applies_when'].get('baselines') or []
                    self.assertTrue(not baselines or LIBRARY['default_baseline'] in baselines, (pid, name, gid))
                    when = rule['applies_when']
                    self.assertTrue(when.get('board') or when.get('device_kinds')
                                    or set(when.get('circuit_types') or []) & set(info['circuit_types']),
                                    '%s#%s 引用 %s，但它既不是全板规则、不按器件类别触发，也不命名典型电路声明的电路类型' % (pid, name, gid))

    def test_the_parser_agrees_with_find_parts_on_the_implementations(self):
        index = find_parts.circuit_index()
        self.assertEqual({pid: list(info['implementations']) for pid, info in CIRCUITS.items()},
                         {pid: info['implementations'] for pid, info in index.items()})

    def test_an_explicit_none_line_claims_no_rule_even_when_it_names_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'p.md').write_text('# 甲\n\n功能：x。\n\n电路类型：无\n\n## 做法\n\n### 做法一\n\n'
                                           '- **落实规则**：无（对应 G05-036，待规范放宽）\n- **已知坑**：\n', encoding='utf-8')
            info = typical_circuits.load(tmp)['p']
        self.assertEqual(info['circuit_types'], [])
        self.assertEqual(info['implementations']['做法一']['criteria'], [])

    def test_claimed_collects_types_and_rules_of_the_named_implementations(self):
        got = typical_circuits.claimed(['pfc-boost#CrM/多模 PFC 控制器 + 外置 MOSFET + 升压二极管', 'no-such#做法',
                                        'zcd-sensing#不存在的做法'])
        self.assertEqual(got['circuit_types'], {'POWER_CONVERTER': ['pfc-boost#CrM/多模 PFC 控制器 + 外置 MOSFET + 升压二极管']})
        self.assertEqual(set(got['criteria']), set(CIRCUITS['pfc-boost']['implementations']['CrM/多模 PFC 控制器 + 外置 MOSFET + 升压二极管']['criteria']))


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
PATTERN_MD = ('# 测试模式\n\n功能：x。\n\n适用范围：y。\n\n电路类型：POWER_CONVERTER\n\n## 做法\n\n### 做法甲\n\n'
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
                mock.patch.object(typical_circuits, 'CIRCUITS_DIR', self.patterns):
            return audit(self.record, self.intent, self.root)

    def codes(self, result):
        return {e['code'] for e in result['errors']} | {p['code'] for p in result['pending']}

    def test_a_design_citing_what_its_patterns_claim_passes_and_lists_them(self):
        result = self.run_audit()
        self.assertFalse({c for c in self.codes(result) if c.startswith('guideline')}, result)
        self.assertEqual(result['guidelines']['circuit_criteria'],
                         {'G03-001': ['test-pattern#做法甲'], 'G05-001': ['test-pattern#做法甲']})

    def test_a_pattern_type_missing_from_the_scope_is_an_error(self):
        self.record['guideline_scope']['circuit_types'] = []
        self.record['calculations'][0]['guidelines'] = ['G01-001', 'G05-001']
        result = self.run_audit()
        self.assertIn('guideline_scope_circuit', self.codes(result))
        items = [e['item'] for e in result['errors'] if e['code'] == 'guideline_scope_circuit']
        self.assertTrue(any(i.startswith('POWER_CONVERTER：典型电路 test-pattern#做法甲 声明电路类型') for i in items), items)
        self.assertTrue(any(i.startswith('G03-001：典型电路 test-pattern#做法甲 的实现方案落实它') for i in items), items)

    def test_a_claimed_rule_the_scope_leaves_out_is_an_error_while_an_uncited_one_is_pending(self):
        self.record['guideline_scope']['device_kinds'] = []
        self.record['calculations'][0]['guidelines'] = ['G01-001']
        result = self.run_audit()
        codes = self.codes(result)
        self.assertIn('guideline_scope_circuit', codes)        # G05-001 is claimed but the scope has no fuse
        self.assertIn('guideline_uncovered', codes)            # G03-001 is applicable and not cited
        self.assertEqual([e['item'][:7] for e in result['errors'] if e['code'] == 'guideline_scope_circuit'], ['G05-001'])

    def test_without_a_page_plan_nothing_is_claimed(self):
        (self.root / 'record' / 'page-plan.json').unlink()
        result = self.run_audit()
        self.assertFalse({c for c in self.codes(result) if c.startswith('guideline')}, result)
        self.assertEqual(result['guidelines']['circuit_criteria'], {})


if __name__ == '__main__':
    unittest.main()
