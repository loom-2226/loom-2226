"""Can air actually follow the zero-expansion shift flow? (SOL review of 2027261). NON-CANON. ALL bodies. ALL sponsors. 2026-2226.

Metric (N = 1, flat slices): ds^2 = -c^2 dt^2 + sum_i (dx^i - beta^i dt)^2, axisymmetric Natario-type shift in Cartesian form:
  u = x - X(t), rho^2 = y^2 + z^2, r^2 = u^2 + rho^2;  beta_x = V(F + rho^2 F'/(2r)),  beta_y = -V y u F'/(2r),  beta_z = -V z u F'/(2r).
Part 1 (exact GR, numerical): at random points, with full 4D Christoffels by 4th-order finite differences (c = 1, V up to 0.3 c):
  (a) 4-acceleration a^nu = u^mu d_mu u^nu + Gamma^nu_{mu lam} u^mu u^lam of u = (1, beta)  -> 0 means the REQUIRED fluid acceleration
      d_t beta + (beta.grad) beta is exactly the GEODESIC acceleration (no pressure gradient needed);
  (b) div T for a perfect fluid with uniform rho, p and u = (1, beta): d_mu T^{mu nu} + Gamma^mu_{mu lam} T^{lam nu} + Gamma^nu_{mu lam} T^{mu lam}.
Part 2 (beyond ideal, sea-level air, the real dash): viscous stress/dissipation from the shear sigma = sym grad beta, pattern Mach number
  |V xhat - beta| / c_s, and growth of small velocity perturbations w along parcel paths: w_dot_i = -(d_i beta_j) w_j (slow geodesic from L = 1/2|xdot - beta|^2; conserves p_phi,
  pressure feedback ignored => test-particle bound). det W = 1 since div beta = 0."""
import os, json, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)
def prof(R, d):
    s2 = lambda z: 1.0 / np.cosh(np.clip(z, -300, 300)) ** 2
    F = lambda r: 0.5 * (np.tanh((r + R) / d) - np.tanh((r - R) / d))
    Fp = lambda r: 0.5 / d * (s2((r + R) / d) - s2((r - R) / d))
    return F, Fp
def beta_cart(t, x, y, z, R, d, Xf, Vf, kind='natario'):
    F, Fp = prof(R, d); u = x - Xf(t); rr2 = y * y + z * z; r = np.sqrt(u * u + rr2) + 1e-300; V = Vf(t); q = Fp(r) / (2 * r)
    if kind == 'alcubierre': return np.array([V * F(r), 0 * y, 0 * z])     # control: div beta != 0
    return np.array([V * (F(r) + rr2 * q), -V * y * u * q, -V * z * u * q])
