"""L4 stretcher path, 3 degrees of freedom -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX evidence for Sol's v0.5.3 habitat candidate. Extends Sol's
EVIDENCE/wayfarer_stretcher_turn.py (which fixes the stretcher's centre at 210 deg and,
as packaged, uses a 1.4 m length) to a rigid 2.0 x 0.60 m rectangle whose centre may move
around the corridor ring, with the two ladderways (theta 0 and 180 deg, r 1.4 m, 0.8 m
square) as obstacles. Plan view only: no patient or attendant envelope, no height.
Start: lying along the corridor (orientation 0-10 deg) anywhere in the ring, or on one
named side of the opening; goal: lying radially inside the medical bay (centre r > 2.65 m).
Usage: python habitat/stretcher_path_3dof.py   (standard library only)"""
import json, math, sys
from collections import deque

RC, RIN, ROUT = 0.9, 1.9, 4.15          # core, corridor outer wall, room outer radius
MED = (165.0, 255.0)                     # medical bay sector, deg
WALL = 0.11                              # wall band either side of r = 1.9 (Sol's value)
LADDERS = [(1.4, 0.0, 0.8), (1.4, 180.0, 0.8)]
L, W = 2.0, 0.6


def ok_point(x, y, door_c, door_w, ladders):
    r = math.hypot(x, y)
    if r < RC or r > ROUT:
        return False
    a = math.degrees(math.atan2(y, x)) % 360
    if r > RIN + WALL and not (MED[0] <= a <= MED[1]):
        return False
    if abs(r - RIN) <= WALL:
        half = math.degrees(door_w / 2 / RIN)
        if abs((a - door_c + 180) % 360 - 180) > half:
            return False
    for lr, la, ls in ladders:
        cx, cy = lr * math.cos(math.radians(la)), lr * math.sin(math.radians(la))
        u = (math.cos(math.radians(la)), math.sin(math.radians(la)))
        dx, dy = x - cx, y - cy
        if abs(dx * u[0] + dy * u[1]) <= ls / 2 and abs(-dx * u[1] + dy * u[0]) <= ls / 2:
            return False
    return True


def pose_ok(rc, phi, psi, door_c, door_w, ladders):
    """centre at radius rc, angle phi (deg); psi = 0 along the corridor (tangent), 90 radial."""
    p = math.radians(phi)
    cx, cy = rc * math.cos(p), rc * math.sin(p)
    t = p + math.pi / 2 - math.radians(psi)          # long axis: tangent rotated toward radial
    ux, uy = math.cos(t), math.sin(t)
    vx, vy = -uy, ux
    for i in range(11):
        s = (i / 10 - 0.5) * L
        for j in range(5):
            q = (j / 4 - 0.5) * W
            if not ok_point(cx + s * ux + q * vx, cy + s * uy + q * vy, door_c, door_w, ladders):
                return False
    return True


def search(door_w, ladders, door_c=210.0, dr=0.05, dphi=2.0, dpsi=5.0, start_side="any"):
    rs = [1.15 + k * dr for k in range(int((3.3 - 1.15) / dr) + 1)]
    phis = [150 + k * dphi for k in range(int((330 - 150) / dphi) + 1)]
    psis = [k * dpsi for k in range(int(90 / dpsi) + 1)]
    ok = set()
    for i, r in enumerate(rs):
        for j, ph in enumerate(phis):
            for k, ps in enumerate(psis):
                if pose_ok(r, ph, ps, door_c, door_w, ladders):
                    ok.add((i, j, k))
    side = {"life_support": lambda ph: ph >= 250, "shelter": lambda ph: ph <= 170, "any": lambda ph: True}[start_side]
    starts = [(i, j, k) for (i, j, k) in ok if psis[k] <= 10 and rs[i] < 1.6 and side(phis[j])]
    goal = lambda s: rs[s[0]] > 2.65 and psis[s[2]] >= 80 and MED[0] + 15 <= phis[s[1]] <= MED[1] - 15
    q, seen = deque(starts), set(starts)
    while q:
        u = q.popleft()
        if goal(u):
            return {"door_m": door_w, "ladders": bool(ladders), "valid_poses": len(ok), "start_poses": len(starts), "path": True,
                    "goal_pose": {"r": round(rs[u[0]], 2), "phi": phis[u[1]], "psi": psis[u[2]]}}
        i, j, k = u
        for v in ((i + 1, j, k), (i - 1, j, k), (i, j + 1, k), (i, j - 1, k), (i, j, k + 1), (i, j, k - 1)):
            if v in ok and v not in seen:
                seen.add(v)
                q.append(v)
    return {"door_m": door_w, "ladders": bool(ladders), "valid_poses": len(ok), "start_poses": len(starts), "path": False}


if __name__ == "__main__":
    out = []
    for wall in (0.11, 0.01):
        WALL = wall
        for lad in (LADDERS, []):
            for w in (2.0, 2.4, 2.8):
                r = search(w, lad)
                r["wall_band_m"] = wall
                out.append(r)
                print(json.dumps(r), flush=True)
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "/dev/null", "w"), indent=1)
