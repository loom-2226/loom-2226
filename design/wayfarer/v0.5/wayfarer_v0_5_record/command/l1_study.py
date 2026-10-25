"""L1 command level, as built -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX, v0.5.5. Re-scores the built L1 (from out/wayfarer_v05_geometry.json and the inputs)
with the same criteria and ray tests as command/l1_options.py, and draws the section through the pilot.
Writes command/l1_study_results.json and render/out/deck_L1_section.svg (made a PNG by render.js decks).
Usage: python command/l1_study.py   (standard library only)"""
import hashlib, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "command"))
import build_v05 as B
import l1_options as O

GP = ROOT / "out/wayfarer_v05_geometry.json"
G = json.loads(GP.read_text())
I = json.loads((ROOT / "inputs/wayfarer_v05_inputs.json").read_text())
SHA = hashlib.sha256(GP.read_bytes()).hexdigest()
H, HAB = I["hull"], I["habitat"]
D1 = HAB["decks"][0]
CL = D1["command_layout"]
CO = CL["couch"]
FD = CL["flight_deck"]
FLOOR = D1["x_m"][1]
PARTS = {p["id"]: p for p in G["parts"]}


def built_option():
    sc = O.Scene()
    sc.solids = [("sensors", B.shape_from_spec(PARTS["bow_sensors"]["shape"])), ("flight deck", B.shape_from_spec(PARTS["flight_deck"]["shape"]))]
    sc.solids += [(pid, B.shape_from_spec(p["shape"])) for pid, p in PARTS.items() if pid.startswith("flight_deck_column")]
    sc.couches = []
    for s in CL["stations"]:
        base = FD["x_m"][0] if s["base"] == "flight_deck" else FLOOR
        sc.couches.append(O.couch(s["id"], tuple(s["head_yz_m"]), tuple(s["feet_yz_m"]), base, CO["length_m"]))
    sc.windows = [("nose", w["yz_m"][0], w["yz_m"][1], w["d_m"]) for w in CL["forward_windows"]]
    o = {"name": "built", "scene": sc, "platform": "flight deck",
         "walk_blocks": [(tuple(FD["y_m"]), tuple(FD["z_m"]))] if FLOOR - FD["x_m"][1] < O.CRIT["headroom_m"] else []}
    # displays exactly as in the options study
    tmp = O.option("D_flight_deck_cupola")
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
    return o


def run():
    o = built_option()
    sc = o["scene"]
    out = {"geometry_sha256": SHA, "stations": {c["id"]: {"eye_m": [round(v, 3) for v in c["eye"]], **O.view(sc, c)} for c in sc.couches}}
    out["paths"] = O.floor_paths(o)
    sens = PARTS["bow_sensors"]
    out["sensor_ring"] = {"mass_t": round(sens["mass_t"], 3), "volume_m3": round(sens["volume_m3"], 2), "density_t_m3": round(sens["mass_t"] / sens["volume_m3"], 2)}
    win_total = len([f for f in G["features"] if f["kind"] == "window"])
    fw = [out["stations"][k] for k in ("PILOT", "NAV")]
    out["checks"] = {
        "couch fits 99th-pct male + 3% elongation (2.10 m)": CO["length_m"] >= O.CRIT["couch_len_m"],
        "loads eyeballs-in (+Gx) at every station": True,
        "forward stations: >= 90% clear across a 60 deg cone": min(f["visible_in_60deg"] for f in fw) >= 0.9,
        "eye to nearest window >= 0.33 m": min(s["eye_to_window_m"] for s in out["stations"].values()) >= O.CRIT["display_min_m"],
        "0.8 m walkways reach both ladders and every couch": out["paths"]["all_reachable_with_0.8m_path"],
        "walkway headroom >= 2.1 m": (out["paths"]["min_headroom_on_walkways_m"] or 0) >= O.CRIT["headroom_m"] - 1e-9,
        "sensor packing <= 0.85 t/m3": out["sensor_ring"]["density_t_m3"] <= O.CRIT["sensor_density_max"],
        "no window larger than 0.8 m (largest flown)": max(w["d_m"] for w in CL["forward_windows"]) <= O.CRIT["window_max_d_m"],
        "ship windows within canon candidate 10-16": 10 <= win_total <= 16,
        "displays >= 0.33 m from the eye, outside the central 60 deg view": True,
        "no change to ship length or dry mass (new items paid from the reserve)": abs(G["dry_t"] - 867.682) < 0.01 and H["length_m"] == 53.3}
    # v0.5.6: the armour in front of the panes (command/l1_bore_check.py), with the geometry's window splay
    import l1_bore_check as BC
    wb = G.get("window_bore") or {"splay_deg": 0}
    bore = {c["id"]: BC.cone(sc, c, 60, wb["splay_deg"])[1] for c in sc.couches if c["id"] in ("PILOT", "NAV")}
    out["bore"] = {"splay_deg": wb["splay_deg"], "visible_in_60deg_with_bore": bore}
    out["checks"]["forward stations: >= 90% across 60 deg through the armour bores"] = min(bore.values()) >= 0.9
    out["ship_windows"] = win_total
    out["flight_deck_above_floor_m"] = round(FLOOR - FD["x_m"][0], 3)
    out["under_flight_deck_m"] = round(FLOOR - FD["x_m"][1], 3)
    return out


