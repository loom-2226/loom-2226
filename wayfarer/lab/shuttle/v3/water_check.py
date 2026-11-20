"""Shuttle v3 water constraints W2/W5 (kT option D, 2026-11-20).
ALL bodies. ALL sponsors. 2026-2226."""
import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle
RHO = 1.025            # seawater t/m3
B4S_VOL = 82.45        # B4 enclosed_volume_m3 (shuttle_v2b_manifest)
WATER = 23.1           # shuttle water capacity t
cases = {"B4-S 36.5 t, empty tank": 36.5,
         "B4-S 36.5 t + full water": 36.5 + WATER,
         "52.5 t ceiling + full water": 52.5 + WATER}
out = {"rho_t_m3": RHO, "reserve_target": 0.5, "cases": {}}
for k, m in cases.items():
    v = m / RHO
    out["cases"][k] = {"mass_t": round(m, 2), "displaced_m3": round(v, 1),
                       "b4s_reserve_pct": round((B4S_VOL - v) / v * 100),
                       "hull_needed_m3": round(1.5 * v, 1)}
cap = {"ext_m3": 6.7, "displaces_t": round(6.7 * RHO, 2), "shell_fittings_t": 4.51,
       "rating_bar": round(92 / 1.5, 1), "rating_m": round((92 / 1.5 - 1) * 10 / RHO)}
out["capsule_sub"] = cap
json.dump(out, open("water_check.json", "w"), indent=1)

fig, ax = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1.1, 1]})
a = ax[0]
names = list(out["cases"]); need = [out["cases"][n]["hull_needed_m3"] for n in names]
disp = [out["cases"][n]["displaced_m3"] for n in names]
y = range(len(names))
a.barh(y, need, color="#9cc3e6", label="watertight volume for 50% reserve")
a.barh(y, disp, color="#2f6fb0", label="volume under water")
a.axvline(B4S_VOL, color="#c0392b", lw=2); a.text(B4S_VOL + 1, 2.45, "B4-S 82 m³", color="#c0392b")
a.set_yticks(list(y)); a.set_yticklabels(names); a.set_xlabel("m³")
a.set_title("W2: does it float with margin?"); a.legend(loc="lower right", fontsize=8)
for i, n in enumerate(names):
    a.text(need[i] + 1, i, f"{out['cases'][n]['b4s_reserve_pct']}% in B4-S", va="center", fontsize=8)
a.set_xlim(0, 135)
b = ax[1]; b.set_xlim(-1, 15); b.set_ylim(-9, 4); b.set_aspect("equal"); b.axis("off")
b.add_patch(Rectangle((-1, -9), 16, 9, color="#d6eaf8"))
for xw in range(-1, 15): b.plot([xw, xw + .5, xw + 1], [0, .15, 0], color="#2f6fb0", lw=1)
b.add_patch(Ellipse((6, 0.3), 12, 2.8, color="#7f8c8d"))
b.add_patch(Rectangle((7.6, -1.05), 2.6, 1.0, color="#5dade2", ec="k", lw=.8))
b.text(8.9, -0.55, "flooded\nwell", ha="center", fontsize=7)
b.annotate("torch exit\nabove water+1 m (W3)", (11.8, 0.9), (12, 3), fontsize=7, arrowprops={"arrowstyle": "->"})
b.add_patch(FancyBboxPatch((7.4, -6.2), 2.6, 1.6, boxstyle="round,pad=0,rounding_size=.8", color="#d4ac0d", ec="k"))
b.plot([8.7, 8.9], [-4.6, -1.1], "k--", lw=.8)
b.text(10.3, -5.6, f"Ti capsule sub\n~{cap['rating_m']} m rated\n6.9 t displaced vs 4.5 t shell", fontsize=7)
b.text(0, 2.5, "Option D: land, float, flood the well,\ncapsule dives, recover, take off", fontsize=9)
b.set_title("Deploy afloat (W4, W5)")
fig.suptitle("Shuttle v3 water constraints (kT option D, 2026-11-20)", fontsize=12)
fig.tight_layout(); fig.savefig("water_check.png", dpi=140)
print(json.dumps(out, indent=1))
