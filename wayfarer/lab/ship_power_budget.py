"""One discrete Wayfarer ship-power ledger plus half-performance sensitivity.
No new flight simulator. All 2226 densities, peak-power and conversion
assumptions are engineering declarations, NOT hardware qualifications.
"""
from pathlib import Path
import math,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
INP=ROOT/'config/wayfarer_v05_inputs.json'
GEO=ROOT/'results/out/wayfarer_v05_geometry.json'
TRACE=ROOT/'lab/flight_qual/fq_house_power_20261101/RCS_40S_CURRENT_TRACE.json'
TRACE60=ROOT/'lab/flight_qual/fq_house_power_20261101/RCS_60S_DEGRADED_TRACE.json'
RES=ROOT/'results/out/ship_power_budget.json'
DOC=ROOT/'docs/SHIP_POWER_BUDGET_2026_11_01.md'

def evaluate():
    I=json.loads(INP.read_text());H=I['ship_power'];G=json.loads(GEO.read_text())
    sha=hashlib.sha256(GEO.read_bytes()).hexdigest()
    trace=json.loads(TRACE.read_text())
    trace60=json.loads(TRACE60.read_text())
    assert trace['geometry_sha256']==sha and trace60['geometry_sha256']==sha,'RCS traces must match current geometry'
    eta=H['direct_conversion_electric_efficiency'];each=H['reactor_net_electric_mw']
    min_power=each*H['reactor_minimum_fraction']
    e_f=math.sqrt(H['peak_store_round_trip_efficiency'])
    e_b=math.sqrt(H['battery_energy_round_trip_efficiency'])
    f_nom=H['peak_store_nominal_mwh'];f_del=f_nom*e_f
    b_nom=H['battery_energy_nominal_mwh'];b_del=b_nom*e_b
    fuel_j=H['fuel_specific_fusion_j_kg']
    hh=I['habitat_heat'];cr=I['cold_running'];rad=I['radiators']
    crew=I['decisions']['people']['crew']+I['decisions']['people']['guests']
    metabolic=crew*hh['metabolic_w_per_person']/1000
    fixed=(hh['avionics_kw']+hh['eclss_galley_kw']+hh['lighting_misc_kw'])/1000
    standby=(cr['plant_standby_kw']+cr['cryo_standby_kw'])/1000
    essential=fixed+standby
    crit=json.loads((ROOT/'config/cert_criteria.json').read_text())
    heat_in_kw=metabolic+fixed*1000
    hp=heat_in_kw*(rad['temperature_k']/hh['radiator']['temperature_k']-1)/crit['G4']['heat_pump_carnot_fraction']/1000
    ordinary=essential+hp
    hab_reject=(heat_in_kw+hp*1000)/1000
    import certify as C
    full_cap=C.rad_net_mw(I,crit,rad['max_span_m'],rad['azimuths_deg'])[0]
    torch_cap=C.rad_net_mw(I,crit,rad['torch_span_m'],rad['azimuths_deg'])[0]
    skin_emissivity=I['skin']['flanks']['modes']['cold_running']['emissivity']
    skin_area=2*math.pi*I['hull']['outer_r_m']*(hh['radiator']['x_m'][1]-hh['radiator']['x_m'][0])*hh['radiator']['share_of_skin']
    leak_kw=skin_emissivity*5.670374419e-8*hh['radiator']['temperature_k']**4*skin_area/1000
    cold_capacity=I['canon']['protected_water_t']*1000*cr['water_cp_kj_kg_k']*cr['buffer_dT_k']/3600
    cold_retained=heat_in_kw*1.25+standby*1000+essential*(1/e_b-1)*1000-leak_kw
    cold_hours=cold_capacity/cold_retained
    routine=H['rcs_nominal_40s_nameplate_mw']*H['rcs_routine_scale_from_40s']
    fast=trace['trace_ideal_peak_mw']
    fastcase=trace['reactor_assist_cases'][str(int(each))]
    fast_store=fastcase['storage_peak_mw']
    fast_energy=fastcase['storage_ideal_gj']/3.6  # GJ -> MWh
    slowcase=trace60['reactor_assist_cases'][str(int(each))]
    degraded_mwh=slowcase['storage_ideal_gj']/3.6
    degraded_peak=slowcase['storage_peak_mw']
    pmad=H['metric_delivered_pm_ad_fraction']
    rows=[]
    def record(name,load,house=0,fly=0,bat=0,charging=0,capacity=None,base_heat=0,
               ship_heat=0,heat_type='active_radiator',duration_s=None,
               store_event_mwh=None,deficits=(),notes=(),reactors=1,hot_fin=None,
               unserved=0,chemical_kg=None,shore=0,torch_self=0):
        known=sum(load.values())
        difference=house+fly+bat+unserved+shore+torch_self-known-charging
        loss=house*(1/eta-1) if house else 0
        flyheat=fly*(1/e_f-1);batheat=bat*(1/e_b-1)
        torch_extract=torch_self/H['torch_self_power_conversion_efficiency_declared'] if torch_self else 0
        heat=loss+base_heat+ship_heat+charging*(1-e_f)+flyheat+batheat+(torch_extract-torch_self)
        named=list(deficits)
        if abs(difference)>1e-6:named.append('POWER_ACCOUNTING_MISMATCH')
        if house>each*reactors+1e-7:named.append('REACTOR_CAPACITY_EXCEEDED')
        if shore>H['docked_shore_power_limit_mw_declared']:named.append('SHORE_POWER_RATING_EXCEEDED')
        if torch_self and name not in ('pulsed_torch_burn','one_unit_failed_torch_magnets'):named.append('TORCH_POWER_CREDIT_OUTSIDE_BURN')
        if reactors and 0<house<min_power-1e-7:named.append('REACTOR_BELOW_10_PERCENT')
        if fly>H['peak_store_discharge_mw']+1e-7:named.append('FLYWHEEL_PEAK_EXCEEDED')
        delivered_event=store_event_mwh if store_event_mwh is not None else (fly*duration_s/3600 if duration_s else 0)
        if delivered_event>f_del+1e-8:named.append('FLYWHEEL_EVENT_ENERGY_EXCEEDED')
        if bat*duration_s/3600>b_del+1e-8 if duration_s else False:named.append('BATTERY_EVENT_ENERGY_EXCEEDED')
        if capacity is not None and heat>capacity+1e-7:named.append('HEAT_REJECTION_CAPACITY_EXCEEDED')
        if unserved:named.append('UNSERVED_LOAD')
        gh=house*1e6*3600/fuel_j/eta*1000
        item=dict(state=name,loads_mw=load,known_load_mw=round(known,6),
           reactors_online=reactors,house_reactor_mw=round(house,6),
           flywheel_discharge_mw=round(fly,6),flywheel_charge_mw=round(charging,6),
           battery_mw=round(bat,6),shore_mw=round(shore,6),torch_self_mw=round(torch_self,6),
           torch_raw_extraction_mw=round(torch_extract,6),unserved_mw=round(unserved,6),
           electric_accounting_mw=round(difference,9),
           house_reactor_waste_heat_mw=round(loss,6),
           heat_rejected_mw=round(heat,6) if heat_type=='active_radiator' else 0,
           heat_scope=heat_type,heat_retained_mw=round(cold_retained/1000,6) if heat_type=='cold_buffer' else 0,
           passive_skin_rejection_mw=round(leak_kw/1000,6) if heat_type=='cold_buffer' else None,
           radiator_capacity_mw=round(capacity,3) if capacity is not None else None,
           house_fuel_g_hr=round(gh,6),duration_s=duration_s,
           flywheel_event_delivered_mwh=round(delivered_event,6) if delivered_event else None,
           chemical_propellant_kg=chemical_kg,
           deficits=named,note='; '.join(notes))
        if hot_fin is not None:item['torch_hot_fins_rejected_mw']=hot_fin
        rows.append(item)
    dock=ordinary+.01
    record('docked_shore_power',{'ordinary_ship_services':ordinary,'docking_control':.01},
           shore=dock,reactors=0,capacity=full_cap,base_heat=hab_reject+standby,
           deficits=['SHORE_PLUG_AND_SUPPLY_INTERFACE_UNQUALIFIED'])
    crown=I['habitat']['decks'][0]['command_layout']['crown_dome']
    a_sun=math.pi*(crown['i4_crown_option_B']['inner_diameter_m']/2)**2
    sun_kw=hh['radiator']['worst_sun_w_m2']*a_sun/1000
    solar_hp=(heat_in_kw+sun_kw)*(rad['temperature_k']/hh['radiator']['temperature_k']-1)/crit['G4']['heat_pump_carnot_fraction']/1000
    solar_load=fixed+standby+solar_hp+.01
    record('docked_crown_open_worst_sun',{'avionics_ECLSS':fixed,'standby':standby,'heat_pump':solar_hp,'docking':.01},
           shore=solar_load,reactors=0,capacity=full_cap,base_heat=(heat_in_kw+sun_kw+solar_hp*1000)/1000+standby,
           deficits=['AOI_OPTICAL_ATTENUATION_UNCREDITED','SHORE_PLUG_AND_SUPPLY_INTERFACE_UNQUALIFIED'])
    record('coast_one_online_min',{'ordinary_ship_services':ordinary},min_power,
           charging=min_power-ordinary,capacity=full_cap,base_heat=hab_reject+standby,
           deficits=['FULL_PULSE_STORE_REACTOR_OFF_OR_BATTERY_CHARGE'])
    record('coast_recharging_fast_flip',{'ordinary_ship_services':ordinary},each,
           charging=each-ordinary,capacity=full_cap,base_heat=hab_reject+standby,
           deficits=['CHARGER_BULK_POWER_UNQUALIFIED'])
    rshort=max(0,ordinary+routine-each)
    record('routine_120s_flip',{'ordinary_ship_services':ordinary,'RCS_120s_UNTRACED_proxy':routine},each,
           fly=rshort,capacity=full_cap,base_heat=hab_reject+standby,
           ship_heat=routine*H['rcs_nozzle_ship_heat_fraction'],duration_s=120,
           deficits=['RCS_ROUTINE_THROTTLE_PROXY_UNTRACED'])
    # Peak row is INSTANTANEOUS. Integrated event draw is the actual 400-step
    # max(load(t)+hotel-50MW,0) time integral, NOT 40s x peak.
    record('fast_40s_flip',{'ordinary_ship_services':ordinary,'RCS_40s_TRACE_PEAK':fast},each,
           fly=fast_store,capacity=full_cap,base_heat=hab_reject+standby,
           ship_heat=fast*H['rcs_nozzle_ship_heat_fraction'],duration_s=40,
           store_event_mwh=fast_energy,
           deficits=['FAST_FLIP_REACTOR_DISPATCH_BUS_HEAT_HARDWARE_UNQUALIFIED'],
           notes=[f"peak {fast:.3f}MW, integrated {trace['trace_ideal_energy_gj']:.3f}GJ, supplemental {fastcase['storage_ideal_gj']:.3f}GJ"])
    torch=H['torch_magnet_burn_only_self_power_mw']
    record('pulsed_torch_burn',{'ordinary_ship_services':ordinary,'magnet_cryocooling':torch},
           min_power,torch_self=torch,charging=min_power-ordinary,
           capacity=torch_cap,base_heat=hab_reject+standby+48,
           hot_fin=round(C.torch_budget()['ship_heat_gw']*1000,3),
           deficits=['TORCH_BURN_ONLY_POWER_TAP_UNQUALIFIED','TORCH_TAP_NOT_DEBITED_FROM_FLIGHT_THRUST'],
           notes=['magnet electric is burn-only torch tap; one house reactor charges store'])
    for mode in ('NORMAL','FAST','EXPEDITE','HARD'):
        cryo=I['canon']['metric_cryo_electrical_mw_at_900K'][mode]*(rad['temperature_k']-20)/880
        field=H['metric_field_control_electric_mw_by_mode'][mode]
        upstream=(cryo+field)/pmad;dist=upstream-cryo-field
        cold=I['canon']['metric_cold_load_kw'][mode]/1000
        record('Metric_'+mode,{'ordinary':ordinary,'scaled_cryo':cryo,'declared_field':field,'PMAD_loss':dist},
           ordinary+upstream,capacity=full_cap,base_heat=hab_reject+standby+cryo+cold+field+dist,
           deficits=['FIELD_POWER_NONCANON_DECLARED','ENVIRONMENTAL_CORRECTION_POWER_OPEN'])
    for mode in ('quiet_reactors_off','cold_running_reactors_off'):
        record(mode,{'essential_habitat':essential},bat=essential,reactors=0,heat_type='cold_buffer',
               deficits=['THERMAL_BUFFER_LIMIT','BATTERY_THERMAL_COUPLING_UNQUALIFIED'],
               notes=[f"battery energy-only {b_del/essential:.2f}h; thermal-buffer {cold_hours:.2f}h"])
    cryo=I['canon']['metric_cryo_electrical_mw_at_900K']['HARD']*(rad['temperature_k']-20)/880
    field=H['metric_field_control_electric_mw_by_mode']['HARD']
    up=(cryo+field)/pmad;loss=up-cryo-field
    record('one_unit_failed_Metric_HARD',{'ordinary':ordinary,'cryo':cryo,'field':field,'PMAD_loss':loss},
           ordinary+up,capacity=full_cap,base_heat=hab_reject+standby+cryo+field+.136+loss,
           deficits=['FAILED_REACTOR_ISOLATION_UNQUALIFIED','METRIC_ENVIRONMENTAL_CORRECTION_OPEN'])
    record('one_unit_failed_torch_magnets',{'ordinary':ordinary,'magnet_cryocooling':torch},
           min_power,torch_self=torch,charging=min_power-ordinary,capacity=torch_cap,
           base_heat=hab_reject+standby+48,hot_fin=round(C.torch_budget()['ship_heat_gw']*1000,3),
           deficits=['FAILED_REACTOR_ISOLATION_UNQUALIFIED','TORCH_BURN_ONLY_POWER_TAP_UNQUALIFIED','TORCH_TAP_NOT_DEBITED_FROM_FLIGHT_THRUST'])
    record('degraded_60s_flip',{'ordinary_ship_services':ordinary,
            'RCS_60s_trace_peak':trace60['trace_ideal_peak_mw']},each,
           fly=degraded_peak,capacity=full_cap,base_heat=hab_reject+standby,
           ship_heat=trace60['trace_ideal_peak_mw']*H['rcs_nozzle_ship_heat_fraction'],
           duration_s=60,store_event_mwh=degraded_mwh,
           deficits=['DEGRADED_FLIP_REAL_BUS_AND_HEAT_UNQUALIFIED'],
           notes=[f"60s supplemental event {degraded_mwh:.4f}MWh peak {degraded_peak:.2f}MW"])
    record('both_house_reactors_failed_hour1',{'ordinary_services':ordinary},bat=ordinary,reactors=0,
           duration_s=3600,capacity=full_cap,base_heat=hab_reject+standby,
           deficits=['FAILED_REACTORS_ACTIVE_COOLING_UNQUALIFIED'])
    remaining=b_del-ordinary
    essential_h=max(0,remaining/essential)
    record('both_house_reactors_failed_essentials',{'essential_services':essential},bat=essential,reactors=0,
           duration_s=3600,capacity=full_cap,base_heat=hab_reject+standby,
           deficits=['NONESSENTIAL_LOADS_SHED','BOTH_FAILED_COOLING_UNQUALIFIED'],
           notes=[f"{essential_h:.2f}h essentials following 1h ordinary, battery energy-only"])
    record('c_lite_slow_attitude_recovery',{},reactors=0,heat_type='chemical_only',
           duration_s=H['c_lite_turn_s'],
           chemical_kg=H['c_lite_propellant_per_slow_turn_kg'],
           deficits=['CHEMICAL_THRUSTER_GEOMETRY_AND_TORQUE_UNQUALIFIED'],
           notes=['~75kg/600s is an idealized scaling hypothesis, not a simulated turn'])
    record('shelter_battery_only',{'shelter_essential':.0006},bat=.0006,reactors=0,
           duration_s=86400,deficits=['DEDICATED_SHELTER_BATTERY_ONLY','24H_ENDURANCE_LIMIT'])
    # Half PERFORMANCE is same installed mass, with 50% stored energy per kg
    # and 50% flywheel pulse specific power. Do not falsely claim unchanged peak.
    half_b=b_del*.5;half_f=f_del*.5;half_peak=H['peak_store_discharge_mw']*.5
    checks=[]
    for row in rows:
        name=row['state']
        energy_req=row['flywheel_event_delivered_mwh'] or 0.
        if name=='fast_40s_flip':
            closes=energy_req<=half_f and row['flywheel_discharge_mw']<=half_peak
            reason=('fast trace supplemental energy and peak power' if not closes else 'fast trace within envelope')
        elif name=='degraded_60s_flip':
            closes=energy_req<=half_f and row['flywheel_discharge_mw']<=half_peak
            reason='60s source-recomputed half-performance, one 50MW reactor'
        elif name=='routine_120s_flip':
            closes=energy_req<=half_f and row['flywheel_discharge_mw']<=half_peak
            reason='routine untraced throttle proxy, energy and power only'
        elif name=='both_house_reactors_failed_hour1':
            closes=ordinary<=half_b
            reason='one hour ordinary services on half-energy battery'
        elif name=='both_house_reactors_failed_essentials':
            closes=half_b>ordinary and (half_b-ordinary)>=essential
            reason='>=1 hour essentials after 1 hour ordinary; full nominal-hours are reduced'
        elif name in ('quiet_reactors_off','cold_running_reactors_off'):
            closes=half_b>=essential*cold_hours
            reason='battery covers existing cold thermal-buffer limit'
        else:
            closes=not bool(row['unserved_mw'])
            reason='electric ledger unchanged; named hardware/physics holds retained'
        checks.append({'state':name,'half_performance_energy_and_power_close':bool(closes),'basis':reason})
    sens={'same_installed_mass':True,'battery_specific_energy_kwh_kg':H['battery_energy_specific_kwh_kg']*.5,
       'flywheel_specific_energy_kwh_kg':H['peak_store_specific_kwh_kg']*.5,
       'flywheel_specific_power_kw_kg':H['peak_store_specific_kw_kg_min']*.5,
       'battery_deliverable_mwh':round(half_b,6),'flywheel_deliverable_mwh':round(half_f,6),
       'flywheel_peak_mw':round(half_peak,3),'fast_flip_stored_need_mwh':round(fast_energy,6),
       'fast_flip_peak_store_mw':round(fast_store,6),
       'degraded_60s_store_need_mwh':round(degraded_mwh,6),
       'degraded_60s_peak_store_mw':round(degraded_peak,6),
       'one_hour_normal_then_essential_hours':round(max(0,(half_b-ordinary)/essential),3),
       'rows':checks}
    return {
      'status':'NON-CANON ENGINEERING SCREEN; NO PHYSICAL QUALIFICATION',
      'geometry_sha256':sha,'input_sha256':hashlib.sha256(INP.read_bytes()).hexdigest(),
      'rcs_trace_sha256':hashlib.sha256(TRACE.read_bytes()).hexdigest(),
      'rcs_trace_60s_sha256':hashlib.sha256(TRACE60.read_bytes()).hexdigest(),
      'reactor':{'count':2,'per_unit_net_mw':each,'minimum_net_mw':min_power,
                 'dry_t':H['reactor_dry_t'],'net_specific_kw_kg':H['reactor_net_specific_kw_kg'],'conversion_efficiency':eta},
      'battery':{'nominal_mwh':b_nom,'deliverable_mwh':round(b_del,6),'mass_t':H['battery_energy_dry_t'],
                 'specific_kwh_kg':H['battery_energy_specific_kwh_kg'],
                 'quiet_essential_hours_energy_only':round(b_del/essential,3),
                 'one_hour_normal_then_essential_hours':round(essential_h,3)},
      'flywheel':{'nominal_mwh':f_nom,'deliverable_mwh':round(f_del,6),'mass_t':H['peak_store_dry_t'],
                  'specific_kwh_kg':H['peak_store_specific_kwh_kg'],'specific_kw_kg':H['peak_store_specific_kw_kg_min'],
                  'peak_mw':H['peak_store_discharge_mw'],'counter_rotating_pairs':True,
                  'burst_containment':'DECLARED included in mass; unqualified',
                  'fast_flip_store_mwh':round(fast_energy,6),
                  'fast_flip_store_peak_mw':round(fast_store,6),
                  'degraded_60s_store_mwh':round(degraded_mwh,6),
                  'degraded_60s_store_peak_mw':round(degraded_peak,6),
                  'recharge_minutes_from_one_reactor':round(fast_energy/(e_f*e_f)/(each-ordinary)*60,3)},
      'c_lite':{'mass_total_t':H['c_lite_total_nominal_t'],'dry_t':H['c_lite_dry_t'],
                'wet_propellant_t':H['c_lite_wet_propellant_t'],'per_slow_turn_kg':H['c_lite_propellant_per_slow_turn_kg'],
                'nominal_turn_count':int(H['c_lite_wet_propellant_t']*1000/H['c_lite_propellant_per_slow_turn_kg']),
                'turn_duration_s':H['c_lite_turn_s'],'status':'DECLARED SCREEN, no chemical thruster torque qualification'},
      'rcs_trace':{k:v for k,v in trace.items() if k!='trace'},
      'rcs_60s_degraded_trace':{k:v for k,v in trace60.items() if k!='trace'},
      'supply_doctrine':{'docked':'shore power, reactors OFF','failure_chain':['reactor B','battery','C-lite slow attitude only'],
       'reactor_bays':['A aft C-ring','B service ring'],'torch_burn_only_magnet_electric_mw':torch,
       'torch_raw_extraction_mw':torch/H['torch_self_power_conversion_efficiency_declared'],
       'torch_house_power_continuous':False},
      'thermal':{'full_strake_capacity_mw':round(full_cap,3),'torch_strake_capacity_mw':round(torch_cap,3),
                 'cold_buffer_kwh':round(cold_capacity,3),'cold_retained_kw':round(cold_retained,3),
                 'cold_thermal_limit_hours':round(cold_hours,3)},
      'metric':{'field_power_status':'NONCANON DECLARED; environmental correction OPEN'},
      'mass':{'dry_t':round(G['dry_t'],6),'S1_wet_t':round(G['states']['S1']['mass_t'],6),
              'electrical_loaded_t':I['ledger']['electrical_t'],'electrical_dry_t':I['ledger']['electrical_dry_t'],
              'monoprop_wet_inside_loaded_electrical_t':H['c_lite_wet_propellant_t'],
              'growth_reserve_t':I['ledger']['engineering_reserve_t'],
              'reserve_headroom_over_5t_t':round(I['ledger']['engineering_reserve_t']-5,6)},
      'states':rows,'half_performance_sensitivity':sens}

