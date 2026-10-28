"""One bounded failure challenge to Wayfarer's TWO visually seamless pressure domes.

NON-CANON. Hold r3.5 37-panel outer armour, 12cm offset, original inner
pressure ellipsoid and two independent pressure panes fixed. Example assumes:
- 0.25 m² effective open fracture area Cd=0.8 (not source),
- 0.25 m² detached full-thickness pane patch (not source),
- zero initial shard velocity (optimistic),
- 85.2 kg/m² fused silica-like reference areal mass,
- 101.3 kPa, T=293.15 K air from source analogue,
- fixed cabin reservoir pressure; isothermal, spatially uniform cavity.
The sound-speed distance proxy, compressible filling and ideal planar fragment motion
are separate scale tests, NOT coupled fracture CFD/FEA or survival proof.
"""
import json,math
from pathlib import Path
import l1_nested_pressure_dome_failover as N

ROOT=Path(__file__).resolve().parent.parent
B=json.loads((ROOT/'command/l1_nested_pressure_dome_failover_results.json').read_text())
OFFSET=.12
G=next(x for x in B['separation_sensitivity'] if x['axial_center_separation_m']==OFFSET)
P0=101300.
T=293.15
R_AIR=287.05
GAMMA=1.4
CD=.8  # assumed, not measured
APERTURE=.25  # m²
FRAGMENT_AREA=.25  # m²: a separate ideal detached pressure-pane patch
AREAL=85.2  # kg/m²
GAP=G['min_free_gap_between_pressure_shells_normal_approx_m']
V=G['inter_pressure_void_volume_m3']
MFRAG=FRAGMENT_AREA*AREAL
SOUND=math.sqrt(GAMMA*R_AIR*T)
CRITICAL=(2/(GAMMA+1))**(GAMMA/(GAMMA-1))
STEP=1.e-5
TIMELIMIT=.5

def mdot(q):
    """Gas from constant-cabin reservoir p0 to evacuated/uniform interspace.
    NASA's isentropic compressible sharp-orifice formula with assumed Cd.
    No dynamics or bulk gas inertia. q must be 0<=q<=p0.
    """
    if q>=P0:return 0.
    ratio=q/P0
    fac=(GAMMA*(2/(GAMMA+1))**((GAMMA+1)/(GAMMA-1))) if ratio<=CRITICAL else (
        2*GAMMA/(GAMMA-1)*(ratio**(2/GAMMA)-ratio**((GAMMA+1)/GAMMA)))
    return CD*APERTURE*P0*math.sqrt(max(fac,0)/(R_AIR*T))

