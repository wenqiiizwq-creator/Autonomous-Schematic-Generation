"""Key and special parts carry an MPN, a datasheet and a kind declaration; common parts carry their ratings; a cited
datasheet is the part's own (R7: 21 parts unnamed; P3 aligned with schematic-review, user 2026-10-26)."""
import framework_required  # noqa: F401  没配知识框架时本模块整个跳过
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from schematic_layout import part_classes as pc

BXW = 'Datasheet/20_电容器/铝电解电容/Rubycon - BXW.pdf'
PAGE = ('SMBJ series 600 W surface mount transient voltage suppressor. Unidirectional TVS, peak pulse power 600 W. '
        'Replaces Zener diode clamps. ') * 2


def part(ref, lib, value='', mpn='', datasheet='', **fields):
    return {'ref': ref, 'lib_id': lib, 'value': value, 'mpn': mpn, 'datasheet': datasheet, 'fields': fields}


def declared(ref, lib, kind, quote, value='', mpn='X', datasheet='SMBJ24A.pdf', **fields):
    return part(ref, lib, value, mpn, datasheet, Kind=kind, KindSource='datasheet:SMBJ24A.pdf#p1', KindQuote=quote, **fields)


PD_NETS = {'L_IN': ['J101.1', 'F101.1'], 'L_F': ['F101.2', 'TH101.1'], 'L_NTC': ['TH101.2', 'RV101.1'],
           'VBUS': ['J701.1', 'TH701.1'], 'VBUS_P': ['TH701.2', 'Q701.1'], 'NTC_SENSE': ['TH601.1', 'U601.3'],
           'SGND': ['TH601.2', 'K1.1']}
PD = {'nets': PD_NETS, 'net_roles': {'VBUS': 'power', 'VBUS_P': 'power', 'SGND': 'return', 'NTC_SENSE': 'signal'},
      'high_voltage_nets': ['L_IN', 'L_F', 'L_NTC']}


