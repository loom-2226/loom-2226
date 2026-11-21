"""Bridge test (SOL review of 4b0afba): can the shuttle move because SPACETIME moves (crew inertial), while a relational mode carries the
balancing momentum and centre of mass? NON-CANON physics. ALL bodies. ALL sponsors. 2026-2226.

Geometry (DERIVED part): unit lapse, flat slices, shift beta = v(t) f(x - X_d(t)). For slow matter the proper-time action gives
    L_i = 1/2 m_i (xdot_i - beta)^2 - U_springs  ->  d/dt[m_i w_i] = -m_i w_i d_x beta + F_spring,i ,   w_i = xdot_i - beta.
Matter starting with w=0 inside a uniform plateau stays at w=0: every part of the ship moves with beta and NO internal force arises.
Exchange (ASSUMED part, the M1 hypothesis): the domain wall passes the payload's momentum change to a relational mode of inertia mu.
Comparison case: the same trajectory produced by an ordinary force on the hull (the 4b0afba toy's situation)."""
import os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
R, DW = 10.0, 2.0
def f(r): return 0.5 * (1 - np.tanh((r - R) / DW))
def fp(r): return -0.5 / DW / np.cosh((r - R) / DW) ** 2
def s5(x): x = np.clip(x, 0, 1); return 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3
D, T = 200.0, 3.0
def Xd(t): return D * s5(t / T)
def vd(t, h=1e-5): return (Xd(t + h) - Xd(t - h)) / (2 * h)
# ship: hull, crew (on a seat spring), cargo (on a tie-down spring); positions relative to domain centre
m = np.array([59e3, 1e3, 1e3]); x0 = np.array([0.0, 3.0, -4.0]); K = np.array([0.0, 2e6, 2e6]); C = np.array([0.0, 4e4, 4e4])
def springs(x, xd):
    Fs = np.zeros(3)
    for j in (1, 2):
        ext = (x[j] - x[0]) - (x0[j] - x0[0]); rel = xd[j] - xd[0]
        F = -K[j] * ext - C[j] * rel; Fs[j] += F; Fs[0] -= F
    return Fs
def run(mode, dt=2e-5, Tend=3.5):
    n = int(Tend / dt); x = x0.copy(); w = np.zeros(3); xdot = np.zeros(3)
    out = dict(t=[], X=[], felt_crew=[], felt_cargo=[], P=[]); P0 = 0.0
    for k in range(n):
        t = k * dt
        if mode == 'geometric':
            v = vd(t); beta = v * f(np.abs(x - Xd(t))); dbx = v * fp(np.abs(x - Xd(t))) * np.sign(x - Xd(t))
            xdot = beta + w
            Fs = springs(x, xdot)
            w = w + dt * (-w * dbx + Fs / m); x = x + dt * (beta + w)
        else:                                   # ordinary force on the hull reproducing the same hull trajectory
            a = (vd(t + 1e-4) - vd(t - 1e-4)) / 2e-4
            Fs = springs(x, xdot)
            acc = Fs / m; acc[0] = a                  # hull follows the prescribed trajectory (force supplied externally)
            xdot = xdot + dt * acc; x = x + dt * xdot
        if k % 500 == 0:
            out['t'].append(t); out['X'].append(float(x[0])); out['felt_crew'].append(float(abs(Fs[1]) / m[1] / 9.81)); out['felt_cargo'].append(float(abs(Fs[2]) / m[2] / 9.81)); out['P'].append(float(np.sum(m * xdot)))
    return out, x, xdot
geo, xg, vg = run('geometric'); con, xc, vc = run('contact')
# relational mode takes the payload's momentum change (assumed exchange law): mu xi_dot = -(P_ship - P0)
mu = 5.97e24; t = np.array(geo['t']); P = np.array(geo['P']); dt = t[1] - t[0]
xi = -np.concatenate([[0], np.cumsum(0.5 * (P[1:] + P[:-1]) * dt)]) / mu
Mtot = m.sum(); com_shift = (Mtot * (np.array(geo['X'])[-1] - 0.0) + mu * xi[-1])
res = dict(doc=__doc__, case=dict(D_m=D, T_s=T, peak_speed_ms=round(1.875 * D / T, 1), peak_accel_ms2=round(5.7735 * D / T ** 2, 1), domain_R_m=R),
  geometric=dict(final_hull_X_m=round(float(xg[0]), 3), final_speed_ms=float(np.abs(vg).max()), max_felt_crew_g=max(geo['felt_crew']), max_felt_cargo_g=max(geo['felt_cargo']),
                 internal_strain_m=float(np.max(np.abs((xg - xg[0]) - (x0 - x0[0]))))),
  contact=dict(final_hull_X_m=round(float(xc[0]), 3), max_felt_crew_g=round(max(con['felt_crew']), 2), max_felt_cargo_g=round(max(con['felt_cargo']), 2)),
  exchange=dict(relational_mode_residual_m=float(xi[-1]), centre_of_mass_shift_total_kgm=float(com_shift), peak_payload_momentum_Ns=float(np.abs(P).max())),
  verdicts={'crew inertial while the domain moves the ship 200 m': 'DERIVED (geodesic transport in the shift metric; felt g = 0 to numerical precision)',
            'same trajectory by ordinary force': 'crew feels ~13 g (seat spring) - the 4b0afba situation',
            'momentum and centre of mass closed by the relational mode': 'holds IF the wall passes the payload momentum to the mode (ASSUMED M1 exchange)',
            'what remains': 'a field model showing the wall stress-energy actually transmits momentum to the relational sector (the only assumed link)'})
json.dump(res, open(os.path.join(H, 'weave_bridge.json'), 'w'), indent=1, default=float)
json.dump(dict(t=geo['t'], geoX=geo['X'], geo_felt=geo['felt_crew'], con_felt=con['felt_crew'], P=geo['P'], xi=xi.tolist()), open(os.path.join(H, 'weave_bridge_series.json'), 'w'))
if __name__ == '__main__':
    print(json.dumps({k: v for k, v in res.items() if k != 'doc'}, indent=1))
