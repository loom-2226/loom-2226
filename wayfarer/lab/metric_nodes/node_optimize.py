"""Even node layouts that fit around everything: a design search (NON-CANON proposal).
ALL bodies. ALL sponsors. 2026-2226.
Places 208 node faces on ALLOWED mount sites only, so that every part of Wayfarer's outer
skin (Loom configuration: radiators stowed, shuttle docked) is served as evenly as possible.
Ring 0 (16 bow-shoulder faces) is fixed by kt_decisions bow_shoulder_surface_2026_11_13.
Geometric evenness only: it says nothing certified about the translation domain (PR #356)."""
import os, json, math, struct
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse.csgraph import connected_components
from scipy.sparse import coo_matrix
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.abspath(os.path.join(HERE, '..', '..'))
G = json.load(open(os.path.join(W, 'results/out/wayfarer_v05_geometry.json')))
HW = json.load(open(os.path.join(W, 'print/hardware_1to100/hardware_inventory.json')))
NB = json.load(open(os.path.join(HERE, 'nodes_before_after.json')))['before']
D_REACH, ELL = 2.089, 4.178          # same reach / link length as the lab study (1,900 m2 / 208, kappa 1.5)
STRK, LONG = [40, 140, 220, 320], [43.4, 136.6, 223.4, 316.6]
ad = lambda a, b: abs((a - b + 180) % 360 - 180)
cyl = lambda x, a, r: np.array([x, r * math.cos(math.radians(a)), r * math.sin(math.radians(a))])

# ---------- ship outer skin (Loom config), same construction as the lab study ----------
def load_glb(path):
    f = open(path, 'rb').read(); L = struct.unpack('<I', f[12:16])[0]; j = json.loads(f[20:20 + L]); b0 = 20 + L
    BL = struct.unpack('<I', f[b0:b0 + 4])[0]; buf = f[b0 + 8:b0 + 8 + BL]
    def acc(i):
        a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]; off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[a['componentType']]; n = {'SCALAR': 1, 'VEC3': 3}[a['type']]
        return np.frombuffer(buf, dt, count=a['count'] * n, offset=off).reshape(a['count'], n)
    def mat(n):
        if 'matrix' in n: return np.array(n['matrix']).reshape(4, 4).T
        T = np.eye(4); t = n.get('translation', [0, 0, 0]); x, y, z, w = n.get('rotation', [0, 0, 0, 1]); s = n.get('scale', [1, 1, 1])
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        T[:3, :3] = R * np.array(s); T[:3, 3] = t; return T
    tris = []
    def walk(i, M):
        n = j['nodes'][i]; M2 = M @ mat(n)
        if 'mesh' in n:
            for pr in j['meshes'][n['mesh']]['primitives']:
                V = acc(pr['attributes']['POSITION']).astype(float); I = acc(pr['indices']).reshape(-1) if 'indices' in pr else np.arange(len(V))
                tris.append((np.c_[V, np.ones(len(V))] @ M2.T)[:, :3][I.reshape(-1, 3)])
        for c in n.get('children', []): walk(c, M2)
    for r in j['scenes'][j.get('scene', 0)]['nodes']: walk(r, np.eye(4))
    T = np.concatenate(tris); return np.stack([T[..., 0], -T[..., 2], T[..., 1]], -1)
def envelope(T, rng):
    a, b, c = T[:, 0], T[:, 1], T[:, 2]; A = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    k = rng.choice(len(T), 600000, p=A / A.sum()); u, v = rng.random(600000), rng.random(600000); fl = u + v > 1; u[fl], v[fl] = 1 - u[fl], 1 - v[fl]
    P = a[k] + u[:, None] * (b[k] - a[k]) + v[:, None] * (c[k] - a[k]); r = np.hypot(P[:, 1], P[:, 2]); az = np.degrees(np.arctan2(P[:, 2], P[:, 1])) % 360
    key = np.floor(P[:, 0] / 0.25).astype(int) * 1000 + np.floor(az / 2).astype(int); o = np.lexsort((-r, key))
    sel = o[np.r_[True, key[o][1:] != key[o][:-1]]]; sel = sel[r[sel] >= 0.3]
    return P[sel], r[sel] * math.radians(2) * 0.25

# ---------- allowed mount sites ----------
others = [f for f in G['features'] if f['kind'] in ('window', 'hatch', 'hold_door', 'camera')]
def blocked_by_hardware(x, a, R):
    for h in HW:
        if h['name'] == 'bow_sensors': continue
        L = max(h['size_m'][0], .2); Cc = max(h['size_m'][1], h['size_m'][2], .2)
        if abs(x - h['x']) < L / 2 + .33 and math.radians(ad(a, h['az'])) * R < Cc / 2 + .33: return True
    for o in others:
        oa = (math.degrees(math.atan2(o['pos'][2], o['pos'][1])) + 360) % 360
        if abs(x - o['pos'][0]) < .6 and math.radians(ad(a, oa)) * R < .6: return True
    return False
