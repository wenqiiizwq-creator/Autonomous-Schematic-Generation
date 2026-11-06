"""The derating spec (I/II/III levels from T/CPSS 1013, GJB/Z 35 and T/CPSS 1006) is one file shared with
schematic-review (references/shared, validated locally by test_installed_release): every rule names a known kind,
a measure, a condition and a cited page, and the levels run from most to least derating (user 2026-10-27)."""
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from schematic_layout import part_classes as pc

JSON_PATH = ROOT / 'references' / 'shared' / 'derating-rules.json'
MD_PATH = ROOT / 'references' / 'shared' / 'derating-rules.md'
import guideline_criteria
LIBRARY = Path.home() / 'Documents' / '知识库' / 'HardwareWiki'
SPEC = json.loads(JSON_PATH.read_text(encoding='utf-8'))
LEVELS = ('I', 'II', 'III')
# Direction of each measure from level I to level III: less derating allows a larger ratio or temperature and asks a
# smaller margin or life.
RISING = {'ratio', 'pulse_ratio', 'tj_percent', 'max_c', 'max_rise_k', 'max_v'}
FALLING = {'margin_c', 'min_hours', 'min_years'}


class DeratingSpecTests(unittest.TestCase):
    def test_header(self):
        self.assertEqual(SPEC['levels'], list(LEVELS))
        # NB/T 10297 is cited for comparison only and gives no default value (derating-rules.md, NB/T 10297 的差异).
        self.assertEqual(sorted(SPEC['priority']), sorted(set(SPEC['sources']) - {'nbt10297'}))
        self.assertEqual(SPEC['priority'][0], 'cpss1013')
        self.assertTrue({r['source'] for r in SPEC['rules']} <= set(SPEC['priority']))

    def test_every_rule_is_well_formed(self):
        kinds = set(pc.KINDS) | set(SPEC['extra_kinds'])
        for rule in SPEC['rules']:
            rid = rule['id']
            self.assertTrue(set(rule['kinds']) <= kinds, rid)
            self.assertIn(rule['measure'], SPEC['measures'], rid)
            self.assertIn(rule['condition'], SPEC['conditions'], rid)
            source = SPEC['sources'][rule['source']]
            self.assertTrue(1 <= rule['page'] <= source['pages'], rid)
            self.assertEqual(tuple(rule['values']), LEVELS, rid)
            numeric = all(isinstance(v, (int, float)) for v in rule['values'].values())
            self.assertEqual(numeric, rule['measure'] != 'text', rid)

    def test_a_kind_holding_several_technologies_names_each_rules_subtype(self):
        # R7: silicon MOS, IGBT, GaN and SiC share the mosfet kind, a crystal and an oscillator the crystal kind.
        for rule in SPEC['rules']:
            mixed = [k for k in rule['kinds'] if k in SPEC['subtypes']]
            if mixed:
                self.assertIn(rule.get('subtype'), SPEC['subtypes'][mixed[0]], rule['id'])
            else:
                self.assertNotIn('subtype', rule, rule['id'])

    def test_ids_are_unique_and_one_rule_per_type_parameter_condition(self):
        ids = [r['id'] for r in SPEC['rules']]
        self.assertEqual(len(ids), len(set(ids)))
        keys = [(r['type'], r['parameter'], r['condition']) for r in SPEC['rules']]
        self.assertEqual(sorted(k for k in set(keys) if keys.count(k) > 1), [])

    def test_an_ungraded_source_gives_one_value_for_all_levels(self):
        for rule in SPEC['rules']:
            if not SPEC['sources'][rule['source']]['graded']:
                self.assertEqual(len(set(map(str, rule['values'].values()))), 1, rule['id'])

    def test_levels_run_from_most_to_least_derating(self):
        for rule in SPEC['rules']:
            v = [rule['values'][k] for k in LEVELS]
            if rule['measure'] in RISING:
                self.assertEqual(v, sorted(v), rule['id'])
            elif rule['measure'] in FALLING:
                self.assertEqual(v, sorted(v, reverse=True), rule['id'])

    def test_the_document_lists_every_rule(self):
        listed = re.findall(r'^\| ([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+) \|', MD_PATH.read_text(encoding='utf-8'), flags=re.M)
        self.assertEqual(sorted(listed), sorted(r['id'] for r in SPEC['rules']))

    @unittest.skipUnless((LIBRARY / 'raw' / 'Standard').is_dir(), 'HardwareWiki not installed')
    def test_sources_are_the_library_files(self):
        for key, source in SPEC['sources'].items():
            path = LIBRARY / source['path']
            self.assertTrue(path.is_file(), source['path'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source['sha256'], key)

    def test_engineering_values_live_in_the_rule_library(self):
        # Values the standards do not give (user 2026-10-29: SOA 段系数并入降额规范；等级未定按 I 级) moved into the rule
        # library on 2026-11-02 (user: 迁进设计准则库): the derating table holds none, its document points at the library.
        self.assertNotIn('engineering_values', SPEC)
        values = guideline_criteria.load()['engineering_values']
        self.assertEqual(values['unset_level']['value'], 'I')
        self.assertEqual(values['soa_segment_share']['value'], {'CONSTANT_POWER': 1.0, 'THERMAL_INSTABILITY': 0.8})
        text = MD_PATH.read_text(encoding='utf-8')
        for name in ('unset_level', 'soa_segment_share', 'thermal_calc_trigger'):
            self.assertRegex(values[name]['confirmed'], r'^user:\d{4}-\d{2}-\d{2}', name)
            self.assertIn('`%s`' % name, text)
        self.assertNotRegex(text, r'(?m)^\| `unset_level` \|')

    def test_a_missing_capacitor_voltage_is_chosen_by_the_spec(self):
        # 2026-10-29 (user: 类似这种单一的规则，都先不要，全都并入到降额规范里面去): no 1.5–2× rule of thumb
        text = (ROOT / 'references' / 'pdf-schematic-extraction.md').read_text(encoding='utf-8')
        line = next(l for l in text.splitlines() if '电容没写耐压' in l)
        self.assertNotRegex(line, r'\d\s*倍')
        self.assertIn('CAP-MLCC-CHIP-V', line)
        self.assertIn('unset_level', line)

    def test_the_thermal_calculation_trigger_is_the_spec_value(self):
        # 2026-10-29 (user: 这些也都处理): when to estimate junction temperature is named in the spec, not in the text
        self.assertEqual(guideline_criteria.engineering_value('thermal_calc_trigger'), {'power_w': 0.3, 'rating_share': 0.5})
        text = (ROOT / 'references' / 'requirements-to-intent.md').read_text(encoding='utf-8')
        self.assertIn('thermal_calc_trigger', text)
        self.assertNotIn('0.3 W', text)



if __name__ == '__main__':
    unittest.main()
