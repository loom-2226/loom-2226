"""WALTER R3 — machine-first utility quadruped, resting on belly skids.
Model space (mm, before global scale): x forward, y left, z up, deck z = 0.
"""
import numpy as np
import sdf
from sdf import (loc, rotm, box, sphere, capsule, cyl, box2d, smin, smax, carve,
                 active, full, frame_from_axis)

MATS = ['hull', 'struct', 'joint', 'pad', 'glass', 'accent', 'repl']


def beam(P, a, b, w, hgt, r, side=(0, 1, 0)):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ax = b - a; L = np.linalg.norm(ax); ax /= L
    yv = np.asarray(side, float); yv = yv - ax * (yv @ ax); yv /= np.linalg.norm(yv)
    zv = np.cross(ax, yv)
    return box(loc(P, (a + b) / 2, np.stack([ax, yv, zv], 1)), (L / 2, w, hgt), r)


def ycyl(P, c, r, h, rr=0.35):
    return cyl(loc(P, c, frame_from_axis((0, 1, 0))), r, h, rr)


def xcyl(P, c, r, h, rr=0.35):
    return cyl(loc(P, c, frame_from_axis((1, 0, 0))), r, h, rr)


def cbox(q, half, ch, r=0.6):
    """Box with chamfered long (x-direction) edges."""
    hx, hy, hz = half
    d = box(q, half, r)
    cham = (np.abs(q[:, 1]) + np.abs(q[:, 2]) - (hy + hz - ch)) / np.sqrt(2)
    return np.maximum(d, cham)


# ------------------------------------------------------------------ chassis
BODY_TOP = 20.5


def chassis(P):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    q = loc(P, (34, 0, 11.6))
    d = cbox(q, (26.5, 11.8, 9.0), 3.2, 0.8)
    # front prow: lower front edge chamfer (nav sensor bay faces forward-down)
    d = np.maximum(d, ((x - 60.5) + (5.5 - z)) / np.sqrt(2) - 0.0)
    # rear lower chamfer
    d = np.maximum(d, ((7.5 - x) + (5.0 - z)) / np.sqrt(2))
    # belly skids
    for s in (1, -1):
        d = np.minimum(d, box(loc(P, (34, s * 7.0, 1.6)), (21, 2.6, 1.8), 0.6))
    # bolted flank panels: shallow raised plates + seam + fasteners
    for s in (1, -1):
        for cx, hx in ((22.5, 9.0), (42.5, 8.5)):
            plate = box(loc(P, (cx, s * 11.9, 11.8)), (hx, 0.45, 5.2), 0.3)
            d = np.minimum(d, plate)
            for fx in (-1, 1):
                for fz in (-1, 1):
                    fq = loc(P, (cx + fx * (hx - 1.2), s * 12.4, 11.8 + fz * 4.0), frame_from_axis((0, 1, 0)))
                    d = carve(d, cyl(fq, 0.38, 3), 0.3)
    # longitudinal seam between upper deck and flank
    for s in (1, -1):
        d = carve(d, np.maximum(np.abs(z - 17.6) - 0.16, -(s * y - 6)), 0.35)
    # front nav-sensor window frame (recess) on the prow face
    fw = loc(P, (60.0, 0, 9.2), rotm(pitch=-45) )
    d = carve(d, box(fw, (0.6, 6.5, 1.9), 0.4), 0.7)
    # top deck access panel seam
    d = carve(d, np.maximum(np.abs(box2d(np.stack([x - 30, y], -1), (17, 5.8))) - 0.16, -(z - 19)), 0.3)
    return d


def nav_glass(P):
    fw = loc(P, (60.05, 0, 9.2), rotm(pitch=-45))
    g = box(fw, (0.35, 6.0, 1.5), 0.3)
    # side cameras
    for s in (1, -1):
        g = np.minimum(g, cyl(loc(P, (55.5, s * 11.85, 15.3), frame_from_axis((0, s, 0))), 0.9, 0.35, 0.2))
    return g


def rails(P):
    if not active((30, 0, 22), 30):
        return full(P)
    d = full(P)
    for s in (1, -1):
        d = np.minimum(d, capsule(P, (11.5, s * 9.6, 23.0), (36.5, s * 9.6, 23.0), 0.95))
        for px in (12.0, 24.0, 36.0):
            d = np.minimum(d, box(loc(P, (px, s * 9.6, 21.4)), (0.9, 0.9, 1.9), 0.3))
    # rear transverse drag handle
    d = np.minimum(d, capsule(P, (13.0, -5.5, 23.3), (13.0, 5.5, 23.3), 1.0))
    for s in (1, -1):
        d = np.minimum(d, box(loc(P, (13.0, s * 5.5, 21.5)), (0.9, 0.9, 2.0), 0.3))
    return d


