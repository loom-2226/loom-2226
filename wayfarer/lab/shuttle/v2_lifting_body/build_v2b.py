"""Shuttle v2-B lifting body: twin 2.0 m Ti spheres inside a non-pressure
aeroshell. NON-CANON lab model. ALL bodies. ALL sponsors. 2026-2226.
Frame: x aft from nose (m), y starboard, z up. GLB written glTF y-up as
(x, z, -y). Outputs: shuttle_v2b.glb, shuttle_v2b_manifest.json."""
import numpy as np, json, struct, os
HERE = os.path.dirname(os.path.abspath(__file__))
L, W2, BORE_R = 12.8, 2.125, 2.15
SPH_R, SPH_X, SPH_Y, SPH_Z = 0.95, 7.8, 1.0, 0.20
AXIS_Z = 0.0                         # bay axis = chine line (widest point)

def w(x):  # planform half-width
    x = np.asarray(x, float)
    a = W2 * np.clip(x / 6.8, 0, 1) ** 0.6
    return np.where(x > 11.4, a * (1 - 0.12 * ((x - 11.4) / 1.4) ** 2), a)
def ht(x):  # upper surface height above zc
    x = np.asarray(x, float)
    up = 1.45 * np.clip(x / 7.8, 0, 1) ** 0.55
    dn = 1.45 - 0.60 * np.clip((x - 7.8) / 5.0, 0, 1) ** 1.4
    return np.where(x < 7.8, up, dn)
def hb(x):  # belly depth below zc
    x = np.asarray(x, float)
    return np.where(x < 5.0, 0.9 * np.clip(x / 5.0, 0, 1) ** 0.45, 0.9 - 0.08 * np.clip((x - 9.2) / 3.6, 0, 1))
def zc(x):  # nose droop (flat belly line)
    x = np.asarray(x, float)
    return np.where(x < 4.0, -0.25 * (1 - x / 4.0) ** 2, 0.0)