class ClassTests(unittest.TestCase):
    def test_level_follows_kind_and_position(self):
        ctx = pc.context(PD)
        cases = {
            'key': [part('U201', 'PD100:NCP1623'), part('Q701', 'PD100:NTMFS5C604NL'), part('T301', 'PD100:Transformer'),
                    part('D712', 'PD100:D_TVS_Uni'), part('BR101', 'PD100:GBU4M'), part('D405', 'Device:D', 'BZT52H-B18'),
                    part('L201', 'Device:L', DesignSheet='设计资料/L201.md')],
            'special': [part('F101', 'Device:Fuse'), part('RV101', 'Device:Varistor'), part('CX101', 'Device:C'),
                        part('C305', 'Device:C', '1n/Y1/400Vac'), part('J101', 'Connector_Generic:Conn_01x02'),
                        part('TH101', 'Device:Thermistor_NTC'), part('TH701', 'Device:Thermistor_NTC')],
            'common': [part('D302', 'Device:D_Schottky'), part('D101', 'Device:LED'), part('C201', 'Device:C_Polarized'),
                       part('L401', 'Device:L'), part('L101', 'PD100:CMC'), part('J701', 'Connector:USB_C_Receptacle_USB2.0_16P'),
                       part('TH601', 'Device:Thermistor_NTC'), part('K1', 'Relay:G5V-1'), part('R303', 'Device:R'),
                       part('C101', 'Device:C'), part('TP601', 'Connector:TestPoint'), part('Y1', 'Device:Crystal'),
                       part('BT1', 'Device:Battery_Cell')]}
        for level, parts in cases.items():
            for p in parts:
                self.assertEqual(level, pc.part_class(p, ctx), p['ref'])

    def test_without_high_voltage_nets_connectors_relays_and_ntcs_are_special(self):
        ctx = pc.context({'nets': PD_NETS})
        for p in (part('J701', 'Connector:USB_C_Receptacle_USB2.0_16P'), part('K1', 'Relay:G5V-1'),
                  part('TH601', 'Device:Thermistor_NTC')):
            self.assertEqual('special', pc.part_class(p, ctx), p['ref'])

    def test_kind_from_symbol_and_part_number_before_the_prefix(self):
        # Scan of 20 public KiCad projects: MPN-named project symbols and unlisted kinds.
        cases = {'mosfet': [part('AH2', 'Device:Q_NMOS_SGD'), part('Q3', 'Transistor_FET:2N7002')],
                 'bjt': [part('T5', 'tesla_smps-rescue:Q_NPN_EBC')], 'transformer': [part('Tr1', 'tesla_smps-rescue:Transformer')],
                 'ic': [part('REF1', 'Reference_Voltage:TL431LP'), part('A1', 'MCU_Module:Arduino_Nano_v3.x'),
                        part('Module1', 'CM5IO:ComputeModule5-CM5'), part('U4', 'Interface_USB:CP2102N-A01-GQFN28')],
                 'tvs': [part('D1', 'Power_Protection:PRTR5V0U2X'), part('D29', 'Diode:SMF54A')],
                 'diode': [part('D21', 'Diode:1N4148WT'), part('D33', 'MotorBuck:WS2812B')],
                 'crystal': [part('Y1', 'Device:Crystal_GND24'), part('X1', 'Oscillator:TXC-7C')],
                 'fuse': [part('F1', 'Device:Polyfuse')], 'ferrite': [part('FB2', 'Device:FerriteBead')],
                 'inductor': [part('FL1', 'tesla_smps-rescue:F_CHOKE')], 'connector': [part('J10', 'HR911105A:HR911105A')],
                 'relay': [part('K20', 'Relay:FINDER-40.41')], 'battery': [part('BT1', 'Device:Battery_Cell')],
                 'varistor': [part('RV2', 'Device:Varistor')], 'ntc': [part('R9', 'Device:Thermistor_NTC')],
                 'capacitor': [part('C4', 'Device:CP_Small')], 'resistor': [part('RV3', 'Device:R_Potentiometer_Trim')],
                 'switch': [part('SW1', 'Switch:SW_Push'), part('K32', 'keyboard_parts:KEYSW')],
                 'jumper': [part('JP1', 'Jumper:SolderJumper_2_Open')], 'testpoint': [part('TP3', 'otter:test-pad-1')],
                 'mechanical': [part('H1', 'Mechanical:MountingHole_Pad'), part('FID1', 'Mechanical:Fiducial')],
                 None: [part('BZ1', 'Device:Buzzer'), part('AE1', 'otter:KH-5220-A56_U.FL')]}
        for kind, parts in cases.items():
            for p in parts:
                self.assertEqual(kind, pc.kind_of(p)[0], p['ref'])
        self.assertIsNone(pc.part_class(part('BZ1', 'Device:Buzzer')))

    def test_a_declaration_against_the_symbol_is_a_problem(self):
        self.assertIn('不一致', pc.kind_of(part('D1', 'Device:D_TVS', Kind='diode'))[1])
        self.assertEqual(('tvs', None), pc.kind_of(part('D1', 'Device:D', Kind='tvs')))
        self.assertIn('不是器件类型', pc.kind_of(part('D1', 'Device:D', Kind='suppressor'))[1])

    def test_kind_vocabulary_is_the_framework_vocabulary(self):
        # names and titles come from the framework's 词表.json, not from SR's code
        import json
        import knowledge_source
        shared = json.loads(knowledge_source.vocabulary_path().read_text(encoding='utf-8'))['device_kinds']
        self.assertEqual({x['name'] for x in shared}, set(pc.KINDS) - {'mechanical'})
        for item in shared:
            self.assertEqual(pc.KINDS[item['name']].title, item['title'], item['name'])

    def test_kind_cues_have_explicit_local_expectations(self):
        # Classification evidence has independent, named examples; no other skill defines the answer.
        expected = {
            'relay': ('relay',), 'varistor': ('varistor', 'siov'),
            'ntc': ('ntcthermistor', 'thermistor', 'inrushcurrentlimiter'),
            'opto': ('optocoupler', 'photocoupler', 'optoisolator', 'opticallycoupled', 'opticalisolator', 'opticalcoupler'),
            'tvs': ('tvs', 'esdprotection', 'transientvoltagesuppress', 'transientsuppress', 'surgeprotectiondevice'),
            'zener': ('zener',), 'bjt': ('npn', 'pnp', 'bipolar'),
            'mosfet': ('mosfet', 'nchannel', 'pchannel', 'superjunction'), 'diode': ('rectifier', 'diode', 'schottky'),
            'common_mode_choke': ('commonmodechoke', 'commonmodefilter', 'commonmodeinductor', 'commonmodecoil'),
            'coupled_inductor': ('coupledinductor',), 'ferrite': ('ferrite', 'bead'),
            'transformer': ('transformer',), 'fuse': ('fuse', 'pptc'),
            'connector': ('connector', 'receptacle', 'terminalblock'), 'bridge_rectifier': ('bridgerectifier',),
            'inductor': (), 'crystal': (), 'battery': (), 'testpoint': (), 'resistor': (), 'capacitor': (),
            'jumper': (), 'switch': (), 'ic': ()}
        self.assertEqual(set(expected), set(pc.KINDS) - {'mechanical'})
        for name, cues in expected.items():
            self.assertLessEqual(set(cues), set(pc.KINDS[name].cues), name)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        (self.root / 'SMBJ24A.pdf').write_bytes(b'%PDF smbj')
        (self.root / 'T301设计单.md').write_text('ETD39 N87 56:7:21')
        for target, value in (('library_present', True), ('check', {'status': 'PASS', 'reason': '', 'unshown': []}),
                              ('page_text', PAGE)):
            patcher = mock.patch.object(pc, target, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.dir.cleanup)

    def intent(self):
        return {'nets': PD_NETS, 'high_voltage_nets': ['L_IN'], 'components': [
            part('C201', 'Device:C_Polarized', '120u'),
            part('D712', 'PD100:D_TVS_Uni', 'SMBJ24A', mpn='SMBJ24A-E3/52', datasheet='SMBJ24A.pdf'),
            part('CX101', 'Device:C', '220n/X2/310Vac'),
            part('T301', 'PD100:Transformer', '300uH 56:7:21', mpn='R7-ETD39', DesignSheet='T301设计单.md'),
            part('L201', 'Device:L', '300uH'),
            part('D302', 'Device:D_Schottky', 'BAT54'),
            part('R303', 'Device:R', '0R30', Specification='1%/1W'),
            part('BZ1', 'Device:Buzzer', 'Buzzer'),
            declared('D706', 'PD100:D_TVS_Uni', 'tvs', 'Unidirectional TVS', 'SMBJ24A')]}

    def refs(self, lines):
        return [line.split('（')[0].split(' ')[-1] for line in lines]

    def test_new_design_lists_every_incomplete_part_as_a_problem(self):
        problems, unchecked = pc.audit_identity(self.intent(), [self.root])
        self.assertEqual([], unchecked)
        self.assertEqual(['C201', 'D712', 'CX101', 'L201', 'BZ1'], self.refs(problems))
        self.assertIn('常规件 C201（120u）缺耐压', problems[0])
        self.assertIn('关键器件 D712（SMBJ24A）缺类型声明', problems[1])
        self.assertIn('特殊器件 CX101（220n/X2/310Vac）缺料号（mpn）、数据手册（datasheet）、类型声明', problems[2])
        self.assertIn('缺额定电流', problems[3])
        self.assertIn('器件类型（认不出，写 fields.Kind', problems[4])

    def status(self, kind, quote, lib='PD100:D_TVS_Uni'):
        return pc.verify_declaration(declared('D706', lib, kind, quote), kind, [self.root], True)[0]

    def test_declarations_get_schematic_reviews_statuses(self):
        self.assertEqual('VERIFIED', self.status('tvs', 'Unidirectional TVS'))
        self.assertEqual('QUOTE_NOT_FOUND', self.status('tvs', 'Bidirectional TVS 400 W'))
        # A Zener or TVS quote is not evidence for a plain diode, and naming a second kind is a conflict.
        self.assertEqual('QUOTE_LACKS_TYPE', self.status('tvs', 'Replaces Zener diode clamps'))
        self.assertEqual('QUOTE_LACKS_TYPE', self.status('diode', 'Unidirectional TVS', 'Device:D'))
        self.assertEqual('QUOTE_CONFLICT', self.status('tvs', 'Unidirectional TVS, peak pulse power 600 W. Replaces Zener diode'))
        problems = pc.audit_identity({'nets': {}, 'components': [declared('D706', 'PD100:D_TVS_Uni', 'tvs', 'Bidirectional TVS')]},
                                     [self.root])[0]
        self.assertIn('QUOTE_NOT_FOUND', problems[0])

    def test_a_page_without_text_is_listed_not_passed_or_blocked(self):
        with mock.patch.object(pc, 'page_text', return_value=''):
            problems, unchecked = pc.audit_identity(
                {'nets': {}, 'components': [declared('D706', 'PD100:D_TVS_Uni', 'tvs', 'Unidirectional TVS')]}, [self.root])
        self.assertEqual([], problems)
        self.assertEqual(1, len(unchecked))
        self.assertIn('取不出文字', unchecked[0])

    def test_short_cues_are_whole_words(self):
        self.assertEqual(set(), pc.cues('Thermally controlled; remove the cover'))
        self.assertEqual({'diode'}, pc.cues('Red LED, 0603'))
        self.assertEqual({'mosfet'}, pc.cues('N-ChannelMOSFET'))

    def test_fuses_and_relays_named_by_an_ic_or_a_thermistor_are_not_the_part(self):
        # schematic-review 2026-10-27: a kind is what the part does at its pins, not what is inside it.
        self.assertEqual(set(), pc.cues('Littelfuse Inc.'))
        self.assertEqual({'fuse'}, pc.cues('Surface mount fuses'))
        self.assertEqual({'fuse'}, pc.cues('PPTC resettable device'))
        self.assertEqual(set(), pc.cues('Industrial eFuse with integrated N-channel MOSFET'))
        self.assertEqual({'varistor'}, pc.cues('Metal oxide varistor, ThermoFuse types'))
        self.assertEqual(set(), pc.cues('Low-side relay driver'))
        self.assertEqual({'fuse'}, pc.cues('Industrial eFuse', specific=False) & {'fuse'})

    def test_multi_winding_magnetics_by_what_they_do(self):
        self.assertEqual({'common_mode_choke'}, pc.cues('SMD Common Mode Filter'))
        self.assertEqual({'coupled_inductor'}, pc.cues('Coupled Inductor'))
        cmc = part('L101', 'PD100:Common_Mode_Choke', '10mH')
        self.assertEqual('common_mode_choke', pc.kind_of(cmc)[0])
        self.assertEqual('coupled_inductor', pc.kind_of(part('L3', 'PD100:Coupled_Inductor'))[0])
        self.assertEqual('inductor', pc.kind_of(part('FL1', 'tesla_smps-rescue:F_CHOKE'))[0])
        # Declared on an inductor symbol it refines the symbol; with a design sheet it is a custom magnetic.
        self.assertIsNone(pc.kind_of(declared('L5', 'Device:L', 'common_mode_choke', 'Common mode choke'))[1])
        self.assertEqual('key', pc.part_class(part('L101', 'PD100:Common_Mode_Choke', DesignSheet='设计资料/L101.md')))
        self.assertEqual('common', pc.part_class(cmc))
        problems = pc.audit_identity({'nets': {}, 'components': [cmc]}, [self.root])[0]
        self.assertIn('额定电流', problems[0])

    def test_the_declaration_cites_the_parts_own_datasheet(self):
        comp = declared('D706', 'PD100:D_TVS_Uni', 'tvs', 'Unidirectional TVS')
        comp['fields']['KindSource'] = 'datasheet:Datasheet/23_分立半导体/TVS/Littelfuse - SMAJ.pdf#p1'
        self.assertIn('不是同一份', pc.audit_identity({'components': [comp]}, [self.root])[0][0])

    def test_a_datasheet_that_is_nowhere_is_not_a_datasheet(self):
        intent = {'components': [declared('D706', 'PD100:D_TVS_Uni', 'tvs', 'Unidirectional TVS', datasheet='gone.pdf')]}
        self.assertIn('不在交付目录或知识库里', pc.audit_identity(intent, [self.root])[0][0])


