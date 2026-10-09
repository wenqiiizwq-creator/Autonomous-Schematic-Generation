"""The standalone gate accepts both documented net forms, preserving contacts."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(os.environ.get('ASG_ROOT',Path(__file__).resolve().parents[1]))


class GeometryIntentCliTests(unittest.TestCase):
    def invoke(self, nets):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp); sch=base/'fixture.kicad_sch'; out=base/'geometry.json'
            sch.write_text('''(kicad_sch (paper "A4") (lib_symbols
              (symbol "Test:X" (symbol "X_0_0" (rectangle (start 0 -2) (end 4 2) (stroke (width 0.1))))
                (symbol "X_1_1" (pin passive line (at -2.54 0 0) (length 2.54) (number "1") (name "A")))))
              (symbol (lib_id "Test:X") (at 50.8 50.8 0) (unit 1) (property "Reference" "R1" (at 50.8 45.72 0) (effects hide)))
              (symbol (lib_id "Test:X") (at 60.96 50.8 0) (unit 1) (property "Reference" "R2" (at 60.96 45.72 0) (effects hide)))
              (wire (pts (xy 48.26 50.8) (xy 58.42 50.8))))''')
            intent=base/'intent.json';intent.write_text(json.dumps({'components':[],'nets':nets}))
            cp=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/check_schematic_geometry.py'),str(sch),'--intent',str(intent),'--output',str(out)],capture_output=True,text=True)
            return cp,json.loads(out.read_text()) if out.exists() else None
    def test_dict_and_list_membership_have_identical_reports(self):
        a, ar=self.invoke({'A':['R1.1'],'B':['R2.1']})
        b, br=self.invoke([{'name':'A','pins':['R1.1']},{'name':'B','pins':['R2.1']}])
        self.assertEqual(2,a.returncode,a.stderr)
        self.assertEqual((a.returncode,ar),(b.returncode,br))
        self.assertTrue(ar['coverage']['pin_net_intent_checked'])
        self.assertTrue(any(x['code']=='different_net_contact' for x in ar['findings']))
    def test_same_net_contact_is_not_different_net_contact(self):
        cp, report=self.invoke({'A':['R1.1','R2.1']})
        self.assertIsNotNone(report,cp.stderr)
        self.assertFalse(any(x['code']=='different_net_contact' for x in report['findings']))
    def test_duplicate_pin_membership_is_rejected_with_actionable_message(self):
        cp, report=self.invoke({'A':['R1.1'],'B':['R1.1']})
        self.assertIsNone(report)
        self.assertNotEqual(0,cp.returncode)
        self.assertIn('Pin assigned to multiple nets',cp.stderr)
        self.assertNotIn('TypeError',cp.stderr)


if __name__=='__main__':unittest.main()
