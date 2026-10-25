"""Deck plans for Wayfarer v0.5 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX, VISUAL REFERENCE. Draws one SVG plan per deck from the rooms
and features in out/wayfarer_v05_geometry.json, plus an overview sheet.
Plan view looks aft (down, under thrust): +Z (slot side) at the top, starboard on the left.
Usage: python deckplans.py"""
import hashlib, json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
G = json.loads((ROOT / "out/wayfarer_v05_geometry.json").read_text())
I = json.loads((ROOT / "inputs/wayfarer_v05_inputs.json").read_text())
SHA = hashlib.sha256((ROOT / "out/wayfarer_v05_geometry.json").read_bytes()).hexdigest()
OUT = HERE / "out"
FILL = {"command": "#7cc4bf", "galley": "#efc27a", "wardroom": "#f1a97c", "observation": "#a8d2f0", "exercise": "#a9d49a",
        "hygiene": "#c6e3ef", "cabin": "#a9bdf0", "cabin_guest": "#c9b8ec", "shelter": "#8d9ab8", "medical": "#f0a3aa",
        "eclss": "#aac3b0", "airlock": "#f3df8a", "suits": "#f2c98d", "workshop": "#cdb59c", "custody": "#c98a8c",
        "stores": "#e4dccb", "vestibule": "#d9dde2", "corridor": "#eceef1"}
INK, MUTED = "#1f2733", "#5b6575"


def P(cx, cy, s, r, th):
    t = math.radians(th)
    return cx - r * math.cos(t) * s, cy - r * math.sin(t) * s


def sector(cx, cy, s, r0, r1, a0, a1, n=None):
    span = a1 - a0
    n = n or max(8, int(abs(span) / 2))
    pts = [P(cx, cy, s, r1, a0 + span * k / n) for k in range(n + 1)]
    if r0 > 0:
        pts += [P(cx, cy, s, r0, a1 - span * k / n) for k in range(n + 1)]
    else:
        pts.append((cx, cy))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


def text(x, y, t, size=16, w=500, color=INK, anchor="middle"):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{w}" fill="{color}" text-anchor="{anchor}" font-family="Helvetica Neue, Arial, sans-serif">{t}</text>'


