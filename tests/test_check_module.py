"""Capability modules (SKILL.md 架构 and P7, user 2026-11-09 “确认写入”): each module's gate checks only what it owns,
and record/modules.json says when an upstream change leaves a module stale."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import block_circuits
import blocks
import check_module
from architecture import check_architecture
from audit_design_closure import audit, sha256
from current_record import make_current, split, write_record
import test_design_closure


def setUpModule():
    test_design_closure.setUpModule()


def tearDownModule():
    test_design_closure.tearDownModule()


ARCH = {
    'schema_version': 1,
    'domains': [{'name': '一次侧'}, {'name': '二次侧'}],
    'blocks': [
        {'id': 'PSU', 'name': '隔离电源', 'domain': '二次侧', 'inputs': ['VIN'], 'outputs': ['+3V3'], 'ref_range': [1, 99],
         'spec': {'text': '24 V 输入，3.3 V 1 A，隔离 1500 Vrms', 'requirements': ['R1']}},
        {'id': 'IN', 'name': '电源入口', 'domain': '一次侧', 'inputs': ['24 V'], 'outputs': ['VIN'], 'ref_range': [100, 199],
         'spec': {'text': '24 V 工业直流，反接与浪涌防护'}},
    ],
    'flows': [{'name': 'VIN', 'kind': 'power', 'from': 'IN', 'to': 'PSU', 'nets': ['VIN'],
               'params': {'voltage': '18～36 V', 'current_max': '0.3 A'}}],
    'boundaries': [{'name': '电源隔离', 'sides': ['一次侧', '二次侧']}],
    'interfaces': [{'name': '电源端子', 'block': 'IN'}],
}


class ArchitectureTests(unittest.TestCase):
    def test_a_complete_architecture_passes(self):
        self.assertEqual([], check_architecture(ARCH, {'R1'}))

    def test_each_done_mark_of_task_1_2_is_checked(self):
        cases = [
            (lambda a: a['blocks'][0].pop('spec'), '块规格'),
            (lambda a: a['blocks'][0].update(outputs=[]), 'outputs'),
            (lambda a: a['blocks'][0].update(domain='三次侧'), 'domain'),
            (lambda a: a['flows'][0].update(name=''), 'name'),
            (lambda a: a['flows'][0].update(to='IN'), 'from、to'),
            (lambda a: a['flows'][0].pop('nets'), 'nets'),
            (lambda a: a['flows'][0].update(params={}), 'params'),
            (lambda a: a['blocks'][0].pop('ref_range'), 'ref_range'),
            (lambda a: a['blocks'][1].update(ref_range=[50, 120]), '编号段重叠'),
            (lambda a: a['blocks'][1].update(domain='二次侧'), '一侧还没有功能块'),
            (lambda a: a['blocks'][0]['spec'].update(requirements=['R9']), '需求编号'),
        ]
        for change, words in cases:
            arch = copy.deepcopy(ARCH)
            change(arch)
            problems = check_architecture(arch, {'R1'})
            self.assertTrue(any(words in p for p in problems), (words, problems))


class ModuleAuditTests(unittest.TestCase):
    """audit_design_closure --module: C1 needs no design netlist; C4 leaves the whole-board sections to C5."""

    def setUp(self):
        case = test_design_closure.DesignClosureTests('run_audit')
        case.setUp()
        self.addCleanup(case.tmp.cleanup)
        self.record, self.intent, self.root = case.record, case.intent, case.root
        make_current(self.record, self.intent, self.root)

    def requirements(self):
        _, requirements = split(self.record)
        requirements['requirements'][0]['text'] = 'R1 输出 3.3 V'
        return requirements

    def test_c1_runs_without_a_netlist_and_checks_only_requirements_json(self):
        result = audit(self.requirements(), None, self.root, module='C1')
        self.assertEqual('C1', result['module'])
        self.assertNotEqual('FAIL', result['status'], result['errors'])
        cases = [(lambda r: r.update(derating={}), 'derating_level_missing'),
                 (lambda r: r['requirements'][0].pop('text'), 'missing_text'),
                 (lambda r: r['requirements'][0].update(evidence=[]), 'missing_evidence'),
                 (lambda r: r['requirements'][0].update(evidence=['E9']), 'unknown_evidence'),
                 (lambda r: r['requirements'][0].update(status='design_supported'), 'trace_in_requirements')]
        for change, code in cases:
            broken = self.requirements()
            change(broken)
            self.assertIn(code, {e['code'] for e in audit(broken, None, self.root, module='C1')['errors']}, code)

    def test_the_whole_audit_merges_the_two_files(self):
        closure, requirements = split(self.record)
        self.assertEqual([], audit(closure, self.intent, self.root, requirements=requirements)['errors'])
        old = copy.deepcopy(closure)
        old['requirements'] = requirements['requirements']
        self.assertIn('outdated_record', {e['code'] for e in audit(old, self.intent, self.root, requirements=requirements)['errors']})
        untraced = copy.deepcopy(closure)
        untraced['traceability'] = []
        codes = {e['code'] for e in audit(untraced, self.intent, self.root, requirements=requirements)['errors']}
        self.assertIn('requirement_untraced', codes)
        self.assertNotIn('requirement_untraced', {e['code'] for e in audit(
            copy.deepcopy(untraced), self.intent, self.root, module='C4', requirements=requirements)['errors']})
        stray = copy.deepcopy(closure)
        stray['traceability'].append({'requirement': 'R9', 'status': 'open'})
        stray['traceability'][0]['text'] = '条文写在这里'
        codes = {e['code'] for e in audit(stray, self.intent, self.root, requirements=requirements)['errors']}
        self.assertTrue({'unknown_requirement', 'trace_field'} <= codes, codes)
        self.assertIn('requirements_file', {e['code'] for e in audit(copy.deepcopy(closure), self.intent, self.root,
                                                                    requirements={})['errors']})

    def test_other_modules_need_the_netlist(self):
        with self.assertRaises(ValueError):
            audit(copy.deepcopy(self.record), None, self.root, module='C4')

    def test_c4_does_not_audit_the_whole_board_sections(self):
        result = audit(copy.deepcopy(self.record), self.intent, self.root, module='C4')
        self.assertEqual('NOT_CHECKED', result['matrices'])
        self.assertEqual('NOT_CHECKED', result['binding']['net_voltages'])
        self.assertNotEqual('NOT_CHECKED', result['binding']['pin_dispositions'])     # task C4.4 writes them
        whole = audit(copy.deepcopy(self.record), self.intent, self.root)
        self.assertEqual('C5', whole['module'])
        self.assertNotEqual('NOT_CHECKED', whole['matrices'])


class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.record = self.root / 'record'
        self.record.mkdir()
        self.write('design-closure.json', {'traceability': [{'requirement': 'R1'}], 'calculations': []})
        self.write('requirements.json', {'schema_version': 1, 'requirements': [{'id': 'R1'}]})
        self.write('architecture.json', ARCH)

    def write(self, name, data):
        (self.record / name).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def test_a_section_fingerprint_ignores_the_other_sections(self):
        before = check_module.fingerprint(self.record, 'design-closure.json#traceability')
        self.write('design-closure.json', {'traceability': [{'requirement': 'R1'}], 'calculations': [{'id': 'C1'}]})
        self.assertEqual(before, check_module.fingerprint(self.record, 'design-closure.json#traceability'))
        self.assertEqual('absent', check_module.fingerprint(self.record, 'page-plan.json'))

    def test_a_folder_fingerprint_covers_every_block_file(self):
        self.assertEqual('absent', check_module.fingerprint(self.record, 'block-circuits/'))
        (self.record / 'block-circuits').mkdir()
        self.write('block-circuits/PSU.json', {'block': 'PSU'})
        before = check_module.fingerprint(self.record, 'block-circuits/')
        self.write('block-circuits/IN.json', {'block': 'IN'})
        self.assertNotEqual(before, check_module.fingerprint(self.record, 'block-circuits/'))

    def test_an_upstream_change_leaves_the_module_stale_and_an_own_change_modified(self):
        check_module.record_module(self.root, 'C1', [])
        check_module.record_module(self.root, 'C2', [])
        self.assertEqual({'C1': 'OK', 'C2': 'OK'}, check_module.status(self.root))
        self.write('requirements.json', {'schema_version': 1, 'requirements': [{'id': 'R1'}, {'id': 'R2'}]})
        self.assertEqual({'C1': 'MODIFIED', 'C2': 'STALE'}, check_module.status(self.root))
        check_module.record_module(self.root, 'C1', [])
        arch = copy.deepcopy(ARCH)
        arch['blocks'][0]['name'] = '隔离电源 3.3 V'
        self.write('architecture.json', arch)
        self.assertEqual({'C1': 'OK', 'C2': 'MODIFIED'}, check_module.status(self.root))

    def test_given_inputs_are_fingerprinted(self):
        given = self.root / '需求.md'
        given.write_text('R1 输出 3.3 V', encoding='utf-8')
        check_module.record_module(self.root, 'C1', [str(given)])
        self.assertEqual('OK', check_module.status(self.root)['C1'])
        given.write_text('R1 输出 5 V', encoding='utf-8')
        self.assertEqual('STALE', check_module.status(self.root)['C1'])

    def test_c2_gate_reads_architecture_json(self):
        self.assertEqual(([], []), check_module.gate('C2', self.root))
        self.write('requirements.json', {'schema_version': 1, 'requirements': [{'id': 'R2'}]})
        problems, _ = check_module.gate('C2', self.root)
        self.assertTrue(any('需求编号' in p for p in problems), problems)
        self.write('requirements.json', {'schema_version': 1, 'requirements': [{'id': 'R1'}]})
        (self.record / 'architecture.json').unlink()
        problems, _ = check_module.gate('C2', self.root)
        self.assertTrue(any('architecture.json' in p for p in problems))


class ModuleRunTests(unittest.TestCase):
    """task.json `modules` (workflow-handoff.md): the given inputs stay as given; the run delivers a module report."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / 'given'
        self.source.mkdir()
        (self.source / 'requirements.json').write_text(json.dumps({'schema_version': 1, 'requirements': [{'id': 'R1'}]}),
                                                       encoding='utf-8')
        self.root = self.base / 'run'
        self.record = self.root / 'record'
        self.record.mkdir(parents=True)
        (self.record / 'requirements.json').write_bytes((self.source / 'requirements.json').read_bytes())
        (self.record / 'architecture.json').write_text(json.dumps(ARCH, ensure_ascii=False), encoding='utf-8')
        given = {'requirements.json': {'path': str(self.source / 'requirements.json'),
                                       'sha256': sha256(self.source / 'requirements.json')}}
        self.task = {'id': 'T-C2', 'modules': {'from': 'C2', 'to': 'C2', 'given': given}}
        (self.record / 'task.json').write_text(json.dumps(self.task), encoding='utf-8')

    def test_scope_is_validated(self):
        self.assertIsNone(check_module.scope_of({}))
        self.assertEqual(('C2',), check_module.scope_of(self.task)[0])
        for bad in ({'from': 'C4', 'to': 'C2'}, {'from': 'C9', 'to': 'C9'},
                    {'from': 'C2', 'to': 'C2', 'given': {'architecture.json': {'path': 'x', 'sha256': 'y'}}}):
            with self.assertRaises(ValueError):
                check_module.scope_of({'modules': bad})
        block = {'from': 'C4', 'to': 'C4', 'given': {'block-circuits/PSU.json': {'path': 'x', 'sha256': 'y'}}}
        self.assertEqual(('C4',), check_module.scope_of({'modules': block})[0])

    def test_a_given_input_is_read_only(self):
        self.assertEqual(([], []), check_module.gate('C2', self.root))
        requirements = json.loads((self.record / 'requirements.json').read_text(encoding='utf-8'))
        requirements['requirements'].append({'id': 'R2'})
        (self.record / 'requirements.json').write_text(json.dumps(requirements), encoding='utf-8')
        problems, _ = check_module.gate('C2', self.root)
        self.assertTrue(any('被改动' in p for p in problems), problems)

    def test_a_module_outside_the_run_is_refused(self):
        problems, _ = check_module.gate('C3', self.root)
        self.assertTrue(any('不在任务书' in p for p in problems), problems)

    def test_the_module_delivery_has_a_report_and_fresh_records(self):
        errors = check_module.check_delivery(self.root)
        self.assertTrue(any('模块报告.md' in e for e in errors) and any('未记录' in e for e in errors), errors)
        check_module.record_module(self.root, 'C2', [])
        report_text, problems = check_module.module_report(self.root)
        self.assertEqual([], problems)
        self.assertIn('功能块 2 个', report_text)
        (self.root / check_module.MODULE_REPORT).write_text(report_text, encoding='utf-8')
        self.assertEqual([], check_module.check_delivery(self.root))
        (self.root / '原理图').mkdir()
        self.assertTrue(any('原理图' in e for e in check_module.check_delivery(self.root)))

    def test_pack_design_hands_a_module_run_to_the_module_check(self):
        import pack_design
        self.assertEqual(check_module.check_delivery(self.root), pack_design.check(self.root))


