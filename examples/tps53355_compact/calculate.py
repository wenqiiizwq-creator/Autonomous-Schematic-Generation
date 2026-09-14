"""TI Rev G equations 8–16; estimates and conditional corners, not SPICE."""
import itertools, json, math
from pathlib import Path

def calc(vin=5, vout=.85, amps=15, L=.47e-6, fs=500e3, cout=610.1e-6,
         esr=.0003333333333, rinj=1000, cinj=100e-9, rtop=3970, rbottom=10000, rtrip=100000, itrip=10e-6, rds=.0017):
    d=vout/vin; delta=(vin-vout)*d/(L*fs); ton=d/fs; n=4 if L<=250e-9 else 2
    vsw=(vin-vout)*d/(rinj*cinj*fs)
    vo=esr*delta+delta/(8*cout*fs); fb=.6+(vsw+vo)/2
    ocp=rtrip*itrip/(32*rds)+delta/2
    return {'duty':d,'delta_i_pp_A':delta,'i_peak_at_load_A':amps+delta/2,
      'i_inductor_rms_A':math.sqrt(amps**2+delta**2/12),'i_cin_rms_A':amps*math.sqrt(d*(1-d)),
      'ton_ns':ton*1e9,'toff_ns':(1-d)/fs*1e9,'N':n,
      'eq11_margin':L*cout/(rinj*cinj)/(n*ton/2),
      'v_inj_sw_mV':vsw*1e3,'v_inj_output_mV':vo*1e3,'v_inj_total_mV':(vsw+vo)*1e3,
      'vfb_average_estimate_V':fb,'vout_estimate_V':fb*(1+rtop/rbottom),
      'ocp_average_estimate_A':ocp,'ocp_peak_estimate_A':ocp+delta/2}

if __name__=='__main__':
    nominal=calc(); corners=[]
    # Tolerances include an assumed extra 30% inductance drop, not a guaranteed
    # hot-current minimum. Frequency limits are application sensitivity inputs.
    for vin,L,fs,c,esr,r,cj in itertools.product([4.75,5.25],[.47e-6*.8*.7,.47e-6*1.2],
        [450e3,550e3],[300e-6,720e-6],[0,.001],[990,1010],[90e-9,110e-9]):
        corners.append(calc(vin=vin,L=L,fs=fs,cout=c,esr=esr,rinj=r,cinj=cj))
    ref=calc(L=.22e-6,cout=674.1e-6,esr=0,rinj=15000,cinj=15e-9,rtop=14700,rbottom=35100,rtrip=200000)
    ocps=[calc(vin=vin,L=L,fs=fs,rtrip=r,itrip=i,rds=rd) for vin,L,fs,r,i,rd in itertools.product(
      [4.75,5.25],[.47e-6*.8*.7,.47e-6*1.2],[450e3,550e3],[99000,101000],[9.4e-6,10.6e-6],[.0015,.0017])]
    result={'status':'CALCULATED_DRAFT_CONDITIONAL','datasheet':'TI TPS53355 SLUSAE5G, equations 8-16, Tables 6.5/7-1/7-3',
      'nominal':nominal,'corners':{k:{'min':min(x[k] for x in corners),'max':max(x[k] for x in corners)} for k in nominal},
      'ocp_parameter_sensitivity':{k:{'min':min(x[k] for x in ocps),'max':max(x[k] for x in ocps)} for k in ['ocp_average_estimate_A','ocp_peak_estimate_A']},
      'engineer_image_all_ceramic_conditional':ref,
      'engineer_no_ripple_divider_V':.6*(1+14700/35100),
      'engineer_min_Cout_nominal_eq11_uF':4*(.85/5/500e3)/2*(15000*15e-9)/.22e-6*1e6,
      'loss_estimates':{'L1_copper_25C_max_DCR_W':nominal['i_inductor_rms_A']**2*.0023,
       'L1_copper_100C_DCR_est_W':nominal['i_inductor_rms_A']**2*.0023*(1+.00393*75),
       'input_average_at_4_75V_85pct_eff_A':(.85*15)/(.85*4.75),
       'ideal_charge_current_610_1uF_1_4ms_A':610.1e-6*.85/.0014},
      'assumptions':['COUT effective >=300uF including tolerance/DC bias/temperature/aging is a requirement, not supplier-curve evidence.',
       'ESR aggregate 0.333mOhm nominal and 0-1mOhm sensitivity are assumed; output-voltage estimate excludes ESL and dynamic skip behavior.',
       '450-550kHz is not a guaranteed all-temperature/5V range; TI table test condition differs.',
       'Isat curves are at 25C. OCP sensitivity excludes unbounded VOCL and MOSFET hot variation; not a guaranteed trip range.',
       'VREF +/-1% and divider tolerance add output uncertainty; no +/-1% rail-accuracy claim.',
       'Engineer capacitance type/MPN unknown: Eq11 comparison applies ONLY if the bank is all ceramic.',
       'No simulator installed; these calculations are not a switching/closed-loop simulation.']}
    path=Path(__file__).resolve().parent/'calculations.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'nominal':nominal,'eq11_min':result['corners']['eq11_margin']['min'],'reference':ref,'ocp_sensitivity':result['ocp_parameter_sensitivity']},indent=2))
