"""Wayfarer 1:100 plug-in hot fin + strake print parts (Claude, 13 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.
Decision: fin_strake_plugin_1to100_2026_11_13. Print LOD only; PLACEHOLDER until the printer arrives.
Exact rectilinear solids: boxes added/cut in order on a grid made of every box boundary, then every face between a
filled and an empty cell is emitted. Faces share grid vertices, so meshes are watertight by construction.
Prints flat, largest face down, no supports. Units mm."""
import numpy as np, struct, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'parts'); os.makedirs(OUT, exist_ok=True)
PROF = json.load(open(os.path.join(HERE, '..', 'hull_1to100', 'print_profile_1to100.json'))); P = PROF['profiles'][PROF['active']]
GW, GD = P['groove_width_mm'], P['groove_depth_mm']        # 0.5 x 0.24
HOLE = 1.85     # square peg socket for 1.75 mm filament: FDM holes print ~0.1 small, so this lands near a friction fit
BAR_Y, BAR_Z = 3.0, 4.0                                   # root bar: 3 mm radial x 4 mm thick

class Solid:
    def __init__(s): s.ops = []
    def add(s, *b): s.ops.append((1, b)); return s
    def cut(s, *b): s.ops.append((0, b)); return s
    def mesh(s):
        ax = [sorted({round(v, 4) for _, b in s.ops for v in b[2 * k:2 * k + 2]}) for k in range(3)]
        cx = [(np.array(a[:-1]) + np.array(a[1:])) / 2 for a in ax]
        X, Y, Z = np.meshgrid(*cx, indexing='ij'); occ = np.zeros(X.shape, bool)
        for add, (x0, x1, y0, y1, z0, z1) in s.ops:
            m = (X > x0) & (X < x1) & (Y > y0) & (Y < y1) & (Z > z0) & (Z < z1)
            occ = occ | m if add else occ & ~m
        F = []; A = [np.array(a) for a in ax]
        O = np.pad(occ, 1)
        for d in range(3):
            sl_a = [slice(1, -1)] * 3; sl_b = [slice(1, -1)] * 3
            sl_a[d] = slice(0, -1); sl_b[d] = slice(1, None)
            a = O[tuple(sl_a)]; b = O[tuple(sl_b)]              # cells either side of each face plane index
            for sign, mask in ((1, a & ~b), (-1, ~a & b)):     # +d facing where filled -> empty
                for idx in zip(*np.nonzero(mask)):
                    i = list(idx); c = [None] * 3
                    o = [k for k in range(3) if k != d]
                    p = A[d][i[d]]
                    u0, u1 = A[o[0]][i[o[0]]], A[o[0]][i[o[0]] + 1]; v0, v1 = A[o[1]][i[o[1]]], A[o[1]][i[o[1]] + 1]
                    def P3(u, v):
                        q = [0.0] * 3; q[d] = p; q[o[0]] = u; q[o[1]] = v; return q
                    quad = [P3(u0, v0), P3(u1, v0), P3(u1, v1), P3(u0, v1)]
                    # orientation: (o0 x o1) is +d for d=0 (y,z), d=1 (x,z) gives -y, d=2 (x,y) gives +z
                    right = {0: 1, 1: -1, 2: 1}[d] * sign
                    if right < 0: quad = quad[::-1]
                    F += [(quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])]
        return np.array(F, np.float32), occ, A

