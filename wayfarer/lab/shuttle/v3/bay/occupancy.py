"""Occupancy of candidate bay-extension regions in the Wayfarer v0.5 geometry record (read-only).
ALL bodies. ALL sponsors. 2026-2226."""
import json, math, numpy as np, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), *(['..'] * 5))
G = json.load(open(os.path.join(ROOT, 'wayfarer/results/out/wayfarer_v05_geometry.json')))['parts']
def inside(s, x, y, z):
    k = s.get('k'); r = math.hypot(y, z); az = math.degrees(math.atan2(z, y)) % 360
    if k in ('sector', 'cslot') and not (s['x0'] <= x <= s['x1'] and s['r0'] <= r <= s['r1']): return False
    if k == 'sector':
        a0, a1 = s.get('a0', 0) % 360, s.get('a1', 360) % 360
        if s.get('a1', 360) - s.get('a0', 0) >= 360: return True
        return (a0 <= az <= a1) if a0 <= a1 else (az >= a0 or az <= a1)
    if k == 'cslot': return not (abs(y) < s['hw'] and z > 0)
    if k == 'box': return s['x0'] <= x <= s['x1'] and s['y0'] <= y <= s['y1'] and s['z0'] <= z <= s['z1']
    if k == 'tube':
        p0, p1 = np.array(s['p0']), np.array(s['p1']); q = np.array([x, y, z]); d = p1 - p0
        t = np.clip((q - p0) @ d / (d @ d), 0, 1); return np.linalg.norm(q - (p0 + t * d)) <= s['r']
    return False
def scan(x0, x1, r0, r1, n=24000, seed=1):
    rng = np.random.default_rng(seed); hits = {}; free = 0
    for _ in range(n):
        x = rng.uniform(x0, x1); r = math.sqrt(rng.uniform(r0 ** 2, r1 ** 2)); a = rng.uniform(0, 2 * math.pi); y, z = r * math.cos(a), r * math.sin(a)
        who = [p['id'] for p in G if isinstance(p, dict) and 'shape' in p and inside(p['shape'], x, y, z)]
        if not who: free += 1
        for w in who: hits[w] = hits.get(w, 0) + 1
    vol = math.pi * (r1 ** 2 - r0 ** 2) * (x1 - x0)
    return dict(region=dict(x=[x0, x1], r=[r0, r1]), volume_m3=round(vol, 1), free_m3=round(vol * free / n, 1),
                occupants={k: round(vol * v / n, 1) for k, v in sorted(hits.items(), key=lambda t: -t[1])[:12]})
if __name__ == '__main__':
    out = {'x14-17 r2-4.3 (fore annulus)': scan(14, 17, 2.0, 4.3), 'x17-18 r0-4.3': scan(17, 18, 0, 4.3, 12000),
           'x13.4-14 r0-4.3': scan(13.4, 14, 0, 4.3, 8000), 'x32.05-34.3 r0-4.48 (aft)': scan(32.05, 34.3, 0, 4.48, 12000)}
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'occupancy.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))
