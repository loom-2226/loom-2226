"""Shuttle v2-B variants: B2 angular body, B3 single-fold flank wings,
B4 double-fold flank wings. Wings are the flank skin itself, hinged on the
chine line; stowed flush on the flank (inside the 4.3 m bay envelope),
deployed after entry for subsonic glide and landing. NON-CANON lab model.
ALL bodies. ALL sponsors. 2026-2226."""
import numpy as np
import build_v2b as B

CH_Y, CH_Z, SH_Y, SH_Z = 2.13, 0.20, 1.52, 1.40          # constant-section chine & shoulder
FLANK = np.array([SH_Y - CH_Y, SH_Z - CH_Z]); FLANK_L = float(np.hypot(*FLANK)); FLANK_U = FLANK / FLANK_L

def plate(quad, nrm, t=0.05):
    q = [np.array(p, float) for p in quad]; n = np.array(nrm, float); n /= np.linalg.norm(n)
    return B.hexa([p - t / 2 * n for p in q] + [p + t / 2 * n for p in q])

def panel(side, x_root, x_tip, y0, z0, dirv, length, inset=0.0):
    """Trapezoid: root chord x_root on hinge line, tip chord x_tip at distance length along dirv (y,z)."""
    d = np.array([0, side * dirv[0], dirv[1]]); h = np.array([0, side * y0, z0])
    n = np.cross([1, 0, 0], d) * side
    q = [h + [x_root[0], 0, 0], h + [x_root[1], 0, 0], h + d * length + [x_tip[1], 0, 0], h + d * length + [x_tip[0], 0, 0]]
    q = [p + inset * n for p in q]   # n points inboard here: recess into the flank
    return plate(q, n)

WING = {  # inner panel = flank skin (root x 6.6-11.7), outer panel folds back onto inner
    'B3': dict(inner=((6.6, 11.7), (8.6, 11.7)), outer=None, mass_t=0.8),
    'B4': dict(inner=((6.6, 11.7), (8.6, 11.7)), outer=((8.6, 11.7), (9.8, 11.7), 1.30, 10.0), mass_t=1.6)}

def wings(var, deployed):
    P = {}
    w = WING.get(var)
    if not w: return P
    for side, sn in ((1, 'stbd'), (-1, 'port')):
        if deployed:
            P[f'wing_in_{sn}'] = panel(side, w['inner'][0], w['inner'][1], CH_Y, CH_Z, (1.0, 0.0), FLANK_L)
            if w['outer']:
                dih = np.radians(w['outer'][3]); y1 = CH_Y + FLANK_L
                P[f'wing_out_{sn}'] = panel(side, w['outer'][0], w['outer'][1], y1, CH_Z, (np.cos(dih), np.sin(dih)), w['outer'][2])
        else:  # flush on the flank, recessed by panel thickness(es)
            P[f'wing_in_{sn}'] = panel(side, w['inner'][0], w['inner'][1], CH_Y, CH_Z, FLANK_U, FLANK_L, inset=0.03)
            if w['outer']:
                P[f'wing_out_{sn}'] = panel(side, (w['outer'][0][0], w['outer'][0][1]), (w['outer'][0][0] + 0.4, w['outer'][0][1]),
                                            CH_Y, CH_Z, FLANK_U, w['outer'][2], inset=0.09)
    return P

def model(var, deployed=True):
    P = B.parts()
    if not deployed:
        for sd, nm in ((1, 'fin_stbd'), (-1, 'fin_port')): P[nm] = B.fin(sd, False)
    P.update(wings(var, deployed))
    for k in [k for k in P if k.startswith('wing')]:
        V, F = P[k]; c = V.mean(0); a, b, cc = V[F[:, 0]] - c, V[F[:, 1]] - c, V[F[:, 2]] - c
        if np.einsum('ij,ij->i', a, np.cross(b, cc)).sum() < 0: P[k] = (V, F[:, ::-1])
    return P

def wing_geom(var):
    """Added planform area (m2, both sides, deployed, horizontal projection) and span (m)."""
    w = WING.get(var)
    if not w: return 0.0, 2 * CH_Y
    ci, ct = w['inner'][0][1] - w['inner'][0][0], w['inner'][1][1] - w['inner'][1][0]
    A = 2 * (ci + ct) / 2 * FLANK_L; span = 2 * (CH_Y + FLANK_L)
    if w['outer']:
        co, cto = w['outer'][0][1] - w['outer'][0][0], w['outer'][1][1] - w['outer'][1][0]
        L = w['outer'][2] * np.cos(np.radians(w['outer'][3]))
        A += 2 * (co + cto) / 2 * L; span += 2 * L
    return float(A), float(span)

for k in ('wing_in_stbd', 'wing_in_port', 'wing_out_stbd', 'wing_out_port'):
    B.MAT[k] = ([0.80, 0.81, 0.79, 1], 0.6, 0.0)

if __name__ == '__main__':
    for v in ('B2', 'B3', 'B4'):
        A, s = wing_geom(v)
        stow = model(v, False); allv = np.vstack([stow[k][0] for k in stow if k not in ('sphere_stbd', 'sphere_port', 'tunnel', 'hatch_trunk')])
        r = float(np.max(np.hypot(allv[:, 1], allv[:, 2])))
        print(v, 'wing area', round(A, 1), 'span', round(s, 2), 'stowed rmax', round(r, 3))

