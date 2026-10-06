from copy import deepcopy
import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_design_preflight import DOMAINS, verify_preflight, contract_objects
from test_calculation_preflight import calculation, E


def manifest():
    return {'schema_version': 1, 'revision': 'synthetic-2', 'baseline_sha256': 'a'*64,
            'changed_objects': ['T1'], 'calculations': [calculation()],
            'impacts': [{'trigger': 'T1', 'affected_objects': ['T1', 'C1', 'Q1', 'D1'],
                         'checks': {d: {'disposition': 'CALCULATED', 'calculation_ids': ['BIAS'],
                                        'reason': 'Synthetic arithmetic exercises schema only'} for d in DOMAINS}}],
            'facts': {'bias_turns': {'value': '4', 'evidence': E}},
            'artifact_bindings': [{'fact': 'bias_turns', 'path': 'notes.txt', 'format': 'text',
                                   'pattern': r'^T1 bias turns=(\d+)$'}]}


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); (self.root/'notes.txt').write_text('T1 bias turns=4\n')
        self.manifest = manifest()
        self.contract = {'baseline_sha256': 'a'*64, 'component_changes': {'T1': {'value': {'before': '3', 'after': '4'}}}}

    def verify(self, artifacts=True):
        return verify_preflight(self.manifest, self.root, self.contract, artifacts)

    def test_design_fact_and_contract_agree(self):
        result = self.verify()
        self.assertEqual(result['status'], 'PASS', result)
        self.assertTrue(result['artifact_sha256'])

    def test_stale_3t_note_rejected_after_4t_change(self):
        (self.root/'notes.txt').write_text('T1 bias turns=3\n')
        result = self.verify()
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('stale/conflicting' in e for e in result['errors']))

    def test_bom_and_json_bindings_do_not_disappear_on_missing_row(self):
        (self.root/'bom.csv').write_text('Ref,Turns\nT1,4\n')
        (self.root/'constraints.json').write_text('{"T1":{"turns":"4"}}')
        self.manifest['artifact_bindings'] += [
            {'fact': 'bias_turns', 'path': 'bom.csv', 'format': 'csv', 'key_column': 'Ref', 'key': 'T1', 'column': 'Turns'},
            {'fact': 'bias_turns', 'path': 'constraints.json', 'format': 'json', 'pointer': '/T1/turns'}]
        self.assertEqual(self.verify()['status'], 'PASS')
        (self.root/'bom.csv').write_text('Ref,Turns\nT2,4\n')
        self.assertEqual(self.verify()['status'], 'FAIL')

    def test_duplicate_or_missing_note_is_not_success(self):
        for content in ('', 'T1 bias turns=4\nT1 bias turns=4\n'):
            (self.root/'notes.txt').write_text(content)
            self.assertEqual(self.verify()['status'], 'FAIL')

    def test_linked_capacitor_stress_cannot_be_omitted(self):
        del self.manifest['impacts'][0]['checks']['voltage_stress']
        self.assertEqual(self.verify()['status'], 'FAIL')

    def test_conditional_model_permits_only_conditional_candidate(self):
        c = self.manifest['calculations'][0]
        c['inputs']['vz']['basis'] = 'ASSUMED'; c.update(claim='CONDITIONAL', closure='Obtain limit')
        result = self.verify()
        self.assertEqual(result['status'], 'CONDITIONAL')
        self.assertTrue(result['open_impacts'])

    def test_contract_additions_and_rewiring_need_coverage(self):
        self.contract['component_changes']['C1'] = {'value': {'before': '50V', 'after': '100V'}}
        self.assertEqual(self.verify()['status'], 'FAIL')
        self.assertEqual(contract_objects({'replace_partitions': [{'before': [['J1.1', 'R1.2']], 'after': [['J1.1'], ['R1.2']]}]}), {'J1', 'R1'})

    def test_before_generation_checks_impact_without_existing_outputs(self):
        (self.root/'notes.txt').unlink()
        self.assertEqual(self.verify(artifacts=False)['status'], 'PASS')
        self.assertEqual(self.verify()['status'], 'FAIL')

    def test_combined_native_failure_is_not_downgraded_by_conditional_preflight(self):
        from test_design_change import identity, write_xml
        old, new = self.root/'old.xml', self.root/'new.xml'
        write_xml(old, {'R1': identity()}, [['R1.1'], ['R1.2']])
        write_xml(new, {'R1': identity('2k')}, [['R1.1'], ['R1.2']])
        baseline = hashlib.sha256(old.read_bytes()).hexdigest()
        contract = {'schema_version': 1, 'baseline_sha256': baseline}
        manifest = self.manifest; manifest['baseline_sha256'] = baseline
        calc = manifest['calculations'][0]; calc['inputs']['vz']['basis'] = 'ASSUMED'
        calc.update(claim='CONDITIONAL', closure='Get guaranteed bounds')
        for name, value in [('contract.json', contract), ('manifest.json', manifest)]:
            (self.root/name).write_text(json.dumps(value))
        command = [sys.executable, '-B', str(Path(__file__).resolve().parents[1]/'scripts/verify_design_change.py'),
                   str(old), str(new), str(self.root/'contract.json'), '--preflight', str(self.root/'manifest.json'),
                   '--out', str(self.root/'combined.json')]
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(result.returncode, 1)
        report = json.loads((self.root/'combined.json').read_text())
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['preflight']['status'], 'CONDITIONAL')

    def test_cli_fails_stale_artifact_and_never_overwrites_output(self):
        path = self.root/'manifest.json'; path.write_text(json.dumps(self.manifest))
        out = self.root/'out.json'
        command = [sys.executable, '-B', str(Path(__file__).resolve().parents[1]/'scripts/verify_design_preflight.py'), str(path), '--out', str(out)]
        (self.root/'notes.txt').write_text('T1 bias turns=3\n')
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(result.returncode, 1)
        before = out.read_bytes()
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
        self.assertEqual(out.read_bytes(), before)
