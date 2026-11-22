"""Shuttle v2 angular family with SIDE rover egress. NON-CANON lab model.
ALL bodies. ALL sponsors. 2026-2226.

B2  angular body; upper flank panels are gull-wing doors only.
B3  upper flank panels are wings: hinged on the SHOULDER, stowed flush on the
    flank, deployed horizontal (high wing). On the ground the starboard panel
    swings up as the upper half of the side door and becomes an awning.
B4  as B3 plus an outer panel folded back onto the inner one (double fold).
Side door (all variants, starboard): lower flank panel hinged on the belly
corner folds down as a ramp; upper flank panel (wing) swings up. The twin-sphere
rover crab-steers out sideways. kT 2026-11-15: "Rather go out the side".
"""
import numpy as np
import build_v2b as B

CH_Y, CH_Z, SH_Y, SH_Z, BC_Y, BC_Z = 2.13, 0.20, 1.52, 1.40, 1.85, -0.95   # constant section
FLANK = np.array([CH_Y - SH_Y, CH_Z - SH_Z]); FLANK_L = float(np.hypot(*FLANK)); FLANK_D = FLANK / FLANK_L   # shoulder -> chine
LOW = np.array([CH_Y - BC_Y, CH_Z - BC_Z]); LOW_L = float(np.hypot(*LOW)); LOW_D = LOW / LOW_L               # belly corner -> chine
GROUND_Z = -1.55                                     # shuttle on its own legs: belly 0.6 m above ground

def box(x0, x1, y0, y1, z0, z1):
    return B.hexa([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])

def plate(quad, nrm, t=0.05):
    q = [np.array(p, float) for p in quad]; n = np.array(nrm, float); n /= np.linalg.norm(n)
    return B.hexa([p - t / 2 * n for p in q] + [p + t / 2 * n for p in q])

def panel(side, x_root, x_tip, y0, z0, dirv, length, inset=0.0):
    """Trapezoid: root chord on the hinge line at (y0,z0), tip chord at distance `length` along dirv=(dy,dz)."""
    d = np.array([0, side * dirv[0], dirv[1]]); h = np.array([0, side * y0, z0])
    n = np.cross([1, 0, 0], d); n = n / np.linalg.norm(n)
    if n @ np.array([0, side, 1]) < 0: n = -n                      # n points outboard/up
    q = [h + [x_root[0], 0, 0], h + [x_root[1], 0, 0], h + d * length + [x_tip[1], 0, 0], h + d * length + [x_tip[0], 0, 0]]
    q = [p - inset * n for p in q]                                  # recess inboard
    return plate(q, n)

WING = {   # inner = upper flank skin hinged at the shoulder; outer folds back onto inner
    'B2': dict(inner=((6.3, 11.7), (6.3, 11.7)), outer=None, mass_t=0.0, aero=False),
    'B3': dict(inner=((6.3, 11.7), (8.3, 11.7)), outer=None, mass_t=0.8, aero=True),
    'B4': dict(inner=((6.3, 11.7), (8.3, 11.7)), outer=((8.3, 11.7), (9.5, 11.7), 1.30, 10.0), mass_t=1.6, aero=True)}
DOOR_LOW_X = (5.9, 10.1)                                            # starboard ramp panel

def upper_panels(var, mode):
    """mode: 'stowed' (flush on flank), 'wing' (both horizontal), 'door' (stbd up as awning, port stowed)."""
    P = {}; w = WING[var]
    for side, sn in ((1, 'stbd'), (-1, 'port')):
        m = mode if not (mode == 'door' and side == -1) else 'stowed'
        if m == 'stowed':
            P[f'wing_in_{sn}'] = panel(side, w['inner'][0], w['inner'][1], SH_Y, SH_Z, FLANK_D, FLANK_L, inset=0.03)
            if w['outer']:
                o = w['outer']
                P[f'wing_out_{sn}'] = panel(side, o[0], (o[0][0] + 0.4, o[0][1]), SH_Y, SH_Z, FLANK_D, o[2], inset=0.09)
        else:
            P[f'wing_in_{sn}'] = panel(side, w['inner'][0], w['inner'][1], SH_Y, SH_Z, (1.0, 0.0), FLANK_L)
            if w['outer']:
                o = w['outer']; dih = np.radians(o[3])
                P[f'wing_out_{sn}'] = panel(side, o[0], o[1], SH_Y + FLANK_L, SH_Z, (np.cos(dih), np.sin(dih)), o[2])
    return P

def ramp(open_):
    if not open_:
        return {'door_ramp': panel(1, DOOR_LOW_X, DOOR_LOW_X, BC_Y, BC_Z, LOW_D, LOW_L, inset=0.03)}
    drop = BC_Z - GROUND_Z; ang = np.arcsin(min(drop / LOW_L, 1.0))
    return {'door_ramp_open': panel(1, DOOR_LOW_X, DOOR_LOW_X, BC_Y, BC_Z, (np.cos(ang), -np.sin(ang)), LOW_L)}

