"""Shuttle B4-S: B4 angular lifting body with a big 1-bar cabin and ONE Venus pod (2.1 m Ti sphere) that becomes the rover.
NON-CANON lab model. ALL bodies. ALL sponsors. 2026-2226.
kT decision shuttle_b4_split_cabin_venus_pod_2026_11_19 ('Yes' to option B; 'Go' to the full build).
Reuses build_v2b (body, fins, windscreen, kit fairing, GLB writer) and variants (B4 double-fold wings, side door, legs).
Frame: x aft from nose, y starboard, z up (GLB y-up as x, z, -y).
States written to viewer/glb/b4s_<state>.glb:
  flight      standard flight: cabin runs the full length (flex bay is cabin), wings folded, no pod
  venus       Venus flight: pod docked to the cabin's aft bulkhead hatch, flex bay holds the pod
  glide       Venus flight, wings out (high double-fold wing)
  landed      on its own legs, doors shut, crew in the pod
  rover_out   side door open (ramp + wing awning), pod out on the ground as a 4-wheel crab-steer rover
Checks in b4s_manifest.json: bay fit (all stowed parts inside r 2.15 m), pod and cabin clearance to the skin,
cabin volumes, door opening vs pod passage."""
import json, os, base64
import numpy as np
import build_v2b as B, variants as VA

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'viewer', 'glb'); os.makedirs(OUT, exist_ok=True)

# ---------- layout (ASSUMPTIONS, kT-approved option B) ----------
CAB_X0, BULK_X, CAB_X1 = 3.9, 8.75, 11.45      # cabin front, aft pressure bulkhead (Venus trips), flex-bay end
INSET = 0.20                                   # cabin wall to aeroshell skin: insulation, frames, TPS backing
POD_R, POD_X, POD_Z = 1.05, 10.20, 0.26        # 2.1 m Ti sphere, 92 bar outside / 1 bar inside
FLOOR_Z = POD_Z - POD_R - 0.03                 # rover rails just under the pod
WHEEL_R, WHEEL_W, WHEEL_X, WHEEL_Y = 0.45, 0.34, (9.25, 11.15), 1.30
DOOR_X = (8.75, 11.70)                         # starboard ramp panel, moved aft to the pod (B4 had 5.9-10.1)
VA.DOOR_LOW_X = DOOR_X

def inner_section(x, inset=INSET):
    """Cabin wall section: the body's 8-point facet ring pulled in by `inset` along each corner's bisector."""
    S = np.array(B.section(x)); n = len(S); out = []
    for i in range(n):
        p, a, b = S[i], S[i - 1], S[(i + 1) % n]
        e1 = (p - a) / np.linalg.norm(p - a); e2 = (b - p) / np.linalg.norm(b - p)
        n1 = np.array([e1[1], -e1[0]]); n2 = np.array([e2[1], -e2[0]])          # outward normals (ring is clockwise in y-z)
        if (n1 @ (p - S.mean(0))) < 0: n1, n2 = -n1, -n2
        bis = n1 + n2; bis /= np.linalg.norm(bis); c = max(bis @ n1, .35)
        out.append(p - inset / c * bis)
    return out

def loft_closed(xs, secfun):
    V, F = [], []; rings = []
    for x in xs: rings.append(len(V)); V += [(x, y, z) for y, z in secfun(x)]
    n = len(secfun(xs[0]))
    for k in range(len(xs) - 1):
        a0, b0 = rings[k], rings[k + 1]
        for i in range(n):
            j = (i + 1) % n; F += [(a0 + i, b0 + i, a0 + j), (a0 + j, b0 + i, b0 + j)]
    for r, flip in ((rings[0], True), (rings[-1], False)):
        c = len(V); V.append(tuple(np.mean([V[r + i] for i in range(n)], 0)))
        for i in range(n):
            j = (i + 1) % n; F.append((c, r + j, r + i) if flip else (c, r + i, r + j))
    return np.array(V, float), np.array(F)

def poly_area(S):
    S = np.array(S); return 0.5 * abs(float(np.dot(S[:, 0], np.roll(S[:, 1], -1)) - np.dot(S[:, 1], np.roll(S[:, 0], -1))))
def cab_vol(x1):
    xs = np.linspace(CAB_X0, x1, 400); return float(np.trapezoid([poly_area(inner_section(x)) for x in xs], xs))

def cabin(x1):
    xs = sorted(set([CAB_X0, x1] + [s for s in B.STATIONS if CAB_X0 < s < x1]))
    return loft_closed(xs, inner_section)

def disc(x, r, z, t=0.06):
    return B.tube((x - t / 2, 0, z), (x + t / 2, 0, z), r, 32)

