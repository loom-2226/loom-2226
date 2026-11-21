"""Finite Weave dash: what the moving shift domain does to ambient matter (air), Alcubierre-type vs Natario-type.
NON-CANON physics exercise (SOL handoff e17fd62). ALL bodies. ALL sponsors. 2026-2226.

DERIVED (exact, not an assumption): with unit lapse and flat slices (Weave foundations §5, N=1, gamma_ij=delta_ij), Eulerian
observers are geodesic. Matter initially at rest where beta=0 is Eulerian, and a geodesic congruence keeps it Eulerian, so
    dx^i/dt = beta^i(x,t)          (dust; exact for geodesic test matter)
    d ln(rho)/dt = -div(beta)      (continuity along the flow)
A perfect fluid at uniform pressure is consistent with this motion only where div(beta)=0 (no pressure gradient is created).
So the domain's EXPANSION field theta = div(beta) decides whether air is compressed (pressure waves) or displaced incompressibly.
Earth gravity, free surfaces, solids and viscosity are not modelled (stated as open)."""
import os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
R, D, V0 = 10.0, 2.0, 100.0                  # domain radius, wall width (m), dash speed (m/s): SOL's test case
P0, RHO0, GAM = 101325.0, 1.225, 1.4
def f(r): return 0.5 * (1 - np.tanh((r - R) / D))
def fp(r): return -0.5 / D / np.cosh((r - R) / D) ** 2
def vt(t):                                   # smooth start (0-1 s), cruise (1-2 s), stop (2-3 s)
    s = lambda u: np.clip(u, 0, 1) ** 2 * (3 - 2 * np.clip(u, 0, 1))
    return V0 * (s(t) - s(t - 2.0))
def field(kind, x, y, X, v):
    sx = x - X; r = np.sqrt(sx ** 2 + y ** 2) + 1e-9
    if kind == 'alcubierre':
        bx = v * f(r); by = 0 * x; div = v * fp(r) * sx / r
    else:                                     # Natario zero-expansion: beta = v curl( f(r) e_x x r / 2 )
        bx = v * (f(r) + 0.5 * r * fp(r) - 0.5 * fp(r) * sx ** 2 / r); by = v * (-0.5 * fp(r) * sx * y / r); div = 0 * x
    return bx, by, div
def run(kind, dt=0.002, T=3.6):
    xs, ys = np.meshgrid(np.arange(-40, 262, 1.0), np.arange(0.25, 30.25, 0.5))
    x, y = xs.ravel().copy(), ys.ravel().copy(); x0, y0 = x.copy(), y.copy(); lnr = np.zeros_like(x)
    X = 0.0; t = 0.0; rmax = np.zeros_like(x); rmin = np.zeros_like(x); ke_peak = 0.0
    w = 2 * math.pi * ys.ravel() * 1.0 * 0.5    # ring volume per particle (axisymmetric about the dash axis)
    while t < T:
        def rhs(x, y, X, t):
            bx, by, div = field(kind, x, y, X, vt(t)); return bx, by, -div
        k1 = rhs(x, y, X, t); Xm = X + 0.5 * dt * vt(t)
        k2 = rhs(x + .5 * dt * k1[0], y + .5 * dt * k1[1], Xm, t + .5 * dt)
        k3 = rhs(x + .5 * dt * k2[0], y + .5 * dt * k2[1], Xm, t + .5 * dt)
        k4 = rhs(x + dt * k3[0], y + dt * k3[1], X + dt * vt(t + .5 * dt), t + dt)
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); y += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        lnr += dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]); X += dt * vt(t + .5 * dt); t += dt
        rmax = np.maximum(rmax, lnr); rmin = np.minimum(rmin, lnr)
        if abs(t - 1.5) < dt / 2:              # ambient kinetic energy at cruise (dust follows beta)
            bx, by, _ = field(kind, x, y, X, vt(t)); ke_peak = float(np.sum(0.5 * RHO0 * np.exp(lnr) * (bx ** 2 + by ** 2) * w * np.exp(-lnr)))
    r = np.exp(lnr); rr = np.exp(rmax)
    A = P0 * w * ((rr ** (GAM - 1) - 1) / (GAM - 1) + (1 / rr - 1))           # isentropic exergy of the peak compression (upper-bound scale)
    Afin = P0 * w * ((r ** (GAM - 1) - 1) / (GAM - 1) + (1 / r - 1))
    dxf = x - x0; dist = X
    captured = (dxf > 0.8 * dist); swept = (np.abs(y0) < R) & (x0 > 0) & (x0 < dist)
    return dict(kind=kind, dash_distance_m=round(dist, 1), max_density_ratio=round(float(rr.max()), 2), min_density_ratio=round(float(np.exp(rmin).min()), 3),
                final_density_range=[round(float(r.min()), 3), round(float(r.max()), 2)], compression_exergy_peak_GJ=round(float(A.sum()) / 1e9, 3),
                residual_exergy_after_stop_GJ=round(float(Afin.sum()) / 1e9, 3), ambient_KE_at_cruise_MJ=round(ke_peak / 1e6, 2),
                fraction_of_swept_cylinder_carried_to_end=round(float(captured[swept].mean()), 3) if swept.any() else None,
                max_forward_drift_outside_domain_m=round(float(dxf[(np.abs(y0) > R + 3 * D)].max()), 2), mean_drift_on_axis_ahead_m=round(float(dxf[(y0 < 2) & (x0 > dist + 3 * R)].mean()), 3),
                _grid=dict(nx=302, ny=60, dx=np.round(dxf, 2).tolist(), r=np.round(r, 4).tolist()))
res = {k: run(k) for k in ('alcubierre', 'natario')}
summary = {k: {a: b for a, b in v.items() if a != '_grid'} for k, v in res.items()}
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='NON-CANON physics', doc=__doc__, case=dict(R_m=R, wall_m=D, v_ms=V0, profile='f=1/2[1-tanh((r-R)/delta)]', ramp='1 s up, 1 s cruise, 1 s down'),
           results=summary, grids={k: v['_grid'] for k, v in res.items()})
json.dump(out, open(os.path.join(H, 'dash_ambient.json'), 'w'))
if __name__ == '__main__':
    for k, v in summary.items(): print(k, v)
