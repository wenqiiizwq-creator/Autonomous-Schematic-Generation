"""Purpose-driven specifications, honest selection and real KiCad projection.

All part numbers and guarantees below are synthetic test data, not approved parts.
"""
import copy
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from schematic_layout import component_requirements as cr
from schematic_layout.part_classes import part_class, category, COMMON, SPECIAL, GENERAL_R
from schematic_layout.pages import page_intents
from schematic_layout.recipes import Sheet, LEFT, RIGHT
from schematic_layout.sexpr import all_nodes, dump, first, form, Atom


def fixture(root, qualified=False, actual_tolerance=1):
    evidence = root / 'calculation.txt'
    guarantee = f'tolerance {actual_tolerance:g} %; pulse energy 2 J.'
    evidence.write_text('Synthetic test calculation and manufacturer guarantees: ' + guarantee + '\n', encoding='utf-8')
    source = {'path': 'calculation.txt', 'sha256': hashlib.sha256(evidence.read_bytes()).hexdigest(), 'locator': 'line 1'}
    conditions = {'waveform': 'exponential', 'duration': '10 ms', 'repetition': '1 per 60 s',
                  'temperature': '70 degC', 'drift': '<=1 % after 1000 pulses'}
    reqs = [dict(parameter='tolerance', op='le', value=5, unit='%', conditions={'temperature': '25 degC'},
                 basis='requirement', source=source),
            dict(parameter='pulse_energy', op='ge', value=1, unit='J', conditions=conditions,
                 basis='calculation', source=source)]
    selection = {'status': 'not_selected'}
    if qualified:
        selection = {'status': 'qualified', 'mpn': 'SYNTHETIC-TEST-1', 'route': 'synthetic manufacturer fixture',
                     'properties': [dict(parameter=r['parameter'], value=v, unit=r['unit'], conditions=r['conditions'],
                                         basis='guaranteed', source=dict(source, kind='manufacturer',
                                             quote=guarantee)) for r, v in zip(reqs, [actual_tolerance, 2])]}
    entry = dict(ref='R1', kind='resistor', purpose='pulse discharge', definition_status='complete', display='note',
                 required_parameters=['tolerance', 'pulse_energy'], requirements=reqs,
                 procurement={'mode': 'spec', 'reason': 'finite performance contract permits equivalent parts'}, selection=selection)
    record = {'schema_version': 1, 'screening': [{'refs': ['R1'], 'decision': 'contract', 'reason': 'pulse discharge duty'}],
              'components': [entry]}
    intent = {'schema_version': 1, 'design_id': 'performance-fixture', 'title': 'Synthetic performance test',
              'components': [{'ref': 'R1', 'lib_id': 'Device:R', 'value': '100R', 'fields': {'Circuit': 'load'}}],
              'nets': [{'name': 'A', 'pins': ['R1.1']}, {'name': 'B', 'pins': ['R1.2']}], 'no_connect': []}
    return intent, record


class PerformanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.intent, self.record = fixture(self.root)

    def project(self):
        return cr.project(self.intent, self.record, self.root)

    def test_complete_pulse_contract_does_not_force_mpn(self):
        intent = self.project()
        self.assertNotIn('mpn', intent['components'][0])
        self.assertEqual(COMMON, part_class(intent['components'][0]))
        result = cr.audit(intent, self.record, self.root)
        self.assertEqual([], result['errors'])
        self.assertEqual({'R1': 'complete'}, result['definition'])
        self.assertEqual({'R1': 'not_selected'}, result['selection'])
        self.assertEqual('INCOMPLETE', result['status'])

    def test_pulse_word_alone_cannot_define_requirement(self):
        self.record['components'][0]['requirements'] = self.record['components'][0]['requirements'][:1]
        self.record['components'][0]['required_parameters'] = ['tolerance']
        with self.assertRaisesRegex(ValueError, 'finite pulse'):
            self.project()

    def test_missing_conditions_and_nonfinite_rejected(self):
        req = self.record['components'][0]['requirements'][1]
        req['value'] = float('nan')
        req['conditions'].pop('repetition')
        errors, _ = cr.record_errors(self.record, self.intent, self.root)
        self.assertTrue(any('finite' in e for e in errors), errors)
        self.assertTrue(any('repetition' in e for e in errors), errors)

    def test_candidate_is_not_bom_mpn(self):
        self.record['components'][0]['selection'] = {'status': 'candidate', 'mpn': 'UNVERIFIED', 'route': 'catalog search'}
        self.intent['components'][0]['mpn'] = 'OLD'
        self.intent['components'][0]['datasheet'] = 'OLD.pdf'
        intent = self.project()
        self.assertNotIn('mpn', intent['components'][0])
        self.assertNotIn('datasheet', intent['components'][0])
        self.assertEqual('candidate', intent['components'][0]['fields']['SelectionStatus'])
        intent['components'][0]['mpn'] = 'UNVERIFIED'
        self.assertEqual('FAIL', cr.audit(intent, self.record, self.root)['status'])

    def test_one_percent_meets_five_percent_requirement(self):
        intent, record = fixture(self.root, True)
        projected = cr.project(intent, record, self.root)
        result = cr.audit(projected, record, self.root)
        self.assertEqual('PASS', result['status'], result)
        self.assertIn('tolerance<=5 %', projected['components'][0]['fields']['RequirementSpec'])
        self.assertIn('tolerance=1 %', projected['components'][0]['fields']['SelectedSpec'])

    def test_verified_controlled_spec_can_finish_without_fixed_mpn(self):
        intent, record = fixture(self.root, True)
        selected = record['components'][0]['selection']
        selected.update(status='by_spec', standard_id='SYNTHETIC-CONTROLLED-SPEC-1', route='synthetic qualified standard catalog')
        selected.pop('mpn')
        for prop in selected['properties']:
            prop['source']['kind'] = 'controlled_standard'
        projected = cr.project(intent, record, self.root)
        self.assertNotIn('mpn', projected['components'][0])
        self.assertEqual('PASS', cr.audit(projected, record, self.root)['status'])
        self.assertEqual('by_spec', projected['components'][0]['fields']['SelectionStatus'])

    def test_generic_spec_is_not_a_qualified_controlled_standard(self):
        intent, record = fixture(self.root, True)
        selected = record['components'][0]['selection']
        selected.update(status='by_spec', standard_id='TEST-SPEC', route='catalog')
        selected.pop('mpn')
        with self.assertRaisesRegex(ValueError, 'controlled standard guarantees'):
            cr.project(intent, record, self.root)

    def test_five_percent_part_cannot_be_labelled_one_percent(self):
        intent, record = fixture(self.root, True, actual_tolerance=5)
        projected = cr.project(intent, record, self.root)
        projected['components'][0]['value'] = '100R/1%'
        result = cr.audit(projected, record, self.root)
        self.assertEqual('FAIL', result['status'])
        self.assertTrue(any('value tolerance' in e for e in result['errors']))

    def test_generic_tolerance_field_is_ambiguous(self):
        projected = self.project()
        projected['components'][0]['fields']['Tolerance'] = '1%'
        self.assertTrue(any('ambiguous' in e for e in cr.audit(projected, self.record, self.root)['errors']))

    def test_changed_calculation_invalidates_evidence(self):
        projected = self.project()
        (self.root / 'calculation.txt').write_text('changed calculation')
        self.assertTrue(any('source changed' in e for e in cr.audit(projected, self.record, self.root)['errors']))

    def test_changed_requirement_invalidates_projection(self):
        projected = self.project()
        self.record['components'][0]['requirements'][1]['value'] = 1.5
        self.assertTrue(any('stale' in e for e in cr.audit(projected, self.record, self.root)['errors']))

    def add_nominal(self, parameter, value, unit):
        req = copy.deepcopy(self.record['components'][0]['requirements'][0])
        req.update(parameter=parameter, op='eq', value=value, unit=unit)
        self.record['components'][0]['requirements'].append(req)
        self.record['components'][0]['required_parameters'].append(parameter)

    def test_exact_resistance_generates_nominal_from_single_source(self):
        self.add_nominal('resistance', 100, 'ohm')
        self.intent['components'][0]['value'] = '220R'
        projected = self.project()
        self.assertEqual('100R', projected['components'][0]['value'])
        self.assertEqual([], cr.audit(projected, self.record, self.root)['errors'])

    def test_nominal_tampering_is_rejected_even_with_consistent_fields(self):
        self.add_nominal('resistance', 100, 'ohm')
        projected = self.project()
        projected['components'][0]['value'] = '220R'
        self.assertTrue(any('nominal Value' in e for e in cr.audit(projected, self.record, self.root)['errors']))

    def test_capacitor_and_inductor_exact_nominals_are_projected(self):
        for kind, parameter, value, unit, expected in [('capacitor', 'capacitance', 100, 'nF', '100nF'),
                                                      ('inductor', 'inductance', 10, 'uH', '10uH')]:
            entry = {'kind': kind, 'requirements': [{'parameter': parameter, 'op': 'eq', 'value': value, 'unit': unit}]}
            self.assertEqual(expected, cr.nominal_value(entry))
            entry['requirements'][0]['op'] = 'ge'
            self.assertIsNone(cr.nominal_value(entry))  # effective/capability bounds do not rename the nominal

    def test_typical_or_model_cannot_be_guarantee(self):
        intent, record = fixture(self.root, True)
        record['components'][0]['selection']['properties'][0]['basis'] = 'typical'
        with self.assertRaisesRegex(ValueError, 'typical/model'):
            cr.project(intent, record, self.root)

    def test_unsupported_condition_does_not_qualify(self):
        intent, record = fixture(self.root, True)
        record['components'][0]['selection']['properties'][1]['conditions'] = {'temperature': '25 degC'}
        with self.assertRaisesRegex(ValueError, 'conditions'):
            cr.project(intent, record, self.root)

    def test_exact_quote_must_exist(self):
        intent, record = fixture(self.root, True)
        record['components'][0]['selection']['properties'][0]['source']['quote'] = 'not in the document'
        with self.assertRaisesRegex(ValueError, 'quote not found'):
            cr.project(intent, record, self.root)

    def test_five_percent_quote_cannot_be_recorded_as_one_percent(self):
        intent, record = fixture(self.root, True, actual_tolerance=5)
        record['components'][0]['selection']['properties'][0]['value'] = 1
        with self.assertRaisesRegex(ValueError, 'value/unit not found'):
            cr.project(intent, record, self.root)

    def test_required_identity_is_not_waived(self):
        for kind, lib, ref in [('ic', 'Timer:NE555', 'U1'), ('varistor', 'Device:Varistor', 'RV101'),
                               ('capacitor', 'Device:C', 'CX1')]:
            intent, record = fixture(self.root)
            intent['components'][0].update(ref=ref, lib_id=lib, value='X2 100n' if ref == 'CX1' else kind)
            record['components'][0].update(ref=ref, kind=kind)
            record['screening'][0]['refs'] = [ref]
            with self.assertRaisesRegex(ValueError, 'needs mpn'):
                cr.project(intent, record, self.root)

    def test_curve_dependency_requires_binding(self):
        self.record['components'][0]['binding_dependencies'] = ['manufacturer-specific pulse curve used in the calculation']
        with self.assertRaisesRegex(ValueError, 'needs mpn'):
            self.project()

    def test_mov_cannot_inherit_resistor_category(self):
        mov = {'ref': 'RV101', 'lib_id': 'Device:Varistor', 'value': 'MOV', 'fields': {'Category': GENERAL_R}}
        self.assertIn('实际器件类型', category(mov)[1])
        self.assertEqual(SPECIAL, part_class(mov))

    def test_screening_is_required_and_purpose_driven(self):
        self.record['screening'] = []
        with self.assertRaisesRegex(ValueError, 'screening must cover'):
            self.project()

    def test_pending_calculation_is_visible_not_complete(self):
        entry = self.record['components'][0]
        entry.update(definition_status='pending', gaps=['calculate actual capacitor discharge energy'], requirements=[])
        projected = self.project()
        self.assertIn('待计算', projected['components'][0]['fields']['RequirementSpec'])
        self.assertIn('性能计算未完成', str(cr.audit(projected, self.record, self.root)['pending']))

    def test_marker_survives_page_split(self):
        local = page_intents(self.project())['load']['intent']
        self.assertEqual(1, local['component_requirements_version'])
        self.assertIn('performance_contract', local['components'][0])

    def test_declared_external_sources_and_path_escape(self):
        input_dir = self.root / 'input-root'
        input_dir.mkdir()
        shutil.copy2(self.root / 'calculation.txt', input_dir / 'basis.txt')
        source = copy.deepcopy(self.record['components'][0]['requirements'][0]['source'])
        source['path'] = 'input:requirements/basis.txt'
        self.assertEqual([], cr.source_errors(source, self.root, inputs={'requirements': input_dir}))
        self.assertTrue(cr.source_errors(source, self.root))
        source['path'] = 'input:requirements/../calculation.txt'
        self.assertTrue(cr.source_errors(source, self.root, inputs={'requirements': input_dir}))

    def test_typical_quote_cannot_be_relabelled_guaranteed(self):
        intent, record = fixture(self.root, True)
        evidence = self.root / 'calculation.txt'
        evidence.write_text('typical tolerance 1 %; pulse energy 2 J.')
        for req in record['components'][0]['requirements']:
            req['source']['sha256'] = hashlib.sha256(evidence.read_bytes()).hexdigest()
        for prop in record['components'][0]['selection']['properties']:
            prop['source'].update(sha256=hashlib.sha256(evidence.read_bytes()).hexdigest(), quote=evidence.read_text())
        with self.assertRaisesRegex(ValueError, 'typical/model quote'):
            cr.project(intent, record, self.root)

    def test_continuous_power_constraint_is_used_by_existing_stress_gate(self):
        import audit_design_closure as adc
        req = copy.deepcopy(self.record['components'][0]['requirements'][0])
        req.update(parameter='power', op='ge', value=3, unit='W', conditions={'temperature': '70 degC'})
        self.record['components'][0]['requirements'].append(req)
        self.record['components'][0]['required_parameters'].append('power')
        projected = self.project()
        self.assertEqual(3, adc.written_power(projected['components'][0]))

    def test_missing_new_record_fails_old_record_is_unchecked(self):
        self.assertEqual('NOT_CHECKED', cr.audit(self.intent, None, self.root)['status'])
        self.intent['component_requirements_version'] = 1
        self.assertEqual('FAIL', cr.audit(self.intent, None, self.root)['status'])

    def test_missing_marker_does_not_hide_a_projected_contract(self):
        projected = self.project()
        projected.pop('component_requirements_version')
        self.assertEqual('FAIL', cr.audit(projected, None, self.root)['status'])

    def test_pending_requirements_cannot_qualify_a_part(self):
        intent, record = fixture(self.root, True)
        record['components'][0].update(definition_status='pending', gaps=['derive continuous power'])
        with self.assertRaisesRegex(ValueError, 'cannot qualify'):
            cr.project(intent, record, self.root)


class NativePerformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli = shutil.which('kicad-cli')
        if not cls.cli or not shutil.which('pdftotext'):
            raise unittest.SkipTest('native KiCad and pdftotext required')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        intent, self.record = fixture(self.root)
        self.intent = cr.project(intent, self.record, self.root)
        self.sheet = Sheet(self.intent)
        self.sheet.place('R1', (50.8, 50.8), rotation=90)
        self.sheet.label('R1.1', outward=LEFT)
        self.sheet.label('R1.2', outward=RIGHT)
        self.sheet.performance_notes((20.32, 90.17), width=78)
        self.tree, self.report = self.sheet.build('performance')
        self.sch = self.root / 'performance.kicad_sch'
        self.bom, self.xml, self.pdf = [self.root / p for p in ('BOM.csv', 'netlist.xml', 'schematic.pdf')]
        cr.write_bom(self.intent, self.bom)

    def export(self):
        self.sch.write_text(dump(self.tree), encoding='utf-8')
        for fmt, out in [('netlist', self.xml), ('pdf', self.pdf)]:
            args = [self.cli, 'sch', 'export', fmt]
            if fmt == 'netlist':
                args += ['--format', 'kicadxml']
            result = subprocess.run([*args, '-o', str(out), str(self.sch)], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)

    def audit(self):
        return cr.audit(self.intent, self.record, self.root, bom=self.bom, xml=self.xml, schematic=self.sch, pdf=self.pdf)

    def test_native_pdf_xml_bom_and_visible_note_agree(self):
        self.export()
        result = self.audit()
        self.assertEqual([], result['errors'], result)
        self.assertEqual('CHECKED', result['native'], result)
        self.assertEqual('INCOMPLETE', result['status'])  # selection is intentionally unqualified
        self.assertTrue(all('型号未定' in p for p in result['pending']), result)

    def test_controlled_spec_qualification_passes_native_gate_without_mpn(self):
        intent, self.record = fixture(self.root, True)
        selected = self.record['components'][0]['selection']
        selected.update(status='by_spec', standard_id='SYNTHETIC-STANDARD', route='synthetic controlled catalog')
        selected.pop('mpn')
        for prop in selected['properties']:
            prop['source']['kind'] = 'controlled_standard'
        self.intent = cr.project(intent, self.record, self.root)
        sheet = Sheet(self.intent)
        sheet.place('R1', (50.8, 50.8), rotation=90)
        sheet.label('R1.1', outward=LEFT)
        sheet.label('R1.2', outward=RIGHT)
        sheet.performance_notes((20.32, 90.17))
        self.tree, _ = sheet.build('performance')
        cr.write_bom(self.intent, self.bom)
        self.export()
        result = self.audit()
        self.assertEqual('PASS', result['status'], result)
        self.assertEqual('CHECKED', result['native'])
        self.assertNotIn('mpn', self.intent['components'][0])

    def test_hidden_property_is_not_visible_requirement(self):
        sym = all_nodes(self.tree, 'symbol')[0]
        prop = next(p for p in all_nodes(sym, 'property') if p[1] == 'Performance')
        first(prop, 'effects').append(form('hide', Atom('yes')))
        self.export()
        result = self.audit()
        self.assertEqual('FAIL', result['status'], result)
        self.assertTrue(any('hidden property' in e for e in result['errors']))

    def test_missing_same_page_note_fails(self):
        self.tree[:] = [n for n in self.tree if not isinstance(n, list) or not n or n[0] != 'text']
        self.export()
        result = self.audit()
        self.assertEqual('FAIL', result['status'], result)
        self.assertTrue(any('same-page technical note' in e for e in result['errors']))

    def test_hidden_property_still_fails_when_pdf_text_unavailable(self):
        sym = all_nodes(self.tree, 'symbol')[0]
        prop = next(p for p in all_nodes(sym, 'property') if p[1] == 'Performance')
        first(prop, 'effects').append(form('hide', Atom('yes')))
        self.export()
        with mock.patch.object(cr, 'document_text', return_value=None):
            result = self.audit()
        self.assertEqual('FAIL', result['status'], result)
        self.assertTrue(any('hidden property' in e for e in result['errors']))
        self.assertEqual('INSUFFICIENT', result['native'])

    def test_stale_bom_fails(self):
        self.export()
        self.bom.write_text(self.bom.read_text(encoding='utf-8-sig').replace('tolerance<=5 %', 'tolerance<=1 %'), encoding='utf-8-sig')
        result = self.audit()
        self.assertEqual('FAIL', result['status'], result)
        self.assertTrue(any('BOM RequirementSpec' in e for e in result['errors']))

    def test_missing_pdf_is_insufficient(self):
        self.export()
        self.pdf.unlink()
        result = self.audit()
        self.assertEqual('INSUFFICIENT', result['native'], result)
        self.assertNotEqual('PASS', result['status'])

    def test_native_gate_is_included_in_verification_summary(self):
        self.export()
        (self.root / 'record').mkdir()
        (self.root / 'record' / 'component-requirements.json').write_text(json.dumps(self.record))
        intent_file = self.root / 'record' / 'electrical-intent.json'
        intent_file.write_text(json.dumps(self.intent))
        output = self.root / 'verification'
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'verify_schematic.py'
        subprocess.run([sys.executable, '-B', str(script), str(self.sch), '--intent', str(intent_file),
                        '--artifact-root', str(self.root), '--out', str(output), '--cli', self.cli],
                       capture_output=True, text=True, timeout=120)
        summary = json.loads((output / 'summary.json').read_text())
        gate = json.loads((output / 'component-requirements-check.json').read_text())
        self.assertEqual('INCOMPLETE', summary['gates']['component_requirements']['status'])
        self.assertEqual([], gate['errors'], gate)
        self.assertEqual('CHECKED', gate['native'], gate)

    def test_bom_cannot_reclassify_resistor_as_another_kind(self):
        self.export()
        self.bom.write_text(self.bom.read_text(encoding='utf-8-sig').replace(',resistor,', ',varistor,'), encoding='utf-8-sig')
        self.assertTrue(any('BOM Kind' in e for e in self.audit()['errors']))


if __name__ == '__main__':
    unittest.main()
