"""Single-state-table Wayfarer house-power screening. Not a new runtime simulator.

Numbers are kT's explicit 2226 engineering assumptions, not reactor or storage
qualification. All heat and fuel flows are energy-accounted; unsized loads get
named deficits rather than invented figures.
"""
from pathlib import Path
import math,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
INP=ROOT/'config/wayfarer_v05_inputs.json'
GEO=ROOT/'results/out/wayfarer_v05_geometry.json'
RES=ROOT/'results/out/ship_power_budget.json'
DOC=ROOT/'docs/SHIP_POWER_BUDGET_2026_11_01.md'

def evaluate():
    I=json.loads(INP.read_text());H=I['ship_power'];G=json.loads(GEO.read_text())
    eta=H['direct_conversion_electric_efficiency'];rated=H['reactor_net_electric_mw']
    store_eta=math.sqrt(H['peak_store_round_trip_efficiency'])
    fuel_j_kg=H['fuel_specific_fusion_j_kg']
    hh=I['habitat_heat'];cr=I['cold_running'];rad=I['radiators']
    crew=I['decisions']['people']['crew']+I['decisions']['people']['guests']
    metabolic=crew*hh['metabolic_w_per_person']/1000.
    fixed=(hh['avionics_kw']+hh['eclss_galley_kw']+hh['lighting_misc_kw'])/1000.
    background=(cr['plant_standby_kw']+cr['cryo_standby_kw'])/1000.
    hbase_kw=metabolic+fixed*1000
    hp_w=hbase_kw*(rad['temperature_k']/hh['radiator']['temperature_k']-1)/json.loads((ROOT/'config/cert_criteria.json').read_text())['G4']['heat_pump_carnot_fraction']
    base_elec_mw=fixed+background+hp_w/1000.
    # Torch cryo: reject=48MW, coil coldload=0.48MW. Remaining is drive electrical.
    torch_cryo_drive_mw=47.52
    hard_cryo_elec=I['canon']['metric_cryo_electrical_mw_at_900K']['HARD']*(rad['temperature_k']-20)/880.
    hard_cryo_cold=I['canon']['metric_cold_load_kw']['HARD']/1000.
    fast=H['rcs_nominal_40s_nameplate_mw'];routine=fast*H['rcs_routine_scale_from_40s']
    # Standard open-strake capacity is taken from current G4 source; do not
    # grant cold-running radiators or use torch hot fins to reject house heat.
    import certify as C
    crit=json.loads((ROOT/'config/cert_criteria.json').read_text())
    azs=rad['azimuths_deg']
    cap_full=C.rad_net_mw(I,crit,rad['max_span_m'],azs)[0]
    cap_torch=C.rad_net_mw(I,crit,rad['torch_span_m'],azs)[0]
    # ship skin cold leakage is existing G4 approximation
    s=I['skin']['flanks']['modes']['cold_running']['emissivity']
    area=2*math.pi*I['hull']['outer_r_m']*(hh['radiator']['x_m'][1]-hh['radiator']['x_m'][0])*hh['radiator']['share_of_skin']
    leak_kw=s*5.670374419e-8*hh['radiator']['temperature_k']**4*area/1000
    # Correct reactor heat waste at measured load, not at rated all states.
    rows=[]
    def add(name, loads,store=0, batt=0, heat_plant=None, heat_extra=0, heat_scope='radiator', cap=None, deficits=(),duration_s=None):
        total=sum(loads.values())
        house=max(0,total-store-batt)
        shortage=max(0,house-rated)
        waste=house*(1/eta-1) if heat_plant is None else heat_plant
        # Loads dissipate electrically as specified; propulsive energy leaves
        # as exhaust, only declared 10% nozzle inefficiency stays aboard.
        reject=(waste+heat_extra) if heat_scope=='radiator' else 0
        balance=house+store+batt-total
        issues=list(deficits)
        if shortage>1e-8:issues.append(f'HOUSE_ELECTRIC_CAPACITY_{shortage:.3f}_MW')
        if cap is not None and reject>cap:issues.append(f'RADIATOR_SHORTFALL_{reject-cap:.3f}_MW')
        if abs(balance)>1e-8:issues.append('SOURCE_LOAD_ACCOUNTING_MISMATCH')
        if store>H['peak_store_discharge_mw']+1e-8:issues.append('STORE_PEAK_POWER_EXCEEDED')
        if duration_s and store*duration_s/3600 > H['peak_store_nominal_mwh']*store_eta:
            issues.append('STORE_DELIVERABLE_ENERGY_EXCEEDED')
        fuel_kg_hr=(house*1e6/eta)/fuel_j_kg*3600
        rows.append({'state':name,'loads_mw':loads,'total_load_mw':round(total,6),
          'house_reactor_mw':round(house,6),'charged_store_mw':round(store,6),
          'battery_mw':round(batt,6),'house_reactor_waste_heat_mw':round(waste,6),
          'other_heat_to_reject_mw':round(heat_extra,6),
          'heat_rejected_mw':round(reject,6),'radiator_capacity_mw':round(cap,3) if cap is not None else None,
          'heat_scope':heat_scope,'house_fuel_g_hr':round(fuel_kg_hr*1000,6),
          'house_fuel_g_event':round(fuel_kg_hr*1000*duration_s/3600,6) if duration_s else None,
          'duration_s':duration_s,'deficits':issues,'electrical_balance_mw':round(balance,8)})
    # q_hab exported to 1300K: compute heat-pump reject separately.
    hreject=(hbase_kw+hp_w)/1000
    add('docked',{'avionics_ECLSS_lighting':fixed,'habitat_heat_pump':hp_w/1000,
                  'plant_and_cryo_standby':background,'docking_control':.01},
        heat_extra=hreject+background,cap=cap_full)
    add('coast',{'avionics_ECLSS_lighting':fixed,'habitat_heat_pump':hp_w/1000,
                'plant_and_cryo_standby':background},
        heat_extra=hreject+background,cap=cap_full)
    # The fast-flip store is recharged from the SAME 80MW source in coast,
    # not by multiplying the reactor's output or borrowing a Metric bank.
    charger=rated-base_elec_mw
    add('coast_recharging_store',{'ordinary_ship_services':base_elec_mw,
                                  'flywheel_charger_DC':charger},
        heat_extra=hreject+background+charger*(1-store_eta),cap=cap_full,
        deficits=['CHARGER_ELECTRONICS_NOT_PHYSICALLY_QUALIFIED'])
    add('routine_120s_flip',{'ordinary_ship_services':base_elec_mw,'RCS_120s_throttled_proxy':routine},
        heat_extra=hreject+background+routine*H['rcs_nozzle_ship_heat_fraction'],
        cap=cap_full,duration_s=120,
        deficits=['RCS_120S_THROTTLING_LAW_DECLARED_NOT_TRACED'])
    discharge=fast
    store_losses=fast*(1/store_eta-1)
    add('fast_40s_flip',{'ordinary_ship_services':base_elec_mw,'RCS_40s_emergency':fast},
        store=discharge,heat_extra=hreject+background+fast*H['rcs_nozzle_ship_heat_fraction']+store_losses,
        cap=cap_full,duration_s=40,
        deficits=['FAST_FLIP_TRANSIENT_POWER_BUS_AND_WASTE_HEAT_UNQUALIFIED'])
    add('pulsed_torch_burn',{'ordinary_ship_services':base_elec_mw,'magnet_cryocooling_electric':torch_cryo_drive_mw},
        heat_extra=hreject+background+48.0,cap=cap_torch,
        deficits=['TORCH_1_TO_10_HZ_PULSES_NOT_HOUSE_POWER_SOURCE'])
    rows[-1]['torch_hot_fins_rejected_mw']=round(C.torch_budget()['ship_heat_gw']*1000,3)
    add('Metric_HARD',{'ordinary_ship_services':base_elec_mw,'Metric_cryo_chain_at_1300K':hard_cryo_elec},
        heat_extra=hreject+background+hard_cryo_elec+hard_cryo_cold,cap=cap_full,
        deficits=['METRIC_FIELD_DRIVE_ELECTRIC_DRAW_UNQUANTIFIED'])
    cold_house=fixed+background
    cold_waste=cold_house*(1/eta-1)
    cold_heat_kw=(hbase_kw*1.25+cr['plant_standby_kw']+cr['cryo_standby_kw']+cold_waste*1000-leak_kw)
    cold_kwh=I['canon']['protected_water_t']*1000*cr['water_cp_kj_kg_k']*cr['buffer_dT_k']/3600
    cold_hours=cold_kwh/cold_heat_kw if cold_heat_kw>0 else None
    add('cold_running',{'basic_habitat_electrical':fixed,'plant_and_cryo_standby':background},
        heat_scope='passive_skin_and_water_heat_buffer',deficits=[f'BUFFER_FULL_AFTER_{cold_hours:.2f}_H',
          'REACTOR_DEEP_THROTTLE_UNQUALIFIED'])
    rows[-1]['heat_rejected_mw']=round(leak_kw/1000,6)
    rows[-1]['heat_retained_in_shield_water_mw']=round(cold_heat_kw/1000,6)
    add('shelter_emergency',{'minimal_shelter_24h_backup':.0006,'plant_cryo_and_safety_watch':background},
        cap=cap_full,heat_extra=.0014+background+.0006,
        deficits=['SHELTER_72H_LIFE_SUPPORT_DECLARED_BUT_ONLY_24H_BATTERY_IF_HOUSE_LOST'])
    # Reactor failed: the 24h emergency battery is the only admitted source.
    rows.append({'state':'house_reactor_failed','loads_mw':{'essential_shelter':.0006,
        'ordinary_ship_services_unavailable':base_elec_mw-.0006},
        'total_load_mw':round(base_elec_mw,6),'house_reactor_mw':0.0,
        'charged_store_mw':0.,'battery_mw':.0006,'house_reactor_waste_heat_mw':0.,
        'other_heat_to_reject_mw':0.,'heat_rejected_mw':0.,'radiator_capacity_mw':None,
        'heat_scope':'passive_crown_closed_skin','house_fuel_g_hr':0.,
        'house_fuel_g_event':None,'duration_s':24*3600,
        'electrical_balance_mw':round(.0006-base_elec_mw,6),
        'deficits':['NORMAL_LOADS_UNPOWERED_'+str(round(base_elec_mw-.0006,3))+'_MW',
                    'ESSENTIAL_BATTERY_EXHAUSTED_AFTER_24_H',
                    'PULSED_TORCH_HOUSE_MODE_EMERGENCY_ONLY_NOT_CREDITED']})
    recharge_min=(H['peak_store_nominal_mwh']/store_eta)/(rated-base_elec_mw)*60
    fuel=H['fuel_t']
    geom_hash=hashlib.sha256(GEO.read_bytes()).hexdigest()
    return {'geometry_sha256':geom_hash,'input_sha256':hashlib.sha256(INP.read_bytes()).hexdigest(),
      'status':'ENGINEERING SCREEN / NOT FLIGHT QUALIFICATION',
      'reactor':{'rated_net_electric_mw':rated,'net_specific_kw_kg':H['reactor_net_specific_kw_kg'],
           'dry_mass_t_within_existing_55t_electrical':H['reactor_dry_t'],'direct_conversion_efficiency':eta},
      'store':{'type':H['peak_store'],'nominal_energy_mwh':H['peak_store_nominal_mwh'],
           'deliverable_energy_mwh':round(H['peak_store_nominal_mwh']*store_eta,4),
           '40s_requirement_mwh':round(fast*40/3600,4),
           'mass_t_within_existing_55t_electrical':H['peak_store_dry_t'],
           'energy_density_kwh_kg':H['peak_store_specific_kwh_kg'],
           'discharge_density_kw_kg':H['peak_store_specific_kw_kg_min'],
           'recharge_min_at_coast_house_rating':round(recharge_min,3),
           'fast_flips_per_hour_at_steady_coast':round(60/recharge_min,2),
           'charge_and_discharge_eff_each':round(store_eta,6)},
      'fuel':{'initial_wet_t':fuel,'tank_dry_t_from_reserve':H['fuel_tank_dry_t'],
              'fusion_energy_j_per_kg':fuel_j_kg,'house_consumption_only':True},
      'thermal':{'radiator_span_full_capacity_mw':round(cap_full,3),
          'radiator_span_torch_capacity_mw':round(cap_torch,3),
          'habitat_heat_pump_electric_mw':round(hp_w/1000,5),
          'cold_running_thermal_buffer_kwh':round(cold_kwh,2),
          'cold_running_retained_kw':round(cold_heat_kw,2),
          'cold_running_hours':round(cold_hours,2)},
      'mass':{'S1_wet_t':round(G['states']['S1']['mass_t'],6),
           'dry_t':round(G['dry_t'],6),'reserve_t':I['ledger']['engineering_reserve_t'],
           'remaining_above_5t_floor_t':round(I['ledger']['engineering_reserve_t']-5,6),
           'electrical_original_55t_reallocation_t':H['reactor_dry_t']+H['peak_store_dry_t']},
      'states':rows}