# ---------------- Part 1: exact GR check ----------------
def part1(R=15.0, d=2.0, n=60, h=2e-3, kind='natario'):
    Vf = lambda t: 0.3 * np.sin(t / 20.0); Xf = lambda t: 6.0 * (1 - np.cos(t / 20.0))
    def metric(P):
        b = beta_cart(P[0], P[1], P[2], P[3], R, d, Xf, Vf, kind); g = np.eye(4); g[0, 0] = -1 + b @ b; g[0, 1:] = g[1:, 0] = -b; return g
    def bvec(P): return beta_cart(P[0], P[1], P[2], P[3], R, d, Xf, Vf, kind)
    def D(fun, P, mu):                                                       # 4th-order central difference
        e = np.zeros(4); e[mu] = h
        return (-fun(P + 2 * e) + 8 * fun(P + e) - 8 * fun(P - e) + fun(P - 2 * e)) / (12 * h)
    def christ(P):
        gi = np.linalg.inv(metric(P)); dg = np.array([D(metric, P, m) for m in range(4)])        # dg[c,a,b] = d_c g_ab
        return 0.5 * (np.einsum('ad,cdb->abc', gi, dg) + np.einsum('ad,bdc->abc', gi, dg) - np.einsum('ad,dbc->abc', gi, dg))  # Gam[a,b,c]
    def u4(P): return np.concatenate([[1.0], bvec(P)])
    def Tmn(P, rho0=1.0, p0=0.37):
        g = metric(P); gi = np.linalg.inv(g); u = u4(P); return (rho0 + p0) * np.outer(u, u) + p0 * gi
    out = []
    for _ in range(n):
        # sample points concentrated in the wall shell where gradients are largest
        t = rng.uniform(5, 30); rr = R + d * rng.normal(0, 1.2); th = rng.uniform(0, np.pi); ph = rng.uniform(0, 2 * np.pi)
        P = np.array([t, Xf(t) + rr * np.cos(th), rr * np.sin(th) * np.cos(ph), rr * np.sin(th) * np.sin(ph)])
        G = christ(P); u = u4(P)
        du = np.array([D(u4, P, m) for m in range(4)])                      # du[m, nu] = d_m u^nu
        acc = u @ du + np.einsum('nml,m,l->n', G, u, u)
        req = (u @ du)[1:]                                                   # = d_t beta + (beta.grad) beta
        geo = -np.einsum('nml,m,l->n', G, u, u)[1:]
        dT = np.array([D(Tmn, P, m) for m in range(4)])                     # dT[m, mu, nu] = d_m T^{mu nu}
        T = Tmn(P)
        divT = np.einsum('mmn->n', dT) + np.einsum('mml,ln->n', G, T) + np.einsum('nml,ml->n', G, T)
        scale = np.max(np.abs(dT)) + 1e-300
        divb = sum(D(lambda Q, i=i: bvec(Q)[i], P, i + 1) for i in range(3))
        out.append(dict(norm_u=float(u @ metric(P) @ u), a4_over_req=float(np.max(np.abs(acc)) / (np.max(np.abs(req)) + 1e-300)),
                        geo_minus_req_rel=float(np.max(np.abs(geo - req)) / (np.max(np.abs(req)) + 1e-300)),
                        divT_rel=float(np.max(np.abs(divT)) / scale), div_beta=float(abs(divb)), req_accel=float(np.max(np.abs(req)))))
    keys = out[0].keys()
    return {k: dict(max=float(max(abs(o[k]) for o in out)), median=float(np.median([abs(o[k]) for o in out]))) for k in keys}
# ---------------- Part 2: real dash, beyond ideal ----------------
D_, T_ = 200.0, 3.0; ETA, RHO_AIR, CS = 1.8e-5, 1.2, 343.0
def s5(x): x = np.clip(x, 0, 1); return D_ * (6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3)
def v5(x): x = np.clip(x, 0, 1); return D_ / T_ * (30 * x ** 4 - 60 * x ** 3 + 30 * x ** 2)
def bm(xx, pp, t, R, d):                                                     # meridional components (beta_x, beta_rho)
    F, Fp = prof(R, d); u = xx - s5(t / T_); r = np.sqrt(u * u + pp * pp) + 1e-300; V = v5(t / T_); q = Fp(r) / (2 * r)
    return V * (F(r) + pp * pp * q), -V * pp * u * q
def grad_m(xx, pp, t, R, d, e=1e-5):
    bxp, bpp = bm(xx + e, pp, t, R, d); bxm, bpm = bm(xx - e, pp, t, R, d); bxP, bpP = bm(xx, pp + e, t, R, d); bxM, bpM = bm(xx, pp - e, t, R, d)
    bx, bp = bm(xx, pp, t, R, d)
    return (bxp - bxm) / (2 * e), (bpp - bpm) / (2 * e), (bxP - bxM) / (2 * e), (bpP - bpM) / (2 * e), bp / np.maximum(pp, 1e-9)
    # returns d_x bx, d_x bp, d_rho bx, d_rho bp, bp/rho
def viscous(R, d, nt=61):
    L = R + 8 * d; hx = d / 20; xs = np.arange(-L, L, hx); ps = np.arange(hx / 2, L, hx); U, P = np.meshgrid(xs, ps, indexing='ij')
    ts = np.linspace(0, T_, nt); diss = []; smax = 0.0; lapmax = 0.0; mach = 0.0
    for t in ts:
        X = s5(t / T_); dxbx, dxbp, dpbx, dpbp, bpr = grad_m(U + X, P, t, R, d)
        sxx, spp, sff, sxp = dxbx, dpbp, bpr, 0.5 * (dpbx + dxbp)
        s2 = sxx ** 2 + spp ** 2 + sff ** 2 + 2 * sxp ** 2
        diss.append(float(np.sum(2 * ETA * s2 * 2 * np.pi * P * hx * hx))); smax = max(smax, float(np.sqrt(s2).max()))
        bx, bp = bm(U + X, P, t, R, d); mach = max(mach, float(np.sqrt((v5(t / T_) - bx) ** 2 + bp ** 2).max() / CS))
        # viscous acceleration (eta/rho) lap(beta) ~ via divergence of 2 sigma: estimate with finite differences of sigma_xx along x and sigma_xp along rho
        dsx = np.gradient(sxx, hx, axis=0) + np.gradient(sxp, hx, axis=1); lapmax = max(lapmax, float(np.abs(2 * dsx).max()))
    E = float(np.trapezoid(diss, ts))
    return dict(peak_shear_per_s=smax, peak_viscous_normal_stress_Pa=2 * ETA * smax, peak_viscous_accel_ms2=ETA / RHO_AIR * lapmax,
                viscous_dissipation_J=E, peak_dissipation_W=max(diss), peak_pattern_mach=mach,
                viscous_stress_SPL_dB=float(20 * np.log10(2 * ETA * smax / 2e-5)))
