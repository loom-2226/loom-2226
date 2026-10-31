"""Generate scratch spacecraft experiment fixtures from Wayfarer source data."""
import copy,json,sys
from pathlib import Path
import numpy as np
from flightlab import crossmat,mass_properties
ROOT=Path(__file__).resolve().parent
REV=ROOT/'source/design/wayfarer/v0.5.7'
sys.path[:0]=[str(ROOT/'source'),str(REV),str(REV/'g10')]
import g10_flight_dynamics as G
C=G.CARD
s1=C['states']['S1'];s4=C['states']['S4']
m1=s1['mass_t']*1000;m4=s4['mass_t']*1000;fm=m1-m4
cg1=np.array(s1['cg_m']);cg4=np.array(s4['cg_m'])
tankcg=(m1*cg1-m4*cg4)/fm
itank=np.array(s1['inertia_tensor_kg_m2'])+m1*crossmat(cg1)-np.array(s4['inertia_tensor_kg_m2'])-m4*crossmat(cg4)-fm*crossmat(tankcg)
assert np.min(np.linalg.eigvalsh(itank))>0
rcs=[{'id':t['cluster']+'_'+t['kind'],'pos_m':list(t['pos']),
      'direction':(np.array(t['f'])/25000).tolist(),'max_N':25000.,
      'lag_s':.05,'command_slew_fullscale_s':10.,
      'tank':None,'ve_m_s':None} for t in G.TH]
modes={}
for name in G.TORCH.MODE_CARDS:
    mdot,ve,F,P=map(float,G.TORCH.mode_outputs(name))
    modes[name]={'max_N':F,'ve_m_s':ve,'working_card_mdot_kg_s':mdot}
cm=G.METRIC.build_metric_closure()
metric_modes={name:{'beta':float(v['beta']),'ramp_s':float(v['ramp_s']),
                    'cold_load_W':float(v['cold_load_w'])} for name,v in cm['modes'].items()}
torch=[{'id':'torch_centerline',
        'pos_m':[52.3,C['torch']['thrust_line_offset_m']['y'],C['torch']['thrust_line_offset_m']['z']],
        'direction':[-1,0,0],'modes':modes,'tank':'remass',
        'jet_power_ceiling_W':C['torch']['jet_power_ceiling_tw']*1e12,
        'accel_cap_g':C['torch']['accel_cap_g'],
        'gimbal_limit_deg':C['torch']['tvc_authority_deg'],
        'auto_trim':True}]
base={'name':'Wayfarer Rev7 S1 reconstructed from S4 and tank',
      'provenance':{'source':'copied LOOM Wayfarer Rev7 snapshot',
                    'card':'source/design/wayfarer/v0.5.7/out/wayfarer_v05_card.json',
                    'fuel_mass_law':'linear fixed-centroid scaling; intermediate S3 not exact',
                    'baseline_engine_mass':'already included in base vehicle mass'},
      'base':{'mass_kg':m4,'cg_m':cg4.tolist(),
              'inertia_kg_m2':s4['inertia_tensor_kg_m2']},
      'components':[],
      'tanks':[{'id':'remass','capacity_kg':fm,'initial_kg':fm,
                'cg_m':tankcg.tolist(),'inertia_full_kg_m2':itank.tolist()}],
      'rcs':rcs,'torch':torch,
      'metric':{'canonical':{'law':'canonical_envelope','modes':metric_modes,
                             'epistemic':'mode envelope only; physical arrival unresolved'},
                'experimental_shift':{'law':'experimental_coordinate_shift','modes':metric_modes,
                     'epistemic':'stipulated coordinate translation without ordinary delta-v; non-canon'}}}