NU, NX = 128, 160
def ring(x):
    t = np.linspace(0, 2 * np.pi, NU, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    n_up, n_lo = 2.4, 3.6
    n = np.where(s >= 0, n_up, n_lo)
    y = w(x) * np.sign(c) * np.abs(c) ** (2 / n)
    h = np.where(s >= 0, ht(x), hb(x))
    z = zc(x) + h * np.sign(s) * np.abs(s) ** (2 / n)
    return y, z, s

def loft():
    xs = L * (1 - np.cos(np.linspace(0, np.pi / 2, NX))) ** 1.0   # dense at nose
    xs[0] = 0.0
    V, lower = [], []
    for x in xs[1:]:
        y, z, s = ring(x); V += list(zip(np.full(NU, x), y, z)); lower += list(s < -0.15)
    V.append((0.0, 0.0, float(zc(0.0)))); nose = len(V) - 1
    V.append((L, 0.0, float(zc(L)) + 0.25)); tail = len(V) - 1
    F = []
    R = NX - 1
    for i in range(R - 1):
        for j in range(NU):
            a, b = i * NU + j, i * NU + (j + 1) % NU
            c, d = a + NU, b + NU
            F += [(a, b, c), (b, d, c)]
    for j in range(NU):
        F.append((nose, (j + 1) % NU, j))
        a, b = (R - 1) * NU + j, (R - 1) * NU + (j + 1) % NU
        F.append((a, b, tail))
    return np.array(V), np.array(F), np.array(lower + [True, False])

def uvsphere(c, r, nu=48, nv=24):
    V = [(c[0], c[1], c[2] + r), (c[0], c[1], c[2] - r)]
    for i in range(1, nv):
        th = np.pi * i / nv
        for j in range(nu):
            ph = 2 * np.pi * j / nu
            V.append((c[0] + r * np.sin(th) * np.cos(ph), c[1] + r * np.sin(th) * np.sin(ph), c[2] + r * np.cos(th)))
    F = []
    for j in range(nu):
        F.append((0, 2 + j, 2 + (j + 1) % nu))
        base = 2 + (nv - 2) * nu
        F.append((1, base + (j + 1) % nu, base + j))
    for i in range(nv - 2):
        for j in range(nu):
            a, b = 2 + i * nu + j, 2 + i * nu + (j + 1) % nu
            F += [(a, a + nu, b), (b, a + nu, b + nu)]
    return np.array(V), np.array(F)

def tube(p0, p1, r, n=40, r1=None):
    r1 = r if r1 is None else r1
    p0, p1 = np.array(p0, float), np.array(p1, float); ax = p1 - p0; ax /= np.linalg.norm(ax)
    u = np.cross(ax, [0, 0, 1] if abs(ax[2]) < 0.9 else [1, 0, 0]); u /= np.linalg.norm(u); v = np.cross(ax, u)
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    A = [p0 + r * (np.cos(a) * u + np.sin(a) * v) for a in t]; B = [p1 + r1 * (np.cos(a) * u + np.sin(a) * v) for a in t]
    V = np.array(A + B + [p0, p1]); F = []
    for j in range(n):
        k = (j + 1) % n
        F += [(j, k, n + j), (k, n + k, n + j), (2 * n, k, j), (2 * n + 1, n + j, n + k)]
    return V, np.array(F)

def hexa(P):  # 8 corners: bottom quad 0-3, top quad 4-7 (same order)
    F = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return np.array(P, float), np.array(F)

def fin(side, deployed=True):
    # root on the upper chine near the trailing edge, canted outboard 15 deg
    y0 = side * (float(w(11.6)) - 0.18); z0 = 0.12
    cant = np.radians(15 if deployed else 90 - 4)
    up = np.array([0, side * np.sin(cant), np.cos(cant)]) if deployed else np.array([0, -side * np.cos(np.radians(4)), np.sin(np.radians(4))])
    nrm = np.cross([1, 0, 0], up); t = 0.045
    root = [np.array([10.4, y0, z0]), np.array([12.75, y0, z0])]
    tip = [root[0] + 1.25 * up + [1.3, 0, 0], root[1] + 1.25 * up]
    q = [root[0], root[1], tip[1], tip[0]]
    return hexa([p - t * nrm for p in q] + [p + t * nrm for p in q])

def kit_pod():
    V, F = uvsphere((0, 0, 0), 1.0, 40, 20)
    V = V * [1.45, 0.62, 0.42] + [10.9, 0, float(zc(10.9) + ht(10.9)) - 0.12]
    return V, F

def parts():
    P = {}
    V, F, lower = loft()
    fl = lower[F].sum(1) >= 2
    cen = V[F].mean(1)
    glaze = (cen[:, 0] > 5.6) & (cen[:, 0] < 6.75) & (np.abs(np.abs(cen[:, 1]) - SPH_Y) < 0.42) & (cen[:, 2] > 0.75)
    P['hull'] = (V, F[~fl & ~glaze]); P['belly_tps'] = (V, F[fl]); P['glazing'] = (V, F[glaze])
    s1 = uvsphere((SPH_X, SPH_Y, SPH_Z), SPH_R); s2 = uvsphere((SPH_X, -SPH_Y, SPH_Z), SPH_R)
    P['sphere_stbd'] = s1; P['sphere_port'] = s2
    P['tunnel'] = tube((SPH_X, -0.35, SPH_Z), (SPH_X, 0.35, SPH_Z), 0.38)
    top = float(zc(SPH_X) + ht(SPH_X))
    P['hatch_trunk'] = tube((SPH_X, 0, SPH_Z), (SPH_X, 0, top + 0.06), 0.42)
    P['kit_pod'] = kit_pod()
    P['torch_nozzle'] = tube((12.35, 0, 0.25), (12.80, 0, 0.25), 0.36, 48, 0.58)
    for sd, nm in ((1, 'fin_stbd'), (-1, 'fin_port')): P[nm] = fin(sd)
    bf = [(12.1, -1.35, -0.80), (12.1, 1.35, -0.80), (12.78, 1.35, -0.95), (12.78, -1.35, -0.95)]
    P['body_flap'] = hexa(bf + [(p[0], p[1], p[2] + 0.07) for p in bf])
    for k, (V, F) in list(P.items()):
        if k in ('hull', 'belly_tps', 'glazing'): continue
        a, b_, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
        if np.einsum('ij,ij->i', a - V.mean(0), np.cross(b_ - V.mean(0), c - V.mean(0))).sum() < 0: P[k] = (V, F[:, ::-1])
    return P

MAT = {'hull': ([0.86, 0.87, 0.85, 1], 0.6, 0.0), 'belly_tps': ([0.10, 0.10, 0.11, 1], 0.9, 0.0),
       'glazing': ([0.15, 0.30, 0.45, 1], 0.1, 0.3), 'sphere_stbd': ([0.70, 0.40, 0.30, 1], 0.4, 0.8),
       'sphere_port': ([0.70, 0.40, 0.30, 1], 0.4, 0.8), 'tunnel': ([0.70, 0.40, 0.30, 1], 0.4, 0.8),
       'hatch_trunk': ([0.55, 0.57, 0.60, 1], 0.5, 0.6), 'kit_pod': ([0.78, 0.79, 0.77, 1], 0.6, 0.0),
       'torch_nozzle': ([0.25, 0.26, 0.28, 1], 0.4, 0.9), 'fin_stbd': ([0.86, 0.87, 0.85, 1], 0.6, 0.0),
       'fin_port': ([0.86, 0.87, 0.85, 1], 0.6, 0.0), 'body_flap': ([0.10, 0.10, 0.11, 1], 0.9, 0.0)}

def smooth_normals(V, F):
    N = np.zeros_like(V); fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    for k in range(3): np.add.at(N, F[:, k], fn)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)