def bed(cx, cy, s, r, th, L=2.0, W=0.9):
    t = math.radians(th)
    ux, uy = -math.cos(t), -math.sin(t)
    vx, vy = -uy, ux
    x, y = P(cx, cy, s, r, th)
    pts = [(x + (a * ux * L / 2 + b * vx * W / 2) * s, y + (a * uy * L / 2 + b * vy * W / 2) * s) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return f'<path d="M{" L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)} Z" fill="#ffffff" stroke="#6b7b99" stroke-width="1.5"/>'


def deck_svg(dk, W=1200, Hh=1320, s=112, small=False):
    cx, cy = W / 2, 690
    if dk.get("command_layout"):
        Hh = 1400
    hab = I["habitat"]
    rooms = [r for r in G["rooms"] if r["deck"] == dk["id"]]
    feats = [f for f in G["features"] if f.get("room", "").startswith(dk["id"] + "-")]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">',
         f'<rect width="{W}" height="{Hh}" fill="#f7f8fa"/>',
         '<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="#5c8fd6"/><line x1="0" y1="0" x2="0" y2="8" stroke="#3a6fb8" stroke-width="3"/></pattern></defs>']
    Ro, Rp, Ru = I["hull"]["outer_r_m"], I["hull"]["pressure_r_m"], hab["usable_r_m"]
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{Ro * s}" fill="#c9ccd2"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{Rp * s}" fill="#ffffff" stroke="{INK}" stroke-width="4"/>')
    nhv = 0.0
    for r in rooms:
        nhv += r["nhv_m3"]
        kind = r["kind"]
        fill = FILL.get("cabin_guest" if (kind == "cabin" and r.get("who") == "guest") else kind, "#dddddd")
        a0, a1 = r["theta_deg"]
        if kind == "corridor":
            cr = hab["corridor_r_m"]
            o.append(f'<path d="{sector(cx, cy, s, cr[0], cr[1], 0, 360)}" fill="{fill}" stroke="#9aa3af" stroke-width="1.5"/>')
            continue
        if r["shape"]["k"] == "domecyl":
            o.append(f'<circle cx="{cx}" cy="{cy}" r="{Ru * s}" fill="{fill}" stroke="#4b5563" stroke-width="2"/>')
        else:
            r0, r1 = (r["shape"]["r0"], r["shape"]["r1"]) if r["shape"]["k"] == "sector" and not r.get("jacket") and kind != "shelter" else hab["room_r_m"]
            o.append(f'<path d="{sector(cx, cy, s, r0, r1, a0, a1)}" fill="{fill}" stroke="#4b5563" stroke-width="2"/>')
        if kind == "shelter":
            jac = hab["shelter_jacket"]["water_thickness_m"]
            r0, r1 = hab["room_r_m"]
            da = math.degrees(jac / ((r0 + r1) / 2))
            for p_ in (sector(cx, cy, s, r1 - jac, r1, a0, a1), sector(cx, cy, s, r0, r0 + jac, a0, a1),
                       sector(cx, cy, s, r0, r1, a0, a0 + da), sector(cx, cy, s, r0, r1, a1 - da, a1)):
                o.append(f'<path d="{p_}" fill="url(#hatch)" opacity="0.85"/>')
        if kind == "cabin" and r.get("bunks"):
            for b in r["bunks"]:
                rb = (b["radial_m"][0] + b["radial_m"][1]) / 2
                o.append(bed(cx, cy, s, rb, b["angle_deg"], b["radial_m"][1] - b["radial_m"][0], b["width_m"]))
                if b["tiers"] > 1:
                    bx, by = P(cx, cy, s, b["radial_m"][1] - 0.35, b["angle_deg"])
                    o.append(text(bx, by + 5, f'x{b["tiers"]}', 13, 500, "#3b4a6b"))
        elif kind == "cabin":
            o.append(bed(cx, cy, s, 3.15, (a0 + a1) / 2, 1.9, 0.8))
        for dd in [r.get("door"), r.get("entrance")]:
            if dd:
                rr_ = dd.get("at_r_m", hab["corridor_r_m"][1])
                half = math.degrees(dd["clear_width_m"] / 2 / rr_)
                c_ = dd["center_deg"]
                o.append(f'<path d="{sector(cx, cy, s, rr_ - 0.06, rr_ + 0.06, c_ - half, c_ + half, 10)}" fill="#ffffff" stroke="#d97706" stroke-width="2"/>')
        # label
        am = (a0 + a1) / 2
        if r["shape"]["k"] == "domecyl" and dk.get("command_layout", {}).get("flight_deck"):
            lx, ly = cx, cy + 2.42 * s
        elif r["shape"]["k"] == "domecyl" and dk.get("command_layout"):
            lx, ly = cx, cy - 3.05 * s
        elif r["shape"]["k"] == "domecyl":
            lx, ly = cx, cy - 0.9 * s
        else:
            rr = {"cabin": 3.15, "vestibule": 2.25}.get(kind, 2.95)
            lx, ly = P(cx, cy, s, rr, am)
        name = r["name"].replace("Crew cabin ", "Crew ").replace("Guest cabin ", "Guest ")
        span = (a1 - a0)
        fs = 15 if span <= 40 else 17
        words = name.split(" ")
        if kind == "cabin":
            o.append(text(lx, ly - 2, name, 15))
            o.append(text(lx, ly + 16, f'{r["volume_m3"]:.1f} m³', 12, 400, MUTED))
        elif span <= 40 and len(words) > 1:
            o.append(text(lx, ly - 8, words[0], fs))
            o.append(text(lx, ly + 10, " ".join(words[1:]), fs))
            o.append(text(lx, ly + 28, f'{r["volume_m3"]:.1f} m³', 13, 400, MUTED))
        else:
            o.append(text(lx, ly, name, fs))
            o.append(text(lx, ly + 19, f'{r["volume_m3"]:.1f} m³ · {r["nhv_m3"]:.1f} m³ free', 13, 400, MUTED))
    bs = hab.get("berth_shield")
    if bs and bs["deck"] == dk["id"]:
        o.append(f'<path d="{sector(cx, cy, s, bs["r_m"][0], bs["r_m"][1], 0, 360, 180)}" fill="url(#hatch)" opacity="0.9"/>')
        o.append(text(cx, cy - Rp * s - 4, "8 cm water ring (berth shield)", 13, 500, "#2b5ea8"))
    # command deck stations
    CLy = dk.get("command_layout")
    if dk.get("dome") and CLy:
        Q = lambda y, z: (cx - y * s, cy - z * s)
        ring_r = CLy.get("sensor_ring", {}).get("r_in_m") or CLy.get("sensor_bore_r_m")
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{ring_r * s:.1f}" fill="none" stroke="#6d5aa8" stroke-width="2" stroke-dasharray="10 6"/>')
        pl = CLy.get("flight_deck") or CLy["platform"]
        (ax, ay), (bx_, by_) = Q(pl["y_m"][1], pl["z_m"][1]), Q(pl["y_m"][0], pl["z_m"][0])
        o.append(f'<rect x="{min(ax, bx_):.1f}" y="{min(ay, by_):.1f}" width="{abs(bx_ - ax):.1f}" height="{abs(by_ - ay):.1f}" fill="#e5e7eb" stroke="#4b5563" stroke-width="2.5" stroke-dasharray="{"12 6" if "flight_deck" in CLy else "none"}"/>')
        if "flight_deck" in CLy:
            lx0, ly0 = Q(0.3, pl["z_m"][0] - 0.05)
            lx1, ly1 = Q(-0.3, pl["z_m"][0] - 0.45)
            o.append(f'<rect x="{min(lx0, lx1):.1f}" y="{min(ly0, ly1):.1f}" width="{abs(lx1 - lx0):.1f}" height="{abs(ly1 - ly0):.1f}" fill="#fff7d6" stroke="#8a6d00" stroke-width="2"/>')
            o.append(text((lx0 + lx1) / 2, max(ly0, ly1) + 18, "Ladder up", 13, 500, "#6b5600"))
        cw = CLy["couch"]["width_m"]
        for st in CLy["stations"]:
            (hy, hz), (fy, fz) = st["head_yz_m"], st["feet_yz_m"]
            L = math.hypot(fy - hy, fz - hz); uy, uz = (fy - hy) / L, (fz - hz) / L; vy, vz = -uz, uy
            pts = [Q(y + sg * cw / 2 * vy, z + sg * cw / 2 * vz) for (y, z) in ((hy, hz), (fy, fz)) for sg in ((-1, 1) if (y, z) == (hy, hz) else (1, -1))]
            fwd = st["base"] in ("platform", "flight_deck")
            o.append(f'<path d="M{" L".join(f"{a:.1f},{b:.1f}" for a, b in pts)} Z" fill="{"#ffffff" if not fwd else "#dbeafe"}" stroke="{"#1d4ed8" if fwd else "#3b6b68"}" stroke-width="2.5" />')
            ex, ey = Q(hy + uy * CLy["couch"]["eye_from_head_end_m"], hz + uz * CLy["couch"]["eye_from_head_end_m"])
            o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="7" fill="#dc2626"/>')
            mx, my = Q(hy + uy * L * 0.6, hz + uz * L * 0.6)
            o.append(text(mx, my + 5, st["id"], 14, 500, "#1d4ed8" if fwd else "#3b6b68"))
        if CLy.get("crown_dome", {}).get("adopted"):   # v0.5.7: crown dome overhead
            cr = CLy["crown_dome"]["r_m"]
            qx, qy = Q(0.0, 0.0)
            o.append(f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="{cr * s:.1f}" fill="none" stroke="#0284c7" stroke-width="3" stroke-dasharray="8 5"/>')
            o.append(text(qx, qy - cr * s - 10, f"Crown dome overhead (r {cr} m)", 14, 500, "#0369a1"))
        for w in ([] if CLy.get("crown_dome", {}).get("adopted") else CLy["forward_windows"]):
            wx, wy = Q(*w["yz_m"])
            o.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{w["d_m"] / 2 * s:.1f}" fill="none" stroke="#0284c7" stroke-width="3" stroke-dasharray="6 4"/>')
        for lw in hab["ladderways"]:
            x, y = P(cx, cy, s, lw["r_m"], lw["theta_deg"])
            h = lw["size_m"] * s
            o.append(f'<rect x="{x - h / 2:.1f}" y="{y - h / 2:.1f}" width="{h:.1f}" height="{h:.1f}" fill="#fff7d6" stroke="#8a6d00" stroke-width="2"/>')
            o.append(text(x, y + 5, "Ladder", 13, 500, "#6b5600"))
    elif dk.get("dome"):
        for k, th in enumerate([30, 70, 110, 150, 210, 330]):
            x, y = P(cx, cy, s, 3.15, th)
            o.append(f'<rect x="{x - 0.45 * s:.1f}" y="{y - 0.3 * s:.1f}" width="{0.9 * s:.1f}" height="{0.6 * s:.1f}" rx="10" fill="#ffffff" stroke="#3b6b68" stroke-width="2"/>')
        o.append(text(cx, cy + 0.15 * s, "6 couch stations, facing forward", 15, 400, MUTED))
        o.append(text(cx, cy + 0.55 * s, "Bow sensors and electronics fill the nose", 14, 400, MUTED))
        o.append(text(cx, cy + 0.85 * s, "ahead of this deck (x 0.2-1.0 m)", 14, 400, MUTED))
    else:
        cr = hab["core_r_m"]
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{cr * s}" fill="#6b7280" stroke="#374151" stroke-width="2"/>')
        o.append(text(cx, cy - 4, "Trunk", 15, 500, "#ffffff"))
        o.append(text(cx, cy + 14, "lift, utilities", 12, 400, "#e5e7eb"))
        for lw in hab["ladderways"]:
            x, y = P(cx, cy, s, lw["r_m"], lw["theta_deg"])
            h = lw["size_m"] * s
            o.append(f'<rect x="{x - h / 2:.1f}" y="{y - h / 2:.1f}" width="{h:.1f}" height="{h:.1f}" fill="#fff7d6" stroke="#8a6d00" stroke-width="2"/>')
            for k in range(1, 4):
                yy = y - h / 2 + h * k / 4
                o.append(f'<line x1="{x - h / 2 + 6:.1f}" y1="{yy:.1f}" x2="{x + h / 2 - 6:.1f}" y2="{yy:.1f}" stroke="#8a6d00" stroke-width="2"/>')
            o.append(text(x, y + h / 2 + 16, "Ladder", 13, 500, "#6b5600"))
    # windows, hatches
    for f in feats:
        if f.get("forward"):
            continue          # nose windows are drawn as dashed circles overhead
        th = math.degrees(math.atan2(f["pos"][2], f["pos"][1]))
        span = math.degrees(f["d_m"] / Rp)
        o.append(f'<path d="{sector(cx, cy, s, Rp - 0.04, Rp + 0.16, th - span / 2, th + span / 2, 6)}" fill="#2b6cb0"/>')
    if dk["id"] == I["habitat"]["decks"][-1]["id"]:
        for f in G["features"]:
            if f["kind"] == "hatch":
                th = math.degrees(math.atan2(f["pos"][2], f["pos"][1]))
                span = math.degrees(f["d_m"] / Ro)
                o.append(f'<path d="{sector(cx, cy, s, Rp, Ro, th - span / 2, th + span / 2, 8)}" fill="#e0b400" stroke="#8a6d00" stroke-width="2"/>')
                x, y = P(cx, cy, s, 3.25, th)
                o.append(text(x, y + 48, "outer hatch at the hull", 13, 500, "#6b5600"))
        seg = I["service"]["tunnel"]["segments"][0]["from"]
        th = math.degrees(math.atan2(seg[2], seg[1]))
        x, y = P(cx, cy, s, math.hypot(seg[1], seg[2]), th)
        d = I["service"]["tunnel"]["d_m"] * s
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{d / 2:.1f}" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="8 5"/>')
        o.append(text(x, y + d / 2 + 18, "Floor hatch: tunnel aft to collar and shuttle", 13, 500))
    # orientation and scale
    o.append(text(cx, cy - Ro * s - 22, "+Z  slot side", 15, 500, MUTED))
    o.append(text(cx, cy + Ro * s + 34, "-Z  docking side", 15, 500, MUTED))
    o.append(text(cx - Ro * s - 14, cy - 18, "Starboard", 15, 500, MUTED, "end"))
    o.append(text(cx + Ro * s + 14, cy - 18, "Port", 15, 500, MUTED, "start"))
    x0, y0 = 70, Hh - 70
    o.append(f'<rect x="{x0}" y="{y0}" width="{s}" height="10" fill="{INK}"/><rect x="{x0 + s}" y="{y0}" width="{s}" height="10" fill="#ffffff" stroke="{INK}"/>')
    o.append(text(x0, y0 + 30, "0", 13, 400, MUTED) + text(x0 + s, y0 + 30, "1", 13, 400, MUTED) + text(x0 + 2 * s, y0 + 30, "2 m", 13, 400, MUTED))
    # title block
    x0d, x1d = dk["x_m"]
    people = sum(1 for r in rooms if r["kind"] == "cabin")
    couches = sum(r["couches"] for r in rooms)
    o.append(text(60, 70, f'{dk["id"]}  {dk["name"]}', 34, 500, INK, "start"))
    o.append(text(60, 106, f'Deck x {x0d}-{x1d} m from the bow; floor at x {x1d} m; clear height {hab["clear_height_m"]} m. Looking aft (down under thrust).', 17, 400, MUTED, "start"))
    line = f'Net habitable volume on this deck {nhv:.0f} m³'
    occ = sum(r.get("occupancy", 0) for r in rooms if r["kind"] == "cabin")
    if people and occ:
        line += f'; {people} cabins with {occ} berths ({sum(len(r.get("bunks", [])) for r in rooms)} bunk footprints, 5 g restraints); 8 cm water ring'
    elif people:
        line += f'; {people} private cabins, each with a couch-bunk and a window'
    elif couches:
        line += f'; {couches} acceleration couches'
    o.append(text(60, 134, line, 17, 400, MUTED, "start"))
    if dk.get("command_layout"):
        yb = cy + Ro * s + 72
        if "flight_deck" in CLy:
            o.append(text(60, yb, f"Grey dashed: flight deck {3.0 - CLy['flight_deck']['x_m'][0]:.2f} m up, carrying PILOT and NAV on their backs facing the bow; four support couches lie along the rim.", 15, 400, MUTED, "start"))
            o.append(text(60, yb + 22, "Purple dashed: inner edge of the sensor ring overhead. Blue dashed: the eight nose windows. Red: eye points.", 15, 400, MUTED, "start"))
        else:
            o.append(text(60, yb, "Pilot and navigator on a 1.2 m platform, on their backs facing the bow; four support couches on the floor.", 15, 400, MUTED, "start"))
            o.append(text(60, yb + 22, "Purple dashed: 2.5 m viewing bore through the sensor ring overhead. Blue dashed: the two 0.8 m nose windows. Red: eye points.", 15, 400, MUTED, "start"))
    o.append(text(W - 40, Hh - 40, f"VISUAL REFERENCE · Wayfarer v{G['version']} (NON-GOVERNING) · from wayfarer_v05_geometry.json sha256 {SHA[:16]}…", 12, 400, "#8b94a3", "end"))
    o.append(text(W - 40, Hh - 22, "ALL bodies. ALL sponsors. 2026-2226.", 12, 400, "#8b94a3", "end"))
    o.append("</svg>")
    return "\n".join(o), nhv


def overview(svgs):
    W, H = 2400, 1870
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="#f7f8fa"/>']
    o.append(text(60, 80, f"Wayfarer v{G['version']} habitat: five decks for 6 crew and 4 guests", 40, 500, INK, "start"))
    nhv = sum(r["nhv_m3"] for r in G["rooms"])
    o.append(text(60, 122, f"Pressure vessel 8.6 m across, x 0.2-13.7 m. Net habitable volume {nhv:.0f} m³ ({nhv / 10:.1f} m³ per person). {sum(len([f for f in G["features"] if f["kind"] == "window"]) for _ in [0])} windows, {sum(r["couches"] for r in G["rooms"])} couches and berths, two ladders per deck.", 22, 400, MUTED, "start"))
    pos = [(60, 170), (860, 170), (1660, 170), (460, 1000), (1260, 1000)]
    for (x, y), (svg, dk) in zip(pos, svgs):
        inner = svg.split("\n", 1)[1].rsplit("</svg>", 1)[0]
        o.append(f'<g transform="translate({x},{y}) scale(0.6)">{inner}</g>')
    o.append(text(W - 40, H - 24, f"VISUAL REFERENCE · from wayfarer_v05_geometry.json sha256 {SHA[:16]}… · ALL bodies. ALL sponsors. 2026-2226.", 16, 400, "#8b94a3", "end"))
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    made = []
    for dk in I["habitat"]["decks"]:
        svg, nhv = deck_svg(dk)
        (OUT / f"deck_{dk['id']}.svg").write_text(svg)
        made.append((svg, dk))
        print(dk["id"], f"{nhv:.0f} m3")
    (OUT / "deck_overview.svg").write_text(overview(made))
