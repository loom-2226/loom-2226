"""Picture of the v3 recommendation (b5_concept). ALL bodies. ALL sponsors. 2026-2226."""
import os, sys, json, math, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, Polygon
import b5_concept as C, build_v2b as B
R = json.load(open("b5_concept.json"))
COL = dict(hull=(.86, .87, .85), belly=(.18, .18, .19), glass=(.22, .40, .58), wing=(.80, .81, .79),
           float=(.95, .55, .15), nozzle=(.45, .45, .48), fin=(.75, .76, .74), water=(.55, .75, .90))
def parts(state):
    V, F, tag = C.loft(); T = V[F]
    cx = T[:, :, 0].mean(1); cz = T[:, :, 2].mean(1)
    col = []
    for t, x, z in zip(tag, cx, cz):
        if t in ('belly', 'lower'): col.append(COL['belly'])
        elif t == 'flank' and 2.6 < x < 4.6 and z > 0.55: col.append(COL['glass'])
        elif t == 'top' and 2.5 < x < 4.4: col.append(COL['glass'])
        else: col.append(COL['hull'])
    P = [(T, np.array(col))]
    nz = B.tube((12.6, 0, 0.3), (13.6, 0, 0.3), 0.55, 36, 0.85); P.append((nz[0][nz[1]], np.tile(COL['nozzle'], (len(nz[1]), 1))))
    for s in (1, -1):
        fv, ff = B.fin(s, state != 'stowed'); fv = fv + [0, 0, 0.42]; P.append((fv[ff], np.tile(COL['fin'], (len(ff), 1))))
    if state == 'flight':
        for s in (1, -1):
            y0, y1 = 2.10, C.WING['span'] / 2; (a0, a1), (b0, b1) = C.WING['x'], C.WING['x_tip']
            q = np.array([(a0, s * y0, .2), (a1, s * y0, .2), (b1, s * y1, .32), (b0, s * y1, .32)])
            for dz in (0, .08):
                qq = q + [0, 0, dz]; P.append((np.array([qq[[0, 1, 2]], qq[[0, 2, 3]]]), np.tile(COL['wing'], (2, 1))))
    if state == 'float':
        for s in (1, -1):
            fv, ff = B.tube((C.FLOAT['x'][0], s * C.FLOAT['y'], C.FLOAT['z']), (C.FLOAT['x'][1], s * C.FLOAT['y'], C.FLOAT['z']), C.FLOAT['r'], 36)
            P.append((fv[ff], np.tile(COL['float'], (len(ff), 1))))
            for xe in C.FLOAT['x']:
                sv, sf = B.uvsphere((xe, s * C.FLOAT['y'], C.FLOAT['z']), C.FLOAT['r'], 24, 12); P.append((sv[sf], np.tile(COL['float'], (len(sf), 1))))
            for xa in (5.0, 10.5):
                av, af = B.tube((xa, s * 1.9, -0.45), (xa, s * C.FLOAT['y'], C.FLOAT['z']), 0.07, 12); P.append((av[af], np.tile(COL['nozzle'], (len(af), 1))))
    return P
def view(ax, P, az, el, title, lim, water=None):
    T = np.vstack([p[0] for p in P]) - [6.6, 0, 0.2]; Cc = np.vstack([p[1] for p in P])
    if water is not None:
        zw = water - 0.2; keep = T[:, :, 2].mean(1) > zw; T, Cc = T[keep], Cc[keep]
    a_, e = np.radians(az), np.radians(el)
    Rz = np.array([[np.cos(a_), -np.sin(a_), 0], [np.sin(a_), np.cos(a_), 0], [0, 0, 1]]); Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    V = T @ (Rx @ Rz).T; n = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    Lt = np.array([-.35, -.75, .55]); Lt /= np.linalg.norm(Lt); sh = np.clip(.4 + .7 * np.abs(n @ Lt), 0, 1.1)
    o = np.argsort(-V[:, :, 1].mean(1)); cols = np.clip(Cc[o] * sh[o][:, None], 0, 1)
    if water is not None:
        g = np.array([(-10, -10, zw), (10, -10, zw), (10, 10, zw), (-10, 10, zw)]) @ (Rx @ Rz).T
        ax.add_patch(Polygon(g[:, [0, 2]], fc=COL['water'], ec='none', zorder=0))
        P = T.reshape(-1, 3)[np.isclose(T.reshape(-1, 3)[:, 2], zw, atol=0.25)] @ (Rx @ Rz).T
    ax.add_collection(PolyCollection(V[o][:, :, [0, 2]], facecolors=cols, edgecolors=cols, linewidths=.5, antialiaseds=False, alpha=1))
    ax.set_xlim(-lim[0], lim[0]); ax.set_ylim(-lim[1], lim[1]); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, loc="left", fontsize=11, weight="bold")
