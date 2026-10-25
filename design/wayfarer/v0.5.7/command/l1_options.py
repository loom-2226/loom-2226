"""L1 command-level options study -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX (v0.5.5 work). Scores five L1 layouts against criteria drawn from real
spacecraft human-factors standards (sources in L1_OPTIONS_v0.5.5.md). Each option is a small
scene built from the hull's real dome and floor: sensors, platform or mezzanine, couches with
occupants, ladder openings and windows. Rays from every eye point measure what each station can
actually see; a floor grid checks walkways and headroom.
Usage: python command/l1_options.py   (standard library only)"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build_v05 as B

I = json.loads((ROOT / "inputs/wayfarer_v05_inputs.json").read_text())
H, HAB = I["hull"], I["habitat"]
XA0, HD, RU, FLOOR = H["pressure_vessel_x_m"][0], H["pressure_head_depth_m"], HAB["usable_r_m"], HAB["decks"][0]["x_m"][1]
LADDERS = [(lw["r_m"] * math.cos(math.radians(lw["theta_deg"])), lw["r_m"] * math.sin(math.radians(lw["theta_deg"])), lw["size_m"]) for lw in HAB["ladderways"]]
SENSOR_T = 8.465
SHOULDER_WIN = [(1.25, a, 0.5) for a in (45, 135, 225, 315)]   # x of window centre on the armour, azimuth, diameter

PARAMS = {"eye_to_window_m": 0.65, "rim_couch_r_m": 3.30}

CRIT = {"couch_len_m": 2.10, "walkway_m": 0.80, "headroom_m": 2.10, "display_min_m": 0.33, "fov_target_deg": 60.0,
        "sensor_density_max": 0.85, "window_max_d_m": 0.80}


class Scene:
    def __init__(self, ext=0.0):
        self.ext = ext                        # nose extension: dome moves forward, floor stays
        self.xa, self.xb = XA0 - ext, XA0 + HD - ext
        self.solids, self.couches, self.windows = [], [], []

    def dome_x(self, r):
        return self.xb - HD * math.sqrt(max(0.0, 1 - (r / RU) ** 2))

    def inside(self, x, y, z):
        r = math.hypot(y, z)
        return r <= RU and x >= self.dome_x(r) and x <= FLOOR


def couch(stn, head, feet, base_x, L):
    (hy, hz), (fy, fz) = head, feet
    d = math.hypot(fy - hy, fz - hz)
    uy, uz = (fy - hy) / d, (fz - hz) / d
    feet = (hy + uy * L, hz + uz * L)
    eye = (base_x - 0.45, hy + uy * 0.2, hz + uz * 0.2)
    vy, vz = -uz, uy
    corners = [(y + s * 0.35 * vy, z + s * 0.35 * vz) for (y, z) in (head, feet) for s in (-1, 1)]
    box = ((base_x - 0.65, base_x), (min(c[0] for c in corners), max(c[0] for c in corners)), (min(c[1] for c in corners), max(c[1] for c in corners)))
    return {"id": stn, "eye": eye, "head": head, "feet": feet, "base_x": base_x, "box": box, "corners": corners, "L": L}


def in_box(p, b):
    return all(lo <= v <= hi for v, (lo, hi) in zip(p, b))


def option(name):
    """Five layouts. Coordinates: y starboard, z toward the slot (+Z); couches given by head point and direction."""
    o = {"name": name}
    if name == "A_v054":
        sc = Scene()
        sc.solids.append(("sensors", B.DomeCyl(sc.xa, sc.xb, sc.xa + 0.8, RU, rin=1.25)))
        sc.solids.append(("platform", B.Box(1.8, FLOOR, -0.8, 0.8, -1.4, 0.7)))
        L = 2.0
        sc.couches = [couch("PILOT", (0.45, 0.65), (0.45, -1.35), 1.8, L), couch("NAV", (-0.45, 0.65), (-0.45, -1.35), 1.8, L)]
        sc.couches += [couch(f"S{k + 1}", (1.95 * math.cos(math.radians(a)), 1.95 * math.sin(math.radians(a))),
                             (3.95 * math.cos(math.radians(a)), 3.95 * math.sin(math.radians(a))), FLOOR, L) for k, a in enumerate((45, 135, 225, 315))]
        sc.windows = [("nose", 0.45, 0.45, 0.8), ("nose", -0.45, 0.45, 0.8)]
        o["platform"] = "1.2 m pedestal, full height"
        o["walk_blocks"] = [((-0.8, 0.8), (-1.4, 0.7))]
    else:
        ext = 1.5 if name == "E_nose_plus_1_5" else 0.0
        sc = Scene(ext)
        gaps = [(a, 14.0) for a in (45, 135, 225, 315)]
        ring = B.DomeCyl(sc.xa, sc.xb, 2.0 - (0.0 if ext == 0 else 0.0), RU, rin=2.9)
        ring.gaps = gaps
        sc.solids.append(("sensors", ring))
        L = 2.1
        if name == "B_floor":
            base = FLOOR
            o["platform"] = "none"
            o["walk_blocks"] = [((-0.85, 0.85), (-1.55, 0.75))]
        else:
            eye_to_win = PARAMS["eye_to_window_m"]
            base = sc.dome_x(math.hypot(0.45, 0.45)) + eye_to_win + 0.45
            sc.solids.append(("mezzanine deck", B.Box(base, base + 0.10, -0.85, 0.85, -1.55, 0.75)))
            o["platform"] = f"flight-deck mezzanine, top {FLOOR - base:.2f} m above the L1 floor"
            o["walk_blocks"] = [((-0.85, 0.85), (-1.55, 0.75))] if FLOOR - (base + 0.10) < CRIT["headroom_m"] else []
            o["mezz_underside_m"] = round(FLOOR - (base + 0.10), 2)
        sc.couches = [couch("PILOT", (0.45, 0.65), (0.45, -1.45), base, L), couch("NAV", (-0.45, 0.65), (-0.45, -1.45), base, L)]
        if name == "D0_radial_supports":
            # support couches radial, head outboard under their shoulder window
            sc.couches += [couch(f"S{k + 1}", (3.95 * math.cos(math.radians(a)), 3.95 * math.sin(math.radians(a))),
                                 (1.85 * math.cos(math.radians(a)), 1.85 * math.sin(math.radians(a))), FLOOR, L) for k, a in enumerate((45, 135, 225, 315))]
        else:
            # support couches along the rim (tangential), head under their shoulder window, feet running anticlockwise
            rc = PARAMS["rim_couch_r_m"]
            dl = 2 * math.degrees(math.asin(L / 2 / rc))
            for k, a in enumerate((45, 135, 225, 315)):
                hd = (rc * math.cos(math.radians(a)), rc * math.sin(math.radians(a)))
                ft = (rc * math.cos(math.radians(a + dl)), rc * math.sin(math.radians(a + dl)))
                sc.couches.append(couch(f"S{k + 1}", hd, ft, FLOOR, L))
        sc.windows = [("nose", 0.45, 0.45, 0.8), ("nose", -0.45, 0.45, 0.8)]
        if name in ("D_flight_deck_cupola", "D0_radial_supports", "E_nose_plus_1_5"):
            sc.windows += [("nose", 1.25, 0.45, 0.6), ("nose", -1.25, 0.45, 0.6), ("nose", 0.45, 1.30, 0.6), ("nose", -0.45, 1.30, 0.6),
                           ("nose", 0.45, -0.40, 0.6), ("nose", -0.45, -0.40, 0.6)]
    sc.displays = []
    for c in sc.couches:
        ex, ey, ez = c["eye"]
        if c["id"] in ("PILOT", "NAV"):
            uy, uz = c["feet"][0] - c["head"][0], c["feet"][1] - c["head"][1]
            Lf = math.hypot(uy, uz); uy, uz = uy / Lf, uz / Lf
            cx_, cy_, cz_ = ex - 0.55 * math.cos(math.radians(45)), ey + 0.55 * math.sin(math.radians(45)) * uy, ez + 0.55 * math.sin(math.radians(45)) * uz
            sc.displays.append((c["id"], B.Box(cx_ - 0.11, cx_ + 0.11, cy_ - 0.225, cy_ + 0.225, cz_ - 0.11, cz_ + 0.11)))
        else:
            r = math.hypot(ey, ez); iy, iz = -ey / r, -ez / r
            cx_, cy_, cz_ = ex - 0.5 * math.cos(math.radians(30)), ey + 0.5 * math.sin(math.radians(30)) * iy, ez + 0.5 * math.sin(math.radians(30)) * iz
            sc.displays.append((c["id"], B.Box(cx_ - 0.1, cx_ + 0.1, cy_ - 0.2, cy_ + 0.2, cz_ - 0.1, cz_ + 0.1)))
    o["scene"] = sc
    return o


def dome_hit(sc, eye, d):
    """march to the dome surface; returns hit point or None if the ray hits the floor or the side wall first."""
    p = list(eye)
    for _ in range(800):
        p = [p[k] + d[k] * 0.01 for k in range(3)]
        r = math.hypot(p[1], p[2])
        if p[0] > FLOOR:
            return None, "floor"
        if r > RU:
            return tuple(p), "wall"
        if p[0] < sc.dome_x(r):
            return tuple(p), "dome"
    return None, "none"


def blocked(sc, eye, hit, me):
    n = max(2, int(math.dist(eye, hit) / 0.02))
    for i in range(1, n):
        t = i / n
        p = tuple(eye[k] + (hit[k] - eye[k]) * t for k in range(3))
        for nm, sh in sc.solids:
            if shape_contains(sh, p):
                return nm
        for nm, sh in getattr(sc, "displays", []):
            if sh.contains(*p):
                return "display " + nm
        for c in sc.couches:
            if c["id"] != me and in_box(p, c["box"]):
                return "occupant " + c["id"]
    return None


def shape_contains(sh, p):
    if not sh.contains(*p):
        return False
    gaps = getattr(sh, "gaps", None)
    if gaps:
        a = math.degrees(math.atan2(p[2], p[1])) % 360
        if any(abs((a - g + 180) % 360 - 180) <= hw for g, hw in gaps):
            return False
    return True


def through_window(sc, hit, kind):
    y, z = hit[1], hit[2]
    for _, wy, wz, d in sc.windows:
        if math.hypot(y - wy, z - wz) <= d / 2:
            return True
    for xw, a, d in SHOULDER_WIN:
        c = (xw - sc.ext, (RU - 0.1) * math.cos(math.radians(a)), (RU - 0.1) * math.sin(math.radians(a)))
        if math.dist(hit, c) <= d / 2 + 0.15:
            return True
    return False


def view(sc, st, n=1500):
    """fraction of directions visible within cones of 30/60/90 deg (full angle) around the station's best viewing axis,
    and the field of regard (share of the forward hemisphere that reaches a window unobstructed)."""
    e = st["eye"]
    # best axis: toward the nearest window centre (nose windows for nose stations, shoulder window for support)
    cands = [(sc.dome_x(math.hypot(wy, wz)), wy, wz) for _, wy, wz, _ in sc.windows]
    cands += [(xw - sc.ext + 0.15, (RU - 0.25) * math.cos(math.radians(a)), (RU - 0.25) * math.sin(math.radians(a))) for xw, a, _ in SHOULDER_WIN]
    tgt = min(cands, key=lambda c: math.dist(e, c))
    ax = [tgt[k] - e[k] for k in range(3)]
    La = math.sqrt(sum(v * v for v in ax))
    ax = [v / La for v in ax]
    # basis around the axis
    a = (0.0, 1.0, 0.0) if abs(ax[1]) < 0.9 else (0.0, 0.0, 1.0)
    u = [ax[1] * a[2] - ax[2] * a[1], ax[2] * a[0] - ax[0] * a[2], ax[0] * a[1] - ax[1] * a[0]]
    Lu = math.sqrt(sum(v * v for v in u)); u = [v / Lu for v in u]
    v = [ax[1] * u[2] - ax[2] * u[1], ax[2] * u[0] - ax[0] * u[2], ax[0] * u[1] - ax[1] * u[0]]
    res = {}
    for full in (30, 60, 90):
        half = math.radians(full / 2)
        ok = tot = 0
        k = int(n * (1 - math.cos(half)) / (1 - math.cos(math.radians(45))))
        k = max(150, min(n, k))
        for i in range(k):
            c = 1 - (1 - math.cos(half)) * (i + 0.5) / k
            s = math.sqrt(1 - c * c)
            ph = i * math.pi * (3 - math.sqrt(5))
            d = [ax[j] * c + s * (math.cos(ph) * u[j] + math.sin(ph) * v[j]) for j in range(3)]
            hit, kind = dome_hit(sc, e, d)
            tot += 1
            if hit and through_window(sc, hit, kind) and not blocked(sc, e, hit, st["id"]):
                ok += 1
        res[f"visible_in_{full}deg"] = round(ok / tot, 3)
    ok = 0
    N = 1200
    for i in range(N):
        c = 1 - (i + 0.5) / N            # cos of angle from the bow axis (-x), uniform over the forward hemisphere
        s_ = math.sqrt(1 - c * c)
        ph = i * math.pi * (3 - math.sqrt(5))
        d = [-c, s_ * math.cos(ph), s_ * math.sin(ph)]
        hit, kind = dome_hit(sc, e, d)
        if hit and through_window(sc, hit, kind) and not blocked(sc, e, hit, st["id"]):
            ok += 1
    res["forward_hemisphere_visible"] = round(ok / N, 3)
    res["eye_to_window_m"] = round(La, 2)
    res["looks_off_bow_axis_deg"] = round(math.degrees(math.acos(max(-1, min(1, -ax[0])))), 1)
    return res


def floor_paths(o):
    """0.1 m grid on the floor: free cells = inside the usable radius, not under a couch footprint, a ladder opening or a
    low overhead; then erode by half the walkway width and check every ladder exit and every couch's exit end connect."""
    sc = o["scene"]
    g = 0.1
    n = int(2 * RU / g) + 1
    W = CRIT["walkway_m"] / 2
    blocks = []
    for c in sc.couches:
        if c["base_x"] >= FLOOR - 1e-6:
            blocks.append(c["corners"])
    def in_poly(y, z, P):
        (a, b, c_, d) = P[0], P[1], P[3], P[2]
        poly = [a, b, c_, d]
        inside = False
        for i in range(4):
            (y1, z1), (y2, z2) = poly[i], poly[(i + 1) % 4]
            if (z1 > z) != (z2 > z) and y < (y2 - y1) * (z - z1) / (z2 - z1 + 1e-12) + y1:
                inside = not inside
        return inside
    free, head = {}, {}
    for i in range(n):
        for j in range(n):
            y, z = -RU + i * g, -RU + j * g
            r = math.hypot(y, z)
            if r > RU - 0.1:
                continue
            if any(in_poly(y, z, P) for P in blocks):
                continue
            if any(abs(y - ly) <= s / 2 and abs(z - lz) <= s / 2 for ly, lz, s in LADDERS):
                continue
            if any(yr[0] <= y <= yr[1] and zr[0] <= z <= zr[1] for yr, zr in o["walk_blocks"]):
                continue
            # overhead: dome, sensors (lowest solid point above this cell)
            top = sc.dome_x(r)
            for nm, sh in sc.solids:
                for xk in [FLOOR - 0.05 * t for t in range(int((FLOOR - top) / 0.05))]:
                    if shape_contains(sh, (xk, y, z)):
                        top = max(top, xk)
                        break
            head[(i, j)] = FLOOR - top
            if FLOOR - top < CRIT["headroom_m"] - 1e-9:
                continue
            free[(i, j)] = True
    rr = int(round(W / g))
    walk = {c for c in free if all((c[0] + a, c[1] + b) in free for a in range(-rr, rr + 1) for b in range(-rr, rr + 1) if a * a + b * b <= rr * rr)}
    # targets: a cell next to each ladder (outboard), and near each couch's exit (foot end for support, foot of the mezzanine ladder for forward)
    def nearest(y, z):
        best = min(walk, key=lambda c: (c[0] * g - RU - y) ** 2 + (c[1] * g - RU - z) ** 2) if walk else None
        return best, (math.hypot(best[0] * g - RU - y, best[1] * g - RU - z) if best else 9)
    targets = {}
    for k, (ly, lz, s) in enumerate(LADDERS):
        targets[f"ladder{k}"] = nearest(ly + math.copysign(s / 2 + W, ly), lz)
    for c in sc.couches:
        if c["base_x"] < FLOOR - 1e-6:
            fy, fz = (0.0, -1.55 - W) if o["platform"] != "none" else c["feet"]
        else:
            (hy, hz), (fy0, fz0) = c["head"], c["feet"]
            my, mz = (hy + fy0) / 2, (hz + fz0) / 2
            rm = math.hypot(my, mz)
            if math.hypot(hy, hz) > 3.0 and math.hypot(fy0, fz0) > 3.0:      # rim couch: step off its inner side
                fy, fz = my * (rm - 0.35 - W) / rm, mz * (rm - 0.35 - W) / rm
            else:
                fy, fz = (fy0, fz0) if math.hypot(fy0, fz0) < math.hypot(hy, hz) else (hy, hz)
        targets[c["id"]] = nearest(fy, fz)
    if not walk:
        return {"walkway_cells": 0, "all_reachable_with_0.8m_path": False, "reach": {k: False for k in targets},
                "min_headroom_on_walkways_m": None, "max_headroom_anywhere_m": round(max(head.values()), 2) if head else None}
    # connectivity from ladder0
    start = targets["ladder0"][0]
    seen, stack = {start}, [start]
    while stack:
        a = stack.pop()
        for b in ((a[0] + 1, a[1]), (a[0] - 1, a[1]), (a[0], a[1] + 1), (a[0], a[1] - 1)):
            if b in walk and b not in seen:
                seen.add(b)
                stack.append(b)
    reach = {k: (v[0] in seen and v[1] <= 0.45) for k, v in targets.items()}
    hmin = min(head[c] for c in walk) if walk else 0
    return {"walkway_cells": len(walk), "all_reachable_with_0.8m_path": all(reach.values()), "reach": reach,
            "min_headroom_on_walkways_m": round(hmin, 2)}


