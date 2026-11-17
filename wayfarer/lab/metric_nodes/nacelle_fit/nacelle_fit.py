"""Four nacelles + aft ring: clearance of the moving parts against the INSTALLED solids, before drawing them in.
NON-CANON design check. ALL bodies. ALL sponsors. 2026-2226.
Installed solids: the released stowed exterior GLB (geometry unchanged by PR #559: torch chain pinned at z -0.26 m).
Moving parts are sampled at stowed, mid-sweep and deployed states. Distances are surface-sample estimates (+-~0.05 m).
RCS plume: line-of-sight test against a 15 deg half-angle core cone (ASSUMPTION) on each aft axial thruster,
canted 10 deg outward (kT 2026-10-26). Writes nacelle_fit.json."""
import json, os, struct, numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, '..', '..', '..')
GLB = os.path.join(W, 'render', 'out', 'wayfarer_exterior_B_medical_88ce19fc_stowed_closed.glb')

def parts(path, step=0.05):
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
    out = {}; rng = np.random.default_rng(1)
    def walk(i, M):
        n = j['nodes'][i]; M2 = M @ mat(n)
        if 'mesh' in n:
            for pr in j['meshes'][n['mesh']]['primitives']:
                V = acc(pr['attributes']['POSITION']).astype(float); I = acc(pr['indices']).reshape(-1, 3) if 'indices' in pr else np.arange(len(V)).reshape(-1, 3)
                Wv = (np.c_[V, np.ones(len(V))] @ M2.T)[:, :3]; S = np.stack([Wv[:, 0], -Wv[:, 2], Wv[:, 1]], -1); T = S[I]
                if T[..., 0].max() < 33.5: continue
                A = 0.5 * np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1)
                k = np.maximum(1, (A / step ** 2).astype(int)); k = np.minimum(k, 4000)
                idx = np.repeat(np.arange(len(T)), k); u = rng.random((len(idx), 2)); m = u.sum(1) > 1; u[m] = 1 - u[m]
                P = T[idx, 0] + u[:, :1] * (T[idx, 1] - T[idx, 0]) + u[:, 1:] * (T[idx, 2] - T[idx, 0])
                out.setdefault(n.get('name', '?'), []).append(np.vstack([P, S]))
        for c in n.get('children', []): walk(c, M2)
    for r in j['scenes'][j.get('scene', 0)]['nodes']: walk(r, np.eye(4))
    return {k: np.vstack(v) for k, v in out.items()}

def cyl(az, r_axis, x0, x1, rad, n=60, m=40):
    a = np.radians(az); e_r = np.array([0, np.cos(a), np.sin(a)]); e_t = np.array([0, -np.sin(a), np.cos(a)])
    X = np.linspace(x0, x1, int((x1 - x0) / 0.1) + 1); th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    c = r_axis * e_r; P = [np.array([x, 0, 0]) + c + rad * (np.cos(t) * e_r + np.sin(t) * e_t) for x in X for t in th]
    for x in (x0, x1):
        for rr in np.linspace(0, rad, 5): P += [np.array([x, 0, 0]) + c + rr * (np.cos(t) * e_r + np.sin(t) * e_t) for t in th]
    return np.array(P)

def hoop(x, R, r, n=720, m=16):
    ph = np.linspace(0, 2 * np.pi, n, endpoint=False); ps = np.linspace(0, 2 * np.pi, m, endpoint=False)
    return np.array([[x + r * np.sin(s), (R + r * np.cos(s)) * np.cos(p), (R + r * np.cos(s)) * np.sin(p)] for p in ph for s in ps])

def arm_folded(az, r_axis, xh, R, r, side, bow):
    """arm folded alongside its nacelle: chord along -x from the hinge at xh, the arc's sagitta bowed `bow` (radially out)."""
    a = np.radians(az); e_r = np.array([0, np.cos(a), np.sin(a)]); e_t = np.array([0, -np.sin(a), np.cos(a)])
    th = np.linspace(0, np.pi / 4, 30); s = R * np.sin(th); dev = R * (1 - np.cos(th))       # along x / off-axis
    base = np.array([xh, 0, 0]) + r_axis * e_r + side * 0.0 * e_t
    C = np.array([base - si * np.array([1, 0, 0]) + bow * di * e_r for si, di in zip(s, dev)])
    ps = np.linspace(0, 2 * np.pi, 10, endpoint=False)
    return np.array([c + r * (np.cos(p) * e_r + np.sin(p) * e_t) for c in C for p in ps])

