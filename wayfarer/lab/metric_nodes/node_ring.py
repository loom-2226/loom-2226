"""Two nacelles vs four nacelles that lock into an aft ring (White-style hoop). NON-CANON sketch search.
ALL bodies. ALL sponsors. 2026-2226."""
import os, json, math, numpy as np
import node_optimize as NO, node_nacelles as NN
HERE = os.path.dirname(os.path.abspath(__file__))
HOOP = dict(x=52.6, R=4.4, r=0.35)
def hoop_points(n=4000, rng=None):
    rng = rng or np.random.default_rng(1); u = rng.random(n) * 2 * math.pi; v = rng.random(n) * 2 * math.pi
    R, r = HOOP['R'], HOOP['r']; P = np.c_[HOOP['x'] + r * np.sin(v), (R + r * np.cos(v)) * np.cos(u), (R + r * np.cos(v)) * np.sin(u)]
    return P, np.full(n, 4 * math.pi ** 2 * R * r / n)
def hoop_sites(da=6, dv=60):
    R, r = HOOP['R'], HOOP['r'] + .05; S = []
    for a in np.arange(0, 360, da):
        for v in np.arange(0, 360, dv):
            u, w = math.radians(a), math.radians(v); S.append(np.array([HOOP['x'] + r * math.sin(w), (R + r * math.cos(w)) * math.cos(u), (R + r * math.cos(w)) * math.sin(u)]))
    return S
def run(azs, hoop, P0, w0, fixed):
    P, w = P0, w0
    for az in azs: p, ww = NN.nacelle_points(az); P = np.vstack([P, p]); w = np.r_[w, ww]
    if hoop: p, ww = hoop_points(); P = np.vstack([P, p]); w = np.r_[w, ww]
    S, tag = NO.sites('cone')
    for az in azs: s = NN.nacelle_sites(az); S = np.vstack([S, s]); tag = np.r_[tag, ['nacelle'] * len(s)]
    if hoop: s = hoop_sites(); S = np.vstack([S, s]); tag = np.r_[tag, ['hoop'] * len(s)]
    best = None
    for rs in range(4):
        L = NO.optimise(S, fixed, P, w, np.random.default_rng(100 + rs)); m = NO.evaluate(L, P, w)
        sc = m['mean_gap_m'] + 0.5 * m['load_cv']
        if best is None or sc < best[0]: best = (sc, L, m)
    _, L, m = best; tg = NO.cKDTree(S).query(L[16:])[1]
    m['count_by_zone'] = {str(z): int((tag[tg] == z).sum()) for z in set(tag)}; m['count_by_zone']['ring0_fixed'] = 16
    # asymmetry: spread of node count by quadrant aft of 34.3 m
    aft = L[L[:, 0] > 34.3]; q = np.bincount(((np.degrees(np.arctan2(aft[:, 2], aft[:, 1])) + 360 + 45) % 360 // 90).astype(int), minlength=4)
    m['aft_quadrant_counts'] = q.tolist()
    return dict(metrics={k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}, nodes=[[float(v) for v in p] for p in L])
if __name__ == '__main__':
    rng = np.random.default_rng(2226)
    T = NO.load_glb(os.path.join(NO.W, 'render/out/wayfarer_exterior_detail_88ce19fc_stowed_closed.glb')); P, w = NO.envelope(T, rng)
    fixed = np.array([NO.cyl(n['x'], n['a'], n['r']) for n in NO.NB if n['c'] == 'bow'])
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON sketch: 2 nacelles vs 4 nacelles + aft ring', nacelle=NN.NAC, hoop=HOOP, options={})
    out['options']['two_nacelles'] = run([0, 180], False, P, w, fixed)
    out['options']['four_nacelles_ring'] = run([0, 90, 180, 270], True, P, w, fixed)
    for k, v in out['options'].items(): print(k, v['metrics'])
    json.dump(out, open(os.path.join(HERE, 'node_ring.json'), 'w'), indent=1)
