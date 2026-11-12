"""Wayfarer 1:100 printed-hull etch (Claude, 13 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.

Print LOD only, separate from canon (the canon GLBs keep their true-scale etch). Builds:
  etch_spec_1to100.json     every approved groove/frame/opening on the r 4.5 m hull cylinder (x 2.35-34.3), ship metres
  hull_development_1to100.png  the whole hull cylinder unrolled flat, at print scale
  coupon_L4L5_1to100.stl    curved test ring x 8.0-14.2 (62 mm tall, 90 mm dia), printed axis vertical
  manifest_1to100.json      profile, dropped features, volume check
Sources: kt_decisions seam grid (9 Nov, as encoded in render/loomgl.js seamRingM/seamLongM), exterior_surface_2026_11_13
(Option B joints, EVA hatch frame, medical port frames at x 9.30), canon_finish_2026_11_11 (0.5 mm grooves at 1:100),
geometry features (windows, node faces, hatch, viewport bands). The bow cone (x < 2.35) is not covered here.
"""
import json, math, os, struct
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.abspath(os.path.join(HERE, '..', '..'))
PROF = json.load(open(os.path.join(HERE, 'print_profile_1to100.json')))
P = PROF['profiles'][PROF['active']]
G = json.load(open(os.path.join(WF, 'results/out/wayfarer_v05_geometry.json')))
R = 4.5; X0, X1 = 2.35, 34.3; K = 10.0          # hull radius (m), cylinder extent, mm print per m real
def az_of(p): return (math.degrees(math.atan2(p[2], p[1])) + 360) % 360
def adiff(a, b): return abs((a - b + 180) % 360 - 180)

# ------------------------------------------------------------------ spec (ship metres) ------------------------------
def build_spec():
    rings = [dict(x=x, src='9 Nov grid') for x in (2.35, 3.0, 5.6, 8.2, 10.8)] + \
            [dict(x=14.0 + 2 * i, src='9 Nov grid') for i in range(11)] + \
            [dict(x=x, src='B mid-bay') for x in (4.3, 6.9, 9.5, 12.1, 13.4)] + \
            [dict(x=15.0 + 2 * i, src='B mid-bay') for i in range(10)]
    longs = [dict(az=a, x0=X0, x1=X1, src='9 Nov grid') for a in (0, 40, 140, 180, 220, 270, 320)]
    longs += [dict(az=a, x0=18.25, x1=32.05, src='9 Nov grid (bay door edge)') for a in (57.769047364497894, 122.2309526355021)]
    have = {round(l['az'], 3) for l in longs}
    for a in range(0, 360, 20):
        if a in have: continue
        if 57.77 < a < 122.23:   # bay doors x 18.25-32.05: joints stop at the door edges
            longs += [dict(az=a, x0=X0, x1=18.25, src='B 20 deg'), dict(az=a, x0=32.05, x1=X1, src='B 20 deg')]
        else: longs.append(dict(az=a, x0=X0, x1=X1, src='B 20 deg'))
    circles, dots, openings, keep_clear = [], [], [], []
    for f in G['features']:
        x = f['pos'][0]; a = az_of(f['pos'])
        if not (X0 < x < X1): continue
        if f['kind'] == 'window':
            if f.get('room') == 'L4-medical': x = 9.30          # exterior_surface_2026_11_13 / l4_decisions
            openings.append(dict(x=x, az=a, r=f['d_m'] / 2, what='window ' + f.get('room', '')))
            if f.get('room') == 'L4-medical': circles.append(dict(x=x, az=a, r=0.92, what='medical port frame (B)'))
        elif f['kind'] == 'node_face':
            circles.append(dict(x=x, az=a, r=f['d_m'] / 2, what='Metric node face outline'))
            keep_clear.append(dict(x=x, az=a, r=f['d_m'] / 2))
        elif f['kind'] == 'hatch':   # EVA hatch: closed plug, d 1.1 = outer frame (exterior_surface_2026_11_13)
            circles += [dict(x=x, az=a, r=0.55, what='EVA hatch plug edge'), dict(x=x, az=a, r=0.70, what='EVA hatch frame (B)')]
            for k in range(8):
                t = k * math.pi / 4; dots.append(dict(x=x + 0.625 * math.cos(t), az=a + math.degrees(0.625 * math.sin(t) / R), d=0.06, what='hatch latch'))
            keep_clear.append(dict(x=x, az=a, r=0.70))
    bands = [dict(x0=b['x'][0], x1=b['x'][1], a0=b['a'][0], a1=b['a'][1], what='L2 viewport band') for b in G['bands']]
    for o in openings: keep_clear.append(dict(x=o['x'], az=o['az'], r=o['r'] + 0.05))
    for c in circles:
        if 'medical' in c['what']: keep_clear.append(dict(x=c['x'], az=c['az'], r=c['r']))
    return dict(header='ALL bodies. ALL sponsors. 2026-2226.', units='ship metres; az deg (Y = r cos a, Z = r sin a)',
                hull=dict(radius_m=R, x_m=[X0, X1]), groove_real_width_m=0.05,
                rings=rings, longitudinals=longs, outline_circles=circles, dots=dots, openings=openings, bands=bands,
                keep_clear=keep_clear,
                not_covered='bow cone x<2.35, aft of 34.3, protruding fixtures (rails, grapples, RCS, sensors, strakes: separate print parts)')

