"""Lapse-gradient vs zero-expansion shift: same hull, same dash, same air (SOL review of 5871508). NON-CANON.
ALL bodies. ALL sponsors. 2026-2226.

Axisymmetric 3D (x along track, rho radial). Domain centre X(t) = quintic 200 m / 3 s (commanded in both). Profile F(r) = 1/2[tanh((r+R)/d) - tanh((r-R)/d)].

LAPSE (scalar): Phi = (x - X) F(r); matter accel = a(t) grad Phi. A localized scalar with uniform interior gradient MUST have reverse-force
  walls: along any line, integral of dPhi/dx = 0 (DERIVED). [Corrects the 1D Psi' = f profile of 5871508, whose asymptotes differ: not localizable in 3D.]
SHIFT (zero expansion, Natario-type): Stokes stream function psi = 1/2 V rho^2 F(r):
  beta_x = V (F + rho^2 F'/(2r)), beta_rho = -V rho (x - X) F'/(2r);  div beta = 0 exactly; interior beta = (V, 0).
  Slow geodesics with N = 1: L = 1/2 (xdot - beta)^2  =>  d w/dt = (w . grad) beta^T with w = xdot - beta; matter starting at rest has w = 0
  forever => xdot = beta (DERIVED). Physical momentum/energy measured by asymptotic observers as m xdot, 1/2 m xdot^2 (v << c).
REACTION: both route -(P_matter + wall) to the relational mode (A3). Lapse: from the translation-invariant action. Shift: imposed as
  explicit bookkeeping channel (the shift action's own Noether charge omits carried matter).
AIR: collisionless test parcels, sea-level density; compression = binned mass density / initial (2 m cells offset from lattice, interior; shift case = noise floor since div beta = 0), mass 1.2 * 2 pi rho0 h^2 each. Collisionless = exact perfect-fluid solution only when
  the flow is incompressible and pressure stays uniform (true for SHIFT; NOT for LAPSE, where it overestimates crossing; real air would shock)."""
import os, json, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
D, T, g0, RHO_AIR = 200.0, 3.0, 9.81, 1.2
def s5(x): x = np.clip(x, 0, 1); return D * (6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3)
def v5(x): x = np.clip(x, 0, 1); return D / T * (30 * x ** 4 - 60 * x ** 3 + 30 * x ** 2)
def a5(x): x = np.clip(x, 0, 1); return D / T ** 2 * (120 * x ** 3 - 180 * x ** 2 + 60 * x)
def prof(R, d):
    F = lambda r: 0.5 * (np.tanh((r + R) / d) - np.tanh((r - R) / d))
    sech2 = lambda z: 1.0 / np.cosh(np.clip(z, -300, 300)) ** 2
    Fp = lambda r: 0.5 / d * (sech2((r + R) / d) - sech2((r - R) / d))
    return F, Fp
# ---------------- ship on axis: 20 m hull, 11 nodes, crew seat, cargo mount ----------------
NODE_X = np.linspace(-10, 10, 11); M_HULL = 59e3; K_AX = 1.75e9; C_AX = 2e5
M_CREW = M_CARGO = 1e3; K_SEAT, C_SEAT = 2e6, 4e4; CREW_NODE, CARGO_NODE, CREW_OFF = 6, 3, 1.0
def ship(R, d, mode, dt=1e-5, Tend=4.0):
    F, Fp = prof(R, d); nh = len(NODE_X)
    x = np.concatenate([NODE_X, [NODE_X[CREW_NODE] + CREW_OFF, NODE_X[CARGO_NODE]]]); x0 = x.copy()
    m = np.concatenate([np.full(nh, M_HULL / nh), [M_CREW, M_CARGO]]); w = np.zeros_like(x); v = np.zeros_like(x)
    pc = ph = 0.0; ic, ig = nh, nh + 1
    for k in range(int(Tend / dt)):
        t = k * dt; X, V, A = s5(t / T), v5(t / T), a5(t / T); u = x - X; r = np.abs(u)
        Fi = np.zeros_like(x); ext = np.diff(x[:nh]) - np.diff(NODE_X)
        vv = v if mode == 'lapse' else (w + V * F(r))
        fs = K_AX * ext + C_AX * np.diff(vv[:nh]); Fi[:nh - 1] += fs; Fi[1:nh] -= fs
        fc = -K_SEAT * (x[ic] - x[CREW_NODE] - CREW_OFF) - C_SEAT * (vv[ic] - vv[CREW_NODE]); Fi[ic] += fc; Fi[CREW_NODE] -= fc
        fg = -K_SEAT * (x[ig] - x[CARGO_NODE]) - C_SEAT * (vv[ig] - vv[CARGO_NODE]); Fi[ig] += fg; Fi[CARGO_NODE] -= fg
        if mode == 'lapse':                                         # on axis: dPhi/dx = F + |u| F'
            v += dt * (A * (F(r) + r * Fp(r)) + Fi / m); x += dt * v
        else:                                                       # on axis: beta = V F(|u|), d beta/dx = V F'(|u|) sign(u)
            dbdx = V * Fp(r) * np.sign(u); w += dt * (w * dbdx + Fi / m); x += dt * (w + V * F(np.abs(x - X)))
        pc = max(pc, abs(fc) / M_CREW / g0); ph = max(ph, np.max(np.abs(fs)) / 1e3)
    xs = np.sum(m * x) / np.sum(m)
    return dict(crew_peak_g=pc, hull_axial_peak_kN=ph, ship_final_m=float(xs), onaxis_force_at_hull_end=float(F(10.0) + 10.0 * Fp(10.0)) if mode == 'lapse' else float(F(10.0)))