# ------------------------------------------------------------------ arm (stowed along the spine)
ARM_Z = 23.2
SH = np.array([49.0, -3.4, ARM_Z])
EL = np.array([16.5, 0.0, ARM_Z])
WR = np.array([41.0, 3.4, ARM_Z])


def arm(P):
    names = ('struct', 'joint', 'glass', 'pad')
    if not active((33, 0, 23), 22):
        return {k: full(P) for k in names}
    turret = cyl(loc(P, (49.0, 0, BODY_TOP + 0.6)), 4.6, 1.1, 0.35)
    sh = ycyl(P, SH + (0, 0.3, 0), 3.3, 2.4)
    pedestal = box(loc(P, (49.0, -1.6, 21.9)), (2.6, 3.6, 1.6), 0.5)
    upper = beam(P, SH + (0, 0, 0), (EL[0], -3.4, ARM_Z), 1.75, 1.75, 0.6)
    elbow = ycyl(P, EL, 2.7, 5.1)
    fore = beam(P, (EL[0], 3.4, ARM_Z), WR, 1.5, 1.5, 0.55)
    wrist = xcyl(P, WR + (1.6, 0, 0), 2.1, 1.6)
    palm = box(loc(P, WR + (4.6, 0, 0)), (1.6, 2.0, 1.8), 0.5)
    fingers = full(P)
    for s in (1, -1):
        fingers = np.minimum(fingers, beam(P, WR + (5.8, s * 1.2, 0), WR + (10.2, s * 1.0, -0.4), 0.55, 1.2, 0.3))
        fingers = np.minimum(fingers, beam(P, WR + (9.6, s * 1.0, -0.4), WR + (10.6, s * 0.35, -0.6), 0.5, 1.0, 0.25))
    cam = cyl(loc(P, WR + (5.1, 0, 1.75)), 0.75, 0.3, 0.15)          # wrist camera on top of palm
    leds = np.minimum(cyl(loc(P, WR + (4.0, 1.2, 1.75)), 0.35, 0.25, 0.1),
                      cyl(loc(P, WR + (4.0, -1.2, 1.75)), 0.35, 0.25, 0.1))
    # stow cradle under the gripper
    cradle = box(loc(P, WR + (6.5, 0, -2.4)), (3.2, 2.4, 1.0), 0.4)
    out = {'struct': np.minimum(np.minimum(upper, fore), np.minimum(np.minimum(palm, fingers), pedestal)),
           'joint': np.minimum(np.minimum(np.minimum(turret, sh), elbow), wrist),
           'glass': np.minimum(cam, leds),
           'pad': cradle}
    return out


# ------------------------------------------------------------------ sensor head on 3-axis gimbal
MAST_BASE = np.array([57.0, 0, BODY_TOP])
PAN, TILT, ROLL = 30.0, 9.0, 11.0
R_PAN = rotm(yaw=PAN)
TILT_C = MAST_BASE + R_PAN @ np.array([0.8, 0, 11.5])
R_HEAD = R_PAN @ rotm(pitch=TILT) @ rotm(roll=ROLL)


