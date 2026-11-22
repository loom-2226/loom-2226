"""Torchless Tic Tac: Earth surface -> velocity-matched rendezvous with Wayfarer in low orbit on EXPERIMENTAL directional W2.
NON-CANON (Sol recommendation after b99d437, forwarded by kT). ALL bodies. ALL sponsors. 2026-2226.

Granted for this experiment only (not canon, not certified): directional W2 = the lane's existing potential-type field,
carried with the vehicle, pointed in any direction; net ordinary acceleration capped at 0.4 g; partner UNKNOWN; every joule
paid from an onboard source; momentum and angular momentum tallied to the partner. Mechanism unexplained (Sol).
Nothing else is invented. Power and thermal are PARAMETERS, not designs:
  eta_f  field efficiency (delivered work / field input)     lane value 0.6; scanned
  eta_c  source-to-field conversion                          scanned 0.5-1.0
  skin radiation: emissivity 0.85 over the 153 m2 hull at a stated temperature (the hull is the only radiator: no
  appendages); optional water heat sink (heat + boil-off, 2.6 MJ/kg, vented steam noted).
Vehicle: tictac_v1 dry mass, 1.1 t payload, 2 t water kept (life support / ballast); the torch's 7.0 t is kept as the
reactor (nozzle saving not credited). Rotating Earth, equatorial, due east; exponential atmosphere; nose-first drag Cd 0.4
on 11.3 m2 below 100 km. Wayfarer: circular 200 km (ASSUMPTION) - terminal state compared with the local circular velocity."""
import os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(H, 'tictac_v1.json')))
GM, RE, W_E, G0 = 3.986e14, 6.371e6, 7.292e-5, 9.81
H_T = 200e3; R_T = RE + H_T; V_T = math.sqrt(GM / R_T)
M = (T['mass']['dry_t'] + 1.1 + 2.0) * 1e3
A_CAP = 0.4 * G0
SIGMA, EPS, AREA = 5.67e-8, 0.85, 152.6
def rho(h): return 1.225 * math.exp(-h / 7200.0) if h < 150e3 else 0.0

def ascent(a_t_max=A_CAP, P_field_cap=None, dt=0.5, q_cap=2000.0):
    """Polar-plane integration in the inertial frame. Phase 1: climb to H_T co-rotating (field holds the tangential speed at
    omega*r so the air is still), arriving with zero vertical speed. Phase 2: hold altitude, accelerate tangentially to V_T.
    Field acceleration a_f = a_net - g - drag/m. Returns energy, power, impulse and terminal state."""
    r, th, vr, vt = RE, 0.0, 0.0, W_E * RE
    t = 0.0; W = 0.0; P_peak = 0.0; J = np.zeros(2); Lz = 0.0; log = []; phase = 1; E_drag = 0.0
    while t < 4e6:
        h = r - RE; g = GM / r ** 2
        if phase == 1:
            v_up_max = math.sqrt(max(2 * A_CAP * (H_T - h), 0.0))
            v_air = math.sqrt(2 * q_cap / rho(h)) if rho(h) > 0 else 1e9
            vr_tgt = min(v_up_max, v_air); ar = np.clip((vr_tgt - vr) / 2.0, -A_CAP, A_CAP)
            at = np.clip((W_E * r - vt) / 2.0, -A_CAP, A_CAP)
            if h >= H_T - 5.0 and abs(vr) < 0.5: phase = 2
        else:
            ar = np.clip(-(h - H_T) / 50.0 - vr / 5.0, -A_CAP, A_CAP); at = min(a_t_max, max(0.0, (V_T - vt) / 2.0))
            if P_field_cap is not None and vt > 0:                       # field power limit -> cap the tangential accel
                need_r = ar + g - vt ** 2 / r                            # field radial accel needed (support + correction)
                at = min(at, max(0.0, (P_field_cap / M - need_r * vr) / max(vt, 1.0)))
            if V_T - vt < 0.05 and abs(vr) < 0.05 and abs(h - H_T) < 2.0: break
        # drag (nose-first along the air-relative velocity)
        vrel = np.array([vr, vt - W_E * r]); sp = float(np.linalg.norm(vrel))
        D = -0.5 * rho(h) * sp * 0.4 * 11.3 * vrel / M if sp > 0 else np.zeros(2)
        a_net = np.array([ar, at])
        # field accel: a_net = a_f + g_eff + D, in polar: radial a = vr' - vt^2/r ; tangential a = vt' + vr vt / r
        af = np.array([ar + g - vt ** 2 / r, at]) - D                    # field must also cancel gravity (minus centrifugal) and drag
        v = np.array([vr, vt]); Pf = M * float(af @ v)
        W += max(Pf, 0.0) * dt; P_peak = max(P_peak, Pf); E_drag += M * float(-D @ v) * dt
        J += M * af * dt; Lz += M * af[1] * r * dt
        vr += (ar) * dt; vt += (at - vr * vt / r) * dt + 0 * dt          # polar kinematics
        r += vr * dt; th += vt / r * dt; t += dt
        if int(t / dt) % 200 == 0: log.append((t, h, vr, vt, Pf))
    e_vec = None
    v_rel_wayfarer = math.hypot(vr, vt - V_T)
    return dict(t_s=t, field_work_TJ=W / 1e12, P_field_peak_GW=P_peak / 1e9, drag_loss_GJ=E_drag / 1e9, v_rel_to_circular_ms=v_rel_wayfarer,
                altitude_err_m=abs(r - R_T), impulse_to_partner_Ns=float(np.linalg.norm(J)), angmom_to_partner=Lz, log=log)