SCHEME = {'version': 1, 'blocks': [
    {'block': '隔离反激电源', 'block_id': 'PSU', 'circuit_types': ['POWER_CONVERTER'], 'device_kinds': [], 'ports': False,
     'decisive': [{'condition': '输入电压', 'value': '18～36 V'}],
     'candidates': [{'name': '反激', 'source': ['test:格式示例'], 'status': 'selected', 'reason': '功率小'},
                    {'name': '正激', 'source': ['test:格式示例'], 'status': 'rejected', 'reason': '器件多'}],
     'criteria': [{'id': 'G03-001', 'excludes': '正激', 'basis': 'inference', 'how': '反激', 'defer': ['占空比']}]}]}
SELECTION = {'schema_version': 1, 'library_root': '~/lib', 'roles': [
    {'role': '反激控制器', 'block_id': 'PSU', 'refs': ['U1'], 'decisive': [{'param': 'VIN', 'op': 'covers', 'limit': [18, 36]}],
     'candidates': [{'mpn': 'CTRL-A', 'status': 'selected', 'datasheet': 'a.pdf', 'values': {'VIN': {'value': [9, 40], 'page': 1}},
                     'external_dependencies': []},
                    {'mpn': 'CTRL-B', 'status': 'rejected', 'datasheet': 'b.pdf'}]}]}


