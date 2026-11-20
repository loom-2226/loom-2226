"""Shuttle v3 recommendation: B4 angular body grown in the bay + pop-out floats +
telescoping wings + planing step. Concept geometry and ROM numbers.
ALL bodies. ALL sponsors. 2026-2226. NON-CANON engineering screen."""
import sys, os, json, math
import numpy as np
from matplotlib.path import Path
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'v2_lifting_body'))
import build_v2b as B, aero_test as AT

GROW = dict(ridge=0.45, shoulder_z=0.22, shoulder_y=-0.10, keel=0.30)  # m at full section, scaled with local size
STEP_X = 8.6            # planing step (belly drops 0.06 m aft of it is drawn as a line; ROM ignores it)
FLOAT = dict(x=(3.6, 12.0), r=0.62, y=2.55, z=-0.55)   # deployed sponson centre line (from the lower flank)
WING = dict(span=14.0, S=18.0, x=(6.6, 9.4), x_tip=(8.0, 9.6))   # telescoping wing deployed
B4_VOL = 82.45

def section(x):
    P = B.section(x); s = max(0.0, min(1.0, P[2][0] / 2.13))     # local size vs full chine half-width
    rz = P[0][1] + GROW['ridge'] * s
    sy, sz = P[1][0] + GROW['shoulder_y'] * s, P[1][1] + GROW['shoulder_z'] * s
    (cy, cz), (by, bz) = P[2], P[3]
    kz = P[4][1] - GROW['keel'] * s                               # shallow V keel line
    return [(0, rz), (sy, sz), (cy, cz), (by, bz), (0, kz), (-by, bz), (-cy, cz), (-sy, sz)]

def loft():
    V, F, tag = [], [], []; nr = 8; rings = []
    for x in B.STATIONS:
        rings.append(len(V)); V += [(x, y, z) for y, z in section(x)]
    nose = len(V); V.append((0.0, 0.0, -0.5)); tail = len(V); V.append((12.8, 0.0, 0.3))
    for k in range(len(B.STATIONS) - 1):
        a0, b0 = rings[k], rings[k + 1]
        for i in range(nr):
            j = (i + 1) % nr; F += [(a0 + i, a0 + j, b0 + i), (a0 + j, b0 + j, b0 + i)]; tag += [B.EDGE[i]] * 2
    for i in range(nr):
        j = (i + 1) % nr; F.append((nose, rings[0] + j, rings[0] + i)); tag.append(B.EDGE[i])
        F.append((rings[-1] + i, rings[-1] + j, tail)); tag.append('base')
    return np.array(V, float), np.array(F)[:, ::-1], tag

def vol(V, F):
    T = V[F]; return abs(np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6)

def area_below(x, zw, n=120):
    poly = Path(np.array(section(x) + [section(x)[0]]))
    yy, zz = np.meshgrid(np.linspace(-2.3, 2.3, n), np.linspace(-1.6, 2.2, n)); pts = np.c_[yy.ravel(), zz.ravel()]
    inside = poly.contains_points(pts) & (pts[:, 1] < zw)
    return inside.mean() * 4.6 * 3.8

def float_area_below(zw):
    r, zc = FLOAT['r'], FLOAT['z']; h = np.clip(zw - (zc - r), 0, 2 * r)
    return 2 * (r * r * math.acos((r - h) / r) - (r - h) * math.sqrt(max(0, 2 * r * h - h * h)))

def displaced(zw, floats):
    xs = np.linspace(0.02, 12.78, 96); dx = xs[1] - xs[0]
    v = sum(area_below(x, zw) for x in xs) * dx
    if floats: v += float_area_below(zw) * (FLOAT['x'][1] - FLOAT['x'][0])
    return v

def waterline(m_t, floats):
    need = m_t / 1.025; lo, hi = -1.5, 2.2
    for _ in range(30):
        mid = (lo + hi) / 2
        if displaced(mid, floats) < need: lo = mid
        else: hi = mid
    return round((lo + hi) / 2, 3)

if __name__ == '__main__':
    V, F, tag = loft(); Vh = vol(V, F)
    fl_vol = 2 * math.pi * FLOAT['r'] ** 2 * (FLOAT['x'][1] - FLOAT['x'][0])
    yz = np.vstack([np.array(section(x)) for x in np.linspace(0, 12.8, 65)])
    zs = np.linspace(-1.5, 2.2, 371); rr = [np.hypot(yz[:, 0], yz[:, 1] - z).max() for z in zs]
    T = V[F]; n, A = AT.geom(T); Swet = float(A.sum()); Sb = float(AT.planform(T))
    Abase = float(sum(0.5 * np.linalg.norm(np.cross(T[i][1] - T[i][0], T[i][2] - T[i][0])) for i, t in enumerate(tag) if t == 'base'))
    v = dict(T=T, S_body=Sb, S_wing=0.0, span=4.26, Swet=Swet, Abase=Abase, sharp=True, rn=0.25)
    hyper = max(float(np.divide(*AT.newtonian(T, Sb, Swet, a, 1.2))) for a in range(10, 56, 5))
    e = AT.entry(v, 'Earth', 58e3, 40)
    vw = dict(v, S_wing=WING['S'], span=WING['span']); l = AT.landing(vw, 1.225, 9.81, 43.5e3)
    vf = dict(v, S_wing=13.0, span=8.3); lf = AT.landing(vf, 1.225, 9.81, 43.5e3)
    AT.build(); B4 = AT.VEH['B4 double fold']; e4 = AT.entry(B4, 'Earth', 58e3, 40); l4 = AT.landing(B4, 1.225, 9.81, 43.5e3)
    out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "grow_m": GROW, "float": FLOAT, "wing": WING,
           "hull_volume_m3": round(Vh, 1), "float_volume_m3": round(fl_vol, 1), "total_buoyant_m3": round(Vh + fl_vol, 1),
           "W2_hull_plus_floats_ge_111": bool(Vh + fl_vol >= 110.6), "W2_hull_alone_ge_74": bool(Vh >= 73.8),
           "bay_fit": {"min_enclosing_radius_m": round(min(rr), 3), "about_z_m": round(float(zs[int(np.argmin(rr))]), 3), "envelope_r_m": 2.15, "fits": bool(min(rr) <= 2.15)},
           "hyper_LD_max": round(hyper, 2),
           "earth_entry_58t": {k: round(float(e[k]), 2) for k in ("alpha", "LD", "beta", "peak_g", "peak_q_Wcm2", "heat_load_MJm2", "crossrange_km")},
           "glide_43t": {"telescoping_14m": {"LD": round(l["LDmax"], 2), "touchdown_ms": round(l["v_td"], 1)},
                         "B4_fold_8m": {"LD": round(lf["LDmax"], 2), "touchdown_ms": round(lf["v_td"], 1)}},
           "waterline_z_m": {"59t_floats_stowed": waterline(59, False), "59t_floats_out": waterline(59, True),
                             "75.6t_floats_out": waterline(75.6, True)},
           "B4S_reference": {"volume_m3": B4_VOL, "earth_entry_58t": {k: round(float(e4[k]), 2) for k in ("LD", "crossrange_km", "peak_q_Wcm2")},
                             "glide_LD": round(l4["LDmax"], 2), "touchdown_ms": round(l4["v_td"], 1)}}
    json.dump(out, open(os.path.join(HERE, 'b5_concept.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))
