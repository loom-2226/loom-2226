"""Shuttle v3: electric lift fans + house reactor sizing (option 1).
ALL bodies. ALL sponsors. 2026-2226. NON-CANON engineering screen.
Momentum theory: ideal hover power = T^1.5 / sqrt(2 rho A)."""
import json, math
IN = {
 "m_land_t": [59.0, "40 t dry + 2.6 t payload + ~16 t water kept for the climb (step2_propulsion.json R1)"],
 "TW_hover": [1.15, "ASSUMPTION: hover + control margin (VTOL practice 1.1-1.2)"],
 "figure_of_merit": [0.78, "ASSUMPTION: good ducted fan (open rotors 0.7-0.8; ducts help)"],
 "motor_drive_eff": [0.93, "ASSUMPTION: superconducting motor x power electronics"],
 "reactor_t_per_MWe": [3.095/75, "DERIVED: Venus kit house reactor 3.095 t for 75 MWe (b4s_mass.json, shuttle_inputs DECLARED_2226)"],
 "reactor_heat_per_MWe": [1/3, "DERIVED: 75% direct conversion (DECLARED_2226) -> 0.33 MW heat per MWe"],
 "motor_kW_per_kg": [20, "ASSUMPTION 2226: superconducting aero motors (today's research targets ~13-20)"],
 "electronics_kW_per_kg": [50, "ASSUMPTION 2226"],
 "fan_duct_kg_per_m2": [60, "ASSUMPTION 2226: composite fan, duct, louvres/covers"],
 "store_kWh_per_kg": [4.0, "DECLARED_2226 battery density (kt ship_power_2026_11_01); power rating OPEN"],
 "LD_subsonic": [5.0, "ASSUMPTION: low-aspect lifting body + B4 wings (aero_results ROM range)"],
 "cruise_ms": [100, "ASSUMPTION: wing-borne transition/cruise"],
 "prop_eff_cruise": [0.75, "ASSUMPTION"],
}
v = {k: x[0] for k, x in IN.items()}
ATM = {"Earth sea level": (1.225, 9.81, 0), "Earth 3 km": (0.909, 9.81, 0), "Earth 5 km": (0.736, 9.81, 0),
       "Titan surface": (5.4, 1.35, 0), "Venus surface (kit, +15.2 t)": (65.0, 8.87, 15.2), "Mars surface": (0.020, 3.71, 0)}
def hover_MWe(m_t, g, rho, A):
    T = m_t*1e3*g*v["TW_hover"]
    return T**1.5/math.sqrt(2*rho*A)/v["figure_of_merit"]/v["motor_drive_eff"]/1e6
rows = []
for A in (8, 12, 16, 20, 25, 30):
    P = {k: round(hover_MWe(v["m_land_t"]+dm, g, rho, A), 1) for k, (rho, g, dm) in ATM.items()}
    Pd = P["Earth 3 km"]  # design point: hover at 3 km (hot-day/altitude margin)
    reactor = Pd*v["reactor_t_per_MWe"]; motors = Pd*1e3/v["motor_kW_per_kg"]/1e3
    elec = Pd*1e3/v["electronics_kW_per_kg"]/1e3; fans = A*v["fan_duct_kg_per_m2"]/1e3
    rows.append({"fan_area_m2": A, "four_fans_dia_m": round(2*math.sqrt(A/4/math.pi), 2), "hover_MWe": P,
                 "design_MWe": Pd, "mass_t": {"reactor": round(reactor, 2), "motors": round(motors, 2),
                 "electronics": round(elec, 2), "fans_ducts": round(fans, 2),
                 "total": round(reactor+motors+elec+fans, 2)}})
W = v["m_land_t"]*1e3*9.81
cruise = W/v["LD_subsonic"]*v["cruise_ms"]/v["prop_eff_cruise"]/v["motor_drive_eff"]/1e6
out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "inputs": IN, "rows": rows,
       "wingborne_cruise_MWe_earth": round(cruise, 1),
       "credits_possible_t": {"venus_rotor_tipjets": 1.398+0.65, "venus_kit_reactor_exchangers": 3.095+0.649,
                              "note": "only if the core reactor and fans replace the Venus kit's rotor and its reactor (fans + motors must then survive 737 K)"},
       "stored_energy_option": "reactor sized for wing-borne cruise (~%.0f MWe) + store for hover peaks: 3 min at the 16 m2 point needs (P-cruise) x 180 s; battery power rating OPEN" % cruise}
r16 = next(r for r in rows if r["fan_area_m2"] == 16)
e = (r16["design_MWe"]-cruise)*180/3600  # MWh
out["stored_energy_option_16m2"] = {"store_MWh": round(e, 2), "battery_t": round(e/ v["store_kWh_per_kg"], 2),
    "reactor_t": round(cruise*v["reactor_t_per_MWe"], 2), "vs_full_reactor_t": r16["mass_t"]["reactor"]}
json.dump(out, open("lift_fans.json", "w"), indent=1)
for r in rows: print(r["fan_area_m2"], r["four_fans_dia_m"], r["design_MWe"], r["mass_t"], r["hover_MWe"])
print("cruise", out["wingborne_cruise_MWe_earth"], out["stored_energy_option_16m2"])

# ---- Option 1b: seaplane/STOL on Earth, true hover on Titan and Venus ------------
IN["water_hump_drag_frac"] = [0.25, "ASSUMPTION: seaplane hull hump drag 0.15-0.25 of weight at take-off run"]
def static_MWe(T, rho, A): return T**1.5/math.sqrt(2*rho*A)/v["figure_of_merit"]/v["motor_drive_eff"]/1e6
stol = []
for A in (6, 8, 10, 12):
    T = IN["water_hump_drag_frac"][0]*W
    need = {"earth_water_takeoff": round(static_MWe(T, 1.225, A), 1), "earth_cruise": round(cruise, 1),
            "titan_hover": out["rows"][0]["hover_MWe"]["Titan surface"] if A == 8 else round(hover_MWe(59, 1.35, 5.4, A), 1),
            "venus_hover_with_kit": round(hover_MWe(59+15.2, 8.87, 65.0, A), 1)}
    Pd = max(need.values())
    m = {"reactor": Pd*v["reactor_t_per_MWe"], "motors": Pd/v["motor_kW_per_kg"], "electronics": Pd/v["electronics_kW_per_kg"], "fans_ducts": A*v["fan_duct_kg_per_m2"]/1e3}
    m = {k: round(x, 2) for k, x in m.items()}; m["total"] = round(sum(m.values()), 2)
    stol.append({"fan_area_m2": A, "MWe_needed": need, "design_MWe": round(Pd, 1), "mass_t": m})
out["option_1b_seaplane_plus_hover"] = stol
json.dump(out, open("lift_fans.json", "w"), indent=1)
for s in stol: print(s)