class BlockCircuitTests(unittest.TestCase):
    """Module C3's product: one block file per architecture block, extracted from the two working records."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.record = self.root / 'record'
        self.record.mkdir()
        for name, data in (('architecture.json', ARCH), ('scheme-criteria.json', SCHEME), ('selection.json', SELECTION)):
            (self.record / name).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def test_each_block_gets_its_scheme_core_parts_and_deferred_values(self):
        self.assertEqual([], block_circuits.run(self.root))
        psu = json.loads((self.record / 'block-circuits' / 'PSU.json').read_text(encoding='utf-8'))
        self.assertEqual('反激', psu['schemes'][0]['selected']['name'])
        self.assertEqual([{'rule': 'G03-001', 'values': ['占空比']}], psu['schemes'][0]['deferred'])
        self.assertEqual([{'condition': '输入电压', 'value': '18～36 V'}], psu['schemes'][0]['decisive'])
        self.assertEqual(('反激控制器', 'CTRL-A', ['U1']), (psu['core_parts'][0]['role'], psu['core_parts'][0]['mpn'],
                                                       psu['core_parts'][0]['refs']))
        self.assertNotIn('candidates', psu['core_parts'][0])
        empty = json.loads((self.record / 'block-circuits' / 'IN.json').read_text(encoding='utf-8'))
        self.assertEqual(([], []), (empty['schemes'], empty['core_parts']))

    def test_a_record_without_block_id_is_not_extracted(self):
        selection = copy.deepcopy(SELECTION)
        selection['roles'][0]['block_id'] = 'PFC'
        (self.record / 'selection.json').write_text(json.dumps(selection, ensure_ascii=False), encoding='utf-8')
        problems = block_circuits.run(self.root)
        self.assertTrue(any('block_id' in p for p in problems), problems)
        self.assertFalse((self.record / 'block-circuits').exists())

    def test_a_hand_edited_block_file_disagrees_with_the_records(self):
        block_circuits.run(self.root)
        path = self.record / 'block-circuits' / 'PSU.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        data['core_parts'][0]['mpn'] = 'CTRL-B'
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        problems = block_circuits.run(self.root, write=False)
        self.assertTrue(any('重跑 block_circuits.py' in p for p in problems), problems)
        self.assertTrue(any('选定器件' in p for p in problems), problems)
        self.assertEqual([], block_circuits.run(self.root))

    def test_c4_gate_reads_the_deferred_values_from_the_block_files(self):
        case = test_design_closure.DesignClosureTests('run_audit')
        case.setUp()
        self.addCleanup(case.tmp.cleanup)
        intent = self.record / 'electrical-intent.json'
        intent.write_bytes(case.intent.read_bytes())
        (self.root / 'design.txt').write_bytes(case.source.read_bytes())
        make_current(case.record, intent, self.root)
        psu, _, _ = blocks.split(json.loads(intent.read_text(encoding='utf-8')), {'PSU': ['U1']})
        (self.record / 'blocks').mkdir()
        (self.record / 'blocks' / 'PSU.json').write_text(json.dumps(psu['PSU'], ensure_ascii=False), encoding='utf-8')
        intent.unlink()                       # module C4 reads the block designs, not a whole-board netlist
        write_record(case.record, self.record / 'design-closure.json')
        block_circuits.run(self.root)
        (self.record / 'scheme-criteria.json').unlink()
        (self.record / 'selection.json').unlink()
        problems, _ = check_module.gate('C4', self.root)
        self.assertTrue(any('block-circuits/PSU.json' in p and '占空比' in p and '没有闭合' in p for p in problems), problems)
        self.assertFalse(any('scheme-criteria' in p or 'selection' in p for p in problems), problems)

    def test_c5_gate_needs_the_netlist_to_be_the_merge_of_the_block_designs(self):
        case = test_design_closure.DesignClosureTests('run_audit')
        case.setUp()
        self.addCleanup(case.tmp.cleanup)
        intent = self.record / 'electrical-intent.json'
        intent.write_bytes(case.intent.read_bytes())
        make_current(case.record, intent, self.root)
        write_record(case.record, self.record / 'design-closure.json')
        psu, _, _ = blocks.split(json.loads(intent.read_text(encoding='utf-8')), {'PSU': ['U1']})
        (self.record / 'blocks').mkdir()
        (self.record / 'blocks' / 'PSU.json').write_text(json.dumps(psu['PSU'], ensure_ascii=False), encoding='utf-8')
        problems, _ = check_module.gate('C5', self.root)
        self.assertTrue(any('合并结果不一致' in p for p in problems), problems)
        self.assertEqual(0, blocks.main(['merge', str(self.root)]))
        problems, _ = check_module.gate('C5', self.root)
        self.assertFalse(any('合并结果不一致' in p for p in problems), problems)
        with self.assertRaises(SystemExit):
            check_module.main(['C5', str(self.root), '--block', 'PSU'])          # --block is for C4 only


class OneBlockTests(unittest.TestCase):
    """check_module.py C4 --block: one block's calculations, pin dispositions, work-item links and performance records."""

    def test_the_closure_keeps_only_this_blocks_rows(self):
        closure = {'calculations': [{'id': 'A', 'refs': ['U101']}, {'id': 'B', 'refs': ['U101', 'U201']}],
                   'pin_dispositions': [{'pin': 'U101.3'}, {'pin': 'U201.3'}],
                   'work_items': [{'id': 'W1', 'calculations': ['A', 'B']}, {'id': 'W2', 'calculations': ['B']},
                                  {'id': 'W3'}], 'traceability': [{'requirement': 'R1'}]}
        view = check_module.closure_for(closure, {'U101'})
        self.assertEqual(['A'], [c['id'] for c in view['calculations']])
        self.assertEqual([{'pin': 'U101.3'}], view['pin_dispositions'])
        self.assertEqual([('W1', ['A']), ('W3', None)], [(w['id'], w.get('calculations')) for w in view['work_items']])
        self.assertEqual(closure['traceability'], view['traceability'])

    def test_the_performance_record_keeps_only_this_blocks_parts(self):
        record = {'components': [{'ref': 'R101'}, {'ref': 'R201'}],
                  'screening': [{'refs': ['R101', 'C101', 'R201'], 'decision': 'standard'}, {'refs': ['C201']}]}
        view = check_module.requirements_for(record, {'R101', 'C101'})
        self.assertEqual([{'ref': 'R101'}], view['components'])
        self.assertEqual([['R101', 'C101']], [row['refs'] for row in view['screening']])


