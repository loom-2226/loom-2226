"""Relational back-reaction toy (SOL hypothesis, kT 2026-11-21; Claude refinements). NON-CANON physics. ALL bodies. ALL sponsors. 2026-2226.

Model (1D, Galilean limit v << c, where centre of energy = centre of mass):
  - shuttle: its REAL inertial mass m (no separate 'relational mass'), position X, velocity V
  - relational medium: modes a with inertia mu_a, rest velocity u_a relative to the local body frame, and coupling share w_a (sum w_a = 1)
  - M2 control produces a translation-invariant internal force pair: +F on the shuttle, -w_a F on each mode (Newton III by symmetry)
  - actuator work rate  P = sum_a w_a F (V - xi_dot_a)   (work by an internal force pair depends only on relative velocity: Galilean-invariant)
Conserved by construction of the symmetry: total momentum m V + sum mu_a xi_dot_a; centre of mass moves uniformly.
This toy checks those numerically and reads off energy, residuals and harvesting. It does NOT derive the kernel G_R (which sets mu, u, w)."""
import os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
g = 9.81
def s5(x): x = np.clip(x, 0, 1); return 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3
def run(m, X_of_t, t, modes, ext_force=None):
    """modes: list of dict(mu, u, w). X_of_t: target shuttle trajectory. ext_force: external (gravity) force on shuttle, F_total = m Xdd - ext."""
    dt = t[1] - t[0]; X = X_of_t(t); V = np.gradient(X, dt); A = np.gradient(V, dt)
    Fext = ext_force(t) if ext_force else 0 * t
    F = m * A - Fext                                                 # force the Weave coupling must supply to the shuttle
    I = np.concatenate([[0], np.cumsum(0.5 * (F[1:] + F[:-1]) * dt)])   # cumulative impulse delivered to the shuttle by the coupling
    out = dict(modes=[]); P = np.zeros_like(t); Ptot_err = 0.0; com_num = m * X; mtot = m
    p0 = m * V[0] + sum(md['mu'] * md['u'] for md in modes)
    ptot = m * V.copy()
    for md in modes:
        xid = md['u'] - md['w'] * I / md['mu']                       # mode velocity
        xi = md['u'] * t - md['w'] * np.concatenate([[0], np.cumsum(0.5 * (I[1:] + I[:-1]) * dt)]) / md['mu']
        P += md['w'] * F * (V - xid); ptot += md['mu'] * xid; com_num = com_num + md['mu'] * xi; mtot += md['mu']
        out['modes'].append(dict(name=md['name'], mu_kg=md['mu'], u_ms=md['u'], w=md['w'], residual_displacement_m=float(xi[-1] - md['u'] * t[-1]),
                                 residual_velocity_ms=float(xid[-1] - md['u'])))
    E = np.concatenate([[0], np.cumsum(0.5 * (P[1:] + P[:-1]) * dt)])
    ext_imp = np.concatenate([[0], np.cumsum(0.5 * (Fext[1:] + Fext[:-1]) * dt)])
    out.update(net_actuator_energy_J=float(E[-1]), peak_positive_J=float(E.max()), peak_negative_J=float(E.min()), peak_power_W=float(np.abs(P).max()),
               momentum_drift_rel=float(np.max(np.abs(ptot - p0 - ext_imp)) / max(abs(m * V).max(), 1.0)),
               shuttle_final_X_m=float(X[-1]), shuttle_final_V_ms=float(V[-1]), _t=t, _E=E, _P=P, _X=X)
    return out
def strip(o): return {k: v for k, v in o.items() if not k.startswith('_')}
M_SH, M_WF = 61e3, 1168e3
D, T = 200.0, 3.0
t = np.linspace(0, T, 30001)
dash = lambda tt: D * s5(tt / T)
MU_BIG = 5.97e24                                                     # local-medium inertia ~ Earth mass (ASSUMED scale)
SCEN = {
 'local medium (u=0)': [dict(name='local', mu=MU_BIG, u=0.0, w=1.0)],
 'Sun-like medium (u=29.8 km/s)': [dict(name='solar', mu=2e30, u=29.8e3, w=1.0)],
 'cosmic medium (u=370 km/s)': [dict(name='cosmic', mu=1e42, u=370e3, w=1.0)],
 'mixed: local 1-1e-4, cosmic 1e-4': [dict(name='local', mu=MU_BIG, u=0.0, w=1 - 1e-4), dict(name='cosmic', mu=1e42, u=370e3, w=1e-4)],
}
res = {'doc': __doc__, 'dash': {}, 'hover_20s': {}, 'lift_cycle_1km': {}, 'mu_sweep': [], 'wayfarer': {}}
for name, modes in SCEN.items():
    res['dash'][name] = strip(run(M_SH, dash, t, modes))
