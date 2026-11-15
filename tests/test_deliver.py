"""deliver.py runs the delivery steps in order, goes on only on a known good or design-state status, and writes evidence from its own run."""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import deliver  # noqa: E402

# One stub stands in for every skill script; it acts on its own file name.
STUB = r'''
import json, os, sys
from pathlib import Path
name = Path(__file__).stem
args = sys.argv[1:]
out = Path(args[args.index('--out') + 1]) if '--out' in args else None
status = json.loads(os.environ.get('STUB_STATUS', '{}'))
with open(os.environ['STUB_LOG'], 'a') as log:
    log.write(json.dumps([name] + args) + '\n')
if name == 'audit_design_closure':
    out.write_text(json.dumps({'status': status.get(name, 'INCOMPLETE')}))
elif name == 'verify_schematic':
    if status.get(name) == 'none':
        sys.exit(1)
    (out / 'geometry').mkdir(parents=True)
    for f in ('erc.json', 'design-closure.json'):
        (out / f).write_text('{"status": "PASS"}')
    (out / 'summary.json').write_text(json.dumps({'status': status.get(name, 'INCOMPLETE')}))
    (out / 'geometry' / 'board.json').write_text('{}')
    (out / 'netlist.xml').write_text('<x/>')
    (out / 'schematic.pdf').write_text('%PDF')
elif name == 'render_design_report':
    (Path(args[0]) / '设计报告.md').write_text('# 报告')
    if status.get(name):
        print('PROBLEM: 选型角色没有写 external_dependencies')
        sys.exit(1)
elif name == 'knowledge_gaps':
    (Path(args[0]) / 'record' / 'knowledge-gaps.json').write_text('{}')
elif name == 'pack_design':
    sys.exit(int(status.get(name, 0)))
elif name == 'check_delivery_freshness':
    print(json.dumps({'status': status.get(name, 'FRESH')}))
'''
SCRIPTS = ('audit_design_closure', 'verify_schematic', 'knowledge_gaps', 'render_design_report',
           'pack_design', 'check_delivery_freshness')


class DeliverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.stubs = base / 'stubs'
        self.stubs.mkdir()
        for name in SCRIPTS:
            (self.stubs / (name + '.py')).write_text(STUB)
        self.old_here = deliver.HERE
        deliver.HERE = self.stubs
        self.addCleanup(setattr, deliver, 'HERE', self.old_here)
        self.root = base / 'v1'
        for d in ('设计方案', '设计资料', 'record/evidence', 'record/scripts'):
            (self.root / d).mkdir(parents=True)
        (self.root / '设计方案' / 'board.kicad_sch').write_text('old')
        (self.root / '设计方案' / 'BOM.csv').write_text('ref,value')
        (self.root / '设计资料' / '方案.md').write_text('basis')
        (self.root / 'record' / 'evidence' / 'geometry-stale.json').write_text('{}')
        for name in ('electrical-intent.json', 'design-closure.json'):
            (self.root / 'record' / name).write_text('{}')
        # A finished review of the PDF the stub verifier exports ('%PDF').
        (self.root / 'record' / 'visual-review.json').write_text(json.dumps(
            {'status': 'REVIEWED', 'pdf_sha256': hashlib.sha256(b'%PDF').hexdigest()}))
        make = "import sys,pathlib; p=pathlib.Path(sys.argv[1])/'schematic'; p.mkdir(parents=True); (p/'board.kicad_sch').write_text('new')"
        self.config = {'schema_version': 1, 'generate': {'command': [sys.executable, '-c', make, '{out}'], 'schematic': 'schematic'},
                       'root': '设计方案/board.kicad_sch', 'verify': ['--expected-pages', '1'],
                       'inputs': {'requirements': str(base)}}
        self.write_config()

    def write_config(self):
        (self.root / 'record' / 'deliver.json').write_text(json.dumps(self.config, ensure_ascii=False))

    def run_deliver(self, status=None):
        import os
        os.environ['STUB_STATUS'] = json.dumps(status or {})
        self.log = self.stubs / 'calls.jsonl'
        os.environ['STUB_LOG'] = str(self.log)
        self.addCleanup(os.environ.pop, 'STUB_STATUS', None)
        self.addCleanup(os.environ.pop, 'STUB_LOG', None)
        return deliver.deliver(self.root, log=lambda *_: None)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_full_run_in_order_with_fresh_evidence(self):
        code, steps, failure = self.run_deliver()
        self.assertEqual((0, None), (code, failure))
        self.assertEqual(['待办审计', '出图', '自动检查', '知识缺口清单', '生成报告', '交付证据', '证据新鲜度', '打包'],
                         [s['step'] for s in steps])
        self.assertEqual('new', (self.root / '设计方案' / 'board.kicad_sch').read_text())
        self.assertTrue((self.root / '设计方案' / 'BOM.csv').is_file())
        self.assertFalse((self.root / 'record' / 'evidence' / 'geometry-stale.json').exists())
        evidence = json.loads((self.root / 'record' / 'delivery-evidence.json').read_text())
        self.assertEqual('设计方案/board.kicad_sch', evidence['root'])
        self.assertIn('设计方案/board.kicad_sch', evidence['inputs'])
        self.assertIn('设计资料/方案.md', evidence['inputs'])
        self.assertIn('record/deliver.json', evidence['inputs'])
        for out in ('record/design-closure-audit.json', 'record/summary.json', 'record/knowledge-gaps.json', '设计方案/netlist.xml', '设计报告.md',
                    'record/evidence/geometry-board.json', '设计方案/BOM.csv'):
            self.assertIn(out, evidence['outputs'])
            self.assertNotIn(out, evidence['inputs'])
        self.assertEqual(['record/evidence/geometry-board.json'], evidence['roles']['geometry'])
        # The closure audit kept is the run's own audit step, not a second run inside the verifier.
        self.assertEqual('INCOMPLETE', json.loads((self.root / 'record' / 'design-closure-audit.json').read_text())['status'])
        self.assertEqual(['record/visual-review.json'], evidence['roles']['visual_review'])

    def test_the_requirement_baseline_is_written_from_the_record_and_packed_only_when_current(self):
        import requirement_baseline
        (self.root / 'record' / 'requirements.json').write_text(json.dumps({
            'evidence': [{'id': 'E1', 'path': '需求/需求.md', 'sha256': 'ab', 'locator': '§1'}],
            'requirements': [{'id': 'R1', 'text': '输出 3.3 V', 'evidence': ['E1']},
                             {'id': 'CL-A', 'text': '门限 2.97 V', 'evidence': ['E1']}],
            'clarifications': [
                {'id': 'CL-A', 'requirement_ids': ['R1'], 'question': '门限', 'proposed_requirement': '门限 2.97 V',
                 'answer': {'decision': 'ADOPTED_PROPOSAL', 'text': '门限 2.97 V', 'by': '张三', 'date': '2026-11-15'}},
                {'id': 'CL-B', 'requirement_ids': ['R1'], 'question': '纹波带宽', 'proposed_requirement': '20 MHz',
                 'answer': {'decision': 'DEFERRED', 'by': '张三', 'date': '2026-11-15'}}],
            'derating': {'level': 'II', 'source': 'req:R1'}}, ensure_ascii=False))
        code, steps, _ = self.run_deliver()
        self.assertEqual(0, code)
        self.assertIn({'step': '需求基线', 'status': 'DONE'}, steps)
        text = (self.root / '设计资料' / '需求基线.md').read_text()
        self.assertIn('| R1 | 输出 3.3 V | 需求/需求.md（§1） |', text)
        self.assertIn('| CL-A | 门限 2.97 V | 需求澄清（涉及 R1）：采纳建议，张三 2026-11-15 |', text)
        self.assertIn('| CL-B | R1 | 纹波带宽 | 20 MHz |', text)          # deferred: an assumption, not a clause
        self.assertIn('降额等级：II 级', text)
        evidence = json.loads((self.root / 'record' / 'delivery-evidence.json').read_text())
        self.assertIn('设计资料/需求基线.md', evidence['outputs'])
        self.assertIsNone(requirement_baseline.problem(self.root))
        (self.root / '设计资料' / '需求基线.md').write_text(text + '手改\n')
        self.assertIn('不一致', requirement_baseline.problem(self.root))
        (self.root / '设计资料' / '需求基线.md').unlink()
        self.assertIn('缺少', requirement_baseline.problem(self.root))

    def test_a_new_drawing_keeps_the_board_in_the_same_project(self):
        # User 2026-11-13 (AD9361 board): the board shares the KiCad project in 设计方案/. A new drawing replaces the
        # schematic only, keeps the board's sections of .kicad_pro, and the board never becomes a delivery input.
        design = self.root / '设计方案'
        (design / 'board.kicad_pcb').write_text('pcb')
        (design / 'board.kicad_dru').write_text('rules')
        (design / 'scripts').mkdir()
        (design / 'scripts' / 'route.py').write_text('x')
        (design / 'board.kicad_pro').write_text(json.dumps({'meta': {'version': 0}, 'board': {'rules': 1},
                                                             'net_settings': {'classes': []}}))
        make = ("import sys,json,pathlib; p=pathlib.Path(sys.argv[1])/'schematic'; p.mkdir(parents=True); "
                "(p/'board.kicad_sch').write_text('new'); (p/'board.kicad_pro').write_text(json.dumps({'meta': {'version': 1}}))")
        self.config['generate']['command'] = [sys.executable, '-c', make, '{out}']
        self.write_config()
        code, _, failure = self.run_deliver()
        self.assertEqual((0, None), (code, failure))
        project = json.loads((design / 'board.kicad_pro').read_text())
        self.assertEqual({'meta': {'version': 1}, 'board': {'rules': 1}, 'net_settings': {'classes': []}}, project)
        self.assertEqual('pcb', (design / 'board.kicad_pcb').read_text())
        self.assertEqual('rules', (design / 'board.kicad_dru').read_text())
        self.assertTrue((design / 'scripts' / 'route.py').is_file())
        evidence = json.loads((self.root / 'record' / 'delivery-evidence.json').read_text())
        self.assertIn('设计方案/board.kicad_sch', evidence['inputs'])
        self.assertIn('设计方案/board.kicad_pro', evidence['inputs'])   # hashed without its board section
        for board in ('设计方案/board.kicad_pcb', '设计方案/board.kicad_dru', '设计方案/scripts/route.py'):
            self.assertNotIn(board, evidence['inputs'])

    def test_fail_stops_the_run_at_that_step(self):
        code, steps, failure = self.run_deliver({'verify_schematic': 'FAIL'})
        self.assertEqual(1, code)
        self.assertEqual('自动检查', steps[-1]['step'])
        self.assertIn('自动检查', failure)
        self.assertFalse((self.root / '设计报告.md').exists())

    def test_audit_fail_stops_before_drawing(self):
        code, steps, _ = self.run_deliver({'audit_design_closure': 'FAIL'})
        self.assertEqual((1, '待办审计'), (code, steps[-1]['step']))
        self.assertEqual('old', (self.root / '设计方案' / 'board.kicad_sch').read_text())

    def test_record_problems_in_the_report_stop_before_evidence(self):
        code, steps, failure = self.run_deliver({'render_design_report': 1})
        self.assertEqual((1, '生成报告', 'FAIL'), (code, steps[-1]['step'], steps[-1]['status']))
        self.assertFalse((self.root / 'record' / 'delivery-evidence.json').exists())

    def test_pack_rejection_fails_the_run(self):
        code, steps, _ = self.run_deliver({'pack_design': 1})
        self.assertEqual((1, '打包', 'FAIL'), (code, steps[-1]['step'], steps[-1]['status']))

    def test_stale_evidence_stops_before_packing(self):
        code, steps, failure = self.run_deliver({'check_delivery_freshness': 'STALE_OR_INVALID'})
        self.assertEqual((1, '证据新鲜度'), (code, steps[-1]['step']))
        self.assertIn('STALE_OR_INVALID', failure)
        self.assertNotIn('pack_design', [c[0] for c in self.calls()])

    def test_missing_audit_result_stops(self):
        code, steps, failure = self.run_deliver({'audit_design_closure': None})
        self.assertEqual((1, '待办审计', None), (code, steps[-1]['step'], steps[-1]['status']))
        self.assertIn('没有写出结果', failure)

    def test_unknown_status_stops(self):
        code, steps, _ = self.run_deliver({'verify_schematic': 'BROKEN'})
        self.assertEqual((1, '自动检查'), (code, steps[-1]['step']))

    def test_declared_inputs_reach_audit_verify_and_pack(self):
        self.run_deliver()
        expected = ['--input', 'requirements=' + self.config['inputs']['requirements']]
        for call in self.calls():
            if call[0] in ('audit_design_closure', 'verify_schematic', 'pack_design'):
                self.assertTrue(any(call[i:i + 2] == expected for i in range(len(call))), call[0])

    def test_generation_error_and_missing_config_are_reported(self):
        self.config['generate']['command'] = [sys.executable, '-c', 'import sys; sys.exit(3)']
        self.write_config()
        code, _, failure = self.run_deliver()
        self.assertEqual(1, code)
        self.assertIn('出图：命令出错（退出码 3）', failure)
        (self.root / 'record' / 'deliver.json').unlink()
        _, _, failure = self.run_deliver()
        self.assertIn('缺少 record/deliver.json', failure)

    def test_prepare_commands_run_first(self):
        self.config['prepare'] = [[sys.executable, '-c', "open('record/prepared.txt','w').write('1')"]]
        self.write_config()
        code, steps, _ = self.run_deliver()
        self.assertEqual((0, '准备 1'), (code, steps[0]['step']))
        self.assertTrue((self.root / 'record' / 'prepared.txt').is_file())


if __name__ == '__main__':
    unittest.main()
