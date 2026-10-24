"""Concept explorer v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
UNCONSTRAINED EXPLORATION: canon set aside, physics kept. Every input comes
from concepts.json; this script only applies the rocket equation, volumes
and a relative outer-surface figure.
Usage: python concepts.py [--json] [--parts]"""
import json, math, sys
from pathlib import Path

G0 = 9.80665
D = json.loads((Path(__file__).parent / "concepts.json").read_text())
c0 = D["common"]


def ctank_area(r_in, r_out, half_w, n=1200):
    """Cross-section of a C-shaped tank: annulus minus a top slot of width 2*half_w."""
    h = 2 * r_out / n
    area = 0.0
    for i in range(n):
        for j in range(n):
            y = -r_out + (i + 0.5) * h
            z = -r_out + (j + 0.5) * h
            r = math.hypot(y, z)
            if r_in <= r <= r_out and not (z > 0 and abs(y) < half_w):
                area += h * h
    return area


def tank_volume(p):
    if p["kind"] == "cyl":
        v = math.pi * p["r"] ** 2 * (p["x1"] - p["x0"])
        if "minus_box" in p:
            b = p["minus_box"]
            v -= b["dx"] * b["dy"] * b["dz"]
        return v
    if p["kind"] == "ctank":
        return ctank_area(p["r_in"], p["r_out"], p["slot_half_width"]) * (p["x1"] - p["x0"])
    raise ValueError(p["kind"])


def surface(env):
    s = env["sections"]
    a = math.pi * s[0][2] ** 2 + math.pi * s[-1][2] ** 2
    for i, (x0, x1, r) in enumerate(s):
        a += 2 * math.pi * r * (x1 - x0)
        if i:
            a += abs(math.pi * r ** 2 - math.pi * s[i - 1][2] ** 2)
    for p in env["protrusions"]:
        L = p["x1"] - p["x0"]
        a += L * p["dy"] + 2 * L * p["h"] + 2 * p["dy"] * p["h"]
    for x0, x1, r in env["extra_cylinders"]:
        a += 2 * math.pi * r * (x1 - x0) + 2 * math.pi * r ** 2
    return a


def extent(c):
    e = max(2 * r for _, _, r in c["envelope"]["sections"])
    for p in c["envelope"]["protrusions"]:
        e = max(e, 4.5 + p["h"] + 4.5)
    for p in c["parts"]:
        if p["role"] == "droptank":
            e = max(e, 2 * (abs(p["y"]) + p["r"]))
    return e


def evaluate(c):
    dens = c0["water_t_per_m3"] if c["fluid"] == "water" else c0["liquid_hydrogen_t_per_m3"]
    vol = sum(tank_volume(p) for p in c["parts"] if p["role"] == "tank")
    need = c0["normal_remass_t"] / dens
    dry = c0["reference_dry_t"] + c["added_length_m"] * c0["structure_t_per_added_m"]["value"]
    wet = dry + c0["normal_remass_t"] + c0["protected_water_t"]
    drop_w = drop_m = 0.0
    if c["drop_tanks"]:
        drop_w = c["drop_tanks"]["water_t"]
        drop_m = drop_w * c0["drop_tank_mass_fraction"]["value"]
    m0 = wet + drop_w + drop_m
    dv = {}
    for mode, ve in c0["torch_cards_km_s"].items():
        stage1 = ve * math.log(m0 / (m0 - drop_w)) if drop_w else 0.0
        dv[mode] = stage1 + ve * math.log(wet / (wet - c0["normal_remass_t"]))
    return {
        "id": c["id"], "name": c["name"], "idea": c["idea"], "fluid": c["fluid"],
        "length_m": max(x1 for _, x1, _ in c["envelope"]["sections"]),
        "max_extent_m": extent(c),
        "tank_volume_m3": vol, "needed_m3": need, "fill": need / vol,
        "dry_t": dry, "start_mass_t": m0,
        "dv_econ_km_s": dv["ECON"], "dv_cruise_km_s": dv["CRUISE"],
        "dv_from_drop_econ_km_s": c0["torch_cards_km_s"]["ECON"] * math.log(m0 / (m0 - drop_w)) if drop_w else 0.0,
        "cruise_start_g": c0["cruise_thrust_kn"] * 1000 / (m0 * 1000 * G0),
        "shuttle_offset_m": c0["shuttle_t"] * c["shuttle_center_z_m"] / dry,
        "surface_m2": surface(c["envelope"]),
        "notes": c.get("notes", []),
    }


res = [evaluate(c) for c in D["concepts"]]
ref = res[0]["surface_m2"]
for r in res:
    r["surface_vs_today"] = r["surface_m2"] / ref

if "--json" in sys.argv:
    print(json.dumps(res, indent=1))
elif "--parts" in sys.argv:
    out = []
    for c in D["concepts"]:
        a = c["aft_start_m"]
        sec = c["envelope"]["sections"]
        parts = [p for p in c["parts"]]
        parts.append({"kind": "cyl", "role": "torch", "x0": sec[-3][0], "x1": sec[-3][1], "r": sec[-3][2], "y": 0, "z": 0})
        parts.append({"kind": "cyl", "role": "torch", "x0": sec[-2][0], "x1": sec[-2][1], "r": sec[-2][2], "y": 0, "z": 0})
        parts.append({"kind": "nozzle", "role": "torch", "x0": sec[-1][0], "x1": sec[-1][1], "r0": sec[-2][2], "r1": sec[-1][2]})
        parts.append({"kind": "rad", "role": "radiator", "x0": a + 1, "x1": a + 6, "root_r": 4.5})
        out.append({"id": c["id"], "len": sec[-1][1], "parts": parts})
    print(json.dumps(out, separators=(",", ":")))
else:
    for r in res:
        print(f"{r['id']} {r['name']}: L {r['length_m']:.0f} m, max {r['max_extent_m']:.1f} m, "
              f"tanks {r['tank_volume_m3']:.0f} m3 for {r['needed_m3']:.0f} ({r['fill']*100:.0f}% full), "
              f"dry {r['dry_t']:.0f} t, start {r['start_mass_t']:.0f} t, "
              f"dv ECON {r['dv_econ_km_s']:.0f} / CRUISE {r['dv_cruise_km_s']:.0f} km/s, "
              f"CRUISE {r['cruise_start_g']:.2f} g, shuttle offset {r['shuttle_offset_m']:.2f} m, "
              f"surface x{r['surface_vs_today']:.2f}")
