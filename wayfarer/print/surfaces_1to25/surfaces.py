"""Wayfarer interior surface library, 1:25 FDM (Claude, 13 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.

Swappable surfaces: each surface is a 40 x 40 mm tile (1 m x 1 m real), detail face up, base 1.6 mm.
Feature sizes are written as the IDEAL real-world size at 1:25 and clamped UP to the active printer
profile in print_profile.json. Change the profile (or its numbers after the test print) and rerun:
    python3 surfaces.py            -> tiles/<ID>.stl, test sheet STL + preview, surfaces_manifest.json
Room assignment lives in surface_map.json; deck print files reference surfaces by ID only.
"""
import numpy as np, json, struct, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROF = json.load(open(os.path.join(HERE, 'print_profile.json')))
P = PROF['profiles'][PROF['active']]
S, Q = 0.05, 0.04                      # heightmap cell and height quantum (mm)
T, BASE = 40.0, 1.6                    # tile size, base thickness (mm)
LAYER = P['layer_mm']

# ---- profile clamps: design intent in, printable size out ----
def rb(w):  return max(w, P['min_raised_mm'])          # raised line / rib width
def gv(w):  return max(w, P['min_groove_mm'])          # groove / seam width
def sl(w):  return max(w, P['min_slot_mm'])            # through-ish slot width
def hd(d):  return max(d, P['min_hole_dia_mm'])        # hole / fastener diameter
def rl(h):  return max(round(h / LAYER) * LAYER, P['min_relief_mm'])   # relief height/depth
CLAMPS = []                                            # record of every clamped feature (manifest)
def note(sid, what, ideal, got):
    if abs(ideal - got) > 1e-9: CLAMPS.append({'surface': sid, 'feature': what, 'ideal_mm': ideal, 'printed_mm': round(got, 3)})

class Tile:
    def __init__(s, n=T):
        s.n = n; m = int(round(n / S)); s.H = np.full((m, m), BASE, np.float32)
        c = (np.arange(m) + 0.5) * S; s.XX, s.YY = np.meshgrid(c, c)
    def sl_(s, x0, y0, x1, y1):
        return slice(int(round(y0 / S)), int(round(y1 / S))), slice(int(round(x0 / S)), int(round(x1 / S)))
    def rect(s, x0, y0, x1, y1, h, mode='set'):
        sy, sx = s.sl_(x0, y0, x1, y1)
        if mode == 'set': s.H[sy, sx] = h
        elif mode == 'max': s.H[sy, sx] = np.maximum(s.H[sy, sx], h)
        elif mode == 'min': s.H[sy, sx] = np.minimum(s.H[sy, sx], h)
    def field(s, f, mode='max'):
        v = f(s.XX, s.YY); s.H[:] = np.maximum(s.H, v) if mode == 'max' else np.minimum(s.H, v)
    def rrect(s, x0, y0, x1, y1, rad, h, mode='max'):
        def f(XX, YY):
            cx = np.clip(XX, x0 + rad, x1 - rad); cy = np.clip(YY, y0 + rad, y1 - rad)
            ins = (XX >= x0) & (XX <= x1) & (YY >= y0) & (YY <= y1) & (np.hypot(XX - cx, YY - cy) <= rad)
            return np.where(ins, h, -1e9 if mode == 'max' else 1e9)
        s.field(f, mode)
    def pipe(s, axis, c, a0, a1, dia, top):
        r = dia / 2
        def f(XX, YY):
            u, v = (YY, XX) if axis == 'x' else (XX, YY)
            ins = (np.abs(u - c) < r) & (v >= a0) & (v <= a1)
            return np.where(ins, top - r + np.sqrt(np.clip(r * r - (u - c) ** 2, 0, None)), -1e9)
        s.field(f)
    def disc(s, cx, cy, rad, h, mode='max'):
        s.field(lambda XX, YY: np.where(np.hypot(XX - cx, YY - cy) <= rad, h, -1e9 if mode == 'max' else 1e9), mode)

# ---------------------------------------------------------------------------------------------
# Surfaces. Ideal sizes noted as real mm / 25.  B = base top.
# ---------------------------------------------------------------------------------------------
SURF = {}
def surface(sid, kind, name, purpose):
    def deco(fn): SURF[sid] = dict(kind=kind, name=name, purpose=purpose, fn=fn); return fn
    return deco
B = BASE