fig = plt.figure(figsize=(16, 11)); fig.patch.set_facecolor("#f4f3ef")
a1 = fig.add_axes([0.01, 0.50, 0.55, 0.45]); view(a1, parts('flight'), 28, 30, "Flight: telescoping wings out (14 m span)", (8.4, 4.6))
a2 = fig.add_axes([0.01, 0.03, 0.55, 0.45]); view(a2, parts('float'), 150, 22, "On the water: floats out, wings in", (8.4, 4.6), water=R["waterline_z_m"]["59t_floats_out"])
a3 = fig.add_axes([0.60, 0.53, 0.18, 0.40])
a3.add_patch(Circle((0, 0), 2.4, fc="#e5e7e9", ec="#95a5a6")); a3.add_patch(Circle((0, 0), 2.15, fc="none", ec="#95a5a6", ls="--"))
old = np.array(B.section(8.0)); new = np.array(C.section(8.0))
a3.add_patch(Polygon(new, fc="#2f6fb0", alpha=.55, ec="k")); a3.add_patch(Polygon(old, fc="none", ec="#c0392b", lw=2, ls="--"))
for s in (1, -1):
    a3.add_patch(Circle((s * C.FLOAT['y'], C.FLOAT['z']), C.FLOAT['r'], fc="#f39c12", alpha=.5, ec="#d35400", ls=":"))
a3.axhline(R["waterline_z_m"]["59t_floats_out"], color="#2e86c1", lw=1.5); a3.text(-3.2, R["waterline_z_m"]["59t_floats_out"] + .08, "water 59 t", fontsize=7, color="#2e86c1")
a3.set_xlim(-3.3, 3.3); a3.set_ylim(-2.6, 2.6); a3.set_aspect("equal"); a3.axis("off")
a3.set_title("Section at x 8 m: B4-S (red dashed)\nvs grown (blue); floats out (orange)", fontsize=9)
a4 = fig.add_axes([0.60, 0.05, 0.38, 0.44]); a4.axis("off")
E4 = R["B4S_reference"]
rows = [("", "B4-S today", "Recommended"),
        ("Hull volume", f"{E4['volume_m3']:.0f} m³", f"{R['hull_volume_m3']:.0f} m³ (+{R['hull_volume_m3']-E4['volume_m3']:.0f})"),
        ("+ pop-out floats", "—", f"{R['float_volume_m3']:.0f} m³ → {R['total_buoyant_m3']:.0f} m³ ✓"),
        ("Fits bay (≤ 2.15 m)", "2.14 m", f"{R['bay_fit']['min_enclosing_radius_m']:.2f} m ✓"),
        ("Re-entry L/D (58 t)", f"{E4['earth_entry_58t']['LD']:.2f}", f"{R['earth_entry_58t']['LD']:.2f}"),
        ("Crossrange", f"{E4['earth_entry_58t']['crossrange_km']:.0f} km", f"{R['earth_entry_58t']['crossrange_km']:.0f} km"),
        ("Peak heating", f"{E4['earth_entry_58t']['peak_q_Wcm2']:.0f} W/cm²", f"{R['earth_entry_58t']['peak_q_Wcm2']:.0f} W/cm²"),
        ("Glide L/D", f"{E4['glide_LD']:.1f}", f"{R['glide_43t']['telescoping_14m']['LD']:.1f}"),
        ("Touchdown speed", f"{E4['touchdown_ms']:.0f} m/s", f"{R['glide_43t']['telescoping_14m']['touchdown_ms']:.0f} m/s ✗ (needs ~40)"),
        ("Waterline 59 t", "—", f"z {R['waterline_z_m']['59t_floats_out']:+.2f} m (below chine)"),]
for i, r in enumerate(rows):
    for j, c in enumerate(r):
        a4.text([0, .42, .68][j], .95 - i * .085, c, fontsize=10, weight="bold" if i == 0 or j == 0 else "normal", transform=a4.transAxes)
a4.text(0, .02, "Still to fix: water touchdown speed (flaps + fan lift, step 5);\ntorch exit only ~0.4 m above water (W3): light it airborne.", fontsize=9, color="#c0392b", transform=a4.transAxes)
fig.suptitle("Shuttle v3 recommendation: B4 body grown in the bay + pop-out floats + telescoping wings", fontsize=14, y=.99)
fig.savefig("b5_concept.png", dpi=110, facecolor=fig.get_facecolor())
