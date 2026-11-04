"""Nets declared to leave the design (boundary_nets): global label on one page, contract row, ERC waiver only for them."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from schematic_layout import boundary
from schematic_layout.generate import Libraries, library_dirs
from schematic_layout.native import find_cli, project_settings, verify
from schematic_layout.pages import page_intents
from schematic_layout.recipes import DOWN, Sheet
from schematic_layout.sexpr import dump


def intent(declared=True):
    i = {'schema_version': 1, 'design_id': 'edge', 'title': 'edge', 'components': [
        {'ref': 'R1', 'lib_id': 'Device:R', 'value': '10k', 'footprint': '', 'fields': {'Circuit': 'A'}},
        {'ref': 'R2', 'lib_id': 'Device:R', 'value': '10k', 'footprint': '', 'fields': {'Circuit': 'B'}}],
        'nets': [{'name': 'EN_N1', 'pins': ['R1.1']}, {'name': 'FLT1', 'pins': ['R2.1']},
                 {'name': 'GND', 'pins': ['R1.2', 'R2.2']}], 'no_connect': []}
    if declared:
        i['boundary_nets'] = [{'net': 'EN_N1', 'to': 'MCU 板', 'contract': '设计资料/MCU与固件接口.md'}]
    return i


def single(name):
    return {'type': 'single_global_label', 'description': 'Global label only appears once in the schematic',
            'items': [{'description': "全局标签 '%s'" % name}]}


class DeclarationTests(unittest.TestCase):
    def test_malformed_unknown_and_repeated_declarations_are_rejected(self):
        for ds in ({'net': 'EN_N1'}, [{'net': 'EN_N1', 'to': 'MCU'}], [{'net': 'NOPE', 'to': 'MCU', 'contract': 'c.md'}],
                   [{'net': 'EN_N1', 'to': 'MCU', 'contract': 'c.md'}] * 2, [{'net': 'EN_N1', 'to': ' ', 'contract': 'c.md'}]):
            i = intent()
            i['boundary_nets'] = ds
            with self.subTest(ds=ds):
                self.assertRaises(ValueError, boundary.declarations, i)

    def test_only_a_declared_single_global_label_is_waived(self):
        dangling = dict(single('EN_N1'), type='label_dangling')
        kept, waived = boundary.split_erc([single('EN_N1'), single('FLT1'), dangling], intent())
        self.assertEqual([{'type': 'single_global_label', 'nets': ['EN_N1'], 'to': ['MCU 板']}], waived)
        self.assertEqual([single('FLT1'), dangling], kept)
        kept, waived = boundary.split_erc([single('EN_N1')], intent(declared=False))
        self.assertEqual(([single('EN_N1')], []), (kept, waived))

    def test_contract_document_and_row_are_required(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            found = []
            resolve = lambda p: (root / p) if (root / p).is_file() else None
            boundary.audit_contracts(intent(), resolve, lambda code, item: found.append(code))
            self.assertEqual(['boundary_contract_missing'], found)
            doc = root / '设计资料/MCU与固件接口.md'
            doc.parent.mkdir()
            doc.write_text('EN_N1 在正文里出现不算\n\n| 网络 | 方向 |\n|---|---|\n| EN_N10 | 输入 |\n', encoding='utf-8')
            found.clear()
            boundary.audit_contracts(intent(), resolve, lambda code, item: found.append(code))
            self.assertEqual(['boundary_net_not_in_contract'], found)
            doc.write_text('| 网络 | 方向 |\n|---|---|\n| `EN_N1` | MCU → 本板 |\n', encoding='utf-8')
            found.clear()
            self.assertEqual(['EN_N1'], boundary.audit_contracts(intent(), resolve, lambda code, item: found.append(code)))
            self.assertEqual([], found)

    def test_pages_carry_the_declaration_and_make_the_net_leave_the_page(self):
        pages = page_intents(intent(), rails=['GND'])
        self.assertEqual(['EN_N1'], pages['A']['external'])
        self.assertEqual(intent()['boundary_nets'], pages['A']['intent']['boundary_nets'])
        self.assertEqual([], pages['B']['external'])
        self.assertNotIn('boundary_nets', pages['B']['intent'])

    def test_design_closure_audit_checks_the_contract(self):
        from test_derating_audit import DeratingAuditTests
        from audit_design_closure import sha256
        base = DeratingAuditTests('run_audit')
        base.setUp()
        self.addCleanup(base.tmp.cleanup)
        i = json.loads(base.intent.read_text())
        i['nets'] = [{'name': 'EN_N1', 'pins': ['Q1.1']}]
        i['boundary_nets'] = [{'net': 'EN_N1', 'to': 'MCU 板', 'contract': '设计资料/MCU与固件接口.md'}]
        base.intent.write_text(json.dumps(i, ensure_ascii=False))
        base.record['intent_sha256'] = sha256(base.intent)
        codes = lambda: {e['code'] for e in base.run_audit()['errors']}
        self.assertIn('boundary_contract_missing', codes())
        doc = base.root / '设计资料/MCU与固件接口.md'
        doc.parent.mkdir()
        doc.write_text('| 网络 | 方向 |\n|---|---|\n| EN_N1 | MCU → 本板 |\n', encoding='utf-8')
        self.assertFalse({c for c in codes() if c.startswith('boundary')})
        self.assertEqual(['EN_N1'], base.run_audit()['boundary_nets'])


class DrawingTests(unittest.TestCase):
    def page(self, declared):
        try:
            Libraries(library_dirs()).load('Device:R')
        except ValueError:
            self.skipTest('KiCad symbol libraries are not installed')
        i = {'schema_version': 1, 'design_id': 'edge', 'title': 'edge',
             'components': [{'ref': 'R1', 'lib_id': 'Device:R', 'value': '10k', 'footprint': ''}],
             'nets': [{'name': 'EN_N1', 'pins': ['R1.1']}, {'name': 'ADC1', 'pins': ['R1.2']}], 'no_connect': []}
        if declared:
            i['boundary_nets'] = [{'net': n, 'to': 'MCU 板', 'contract': 'c.md'} for n in ('EN_N1', 'ADC1')]
        s = Sheet(i, rails={})
        s.put('R1', '1', (50.8, 50.8), DOWN)
        s.label('R1.1', 'global', length=2)
        s.label('R1.2', 'global', length=2)
        return i, s

    def test_sheet_plans_a_global_label_for_a_declared_net_only(self):
        _, s = self.page(True)
        self.assertEqual('global', s.plan['nets']['EN_N1'])
        _, s = self.page(False)
        self.assertIsNone(s.plan['nets']['EN_N1'])

    @unittest.skipUnless(find_cli(), 'KiCad CLI absent')
    def test_native_erc_waives_the_declared_single_label(self):
        for declared in (True, False):
            i, s = self.page(declared)
            root, report = s.build('edge', draft=not declared)
            with tempfile.TemporaryDirectory() as d, self.subTest(declared=declared):
                path = Path(d) / 'edge.kicad_sch'
                path.write_text(dump(root) + '\n', encoding='utf-8')
                (Path(d) / 'edge.kicad_pro').write_text(json.dumps(project_settings()) + '\n')
                erc = verify(path, i, None, Path(d) / 'native')['erc']
                if declared:
                    self.assertEqual('PASS', erc['status'], erc)
                    self.assertEqual({('single_global_label', 'EN_N1'), ('single_global_label', 'ADC1'),
                                      ('isolated_pin_label', 'EN_N1'), ('isolated_pin_label', 'ADC1')},
                                     {(w['type'], n) for w in erc['boundary_waived'] for n in w['nets']})
                else:
                    self.assertEqual('FAIL', erc['status'])
                    self.assertEqual({'single_global_label', 'isolated_pin_label'}, {v['type'] for v in erc['violations']})


if __name__ == '__main__':
    unittest.main()