def write_glb(P, path):
    bin_, views, accs, meshes, nodes, mats = bytearray(), [], [], [], [], []
    def add(arr, target, comp, typ):
        nonlocal bin_
        while len(bin_) % 4: bin_ += b'\0'
        off = len(bin_); b = arr.tobytes(); bin_ += b
        views.append(dict(buffer=0, byteOffset=off, byteLength=len(b), target=target))
        a = dict(bufferView=len(views) - 1, componentType=comp, count=int(arr.shape[0] if typ != 'SCALAR' else arr.size), type=typ)
        if typ == 'VEC3' and comp == 5126: a['min'] = arr.min(0).tolist(); a['max'] = arr.max(0).tolist()
        accs.append(a); return len(accs) - 1
    for name, (V, F) in P.items():
        used = np.unique(F); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
        Vu, Fu = V[used], remap[F]
        flat = name in ('fin_stbd', 'fin_port', 'body_flap')
        if flat: Vu = Vu[Fu].reshape(-1, 3); Fu = np.arange(len(Vu)).reshape(-1, 3)
        Nn = smooth_normals(Vu, Fu)
        G = np.c_[Vu[:, 0], Vu[:, 2], -Vu[:, 1]].astype('<f4'); Ng = np.c_[Nn[:, 0], Nn[:, 2], -Nn[:, 1]].astype('<f4')
        pa = add(G, 34962, 5126, 'VEC3'); na = add(Ng, 34962, 5126, 'VEC3'); ia = add(Fu.astype('<u4').ravel(), 34963, 5125, 'SCALAR')
        col, rough, metal = MAT[name]
        m = dict(name=name, pbrMetallicRoughness=dict(baseColorFactor=col, roughnessFactor=rough, metallicFactor=metal), doubleSided=False)
        if name == 'glazing': m['emissiveFactor'] = [0.05, 0.12, 0.2]
        mats.append(m)
        meshes.append(dict(name=name, primitives=[dict(attributes=dict(POSITION=pa, NORMAL=na), indices=ia, material=len(mats) - 1)]))
        nodes.append(dict(name=name, mesh=len(meshes) - 1))
    gl = dict(asset=dict(version='2.0', generator='LOOM build_v2b.py'), scene=0, scenes=[dict(nodes=list(range(len(nodes))))],
              nodes=nodes, meshes=meshes, materials=mats, accessors=accs, bufferViews=views, buffers=[dict(byteLength=len(bin_))])
    js = json.dumps(gl, separators=(',', ':')).encode()
    while len(js) % 4: js += b' '
    while len(bin_) % 4: bin_ += b'\0'
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(bin_), 0x004E4942) + bytes(bin_)
    open(path, 'wb').write(out); return len(out)

