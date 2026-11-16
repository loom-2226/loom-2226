"""Creative options for an even node field (design search, NON-CANON). ALL bodies. ALL sponsors. 2026-2226.
Reuses node_optimize.py. Each option changes the ship's Loom-configuration shape and/or the allowed mount sites,
then searches for the most even 208-node layout. Geometric evenness only (not a PR #356 certification)."""
import os, json, math, numpy as np
import node_optimize as NO
HERE = os.path.dirname(os.path.abspath(__file__))
STRK = NO.STRK
def squash(P, segs):
    """Piecewise-linear remap of x for points aft of 39.3 m: segs = [(x0, x1, new_x0, new_x1), ...]."""
    Q = P.copy(); x = P[:, 0]
    for x0, x1, n0, n1 in segs:
        m = (x >= x0) & (x <= x1); Q[m, 0] = n0 + (x[m] - x0) * (n1 - n0) / (x1 - x0)
    return Q
def nozzle_sites(x0, x1, r0, r1, step=0.3):
    S = []
    for x in np.arange(x0, x1 - .1, step):
        r = r0 + (x - x0) / (x1 - x0) * (r1 - r0) + .12
        for a in np.arange(0, 360, 3.0):
            if any(math.radians(NO.ad(a, s)) * r < 0.45 for s in STRK): continue
            S.append(NO.cyl(x, a, r))
    return S
def mount_ring_sites():   # reactor mount ring: the structural collar where the cone meets the reactor (x 39.3-40.0, r 2.95)
    S = []
    for x in (39.4, 39.7, 39.95):
        for a in np.arange(0, 360, 3.0):
            if any(math.radians(NO.ad(a, s)) * 3.0 < 0.45 for s in STRK): continue
            S.append(NO.cyl(x, a, 3.0))
    return S
def door_sites():
    S = []
    for x in np.arange(18.4, 32.0, 0.3):
        for a in np.arange(57.0 + 1.5, 123.0, 3.0): S.append(NO.cyl(x, a, 4.5))
    return S
def run(name, P, w, extra, base_variant='cone', fixed=None):
    S, tag = NO.sites(base_variant)
    if extra:
        for t, pts in extra.items(): S = np.vstack([S, np.array(pts)]); tag = np.r_[tag, [t] * len(pts)]
    best = None
    for rs in range(4):
        L = NO.optimise(S, fixed, P, w, np.random.default_rng(100 + rs)); m = NO.evaluate(L, P, w)
        sc = m['mean_gap_m'] + 0.5 * m['load_cv']
        if best is None or sc < best[0]: best = (sc, L, m)
    _, L, m = best; tg = NO.cKDTree(S).query(L[16:])[1]
    m['count_by_zone'] = {str(z): int((tag[tg] == z).sum()) for z in set(tag)}; m['count_by_zone']['ring0_fixed'] = 16
    m['ship_x_max_m'] = round(float(P[:, 0].max()), 2)
    print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()})
    return dict(metrics={k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()},
                nodes=[[round(float(p[0]), 3), round(float((math.degrees(math.atan2(p[2], p[1])) + 360) % 360), 2), round(float(math.hypot(p[1], p[2])), 3)] for p in L])
if __name__ == '__main__':
    rng = np.random.default_rng(2226)
    T = NO.load_glb(os.path.join(NO.W, 'render/out/wayfarer_exterior_detail_88ce19fc_stowed_closed.glb')); P, w = NO.envelope(T, rng)
    fixed = np.array([NO.cyl(n['x'], n['a'], n['r']) for n in NO.NB if n['c'] == 'bow'])
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON creative options; geometric evenness only', options={})
    # 1 compact torch: reactor 7 -> 4 m, nozzle 7 -> 5 m (burn point 6 -> 4 m aft of the reactor face); aft nodes on the nozzle coil frame
    P1 = squash(P, [(39.3, 46.3, 39.3, 43.3), (46.3, 53.4, 43.3, 48.3)])
    out['options']['1_compact_torch_coil_ring'] = run('1 compact torch + nozzle coil frame', P1, w, {'nozzle_coils': nozzle_sites(43.3, 48.3, 2.125, 3.0), 'mount_ring': mount_ring_sites()}, fixed=fixed)
    # 2 telescoping nozzle: for a Loom jump the nozzle coil rings slide forward on rails and park as a collar round the
    #   reactor's waist (x 41.3-43.3); the hot-fin tails fold forward with them. Torch length unchanged when burning.
    P2 = squash(P, [(46.3, 53.4, 41.3, 43.3)])
    out['options']['2_telescoping_nozzle'] = run('2 telescoping nozzle (Loom config)', P2, w, {'coil_collar': nozzle_sites(41.3, 43.3, 2.5, 3.0, 0.25)}, fixed=fixed)
    # 3 shuttle as the missing hull piece, on top of option 1: no door leaves; the docked shuttle's back carries nodes that plug in
    out['options']['3_shuttle_completes_hull'] = run('3 shuttle carries the bay-sector nodes (+ option 1)', P1, w,
        {'nozzle_coils': nozzle_sites(43.3, 48.3, 2.125, 3.0), 'mount_ring': mount_ring_sites(), 'shuttle_back': door_sites()}, fixed=fixed)
    # 4 end-cap lens (no aft hardware at all): best evenness with nodes allowed only forward of the reactor
    out['options']['4_end_cap_lens'] = run('4 end-cap lens: no nodes aft of the cone (geometric score only)', P, w, {}, fixed=fixed)
    json.dump(out, open(os.path.join(HERE, 'node_options.json'), 'w'), indent=1)