def pod_parts(at=(0, 0, 0), wheels='stowed'):
    """Pod + its rover chassis in the shuttle frame, offset by `at`. wheels: 'stowed' (folded beside the sphere) or 'down'."""
    o = np.array(at, float); P = {}
    P['pod'] = B.uvsphere(tuple(np.array([POD_X, 0, POD_Z]) + o), POD_R)
    P['pod_window'] = B.tube(tuple(np.array([POD_X - .55, .78, POD_Z + .45]) + o), tuple(np.array([POD_X - .62, .84, POD_Z + .50]) + o), .16, 24)
    P['pod_hatch'] = B.tube(tuple(np.array([(BULK_X + .03) if not any(o) else POD_X - POD_R - .02, 0, POD_Z]) + o), tuple(np.array([POD_X - POD_R + .12, 0, POD_Z]) + o), .42, 32)
    rails = [(WHEEL_X[0] - .25, WHEEL_X[1] + .25)]
    for s, nm in ((1, 'stbd'), (-1, 'port')):
        P[f'pod_rail_{nm}'] = VA.box(rails[0][0] + o[0], rails[0][1] + o[0], s * .62 - .06 + o[1], s * .62 + .06 + o[1], FLOOR_Z - .08 + o[2], FLOOR_Z + o[2])
    for x, a in zip(WHEEL_X, ('fwd', 'aft')):
        P[f'pod_beam_{a}'] = VA.box(x - .07 + o[0], x + .07 + o[0], -.72 + o[1], .72 + o[1], FLOOR_Z - .08 + o[2], FLOOR_Z - .01 + o[2])
        for s, nm in ((1, 'stbd'), (-1, 'port')):
            if wheels == 'down':          # crab-steered for sideways driving: axle along x
                wy, wz = s * WHEEL_Y, FLOOR_Z - .55
                P[f'pod_wheel_{a}_{nm}'] = B.tube((x - WHEEL_W / 2 + o[0], wy + o[1], wz + o[2]), (x + WHEEL_W / 2 + o[0], wy + o[1], wz + o[2]), WHEEL_R, 28)
                P[f'pod_strut_{a}_{nm}'] = VA.box(x - .05 + o[0], x + .05 + o[0], min(s * .72, wy) - .04 + o[1], max(s * .72, wy) + .04 + o[1], wz - .04 + o[2], FLOOR_Z - .06 + o[2])
            else:                         # folded up beside the sphere, axle along y
                wy, wz = s * 1.10, FLOOR_Z + .48
                P[f'pod_wheel_{a}_{nm}'] = B.tube((x + o[0], wy - WHEEL_W / 2 + o[1], wz + o[2]), (x + o[0], wy + WHEEL_W / 2 + o[1], wz + o[2]), WHEEL_R, 28)
                P[f'pod_strut_{a}_{nm}'] = VA.box(x - .05 + o[0], x + .05 + o[0], s * .62 - .05 + o[1], s * .62 + .05 + o[1], FLOOR_Z - .1 + o[2], wz + o[2])
    P['pod_cooler'] = VA.box(POD_X - .45 + o[0], POD_X + .45 + o[0], -.45 + o[1], .45 + o[1], POD_Z + POD_R - .02 + o[2], POD_Z + POD_R + .10 + o[2])
    return P

def shuttle(state):
    P = VA.model('B4', deployed=(state == 'glide'))
    for k in ('sphere_stbd', 'sphere_port', 'tunnel', 'hatch_trunk'): P.pop(k, None)
    venus = state != 'flight'
    P['cabin'] = cabin(BULK_X if venus else CAB_X1)
    P['dorsal_hatch'] = B.tube((5.2, 0, 1.0), (5.2, 0, 1.46), .40, 32)
    if venus:
        P['aft_bulkhead_hatch'] = disc(BULK_X, .45, POD_Z)
        if state == 'rover_out':
            P.update(pod_parts(at=(0, 5.6, (VA.GROUND_Z + WHEEL_R) - (FLOOR_Z - .55)), wheels='down'))
        else:
            P.update(pod_parts())
    if state in ('landed', 'rover_out'): P.update(VA.legs())
    if state == 'rover_out':
        P.pop('door_ramp', None); P.update(VA.upper_panels('B4', 'door')); P.update(VA.ramp(True))
        for nm, (y0, z0, d, L, xs) in {'opening_low': (VA.BC_Y, VA.BC_Z, VA.LOW_D, VA.LOW_L, DOOR_X), 'opening_up': (VA.SH_Y, VA.SH_Z, VA.FLANK_D, VA.FLANK_L, VA.WING['B4']['inner'][0])}.items():
            P[nm] = VA.panel(1, xs, xs, y0, z0, d, L, inset=-0.012)
    else:
        P.update(VA.ramp(False))
    if state != 'glide':   # fins stowed except gliding
        for sd, nm in ((1, 'fin_stbd'), (-1, 'fin_port')): P[nm] = B.fin(sd, state in ('landed', 'rover_out'))
    return VA.orient(P)

