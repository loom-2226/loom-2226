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
            r0, r1 = hab["room_r_m"]
            o.append(f'<path d="{sector(cx, cy, s, r0, r1, a0, a1)}" fill="{fill}" stroke="#4b5563" stroke-width="2"/>')
        if kind == "shelter":
            jac = hab["shelter_jacket"]["water_thickness_m"]
            r0, r1 = hab["room_r_m"]
            da = math.degrees(jac / ((r0 + r1) / 2))
            for p_ in (sector(cx, cy, s, r1 - jac, r1, a0, a1), sector(cx, cy, s, r0, r0 + jac, a0, a1),
                       sector(cx, cy, s, r0, r1, a0, a0 + da), sector(cx, cy, s, r0, r1, a1 - da, a1)):
                o.append(f'<path d="{p_}" fill="url(#hatch)" opacity="0.85"/>')
        if kind == "cabin":
            o.append(bed(cx, cy, s, 3.15, (a0 + a1) / 2, 1.9, 0.8))
        # label
        am = (a0 + a1) / 2
        if r["shape"]["k"] == "domecyl":
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
    # command deck stations
    if dk.get("dome"):
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
    if people:
        line += f'; {people} private cabins, each with a couch-bunk and a window'
    elif couches:
        line += f'; {couches} acceleration couches'
    o.append(text(60, 134, line, 17, 400, MUTED, "start"))
    o.append(text(W - 40, Hh - 40, f"VISUAL REFERENCE · Wayfarer v0.5 (NON-GOVERNING) · from wayfarer_v05_geometry.json sha256 {SHA[:16]}…", 12, 400, "#8b94a3", "end"))
    o.append(text(W - 40, Hh - 22, "ALL bodies. ALL sponsors. 2026-2226.", 12, 400, "#8b94a3", "end"))
    o.append("</svg>")
    return "\n".join(o), nhv


def overview(svgs):
    W, H = 2400, 1700
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="#f7f8fa"/>']
    o.append(text(60, 80, "Wayfarer v0.5 habitat: five decks for 6 crew and 4 guests", 40, 500, INK, "start"))
    nhv = sum(r["nhv_m3"] for r in G["rooms"])
    o.append(text(60, 122, f"Pressure vessel 8.6 m across, x 0.2-13.7 m. Net habitable volume {nhv:.0f} m³ ({nhv / 10:.1f} m³ per person). 16 windows, 16 couches, two ladders per deck.", 22, 400, MUTED, "start"))
    pos = [(60, 170), (860, 170), (1660, 170), (460, 930), (1260, 930)]
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