def model(var, deployed=True):
    P = B.parts()
    if not deployed:
        for sd, nm in ((1, 'fin_stbd'), (-1, 'fin_port')): P[nm] = B.fin(sd, False)
    P.update(upper_panels(var, 'wing' if (deployed and WING[var]['aero']) else 'stowed'))
    P.update(ramp(False))
    return P

def wing_geom(var):
    """Planform added beyond the body edge (y > CH_Y), both sides, deployed; span (m)."""
    w = WING[var]
    if not w['aero']: return 0.0, 2 * CH_Y
    cr = w['inner'][0][1] - w['inner'][0][0]; ct = w['inner'][1][1] - w['inner'][1][0]
    f0 = (CH_Y - SH_Y) / FLANK_L; c0 = cr + (ct - cr) * f0
    A = 2 * (c0 + ct) / 2 * (1 - f0) * FLANK_L; span = 2 * (SH_Y + FLANK_L)
    if w['outer']:
        o = w['outer']; co, cto = o[0][1] - o[0][0], o[1][1] - o[1][0]; L = o[2] * np.cos(np.radians(o[3]))
        A += 2 * (co + cto) / 2 * L; span += 2 * L
    return float(A), float(span)

# ---------------- twin-sphere rover, side egress ----------------
ROVER_PARTS = ('sphere_stbd', 'sphere_port', 'tunnel', 'rover_floor', 'rover_rail_stbd', 'rover_rail_port',
               'rover_beam_fwd', 'rover_beam_aft') + tuple(f'wheel_{a}_{s}' for a in ('fwd', 'aft') for s in ('stbd', 'port')) \
               + tuple(f'strut_{a}_{s}' for a in ('fwd', 'aft') for s in ('stbd', 'port'))
WHEEL_R, WHEEL_W, WHEEL_X, WHEEL_Y = 0.45, 0.36, (6.4, 9.6), 1.55
def rover(outside):
    """Rover parts in the shuttle frame. outside=True: wheels down and crabbed 90 deg (axis fore-aft)."""
    BP = B.parts(); P = {k: BP[k] for k in ('sphere_stbd', 'sphere_port', 'tunnel')}
    P['rover_floor'] = box(5.95, 10.05, -1.62, 1.62, -0.90, -0.86)
    for s, n in ((1, 'stbd'), (-1, 'port')):
        P[f'rover_rail_{n}'] = box(5.95, 10.05, s * WHEEL_Y - 0.07, s * WHEEL_Y + 0.07, -0.86, -0.74)
    P['rover_beam_fwd'] = box(7.1, 7.25, -1.55, 1.55, -0.86, -0.80); P['rover_beam_aft'] = box(8.35, 8.5, -1.55, 1.55, -0.86, -0.80)
    for x, a in zip(WHEEL_X, ('fwd', 'aft')):
        for s, n in ((1, 'stbd'), (-1, 'port')):
            if outside:     # wheel centre at rail-bottom height, outboard, crab-steered (axis along x)
                y, zc = s * (WHEEL_Y + 0.07 + WHEEL_R * 0 + 0.30), -0.86
                P[f'wheel_{a}_{n}'] = B.tube((x - WHEEL_W / 2, y, zc), (x + WHEEL_W / 2, y, zc), WHEEL_R, 28)
                P[f'strut_{a}_{n}'] = box(x - 0.05, x + 0.05, min(s * WHEEL_Y, y) - 0.04, max(s * WHEEL_Y, y) + 0.04, zc - 0.05, zc + 0.05)
            else:           # stowed inboard of the rail, bottom on the floor
                y, zc = s * (WHEEL_Y - 0.07 - WHEEL_W / 2 - 0.02), -0.86 + WHEEL_R
                P[f'wheel_{a}_{n}'] = B.tube((x, y - WHEEL_W / 2, zc), (x, y + WHEEL_W / 2, zc), WHEEL_R, 28)
                P[f'strut_{a}_{n}'] = box(x - 0.05, x + 0.05, s * WHEEL_Y - 0.05, s * WHEEL_Y + 0.05, -0.80, -0.74)
    return P
def legs():
    P = {}
    for x, y, n in ((3.6, 0.9, 'nose_stbd'), (3.6, -0.9, 'nose_port'), (11.6, 1.5, 'aft_stbd'), (11.6, -1.5, 'aft_port')):
        P[f'leg_{n}'] = box(x - 0.08, x + 0.08, y - 0.08, y + 0.08, GROUND_Z + 0.06, -0.95 if x > 5 else -0.80)
        P[f'pad_{n}'] = box(x - 0.25, x + 0.25, y - 0.25, y + 0.25, GROUND_Z, GROUND_Z + 0.06)
    return P
