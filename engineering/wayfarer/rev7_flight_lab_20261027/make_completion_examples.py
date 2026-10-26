"""Small additional NON-CANON fixtures; never rewrites source or historical outputs."""
import copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def load(folder,name):return json.loads((ROOT/folder/(name+'.json')).read_text())
def save(folder,name,obj):(ROOT/folder/(name+'.json')).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def main():
    w=load('configs','wayfarer');sc=load('configs','scout')
    witnesses=json.loads((ROOT/'results/gimbal_static.json').read_text())
    w['name']='Wayfarer historical 8 added gimbals plus 32 fixed; conditional frozen RCS mass'
    w['provenance']['gimbals']='Saved Astra static witnesses; prepositioning excluded; added hardware mass and RCS feed UNKNOWN'
    inward=[copy.deepcopy(e) for e in w['rcs'] if e['id'].endswith('_inward')]
    for k,e in enumerate(inward):
        e['id']+='_extra_gimbal';e['max_N']=300000.
        e['gimbal']={'axial_direction':[1,0,0],'limit_deg':25.,'rate_deg_s':30.,'lag_s':.1,
                     'policy':'phase_fraction','switch_fraction':.5,
                     'positive_angles_deg':witnesses[0]['gimbal_angles_deg'][k],
                     'negative_angles_deg':witnesses[1]['gimbal_angles_deg'][k],
                     'initial_angles_deg':witnesses[0]['gimbal_angles_deg'][k],
                     'initialization_note':'PREPOSITIONED at positive static witness; setup time excluded; no in-run reset'}
    w['rcs']+=inward
    save('configs','wayfarer_gimbal_reference',w)
    cold=copy.deepcopy(w);cold['name']='Wayfarer added gimbals neutral start; same conditional hardware'
    for e in cold['rcs']:
        if 'gimbal' in e:e['gimbal']['initial_angles_deg']=[0,0];e['gimbal']['initialization_note']='Neutral start; all slew time included'
    save('configs','wayfarer_gimbal_cold',cold)
    # A distinct ship uses the SAME two-axis kinematics and allocation, feedback-selected vectors.
    sg=copy.deepcopy(sc);sg['name']='Scout experimental separate RCS tank and feedback gimbals'
    sg['tanks'].append({'id':'rcs_prop','capacity_kg':200.,'initial_kg':200.,'cg_m':[1,1,0],
                        'inertia_full_kg_m2':[[200,0,0],[0,200,0],[0,0,200]]})
    for e in sg['rcs']:
        e['tank']='rcs_prop';e.pop('ve_m_s',None);e['isp_s']=3000.
    for k,e in enumerate([copy.deepcopy(e) for e in sg['rcs'] if e['id'].endswith('_inward')]):
        e['id']+='_extra_gimbal';e['max_N']=12000.;e['installed_mass_kg']=12.
        e['gimbal']=copy.deepcopy(inward[k]['gimbal']);e['gimbal'].update(policy='wrench_sign',wrench_component=4,
                  initial_angles_deg=[0,0],initialization_note='Neutral start; feedback chooses saved direction targets; extra hardware mass assumed 12 kg each')
        sg['rcs'].append(e)
    save('configs','scout_gimbal',sg)
    # Physical engine changes remain explicitly hypothetical fixtures.
    off=copy.deepcopy(sg);off['name']='Scout hypothetical off-axis torch, finite actuators, separate tanks'
    off['torch'][0].update(pos_m=[6.5,.2,.12],auto_trim=False,installed_mass_kg=75.,
                           max_N=200000.,lag_s=.1,command_slew_fullscale_s=2.)
    save('configs','scout_offset_torch',off)
    twin=copy.deepcopy(off);twin['name']='Scout hypothetical twin torch and independent tanks'
    twin['torch']=[copy.deepcopy(off['torch'][0]),copy.deepcopy(off['torch'][0])]
    twin['torch'][0].update(id='torch_port',pos_m=[6.5,.2,.12],max_N=100000.)
    twin['torch'][1].update(id='torch_starboard',pos_m=[6.5,-.2,-.12],max_N=100000.,tank='aux')
    twin['tanks'].append({'id':'aux','capacity_kg':100.,'initial_kg':100.,'cg_m':[0,-1,1],
                         'inertia_full_kg_m2':[[100,0,0],[0,100,0],[0,0,100]]})
    save('configs','scout_twin_torch',twin)
    exhausted=copy.deepcopy(twin);exhausted['name']='Scout twin with exhausted port feed; starboard remains fueled'
    exhausted['tanks'][0]['initial_kg']=0
    save('configs','scout_twin_empty',exhausted)
    # Metric law selection is entirely declarative.
    for ship,name in ((sc,'scout_metric_models'),(off,'scout_offset_metric')):
        ship=copy.deepcopy(ship)
        ship['metric']['experimental_rotation']={'law':'experimental_frame_rotation',
             'modes':copy.deepcopy(ship['metric']['experimental_shift']['modes']),
             'rotation_deg':90.,'rotation_axis':[0,0,1],'pivot_m':[0,0,0],
             'epistemic':'NON-CANON coordinate rotation of r,v,q; no asserted physical energy/momentum closure'}
        save('configs',name,ship)
    def ex(name,phases,checks=None,**kw):save('experiments',name,dict(name=name,phases=phases,checks=checks or {},**kw))
    terminal={'attitude_error_deg':{'max':.25},'rate_deg_s':{'max':.05}}
    for T in (10,12,14):
        ex(f'gimbal{T}',[{'kind':'rcs_turn','duration_s':T,'post_hold_s':4.,'axis':'pitch','angle_deg':180.}],terminal)
    ex('gimbal_constraints',[{'kind':'rcs_turn','duration_s':12.,'post_hold_s':4.,'axis':'pitch',
           'checks':{'peak_force_residual_N':{'max':8000.},'peak_offaxis_torque_Nm':{'max':80000.},
                     'residual_velocity_m_s':{'max':.005},'residual_displacement_m':{'max':.05},
                     'peak_gimbal_rate_deg_s':{'max':30.000001},'peak_gimbal_angle_deg':{'max':25.000001},
                     'gate_entry_s':{'max':12.1},'gate_hold_s':{'min':3.9}}}],terminal)
    ex('scout_gimbal_turn',[{'kind':'rcs_turn','duration_s':20.,'post_hold_s':4.,'axis':'pitch'}],
       {**terminal,'propellant_available':{'min':1},'peak_gimbal_rate_deg_s':{'max':30.000001},
        'peak_gimbal_angle_deg':{'max':25.000001},'residual_velocity_m_s':{'max':.1}})
    for name,hold in (('offset_free',False),('offset_hold',True)):
        ex(name,[{'kind':'torch','duration_s':12.,'hold_attitude':hold}, {'kind':'coast','duration_s':2.,'hold_attitude':hold}],
           {'torch_attitude_drift_deg':{'max':1.},'torch_final_angular_rate_deg_s':{'max':.05},
            'propellant_available':{'min':1},'known_propellant_used_kg':{'min':1.},
            'peak_throttle':{'max':1.000001},'final_angular_rate_deg_s':{'max':.05}})
    ex('twin_burn',[{'kind':'torch','duration_s':12.,'hold_attitude':True}],
       {'propellant_available':{'min':1},'known_propellant_used_kg':{'min':1}})
    for law,key in (('shift','experimental_shift'),('rotation','experimental_rotation'),('canonical','canonical')):
        metric_phase={'kind':'metric','duration_s':80,'model':key,'mode':'NORMAL'}
        if law=='canonical':metric_phase['illustrative_profile']='linear_ramp_plateau_collapse'
        ex('metric_'+law+'_compare',[metric_phase],
           {'metric_path_m':{'min':1}},initial={'position_m':[1000,0,0],'velocity_m_s':[10,0,0],
                                           'omega_rad_s':[0,0,.001]})
    ex('continuous',[{'kind':'torch','duration_s':12.,'hold_attitude':True,
                      'checks':{'phase_attitude_drift_deg':{'max':1.},'propellant_available':{'min':1}}},
          {'kind':'coast','duration_s':2.,'hold_attitude':True},
          {'kind':'rcs_turn','duration_s':20.,'post_hold_s':4.,'axis':'pitch',
           'checks':{**terminal,'gate_hold_s':{'min':3.}}},
          {'kind':'coast','duration_s':2.},
          {'kind':'metric','duration_s':80.,'model':'experimental_rotation','mode':'NORMAL'},
          {'kind':'coast','duration_s':2.}, {'kind':'torch','duration_s':2.,'hold_attitude':True}],
          {'propellant_available':{'min':1},'total_propellant_used_kg':{'min':1},'metric_path_m':{'min':1}},
          sequence_constraints={'metric_entry_max_throttle':1e-6,'coast_before_s':{'metric':2.},
             'allowed_next':{'torch':['coast'],'coast':['rcs_turn','metric','torch'],
                             'rcs_turn':['coast'],'metric':['coast']}})
    pairs=[['wayfarer_gimbal_reference',f'gimbal{T}'] for T in (10,12,14)]
    pairs += [['wayfarer_gimbal_cold','gimbal12'],['wayfarer_gimbal_reference','gimbal_constraints'],
              ['scout_gimbal','scout_gimbal_turn'],['scout_offset_torch','offset_free'],
              ['scout_offset_torch','offset_hold'],['scout_twin_torch','twin_burn'],['scout_twin_empty','twin_burn']]
    pairs += [['scout_metric_models','metric_'+law+'_compare'] for law in ('shift','rotation','canonical')]
    pairs += [['scout_offset_metric','continuous']]
    (ROOT/'completion_manifest.json').write_text(json.dumps(pairs,indent=2)+'\n')
    print('Generated completion configurations, experiments and manifest')
if __name__=='__main__':main()
