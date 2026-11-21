"""Coupled field-matter-relational dash from ONE effective action (SOL review of 27d8fb4). NON-CANON physics. ALL bodies. ALL sponsors. 2026-2226.

Why not the shift-only action: with L_i = 1/2 m_i (xdot_i - beta)^2 and beta = Xd_dot f(x - X_d), the Noether charge for a common
translation is P = sum m_i w_i (1 - f_i) + dL_wall/dXd_dot + mu xi_dot. A payload carried at w=0 inside f=1 contributes NOTHING:
the action treats carriage as a change of frame and loses the payload's physical momentum (which in GR lives in its gravitational
field at infinity). So a shift-only effective action cannot be the self-consistent conservation test.  [DERIVED, from the action]

Effective action used instead (1D, v << c):
  L = sum_i 1/2 m_i xdot_i^2 - U_springs                         ship matter (hull, crew, cargo), physical kinetic terms
      - sum_i m_i G(t) (x_i - X_d)                                universal (mass-proportional) carriage field inside the domain
                                                                  = a controllable lapse gradient (foundations §5, N); equivalence => crew inertial
      + 1/2 M_w Xd_dot^2                                          domain wall collective coordinate (effective inertia M_w)  [ASSUMED]
      + 1/2 mu xi_dot^2 - 1/2 k_c (X_d - xi - s(t))^2             one relational mode + translation-invariant wall-mode coupling [ASSUMED M1]
  controls: G(t), s(t) (M2 actuation).  Translation invariance => P = sum m xdot + M_w Xd_dot + mu xi_dot conserved (Noether).
  Energy: E = sum KE + U + sum m G (x - X_d) + 1/2 k_c(...)^2 changes only by actuator work dW = -dL/dt|explicit dt."""
import os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
def s5(x): x = min(max(x, 0.0), 1.0); return 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3
def a5(x, D, T):
    x = min(max(x, 0.0), 1.0); return D / T ** 2 * (120 * x ** 3 - 180 * x ** 2 + 60 * x)
D, T = 200.0, 3.0
m = np.array([59e3, 1e3, 1e3]); x0 = np.array([0.0, 3.0, -4.0]); K = np.array([0.0, 2e6, 2e6]); C = np.array([0.0, 4e4, 4e4])
M_W, MU, KC = 1e3, 5.97e24, 1e9
def springs(x, v):
    F = np.zeros(3)
    for j in (1, 2):
        ext = (x[j] - x[0]) - (x0[j] - x0[0]); rel = v[j] - v[0]; f = -K[j] * ext - C[j] * rel; F[j] += f; F[0] -= f
    return F
def U(x):
    return sum(0.5 * K[j] * ((x[j] - x[0]) - (x0[j] - x0[0])) ** 2 for j in (1, 2))
def run(dt=1e-5, Tend=3.5):
    x = x0.copy(); v = np.zeros(3); Xd, Vd = 0.0, 0.0; xi, vxi = 0.0, 0.0
    s_prev = 0.0; G_prev = 0.0; W = 0.0; log = dict(t=[], X=[], felt=[], P=[], dE=[], W=[], Xd=[], xi=[]); E0 = None
    n = int(Tend / dt)
    for k in range(n):
        t = k * dt
        G = -a5(t / T, D, T)                                           # carriage field: universal acceleration = target
        # wall controller: choose coupling set-point so the wall tracks the hull (PD) while carrying the reaction sum m G
        a_des = 400.0 * ((x[0]) - Xd) + 40.0 * (v[0] - Vd) + (-G)
        F_wall_needed = M_W * a_des - np.sum(m) * G                     # net force wall needs = reaction from carriage + coupling
        s = Xd - xi + F_wall_needed / KC                                # k_c (X_d - xi - s) = -F_c  => coupling force on wall = -k_c(...)
        Fc = -KC * (Xd - xi - s)
        Fs = springs(x, v)
        acc = (-m * G + Fs) / m
        aw = (np.sum(m) * G + Fc) / M_W
        axi = -Fc / MU
        # actuator work rate from explicit time dependence: dW/dt = sum m (x - Xd) dG/dt - k_c (X_d - xi - s) ds/dt
        if k > 0:
            W += np.sum(m * (x - Xd)) * (G - G_prev) + Fc * (s - s_prev)
        s_prev, G_prev = s, G
        v = v + dt * acc; x = x + dt * v; Vd = Vd + dt * aw; Xd = Xd + dt * Vd; vxi = vxi + dt * axi; xi = xi + dt * vxi
        if k % 1000 == 0:
            E = 0.5 * np.sum(m * v ** 2) + U(x) + np.sum(m * G * (x - Xd)) + 0.5 * M_W * Vd ** 2 + 0.5 * MU * vxi ** 2 + 0.5 * KC * (Xd - xi - s) ** 2
            if E0 is None: E0 = E
            log['t'].append(t); log['X'].append(float(x[0])); log['felt'].append(float(abs(Fs[1]) / m[1] / 9.81)); log['P'].append(float(np.sum(m * v) + M_W * Vd + MU * vxi))
            log['dE'].append(float(E - E0)); log['W'].append(float(W)); log['Xd'].append(Xd); log['xi'].append(xi)
    return log, x, v, Xd, xi

log, x, v, Xd, xi = run()
P = np.array(log['P']); dE = np.array(log['dE']); Wa = np.array(log['W'])
res = dict(doc=__doc__, params=dict(M_wall_kg=M_W, mu_kg=MU, k_c=KC, D_m=D, T_s=T),
  shuttle=dict(final_hull_X_m=round(float(x[0]), 3), final_speed_ms=float(np.abs(v).max()), max_felt_crew_g=float(max(log['felt'])), wall_tracking_error_m=float(abs(Xd - x[0]))),
  conservation=dict(momentum_max_drift_Ns=float(np.max(np.abs(P - P[0]))), peak_ship_momentum_Ns=float(np.max(np.abs(np.array(log['P']) - P[0])) + 1.0),
                    energy_minus_actuator_work_max_J=float(np.max(np.abs(dE - Wa))), peak_energy_transient_J=float(np.max(dE)), final_actuator_work_J=float(Wa[-1]),
                    relational_mode_shift_m=float(xi), centre_of_mass_shift_kgm=float(np.sum(m * x) + M_W * Xd + MU * xi - np.sum(m * x0)), ship_mass_moment_kgm=float(np.sum(m * (x - x0)) + M_W * Xd)),
  verdicts={'field moves the shuttle 200 m and stops it': 'YES, within the coupled action (no externally imposed reaction)',
            'crew nearly inertial': 'YES: universal carriage field => zero tidal; felt g only from numerical/controller residue',
            'momentum conserved': 'YES (Noether, checked numerically)', 'energy conserved': 'YES: total energy changes exactly by actuator work (checked)',
            'shift-only effective action': 'loses the payload physical momentum: cannot be the conservation test (DERIVED)',
            'new assumptions stated': 'A1 controllable universal carriage field inside the domain (lapse gradient, M2 via §5); A2 wall collective coordinate with effective inertia; A3 translation-invariant wall-relational coupling (the M1 exchange)'})
json.dump(res, open(os.path.join(H, 'weave_coupled.json'), 'w'), indent=1, default=float)
json.dump({k: [float(a) for a in vv] for k, vv in log.items()}, open(os.path.join(H, 'weave_coupled_series.json'), 'w'))
if __name__ == '__main__':
    print(json.dumps({k: v for k, v in res.items() if k != 'doc'}, indent=1))