# ---------------- air: axisymmetric lattice ----------------
HX = 0.5; XS = np.arange(-30.0, 240.0 + 1e-9, HX); RS = np.arange(HX / 2, 25.0, HX)
BX = np.arange(-30.25, 241.0, 2.0); BP = np.arange(0.0, 25.0, 2.0); PC = 0.5 * (BP[1:] + BP[:-1])
def air(R, d, mode, dt=1e-4, Tend=4.0, every=100):
    F, Fp = prof(R, d)
    X0, P0 = np.meshgrid(XS, RS, indexing='ij'); x = X0.copy(); p = P0.copy(); vx = np.zeros_like(x); vp = np.zeros_like(x)
    mass = RHO_AIR * 2 * np.pi * P0 * HX * HX
    def acc_lapse(x, p, t):
        X, A = s5(t / T), a5(t / T); u = x - X; r = np.sqrt(u * u + p * p) + 1e-12; Fr, Fpr = F(r), Fp(r)
        return A * (Fr + u * u * Fpr / r), A * (u * p * Fpr / r)
    def beta(x, p, t):
        X, V = s5(t / T), v5(t / T); u = x - X; r = np.sqrt(u * u + p * p) + 1e-12; Fr, Fpr = F(r), Fp(r)
        return V * (Fr + p * p * Fpr / (2 * r)), -V * p * u * Fpr / (2 * r)
    log = dict(t=[], ke=[], px=[]); cmax = 1.0; cmin = 1.0; vmax = 0.0; n = int(Tend / dt)
    for k in range(n + 1):
        t = k * dt
        if mode == 'shift':
            bx, bp = beta(x, p, t); vx, vp = bx, bp
        if k % every == 0:
            ke = 0.5 * np.sum(mass * (vx * vx + vp * vp)); log['t'].append(t); log['ke'].append(float(ke)); log['px'].append(float(np.sum(mass * vx)))
            vs = np.sqrt(vx * vx + vp * vp); vmax = max(vmax, float(vs.max()))
            Hm, _, _ = np.histogram2d(x.ravel(), p.ravel(), bins=[BX, BP], weights=mass.ravel())
            dens = Hm / (RHO_AIR * 2 * np.pi * PC[None, :] * 2.0 * 2.0); inner = dens[3:-3, 0:-2]
            cmax = max(cmax, float(inner.max())); cmin = min(cmin, float(inner.min()))
        if k == n: break
        if mode == 'lapse':                                          # velocity Verlet
            ax, ap = acc_lapse(x, p, t); vx += 0.5 * dt * ax; vp += 0.5 * dt * ap; x += dt * vx; p += dt * vp
            ax, ap = acc_lapse(x, p, t + dt); vx += 0.5 * dt * ax; vp += 0.5 * dt * ap
        else:                                                        # RK4 advection xdot = beta
            k1 = beta(x, p, t); k2 = beta(x + 0.5 * dt * k1[0], p + 0.5 * dt * k1[1], t + 0.5 * dt)
            k3 = beta(x + 0.5 * dt * k2[0], p + 0.5 * dt * k2[1], t + 0.5 * dt); k4 = beta(x + dt * k3[0], p + dt * k3[1], t + dt)
            x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); p += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        neg = p < 0; p[neg] *= -1; vp[neg] *= -1
    disp = np.sqrt((x - X0) ** 2 + (p - P0) ** 2); res_v = np.sqrt(vx * vx + vp * vp)
    moved = disp > 1.0
    return dict(peak_air_KE_J=max(log['ke']), residual_air_KE_J=log['ke'][-1], residual_air_px_Ns=log['px'][-1],
                residual_max_speed_ms=float(res_v.max()), max_displacement_m=float(disp.max()), mass_moved_over_1m_kg=float(mass[moved].sum()),
                peak_air_speed_ms=vmax, max_density_ratio=cmax, min_density_ratio=cmin), log, (X0, P0, x - X0, p - P0, res_v)
CASES = [(15.0, 2.0), (12.0, 0.5), (12.0, 2.0)]
if __name__ == '__main__':
    out, series, fields = [], {}, {}
    for R, d in CASES:
        for mode in ('lapse', 'shift'):
            t0 = time.time(); s = ship(R, d, mode); a, L, fld = air(R, d, mode)
            rec = dict(mode=mode, R_m=R, wall_d_m=d, **s, **a); out.append(rec); series[f'{mode}_R{R:g}_d{d:g}'] = L
            if (R, d) == (15.0, 2.0): fields[mode] = dict(x0=fld[0][::2, ::2].tolist(), p0=fld[1][::2, ::2].tolist(), dx=fld[2][::2, ::2].tolist(), dp=fld[3][::2, ::2].tolist(), v=fld[4][::2, ::2].tolist())
            print(mode, R, d, {k: (float('%.4g' % v) if isinstance(v, float) else v) for k, v in rec.items() if k not in ('mode', 'R_m', 'wall_d_m')}, f'{time.time() - t0:.0f}s', flush=True)
    json.dump(dict(doc=__doc__, cases=out), open(os.path.join(H, 'weave_geometry_compare.json'), 'w'), indent=1)
    json.dump(dict(series=series, fields=fields), open(os.path.join(H, 'weave_geometry_compare_series.json'), 'w'))
