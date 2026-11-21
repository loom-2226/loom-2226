"""Picture for interior_pack.json. ALL bodies. ALL sponsors. 2026-2226."""
import json, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle, FancyBboxPatch
import b5_concept as C, interior_pack as IP
d = json.load(open("interior_pack.json")); Z = IP.Z
COL = {"cabin": "#5dade2", "water": "#1f618d", "rover well": "#f5b041", "aft systems": "#922b21", "door path/ramp": "#fad7a0",
       "avionics/sensors": "#7d3c98", "life support/equipment": "#a569bd"}
fig = plt.figure(figsize=(17, 10.5)); fig.patch.set_facecolor("#f7f7f5")
# side view: profile from sections (top = ridge, bottom = keel) on the centreline
xs = np.linspace(0, 12.8, 200); top = [C.section(x)[0][1] for x in xs]; bot = [C.section(x)[4][1] for x in xs]
ti = [IP.inset(C.section(x), .2)[0][1] if x > .4 else 0 for x in xs]; bi = [IP.inset(C.section(x), .1)[4][1] if x > .4 else 0 for x in xs]
a = fig.add_axes([0.03, 0.55, 0.62, 0.38])
a.fill_between(xs, bot, top, color="#d5d8dc"); a.plot(xs, top, "k", lw=1); a.plot(xs, bot, "k", lw=1)
def band(x0, x1, z0f, z1f, col, label=None):
    m = (xs >= x0) & (xs <= x1); lo = np.maximum(np.array(bi)[m], z0f); hi = np.minimum(np.array(ti)[m], z1f)
    a.fill_between(xs[m], lo, hi, color=col, alpha=.9, lw=0)
    if label: a.text((x0 + x1) / 2, (np.mean(lo) + np.mean(hi)) / 2, label, ha="center", va="center", fontsize=8, color="w", weight="bold")
band(*Z["nose"], -9, 9, COL["avionics/sensors"], "avionics\nsensors")
band(*Z["cabin"], IP.FLOOR_CAB, 9, COL["cabin"], ""); band(*Z["cabin"], -9, IP.FLOOR_CAB, COL["water"], "water (belly)")
band(*Z["well"], IP.FLOOR_WELL, IP.ROVER_TOP, COL["rover well"], ""); band(*Z["well"], -9, IP.FLOOR_WELL - .05, COL["water"], "")
band(*Z["well"], IP.ROVER_TOP, 9, COL["life support/equipment"], "life support")
band(*Z["shield"], -9, 9, COL["water"], "water\nshield"); band(*Z["aft"], -9, 9, COL["aft systems"], "reactor\ntorch")
a.add_patch(Rectangle((12.8, -0.25), 0.9, 1.1, color="#566573")); a.text(13.25, -.45, "nozzle", ha="center", fontsize=7)
# couches (reclined ~60 deg), 2 rows
for x0 in (3.1, 5.2):
    a.plot([x0, x0 + 1.25, x0 + 1.75], [-0.35, -0.2, 0.75], color="k", lw=4, solid_capstyle="round")
    a.add_patch(Circle((x0 + 1.85, 0.95), 0.13, color="#f0b27a"))
