# ALL bodies. ALL sponsors. 2026-2226. Concept figure: shielded berth viewports (NON-GOVERNING; nothing in the build changes)
import json, math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, Wedge
from matplotlib import font_manager as fm
ROOT = Path(__file__).resolve().parent.parent
for f in ["Inter-Regular.otf", "Inter-SemiBold.otf"]:
    fm.fontManager.addfont("/usr/share/fonts/opentype/inter/" + f)
plt.rcParams["font.family"] = "Inter"
I = json.loads((ROOT / "inputs/wayfarer_v05_inputs.json").read_text())
BG, FG, MUT = "#0d1018", "#e8edf5", "#9aa6b8"
WATER, ACR, ARM, PH, GLASS = "#2f6fb5", "#9fe3f0", "#8c7a5b", "#9aa0aa", "#cfeff7"
fig = plt.figure(figsize=(12, 18), dpi=160); fig.patch.set_facecolor(BG)
fig.text(0.04, 0.985, "Shielded viewports for the berths", color=FG, fontsize=28, fontweight="semibold", va="top")
fig.text(0.04, 0.962, "ALL bodies. ALL sponsors. 2026-2226.  Wayfarer v0.5.7 candidate, NON-GOVERNING.", color=MUT, fontsize=15, va="top")

# ---------- (1) section through the berth wall
fig.text(0.04, 0.935, "1  Section through the hull at one berth (looking along the deck)", color=FG, fontsize=19, fontweight="semibold")
ax = fig.add_axes([0.04, 0.50, 0.92, 0.42]); ax.set_facecolor(BG); ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(2.55, 5.2); ax.set_ylim(8.45, 5.75)    # x along the ship downward (floor at x 8.2 under 1 g thrust)
ax.add_patch(Rectangle((1.9, 8.2), 2.17, 0.12, fc="#3a3f49"))                     # floor L3
ax.text(2.62, 8.37, "floor L3", color=MUT, fontsize=12)
for top, lab in ((7.94, "lower berth"), (6.86, "upper berth")):
    ax.add_patch(Rectangle((1.925, top), 2.1, 0.12, fc="#55657c"))                  # mattress
    ax.add_patch(Rectangle((1.925, top + 0.12), 2.1, 0.14, fc="#2a2f38"))           # berth frame
    ax.text(2.62, top + 0.10, lab, color=FG, fontsize=12, va="center")
D = 0.35
for xc in (7.55, 6.45):
    # berth water ring with an acrylic insert
    ax.add_patch(Rectangle((4.07, 5.9), 0.08, 2.3, fc=WATER, ec="none"))
    # pressure hull and armour
    ax.add_patch(Rectangle((4.27, 5.9), 0.03, 2.3, fc=PH, ec="none"))
    ax.add_patch(Rectangle((4.30, 5.9), 0.20, 2.3, fc=ARM, ec="none"))
for xc in (7.55, 6.45):
    ax.add_patch(Rectangle((4.07, xc - D / 2), 0.08, D, fc=ACR, ec="none"))
    sp = math.tan(math.radians(12))
    ax.add_patch(Polygon([(4.30, xc - D / 2), (4.50, xc - D / 2 - 0.2 * sp), (4.50, xc + D / 2 + 0.2 * sp), (4.30, xc + D / 2)], fc=ACR, ec="none"))
    ax.add_patch(Rectangle((4.27, xc - D / 2), 0.03, D, fc=GLASS, ec="none"))
    ax.add_patch(Rectangle((4.15, xc - D / 2), 0.12, D, fc="#151a22", ec="#4a5262", lw=0.8))   # sealed light tunnel through the utility gap
    ax.add_patch(Rectangle((4.505, xc - D / 2 - 0.06), 0.012, D + 0.12, fc="#e8edf5", ec="none"))   # outer debris pane
    ax.add_patch(Rectangle((4.53, xc + D / 2 + 0.07), 0.03, 0.42, fc="#6b7280", ec="none"))       # dust shutter, open (slid aft)
    ax.add_patch(Rectangle((4.035, xc - D / 2), 0.012, D, fc="#c9a86a", ec="none"))               # blind
    ax.annotate("", xy=(3.2, xc), xytext=(4.9, xc), arrowprops=dict(arrowstyle="<-", color="#ffd27a", lw=1.6, ls="--"))
lab = [(3.85, 5.83, "berth water ring\n8 cm = 8 g/cm²", "#6fa8e8"), (4.62, 5.83, "armour 20 cm\n= 27 g/cm²", "#c7b48e"),
       (4.285, 8.43, "pressure hull", PH)]
