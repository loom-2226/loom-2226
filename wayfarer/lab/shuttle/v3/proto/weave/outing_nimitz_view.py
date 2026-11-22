"""Observer's view of a Weave shuttle low over calm water, for a non-canon theory-to-observation comparison (SOL, after 26a3c30).
NON-CANON. ALL bodies. ALL sponsors. 2026-2226.

Two regimes, existing geometry only (R 15 m / wall 2 m):
A. HOVER on the W2 cushion with the field centre Z above calm water. The cushion is a universal conservative force
   f = -grad(Phi_tot), Phi_tot = g [ Z F(r) + z (1 - F(r)) ] (gravity cancelled inside). For two immiscible fluids at rest in a
   conservative universal force field the interface is an equipotential (surface tension neglected): the far surface z = 0 has
   Phi_tot = 0, so the sea surface beneath the craft satisfies  Z F(r) + z (1 - F(r)) = 0   (DERIVED, static equilibrium).
   Reports bowl depth/width vs hover height, rim slope, and the energy released as waves if the cushion lets go or the craft jinks away.
B. PASS: the Weave shift dash (200 m / 3 s) with the field centre 10 m above the water; surface points advected kinematically
   (x_dot = beta), snapshots mid-pass and after.
Whitewater is NOT computed; steep rim slope and large surface stretching are shown only as breaking-likely proxies."""
import os, json
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
H = os.path.dirname(os.path.abspath(__file__))
R, DW, g0, RW = 15.0, 2.0, 9.81, 1000.0
def sech2(z): return 1.0 / np.cosh(np.clip(z, -300, 300)) ** 2
def F(r): return 0.5 * (np.tanh((r + R) / DW) - np.tanh((r - R) / DW))
def bowl(Z, s):
    """sea-surface height z(s) beneath a cushion centred Z above the undisturbed surface (root continuous with z=0 far away)"""
    zz = np.linspace(-(R + 4 * DW), 0.0, 20001); out = np.zeros_like(s)
    for i, si in enumerate(s):
        r = np.sqrt(si ** 2 + (zz - Z) ** 2); Fr = F(r); G = Z * Fr + zz * (1 - Fr)
        # potential along the vertical at radius s increases with z; water occupies G < 0. Interface = highest z with G <= 0 below 0.
        idx = np.where(G <= 0)[0]; out[i] = zz[idx.max()] if idx.size else zz[0]
    return out
def hover_table(Zs=np.arange(0.0, 21.0, 1.0)):
    s = np.linspace(0, 40, 801); rows = []
    for Z in Zs:
        eta = bowl(Z, s); depth = -eta.min(); w = s[np.argmax(eta > -0.05)] if np.any(eta > -0.05) else s[-1]
        slope = np.degrees(np.arctan(np.abs(np.gradient(eta, s)))).max()
        ape = 0.5 * RW * g0 * np.trapezoid(eta ** 2 * 2 * np.pi * s, s); vol = -np.trapezoid(eta * 2 * np.pi * s, s)
        rows.append(dict(Z_m=float(Z), depth_m=float(depth), surface_radius_m=float(w), max_rim_slope_deg=float(slope), displaced_t=float(vol * RW / 1e3), wave_energy_J=float(ape)))
    return rows
# ---------------- B. pass (kinematic) ----------------
def s5(t): x = np.clip(t / 3.0, 0, 1); return 200.0 * (6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3)
def v5(t): x = np.clip(t / 3.0, 0, 1); return 200.0 / 3.0 * (30 * x ** 4 - 60 * x ** 3 + 30 * x ** 2)
def bvec(t, x, y, z):
    u = x - s5(t); rr2 = y * y + z * z; r = np.sqrt(u * u + rr2) + 1e-300; V = v5(t)
    Fp = 0.5 / DW * (sech2((r + R) / DW) - sech2((r - R) / DW)); q = Fp / (2 * r)
    return np.array([V * (F(r) + rr2 * q), -V * y * u * q, -V * z * u * q])
def pass_surface(h=10.0, dt=1e-3, snaps=(1.5, 3.0)):
    xs = np.arange(-30.0, 240.0, 1.0); ys = np.arange(-30.0, 30.5, 1.0); X, Y = np.meshgrid(xs, ys, indexing='ij')
    P = np.stack([X.ravel(), Y.ravel(), np.full(X.size, -h)]); out = {}; t = 0.0
    for k in range(int(max(snaps) / dt) + 1):
        if any(abs(t - s) < dt / 2 for s in snaps): out[f'{t:.1f}'] = P.reshape(3, *X.shape).copy()
        k1 = bvec(t, *P); k2 = bvec(t + dt / 2, *(P + dt / 2 * k1)); k3 = bvec(t + dt / 2, *(P + dt / 2 * k2)); k4 = bvec(t + dt, *(P + dt * k3))
        P = P + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += dt
    return xs, ys, out
if __name__ == '__main__':
    tab = hover_table(); res = dict(doc=__doc__, hover=tab)
    for r in tab:
        if r['Z_m'] in (0, 5, 10, 15, 18, 19, 20): print(r)
    xs, ys, snaps = pass_surface(); res['pass'] = {}
    for k, P in snaps.items():
        eta = P[2] + 10.0; res['pass'][k] = dict(max_rise_m=float(eta.max()), max_drop_m=float(-eta.min()), disturbed_area_m2=float(np.sum(np.abs(eta) > 0.3)))
    print(res['pass'])
    json.dump(res, open(os.path.join(H, 'outing_nimitz_view.json'), 'w'), indent=1)
    np.savez_compressed(os.path.join(H, 'outing_nimitz_pass.npz'), **{f's{k}': v for k, v in snaps.items()})
