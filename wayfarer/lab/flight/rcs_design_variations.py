"""Conditional RCS configuration trades on the validated original-mount 300 kN case.

Alter exactly one design dimension at a time. No asserted hardware feasibility.
"""
import copy, json
from pathlib import Path
from lab import save_run
ROOT=Path(__file__).resolve().parent
CF=ROOT/'configs'; EX=ROOT/'experiments'; OUT=ROOT/'lab_results'
base=json.loads((CF/'wayfarer_original_mount_300k.json').read_text())
base_exp=json.loads((EX/'reversal10.json').read_text())
base_exp['phases'][0]['post_hold_s']=4.
cases={}
cases['fixed300_original']=copy.deepcopy(base)
mass=copy.deepcopy(base);mass['name']='300 kN reference mounts plus 375kg per uprated nozzle'
mass['provenance']['added_mass']='24 hypothetical 375kg engine packages; 9 tonnes total'
for e in mass['rcs']:
    if e['max_N']>25000:
        mass['components'].append({'mass_kg':375.,'cg_m':e['pos_m']})
cases['fixed300_plus9t']=mass
shift=copy.deepcopy(base);shift['name']='300 kN mounts 1m farther fore/aft, fixed original mass'
shift['provenance']['mount_shift']='1m farther apart; no hardware mass change, geometric sensitivity only'
for e in shift['rcs']:
    if e['max_N']>25000:
        e['pos_m'][0]+= -1. if e['pos_m'][0]<20 else 1.
cases['fixed300_shifted']=shift
both=copy.deepcopy(shift);both['name']='300 kN mounts shifted and 9t of hypothetical engines'
both['provenance']['added_mass']='24 engine packages x375kg with shifted mounts'
for e in both['rcs']:
    if e['max_N']>25000:
        both['components'].append({'mass_kg':375.,'cg_m':e['pos_m']})
cases['fixed300_shifted_plus9t']=both
only8=copy.deepcopy(base);only8['name']='Only eight original inward thrusters uprated to 300 kN'
only8['provenance']['alternative']='Eight coarse engines only; original mounts, mass unchanged'
for e in only8['rcs']:
    if e['max_N']>25000 and not e['id'].endswith('_inward'):e['max_N']=25000.
cases['inward8_300k']=only8
for kn in [260,280,290]:
    s=copy.deepcopy(base);s['name']=f'Original mount {kn} kN nonaxial trade'
    s['provenance']['alternative']='performance-only fixed mounts, no engine mass claim'
    for e in s['rcs']:
        if e['max_N']>25000:e['max_N']=kn*1000.
    cases[f'fixed{kn}_original']=s
rows=[]
for case,ship in cases.items():
    exp=copy.deepcopy(base_exp);exp['name']=case+'_10s_180deg'
    (CF/(case+'.json')).write_text(json.dumps(ship,indent=2)+'\n')
    (EX/(case+'.json')).write_text(json.dumps(exp,indent=2)+'\n')
    result=save_run(CF/(case+'.json'),EX/(case+'.json'),OUT,.02,.1)
    p=result['phases'][0]
    row={'case':case,'terminal_pass':result['qualification']['status']=='pass',
         'error_deg_at_10s':p['attitude_error_deg'],
         'rate_deg_s_at_10s':p['rate_deg_s'],
         'final_uninterrupted_gate_s':p['gate_entry_s'],
         'ship_mass_kg':p['mass_end_kg'],
         'max_offaxis_torque_Nm':p['peak_offaxis_torque_Nm'],
         'min_allocation_fraction':p['minimum_allocated_fraction'],
         'RCS_scalar_impulse_Ns':result['rcs_impulse_Ns'],
         'RCS_propellant':'unknown for original Wayfarer specification',
         'equipment_mass':'invented conditional study values where specified'}
    rows.append(row)
    (OUT/'rcs_design_variations.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
    print('DESIGN',case,'pass=',row['terminal_pass'],'error=',row['error_deg_at_10s'],
          'rate=',row['rate_deg_s_at_10s'],'gate=',row['final_uninterrupted_gate_s'],flush=True)
print('COMPLETE',len(rows),'design variations',flush=True)