# ------------------------------------------------------------------ rasteriser ---------------------------------------
def raster(spec, x0, x1, dx_mm, n_th, dropped):
    """Wall map over (x rows, theta cols): 2 = full wall, 1 = etched, 0 = through-opening."""
    xs = x0 + (np.arange(int(round((x1 - x0) * K / dx_mm))) + 0.5) * dx_mm / K
    th = (np.arange(n_th) + 0.5) * 360.0 / n_th
    XX, TT = np.meshgrid(xs, th, indexing='ij')
    hw = P['groove_width_mm'] / 2 / K                      # half groove width, metres real
    S = lambda a: np.radians((TT - a + 180) % 360 - 180) * R   # signed arc distance (m) from azimuth a
    D = lambda f: np.hypot(XX - f['x'], S(f['az']))
    clear = np.zeros(XX.shape, bool)
    for c in spec['keep_clear']: clear |= D(c) < c['r']
    for b in spec['bands']:
        clear |= (XX > b['x0'] - .05) & (XX < b['x1'] + .05) & (((TT - b['a0']) % 360) < (b['a1'] - b['a0']) % 360 + 1e-9)
    g = np.zeros(XX.shape, bool)
    for r_ in spec['rings']:
        if x0 - hw < r_['x'] < x1 + hw: g |= np.abs(XX - r_['x']) < hw
    for l in spec['longitudinals']:
        g |= (np.abs(S(l['az'])) < hw) & (XX >= l['x0']) & (XX <= l['x1'])
    g &= ~clear
    for c in spec['outline_circles']: g |= np.abs(D(c) - c['r']) < hw
    for d in spec['dots']:
        if d['d'] * K < P['min_hole_dia_mm']: dropped.add(f"{d['what']} ({d['d']*K:.2f} mm < min hole {P['min_hole_dia_mm']} mm)"); continue
        g |= D(d) < d['d'] / 2
    W = np.where(g, 1, 2).astype(np.int8)
    for o in spec['openings']:
        if o['r'] * 2 * K < P['min_hole_dia_mm']: dropped.add(f"{o['what']} opening"); continue
        W[D(o) < o['r']] = 0
    for b in spec['bands']:
        W[(XX > b['x0']) & (XX < b['x1']) & (((TT - b['a0']) % 360) < (b['a1'] - b['a0']) % 360)] = 0
    return W, xs, th

