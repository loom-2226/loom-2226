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
    """A discrete operating ledger, not an evolving powerplant or flight simulator."""
    I=json.loads(INP.read_text()); H=I["ship_power"]; G=json.loads(GEO.read_text())
    eta=H["direct_conversion_electric_efficiency"]
    each=H["reactor_net_electric_mw"]; count=H["reactor_count"]
    minimum=each*H["reactor_minimum_fraction"]
    charge_eff=discharge_eff=math.sqrt(H["peak_store_round_trip_efficiency"])
    energy=H["peak_store_nominal_mwh"]
    deliverable=energy*discharge_eff
    fuel_j=H["fuel_specific_fusion_j_kg"]
    hh=I["habitat_heat"]; cr=I["cold_running"]; rad=I["radiators"]
    crew=I["decisions"]["people"]["crew"]+I["decisions"]["people"]["guests"]
    metabolic=crew*hh["metabolic_w_per_person"]/1000
    fixed=(hh["avionics_kw"]+hh["eclss_galley_kw"]+hh["lighting_misc_kw"])/1000
    standby=(cr["plant_standby_kw"]+cr["cryo_standby_kw"])/1000
    basic=fixed+standby
    crit=json.loads((ROOT/"config/cert_criteria.json").read_text())
    heat_in_kw=(metabolic+fixed*1000)
    heat_pump=heat_in_kw*(rad["temperature_k"]/hh["radiator"]["temperature_k"]-1)/crit["G4"]["heat_pump_carnot_fraction"]/1000
    ordinary=basic+heat_pump
    hab_reject=(heat_in_kw+heat_pump*1000)/1000
    import certify as C
    full_cap=C.rad_net_mw(I,crit,rad["max_span_m"],rad["azimuths_deg"])[0]
    torch_cap=C.rad_net_mw(I,crit,rad["torch_span_m"],rad["azimuths_deg"])[0]
    skin_emissivity=I["skin"]["flanks"]["modes"]["cold_running"]["emissivity"]
    skin_area=2*math.pi*I["hull"]["outer_r_m"]*(hh["radiator"]["x_m"][1]-hh["radiator"]["x_m"][0])*hh["radiator"]["share_of_skin"]
    leak_kw=skin_emissivity*5.670374419e-8*hh["radiator"]["temperature_k"]**4*skin_area/1000
    cold_buffer_kwh=I["canon"]["protected_water_t"]*1000*cr["water_cp_kj_kg_k"]*cr["buffer_dT_k"]/3600
    store_idle=basic
    store_idle_heat=store_idle*(1/discharge_eff-1)
    cold_retained_kw=heat_in_kw*1.25+standby*1000+store_idle_heat*1000-leak_kw
    cold_hours=cold_buffer_kwh/cold_retained_kw
    store_idle_h=deliverable/store_idle
    store_ordinary_h=deliverable/ordinary
    fast=H["rcs_nominal_40s_nameplate_mw"]
    routine=fast*H["rcs_routine_scale_from_40s"]
    pmad=H["metric_delivered_pm_ad_fraction"]
    rows=[]

    def record(state,load,house,store=0,battery=0,charging=0,capacity=None,
               base_heat=0,ship_heat=0,heat_type="active_radiator",
               duration_s=None,extra=(),technical_deficits=(),reactors_on=1,
               hot_fin_mw=None,unserved=0):
        supplied=house+store+battery+unserved
        consumed=sum(load.values())+charging
        # Any unserved capacity is kept separate from supplied MW, NOT magically generated.
        accounting=round(supplied-consumed,9)
        losses=house*(1/eta-1) if house else 0
        charge_heat=charging*(1-charge_eff)
        discharge_heat=store*(1/discharge_eff-1)
        rejected=losses+base_heat+ship_heat+charge_heat+discharge_heat
        named=list(technical_deficits)
        if abs(accounting)>1e-6:named.append("POWER_ACCOUNTING_MISMATCH")
        if house>each*reactors_on+1e-8:named.append("REACTOR_MAX_CAPACITY_EXCEEDED")
        if reactors_on and 0<house<minimum-1e-8:named.append("REACTOR_UNDER_10_PERCENT_MINIMUM")
        if store>H["peak_store_discharge_mw"]+1e-8:named.append("FLYWHEEL_PEAK_POWER_EXCEEDED")
        if duration_s and store*duration_s/3600>deliverable+1e-8:named.append("FLYWHEEL_EVENT_ENERGY_EXCEEDED")
        if capacity is not None and rejected>capacity+1e-8:named.append("RADIATOR_CAPACITY_EXCEEDED")
        if unserved>1e-9:named.append("UNSERVED_ELECTRIC_LOAD")
        fuel_gh=house*1e6*3600/fuel_j/eta*1000
        row={
            "state":state,"loads_mw":load,"known_load_mw":round(sum(load.values()),6),
            "reactors_online":reactors_on,"house_reactor_mw":round(house,6),
            "flywheel_discharge_mw":round(store,6),"flywheel_charge_mw":round(charging,6),
            "battery_mw":round(battery,6),"unserved_mw":round(unserved,6),
            "electric_accounting_mw":accounting,
            "house_reactor_waste_heat_mw":round(losses,6),
            "heat_rejected_mw":round(rejected if heat_type=="active_radiator" else 0,6),
            "heat_scope":heat_type,"heat_retained_mw":round(cold_retained_kw/1000,6) if heat_type=="cold_buffer" else 0,
            "passive_skin_rejection_mw":round(leak_kw/1000,6) if heat_type=="cold_buffer" else None,
            "radiator_capacity_mw":round(capacity,3) if capacity is not None else None,
            "house_fuel_g_hr":round(fuel_gh,6),
            "house_fuel_g_event":round(fuel_gh*duration_s/3600,6) if duration_s is not None else None,
            "duration_s":duration_s,"deficits":named,
            "note":"; ".join(extra)}
        if hot_fin_mw is not None:row["torch_hot_fins_rejected_mw"]=hot_fin_mw
        rows.append(row)

    # Online house reactors must make at least 5MW; the extra electric power
    # charges a flywheel ONLY until its finite capacity is reached.
    dock=ordinary+.01
    record("docked_one_online_min",{"avionics_ECLSS_lighting":fixed,"heat_pump":heat_pump,
       "plant_and_cryo_standby":standby,"docking_control":.01},minimum,
       charging=minimum-dock,capacity=full_cap,
       base_heat=hab_reject+standby,
       technical_deficits=["FULL_STORE_REQUIRES_REACTOR_CYCLE_OFF"],
       extra=["reactor at 10% minimum; surplus goes to store while not full"])
    # Crown open at worst Venus sunlight needs extra heat-pump input. No optical credit.
    crown=I["habitat"]["decks"][0]["command_layout"]["crown_dome"]
    a_sun=math.pi*(crown["i4_crown_option_B"]["inner_diameter_m"]/2)**2
    sun_kw=hh["radiator"]["worst_sun_w_m2"]*a_sun/1000
    solar_hp=(heat_in_kw+sun_kw)*(rad["temperature_k"]/hh["radiator"]["temperature_k"]-1)/crit["G4"]["heat_pump_carnot_fraction"]/1000
    solar_power=fixed+standby+solar_hp+.01
    solar_reject=(heat_in_kw+sun_kw+solar_hp*1000)/1000
    record("docked_crown_open_worst_sun",{"avionics_ECLSS_lighting":fixed,
           "solar_aperture_heat_pump":solar_hp,"standby":standby,"docking_control":.01},
       minimum,charging=minimum-solar_power,capacity=full_cap,
       base_heat=solar_reject+standby,
       technical_deficits=["FULL_STORE_REQUIRES_REACTOR_CYCLE_OFF",
           "AOI_OPTICAL_ATTENUATION_NOT_CREDITED"],
       extra=[f"crown-open solar: {sun_kw:.1f} kW additional to enclosed state"])
    record("coast_one_online_min",{"ordinary_ship_services":ordinary},minimum,
       charging=minimum-ordinary,capacity=full_cap,
       base_heat=hab_reject+standby,
       technical_deficits=["FULL_STORE_REQUIRES_REACTOR_CYCLE_OFF"],
       extra=["minimum stable output, no 0.389MW idle generator fiction"])
    record("coast_recharging_fast_flip",{"ordinary_ship_services":ordinary},each,
       charging=each-ordinary,capacity=full_cap,base_heat=hab_reject+standby,
       technical_deficits=["CHARGER_BULK_POWER_HARDWARE_UNQUALIFIED"])
    # One unit cannot meet the routine-flip throttled proxy alone.
    routine_short=ordinary+routine-each
    record("routine_120s_flip",{"ordinary_ship_services":ordinary,
       "RCS_120s_throttled_proxy":routine},each,store=routine_short,
       capacity=full_cap,base_heat=hab_reject+standby,
       ship_heat=routine*H["rcs_nozzle_ship_heat_fraction"],duration_s=120,
       technical_deficits=["RCS_THROTTLING_1_OVER_T_SQUARED_NOT_TRACED"])
    # Emergency uses the precharged wheel, leaving reactor capacity uncredited
    # and the RCS high-rate bus qualified only at a declared screening level.
    record("fast_40s_flip",{"ordinary_ship_services":ordinary,"RCS_40s_emergency":fast},
       0,store=ordinary+fast,reactors_on=0,capacity=full_cap,
       base_heat=hab_reject+standby,ship_heat=fast*H["rcs_nozzle_ship_heat_fraction"],
       duration_s=40,technical_deficits=["FAST_FLIP_BUS_AND_THERMAL_TRANSIENT_UNQUALIFIED"])
    torch_load=47.52+ordinary
    record("pulsed_torch_burn",{"ordinary_ship_services":ordinary,"magnet_cryocooling_electric":47.52},
       torch_load,capacity=torch_cap,base_heat=hab_reject+standby+48,
       hot_fin_mw=round(C.torch_budget()["ship_heat_gw"]*1000,3),
       technical_deficits=["PULSED_MAIN_TORCH_NOT_A_HOUSE_GENERATOR"])
    for mode in ["NORMAL","FAST","EXPEDITE","HARD"]:
        cryo=I["canon"]["metric_cryo_electrical_mw_at_900K"][mode]*(rad["temperature_k"]-20)/880
        field=H["metric_field_control_electric_mw_by_mode"][mode]
        delivered=cryo+field
        upstream=delivered/pmad
        dist_heat=upstream-delivered
        house=ordinary+upstream
        cold=I["canon"]["metric_cold_load_kw"][mode]/1000
        record("Metric_"+mode,{"ordinary_ship_services":ordinary,
            "canon_cryo_scaled_1300K_delivered":cryo,
            "declared_field_and_control_delivered":field,
            "E1_PMAD_distribution_losses":dist_heat},
            house,capacity=full_cap,base_heat=hab_reject+standby+cryo+cold+field+dist_heat,
            technical_deficits=["FIELD_CONTROL_"+mode+"_NONCANON_DECLARATION",
               "ENVIRONMENTAL_CORRECTION_POWER_STILL_OPEN"])
    record("quiet_reactors_off",{"essential_habitat":store_idle},0,
       store=store_idle,reactors_on=0,heat_type="cold_buffer",
       technical_deficits=["COLD_BUFFER_EXHAUSTED_BEFORE_FLYWHEEL",
           "QUIET_SKIN_EMISSIVITY_DECLARED"],
       extra=[f"flywheel ~{store_idle_h:.2f}h ideal discharge; cold thermal buffer ~{cold_hours:.2f}h"])
    record("cold_running_reactors_off",{"essential_habitat":store_idle},0,
       store=store_idle,reactors_on=0,heat_type="cold_buffer",
       technical_deficits=["COLD_BUFFER_EXHAUSTED_BEFORE_FLYWHEEL",
          "FLYWHEEL_THERMAL_COUPLING_UNQUALIFIED"],
       extra=[f"0 house-fuel; flywheel ~{store_idle_h:.2f}h energy limit; cold thermal ~{cold_hours:.2f}h"])
    # Single reactor failure: no 100MW assumption; one remains able to carry
    # the full HARD metric card and the torch-magnet load independently.
    hard_cryo=I["canon"]["metric_cryo_electrical_mw_at_900K"]["HARD"]*(rad["temperature_k"]-20)/880
    hard_field=H["metric_field_control_electric_mw_by_mode"]["HARD"]
    hard_up=(hard_cryo+hard_field)/pmad
    hard_loss=hard_up-hard_cryo-hard_field
    record("one_unit_failed_Metric_HARD",{"ordinary_ship_services":ordinary,
        "canon_cryo_scaled_1300K_delivered":hard_cryo,
        "declared_field_control":hard_field,"PMAD_loss":hard_loss},
        ordinary+hard_up,capacity=full_cap,base_heat=hab_reject+standby+hard_cryo+hard_field+.136+hard_loss,
        technical_deficits=["FAILED_REACTOR_ISOLATION_UNQUALIFIED",
            "ENVIRONMENTAL_CORRECTION_POWER_STILL_OPEN"])
    record("one_unit_failed_torch_magnets",{"ordinary_ship_services":ordinary,
        "magnet_cryocooling_electric":47.52},torch_load,
        capacity=torch_cap,base_heat=hab_reject+standby+48,
        hot_fin_mw=round(C.torch_budget()["ship_heat_gw"]*1000,3),
        technical_deficits=["FAILED_REACTOR_ISOLATION_UNQUALIFIED"])
    record("both_house_reactors_failed_flywheel",{"ordinary_ship_services":ordinary},
       0,store=ordinary,reactors_on=0,capacity=full_cap,
       base_heat=hab_reject+standby,
       technical_deficits=["FLYWHEEL_EXHAUSTS_AFTER_"+f"{store_ordinary_h:.2f}"+"_H",
         "FAILED_PLANT_ACTIVE_RADIATORS_UNQUALIFIED"],
       extra=["two house reactors off; normal services charged-store only"])
    # Torch emergency source is explicitly NOT quantified; do not mint a watt
    # or count a 1–10Hz pulsed propulsion source as a continuous alternator.
    record("torch_emergency_house_unqualified",{"ordinary_ship_services":ordinary},0,
       reactors_on=0,unserved=ordinary,technical_deficits=[
       "TORCH_EMERGENCY_HOUSE_OUTPUT_NOT_SIZED","CONTINUOUS_SUPPLY_NOT_AUTHORISED"],
       extra=["fallback attempted; fuel/energy/pulse interface OPEN"])
    record("shelter_battery_only",{"essential_shelter":.0006},0,
       battery=.0006,reactors_on=0,duration_s=86400,
       technical_deficits=["24_H_BATTERY_EXHAUSTION",
         "NORMAL_SHIP_SERVICES_SHED","72_H_SHELTER_STORE_NOT_72_H_ELECTRIC_SOURCE"],
       extra=["14.4kWh essential energy, declared 4kWh/kg -> 3.6kg batteries"])
    # Recharge from a charged-store-depleted fast event, one reactor at its
    # full 50MW net electric, after the required 0.389MW ordinary load.
    fast_need=(ordinary+fast)*40/3600
    fast_recharge_hours=(fast_need/(charge_eff*discharge_eff))/(each-ordinary)
    cold_flywheel_energy=deliverable
    return {
      "status":"NON-CANON ENGINEERING SCREEN / NOT HARDWARE QUALIFICATION",
      "geometry_sha256":hashlib.sha256(GEO.read_bytes()).hexdigest(),
      "input_sha256":hashlib.sha256(INP.read_bytes()).hexdigest(),
      "reactor":{"count":count,"per_unit_net_mw":each,"total_net_mw":each*count,
        "minimum_net_mw_per_online_unit":minimum,
        "net_specific_kw_kg":H["reactor_net_specific_kw_kg"],
        "total_dry_mass_t_within_55t_electrical":H["reactor_dry_t"],
        "direct_conversion_efficiency":eta},
      "store":{"type":H["peak_store"],"nominal_energy_mwh":energy,
        "deliverable_energy_mwh":round(deliverable,5),
        "mass_t_within_55t_electrical":H["peak_store_dry_t"],
        "density_kwh_kg":H["peak_store_specific_kwh_kg"],
        "discharge_power_density_kw_kg":H["peak_store_specific_kw_kg_min"],
        "peak_discharge_mw":H["peak_store_discharge_mw"],
        "fast_40s_event_mwh":round(fast_need,5),
        "fast_40s_recharge_min_one_unit":round(fast_recharge_hours*60,3),
        "fast_flips_per_hour_energy_only_one_unit":round(1/fast_recharge_hours,2),
        "minimum_reactor_coast_charge_mw":round(minimum-ordinary,5),
        "store_discharge_eff":round(discharge_eff,8),
        "store_charge_eff":round(charge_eff,8),
        "quiet_65kw_energy_limit_hours":round(store_idle_h,3),
        "normal_services_energy_limit_hours_both_reactors_failed":round(store_ordinary_h,3)},
      "metric":{"canon_900k_cryo_delivered_mw":I["canon"]["metric_cryo_electrical_mw_at_900K"],
        "scaling_to_reject_k":rad["temperature_k"],"pmad_delivery_fraction":pmad,
        "additional_field_and_control_mw_declared_noncanon":H["metric_field_control_electric_mw_by_mode"],
        "environmental_correction_power":"OPEN, not inferred from 5MW declared field/control allowance",
        "field_source":"Engineering declaration because frozen E1 Metric canon has no separate steady field-power MW"},
      "thermal":{"full_strake_capacity_mw":round(full_cap,3),
         "torch_strake_capacity_mw":round(torch_cap,3),
         "cold_skin_passive_leak_kw":round(leak_kw,4),
         "cold_buffer_capacity_kwh":round(cold_buffer_kwh,3),
         "cold_buffer_retained_kw":round(cold_retained_kw,4),
         "cold_hours_before_heat_buffer_full":round(cold_hours,3)},
      "fuel":{"initial_house_wet_t":H["fuel_t"],"dry_tank_from_reserve_t":H["fuel_tank_dry_t"],
         "fusion_energy_j_kg":fuel_j,"fuel_burn_by_mode_in_states":True},
      "mass":{"S1_wet_t":round(G["states"]["S1"]["mass_t"],6),
          "dry_t":round(G["dry_t"],6),
          "engineering_reserve_t":I["ledger"]["engineering_reserve_t"],
          "headroom_over_5t_floor_t":round(I["ledger"]["engineering_reserve_t"]-5,6),
          "electrical_line_t":I["ledger"]["electrical_t"],
          "reactors_plus_store_reallocated_in_electrical_t":H["reactor_dry_t"]+H["peak_store_dry_t"]},
      "states":rows}