def head(P):
    names = ('hull', 'struct', 'joint', 'glass')
    if not active(TILT_C + np.array([4, 0, 0]), 20):
        return {k: full(P) for k in names}
    qp = loc(P, MAST_BASE, R_PAN)
    pan = cyl(loc(qp, (0, 0, 1.0)), 4.0, 1.0, 0.35)
    mast = beam(qp, (0, 0, 1.4), (0.8, 0, 10.6), 2.1, 2.4, 0.7)
    yoke = box(loc(qp, (0.6, 0, 10.2)), (1.6, 4.6, 0.9), 0.35)
    q = loc(P, TILT_C, R_HEAD) / 1.2
    tilt = cyl(loc(q, (0, 0, 0), frame_from_axis((0, 1, 0))), 1.8, 4.6, 0.3)
    roll = cyl(loc(q, (-1.2, 0, 0.6), frame_from_axis((1, 0, 0))), 2.1, 1.0, 0.3)
    shell = cbox(loc(q, (4.2, 0, 1.6)), (6.0, 5.6, 3.3), 1.6, 0.5)
    shell = np.minimum(shell, box(loc(q, (10.0, 0, 4.6)), (1.2, 5.3, 0.4), 0.25))   # sun visor
    shell = carve(shell, box(loc(q, (10.3, 0, 1.6)), (1.0, 4.6, 1.8), 0.4), 0.7)    # window recess
    glass = np.minimum(cyl(loc(q, (9.9, 2.9, 1.7), frame_from_axis((1, 0, 0))), 1.05, 0.5, 0.2),
                       cyl(loc(q, (9.9, -2.9, 1.7), frame_from_axis((1, 0, 0))), 1.05, 0.5, 0.2))
    glass = np.minimum(glass, box(loc(q, (9.8, 0, 1.6)), (0.45, 1.3, 1.25), 0.35))
    return {'hull': shell * 1.2, 'struct': np.minimum(mast, yoke), 'joint': np.minimum(np.minimum(pan, tilt * 1.2), roll * 1.2), 'glass': glass * 1.2}


# ------------------------------------------------------------------ docked tail: tether fairlead boom
TAIL_BASE = np.array([9.0, 0, 19.2])
TAIL_UP = 48.0


def tail(P):
    names = ('struct', 'joint', 'glass', 'accent')
    if not active(TAIL_BASE, 13):
        return {k: full(P) for k in names}
    R = rotm(pitch=180 - TAIL_UP)   # points backward and up
    tip = TAIL_BASE + R @ np.array([8.0, 0, 0])
    base = ycyl(P, TAIL_BASE, 3.0, 2.9)
    boom = beam(P, TAIL_BASE, tip, 1.9, 2.1, 0.7)
    ax = (tip - TAIL_BASE) / np.linalg.norm(tip - TAIL_BASE)
    fq = loc(P, tip, frame_from_axis(ax))
    rr = np.sqrt(fq[:, 0] ** 2 + fq[:, 1] ** 2)
    fair = np.maximum(np.abs(rr - 1.5) - 0.65, np.abs(fq[:, 2]) - 0.8)          # fairlead ring
    rearcam = cyl(loc(P, tip + R @ np.array([-1.4, 0, 2.15]), R), 0.6, 0.3, 0.1)
    lamp = sphere(loc(P, tip + R @ np.array([-3.2, 0, 2.0])), 0.5)
    return {'struct': boom, 'joint': np.minimum(base, fair), 'glass': rearcam, 'accent': lamp}


