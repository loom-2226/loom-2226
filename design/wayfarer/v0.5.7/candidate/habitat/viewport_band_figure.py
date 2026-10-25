# ALL bodies. ALL sponsors. 2026-2226. Figure for habitat/viewport_band_study_results.json (NON-GOVERNING)
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib import font_manager as fm
ROOT = Path(__file__).resolve().parent.parent
for f in ["Inter-Regular.otf", "Inter-SemiBold.otf"]:
    fm.fontManager.addfont("/usr/share/fonts/opentype/inter/" + f)
plt.rcParams["font.family"] = "Inter"
R = json.loads((ROOT / "habitat/viewport_band_study_results.json").read_text())
BG, FG, MUT, TI, GL, SH, ACC = "#0d1018", "#e8edf5", "#9aa6b8", "#b8c2cf", "#2f6fb5", "#8c7a5b", "#f0a03c"
fig = plt.figure(figsize=(12, 15), dpi=160); fig.patch.set_facecolor(BG)
fig.text(0.04, 0.99, "L2 viewport band: the full load path", color=FG, fontsize=26, fontweight="semibold", va="top")
fig.text(0.04, 0.966, "ALL bodies. ALL sponsors. 2026-2226.  Study on v0.5.7 rev 3 (PR #432); the build is unchanged.", color=MUT, fontsize=14, va="top")

# (1) elevation: two general bays and one lounge bay, seen from inside
fig.text(0.04, 0.93, "1  Elevation from inside (unrolled): general band and lounge", color=FG, fontsize=18, fontweight="semibold")
ax = fig.add_axes([0.04, 0.60, 0.92, 0.32]); ax.set_facecolor(BG); ax.set_aspect("equal"); ax.axis("off")
sp = R["mullion_spacing_m"]
ax.set_xlim(-0.6, 5 * sp + 0.6); ax.set_ylim(-0.75, 2.35)
def bay(x0, h, transom=False):
    ax.add_patch(Rectangle((x0, 0), sp, h, fc=GL, ec="none", alpha=0.85))
    if transom:
        ax.add_patch(Rectangle((x0, h / 2 - 0.02), sp, 0.04, fc=TI, ec="none"))
for k in range(2):
    bay(k * sp, 0.6)
for k in range(2, 5):
    bay(k * sp, 1.6, transom=True)
for y, lab in ((0.0, "sill ring"), (1.6, "head ring (lounge)")):
    pass
ax.add_patch(Rectangle((-0.3, -0.07), 5 * sp + 0.6, 0.07, fc=TI, ec="none"))                         # sill ring
ax.add_patch(Rectangle((-0.3, 0.6), 2 * sp + 0.02, 0.07, fc=TI, ec="none"))                          # head ring, general
ax.add_patch(Rectangle((2 * sp - 0.02, 1.6), 3 * sp + 0.32, 0.07, fc=TI, ec="none"))                # head ring, lounge
for k in range(6):
    h = 0.6 if k < 2 else 1.6
    if k == 2:
        h = 1.6
    ax.add_patch(Rectangle((k * sp - 0.025, 0), 0.05, h, fc=TI, ec="none"))
    for yy in (0, h):     # forked roots
        ax.plot([k * sp - 0.09, k * sp, k * sp + 0.09], [yy + (0.09 if yy == 0 else -0.09), yy, yy + (0.09 if yy == 0 else -0.09)], color=TI, lw=3)
ax.add_patch(Rectangle((-0.6, -0.07), 0.3, 0.74, fc=SH, ec="none")); ax.add_patch(Rectangle((-0.6, 0.67), 0.3, 1.0, fc=SH, ec="none"))
ax.text(-0.45, 1.2, "shell", color=FG, fontsize=11, ha="center", rotation=90)
ax.add_patch(Rectangle((-0.6, 1.67), 2 * sp + 0.62, 0.68, fc=SH, ec="none"))
ax.text(0.9, 2.0, "pressure shell (continues above)", color=FG, fontsize=11, ha="center")
ax.add_patch(Rectangle((-0.6, -0.75), 5 * sp + 1.2, 0.68, fc=SH, ec="none"))
ax.text(2.8, -0.45, "pressure shell (continues below); axial flow 436 kN/m collects into the mullions", color=FG, fontsize=11, ha="center")
r3, r5, pn = R["3_rings"], R["5_mullion_root_joint"], R["2_panes_mm_each"]
ax.annotate(f"edge rings: Ti {r3['ring_section_cm'][0]:.0f} x {r3['ring_section_cm'][1]:.0f} cm, {r3['with_lounge_hoop_mpa']:.0f} MPa (allow {r3['allow_mpa']:.0f})",
            xy=(3.5 * sp, 1.64), xytext=(3.1 * sp, 2.12), color=ACC, fontsize=12, ha="center", arrowprops=dict(arrowstyle="-", color=ACC))
