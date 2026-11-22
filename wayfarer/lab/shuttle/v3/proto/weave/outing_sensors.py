"""Weave outing 2: SENSOR SIGNATURE - one radar and one optical geometry (SOL outings brief). NON-CANON.
ALL bodies. ALL sponsors. 2026-2226.

Rays in the shift metric ds^2 = -c^2dt^2 + (dx - b dt)^2: dispersion omega = c|k| + b.k (omega = frequency w.r.t. coordinate time,
equal to the frequency measured by static observers outside the field). Ray equations:
  dx/dt = c khat + b,   dk_i/dt = -k_j d_i b_j,   d omega/dt = k . d_t b.
Locally measured (Eulerian) frequency = c|k|. A mirror at rest in the local Eulerian frame (the hull, w = 0) reflects with c|k| conserved.
RADAR: monostatic, head-on on the track axis ahead of the 200 m / 3 s dash; reflection from the hull nose; received/emitted frequency vs
       the classical two-way Doppler of a mirror at the hull's coordinate speed; excess delay.
OPTICAL: side-on camera; rays crossing the domain at peak speed; deflection map. Plus refraction by air rearranged by the dash in a
       vertically stratified atmosphere (parcel displacement map, dn/dz given)."""
import os, json, time
import numpy as np
from scipy.interpolate import griddata
H = os.path.dirname(os.path.abspath(__file__))
C = 2.998e8; R, DW = 15.0, 2.0
def s5(t): x = np.clip(t / 3.0, 0, 1); return 200.0 * (6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3)
def v5(t): x = np.clip(t / 3.0, 0, 1); return 200.0 / 3.0 * (30 * x ** 4 - 60 * x ** 3 + 30 * x ** 2)
def sech2(z): return 1.0 / np.cosh(np.clip(z, -300, 300)) ** 2
def bvec(t, x, y, z):
    u = x - s5(t); rr2 = y * y + z * z; r = np.sqrt(u * u + rr2) + 1e-300; V = v5(t)
    F = 0.5 * (np.tanh((r + R) / DW) - np.tanh((r - R) / DW)); Fp = 0.5 / DW * (sech2((r + R) / DW) - sech2((r - R) / DW)); q = Fp / (2 * r)
    return np.array([V * (F + rr2 * q), -V * y * u * q, -V * z * u * q])
def jac(t, P, e=1e-4):                                                   # J[i, j] = d_i b_j
    J = np.empty((3, 3))
    for i in range(3):
        d = np.zeros(3); d[i] = e; J[i] = (bvec(t, *(P + d)) - bvec(t, *(P - d))) / (2 * e)
    return J
# ---------------- RADAR (on axis, 1D) ----------------
def radar(t0, dt=2e-11, start=80.0):
    """ray starts 'start' m ahead of the hull nose moving toward -x; reflects at the nose (centre + 10 m); returns to the same distance."""
    def bx(t, x): return bvec(t, x, 0.0, 0.0)[0]
    def dbdx(t, x, e=1e-4): return (bx(t, x + e) - bx(t, x - e)) / (2 * e)
    def dbdt(t, x, e=1e-6): return (bx(t + e, x) - bx(t - e, x)) / (2 * e)
    t = t0; x = s5(t) + 10.0 + start; k = -1.0; om = C * 1.0; om0 = om; T_flat = None; phase = 'in'; tref = None
    while True:
        b = bx(t, x); sgn = np.sign(k)
        xd = C * sgn + b; kd = -k * dbdx(t, x); omd = k * dbdt(t, x)
        x += dt * xd; k += dt * kd; om += dt * omd; t += dt
        if phase == 'in' and x <= s5(t) + 10.0:                         # nose reached: reflect in local Eulerian frame
            tref = t; Vref = v5(t); om_loc = C * abs(k); k = abs(k); om = om_loc + bx(t, x) * k; phase = 'out'
        if phase == 'out' and x >= s5(tref) + 10.0 + start:
            break
    ratio = om / om0; classical = (1 + Vref / C) / (1 - Vref / C)
    # flat-space delay for a mirror at the same reflection event
    t_flat = 2 * start / C
    return dict(t_emit=t0, V_at_reflection=Vref, freq_ratio_minus_1=ratio - 1, classical_minus_1=classical - 1,
                rel_diff=(ratio - classical) / (classical - 1), round_trip_s=t - t0, xband_doppler_Hz=(ratio - 1) * 1e10)
