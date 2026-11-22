"""Picture for lift_fans.json. ALL bodies. ALL sponsors. 2026-2226."""
import json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
d = json.load(open("lift_fans.json"))
fig, ax = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.2, 1]})
a = ax[0]
A = [r["fan_area_m2"] for r in d["rows"]]; M = [r["mass_t"]["total"] for r in d["rows"]]
a.plot(A, M, "o-", color="#c0392b", lw=2, label="1a: hover on Earth (fans hold all 59 t)")
B = [r["fan_area_m2"] for r in d["option_1b_seaplane_plus_hover"]]; N = [r["mass_t"]["total"] for r in d["option_1b_seaplane_plus_hover"]]
a.plot(B, N, "s-", color="#27ae60", lw=2, label="1b: seaplane on Earth, hover on Titan & Venus")
for x, y, r in zip(A, M, d["rows"]): a.text(x, y+0.6, f"{r['design_MWe']:.0f} MW", ha="center", fontsize=7, color="#c0392b")
for x, y, r in zip(B, N, d["option_1b_seaplane_plus_hover"]): a.text(x, y-1.4, f"{r['design_MWe']:.0f} MW", ha="center", fontsize=7, color="#27ae60")
a.axhspan(5.8, 5.8, color="k"); a.axhline(5.8, color="#2f6fb0", ls="--")
a.text(30.5, 6.3, "could come off the Venus kit\n(rotor + its reactor 5.8 t)", ha="right", fontsize=8, color="#2f6fb0")
a.set_xlabel("total fan disc area, m²"); a.set_ylabel("added shuttle mass, t (reactor, motors, electronics, fans)")
a.set_title("Electric fans: what they cost", fontsize=10); a.legend(fontsize=8, loc="upper right"); a.set_ylim(0, 25)
b = ax[1]; b.axis("off")
txt = [("1a  Earth hover", "#c0392b", ["13-22 t added: busts the 52.5 t ceiling", "motors dominate (~120-200 MW)", "verdict: no"]),
       ("1b  ~8-10 m² fans, ~28 MW reactor", "#27ae60", ["+3.4-3.6 t", "Earth: takes off and lands on water/runway,", "  flies on reactor power (~17 MW), no water used", "Titan: true hover (~4 MW)", "Venus: true hover with kit (~28 MW)", "  → may retire the kit rotor + reactor (-5.8 t)", "  OPEN: fans/motors at 737 K", "Earth vertical landing on land: belly rockets", "verdict: yes"])]
y = 0.95
for head, col, lines in txt:
    b.text(0, y, head, fontsize=11, color=col, weight="bold", transform=b.transAxes); y -= 0.07
    for l in lines: b.text(0.03, y, l, fontsize=9, transform=b.transAxes); y -= 0.06
    y -= 0.04
fig.suptitle("Shuttle v3 option 1: electric fans + house reactor", fontsize=12)
fig.tight_layout(); fig.savefig("lift_fans.png", dpi=130)
