"""Wayfarer v1 shuttle, 1:100 print solid (Claude, 14 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.
Decision: shuttle_print_1to100_2026_11_14 (NON-CANON v1 shuttle; print LOD only).
Source numbers: wayfarer/lab/shuttle/shuttle_v1_full_docked_G8.py (lathe profile, door/TPS sectors, spine groove, seams,
blades, belly nozzles, nozzle ring). Ship frame: s = X - 18.75 (nose 0, tail 12.8 m); azimuth a: Y = r cos a, Z = r sin a.
Method: a lathe grid. Rows run along the meridian (profile + every feature edge), columns around the axis (1 deg + every
feature edge). Grooves are depth offsets on vertices; paired grid lines 0.004 mm apart give near-vertical groove walls.
Poles (nose tip, tail centre) collapse to single vertices. Prints standing on its tail. Units mm."""
import numpy as np, math, struct, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'parts'); os.makedirs(OUT, exist_ok=True)
PROF = json.load(open(os.path.join(HERE, '..', 'hull_1to100', 'print_profile_1to100.json'))); PP = PROF['profiles'][PROF['active']]
GW, GD = PP['groove_width_mm'], PP['groove_depth_mm']; EPS = 0.002; K = 10.0
PROFILE = [(0, 0), (.05, .33), (.28, .55), (1.5, 1.12), (4.0, 1.9), (12.4, 1.9), (12.8, 1.72), (12.8, 0)]
PROFILE = [(s * K, r * K) for s, r in PROFILE]
DOOR = (math.degrees(math.pi / 2 - (-.75 + 1.62)), math.degrees(math.pi / 2 + .75))     # 40.15 .. 132.97
TPS = (137.0, 223.0)
GROOVE = dict(s0=7.2 * K, s1=12.4 * K, y_floor=1.64 * K, z_half=.55 * K)
A_GROOVE = math.degrees(math.asin(.55 / 1.9))                                         # groove wall azimuth at the skin
def adiff(a, b): return (a - b + 180) % 360 - 180

# ---------------- features in (s mm, a deg) ----------------
rings = []   # (s, a_from, a_to) ; a range None = full circle
for s in (4.35, 6.50): rings.append((s * K, DOOR[1], DOOR[0] + 360))          # mid hull, outside the door
for s in (4.08, 6.82): rings.append((s * K, DOOR[0], DOOR[1]))                # door panel
for s in (7.8, 9.6, 11.4): rings.append((s * K, None, None))                  # aft hull
for s in (5.0, 7.2, 9.5, 11.6): rings.append((s * K, TPS[0], TPS[1]))         # heat shield
for s in (4.0, 6.9): rings.append((s * K, DOOR[0], DOOR[1]))                  # door outline ends
longs = [(a, 4.0 * K, 6.9 * K) for a in DOOR] + [(a, 0.5 * K, 12.4 * K) for a in TPS]   # door edges; heat-shield edges
PITS = [(s * K, 180 + sg * math.degrees(math.asin(.45 / 1.7)), 1.6, 1.0) for s in (3.4, 10.0) for sg in (-1, 1)]  # belly nozzles: centre, a, radius, depth
BLADE_Z = [(.02, .44), (-.44, -.02)]                                            # upper blade pair (chord .42 at z +-.23)
CAP_BANDS = [(6.8, 8.8)]                                                        # nozzle ring torus .78 +- .10 on the tail face (mm)

def in_arc(a, a0, a1):
    if a0 is None: return np.ones_like(a, bool)
    return ((a - a0) % 360) <= ((a1 - a0) % 360)