def thermal(Wf, t, eta_f, eta_c, T_skin, water_t=0.0):
    src = Wf / (eta_f * eta_c); waste = src - Wf
    rad = EPS * SIGMA * T_skin ** 4 * AREA; sink = water_t * 1e3 * 2.6e6
    return dict(source_TJ=src / 1e12, waste_TJ=waste / 1e12, radiated_TJ=rad * t / 1e12, sink_TJ=sink / 1e12, closes=(rad * t + sink) >= waste,
                rad_MW=rad / 1e6, min_time_h_if_radiation_only=waste / rad / 3600)

if __name__ == '__main__':
    fast = ascent()
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, mass_t=M / 1e3, wayfarer_orbit_km=H_T / 1e3, v_circular_ms=round(V_T, 1))
    out['fast_0p4g'] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in fast.items() if k != 'log'}
    grid = []
    for eta_f in (0.6, 0.9, 0.99):
        for eta_c in (0.5, 0.8, 1.0):
            for T_skin in (600, 900, 1200):
                th_ = thermal(fast['field_work_TJ'] * 1e12, fast['t_s'], eta_f, eta_c, T_skin)
                grid.append(dict(eta_f=eta_f, eta_c=eta_c, T_skin_K=T_skin, **{k: round(v, 3) if isinstance(v, float) else v for k, v in th_.items()},
                                 water_sink_needed_t=round(max(0.0, th_['waste_TJ'] * 1e12 - th_['radiated_TJ'] * 1e12) / 2.6e9, 1)))
    out['fast_thermal_grid'] = grid
    # thermal-limited ascents: field power capped so the waste rate equals skin radiation (no sink), lane eta_f 0.6, eta_c 0.8
    slow = {}
    for T_skin in (900, 1200):
        rad = EPS * SIGMA * T_skin ** 4 * AREA; eta = 0.6 * 0.8
        Pcap = rad * eta / (1 - eta)                                       # waste = Pfield (1/eta - 1) <= rad
        a = ascent(P_field_cap=Pcap, dt=2.0)
        slow[f'{T_skin}K'] = dict(P_field_cap_MW=round(Pcap / 1e6, 2), time_h=round(a['t_s'] / 3600, 1), time_days=round(a['t_s'] / 86400, 2),
                                   field_work_TJ=round(a['field_work_TJ'], 3), v_rel_ms=round(a['v_rel_to_circular_ms'], 3), altitude_err_m=round(a['altitude_err_m'], 2))
    out['thermal_limited_slow'] = slow
    out['reactor'] = dict(torch_reactor_GW=7.7, fast_peak_source_GW_at_eta_0p48=round(fast['P_field_peak_GW'] / 0.48, 2), note='source power is not the binding limit; waste heat is')
    json.dump(out, open(os.path.join(H, 'directional_w2_ascent.json'), 'w'), indent=1, default=float)
    print(json.dumps(out['fast_0p4g'], indent=1)); print(json.dumps(slow, indent=1))
    for g in grid:
        if g['T_skin_K'] == 1200: print(g['eta_f'], g['eta_c'], 'waste', g['waste_TJ'], 'water sink t', g['water_sink_needed_t'], 'rad-only h', round(g['min_time_h_if_radiation_only'], 1))
