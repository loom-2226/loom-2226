"""Shuttle v3 step 2: propulsion and power screen.
ALL bodies. ALL sponsors. 2026-2226.
NON-CANON engineering screen. Every input carries a source or is labelled ASSUMPTION."""
import json, math

G0 = 9.81
IN = {
 "jet_power_GW": [7.7, "DECLARED_2226 kT 2026-11-03 (shuttle_inputs research.torch_source)"],
 "ve_min_kms": [10, "PROJECTION shuttle_inputs torch_low_ve_kmps min"],
 "ve_max_kms": [50, "PROJECTION mid of torch_high_ve_kmps 25-100 (swept 25/50/100)"],
 "engine_t_at_7p7GW": [7.0, "DECLARED_2226 shuttle sizer torch_low_high_engine_t mid"],
 "water_capacity_t": [23.1, "ASSUMPTION v1 retained capacity (shuttle_inputs water)"],
 "dry_core_t": [[36.5, 40, 45], "B4-S p95 36.48 t; 40 and 45 allow growth for the 111 m3 hull (W2)"],
 "venus_kit_t": [15.2, "b4s_mass.json venus_kit mid (payload, outside the 52.5 t core ceiling)"],
 "end_reserve_water_t": [1.0, "ASSUMPTION: 1 t left on return to Wayfarer"],
 "liftoff_TW": [1.4, "ASSUMPTION: rocket-practice liftoff thrust/weight; first 3 km/s"],
 "upper_TW": [0.8, "ASSUMPTION: after pitch-over"],
 "earth_ascent_dv_kms": [9.4, "standard sea-level-to-LEO figure 9.3-9.5 incl. gravity and drag losses"],
}
# legs: (dv m/s, accel in local g, local g)
MISSIONS = {
 "R1 Earth: sea to orbit, 6 pax + 2 t": dict(pay=2.6, kit=False, legs=[(200,.1,1),(300,1.3,9.81),(3000,1.4,9.81),(6400,.8,9.81),(400,.1,1)]),
 "R2 Venus: kit, 3 crew, ascent 10.5 km/s from rotor handover": dict(pay=0.3, kit=True, legs=[(200,.1,1),(3000,1.4,8.87),(7500,.8,8.87),(400,.1,1)]),
 "R3 Titan": dict(pay=2.6, kit=False, legs=[(200,.1,1),(300,1.3,1.35),(2000,1.4,1.35),(400,.1,1)]),
 "R4 Mars (0.8 km/s powered descent)": dict(pay=2.6, kit=False, legs=[(200,.1,1),(800,1.3,3.71),(4100,1.4,3.71),(400,.1,1)]),
 "R5 Moon": dict(pay=2.6, kit=False, legs=[(1900,1.0,1.62),(1900,1.4,1.62),(400,.1,1)]),
 "R6 Europa class": dict(pay=2.6, kit=False, legs=[(1500,1.0,1.31),(1500,1.4,1.31),(400,.1,1)]),
}

def burn(m_end, dv, a_g, g, P, ve_max, ve_min=10e3, n=400):
    """Backwards integration. Fixed jet power: thrust = 2P/ve, so pick the
    highest ve that still gives the needed acceleration."""
    m, vlo = m_end, 1e9
    for _ in range(n):
        ve = max(ve_min, min(ve_max, 2*P/(m*1e3*a_g*g)))
        vlo = min(vlo, ve); m *= math.exp(dv/n/ve)
    return m, vlo

def water(dry, pay, legs, P_GW=7.7, ve_max=50e3):
    m = dry + pay + IN["end_reserve_water_t"][0]; lift = None
    for dv, a, g in reversed(legs):
        m2, vlo = burn(m, dv, a, g, P_GW*1e9, ve_max)
        if a >= 1.3 and g > 2: lift = (round(m2,1), round(vlo/1e3,1), round(2*P_GW*1e9/vlo/1e3))
        m = m2
    return round(m - dry - pay, 1), lift

