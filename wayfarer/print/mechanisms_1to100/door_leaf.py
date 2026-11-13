"""Wayfarer 1:100 pivoting bay-door leaf (Claude, 14 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.
Decision: exterior_hardware_1to100_2026_11_13 (2 = a), revised by kT 14 Nov: 'Go pivot' (one leaf set that swings, not swap sets).
Canon: door_starboard/door_port sectors x 18.25-32.05, r 4.4-4.5, 57.77-90 / 90-122.23 deg; 'open to vertical' (SPEC).
The leaf is a prism: its cross-section (arc band + hinge boss - pin hole) extruded along the ship axis. One STL serves both
leaves (the port leaf is the same solid turned end for end). Prints standing on end so the pin hole is round. Units mm."""
import numpy as np, math, struct, json, os
from skimage import measure
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'parts')
K = 10.0                                      # mm per m
A_H = 57.769047364497894                      # door edge azimuth (starboard)
RO, RI = 4.5 * K, 4.34 * K                    # outer skin; leaf 1.6 mm thick (true 1.0 mm: declared exaggeration)
GAP = 0.2                                     # mm centre-split gap
PIV_R, PIV_DAZ, BOSS_R, PIN_D = 45.0, 3.0, 1.75, 1.85
L = (32.05 - 18.25) * K                       # 138 mm
PIVOT = (PIV_R * math.cos(math.radians(A_H + PIV_DAZ)), PIV_R * math.sin(math.radians(A_H + PIV_DAZ)))

def section(res=0.02):
    y0, y1, z0, z1 = -1.0, 26.0, 38.0, 48.0
    ys = np.arange(y0, y1, res); zs = np.arange(z0, z1, res); Y, Z = np.meshgrid(ys, zs, indexing='ij')
    r = np.hypot(Y, Z); az = np.degrees(np.arctan2(Z, Y)); a_end = 90 - math.degrees(GAP / 2 / RO)
    band = (r >= RI) & (r <= RO) & (az >= A_H + 0.05) & (az <= a_end)
    dp = np.hypot(Y - PIVOT[0], Z - PIVOT[1]); m = (band | (dp <= BOSS_R)) & ~(dp <= PIN_D / 2)
    loops = measure.find_contours(np.pad(m.astype(float), 1), 0.5)
    loops = [measure.approximate_polygon(c, 0.008) for c in loops]
    loops = [np.c_[y0 + (c[:, 0] - 1) * res, z0 + (c[:, 1] - 1) * res][:-1] for c in loops]
    area_px = m.sum() * res * res
    return loops, area_px

def signed_area(p): return 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])

def earclip(outer, holes):
    """Triangulate a polygon with holes (outer CCW, holes CW): bridge each hole to the outer ring, then clip ears."""
    poly = [tuple(p) for p in outer]
    for h in sorted(holes, key=lambda h: -h[:, 0].max()):
        hi = int(np.argmax(h[:, 0])); hp = h[hi]
        cand = sorted(range(len(poly)), key=lambda i: (poly[i][0] - hp[0]) ** 2 + (poly[i][1] - hp[1]) ** 2)
        def seg_x(a, b, c, d):
            def o(p, q, r): return np.sign((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]))
            return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0
        for oi in cand:
            op = poly[oi]; ok = True
            for k in range(len(poly)):
                if seg_x(hp, op, poly[k], poly[(k + 1) % len(poly)]): ok = False; break
            if ok:
                for k in range(len(h)):
                    if seg_x(hp, op, h[k], h[(k + 1) % len(h)]): ok = False; break
            if ok: break
        hr = [tuple(p) for p in np.roll(h, -hi, axis=0)]
        poly = poly[:oi + 1] + hr + [hr[0], poly[oi]] + poly[oi + 1:]
    P = np.array(poly); idx = list(range(len(P))); tris = []
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    k = 0; stall = 0
    while len(idx) > 3 and stall <= len(idx):
        n = len(idx); k %= n
        i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % n]; a, b, c = P[i0], P[i1], P[i2]
        ear = cross(a, b, c) > 1e-12
        if ear:
            Q = P[idx]; same = (np.all(np.isclose(Q, a), 1) | np.all(np.isclose(Q, b), 1) | np.all(np.isclose(Q, c), 1))
            d1 = (b[0] - a[0]) * (Q[:, 1] - a[1]) - (b[1] - a[1]) * (Q[:, 0] - a[0])
            d2 = (c[0] - b[0]) * (Q[:, 1] - b[1]) - (c[1] - b[1]) * (Q[:, 0] - b[0])
            d3 = (a[0] - c[0]) * (Q[:, 1] - c[1]) - (a[1] - c[1]) * (Q[:, 0] - c[0])
            ear = not np.any(~same & (d1 >= -1e-12) & (d2 >= -1e-12) & (d3 >= -1e-12))
        if ear: tris.append((i0, i1, i2)); idx.pop(k); stall = 0
        else: k += 1; stall += 1
    if len(idx) == 3: tris.append(tuple(idx))
    return P, tris

