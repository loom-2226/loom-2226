"""Tic Tac first experimental flight: an atmospheric sortie over calm ocean (Sol brief after c6a2282). NON-CANON.
ALL bodies. ALL sponsors. 2026-2226.

Profile (field centre height Z above calm water; W2 cushion on throughout; no torch, no Loom hop, no ledger, no partner rule):
  0-5 s    hover at Z = 24 m
  5-5.5 s  30 m Weave sidestep, quintic, 0.5 s
  5.5-9 s  hover
  9-29 s   slow descent 24 -> 10 m (0.7 m/s), through the ~19 m threshold where the sea-bowl begins
  29-44 s  hold at 10 m, watch the water
  44-58 s  climb back to 24 m (1.0 m/s)
  58-75 s  hover, watch what the sea does after she leaves
Existing lane models only, reused unchanged:
  water  outing_nimitz_view.bowl (static equilibrium under the cushion) driven through the outing_bowl_dynamics linear deep-water
         response (a_k'' = -omega_k^2 (a_k - f_k)), with the equilibrium profile following Z(t) and the craft position x(t)
  crew   outing_dodge.ship (hull nodes, seat springs, slow-geodesic law) with the Tic Tac's 12.8 m hull and mass
  air    outing_dodge.wall_mach (field-edge Mach number in the sidestep)
Vehicle: Tic Tac as built (torch aboard but unused), 69.6 t with a full tank, field R 15 m / wall 2 m."""
import os, sys, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); W8 = os.path.join(H, '..', 'proto', 'weave'); sys.path.insert(0, W8)
import outing_nimitz_view as nv, outing_dodge as od
T1 = json.load(open(os.path.join(H, 'tictac_v1.json')))
M = T1['hydrostatics']['cases']['full tank']['mass_t'] * 1e3
g0, RW = 9.81, 1000.0
SEG = [(0, 5, 'hover'), (5, 5.5, 'sidestep'), (5.5, 9, 'hover'), (9, 29, 'descent'), (29, 44, 'hold 10 m'), (44, 58, 'climb'), (58, 75, 'hover')]
def q5(u): u = np.clip(u, 0, 1); return 6 * u ** 5 - 15 * u ** 4 + 10 * u ** 3
def Z_of(t):
    if t < 9: return 24.0
    if t < 29: return 24.0 - 14.0 * (t - 9) / 20.0
    if t < 44: return 10.0
    if t < 58: return 10.0 + 14.0 * (t - 44) / 14.0
    return 24.0
def X_of(t): return 30.0 * q5((t - 5.0) / 0.5)
# ---------------------------------------------------------------- water (existing linear model, Z now varies)
L_, N = 512.0, 512
x = (np.arange(N) - N / 2) * (L_ / N); XX, YY = np.meshgrid(x, x, indexing='ij')
k1 = 2 * np.pi * np.fft.fftfreq(N, d=L_ / N); KX, KY = np.meshgrid(k1, k1, indexing='ij'); W = np.sqrt(g0 * np.hypot(KX, KY))
sg = np.linspace(0, 80, 1601); Zg = np.arange(9.0, 25.01, 0.5)
PROF = np.array([nv.bowl(z, sg) for z in Zg])                     # static equilibrium profiles (DERIVED in the lane)
def eq_field(xc, Z):
    i = np.clip(np.searchsorted(Zg, Z) - 1, 0, len(Zg) - 2); w = (Z - Zg[i]) / (Zg[i + 1] - Zg[i]); prof = (1 - w) * PROF[i] + w * PROF[i + 1]
    return np.interp(np.hypot(XX - xc, YY), sg, prof, right=0.0), prof