class CitationTests(unittest.TestCase):
    def setUp(self):
        self.intent = {'components': [
            part('C201', 'Device:C_Polarized', mpn='450BXW120MEFR18X40', datasheet='/x/原厂资料/Rubycon-BXW.pdf'),
            part('C503', 'Device:C_Polarized', mpn='35PZJ330M10X9', datasheet='/x/原厂资料/Rubycon-PZJ.pdf'),
            part('C208', 'Device:C_Polarized', '100u/450V', datasheet='/x/原厂资料/Rubycon-BXW.pdf'),
            part('T301', 'PD100:Transformer', mpn='R7-ETD39', DesignSheet='设计资料/T301.md'),
            part('C206', 'Device:C', '10u/25V')]}

    def closure(self, params=(), gaps=()):
        return {'calculations': [{'id': 'C-LIFE', 'parameters': list(params)}],
                'work_items': [{'id': 'W-INPUT', 'missing': list(gaps)}]}

    def problems(self, **kw):
        return pc.audit_citations(self.intent, self.closure(**kw), [])

    def test_same_datasheet_under_another_file_name_binds(self):
        self.assertEqual([], self.problems(params=[{'name': '寿命', 'ref': 'C201', 'source': 'datasheet:%s#p1' % BXW}],
                                           gaps=[{'source': 'datasheet:%s#p1' % BXW, 'refs': ['C201']}]))

    def test_a_gap_that_cites_a_datasheet_names_its_parts(self):
        # R7 W-INPUT cited BXW and S3J without saying which parts; C201/C208 carried no datasheet.
        self.assertEqual(['待办 W-INPUT 的第 1 项资料缺口 引用了手册 %s，要写明它说的是哪个位号' % BXW],
                         self.problems(gaps=[{'source': 'datasheet:%s#p1' % BXW}]))

    def test_a_cited_datasheet_must_be_the_parts_own(self):
        found = self.problems(params=[{'name': '寿命', 'ref': 'C503', 'source': 'datasheet:%s#p1' % BXW}])
        self.assertEqual(1, len(found))
        self.assertIn('与设计网表里 C503 的 datasheet', found[0])

    def test_a_common_part_cited_for_a_datasheet_value_becomes_special(self):
        found = self.problems(params=[{'name': '有效电容', 'ref': 'C206', 'source': 'datasheet:Datasheet/20_电容器/X - GRM.pdf#p3'}])
        self.assertIn('C206 没有写 datasheet', found[0])
        # A lifetime calculated from the BXW series formula binds C208 to that series: it needs the exact MPN.
        found = self.problems(params=[{'name': '寿命', 'ref': 'C208', 'source': 'datasheet:%s#p1' % BXW}])
        self.assertIn('C208 因此是特殊器件，设计网表里要写它的 mpn', found[0])

    def test_standards_and_design_sheets_are_not_bound(self):
        self.assertEqual([], self.problems(
            params=[{'name': 'Bsat', 'ref': 'T301', 'source': 'datasheet:Datasheet/21_电感器与磁件/铁氧体磁芯/TDK - N87.pdf#p2'}],
            gaps=[{'source': 'datasheet:Standard/GB 4943.1 - 2022.pdf#p40'}]))