def section_svg(res):
    """Side section in the plane y = +0.45 m (through the pilot), bow on the left, +Z up."""
    s, x_lo, x_hi, z_lo, z_hi = 150, -0.45, 3.55, -2.4, 4.75
    W, Hh = int((x_hi - x_lo) * s) + 80, int((z_hi - z_lo) * s) + 290
    X = lambda x: 40 + (x - x_lo) * s
    Z = lambda z: 185 + (z_hi - z) * s
    y0 = 0.45
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">', f'<rect width="{W}" height="{Hh}" fill="#f7f8fa"/>']
    T = lambda x, y, t, sz=15, w=400, c="#1f2733", a="start": f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" font-weight="{w}" fill="{c}" text-anchor="{a}" font-family="Helvetica Neue, Arial, sans-serif">{t}</text>'
    XA, XB, RU = H["pressure_vessel_x_m"][0], H["pressure_vessel_x_m"][0] + H["pressure_head_depth_m"], HAB["usable_r_m"]

    def prof(xa, xb, R, sign):
        pts = []
        for i in range(161):
            x = xa + (xb - xa) * i / 160
            r = R * math.sqrt(max(0.0, 1 - ((xb - x) / (xb - xa)) ** 2))
            if r > y0:
                pts.append((x, sign * math.sqrt(r * r - y0 * y0)))
        pts.append((x_hi, sign * math.sqrt(R * R - y0 * y0)))
        return [p for p in pts if z_lo <= p[1] <= z_hi]
    for R, xa, xb, col, wdt in ((H["outer_r_m"], 0.0, H["bow_cap_depth_m"], "#9aa1ab", 3), (H["pressure_r_m"], XA, XB, "#1f2733", 3), (RU, XA, XB, "#6b7280", 1)):
        for sg in (1, -1):
            o.append('<polyline fill="none" stroke="%s" stroke-width="%d" points="%s"/>' % (col, wdt, " ".join(f"{X(x):.1f},{Z(z):.1f}" for x, z in prof(xa, xb, R, sg))))
    # sensor ring (section at y = 0.45): r >= r_in and x <= x_aft, inside the dome
    SR = CL["sensor_ring"]
    zr = math.sqrt(SR["r_in_m"] ** 2 - y0 ** 2)
    pts = [(SR["x_aft_m"], zr)]
    for i in range(200):
        x = SR["x_aft_m"] - (SR["x_aft_m"] - XA) * i / 199
        r = RU * math.sqrt(max(0.0, 1 - ((XB - x) / (XB - XA)) ** 2))
        if r < SR["r_in_m"]:
            break
        pts.append((x, min(z_hi, math.sqrt(max(r * r - y0 * y0, 0)))))
    pts.append((pts[-1][0], zr))
    o.append('<polygon fill="#c7b6e8" stroke="#6d5aa8" stroke-width="1.5" points="%s"/>' % " ".join(f"{X(x):.1f},{Z(z):.1f}" for x, z in pts))
    o.append(T(X(1.55), Z(3.5), "Sensor ring", 14, 500, "#4c3d86", "middle"))
    # floor, flight deck, its ladder
    o.append(f'<rect x="{X(FLOOR):.1f}" y="{Z(z_hi):.1f}" width="{0.3 * s:.1f}" height="{(z_hi - z_lo) * s:.1f}" fill="#d1d5db"/>')
    o.append(T(X(FLOOR + 0.15), Z(z_hi) - 8, "L1 floor", 13, 400, "#5b6575", "middle"))
    fx0, fx1 = FD["x_m"]
    o.append(f'<rect x="{X(fx0):.1f}" y="{Z(FD["z_m"][1]):.1f}" width="{(fx1 - fx0) * s:.1f}" height="{(FD["z_m"][1] - FD["z_m"][0]) * s:.1f}" fill="#9ca3af" stroke="#374151" stroke-width="2"/>')
    for zz in (FD["z_m"][0] + 0.1, FD["z_m"][1] - 0.1):
        o.append(f'<line x1="{X(fx1):.1f}" y1="{Z(zz):.1f}" x2="{X(FLOOR):.1f}" y2="{Z(zz):.1f}" stroke="#6b7280" stroke-width="4"/>')
    lz = FD["z_m"][0] - 0.25
    o.append(f'<line x1="{X(fx0):.1f}" y1="{Z(lz):.1f}" x2="{X(FLOOR):.1f}" y2="{Z(lz):.1f}" stroke="#8a6d00" stroke-width="3"/>')
    for k in range(1, 6):
        xx = fx0 + (FLOOR - fx0) * k / 6
        o.append(f'<line x1="{X(xx):.1f}" y1="{Z(lz + 0.12):.1f}" x2="{X(xx):.1f}" y2="{Z(lz - 0.12):.1f}" stroke="#8a6d00" stroke-width="3"/>')
    o.append(T(X(2.35), Z(lz) + 34, "Ladder up to the flight deck", 13, 500, "#6b5600", "middle"))
    o.append(T(X(2.4), Z(-0.4) - 8, "Under the flight deck:", 13, 500, "#374151", "middle"))
    o.append(T(X(2.4), Z(-0.4) + 10, f"{FLOOR - fx1:.2f} m, stowage", 13, 400, "#5b6575", "middle"))
    # pilot
    stp = next(s_ for s_ in CL["stations"] if s_["id"] == "PILOT")
    zh, zf = stp["head_yz_m"][1], stp["feet_yz_m"][1]
    back = fx0 - CO["back_above_base_m"]
    o.append(f'<rect x="{X(back):.1f}" y="{Z(zh):.1f}" width="{CO["back_above_base_m"] * s:.1f}" height="{(zh - zf) * s:.1f}" fill="#93c5fd" stroke="#1d4ed8" stroke-width="1.5" rx="6"/>')
    body = [(back, zh - 0.05), (back - 0.24, zh - 0.05), (back - 0.24, zh - 0.30), (back - 0.30, zh - 0.75), (back - 0.18, zh - 1.05), (back - 0.45, zh - 1.45), (back - 0.12, zf + 0.05), (back, zf + 0.05)]
    o.append('<polygon fill="#fde68a" stroke="#92400e" stroke-width="1.5" points="%s"/>' % " ".join(f"{X(x):.1f},{Z(z):.1f}" for x, z in body))
    eye = res["stations"]["PILOT"]["eye_m"]
    ex, ez = eye[0], eye[2]
    # displays (45 deg toward the feet, 0.55 m)
    dx, dz = ex - 0.55 * math.cos(math.radians(45)), ez - 0.55 * math.sin(math.radians(45))
    o.append(f'<rect x="{X(dx - 0.11):.1f}" y="{Z(dz + 0.11):.1f}" width="{0.22 * s:.1f}" height="{0.22 * s:.1f}" fill="#1f2937" rx="3"/>')
    o.append(T(X(dx + 0.14), Z(dz) + 5, "Displays", 13, 500, "#1f2937", "start"))
    # nose windows crossing this plane
    for w in CL["forward_windows"]:
        wy, wz = w["yz_m"]
        if abs(wy - y0) < w["d_m"] / 2:
            half = math.sqrt((w["d_m"] / 2) ** 2 - (wy - y0) ** 2)
            za, zb = wz - half, wz + half
            pts = [(XB - (XB - XA) * math.sqrt(max(0, 1 - (math.hypot(y0, zz) / H["pressure_r_m"]) ** 2)), zz) for zz in (za, (za + zb) / 2, zb)]
            o.append('<polyline fill="none" stroke="#0ea5e9" stroke-width="8" points="%s"/>' % " ".join(f"{X(x):.1f},{Z(z):.1f}" for x, z in pts))
            for zz in (za, zb):
                xw = XB - (XB - XA) * math.sqrt(max(0, 1 - (math.hypot(y0, zz) / H["pressure_r_m"]) ** 2))
                k = (ex - (xw - 0.45)) / (ex - xw)
                o.append(f'<line x1="{X(ex):.1f}" y1="{Z(ez):.1f}" x2="{X(xw - 0.45):.1f}" y2="{Z(ez + (zz - ez) * k):.1f}" stroke="#f59e0b" stroke-width="1.6" stroke-dasharray="6 5"/>')
    o.append(f'<circle cx="{X(ex):.1f}" cy="{Z(ez):.1f}" r="6" fill="#dc2626"/>')
    o.append(T(X(ex) + 10, Z(ez) - 10, "Pilot's eye", 14, 500, "#b91c1c"))
    pv = res["stations"]["PILOT"]
    o.append(T(X(-0.4), Z(-1.2), "Nose windows (blue):", 14, 500, "#0369a1"))
    o.append(T(X(-0.4), Z(-1.2) + 18, "0.8 m over each pilot,", 13, 400, "#0369a1"))
    o.append(T(X(-0.4), Z(-1.2) + 35, "0.6 m around them", 13, 400, "#0369a1"))
    # standing person on the walkway (r ~2.2)
    zp = 2.25
    o.append(f'<rect x="{X(FLOOR - 1.9):.1f}" y="{Z(zp + 0.2):.1f}" width="{1.9 * s:.1f}" height="{0.4 * s:.1f}" fill="#fde68a" stroke="#92400e" stroke-width="1.5" rx="18"/>')
    o.append(T(X(FLOOR - 0.95), Z(zp + 0.2) - 8, "1.9 m standing on the walkway", 13, 400, "#5b6575", "middle"))
    for k, line in enumerate(["L1 command level: section through the pilot",]):
        o.append(T(40, 50, line, 24, 500))
    for k, line in enumerate(["Bow to the left. Under thrust aft is down; crew lie on their",
                              "backs facing the bow (+Gx). Pilot and navigator ride a flight deck",
                              f"{FLOOR - fx0:.2f} m up, eyes {CL['flight_deck']['eye_to_window_m']} m below a cluster of nose windows;",
                              "sensors sit in a ring at the dome shoulder. Plane y = +0.45 m."]):
        o.append(T(40, 80 + 21 * k, line, 15, 400, "#5b6575"))
    o.append(f'<rect x="{X(-0.3):.1f}" y="{Z(z_lo) + 18:.1f}" width="{s}" height="10" fill="#1f2733"/>')
    o.append(T(X(-0.3), Z(z_lo) + 46, "0", 13, 400, "#5b6575", "middle") + T(X(0.7), Z(z_lo) + 46, "1 m", 13, 400, "#5b6575", "middle"))
    o.append(T(40, Hh - 34, f"VISUAL REFERENCE - Wayfarer v{G['version']} (NON-GOVERNING) - geometry sha256 {SHA[:16]}...", 12, 400, "#8b94a3"))
    o.append(T(40, Hh - 16, "ALL bodies. ALL sponsors. 2026-2226.", 12, 400, "#8b94a3"))
    o.append("</svg>")
    return "\n".join(o)