def write_stl(path, F, title):
    n = np.cross(F[:, 1] - F[:, 0], F[:, 2] - F[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(F), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); rec['n'] = n; rec['v'] = F
    with open(path, 'wb') as fh: fh.write(title.encode()[:80].ljust(80, b' ')); fh.write(struct.pack('<I', len(F))); fh.write(rec.tobytes())

def checks(F, occ, A):
    vol = float(np.einsum('ij,ij->i', F[:, 0].astype(float), np.cross(F[:, 1].astype(float), F[:, 2].astype(float))).sum() / 6)
    d = [np.diff(a) for a in A]; ref = float((occ * d[0][:, None, None] * d[1][None, :, None] * d[2][None, None, :]).sum())
    from collections import Counter
    k = np.round(F.astype(float) * 1e4).astype(np.int64); kk = lambda p: p[..., 0] * 7919 ** 4 + p[..., 1] * 7919 ** 2 + p[..., 2]
    ed = Counter(map(tuple, np.stack([np.stack([kk(k[:, i]), kk(k[:, (i + 1) % 3])], 1) for i in range(3)], 1).reshape(-1, 2)))
    un = sum(1 for (a, b), c in ed.items() if ed.get((b, a), 0) != c)
    return dict(volume_mm3=round(vol, 2), occupancy_volume_mm3=round(ref, 2), volume_check='PASS' if abs(vol - ref) < 1e-3 * max(ref, 1) else 'FAIL',
                unmatched_edges=un, watertight='PASS' if un == 0 else 'FAIL')

def root_bar(s, L, pegs=(40.0, 150.0)):
    """Bar along x at y in [-BAR_Y, 0], z in [0, BAR_Z]; two square peg sockets drilled in -y from the root face."""
    s.add(10, L - 10, -BAR_Y, 0.4, 0, BAR_Z)
    for px in pegs: s.cut(px - HOLE / 2, px + HOLE / 2, -BAR_Y - 1, -BAR_Y + 2.5, BAR_Z / 2 - HOLE / 2, BAR_Z / 2 + HOLE / 2)
    return s

def channels(s, L, y0, y1, z_top, both=True, z_bot=0.0, pitch=5.0, x0=2.5):
    """Heat-pipe channels: grooves along y (root to tip) every 5 mm in x (0.5 m real), top and bottom faces."""
    for x in np.arange(x0, L, pitch):
        s.cut(x - GW / 2, x + GW / 2, y0, y1, z_top - GD, z_top + 1)
        if both: s.cut(x - GW / 2, x + GW / 2, y0, y1, z_bot - 1, z_bot + GD)
    return s

def pleat_lines(s, L, y_lines, z_top, both=True, z_bot=0.0):
    for y in y_lines:
        s.cut(-1, L + 1, y - GW / 2, y + GW / 2, z_top - GD, z_top + 1)
        if both: s.cut(-1, L + 1, y - GW / 2, y + GW / 2, z_bot - 1, z_bot + GD)
    return s

PARTS = {}
def part(name, qty, what):
    def deco(fn): PARTS[name] = dict(qty=qty, what=what, fn=fn); return fn
    return deco
L_FIN, L_STR = 190.0, 183.0

@part('hotfin_deployed', 4, 'Hot fin, deployed (torch): 190 x 280 x 1.6 mm panel, 13 pleat lines + heat-pipe channels both faces')
def _():
    s = Solid().add(0, L_FIN, 0, 280, 0, 1.6); root_bar(s, L_FIN)
    channels(s, L_FIN, 0.6, 280, 1.6, z_bot=0.0); pleat_lines(s, L_FIN, [20.0 * k for k in range(1, 14)], 1.6, z_bot=0.0)
    return s

@part('hotfin_folded', 4, 'Hot fin, folded (stowed/Metric): 190 x 20 x 6 mm stack, true scale, channels both faces')
def _():
    s = Solid().add(0, L_FIN, 0, 20, 0, 6.0); root_bar(s, L_FIN)
    return channels(s, L_FIN, 0.6, 20, 6.0, z_bot=0.0)

@part('strake_loom', 4, 'Strake, Loom 0 m: 5 mm root fill, flush with the hull (r 4.0 to 4.5)')
def _():
    s = Solid().add(0, L_STR, 0, 5.0, 0, 1.6); return root_bar(s, L_STR, pegs=(40.0, 143.0))

@part('strake_metric', 4, 'Strake, Metric 2 m: 25 mm (5 root + 20), 3 mm accordion block, 4 pleat lines')
def _():
    s = Solid().add(0, L_STR, 0, 25.0, 0, 3.0); root_bar(s, L_STR, pegs=(40.0, 143.0))
    return pleat_lines(s, L_STR, [10.0, 15.0, 20.0], 3.0, z_bot=0.0)

@part('strake_torch', 4, 'Strake, torch 4 m: 45 mm (5 root + 40) x 1.6 mm panel, heat-pipe channels both faces')
def _():
    s = Solid().add(0, L_STR, 0, 45.0, 0, 1.6); root_bar(s, L_STR, pegs=(40.0, 143.0))
    return channels(s, L_STR, 5.0, 45, 1.6, z_bot=0.0)

@part('peg_test', 1, 'Peg fit test: 6 square sockets 1.70-1.95 mm, labelled by notches; plus a 20 mm fin stub with a 1.85 socket')
def _():
    s = Solid().add(0, 60, 0, 12, 0, 6.0)
    for i, h in enumerate((1.70, 1.75, 1.80, 1.85, 1.90, 1.95)):
        cx = 6 + i * 9.6; s.cut(cx - h / 2, cx + h / 2, 6 - h / 2, 6 + h / 2, 1.0, 7)
        for k in range(i + 1): s.cut(cx - 3.5 + k * 1.4, cx - 3.5 + k * 1.4 + 0.7, -1, 1.2, 4.8, 7)   # count notches = size index
    s.add(0, 20, 20, 26, 0, 1.6); s.add(4, 16, 17, 20, 0, 4.0)
    s.cut(10 - 0.925, 10 + 0.925, 16, 19.5, 2 - 0.925, 2 + 0.925)
    return s

def main():
    man = dict(header='ALL bodies. ALL sponsors. 2026-2226.', decision='fin_strake_plugin_1to100_2026_11_13', profile=PROF['active'],
               status='PLACEHOLDER, untested', peg='1.75 mm filament offcut, cut to 5 mm (2.5 in the part + 2.5 in the ship socket)',
               socket_square_mm=HOLE, parts={})
    for name, p in PARTS.items():
        F, occ, A = p['fn']().mesh(); write_stl(os.path.join(OUT, f'{name}.stl'), F, f'Wayfarer 1:100 {name} [{PROF["active"]}]')
        V = F.reshape(-1, 3); man['parts'][name] = dict(qty=p['qty'], what=p['what'], file=f'parts/{name}.stl', triangles=len(F),
            size_mm=[round(float(v), 2) for v in (V.max(0) - V.min(0))], **checks(F, occ, A))
    man['dropped_at_1to100'] = ['folded-stack pleat edges: 14 layers in 6 mm = 0.43 mm pitch, below the 0.5 mm minimum groove']
    man['notes'] = ['Root bar is offset to one face so every part prints flat with no supports; fin-line offset on the ship socket is 0.8-2 mm (80-200 mm real), visually nil.',
                    'Ship-side sockets belong to the whole model and are cut at the end (kT: keep the model whole); their positions are fixed here: pegs at x 40 and 150 mm along each fin from its forward end, 40 and 143 along each strake.']
    json.dump(man, open(os.path.join(HERE, 'parts_manifest.json'), 'w'), indent=1)
    for k, v in man['parts'].items(): print(k, v['qty'], v['size_mm'], v['triangles'], v['volume_check'], v['watertight'])
if __name__ == '__main__': main()