class KeywordTests(unittest.TestCase):
    def test_a_family_never_starts_inside_a_longer_part_number(self):
        # R7 U701 TPS26630RGER (eFuse) read as a PS25xx optocoupler; schematic-review reads it the same way.
        self.assertEqual('ic', pc.kind_of(part('U701', 'PD100:TPS26630RGER', 'TPS26630RGER'))[0])
        for p in (part('U2', 'x:PS2501-1'), part('U3', 'x:TLP291'), part('U4', 'x:X', 'LTV-817'), part('U5', 'x:SFH6186-4')):
            self.assertEqual('opto', pc.kind_of(p)[0], p['lib_id'])
        self.assertEqual('tvs', pc.kind_of(part('D2', 'x:X', 'SMBJ24A'))[0])
        self.assertEqual('zener', pc.kind_of(part('D3', 'Device:D', 'BZT52H-B18'))[0])


class TierTests(unittest.TestCase):
    # R6: R303 0.30 Ω 1 % 2 W exceeds the sense tier S4 (1 W); R403/R504/R604 are pulse resistors.
    def level(self, ref, lib, value, spec=''):
        p = part(ref, lib, value, Specification=spec)
        return pc.category(p)[0], pc.part_class(p, pc.context({'high_voltage_nets': []}))

    def test_resistors_and_capacitors_by_subcategory_and_tier(self):
        cases = [
            (('R503', 'Device:R', '10m/1%/1W'), (pc.SENSE_R, 'common')),
            (('R201', 'Device:R', '0.10/1%/1W'), (pc.SENSE_R, 'common')),
            (('R303', 'Device:R', '0.30/1%/2W'), (pc.SENSE_R, 'special')),
            (('R9', 'Device:R', '0.0005'), (pc.SENSE_R, 'special')),
            (('R8', 'Device:R', '10m/1%/1W', '50ppm'), (pc.SENSE_R, 'special')),
            (('R304', 'Device:R', '33k/3W'), (pc.POWER_R, 'common')),
            (('R7', 'Device:R', '1k', '10W'), (pc.POWER_R, 'special')),
            (('R403', 'Device:R', '4.7k/1%/0.5W/pulse'), (pc.GENERAL_R, 'special')),
            (('R1', 'Device:R', '10k'), (pc.GENERAL_R, 'common')),
            (('RV3', 'Device:R_Potentiometer_Trim', '10k'), (pc.POT_R, 'common')),
            (('C1', 'Device:C', '1n/630V', 'MKP snubber dv/dt'), (pc.FILM, 'special')),
            (('C2', 'Device:C', '100n/50V/X7R'), (pc.MLCC, 'common')),
            (('C3', 'Device:C_Polarized', '100u/35V'), (pc.ALUMINUM, 'common')),
            (('C4', 'Device:C_Polarized', '330u/35V', 'polymer ESR≤20mΩ'), (pc.POLYMER, 'common')),
            (('CY1', 'Device:C', '1n/400Vac'), (pc.SAFETY_C, 'special'))]
        for args, expected in cases:
            self.assertEqual(expected, self.level(*args), args[0])

    def test_the_library_folder_and_a_declaration_set_the_subcategory(self):
        filed = part('R5', 'Device:R', '10k', datasheet='raw/Datasheet/22_电阻器/电流检测电阻 (分流)/Vishay - WSL.pdf')
        self.assertEqual(pc.SENSE_R, pc.category(filed)[0])
        self.assertIn('不是电阻的子类', pc.category(part('R6', 'Device:R', '10k', Category='20_电容器/铝电解电容'))[1])

    def test_common_sense_and_power_resistors_state_their_ratings(self):
        # R7 kept only the values of its sense resistors (R106 0R68, R201 0R10, R303 0R30, R503 10m).
        intent = {'components': [part('R106', 'Device:R', '0R68'), part('R304', 'Device:R', '33k/3W')]}
        with mock.patch.object(pc, 'library_present', return_value=False):
            problems = pc.audit_identity(intent, [])[0]
        self.assertIn('容差（电流检测电阻 (分流)要写）、功率', problems[0])
        self.assertIn('容差（功率电阻 (线绕_金属板)要写）', problems[1])


