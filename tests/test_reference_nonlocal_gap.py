"""Synthetic forward criteria: keep native rejection and report local pin defects."""
import json
import os
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(os.environ.get('ASG_RUNTIME', str(Path(__file__).resolve().parents[1])))
sys.path.insert(0, str(ROOT / 'scripts'))
from schematic_layout.reference_contract import verify_reference
from schematic_layout.design_change import read_native, NativeEvidenceGap


class ReferenceNonlocalGapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        for source in (ROOT / 'tests/fixtures/reference_contract').iterdir():
            shutil.copy2(source, self.base / source.name)
        self.net = self.base / 'netlist.xml'
        self.contract = json.loads((self.base / 'contract.json').read_text())

    def mutate(self, blank=False, zero=True):
        tree = ET.parse(self.net)
        if zero:
            comp = ET.SubElement(tree.getroot().find('components'), 'comp', ref='UNQUALIFIED')
            ET.SubElement(comp, 'value').text = 'unknown object'
            ET.SubElement(comp, 'libsource', lib='Synthetic', part='Unknown')
            fields = ET.SubElement(comp, 'fields')
            ET.SubElement(fields, 'field', name='ComponentRole').text = 'mechanical'
        if blank:
            tree.getroot().find("libparts/libpart/pins/pin[@num='3']").set('name', '~')
        tree.write(self.net)

    def test_global_gap_still_rejects_and_never_qualifies_a_self_declared_role(self):
        self.mutate()
        with self.assertRaisesRegex(ValueError, 'UNQUALIFIED.*physical pins'):
            read_native(self.net)
        try:
            report = verify_reference(self.net, self.contract, self.base)
        except ValueError:
            report = {'status': 'FAIL'}
        self.assertEqual(report['status'], 'FAIL')

    def test_unqualified_object_keeps_existing_consumer_fail_exception_class(self):
        self.mutate()
        with self.assertRaises(ValueError) as caught:
            read_native(self.net)
        self.assertNotIsInstance(caught.exception, NativeEvidenceGap)
        report = verify_reference(self.net, self.contract, self.base)
        self.assertEqual(report['native_qualification']['status'], 'FAIL')
        self.assertEqual(report['native_qualification']['unqualified_zero_pin_objects'], ['UNQUALIFIED'])

    def test_cli_fails_and_retains_local_target_and_global_rejection(self):
        self.mutate(blank=True)
        output = self.base / 'report.json'
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/verify_reference_contract.py'),
                                 str(self.net), str(self.base / 'contract.json'), '--out', str(output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(output.read_text())
        self.assertEqual(report['native_qualification']['status'], 'FAIL')
        self.assertTrue(any(isinstance(f, dict) and f.get('pin') == '3'
                            for f in report['pin_maps']['U1']['failures']))

    def test_local_pin_mismatch_reported_even_with_unrelated_gap(self):
        self.mutate(blank=True)
        try:
            report = verify_reference(self.net, self.contract, self.base)
        except ValueError as error:
            self.fail('Whole-input failure masks independently inspectable pin metadata: ' + str(error))
        self.assertEqual(report['status'], 'FAIL')
        failures = report.get('pin_maps', {}).get('U1', {}).get('failures', [])
        self.assertTrue(any(isinstance(f, dict) and f.get('pin') == '3' for f in failures), report)
        self.assertIn('UNQUALIFIED', report.get('error', '') + json.dumps(report.get('errors', [])))

    def test_complete_valid_fixture_stays_pass(self):
        self.assertEqual(verify_reference(self.net, self.contract, self.base)['status'], 'PASS')

    def test_blank_name_without_global_gap_still_fails(self):
        self.mutate(blank=True, zero=False)
        report = verify_reference(self.net, self.contract, self.base)
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['pin_maps']['U1']['status'], 'FAIL')

    def test_duplicate_physical_assignment_remains_hard_rejection(self):
        tree = ET.parse(self.net)
        original = tree.getroot().find("nets/net/node[@ref='U1'][@pin='3']")
        other = ET.SubElement(tree.getroot().find('nets'), 'net', name='duplicate')
        ET.SubElement(other, 'node', **original.attrib)
        tree.write(self.net)
        with self.assertRaisesRegex(ValueError, 'multiple nets'):
            verify_reference(self.net, self.contract, self.base)

    def test_malformed_xml_remains_hard_rejection(self):
        self.net.write_text('<export>')
        with self.assertRaisesRegex(ValueError, 'Malformed'):
            verify_reference(self.net, self.contract, self.base)


if __name__ == '__main__':
    unittest.main()
