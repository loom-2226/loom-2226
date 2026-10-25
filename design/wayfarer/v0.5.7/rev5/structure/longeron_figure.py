# ALL bodies. ALL sponsors. 2026-2226. Summary figure for structure/longeron_study_results.json (NON-GOVERNING)
import json, math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Rectangle
from matplotlib import font_manager as fm
HERE = Path(__file__).resolve().parent
for f in ["Inter-Regular.otf", "Inter-SemiBold.otf"]:
    fm.fontManager.addfont("/usr/share/fonts/opentype/inter/" + f)
plt.rcParams["font.family"] = "Inter"
R = json.loads((HERE / "longeron_study_results.json").read_text())
L4, L5 = R["layouts"]["4"], R["layouts"]["5"]
BG, FG, MUT, ACC, OST, NODE = "#0d1018", "#e8edf5", "#9aa6b8", "#f0a03c", "#7fd17a", "#5fd0e6"
fig = plt.figure(figsize=(12, 19), dpi=160); fig.patch.set_facecolor(BG)
fig.text(0.04, 0.988, "Wayfarer longerons: four, sized, Osteon at the joints", color=FG, fontsize=27, fontweight="semibold", va="top")
fig.text(0.04, 0.966, "ALL bodies. ALL sponsors. 2026-2226.  NON-GOVERNING study; the v0.5.6 build is unchanged.", color=MUT, fontsize=15, va="top")

# (a) mass
ax = fig.add_axes([0.30, 0.74, 0.62, 0.17]); ax.set_facecolor(BG)
rows = [("Today (v0.5.6)\n5 longerons, no fittings", R["today"]["longeron_mass_t"], 0, "#8a93a3"),
        ("5 longerons, sized\n(planks buckle in the 18 cm gap)", L5["span_mass_t"], L5["fittings"]["conventional_t"], "#b9a37a"),
        ("4 tubes, sized\nconventional joints", L4["span_mass_t"], L4["fittings"]["conventional_t"], ACC),
        ("4 tubes, sized\nOsteon joints", L4["span_mass_t"], L4["fittings"]["osteon_t"]["central"], OST)]
for i, (lab, s, f, c) in enumerate(rows[::-1]):
    ax.barh(i, s, color=c, height=0.62); ax.barh(i, f, left=s, color=c, alpha=0.45, height=0.62, hatch="//", edgecolor=BG)
    ax.text(s + f + 0.6, i, f"{s + f:.1f} t", va="center", color=FG, fontsize=17, fontweight="semibold")
    ax.text(-1.0, i, lab, va="center", ha="right", color=FG, fontsize=14)
ax.set_xlim(0, 44); ax.set_yticks([]); ax.tick_params(colors=MUT, labelsize=12)
for s in ax.spines.values(): s.set_visible(False)
ax.set_xlabel("tonnes (solid: spans; hatched: fittings, node mounts and hatches, bay corners, strake housings)", color=MUT, fontsize=13)
fig.text(0.04, 0.932, f"1  Mass: about {L4['saving_vs_today_t']['central']:.0f} t could go back to the reserve", color=FG, fontsize=20, fontweight="semibold")

# (b) section
fig.text(0.04, 0.69, "2  Four tubes in an X, looking aft", color=FG, fontsize=20, fontweight="semibold")
ax = fig.add_axes([0.04, 0.36, 0.55, 0.32]); ax.set_facecolor(BG); ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-5.6, 5.6); ax.set_ylim(-5.6, 5.6)
ax.add_patch(Circle((0, 0), 4.5, fc="#20242c", ec="#cfd0cc", lw=2.5))
ax.add_patch(Wedge((0, 0), 4.3, 90 + 34, 90 - 34 + 360, width=1.85, fc="#3b4f6b", ec="none"))
ax.add_patch(Rectangle((-2.4, 2.0), 4.8, 2.6, fc="#11141a", ec="none")); ax.text(0, 3.3, "bay slot", ha="center", color=MUT, fontsize=13)
for k in range(16):
    t = math.radians(22.5 * k); ax.plot(4.95 * math.cos(t), 4.95 * math.sin(t), "o", ms=5, color=NODE)
for d in (40, 140, 220, 320):
    t = math.radians(d); c, s = math.cos(t), math.sin(t)
    ax.plot([4.25 * c + s, 4.25 * c - s], [4.25 * s - c, 4.25 * s + c], color="#555b66", lw=7, solid_capstyle="butt")
for m in L4["members"]:
    t = math.radians(m["azimuth_deg"]); r = math.hypot(2.75, 2.6)
    ax.add_patch(Circle((r * math.cos(t), r * math.sin(t)), 0.2, fc=ACC, ec="none"))
    ax.add_patch(Circle((r * math.cos(t), r * math.sin(t)), 0.2 - m["wall_mm"] / 1000, fc="#20242c", ec="none"))
