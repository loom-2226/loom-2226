"""Shuttle physics v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Atmospheres, engines, an ascent simulator and an entry
simulator. Every input comes from shuttle_space.json; nothing here is canon."""
import json, math
from pathlib import Path

S = json.loads((Path(__file__).resolve().parent / "shuttle_space.json").read_text())
RGAS = 8.314462


# ---------------------------------------------------------------- atmospheres
class Atmosphere:
    def __init__(self, body):
        b = S["bodies"][body]
        self.name, self.gm, self.R = body, b["gm"], b["r_km"] * 1e3
        self.a = b["atm"]
        if self.a and self.a["kind"] == "vira":
            M = self.a["molar_kg"]
            self.tab = []
            for h, tc, pa in zip(self.a["alt_km"], self.a["t_c"], self.a["p_atm"]):
                p = pa * 101325.0
                T = tc + 273.15
                self.tab.append((h, p, p * M / (RGAS * T), T))
        if self.a and self.a["kind"] == "table":
            self.tab = [(h, p, r, None) for h, r, p in zip(self.a["alt_km"], self.a["rho"], self.a["p_pa"])]

    def g(self, h_m=0.0):
        r = self.R + h_m
        return self.gm / (r * r)

    def _interp(self, hk):
        t = self.tab
        if hk <= t[0][0]:
            return t[0][1], t[0][2], t[0][3]
        for (h0, p0, r0, T0), (h1, p1, r1, T1) in zip(t, t[1:]):
            if hk <= h1:
                f = (hk - h0) / (h1 - h0)
                p = math.exp(math.log(p0) + f * (math.log(p1) - math.log(p0)))
                r = math.exp(math.log(r0) + f * (math.log(r1) - math.log(r0)))
                T = None if T0 is None else T0 + f * (T1 - T0)
                return p, r, T
        h0, p0, r0, T0 = t[-2]
        h1, p1, r1, T1 = t[-1]
        if self.a["kind"] == "vira":
            H = self.a["above_100_scale_km"]
            k = math.exp(-(hk - h1) / H)
            return p1 * k, r1 * k, T1
        H = (h1 - h0) / math.log(r0 / r1)
        k = math.exp(-(hk - h1) / H)
        return p1 * k, r1 * k, None

    def state(self, h_m):
        """(pressure Pa, density kg/m3) at altitude h_m"""
        a = self.a
        if a is None:
            return 0.0, 0.0
        hk = max(h_m, 0.0) / 1e3
        if a["kind"] == "exp":
            k = math.exp(-hk / a["h_km"])
            return a["p0"] * k, a["rho0"] * k
        if a["kind"] == "exp2":
            if hk <= a["break_km"]:
                k = math.exp(-hk / a["h1_km"])
            else:
                k = math.exp(-a["break_km"] / a["h1_km"]) * math.exp(-(hk - a["break_km"]) / a["h2_km"])
            return a["p0"] * k, a["rho0"] * k
        p, r, _ = self._interp(hk)
        return p, r

    def temperature(self, h_m):
        if self.a and self.a["kind"] == "vira":
            return self._interp(h_m / 1e3)[2]
        return None


# ---------------------------------------------------------------- engines
def expansion_factor(pa, pc_bar, gamma):
    """fraction of full-expansion exhaust speed left when the nozzle can only
    expand to ambient pressure pa (adapted nozzle, isentropic)."""
    k = (gamma - 1) / gamma
    x = pa / (pc_bar * 1e5)
    if x >= 1:
        return 0.0
    return math.sqrt(max(0.0, 1 - x ** k))


