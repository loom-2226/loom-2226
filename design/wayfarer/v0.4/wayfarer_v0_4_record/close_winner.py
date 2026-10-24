"""Closing checks on the v0.3 winner v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
UNCONSTRAINED, physics kept. (1) pleat size, (2) strake heat onto drop tanks,
(3) longeron load path past the shuttle slot at LIMIT thrust. Inputs authored below."""
import math, random, sys
sys.path.insert(0, "/home/claude/ship_sizer")
import optimize_v3 as op

HULL, CHORD, T, G0 = 4.5, 19.0, 1300, 9.80665
FLUX = 0.90 * op.SIGMA * T ** 4
HC = op.RV["hull_coating"]
AZ = [45, 135, 225, 315]
INPUTS = {"recess_m": 0.5, "pleat_stack_m": 0.04, "drop_r": 1.5, "drop_c": 6.3, "drop_alpha_bare": 0.9,
          "drop_alpha_coated": 0.1, "drop_water_t": 200, "limit_g": 7.5, "cfrp_allow_mpa": 400, "cfrp_e_gpa": 150,
          "cfrp_t_m3": 1.6, "frame_spacing_m": 2.0, "tube_d_m": 0.4}


def trace(span, drops, n=24000, seed=3):
    rng = random.Random(seed)
    segs = [((HULL * math.cos(math.radians(t)), HULL * math.sin(math.radians(t))),
             ((HULL + span) * math.cos(math.radians(t)), (HULL + span) * math.sin(math.radians(t)))) for t in AZ]
    out = {"space": 0, "hull": 0, "wing": 0, "drop": 0}
    tot = 0
    for wi, t in enumerate(AZ):
        th = math.radians(t); ux, uy = math.cos(th), math.sin(th)
        for side in (1, -1):
            nx, ny = -uy * side, ux * side
            for _ in range(n // 8):
                r = HULL + rng.random() * span
                px, py = r * ux + nx * 1e-6, r * uy + ny * 1e-6
                phi = math.asin(2 * rng.random() - 1)
                dx, dy = nx * math.cos(phi) + ux * math.sin(phi), ny * math.cos(phi) + uy * math.sin(phi)
                best, what = float("inf"), "space"
                for (cx, cy, rr, name) in [(0, 0, HULL, "hull")] + [(c, 0, INPUTS["drop_r"], "drop") for c in drops]:
                    ox, oy = px - cx, py - cy
                    b = ox * dx + oy * dy; c = ox * ox + oy * oy - rr * rr
                    if b * b - c >= 0:
                        tt = -b - math.sqrt(b * b - c)
                        if 1e-9 < tt < best:
                            best, what = tt, name
                for wj, ((x1, y1), (x2, y2)) in enumerate(segs):
                    if wj == wi: continue
                    ex, ey = x2 - x1, y2 - y1; den = dx * ey - dy * ex
                    if abs(den) < 1e-12: continue
                    tt = ((x1 - px) * ey - (y1 - py) * ex) / den; u = ((x1 - px) * dy - (y1 - py) * dx) / den
                    if tt > 1e-9 and 0 <= u <= 1 and tt < best:
                        best, what = tt, "wing"
                out[what] += 1; tot += 1
    return {k: v / tot for k, v in out.items()}


def net_mw(span, f, drop_alpha=None):
    e = 2 * len(AZ) * CHORD * span * FLUX
    esc = f["space"] + f["hull"] * (1 - HC["absorptivity"]) * HC["reflected_escape_fraction"]
    if drop_alpha is not None:
        esc += f["drop"] * (1 - drop_alpha) * 0.5
    return e * esc / 1e6, e / 1e6


# 1. pleat size
print("1. PLEAT SIZE (12 pleats fit the 0.5 m recess either way)")
for pw in (2.0, 1.0):
    n = int(INPUTS["recess_m"] / INPUTS["pleat_stack_m"] + 1e-9)
    maxspan = min(n, 12) * pw
    res = {}
    for mode in op.MODES:
        q = op.heat_mw(mode, T)
        for k in range(1, 13):
            s = k * pw
            if net_mw(s, trace(s, []))[0] >= q:
                res[mode] = s; break
    cap = net_mw(maxspan, trace(maxspan, []))[0]
    print(f"  {pw:.0f} m pleats: spans N/F/E/H {res} -> clearance {[round(HULL + v, 1) for v in res.values()]} m; "
          f"max span {maxspan:.0f} m, torch capacity {cap:.0f} MW")

# 2. drop tanks in view of the strakes (200 t kit on the sides)
print("2. STRAKES SHINING ON SIDE DROP TANKS")
for span, label in ((24.0, "full span, torch burn"), (2.0, "one pleat, Metric HARD")):
    f = trace(span, [INPUTS["drop_c"], -INPUTS["drop_c"]])
    e = 2 * len(AZ) * CHORD * span * FLUX / 1e6
    for a, tag in ((INPUTS["drop_alpha_bare"], "bare"), (INPUTS["drop_alpha_coated"], "reflective-coated")):
        heat = e * f["drop"] * a
        k_per_h = heat * 1e6 * 3600 / (INPUTS["drop_water_t"] * 1000 * 4180)
        print(f"  {label}: {f['drop']*100:.1f}% of emission hits drop tanks; {tag}: {heat:.1f} MW -> {k_per_h:.0f} K/h in 200 t")

# 3. longerons past the shuttle slot
print("3. LONGERON LOAD PATH AT LIMIT THRUST")
wet_ahead_t = 1186 - 160          # v0.3 winner wet mass less propulsion (mass the thrust frame must push)
F = wet_ahead_t * 1000 * INPUTS["limit_g"] * G0
layout = {"sills flanking slot": [55, 125], "sides (drop-tank hardpoints)": [0, 180], "keel": [270]}
n = sum(len(v) for v in layout.values())
per = F / n
A_need = per / (INPUTS["cfrp_allow_mpa"] * 1e6)
D = INPUTS["tube_d_m"]; t = A_need / (math.pi * D)
I = math.pi / 8 * D ** 3 * t
Pcr = math.pi ** 2 * INPUTS["cfrp_e_gpa"] * 1e9 * I / INPUTS["frame_spacing_m"] ** 2
mass = n * A_need * 36 * INPUTS["cfrp_t_m3"]
print(f"  thrust-frame load at {INPUTS['limit_g']} g: {F/1e6:.0f} MN over {n} longerons = {per/1e6:.1f} MN each")
print(f"  CFRP tube {D} m dia, wall {t*1000:.0f} mm: area {A_need:.3f} m2, buckling load {Pcr/1e6:.0f} MN ({Pcr/per:.0f}x margin)")
print(f"  mass of {n} x 36 m: {mass:.1f} t (inside the 150 t structure line)")
for name, az in layout.items():
    print(f"  {name}: azimuth {az} -> y = {[round(4.1*math.cos(math.radians(a)),2) for a in az]} m at r 4.1 m")
print("  slot half-width 2.2 m; strake roots at |y| 3.18 m")