ax.annotate("mid transom in the lounge", xy=(3.5 * sp, 0.82), xytext=(3.5 * sp, 1.3), color=FG, fontsize=11.5, ha="center", arrowprops=dict(arrowstyle="-", color=FG))
ax.annotate(f"mullion root: {r5['load_kn']:.0f} kN, 4 x M16 Ti\nin double shear, margin {r5['margin']}", xy=(2 * sp, 0.03), xytext=(1.0 * sp, 1.05),
            color=FG, fontsize=11.5, ha="center", arrowprops=dict(arrowstyle="-", color=FG))
ax.text(0.5 * sp, 0.3, "0.6 m", color=FG, fontsize=11, ha="center")
ax.text(4.5 * sp, 0.3, "1.6 m", color=FG, fontsize=11, ha="center")
ax.plot([0, sp], [-0.02, -0.02], alpha=0)
ax.text(0.5 * sp, 0.68 + 0.12, f"{sp:.2f} m", color=MUT, fontsize=10.5, ha="center")

# (2) results table
fig.text(0.04, 0.565, "2  Results", color=FG, fontsize=18, fontweight="semibold")
tx = fig.add_axes([0.04, 0.17, 0.92, 0.38]); tx.axis("off")
h1 = R["1_hoop_to_edge_rings"]; s4 = R["4_shell_at_ring"]; m = R["mass"]
rows = [("Hoop across the band", f"carried by the sill and head rings, half each: {h1['general band 0.6 m']['ring_tension_kn']:.0f} kN (general), {h1['lounge 1.6 m']['ring_tension_kn']:.0f} kN (lounge) per ring", "ok"),
        ("Glass joints", "the glass is not trusted to pass hoop tension through its edges; each pane is a plate between frame members", "ok"),
        ("Rings as beams", f"{r3['ring_moment_knm']:.0f} kN·m between mullions + lounge hoop: {r3['with_lounge_hoop_mpa']:.0f} MPa against {r3['allow_mpa']:.0f} (12 cm rings failed at 625; now 14 cm)", "ok"),
        ("Shell next to a ring", f"rigid-ring bending {s4['discontinuity_bending_mpa']:.0f} + axial {s4['axial_mpa']:.0f} = {s4['axial_plus_bending_mpa']:.0f} MPa against {s4['allow_mpa']:.0f}; dies out within {s4['decay_length_m']:.2f} m", "ok"),
        ("Mullion roots", f"{r5['load_kn']:.0f} kN each; 4 x M16 Ti bolts in double shear carry {r5['four_M16_double_shear_kn']:.0f} kN (margin {r5['margin']}); an integral Osteon fork removes the bolts", "ok"),
        ("Panes, 2226 ceramic (crown milestone)", f"{pn['general band (0.6 x 1.13 m)']['ceramic 2226 (crown milestone)']} mm general, {pn['lounge with a mid transom (0.8 x 1.13 m)']['ceramic 2226 (crown milestone)']} mm lounge with transom (16 assumed)", "warn"),
        ("Panes, 2026 ALON", f"{pn['general band (0.6 x 1.13 m)']['ALON 2026']} mm and {pn['lounge with a mid transom (0.8 x 1.13 m)']['ALON 2026']} mm: rev 3's 16 mm needs the crown's ceramic milestone", "warn"),
        ("Mass", f"frame needs {m['frame_needed_t']} t against {m['frame_allowed_rev3_t']} t in rev 3; with the thicker lounge panes the band grows {m['band_increase_t']} t (reserve 54.6 t)", "warn")]
for i, (k, v, st) in enumerate(rows):
    y = 1 - i * 0.125
    tx.text(0, y, ("✓ " if st == "ok" else "! ") + k, color=("#7fd17a" if st == "ok" else ACC), fontsize=13.5, fontweight="semibold", va="top")
    tx.text(0.02, y - 0.045, v, color=FG, fontsize=12.2, va="top", wrap=True)
fig.text(0.04, 0.12, "Verdict: the load path closes with 14 cm titanium edge rings, a mid transom in the lounge and bolted (or integral) mullion roots.\n"
         "Two corrections to rev 3: the frame is ~1.5 t heavier, and the 16 mm panes rely on the crown's 2226 ceramic milestone\n"
         "(2026 ALON would need 25-29 mm). Method: closed-form; a shell finite-element model of the band is the next fidelity step.",
         color=FG, fontsize=12.5, va="top")
fig.savefig(ROOT / "habitat/viewport_band_study.png", facecolor=BG)
print("ok")
