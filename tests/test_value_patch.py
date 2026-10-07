"""Surgical edits preserve all unrelated bytes and native physical partitions."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from schematic_layout.value_patch import prepare, apply, frozen_files
from schematic_layout.project_audit import audit_project
from schematic_layout.generate import generate, library_dirs
from schematic_layout.native import find_cli
from schematic_layout.sexpr import dump, parse, all_nodes, form, first
from test_project_audit import library, symbol, sheet


class ValuePatch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name); self.root = self.base / 'board.kicad_sch'
        self.root.write_text('(kicad_sch (uuid root) ' + '(lib_symbols ' + dump(library()) + ')' + ' ' + dump(symbol('U1', 1, '/root')) + ')\n')
        # Existing synthetic audit fixture lacks Value; add exactly one.
        self.root.write_text(self.root.read_text().replace('(property "Reference"', '(property "Value" "old")\n(property "Reference"'))
        self.contract = {'schema_version': 1, 'baseline_files': frozen_files(self.root, audit_project(self.root)), 'changes': {'U1': {'before': 'old', 'after': 'new'}}}

    def refresh(self):
        self.contract['baseline_files'] = frozen_files(self.root, audit_project(self.root))

    def test_only_value_token_changes_source_remains_unchanged(self):
        original = self.root.read_bytes()
        blobs, _, edits = prepare(self.root, self.contract)
        self.assertEqual(blobs[self.root.name], original.replace(b'"Value" "old"', b'"Value" "new"'))
        self.assertEqual(self.root.read_bytes(), original); self.assertEqual(len(edits), 1)

    def test_stale_baseline_wrong_before_and_missing_ref_rejected(self):
        for c in [dict(self.contract, baseline_files={}), dict(self.contract, changes={'U1': {'before': 'wrong', 'after': 'new'}}), dict(self.contract, changes={'ABSENT': {'before': 'old', 'after': 'new'}})]:
            with self.assertRaises(ValueError): prepare(self.root, c)

    def test_multiunit_values_change_together(self):
        text = self.root.read_text().rstrip()[:-1] + ' ' + dump(symbol('U1', 2, '/root')).replace('(property "Reference"', '(property "Value" "old") (property "Reference"') + ')\n'
        self.root.write_text(text); self.refresh()
        blobs, _, edits = prepare(self.root, self.contract)
        self.assertEqual(len(edits), 2); self.assertEqual(blobs[self.root.name].count(b'"Value" "new"'), 2)

    def test_one_wrong_unit_aborts_entire_preparation(self):
        text = self.root.read_text().rstrip()[:-1] + ' ' + dump(symbol('U1', 2, '/root')).replace('(property "Reference"', '(property "Value" "other") (property "Reference"') + ')'
        self.root.write_text(text); self.refresh(); original = self.root.read_bytes()
        with self.assertRaises(ValueError): prepare(self.root, self.contract)
        self.assertEqual(self.root.read_bytes(), original)

    def test_fields_noop_and_virtual_refs_are_rejected(self):
        for changes in [{'U1': {'before': 'old', 'after': 'old'}}, {'U1': {'before': 'old', 'after': 'new', 'footprint': 'x'}}, {'#PWR1': {'before': 'old', 'after': 'new'}}]:
            with self.assertRaises(ValueError): prepare(self.root, dict(self.contract, changes=changes))

    def test_duplicate_value_and_missing_value_rejected(self):
        original = self.root.read_text()
        for text in [original.replace('(property "Value" "old")', ''), original.replace('(property "Value" "old")', '(property "Value" "old") (property "Value" "old")')]:
            self.root.write_text(text); self.refresh()
            with self.assertRaises(ValueError): prepare(self.root, self.contract)

    def test_shared_symbol_other_instance_or_project_rejected(self):
        self.root.write_text(self.root.read_text().replace('(instances', '(instances (project "other" (path "/root" (reference "U9") (unit 1)))', 1)); self.refresh()
        with self.assertRaisesRegex(ValueError, 'Shared'): prepare(self.root, self.contract)

    def test_hierarchical_units_edit_only_child_files(self):
        self.root.write_text(dump(form('kicad_sch', form('uuid', 'root'), sheet('one', 'a.kicad_sch', '2'), sheet('two', 'b.kicad_sch', '3'))) + '\n')
        for filename, uid, unit in [('a', 'one', 1), ('b', 'two', 2)]:
            sym = symbol('U1', unit, '/root/' + uid); sym.append(form('property', 'Value', 'old'))
            (self.base / (filename + '.kicad_sch')).write_text(dump(form('kicad_sch', form('uuid', filename), form('lib_symbols', library()), sym)) + '\n')
        self.refresh(); original = self.root.read_bytes()
        blobs, audit, edits = prepare(self.root, self.contract)
        self.assertEqual(audit['page_count'], 3); self.assertEqual(len(edits), 2)
        self.assertEqual(blobs[self.root.name], original)
        for filename in ['a.kicad_sch', 'b.kicad_sch']:
            self.assertEqual(blobs[filename], (self.base / filename).read_bytes().replace(b'"Value" "old"', b'"Value" "new"'))

    def test_shared_child_file_cannot_change_one_of_two_instances(self):
        self.root.write_text(dump(form('kicad_sch', form('uuid', 'root'), sheet('one', 'a.kicad_sch', '2'), sheet('two', 'a.kicad_sch', '3'))))
        sym = symbol('U1', 1, '/root/one'); sym.append(form('property', 'Value', 'old'))
        first(first(sym, 'instances'), 'project').append(form('path', '/root/two', form('reference', 'U2'), form('unit', 1)))
        (self.base / 'a.kicad_sch').write_text(dump(form('kicad_sch', form('uuid', 'a'), form('lib_symbols', library()), sym)))
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'Shared'): prepare(self.root, self.contract)

    def test_project_configuration_is_frozen_and_copied(self):
        config = self.root.with_suffix('.kicad_pro'); config.write_text('{"board": {}}'); self.refresh()
        blobs, _, _ = prepare(self.root, self.contract)
        self.assertEqual(blobs[config.name], config.read_bytes())
        config.write_text('{"board": {"changed": true}}')
        with self.assertRaisesRegex(ValueError, 'hashes'): prepare(self.root, self.contract)

    def test_output_inside_source_project_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'outside source'): apply(self.root, self.contract, self.base / 'candidate')

    def test_failed_precondition_does_not_publish_candidate(self):
        out = self.base.parent / (self.base.name + '-candidate')
        c = dict(self.contract, baseline_files={})
        with self.assertRaises(ValueError): apply(self.root, c, out)
        self.assertFalse(out.exists())

    @unittest.skipUnless(find_cli() and library_dirs(), 'native KiCad unavailable')
    def test_real_rc_native_exports_preserve_geometry_connectivity_and_values(self):
        fixture = Path(__file__).parent / 'fixtures/generation'
        intent = json.loads((fixture / 'rc_filter.intent.json').read_text())
        layout = json.loads((fixture / 'rc_filter.layout.json').read_text())
        tree, _ = generate(intent, layout, 'board'); self.root.write_text(dump(tree) + '\n')
        self.refresh(); self.contract['changes'] = {'R1': {'before': '1k', 'after': '2k'}}
        out = self.base / 'candidate-output'
        # Output cannot sit inside the source project: use a separate sibling.
        with tempfile.TemporaryDirectory() as candidate_parent:
            result = apply(self.root, self.contract, Path(candidate_parent) / 'candidate')
            self.assertEqual(result['status'], 'PATCH_VERIFIED', result.get('error'))
            self.assertEqual(result['native_change']['status'], 'PASS')
            after = (Path(candidate_parent) / 'candidate/project/board.kicad_sch').read_bytes()
            self.assertEqual(after, self.root.read_bytes().replace(b'"Value" "1k"', b'"Value" "2k"'))
            self.assertEqual(result['hierarchy']['page_count'], 1)
            self.assertEqual(result['visual_review'], 'REVIEW_PENDING')


if __name__ == '__main__':
    unittest.main()