def sites(variant):
    S, tag = [], []
    for x in np.arange(2.7, 34.15, 0.3):                         # hull skin r 4.5
        for a in np.arange(0, 360, 3.0):
            if 18.0 <= x <= 32.3 and 55.0 <= a <= 125.0: continue                  # bay-door leaves + edge margin
            if 14 <= x <= 32.3 and any(ad(a, s) <= 12.7 for s in STRK) and not any(ad(a, s) < 1.6 for s in STRK): continue   # under a stowed strake (root line allowed)
            if 14 <= x <= 34.3 and any(ad(a, l) < 3.0 for l in LONG): continue     # over a longeron
            if blocked_by_hardware(x, a, 4.5): continue
            S.append(cyl(x, a, 4.5)); tag.append('hull')
    if variant in ('cone', 'cone_fins'):
        for x in np.arange(34.45, 39.2, 0.3):                    # thrust-cone outer skin
            r = 4.4 + (x - 34.3) / 5.0 * (2.95 - 4.4)
            for a in np.arange(0, 360, 3.0):
                if any(math.radians(ad(a, s)) * r < 0.45 for s in STRK): continue  # hot-fin attachment
                if blocked_by_hardware(x, a, r): continue
                S.append(cyl(x, a, r + .05)); tag.append('cone')
    if variant == 'cone_fins':
        for s in STRK:                                           # both faces of each hot-fin root truss
            for x in np.arange(39.45, 53.2, 0.3):
                for r in np.arange(3.15, 4.7, 0.25):
                    for side in (-1, 1):
                        a = s + side * math.degrees(0.18 / r); S.append(cyl(x, a, r)); tag.append('finroot')
    return np.array(S), np.array(tag)

# ---------- search: weighted k-means with snapping to allowed sites ----------
def evaluate(nodes, P, w):
    dist, idx = cKDTree(nodes).query(P)
    load = np.bincount(idx, weights=w, minlength=len(nodes))
    pairs = np.array(sorted(cKDTree(nodes).query_pairs(ELL))); n = len(nodes)
    if len(pairs):
        ww = np.exp(-np.linalg.norm(nodes[pairs[:, 0]] - nodes[pairs[:, 1]], axis=1) / D_REACH)
        Wm = coo_matrix((np.r_[ww, ww], (np.r_[pairs[:, 0], pairs[:, 1]], np.r_[pairs[:, 1], pairs[:, 0]])), shape=(n, n)).toarray()
    else: Wm = np.zeros((n, n))
    nc, lab = connected_components(Wm > 0); gc = np.bincount(lab).max() / n
    return dict(reach_cover=float(w[dist <= D_REACH].sum() / w.sum()), p95_gap_m=float(np.percentile(np.repeat(dist, 1), 95)),
                max_gap_m=float(dist.max()), mean_gap_m=float((dist * w).sum() / w.sum()),
                load_cv=float(load.std() / load.mean()), web_connected=float(gc), web_pieces=int(nc))
def optimise(S, fixed, P, w, rng, iters=45):
    k = 208 - len(fixed); tree = cKDTree(S)
    # init: k-means++ on the skin points, snapped to sites
    C = [P[rng.choice(len(P), p=w / w.sum())]]
    d2 = np.full(len(P), np.inf)
    for _ in range(k - 1):
        d2 = np.minimum(d2, ((P - C[-1]) ** 2).sum(1)); pr = w * d2; C.append(P[rng.choice(len(P), p=pr / pr.sum())])
    cur = snap(np.array(C), tree, S)
    for it in range(iters):
        allc = np.vstack([fixed, cur]); _, idx = cKDTree(allc).query(P)
        newc = []
        for j in range(len(fixed), len(allc)):
            m = idx == j
            newc.append((P[m] * w[m, None]).sum(0) / w[m].sum() if m.any() else allc[j])
        nxt = snap(np.array(newc), tree, S)
        if np.allclose(nxt, cur): break
        cur = nxt
    return np.vstack([fixed, cur])
def snap(C, tree, S):
    used, out = set(), []
    for c in C:
        dd, ii = tree.query(c, k=12)
        for i in np.atleast_1d(ii):
            if int(i) not in used: used.add(int(i)); out.append(S[int(i)]); break
    return np.array(out)

if __name__ == '__main__':
    rng = np.random.default_rng(2226)
    T = load_glb(os.path.join(W, 'render/out/wayfarer_exterior_detail_88ce19fc_stowed_closed.glb')); P, w = envelope(T, rng)
    fixed = np.array([cyl(n['x'], n['a'], n['r']) for n in NB if n['c'] == 'bow'])
    base = np.array([cyl(n['x'], n['a'], n['r']) for n in NB])
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON design search; geometric evenness only, not a domain certification (PR #356)',
               skin=dict(points=int(len(P)), area_m2=round(float(w.sum()), 1)), baseline_A0=evaluate(base, P, w), layouts={})
    for var in ('hull_only', 'cone', 'cone_fins'):
        S, tag = sites(var); best = None
        for rs in range(4):
            L = optimise(S, fixed, P, w, np.random.default_rng(100 + rs)); m = evaluate(L, P, w)
            score = m['mean_gap_m'] + 0.5 * m['load_cv']
            if best is None or score < best[0]: best = (score, L, m)
        _, L, m = best; tg = cKDTree(S).query(L[16:])[1]
        m['sites_available'] = int(len(S)); m['count_by_zone'] = {z: int((tag[tg] == z).sum()) for z in set(tag)}; m['count_by_zone']['ring0_fixed'] = 16
        out['layouts'][var] = dict(metrics={k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()},
                                   nodes=[[round(float(p[0]), 3), round(float((math.degrees(math.atan2(p[2], p[1])) + 360) % 360), 2), round(float(math.hypot(p[1], p[2])), 3)] for p in L])
        print(var, out['layouts'][var]['metrics'])
    print('A0', out['baseline_A0'])
    json.dump(out, open(os.path.join(HERE, 'node_layouts_even.json'), 'w'), indent=1)