class Chemical:
    """fixed mass flow at full throttle; exhaust speed set by ambient pressure"""
    def __init__(self, key, f_vac_n):
        p = S["propulsion"][key]
        self.key, self.p = key, p
        self.ve_vac = p["ve_vac_km_s"] * 1e3
        self.ve_inf = self.ve_vac / expansion_factor(1e-4 * p["pc_bar"] * 1e5, p["pc_bar"], p["gamma"])
        self.mdot_max = f_vac_n / self.ve_vac

    def ve(self, pa):
        return min(self.ve_vac, self.ve_inf * expansion_factor(pa, self.p["pc_bar"], self.p["gamma"]))

    def f_max(self, pa):
        return self.mdot_max * self.ve(pa)

    def burn(self, pa, f_req):
        """-> (thrust N, mass flow kg/s)"""
        ve = self.ve(pa)
        if ve <= 0:
            return 0.0, 0.0
        f = min(f_req, self.mdot_max * ve)
        return f, f / ve

    def ve_vacuum(self):
        return self.ve_vac

    @staticmethod
    def f_vac_for(key, pa, f_needed):
        p = S["propulsion"][key]
        ve_vac = p["ve_vac_km_s"] * 1e3
        ve_inf = ve_vac / expansion_factor(1e-4 * p["pc_bar"] * 1e5, p["pc_bar"], p["gamma"])
        ve = min(ve_vac, ve_inf * expansion_factor(pa, p["pc_bar"], p["gamma"]))
        if ve <= 0:
            return math.inf
        return f_needed * ve_vac / ve


class Torch:
    """power-limited: 0.5 * mdot * ve_set^2 = P; ambient pressure takes a
    fraction f of the exhaust speed (magnetic nozzle treated as ~400 bar)"""
    def __init__(self, power_w):
        p = S["propulsion"]["TORCH"]
        self.p, self.P = p, power_w
        self.ve_max, self.ve_min = p["ve_max_km_s"] * 1e3, p["ve_min_km_s"] * 1e3

    def f(self, pa):
        return expansion_factor(pa, self.p["pc_equiv_bar"], self.p["gamma"])

    def f_max(self, pa):
        return 2 * self.P * self.f(pa) / self.ve_min

    def burn(self, pa, f_req):
        fa = self.f(pa)
        if fa <= 0 or f_req <= 0:
            return 0.0, 0.0
        f = min(f_req, 2 * self.P * fa / self.ve_min)
        ve_set = min(self.ve_max, max(self.ve_min, 2 * self.P * fa / f))
        return f, f / (fa * ve_set)

    def ve_vacuum(self):
        return self.ve_max


# ---------------------------------------------------------------- ascent
def orbit_apo(atm, x, y, vx, vy):
    r = math.hypot(x, y)
    v2 = vx * vx + vy * vy
    eps = v2 / 2 - atm.gm / r
    if eps >= 0:
        return math.inf, 0.0
    a = -atm.gm / (2 * eps)
    h = x * vy - y * vx
    e = math.sqrt(max(0.0, 1 + 2 * eps * h * h / atm.gm ** 2))
    return a * (1 + e), h


def atm_top_m(atm):
    """altitude where density first drops below 1e-4 kg/m3 (0 if airless)"""
    if atm.a is None:
        return 0.0
    h = 0.0
    while atm.state(h)[1] > 1e-4 and h < 2e6:
        h += 1000.0
    return h


