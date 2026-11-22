"""Gait test: is the Weave a swimmer? (kT/Sol, 2026-11-22). NON-CANON Builder physics investigation. ALL bodies. ALL sponsors. 2026-2226.

ONE hypothesis (explicit): the hull has a bounded configuration q = (q1, q2) in [-1, 1]^2 (two hull modes), and the field it
generates is set by how fast that configuration changes (the swimmer form, cf. Shapere-Wilczek):
    field-centre velocity  V = R(theta) [A_x(q), A_y(q)] . qdot      field rotation rate  Omega = A_th(q) . qdot
A is a connection on configuration space. FLAT A (exact, A = grad f) is a joystick with new vocabulary; CURVED A gives holonomy.
Everything else is the lane's existing model, unchanged: zero-expansion shift carriage (Natario translation form of
outing_dodge.b_axis_y, rotation Omega x (x - X) F(r), divergence-free), slow-geodesic law dw/dt = -(grad b) w for hull points,
R 15 m / wall 2 m, Tic Tac hull ends at +-6.4 m. The model does NOT constrain A: this test maps what each A does, it does not
derive A."""
import os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
R, DW = 15.0, 2.0
def sech2(z): return 1.0 / np.cosh(np.clip(z, -300, 300)) ** 2
def F(r): return 0.5 * (np.tanh((r + R) / DW) - np.tanh((r - R) / DW))
def Fp(r): return 0.5 / DW * (sech2((r + R) / DW) - sech2((r - R) / DW))
def bfield(P, X, V, Om):
    """2D: Natario-type translation along V (zero expansion) plus rigid rotation, both carried by the field centred at X"""
    d = P - X; r = np.hypot(d[:, 0], d[:, 1]) + 1e-300; vn = np.linalg.norm(V)
    out = np.zeros_like(P)
    if vn > 0:
        e = V / vn; u = d @ e; p = d @ np.array([-e[1], e[0]]); q = Fp(r) / (2 * r)
        bu = vn * (F(r) + p * p * q); bp = -vn * u * p * q
        out += np.outer(bu, e) + np.outer(bp, np.array([-e[1], e[0]]))
    out += Om * np.c_[-d[:, 1], d[:, 0]] * F(r)[:, None]
    return out
# ---------------------------------------------------------------- connections (hull property; chosen per case)
def A_flat(L0):            # exact: A = grad f with f = L0 (q1, q2) -> position follows configuration directly
    return lambda q: (np.array([L0, 0.0]), np.array([0.0, L0]), np.array([0.0, 0.0]))
def A_curved_trans(L0, k): # exact part + curvature k (metres per unit loop area) in body-x translation
    return lambda q: (np.array([L0 - 0.5 * k * q[1], 0.5 * k * q[0]]), np.array([0.0, L0]), np.array([0.0, 0.0]))
def A_curved_rot(c):       # attitude curvature c (radians per unit loop area)
    return lambda q: (np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([-0.5 * c * q[1], 0.5 * c * q[0]]))
def A_both(L0, k, c):
    return lambda q: (np.array([L0 - 0.5 * k * q[1], 0.5 * k * q[0]]), np.array([0.0, L0]), np.array([-0.5 * c * q[1], 0.5 * c * q[0]]))
# ---------------------------------------------------------------- configuration paths (smooth)
def seg(qa, qb, T):
    qa, qb = np.array(qa, float), np.array(qb, float)
    def q(t): s = np.clip(t / T, 0, 1); return qa + (qb - qa) * (6 * s ** 5 - 15 * s ** 4 + 10 * s ** 3)
    def qd(t): s = np.clip(t / T, 0, 1); return (qb - qa) / T * (30 * s ** 4 - 60 * s ** 3 + 30 * s ** 2)
    return q, qd, T
def path(points, T_each):
    return [seg(points[i], points[i + 1], T_each) for i in range(len(points) - 1)]
SQUARE = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]            # loop area 1 (anticlockwise)
SQUARE_REV = SQUARE[::-1]
def fly(A, segs, dt=2e-4):
    """integrate field centre X, attitude th, and the two hull ends under the slow-geodesic law"""
    X = np.zeros(2); th = 0.0; Pts = np.array([[6.4, 0.0], [-6.4, 0.0]]); W = np.zeros_like(Pts)
    a_peak = 0.0; v_prev = np.zeros(2); V_peak = 0.0
    for q, qd, T in segs:
        n = max(1, int(T / dt))
        for i in range(n):
            t = i * dt; qq, qv = q(t), qd(t); Ax, Ay, Ath = A(qq)
            Vb = np.array([Ax @ qv, Ay @ qv]); c, s = math.cos(th), math.sin(th); V = np.array([c * Vb[0] - s * Vb[1], s * Vb[0] + c * Vb[1]]); Om = Ath @ qv
            b = bfield(Pts, X, V, Om); eps = 1e-4
            J = np.zeros((len(Pts), 2, 2))
            for k_, e in enumerate(np.eye(2)):
                J[:, k_, :] = (bfield(Pts + eps * e, X, V, Om) - bfield(Pts - eps * e, X, V, Om)) / (2 * eps)
            W = W + dt * (-np.einsum('nkj,nj->nk', J, W)); Pts = Pts + dt * (b + W)
            X = X + dt * V; th = th + dt * Om
            a_peak = max(a_peak, float(np.linalg.norm(V - v_prev)) / dt) if i > 0 else a_peak; v_prev = V; V_peak = max(V_peak, float(np.linalg.norm(V)))
    hull_c = Pts.mean(0); ax = Pts[0] - Pts[1]; hull_th = math.atan2(ax[1], ax[0])
    return dict(field_centre=X.round(4).tolist(), attitude_deg=round(math.degrees(th), 3), hull_centre=hull_c.round(4).tolist(), hull_attitude_deg=round(math.degrees(hull_th), 3),
                residual_w=float(np.abs(W).max()), peak_field_speed=round(V_peak, 2), peak_field_accel_g=round(a_peak / 9.81, 2))
