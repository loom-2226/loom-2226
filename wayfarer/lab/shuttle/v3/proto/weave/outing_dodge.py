"""Weave outing 1: DODGE - one lateral avoidance manoeuvre (SOL outings brief). NON-CANON. ALL bodies. ALL sponsors. 2026-2226.

Geometry: R 15 m / wall 2 m zero-expansion shift, domain axis along the dodge direction (y). The 20 m hull lies ACROSS the motion (x).
Manoeuvre: sidestep D = 30 m, quintic, T = 0.5 s (also T = 0.4 s, the quiet limit). Gravity: W2 cushion assumed on (interior weightless);
shift-only hover limit computed separately.
Ship: 11 hull nodes along x with axial (EA) and lateral shear springs, crew seat at x = +3 m, cargo at x = -4 m, all moving in (x, y);
slow geodesic law in the field: w = xdot - b, w_dot_i = -w_j d_i b_j + F_i/m.
Air: axisymmetric parcel transport (weave_geometry_compare.air) with the dodge trajectory."""
import os, json, time
import numpy as np
import weave_geometry_compare as gc
H = os.path.dirname(os.path.abspath(__file__))
R, DW, g0, CS = 15.0, 2.0, 9.81, 343.0
def quint(D, T):
    s = lambda t: D * (lambda x: 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3)(np.clip(t / T, 0, 1))
    v = lambda t: D / T * (lambda x: 30 * x ** 4 - 60 * x ** 3 + 30 * x ** 2)(np.clip(t / T, 0, 1))
    return s, v
def sech2(z): return 1.0 / np.cosh(np.clip(z, -300, 300)) ** 2
def b_axis_y(t, x, y, s, v):
    """shift with motion axis y, evaluated in the z = 0 plane; returns (b_x, b_y)"""
    u = y - s(t); r = np.sqrt(u * u + x * x) + 1e-300; V = v(t)
    F = 0.5 * (np.tanh((r + R) / DW) - np.tanh((r - R) / DW)); Fp = 0.5 / DW * (sech2((r + R) / DW) - sech2((r - R) / DW)); q = Fp / (2 * r)
    return -V * x * u * q, V * (F + x * x * q)
NODE_X = np.linspace(-10, 10, 11); M_HULL = 59e3; K_AX = 1.75e9; K_SH = 5e8; C_N = 2e5
M_CREW = M_CARGO = 1e3; K_SEAT, C_SEAT = 2e6, 4e4; CREW_NODE, CARGO_NODE = 6, 3
def ship(D, T, dt=1e-5, Tend=None):
    s, v = quint(D, T); Tend = Tend or T + 0.3
    nh = len(NODE_X); X = np.zeros((nh + 2, 2)); X[:nh, 0] = NODE_X; X[nh] = [3.0, 0]; X[nh + 1] = [-4.0, 0]; X0 = X.copy()
    m = np.concatenate([np.full(nh, M_HULL / nh), [M_CREW, M_CARGO]]); W = np.zeros_like(X); ic, ig = nh, nh + 1
    pk = dict(crew=0.0, cargo=0.0, hull=0.0); e = 1e-4
    for k in range(int(Tend / dt)):
        t = k * dt; x, y = X[:, 0], X[:, 1]
        bx, by = b_axis_y(t, x, y, s, v)
        bxp, byp = b_axis_y(t, x + e, y, s, v); bxm, bym = b_axis_y(t, x - e, y, s, v)
        bxq, byq = b_axis_y(t, x, y + e, s, v); bxr, byr = b_axis_y(t, x, y - e, s, v)
        dxbx, dxby = (bxp - bxm) / (2 * e), (byp - bym) / (2 * e); dybx, dyby = (bxq - bxr) / (2 * e), (byq - byr) / (2 * e)
        vel = W + np.stack([bx, by], 1); Fi = np.zeros_like(X)
        d = X[1:nh] - X[:nh - 1] - (X0[1:nh] - X0[:nh - 1]); dv = vel[1:nh] - vel[:nh - 1]
        f = np.stack([K_AX * d[:, 0] + C_N * dv[:, 0], K_SH * d[:, 1] + C_N * dv[:, 1]], 1); Fi[:nh - 1] += f; Fi[1:nh] -= f
        for j, nd in ((ic, CREW_NODE), (ig, CARGO_NODE)):
            fs = -K_SEAT * ((X[j] - X[nd]) - (X0[j] - X0[nd])) - C_SEAT * (vel[j] - vel[nd]); Fi[j] += fs; Fi[nd] -= fs
            key = 'crew' if j == ic else 'cargo'; pk[key] = max(pk[key], float(np.hypot(*fs)) / m[j] / g0)
        pk['hull'] = max(pk['hull'], float(np.abs(f).max()) / 1e3)
        Wd = np.stack([-(W[:, 0] * dxbx + W[:, 1] * dxby), -(W[:, 0] * dybx + W[:, 1] * dyby)], 1) + Fi / m[:, None]
        W = W + dt * Wd; X = X + dt * (W + np.stack([bx, by], 1))
    return dict(crew_peak_g=pk['crew'], cargo_peak_g=pk['cargo'], hull_peak_kN=pk['hull'], final_y_m=float(np.mean(X[:nh, 1])), final_speed=float(np.abs(W).max()))