# ------------------------------------------------------------------ cylindrical shell mesher -------------------------
def mesh_cyl(W, x0, dx_mm, n_th, r_out_mm, wall, depth, chunk=16):
    """W rows = x, cols = theta (periodic). Levels: 2 -> r_out, 1 -> r_out-depth, 0 -> inner wall / no material.
    Quads are merged in integer index space (theta col i, x row j, level l), then made conforming: every quad edge is
    split at all vertices used on that grid line, so the mesh has no T-junctions. Faces are outward-facing."""
    ri = r_out_mm - wall; radv = [ri, r_out_mm - depth, r_out_mm]; rad = {0: ri, 1: radv[1], 2: r_out_mm}
    ny, nx = W.shape; dth = 2 * math.pi / n_th; Qd = []
    def quad(a, b, c, d): Qd.append((a, b, c, d))            # built inward-facing, reversed at the end
    brk = set(range(0, nx + 1, chunk))
    def runs(row):
        ch = set((np.flatnonzero(np.diff(row)) + 1).tolist()) | brk | {nx}
        st = sorted(ch | {0}); return [(s, e, int(row[s])) for s, e in zip(st[:-1], st[1:]) if row[s] > 0]
    def sweep(A, flush):
        prev = {}
        for j in range(ny):
            cur = {}
            for k in runs(A[j]): cur[k] = prev.pop(k, j)
            for k, y0 in prev.items(): flush(k, y0, j)
            prev = cur
        for k, y0 in prev.items(): flush(k, y0, ny)
    sweep(W, lambda k, y0, y1: quad((k[0], y0, k[2]), (k[0], y1, k[2]), (k[1], y1, k[2]), (k[1], y0, k[2])))
    sweep((W > 0).astype(np.int8), lambda k, y0, y1: quad((k[0], y0, 0), (k[1], y0, 0), (k[1], y1, 0), (k[0], y1, 0)))
    prev = {}
    def tflush(k, y0, y1):
        i, ha, hb = k
        if ha > hb: quad((i, y0, hb), (i, y0, ha), (i, y1, ha), (i, y1, hb))
        else: quad((i, y0, ha), (i, y1, ha), (i, y1, hb), (i, y0, hb))
    for j in range(ny):
        a = np.roll(W[j], 1); b = W[j]; cur = {}
        for i in np.flatnonzero(a != b): k = (int(i), int(a[i]), int(b[i])); cur[k] = prev.pop(k, j)
        for k, y0 in prev.items(): tflush(k, y0, j)
        prev = cur
    for k, y0 in prev.items(): tflush(k, y0, ny)
    Pd = np.pad(W, ((1, 1), (0, 0)))
    for j in range(ny + 1):
        a = Pd[j]; b = Pd[j + 1]
        if not (a != b).any(): continue
        key = np.where(a != b, a.astype(np.int32) * 10 + b, -1)
        ch = set((np.flatnonzero(np.diff(key)) + 1).tolist()) | brk | {nx}; st = sorted(ch | {0})
        for s, e in zip(st[:-1], st[1:]):
            if key[s] < 0: continue
            la, lb = int(a[s]), int(b[s])
            if la > lb: quad((s, j, lb), (e, j, lb), (e, j, la), (s, j, la))
            else: quad((s, j, la), (s, j, lb), (e, j, lb), (e, j, la))
    # ---- conforming pass: collect used vertices per grid line (theta index wraps: nx == 0) ----
    from collections import defaultdict
    Li, Lj, Ll = defaultdict(set), defaultdict(set), defaultdict(set)
    for q in Qd:
        for (i, j, l) in q:
            for ii in ({0, nx} if i % nx == 0 else {i}):
                Li[(j, l)].add(ii); Lj[(ii, l)].add(j); Ll[(ii, j)].add(l)
    Li = {k: np.array(sorted(v)) for k, v in Li.items()}; Lj = {k: np.array(sorted(v)) for k, v in Lj.items()}
    Ll = {k: np.array(sorted(v)) for k, v in Ll.items()}
    def between(arr, a, b):
        lo, hi = min(a, b), max(a, b); m = arr[(arr > lo) & (arr < hi)]
        return m if a < b else m[::-1]
    def P3(i, j, l):
        r = np.interp(l, [0, 1, 2], radv) if l != int(l) else radv[int(l)]
        return (x0 * K + j * dx_mm, r * math.cos(i * dth), r * math.sin(i * dth))
    F = []
    for q in Qd:
        poly = []
        for t in range(4):
            (i0, j0, l0), (i1, j1, l1) = q[t], q[(t + 1) % 4]; poly.append((i0, j0, l0))
            if i0 != i1: poly += [(int(m), j0, l0) for m in between(Li.get((j0, l0), np.array([])), i0, i1)]
            elif j0 != j1: poly += [(i0, int(m), l0) for m in between(Lj.get((i0 % nx if i0 != nx else nx, l0), np.array([])), j0, j1)]
            elif l0 != l1: poly += [(i0, j0, int(m)) for m in between(Ll.get((i0, j0), np.array([])), l0, l1)]
        pts = [P3(*v) for v in poly]
        if len(pts) == 4: F += [(pts[0], pts[1], pts[2]), (pts[0], pts[2], pts[3])]
        else:
            ci = sum(v[0] for v in q) / 4; cj = sum(v[1] for v in q) / 4; cl = sum(v[2] for v in q) / 4
            c = P3(ci, cj, cl)
            F += [(c, pts[k], pts[(k + 1) % len(pts)]) for k in range(len(pts))]
    return np.array(F, np.float32)[:, ::-1, :].copy(), rad

