# ALL bodies. ALL sponsors. 2026-2226. One-page figure for g10_results.json (NON-GOVERNING)
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
HERE = Path(__file__).resolve().parent
try:
    for f in ["Inter-Regular.otf", "Inter-SemiBold.otf"]:
        fm.fontManager.addfont("/usr/share/fonts/opentype/inter/" + f)
    plt.rcParams["font.family"] = "Inter"
except Exception:
    pass
R = json.loads((HERE / "g10_results.json").read_text())
BG, FG, MUT, OK, BAD, A1, A2 = "#0d1018", "#e8edf5", "#9aa6b8", "#7fd17a", "#f0a03c", "#5b9bd5", "#f0a03c"
fig = plt.figure(figsize=(12, 16), dpi=150); fig.patch.set_facecolor(BG)
fig.text(0.04, 0.985, "G10 v0.2: flight dynamics of RCS, torch, Metric and Loom", color=FG, fontsize=22, fontweight="semibold", va="top")
fig.text(0.04, 0.962, f"ALL bodies. ALL sponsors. 2026-2226.  Wayfarer v0.5.7 rev 5 ({R['geometry_sha256'][:8]}), main {R['sources']['main_commit'][:8]}.  "
         f"{R['passed']} of {R['total']} checks pass.", color=MUT, fontsize=12.5, va="top")
names = {"C_card": "Card conformance", "R_rcs": "RCS", "T_torch": "Torch", "M_metric": "Metric", "L_loom": "Loom"}
y = 0.935
for g, cs in R["checks"].items():
    fig.text(0.04, y, names[g], color=FG, fontsize=15, fontweight="semibold", va="top"); y -= 0.022
    for c in cs:
        col = OK if c["pass"] else BAD
        val = f"{c['value']} vs {c['limit']} {c['unit']}".strip()
        fig.text(0.05, y, ("✓ " if c["pass"] else "✗ ") + c["name"].split("; delta-v")[0][:100], color=col, fontsize=10.5, va="top")
        fig.text(0.96, y, val[:34], color=col if not c["pass"] else MUT, fontsize=10.5, va="top", ha="right"); y -= 0.0165
    y -= 0.008
# chart 1: torch thrust, ship card vs working card
tc = R["detail"]["torch_cards"]
ax = fig.add_axes([0.07, 0.10, 0.40, 0.23]); ax.set_facecolor(BG)
xs = range(len(tc)); w = 0.38
ax.bar([i - w / 2 for i in xs], [t["ship_card_thrust_mn"] for t in tc], w, color=A1, label="rev 5 ship card")
ax.bar([i + w / 2 for i in xs], [t["working_card_thrust_mn"] for t in tc], w, color=A2, label="main working card")
ax.set_xticks(list(xs)); ax.set_xticklabels([t["mode"] for t in tc], color=FG, fontsize=9.5)
ax.set_ylabel("thrust, MN", color=FG); ax.tick_params(colors=MUT)
ax.set_title("Torch thrust: two cards disagree (kT to choose)", color=FG, fontsize=12.5, loc="left")
ax.legend(frameon=False, labelcolor=FG, fontsize=9.5)
for s in ax.spines.values(): s.set_color("#2a3242")
# chart 2: torch disturbance vs RCS authority, worst state per mode
hold = R["detail"]["rcs"]["torch_disturbance"]; modes = [t["mode"] for t in tc]
worst = [max(h["disturbance_mnm"] for h in hold if h["mode"] == m) for m in modes]
ax2 = fig.add_axes([0.56, 0.10, 0.40, 0.23]); ax2.set_facecolor(BG)
ax2.bar(range(len(modes)), worst, 0.6, color=A2)
rc = R["detail"]["rcs"]["rcs_full_pitch_mnm"]
ax2.axhline(rc, color=OK, lw=2); ax2.text(-0.4, rc + 0.4, f"all RCS: {rc} MN·m", color=OK, ha="left", fontsize=10)
ax2.set_xticks(range(len(modes))); ax2.set_xticklabels(modes, color=FG, fontsize=9.5)
ax2.set_ylabel("disturbance torque, MN·m", color=FG); ax2.tick_params(colors=MUT)
ax2.set_title(f"Torch error torque vs RCS (0.5° error assumed)", color=FG, fontsize=12.5, loc="left")
for s in ax2.spines.values(): s.set_color("#2a3242")
fig.text(0.04, 0.02, "Decisions held for kT: which torch card governs (ship card or MODE_CARDS);  torch thrust-vector authority (needs 0.85°, if the 0.5° error\n"
         "assumption holds);  axial RCS thrusters (rev 6).  Card gap: declare the Loom configuration (strakes, crown gores, docking collar).\n"
         "Not computed by design: Metric Δv/remass (CANON II §20); Loom domain fit (PR #356). Navigator missions are follow-up validation.",
         color=FG, fontsize=10.5, va="bottom")
fig.savefig(HERE / "g10_results.png", facecolor=BG)
print("ok")