# ---------------- twin-sphere belly rover (concept C, rebuilt for v2) ----------------
ROVER_PARTS = ('sphere_stbd', 'sphere_port', 'tunnel', 'rover_floor', 'rover_rail_stbd', 'rover_rail_port',
               'rover_beam_fwd', 'rover_beam_aft') + tuple(f'wheel_{a}_{s}' for a in ('fwd', 'aft') for s in ('stbd', 'port')) \
               + tuple(f'strut_{a}_{s}' for a in ('fwd', 'aft') for s in ('stbd', 'port'))
WHEEL_R, WHEEL_W, WHEEL_X, WHEEL_Y = 0.45, 0.36, (6.0, 9.6), 1.55
GROUND_Z = -1.92                     # wheel bottoms with gear down, shuttle frame
def box(x0, x1, y0, y1, z0, z1):
    return B.hexa([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
def rover(gear_down):
    P = {}
    P['rover_floor'] = box(5.6, 10.0, -1.70, 1.70, -0.965, -0.905)             # belly TPS panel = rover floor (seam 5 mm proud)
    for s, n in ((1, 'stbd'), (-1, 'port')):
        P[f'rover_rail_{n}'] = box(5.6, 10.0, s * WHEEL_Y - 0.07, s * WHEEL_Y + 0.07, -0.90, -0.74)
    P['rover_beam_fwd'] = box(7.1, 7.25, -1.55, 1.55, -0.90, -0.80); P['rover_beam_aft'] = box(8.35, 8.5, -1.55, 1.55, -0.90, -0.80)
    zc = GROUND_Z + WHEEL_R if gear_down else -0.90 + WHEEL_R + 0.0      # stowed: bottom flush with floor top
    for x, a in zip(WHEEL_X, ('fwd', 'aft')):
        for s, n in ((1, 'stbd'), (-1, 'port')):
            yo = s * (WHEEL_Y + 0.07 + WHEEL_W / 2 + 0.02)
            if not gear_down: yo = s * (WHEEL_Y - 0.07 - WHEEL_W / 2 - 0.02)      # stowed inboard of the rail
            P[f'wheel_{a}_{n}'] = B.tube((x, yo - WHEEL_W / 2, zc), (x, yo + WHEEL_W / 2, zc), WHEEL_R, 28)
            P[f'strut_{a}_{n}'] = box(x - 0.06, x + 0.06, yo - 0.05, yo + 0.05, zc, -0.74) if gear_down else box(x - 0.05, x + 0.05, s * WHEEL_Y - 0.05, s * WHEEL_Y + 0.05, -0.80, -0.74)
    return P
def legs(top_z):
    P = {}
    for x, y, n in ((3.6, 1.0, 'nose_stbd'), (3.6, -1.0, 'nose_port'), (11.6, 1.5, 'aft_stbd'), (11.6, -1.5, 'aft_port')):
        P[f'leg_{n}'] = box(x - 0.08, x + 0.08, y - 0.08, y + 0.08, GROUND_Z + 0.08, top_z)
        P[f'pad_{n}'] = box(x - 0.3, x + 0.3, y - 0.3, y + 0.3, GROUND_Z, GROUND_Z + 0.08)
    return P
def shifted(P, d):
    return {k: (V + np.array(d, float), F) for k, (V, F) in P.items()}
def model_rover(var, state):
    """state: 'flight' (rover stowed, gear up), 'landed' (gear down = rover wheels), 'out' (shuttle jacked up, rover driven aft)."""
    P = model(var, deployed=False)                 # wings and fins folded in bay, entry and ground ops
    P.update(rover(gear_down=state != 'flight'))
    if state == 'out':
        rov = {k: P.pop(k) for k in list(P) if k in ROVER_PARTS}
        lift = (0.10 + 0.95 + 0.15) - (-0.95)                       # belly clears sphere tops by 0.15 m
        P = shifted(P, (0, 0, lift))
        P['bay_opening'] = box(5.6, 10.0, -1.70, 1.70, -0.97 + lift, -0.955 + lift)
        P.update(legs(-0.95 + lift)); P.update(shifted(rov, (9.5, 0, 0)))
    return P
for k in ('rover_floor', 'bay_opening'): B.MAT[k] = ([0.16, 0.16, 0.17, 1], 0.9, 0.0)
B.MAT['bay_opening'] = ([0.05, 0.05, 0.06, 1], 1.0, 0.0)
for k in ROVER_PARTS:
    if k.startswith(('rover_rail', 'rover_beam', 'strut')): B.MAT[k] = ([0.42, 0.45, 0.50, 1], 0.5, 0.7)
    if k.startswith('wheel'): B.MAT[k] = ([0.12, 0.12, 0.12, 1], 0.95, 0.0)
for n in ('nose_stbd', 'nose_port', 'aft_stbd', 'aft_port'):
    B.MAT[f'leg_{n}'] = ([0.42, 0.45, 0.50, 1], 0.5, 0.7); B.MAT[f'pad_{n}'] = ([0.30, 0.31, 0.33, 1], 0.8, 0.3)
