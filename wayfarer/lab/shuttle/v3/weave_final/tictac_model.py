"""Tic Tac: one 3D model for kT's visual approval. NON-CANON lab asset (not a canon GLB; canon_glb.json untouched).
ALL bodies. ALL sponsors. 2026-2226.

Design language (Sol / kT 2026-11-22): aggressively restrained. Continuous smooth warm-white hull; flush nose docking hatch
and flush side door are the only marks; no wings, engines, antenna farms, decorative lights or panel lines.
Outputs:
  tictac_v1_model.glb         hull + two seam meshes (nose hatch ring, side door outline), glTF Y-up
  weave_tictac_v1_render.png  ray-traced 3/4 view hovering over the sea (analytic capsule, exact)
  weave_tictac_v1_views.png   orthographic sheet: side, front (in the Wayfarer bay envelope), top, with a 1.8 m figure"""
import os, sys, json, math, struct
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, Polygon
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import tictac_v1 as T
L, R = T.L, T.R
O = json.load(open(os.path.join(H, 'tictac_v1.json')))
BAY = O['layout']['x']['bay']
HULL_RGB = np.array([0.93, 0.915, 0.875])          # warm white
SEAM_RGB = np.array([0.62, 0.61, 0.58])
HATCH_R = 0.46                                      # flush nose hatch ring radius (0.8 m clear passage + frame)
DOOR = dict(x0=BAY[0] + 0.15, x1=BAY[0] + 0.15 + 3.2, phi0=math.radians(-80), phi1=math.radians(-5), corner=0.18)   # lower +y flank (phi from +y toward -z)

# ======================================================== mesh + GLB
def capsule_mesh(n_th=96, n_cap=24, n_cyl=60):
    xs, rs = [], []
    for t in np.linspace(0, math.pi / 2, n_cap): xs.append(R - R * math.cos(t)); rs.append(R * math.sin(t))
    for x in np.linspace(R, L - R, n_cyl)[1:-1]: xs.append(x); rs.append(R)
    for t in np.linspace(0, math.pi / 2, n_cap)[::-1]: xs.append(L - R + R * math.cos(t)); rs.append(R * math.sin(t))
    th = np.linspace(0, 2 * math.pi, n_th, endpoint=False)
    V = []; Nn = []
    for x, r in zip(xs, rs):
        for a in th:
            V.append((x, r * math.cos(a), r * math.sin(a)))
            c = (R, 0, 0) if x < R else ((L - R, 0, 0) if x > L - R else (x, 0, 0))
            n = np.array([x - c[0], r * math.cos(a), r * math.sin(a)]); Nn.append(n / (np.linalg.norm(n) + 1e-12))
    F = []
    for k in range(len(xs) - 1):
        for i in range(n_th):
            j = (i + 1) % n_th; a0, a1, b0, b1 = k * n_th + i, k * n_th + j, (k + 1) * n_th + i, (k + 1) * n_th + j
            F += [(a0, b0, a1), (a1, b0, b1)]
    return np.array(V), np.array(Nn), np.array(F)
def strip_mesh(pts, nrm, w=0.025, lift=0.003):
    """thin ribbon along a closed polyline on the surface (seam), lifted slightly to avoid z-fighting"""
    V, Nn, F = [], [], []
    n = len(pts)
    for i in range(n):
        p, q, nv = pts[i], pts[(i + 1) % n], nrm[i]
        t = q - p; t /= np.linalg.norm(t) + 1e-12; s = np.cross(nv, t); s /= np.linalg.norm(s) + 1e-12
        base = p + nv * lift; V += [base - s * w / 2, base + s * w / 2]; Nn += [nv, nv]
    for i in range(n):
        j = (i + 1) % n; F += [(2 * i, 2 * j, 2 * i + 1), (2 * i + 1, 2 * j, 2 * j + 1)]
    return np.array(V), np.array(Nn), np.array(F)
