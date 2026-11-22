"""Shuttle v3 (B5 concept) atmospheric agility screen for contested ingress/egress.
ALL bodies. ALL sponsors. 2026-2226. NON-CANON ROM screen: subsonic ROM polar
(aero_test.subsonic) is only valid below ~Mach 0.8; no transonic drag rise modelled."""
import sys, os, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'v2_lifting_body'))
import aero_test as AT, b5_concept as C

G = 9.81
IN = {
 "mass_t": [[59.0, 45.0], "59 t inbound with climb water; 45 t light (b5_concept/step2)"],
 "n_limit": [4.0, "ASSUMPTION: courier limit load factor (transport aircraft 2.5-3.8; aerobatic 6)"],
 "fan_MWe": [28.0, "lift_fans.json option 1b design power"],
 "fan_area_m2": [8.0, "lift_fans option 1b"],
 "prop_eff": [0.75, "ASSUMPTION fan propulsive efficiency in forward flight"],
 "torch_atm_kN": [770.0, "step2_propulsion R1 liftoff at 40 t dry (atmosphere mode, ve ~20 km/s)"],
 "jet_power_GW": [7.7, "DECLARED_2226"],
 "mach_limit": [0.8, "validity of the subsonic ROM polar"],
}
v = {k: x[0] for k, x in IN.items()}

def vehicle(wings_out=True):
    V, F, tag = C.loft(); T = V[F]; n, A = AT.geom(T)
    Abase = float(sum(0.5 * np.linalg.norm(np.cross(T[i][1] - T[i][0], T[i][2] - T[i][0])) for i, t in enumerate(tag) if t == 'base'))
    d = dict(T=T, S_body=float(AT.planform(T)), S_wing=0.0, span=4.26, Swet=float(A.sum()), Abase=Abase, sharp=True, rn=0.25)
    if wings_out: d.update(S_wing=C.WING['S'], span=C.WING['span'])
    return d

def rho(h): return AT.rho(AT.WORLDS['Earth'], h)
def sound(h): return 340.3 - 0.0041 * h          # troposphere approx

def polar(veh):
    al = np.linspace(0, 32, 129); CL, CD = [], []
    for a in al:
        cl, cd, S, A, cd0 = AT.subsonic(veh, a); CL.append(cl); CD.append(cd)
    return al, np.array(CL), np.array(CD), S

def fan_thrust(V, h):
    P = v["fan_MWe"] * 1e6
    static = (P * 0.78 * 0.93 * math.sqrt(2 * rho(h) * v["fan_area_m2"])) ** (2 / 3)
    return min(static, v["prop_eff"] * P / max(V, 1.0))

def envelope(veh, m_t, h, thrust):
    al, CL, CD, S = polar(veh); W = m_t * 1e3 * G; out = []
    for V in np.linspace(40, v["mach_limit"] * sound(h), 60):
        q = 0.5 * rho(h) * V * V
        n_aero = q * S * CL.max() / W; n_inst = min(n_aero, v["n_limit"])
        T = thrust(V, h)
        # sustained: largest n with drag <= thrust (and <= limit)
        n_sus = 0.0
        for cl, cd in zip(CL, CD):
            n = q * S * cl / W
            if n > v["n_limit"]: break
            if q * S * cd <= T: n_sus = max(n_sus, n)
        w = lambda n: math.degrees(G * math.sqrt(max(n * n - 1, 0)) / V)
        # 1 g level: excess power -> climb rate
        cl1 = W / (q * S); i = np.searchsorted(CL, cl1)
        ps = (T - q * S * CD[min(i, len(CD) - 1)]) * V / W if cl1 <= CL.max() else float('nan')
        out.append(dict(V=round(float(V), 1), n_inst=round(n_inst, 2), turn_inst_dps=round(w(n_inst), 1),
                        n_sus=round(n_sus, 2), turn_sus_dps=round(w(n_sus), 1),
                        radius_inst_m=round(V * V / (G * math.sqrt(max(n_inst ** 2 - 1, 1e-9))), 0) if n_inst > 1 else None,
                        climb_ms=round(ps, 1)))
    stall = math.sqrt(2 * W / (rho(h) * S * CL.max()))
    return dict(stall_ms=round(stall, 1), points=out)

def egress(TW0, m_t=59.0, top_km=30.0):
    """Vertical-ish torch pop-up from sea level: fixed jet power, thrust set by T/W0 at start.
    Drag ignored above the first km beyond a crude CdA (wings in). Returns time, water used."""
    P = v["jet_power_GW"] * 1e9; m = m_t * 1e3; F = TW0 * m * G; ve = 2 * P / F
    h = vz = t = 0.0; dt = 0.1; mdot = F / ve; CdA = 0.6 * 12.0
    while h < top_km * 1e3 and t < 600:
        D = 0.5 * rho(h) * vz * vz * CdA
        a = (F - D) / m - G; vz += a * dt; h += vz * dt; m -= mdot * dt; t += dt
    return dict(TW0=TW0, ve_kms=round(ve / 1e3, 1), thrust_kN=round(F / 1e3), time_s=round(t, 1),
                speed_ms=round(vz), water_t=round(m_t - m / 1e3, 2))

if __name__ == "__main__":
    out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "inputs": IN, "cases": {}}
    vw = vehicle(True); vc = vehicle(False)
    for m in v["mass_t"]:
        for h in (0.0, 3000.0):
            out["cases"][f"{m:.0f}t_{h/1e3:.0f}km_wings_out_fans"] = envelope(vw, m, h, fan_thrust)
            out["cases"][f"{m:.0f}t_{h/1e3:.0f}km_wings_out_torch"] = envelope(vw, m, h, lambda V, hh: v["torch_atm_kN"] * 1e3)
            out["cases"][f"{m:.0f}t_{h/1e3:.0f}km_wings_in_torch"] = envelope(vc, m, h, lambda V, hh: v["torch_atm_kN"] * 1e3)
    out["egress_to_30km"] = [egress(tw) for tw in (1.4, 2.0, 2.5, 3.0)]
    def best(c, k): return max(c["points"], key=lambda p: p[k])
    summ = {}
    for name, c in out["cases"].items():
        bi, bs = best(c, "turn_inst_dps"), best(c, "turn_sus_dps")
        summ[name] = dict(stall_ms=c["stall_ms"], max_inst_dps=bi["turn_inst_dps"], at_ms=bi["V"], radius_m=bi["radius_inst_m"],
                          max_sus_dps=bs["turn_sus_dps"], sus_at_ms=bs["V"], best_climb_ms=max(p["climb_ms"] for p in c["points"] if p["climb_ms"] == p["climb_ms"]))
    out["summary"] = summ
    json.dump(out, open(os.path.join(HERE, "agility.json"), "w"), indent=1)
    for k, s in summ.items(): print(k, s)
    for e in out["egress_to_30km"]: print(e)
