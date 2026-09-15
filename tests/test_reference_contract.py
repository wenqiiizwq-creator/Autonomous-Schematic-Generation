"""Mutation tests for source identity, package pins, peripheral and stage coverage."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from schematic_layout.reference_contract import verify_reference


class ReferenceContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        for p in (ROOT / "tests/fixtures/reference_contract").iterdir(): shutil.copy2(p, self.base / p.name)
        self.net = self.base / "netlist.xml"
        self.contract = json.loads((self.base / "contract.json").read_text())

    def audit(self): return verify_reference(self.net, self.contract, self.base)

    def mutate(self, action):
        tree = ET.parse(self.net); action(tree.getroot()); tree.write(self.net)

    def test_declared_facts_pass_without_claiming_qualification(self):
        r = self.audit()
        self.assertEqual(r["status"], "PASS", r)
        self.assertTrue(r["unverified"])
        self.assertEqual(len(r["checks"]), 5)

    def test_changed_document_fails_missing_document_is_insufficient(self):
        source = self.base / "source.txt"; source.write_text('different revision')
        self.assertEqual(self.audit()["status"], "FAIL")
        source.unlink()
        self.assertEqual(self.audit()["status"], "INSUFFICIENT")

    def test_exact_package_variant_mismatch_fails(self):
        self.mutate(lambda r: setattr(r.find("components/comp[@ref='U1']/value"), "text", "Probe5-OTHER-PACKAGE"))
        self.assertEqual(self.audit()["pin_maps"]["U1"]["status"], "FAIL")

    def test_mpn_field_cannot_silently_override_correct_display_value(self):
        def change(r):
            fields = ET.SubElement(r.find("components/comp[@ref='U1']"), 'fields')
            ET.SubElement(fields, 'field', name='MPN').text = 'Probe5-WRONG'
        self.mutate(change)
        self.assertEqual(self.audit()["status"], "FAIL")

    def test_all_pins_including_nc_must_be_mapped(self):
        del self.contract["pin_maps"]["U1"]["pins"]["4"]
        self.assertEqual(self.audit()["pin_maps"]["U1"]["status"], "FAIL")

    def test_electrical_type_mismatch_is_independent_of_number(self):
        self.mutate(lambda r: r.find("nets/net/node[@ref='U1'][@pin='3']").set("pintype", "bidirectional"))
        r = self.audit()
        self.assertEqual(r["pin_maps"]["U1"]["status"], "FAIL")
        self.assertEqual(r["checks"]["bypass-high"]["status"], "PASS")

    def test_names_need_explicit_aliases_not_global_punctuation_stripping(self):
        self.mutate(lambda r: r.find("nets/net/node[@ref='U1'][@pin='5']").set("pinfunction", "VCC_5"))
        self.assertEqual(self.audit()["status"], "FAIL")
        self.contract["pin_maps"]["U1"]["pins"]["5"]["names"].append("VCC_5")
        self.assertEqual(self.audit()["status"], "PASS")

    def test_native_nc_marker_is_not_an_electrical_type(self):
        self.mutate(lambda r: r.find("nets/net/node[@ref='U1'][@pin='3']").set("pintype", "output+no_connect"))
        self.assertEqual(self.audit()["pin_maps"]["U1"]["status"], "PASS")

    def test_required_capacitor_deletion_fails(self):
        def remove(r):
            cs = r.find('components'); cs.remove(cs.find("comp[@ref='C1']"))
            for net in r.findall('nets/net'):
                for pin in list(net):
                    if pin.get('ref') == 'C1': net.remove(pin)
        self.mutate(remove)
        self.assertEqual(self.audit()["features"]["analog"]["status"], "FAIL")

    def test_return_moved_to_different_ground_fails(self):
        def move(r):
            g = r.find("nets/net[@name='GND']"); pin = g.find("node[@ref='C1']"); g.remove(pin)
            ET.SubElement(r.find('nets'), 'net', name='OTHER_GND').append(pin)
        self.mutate(move)
        self.assertEqual(self.audit()["checks"]["bypass-low"]["status"], "FAIL")

    def test_same_name_alias_cannot_replace_physical_partition(self):
        def rename(r):
            r.find("nets/net[@name='VCC']").set('name', '/other-name')
        self.mutate(rename)
        self.assertEqual(self.audit()["status"], "PASS")

    def test_wrong_value_and_dnp_cannot_satisfy_required_branch(self):
        self.mutate(lambda r: setattr(r.find("components/comp[@ref='C1']/value"), 'text', '1nF'))
        self.assertEqual(self.audit()["checks"]["bypass-value"]["status"], "FAIL")
        self.mutate(lambda r: ET.SubElement(r.find("components/comp[@ref='C1']"), 'property', name='dnp'))
        self.assertEqual(self.audit()["checks"]["bypass-high"]["status"], "FAIL")

    def test_short_between_required_distinct_rails_fails(self):
        def short(r):
            nets = r.find('nets'); hi = nets.find("net[@name='VCC']"); lo = nets.find("net[@name='GND']")
            hi.extend(list(lo)); nets.remove(lo)
        self.mutate(short)
        self.assertEqual(self.audit()["checks"]["rails-distinct"]["status"], "FAIL")

    def test_missing_declared_driver_stage_component_fails(self):
        self.contract['features'][0]['stages'].append({'id':'load-driver','role':'Coil power driver','refs':['Q_REQUIRED'],'checks':['enable']})
        r = self.audit()
        self.assertEqual(r['features']['analog']['stages'][-1]['status'], 'FAIL')

    def test_uncovered_core_or_feature_is_insufficient_not_pass(self):
        self.contract['scope']['core_refs'].append('U2')
        self.contract['scope']['feature_ids'].append('load-actuation')
        r = self.audit()
        self.assertEqual(r['status'], 'INSUFFICIENT')
        self.assertEqual(len(r['coverage_gaps']), 2)

    def test_malformed_or_empty_contract_does_not_pass(self):
        for mutate in (lambda c: c.update(unknown=True), lambda c: c['checks'][0].update(kind='simulate'), lambda c: c['features'][0]['stages'][0].update(checks=['absent']), lambda c: c['scope'].update(core_refs=[])):
            original = copy.deepcopy(self.contract); mutate(self.contract)
            with self.assertRaises(ValueError): self.audit()
            self.contract = original

    def test_cli_rejects_source_output_alias_and_keeps_hash(self):
        source = self.base / 'source.txt'; before = source.read_bytes()
        alias = self.base / 'alias.json'; alias.hardlink_to(source)
        r = subprocess.run([sys.executable, str(ROOT / 'scripts/verify_reference_contract.py'), str(self.net), str(self.base / 'contract.json'), '--out', str(alias)], capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(source.read_bytes(), before)


if __name__ == '__main__': unittest.main()
