"""Weave outing 4: TRANSMEDIUM - entry, exit and skim through a two-layer air/water model with gravity (SOL outings brief). NON-CANON.
ALL bodies. ALL sponsors. 2026-2226.

Model (simplest existing): R 15 m / wall 2 m zero-expansion shift; parcel transport x_dot = beta (exact geodesic, density-independent,
volume-preserving); W2 cushion keeps the domain interior weightless. Gravity enters through the advected configuration:
  - available potential energy APE = g sum m_i dz_i (released as splash / waves / bubble rise once the field lets go);
  - carried fluid across the interface; hydrostatic checks (column tension / cavitation, carried-bubble pressure mismatch).
Transit is kinematic: interface relaxation under gravity during transit is NOT modelled (transit 1.5 s ~ gravity-wave time sqrt(R/g)).
EXIT/ENTRY: vertical transit of 60 m in 1.5 s, domain centre from 30 m below to 30 m above the surface (exit) or reverse (entry);
  one axisymmetric run, gravity direction flipped in post-processing.
SKIM: the existing horizontal 200 m / 3 s dash map with the water surface h metres below the domain centre (3D sampling)."""
import os, json, time
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import weave_geometry_compare as gc
H = os.path.dirname(os.path.abspath(__file__))
R, DW, g0, RW, RA, PATM = 15.0, 2.0, 9.81, 1000.0, 1.2, 101325.0
def F_prof(r): return 0.5 * (np.tanh((r + R) / DW) - np.tanh((r - R) / DW))
def vertical_run(h=0.5):
    gc.D, gc.T = 60.0, 1.5; gc.XS = np.arange(-40.0, 100.0 + 1e-9, h); gc.RS = np.arange(h / 2, 30.0, h)
    a, L, fld = gc.air(R, DW, 'shift', Tend=1.8)
    X0, P0, dX, dP, _ = fld
    return X0, P0, X0 + dX, P0 + dP, h
def analyse_vertical(X0, P0, Xf, Pf, h, mode):
    vol = 2 * np.pi * P0 * h * h; S = 30.0; Xend = 60.0
    if mode == 'exit':                                           # +x up, water below x = 30
        water = X0 < S; height_f = Xf - S; height_0 = X0 - S
    else:                                                        # entry: +x down, water below the surface = x > 30
        water = X0 > S; height_f = S - Xf; height_0 = S - X0
    rho = np.where(water, RW, RA); m = rho * vol; dz = height_f - height_0
    APE = float(g0 * np.sum(m * dz))
    above = water & (height_f > 0.05)                             # water now above the surface
    below_air = (~water) & (height_f < -0.05)                    # air now below the surface
    res = dict(APE_J=APE, water_above_surface_t=float(np.sum(m[above]) / 1e3), water_above_PE_J=float(g0 * np.sum(m[above] * height_f[above])),
               water_above_centroid_m=float(np.sum(m[above] * height_f[above]) / max(np.sum(m[above]), 1e-9)),
               air_below_surface_m3=float(np.sum(vol[below_air])), air_below_mean_depth_m=float(np.sum(vol[below_air] * -height_f[below_air]) / max(np.sum(vol[below_air]), 1e-9)))
    if mode == 'exit':
        # connected water column on the axis from the sea surface up to the weightless interior? weight-bearing height h_eff
        ax = water & (Pf < 1.5); xs = np.sort(Xf[ax]); xs = xs[(xs > S) & (xs < Xend + R)]
        gaps = np.diff(np.concatenate([[S], xs])); connected_to = float(xs[np.argmax(gaps > 3 * h)] if np.any(gaps > 3 * h) else (xs.max() if xs.size else S))
        zz = np.linspace(S, connected_to, 400); heff = float(np.trapezoid(1 - F_prof(np.abs(zz - Xend)), zz)) if connected_to > S else 0.0
        res.update(axis_column_top_m=connected_to - S, weight_bearing_height_m=heff, column_tension_Pa=float(RW * g0 * heff - PATM),
                   cavitates=bool(RW * g0 * heff > PATM - 2.3e3))
    else:
        dc = 30.0; pc = PATM + RW * g0 * dc; Vb = res['air_below_surface_m3']
        res.update(bubble_pressure_mismatch_Pa=pc - PATM, isothermal_volume_ratio=PATM / pc,
                   collapse_energy_J=float(pc * Vb * (1 - PATM / pc) - PATM * Vb * np.log(pc / PATM)), buoyant_APE_J=float(RW * g0 * Vb * res['air_below_mean_depth_m']))
    return res
def skim(hs=(5.0, 10.0, 15.0, 19.0)):
    Fm = json.load(open(os.path.join(H, 'weave_geometry_compare_series.json')))['fields']['shift']
    x0 = np.array(Fm['x0'])[:, 0]; p0 = np.array(Fm['p0'])[0, :]; DX = np.array(Fm['dx']); DP = np.array(Fm['dp'])
    idx = RegularGridInterpolator((x0, p0), DX, bounds_error=False, fill_value=0.0); idp = RegularGridInterpolator((x0, p0), DP, bounds_error=False, fill_value=0.0)
    xs = np.arange(-25.0, 235.0, 1.0); ys = np.arange(-24.5, 25.0, 1.0); out = {}
    for hgt in hs:
        zs = np.arange(-hgt - 24.5, min(-hgt, 24.5) + 1e-9, 1.0) if -hgt > -24.5 else np.array([])
        zs = zs[zs < -hgt]
        Xg, Yg, Zg = np.meshgrid(xs, ys, zs, indexing='ij'); rho0 = np.sqrt(Yg ** 2 + Zg ** 2); ok = rho0 <= p0.max()
        pts = np.stack([Xg[ok], rho0[ok]], 1); dxv = idx(pts); dpv = idp(pts); sinp = Zg[ok] / np.maximum(rho0[ok], 1e-9)
        dz = dpv * sinp; zf = Zg[ok] + dz; m = RW * 1.0
        lifted = zf > -hgt
        out[f'{hgt:g}'] = dict(APE_J=float((RW - RA) * g0 * np.sum(dz)), APE_per_m_J=float((RW - RA) * g0 * np.sum(dz) / 200.0),
            water_lifted_above_surface_t=float(np.sum(lifted) * m / 1e3), max_lift_above_surface_m=float((zf[lifted] + hgt).max()) if lifted.any() else 0.0,
            carried_cap_t=float(np.sum(dxv > 150.0) * m / 1e3), max_horizontal_drift_m=float(dxv.max()) if dxv.size else 0.0)
    return out
if __name__ == '__main__':
    out = dict(doc=__doc__)
    t0 = time.time(); X0, P0, Xf, Pf, h = vertical_run(); print('vertical run', f'{time.time() - t0:.0f}s', flush=True)
    out['exit'] = analyse_vertical(X0, P0, Xf, Pf, h, 'exit'); out['entry'] = analyse_vertical(X0, P0, Xf, Pf, h, 'entry')
    print('exit', json.dumps(out['exit'])); print('entry', json.dumps(out['entry']))
    out['skim'] = skim(); print('skim', json.dumps(out['skim']))
    np.savez_compressed(os.path.join(H, 'outing_transmedium_vertical.npz'), X0=X0[::2, ::2], P0=P0[::2, ::2], Xf=Xf[::2, ::2], Pf=Pf[::2, ::2])
    json.dump(out, open(os.path.join(H, 'outing_transmedium.json'), 'w'), indent=1, default=float)
