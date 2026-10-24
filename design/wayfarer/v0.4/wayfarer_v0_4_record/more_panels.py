"""More-strakes check v0.1 -- ALL bodies. ALL sponsors. 2026-2226. UNCONSTRAINED, physics kept.
Compares strake layouts on the v0.3 winner: view-factor loss (2D Monte Carlo, both faces of every
wing), spans for HARD Metric at 1,300 K, full-span torch capacity, shuttle exit margin and balance."""
import math, random, sys, json
sys.path.insert(0, "/home/claude/ship_sizer")
import optimize_v3 as op

HULL, CHORD, T = 4.5, 19.0, 1300
SLOT_HALF, SHUTTLE_HALF = 2.2, 1.95
HC = op.RV["hull_coating"]
FLUX = 0.90 * op.SIGMA * T ** 4
LAYOUTS = {
    "4 diagonals (winner)": [45, 135, 225, 315],
    "5: diagonals + keel": [45, 135, 225, 270, 315],
    "6 even, 60 deg": [0, 60, 120, 180, 240, 300],
    "8 even, 45 deg": [0, 45, 90, 135, 180, 225, 270, 315],
    "8 even, offset 22.5": [22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5],
}


def vf(az, span, n=12000):
    rng = random.Random(7)
    segs = [((HULL * math.cos(math.radians(t)), HULL * math.sin(math.radians(t))),
             ((HULL + span) * math.cos(math.radians(t)), (HULL + span) * math.sin(math.radians(t)))) for t in az]
    space = hull = tot = 0
    for wi, t in enumerate(az):
        th = math.radians(t)
        ux, uy = math.cos(th), math.sin(th)
        for side in (1, -1):
            nx, ny = -uy * side, ux * side
            for _ in range(n // (2 * len(az)) + 1):
                r = HULL + rng.random() * span
                px, py = r * ux + nx * 1e-6, r * uy + ny * 1e-6
                phi = math.asin(2 * rng.random() - 1)
                dx = nx * math.cos(phi) + ux * math.sin(phi)
                dy = ny * math.cos(phi) + uy * math.sin(phi)
                best, what = float("inf"), "space"
                b = px * dx + py * dy
                c = px * px + py * py - HULL * HULL
                if b * b - c >= 0:
                    tt = -b - math.sqrt(b * b - c)
                    if tt > 1e-9:
                        best, what = tt, "hull"
                for wj, ((x1, y1), (x2, y2)) in enumerate(segs):
                    if wj == wi:
                        continue
                    ex, ey = x2 - x1, y2 - y1
                    den = dx * ey - dy * ex
                    if abs(den) < 1e-12:
                        continue
                    tt = ((x1 - px) * ey - (y1 - py) * ex) / den
                    u = ((x1 - px) * dy - (y1 - py) * dx) / den
                    if tt > 1e-9 and 0 <= u <= 1 and tt < best:
                        best, what = tt, "wing"
                tot += 1
                space += what == "space"
                hull += what == "hull"
    fs, fh = space / tot, hull / tot
    return fs + fh * (1 - HC["absorptivity"]) * HC["reflected_escape_fraction"], fh * HC["absorptivity"]


def net(az, span):
    esc, hl = vf(az, span)
    e = 2 * len(az) * CHORD * span * FLUX
    return e * esc / 1e6, e * hl / 1e6, esc


q_hard = op.heat_mw("HARD", T)
rows = []
for name, az in LAYOUTS.items():
    hard_span = next((s for s in [2 * k for k in range(1, 13)] if net(az, s)[0] >= q_hard), None)
    cap, _, esc24 = net(az, 24.0)
    _, _, esc2 = net(az, 2.0)
    upper = [a for a in az if 0 < a < 180]
    margin = min(abs(HULL * math.cos(math.radians(a))) for a in upper) - SHUTTLE_HALF if upper else 9.9
    blocks_slot = any(abs(HULL * math.cos(math.radians(a))) < SLOT_HALF for a in upper)
    hits_drop = any(a in (0, 180) for a in az)
    panel_t = len(az) * CHORD * 24 * 5.0 / 1000
    zmom = sum(CHORD * 24 * 5.0 / 1000 * HULL * math.sin(math.radians(a)) for a in az)
    rows.append({"name": name, "n": len(az), "hard_span_m": hard_span, "torch_cap_mw": cap,
                 "escape_2m": esc2, "escape_24m": esc24, "shuttle_margin_m": margin, "blocks_slot": blocks_slot,
                 "hits_side_drop_tanks": hits_drop, "panel_mass_t": panel_t, "panel_z_moment_tm": zmom})
for r in rows:
    print(f"{r['name']:24s} n{r['n']} HARD span {r['hard_span_m']} m | torch {r['torch_cap_mw']:.0f} MW | escape {r['escape_2m']*100:.0f}% at 2 m, "
          f"{r['escape_24m']*100:.0f}% at 24 m | shuttle margin {r['shuttle_margin_m']:+.2f} m blocks slot {r['blocks_slot']} | "
          f"drop-tank clash {r['hits_side_drop_tanks']} | panels {r['panel_mass_t']:.1f} t, z-moment {r['panel_z_moment_tm']:+.1f} t.m")
print("shuttle moment if carried on top (saddle layout):", round(33 * 3.7, 1), "t.m")
json.dump(rows, open("/home/claude/ship_sizer/more_panels_results.json", "w"), indent=1)