def perturb(R, d, dt=1e-4, Tend=3.2, h=1.0):
    xs = np.arange(-30.0, 240.0 + 1e-9, h); ps = np.arange(h / 2, 25.0, h); X0, P0 = np.meshgrid(xs, ps, indexing='ij'); x = X0.ravel().copy(); p = P0.ravel().copy(); n = x.size
    W = np.tile(np.eye(3), (n, 1, 1))
    def rhs(x, p, W, t):
        bx, bp = bm(x, p, t, R, d); dxbx, dxbp, dpbx, dpbp, bpr = grad_m(x, p, t, R, d)
        G = np.zeros((n, 3, 3)); G[:, 0, 0] = dxbx; G[:, 0, 1] = dxbp; G[:, 1, 0] = dpbx; G[:, 1, 1] = dpbp; G[:, 2, 2] = bpr   # G[i,j] = d_i beta_j
        return bx, bp, -(G @ W)
    for k in range(int(Tend / dt)):
        t = k * dt
        k1 = rhs(x, p, W, t); k2 = rhs(x + 0.5 * dt * k1[0], p + 0.5 * dt * k1[1], W + 0.5 * dt * k1[2], t + 0.5 * dt)
        k3 = rhs(x + 0.5 * dt * k2[0], p + 0.5 * dt * k2[1], W + 0.5 * dt * k2[2], t + 0.5 * dt); k4 = rhs(x + dt * k3[0], p + dt * k3[1], W + dt * k3[2], t + dt)
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); p += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); W += dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        p = np.abs(p)
    sv = np.linalg.svd(W, compute_uv=False); det = np.linalg.det(W); mass = RHO_AIR * 2 * np.pi * P0.ravel() * h * h
    top = sv[:, 0]
    return dict(max_amplification=float(top.max()), p99_amplification=float(np.percentile(top, 99)), median_amplification=float(np.median(top)),
                mass_amplified_over_2x_kg=float(mass[top > 2].sum()), mass_amplified_over_10x_kg=float(mass[top > 10].sum()), max_det_error=float(np.abs(det - 1).max()),
                residual_speed_for_0p1ms_ambient_max=float(0.1 * top.max())), (X0, P0, top.reshape(X0.shape))
if __name__ == '__main__':
    t0 = time.time(); p1 = part1(); p1c = part1(kind='alcubierre'); print('PART 1', json.dumps(p1, indent=1), 'CONTROL', json.dumps(p1c, indent=1), f'{time.time() - t0:.0f}s', flush=True)
    res = dict(doc=__doc__, part1_exact_GR=p1, part1_control_alcubierre=p1c, part2={}); maps = {}
    for R, d in ((15.0, 2.0), (12.0, 2.0), (12.0, 0.5)):
        t0 = time.time(); v = viscous(R, d); pr, mp = perturb(R, d); res['part2'][f'R{R:g}_d{d:g}'] = dict(viscous=v, perturbation=pr)
        maps[f'R{R:g}_d{d:g}'] = dict(x0=mp[0].tolist(), p0=mp[1].tolist(), amp=mp[2].tolist())
        print(R, d, json.dumps(v), json.dumps(pr), f'{time.time() - t0:.0f}s', flush=True)
    json.dump(res, open(os.path.join(H, 'weave_shift_fluid.json'), 'w'), indent=1)
    json.dump(maps, open(os.path.join(H, 'weave_shift_fluid_maps.json'), 'w'))
