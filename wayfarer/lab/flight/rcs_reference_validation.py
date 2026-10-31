"""Reproduce Astra's fixed coarse RCS study in the generalized scratch flight lab.

Use original Rev7 mounts: 24 non-axial engines at specified coarse N,
8 axial engines always 25 kN. No RCS mass, fuel, or Isp assumptions.
Runs are non-governing numerical comparisons, not hardware qualification.
"""
import copy, json, math
from pathlib import Path
import numpy as np
import study
from flightlab import run, mass_properties, crossmat
from lab import save_run

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'lab_results'
OUT.mkdir(exist_ok=True)
CF=ROOT/'configs'
EX=ROOT/'experiments'
base=json.loads((CF/'wayfarer.json').read_text())
card=json.loads((ROOT/'fixtures/rev7/wayfarer_v05_card.json').read_text())
historical={r['label']:r for r in json.loads((ROOT/'results/rcs_runs.json').read_text())}
assert len(study.G.TH)==32
assert sum(t['kind']=='axial' for t in study.G.TH)==8
assert sum(t['kind']!='axial' for t in study.G.TH)==24

def ship_config(coarse_kN,state='S1',disabled=None,lag=.05):
    ship=copy.deepcopy(base)
    for e in ship['rcs']:
        if not e['id'].endswith('_axial'):e['max_N']=coarse_kN*1000.
        e['lag_s']=lag
        if disabled is not None and e['id'].startswith(disabled+'_'):
            e['enabled']=False
    ship['name']=f'Wayfarer original mounts {coarse_kN} kN nonaxial, {state}, lag {lag}'
    ship['provenance']['rcs_study']='study.py fixed original mounts; no Isp/fuel or extra hardware mass'
    if disabled:ship['provenance']['failed_cluster']=disabled
    if state=='S2':
        a=card['states']['S1'];b=card['states']['S2']
        m1=a['mass_t']*1000;m2=b['mass_t']*1000;payload=m2-m1
        cg1=np.array(a['cg_m']);cg2=np.array(b['cg_m'])
        cg=(m2*cg2-m1*cg1)/payload
        I=(np.array(b['inertia_tensor_kg_m2'])+m2*crossmat(cg2)
           -np.array(a['inertia_tensor_kg_m2'])-m1*crossmat(cg1)
           -payload*crossmat(cg))
        assert np.linalg.eigvalsh(I).min()>0
        ship['components'].append({'mass_kg':payload,'cg_m':cg.tolist(),'inertia_kg_m2':I.tolist(),
                                   'note':'reconstructed aggregate S2 payload from Rev7 card'})
    m,cg,I=mass_properties(ship,{'remass':250000})
    st=card['states'][state]
    np.testing.assert_allclose(m,st['mass_t']*1000,atol=.01)
    np.testing.assert_allclose(cg,st['cg_m'],atol=1e-6)
    np.testing.assert_allclose(I,st['inertia_tensor_kg_m2'],atol=1e-3)
    engines=[e for e in ship['rcs'] if e.get('enabled',True)]
    truth=[t for t in study.G.TH if t['cluster']!=disabled]
    assert len(engines)==len(truth)
    for a,b in zip(engines,truth):
        np.testing.assert_allclose(a['pos_m'],b['pos'],atol=1e-12)
        np.testing.assert_allclose(a['direction'],np.asarray(b['f'])/25000,atol=1e-12)
        assert a['max_N']==(25000 if b['kind']=='axial' else coarse_kN*1000)
    return ship