# ------------------------------------------------------------------ legs: hip-driven knees, gripper feet
def leg(P, H, K, A, F, s, replacement=False):
    names = ('struct', 'joint', 'pad', 'repl')
    H = np.asarray(H, float); K = np.asarray(K, float); A = np.asarray(A, float); F = np.asarray(F, float)
    if not active((H + F) / 2, 30):
        return {k: full(P) for k in names}
    sv = (0, s, 0)
    aa = xcyl(P, H + (0, -s * 3.6, 0), 3.8, 3.4)                     # abduction stage on body side
    stack = ycyl(P, H, 5.0, 2.9, 0.5)                                 # hip pitch + knee motor stack
    cap = ycyl(P, H + (0, s * 3.0, 0), 3.2, 0.5, 0.25)
    thigh = beam(P, H + (0, s * 0.4, 0), K, 2.0, 2.6, 0.7, sv)
    # pushrod: hip crank -> knee crank (outboard of the thigh)
    crank_h = H + (2.4, s * 2.6, -1.4)
    crank_k = K + (1.9, s * 2.6, 1.1)
    rod = capsule(P, crank_h, crank_k, 0.62)
    rod_ends = np.minimum(ycyl(P, crank_h, 1.0, 0.7, 0.2), ycyl(P, crank_k, 1.0, 0.7, 0.2))
    knee = ycyl(P, K + (0, s * 0.6, 0), 2.6, 2.6)
    kcap = box(loc(P, K + (-0.8, s * 0.3, -3.4)), (2.0, 2.0, 1.4), 0.5)  # knee wear pad (rest contact)
    shank = beam(P, K, A, 1.6, 1.9, 0.6, sv)
    if replacement:
        shank = capsule(P, K + (A - K) * 0.12, A - (A - K) * 0.06, 1.85)
    ankle = np.minimum(ycyl(P, A, 2.1, 1.9), xcyl(P, A + (1.9, 0, -0.3), 1.7, 1.0))
    # gripper foot: sole block + two latching jaws (closed, folded flat) = "toes"
    fq = loc(P, F)
    sole_body = box(loc(fq, (0, 0, 0.6)), (5.2, 4.2, 1.6), 0.9)
    jaws = full(P)
    for t in (1, -1):
        jaws = np.minimum(jaws, beam(P, F + (-3.4, t * 2.05, 2.4), F + (3.2, t * 2.05, 2.4), 1.6, 1.15, 0.55))
        jaws = np.minimum(jaws, beam(P, F + (3.0, t * 2.05, 2.5), F + (5.6, t * 2.0, 0.9), 1.55, 1.05, 0.5))
    jaw_gap = box(loc(fq, (1.0, 0, 2.6)), (5.5, 0.32, 2.0), 0.0)
    jaws = np.maximum(jaws, -jaw_gap)
    jaw_hinge = ycyl(P, F + (-3.6, 0, 2.4), 1.4, 3.7, 0.3)
    strut = beam(P, A, F + (-3.2, 0, 2.8), 1.3, 1.2, 0.5, sv)
    sole = box(loc(fq, (0, 0, -0.65)), (5.5, 4.5, 0.75), 0.5)
    sole = carve(sole, np.abs(fq[:, 1]) - 0.2, 0.3)
    st = np.minimum(np.minimum(thigh, np.minimum(sole_body, jaws)), np.minimum(strut, rod))
    out = {'struct': st if replacement else np.minimum(st, shank),
           'joint': np.minimum(np.minimum(np.minimum(aa, stack), np.minimum(cap, knee)), np.minimum(np.minimum(ankle, rod_ends), jaw_hinge)),
           'pad': np.minimum(kcap, sole),
           'repl': shank if replacement else full(P)}
    return out


LEGS = [
    ((51.5, 15.8, 12.0), (43.0, 17.0, 4.6), (64.5, 17.0, 4.2), (71.0, 17.0, 1.25), 1, True),
    ((51.5, -15.8, 12.0), (43.0, -17.0, 4.6), (65.5, -17.0, 4.2), (72.0, -17.0, 1.25), -1, False),
    ((16.0, 15.8, 12.0), (7.5, 17.0, 4.6), (29.0, 17.0, 4.2), (35.5, 17.0, 1.25), 1, False),
    ((16.0, -15.8, 12.0), (7.5, -17.0, 4.6), (29.0, -17.0, 4.2), (35.5, -17.0, 1.25), -1, False),
]


BODY_PITCH = 5.0                     # alert rest: front hips carry a little load, rear on skids
PIVOT = np.array([12.5, 0.0, 0.0])
R_BODY = rotm(pitch=BODY_PITCH)


def body_pt(v):
    return PIVOT + R_BODY @ (np.asarray(v, float) - PIVOT)


def model(P, groups=False):
    G = {k: full(P) for k in MATS}
    Pb = (P - PIVOT) @ R_BODY + PIVOT        # body frame
    G['hull'] = chassis(Pb)
    G['glass'] = nav_glass(Pb)
    G['accent'] = rails(Pb)
    for part in (arm(Pb), head(Pb), tail(Pb)):
        for k, v in part.items():
            G[k] = np.minimum(G[k], v)
    for H, K, A, F, s, rep in LEGS:
        L = leg(P, body_pt(H), K, A, F, s, rep)
        for k, v in L.items():
            G[k] = np.minimum(G[k], v)
    d = full(P)
    for k in MATS:
        d = np.minimum(d, G[k])
    d = np.maximum(d, -P[:, 2])
    if groups:
        return d, G
    return d


GS = 100.0 / 78.0  # measured model-space length 78.0 mm -> 100 mm


def walter(P, groups=False):
    if groups:
        d, G = model(P / GS, groups=True)
        return d * GS, {k: v * GS for k, v in G.items()}
    return model(P / GS) * GS


def walter_material_ids(P):
    sdf.CHUNK = None
    out = np.empty(len(P), np.int8)
    for i in range(0, len(P), 150000):
        _, G = model(P[i:i + 150000] / GS, groups=True)
        out[i:i + 150000] = np.argmin(np.stack([G[k] for k in MATS], -1), -1)
    return out