tx = fig.add_axes([0.60, 0.36, 0.37, 0.32]); tx.axis("off")
m = L4["members"][0]; tq = L4["torsion"]
lines = [("Tubes", f"4 x CFRP, {m['D_m']:.2f} m dia, {m['wall_mm']:.0f} mm wall"),
         ("Stress at 5 g x 1.5", f"{m['stress_mpa']:.0f} MPa (design 250)"),
         ("Buckling between frames", f"{m['buckling_margin']:.0f}x (need 1.5)"),
         ("One longeron lost, 1 g", f"{L4['one_out_worst_mpa']:.0f} MPa, incl. bending"),
         ("First bending mode", f"{L4['first_bending_hz']:.1f} Hz (need 1.0)"),
         ("Twist: tank cell wall", f"{tq['cell_wall_shear_mpa']:.0f} MPa shear (allow 60)"),
         ("Twist: 0.8 m open bay end", f"{tq['portal_bending_mpa']:.0f} MPa in the tubes"),
         ("Tank volume", f"{L4['tank_volume_m3']:.1f} m3 (need 315)"),
         ("Strake roots", f"clear by {L4['strake_root_clearance_m'][0] * 100:.1f} cm"),
         ("Node azimuths", f"all 4 within {max(L4['node_azimuth_offset_deg']):.1f} deg")]
for i, (k, v) in enumerate(lines):
    tx.text(0, 1 - i * 0.1, k, color=MUT, fontsize=13, va="top"); tx.text(0, 1 - i * 0.1 - 0.045, v, color=FG, fontsize=14.5, va="top")
fig.text(0.04, 0.345, "Orange: longerons (upper pair edge the bay slot, as the sills do today). Blue dots: the 16 node azimuths. Grey: stowed strakes.",
         color=MUT, fontsize=12.5)

# (c) side strip
fig.text(0.04, 0.30, "3  Where Osteon structure goes (only at the joints)", color=FG, fontsize=20, fontweight="semibold")
ax = fig.add_axes([0.04, 0.10, 0.92, 0.18]); ax.set_facecolor(BG); ax.axis("off"); ax.set_xlim(-1, 55); ax.set_ylim(-3.5, 6)
ax.add_patch(Rectangle((0, -2.2), 34.3, 4.4, fc="#20242c", ec="#cfd0cc", lw=1.5))
ax.add_patch(Rectangle((34.3, -1.4), 19, 2.8, fc="#191c22", ec="#6a707c", lw=1))
for x0, x1, lab in ((0, 14, "habitat\n(its own pressure shell)"), (14, 34.3, "longerons x 14-34.3"), (34.3, 53.3, "thrust cone, shield, torch")):
    ax.text((x0 + x1) / 2, 4.6, lab, ha="center", color=MUT, fontsize=12.5)
ax.plot([14, 34.3], [1.6, 1.6], color=ACC, lw=5); ax.plot([14, 34.3], [-1.6, -1.6], color=ACC, lw=5)
for y in (1.15, -1.15): ax.plot([14, 34.3], [y, y], color="#cfd0cc", lw=1.4, ls=(0, (5, 4)))
ax.text(24.2, 0.0, "flush service bands along the longeron lines (node hatches)", ha="center", va="center", color="#cfd0cc", fontsize=11)
ax.add_patch(Rectangle((18, 1.75), 14.3, 0.45, fc="#11141a", ec="none")); ax.text(25.2, 2.55, "bay slot", ha="center", color=MUT, fontsize=11)
for x in (14, 34.3):
    for y in (1.6, -1.6): ax.plot(x, y, "s", ms=15, color=OST)
for x in (18, 32.3): ax.plot(x, 2.0, "^", ms=13, color=OST)
for s in L4["node_stations_on_longerons"]:
    for y in (1.6, -1.6): ax.plot(s, y, "o", ms=11, color=OST, mec=NODE, mew=2)
for k in range(13):
    s = 53.3 * (k + 0.5) / 13
    if not (14 < s < 34.3): ax.plot(s, 0, "o", ms=7, color=NODE, alpha=0.55)
f = L4["fittings"]
ax.text(0, -3.3, f"Squares: {f['end_fittings']} end fittings.  Triangles: {f['bay_corners']} bay-slot corners.  Circles: {f['node_mounts']} node mounts on the ring frames in the dry gap\n"
        f"(the longerons run inside the remass tank), reached through flush hatches.  Faint dots: node rings mounted by the habitat and torch structures.",
        color=MUT, fontsize=12, va="top")
fig.text(0.04, 0.025, "Osteon saving at the joints: about 1 t. Strake-root housings fix the v0.5.6 sill clash.\nThe big saving is the sizing itself: v0.5.6 longerons run at 65 MPa against 400.\n"
         "Caveats: all mass ahead of the cone is put on the longerons (conservative);\nnode-mount stiffness and alignment are unknown and could govern.",
         color=FG, fontsize=13)
fig.savefig(HERE / "longeron_study.png", facecolor=BG)
print("ok")