CABIN_COL = ([0.17, 0.47, 0.84, 1], .55, 0.0)
B.MAT.update({'cabin': CABIN_COL, 'dorsal_hatch': ([.55, .57, .6, 1], .5, .6), 'aft_bulkhead_hatch': ([.12, .12, .13, 1], .6, .5),
              'pod': ([.70, .40, .30, 1], .4, .8), 'pod_window': ([.55, .85, .95, 1], .1, .2), 'pod_hatch': ([.55, .57, .6, 1], .5, .6),
              'pod_cooler': ([.85, .6, .12, 1], .5, .4)})
for k in ('pod_rail_stbd', 'pod_rail_port', 'pod_beam_fwd', 'pod_beam_aft') + tuple(f'pod_strut_{a}_{n}' for a in ('fwd', 'aft') for n in ('stbd', 'port')):
    B.MAT[k] = ([.42, .45, .5, 1], .5, .7)
for a in ('fwd', 'aft'):
    for n in ('stbd', 'port'): B.MAT[f'pod_wheel_{a}_{n}'] = ([.12, .12, .12, 1], .95, 0)

def skin_clearance(pts):
    """min distance from points (inside) to the body skin, using the dense section outline at each point's x."""
    d = 9.0
    for p in pts:
        yy, zz, _ = B.ring(p[0]); d = min(d, float(np.min(np.hypot(yy - p[1], zz - p[2]))))
    return d

if __name__ == '__main__':
    man = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON lab model', decision='shuttle_b4_split_cabin_venus_pod_2026_11_19', states={})
    for st in ('flight', 'venus', 'glide', 'landed', 'rover_out'):
        P = shuttle(st); size = B.write_glb(P, os.path.join(OUT, f'b4s_{st}.glb')); man['states'][st] = dict(parts=len(P), glb_bytes=size)
    # checks
    Pf, Pv = shuttle('flight'), shuttle('venus')
    stow = [k for k in Pv if not k.startswith(('fin_',))] ; allv = np.vstack([Pv[k][0] for k in stow] + [B.fin(1, False)[0], B.fin(-1, False)[0]])
    rmax = float(np.max(np.hypot(allv[:, 1], allv[:, 2] - B.AXIS_Z)))
    podpts = B.uvsphere((POD_X, 0, POD_Z), POD_R, 64, 32)[0]
    cabpts = np.vstack([Pf['cabin'][0]])
    folded = np.vstack([Pv[k][0] for k in Pv if k.startswith('pod_wheel')])
    man['bay_fit'] = dict(bore_radius_m=B.BORE_R, max_radius_stowed_m=round(rmax, 3), PASS=bool(rmax <= B.BORE_R))
    man['pod'] = dict(od_m=2 * POD_R, centre=[POD_X, 0, POD_Z], volume_m3=round(4 / 3 * np.pi * POD_R ** 3, 2), min_clearance_to_skin_m=round(skin_clearance(podpts), 3),
                      folded_wheels_min_clearance_to_skin_m=round(skin_clearance(folded), 3))
    man['cabin'] = dict(wall_inset_m=INSET, standard_flight_m3=round(cab_vol(CAB_X1), 1), venus_flight_m3=round(cab_vol(BULK_X), 1),
                        x_range_standard=[CAB_X0, CAB_X1], x_range_venus=[CAB_X0, BULK_X], min_clearance_to_skin_m=round(skin_clearance(cabpts), 3))
    rz = np.vstack([Pv[k][0] for k in Pv if k.startswith('pod')])
    man['door'] = dict(ramp_x=list(DOOR_X), pod_and_chassis_x=[round(float(rz[:, 0].min()), 2), round(float(rz[:, 0].max()), 2)],
                       opening_z=[VA.BC_Z, VA.SH_Z], pod_and_chassis_z=[round(float(rz[:, 2].min()), 2), round(float(rz[:, 2].max()), 2)],
                       note='upper opening is the wing (shoulder hinge) swung up as an awning, so the pod top may pass above the shoulder line')
    json.dump(man, open(os.path.join(HERE, 'b4s_manifest.json'), 'w'), indent=1); print(json.dumps(man, indent=1))