out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "inputs": IN, "missions": {}, "earth_power_trade": {}}
for name, M in MISSIONS.items():
    row = {}
    for vm in (25e3, 50e3, 100e3):
        for d in IN["dry_core_t"][0]:
            dry = d + (IN["venus_kit_t"][0] if M["kit"] else 0)
            w, lift = water(dry, M["pay"], M["legs"], ve_max=vm)
            row[f"ve{int(vm/1e3)}_dry{d}"] = {"water_t": w, "liftoff_t_ve_kms_thrust_kN": lift}
    out["missions"][name] = row
# Earth: does a bigger torch pay? engine mass scaled linearly with jet power (ASSUMPTION)
for P in (7.7, 10, 12, 15, 20):
    eng = IN["engine_t_at_7p7GW"][0]*P/7.7
    d = 40 + eng - 7.0
    w, lift = water(d, 2.6, MISSIONS["R1 Earth: sea to orbit, 6 pax + 2 t"]["legs"], P_GW=P)
    out["earth_power_trade"][P] = {"engine_t": round(eng,1), "dry_t": round(d,1), "water_t": w, "dry_plus_water_t": round(d+w,1)}

# ---- Neutrons: the pulse shell is the shield -------------------------------
# Wayfarer torch lineage (wayfarer/lab/torch/torch_heat_results.json, step S4):
# fusion/jet = 12.64/11.361; clean D-He3 neutron fraction 0.0076 (torch_heat_inputs);
# its 50 g/cm2 shell lets 15% of neutron energy out -> effective 0.038 cm2/g.
# Removal theory for water gives 0.103 cm2/g (thick hydrogenous shield). Both are shown.
fus = 7.7e9*12.64/11.361; n_frac = 0.0076
def leak_W(sigma, mu): return fus*n_frac*math.exp(-mu*sigma)
def shell_kg(sigma_gcm2, r_cm=2.7): return sigma_gcm2*4*math.pi*r_cm**2/1000
E_n = 2.45e6*1.602e-19          # J per D-D neutron
H = 4.0e-10                      # Sv cm2, ICRP-74 order for ~2.5 MeV neutrons
def dose_rate(Pn, r_m): return Pn/E_n/(4*math.pi*(r_m*100)**2)*H
mdot_full = lambda ve: 2*7.7e9/ve**2
neut = {"fusion_GW": round(fus/1e9,2), "rows": []}
for sigma in (50, 100, 250, 400, 600):
    r = {"shell_g_cm2": sigma, "shell_kg_per_pulse": round(shell_kg(sigma),1)}
    for lbl, mu in (("wayfarer_lineage_0.038", 0.038), ("removal_theory_0.103", 0.103)):
        P = leak_W(sigma, mu)
        r[lbl] = {"leak_W": float(f"{P:.3g}"), "cabin_8m_unshielded_Sv_s": float(f"{dose_rate(P,8):.3g}")}
    r["pulse_rate_hz_at_ve20"] = round(mdot_full(20e3)/shell_kg(sigma), 2)
    neut["rows"].append(r)
# shadow shield: water between burn and cabin; 10 cm relaxation length (ASSUMPTION, fast neutrons in water)
neut["shadow_water_relaxation_cm"] = 10
neut["note"] = ("In dense air, neutrons scatter around a shadow shield (skyshine, mean free path ~100 m "
                "at sea level). So in atmosphere the shell must do most of the work; in vacuum the "
                "shadow shield of protected water helps fully.")
out["neutrons"] = neut
json.dump(out, open("step2_propulsion.json", "w"), indent=1)
if __name__ == "__main__":
    for k, v in out["missions"].items():
        print(k, {kk: vv["water_t"] for kk, vv in v.items() if "dry40" in kk})
    print(out["earth_power_trade"])
    for r in neut["rows"]: print(r)