def meridian_rows():
    """Meridian samples (s, r, ns, nr, seg) incl. every feature line (paired +-EPS edges)."""
    s_lines = set()
    for s, *_ in rings: s_lines |= {s - GW / 2, s - GW / 2 + EPS, s + GW / 2 - EPS, s + GW / 2}
    for _, s0, s1 in longs: s_lines |= {s0, s1}
    s_lines |= {GROOVE['s0'], GROOVE['s0'] + EPS, GROOVE['s1'] - EPS, GROOVE['s1']}
    for sc, a, rad, d in PITS: s_lines |= set(np.round(np.arange(sc - rad - .2, sc + rad + .21, 0.1), 4))
    r_lines = set()
    for r0, r1 in CAP_BANDS: r_lines |= {r0, r0 + EPS, r1 - EPS, r1}
    rows = []
    for i, ((s0, r0), (s1, r1)) in enumerate(zip(PROFILE, PROFILE[1:])):
        L = math.hypot(s1 - s0, r1 - r0); ns, nr = -(r1 - r0) / L, (s1 - s0) / L        # outward normal (cap: +s)
        if s1 > s0 + 1e-9:
            ts = sorted({0.0, 1.0} | {(s - s0) / (s1 - s0) for s in s_lines if s0 < s < s1})
            ts = sorted(set(ts) | set(np.linspace(0, 1, max(2, int(L / 2.0) + 1))))     # 2 mm along long spans for safety
        else:
            ts = sorted({0.0, 1.0} | {(r0 - r) / (r0 - r1) for r in r_lines if min(r0, r1) < r < max(r0, r1)})
        for t in ts[:-1] if i < len(PROFILE) - 2 else ts:
            rows.append([s0 + t * (s1 - s0), r0 + t * (r1 - r0), ns, nr, i])
    R = np.array(rows)
    # average normals at profile corners (duplicate s,r)
    return R

def columns():
    a = set(np.round(np.arange(0, 360, 1.0), 6))
    for s, a0, a1 in rings:
        if a0 is not None: a |= {a0 % 360, a1 % 360}
    for aa, *_ in longs:
        h = math.degrees(GW / 2 / 19.0); a |= {(aa - h) % 360, (aa - h + .01) % 360, (aa + h - .01) % 360, (aa + h) % 360}
    for e in (A_GROOVE, -A_GROOVE): a |= {e % 360, (e + 0.02 * np.sign(-e)) % 360}
    for z0, z1 in BLADE_Z:
        for z in (z0, z1):
            for zz in (z * K - GW / 2, z * K - GW / 2 + EPS, z * K + GW / 2 - EPS, z * K + GW / 2):
                a |= {math.degrees(math.atan2(zz, GROOVE['y_floor'])) % 360}
    for sc, ac, rad, d in PITS: a |= set(np.round(np.arange(ac - 6, ac + 6.01, 0.2), 4) % 360)
    return np.array(sorted(a))

def depth_and_floor(S, A, Rm, seg):
    """Groove depth (mm, along the inward normal) per vertex, and the spine-groove radius cap."""
    D = np.zeros_like(S)
    on_hull = seg <= 6 - 1  # cones + cylinder + tail cone (cap handled separately)
    for s, a0, a1 in rings:
        D = np.where((np.abs(S - s) < GW / 2 - 1e-6) & in_arc(A, a0, a1) & (seg < 6), GD, D)
    for aa, s0, s1 in longs:
        D = np.where((np.abs(np.radians(adiff(A, aa)) * Rm) < GW / 2 - 1e-6) & (S >= s0 - 1e-6) & (S <= s1 + 1e-6) & (seg < 6), GD, D)
    for sc, ac, rad, d in PITS:
        D = np.where((np.hypot(S - sc, np.radians(adiff(A, ac)) * Rm) < rad) & (seg < 6), np.maximum(D, d), D)
    for r0, r1 in CAP_BANDS:
        D = np.where((seg == 6) & (Rm > r0 + 1e-6) & (Rm < r1 - 1e-6), GD, D)
    # spine groove: radius limited to the floor plane Y = 16.4 mm inside |a| < A_GROOVE, s in [s0, s1]
    ing = (S > GROOVE['s0'] + 1e-6) & (S < GROOVE['s1'] - 1e-6) & (np.abs(adiff(A, 0)) < A_GROOVE + 1e-6) & (seg < 6)
    Rfloor = np.where(ing, GROOVE['y_floor'] / np.cos(np.radians(np.clip(np.abs(adiff(A, 0)), 0, 89))), np.inf)
    # blade outlines engraved into the groove floor
    Zf = Rfloor * np.sin(np.radians(adiff(A, 0)))
    for z0, z1 in BLADE_Z:
        for z in (z0 * K, z1 * K): D = np.where(ing & (np.abs(Zf - z) < GW / 2 - 1e-6), GD, D)
    return D, Rfloor