def ascent(body, engine, m0, start_km=0.0, v0=0.0, h_kick_km=1.0, kick_deg=5.0, tau_s=0.0,
           cd=None, front_m2=None, vol_m3=None, q_max=None, a_max_g=4.0, dt=0.5, t_max=9000):
    """2D point-mass ascent in three phases: vertical climb to h_kick (dynamic
    pressure held at q_max); gravity turn to the top of the atmosphere; then
    insertion guidance that thrusts near-horizontally while holding a low
    altitude (top of the air + tau_s km). Burn ends when apoapsis reaches the
    parking orbit; a Hohmann-style circularisation follows.
    Returns dict, or None if the vehicle cannot reach orbit."""
    atm = Atmosphere(body)
    ref = S["ascent_reference"]
    cd = ref["cd"] if cd is None else cd
    front_m2 = ref["front_m2_per_t23"] * (m0 / 1e3) ** (2 / 3) if front_m2 is None else front_m2
    vol_m3 = ref["volume_m3_per_t"] * m0 / 1e3 if vol_m3 is None else vol_m3
    q_max = S["job_rules"]["q_max_kpa"] * 1e3 if q_max is None else q_max
    r_tgt = atm.R + S["bodies"][body]["orbit_km"] * 1e3
    h_top = atm_top_m(atm)
    h_hold = max(h_top, start_km * 1e3 + 3e3) + tau_s * 1e3
    x, y, vx, vy, m = 0.0, atm.R + start_km * 1e3, 0.0, v0, m0
    phase = "A" if h_kick_km * 1e3 > start_km * 1e3 else "B"
    if atm.a is None and phase == "B":
        phase = "C"
    dv_burn = loss_g = loss_d = 0.0
    qpk, t = 0.0, 0.0

    def deriv(x, y, vx, vy, m):
        r = math.hypot(x, y)
        h = r - atm.R
        ux, uy = x / r, y / r
        hx, hy = uy, -ux                      # local horizontal (downrange +x)
        g = atm.gm / (r * r)
        pa, rho = atm.state(h)
        v = math.hypot(vx, vy)
        q = 0.5 * rho * v * v
        drag = q * cd * front_m2
        buoy = rho * g * vol_m3
        vr = vx * ux + vy * uy
        vt = vx * hx + vy * hy
        f_cap = a_max_g * 9.80665 * m
        if phase == "A" or v < 1.0:
            tx, ty = ux, uy
        elif phase == "B":
            tx, ty = vx / v, vy / v
        else:
            fm = engine.f_max(pa) / m if hasattr(engine, "f_max") else 1.0
            fm = min(fm, a_max_g * 9.80665)
            vr_des = max(-20.0, min(250.0, (h_hold - h) / 40.0))
            a_r = g - vt * vt / r + (vr_des - vr) / 8.0
            s = max(-0.3, min(1.0, a_r / max(fm, 1e-6)))
            c = math.sqrt(1 - s * s)
            tx, ty = s * ux + c * hx, s * uy + c * hy
        sin_g = vr / v if v > 1.0 else 1.0
        f_req = f_cap
        hold = q > q_max
        if phase == "A" and rho > 0:
            # vertical climb no faster than terminal speed: the loss-minimising climb in dense air
            v_term = math.sqrt(max(0.0, 2 * (m * g - buoy) / (rho * cd * front_m2)))
            hold = hold or v > v_term
        if hold:
            f_req = min(f_req, max(0.0, drag + (m * g - buoy) * sin_g))
        f, mdot = engine.burn(pa, f_req)
        dxv = (vx / v, vy / v) if v > 1e-6 else (0.0, 0.0)
        ax = (f * tx - drag * dxv[0] + buoy * ux) / m - g * ux
        ay = (f * ty - drag * dxv[1] + buoy * uy) / m - g * uy
        return ax, ay, -mdot, f, drag, g, q

    while t < t_max:
        r = math.hypot(x, y)
        h = r - atm.R
        if phase == "A" and h >= h_kick_km * 1e3:
            v = math.hypot(vx, vy)
            ux, uy = x / r, y / r
            hx, hy = uy, -ux
            a = math.radians(kick_deg)
            vx, vy = v * (math.cos(a) * ux + math.sin(a) * hx), v * (math.cos(a) * uy + math.sin(a) * hy)
            phase = "B" if atm.a is not None else "C"
        if phase == "B" and h >= h_top:
            phase = "C"
        apo, hm = orbit_apo(atm, x, y, vx, vy)
        if apo >= r_tgt:
            break
        k1 = deriv(x, y, vx, vy, m)
        x2, y2, vx2, vy2, m2 = x + vx * dt / 2, y + vy * dt / 2, vx + k1[0] * dt / 2, vy + k1[1] * dt / 2, m + k1[2] * dt / 2
        k2 = deriv(x2, y2, vx2, vy2, m2)
        x3, y3, vx3, vy3, m3 = x + vx2 * dt / 2, y + vy2 * dt / 2, vx + k2[0] * dt / 2, vy + k2[1] * dt / 2, m + k2[2] * dt / 2
        k3 = deriv(x3, y3, vx3, vy3, m3)
        x4, y4, vx4, vy4, m4 = x + vx3 * dt, y + vy3 * dt, vx + k3[0] * dt, vy + k3[1] * dt, m + k3[2] * dt
        k4 = deriv(x4, y4, vx4, vy4, m4)
        f, drag, g, q = k1[3], k1[4], k1[5], k1[6]
        v = math.hypot(vx, vy)
        sin_g = (vx * x + vy * y) / (r * v) if v > 1 else 1.0
        dv_burn += f / m * dt
        loss_g += g * sin_g * dt
        loss_d += drag / m * dt
        qpk = max(qpk, q)
        x += dt / 6 * (vx + 2 * vx2 + 2 * vx3 + vx4)
        y += dt / 6 * (vy + 2 * vy2 + 2 * vy3 + vy4)
        vx += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        vy += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        m += dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        t += dt
        if math.hypot(x, y) < atm.R + start_km * 1e3 - 50 or m <= 0.02 * m0:
            return None
    else:
        return None
    apo, hm = orbit_apo(atm, x, y, vx, vy)
    if not math.isfinite(apo):
        return None
    v_apo = abs(hm) / apo
    dv_circ = max(0.0, math.sqrt(atm.gm / apo) - v_apo)
    mr = (m0 / m) * math.exp(dv_circ / engine.ve_vacuum())
    dv = dv_burn + dv_circ
    return {"dv_km_s": dv / 1e3, "mass_ratio": mr, "ve_eff_km_s": dv / 1e3 / math.log(mr),
            "gravity_loss_km_s": loss_g / 1e3, "drag_loss_km_s": loss_d / 1e3, "circ_km_s": dv_circ / 1e3,
            "burn_s": t, "q_peak_kpa": qpk / 1e3, "h_kick_km": h_kick_km, "kick_deg": kick_deg, "tau_s": tau_s}