def safety_intent(**extra):
    nets = {'L_IN': ['J1.1', 'F1.1'], 'N_IN': ['J1.2', 'RV1.2', 'CX1.2', 'BR1.3'], 'L_F': ['F1.2', 'RV1.1', 'CX1.1', 'BR1.2'],
            'RECT': ['BR1.1', 'T1.1'], 'PGND': ['BR1.4', 'CY1.1', 'U1.4'], 'SW': ['T1.2', 'Q1.3'], 'SEC': ['T1.3', 'D1.2'],
            'VOUT': ['D1.1', 'U1.1', 'R1.1'], 'SGND': ['T1.4', 'CY1.2', 'R2.2'], 'FB': ['U1.2', 'R1.2', 'R2.1'],
            'COMP': ['U1.3', 'Q1.1'], 'GATE': ['Q1.2']}
    comps = [part('J1', 'Connector:Conn_01x02'), part('F1', 'Device:Fuse', 'T3.15A/250Vac'), part('RV1', 'Device:Varistor', 'S14K275'),
             part('CX1', 'Device:C', '220n/X2/310Vac'), part('BR1', 'PD100:GBU4M'), part('T1', 'PD100:Transformer'),
             part('Q1', 'Transistor_FET:IPD80R280P7'), part('D1', 'Device:D_Schottky'), part('CY1', 'Device:C', '1n/Y1/400Vac'),
             part('U1', 'x:SFH6186-4'), part('R1', 'Device:R', '1k'), part('R2', 'Device:R', '10k')]
    intent = {'nets': nets, 'high_voltage_nets': ['L_IN', 'N_IN', 'L_F', 'RECT'], 'components': comps}
    intent.update(extra)
    return intent


