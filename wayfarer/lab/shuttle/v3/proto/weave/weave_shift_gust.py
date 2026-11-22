"""Shift atmospheric perturbation check: one 1 m/s gust, with and without pressure (SOL brief after ed8843c). NON-CANON.
ALL bodies. ALL sponsors. 2026-2226.

Background: R = 15 m, wall d = 2 m zero-expansion shift, same 200 m / 3 s quintic, uniform sea-level air in free fall (w = 0).
Perturbation: w = locally measured fluid velocity relative to the Eulerian (free-fall) frame; rho' = density perturbation. Linearized
slow-motion equations in the N = 1 shift metric (axisymmetric, no swirl), coordinate frame:
  d_t w   = -grad(beta . w) + beta x omega - c_s^2 grad(rho')/rho0        omega = curl w
  d_t rho' = -beta . grad rho' - rho0 div w                                 (div beta = 0 used)
Pressure-free control: drop the c_s^2 term (this is the Eulerian form of the earlier test-particle law w_dot = -grad(beta) . w).
Curl of the momentum equation: d_t omega = curl(beta x omega)  -- pressure-independent (DERIVED): vorticity is frozen into the beta flow.
Pressure only acts on the compressive part, which becomes sound.
Numerics: collocated 2nd-order central differences on (x, rho), cell-centred rho with parity ghosts, RK4, 4th-order explicit filter,
absorbing sponge on the outer 15 m (energy absorbed is logged as radiated). Energy E = int [1/2 rho0 |w|^2 + 1/2 c^2 rho'^2/rho0] dV.
Runs: {dash, no dash} x {pressure, pressure-free} at h = 0.5 m, plus h = 0.25 m for the dash cases (numerical check)."""
import os, json, time, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
R, DW, D, T, CS, RHO0 = 15.0, 2.0, 200.0, 3.0, 343.0, 1.2
X0B, AMP, LB = 60.0, 1.0, 3.0                                          # gust: axial blob on the track axis at x = 60 m
def s5(x): x = np.clip(x, 0, 1); return D * (6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3)
def v5(x): x = np.clip(x, 0, 1); return D / T * (30 * x ** 4 - 60 * x ** 3 + 30 * x ** 2)
def sech2(z): return 1.0 / np.cosh(np.clip(z, -300, 300)) ** 2
def background(X, P, t, dash):
    if not dash: return np.zeros_like(X), np.zeros_like(X)
    u = X - s5(t / T); r = np.sqrt(u * u + P * P) + 1e-300; V = v5(t / T)
    F = 0.5 * (np.tanh((r + R) / DW) - np.tanh((r - R) / DW)); Fp = 0.5 / DW * (sech2((r + R) / DW) - sech2((r - R) / DW)); q = Fp / (2 * r)
    return V * (F + P * P * q), -V * P * u * q
