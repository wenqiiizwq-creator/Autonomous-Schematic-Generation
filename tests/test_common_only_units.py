"""Generic common-only unit regressions; no third-party circuit fixture."""
import copy, os, sys, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(os.environ.get('ASG_ROOT',Path(__file__).resolve().parents[1]));sys.path.insert(0,str(ROOT/'scripts'))
from schematic_layout.generate import make_root, Libraries
from schematic_layout.scene import read_scene
from schematic_layout.sexpr import parse, all_nodes, first, value

def lib(unit=0, style=1, pin=True):
    p='(pin passive line (at -2.54 0 0) (length 2.54) (name "A") (number "1"))' if pin else ''
    if unit==0 and style==0:
        return parse(f'''(symbol "Synthetic:Probe" (property "Reference" "U")
          (symbol "Probe_0_0" (rectangle (start 0 -2.54) (end 5.08 2.54) (stroke (width 0.254))) {p}))''')
    return parse(f'''(symbol "Synthetic:Probe" (property "Reference" "U")
      (symbol "Probe_0_0" (rectangle (start 0 -2.54) (end 5.08 2.54) (stroke (width 0.254))))
      (symbol "Probe_{unit}_{style}" {p}))''')

class CommonOnlyUnits(unittest.TestCase):
    def build(self, symbol, units=None, no_connect=None):
        c={'ref':'U1','lib_id':'Synthetic:Probe','value':'Probe'}
        if units is not None:c['units']=units
        i={'schema_version':1,'components':[c],'nets':[], 'no_connect':['U1.1'] if no_connect is None else no_connect}
        l={'schema_version':1,'placements':{'U1':{'at':[50.8,50.8]}}}
        if units is not None and units!=[1]:l['placements']={f'U1:{u}':{'at':[50.8,50.8]} for u in units}
        with patch.object(Libraries,'load',return_value=copy.deepcopy(symbol)):
            return make_root(i,l,'common_only')
    def test_common_only_physical_pins_use_implicit_unit_one(self):
        root,*_=self.build(lib());scene=read_scene(root)
        self.assertEqual([p.id for s in scene.symbols for p in s.pins],['U1.1'])
        self.assertEqual(value(all_nodes(root,'symbol')[0],'unit'),1)
        # Original cached common-unit geometry survives, no renumbering.
        cache=all_nodes(first(root,'lib_symbols'),'symbol')[0]
        self.assertTrue(any(str(s[1])=='Probe_0_1' for s in all_nodes(cache,'symbol')))
    def test_common_body_style_zero_physical_pins(self):
        self.build(lib(style=0))
    def test_common_only_still_requires_complete_pin_intent(self):
        with self.assertRaisesRegex(ValueError,'Pin coverage mismatch'):
            self.build(lib(),no_connect=[])
    def test_common_graphics_without_physical_pins_not_inferred(self):
        with self.assertRaisesRegex(ValueError,'multi-unit'):
            self.build(lib(pin=False),no_connect=[])
    def test_alternate_style_only_not_qualified_for_default_style(self):
        with self.assertRaisesRegex(ValueError,'multi-unit'):
            self.build(lib(style=2))
    def test_explicit_unknown_unit_not_inferred(self):
        with self.assertRaisesRegex(ValueError,'multi-unit'):
            self.build(lib(),units=[2])
    def test_positive_unit_contract_remains_complete(self):
        symbol=lib(unit=2)
        with self.assertRaisesRegex(ValueError,'multi-unit'):
            self.build(symbol)
    def test_existing_positive_unit_one_still_builds(self):
        self.build(lib(unit=1))
    def test_true_multiunit_complete_views_are_not_flattened(self):
        symbol=lib(unit=1)
        extra=copy.deepcopy(all_nodes(symbol,'symbol')[-1]);extra[1]='Probe_2_1'
        first(all_nodes(extra,'pin')[0],'number')[1]='2';symbol.append(extra)
        c={'ref':'U1','lib_id':'Synthetic:Probe','value':'Probe','units':[1,2]}
        i={'schema_version':1,'components':[c],'nets':[],'no_connect':['U1.1','U1.2']}
        l={'schema_version':1,'placements':{'U1:1':{'at':[50.8,50.8]},'U1:2':{'at':[76.2,50.8]}}}
        with patch.object(Libraries,'load',return_value=copy.deepcopy(symbol)):
            root,*_=make_root(i,l,'multiunit')
        self.assertEqual([value(s,'unit') for s in all_nodes(root,'symbol')],[1,2])
        self.assertEqual([p.id for s in read_scene(root).symbols for p in s.pins],['U1.1','U1.2'])

if __name__=='__main__':unittest.main()
