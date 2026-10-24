"""Aerocapture/direct-entry heating check v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Fast arrivals straight from an interplanetary transfer:
peak heating and g for the umbrella shield at two sizes. Steepest angle that
still captures is not searched; a shallow fixed angle is flown."""
import math, json
import shuttle_physics as sp
S = sp.S
CASES = {"Earth": (11.5, -5.5), "Mars": (6.0, -10.0), "Venus": (10.5, -5.5), "Titan": (6.0, -30.0)}


def fly(body, v_kms, gam_deg, beta, ld, rn, bank_deg=60.0):
    atm = sp.Atmosphere(body)
    a = atm.a
    k = S["sutton_graves_k"][a["gas"]]
    h = a["interface_km"] * 1e3
    v, gam = v_kms * 1e3, math.radians(gam_deg)
    ldv = ld * math.cos(math.radians(bank_deg))
    qpk = gpk = Q = 0.0
    t = 0.0
    while h > 0 and t < 4000:
        r = atm.R + h
        g = atm.gm / r ** 2
        _, rho = atm.state(h)
        d = 0.5 * rho * v * v / beta
        l = d * ldv if gam < 0 else 0.0
        qd = k * math.sqrt(rho / rn) * v ** 3
        dt = 0.05
        v += (-d - g * math.sin(gam)) * dt
        gam += (l / v - (g / v - v / r) * math.cos(gam)) * dt
        h += v * math.sin(gam) * dt
        Q += qd * dt
        qpk, gpk = max(qpk, qd), max(gpk, math.hypot(d, l) / 9.80665)
        t += dt
        if gam > 0 and h > a["interface_km"] * 1e3:
            break
        if v < 1500:
            break
    return {"q_peak_w_cm2": round(qpk / 1e4, 1), "g_peak": round(gpk, 1), "heat_load_j_cm2": round(Q / 1e4)}


if __name__ == "__main__":
    out = {}
    for body, (v, g) in CASES.items():
        for beta in (800, 400, 200):
            d = math.sqrt(4 * 70e3 / (math.pi * 1.4 * beta))
            r = fly(body, v, g, beta, 0.2, 0.25 * d)
            out[f"{body} {v} km/s beta {beta}"] = r
            print(body, v, beta, r)
    json.dump(out, open("aerocapture_check.json", "w"), indent=1)