class SafetyTests(unittest.TestCase):
    def test_positions_follow_dc_domains_and_high_voltage_nets(self):
        self.assertEqual({'J1': 'mains', 'F1': 'mains', 'RV1': 'mains', 'CX1': 'mains', 'T1': 'isolation', 'CY1': 'isolation',
                          'U1': 'isolation'}, pc.safety_positions(safety_intent()))

    def test_protection_needs_a_two_sided_threshold_and_safety_positions_an_approval(self):
        problems = pc.audit_safety(safety_intent(), {'calculations': [{'id': 'FUSE', 'refs': ['F1', 'RV1']}]})
        text = '\n'.join(problems)
        for said in ('保护器件 F1', '保护器件 RV1', '跨隔离的器件 T1', '跨隔离的器件 CY1', '跨隔离的器件 U1',
                     '市电/高压侧的安规件 J1', 'X 电容 CX1（220n/X2/310Vac）要进放电', 'Y 电容 CY1（1n/Y1/400Vac）要进接触电流'):
            self.assertIn(said, text)
        intent = safety_intent()
        for c in intent['components']:
            c['fields']['Approval'] = 'IEC 60384-14；UL E123456'
        closure = {'calculations': [{'id': 'INPUT', 'kind': 'threshold', 'refs': ['F1', 'RV1', 'CX1']},
                                    {'id': 'TOUCH', 'refs': ['CY1']}]}
        self.assertEqual([], pc.audit_safety(intent, closure))

    def test_a_design_with_safety_parts_declares_its_high_voltage_nets(self):
        intent = safety_intent()
        del intent['high_voltage_nets']
        problems = pc.audit_safety(intent, {})
        self.assertIn('没写 high_voltage_nets', problems[0])


