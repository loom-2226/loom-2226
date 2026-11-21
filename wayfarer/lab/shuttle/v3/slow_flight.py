"""Shuttle v3: slow flight / water touchdown speed with powered lift.
ALL bodies. ALL sponsors. 2026-2226. NON-CANON ROM screen.
Touchdown speed V = sqrt(2 (W - fan lift) / (rho S CLmax))."""
import json, math, numpy as np
import agility as AG
veh = AG.vehicle(True); al, CL, CD, S = AG.polar(veh)
CL_ROM = float(CL[al <= 20].max())          # unpowered ROM at <= 20 deg (realistic attitude for touching water)
IN = {
 "S_ref_m2": [round(S, 1), "b5 planform + 18 m2 telescoping wing"],
 "CL_unpowered": [round(CL_ROM, 2), "aero_test.subsonic ROM, alpha <= 20 deg"],
 "flap_dCL_on_wing": [1.2, "ASSUMPTION: slotted flaps on the wing area only"],
 "USB_CLmax_total": [4.0, "QSRA-class upper-surface blowing (NASA TM: USB flight-verified on QSRA); applied to whole S: OPTIMISTIC for a lifting body"],
 "CCW_CLmax_total": [6.0, "circulation-control wing: A-6 CCW demo CLmax slightly over 10 (NASA N88-17609) on its wing; ~6 on our whole S: ASSUMPTION"],
 "fan_lift_kN": [{"28 MW": 200, "42 MW (dash kit)": 263}, "static thrust from lift_fans option 1b at 8 m2, vectored down"],
 "masses_t": [{"heavy: climb water aboard (44 t dry)": 64.6, "light: refill at port": 47.0}, "dry 44 t after 8 g; 2.6 t payload; 18 t climb water"],
 "target_ms": [40, "US-2 class (min controllable ~26 m/s, lands in 3 m waves at 43 t, 136 m2 wing)"],
}
v = {k: x[0] for k, x in IN.items()}
Swing = 18.0
def vtd(m, CLmax, lift_kN):
    W = m * 1e3 * 9.81 - lift_kN * 1e3
    return round(math.sqrt(2 * max(W, 0) / (1.225 * v["S_ref_m2"] * CLmax)), 1)
CASES = {
 "today (no flaps, no fan lift)": (v["CL_unpowered"], 0),
 "+ slotted flaps": (v["CL_unpowered"] + v["flap_dCL_on_wing"] * Swing / v["S_ref_m2"], 0),
 "+ flaps + fan lift 28 MW": (v["CL_unpowered"] + v["flap_dCL_on_wing"] * Swing / v["S_ref_m2"], 200),
 "fans blow the flaps (USB) 28 MW": (v["USB_CLmax_total"], 200),
 "USB + dash kit 42 MW": (v["USB_CLmax_total"], 263),
 "circulation-control wing + 42 MW": (v["CCW_CLmax_total"], 263),
}
out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "inputs": IN, "touchdown_ms": {}}
for name, (cl, fl) in CASES.items():
    out["touchdown_ms"][name] = {k: vtd(m, cl, fl) for k, m in v["masses_t"].items()}
    out["touchdown_ms"][name]["CLmax"] = round(cl, 2)
json.dump(out, open("slow_flight.json", "w"), indent=1); print(json.dumps(out["touchdown_ms"], indent=1))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
names = list(CASES); H = [out["touchdown_ms"][n]["heavy: climb water aboard (44 t dry)"] for n in names]; L = [out["touchdown_ms"][n]["light: refill at port"] for n in names]
fig, a = plt.subplots(figsize=(11, 5)); y = np.arange(len(names))
a.barh(y - .2, H, .4, color="#2f6fb0", label="64.6 t (climb water aboard)"); a.barh(y + .2, L, .4, color="#9cc3e6", label="47 t (refill at port)")
a.axvline(40, color="#27ae60", lw=2); a.text(41, len(names) - .6, "target ≤ 40 m/s\n(2 m waves)", color="#27ae60", fontsize=9)
a.axvline(26, color="#7f8c8d", ls=":"); a.text(27, -.7, "US-2 min ~26 m/s", fontsize=8, color="#7f8c8d")
for i, (h, l) in enumerate(zip(H, L)): a.text(h + .8, i - .2, f"{h:.0f}", va="center", fontsize=8); a.text(l + .8, i + .2, f"{l:.0f}", va="center", fontsize=8)
a.set_yticks(y); a.set_yticklabels([f"{n}\n(CL {out['touchdown_ms'][n]['CLmax']})" for n in names], fontsize=8); a.invert_yaxis()
a.set_xlabel("water touchdown speed, m/s"); a.legend(fontsize=8, loc="lower right"); a.set_xlim(0, 120)
a.set_title("Shuttle v3: getting the water landing speed down (ROM)", fontsize=11)
fig.tight_layout(); fig.savefig("slow_flight.png", dpi=120)