for x, y, t, c in lab: ax.text(x, y, t, color=c, fontsize=12, ha="center", va="bottom" if y < 6 else "top")
notes = [((4.11, 6.40), (3.35, 6.08), "acrylic insert, 7 cm = 8 g/cm²\n(replaces the ring's water)"),
         ((4.40, 7.25), (4.85, 6.1), "acrylic plug, 23 cm = 27 g/cm²\n(fills the 12° splayed bore)"),
         ((4.285, 7.62), (4.75, 8.0), "pressure panes"),
         ((4.545, 6.85), (4.95, 6.95), "dust shutter\n(open)"),
         ((4.04, 7.62), (3.4, 7.7), "blind")]
for (xa, ya), (xt, yt), t in notes:
    ax.annotate(t, xy=(xa, ya), xytext=(xt, yt), color=FG, fontsize=12, ha="center",
                arrowprops=dict(arrowstyle="-", color="#cfe0ff", lw=1))
ax.text(3.2, 6.40, "line of sight", color="#ffd27a", fontsize=12)
ax.plot([4.6, 5.1], [8.38, 8.38], color=FG, lw=2); ax.text(4.85, 8.35, "0.5 m", color=FG, fontsize=11, ha="center", va="bottom")

# ---------- (2) plan of L3
fig.text(0.04, 0.475, "2  Deck L3: one viewport at the outer end of every berth", color=FG, fontsize=19, fontweight="semibold")
ax = fig.add_axes([0.04, 0.17, 0.52, 0.30]); ax.set_facecolor(BG); ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
ax.add_patch(Circle((0, 0), 4.5, fc="#8c7a5b", ec="none")); ax.add_patch(Circle((0, 0), 4.3, fc="#20242c", ec="none"))
ax.add_patch(Wedge((0, 0), 4.15, 0, 360, width=0.08, fc=WATER, ec="none")); ax.add_patch(Circle((0, 0), 1.9, fc="#2a2f38", ec="none"))
rooms = [r for d in I["habitat"]["decks"] if d["id"] == "L3" for r in d["rooms"]]
nwin = 0
for r in rooms:
    t0, t1 = r["theta_deg"]
    for t in (t0,):
        a = math.radians(t); ax.plot([1.9 * math.cos(a), 4.07 * math.cos(a)], [1.9 * math.sin(a), 4.07 * math.sin(a)], color="#5a6170", lw=1)
    tm = math.radians((t0 + t1) / 2)
    ax.text(3.0 * math.cos(tm), 3.0 * math.sin(tm), r["name"].replace(" cabin", "\ncabin").replace("Crew ", "Crew\n"), color=MUT, fontsize=9, ha="center", va="center")
    for b in r.get("bunks", []):
        a = math.radians(b["angle_deg"]); c, s = math.cos(a), math.sin(a)
        w = b["width_m"] / 2
        P = [(r0 * c - sg * w * s, r0 * s + sg * w * c) for r0, sg in ((1.925, -1), (4.025, -1), (4.025, 1), (1.925, 1))]
        ax.add_patch(Polygon(P, fc="#55657c", ec="none", alpha=0.85))
        ax.plot([4.3 * c - 0.2 * s, 4.3 * c + 0.2 * s], [4.3 * s + 0.2 * c, 4.3 * s - 0.2 * c], color=ACR, lw=5)
        ax.text(4.78 * c, 4.78 * s, f"x{b['tiers']}", color=ACR, fontsize=11, ha="center", va="center")
        nwin += b["tiers"]
fig.text(0.04, 0.155, "Blue ring: berth water ring. Cyan: viewports (x2 where berths are stacked).", color=MUT, fontsize=12.5)
tx = fig.add_axes([0.58, 0.17, 0.40, 0.29]); tx.axis("off")
rows = [("Berth viewports", f"{nwin} (one per berth), 0.35 m clear"),
        ("Shielding, shutter open", "unchanged: the acrylic carries the ring's and the armour's g/cm²"),
        ("Shutter's job", "dust, glare and heat only; closed at cruise speed, like every window"),
        ("Mass", f"{nwin * 0.08:.1f} t for {nwin} (+0.6 t service-section band); plug and insert replace the mass they remove"),
        ("Psych value", "a real window from your own bed; NASA rates windows top for habitability"),
        ("Berth screen", "41.06 g/cm² minimum (v0.5.6: 40.24); open: dose for acrylic vs armour, fire load")]
for i, (k, v) in enumerate(rows):
    tx.text(0, 1 - i * 0.17, k, color=MUT, fontsize=12.5, va="top")
    tx.text(0, 1 - i * 0.17 - 0.055, v, color=FG, fontsize=13, va="top", wrap=True)

fig.text(0.04, 0.105, "The idea: make the shield itself transparent. Acrylic (PMMA) is hydrogen-rich like water, aquarium-clear at 30 cm,\n"
         "and carries roughly the same g/cm² per centimetre as the armour. So the window keeps the berth at shelter grade\n"
         "whether the shutter is open or closed. Encapsulated between glass for fire; outer panes block UV.",
         color=FG, fontsize=13.5, va="top")
fig.savefig(ROOT / "habitat/berth_viewports.png", facecolor=BG)
print(nwin)