a.text(4.4, 1.2, "6 reclined couches (2 rows of 3)", fontsize=8, ha="center"); a.text(7.5, 0.3, "hygiene\ngalley", fontsize=7, ha="center")
# rover capsule in the well
a.add_patch(FancyBboxPatch((8.0, -0.75), 3.0, 1.9, boxstyle="round,pad=0,rounding_size=.9", fc="#d4ac0d", ec="k"))
a.text(9.5, 0.2, "rover / Ti capsule\n(floodable well)", ha="center", fontsize=8)
a.set_xlim(-0.2, 13.9); a.set_ylim(-1.6, 2.4); a.set_aspect("equal"); a.axis("off")
a.set_title("Side view (centreline), nose left", loc="left", fontsize=11, weight="bold")
# sections
def section_ax(rect, x, title, kind):
    s = fig.add_axes(rect); outer = np.array(C.section(x)); o1 = IP.inset(C.section(x), .1); o2 = IP.inset(C.section(x), .2)
    s.add_patch(Polygon(outer, fc="#d5d8dc", ec="k"))
    yy, zz = np.meshgrid(np.linspace(-2.2, 2.2, 160), np.linspace(-1.4, 2.1, 140)); from matplotlib.path import Path
    P1, P2 = Path(o1), Path(o2); pts = np.c_[yy.ravel(), zz.ravel()]; i1, i2 = P1.contains_points(pts), P2.contains_points(pts)
    for (y, z), a1, a2 in zip(pts, i1, i2):
        if not a1: continue
        k = IP.classify(x, y, z)
        if k == "cabin" and not a2: continue
        s.add_patch(Rectangle((y - .014, z - .013), .028, .026, color=COL.get(k, "#bbb"), lw=0))
    if kind == "cabin":
        for y in (-1.0, 0.0, 1.0): s.add_patch(FancyBboxPatch((y - .3, IP.FLOOR_CAB + .05), .6, .55, boxstyle="round,pad=.02", fc="#2c3e50", ec="none"))
        s.text(0, 1.3, "3 couches abreast", ha="center", fontsize=8)
    else:
        s.add_patch(Circle((0, 0.2), 0.95, fc="#d4ac0d", ec="k")); s.text(0, .2, "capsule\n1.9 m", ha="center", va="center", fontsize=8)
        for y in (-.75, .75): s.add_patch(Circle((y, -0.55), .22, fc="#333"))
        s.annotate("side door + ramp", (1.95, -.3), (2.3, -1.25), fontsize=8, arrowprops={"arrowstyle": "->"})
        s.text(-1.55, -.2, "water", fontsize=7, color="w", rotation=90)
    s.set_xlim(-2.6, 2.6); s.set_ylim(-1.5, 2.2); s.set_aspect("equal"); s.axis("off"); s.set_title(title, fontsize=10, weight="bold")
section_ax([0.67, 0.55, 0.15, 0.38], 5.5, "Section x 5.5 m (cabin)", "cabin")
section_ax([0.83, 0.55, 0.15, 0.38], 9.5, "Section x 9.5 m (well)", "well")
# budget
b = fig.add_axes([0.20, 0.06, 0.42, 0.38]); keys = list(d["demand_m3"]); dem = [d["demand_m3"][k] for k in keys]; sup = [d["supply_m3"][k] for k in keys]
y = np.arange(len(keys)); b.barh(y - .2, dem, .38, color="#bdc3c7", label="needed"); b.barh(y + .2, sup, .38, color="#2e86c1", label="fits in B5")
for i, (dd, ss) in enumerate(zip(dem, sup)): b.text(max(dd, ss) + .4, i, f"{ss - dd:+.1f} m³", va="center", fontsize=9, color="#27ae60" if ss >= dd else "#c0392b")
b.set_yticks(y); b.set_yticklabels(keys, fontsize=9); b.invert_yaxis(); b.set_xlabel("m³"); b.legend(fontsize=8, loc="lower right"); b.set_xlim(0, 33)
b.set_title("Volume budget: it closes to within ~1 m³ (water)", fontsize=11, weight="bold")
t = fig.add_axes([0.66, 0.06, 0.32, 0.38]); t.axis("off")
notes = ["Water wraps the people: belly under the cabin floor,", "port side and roof of the well, and a shield slab", "between the well and the reactor/torch.",
         "Low water = low centre of gravity: helps it float upright.", "", "Short ~1 m³ of water (holds ~22.1 t vs 23.1 t)", "→ trim the well (+2 m³ spare) in the next pass.",
         "", "Wings fold onto the upper flanks as on B4 (no", "internal volume); floats pack into the flanks.", "Fans sit in the wings (fan-in-wing, blowing the flaps)."]
for i, n in enumerate(notes): t.text(0, .95 - i * .085, n, fontsize=9.5, transform=t.transAxes)
fig.suptitle("Shuttle v3 step 4: first interior packaging of the B5 concept", fontsize=14, y=.99)
fig.savefig("interior_pack.png", dpi=110, facecolor=fig.get_facecolor())