def common_ground_intent(hv):
    """Matrix R3 S29: a 24 V board with one ground; a buck's bootstrap and a D connector carrying 24 V, GND and a PPS
    pin whose buffer is on another board (the PPS net has no second endpoint here)."""
    nets = {'VIN': ['J1.1', 'U1.1', 'C1.1', 'J2.1'], 'GND': ['J1.2', 'U1.2', 'C1.2', 'J2.2', 'R1.2'],
            'BST': ['U1.3', 'C2.1'], 'SW': ['U1.4', 'C2.2', 'L1.1'], 'VOUT': ['L1.2', 'R1.1'],
            'PPS_OUT_1': ['J2.3']}
    comps = [part('J1', 'Connector:Conn_01x02'), part('U1', 'Regulator_Switching:LM5164'), part('C1', 'Device:C', '1u/50V'),
             part('C2', 'Device:C', '100n/50V'), part('L1', 'Device:L', '10u'), part('R1', 'Device:R', '10k'),
             part('J2', 'Connector_Generic:Conn_01x03')]
    return {'nets': nets, 'high_voltage_nets': hv, 'components': comps}


class CommonGroundSafetyTests(unittest.TestCase):
    """A part bridges an isolation only when the other side is a separate domain with circuitry of its own on the
    board; an off-board pin with no second on-board endpoint is not another ground (Matrix R3 S29)."""
    def test_a_24v_common_ground_board_has_no_isolation_position(self):
        self.assertEqual({}, pc.safety_positions(common_ground_intent([])))

    def test_a_39v_bootstrap_does_not_make_the_pps_connector_an_isolation_part(self):
        self.assertNotIn('J2', pc.safety_positions(common_ground_intent(['BST'])))
        problems = pc.audit_safety(common_ground_intent(['BST']), {})
        self.assertFalse([p for p in problems if '跨隔离' in p], problems)

    def test_signals_between_pins_of_one_connector_are_not_another_domain(self):
        intent = common_ground_intent(['BST'])
        intent['nets']['PPS_OUT_1'] = ['J2.3', 'J2.4']
        self.assertNotIn('J2', pc.safety_positions(intent))

    def test_a_real_isolator_beside_the_pps_connector_is_still_found(self):
        intent = common_ground_intent(['BST'])
        intent['nets'].update({'LED_A': ['U2.1', 'R2.1'], 'ISO_OUT': ['U2.4', 'R3.1'], 'ISO_GND': ['U2.3', 'R3.2']})
        intent['nets']['VIN'].append('R2.2')
        intent['nets']['GND'].append('U2.2')
        intent['components'] += [part('U2', 'x:SFH6186-4'), part('R2', 'Device:R', '2k'), part('R3', 'Device:R', '10k')]
        positions = pc.safety_positions(intent)
        self.assertEqual('isolation', positions.get('U2'))
        self.assertNotIn('J2', positions)


