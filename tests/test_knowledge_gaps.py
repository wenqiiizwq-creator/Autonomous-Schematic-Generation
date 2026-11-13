"""knowledge_gaps.py: the knowledge-gap list is extracted from the module products, one row per signal (SKILL.md 能力目标 7)."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import knowledge_gaps

RECORDS = {
    'block-circuits/PSU.json': {'schemes': [{'name': '隔离电源', 'selected': {'name': '自拟方案'}},
                                            {'name': '入口保护', 'selected': {'name': 'TVS', 'circuit': 'tvs#单级'}}]},
    'scheme-criteria.json': {'blocks': [{'block': '隔离电源', 'candidates': [
        {'name': '自拟方案', 'status': 'selected'}, {'name': '听说的方案', 'status': 'rejected', 'unverified': True}]}]},
    'design-closure.json': {
        'calculations': [{'id': 'C-1', 'parameters': [{'name': 'Rds 典型', 'basis': 'typical'}, {'name': 'R1', 'basis': 'design_choice'}],
                          'checks': [{'name': '结温', 'limit_basis': 'model'}, {'name': '耐压', 'limit_basis': 'guaranteed'}]}],
        'work_items': [{'id': 'W-1', 'stage': 'external', 'status': 'open', 'action': '向原厂要 SOA 曲线'},
                       {'id': 'W-2', 'stage': 'external', 'status': 'closed', 'action': 'x'}]},
    'modules.json': {'returns': [{'from': 'C4.2', 'to': 'C3.3', 'reason': '电流预算不够', 'evidence': 'calc:C-1'}],
                     'knowledge_lookups': [{'task': 'C4.2', 'component': '计算方法', 'query': '电荷泵飞电容取值', 'found': []},
                                           {'task': 'C4.2', 'component': '计算方法', 'query': '降压电感', 'found': ['计算方法/x.md']}]},
    'requirements.json': {'clarifications': [
        {'id': 'Q1', 'proposed_requirement': '输出 2 A', 'answer': {'decision': 'DECIDED', 'text': '输出 3 A'}},
        {'id': 'Q2', 'proposed_requirement': '输出 2 A', 'answer': {'decision': 'ADOPTED_PROPOSAL', 'text': '输出 2 A'}}]},
    'selection.json': {'roles': [{'role': '控制器', 'options': [{'name': 'A', 'recommended': True}, {'name': 'B'}],
                                  'decision': {'option': 'B', 'source': 'user:2026-11-09'}}]},
}


class KnowledgeGapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name, data in RECORDS.items():
            path = self.root / 'record' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def test_each_signal_comes_from_its_record(self):
        data = knowledge_gaps.extract(self.root, ['Y - ABC200.pdf'])
        self.assertEqual({'no_typical_circuit': 1, 'unverified_candidate': 1, 'datasheet_not_in_library': 1, 'weak_basis': 2,
                          'external_item': 1, 'returned_upstream': 1, 'user_overrode': 2, 'knowledge_missing': 1}, data['counts'])
        by = {g['signal']: g for g in data['gaps']}
        self.assertEqual(('C3', 'PSU：隔离电源'), (by['no_typical_circuit']['module'], by['no_typical_circuit']['item']))
        self.assertEqual(('C3', 'C3.3'), (by['returned_upstream']['module'], by['returned_upstream']['task']))
        self.assertEqual({'Q1', '控制器'}, {g['item'] for g in data['gaps'] if g['signal'] == 'user_overrode'})
        # 知识框架里哪个组件查不到什么（modules.json 的 knowledge_lookups 里 found 为空的）
        self.assertEqual(('C4', 'C4.2', '计算方法：电荷泵飞电容取值'), (by['knowledge_missing']['module'],
                         by['knowledge_missing']['task'], by['knowledge_missing']['item']))

    def test_an_empty_design_folder_gives_an_empty_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual({'schema_version': 1, 'counts': {}, 'gaps': []}, knowledge_gaps.extract(tmp))

    def test_the_list_is_stale_once_a_record_changes_and_the_report_prints_it(self):
        self.assertIn('缺失', knowledge_gaps.stale(self.root))
        self.assertEqual(0, knowledge_gaps.main([str(self.root)]))
        self.assertIsNone(knowledge_gaps.stale(self.root))
        (self.root / 'record' / 'modules.json').write_text('{"returns": []}', encoding='utf-8')
        self.assertIn('不一致', knowledge_gaps.stale(self.root))
        text = '\n'.join(knowledge_gaps.render(knowledge_gaps.extract(self.root, ['Y.pdf'])))
        self.assertIn('| 手册不在知识库 | 器件知识库 | 1 |', text)
        self.assertIn('| 典型电路没有适用方案 | 知识框架/典型电路 | 1 |', text)
        self.assertIn('本版没有抽出知识缺口', '\n'.join(knowledge_gaps.render({'gaps': []})))


if __name__ == '__main__':
    unittest.main()
