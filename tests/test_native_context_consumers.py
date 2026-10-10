"""Native field semantics and explicit, independently bound consumer contexts."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from schematic_layout.design_change import read_native, verify_change
from schematic_layout.reference_contract import verify_reference
import test_pinless_evidence as fixtures


class NativeContextConsumerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.PinlessEvidenceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.base = self.fixture.base

    def test_actual_native_field_exports_preserve_exact_source_and_inventory(self):
        root = ROOT / 'tests/fixtures/pinless_native_fields'
        for case in sorted(p for p in root.iterdir() if p.is_dir()):
            with self.subTest(case=case.name):
                roles = json.loads((case / 'roles.json').read_text())
                native = read_native(case / 'native.xml', source_root=case / 'specimen.kicad_sch', source_roles=roles)
                self.assertEqual(native['components']['Z7'], roles['objects'][0]['native_identity'])
                self.assertEqual(set(native['pinless_objects']), {'Z7'})
                self.assertFalse(native['pin_nets'])
        literal = root / 'value-tilde'
        roles = json.loads((literal / 'roles.json').read_text())
        self.assertEqual(roles['objects'][0]['native_identity']['value'], '~')
        roles['objects'][0]['native_identity']['value'] = ''
        with self.assertRaisesRegex(ValueError, 'contradicts source'):
            read_native(literal / 'native.xml', source_root=literal / 'specimen.kicad_sch', source_roles=roles)

    def test_missing_custom_field_nonempty_changes_and_stale_source_remain_errors(self):
        case = ROOT / 'tests/fixtures/pinless_native_fields/custom-present'
        original = json.loads((case / 'roles.json').read_text())
        for field, value in [('Missing', ''), ('Custom', ''), ('Custom', 'Exact custom '), ('MPN', '~')]:
            with self.subTest(field=field, value=value):
                roles = copy.deepcopy(original)
                roles['objects'][0]['native_identity']['fields'][field] = value
                with self.assertRaisesRegex(ValueError, 'contradicts source'):
                    read_native(case / 'native.xml', source_root=case / 'specimen.kicad_sch', source_roles=roles)
        roles = copy.deepcopy(original)
        roles['objects'][0]['source_properties']['MPN'] = 'Other'
        with self.assertRaisesRegex(ValueError, 'properties mismatch'):
            read_native(case / 'native.xml', source_root=case / 'specimen.kicad_sch', source_roles=roles)

    def test_change_requires_each_side_own_evidence_and_retains_inventory(self):
        f = self.fixture
        options = dict(before_source_root=f.root, before_source_roles=f.contract,
                       after_source_root=f.root, after_source_roles=f.contract)
        contract = {'schema_version': 1, 'baseline_sha256': hashlib.sha256(f.xml.read_bytes()).hexdigest()}
        self.assertEqual(verify_change(f.xml, f.xml, contract, **options)['status'], 'PASS')
        with self.assertRaisesRegex(ValueError, 'no exported physical pins'):
            verify_change(f.xml, f.xml, contract, before_source_root=f.root, before_source_roles=f.contract)
        for key in ('before_source_roles', 'after_source_roles'):
            bad = copy.deepcopy(options)
            bad[key]['native_xml_sha256'] = '0' * 64
            with self.assertRaises(ValueError):
                verify_change(f.xml, f.xml, contract, **bad)
        changed = self.base / 'changed.xml'
        changed.write_text(f.xml.read_text().replace('Reviewed marker', 'Other marker'))
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            verify_change(f.xml, changed, contract, **options)

    def reference_inputs(self):
        f = self.fixture
        directory = ROOT / 'tests/fixtures/reference_contract'
        for path in directory.iterdir():
            shutil.copy2(path, self.base / path.name)
        core = self.base / 'netlist.xml'
        tree = ET.parse(core)
        tree.getroot().find('components').append(ET.parse(f.xml).getroot().find('components/comp'))
        tree.write(core)
        roles = copy.deepcopy(f.contract)
        roles['native_xml_sha256'] = hashlib.sha256(core.read_bytes()).hexdigest()
        return core, json.loads((self.base / 'contract.json').read_text()), roles

    def test_reference_core_pin_name_mutation_reports_new_object_error(self):
        core, contract, roles = self.reference_inputs()
        options = dict(source_root=self.fixture.root, source_roles=roles)
        baseline = verify_reference(core, contract, self.base, **options)
        self.assertEqual(baseline['status'], 'PASS', baseline)
        tree = ET.parse(core)
        pin = tree.getroot().find('libparts/libpart/pins/pin')
        self.assertIsNotNone(pin)
        number = pin.get('num')
        pin.set('name', '~')
        tree.write(core)
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            verify_reference(core, contract, self.base, **options)
        # Explicit test review/rebinding of this XML only, never done by checker.
        roles['native_xml_sha256'] = hashlib.sha256(core.read_bytes()).hexdigest()
        mutated = verify_reference(core, contract, self.base, **options)
        self.assertEqual(mutated['status'], 'FAIL')
        failures = mutated['pin_maps']['U1']['failures']
        self.assertTrue(any(isinstance(x, dict) and x.get('pin') == number for x in failures), failures)

    def test_reference_cli_forwards_roles_protects_inputs_and_rejects_partial_context(self):
        core, contract, roles = self.reference_inputs()
        path = self.base / 'roles.json'
        path.write_text(json.dumps(roles))
        report = self.base / 'reference.json'
        base = [sys.executable, '-B', str(ROOT / 'scripts/verify_reference_contract.py'), str(core),
                str(self.base / 'contract.json'), '--source-root', str(self.fixture.root),
                '--source-role-contract', str(path)]
        result = subprocess.run([*base, '--out', str(report)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(report.read_text())['source_role_contract']['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        before = path.read_bytes()
        self.assertNotEqual(subprocess.run([*base, '--out', str(path)], capture_output=True).returncode, 0)
        self.assertEqual(path.read_bytes(), before)
        partial = base[:-2]
        self.assertNotEqual(subprocess.run([*partial, '--out', str(self.base / 'partial.json')], capture_output=True).returncode, 0)

    def test_change_cli_separate_bindings_and_partial_pairs(self):
        f = self.fixture
        contract = self.base / 'change.json'
        contract.write_text(json.dumps({'schema_version': 1}))
        roles = self.base / 'roles.json'
        roles.write_text(json.dumps(f.contract))
        base = [sys.executable, '-B', str(ROOT / 'scripts/verify_design_change.py'), str(f.xml), str(f.xml), str(contract)]
        contexts = ['--baseline-source-root', str(f.root), '--baseline-source-role-contract', str(roles),
                    '--source-root', str(f.root), '--source-role-contract', str(roles)]
        report = self.base / 'change-result.json'
        result = subprocess.run([*base, *contexts, '--out', str(report)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(set(json.loads(report.read_text())['source_role_contracts']), {'baseline', 'candidate'})
        for extra in (contexts[:4], contexts[4:], contexts[:-2]):
            self.assertNotEqual(subprocess.run([*base, *extra, '--out', str(self.base / 'partial-change.json')], capture_output=True).returncode, 0)
        before = roles.read_bytes()
        self.assertNotEqual(subprocess.run([*base, *contexts, '--out', str(roles)], capture_output=True).returncode, 0)
        self.assertEqual(roles.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