def air(D, T):
    gc.D, gc.T = D, T; gc.XS = np.arange(-30.0, D + 40.0, 0.5)
    a, L, fld = gc.air(R, DW, 'shift', Tend=T + 0.3); return a, L
def wall_mach(Vpk):
    F = lambda r: 0.5 * (np.tanh((r + R) / DW) - np.tanh((r - R) / DW)); Fp = lambda r: 0.5 / DW * (sech2((r + R) / DW) - sech2((r - R) / DW))
    u = np.linspace(-R - 6 * DW, R + 6 * DW, 801); p = np.linspace(0, R + 6 * DW, 401); U, P = np.meshgrid(u, p); r = np.sqrt(U * U + P * P) + 1e-12
    bx = F(r) + P * P * Fp(r) / (2 * r); bp = -P * U * Fp(r) / (2 * r)
    return float(np.sqrt((1 - bx) ** 2 + bp ** 2).max() * Vpk / CS), float(np.sqrt((1 - bx) ** 2 + bp ** 2).max())
if __name__ == '__main__':
    out = dict(doc=__doc__, cases={})
    M_SHIP = M_HULL + M_CREW + M_CARGO
    for D, T in ((30.0, 0.5), (30.0, 0.4)):
        t0 = time.time(); Vpk = 1.875 * D / T; Apk = 5.7735 * D / T ** 2
        sh = ship(D, T); a, L = air(D, T); mach, fac = wall_mach(Vpk)
        ke = 0.5 * M_SHIP * Vpk ** 2; tt = np.array(L['t']); ka = np.array(L['ke'])
        out['cases'][f'D{D:g}_T{T:g}'] = dict(peak_speed_ms=Vpk, peak_accel_g=Apk / g0, ship=sh, ship_KE_lent_J=ke, air=a,
            wall_mach=mach, quiet_limit_T_s=1.875 * D * fac / CS, peak_power_W=float(max(np.gradient(ka, tt).max(), 0) + M_SHIP * Vpk * Apk / 1.6))
        print(D, T, json.dumps(out['cases'][f'D{D:g}_T{T:g}'], default=float)[:900], f'{time.time() - t0:.0f}s', flush=True)
    # shift-only hover limit: interior shift must grow as g t; wall pattern vs local air reaches c_s at t = c_s / (fac g)
    _, fac = wall_mach(1.0); out['shift_only_hover'] = dict(time_to_sonic_wall_s=CS / (fac * g0), factor=fac,
        note='interior shift beta_z = g t; wall relative speed = fac * g t; lent air KE grows ~ t^2')
    json.dump(out, open(os.path.join(H, 'outing_dodge.json'), 'w'), indent=1, default=float)
    print(out['shift_only_hover'])
