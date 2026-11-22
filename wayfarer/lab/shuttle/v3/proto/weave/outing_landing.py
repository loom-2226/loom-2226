"""Weave outing 3: LANDING IN MODERATE WEATHER (SOL outings brief). NON-CANON. ALL bodies. ALL sponsors. 2026-2226.

Gravity support: W2 cushion = lapse-type field that cancels gravity inside the domain (interior weightless); the zero-expansion shift
alone can hold altitude only ~14 s (outing_dodge.py). Weave shift used for the approach translation.
Part A (air with pressure): linear compressible air (same scheme as weave_shift_gust.py, beta = 0) driven by the field's body force
  d_t w = -c^2 grad(rho')/rho0 + a(t) grad(Phi),  d_t rho' = -rho0 div w,   Phi = (x - X(t)) F(r)
  A1: cushion switching on to a = g over 2 s, held (x = vertical axis).  A2: the earlier lapse DASH (a = a5, X = s5), as a check of the
  collisionless "lapse wake" in weave_geometry_compare.py.
Part B (analytic): wind and gust loads, rain in the weightless interior, ground intersection at touchdown, release."""
import os, json, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
R, DW, CS, RHO0, g0 = 15.0, 2.0, 343.0, 1.2, 9.81
def sech2(z): return 1.0 / np.cosh(np.clip(z, -300, 300)) ** 2
def Fp(r): return 0.5 * (np.tanh((r + R) / DW) - np.tanh((r - R) / DW)), 0.5 / DW * (sech2((r + R) / DW) - sech2((r - R) / DW))
def q5(x): x = np.clip(x, 0, 1); return 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3
def run_forced(acc, Xc, h=1.0, Tend=3.6, xlo=-60.0, xhi=60.0, plo=60.0, sponge=15.0, cfl=0.35, filt=0.2):
    xs = np.arange(xlo, xhi, h) + h / 2; ps = np.arange(0, plo, h) + h / 2; X, P = np.meshgrid(xs, ps, indexing='ij'); nx, npp = X.shape
    dV = 2 * np.pi * P * h * h; dist = np.minimum.reduce([X - xlo, xhi - X, plo - P]); sig = np.where(dist < sponge, 60.0 * ((sponge - dist) / sponge) ** 2, 0.0)
    wx = np.zeros_like(X); wp = np.zeros_like(X); rp = np.zeros_like(X); c2 = CS * CS
    def pad(f, par):
        g = np.empty((nx + 2, npp + 2)); g[1:-1, 1:-1] = f; g[1:-1, 0] = par * f[:, 0]; g[1:-1, -1] = f[:, -1]; g[0, :] = g[1, :]; g[-1, :] = g[-2, :]; return g
    def dx(f, par): g = pad(f, par); return (g[2:, 1:-1] - g[:-2, 1:-1]) / (2 * h)
    def dp(f, par): g = pad(f, par); return (g[1:-1, 2:] - g[1:-1, :-2]) / (2 * h)
    def force(t):
        u = X - Xc(t); r = np.sqrt(u * u + P * P) + 1e-300; F, Fd = Fp(r); a = acc(t)
        return a * (F + u * u * Fd / r), a * (u * P * Fd / r)              # a grad Phi, Phi = u F(r)
    def rhs(wx, wp, rp, t):
        fx, fp = force(t)
        return (-c2 * dx(rp, 1) / RHO0 + fx - sig * wx, -c2 * dp(rp, 1) / RHO0 + fp - sig * wp,
                -RHO0 * (dx(wx, 1) + dp(P * wp, 1) / P) - sig * rp)
    def flt(f, par):
        g = np.empty((nx + 4, npp + 4)); g[2:-2, 2:-2] = f; g[2:-2, 1] = par * f[:, 0]; g[2:-2, 0] = par * f[:, 1]
        g[2:-2, -2] = f[:, -1]; g[2:-2, -1] = f[:, -1]; g[1, :] = g[2, :]; g[0, :] = g[2, :]; g[-2, :] = g[-3, :]; g[-1, :] = g[-3, :]
        d4x = g[:-4, 2:-2] - 4 * g[1:-3, 2:-2] + 6 * g[2:-2, 2:-2] - 4 * g[3:-1, 2:-2] + g[4:, 2:-2]
        d4p = g[2:-2, :-4] - 4 * g[2:-2, 1:-3] + 6 * g[2:-2, 2:-2] - 4 * g[2:-2, 3:-1] + g[2:-2, 4:]
        return f - filt / 16 * (d4x + d4p)
    dt = cfl * h / (CS + 1.0); n = int(Tend / dt); absorbed = 0.0; vmax = 0.0; pmax = 0.0; log = dict(t=[], ke=[], pmax=[])
    for k in range(n):
        t = k * dt; inner = sig == 0
        absorbed += dt * float(np.sum(sig * (RHO0 * (wx * wx + wp * wp) + c2 * rp * rp / RHO0) * dV))
        a = rhs(wx, wp, rp, t); b = rhs(wx + 0.5 * dt * a[0], wp + 0.5 * dt * a[1], rp + 0.5 * dt * a[2], t + 0.5 * dt)
        cc = rhs(wx + 0.5 * dt * b[0], wp + 0.5 * dt * b[1], rp + 0.5 * dt * b[2], t + 0.5 * dt); d = rhs(wx + dt * cc[0], wp + dt * cc[1], rp + dt * cc[2], t + dt)
        wx = flt(wx + dt / 6 * (a[0] + 2 * b[0] + 2 * cc[0] + d[0]), 1); wp = flt(wp + dt / 6 * (a[1] + 2 * b[1] + 2 * cc[1] + d[1]), -1); rp = flt(rp + dt / 6 * (a[2] + 2 * b[2] + 2 * cc[2] + d[2]), 1)
        sp = np.sqrt(wx * wx + wp * wp); vmax = max(vmax, float(sp[inner].max())); pmax = max(pmax, float(np.abs(c2 * rp[inner]).max()))
        if k % max(1, int(0.02 / dt)) == 0:
            log['t'].append(t); log['ke'].append(float(np.sum(0.5 * RHO0 * (wx * wx + wp * wp) * dV))); log['pmax'].append(float(np.abs(c2 * rp).max()))
    # quasi-static prediction p' = rho0 a Phi (max |Phi| ~ R)
    u = X - Xc(Tend); r = np.sqrt(u * u + P * P); F, _ = Fp(r); p_qs = RHO0 * acc(Tend) * np.abs(u * F).max()
    return dict(max_air_speed_ms=vmax, max_pressure_pert_Pa=pmax, final_KE_J=log['ke'][-1], peak_KE_J=max(log['ke']), radiated_J=absorbed,
                quasistatic_pressure_Pa=float(p_qs)), log