class InputItemTests(unittest.TestCase):
    """stage `input`: only a module run reports a wrong given input; the whole flow goes back upstream."""

    def setUp(self):
        case = test_design_closure.DesignClosureTests('run_audit')
        case.setUp()
        self.addCleanup(case.tmp.cleanup)
        self.record, self.intent, self.root = case.record, case.intent, case.root
        self.record['work_items'].append({
            'id': 'W-IN', 'stage': 'input', 'status': 'open', 'requirements': ['R1'], 'evidence': [], 'owner': '任务书提供方',
            'action': '给定方案在 9 V 输入时占空比超限，建议改用升降压', 'consequence_class': 'function', 'occurrence': 'condition',
            'upstream': 'C3', 'given': 'scheme-criteria.json'})
        self.record['requirements'][0]['depends_on'].append('W-IN')
        make_current(self.record, self.intent, self.root)

    def codes(self):
        return {e['code'] for e in audit(copy.deepcopy(self.record), self.intent, self.root, module='C4')['errors']}

    def test_input_items_belong_to_module_runs(self):
        self.assertIn('input_item_in_whole_flow', self.codes())
        (self.root / 'record').mkdir(exist_ok=True)
        (self.root / 'record' / 'task.json').write_text(json.dumps({'modules': {'from': 'C4', 'to': 'C4'}}))
        self.assertNotIn('input_item_in_whole_flow', self.codes())
        self.record['work_items'][-1]['upstream'] = 'C6'
        self.assertIn('input_item_schema', self.codes())


if __name__ == '__main__':
    unittest.main()