def hatch_ring(n=180):
    pts, nrm = [], []
    for a in np.linspace(0, 2 * math.pi, n, endpoint=False):
        y, z = HATCH_R * math.cos(a), HATCH_R * math.sin(a); x = R - math.sqrt(R * R - y * y - z * z)
        p = np.array([x, y, z]); pts.append(p); nv = p - np.array([R, 0, 0]); nrm.append(nv / np.linalg.norm(nv))
    return np.array(pts), np.array(nrm)
def door_outline(n=260):
    """rounded rectangle in (x, s = R*phi) on the cylinder; phi measured from +y toward -z"""
    x0, x1, s0, s1, c = DOOR['x0'], DOOR['x1'], R * DOOR['phi0'], R * DOOR['phi1'], DOOR['corner']
    pts2 = []
    for cx, cs, a0 in ((x1 - c, s1 - c, 0), (x0 + c, s1 - c, 90), (x0 + c, s0 + c, 180), (x1 - c, s0 + c, 270)):
        for a in np.radians(np.linspace(a0, a0 + 90, n // 4, endpoint=False)): pts2.append((cx + c * math.cos(a), cs + c * math.sin(a)))
    pts, nrm = [], []
    for x, s_ in pts2:
        ph = s_ / R; y, z = R * math.cos(ph), R * math.sin(ph); pts.append((x, y, z)); nrm.append((0, math.cos(ph), math.sin(ph)))
    return np.array(pts), np.array(nrm)
def write_glb(parts, path):
    bin_, views, accs, meshes, nodes, mats = bytearray(), [], [], [], [], []
    def add(arr, target, comp, typ):
        nonlocal bin_
        while len(bin_) % 4: bin_ += b'\0'
        off = len(bin_); b = arr.tobytes(); bin_ += b
        views.append(dict(buffer=0, byteOffset=off, byteLength=len(b), target=target))
        a = dict(bufferView=len(views) - 1, componentType=comp, count=int(arr.shape[0] if typ != 'SCALAR' else arr.size), type=typ)
        if typ == 'VEC3': a['min'] = arr.min(0).tolist(); a['max'] = arr.max(0).tolist()
        accs.append(a); return len(accs) - 1
    for name, (V, Nn, F, col, rough) in parts.items():
        G = np.c_[V[:, 0] - L / 2, V[:, 2], -V[:, 1]].astype('<f4'); Ng = np.c_[Nn[:, 0], Nn[:, 2], -Nn[:, 1]].astype('<f4')   # glTF Y-up, centred
        pa = add(G, 34962, 5126, 'VEC3'); na = add(Ng, 34962, 5126, 'VEC3'); ia = add(F.astype('<u4').ravel(), 34963, 5125, 'SCALAR')
        mats.append(dict(name=name, pbrMetallicRoughness=dict(baseColorFactor=list(col) + [1.0], roughnessFactor=rough, metallicFactor=0.0)))
        meshes.append(dict(name=name, primitives=[dict(attributes=dict(POSITION=pa, NORMAL=na), indices=ia, material=len(mats) - 1)]))
        nodes.append(dict(name=name, mesh=len(meshes) - 1))
    gl = dict(asset=dict(version='2.0', generator='LOOM tictac_model.py (NON-CANON lab asset)'), scene=0, scenes=[dict(nodes=list(range(len(nodes))))],
              nodes=nodes, meshes=meshes, materials=mats, accessors=accs, bufferViews=views, buffers=[dict(byteLength=len(bin_))])
    js = json.dumps(gl, separators=(',', ':')).encode()
    while len(js) % 4: js += b' '
    while len(bin_) % 4: bin_ += b'\0'
    open(path, 'wb').write(struct.pack('<III', 0x46546C67, 2, 28 + len(js) + len(bin_)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(bin_), 0x004E4942) + bytes(bin_))

# ======================================================== ray-traced render
def hit_capsule(ro, rd):
    """ray (N,3) vs capsule A=(R,0,0) B=(L-R,0,0) radius R in shuttle coords; returns t (inf = miss) and normals"""
    A = np.array([R, 0, 0.]); B = np.array([L - R, 0, 0.]); ba = B - A; oa = ro - A
    baba = ba @ ba; bard = rd @ ba; baoa = oa @ ba; rdoa = np.sum(rd * oa, 1); oaoa = np.sum(oa * oa, 1)
    a = baba - bard * bard; b = baba * rdoa - baoa * bard; c = baba * oaoa - baoa * baoa - R * R * baba
    hdisc = b * b - a * c; t = np.full(len(ro), np.inf)
    ok = hdisc >= 0; tt = np.where(ok, (-b - np.sqrt(np.maximum(hdisc, 0))) / np.where(a == 0, 1e-12, a), np.inf)
    y = baoa + tt * bard; body = ok & (y > 0) & (y < baba) & (tt > 0); t[body] = tt[body]
    for cap in (A, B):
        oc = ro - cap; bb = np.sum(rd * oc, 1); cc = np.sum(oc * oc, 1) - R * R; hh = bb * bb - cc
        tc = np.where(hh >= 0, -bb - np.sqrt(np.maximum(hh, 0)), np.inf); p = ro + rd * tc[:, None]
        p = np.nan_to_num(p, posinf=0.0, neginf=0.0); side = ((p - A) @ ba) <= 0 if cap is A else ((p - A) @ ba) >= baba
        m = (hh >= 0) & (tc > 0) & side & (tc < t); t[m] = tc[m]
    P = ro + rd * np.where(np.isfinite(t), t, 0)[:, None]
    xc = np.clip(P[:, 0], R, L - R); C = np.c_[xc, np.zeros(len(P)), np.zeros(len(P))]; N = P - C; N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    return t, P, N
def seam_mask(P):
    y, z = P[:, 1], P[:, 2]; m = np.zeros(len(P), bool)
    nose = P[:, 0] < R; rp = np.hypot(y, z); m |= nose & (np.abs(rp - HATCH_R) < 0.014)
    phi = np.arctan2(z, y); s = R * phi; x = P[:, 0]
    x0, x1, s0, s1, c = DOOR['x0'], DOOR['x1'], R * DOOR['phi0'], R * DOOR['phi1'], DOOR['corner']
    qx = np.abs(x - 0.5 * (x0 + x1)) - (0.5 * (x1 - x0) - c); qs = np.abs(s - 0.5 * (s0 + s1)) - (0.5 * (s1 - s0) - c)
    d = np.hypot(np.maximum(qx, 0), np.maximum(qs, 0)) + np.minimum(np.maximum(qx, qs), 0) - c
    m |= (x > R) & (x < L - R) & (np.abs(d) < 0.012) & (y > 0)
    return m
def render(path, W=1600, Hh=900, ss=2):
    # world: shuttle x -> X, shuttle z (up) -> Y, shuttle y -> -Z ; hover: axis 12 m above the sea
    HOV = 24.0                                                   # field centre above ~19 m: no sea bowl (operating card)
    def to_sh(Pw): return np.c_[Pw[:, 0] + L / 2, -Pw[:, 2], Pw[:, 1] - HOV]
    def dir_sh(Dw): return np.c_[Dw[:, 0], -Dw[:, 2], Dw[:, 1]]
    def dir_w(Ds): return np.c_[Ds[:, 0], Ds[:, 2], -Ds[:, 1]]
    cam = np.array([-13.0, 27.0, -17.0]); look = np.array([0.3, 21.5, 0.0]); up = np.array([0, 1.0, 0])
    fw = look - cam; fw /= np.linalg.norm(fw); rt = np.cross(fw, up); rt /= np.linalg.norm(rt); u2 = np.cross(rt, fw)
    fov = math.radians(38); aspect = W / Hh
    sun = np.array([-0.55, 0.62, -0.45]); sun /= np.linalg.norm(sun); sun_col = np.array([1.0, 0.95, 0.86]) * 1.05
    def sky(d):
        h = np.clip(d[:, 1], -0.2, 1); zen = np.array([0.30, 0.45, 0.68]); hor = np.array([0.80, 0.84, 0.88])
        col = hor[None] + (zen - hor)[None] * (np.clip(h, 0, 1) ** 0.6)[:, None]
        sd = np.clip(d @ sun, 0, 1); col += (sd ** 400)[:, None] * 6 * sun_col + (sd ** 12)[:, None] * 0.12 * sun_col
        return col
    def shade_hull(Pw_s, N_s, Vd_w):
        Nw = dir_w(N_s); Vd = -Vd_w
        amb = np.array([0.42, 0.44, 0.47]) * (0.55 + 0.45 * Nw[:, 1:2]) + np.array([0.10, 0.12, 0.15]) * (0.5 - 0.5 * Nw[:, 1:2])
        dif = np.clip(Nw @ sun, 0, 1)[:, None] * sun_col
        Hv = sun[None] + Vd; Hv /= np.linalg.norm(Hv, axis=1, keepdims=True)
        spec = (np.clip(np.sum(Nw * Hv, 1), 0, 1) ** 90)[:, None] * 0.35 * sun_col
        fr = 0.04 + 0.96 * (1 - np.clip(np.sum(Nw * Vd, 1), 0, 1)) ** 5
        rdir = Vd_w - 2 * np.sum(Vd_w * Nw, 1, keepdims=True) * Nw
        base = np.where(seam_mask(Pw_s)[:, None], SEAM_RGB[None], HULL_RGB[None])
        return base * (amb + dif * 0.85) + spec + fr[:, None] * sky(rdir) * 0.35
    img = np.zeros((Hh, W, 3))
    ys_ = np.arange(Hh); xs_ = np.arange(W)
    for row0 in range(0, Hh, 100):
        rows = ys_[row0:row0 + 100]; acc = np.zeros((len(rows), W, 3))
        for sy in range(ss):
            for sx in range(ss):
                px = (xs_[None, :] + (sx + 0.5) / ss) / W * 2 - 1; py = 1 - (rows[:, None] + (sy + 0.5) / ss) / Hh * 2
                px = np.broadcast_to(px, (len(rows), W)).ravel(); py = np.broadcast_to(py, (len(rows), W)).ravel()
                tanf = math.tan(fov / 2); D = fw[None] + rt[None] * (px * tanf * aspect)[:, None] + u2[None] * (py * tanf)[:, None]
                D /= np.linalg.norm(D, axis=1, keepdims=True); O_ = np.broadcast_to(cam, D.shape)
                t, P, N = hit_capsule(to_sh(O_), dir_sh(D)); col = sky(D)
                hit = np.isfinite(t)
                if hit.any(): col[hit] = shade_hull(P[hit], N[hit], D[hit])
                # sea plane Y = 0
                ts = np.where(D[:, 1] < -1e-4, -O_[:, 1] / D[:, 1], np.inf); sea = (~hit) & np.isfinite(ts)
                if sea.any():
                    Ps = O_[sea] + D[sea] * ts[sea][:, None]
                    k1 = 0.9 * np.sin(0.31 * Ps[:, 0] + 0.17 * Ps[:, 2]) + 0.6 * np.sin(0.53 * Ps[:, 2] - 0.21 * Ps[:, 0]) + 0.35 * np.sin(1.3 * Ps[:, 0] + 0.9 * Ps[:, 2])
                    fade = np.clip(1 - (ts[sea] - 20) / 260, 0.05, 1)
                    Nw = np.c_[fade * 0.018 * np.cos(0.31 * Ps[:, 0]) + fade * 0.012 * np.cos(1.3 * Ps[:, 0] + 0.9 * Ps[:, 2]), np.ones(len(Ps)), fade * (0.014 * np.cos(0.53 * Ps[:, 2]) + 0.01 * k1)]
                    Nw /= np.linalg.norm(Nw, axis=1, keepdims=True); Dv = D[sea]
                    rdir = Dv - 2 * np.sum(Dv * Nw, 1, keepdims=True) * Nw
                    fr = 0.02 + 0.98 * (1 - np.clip(-np.sum(Dv * Nw, 1), 0, 1)) ** 5
                    refl = sky(rdir); tr, Pr, Nr = hit_capsule(to_sh(Ps + Nw * 0.01), dir_sh(rdir)); rh = np.isfinite(tr)
                    if rh.any(): refl[rh] = shade_hull(Pr[rh], Nr[rh], rdir[rh])
                    deep = np.array([0.05, 0.16, 0.24])
                    tsh, _, _ = hit_capsule(to_sh(Ps + np.array([0, 0.01, 0])), dir_sh(np.broadcast_to(sun, Ps.shape).copy()))
                    shadow = np.where(np.isfinite(tsh), 0.55, 1.0)[:, None]
                    c_sea = (deep[None] * (0.6 + 0.4 * np.clip(Nw @ sun, 0, 1))[:, None] * shadow) * (1 - fr[:, None]) + refl * fr[:, None]
                    dist = ts[sea]; fog = np.clip((dist - 40) / 900, 0, 1)[:, None] ** 0.7
                    col[sea] = c_sea * (1 - fog) + sky(np.c_[Dv[:, 0], np.full(len(Dv), 0.02), Dv[:, 2]]) * fog
                acc += col.reshape(len(rows), W, 3)
        img[row0:row0 + 100] = acc / (ss * ss)
    img = img / (1 + img * 0.35) * 1.25; img = np.clip(img, 0, 1) ** (1 / 1.1)                     # gentle tone map
    plt.imsave(path, img)

# ======================================================== orthographic sheet
def views(path):
    INK = '#1f2933'; MUT = '#6b7280'; SH = '#2563eb'; WARN = '#d97706'
    f = plt.figure(figsize=(13, 8.6)); f.suptitle("Weave shuttle 'Tic Tac' — general arrangement for kT's visual approval (NON-CANON)", x=0.02, ha='left', y=0.985, color=INK, fontsize=13)
    f.text(0.02, 0.948, 'Smooth warm-white capsule. The only marks: the flush nose docking hatch and the flush side door. Everything else lives under the skin.', color=MUT, fontsize=9.5)
    xs = np.linspace(0, L, 400); ro = np.array([T.r_out(x) for x in xs]); hull = '#eeeae0'
    def person(ax, x0, z0, h=1.8):
        ax.add_patch(Circle((x0, z0 + h - 0.12), 0.12, fc='#9ca3af', ec='none')); ax.add_patch(Rectangle((x0 - 0.17, z0), 0.34, h - 0.26, fc='#9ca3af', ec='none'))
    # side
    a = f.add_axes([0.04, 0.5, 0.6, 0.38]); a.fill_between(xs, -ro, ro, color=hull); a.plot(xs, ro, color=INK, lw=1.2); a.plot(xs, -ro, color=INK, lw=1.2)
    s0, s1 = R * math.sin(DOOR['phi0']), R * math.sin(DOOR['phi1'])
    a.add_patch(FancyBboxPatch((DOOR['x0'], s0), DOOR['x1'] - DOOR['x0'], s1 - s0, boxstyle=f"round,pad=0,rounding_size={DOOR['corner']}", fc='none', ec='#8a877f', lw=1.0))
    a.text(0.5 * (DOOR['x0'] + DOOR['x1']), s1 + 0.15, 'flush side door (wet dock)', ha='center', fontsize=8.5, color=MUT)
    a.plot([0, 0], [-HATCH_R, HATCH_R], color='#8a877f', lw=2); a.text(-0.5, R + 0.25, 'flush nose hatch (0.8 m passage)', fontsize=8.5, color=MUT)
    person(a, 14.6, -R); a.text(14.6, -R - 0.35, '1.8 m', ha='center', fontsize=8, color=MUT)
    a.annotate('', xy=(0, -2.5), xytext=(L, -2.5), arrowprops=dict(arrowstyle='<->', color=INK)); a.text(L / 2, -2.85, '12.8 m', ha='center', fontsize=9.5)
    a.annotate('', xy=(13.2, -R), xytext=(13.2, R), arrowprops=dict(arrowstyle='<->', color=INK)); a.text(13.3, 0, '3.8 m', va='center', fontsize=9.5)
    a.set_xlim(-0.6, 15.2); a.set_ylim(-3.1, 2.6); a.set_aspect('equal'); a.axis('off'); a.set_title('side', loc='left', color=INK, fontsize=10)
    # top
    t = f.add_axes([0.04, 0.08, 0.6, 0.36]); t.fill_between(xs, -ro, ro, color=hull); t.plot(xs, ro, color=INK, lw=1.2); t.plot(xs, -ro, color=INK, lw=1.2)
    t.text(L / 2, 0, 'no wings · no engines on the skin · no antennas · no lights', ha='center', va='center', fontsize=9, color=MUT)
    t.set_xlim(-0.6, 15.2); t.set_ylim(-2.6, 2.6); t.set_aspect('equal'); t.axis('off'); t.set_title('top', loc='left', color=INK, fontsize=10)
    # front in the bay
    b = f.add_axes([0.67, 0.12, 0.31, 0.74]); th = np.linspace(0, 2 * np.pi, 300)
    b.add_patch(Circle((0, 0), 2.4, fc='#f8fafc', ec=MUT, lw=1.0)); b.add_patch(Circle((0, 0), 2.15, fc='none', ec=SH, lw=1.0, ls='--'))
    b.plot([-2.4, -2.4], [0, 3.6], color=MUT, lw=1); b.plot([2.4, 2.4], [0, 3.6], color=MUT, lw=1)
    b.plot([-1.9, -1.9], [0, 3.6], color=WARN, lw=1, ls=':'); b.plot([1.9, 1.9], [0, 3.6], color=WARN, lw=1, ls=':')
    b.add_patch(Circle((0, 0), R, fc=hull, ec=INK, lw=1.4)); b.add_patch(Circle((0, 0), HATCH_R, fc='none', ec='#8a877f', lw=1.2))
    b.text(0, 3.75, 'exit slot (+Z)', ha='center', fontsize=8.5, color=MUT); b.text(0, -2.75, 'bay bore r 2.4 m', ha='center', fontsize=8.5, color=MUT)
    b.text(2.2, 2.2, 'envelope\nr 2.15 m', fontsize=8, color=SH); b.text(-1.85, 3.2, '3.8 m exit width (incl.\n0.5 m each side)', fontsize=8, color=WARN)
    b.set_xlim(-2.9, 2.9); b.set_ylim(-3.0, 4.1); b.set_aspect('equal'); b.axis('off'); b.set_title('front, in the Wayfarer bay', loc='left', color=INK, fontsize=10)
    f.savefig(path, dpi=150, facecolor='white'); plt.close(f)

if __name__ == '__main__':
    V, Nn, F = capsule_mesh(); hp, hn = hatch_ring(); dp, dn = door_outline()
    hv, hnn, hf = strip_mesh(hp, hn); dv, dnn, df = strip_mesh(dp, dn)
    write_glb({'hull': (V, Nn, F, HULL_RGB, 0.35), 'seam_nose_hatch': (hv, hnn, hf, SEAM_RGB, 0.6), 'seam_side_door': (dv, dnn, df, SEAM_RGB, 0.6)},
              os.path.join(H, 'tictac_v1_model.glb'))
    views(os.path.join(H, 'weave_tictac_v1_views.png'))
    render(os.path.join(H, 'weave_tictac_v1_render.png'))
    print('ok', os.path.getsize(os.path.join(H, 'tictac_v1_model.glb')))