# hover 20 s against gravity (sustained net impulse into the medium)
th = np.linspace(0, 20, 20001)
for name, modes in SCEN.items():
    o = run(M_SH, lambda tt: 0 * tt, th, modes, ext_force=lambda tt: -M_SH * g + 0 * tt)
    res['hover_20s'][name] = dict(net_actuator_energy_J=o['net_actuator_energy_J'], mean_power_W=o['net_actuator_energy_J'] / 20,
                                  note='negative = energy delivered TO the actuator (harvest); sign flips with the medium direction')
# lift 1 km in 20 s by the field, then ordinary fall with ideal harvest of m g h
tl = np.linspace(0, 20, 20001)
for name, modes in SCEN.items():
    o = run(M_SH, lambda tt: 1000 * s5(tt / 20), tl, modes, ext_force=lambda tt: -M_SH * g + 0 * tt)
    harvest = M_SH * g * 1000
    res['lift_cycle_1km'][name] = dict(lift_cost_J=o['net_actuator_energy_J'], fall_harvest_J=harvest, cycle_net_gain_J=harvest - o['net_actuator_energy_J'])
# inertia sweep (local medium, dash)
for mu in (1e5, 1e6, 1e7, 1e9, 1e12, MU_BIG):
    o = run(M_SH, dash, t, [dict(name='local', mu=mu, u=0.0, w=1.0)])
    res['mu_sweep'].append(dict(mu_kg=mu, peak_transient_J=o['peak_positive_J'], net_J=o['net_actuator_energy_J'], medium_residual_m=o['modes'][0]['residual_displacement_m']))
# same law on Wayfarer
res['wayfarer']['dash_200m'] = strip(run(M_WF, dash, t, SCEN['local medium (u=0)']))
c = 2.998e8; gam = 1 / math.sqrt(1 - 0.268 ** 2)
res['wayfarer']['cruise_0p268c_transient_energy_J'] = (gam - 1) * M_WF * c ** 2
res['wayfarer']['canon_bank_J'] = 2e9
res['wayfarer']['note'] = 'Under this law a start-cruise-stop transfers (gamma-1) m c^2 into the ship during cruise and returns it at stop. The 2 GJ bank cannot hold it, so the relational sector must be the transient energy store (SOL reading of foundations §8). Net cost of a symmetric transit: losses only.'
# requirement on non-local weight so that harvesting stays below m g h for a 20 s, 1 km lift
I_lift = M_SH * g * 20
res['requirement'] = dict(u_eff_max_ms=M_SH * g * 1000 / I_lift, w_max_sun=M_SH * g * 1000 / I_lift / 29.8e3, w_max_cosmic=M_SH * g * 1000 / I_lift / 370e3,
                          meaning='harvest per sustained impulse I is u_eff * I with u_eff = sum w_a u_a. To keep it below the lift work itself, the non-local share must be below these weights.')
json.dump(res, open(os.path.join(H, 'relational_backreaction.json'), 'w'), indent=1, default=float)
if __name__ == '__main__':
    for k, v in res['dash'].items(): print('DASH', k, {a: (round(b, 6) if isinstance(b, float) else b) for a, b in v.items() if a != 'modes'}, v['modes'])
    for k, v in res['hover_20s'].items(): print('HOVER', k, f"{v['net_actuator_energy_J']:.3e} J, {v['mean_power_W']:.3e} W")
    for k, v in res['lift_cycle_1km'].items(): print('CYCLE', k, f"lift {v['lift_cost_J']:.3e}  harvest {v['fall_harvest_J']:.3e}  net gain {v['cycle_net_gain_J']:.3e}")
    for r in res['mu_sweep']: print('MU', r)
    print('WAYFARER', {a: b for a, b in res['wayfarer']['dash_200m'].items() if a != 'modes'}, f"{res['wayfarer']['cruise_0p268c_transient_energy_J']:.2e}")
    print('REQ', res['requirement'])
