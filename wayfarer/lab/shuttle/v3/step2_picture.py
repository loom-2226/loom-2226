"""Picture for step2_propulsion.json. ALL bodies. ALL sponsors. 2026-2226."""
import json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
d = json.load(open("step2_propulsion.json"))
fig, ax = plt.subplots(1, 3, figsize=(16, 5.2), gridspec_kw={"width_ratios": [1.5, 1, 1.1]})
# 1 water per mission
a = ax[0]; names = list(d["missions"]); short = ["R1 Earth\nsea→orbit", "R2 Venus\n(kit)", "R3 Titan", "R4 Mars", "R5 Moon", "R6 Europa"]
mid = [d["missions"][n]["ve50_dry40"]["water_t"] for n in names]
lo = [min(v["water_t"] for k, v in d["missions"][n].items()) for n in names]
hi = [max(v["water_t"] for k, v in d["missions"][n].items()) for n in names]
cols = ["#2f6fb0" if m <= 23.1 else "#c0392b" for m in mid]
a.bar(range(6), mid, color=cols, yerr=[[m-l for m, l in zip(mid, lo)], [h-m for m, h in zip(mid, hi)]], capsize=4)
a.axhline(23.1, color="k", ls="--"); a.text(5.45, 23.8, "tank 23.1 t", ha="right")
a.set_xticks(range(6)); a.set_xticklabels(short, fontsize=8); a.set_ylabel("water for the whole sortie, t")
a.set_title("Water per mission (7.7 GW torch)\nbar: 40 t dry, 50 km/s top ve; whiskers: 36.5-45 t dry, 25-100 km/s", fontsize=9)
a.text(1, mid[1]+1, "kit brings\nextra water", ha="center", fontsize=8, color="#c0392b")
# 2 power trade
b = ax[1]; tr = d["earth_power_trade"]; P = [float(k) for k in tr]
b.plot(P, [tr[k]["dry_plus_water_t"] for k in tr], "o-", color="#2f6fb0", label="dry + water")
b.plot(P, [tr[k]["water_t"] for k in tr], "s--", color="#7f8c8d", label="water only")
b.axvline(7.7, color="#27ae60"); b.text(7.9, 40, "keep\n7.7 GW", color="#27ae60")
b.set_xlabel("torch jet power, GW"); b.set_ylabel("t (Earth sortie)"); b.legend(fontsize=8)
b.set_title("Bigger torch doesn't pay:\nwater saved ≈ engine mass added", fontsize=9); b.set_ylim(0, 70)
# 3 neutrons
c = ax[2]; rows = d["neutrons"]["rows"]; s = [r["shell_kg_per_pulse"] for r in rows]
for key, lbl, col in (("wayfarer_lineage_0.038", "conservative (Wayfarer torch model)", "#c0392b"), ("removal_theory_0.103", "removal theory (water)", "#2f6fb0")):
    c.semilogy(s, [max(r[key]["cabin_8m_unshielded_Sv_s"], 1e-12) for r in rows], "o-", color=col, label=lbl)
c.axhline(1e-6, color="k", ls=":"); c.text(3, 2e-6, "≈1 mSv over a 15 min ascent", fontsize=8)
c.axvspan(55, 60, color="#27ae60", alpha=.25); c.text(44, 1e1, "≥ 55 kg\nper pulse", color="#27ae60", fontsize=8)
c.set_xlabel("remass shell per pulse, kg"); c.set_ylabel("cabin dose at 8 m, Sv/s (no shadow shield)")
c.set_title("The remass shell is the radiation shield\n(it must be, in air: neutrons scatter round a shadow shield)", fontsize=9)
c.legend(fontsize=7, loc="lower left"); c.set_ylim(1e-12, 1e4)
fig.suptitle("Shuttle v3 step 2: propulsion and power", fontsize=12)
fig.tight_layout(); fig.savefig("step2_propulsion.png", dpi=130)