@surface('W-A', 'wall', 'Habitat lining', 'Living spaces: padded panels, light reveal, timber-slat lower panel')
def w_a(t, sid):
    t.rrect(2, 2, 38, 38, 1.6, B + rl(0.24))
    rv = gv(0.6); t.rrect(5, 34.3 - rv / 2, 35, 34.3 + rv / 2 + 2.0, 1.0, B - rl(0.36), 'min')   # light reveal
    for y0 in (24.5, 17.5):
        t.rrect(4, y0, 36, y0 + 6.2, 1.6, B + rl(0.48)); t.rrect(4.6, y0 + 0.6, 35.4, y0 + 5.6, 1.2, B + rl(0.6))
    t.rrect(4, 3.5, 36, 15.5, 1.4, B + rl(0.16))
    g = gv(0.32); note(sid, 'slat groove (8 mm real)', 0.32, g)
    pitch = max(1.6, g + 1.0)
    for x in np.arange(5.6, 35.0 - g, pitch): t.rect(x, 4.3, x + g, 14.7, B, 'min')

@surface('W-B', 'wall', 'Service lining', 'Wet rooms, galley, medical: routing ribs, access panel, fasteners')
def w_b(t, sid):
    t.rrect(2, 2, 38, 38, 1.6, B + rl(0.16))
    r = rb(1.4)
    for y in (33, 29.4, 25.8): t.rrect(4, y, 36, y + r, 0.6, B + rl(0.56))
    for y in (21.4, 17.8, 14.2, 10.6, 7.0): t.rrect(4, y, 17, y + r, 0.6, B + rl(0.56))
    t.rrect(20, 4, 36, 21.5, 1.2, B + rl(0.4)); t.rrect(21, 5, 35, 20.5, 0.8, B + rl(0.32), 'min')
    d = hd(0.8); note(sid, 'fastener head (20 mm real)', 0.8, d)
    for cx, cy in ((22.6, 6.6), (33.4, 6.6), (22.6, 18.9), (33.4, 18.9)): t.disc(cx, cy, d / 2, B + rl(0.6))

@surface('W-C', 'wall', 'Utility wall', 'ECLSS, workshop, stores: exposed pipes, clamps, louvre box')
def w_c(t, sid):
    t.rrect(2, 2, 38, 38, 1.6, B + rl(0.08))
    t.pipe('x', 34, 3, 37, 2.6, B + 1.6); t.pipe('x', 29.5, 3, 19.5, 2.6, B + 1.6); t.pipe('y', 19.5, 4, 29.5, 2.6, B + 1.6)
    for x in (9, 19, 31): t.rrect(x, 32.0, x + rb(1.4), 36.0, 0.4, B + 1.8)
    t.rrect(4, 4, 16.8, 22, 1.0, B + rl(0.6)); t.rrect(5, 5, 15.8, 21, 0.6, B + rl(0.4), 'min')
    t.rrect(22.2, 4, 36, 20, 1.0, B + rl(0.64))
    s_ = sl(0.8); note(sid, 'louvre slot (20 mm real)', 0.8, s_)
    for y in np.arange(6.0, 18.5 - s_, s_ + 1.1): t.rrect(24, y, 34.2, y + s_, 0.3, B + rl(0.16), 'min')

@surface('W-D', 'wall', 'Bulkhead frame', 'Hatches, airlock, vestibule, vault: octagonal sealing frame, gussets')
def w_d(t, sid):
    oc = lambda XX, YY, R: (np.abs(XX - 20) <= R) & (np.abs(YY - 20) <= R) & (np.abs(XX - 20) + np.abs(YY - 20) <= R * 1.42)
    t.field(lambda XX, YY: np.where(oc(XX, YY, 17) & ~oc(XX, YY, 13.4), B + rl(0.8), -1e9))
    t.field(lambda XX, YY: np.where(oc(XX, YY, 12.6), B - rl(0.32), 1e9), 'min')
    t.field(lambda XX, YY: np.where(oc(XX, YY, 10.0), B - rl(0.16), -1e9))
    for cx, cy in ((4.5, 4.5), (35.5, 4.5), (4.5, 35.5), (35.5, 35.5)): t.rrect(cx - 3, cy - 3, cx + 3, cy + 3, 1.0, B + rl(0.48))
    for cx, cy, hor in ((20, 2.6, 1), (20, 37.4, 1), (2.6, 20, 0), (37.4, 20, 0)):
        a, b = (4, 1.6) if hor else (1.6, 4); t.rrect(cx - a, cy - b, cx + a, cy + b, 0.6, B + rl(0.48))

