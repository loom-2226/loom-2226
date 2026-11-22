"""Picture for agility.json. ALL bodies. ALL sponsors. 2026-2226."""
import json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
d = json.load(open("agility.json")); c = d["cases"]
fig, ax = plt.subplots(1, 3, figsize=(17, 5.6), gridspec_kw={"width_ratios": [1.25, 1, 1.05]})
a = ax[0]
def line(key, k, **kw):
    P = [p for p in c[key]["points"] if p[k] > 0]; a.plot([p["V"] for p in P], [p[k] for p in P], **kw)
line("59t_0km_wings_out_torch", "turn_inst_dps", color="k", lw=2, label="max turn, wings out (aero / 4 g limit)")
line("59t_0km_wings_out_torch", "turn_sus_dps", color="#c0392b", lw=2, label="sustained, torch (770 kN)")
line("59t_0km_wings_out_fans", "turn_sus_dps", color="#27ae60", lw=2, label="sustained, fans only (28 MW)")
line("59t_0km_wings_in_torch", "turn_inst_dps", color="#7f8c8d", lw=1.5, ls="--", label="max turn, wings in (dash)")
line("45t_0km_wings_out_torch", "turn_inst_dps", color="k", lw=1, ls=":", label="max turn at 45 t")
a.axvline(c["59t_0km_wings_out_torch"]["stall_ms"], color="#7f8c8d", lw=.8); a.text(c["59t_0km_wings_out_torch"]["stall_ms"] + 2, 1, "stall 86 m/s", fontsize=8)
a.set_xlabel("speed, m/s (sea level, 59 t)"); a.set_ylabel("turn rate, deg/s"); a.set_ylim(0, 16); a.grid(alpha=.3)
a.legend(fontsize=8, loc="upper right"); a.set_title("Turning: torch gives it fighter-like energy; fans don't", fontsize=10)
b = ax[1]; E = d["egress_to_30km"]
b.plot([e["water_t"] for e in E], [e["time_s"] for e in E], "o-", color="#2f6fb0", lw=2)
for e in E: b.text(e["water_t"] + .15, e["time_s"] + 2, f"T/W {e['TW0']}\n{e['thrust_kN']} kN, ve {e['ve_kms']}", fontsize=8)
b.set_xlabel("water burned to reach 30 km, t"); b.set_ylabel("seconds from sea level to 30 km"); b.grid(alpha=.3)
b.set_title("Egress: torch pop-up to 30 km\n(harder pop = more water)", fontsize=10); b.set_xlim(4, 14); b.set_ylim(40, 150)
b.text(11.6, 52, "ve < 10 km/s:\nbelow the\ntorch's range", fontsize=7, color="#c0392b")
t = ax[2]; t.axis("off")
S = d["summary"]; s0 = S["59t_0km_wings_out_torch"]; sf = S["59t_0km_wings_out_fans"]; sf3 = S["59t_3km_wings_out_fans"]
lines = [("Torch, wings out (59 t, sea level)", "#c0392b"), (f"  max turn {s0['max_inst_dps']}°/s at {s0['at_ms']:.0f} m/s, radius {s0['radius_m']:.0f} m", None),
         (f"  sustained {s0['max_sus_dps']}°/s (4 g limit), climb {s0['best_climb_ms']:.0f} m/s", None),
         ("Fans only", "#27ae60"), (f"  sustained {sf['max_sus_dps']}°/s, climb {sf['best_climb_ms']} m/s", None),
         (f"  at 3 km and 59 t it can't hold altitude", None),
         ("Slow flight", "#7f8c8d"), ("  stall 75-100 m/s: no hover, no slow", None), ("  terrain-hugging on Earth", None),
         ("Signature", "#7f8c8d"), ("  torch low down = 7.7 GW plume, pulsed bangs,", None), ("  seen for hundreds of km; neutrons on the ground", None)]
y = .97
for txt, col in lines:
    t.text(0, y, txt, fontsize=10 if col else 9, color=col or "k", weight="bold" if col else "normal", transform=t.transAxes); y -= .075
fig.suptitle("Shuttle v3 (B5 concept): atmospheric agility for contested ingress / egress (ROM, subsonic)", fontsize=12)
fig.tight_layout(); fig.savefig("agility.png", dpi=120)