def s5(t): return 200.0 * q5(t / 3.0)
def a5(t): x = np.clip(t / 3.0, 0, 1); return 200.0 / 9.0 * (120 * x ** 3 - 180 * x ** 2 + 60 * x)
if __name__ == '__main__':
    out = dict(doc=__doc__)
    t0 = time.time(); r1, L1 = run_forced(lambda t: g0 * q5(t / 2.0), lambda t: 0.0, Tend=3.0); out['A1_cushion_on'] = r1; out['A1_series'] = L1
    print('cushion', r1, f'{time.time() - t0:.0f}s', flush=True)
    t0 = time.time(); r2, L2 = run_forced(a5, s5, xhi=290.0, Tend=3.6); out['A2_lapse_dash_with_pressure'] = r2; out['A2_series'] = L2
    print('lapse dash', r2, f'{time.time() - t0:.0f}s', flush=True)
    # ---------------- Part B ----------------
    u = np.linspace(-R - 8 * DW, R + 8 * DW, 4001); F, Fd = Fp(np.abs(u)); dPhi = F + np.abs(u) * Fd
    reverse = float(-dPhi.min())                                          # peak reverse-force factor in the wall (on axis), in units of g
    M = 61e3; A_side, Cd = 80.0, 1.0                                      # ASSUMED hull side area and drag coefficient
    wind = {}
    for U in (10.0, 15.0):
        Fd_ = 0.5 * RHO0 * U * U * Cd * A_side; wind[f'{U:g}'] = dict(drag_N=Fd_, crew_accel_g=Fd_ / M / g0)
    vt, rain_mm_h = 4.0, 4.0                                              # ~1 mm drops, moderate rain
    out['B'] = dict(reverse_wall_factor_g=reverse, wind_hull_drag=wind,
        rain=dict(drop_terminal_ms=vt, stopping_distance_m=float(vt ** 2 / g0 * np.log(2)), relax_time_s=vt / g0,
                  residence_in_domain_s_at_10ms=2 * R / 10.0, note='drops weightless inside: stop falling within ~1 m, drift with the wind, exit downwind; dry patch under the craft, wetter strip downwind'),
        ground=dict(domain_touches_ground_when_centre_above_m=R + 2 * DW, ring_radius_at_centre_3m_m=float(np.sqrt(R ** 2 - 3.0 ** 2)),
                    note='inside the footprint loose ground matter, water and people are weightless; the wall band presses surface matter down by up to the reverse factor'),
        shift_only_hover_s=14.3)
    json.dump(out, open(os.path.join(H, 'outing_landing.json'), 'w'), indent=1, default=float)
    print(json.dumps(out['B'], default=float))
