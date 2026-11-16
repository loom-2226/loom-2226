"""Retractable node nacelles (kT idea, 16 Nov): sketch + even-layout search. NON-CANON. ALL bodies. ALL sponsors. 2026-2226.
Nacelles stow flush in hull recesses between the strakes and slide aft to flank the torch for Metric/Loom.
Torch burn and Metric/Loom are mutually exclusive (Canon II s14), so the nacelles are only out when the torch is cold."""
import os, json, math, numpy as np
import node_optimize as NO
HERE = os.path.dirname(os.path.abspath(__file__))
NAC = dict(r_axis=4.6, radius=0.6, x0=39.5, x1=53.5, stow_x0=14.5, stow_x1=32.0)
def nacelle_points(az, n=3000, rng=None):
    rng = rng or np.random.default_rng(0); t = rng.random(n); ph = rng.random(n) * 2 * math.pi
    x = NAC['x0'] + t * (NAC['x1'] - NAC['x0']); a = math.radians(az)
    cy, cz = NAC['r_axis'] * math.cos(a), NAC['r_axis'] * math.sin(a)
    P = np.c_[x, cy + NAC['radius'] * np.cos(ph), cz + NAC['radius'] * np.sin(ph)]
    w = np.full(n, 2 * math.pi * NAC['radius'] * (NAC['x1'] - NAC['x0']) / n); return P, w
def nacelle_sites(az, step=0.35):
    S = []; a = math.radians(az); cy, cz = NAC['r_axis'] * math.cos(a), NAC['r_axis'] * math.sin(a)
    for x in np.arange(NAC['x0'] + .2, NAC['x1'] - .1, step):
        for ph in np.arange(0, 360, 30): S.append(np.array([x, cy + (NAC['radius'] + .05) * math.cos(math.radians(ph)), cz + (NAC['radius'] + .05) * math.sin(math.radians(ph))]))
    return S
def run(azs, P0, w0, fixed):
    P, w = P0, w0
    for az in azs:
        p, ww = nacelle_points(az); P = np.vstack([P, p]); w = np.r_[w, ww]
    S, tag = NO.sites('cone')
    for az in azs:
        s = nacelle_sites(az); S = np.vstack([S, s]); tag = np.r_[tag, [f'nacelle_{az}'] * len(s)]
    best = None
    for rs in range(4):
        L = NO.optimise(S, fixed, P, w, np.random.default_rng(100 + rs)); m = NO.evaluate(L, P, w)
        sc = m['mean_gap_m'] + 0.5 * m['load_cv']
        if best is None or sc < best[0]: best = (sc, L, m)
    _, L, m = best; tg = NO.cKDTree(S).query(L[16:])[1]
    m['count_by_zone'] = {str(z): int((tag[tg] == z).sum()) for z in set(tag)}; m['count_by_zone']['ring0_fixed'] = 16
    return dict(metrics={k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}, nodes=[[float(v) for v in p] for p in L])
if __name__ == '__main__':
    rng = np.random.default_rng(2226)
    T = NO.load_glb(os.path.join(NO.W, 'render/out/wayfarer_exterior_detail_88ce19fc_stowed_closed.glb')); P, w = NO.envelope(T, rng)
    fixed = np.array([NO.cyl(n['x'], n['a'], n['r']) for n in NO.NB if n['c'] == 'bow'])
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON sketch (kT idea: retractable nacelles)', nacelle=NAC, options={})
    for name, azs in (('two_nacelles', [0, 180]), ('three_nacelles', [0, 180, 270]), ('four_nacelles_reference', [0, 90, 180, 270])):
        out['options'][name] = run(azs, P, w, fixed); print(name, out['options'][name]['metrics'])
    json.dump(out, open(os.path.join(HERE, 'node_nacelles.json'), 'w'), indent=1)