CASES=[
 ('baseline25_10s',25,10,'pitch','S1',None,.05,.02),
 ('baseline25_40s',25,40,'pitch','S1',None,.05,.02),
 ('fixed150_10s',150,10,'pitch','S1',None,.05,.02),
 ('fixed200_10s',200,10,'pitch','S1',None,.05,.02),
 ('fixed250_10s',250,10,'pitch','S1',None,.05,.02),
 ('fixed300_pitch',300,10,'pitch','S1',None,.05,.02),
 ('fixed300_yaw',300,10,'yaw','S1',None,.05,.02),
 ('fixed300_loaded',300,10,'pitch','S2',None,.05,.02),
 ('fixed300_clusterout',300,10,'pitch','S1','F+Z',.05,.02),
 ('fixed300_slowactuator',300,10,'pitch','S1',None,.2,.02),
 ('fixed300_halfstep',300,10,'pitch','S1',None,.05,.01)
]
rows=[]
for label,force,T,axis,state,failed,lag,dt in CASES:
    ship=ship_config(force,state,failed,lag)
    experiment={'name':label+'_reference_replay',
                'phases':[{'kind':'rcs_turn','duration_s':T,'post_hold_s':4.,
                           'axis':axis,'angle_deg':180.,
                           'gate_attitude_deg':.25,'gate_rate_deg_s':.05}],
                'checks':{'attitude_error_deg':{'max':.25},
                          'rate_deg_s':{'max':.05}}}
    config_name='reference_'+label
    (CF/(config_name+'.json')).write_text(json.dumps(ship,indent=2)+'\n')
    (EX/(config_name+'.json')).write_text(json.dumps(experiment,indent=2)+'\n')
    result=save_run(CF/(config_name+'.json'),EX/(config_name+'.json'),OUT,dt,.1)
    p=result['phases'][0]
    row={'label':label,'coarse_kN':force,'axial_kN':25,'state':state,
         'axis':axis,'failed_cluster':failed,'lag_s':lag,'dt_s':dt,
         'at_10_or_40s_error_deg':p['attitude_error_deg'],
         'at_10_or_40s_rate_deg_s':p['rate_deg_s'],
         'simulation_pass_at_target':result['qualification']['status']=='pass',
         'gate_entry_s':p['gate_entry_s'],'gate_hold_s':p['gate_hold_s'],
         'RCS_impulse_Ns':result['rcs_impulse_Ns'],
         'mass_model':'original Rev7, fixed mass & inertia; RCS propellant unresolved',
         'config_sha256':result['ship_sha256'],'experiment_sha256':result['experiment_sha256']}
    if label in historical:
        old=historical[label]
        row['historical_at_target']=old['at_target_time']
        row['historical_gate_entry_s']=old['gate_entry_s']
        row['delta_error_deg']=row['at_10_or_40s_error_deg']-old['at_target_time']['attitude_error_deg']
        row['delta_rate_deg_s']=row['at_10_or_40s_rate_deg_s']-old['at_target_time']['rate_deg_s']
        row['delta_gate_entry_s']=(None if row['gate_entry_s'] is None or old['gate_entry_s'] is None
                                    else row['gate_entry_s']-old['gate_entry_s'])
        row['agreement']=(
             abs(row['delta_error_deg'])<.02
             and abs(row['delta_rate_deg_s'])<.02
             and row['simulation_pass_at_target']==old['pass_at_target']
             and ((row['gate_entry_s'] is None and old['gate_entry_s'] is None)
                  or (row['delta_gate_entry_s'] is not None and abs(row['delta_gate_entry_s'])<.1)))
    rows.append(row)
    (OUT/'rcs_reference_comparison.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
    print('COMPARISON',label,'gate=',row['gate_entry_s'],
          'error-delta=',row.get('delta_error_deg'),'rate-delta=',row.get('delta_rate_deg_s'),
          'agreement=',row.get('agreement'),flush=True)

comparisons=[r for r in rows if 'historical_at_target' in r]
overall=all(r['agreement'] for r in comparisons)
summary={'scope':'Original Wayfarer Rev7 positions; 24 coarse uprated nonaxial thrusters plus eight fixed 25kN axial',
         'reference_count':len(comparisons),
         'all_historical_results_reproduced':overall,
         'gate_definition':'last uninterrupted gate interval after nominal target time; not first transient entry',
         'acceptance':'attitude <=0.25 deg AND angular rate <=0.05 deg/s at requested target time',
         'simulation_only':'RCS Isp/flow, dry hardware mass, and installation feasibility not established',
         'cases':rows}
(OUT/'rcs_reference_summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
print('FINAL_MATCH',overall,'matching',len(comparisons),'of',len(comparisons),'reference cases',flush=True)
if not overall:
    raise SystemExit('Historical reference mismatch, inspect saved comparison')