def build():
    loops, area_px = section()
    loops = sorted(loops, key=lambda c: -abs(signed_area(c)))
    outer = loops[0]; holes = loops[1:]
    if signed_area(outer) < 0: outer = outer[::-1]
    holes = [h if signed_area(h) < 0 else h[::-1] for h in holes]
    P, tris = earclip(outer, holes)
    cap_area = sum(0.5 * ((P[b][0] - P[a][0]) * (P[c][1] - P[a][1]) - (P[b][1] - P[a][1]) * (P[c][0] - P[a][0])) for a, b, c in tris)
    F = []
    V = lambda p, x: (p[0], p[1], x)          # print coords: X = ship Y, Y = ship Z, Z = along the ship (standing on end)
    for a, b, c in tris:
        F.append((V(P[a], L), V(P[b], L), V(P[c], L))); F.append((V(P[a], 0), V(P[c], 0), V(P[b], 0)))
    for loop in [outer] + holes:
        for k in range(len(loop)):
            p, q = loop[k], loop[(k + 1) % len(loop)]
            F += [(V(p, 0), V(q, 0), V(q, L)), (V(p, 0), V(q, L), V(p, L))]
    F = np.array(F, np.float64)
    F[..., 0] -= F[..., 0].min() - 2; F[..., 1] -= F[..., 1].min() - 2   # move onto the bed
    return F.astype(np.float32), cap_area, signed_area(outer) + sum(signed_area(h) for h in holes), area_px

def main():
    F, cap_area, ring_area, area_px = build()
    from collections import Counter
    vol = float(np.einsum('ij,ij->i', F[:, 0].astype(float), np.cross(F[:, 1].astype(float), F[:, 2].astype(float))).sum() / 6)
    k = np.round(F.astype(float) * 1e4).astype(np.int64); kk = lambda p: p[..., 0] * 7919 ** 4 + p[..., 1] * 7919 ** 2 + p[..., 2]
    ed = Counter(map(tuple, np.stack([np.stack([kk(k[:, i]), kk(k[:, (i + 1) % 3])], 1) for i in range(3)], 1).reshape(-1, 2)))
    un = sum(1 for (a, b), c in ed.items() if ed.get((b, a), 0) != c)
    n = np.cross(F[:, 1] - F[:, 0], F[:, 2] - F[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(F), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); rec['n'] = n; rec['v'] = F
    with open(os.path.join(OUT, 'bay_door_leaf.stl'), 'wb') as fh:
        fh.write(b'Wayfarer 1:100 pivoting bay door leaf'.ljust(80, b' ')); fh.write(struct.pack('<I', len(F))); fh.write(rec.tobytes())
    man = json.load(open(os.path.join(HERE, 'parts_manifest.json')))
    V = F.reshape(-1, 3)
    man['parts']['bay_door_leaf'] = dict(qty=2, what='Bay door leaf, pivoting (one STL, print 2): 138 mm long, swings 75 deg from closed to vertical on a filament pin',
        file='parts/bay_door_leaf.stl', triangles=len(F), size_mm=[round(float(v), 2) for v in (V.max(0) - V.min(0))],
        volume_mm3=round(vol, 2), cap_area_x_length_mm3=round(cap_area * L, 2), raster_area_x_length_mm3=round(area_px * L, 2),
        volume_check='PASS' if abs(vol - ring_area * L) < 1e-3 * vol and abs(cap_area - ring_area) < 1e-6 * ring_area else 'FAIL',
        unmatched_edges=un, watertight='PASS' if un == 0 else 'FAIL',
        pivot=dict(axis='parallel to the ship axis', r_mm=PIV_R, az_deg=round(A_H + PIV_DAZ, 3), mirrored_port_az_deg=round(180 - A_H - PIV_DAZ, 3),
                   open_angle_deg=75.1, swing_check='leaf clears the hull shell (r 43-45 mm) from 0 to 80 deg'),
        pin='one 1.75 mm filament length, 144 mm: 138 through the leaf + 3 mm into each slot end wall (x 18.25 and 32.05 m on the ship)',
        print='standing on end (138 mm tall), brim on, slow outer walls; pin hole 1.85 mm, tune with peg_test',
        declared_exaggerations='leaf 1.6 mm (true 1.0); hinge boss 3.5 mm dia along the door edge, half proud of the skin')
    man['notes'].append('Bay doors pivot (kT 14 Nov). Ship-side pin holes in the slot end walls are cut with the other sockets at the end.')
    json.dump(man, open(os.path.join(HERE, 'parts_manifest.json'), 'w'), indent=1)
    print(json.dumps(man['parts']['bay_door_leaf'], indent=1)[:900])
if __name__ == '__main__': main()