props=mass_properties(base,{'remass':fm})
assert abs(props[0]-m1)<1e-6 and np.linalg.norm(props[1]-cg1)<1e-9
assert np.max(abs(props[2]-np.array(s1['inertia_tensor_kg_m2'])))<1e-4
folder=ROOT/'configs';folder.mkdir(exist_ok=True)
def save(name,obj):(folder/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
save('wayfarer.json',base)
# Exact historical Astra fixed-RCS force-only variants: 24 non-axial nozzles
# share the original mounts and 25 kN axial nozzles are NOT upgraded.
for force_kn in (150,200,300):
    matched=copy.deepcopy(base)
    matched['name']=f'Wayfarer Rev7 original-mount fixed {force_kn} kN RCS study'
    matched['provenance']['alternative']=(
        'Match to study.py model(): non-axial thrusters uprated in place; '
        'eight axial thrusters remain 25 kN; no assumed RCS hardware mass, '
        'exhaust velocity, or tank law; CONDITIONAL physics comparison')
    changed=0
    for e in matched['rcs']:
        if not e['id'].endswith('_axial'):
            e['max_N']=force_kn*1000.
            changed+=1
    assert changed==24
    save(f'wayfarer_original_mount_{force_kn}k.json',matched)
upgrade=copy.deepcopy(base)
upgrade['name']='Wayfarer alternative shifted 300 kN coarse RCS'
for e in upgrade['rcs']:
    if e['id'].endswith('_inward'):
        e['max_N']=300000.
        e['pos_m'][0]+=(-1. if e['pos_m'][0]<20 else 1.)
        e['tank']='remass';e['ve_m_s']=30000.
        upgrade['components'].append({'mass_kg':375.,'cg_m':e['pos_m'],
                                       'inertia_kg_m2':np.zeros((3,3)).tolist()})
upgrade['provenance']['alternative']='300 kN and 375 kg engines are hypothetical design assumptions'
save('wayfarer_rcs_300k.json',upgrade)
alt=copy.deepcopy(base)
alt['name']='Wayfarer conditional twin-torch installation'
alt['torch']=[]
for j,z in enumerate([-.45,.45]):
    t=copy.deepcopy(torch[0]);t['id']='torch_'+str(j+1);t['pos_m'][2]+=z
    for spec in t['modes'].values():spec['max_N']*=.5
    alt['torch'].append(t)
    alt['components'].append({'mass_kg':800.,'cg_m':t['pos_m'],
                              'inertia_kg_m2':np.zeros((3,3)).tolist()})
alt['provenance']['alternative']='two 50 percent engines and masses are experimental'
save('wayfarer_twin_torch.json',alt)
scout={'name':'Scout example cylinder; non-canon',
       'provenance':{'source':'authored scratch fixture, cylinder 90 t, length 12 m, radius 2 m'},
       'base':{'mass_kg':90000.,'cg_m':[0.,0.,0.],
               'inertia_kg_m2':np.diag([180000.,1170000.,1170000.]).tolist()},
       'components':[],
       'tanks':[{'id':'prop','capacity_kg':10000.,'initial_kg':10000.,
                 'cg_m':[0,0,0],'inertia_full_kg_m2':np.diag([20000.,100000.,100000.]).tolist()}],
       'rcs':[],'torch':[{'id':'scout_torch','pos_m':[6.5,0,0],'direction':[-1,0,0],
                          'modes':{'CRUISE':{'max_N':300000.,'ve_m_s':500000.}},
                          'tank':'prop','gimbal_limit_deg':1.,'auto_trim':True}],
       'metric':copy.deepcopy(base['metric'])}
for e in rcs:
    el=copy.deepcopy(e);el['pos_m']=[(el['pos_m'][0]-24.)*.2,
                                    el['pos_m'][1]*.5,el['pos_m'][2]*.5]
    el['max_N']=4000.;el['tank']='prop';el['ve_m_s']=30000.
    scout['rcs'].append(el)
save('scout.json',scout)
print('Generated 4 configs. Wayfarer S1 reconstructed:',props[0],props[1].tolist())
# Portable experiment definitions and a one-command demonstration manifest.
expdir=ROOT/'experiments';expdir.mkdir(exist_ok=True)
def ex(name,phases,checks=None,initial=None):
    obj={'name':name,'phases':phases,'checks':checks or {}}
    if initial:obj['initial']=initial
    (expdir/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
ex('reversal40',[{'kind':'rcs_turn','duration_s':40,'axis':'pitch','angle_deg':180}],
   {'attitude_error_deg':{'max':.25},'rate_deg_s':{'max':.05}})
ex('reversal10',[{'kind':'rcs_turn','duration_s':10,'axis':'pitch','angle_deg':180}],
   {'attitude_error_deg':{'max':.25},'rate_deg_s':{'max':.05}})
ex('translate20',[{'kind':'rcs_translate','duration_s':20,
                   'delta_v_body_m_s':[0.5,0,0]}],
   {'translation_velocity_error_m_s':{'max':0.02},
    'attitude_hold_error_deg':{'max':0.1}})
ex('burn120',[{'kind':'torch','duration_s':120,'mode':'CRUISE','throttle':1.}],
   {'total_propellant_used_kg':{'min':1},
    'torch_attitude_drift_deg':{'max':1.0},'torch_final_angular_rate_deg_s':{'max':.05}})
ex('burn120_rcs_hold',[{'kind':'torch','duration_s':120,'mode':'CRUISE','throttle':1.,'hold_attitude':True}],
   {'known_propellant_used_kg':{'min':1},'torch_attitude_drift_deg':{'max':1.0},
    'torch_final_angular_rate_deg_s':{'max':.05}})
ex('metric_canonical',[{'kind':'metric','duration_s':80,'model':'canonical','mode':'NORMAL',
                       'illustrative_profile':'linear_ramp_plateau_collapse'}],
   {'metric_path_m':{'min':1}})
ex('metric_experimental',[{'kind':'metric','duration_s':80,'model':'experimental_shift','mode':'NORMAL'}],
   {'metric_path_m':{'min':1}})
ex('combined',[{'kind':'torch','duration_s':120,'mode':'CRUISE'},
               {'kind':'coast','duration_s':60},
               {'kind':'rcs_turn','duration_s':40,'axis':'pitch'},
               {'kind':'metric','duration_s':80,'model':'experimental_shift','mode':'NORMAL'}],
   {'attitude_error_deg':{'max':.25},'rate_deg_s':{'max':.05},
    'known_propellant_used_kg':{'min':1},'metric_path_m':{'min':1}})
manifest=[['wayfarer','reversal40'],['wayfarer','translate20'],['wayfarer_rcs_300k','reversal10'],
          ['scout','reversal40'],['wayfarer','burn120'],
          ['wayfarer_twin_torch','burn120'],['wayfarer_twin_torch','burn120_rcs_hold'],['scout','burn120'],
          ['wayfarer','metric_canonical'],['wayfarer','metric_experimental'],
          ['wayfarer','combined']]
(ROOT/'demo_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