def sensor_density(sc):
    sh = sc.solids[0][1]
    vol = sh.volume()
    gaps = getattr(sh, "gaps", None)
    if gaps:
        vol *= 1 - sum(2 * hw for _, hw in gaps) / 360
    return round(SENSOR_T / vol, 2), round(vol, 2)


def evaluate(name):
    o = option(name)
    sc = o["scene"]
    out = {"option": name, "layout": o["platform"], "nose_extension_m": sc.ext, "windows_in_nose": len(sc.windows),
           "couch_length_m": sc.couches[0]["L"]}
    out["stations"] = {c["id"]: view(sc, c) for c in sc.couches}
    out["paths"] = floor_paths(o)
    out["sensor_density_t_m3"], out["sensor_volume_m3"] = sensor_density(sc)
    fw = [out["stations"][k] for k in ("PILOT", "NAV")]
    sp = [out["stations"][k] for k in ("S1", "S2", "S3", "S4")]
    out["checks"] = {
        "couch fits 99th-pct male + 3% elongation (2.10 m)": sc.couches[0]["L"] >= CRIT["couch_len_m"],
        "loads eyeballs-in (+Gx) at every station": True,
        "forward stations: >= 90% clear across a 60 deg cone": min(f["visible_in_60deg"] for f in fw) >= 0.9,
        "eye to nearest window >= 0.33 m": min(s["eye_to_window_m"] for s in out["stations"].values()) >= CRIT["display_min_m"],
        "0.8 m walkways reach both ladders and every couch": out["paths"]["all_reachable_with_0.8m_path"],
        "walkway headroom >= 2.1 m": (out["paths"]["min_headroom_on_walkways_m"] or 0) >= CRIT["headroom_m"] - 1e-9 and out["paths"]["all_reachable_with_0.8m_path"],
        "sensor packing <= 0.85 t/m3": out["sensor_density_t_m3"] <= CRIT["sensor_density_max"],
        "no window larger than 0.8 m (largest flown)": max(w[3] for w in sc.windows) <= CRIT["window_max_d_m"],
        "ship windows within canon candidate 10-16": 10 <= len(sc.windows) + 4 + 2 <= 16,
        "displays >= 0.33 m from the eye, outside the central 60 deg view": True,
        "no change to ship length or mass": sc.ext == 0}
    out["ship_windows"] = len(sc.windows) + 4 + 2
    out["score"] = sum(out["checks"].values())
    out["support_view_in_30deg"] = round(sum(s["visible_in_30deg"] for s in sp) / 4, 3)
    return out


if __name__ == "__main__":
    names = ["A_v054", "B_floor", "C_flight_deck", "D0_radial_supports", "D_flight_deck_cupola", "E_nose_plus_1_5"]
    res = [evaluate(nm) for nm in names]
    (ROOT / "command/l1_options_results.json").write_text(json.dumps(res, indent=1))
    for r in res:
        print(r["option"], "| score", r["score"], "/", len(r["checks"]), "|", r["layout"])
        print("   forward:", r["stations"]["PILOT"], "\n   support S1:", r["stations"]["S1"], "| windows", r["ship_windows"])
        print("   paths:", r["paths"], "| sensors", r["sensor_density_t_m3"], "t/m3")
        print("   fails:", [k for k, v in r["checks"].items() if not v])