# ---------------- OPTICAL: rays crossing the domain at peak speed ----------------
def optical_field(tq=1.5, grid=np.linspace(-24, 24, 25), dt=2e-10, half=45.0, e=1e-4):
    Xc = s5(tq); XO, ZO = np.meshgrid(grid, grid, indexing='ij'); n = XO.size
    P = np.stack([Xc + XO.ravel(), np.full(n, -half), ZO.ravel()]); k = np.tile(np.array([[0.0], [1.0], [0.0]]), (1, n)); t = tq
    while P[1].min() < half:
        b = bvec(t, *P); J = np.empty((3, 3, n))
        for i in range(3):
            d = np.zeros((3, 1)); d[i] = e; J[i] = (bvec(t, *(P + d)) - bvec(t, *(P - d))) / (2 * e)
        kn = np.linalg.norm(k, axis=0); P = P + dt * (C * k / kn + b); k = k + dt * (-np.einsum('ijn,jn->in', J, k)); t += dt
    kh = k / np.linalg.norm(k, axis=0); defl = np.hypot(kh[0], kh[2]).reshape(XO.shape)
    return grid.tolist(), defl.tolist()
# ---------------- OPTICAL: stratified-air refraction after the dash ----------------
def stratified(dndz_list=(-4e-8, -1e-7, -1.57e-7)):
    F = json.load(open(os.path.join(H, 'weave_geometry_compare_series.json')))['fields']['shift']
    x0 = np.array(F['x0']).ravel(); p0 = np.array(F['p0']).ravel(); dx = np.array(F['dx']).ravel(); dp = np.array(F['dp']).ravel()
    xf, pf = x0 + dx, p0 + dp
    xs = np.arange(-20.0, 225.0, 1.0); ps = np.arange(0.5, 24.0, 1.0); XX, PP = np.meshgrid(xs, ps, indexing='ij')
    Dm = griddata((xf, pf), dp, (XX, PP), method='linear', fill_value=0.0)    # radial displacement of the parcel now at (x, rho)
    ys = np.arange(-23.5, 24.0, 0.5); zs = np.arange(-20.0, 20.5, 1.0)
    res = {}
    for G in dndz_list:
        th = np.zeros((len(xs), len(zs)))
        for j, z0 in enumerate(zs):
            def dn(z):
                rho = np.sqrt(ys[None, :] ** 2 + z ** 2); Dv = np.array([np.interp(rho[0], ps, Dm[i]) for i in range(len(xs))])
                return -G * (z / np.maximum(rho, 1e-9)) * Dv * (rho <= 23.5)
            th[:, j] = np.sum((dn(z0 + 0.25) - dn(z0 - 0.25)) / 0.5, axis=1) * 0.5
        res[f'{G:g}'] = dict(max_rad=float(np.abs(th).max()), map=th[::2, ::2].tolist())
    return dict(x=xs[::2].tolist(), z=zs[::2].tolist(), by_gradient=res, max_vertical_displacement_m=float(np.abs(dp).max()))
if __name__ == '__main__':
    out = dict(doc=__doc__)
    t0 = time.time(); out['radar'] = [radar(te, dt=dtr) for te in (0.5, 1.0, 1.5, 2.0, 2.5) for dtr in (1e-10, 2e-11)]; print('radar', json.dumps(out['radar'])[:800], f'{time.time() - t0:.0f}s', flush=True)
    t0 = time.time(); g, m = optical_field(); out['optical_metric'] = dict(grid_m=g, deflection_rad=m, max_rad=float(np.max(m))); print('optical max', out['optical_metric']['max_rad'], f'{time.time() - t0:.0f}s', flush=True)
    t0 = time.time(); out['optical_air'] = stratified(); print('air', {k: v['max_rad'] for k, v in out['optical_air']['by_gradient'].items()}, out['optical_air']['max_vertical_displacement_m'], f'{time.time() - t0:.0f}s', flush=True)
    out['radar_field_rcs_estimate'] = dict(reflection_power=(125.0 / (2 * C)) ** 2, field_rcs_m2=(125.0 / (2 * C)) ** 2 * np.pi * R ** 2,
        note='ESTIMATE: shift metric acts as a moving medium with velocity contrast ~V; reflection amplitude ~ dV/2c per wall')
    json.dump(out, open(os.path.join(H, 'outing_sensors.json'), 'w'), indent=1, default=float)
