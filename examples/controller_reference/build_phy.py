"""KSZ8081RNA sample: reference supply, strap, clock and connector circuits."""
import copy,json
from pathlib import Path
from build_reference import run
BASE=Path(__file__).resolve().parent

def phy():
 d=json.loads((BASE/'phy_intent.json').read_text());p={}
 def place(ref,x,y,r=0,style=None):
  p[ref]={'at':[x,y],'rotation':r}
  if style=='bank':p[ref]['fields']={'Reference':{'at':[x+3.81,y],'angle':90,'font_mm':1.016},'Value':{'at':[x+5.588,y],'angle':90,'font_mm':1.016}}
  if style=='h':p[ref]['fields']={'Reference':{'at':[x,y-6.35],'font_mm':1.016},'Value':{'at':[x,y-3.81],'font_mm':1.016}}
 place('U2601',165.1,111.76)
 p['U2601']['fields']={'Reference':{'at':[187.96,76.2],'font_mm':1.016},'Value':{'at':[187.96,78.74],'font_mm':1.016}}
 # Three separate supply branches: internal regulator output, filtered analog, I/O.
 for ref,x,y in [('C26012',114.3,60.96),('C26013',127,60.96),('C26010',119.38,43.18),('C26014',106.68,43.18),('C26011',200.66,43.18),('C26015',213.36,43.18)]:place(ref,x,y,style='bank')
 place('FB2601',90.17,31.75,90,'h')
 # Clock, bias and reset are kept beside the relevant pins.
 place('Y2601',78.74,137.16,90)
 p['Y2601']['fields']={'Reference':{'at':[64.77,137.16],'font_mm':1.016},'Value':{'at':[64.77,139.7],'font_mm':1.016}}
 place('C260191',66.04,148.59,270,'h');place('C260192',66.04,125.73,270,'h')
 place('R26010',205.74,137.16,style='bank')
 place('R26011',99.06,114.3,90)
 place('R26014',45.72,121.92,90)
 p['R26014']['fields']={'Reference':{'at':[45.72,125.73],'font_mm':1.016},'Value':{'at':[45.72,128.27],'font_mm':1.016}}
 place('R26013',104.14,124.46,90)
 p['R26013']['fields']={'Reference':{'at':[104.14,118.11],'font_mm':1.016},'Value':{'at':[104.14,120.65],'font_mm':1.016}}
 place('R26012',99.06,106.68,270)
 # Strap resistors are a compact, explicitly labelled local configuration group.
 for ref,x in [('R26015',45.72),('R26016',86.36),('R26017',127.0)]:place(ref,x,200.66,style='bank')
 place('J2601',299.72,100.33)
 p['J2601']['fields']={'Reference':{'at':[299.72,80.01],'font_mm':1.016},'Value':{'at':[299.72,82.55],'font_mm':1.016}}
 place('C26060',223.52,95.25,270,'h');place('C26061',223.52,102.87,270)
 p['C26061']['fields']={'Reference':{'at':[223.52,106.68],'font_mm':1.016},'Value':{'at':[223.52,109.22],'font_mm':1.016}}
 place('R26060',349.25,97.79,270,'h')
 place('U2651',299.72,165.1)
 p['U2651']['fields']={'Reference':{'at':[299.72,147.32],'font_mm':1.016},'Value':{'at':[299.72,149.86],'font_mm':1.016}}
 policies={n['name']:{'mode':'labels'} for n in d['nets']}
 # Each functional analog loop is directly wired; page I/O and MDI endpoints use labels.
 direct=['TCU_PHY_1V2','TCU_PHY_AVDD','TCU_PHY_XI','TCU_PHY_XO','TCU_PHY_REXT','TCU_MDI_TCT','TCU_MDI_RCT','TCU_PHY_LED_A','TCU_PHY_LED0','TCU_ETH_SHIELD']
 for n in direct:policies[n]={'mode':'wire','label':True}
 # local power banks deliberately form visible paired capacitor branches
 policies['TCU_ETH_SHIELD']['rail_y']=130.81
 policies['TCU_PHY_1V2']['groups']=[['C26012.1','C26013.1','U2601.1']]
 policies['TCU_PHY_AVDD']['groups']=[{'pins':['FB2601.2','C26010.1','C26014.1','U2601.2'],'rail_y':31.75}]
 for n,refs in [('TCU_3V3',[['FB2601.1'],['C26011.1','C26015.1','U2601.14'],['R26011.1'],['R26014.1'],['R26013.1'],['R26060.1']]),
 ('TCU_GND',[['C26012.2','C26013.2'],['C26010.2','C26014.2'],['C26011.2','C26015.2'],['U2601.22','U2601.25'],['R26010.2'],['C260191.2','C260192.2'],{'pins':['R26015.2','R26016.2','R26017.2'],'rail_y':213.36},['C26060.2','C26061.2'],['U2651.3','U2651.8']])]:
  policies[n]={'mode':'wire','groups':refs}
 # PHY management pull-ups and reset connection are attached to their actual pins.
 for n in ['TCU_ETH_MDIO','TCU_PHY_IRQ_N','TCU_PHY_RESET_N']:
  policies[n]={'mode':'wire','label':True}
 policies['TCU_ETH_CLK50_RAW']={'mode':'wire','groups':[['U2601.16','R26012.1'],['R26016.1']]}
 policies['TCU_PHY_LED0']['groups']=[['U2601.23'],['J2601.9']]
 # Ground at shared terminals has one drawn stem but two retained physical pads.
 for n in ['TCU_PHY_1V2','TCU_PHY_AVDD']:policies[n]['priority']=-10 if n == 'TCU_PHY_AVDD' else -9
 for n in ['TCU_PHY_XI','TCU_PHY_XO']:policies[n]['priority']=-8
 policies['TCU_GND']['priority']=-7
 layout={'schema_version':1,'paper':'A3','grid_mm':1.27,'placements':p,'nets':policies,'max_route_states':300000,'annotations':[
 {'text':'TCU / KSZ8081RNA Ethernet / Rev C reference-driven validation','at':[15.24,15.24],'font_mm':2.032},
 {'text':'1.2 V internal regulator','at':[101.6,50.8],'font_mm':1.016},
 {'text':'Analog 3.3 V filtered','at':[104.14,21.59],'font_mm':1.016},
 {'text':'I/O 3.3 V','at':[200.66,24.13],'font_mm':1.016},
 {'text':'RMII / MDIO to MAC\nRNA: 25MHz crystal, 50MHz clock output','at':[20.32,66.04],'font_mm':1.016},
 {'text':'MAGJACK / separate TX and RX centre taps\nVoltage-mode PHY: neither CT connects to 3.3 V','at':[241.3,55.88],'font_mm':1.016},
 {'text':'PHY-side ESD array\nPlace beside jack on PCB','at':[241.3,200.66],'font_mm':1.016},
 {'text':'Reset straps: PHY address 0; RXER low\nMAC pins high-Z while reset is asserted','at':[25.4,172.72],'font_mm':1.016},
 {'text':'Source: Microchip DS00002199D pp6-9,23-24,43-44.  MDIO/IRQ: 1k pull-up. REXT: 6.49k 1%.\nC_XTAL=22pF is a tuning candidate for CL=16pF and ~5pF stray. Crystal MPN/ESR/drive remain open.\nFerrite impedance/DC bias, MLCC MPN, reset timing and host power-up strap loading require confirmation.\nSHIELD is chassis; TCU_GND remains the isolated control ground. This sample does not release the full board.','at':[15.24,231.14],'font_mm':1.016}]}
 return d,layout
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args();run(*phy(),args.out/'TCU-Ethernet')
