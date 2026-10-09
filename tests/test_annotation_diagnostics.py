"""Report rejected annotation provenance without borrowing its identity."""
import os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(os.environ.get('ASG_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
from schematic_layout.project_audit import audit_project
from schematic_layout.native_hierarchy import NativeHierarchy


class AnnotationDiagnosticsTests(unittest.TestCase):
    def report(self, project='old', declared_unit=1):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        p=Path(self.temp.name)/'board.kicad_sch'
        p.write_text(f'''(kicad_sch (version 20250114) (uuid "root")
           (symbol (uuid "symbol-uuid") (lib_id "Test:Cached") (unit {declared_unit})
             (property "Reference" "U7") (instances (project "{project}"
              (path "/root" (reference "U99") (unit 1))))))''')
        return audit_project(p),NativeHierarchy(p)
    def test_missing_selection_has_precise_uuid_and_available_project(self):
        report,ctx=self.report()
        gap=report['missing_symbol_annotations'][0]
        self.assertEqual(('board.kicad_sch','/root','symbol-uuid','board'),
             (gap['file'],gap['instance'],gap['symbol_uuid'],gap['selected_project']))
        self.assertEqual('U7',gap['non_authoritative_reference_property'])
        self.assertEqual([{'project':'old','paths':['/root']}],gap['available_local_contexts'])
        self.assertEqual(0,report['component_count'])
        self.assertEqual({},ctx.symbol_contexts)
        self.assertEqual('INSUFFICIENT',report['status'])
    def test_empty_project_is_diagnostic_not_fallback(self):
        report,ctx=self.report('')
        self.assertEqual('',report['missing_symbol_annotations'][0]['available_local_contexts'][0]['project'])
        self.assertFalse(ctx.symbol_contexts)
    def test_valid_selection_has_no_missing_symbol_diagnostic(self):
        report,ctx=self.report('board')
        self.assertEqual([],report['missing_symbol_annotations'])
        self.assertEqual({'U99'}, {c['reference'] for c in ctx.symbol_contexts.values()})
    def test_declared_unit_is_evidence_not_selected_annotation(self):
        report,ctx=self.report(declared_unit=2)
        self.assertEqual('2',report['missing_symbol_annotations'][0]['declared_unit'])
        self.assertFalse(ctx.symbol_contexts)


if __name__=='__main__':unittest.main()