def save(rep):
    RES.write_text(json.dumps(rep,indent=1)+'\n')
    h=rep; R=h['reactor'];S=h['store'];M=h['mass']
    lines=['# Wayfarer ship power budget (kT 2026-11-01)','',
      '**ENGINEERING SCREEN / NOT HARDWARE FLIGHT CERTIFICATION.** No new simulation, Navigator, Metric arrival or canon mutation. Main base ce9ee081.','',
      f'Geometry sha256: `{h["geometry_sha256"]}`.','',
      f'**Source:** dedicated {R["rated_net_electric_mw"]:g} MW net D–He3 reactor and direct converter at declared 2226 **{R["net_specific_kw_kg"]:g} kW/kg** net, {R["direct_conversion_efficiency"]:.0%} electric efficiency. Reactor dry {R["dry_mass_t_within_existing_55t_electrical"]:.2f}t is reallocated WITHIN the existing 55t electrical ledger; not a fresh reserve draw. Relational plant is a consumer, Metric bank is never a power source.','',
      f'**Peak store:** {S["type"]}, {S["nominal_energy_mwh"]:.2f}MWh nominal, {S["deliverable_energy_mwh"]:.2f}MWh delivered at {S["charge_and_discharge_eff_each"]:.1%} charge and discharge; {S["40s_requirement_mwh"]:.2f}MWh for ~519MW×40s. {S["energy_density_kwh_kg"]:g}kWh/kg and {S["discharge_density_kw_kg"]:g}kW/kg declared 2226 **NOT DEMONSTRATED**; {S["mass_t_within_existing_55t_electrical"]:.2f}t dry also reallocated within 55t. At rated 80MW on the coast, **{S["recharge_min_at_coast_house_rating"]:.2f}min recharge, ≈{S["fast_flips_per_hour_at_steady_coast"]:.1f} energy-only recharge cycles/hour** when the house reactor can maintain net output and the thermal system is available. This is **not** an operational manoeuvre rate: actual fast flips consume finite RCS remass (5t ring-fenced) and require nozzle, thermal and control readiness. No back-to-back charged peaks.','',
      f'**Mass:** 5.000t D–He3 separately counted wet; 0.500t dry fuel tank from reserve. Current S1 {M["S1_wet_t"]:.3f}t, dry {M["dry_t"]:.3f}t, reserve {M["reserve_t"]:.3f}t (5t mandatory floor, {M["remaining_above_5t_floor_t"]:.3f}t free). Fuel location is a mass/CG envelope and actual tank packing, containment and cryo support unqualified.','',
      '| State | House MW | Charged store MW | Battery MW | Loads (MW each) | Heat rejected MW / capacity | Outcome | Fuel g/h |',
      '|---|---:|---:|---:|---|---|---|---:|']
    for row in rep['states']:
        loads=', '.join(k+': '+f'{v:.3f}' for k,v in row['loads_mw'].items())
        heat=f'{row["heat_rejected_mw"]:.3f} / '+(str(row['radiator_capacity_mw']) if row['radiator_capacity_mw'] is not None else row['heat_scope'])
        if row.get('torch_hot_fins_rejected_mw'):
            heat+=f'; +{row["torch_hot_fins_rejected_mw"]:.0f} MW hot-fin rejection'
        outcome='**CLOSED (declared basis)**' if not row['deficits'] else '**NAMED DEFICIT:** '+ '; '.join(row['deficits'])
        lines.append(f'| {row["state"]} | {row["house_reactor_mw"]:.3f} | {row["charged_store_mw"]:.3f} | {row["battery_mw"]:.4f} | {loads} | {heat} | {outcome} | {row["house_fuel_g_hr"]:.4f} |')
    lines +=['','**Heat accounting:** house fusion heat not converted to electricity is rejected at the reactor efficiency; cryogenic cooling, habitat heat-pump load, declared local RCS nozzle waste (10%), and flywheel charge/discharge inefficiency are separately tracked. The water-jet kinetic/conditioning energy leaves in exhaust except declared 10% onboard loss. Hot fins handle the pulsed torch GW-class heat separately; the electric house reactor does **not** generate those pulses. Cold running shuts active rejection: thermal energy accumulates in existing 50t protected water, without withdrawing or moving its shield mass.', '',
      f'**Cold running:** only ~{rep["thermal"]["cold_running_hours"]:.2f} h before the existing 50t ×15K heat buffer is filled under this new reactor-waste estimate; cold-running deep turndown and actual thermal coupling remain OPEN. This replaces the earlier ~17h screen based on 10+10kW standby alone.','',
      '**Fuel draw:** D–He3 assumed 18.35MeV per D+He3 reaction / 3.53×10^14J/kg released. This is fuel energy, not electric output; at 75% direct conversion, mode-specific g/h are shown above. Five tonnes is a kT inventory allowance, not a calculated mission fuel requirement. The separately pulsed main torch has its own pellet/fuel basis and is NEVER silently an ordinary house generator. On house failure it is emergency-only and not counted in continuous availability.','',
      '**Named limits (explicit):** routine RCS power 519MW/9 assumes identical 180° angle, thruster throttlability and 40→120s time scaling of required acceleration; it is not a 120s trace. Electric bus/nozzle transient and real flywheel containment are unqualified. Metric field-load beyond mapped 34.8MW cryo is unknown, so HARD cannot be claimed fully closed. House failure has only 0.6kW×24h battery essential backup: unserved normal loads immediately and emergency battery ends after 24h. The proposed 2226 efficiencies and densities are design assumptions, not extant hardware or accepted canon.', '',
      '**Acceptance boundary:** G1/G3/G4 targeted reruns and fresh FQ1–FQ4 are required after any wet-mass change. Previous 7f620c53 visual/radiation/FQ certificates do NOT automatically transfer to this new geometry; no main merge authorised by this engineering study.', '']
    DOC.write_text('\n'.join(lines))
if __name__=='__main__':
    a=evaluate();save(a)
    print('GEO',a['geometry_sha256'],'REACTOR',a['reactor'],'STORE',a['store'])
    for x in a['states']:print(x['state'],'HOUSE',x['house_reactor_mw'],'STORE',x['charged_store_mw'],'HEAT',x['heat_rejected_mw'],'DEFICITS',x['deficits'])