@surface('F-1', 'floor', 'Smooth deck', 'Living floors: 0.5 m plates, flush seams, corner fixings')
def f_1(t, sid):
    g = gv(0.4); note(sid, 'plate seam (10 mm real)', 0.4, g)
    for v in (0.0, 20.0, 40.0):
        a, b = max(0, v - g / 2), min(40, v + g / 2)
        t.rect(a, 0, b, 40, B - rl(0.24), 'min'); t.rect(0, a, 40, b, B - rl(0.24), 'min')
    d = hd(0.8); note(sid, 'plate fixing (20 mm real)', 0.8, d)
    for cx in (3, 17, 23, 37):
        for cy in (3, 17, 23, 37): t.disc(cx, cy, d / 2, B - rl(0.16), 'min')

@surface('F-2', 'floor', 'Ribbed deck', 'Wet rooms, galley, exercise, suit room: anti-slip ribs')
def f_2(t, sid):
    r = rb(0.8); g = gv(0.8)
    for x in np.arange(2.0, 38.0 - r, r + g): t.rrect(x, 2, x + r, 38, min(0.45, r / 2), B + rl(0.32))

@surface('F-3', 'floor', 'Grated deck', 'ECLSS, airlock, stores: open grating over sumps')
def f_3(t, sid):
    t.rect(0, 0, T, T, B + rl(0.2))
    s_ = sl(1.0); note(sid, 'grating slot (25 mm real)', 1.0, s_)
    pitch = s_ + 1.6
    for row in range(5):
        for col in range(3):
            x0 = 3 + col * 11.8; y0 = 3 + row * 7.0
            for k in range(int((10.4 - s_) // pitch) + 1): t.rrect(x0 + k * pitch, y0, x0 + k * pitch + s_, y0 + 5.4, min(0.45, s_ / 2), B - rl(0.6), 'min')

@surface('F-4', 'floor', 'Corridor walkway', 'Ring corridors: recessed wear strips with tread bars, centre seam')
def f_4(t, sid):
    for x0 in (6, 30):
        t.rect(x0, 0, x0 + 4, 40, B - rl(0.36), 'min')
        bar = rb(0.8)
        for y in np.arange(1.0, 40 - bar, 2.0): t.rect(x0 + 0.5, y, x0 + 3.5, y + bar, B - rl(0.12))
    g = gv(0.4); t.rect(20 - g / 2, 0, 20 + g / 2, 40, B - rl(0.24), 'min')

@surface('C-1', 'ceiling', 'Living ceiling', 'Living spaces: perimeter cove sweep, cove-light reveal, radial seams')
def c_1(t, sid):
    t.field(lambda XX, YY: np.where(YY > 30, B + rl(0.4) * np.clip((YY - 30) / 10, 0, 1) ** 0.5, -1e9))
    t.rect(0, 29.0, 40, 29.0 + gv(1.0), B - rl(0.36), 'min')
    g = gv(0.4); note(sid, 'ceiling seam (10 mm real)', 0.4, g)
    for x in (6.5, 20, 33.5): t.rect(x - g / 2, 0, x + g / 2, 29, B - rl(0.24), 'min')

@surface('C-2', 'ceiling', 'Corridor ceiling', 'Corridors, vestibule: light panel, overhead handrails on standoffs')
def c_2(t, sid):
    t.rrect(6, 10, 34, 30, 1.4, B + rl(0.48)); t.rrect(8, 12, 32, 28, 1.0, B - rl(0.4), 'min')
    t.pipe('x', 5.0, 0, 40, 2.4, B + 1.2); t.pipe('x', 35.0, 0, 40, 2.4, B + 1.2)
    w = rb(1.6) / 2
    for x in (8, 32): t.rrect(x - w, 3.0, x + w, 7.0, 0.3, B + 1.0); t.rrect(x - w, 33.0, x + w, 37.0, 0.3, B + 1.0)

@surface('C-3', 'ceiling', 'Technical ceiling', 'ECLSS, workshop, stores, airlock: open cable trays with rungs')
def c_3(t, sid):
    for y0 in (6, 22):
        t.rect(2, y0, 38, y0 + 10, B + rl(0.16)); t.rect(3.5, y0 + 1.2, 36.5, y0 + 8.8, B - rl(0.24), 'min')
        r = rb(0.6); note(sid, 'tray rung (15 mm real)', 0.6, r)
        for x in np.arange(5, 36, 4.5): t.rect(x, y0 + 1.2, x + r, y0 + 8.8, B + rl(0.16))

# ---------------------------------------------------------------------------------------------
# Closed-solid mesher (heightmap -> binary STL). Verified volume-exact on the first test sheet.
# ---------------------------------------------------------------------------------------------
def mesh(H):
    Hq = np.round(H / Q).astype(np.int32); ny, nx = Hq.shape; F = []
    def quad(a, b, c, d): F.append((a, b, c)); F.append((a, c, d))
    def runs(row):
        b = np.flatnonzero(np.diff(row)) + 1; st = np.r_[0, b]; en = np.r_[b, len(row)]
        return [(int(s), int(e), int(row[s])) for s, e in zip(st, en) if row[s] > 0]
    def sweep(A, flush):
        prev = {}
        for j in range(ny):
            cur = {}
            for k in runs(A[j]): cur[k] = prev.pop(k, j)
            for k, y0 in prev.items(): flush(k, y0, j)
            prev = cur
        for k, y0 in prev.items(): flush(k, y0, ny)
    sweep(Hq, lambda k, y0, y1: quad((k[0]*S, y0*S, k[2]*Q), (k[1]*S, y0*S, k[2]*Q), (k[1]*S, y1*S, k[2]*Q), (k[0]*S, y1*S, k[2]*Q)))
    sweep((Hq > 0).astype(np.int32), lambda k, y0, y1: quad((k[0]*S, y0*S, 0), (k[0]*S, y1*S, 0), (k[1]*S, y1*S, 0), (k[1]*S, y0*S, 0)))
    Pp = np.pad(Hq, ((0, 0), (1, 1))); prev = {}
    def xflush(k, y0, y1):
        i, ha, hb = k; x = i * S; za, zb = ha * Q, hb * Q
        if ha > hb: quad((x, y0*S, zb), (x, y1*S, zb), (x, y1*S, za), (x, y0*S, za))
        else: quad((x, y0*S, za), (x, y0*S, zb), (x, y1*S, zb), (x, y1*S, za))
    for j in range(ny):
        a = Pp[j, :-1]; b = Pp[j, 1:]; cur = {}
        for i in np.flatnonzero(a != b): k = (int(i), int(a[i]), int(b[i])); cur[k] = prev.pop(k, j)
        for k, y0 in prev.items(): xflush(k, y0, j)
        prev = cur
    for k, y0 in prev.items(): xflush(k, y0, ny)
    Pp = np.pad(Hq, ((1, 1), (0, 0)))
    for j in range(ny + 1):
        a = Pp[j]; b = Pp[j + 1]; d = a != b
        if not d.any(): continue
        key = np.where(d, a.astype(np.int64) * 100000 + b, -1)
        bnd = np.flatnonzero(np.diff(key)) + 1; y = j * S
        for s, e in zip(np.r_[0, bnd], np.r_[bnd, len(key)]):
            if key[s] < 0: continue
            za, zb = a[s] * Q, b[s] * Q
            if a[s] > b[s]: quad((s*S, y, zb), (s*S, y, za), (e*S, y, za), (e*S, y, zb))
            else: quad((s*S, y, za), (e*S, y, za), (e*S, y, zb), (s*S, y, zb))
    Fs = np.array(F, np.float32)
    vol = float((Hq * Q).sum() * S * S)
    return Fs, vol

def write_stl(path, Fs, title):
    n = np.cross(Fs[:, 1] - Fs[:, 0], Fs[:, 2] - Fs[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(Fs), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); rec['n'] = n; rec['v'] = Fs
    with open(path, 'wb') as fh:
        fh.write(title.encode()[:80].ljust(80, b' ')); fh.write(struct.pack('<I', len(Fs))); fh.write(rec.tobytes())

def stl_volume(Fs):
    return float(np.einsum('ij,ij->i', Fs[:, 0], np.cross(Fs[:, 1], Fs[:, 2])).sum() / 6)

# ---------------------------------------------------------------------------------------------
# Calibration ladder (test sheet only; not profile-clamped on purpose)
# ---------------------------------------------------------------------------------------------
def ladder():
    t = Tile()
    for i, w in enumerate([0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.80]):
        x = 2.0 + i * 4.0; t.rect(x, 21, x + w, 38, B + 0.4); t.rect(x, 3, x + w, 19, B - 0.4, 'min')
    for i, d in enumerate([0.08, 0.12, 0.16, 0.24, 0.32, 0.48, 0.64]): t.rect(1.0 + i * 5.4, 0.6, 1.0 + i * 5.4 + 4.6, 2.4, B + d)
    return t.H

def build():
    os.makedirs(os.path.join(HERE, 'tiles'), exist_ok=True)
    tag = PROF['active']; man = {'profile': tag, 'status': P['status'], 'tiles': {}}
    Hs = {}
    for sid, s in SURF.items():
        t = Tile(); s['fn'](t, sid); Hs[sid] = t.H
        Fs, vol = mesh(t.H); fn = f'tiles/{sid}.stl'
        write_stl(os.path.join(HERE, fn), Fs, f'Wayfarer 1:25 surface {sid} {s["name"]} [{tag}]')
        ok = abs(stl_volume(Fs) - vol) < 1e-3 * vol
        man['tiles'][sid] = dict(kind=s['kind'], name=s['name'], purpose=s['purpose'], file=fn, triangles=len(Fs),
                                 volume_mm3=round(vol, 1), closed_volume_check='PASS' if ok else 'FAIL',
                                 max_height_mm=round(float(t.H.max()), 2))
    man['clamped_features'] = CLAMPS
    # ---- test sheet: 4 x 3 tiles + labels ----
    G, LAB = 5.0, 7.0; order = [['C-1', 'C-2', 'C-3', 'L'], ['F-1', 'F-2', 'F-3', 'F-4'], ['W-A', 'W-B', 'W-C', 'W-D']]
    Hs['L'] = ladder(); names = dict(zip(['W-A','W-B','W-C','W-D','F-1','F-2','F-3','F-4','C-1','C-2','C-3','L'],['HABITAT','SERVICE','UTILITY','BULKHEAD','SMOOTH','RIBBED','GRATED','WALKWAY','LIVING','CORRIDOR','TECH','LADDER']))
    W = 4 * T + 3 * G; Hh = 3 * (T + LAB) + 2 * G; m = int(round(T / S))
    Sh = np.zeros((int(round(Hh / S)), int(round(W / S))), np.float32)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int(3.2 / S))
    for r, row in enumerate(order):
        for c, sid in enumerate(row):
            x0 = int(round(c * (T + G) / S)); y0 = int(round((r * (T + LAB + G) + LAB) / S))
            Sh[y0:y0 + m, x0:x0 + m] = Hs[sid]
            img = Image.new('L', (m, int((LAB - 1) / S)), 0); ImageDraw.Draw(img).text((int(0.6 / S), int(0.5 / S)), f'{sid} {names[sid]}'[:17], fill=255, font=f)
            a = np.array(img)[::-1] > 128; ly = y0 - int(round((LAB - 0.5) / S))
            Sh[ly:ly + a.shape[0], x0:x0 + m] = np.where(a, B + 0.4, B * 0.75)
    Fs, vol = mesh(Sh); write_stl(os.path.join(HERE, 'wayfarer_1to25_surface_test_sheet.stl'), Fs, f'Wayfarer 1:25 surface test sheet [{tag}]')
    man['test_sheet'] = dict(file='wayfarer_1to25_surface_test_sheet.stl', size_mm=[round(W, 1), round(Hh, 1)], triangles=len(Fs),
                             closed_volume_check='PASS' if abs(stl_volume(Fs) - vol) < 1e-3 * vol else 'FAIL')
    # ---- preview (raking light) ----
    gy, gx = np.gradient(Sh, S); sh = np.clip(0.55 + 0.9 * (-gx * 0.6 + gy * 0.8) / np.sqrt(1 + gx ** 2 + gy ** 2), 0, 1)
    sh = np.where(Sh > 0, sh * (0.75 + 0.25 * (Sh - B * 0.75) / max(1e-6, Sh.max() - B * 0.75)), 0.12)
    im = Image.fromarray((np.dstack([sh * 228, sh * 222, sh * 210]) ).astype(np.uint8)[::-1]).resize((int(W / S / 2.5), int(Hh / S / 2.5)), Image.LANCZOS)
    im.save(os.path.join(HERE, 'test_sheet_preview.png'))
    json.dump(man, open(os.path.join(HERE, 'surfaces_manifest.json'), 'w'), indent=1)
    return man

if __name__ == '__main__':
    m = build()
    print('profile', m['profile']); [print(k, v['triangles'], v['closed_volume_check']) for k, v in m['tiles'].items()]
    print('sheet', m['test_sheet']); print('clamped', len(m['clamped_features']))