def water(dt=0.01, Tend=75.0, snaps=(4.0, 20.0, 29.0, 36.0, 44.0, 50.0, 58.0, 62.0, 70.0)):
    a = np.zeros((N, N), complex); ad = np.zeros((N, N), complex); c, s_ = np.cos(W * dt), np.sin(W * dt); Ws = np.where(W > 0, W, 1.0)
    log = dict(t=[], Z=[], under=[], eq=[], max_rise=[], max_slope=[], wave_E=[]); out = {}
    iy0 = N // 2
    for n in range(int(Tend / dt) + 1):
        t = n * dt; xc, Z = X_of(t), Z_of(t); ef, prof = eq_field(xc, Z); f = np.fft.fft2(ef)
        q = a - f; qn = q * c + ad / Ws * s_; adn = -q * W * s_ + ad * c; a = np.where(W > 0, qn, 0) + f; ad = np.where(W > 0, adn, 0)
        if n % 10 == 0 or any(abs(t - sv) < dt / 2 for sv in snaps):
            eta = np.real(np.fft.ifft2(a)); gx, gy = np.gradient(eta, L_ / N); ix = np.argmin(np.abs(x - xc))
            pe = 0.5 * RW * g0 * np.sum((eta - ef) ** 2) * (L_ / N) ** 2
            ke = 0.5 * RW * g0 * np.sum(np.abs(ad[W > 0]) ** 2 / W[W > 0] ** 2) * (L_ / N) ** 2 / N ** 2
            log['t'].append(t); log['Z'].append(Z); log['under'].append(float(eta[ix, iy0])); log['eq'].append(float(prof[0]))
            log['max_rise'].append(float(eta.max())); log['max_slope'].append(float(np.degrees(np.arctan(np.hypot(gx, gy).max())))); log['wave_E'].append(float(pe + ke))
            for sv in snaps:
                if abs(t - sv) < dt / 2: out[f'{sv:g}'] = eta[N // 2 - 90:N // 2 + 130, N // 2 - 110:N // 2 + 110].astype(np.float32)
    return log, out
if __name__ == '__main__':
    # crew and hull in the sidestep (existing model, Tic Tac hull)
    od.NODE_X = np.linspace(-6.4, 6.4, 11); od.M_HULL = M - 2e3
    crew = od.ship(30.0, 0.5); Vpk = 1.875 * 30 / 0.5; Apk = 5.7735 * 30 / 0.5 ** 2; mach, _ = od.wall_mach(Vpk)
    log, snaps = water()
    t = np.array(log['t']); under = np.array(log['under']); Z = np.array(log['Z']); eq = np.array(log['eq']); wE = np.array(log['wave_E'])
    def win(a, b): return (t >= a) & (t < b)
    first = float(t[np.argmax(eq < -0.05)]) if np.any(eq < -0.05) else None
    res = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, mass_t=M / 1e3, profile=SEG,
        sidestep=dict(D_m=30, T_s=0.5, peak_speed_ms=round(Vpk, 1), peak_accel_g=round(Apk / g0, 1), crew_peak_g=round(crew['crew_peak_g'], 3), cargo_peak_g=round(crew['cargo_peak_g'], 3),
                      hull_peak_kN=round(crew['hull_peak_kN'], 1), final_offset_m=round(crew['final_y_m'], 2), residual_speed_ms=f"{crew['final_speed']:.1e}", field_edge_mach=round(mach, 2),
                      water_effect='none: field centre at 24 m, above the ~19 m bowl threshold', borrowed_KE_GJ_peak=round(0.5 * M * Vpk ** 2 / 1e9, 2), net_KE_after_GJ=0.0),
        water=dict(bowl_first_appears_at_Z_m=round(float(Z[np.argmax(eq < -0.05)]), 1) if first else None, eq_depth_at_10m=round(float(-eq[win(29, 44)][0]), 2),
                   max_depth_during_hold_m=round(float(-under[win(29, 44)].min()), 2), depth_end_of_hold_m=round(float(-under[win(43.9, 44.1)][0]), 2),
                   max_rise_m=round(float(max(log['max_rise'])), 2), max_rim_slope_deg=round(float(max(log['max_slope'])), 1),
                   rebound_under_craft_after_climb_m=round(float(under[win(44, 75)].max()), 2), wave_energy_left_MJ=round(float(wE[-1]) / 1e6, 2),
                   wave_energy_peak_MJ=round(float(wE.max()) / 1e6, 2)),
        work_by_field=dict(cushion_descent_MJ=round(-M * g0 * 14 / 1e6, 1), cushion_climb_MJ=round(M * g0 * 14 / 1e6, 1), net_cushion_MJ=0.0,
                           note='ordinary mechanical work the cushion does on the hull (m g dh): descent and climb cancel. The sidestep borrows and returns its kinetic energy. The work done on the sea (waves left behind) has no booked source.'),
        unresolved=['exchange partner for every field operation (R4): UNKNOWN, not chosen here',
                    'source of the ~' + 'X MJ of wave energy the cushion leaves in the sea: the field did that work; who paid it is the same open exchange question',
                    'local heat of the field: unknown', 'real-sea breaking and spray at rim slopes above ~30 deg: not modelled (linear water)',
                    'nothing here establishes hardware feasibility'],
        series=log)
    res['unresolved'][1] = res['unresolved'][1].replace('X', f"{res['water']['wave_energy_left_MJ']:.1f}")
    json.dump(res, open(os.path.join(H, 'first_flight.json'), 'w'), indent=1, default=float)
    np.savez_compressed(os.path.join(H, 'first_flight_snaps.npz'), **snaps)
    print(json.dumps({k: res[k] for k in ('sidestep', 'water', 'work_by_field')}, indent=1))