if __name__ == '__main__':
    cases = {}
    L0, k, c = 15.0, 7.5, math.radians(30.0)
    cases['1 flat connection, one square loop'] = fly(A_flat(L0), path(SQUARE, 1.0))
    cases['2 curved translation (k 7.5 m), one loop'] = fly(A_curved_trans(L0, k), path(SQUARE, 1.0))
    cases['2r same loop reversed'] = fly(A_curved_trans(L0, k), path(SQUARE_REV, 1.0))
    cases['2s same loop 10x slower'] = fly(A_curved_trans(L0, k), path(SQUARE, 10.0), dt=2e-3)
    cases['3 order: q1 then q2'] = fly(A_curved_trans(L0, k), path([(0, 0), (1, 0), (1, 1)], 1.0))
    cases['3 order: q2 then q1'] = fly(A_curved_trans(L0, k), path([(0, 0), (0, 1), (1, 1)], 1.0))
    cases['4 attitude curvature (30 deg), one loop'] = fly(A_curved_rot(c), path(SQUARE, 1.0))
    both = A_both(L0, k, c)
    cases['5 translation loop then attitude loop'] = fly(both, path(SQUARE, 1.0) + path([(0, 0), (-1, 0), (-1, -1), (0, -1), (0, 0)], 1.0))
    cases['5 attitude loop then translation loop'] = fly(both, path([(0, 0), (-1, 0), (-1, -1), (0, -1), (0, 0)], 1.0) + path(SQUARE, 1.0))
    # range with bounded configuration: repeat the loop n times
    reps = {}
    for n in (1, 4, 10):
        reps[f'flat x{n}'] = fly(A_flat(L0), path(SQUARE, 1.0) * n, dt=5e-4)['hull_centre']
        reps[f'curved x{n}'] = fly(A_curved_trans(L0, k), path(SQUARE, 1.0) * n, dt=5e-4)['hull_centre']
    findings = [
     'FLAT connection: every closed loop returns her exactly (joystick). With a bounded hull configuration her reach is bounded too: max |x| = L0 * max|q|, however many cycles (range test).',
     'CURVED connection: a closed loop moves her by curvature x loop area (7.5 m per unit loop here); reversing the loop moves her back; doing it 10x slower gives the same displacement (geometric: path, not timing). Repeating the gait ratchets her without limit.',
     'ORDER: two paths to the same final configuration (q1 then q2, or q2 then q1) leave her in different places, differing by exactly the enclosed curvature (route memory, cf. RT-B1).',
     'ATTITUDE: an attitude-curved connection turns her (30 deg per loop) and leaves her not rotating: falling-cat reorientation. No conserved charge changes (angular momentum is zero at start and end); translation, unlike attitude, changes the boost charge and still needs an external partner (R4).',
     'NON-COMMUTING: a translation gait then an attitude gait ends somewhere different from the reverse order (translations are made in her body frame).',
     'IN EVERY CASE the hull is carried with residual w ~ 0: the gait changes position and attitude, never lasting velocity (consistent with the lane theorem). Orbit / velocity matching is still not a gait.']
    derived = ('Structural result (mathematics, not a chosen law): if her hull configuration is bounded, unbounded travel by the Weave REQUIRES a curved connection. '
               'A flat connection is a joystick with a leash. Our earlier scripted dashes silently assumed unbounded control.')
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, parameters=dict(L0_m=L0, curvature_trans_m_per_area=k, curvature_rot_deg_per_area=30.0, loop_time_s_per_side=1.0),
               cases=cases, range_by_repetition=reps, findings=findings, structural_result=derived,
               not_determined='Whether the Builder hull connection is flat or curved, its size, and how it depends on the environment: the field model does not constrain A. That is the one quantity to grant or refuse.')
    json.dump(out, open(os.path.join(H, 'gait_test.json'), 'w'), indent=1)
    for k_, v in cases.items(): print(k_, v)
    print(reps)
