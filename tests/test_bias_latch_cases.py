"""Synthetic review cases; no delivered schematic or vendor PDF fixture."""
import unittest,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ReviewedCases(unittest.TestCase):
 def test_line_threshold_must_cover_legal_corner(self):
  divider=lambda bottom:264*math.sqrt(2)*bottom/(6e6+bottom)
  self.assertLess(divider(24900),1.65)
  self.assertGreater(divider(46400*.99)/(1.01),1.95)
 def test_ceramic_is_not_film(self):
  required={'dielectric':'ceramic','effective_F':2.2e-6}
  film={'dielectric':'film','effective_F':2.2e-6}
  self.assertNotEqual(film['dielectric'],required['dielectric'])
 def test_local_output_is_separate_from_external_sr_cap(self):
  nets={'REG':{'LDO.OUT','COUT.1','D.A'},'SR':{'D.K','SR.VCC','CSR.1'}}
  self.assertTrue(nets['REG'].isdisjoint(nets['SR']))
  self.assertIn('COUT.1',nets['REG'])
 def test_exact_order_tolerance_interval(self):
  low,high=75*.95,75*1.05
  self.assertEqual((low,high),(71.25,78.75))
 def test_mov_prefix_needs_specific_identity(self):
  identity=lambda r:'varistor' if r.startswith('RV') else 'resistor'
  self.assertEqual(identity('RV101'),'varistor')
 def test_published_implementations_and_origins(self):
  # 知识包 1.0.0：原条目拆分成指路条目，四种方案并入别的典型电路，原审查案例写在“内容去向”。
  folder=ROOT/'references/knowledge/典型电路'
  text=(folder/'reviewed-bias-and-latch.md').read_text()
  for key in ['F-001','F-005','F-006']:self.assertIn(key,text)
  self.assertEqual(sum(l.startswith('### ') for l in text.splitlines()),0)
  for target in ['aux-bias-supply','ac-indicator','aux-overvoltage-latch','ldo']:
   self.assertIn('](%s.md)'%target,text); self.assertTrue((folder/(target+'.md')).is_file())