def save(r):
    RES.write_text(json.dumps(r,indent=1)+'\n')
    a=r['battery'];f=r['flywheel'];c=r['c_lite'];m=r['mass'];t=r['thermal'];v=r['half_performance_sensitivity']
    lines=['# Wayfarer house power, storage and independent slow recovery | 2026-11-01','',
      '**ENGINEERING CANDIDATE, NON-CANON. NO HARDWARE QUALIFICATION. PR #440 DRAFT, NO MERGE.**','',
      f"Geometry SHA256: `{r['geometry_sha256']}`; exact current 40s RCS trace: `{r['rcs_trace_sha256']}`. Historic FQ/acceptance does not transfer between hashes.",'',
      '**Reactors:** 2×50MW net D–He3, each 5MW minimum online, 2.50t dry, A aft C-ring/B forward service ring; 40kW/kg and 75% net conversion declared. Must cycle off or store/spill surplus; never throttle to sub-MW.','',
      f"**Battery:** {a['nominal_mwh']}MWh nominal / {a['deliverable_mwh']:.3f}MWh discharge, {a['mass_t']:.2f}t at declared {a['specific_kwh_kg']}kWh/kg; quiet 65kW energy-only {a['quiet_essential_hours_energy_only']:.1f}h. Both reactors failed: first 1h normal, then {a['one_hour_normal_then_essential_hours']:.2f}h 65kW essential energy-only.",'',
      f"**Pulse flywheel:** counter-rotating pairs with burst containment, {f['nominal_mwh']}MWh nominal / {f['deliverable_mwh']:.3f}MWh delivered, {f['mass_t']}t at {f['specific_kwh_kg']}kWh/kg and {f['specific_kw_kg']}kW/kg. Declared {f['peak_mw']}MW maximum. The full 40s current-geometry trace requires {f['fast_flip_store_mwh']:.3f}MWh and {f['fast_flip_store_peak_mw']:.1f}MW peak after one steady 50MW reactor. Actual heater/power-switching implementation is OPEN.",'',
      "**Dock and torch:** docked reactors OFF, external shore power 2MW declared. During pulsed torch BURN ONLY magnets get 47.52MW from internal torch power tap (gross 63.36MW at 75% conversion, heat 15.84MW). Source extraction and jet debit physically OPEN; never count it as house generator. Chain: reactor B, battery, C-lite attitude only.",'',
      f"**C-lite:** {c['mass_total_t']:.2f}t provisioned (dry {c['dry_t']:.2f}t + wet {c['wet_propellant_t']:.2f}t), ~{c['per_slow_turn_kg']:.0f}kg for a {c['turn_duration_s']}s recovery, {c['nominal_turn_count']} nominal turns. Dynamics still UNQUALIFIED.",'',
      f"**Mass:** dry {m['dry_t']:.6f}t, loaded S1 {m['S1_wet_t']:.6f}t. Loaded electrical line 55t = 54.85t dry + 0.15t C-lite wet propellant. Engineering reserve **{m['growth_reserve_t']:.6f}t unchanged**; {m['reserve_headroom_over_5t_t']:.3f}t above hard floor. C-lite fuel is a consumable, NOT dry ballast.",'',
      f"**Cold-running thermal bound:** {t['cold_thermal_limit_hours']:.2f}h for the accepted 50t×15K protected-water buffer. Battery energy-only endurance is not a thermal qualification.",'',
      '**Metric:** E1 cryo and PMAD numbers preserved; separately declared field/control NORMAL 1 / FAST 2 / EXPEDITE 3 / HARD 5MW; environmental correction remains OPEN. 2GJ reversible field bank is not a house source.','',
      '| Operating state | House MW | Shore MW | Torch self MW | Flywheel out / charge MW | Battery MW | Loads MW | Heat rejected MW | State deficits |',
      '|---|---:|---:|---:|---:|---:|---|---:|---|']
    for q in r['states']:
        loads=', '.join(f'{k} {val:.3f}' for k,val in q['loads_mw'].items())
        heat=f"{q['heat_rejected_mw']:.3f}" if q['heat_scope']=='active_radiator' else f"{q['heat_retained_mw']:.3f} retained"
        lines.append(f"| {q['state']} | {q['house_reactor_mw']:.3f} | {q['shore_mw']:.3f} | {q['torch_self_mw']:.3f} | {q['flywheel_discharge_mw']:.3f} / {q['flywheel_charge_mw']:.3f} | {q['battery_mw']:.3f} | {loads} | {heat} | {'; '.join(q['deficits']) or 'electrical screen closes'} |")
    lines+=['','### Half battery and flywheel performance at unchanged installation mass','',
      f"Battery delivers {v['battery_deliverable_mwh']:.3f}MWh; flywheel delivers {v['flywheel_deliverable_mwh']:.3f}MWh and at most {v['flywheel_peak_mw']:.1f}MW. Reactor/chemical states unchanged. Half-energy battery carries 1h ordinary followed by {v['one_hour_normal_then_essential_hours']:.2f}h essentials energy-only; cold thermal limit remains. Actual 60s one-reactor store event {v['degraded_60s_store_need_mwh']:.3f}MWh, peak {v['degraded_60s_peak_store_mw']:.1f}MW.",'',
      '| State | Half-performance electrical envelope | Basis |','|---|---|---|']
    for s in v['rows']:lines.append(f"| {s['state']} | {'CLOSES' if s['half_performance_energy_and_power_close'] else 'FAILS'} | {s['basis']} |")
    lines+=['',
      '### Explicit 2226 engineering declarations and outstanding kT choices','',
      '- ACCEPTED BY kT FOR THIS DRAFT: 1.8MWh / 1.8t flywheel, 1kWh/kg, 150kW/kg (270MW max), 90% round trip and counter-rotating contained assembly. Engineering tests of actual rotor packing/containment still OPEN.',
      '- ACCEPTED BY kT FOR THIS DRAFT: reactor A aft C-ring, reactor B forward service ring as separate physical mass envelopes. Independent vessel shielding, reactor-failure isolation and switching NOT QUALIFIED.',
      '- ACCEPTED BY kT FOR THIS DRAFT: if electrical storage half-performance, stretch 40s emergency pitch flip to 60s, using one surviving 50MW house reactor. Source-derived event passes the specified ideal power screen; hardware and other attitude axes OPEN.',
      '- NEW DECLARATION FOR kT: dock external electrical interface rated 2.0MW (current worst solar crown-open dock load ~1.096MW), reactors OFF. Shore-side source/connector, isolation, and thermal fit OPEN.',
      '- NEW DECLARATION FOR kT: pulsed torch supplies 47.52MW net magnet/cryocooling ONLY WHILE BURNING via conversion at 75%: 63.36MW raw torch energy diversion, 15.84MW rejected conversion heat. Not charged to house, but this diversion is NOT YET reflected in the propulsion flight model and real tap/conditioning is OPEN.',
      '- EXISTING UNQUALIFIED DECLARATIONS RETAINED: 2×50MW reactors at 40kW/kg net and 10% minimum; battery 2kWh/kg 90% round trip; C-lite 75kg/600s slow chemical turns and independent torque; Metric field watts NORMAL/FAST/EXPEDITE/HARD 1/2/3/5MW delivered, environment correction HOLD.',
      '- INDEPENDENT CABIN REFUGE: the 0.6kW×24h shelter battery remains isolated; not a replacement for reactor B/battery/C-lite failure chain.',
      '',
      '**Source event scope:** 40s and 60s are full-remass pitch diagnostics with current rigid-body inertia and ideal water heating/jet energy. They do not establish all axes, zero-house-power rescue or actual rotor/chemical hardware.',
      '']
    lines+=['', '**Qualification holds:** flywheel strength, discharge electronics, containment and counter-rotation; battery thermal/isolation; chemical wet containment/nozzle placement and torque; trace-derived ideal RCS power not demonstrated supply; one-reactor 50MW dynamic dispatch; metric correction; full electrical isolation/heat flow. A closed ledger is not a physical flight certificate.','','**Do not merge; preserve full certify verdicts, not inherited historical passes.**','']
    DOC.write_text('\n'.join(lines))
if __name__=='__main__':
    r=evaluate();save(r)
    print('SOURCE',r['geometry_sha256'],'MASS',r['mass'],'BATTERY',r['battery'],'FLYWHEEL',r['flywheel'],'C_LITE',r['c_lite'])
    print('TRACE',r['rcs_trace']['trace_ideal_energy_gj'],r['rcs_trace']['trace_ideal_peak_mw'])
    print('HALF FAILS',[x['state'] for x in r['half_performance_sensitivity']['rows'] if not x['half_performance_energy_and_power_close']])
