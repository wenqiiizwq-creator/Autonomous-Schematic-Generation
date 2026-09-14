"""Review frequency options with the existing L/RC/divider; no automatic adoption."""
import itertools,json
from pathlib import Path
from calculate import calc
BASE=Path(__file__).resolve().parent
result={'scope':'Approximate algebraic sensitivity; additional bypass ESR/ESL not characterized. Conservative minimum COUT remains 300uF, without credit for C22/C23.', 'profiles':{}}
for name,fs,fs_range in [('default_500k',500e3,[450e3,550e3]),('RF_up_650k',650e3,[580e3,720e3]),('RF_down_300k',300e3,[250e3,350e3])]:
 nominal=calc(fs=fs,cout=610.1e-6)
 corners=[calc(vin=v,L=L,fs=f,cout=300e-6,rinj=r,cinj=c) for v,L,f,r,c in itertools.product([4.75,5.25],[.47e-6*.8*.7,.47e-6*1.2],fs_range,[990,1010],[90e-9,110e-9])]
 result['profiles'][name]={'nominal':nominal,'min_eq11_margin':min(x['eq11_margin'] for x in corners),
 'status':'DEFAULT_CALCULATED_DRAFT' if name=='default_500k' else 'DO_NOT_POPULATE_WITHOUT_REDESIGN_REVIEW',
 'frequency_range_note':'TI Table 6.5 range is specified for a different test circuit/operating point; used only for sensitivity.'}
result['notes']=['Nominal total output capacitance changed from 600uF to 610.1uF; R1/R2 values retained.','300kHz option drops the conservative Eq11 margin below 1 under these assumptions; it is a footprint provision, not a qualified alternate assembly.','Changing frequency also shifts the DC output estimate at the same divider; recompute feedback, OCP, loss and transients.','100nF/1nF bypasses are placement provisions; adding unlike capacitors does not prove improved EMI or absence of antiresonance.']
(BASE/'option-calculations.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{'vout':v['nominal']['vout_estimate_V'],'eq11_min':v['min_eq11_margin']} for k,v in result['profiles'].items()},indent=2))