def best_ascent(body, make_engine, m0, start_km=0.0, v0=0.0, kicks=None, angles=None, taus=None, accels=None, **kw):
    """grid search on pitch-over height, kick angle, insertion hold height and
    (for power-limited torches) the acceleration cap, which trades thrust for
    exhaust speed; keeps the lowest mass ratio"""
    atm = Atmosphere(body)
    if kicks is None:
        if atm.a is None:
            kicks = [start_km + 0.1]
        elif body == "Venus":
            kicks = [k for k in (2, 10, 20, 30, 40, 50, 58, 64) if k > start_km + 0.5] or [start_km + 1]
        elif body == "Titan":
            kicks = [50, 100, 150, 200, 250, 300]
        else:
            kicks = [0.3, 1, 3, 8]
    if angles is None:
        angles = [0] if atm.a is None else [1, 2, 4, 8, 15, 25, 40, 60]
    taus = taus or [0, 15, 40]   # extra hold height (km) above the top of the air
    if accels is None:
        accels = [4.0, 1.5, 0.6, 0.25] if isinstance(make_engine(), Torch) else [4.0]
    best = None
    for hk in kicks:
        for a in angles:
            for tau in taus:
                for ag in accels:
                    r = ascent(body, make_engine(), m0, start_km=start_km, v0=v0, h_kick_km=hk, kick_deg=a, tau_s=tau, a_max_g=ag, **kw)
                    if r and (best is None or r["mass_ratio"] < best["mass_ratio"]):
                        r["a_max_g"] = ag
                        best = r
    return best


