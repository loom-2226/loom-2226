"""Re-run 40s pitch RCS on exact current Wayfarer mass tensor. No flight qualification claim."""
from pathlib import Path
import sys, json, hashlib, copy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/'flight'))
from flightlab import run
geo=ROOT/'results/out/wayfarer_v05_geometry.json'
sha=hashlib.sha256(geo.read_bytes()).hexdigest()
G=json.loads(geo.read_text())
old=json.loads((HERE/'fq_20261031/wayfarer_fq_water_rcs_1960.json').read_text())
ship=copy.deepcopy(old);base=G['states']['S4']
ship['base']={'mass_kg':base['mass_t']*1000,'cg_m':base['cg_m'],'inertia_kg_m2':base['inertia_kg_m2']}
ship['provenance']={'authority':'CURRENT GEOMETRY 40s RCS DIAGNOSTIC, not FQ','geometry_sha256':sha}
ship['tanks'][0]['initial_kg']=250000
M=ship['base']['mass_kg']+250000
assert abs(M-G['states']['S1']['mass_t']*1000)<1e-4,'source S1 mass mismatch'
cg=[(ship['base']['mass_kg']*base['cg_m'][i]+250000*ship['tanks'][0]['cg_m'][i])/M for i in range(3)]
assert max(abs(cg[i]-G['states']['S1']['cg_m'][i]) for i in range(3))<.03,'source CG mismatch'
exp={'name':'CURRENT GEOMETRY 40s pitch 180 diagnostic', 'phases':[{'kind':'rcs_turn','duration_s':40.,'axis':'pitch','angle_deg':180.,'post_hold_s':0}],'checks':{}}
print('TRACE START geometry',sha,flush=True)
sim=run(ship,exp,dt=.1,sample_s=5)
series=[];used=0.;peak=0.;peak_nominal=0.;max_count=0.
for step in sim['rcs_trace']:
    flows=[s for s in step['engine_samples'] if s['kind']=='rcs' and s['actual_N']>1.]
    power=sum(s['actual_N']/s['ve_m_s']*(2.6e6+.5*s['ve_m_s']**2) for s in flows)/1e6
    per_step=sum(s['actual_N']/s['ve_m_s']*step['step_s'] for s in flows)
    used+=per_step
    max_count=max(max_count,len(flows));peak=max(peak,power)
    peak_nominal=max(peak_nominal,sum(25e3/s['ve_m_s']*(2.6e6+.5*s['ve_m_s']**2) for s in flows)/1e6)
    series.append({'t_s':step['t_s'],'dt_s':step['step_s'],'ideal_RCS_mw':power,'water_used_kg':per_step,'firing_nozzles':len(flows)})
I=json.loads((ROOT/'config/wayfarer_v05_inputs.json').read_text())
ordinary=.3888965517241379 # matched current single ledger; RCS event also carries hotel
cases={}
for house in (0,50,100):
    deficits=[max(x['ideal_RCS_mw']+ordinary-house,0) for x in series]
    cases[str(house)]={'storage_ideal_gj':sum(p*x['dt_s'] for p,x in zip(deficits,series))/1000,
        'storage_peak_mw':max(deficits),'possible_reactor_surplus_gj':sum(max(house-x['ideal_RCS_mw']-ordinary,0)*x['dt_s'] for x in series)/1000}
out={'status':'CURRENT GEOMETRY NUMERICAL TRACE ONLY; NOT HARDWARE QUALIFICATION','geometry_sha256':sha,
    'dt_s':.1,'scenario':exp['name'],'duration_s':40,'water_consumed_kg':used,
    'trace_ideal_energy_gj':sum(x['ideal_RCS_mw']*x['dt_s'] for x in series)/1000,
    'trace_ideal_peak_mw':peak,'firing_nozzle_max':max_count,'nameplate_peak_proxy_mw':peak_nominal,
    'attitude_error_deg':sim['phases'][0].get('attitude_error_deg'),
    'reconstruction_water_error_kg':used-sim['metrics']['known_propellant_used_kg'],
    'reactor_assist_cases':cases,'trace':series,
    'holds':['conditioning/exhaust is ideal minimum, not actual plant electric load','no guaranteed per-nozzle heat/acceleration coupling','50MW reactor dispatch at 40s time resolution not physically qualified']}
outpath=HERE/'fq_house_power_20261101/RCS_40S_CURRENT_TRACE.json'
outpath.parent.mkdir(exist_ok=True);outpath.write_text(json.dumps(out,indent=1)+'\n')
print('TRACE END',json.dumps({k:v for k,v in out.items() if k!='trace'},indent=1),flush=True)
assert abs(out['reconstruction_water_error_kg'])<.01
