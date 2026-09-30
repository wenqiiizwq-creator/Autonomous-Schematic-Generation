"""Recipe regression fixture: one circuit, a readable and an unreadable drawing.

A test fixture, not a qualified design. ``draw()`` states only structure (anchor
positions, chains, banks, shunts, rails, labels); ``draw(bad=True)`` keeps the
same netlist but reproduces two field failures seen on a real 100 W charger:
a support part's net forced across another net (the R410 pattern) and a
two-terminal U-turn (the J101.2 -> L101.3 pattern).
"""
from schematic_layout.recipes import Sheet, add, DOWN, UP, LEFT, RIGHT


def part(ref, lib, val):
    return {'ref': ref, 'lib_id': lib, 'value': val, 'footprint': ''}


INTENT = {
    'schema_version': 1, 'title': 'Recipe verification: 12 V to 5 V / 3.3 V with USB ESD', 'revision': 'test',
    'design_id': 'recipe-board',
    'components': [
        part('J1', 'Connector:Barrel_Jack', '12V in'), part('F1', 'Device:Fuse', '2A'),
        part('D1', 'Device:D_Schottky', 'SS34'), part('C1', 'Device:C_Polarized', '100u/35V'),
        part('C2', 'Device:C', '1u'), part('U1', 'Regulator_Switching:LM2596S-ADJ', 'LM2596S-ADJ'),
        part('D2', 'Device:D_Schottky', 'SS54'), part('L1', 'Device:L', '33u'),
        part('C3', 'Device:C_Polarized', '220u/10V'), part('C4', 'Device:C', '100n'),
        part('R1', 'Device:R', '3k01'), part('R2', 'Device:R', '1k'),
        part('U2', 'Regulator_Linear:AMS1117-3.3', 'AMS1117-3.3'), part('C5', 'Device:C', '10u'),
        part('C6', 'Device:C', '22u'), part('R3', 'Device:R', '1k'), part('D3', 'Device:LED', 'green'),
        part('R4', 'Device:R', '22R'), part('R5', 'Device:R', '22R'),
        part('D4', 'Device:D_TVS', 'ESD5V'), part('D5', 'Device:D_TVS', 'ESD5V'),
        part('J2', 'Connector:USB_B_Micro', 'USB_B_Micro')],
    'nets': [
        {'name': 'VIN_RAW', 'pins': ['J1.1', 'F1.1']},
        {'name': 'VIN_F', 'pins': ['F1.2', 'D1.2']},
        {'name': 'VIN', 'pins': ['D1.1', 'C1.1', 'C2.1', 'U1.1']},
        {'name': 'GND', 'pins': ['J1.2', 'C1.2', 'C2.2', 'U1.3', 'U1.5', 'D2.2', 'C3.2', 'C4.2', 'R2.2', 'U2.1',
                                 'C5.2', 'C6.2', 'D3.1', 'D4.2', 'D5.2', 'J2.5', 'J2.SH']},
        {'name': 'SW', 'pins': ['U1.2', 'D2.1', 'L1.1']},
        {'name': '+5V', 'pins': ['L1.2', 'C3.1', 'C4.1', 'R1.1', 'U2.3', 'C5.1']},
        {'name': 'FB', 'pins': ['U1.4', 'R1.2', 'R2.1']},
        {'name': '+3V3', 'pins': ['U2.2', 'C6.1', 'R3.1']},
        {'name': 'LED_A', 'pins': ['R3.2', 'D3.2']},
        {'name': 'MCU_DP', 'pins': ['R5.1']}, {'name': 'MCU_DN', 'pins': ['R4.1']},
        {'name': 'USB_DP', 'pins': ['R5.2', 'D5.1', 'J2.3']}, {'name': 'USB_DN', 'pins': ['R4.2', 'D4.1', 'J2.2']},
        {'name': 'USB_VBUS', 'pins': ['J2.1']}],
    'no_connect': ['J2.4'],
}
RAILS = {'GND': 'power:GND', '+5V': 'power:+5V', '+3V3': 'power:+3V3'}
EXTERNAL = ['MCU_DP', 'MCU_DN', 'USB_VBUS']