# ---------------------------------------------------------------- entry
def entry(body, beta, ld, nose_r, vol_per_kg=None, stop_km=0.0, checkpoints_km=(), dt_fast=0.1, dt_slow=0.5, bank_deg=60.0):
    """2D ballistic/lifting entry from the deorbit ellipse. Lift acts only while
    descending (no skips). Returns heat load, peak flux, peak g, speed at stop."""
    atm = Atmosphere(body)
    a = atm.a
    vol_per_kg = S["ascent_reference"]["volume_m3_per_t"] / 1e3 if vol_per_kg is None else vol_per_kg
    k = S["sutton_graves_k"][a["gas"]]
    r_o = atm.R + S["bodies"][body]["orbit_km"] * 1e3
    r_p = atm.R + a["perigee_km"] * 1e3
    r_e = atm.R + a["interface_km"] * 1e3
    v_p = math.sqrt(2 * atm.gm * r_o / (r_p * (r_o + r_p)))
    dv_deorbit = math.sqrt(atm.gm / r_o) - math.sqrt(2 * atm.gm * r_p / (r_o * (r_o + r_p)))
    hmom = r_p * v_p
    eps = 0.5 * v_p ** 2 - atm.gm / r_p
    v = math.sqrt(2 * (eps + atm.gm / r_e))
    gam = -math.acos(min(1.0, hmom / (r_e * v)))
    h = a["interface_km"] * 1e3
    v_ei = v
    ldv = ld * math.cos(math.radians(bank_deg))
    Q = qpk = gpk = 0.0
    t = 0.0
    v_at = {}
    while h > stop_km * 1e3 and t < 20000:
        for c in checkpoints_km:
            if c not in v_at and h <= c * 1e3:
                v_at[c] = v
        r = atm.R + h
        g = atm.gm / r ** 2
        pa, rho = atm.state(h)
        g_eff = g * (1 - rho * vol_per_kg)
        dacc = 0.5 * rho * v * v / beta
        lacc = dacc * ldv if gam < 0 else 0.0
        qdot = k * math.sqrt(rho / nose_r) * v ** 3
        dt = dt_fast if v > 600 else dt_slow
        dv = (-dacc - g_eff * math.sin(gam)) * dt
        dg = (lacc / max(v, 1.0) - (g_eff / max(v, 1.0) - v / r) * math.cos(gam)) * dt
        h += v * math.sin(gam) * dt
        v = max(0.1, v + dv)
        gam = max(-math.pi / 2, min(math.pi / 2, gam + dg))
        Q += qdot * dt
        qpk = max(qpk, qdot)
        gpk = max(gpk, math.hypot(dacc, lacc) / 9.80665)
        t += dt
    return {"v_entry_km_s": v_ei / 1e3, "dv_deorbit_km_s": dv_deorbit / 1e3, "heat_load_j_cm2": Q / 1e4,
            "q_peak_w_cm2": qpk / 1e4, "g_peak": gpk, "v_at_stop_m_s": v, "time_s": t,
            "v_at_m_s": {str(k): w for k, w in v_at.items()}}


def tps_fraction(q_j_cm2):
    """Laub & Venkatapathy correlation, % of entry mass -> fraction"""
    return 0.091 * q_j_cm2 ** 0.51575 / 100


if __name__ == "__main__":
    import time
    t0 = time.time()
    v = Atmosphere("Venus")
    for hk in (0, 40, 55):
        print("Venus", hk, "km  p=%.3g Pa rho=%.3g T=%.0f K" % (*v.state(hk * 1e3), v.temperature(hk * 1e3)))
    for key in ("METHALOX", "HYDROLOX", "NTR"):
        p = S["propulsion"][key]
        e = Chemical(key, 1.0)
        print(key, "ve at Earth SL %.2f km/s, Venus surface %.2f km/s" % (e.ve(101325) / 1e3, e.ve(9.33e6) / 1e3))
    tq = Torch(1.0)
    print("TORCH f at Earth SL %.3f, Venus surface %.3f" % (tq.f(101325), tq.f(9.33e6)))
    print("build", time.time() - t0)
