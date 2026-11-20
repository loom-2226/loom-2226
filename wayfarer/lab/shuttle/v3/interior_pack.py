"""Shuttle v3 step 4: first interior packaging of the B5 concept (97 m3 outer).
ALL bodies. ALL sponsors. 2026-2226. NON-CANON. Zones are proposals; volumes by grid integration."""
import json, numpy as np
from matplotlib.path import Path
import b5_concept as C
def inset(S, d):
    S = np.array(S); n = len(S); out = []; c0 = S.mean(0)
    for i in range(n):
        p, a, b = S[i], S[i - 1], S[(i + 1) % n]
        e1 = (p - a) / np.linalg.norm(p - a); e2 = (b - p) / np.linalg.norm(b - p)
        n1 = np.array([e1[1], -e1[0]]); n2 = np.array([e2[1], -e2[0]])
        if n1 @ (p - c0) < 0: n1, n2 = -n1, -n2
        bis = n1 + n2; bis /= np.linalg.norm(bis); c = max(bis @ n1, .35); out.append(p - d / c * bis)
    return np.array(out)
Z = dict(nose=(0.3, 2.6), cabin=(2.6, 7.9), well=(7.9, 11.1), shield=(11.1, 11.95), aft=(11.95, 12.8))
FLOOR_CAB = -0.55; FLOOR_WELL = -0.80; ROVER_HALF = 1.00; ROVER_TOP = 1.25
DEMAND = {"cabin (6 reclined couches, 3-day leg)": 27.0, "water 23.1 t + 5% ullage": 24.3,
          "rover/capsule + handling (1.9 x 3.0 m)": 11.5, "aft: torch, reactor, H2/O2 RCS, plumbing": 7.0,
          "avionics, life support, batteries": 3.0}
def classify(x, y, z):
    if Z["nose"][0] <= x < Z["nose"][1]: return "avionics/sensors"
    if Z["cabin"][0] <= x < Z["cabin"][1]: return "cabin" if z >= FLOOR_CAB else "water"
    if Z["well"][0] <= x < Z["well"][1]:
        if z < FLOOR_WELL - 0.05: return "water"
        if y < -ROVER_HALF: return "water"
        if y > ROVER_HALF: return "water" if z > 1.0 else "door path/ramp"
        return "rover well" if z <= ROVER_TOP else "life support/equipment"
    if Z["shield"][0] <= x < Z["shield"][1]: return "water"
    return "aft systems"
xs = np.linspace(0.31, 12.79, 125); dx = xs[1] - xs[0]; ny = 90
vol = {}
for x in xs:
    outer = inset(C.section(x), 0.10); cab = inset(C.section(x), 0.20)
    P, Pc = Path(np.vstack([outer, outer[:1]])), Path(np.vstack([cab, cab[:1]]))
    yy, zz = np.meshgrid(np.linspace(-2.2, 2.2, ny), np.linspace(-1.4, 2.1, ny)); pts = np.c_[yy.ravel(), zz.ravel()]
    cell = (4.4 / (ny - 1)) * (3.5 / (ny - 1)) * dx
    inn = P.contains_points(pts); inc = Pc.contains_points(pts)
    for (y, z), a, c in zip(pts, inn, inc):
        if not a: continue
        k = classify(x, y, z)
        if k == "cabin" and not c: k = "cabin wall/frames"
        vol[k] = vol.get(k, 0) + cell
vol = {k: round(v, 1) for k, v in sorted(vol.items(), key=lambda t: -t[1])}
supply = {"cabin (6 reclined couches, 3-day leg)": vol.get("cabin", 0), "water 23.1 t + 5% ullage": vol.get("water", 0),
          "rover/capsule + handling (1.9 x 3.0 m)": vol.get("rover well", 0), "aft: torch, reactor, H2/O2 RCS, plumbing": vol.get("aft systems", 0),
          "avionics, life support, batteries": round(vol.get("avionics/sensors", 0) + vol.get("life support/equipment", 0), 1)}
out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "zones_x_m": Z, "floors_z_m": {"cabin": FLOOR_CAB, "well": FLOOR_WELL},
       "volume_by_use_m3": vol, "demand_m3": DEMAND, "supply_m3": supply,
       "balance_m3": {k: round(supply[k] - DEMAND[k], 1) for k in DEMAND}}
json.dump(out, open("interior_pack.json", "w"), indent=1); print(json.dumps(out, indent=1))