def stats(V, F):
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    vol = np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1).sum()
    e = {}
    for f in F:
        for i in range(3): e[(f[i], f[(i + 1) % 3])] = e.get((f[i], f[(i + 1) % 3]), 0) + 1
    unmatched = sum(1 for (u, v) in e if (v, u) not in e)
    return vol, area, unmatched

if __name__ == '__main__':
    P = parts()
    V, F, _ = loft()
    vol, area, um = stats(V, F)
    # bay fit: every hull/pod/flap vertex within the bore around (y=0, z=AXIS_Z); fins checked stowed
    chk = [P[k][0][np.unique(P[k][1])] for k in ('hull', 'belly_tps', 'glazing', 'kit_pod', 'body_flap', 'torch_nozzle')]
    chk += [fin(1, False)[0], fin(-1, False)[0]]
    allv = np.vstack(chk); rmax = float(np.max(np.hypot(allv[:, 1], allv[:, 2] - AXIS_Z)))
    fins_dep = np.vstack([P['fin_stbd'][0], P['fin_port'][0]])
    # sphere clearance to shell: min distance from shell verts to each sphere surface (outside)
    hv = V
    xs_ = np.linspace(5, 11, 600); clr = 9.0
    for x_ in xs_:
        yy, zz, _ = ring(x_)
        for sg in (1, -1):
            clr = min(clr, float(np.min(np.sqrt((x_ - SPH_X) ** 2 + (yy - sg * SPH_Y) ** 2 + (zz - SPH_Z) ** 2)) - SPH_R))
    sph_vol = 2 * 4 / 3 * np.pi * SPH_R ** 3
    # v1 reference area/volume from the 1:100 print STL (1 mm print = 0.1 m)
    stl = os.path.join(HERE, '..', '..', '..', 'print', 'shuttle_1to100', 'parts', 'shuttle_v1_1to100.stl')
    d = open(stl, 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
    T = np.frombuffer(d[84:], dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')], count=n)['v'].astype(float) * 0.1
    v1_area = float(0.5 * np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1).sum())
    v1_vol = float(abs(np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6))
    plan = float(np.trapezoid(2 * w(np.linspace(0, L, 2000)), np.linspace(0, L, 2000)))
    size = write_glb(P, os.path.join(HERE, 'shuttle_v2b.glb'))
    man = dict(status='NON-CANON lab model (kT: "Go ahead and try to build", 2026-11-14)', concept='v2-B twin spheres in lifting body',
               length_m=L, span_body_m=round(2 * W2, 3), height_m=round(float(np.max(V[:, 2]) - np.min(V[:, 2])), 3),
               fins_deployed_span_m=round(float(2 * np.max(np.abs(fins_dep[:, 1]))), 2),
               bay_fit=dict(bore_radius_m=BORE_R, axis_z_m=AXIS_Z, max_radius_stowed_m=round(rmax, 3), PASS=bool(rmax <= BORE_R)),
               hull=dict(watertight_unmatched_edges=um, enclosed_volume_m3=round(float(vol), 2), wetted_area_m2=round(float(area), 1), planform_area_m2=round(plan, 1)),
               v1_ref=dict(wetted_area_m2=round(v1_area, 1), enclosed_volume_m3=round(v1_vol, 1), source='print/shuttle_1to100/parts/shuttle_v1_1to100.stl x0.1'),
               area_ratio_v2_over_v1=round(float(area) / v1_area, 3), volume_ratio_v2_over_v1=round(float(vol) / v1_vol, 3),
               spheres=dict(od_m=2 * SPH_R, centres=[[SPH_X, SPH_Y, SPH_Z], [SPH_X, -SPH_Y, SPH_Z]], total_volume_m3=round(sph_vol, 2), min_clearance_to_skin_m=round(clr, 3)),
               glb_bytes=size, parts=list(P))
    json.dump(man, open(os.path.join(HERE, 'shuttle_v2b_manifest.json'), 'w'), indent=1)
    print(json.dumps(man, indent=1))
