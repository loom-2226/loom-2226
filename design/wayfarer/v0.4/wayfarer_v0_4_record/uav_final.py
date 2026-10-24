"""Reproduce the two drones v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Lightest closing design per world set, then drop pods
sized at least as wide as the folded drone. Writes uav_candidates.json.
Usage: python uav_final.py"""
import json, math, copy
import uav_search as us

U0 = copy.deepcopy(us.U)


def best(worlds=None, air=None, power=None):
    U = copy.deepcopy(U0)
    if worlds:
        U["worlds"] = {k: v for k, v in U["worlds"].items() if k in worlds}
    b = None
    for d in us.search(U):
        if d["ok_any_stow"] and (air is None or d["airframe"] == air) and (power is None or d["power"] == power):
            if b is None or d["mass_kg"] < b["mass_kg"]:
                b = d
    return b


sets = {"one drone, all worlds": (None, None, None, True),
        "Mars drone": (["Mars"], "ROTOR", "BAT+SOLAR+BEAM", True),
        "dense-air drone": (["Titan", "Venus clouds", "Earth"], "ROTOR", "BAT+RPS", False)}
out = {}
for name, (w, a, p, jet) in sets.items():
    d = best(w, a, p)
    st = d["stow_m"]
    pod = us.drop_pod(d["mass_kg"], jetpack=jet, min_d=math.hypot(st[0], st[1]) + 0.3)
    keep = ("airframe", "power", "mass_kg", "battery_fraction", "disk_loading_cap", "rotor_d_m", "wing_span_m", "payload_kg",
            "stow_m", "fits_shuttle", "parts", "battery_wh", "rps_w", "solar_m2", "roles", "perf")
    out[name] = us.rnd({"d": {k: d[k] for k in keep}, "pod": pod})
    print(name, d["mass_kg"], "kg", d["airframe"], d["power"], "pod", round(pod["entry_kg"]), "kg")
(us.HERE / "uav_candidates.json").write_text(json.dumps(out, indent=1))