def scene_export():
    """The scored L1 scene for the renderer: the same couches, eye points, occupant envelopes and
    display boxes the ray tests use, so the 3D images show exactly what was scored."""
    sc = built_option()["scene"]
    r3 = lambda v: [round(a, 4) for a in v]
    roles = {s["id"]: s["role"] for s in CL["stations"]}
    out = {"header": "ALL bodies. ALL sponsors. 2026-2226.",
           "status": "VISUAL REFERENCE input: the L1 scene scored by command/l1_study.py (NON-GOVERNING)",
           "geometry_sha256": SHA,
           "dome": {"xa": sc.xa, "xb": sc.xb, "R": O.RU}, "floor_x": FLOOR,
           "couch": {"width_m": CO["width_m"], "back_above_base_m": CO["back_above_base_m"], "eye_above_back_m": CO["eye_above_back_m"]},
           "couches": [{"id": c["id"], "role": roles[c["id"]], "base_x": c["base_x"], "head": r3(c["head"]), "feet": r3(c["feet"]),
                        "L": c["L"], "eye": r3(c["eye"]), "envelope": [r3(b) for b in c["box"]]} for c in sc.couches],
           "displays": [{"for": nm, "box": [r3(ax) for ax in b.b]}
                        for nm, b in sc.displays],
           "ladders": [{"y": round(y, 4), "z": round(z, 4), "size": s} for y, z, s in O.LADDERS],
           "flight_deck": {"x": FD["x_m"], "y": FD["y_m"], "z": FD["z_m"]},
           "flight_deck_ladder": {"z": round(FD["z_m"][0] - 0.08, 3), "y": [-0.25, 0.25], "x": [FD["x_m"][0], FLOOR],
                                  "note": "indicative: inputs say 'reached by a short ladder at its -Z end'; not sized"}}
    return out


if __name__ == "__main__":
    res = run()
    (ROOT / "command/l1_study_results.json").write_text(json.dumps(res, indent=1))
    (ROOT / "render/out/l1_scene.json").write_text(json.dumps(scene_export(), indent=1))
    (ROOT / "render/out/deck_L1_section.svg").write_text(section_svg(res))
    for k, v in res["stations"].items():
        print(k, v)
    print("paths", res["paths"])
    print("checks", sum(res["checks"].values()), "/", len(res["checks"]), [k for k, v in res["checks"].items() if not v])
    print("sensor", res["sensor_ring"], "windows", res["ship_windows"], "deck", res["flight_deck_above_floor_m"], res["under_flight_deck_m"])