def draw(intent=INTENT, bad=False):
    s = Sheet(intent, rails=RAILS, external=EXTERNAL, paper='A4')
    # Row 1: input chain, input bank, buck controller, SW node, output bank, divider.
    s.place('J1', (20.32, 50.8))
    s.power('J1.2')
    s.series('J1.1', ['F1', 'D1'], RIGHT, gap=3)
    vin = s.bank('D1.1', ['C1', 'C2'], RIGHT)
    s.put('U1', '1', add(vin, RIGHT, 12), RIGHT)
    s.wire(vin, 'U1.1')
    s.power('U1.5')
    s.power('U1.3')
    sw = s.stub('U1.2', 3)
    s.shunt(sw, 'D2', DOWN)
    l_out = s.series(sw, ['L1'], RIGHT, gap=6)[-1]
    out = s.bank(l_out, ['C3', 'C4'], RIGHT)
    rail = s.wire(out, add(out, RIGHT, 3))
    s.power(rail)
    r1 = s.series(rail, ['R1'], RIGHT, gap=3)[-1]
    tap = s.wire(r1, add(r1, RIGHT, 2))
    s.shunt(tap, 'R2', DOWN)
    fb = s.stub('U1.4', 2)
    if bad:
        # Feedback dropped straight through the +5 V spine and back up to the tap.
        x = l_out[0] + 2.54
        s.wire(fb, (x, fb[1]), (x, 78.74), (tap[0] + 5.08, 78.74), (tap[0] + 5.08, tap[1]), tap)
    else:
        s.connect(fb, tap, y=fb[1] - 10.16)
    # Row 2: LDO with local decoupling and indicator.
    s.place('U2', (80.01, 101.6))
    s.power(s.bank('U2.3', ['C5'], LEFT))
    s.power('U2.1')
    v33 = s.bank('U2.2', ['C6'], RIGHT)
    rail33 = s.wire(v33, add(v33, RIGHT, 3))
    s.power(rail33)
    if bad:
        # LED dropped in reversed: its anode faces away, so the wire loops round.
        r3 = s.series(rail33, ['R3'], RIGHT, gap=3)[-1]
        s.put('D3', '2', add(r3, RIGHT, 12), LEFT)
        s.wire(r3, add(r3, RIGHT, 2), add(add(r3, RIGHT, 2), UP, 4), add(add(r3, RIGHT, 16), UP, 4),
               add(r3, RIGHT, 16), 'D3.2')
    else:
        s.series(rail33, ['R3', 'D3'], RIGHT, gap=3)
    s.power('D3.1')
    # Row 3: two identical protected USB lanes; D+ straight, D- fans out with a Z.
    s.put('J2', '3', (152.4, 149.86), RIGHT)
    s.label('J2.1', 'global', length=3)
    for net, r, d, y in (('MCU_DP', 'R5', 'D5', 149.86), ('MCU_DN', 'R4', 'D4', 172.72)):
        start = (30.48, y)
        s.series(start, [r], RIGHT, gap=3, net=net)
        s.label(start, 'global', length=0, outward=LEFT, net=net)
        node = s.wire(f'{r}.2', add(s.point(f'{r}.2'), RIGHT, 6))
        s.shunt(node, d, DOWN)
        if net == 'MCU_DP':
            s.wire(node, 'J2.3')
        else:
            s.connect(node, 'J2.2', x=146.05)
    g = s.stub('J2.5', 2)
    s.wire('J2.SH', add(s.point('J2.SH'), DOWN, 2), g)
    s.power(g)
    # Selected local names: function nodes of the multi-pin parts.
    for net, role in s.plan['nets'].items():
        if role == 'name':
            s.name(net)
    s.text('Input protection and buck converter', (17.78, 30.48))
    s.text('3.3 V LDO and indicator', (17.78, 88.9))
    s.text('USB data protection lanes', (17.78, 137.16))
    return s