def plume_hits(P, clusters, half=15.0, cant=10.0, L=40.0):
    """points inside any aft axial plume core cone (apex at thruster exit, axis aft, canted out)."""
    hit = np.zeros(len(P), bool)
    for az, x0, r0 in clusters:
        a = np.radians(az); e_r = np.array([0, np.cos(a), np.sin(a)])
        apex = np.array([x0, 0, 0]) + r0 * e_r; ax = np.array([1, 0, 0]) * np.cos(np.radians(cant)) + e_r * np.sin(np.radians(cant))
        v = P - apex; t = v @ ax; perp = np.linalg.norm(v - np.outer(t, ax), axis=1)
        hit |= (t > 0) & (t < L) & (perp <= t * np.tan(np.radians(half)))
    return hit

def option(name, azs, r_tuck, r_dep, x0, x1, hoop_x, hoop_R, hoop_r=0.35, rad=0.6, arm_bow=+1):
    S = {}
    for st, rr in (('tucked', r_tuck), ('mid', (r_tuck + r_dep) / 2), ('deployed', r_dep)):
        P = np.vstack([cyl(a, rr, x0, x1, rad) for a in azs])
        if st != 'deployed': P = np.vstack([P] + [arm_folded(a, rr + rad + hoop_r, hoop_x, hoop_R, hoop_r, 1, arm_bow) for a in azs])
        S[st] = P
    S['ring_locked'] = hoop(hoop_x, hoop_R, hoop_r)
    return dict(name=name, azs=azs, r_tuck=r_tuck, r_dep=r_dep, x=[x0, x1], hoop=dict(x=hoop_x, R=hoop_R, r=hoop_r), states=S)

if __name__ == '__main__':
    PARTS = parts(GLB); TREES = {k: cKDTree(v) for k, v in PARTS.items()}
    RCS = []
    for k, v in PARTS.items():
        if k.startswith('dry:rcs_A'):
            c = v.mean(0); RCS.append((np.degrees(np.arctan2(c[2], c[1])) % 360, v[:, 0].max(), np.hypot(v[:, 1], v[:, 2]).mean()))
    OPTS = [option('as_sketched', [0, 90, 180, 270], 3.7, 4.6, 39.5, 53.5, 52.6, 4.4),
            option('fixed_static', [0, 90, 180, 270], 3.95, 4.6, 39.5, 54.3, 53.9, 4.6),
            option('clocked_24', [24, 114, 204, 294], 3.95, 4.6, 39.5, 54.3, 53.9, 4.6)]
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON clearance check before drawing nacelles into source',
               glb=os.path.basename(GLB), rcs_aft=[dict(az=round(a, 1), x_exit=round(x, 2), r=round(r, 2)) for a, x, r in RCS],
               plume_assumption='15 deg half-angle core, axis aft canted 10 deg out (kT 2026-10-26); plume not modelled in source', options={})
    for o in OPTS:
        res = {}
        for st, P in o['states'].items():
            near = sorted(((float(TREES[k].query(P)[0].min()), k) for k in TREES), key=lambda t: t[0])[:3]
            res[st] = dict(min_clear_m=round(near[0][0], 3), nearest=[(k, round(d, 2)) for d, k in near],
                           in_rcs_plume_frac=round(float(plume_hits(P, RCS).mean()), 3))
        out['options'][o['name']] = dict(azimuths=o['azs'], r_tucked=o['r_tuck'], r_deployed=o['r_dep'], x=o['x'], hoop=o['hoop'], states=res)
        print(o['name']); [print('  ', s, r) for s, r in res.items()]
    json.dump(out, open(os.path.join(HERE, 'nacelle_fit.json'), 'w'), indent=1)
