"""Finite-domain check of A1 (SOL review of 586f1a4). NON-CANON. ALL bodies. ALL sponsors. 2026-2226.

Same action as weave_coupled.py, but the carriage field has a finite spatial profile:
  V = sum_i m_i G(t) Psi(x_i - X_d),  Psi' = f,  f(u) = 1/2[tanh((u+R)/d) - tanh((u-R)/d)]   (flat interior, wall thickness d)
Force on matter: -m G f(x - X_d); equal and opposite on the wall. Still translation invariant => P exact.
Ship: 20 m hull as 11 axial nodes (EA-like springs), crew seat at x=3, cargo mount at x=-4.
Ambient: 1 kg test parcels (on-path air / loose matter, no collisions) from -40 to +260 m.
Wall-mode coupling A3 unchanged. G(t) still commanded (controllability demo, not a derived capability)."""
import os, json
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
def a5(x, D, T):
    x = np.clip(x, 0.0, 1.0); return D / T ** 2 * (120 * x ** 3 - 180 * x ** 2 + 60 * x)
def logcosh(z): z = np.abs(z); return z + np.log1p(np.exp(-2 * z)) - np.log(2.0)
D, T, g0 = 200.0, 3.0, 9.81
NODE_X = np.linspace(-10, 10, 11); M_HULL = 59e3; K_AX = 1.75e9; C_AX = 2e5
M_CREW, M_CARGO, K_SEAT, C_SEAT = 1e3, 1e3, 2e6, 4e4
CREW_NODE, CARGO_NODE = 6, 3                       # node x=2 (crew at +1 m), node x=-4 (cargo at 0 m)
CREW_OFF, CARGO_OFF = 1.0, 0.0
M_W, MU, KC = 1e3, 5.97e24, 1e9
AMB_X = np.arange(-40.0, 262.0, 2.0); M_AMB = 1.0
def run(R, d, dt=1e-5, Tend=4.0, log_every=500):
    f = lambda u: 0.5 * (np.tanh((u + R) / d) - np.tanh((u - R) / d))
    Psi = lambda u: 0.5 * d * (logcosh((u + R) / d) - logcosh((u - R) / d))
    nh = len(NODE_X)
    x = np.concatenate([NODE_X, [NODE_X[CREW_NODE] + CREW_OFF, NODE_X[CARGO_NODE] + CARGO_OFF], AMB_X])
    m = np.concatenate([np.full(nh, M_HULL / nh), [M_CREW, M_CARGO], np.full(len(AMB_X), M_AMB)])
    x0 = x.copy(); v = np.zeros_like(x); Xd = Vd = xi = vxi = 0.0
    ic, ig = nh, nh + 1; ship = slice(0, nh + 2); amb = slice(nh + 2, None)
    W = 0.0; Gp = sp = None; E0 = None; L = dict(t=[], hull=[], crew_g=[], hull_kN=[], dE=[], W=[], P=[])
    peak_crew = peak_hull = 0.0
    for k in range(int(Tend / dt)):
        t = k * dt; G = -float(a5(t / T, D, T))
        # internal forces
        F = np.zeros_like(x)
        ext = np.diff(x[:nh]) - np.diff(NODE_X); rel = np.diff(v[:nh]); fs = K_AX * ext + C_AX * rel
        F[:nh - 1] += fs; F[1:nh] -= fs
        fc = -K_SEAT * (x[ic] - x[CREW_NODE] - CREW_OFF) - C_SEAT * (v[ic] - v[CREW_NODE]); F[ic] += fc; F[CREW_NODE] -= fc
        fg = -K_SEAT * (x[ig] - x[CARGO_NODE] - CARGO_OFF) - C_SEAT * (v[ig] - v[CARGO_NODE]); F[ig] += fg; F[CARGO_NODE] -= fg
        fu = f(x - Xd); Ffield = -m * G * fu
        xh = np.sum(m[ship] * x[ship]) / np.sum(m[ship]); vh = np.sum(m[ship] * v[ship]) / np.sum(m[ship])
        a_des = 400.0 * (xh - Xd) + 40.0 * (vh - Vd) + (-G)
        F_need = M_W * a_des - np.sum(Ffield) * (-1)   # wall gets -sum(Ffield)
        s = Xd - xi + (M_W * a_des + np.sum(Ffield)) / KC
        Fc = -KC * (Xd - xi - s)
        if Gp is not None: W += np.sum(m * Psi(x - Xd)) * (G - Gp) + Fc * (s - sp)
        Gp, sp = G, s
        acc = (F + Ffield) / m; aw = (-np.sum(Ffield) + Fc) / M_W; axi = -Fc / MU
        v += dt * acc; x += dt * v; Vd += dt * aw; Xd += dt * Vd; vxi += dt * axi; xi += dt * vxi
        cg = abs(fc) / M_CREW / g0; hk = np.max(np.abs(fs)) / 1e3
        peak_crew = max(peak_crew, cg); peak_hull = max(peak_hull, hk)
        if k % log_every == 0:
            E = 0.5 * np.sum(m * v ** 2) + 0.5 * K_AX * np.sum(ext ** 2) + 0.5 * K_SEAT * ((x[ic] - x[CREW_NODE] - CREW_OFF) ** 2 + (x[ig] - x[CARGO_NODE] - CARGO_OFF) ** 2) \
                + np.sum(m * G * Psi(x - Xd)) + 0.5 * M_W * Vd ** 2 + 0.5 * MU * vxi ** 2 + 0.5 * KC * (Xd - xi - s) ** 2
            if E0 is None: E0 = E
            L['t'].append(t); L['hull'].append(float(xh)); L['crew_g'].append(float(cg)); L['hull_kN'].append(float(hk))
            L['dE'].append(float(E - E0)); L['W'].append(float(W)); L['P'].append(float(np.sum(m * v) + M_W * Vd + MU * vxi))
    P = np.array(L['P']); dE = np.array(L['dE']); Wa = np.array(L['W'])
    xa, va = x[amb], v[amb]
    return dict(R_m=R, wall_d_m=d, f_at_hull_ends=float(f(10.0)),
                hull_final_m=float(np.sum(m[ship] * x[ship]) / np.sum(m[ship])), hull_final_speed=float(np.max(np.abs(v[ship]))),
                peak_crew_g=peak_crew, peak_hull_axial_kN=peak_hull, momentum_drift_Ns=float(np.max(np.abs(P - P[0]))),
                energy_minus_work_max_J=float(np.max(np.abs(dE - Wa))), net_actuator_work_J=float(Wa[-1]),
                ambient=dict(x0=AMB_X.tolist(), dx=(xa - AMB_X).tolist(), v=va.tolist())), L
CASES = [(30.0, 2.0), (15.0, 2.0), (12.0, 2.0), (12.0, 0.5)]
if __name__ == '__main__':
    out, series = [], {}
    for R, d in CASES:
        r, L = run(R, d); out.append(r); series[f'R{R:g}_d{d:g}'] = L
        print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items() if k != 'ambient'},
              'amb |v|max', round(max(abs(np.array(r['ambient']['v']))), 2), 'amb dx range', round(min(r['ambient']['dx']), 1), round(max(r['ambient']['dx']), 1), flush=True)
    json.dump(dict(doc=__doc__, cases=out), open(os.path.join(H, 'weave_finite.json'), 'w'), indent=1)
    json.dump(series, open(os.path.join(H, 'weave_finite_series.json'), 'w'))