def write_stl(path, Fs, title):
    n = np.cross(Fs[:, 1] - Fs[:, 0], Fs[:, 2] - Fs[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(Fs), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); rec['n'] = n; rec['v'] = Fs
    with open(path, 'wb') as fh: fh.write(title.encode()[:80].ljust(80, b' ')); fh.write(struct.pack('<I', len(Fs))); fh.write(rec.tobytes())

def main():
    spec = build_spec(); dropped = set()
    json.dump(spec, open(os.path.join(HERE, 'etch_spec_1to100.json'), 'w'), indent=1)
    # ---- coupon: x 8.0-14.2, axis vertical ----
    cx0, cx1, dx, n_th = 8.0, 14.2, 0.05, 2880
    W, xs, th = raster(spec, cx0, cx1, dx, n_th, dropped)
    wall, depth = P['shell_wall_mm'], P['groove_depth_mm']
    Fs, rad = mesh_cyl(W, cx0, dx, n_th, R * K, wall, depth)
    # print orientation: ship X -> print Z (bow end up), shift to bed
    Fp = Fs[..., [1, 2, 0]].copy(); Fp[..., 2] = (cx1 * K) - Fp[..., 2]
    Fp[..., 0] += R * K + 5; Fp[..., 1] += R * K + 5
    Fp = Fp[:, ::-1, :]          # mirror from the X flip: restore outward winding
    write_stl(os.path.join(HERE, 'coupon_L4L5_1to100.stl'), Fp, f'Wayfarer 1:100 hull coupon x8.0-14.2 [{PROF["active"]}]')
    vol = float(np.einsum('ij,ij->i', Fp[:, 0], np.cross(Fp[:, 1], Fp[:, 2])).sum() / 6)
    ann = lambda r: math.pi * (r * r - (R * K - wall) ** 2) / n_th * dx
    ref = float(sum((W == v).sum() * ann(rad[v]) for v in (1, 2)))
    from collections import Counter
    kq = np.round(Fp.astype(float) * 1e4).astype(np.int64); kk = lambda p: p[..., 0] * 1000003 ** 2 + p[..., 1] * 1000003 + p[..., 2]
    ed = Counter(map(tuple, np.stack([np.stack([kk(kq[:, i]), kk(kq[:, (i + 1) % 3])], 1) for i in range(3)], 1).reshape(-1, 2)))
    unmatched = sum(1 for (a, b), c in ed.items() if ed.get((b, a), 0) != c)
    # ---- development (unrolled) preview of the whole cylinder hull ----
    Wd, xd, td = raster(spec, X0, X1, 0.25, 1131, set())
    img = np.where(Wd == 2, 222, np.where(Wd == 1, 60, 15)).astype(np.uint8).T[::-1]
    im = Image.fromarray(img).convert('RGB'); d = ImageDraw.Draw(im)
    for a in (0, 90, 180, 270): y = int((1 - a / 360) * im.height); d.text((4, max(0, y - 12)), f'{a} deg', fill=(200, 60, 40))
    for x in (3.0, 5.6, 8.2, 10.8, 14.0, 20.0, 26.0, 32.0): d.text((int((x - X0) * K / 0.25) + 3, 3), f'x{x:g}', fill=(200, 60, 40))
    bg = Image.new('RGB', (im.width + 20, im.height + 60), (245, 245, 242)); bg.paste(im, (10, 50)); dd = ImageDraw.Draw(bg)
    dd.text((10, 8), 'Wayfarer hull cylinder x 2.35-34.3 unrolled, 1:100 print (320 x 283 mm). Dark = 0.5 mm groove, black = opening. B joints + 9 Nov grid.', fill=(0, 0, 0))
    dd.text((10, 26), f'Profile {PROF["active"]} (PLACEHOLDER). Coupon = x 8.0-14.2 (L4 medical ports, L5 EVA hatch).', fill=(0, 0, 0))
    bg.save(os.path.join(HERE, 'hull_development_1to100.png'))
    man = dict(profile=PROF['active'], status=P['status'], coupon=dict(file='coupon_L4L5_1to100.stl', x_m=[cx0, cx1],
               size_mm=[round(2 * R * K, 1), round(2 * R * K, 1), round((cx1 - cx0) * K, 1)], triangles=len(Fp),
               volume_mm3=round(vol, 1), heightmap_volume_mm3=round(ref, 1), volume_check='PASS' if abs(vol - ref) < 0.005 * ref else 'FAIL',
               orientation='axis vertical, bow end up, no supports', unmatched_edges=unmatched, watertight='PASS' if unmatched == 0 else 'FAIL'),
               dropped_at_this_scale=sorted(dropped),
               counts=dict(rings=len(spec['rings']), longitudinals=len(spec['longitudinals']), outline_circles=len(spec['outline_circles']),
                           openings=len(spec['openings']), bands=len(spec['bands'])))
    json.dump(man, open(os.path.join(HERE, 'manifest_1to100.json'), 'w'), indent=1)
    print(json.dumps(man, indent=1))

if __name__ == '__main__': main()