def scenario():
    q=0.; x=0.;vel=0.;tt=0.
    times={};recs=[{'time_s':0.,'cavity_pressure_kPa':0.,'fragment_distance_m':0.,'fragment_speed_m_s':0.,'contact_has_occurred':False,'choked':True}]
    collision=None
    first_choke_end=None
    sampletimes=[i/1000 for i in range(1,101)]
    spos=0
    while tt<TIMELIMIT and (q/P0<.999 or tt<.101):
        flow=mdot(q)
        q_new=min(P0,q+flow*R_AIR*T/V*STEP)
        # Uniform cavity pressure rising reduces the differential pushing
        # fragment, assuming the fragment experiences cavity pressure on front.
        acc=max(0.,P0-q)/AREAL
        vn=vel+acc*STEP
        xn=x+(vel+vn)*STEP/2
        newtt=tt+STEP
        if collision is None and xn>=GAP:
            f=(GAP-x)/(xn-x)
            tc=tt+f*STEP
            vc=vel+f*acc*STEP
            qc=q+f*(q_new-q)
            collision={'time_s':tc,'speed_m_s':vc,
                'cavity_pressure_kPa_at_contact':qc/1000,
                'kinetic_energy_J':MFRAG*vc*vc/2,
                'kinetic_energy_per_fragment_area_J_m2':AREAL*vc*vc/2,
                'fraction_cavity_pressure_at_contact':qc/P0}
        for frac in (.1,.5,.9,.95,.99):
            key=f'pressure_{int(frac*100)}pct_time_s'
            if key not in times and q_new>=P0*frac:
                times[key]=tt+STEP*(P0*frac-q)/(q_new-q)
        if first_choke_end is None and q_new/P0>=CRITICAL:
            first_choke_end=tt+STEP*(P0*CRITICAL-q)/(q_new-q)
        while spos<len(sampletimes) and sampletimes[spos]<=newtt:
            recs.append({'time_s':sampletimes[spos],
                'cavity_pressure_kPa':q_new/1000,
                'fragment_distance_m':min(xn,GAP),
                'fragment_speed_m_s':(vn if collision is None else None),
                'contact_has_occurred':collision is not None,
                'choked':q_new/P0<CRITICAL})
            spos+=1
        x=xn;vel=vn;q=q_new;tt=newtt
    v_const=math.sqrt(2*P0*GAP/AREAL)
    t_const=math.sqrt(2*GAP*AREAL/P0)
    ep_const=P0*GAP*FRAGMENT_AREA
    # kinetic energy in a detached piece if pressure-differential load
    # remains constant during entire displacement: NOT strict physical bound
    # because initial fracture elastic strain & other impulses ignored.
    res={
       'classification':'NON-CANON ONE ILLUSTRATIVE FAILURE, NO CREDIBLE SUCCESS CLAIM',
       'source_pr432_sha':'3485830a56dfead79b2ef8bba031a595b536fbb5',
       'retained_exterior':'37 individually replaceable staggered protective panels unchanged',
       'shell_offset_m':OFFSET,
       'min_normal_gap_m':GAP,
       'inter_pressure_cavity_volume_m3':V,
       'reference_cabin_pressure_kPa':P0/1000,
       'reference_temperature_K':T,
       'event':'A 0.25m² independent effective breach opens suddenly; a full-thickness 0.25m² brittle shell fragment is detached and starts from rest, propelled normal to shell toward backup. Cavity is evacuated and isolated to external vacuum.',
       'assumed_effective_breach_area_m2':APERTURE,
       'assumed_fragment_area_m2':FRAGMENT_AREA,
       'assumed_discharge_coefficient':CD,
       'assumed_fragment_areal_density_kg_m2':AREAL,
       'fragment_mass_kg':MFRAG,
       'speed_of_sound_in_air_m_s':SOUND,
       'sound_speed_gap_transit_PROXY_s':GAP/SOUND,
       'critical_choked_ambient_pressure_ratio':CRITICAL,
       'initial_choked_mass_flow_kg_s':mdot(0),
       'constant_full_pressure_driving_comparison':{
          'contact_time_s':t_const,'impact_speed_m_s':v_const,
          'kinetic_energy_J':ep_const},
       'uniform_cavity_fill_with_fragment':{
          'contact':collision,
          'time_cavity_leaves_choked_regime_s':first_choke_end,
          'pressure_transition_times_s':times,
          'sampled_time_series':recs,
          'end_pressure_kPa':q/1000,
          'integration_end_s':tt,
          'ideal_full_cavity_gas_mass_kg':P0*V/(R_AIR*T)},
       'do_not_claim':[
          'The cavity starts evacuated: sound does not travel in vacuum. Gap divided by cabin air sound speed is only a distance scale, not a predicted arrival time for a shock or gas front.',
          'Unknown fragment size distributions, initial velocities, crack-front velocity, elastic stored energy, brittle fragmentation topology or collision angle; zero launch speed is optimistic.',
          'A 0.25m² effective opening and a 0.25m² detached fragment are separate assumptions; not a coupled fracture-field calculation. Detached fragment might occlude the rupture.',
          'Uniform isothermal pressure assumes a fixed 101.3kPa cabin reservoir and well-mixed cavity; in first milliseconds air forms a jet and shock and may hit backup locally; cavity pressure field and rate can differ enormously.',
          'Fragment accelerates under uniform p_cabin-p_cavity pressure and stays intact at its normal areal mass; flow drag, orientation and 3D orbital paths omitted.',
          'The computed constant-pressure case is a pressure-work comparator, NOT a real upper energy bound: initial elastic fracture release and high-speed ejecta can increase fragment kinetic energy.',
          'Contact speed and impact energy do not imply pane break or survival; backup fracture toughness, compliant stop distance and contact stress untested.',
          'The gap is smallest sampled normal separation near r3.5. A pane piece from another radius may travel further; this case chooses a short collision path.',
          'No transient rim pressure forces, post-failure cavity seal, wave focusing, stress concentration or secondary shattering calculation.',
          'NASA-STD-5018 says redundant pane must include primary fracture dynamic effects; this toy test is not that verification.'
       ]}
    assert collision is not None and collision['time_s']>GAP/SOUND
    assert collision['kinetic_energy_J']<=ep_const+1e-7
    assert times['pressure_90pct_time_s']>collision['time_s']
    assert res['uniform_cavity_fill_with_fragment']['ideal_full_cavity_gas_mass_kg']>3
    return res
if __name__=='__main__':
    r=scenario()
    c=r['uniform_cavity_fill_with_fragment']['contact']
    print('SHARD mass',r['fragment_mass_kg'],'kg, gap',r['min_normal_gap_m']*100,'cm')
    print('GAP/SOUND SPEED proxy ms',r['sound_speed_gap_transit_PROXY_s']*1e3,'initial mdot kg/s',r['initial_choked_mass_flow_kg_s'])
    print('CONSTANT force contact ms',r['constant_full_pressure_driving_comparison']['contact_time_s']*1e3,
        'v',r['constant_full_pressure_driving_comparison']['impact_speed_m_s'],
        'energy J',r['constant_full_pressure_driving_comparison']['kinetic_energy_J'])
    print('PRESSURE RISING contact ms',c['time_s']*1000,'v',c['speed_m_s'],'E J',c['kinetic_energy_J'],'Pc kPa',c['cavity_pressure_kPa_at_contact'])
    print('CAVITY transitions',r['uniform_cavity_fill_with_fragment']['pressure_transition_times_s'])
    (ROOT/'command/l1_primary_fracture_one_case_results.json').write_text(json.dumps(r,indent=2))
