"""Gravity steering (non-canon BMD-1 law) on real trajectories (kT 2026-11-21 final narrow experiment).
Law under test: field acceleration |a_f| <= 1.5 g_P(r) on the whole domain; reaction momentum to partner P; onboard energy = F . v_rel(P).
Case 1: 61 t shuttle, Earth surface -> 400 km circular orbit, field only (no torch), planar, Earth-centred inertial frame, no drag/rotation.
Case 2: 61 t craft in 1 AU heliocentric circular orbit, field used continuously for 24 h (prograde vs normal vs radial).
Power sources: the shuttle's existing fan reactor (29 MWe) and, for comparison only, a torch-class 7.7 GW source. No new hardware.
ALL bodies. ALL sponsors. 2026-2226. NON-CANON."""
import json, math, os
H = os.path.dirname(os.path.abspath(__file__))
GM_E, R_E, GM_S, AU = 3.986e14, 6.371e6, 1.327e20, 1.496e11
m, K = 61e3, 1.5
def to_orbit(P, h_orb=400e3, dt=0.5):
    r_o = R_E + h_orb; v_circ = math.sqrt(GM_E / r_o)
    x, y, vx, vy, t = 0.0, R_E, 0.0, 0.0, 0.0
    W = 0.0; J = [0.0, 0.0]; Jmag = 0.0; log = []; phase = 'climb'
    while True:
        r = math.hypot(x, y); g = GM_E / r ** 2; ur = (x / r, y / r); ut = (ur[1], -ur[0])   # radial up, prograde
        vr = vx * ur[0] + vy * ur[1]; vt = vx * ut[0] + vy * ut[1]; amax = K * g
        if phase == 'climb':
            if r >= r_o - 50: phase = 'spin'
            # vertical: support gravity + accelerate to the power-limited climb speed, brake near the top
            v_lim = min(P / (m * g), math.sqrt(max(2 * 0.5 * g * (r_o - r), 0)))
            ar = g + max(min((v_lim - vr) / 2.0, amax - g), -g)
            at = 0.0
        else:
            ar = g - vt ** 2 / r - vr / 5.0 - (r - r_o) / 100.0     # hold altitude: perpendicular to the velocity, ~zero power
            ar = max(min(ar, amax), -amax)
            at_cap = math.sqrt(max(amax ** 2 - ar ** 2, 0))
            at = min(at_cap, P / (m * max(abs(vt), 1.0)))          # power limit applies to the along-track component
            if vt >= v_circ: break
        ax = ar * ur[0] + at * ut[0] - g * ur[0]; ay = ar * ur[1] + at * ut[1] - g * ur[1]
        Fx, Fy = m * (ar * ur[0] + at * ut[0]), m * (ar * ur[1] + at * ut[1])
        W += (Fx * vx + Fy * vy) * dt; J[0] -= Fx * dt; J[1] -= Fy * dt; Jmag += math.hypot(Fx, Fy) * dt
        vx += ax * dt; vy += ay * dt; x += vx * dt; y += vy * dt; t += dt
        if int(t / dt) % int(600 / dt) == 0: log.append((round(t / 3600, 2), round((r - R_E) / 1e3, 1), round(vt), phase))
        if t > 5 * 86400: break
    E_orb = m * (0.5 * v_circ ** 2 + GM_E / R_E - GM_E / r_o)
    return dict(power_MW=P / 1e6, time_to_orbit_h=round(t / 3600, 2), climb_speed_cap_ms=round(P / (m * 9.81), 1), mechanical_work_TJ=round(W / 1e12, 3),
                orbital_energy_needed_TJ=round(E_orb / 1e12, 3), reaction_impulse_to_Earth_TNs=round(math.hypot(*J) / 1e12, 3), gross_impulse_TNs=round(Jmag / 1e12, 3),
                earth_recoil_velocity_ms=f'{math.hypot(*J) / 5.97e24:.1e}', propellant_t=0.0, track=log[::max(1, len(log) // 8)])
c1 = {'shuttle reactor 29 MWe': to_orbit(29e6), 'torch-class 7.7 GW source (comparison)': to_orbit(7.7e9, dt=0.05)}
# torch reference: Earth sea-to-orbit water from the explorer reference (#2643 + Osteon + W1, step2 legs)
torch_ref = dict(water_t=18.0, note='explorer reference tank for Earth sea-to-orbit (R1 legs), ~minutes; jet energy ~ water x ve^2/2 = several TJ')
# Case 2: heliocentric, 24 h
gS = GM_S / AU ** 2; aS = K * gS; vS = math.sqrt(GM_S / AU); T = 86400.0; F = m * aS
c2 = dict(field_accel_ms2=round(aS, 5), force_N=round(F), dv_24h_ms=round(aS * T),
          prograde=dict(power_MW=round(F * vS / 1e6, 1), work_GJ_24h=round(F * vS * T / 1e9), note='speeds the orbit up: energy = F . v_helio'),
          normal=dict(power_MW='~0 at start (F perpendicular to v)', work_GJ_24h=round(0.5 * m * (aS * T) ** 2 / 1e9, 1), plane_change_deg_24h=round(math.degrees(aS * T / vS), 2),
                      note='rotates the velocity: a plane change costs only 1/2 m dv_n^2'),
          radial=dict(work_GJ_24h=round(0.5 * m * (aS * T) ** 2 / 1e9, 1), note='reshapes the orbit, ~zero power'),
          scaling=dict(acceleration_independent_of_mass=True, wayfarer_1168t_prograde_power_MW=round(1168e3 * aS * vS / 1e6),
                       at_0p3_AU_accel_ms2=round(K * GM_S / (0.3 * AU) ** 2, 4), dv_per_day_at_0p3AU_ms=round(K * GM_S / (0.3 * AU) ** 2 * T),
                       equivalent_solar_sail_area_km2_for_this_force=round(F / 9.1e-6 / 1e6)))
verdict = dict(
 landing_capability='YES: hover and slow lift near a body cost ~0 power; the 200 m exhaust-free lift is available.',
 torch_alternative='ALSO YES - the law as stated is not a landing aid. With only the shuttle\'s existing 29 MWe reactor it reaches 400 km orbit with ZERO propellant in ~%s h; '
                   'with a torch-class 7.7 GW source in ~%s h. Holding altitude while gaining speed costs no power (force perpendicular to velocity), so the only bill is the orbital energy (~2 TJ). '
                   'In heliocentric space it gives ~%s m/s per day to ANY ship (acceleration is mass-independent), plane changes almost free, ~%s m/s per day at 0.3 AU.',
 meaning='Gravity steering as stated is a propellant-free alternative to the torch for orbit insertion and slow interplanetary freight: a setting-scale change, not a shuttle feature.',
 the_leak='Force perpendicular to the partner-relative velocity does no work. Any law that caps force by gravity but prices energy by F . v_rel gives free altitude-holding, free plane changes and power-limited (not propellant-limited) orbit raising.',
 if_landing_only_is_wanted='The capacity must fall off with distance from the partner\'s SURFACE (a proximity law on the scale of the domain, ~10-100 m), not with g_P. That is a different constitutive law and is not tested here.')
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) BMD-1 gravity steering, trajectory test', law='|a_f| <= 1.5 g_P; reaction to P; onboard energy F . v_rel(P)',
           case1_earth_to_orbit=c1, torch_reference=torch_ref, case2_heliocentric_24h=c2, verdict=verdict)
v = out['verdict']; v['torch_alternative'] = v['torch_alternative'] % (c1['shuttle reactor 29 MWe']['time_to_orbit_h'], c1['torch-class 7.7 GW source (comparison)']['time_to_orbit_h'], c2['dv_24h_ms'], c2['scaling']['dv_per_day_at_0p3AU_ms'])
json.dump(out, open(os.path.join(H, 'gs_trajectory.json'), 'w'), indent=1)
if __name__ == '__main__':
    for k, r in c1.items(): print(k, {a: b for a, b in r.items() if a != 'track'}); print('   ', r['track'])
    print(c2); print(v['torch_alternative'])
