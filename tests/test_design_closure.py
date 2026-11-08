"""Design claims must not outrun the evidence or their dependencies."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import guideline_criteria
from audit_design_closure import audit, sha256
from current_record import make_current

# Citations here name no real PDF; without a library they are NOT_CHECKED and leave these checks alone
# (test_citations covers the citation check itself). The CLI subprocesses inherit the setting.
_env = None


def setUpModule():
    global _env
    from unittest import mock
    # the installed shared guideline rules would ask every record here for its guideline scope; test_guideline_closure
    # covers that with its own library
    library = guideline_criteria.load(guideline_criteria.BUNDLE_PATH)
    library.update(library_version='0.0.0', specs={}, criteria=[],
                   content_sha256=guideline_criteria.content_sha256([], library.get('engineering_values')))
    empty = Path(tempfile.gettempdir()) / 'asg-empty-guideline-criteria.json'
    empty.write_text(guideline_criteria.dump(library), encoding='utf-8')
    _env = mock.patch.dict('os.environ', {'HARDWARE_WIKI': str(Path(tempfile.gettempdir()) / 'asg-no-library'),
                                          'GUIDELINE_CRITERIA': str(empty), 'GUIDELINE_CRITERIA_TESTING': '1'})
    _env.start()


def tearDownModule():
    _env.stop()


class DesignClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.intent = self.root / 'intent.json'
        self.intent.write_text(json.dumps({'components': [{'ref': 'U1'}]}))
        self.source = self.root / 'design.txt'
        self.source.write_text('Requirement and design evidence for a synthetic regulator.\n')
        self.record = {'schema_version': 1, 'coverage': 'complete',
            'intent_sha256': sha256(self.intent),
            'evidence': [{'id': 'E1', 'path': 'design.txt', 'sha256': sha256(self.source), 'locator': 'line 1'}],
            'requirements': [{'id': 'R1', 'status': 'design_supported', 'refs': ['U1'], 'evidence': ['E1'],
                              'implementation': 'Regulator output path; rated operating envelope in E1', 'depends_on': ['W1']}],
            'work_items': [{'id': 'W1', 'stage': 'design', 'status': 'closed', 'requirements': ['R1'], 'evidence': ['E1']}],
            'calculations': [{'id': 'C1', 'requirements': ['R1'], 'evidence': ['E1'], 'refs': ['U1'],
                              'coverage': 'bounded', 'conclusion': 'supported', 'omitted_terms': [],
                              'checks': [{'name': 'output ripple', 'value': 18, 'operator': '<=', 'limit': 30, 'unit': 'mV'}]}]}

    def run_audit(self):
        make_current(self.record, self.intent, self.root)
        return audit(self.record, self.intent, self.root)

    def codes(self):
        return {e['code'] for e in self.run_audit()['errors']}

    def external(self):
        self.record['work_items'][0].update(stage='external', status='open', owner='vendor', consequence_class='function', occurrence='normal',
            action='Obtain exact firmware feature evidence', fallback='Compare independent hardware implementation',
            missing=[{'source': 'user:2026-10-27', 'given': 'feature list without limits', 'needed': 'firmware feature limits',
                      'kind': 'firmware'}], why_external='the firmware is the vendor\'s', calculations=[],
            no_calculation_reason='feature presence only', consequence='feature missing at bring-up',
            questions=['Is the feature in the shipped firmware?'])

    def test_complete_design_record_passes_but_does_not_claim_native_or_sr(self):
        result = self.run_audit()
        self.assertEqual('PASS', result['status'])
        self.assertIn('not physics', result['scope'])

    def test_open_firmware_dependency_prevents_supported_requirement(self):
        self.external()
        self.assertIn('unsupported_requirement_claim', self.codes())

    def test_honest_conditional_design_is_incomplete_not_false_failure(self):
        self.external()
        self.record['requirements'][0]['status'] = 'conditional'
        self.assertEqual('INCOMPLETE', self.run_audit()['status'])

    def test_affected_requirement_must_link_back_to_dependency(self):
        self.record['requirements'][0]['depends_on'] = []
        self.assertIn('unlinked_dependency', self.codes())

    def test_downstream_handoff_does_not_hide_unfinished_design(self):
        self.record['work_items'][0].update(status='handoff', owner='lab', action='Measure corner temperature')
        self.assertIn('unfinished_design_handoff', self.codes())
        self.record['work_items'][0]['stage'] = 'validation'
        self.assertEqual('PASS', self.run_audit()['status'])
        self.assertEqual(['W1'], self.run_audit()['downstream_handoffs'])

    def test_failed_calculation_blocks_and_cannot_support_requirement(self):
        self.record['calculations'][0]['conclusion'] = 'failed'
        self.record['calculations'][0]['checks'][0]['value'] = 45
        self.assertIn('requirement_status_not_derived', self.codes())
        self.record['requirements'][0]['status'] = 'conditional'
        result = self.run_audit()
        self.assertEqual('INCOMPLETE', result['status'])
        self.assertIn({'code': 'calculation_failed', 'item': 'C1'}, result['pending'])

    def test_stale_intent_and_source_are_rejected(self):
        self.intent.write_text(json.dumps({'components': [{'ref': 'U1'}, {'ref': 'U2'}]}))
        self.source.write_text('Changed without re-review')
        self.assertTrue({'stale_intent', 'stale_evidence'} <= self.codes())

    def test_missing_source_and_unknown_references_are_rejected(self):
        self.source.unlink()
        self.record['requirements'][0]['refs'] = ['U999']
        self.record['requirements'][0]['depends_on'] = ['W999']
        self.assertTrue({'evidence_missing_or_outside_root', 'unknown_refs', 'unknown_depends_on'} <= self.codes())

    def test_source_path_escape_and_duplicate_ids_rejected(self):
        self.record['evidence'][0]['path'] = '../outside'
        self.record['requirements'].append(copy.deepcopy(self.record['requirements'][0]))
        self.assertTrue({'evidence_missing_or_outside_root', 'duplicate_id'} <= self.codes())

    def test_partial_review_cannot_pass_and_no_calculations_needs_reason(self):
        self.record.update(coverage='partial', calculations=[])
        self.record['requirements'][0]['no_check_reason'] = 'review not finished'
        result = self.run_audit()
        self.assertEqual('INCOMPLETE', result['status'])
        self.assertTrue({'partial_review', 'calculation_scope_missing'} <= {x['code'] for x in result['pending']})

    def test_open_work_needs_a_consequence_level(self):
        self.external()
        del self.record['work_items'][0]['occurrence']
        result = self.run_audit()
        self.assertEqual('FAIL', result['status'])
        self.assertIn({'code': 'missing_consequence', 'item': 'W1'}, result['errors'])

    def test_level_follows_from_consequence_and_occurrence(self):
        self.external()
        item = self.record['work_items'][0]
        for consequence, occurrence, level in (('safety', 'fault', 'P0'), ('damage', 'condition', 'P0'),
                                               ('damage', 'fault', 'P1'), ('function', 'normal', 'P1'),
                                               ('function', 'fault', 'P2'), ('margin', 'condition', 'P2'),
                                               ('margin', 'fault', 'P3'), ('optimization', 'normal', 'P3')):
            item.update(consequence_class=consequence, occurrence=occurrence)
            self.assertEqual({'W1': level}, self.run_audit()['severities'], (consequence, occurrence))
        item.update(consequence_class='margin', occurrence='normal', severity='P0')   # a hand-written level that disagrees
        self.assertIn({'code': 'severity_contradicts_rule', 'item': 'W1: P0, rule gives P2'}, self.run_audit()['errors'])
        item['severity'] = 'P2'
        self.assertNotIn('severity_contradicts_rule', {e['code'] for e in self.run_audit()['errors']})

    def clarification(self, decision=None, answer=None):
        """One requirement question put to the user (requirement-clarifications.md), answered when decision is given."""
        q = {'id': 'CL-STBY', 'requirement_ids': ['R1'], 'found_in': '2.2', 'question': '待机功耗上限没给，启动电阻取值没有依据',
             'requirement_text': '需求规格 §3：未提及待机功耗', 'proposed_requirement': '待机功耗 ≤0.1 W（230 Vac 空载）'}
        if decision:
            q['answer'] = {'decision': decision, 'text': answer or q['proposed_requirement'], 'by': '用户', 'date': '2026-10-27',
                           'source': {'source': '对话记录', 'locator': '2026-10-27 需求澄清第 1 问'}}
            if decision != 'DEFERRED':
                q['answer']['requirement_files'] = {'decision': 'KEPT'}
        self.record['clarifications'] = [q]
        return q

    def written_back(self, text):
        self.record['requirements'].append({'id': 'CL-STBY', 'status': 'design_supported', 'text': text, 'refs': ['U1'],
                                            'evidence': ['E1'], 'implementation': '启动电阻按待机功耗上限取值', 'depends_on': [],
                                            'no_check_reason': '测试夹具只核需求澄清'})

    def deferred_item(self, assumption='待机功耗 ≤0.1 W（230 Vac 空载）'):
        self.record['requirements'][0]['status'] = 'conditional'
        self.record['work_items'][0].update(stage='requirement', status='open', owner='用户', consequence_class='margin',
                                            occurrence='normal', action='确定待机功耗上限', clarification='CL-STBY',
                                            assumption=assumption)

    def test_requirement_gap_is_a_deferred_clarification(self):
        # A requirement gap is asked at once, not carried to delivery (user 2026-10-27).
        self.deferred_item(assumption=None)
        del self.record['work_items'][0]['clarification']
        codes = self.codes()
        self.assertIn('missing_assumption', codes)
        self.assertIn('requirement_without_clarification', codes)
        self.clarification('DEFERRED', '先按建议设计，量产前再定')
        self.deferred_item()
        result = self.run_audit()
        self.assertEqual('INCOMPLETE', result['status'], result['errors'])
        self.assertIn({'code': 'open_requirement', 'item': 'W1'}, result['pending'])

    def test_answer_is_the_users_or_the_task_files(self):
        # 整板评测 2026-11-07 A3: the runner wrote its own answer (by eval-run:auto) and the audit let it through.
        q = self.clarification('ADOPTED_PROPOSAL')
        self.written_back(q['proposed_requirement'])
        self.assertEqual('PASS', self.run_audit()['status'], self.run_audit()['errors'])
        q['answer']['by'] = 'eval-run:auto（无用户，按技能推荐）'
        self.assertIn('decision_self_assigned', self.codes())
        q['answer'].update(by='用户', source={'source': '任务说明 brief.md', 'locator': '任务说明预先授权'})
        self.assertIn('decision_self_assigned', self.codes())
        # an answer taken from the task file must be there, word for word
        q['answer'].update(by='产品负责人', source={'source': '任务书', 'locator': 'T7 clarification_answers CL-STBY'})
        self.assertIn('delegate_without_task', self.codes())
        given = {k: q['answer'][k] for k in ('id', 'decision', 'text', 'by', 'date') if k in q['answer']}
        given['id'] = 'CL-STBY'
        (self.root / 'record').mkdir(exist_ok=True)
        task = self.root / 'record' / 'task.json'
        task.write_text(json.dumps({'schema_version': 1, 'id': 'T7', 'clarification_answers': [dict(given, by='用户')]}))
        self.assertIn('delegate_mismatch', self.codes())
        task.write_text(json.dumps({'schema_version': 1, 'id': 'T7', 'clarification_answers': [given]}))
        self.assertEqual('PASS', self.run_audit()['status'], self.run_audit()['errors'])

    def test_answer_delegated_by_the_task_file(self):
        # 改进 7: delegate:<by>:<date> adopts ASG's proposal, as the task file's delegation allows.
        q = self.clarification('ADOPTED_PROPOSAL')
        self.written_back(q['proposed_requirement'])
        q['answer'].update(by='delegate:eval-wholeboard:2026-11-07', source={'source': '任务书', 'locator': 'T7 delegation'})
        self.assertIn('delegate_without_task', self.codes())
        (self.root / 'record').mkdir(exist_ok=True)
        task = {'schema_version': 1, 'id': 'T7', 'delegation': {
            'by': 'eval-wholeboard', 'date': '2026-11-07', 'scope': ['clarification'], 'rule': 'adopt_recommendation',
            'text': '采纳 ASG 的建议条文'}}
        (self.root / 'record' / 'task.json').write_text(json.dumps(task))
        self.assertEqual('PASS', self.run_audit()['status'], self.run_audit()['errors'])
        q['answer']['by'] = 'delegate:someone-else:2026-11-07'
        self.assertIn('delegate_mismatch', self.codes())
        q['answer']['by'] = 'delegate:eval-wholeboard:2026-11-07'
        task['delegation']['scope'] = ['selection']
        (self.root / 'record' / 'task.json').write_text(json.dumps(task))
        self.assertIn('delegate_mismatch', self.codes())
        task['delegation']['scope'] = ['clarification']
        (self.root / 'record' / 'task.json').write_text(json.dumps(task))
        self.clarification('DECIDED', '待机功耗 ≤0.2 W')['answer'].update(
            by='delegate:eval-wholeboard:2026-11-07', source={'source': '任务书', 'locator': 'T7 delegation'})
        self.written_back('待机功耗 ≤0.2 W')
        self.assertIn('delegate_mismatch', self.codes())    # a delegate does not decide its own requirement

    def test_unanswered_clarification_fails(self):
        self.clarification()
        self.assertEqual('FAIL', self.run_audit()['status'])
        self.assertIn({'code': 'clarification_unanswered', 'item': 'CL-STBY'}, self.run_audit()['errors'])

    def test_answer_is_written_back_as_a_requirement(self):
        q = self.clarification('ADOPTED_PROPOSAL')
        self.assertIn('clarification_not_written_back', self.codes())
        self.written_back('待机功耗 ≤0.2 W')
        self.assertIn('clarification_not_written_back', self.codes())
        self.record['requirements'][-1]['text'] = q['proposed_requirement']
        self.assertEqual('PASS', self.run_audit()['status'], self.run_audit()['errors'])

    def test_adopted_answer_is_the_proposal_word_for_word(self):
        self.clarification('ADOPTED_PROPOSAL', '待机功耗 ≤0.2 W')
        self.written_back('待机功耗 ≤0.2 W')
        self.assertIn('adopted_text_differs', self.codes())
        self.clarification('DECIDED', '待机功耗 ≤0.2 W')
        self.assertEqual('PASS', self.run_audit()['status'], self.run_audit()['errors'])

    def test_decided_answer_records_whether_the_requirement_files_were_changed(self):
        # The user is asked whether to write the decided requirement into the original files (user 2026-10-27).
        q = self.clarification('ADOPTED_PROPOSAL')
        self.written_back(q['proposed_requirement'])
        del q['answer']['requirement_files']
        self.assertIn('requirement_files_not_asked', self.codes())
        q['answer']['requirement_files'] = {'decision': 'MAYBE'}
        self.assertIn('requirement_files_not_asked', self.codes())
        q['answer']['requirement_files'] = {'decision': 'UPDATED', 'files': []}
        self.assertIn('requirement_files_without_files', self.codes())
        q['answer']['requirement_files'] = {'decision': 'UPDATED', 'files': ['需求/工程规格.md']}
        self.assertEqual('PASS', self.run_audit()['status'], self.run_audit()['errors'])
        self.clarification('DEFERRED', '先按建议设计')     # nothing is decided yet, so nothing to ask
        self.deferred_item()
        self.assertNotIn('requirement_files_not_asked', self.codes())

    def test_deferred_answer_needs_an_open_item_on_the_proposed_text(self):
        self.clarification('DEFERRED', '先按建议设计，量产前再定')
        codes = self.codes()
        self.assertIn('deferred_without_requirement_item', codes)
        self.assertIn('deferred_requirement_claimed_supported', codes)
        self.deferred_item(assumption='按待机 ≤0.3W 设计')
        self.assertIn('assumption_differs_from_proposal', self.codes())
        self.deferred_item()
        self.assertNotIn('assumption_differs_from_proposal', self.codes())

    def test_clarification_fields_and_answer_are_checked(self):
        q = self.clarification('DECIDED', '待机功耗 ≤0.2 W')
        self.written_back('待机功耗 ≤0.2 W')
        q['requirement_ids'] = ['R9']
        del q['answer']['date']
        codes = self.codes()
        self.assertIn('unknown_requirement_ids', codes)
        self.assertTrue(any(e['item'].startswith('CL-STBY:answer needs') for e in self.run_audit()['errors']))
        q['id'] = 'STBY'
        self.assertTrue(any('CL-<name>' in e['item'] for e in self.run_audit()['errors']))

    def test_requirement_gap_cannot_be_handed_off(self):
        self.record['work_items'][0].update(stage='requirement', status='handoff', owner='用户',
                                            action='确定待机功耗上限', assumption='按待机 ≤0.1W 设计')
        self.assertIn('unfinished_design_handoff', self.codes())

    def test_convergence_keeps_independent_design_executable(self):
        self.record['convergence_version'] = 1
        self.record['work_items'][0].update(status='open', blocked_by=[], owner='engineering', consequence_class='margin', occurrence='normal',
                                            action='Calculate remaining regulator bounds')
        self.record['requirements'][0]['status'] = 'conditional'
        result = self.run_audit()
        self.assertEqual('INCOMPLETE', result['status'])
        self.assertEqual(['W1'], result['convergence']['ready_design_actions'])
        self.assertEqual('CONTINUE_DESIGN', result['convergence']['status'])

    def test_convergence_rejects_malformed_external_fallback(self):
        self.external()
        self.record['convergence_version'] = 1
        self.record['requirements'][0]['status'] = 'conditional'
        self.record['work_items'][0].update(blocked_by=[], fallback_work=[], fallback_evidence=[{}])
        self.assertIn('convergence_unassessed_fallback', self.codes())

    def pcb_handoff(self):
        self.record['work_items'].append(dict(id='PCB1', stage='pcb', status='handoff',
            scope='footprint_library', electrical_preconditions=['W1'],
            requirements=['R1'], evidence=['E1'], owner='PCB engineer',
            action='Create and verify pads against the selected package drawing'))
        self.record['requirements'][0]['depends_on'].append('PCB1')

    def test_footprint_library_handoff_preserves_schematic_closure(self):
        self.pcb_handoff()
        result = self.run_audit()
        self.assertEqual('PASS', result['status'])
        self.assertEqual(['PCB1'], result['pcb_handoffs'])

    def test_pcb_handoff_cannot_hide_open_electrical_selection(self):
        self.pcb_handoff()
        self.record['work_items'][0].update(status='open', owner='designer', action='Confirm pin map and ratings')
        self.assertIn('pcb_electrical_precondition', self.codes())

    def test_startup_cannot_be_reclassified_as_pcb_implementation(self):
        self.pcb_handoff()
        self.record['work_items'][-1]['scope'] = 'supply_startup'
        self.assertIn('pcb_scope', self.codes())

    def test_pcb_prerequisite_must_be_explicit_electrical_work(self):
        self.pcb_handoff()
        self.record['work_items'][-1]['electrical_preconditions'] = ['UNKNOWN']
        self.assertIn('unknown_electrical_preconditions', self.codes())
        self.record['work_items'][-1]['electrical_preconditions'] = []
        self.assertIn('missing_electrical_preconditions', self.codes())

    def test_cli_malformed_record_fails_with_report(self):
        record = self.root / 'record.json'
        record.write_text('{bad json')
        out = self.root / 'result.json'
        p = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'scripts/audit_design_closure.py'),
            str(record), '--intent', str(self.intent), '--artifact-root', str(self.root), '--out', str(out)], capture_output=True)
        self.assertEqual(1, p.returncode)
        self.assertEqual('FAIL', json.loads(out.read_text())['status'])

    def test_cli_resolves_evidence_in_declared_inputs(self):
        library = Path(self.tmp.name + '-library')
        library.mkdir()
        self.addCleanup(lambda: [f.unlink() for f in library.iterdir()] and library.rmdir())
        self.source.rename(library / 'design.txt')
        record, out = self.root / 'record.json', self.root / 'result.json'
        make_current(self.record, self.intent, self.root)
        record.write_text(json.dumps(self.record))
        cli = [sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'scripts/audit_design_closure.py'),
               str(record), '--intent', str(self.intent), '--artifact-root', str(self.root), '--out', str(out)]
        subprocess.run(cli, capture_output=True)
        self.assertEqual('FAIL', json.loads(out.read_text())['status'])
        subprocess.run(cli + ['--input', 'datasheets=%s' % library], capture_output=True)
        self.assertEqual('PASS', json.loads(out.read_text())['status'])


if __name__ == '__main__':
    unittest.main()


class CalculationChecksTests(unittest.TestCase):
    """Conclusions follow from computed margins; thresholds need both sides."""
    setUp = DesignClosureTests.setUp
    run_audit = DesignClosureTests.run_audit
    codes = DesignClosureTests.codes

    def zener_board(self):
        self.intent.write_text(json.dumps({'components': [{'ref': 'U1'}, {'ref': 'D1', 'lib_id': 'Device:D_Zener'}]}))
        self.record['intent_sha256'] = sha256(self.intent)

    def test_calculation_needs_checks(self):
        del self.record['calculations'][0]['checks']
        self.assertIn('missing_checks', self.codes())

    def test_failed_check_cannot_be_called_conditional(self):
        self.record['calculations'][0].update(conclusion='conditional', rests_on='estimate')
        self.record['calculations'][0]['checks'][0]['value'] = 45
        self.assertIn('conclusion_not_derived', self.codes())

    def test_passing_checks_cannot_be_called_failed(self):
        self.record['calculations'][0]['conclusion'] = 'failed'
        self.assertIn('conclusion_not_derived', self.codes())

    def test_malformed_check_is_schema_error(self):
        self.record['calculations'][0]['checks'][0]['operator'] = 'about'
        self.assertIn('schema', self.codes())

    def test_threshold_part_without_calculation_is_rejected(self):
        self.zener_board()
        self.assertIn('threshold_part_uncalculated', self.codes())
        self.record['calculations'][0]['refs'].append('D1')
        self.assertNotIn('threshold_part_uncalculated', self.codes())

    def test_threshold_part_found_by_series_prefix_or_declared_role(self):
        for part in ({'lib_id': 'Device:D', 'value': 'BZX84C5V1'}, {'lib_id': 'Device:D', 'value': 'D', 'mpn': 'SMBJ15A'},
                     {'lib_id': 'Reference_Voltage:XYZ', 'value': 'XYZ', 'fields': {'ComponentRole': 'threshold'}}):
            with self.subTest(part=part):
                self.intent.write_text(json.dumps({'components': [{'ref': 'U1'}, {'ref': 'D1', **part}]}))
                self.record['intent_sha256'] = sha256(self.intent)
                self.assertIn('threshold_part_uncalculated', self.codes())
        self.intent.write_text(json.dumps({'components': [{'ref': 'U1'}, {'ref': 'D1', 'lib_id': 'Device:D', 'value': '1N4148'}]}))
        self.record['intent_sha256'] = sha256(self.intent)
        self.assertNotIn('threshold_part_uncalculated', self.codes())

    def test_threshold_window_needs_both_sides(self):
        self.zener_board()
        calc = self.record['calculations'][0]
        calc.update(kind='threshold', refs=['U1', 'D1'], checks=[
            {'name': 'aux at 21 V output incl. leakage peak vs Vz min + Vfault min', 'side': 'no_false_trip',
             'value': 66.0, 'operator': '<', 'limit': 69.4, 'unit': 'V'}])
        self.assertIn('threshold_window_incomplete', self.codes())
        calc['checks'].append({'name': 'output at max trip vs output capacitor rating', 'side': 'protection',
                               'value': 25.0, 'operator': '<=', 'limit': 35.0, 'unit': 'V'})
        self.assertEqual('PASS', self.run_audit()['status'], self.run_audit())

    def test_threshold_false_trip_margin_failure_must_be_failed(self):
        self.zener_board()
        calc = self.record['calculations'][0]
        calc.update(kind='threshold', refs=['D1'], conclusion='conditional', rests_on='estimate', checks=[
            {'name': 'no false trip', 'side': 'no_false_trip', 'value': 71.0, 'operator': '<', 'limit': 69.4, 'unit': 'V'},
            {'name': 'protects', 'side': 'protection', 'value': 25.0, 'operator': '<=', 'limit': 35.0, 'unit': 'V'}])
        self.assertIn('conclusion_not_derived', self.codes())


class ParameterSourceTests(unittest.TestCase):
    """Every number a calculation uses names where it came from; an unspecified pin mode needs its alternatives ruled out."""
    setUp = DesignClosureTests.setUp
    run_audit = DesignClosureTests.run_audit
    codes = DesignClosureTests.codes
    SHEET = 'datasheet:Datasheet/PD/Richtek - RT7209.pdf#p12'

    def opto_board(self):
        # The R5 case: a PD controller GPIO sinks an optocoupler LED; the datasheet gives no sink current or VOL.
        self.intent.write_text(json.dumps({'components': [{'ref': 'U1'}, {'ref': 'U601'}, {'ref': 'R407'}]}))
        self.record['intent_sha256'] = sha256(self.intent)
        self.record['work_items'].append({'id': 'W-OPTO', 'stage': 'external', 'status': 'open', 'requirements': ['R1'],
                                          'evidence': [], 'consequence_class': 'function', 'occurrence': 'normal', 'owner': '原厂', 'action': '取得 GPIO 灌电流保证',
                                          'fallback': '见 OP-GPIO1', 'why_external': 'GPIO 驱动能力只有原厂知道', 'calculations': ['C1'],
                                          'consequence': '光耦电流不足时信号丢失', 'questions': ['GPIO1 灌 2 mA 时的最大 VOL'],
                                          'missing': [{'source': self.SHEET, 'given': '开路电压', 'needed': '灌电流时的 VOL',
                                                       'kind': 'unspecified', 'alternatives': [
                                                           {'approach': '小信号 MOS 缓冲', 'specified': True, 'feasible': False,
                                                            'reason': '占位'}]}]})
        self.record['requirements'][0].update(status='conditional', depends_on=['W1', 'W-OPTO'])
        self.record['calculations'][0].update(refs=['U601', 'R407'], conclusion='conditional', rests_on='vendor_data', parameters=[
            {'name': 'R407', 'ref': 'R407', 'value': 470, 'unit': 'ohm', 'basis': 'design_choice'},
            {'name': 'CTR 寿命保持', 'value': 0.5, 'unit': '1', 'basis': 'model', 'reason': '设计折减', 'uncertainty': 0.2},
            {'name': 'VOL', 'ref': 'U601', 'value': 0.4, 'unit': 'V', 'basis': 'unspecified',
             'source': self.SHEET, 'locator': 'GPIO1 一节只有开路电压与偏置电流档', 'operating_point': 'OP-GPIO1'}])
        self.record['operating_points'] = [{
            'id': 'OP-GPIO1', 'refs': ['U601'], 'pins': ['GPIO1'], 'mode': '开漏灌电流驱动光耦 LED', 'specified': False,
            'source': self.SHEET, 'locator': 'GPIO1 特性表无灌电流/VOL', 'work_item': 'W-OPTO',
            'alternatives': [{'approach': '小信号 MOS 缓冲', 'specified': True, 'feasible': False, 'reason': '占位'}]}]
        return self.record['calculations'][0], self.record['operating_points'][0]

    def test_an_older_record_fails_and_is_rewritten_in_the_current_format(self):
        # user 2026-11-08: the audit no longer reads older versions one by one.
        self.run_audit()
        self.record['parameter_version'] = 2
        del self.record['matrix_version']
        result = audit(self.record, self.intent, self.root)
        self.assertEqual('FAIL', result['status'])
        self.assertEqual(['parameter_version', 'matrix_version'],
                         [e['item'].split()[0] for e in result['errors'] if e['code'] == 'outdated_record'])
        del self.record['calculations'][0]['parameters']
        self.assertIn('missing_parameters', {e['code'] for e in audit(self.record, self.intent, self.root)['errors']})

    def test_device_parameter_needs_a_datasheet_page(self):
        calc, _ = self.opto_board()
        calc['parameters'][2].update(basis='guaranteed', source='RT7209 datasheet')   # the invented VOL<=0.4 V
        self.assertIn('parameter_without_datasheet_location', self.codes())
        calc['parameters'][2].update(source=self.SHEET, locator='')
        self.assertIn('parameter_without_datasheet_location', self.codes())

    def test_model_and_derived_parameters_say_why(self):
        calc, _ = self.opto_board()
        del calc['parameters'][1]['reason']
        calc['parameters'].append({'name': 'IF', 'value': 1e-3, 'unit': 'A', 'basis': 'derived', 'source': 'calc:C9'})
        self.assertTrue({'model_parameter_without_reason', 'derived_parameter_without_basis'} <= self.codes())

    def test_unspecified_parameter_ties_to_an_unspecified_operating_point(self):
        calc, point = self.opto_board()
        self.assertEqual(['OP-GPIO1'], self.run_audit()['unspecified_operations'])
        self.assertNotIn('unspecified_parameter_without_operating_point', self.codes())
        point['specified'] = True
        self.assertIn('unspecified_parameter_without_operating_point', self.codes())

    def test_feasible_specified_alternative_refuses_the_unspecified_mode(self):
        _, point = self.opto_board()
        self.assertNotIn('unspecified_operation_with_specified_alternative', self.codes())
        self.assertEqual('INCOMPLETE', self.run_audit()['status'])
        point['alternatives'][0]['feasible'] = True
        result = self.run_audit()
        self.assertEqual('FAIL', result['status'])
        self.assertIn('unspecified_operation_with_specified_alternative', {e['code'] for e in result['errors']})

    def test_kept_unspecified_mode_needs_alternatives_and_a_vendor_item(self):
        _, point = self.opto_board()
        point.update(alternatives=[], work_item='W1')
        self.assertTrue({'unspecified_operation_without_alternatives', 'unspecified_operation_without_vendor_item'}
                        <= self.codes())

    def test_operating_point_cites_where_the_datasheet_was_read(self):
        _, point = self.opto_board()
        point['source'] = 'RT7209 p12'
        self.assertIn('operating_point_source', self.codes())


class DerivedConclusionTests(unittest.TestCase):
    """The conclusion follows from the inputs (R1-R6: all 164 calculations were conditional)."""
    setUp = DesignClosureTests.setUp
    run_audit = DesignClosureTests.run_audit
    codes = DesignClosureTests.codes
    SHEET = 'datasheet:Datasheet/X/Vendor - XYZ.pdf#p4'

    def calc(self, *bases, conclusion='supported', rests_on=None, omitted=()):
        params = {'guaranteed': {'name': 'Vref', 'ref': 'U1', 'value': 1.2, 'unit': 'V', 'source': self.SHEET, 'locator': '表 6'},
                  'design_choice': {'name': 'R1', 'ref': 'U1', 'value': 1e4, 'unit': 'ohm'},
                  'requirement': {'name': 'P_out', 'value': 100, 'unit': 'W', 'source': 'req:R1'},
                  'constant': {'name': 'rho_Cu', 'value': 1.72e-8, 'unit': 'ohm*m', 'reason': '铜 20°C 电阻率'},
                  'model': {'name': 'eta', 'value': 0.88, 'unit': '1', 'reason': '满载效率工程包络'},
                  'typical': {'name': 'Vf', 'ref': 'U1', 'value': 0.7, 'unit': 'V', 'source': self.SHEET, 'locator': '典型曲线'}}
        c = self.record['calculations'][0]
        c.update(parameters=[dict(params[b], basis=b) for b in bases], conclusion=conclusion, omitted_terms=list(omitted),
                 coverage='partial' if any(isinstance(o, dict) and o.get('kind') == 'not_calculated' for o in omitted) else 'bounded')
        c.pop('rests_on', None)
        if rests_on:
            c['rests_on'] = rests_on
        return c

    def basis(self):
        return self.run_audit()['calculation_basis']['C1']

    def test_guaranteed_inputs_requirements_and_constants_hold_the_design(self):
        self.calc('guaranteed', 'design_choice', 'requirement', 'constant')
        self.assertEqual('PASS', self.run_audit()['status'])
        self.assertEqual({'conclusion': 'supported', 'rests_on': None, 'reasons': []}, self.basis())

    def test_a_deferred_requirement_leaves_the_calculation_conditional(self):
        DesignClosureTests.clarification(self, 'DEFERRED', '先按建议设计，量产前再定')
        DesignClosureTests.deferred_item(self)
        self.record['work_items'][0]['calculations'] = ['C1']
        self.calc('guaranteed', 'model', conclusion='conditional', rests_on='estimate')
        self.assertIn('conclusion_not_derived', self.codes())
        self.calc('guaranteed', 'model', conclusion='conditional', rests_on='user_deferred')
        self.assertNotIn('conclusion_not_derived', self.codes())
        self.assertEqual(['待办 W1', 'eta'], self.basis()['reasons'])
        self.record['work_items'][0]['calculations'] = ['C9']
        self.assertIn('unknown_calculations', self.codes())

    def test_an_engineering_model_rests_on_the_estimate(self):
        self.calc('guaranteed', 'model')
        self.assertIn('conclusion_not_derived', self.codes())
        self.record['requirements'][0]['status'] = 'conditional'
        self.calc('guaranteed', 'model', conclusion='conditional', rests_on='estimate')
        self.assertNotIn('conclusion_not_derived', self.codes())
        self.assertEqual(['eta'], self.basis()['reasons'])

    def test_a_typical_value_or_an_open_vendor_item_rests_on_the_vendor(self):
        self.record['requirements'][0]['status'] = 'conditional'
        self.calc('guaranteed', 'model', 'typical', conclusion='conditional', rests_on='vendor_data')
        self.assertNotIn('conclusion_not_derived', self.codes())
        self.assertEqual(['Vf', 'eta'], self.basis()['reasons'])
        self.calc('guaranteed', conclusion='conditional', rests_on='vendor_data')
        self.record['work_items'].append({'id': 'W-V', 'stage': 'external', 'status': 'open', 'requirements': ['R1'],
                                          'evidence': [], 'calculations': ['C1'], 'owner': 'v', 'action': 'a',
                                          'consequence_class': 'function', 'occurrence': 'normal'})
        self.record['requirements'][0]['depends_on'] = ['W1', 'W-V']
        self.assertNotIn('conclusion_not_derived', self.codes())
        self.assertEqual(['待办 W-V'], self.basis()['reasons'])

    def test_a_failed_check_fails_whatever_is_written(self):
        c = self.calc('guaranteed')
        c['checks'][0]['value'] = 40
        self.assertIn('conclusion_not_derived', self.codes())
        self.assertEqual('failed', self.basis()['conclusion'])

    def test_a_requirement_holds_only_when_its_calculations_do(self):
        self.calc('model', conclusion='conditional', rests_on='estimate')
        self.assertIn('requirement_status_not_derived', self.codes())

    def test_omitted_terms_are_open_design_work_or_a_handed_off_test(self):
        self.record['requirements'][0]['status'] = 'conditional'
        self.calc('guaranteed', conclusion='conditional', rests_on='estimate',
                  omitted=[{'term': '低线逐周期充电', 'kind': 'not_calculated', 'work_item': 'W1'}])
        self.assertIn('not_calculated_without_design_item', self.codes())   # W1 is closed
        self.record['work_items'][0]['status'] = 'open'
        self.record['work_items'][0].update(owner='ASG', action='补算低线充电', consequence_class='function', occurrence='condition')
        self.assertNotIn('not_calculated_without_design_item', self.codes())
        self.assertEqual(['没算：低线逐周期充电'], self.basis()['reasons'])
        # R6 redraw: a term that waits for vendor data points at the open external item instead.
        self.record['work_items'][0]['stage'] = 'external'
        self.assertNotIn('not_calculated_without_design_item', self.codes())
        self.record['work_items'][0].update(stage='validation', status='handoff')
        self.assertIn('not_calculated_without_design_item', self.codes())
        self.record['work_items'][0].update(stage='design', status='open')
        self.record['calculations'][0]['coverage'] = 'bounded'
        self.assertIn('coverage_not_derived', self.codes())
        self.calc('guaranteed', omitted=[{'term': '十年 ESR 漂移', 'kind': 'verify_by_test', 'work_item': 'W1'}])
        self.record['requirements'][0]['status'] = 'design_supported'
        self.assertIn('verify_by_test_without_validation_handoff', self.codes())
        self.record['work_items'][0].update(stage='validation', status='handoff', evidence=['E1'])
        self.assertNotIn('verify_by_test_without_validation_handoff', self.codes())
        self.assertEqual('supported', self.basis()['conclusion'])
        self.calc('guaranteed', omitted=['寿命'])
        self.assertIn('schema', self.codes())

    def test_requirement_inputs_name_a_requirement(self):
        c = self.calc('requirement')
        c['parameters'][0]['source'] = 'req:R9'
        self.assertIn('requirement_parameter_without_requirement', self.codes())


    def v3(self, **limit):
        # R8 (user 2026-10-27): limits ASG set itself read like ratings; the cost target was never checked.
        self.calc('guaranteed', 'design_choice', 'requirement', 'constant')
        check = self.record['calculations'][0]['checks'][0]
        for key in ('limit_basis', 'limit_source'):
            check.pop(key, None)
        check.update(limit)
        check.setdefault('limit_basis', None)     # written but empty: the fixture helper leaves it for the audit
        return check

    def test_checks_say_where_their_limit_comes_from(self):
        check = self.v3()
        self.assertIn('check_limit_without_basis', self.codes())
        check.update(limit_basis='requirement', limit_source='req:R9')
        self.assertIn('check_limit_without_source', self.codes())
        check['limit_source'] = 'req:R1'
        self.assertEqual('PASS', self.run_audit()['status'], self.run_audit()['errors'])
        for basis, source in (('standard', 'standard:'), ('guaranteed', 'calc:C1'), ('derived', 'req:R1')):
            check.update(limit_basis=basis, limit_source=source)
            self.assertIn('check_limit_without_source', self.codes(), basis)
        check.update(limit_basis='standard', limit_source='standard:GB 4943.1-2022 5.4.2')
        self.assertEqual('PASS', self.run_audit()['status'])

    def test_a_limit_asg_set_itself_leaves_the_result_on_its_estimate(self):
        check = self.v3(limit_basis='model')
        self.assertIn('check_limit_without_source', self.codes())
        check['limit_reason'] = '采购承认按 20 J 筛查，非器件额定'
        self.assertIn('conclusion_not_derived', self.codes())
        self.assertEqual(('conditional', 'estimate'), (self.basis()['conclusion'], self.basis()['rests_on']))
        self.assertIn('门槛 output ripple', self.basis()['reasons'])
        check.update(limit_basis='typical', limit_source=self.SHEET)
        self.assertEqual('vendor_data', self.basis()['rests_on'])

    def test_every_requirement_is_checked_or_says_why_not(self):
        self.v3(limit_basis='requirement', limit_source='req:R1')
        self.record['requirements'].append({'id': 'R-COST', 'status': 'conditional', 'refs': [], 'evidence': ['E1'],
                                            'implementation': '整机物料目标 60 元', 'depends_on': []})
        self.assertIn('requirement_without_check', self.codes())
        self.record['requirements'][-1]['no_check_reason'] = '只定认证范围，不对应电路'
        self.assertNotIn('requirement_without_check', self.codes())

    def test_a_consistency_check_holds_only_when_equal(self):
        self.calc('guaranteed', 'design_choice')
        check = self.record['calculations'][0]['checks'][0]
        check.update(name='每日能量配对', value=217.5, operator='==', limit=217.5, unit='Wh')
        self.assertEqual('PASS', self.run_audit()['status'], self.run_audit()['errors'])
        check['value'] = 216
        self.assertEqual('failed', self.basis()['conclusion'])

    def test_a_datasheet_is_cited_by_its_library_path_not_this_machines(self):
        c = self.calc('guaranteed', 'design_choice')
        c['parameters'][0]['source'] = 'datasheet:/Users/x/资料依据/原厂资料/NCP1343.pdf#p6'
        self.assertIn('citation_not_in_library', self.codes())


class DataGapTests(unittest.TestCase):
    """An open external item says what the datasheet gives, what is missing, what to ask and a fallback of its own."""
    setUp = DesignClosureTests.setUp
    run_audit = DesignClosureTests.run_audit
    codes = DesignClosureTests.codes
    external = DesignClosureTests.external
    SHEET = 'datasheet:Datasheet/PD/Richtek - RT7209.pdf#p18'

    def gap_board(self):
        # The R6 case: USBP is specified only unloaded, so the blocking MOS turn-off path is unknown.
        self.record['requirements'][0].update(status='conditional')
        self.record['calculations'][0].update(conclusion='conditional', rests_on='vendor_data')
        item = self.record['work_items'][0]
        item.update(stage='external', status='open', consequence_class='function', occurrence='normal', owner='Richtek 应用支持',
                    action='按关断时延积分 Q701 的 VDS-ID-t 并核 SOA',
                    missing=[{'source': self.SHEET, 'given': 'VOH_USBP 只在 RL=10MΩ 下规定', 'needed': '带 120nC 栅荷时的开通与关断时间',
                              'kind': 'internal'}],
                    why_external='电荷泵驱动和故障时序在芯片内部与固件里', calculations=['C1'],
                    consequence='Q701 超出 SOA 后 D-S 短路，端口无法断开', questions=['从检测到故障到 USBP 下拉的最大时延'],
                    fallback='栅极加由短路检测触发的快放电')
        return item

    def test_complete_gap_record_has_no_gap_errors(self):
        self.gap_board()
        result = self.run_audit()
        self.assertEqual([], [e for e in result['errors'] if e['code'].startswith('gap_')])

    def test_each_gap_field_is_required(self):
        item = self.gap_board()
        for field in ('missing', 'why_external', 'calculations', 'consequence', 'questions'):
            saved = item.pop(field)
            self.assertIn({'code': 'gap_missing_fields', 'item': 'W1:' + field}, self.run_audit()['errors'])
            item[field] = saved

    def test_gap_without_dependent_calculation_says_why(self):
        item = self.gap_board()
        item['calculations'] = []
        self.assertIn('gap_missing_fields', self.codes())
        item['no_calculation_reason'] = '只确认固件上电默认行为，没有数值计算依赖它'
        self.assertNotIn('gap_missing_fields', self.codes())

    def test_gaps_say_what_kind_of_data_is_missing(self):
        # R8: an ESD test, a quote and an inrush comparison were all filed as datasheet gaps.
        item = self.gap_board()
        gap = item['missing'][0]
        del gap['kind']
        self.assertIn('gap_kind_missing', self.codes())
        gap['kind'] = 'test'
        self.assertIn('gap_not_external', self.codes())
        gap['kind'] = 'firmware'
        self.assertEqual([], [e for e in self.run_audit()['errors'] if e['code'].startswith('gap_')])

    def test_an_unguaranteed_value_rules_out_the_parts_that_guarantee_it(self):
        item = self.gap_board()
        gap = item['missing'][0]
        gap['kind'] = 'typical_only'
        self.assertIn('gap_without_alternatives', self.codes())
        gap['alternatives'] = [{'approach': '换手册保证最大延迟的比较器', 'specified': True, 'feasible': True,
                                'reason': 'TLV1805 给出最大传播延迟'}]
        self.assertIn('gap_alternative_feasible', self.codes())
        gap['alternatives'][0].update(feasible=False, reason='同封装同供电的候选都只给典型延迟')
        self.assertEqual([], [e for e in self.run_audit()['errors'] if e['code'].startswith('gap_')])

    def test_one_reason_for_every_external_item_is_no_reason(self):
        item = self.gap_board()
        item['missing'][0]['kind'] = 'internal'
        other = copy.deepcopy(item)
        other.update(id='W2', fallback='改用带公开驱动能力的独立高边驱动')
        self.record['work_items'].append(other)
        self.record['requirements'][0]['depends_on'].append('W2')
        self.assertIn('gap_reason_repeated', self.codes())
        other['why_external'] = '短路后的重试间隔由固件决定'
        self.assertNotIn('gap_reason_repeated', self.codes())

    def test_gap_cites_where_it_was_found(self):
        item = self.gap_board()
        item['missing'][0]['source'] = 'RT7209 手册 p18'
        self.assertIn('gap_bad_source', self.codes())

    def test_gap_links_to_existing_conditional_calculations(self):
        item = self.gap_board()
        item['calculations'] = ['C9']
        self.assertIn('gap_unlinked_calculation', self.codes())
        item['calculations'] = ['C1']
        self.record['calculations'][0].update(coverage='bounded', conclusion='supported', omitted_terms=[])
        self.assertIn('gap_unlinked_calculation', self.codes())

    def test_owner_is_required_but_its_wording_is_not_judged(self):
        item = self.gap_board()
        item['owner'] = '电路设计与原厂应用支持'
        self.assertNotIn('gap_vague_owner', self.codes())
        item['owner'] = ''
        self.assertIn('missing_owner', self.codes())

    def test_shared_boilerplate_fallback_is_rejected(self):
        item = self.gap_board()
        twin = copy.deepcopy(item)
        twin['id'] = 'W2'
        self.record['work_items'].append(twin)
        self.assertIn({'code': 'gap_generic_fallback', 'item': 'W1、W2'}, self.run_audit()['errors'])
        twin['fallback'] = '换带短路保护的负载开关'
        self.assertNotIn('gap_generic_fallback', self.codes())