def build():
    Rw = meridian_rows(); A = columns(); nr_, nc = len(Rw), len(A)
    S = np.repeat(Rw[:, 0:1], nc, 1); Rm = np.repeat(Rw[:, 1:2], nc, 1); seg = np.repeat(Rw[:, 4:5], nc, 1)
    NS = np.repeat(Rw[:, 2:3], nc, 1); NR = np.repeat(Rw[:, 3:4], nc, 1); AA = np.repeat(A[None, :], nr_, 0)
    D, Rfloor = depth_and_floor(S, AA, Rm, seg)
    Sx = S - D * NS; Rr = np.minimum(Rm - D * NR, Rfloor - D)
    Rr = np.where(Rm < 1e-9, 0.0, np.maximum(Rr, 0.0))
    th = np.radians(AA); Y = Rr * np.cos(th); Z = Rr * np.sin(th)
    # vertices; poles collapse
    idx = np.arange(nr_ * nc).reshape(nr_, nc); verts = np.stack([Sx, Y, Z], -1).reshape(-1, 3)
    for i in range(nr_):
        if Rm[i, 0] < 1e-9: idx[i, :] = idx[i, 0]
    T = []
    for i in range(nr_ - 1):
        a = idx[i]; b = idx[i + 1]; a2 = np.roll(a, -1); b2 = np.roll(b, -1)
        T.append(np.stack([a, b, b2], 1)); T.append(np.stack([a, b2, a2], 1))
    T = np.concatenate(T); T = T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
    F = verts[T]
    vol = float(np.einsum('ij,ij->i', F[:, 0], np.cross(F[:, 1], F[:, 2])).sum() / 6)
    if vol < 0: F = F[:, ::-1]; T = T[:, ::-1]; vol = -vol
    from collections import Counter
    E = Counter(map(tuple, np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])))
    un = sum(1 for (p, q), c in E.items() if E.get((q, p), 0) != c)
    # print pose: standing on the tail, nose up
    P = np.stack([F[..., 1], F[..., 2], 12.8 * K - F[..., 0]], -1)
    P = P[:, ::-1]                 # mirror from the s flip
    P[..., 0] += 25; P[..., 1] += 25
    return P.astype(np.float32), vol, un, nr_, nc

def main():
    P, vol, un, nr_, nc = build()
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(P), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); rec['n'] = n; rec['v'] = P
    with open(os.path.join(OUT, 'shuttle_v1_1to100.stl'), 'wb') as fh:
        fh.write(b'Wayfarer v1 shuttle 1:100 (NON-CANON) print'.ljust(80, b' ')); fh.write(struct.pack('<I', len(P))); fh.write(rec.tobytes())
    # analytic lathe volume (no grooves) for a sanity bound
    lv = sum(math.pi * (s1 - s0) * (r0 * r0 + r0 * r1 + r1 * r1) / 3 for (s0, r0), (s1, r1) in zip(PROFILE, PROFILE[1:]))
    V = P.reshape(-1, 3)
    man = dict(header='ALL bodies. ALL sponsors. 2026-2226.', decision='shuttle_print_1to100_2026_11_14', status='PLACEHOLDER profile, untested; NON-CANON v1 shuttle',
               file='parts/shuttle_v1_1to100.stl', triangles=len(P), grid=[nr_, nc], size_mm=[round(float(v), 2) for v in (V.max(0) - V.min(0))],
               volume_mm3=round(vol, 1), lathe_volume_no_grooves_mm3=round(lv, 1), volume_ratio=round(vol / lv, 4),
               unmatched_edges=un, watertight='PASS' if un == 0 else 'FAIL',
               print='standing on its tail, nose up, no supports; 128 mm tall',
               features='9 ring-seam sets, door outline, heat-shield edges, spine groove 2.6 mm deep with 2 engraved blade outlines, 4 belly-nozzle pits, nozzle-ring band on the tail face',
               declared='grooves 0.5 mm (true 0.17-0.4); belly nozzles shown as 3.2 mm pits; internal parts not modelled')
    json.dump(man, open(os.path.join(HERE, 'shuttle_print_manifest.json'), 'w'), indent=1)
    print(json.dumps(man, indent=1))
if __name__ == '__main__': main()
