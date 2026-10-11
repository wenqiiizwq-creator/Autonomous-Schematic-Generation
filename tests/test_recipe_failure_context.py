"""Failure locations must support repair while preserving rejection boundaries."""
import copy,os,sys,unittest
from pathlib import Path
ROOT=Path(os.environ.get('ASG_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
from schematic_layout.recipes import Sheet,RIGHT,LEFT
SEGMENTS=[('SIGNAL',(0.,0.),(1.27,0.)),('SIGNAL',(12.7,0.),(13.97,0.))]
PINS={'J1.1':((0.,0.),RIGHT),'R1.1':((1.27,0.),LEFT),'R2.1':((12.7,0.),RIGHT),'U1.1':((13.97,0.),LEFT)}
def sheet(labels=(),powers=()):
    s=object.__new__(Sheet);s.nets={p:'SIGNAL' for p in PINS};s.pins=copy.deepcopy(PINS)
    s.labels=list(labels);s.powers=list(powers);s.flags=[]
    return s
class RecipeFailureContext(unittest.TestCase):
    def test_missing_piece_error_locates_actual_unmarked_pins(self):
        s=sheet([{'net':'SIGNAL','at':(0.,0.)}])
        with self.assertRaises(ValueError) as caught:s._check_connected(SEGMENTS)
        message=str(caught.exception)
        for value in ('SIGNAL','R2.1','U1.1','label','rail'):self.assertIn(value,message)
    def test_wire_only_unmarked_piece_has_coordinates(self):
        s=sheet([{'net':'SIGNAL','at':(0.,0.)},{'net':'SIGNAL','at':(12.7,0.)}])
        with self.assertRaises(ValueError) as caught:s._check_connected(SEGMENTS+[('SIGNAL',(25.4,0.),(26.67,0.))])
        self.assertIn('25.4',str(caught.exception))
    def test_declared_rail_name_is_still_rejected_with_repair_context(self):
        s=object.__new__(Sheet);s.nets={'R1.2':'GND'};s.rails={'GND':'power:GND'}
        with self.assertRaises(ValueError) as caught:s._rail('R1.2','GND')
        for value in ('R1.2','GND','power:','rail=True'):self.assertIn(value,str(caught.exception))
    def test_continuous_unlabelled_net_still_accepted(self):
        sheet()._check_connected(SEGMENTS+[('SIGNAL',(1.27,0.),(12.7,0.))])
    def test_both_labelled_pieces_still_accepted(self):
        sheet([{'net':'SIGNAL','at':(0.,0.)},{'net':'SIGNAL','at':(12.7,0.)}])._check_connected(SEGMENTS)
    def test_detached_or_different_net_label_cannot_name_missing_piece(self):
        for label in ({'net':'SIGNAL','at':(25.4,0.)},{'net':'OTHER','at':(12.7,0.)}):
            with self.subTest(label=label),self.assertRaises(ValueError):
                sheet([{'net':'SIGNAL','at':(0.,0.)},label])._check_connected(SEGMENTS)
    def test_unwired_physical_pin_still_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unwired pins'):
            sheet([{'net':'SIGNAL','at':(0.,0.)}])._check_connected(SEGMENTS[:1])

if __name__=='__main__':unittest.main()