class ProposeTests(unittest.TestCase):
    def test_candidates_come_from_the_title_lines_of_page_one(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
        import propose_part_kinds
        with tempfile.TemporaryDirectory() as tmp:
            sheet = Path(tmp) / 'Datasheet' / '23_分立半导体' / 'TVS二极管' / 'Vishay - SMBJ.pdf'
            sheet.parent.mkdir(parents=True)
            sheet.write_bytes(b'%PDF')
            title = 'SMBJ5.0A thru SMBJ188CA\nSurface Mount TRANSZORB Transient Voltage Suppressors\n' + 'body diode text\n' * 20
            intent = {'components': [part('D706', 'PD100:D_TVS_Uni', 'SMBJ24A', 'SMBJ24A-E3/52', sheet.relative_to(tmp).as_posix())]}
            with mock.patch.object(propose_part_kinds, 'page_text', return_value=title), \
                    mock.patch.object(pc, 'library_present', return_value=False):
                rows = propose_part_kinds.propose(intent, [Path(tmp)])
        self.assertEqual('single', rows[0]['status'])
        self.assertTrue(rows[0]['agrees'])
        self.assertEqual({'Kind': 'tvs', 'KindSource': 'datasheet:Datasheet/23_分立半导体/TVS二极管/Vishay - SMBJ.pdf#p1',
                          'KindQuote': 'Surface Mount TRANSZORB Transient Voltage Suppressors', 'Category': '23_分立半导体/TVS二极管'},
                         rows[0]['candidates'][0])


class DeclarationEvidenceTests(unittest.TestCase):
    def test_declaration_statuses_follow_the_quoted_evidence(self):
        cases = [('tvs', 'Unidirectional TVS', 'VERIFIED'),
                 ('tvs', 'Bidirectional TVS 400 W', 'QUOTE_NOT_FOUND'),
                 ('tvs', 'Replaces Zener diode clamps', 'QUOTE_LACKS_TYPE'),
                 ('diode', 'Unidirectional TVS', 'QUOTE_LACKS_TYPE'),
                 ('tvs', 'Unidirectional TVS, peak pulse power 600 W. Replaces Zener diode', 'QUOTE_CONFLICT')]
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'SMBJ24A.pdf').write_bytes(b'%PDF smbj')
            with mock.patch.object(pc, 'check', return_value={'status': 'PASS', 'reason': '', 'unshown': []}), \
                    mock.patch.object(pc, 'page_text', return_value=PAGE):
                for kind, quote, expected in cases:
                    actual = pc.verify_declaration(declared('D706', 'PD100:D_TVS_Uni', kind, quote), kind, [Path(tmp)], True)[0]
                    self.assertEqual(expected, actual, (kind, quote))

    def test_quotes_name_explicit_kinds_and_exclude_ic_loads(self):
        cases = {'Littelfuse Inc.': set(), 'Surface mount fuses': {'fuse'},
                 'PPTC resettable device': {'fuse'}, 'Industrial eFuse': set(),
                 'Metal oxide varistor, ThermoFuse types': {'varistor'},
                 'Low-side relay driver': set(), 'Power relay, 16 A': {'relay'},
                 'SMD Common Mode Filter': {'common_mode_choke'}, 'Coupled Inductor': {'coupled_inductor'},
                 'Common mode choke': {'common_mode_choke'}, 'MOSFET gate driver': set(),
                 'BidirectionalTVSDiode': {'tvs'}, 'N-Channel MOSFET': {'mosfet'},
                 'Optocoupler, phototransistor output': {'opto'}, 'Unidirectional TVS': {'tvs'}}
        for quote, expected in cases.items():
            self.assertEqual(expected, pc.cues(quote), quote)
        # All locally maintained role cues must suppress the named load's type, not just a sample role name.
        for role in pc.IC_ROLE_CUES:
            for load in pc.ROLE_LOADS:
                cue = pc.KINDS[load].cues[0]
                self.assertNotIn(load, pc.cues(role + ' ' + cue), (role, load))


if __name__ == '__main__':
    unittest.main()