def save(rep):
    RES.write_text(json.dumps(rep,indent=1)+"\n")
    r=rep["reactor"];st=rep["store"];t=rep["thermal"];m=rep["mass"]
    lines=[
      "# Wayfarer two-reactor ship power ledger | 2026-11-01",
      "",
      "**ENGINEERING CANDIDATE, NON-CANON, NO HARDWARE CERTIFICATION.** kT decisions on PR #440. No Navigator, Metric arrival or main merge. Previous 7f620c53 G6/G12 certification does not apply to a new geometry source hash.",
      "",
      f"New physical source hash: `{rep['geometry_sha256']}`.",
      "",
      f"**House source:** **2×{r['per_unit_net_mw']:.0f}MW** D–He3 direct-conversion reactors, **{r['minimum_net_mw_per_online_unit']:.0f}MW minimum per live unit (10%)**, declared 2226 {r['net_specific_kw_kg']:.0f}kW/kg net, 75% conversion. **{r['total_dry_mass_t_within_55t_electrical']:.2f}t** for both inside existing 55t electrical allocation. One unit can independently carry coast/Metric/torch magnet load; 120s RCS uses one unit + flywheel. Surplus from a live reactor charges the store, but **once full it must shut off/cycle**. Never claim 0.389MW continuous plant idle.",
      "",
      f"**Storage:** {st['nominal_energy_mwh']:.2f}MWh flywheel (deliverable {st['deliverable_energy_mwh']:.2f}MWh), {st['mass_t_within_55t_electrical']:.2f}t in existing electrical allocation, declared 2226 {st['density_kwh_kg']:.0f}kWh/kg and {st['discharge_power_density_kw_kg']:.0f}kW/kg, 90% roundtrip. Emergency fast flip {st['fast_40s_event_mwh']:.3f}MWh, **{st['fast_40s_recharge_min_one_unit']:.2f} minutes** to refill that used energy from one 50MW reactor. **{st['fast_flips_per_hour_energy_only_one_unit']:.2f} theoretical electric recharge cycles/hour**, NOT permission for that manoeuvre rate or unlimited RCS remass.",
      "",
      f"**Quiet and cold:** BOTH house reactors OFF. Flywheel supplies {0.065:.3f}MW essentials, {st['quiet_65kw_energy_limit_hours']:.1f} h energy-only endurance, but existing 50t×15K thermal buffer fills after **{t['cold_hours_before_heat_buffer_full']:.2f}h** at ~{t['cold_buffer_retained_kw']:.1f}kW retained. No 200×–4000× speculative reactor throttling.",
      "",
      "**Metric authority distinction:** E1 canon supplies cryogenic load and PMAD efficiency, not standalone Metric field-power watts. The extra delivered control/field power is **declared NON-CANON** NORMAL 1MW / FAST 2MW / EXPEDITE 3MW / HARD 5MW. Apply E1 0.98×0.96 PMAD efficiency to cryo + field delivery, and count distribution losses as heat. Environmental-correction load remains explicitly OPEN, not hidden in the 5MW.",
      "",
      "| Operating state | House MW | Flywheel MW out/in | Battery MW | Loads (MW, components) | Rejected MW | Deficit or closure | House fuel g/h |",
      "|---|---:|---:|---:|---|---:|---|---:|"
    ]
    for q in rep["states"]:
        load=", ".join(f"{k} {v:.3f}" for k,v in q["loads_mw"].items())
        fw=f'{q["flywheel_discharge_mw"]:.3f} / {q["flywheel_charge_mw"]:.3f}'
        rejection=f'{q["heat_rejected_mw"]:.3f}'
        if q["heat_scope"]=="cold_buffer":
            rejection=f'{q["passive_skin_rejection_mw"]:.3f} passive, {q["heat_retained_mw"]:.3f} retained'
        if q.get("torch_hot_fins_rejected_mw"):
            rejection+=f' + {q["torch_hot_fins_rejected_mw"]:.0f} hot-fin'
        disp="CLOSES" if not q["deficits"] else "NAMED: "+"; ".join(q["deficits"])
        lines.append(f'| {q["state"]} | {q["house_reactor_mw"]:.3f} | {fw} | {q["battery_mw"]:.4f} | {load} | {rejection} | {disp} | {q["house_fuel_g_hr"]:.4f} |')
    lines +=["",
      "**Failure sequence:** one reactor fails → surviving 50MW unit carries known steady loads, HARD Metric and torch magnet electrical, with the flywheel required for routine flips → both house units lost: flywheel supports ordinary ~0.389MW services for **"+f"{st['normal_services_energy_limit_hours_both_reactors_failed']:.2f}h"+ "** energy-only → attempt pulsed main torch **emergency house mode** (UNKNOWN electric output, NOT a certified source) → shed to 0.6kW ×24h shelter battery. Failed-source fallback does not provide an invented continuous torch generator. Full physical power switching, battery isolation, flywheel containment, coolant loops and thermal transfer remain OPEN.",
      "",
      "**House fuel inventory:** 5t D–He3 wet consumable, distinct from 250t water remass and 50t protected water; consumption for each reactor-on state is shown in g/h. Main pulsed torch pellet energy is separate. Tank dry 0.5t is paid from engineering reserve. **"+f"Dry {m['dry_t']:.3f}t, departure S1 {m['S1_wet_t']:.3f}t, reserve {m['engineering_reserve_t']:.3f}t (hard floor 5t; headroom {m['headroom_over_5t_floor_t']:.3f}t). Reactor+flywheel {m['reactors_plus_store_reallocated_in_electrical_t']:.2f}t reallocated WITHIN the 55t electrical line, with no additional dry reserve debit."+ "**",
      "",
      "**Engineering gaps:** 2226 reactor 40kW/kg and flywheel 10kWh/kg/800kW/kg unverified; 10% reliable minimum and independent fault isolation untested; RCS 120s throttling is a declared 1/t² assumption, not an FQ trace; electrical bus peaks and radiator integration unqualified; reported thermal rejection is a heat-budget screen; unmodelled environmental Metric correction power remains an explicit named deficit.",
      "",
      "**Qualification:** targeted G1/G4 required; G3 inspected for mass movement. New geometry SHA does not automatically inherit G6, G12 or whole-ship certified=true. FQ1–FQ4 only required if physical mass/CG/inertia actually changes; if unchanged, prove parity and retain previous source-stamped FQ (without copying old PASS to the new hash).",
      ""
    ]
    DOC.write_text("\n".join(lines))
if __name__=='__main__':
    a=evaluate();save(a)
    print('GEO',a['geometry_sha256'],'REACTOR',a['reactor'],'STORE',a['store'])
    for x in a['states']:print(x['state'],'HOUSE',x['house_reactor_mw'],'STORE',x['flywheel_discharge_mw'],'HEAT',x['heat_rejected_mw'],'DEFICITS',x['deficits'])