def shifted(P, d):
    return {k: (V + np.array(d, float), F) for k, (V, F) in P.items()}
ROVER_OUT_Y = 5.4
def model_rover(var, state):
    """state: 'flight' (all stowed), 'landed' (on own legs, doors shut), 'out' (side door open, rover crabbed out)."""
    P = model(var, deployed=False)
    if state == 'flight':
        P.update(rover(False)); return P
    P.update(legs())
    if state == 'landed':
        P.update(rover(False)); return P
    for k in ROVER_PARTS: P.pop(k, None)
    P.pop('door_ramp', None); P.update(upper_panels(var, 'door')); P.update(ramp(True))
    # opening shown as dark plates just outside the starboard flank
    for nm, (y0, z0, d, L, xs) in {'opening_low': (BC_Y, BC_Z, LOW_D, LOW_L, DOOR_LOW_X), 'opening_up': (SH_Y, SH_Z, FLANK_D, FLANK_L, WING[var]['inner'][0])}.items():
        P[nm] = panel(1, xs, xs, y0, z0, d, L, inset=-0.012)
    R = rover(True); dz = (GROUND_Z + WHEEL_R) - (-0.86)          # wheel bottoms on the ground
    P.update(shifted(R, (0, ROVER_OUT_Y, dz)))
    return P

for k in ('wing_in_stbd', 'wing_in_port', 'wing_out_stbd', 'wing_out_port'): B.MAT[k] = ([0.80, 0.81, 0.79, 1], 0.6, 0.0)
B.MAT['door_ramp'] = ([0.16, 0.16, 0.17, 1], 0.9, 0.0)
B.MAT['door_ramp_open'] = ([0.52, 0.54, 0.57, 1], 0.6, 0.5)                 # inner (deck) face up
B.MAT['rover_floor'] = ([0.30, 0.31, 0.33, 1], 0.8, 0.2)
B.MAT['opening_low'] = B.MAT['opening_up'] = ([0.04, 0.04, 0.05, 1], 1.0, 0.0)
for k in ROVER_PARTS:
    if k.startswith(('rover_rail', 'rover_beam', 'strut')): B.MAT[k] = ([0.42, 0.45, 0.50, 1], 0.5, 0.7)
    if k.startswith('wheel'): B.MAT[k] = ([0.12, 0.12, 0.12, 1], 0.95, 0.0)
for n in ('nose_stbd', 'nose_port', 'aft_stbd', 'aft_port'):
    B.MAT[f'leg_{n}'] = ([0.42, 0.45, 0.50, 1], 0.5, 0.7); B.MAT[f'pad_{n}'] = ([0.30, 0.31, 0.33, 1], 0.8, 0.3)

def orient(P):
    for k in list(P):
        V, F = P[k]; c = V.mean(0); a, b, cc = V[F[:, 0]] - c, V[F[:, 1]] - c, V[F[:, 2]] - c
        if k not in ('hull', 'belly_tps', 'glazing') and np.einsum('ij,ij->i', a, np.cross(b, cc)).sum() < 0: P[k] = (V, F[:, ::-1])
    return P
_model, _model_rover = model, model_rover
model = lambda var, deployed=True: orient(_model(var, deployed))
model_rover = lambda var, state: orient(_model_rover(var, state))

if __name__ == '__main__':
    for v in ('B2', 'B3', 'B4'):
        A, s = wing_geom(v); P = model_rover(v, 'flight')
        skip = ('sphere_stbd', 'sphere_port', 'tunnel', 'hatch_trunk')
        allv = np.vstack([P[k][0] for k in P if k not in skip])
        print(v, 'added area', round(A, 1), 'span', round(s, 2), 'bay rmax', round(float(np.max(np.hypot(allv[:, 1], allv[:, 2]))), 3))
    P = model_rover('B3', 'out')
    up = P['wing_in_stbd'][0]; r = np.vstack([P[k][0] for k in ROVER_PARTS])
    print('awning underside z', up[:, 2].min().round(2), 'rover top z', r[:, 2].max().round(2), 'rover y', r[:, 1].min().round(2), r[:, 1].max().round(2),
          'ramp end y', P['door_ramp_open'][0][:, 1].max().round(2), 'rover bottom', r[:, 2].min().round(2))
    # rover passage: stowed rover cross-section must clear the opening z band (belly corner .. shoulder)
    R = rover(False); rr = np.vstack([R[k][0] for k in R] + [B.parts()[k][0] for k in ('sphere_stbd', 'sphere_port')])
    print('rover stowed z band', rr[:, 2].min().round(2), rr[:, 2].max().round(2), 'opening', BC_Z, SH_Z, ' x band', rr[:, 0].min().round(2), rr[:, 0].max().round(2))