def run(h=0.5, dash=True, pressure=True, Tend=3.6, xlo=-60.0, xhi=290.0, plo=60.0, sponge=15.0, cfl=0.35, filt=0.2, snaps=()):
    xs = np.arange(xlo, xhi, h) + h / 2; ps = np.arange(0, plo, h) + h / 2; X, P = np.meshgrid(xs, ps, indexing='ij'); nx, npp = X.shape
    dV = 2 * np.pi * P * h * h
    dist = np.minimum.reduce([X - xlo, xhi - X, plo - P]); sig = np.where(dist < sponge, 60.0 * ((sponge - dist) / sponge) ** 2, 0.0)
    wx = AMP * np.exp(-((X - X0B) ** 2 + P ** 2) / LB ** 2); wp = np.zeros_like(X); rp = np.zeros_like(X)
    c2 = CS * CS if pressure else 0.0
    def pad(f, parity):                                                 # ghost cells: axis parity, outer zero-gradient
        g = np.empty((nx + 2, npp + 2)); g[1:-1, 1:-1] = f
        g[1:-1, 0] = parity * f[:, 0]; g[1:-1, -1] = f[:, -1]; g[0, :] = g[1, :]; g[-1, :] = g[-2, :]; return g
    def dx(f, par): g = pad(f, par); return (g[2:, 1:-1] - g[:-2, 1:-1]) / (2 * h)
    def dp(f, par): g = pad(f, par); return (g[1:-1, 2:] - g[1:-1, :-2]) / (2 * h)
    def rhs(wx, wp, rp, t):
        bx, bp = background(X, P, t, dash)
        bw = bx * wx + bp * wp                                          # even in rho
        om = dx(wp, -1) - dp(wx, +1)                                     # omega_phi, odd in rho
        dwx = -dx(bw, +1) + bp * om - c2 * dx(rp, +1) / RHO0
        dwp = -dp(bw, +1) - bx * om - c2 * dp(rp, +1) / RHO0
        div = dx(wx, +1) + dp(P * wp, +1) / P
        drp = -(bx * dx(rp, +1) + bp * dp(rp, +1)) - RHO0 * div
        return dwx - sig * wx, dwp - sig * wp, drp - sig * rp
    def energy(wx, wp, rp):
        ke = float(np.sum(0.5 * RHO0 * (wx * wx + wp * wp) * dV)); pe = float(np.sum(0.5 * c2 * rp * rp / RHO0 * dV)); return ke, pe
    def flt(f, par):
        if filt <= 0: return f
        g = np.empty((nx + 4, npp + 4)); g[2:-2, 2:-2] = f; g[2:-2, 1] = par * f[:, 0]; g[2:-2, 0] = par * f[:, 1]
        g[2:-2, -2] = f[:, -1]; g[2:-2, -1] = f[:, -1]; g[1, :] = g[2, :]; g[0, :] = g[2, :]; g[-2, :] = g[-3, :]; g[-1, :] = g[-3, :]
        d4x = g[:-4, 2:-2] - 4 * g[1:-3, 2:-2] + 6 * g[2:-2, 2:-2] - 4 * g[3:-1, 2:-2] + g[4:, 2:-2]
        d4p = g[2:-2, :-4] - 4 * g[2:-2, 1:-3] + 6 * g[2:-2, 2:-2] - 4 * g[2:-2, 3:-1] + g[2:-2, 4:]
        return f - filt / 16 * (d4x + d4p)
    vmax = (181.0 if dash else 0.0) + (CS if pressure else 0.0) + 1.0; dt = cfl * h / vmax; n = int(Tend / dt)
    E0 = sum(energy(wx, wp, rp)); absorbed = 0.0; log = dict(t=[], ke=[], pe=[], absorbed=[]); out_snaps = {}
    snapk = {int(s / dt): s for s in snaps}
    for k in range(n):
        t = k * dt
        # sponge absorption (energy removed by the -sig terms), first-order estimate
        absorbed += dt * float(np.sum(sig * (RHO0 * (wx * wx + wp * wp) + c2 * rp * rp / RHO0) * dV))
        a = rhs(wx, wp, rp, t); b = rhs(wx + 0.5 * dt * a[0], wp + 0.5 * dt * a[1], rp + 0.5 * dt * a[2], t + 0.5 * dt)
        c = rhs(wx + 0.5 * dt * b[0], wp + 0.5 * dt * b[1], rp + 0.5 * dt * b[2], t + 0.5 * dt); d = rhs(wx + dt * c[0], wp + dt * c[1], rp + dt * c[2], t + dt)
        wx = flt(wx + dt / 6 * (a[0] + 2 * b[0] + 2 * c[0] + d[0]), +1); wp = flt(wp + dt / 6 * (a[1] + 2 * b[1] + 2 * c[1] + d[1]), -1)
        rp = flt(rp + dt / 6 * (a[2] + 2 * b[2] + 2 * c[2] + d[2]), +1)
        if k % max(1, int(0.02 / dt)) == 0 or k == n - 1:
            ke, pe = energy(wx, wp, rp); log['t'].append(t); log['ke'].append(ke); log['pe'].append(pe); log['absorbed'].append(absorbed)
        if k in snapk:
            out_snaps[f'{snapk[k]:.2f}'] = (np.sqrt(wx * wx + wp * wp)[::2, ::2]).tolist()
    ke, pe = energy(wx, wp, rp); spd = np.sqrt(wx * wx + wp * wp); e = 0.5 * RHO0 * spd ** 2 * dV
    inner = sig == 0; cen = float(np.sum(X * e) / np.sum(e)); spread = float(np.sqrt(np.sum((X - cen) ** 2 * e) / np.sum(e)))
    om = dx(wp, -1) - dp(wx, +1)
    return dict(h=h, dash=dash, pressure=pressure, dt=dt, E0_J=E0, E_final_J=ke + pe, KE_final_J=ke, PE_final_J=pe, absorbed_J=absorbed,
                final_max_speed_ms=float(spd[inner].max()), energy_centroid_x_m=cen, energy_spread_x_m=spread,
                final_enstrophy=float(np.sum(om * om * dV))), log, out_snaps, dict(x=xs[::2].tolist(), p=ps[::2].tolist())
if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'main'
    out = {}; series = {}; snaps = {}
    cfgs = [(0.5, True, True), (0.5, True, False), (0.5, False, True), (0.5, False, False)] if which == 'main' else ([(1.0, True, True), (1.0, True, False)] if which == 'coarse' else [(0.25, True, True), (0.25, True, False)])
    for h, dash, pr in cfgs:
        t0 = time.time(); r, L, S, grid = run(h=h, dash=dash, pressure=pr, snaps=(0.0, 1.0, 2.0, 3.6) if (h == 0.5 and dash) else ())
        key = f"h{h:g}_{'dash' if dash else 'nodash'}_{'pressure' if pr else 'nopressure'}"; out[key] = r; series[key] = L
        if S: snaps[key] = dict(grid=grid, snaps=S)
        print(key, {k: (float('%.4g' % v) if isinstance(v, float) else v) for k, v in r.items()}, f'{time.time() - t0:.0f}s', flush=True)
    json.dump(dict(doc=__doc__, runs=out), open(os.path.join(H, f'weave_shift_gust_{which}.json'), 'w'), indent=1)
    json.dump(dict(series=series, snaps=snaps), open(os.path.join(H, f'weave_shift_gust_{which}_series.json'), 'w'))
