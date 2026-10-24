"""Export v0.3 designs as 3D parts -- ALL bodies. ALL sponsors. 2026-2226.
Presentation only; every number comes from optimize_v3.py.
Usage: python export_v3.py REPO_DIR "Name=ID" ...  (ID 'REF' = today's Wayfarer)"""
import json, sys
from pathlib import Path
import optimize_v3 as op

HERE = Path(__file__).resolve().parent
res = json.loads((HERE / "search_results_v3.json").read_text())
by_id = {d["id"]: d for d in res["designs"]}
S, RV = op.S, op.RV
PLANT = {"AXIS": "plant on the axis", "SPLIT": "plant split fore and aft", "AFT": "plant in one aft block", "KEEL": "plant in the keel"}


def parts_for(d):
    g, lay, F = d["geom"], S["layouts"][d["layout"]], S["fixed_modules"]
    P = [{"k": "cyl", "role": "habitat", "x0": 0, "x1": 14, "r": F["habitat_r"], "y": 0, "z": 0}]
    t0, t1 = g["tank_x"]
    if lay["tank"] == "four_cyl":
        c = round(lay["tank_centre_r"] * 0.70711, 3)
        for y, z in ((c, c), (-c, c), (-c, -c), (c, -c)):
            P.append({"k": "cyl", "role": "tank", "x0": t0, "x1": t1, "r": lay["tank_r"], "y": y, "z": z})
    elif lay["tank"] == "two_cyl":
        for y in (lay["tank_y"], -lay["tank_y"]):
            P.append({"k": "cyl", "role": "tank", "x0": t0, "x1": t1, "r": lay["tank_r"], "y": y, "z": 0})
    else:
        P.append({"k": "ctank", "x0": t0, "x1": t1, "r_in": lay["r_in"], "r_out": lay["r_out"], "hw": lay["slot_half_width"],
                  "grooves": d["layout"] == "CWRAP_G"})
    bx0, bx1, by, bz = g["bay"]
    sh = S["shuttle"]
    P.append({"k": "box", "role": "bay", "x0": bx0, "x1": bx1, "y": by, "z": bz, "dy": sh["bay"]["width_m"], "dz": sh["bay"]["depth_m"]})
    sx, sz = g["shuttle"]
    P.append({"k": "box", "role": "shuttle", "x0": sx - sh["length_m"] / 2, "x1": sx + sh["length_m"] / 2, "y": 0, "z": sz,
              "dy": sh["width_m"], "dz": sh["height_m"]})
    for x0, x1, z in g["blocks"]:
        if d["plant"] == "AXIS":
            P.append({"k": "cyl", "role": "plant", "x0": x0, "x1": x1, "r": 0.9, "y": 0, "z": 0})
        elif d["plant"] == "KEEL":
            P.append({"k": "box", "role": "plant", "x0": x0, "x1": x1, "y": 0, "z": z, "dy": 3.0, "dz": 1.0})
        else:
            P.append({"k": "cyl", "role": "plant", "x0": x0, "x1": x1, "r": 2.0, "y": 0, "z": 0})
    rx0, rx1 = g["root_x"]
    sm = {m: (g["spans"][m][0] or 0) for m in ("FAST", "HARD")}
    P.append({"k": "rad", "mech": d["mech"], "x0": rx0, "x1": rx1, "az": g["wing_az"], "root_r": F["hull_r"],
              "torch": g["max_span"], "fast": sm["FAST"], "hard": sm["HARD"], "stack_pleats": 12})
    if g["fore"]:
        fx0, fx1 = 13.75, 18.75
        sf = {m: (g["spans"][m][1] or 0) for m in ("FAST", "HARD")}
        P.append({"k": "rad", "mech": "ACCORDION", "x0": fx0, "x1": fx1, "az": [45, 135, 225, 315], "root_r": F["hull_r"],
                  "torch": 0, "fast": sf["FAST"], "hard": sf["HARD"], "stack_pleats": 12, "plantfin": True})
    s0, A, ar = g["shield0"], F["aft_block_m"], F["aft_radii_m"]
    P.append({"k": "cyl", "role": "torch", "x0": s0, "x1": s0 + A["shield"], "r": ar["shield"], "y": 0, "z": 0})
    P.append({"k": "cyl", "role": "torch", "x0": s0 + A["shield"], "x1": s0 + A["shield"] + A["reactor"], "r": ar["reactor"], "y": 0, "z": 0})
    n0 = s0 + A["shield"] + A["reactor"]
    P.append({"k": "nozzle", "x0": n0, "x1": n0 + A["nozzle"], "r0": ar["reactor"], "r1": ar["nozzle"]})
    return {"L": g["L"], "skin": [0, s0], "parts": P}


def summary(d, name):
    r = d["metric_radius"]
    return {"name": name, "desc": f"{d['layout_label']}, {PLANT[d['plant']]}, {d['place_label'].lower()}, "
            f"{d['mech_label'].lower()} at {d['T']:,} K" + (f", hull +{d['ext_m']} m" if d["ext_m"] else ""),
            "length_m": d["length_m"], "extent_m": d["extent_m"], "dry_t": d["dry_t"], "dv": d["dv_base_econ"],
            "accel_g": d["accel_g"], "surface_m2": d["surface_m2"],
            "r_fast": r["FAST"], "r_hard": r["HARD"], "torch_mw": d["torch_capacity_mw"],
            "torch_ppm": d["torch_capacity_ppm"], "torch_g": d["torch_g"], "hull_mw": d["hull_heat_mw"]["HARD"],
            "water_k_h": d.get("water_warming_k_per_h_hard", 0), "com_z": d["com_z"], "notes": d["notes"]}


def rnd(o):
    if isinstance(o, float):
        return round(o, 3)
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, list):
        return [rnd(v) for v in o]
    return o


if __name__ == "__main__":
    ledger = op.seed_ledger(sys.argv[1])
    out = []
    for spec in sys.argv[2:]:
        name, did = spec.split("=", 1)
        if did == "REF":
            d, _ = op.build(ledger, "T4_top", "AXIS", "ROOT_QUAD", "RIGID", 900, 0, "-", reference=True)
            d["water_warming_k_per_h_hard"] = 0
        else:
            d = by_id[did]
        out.append({"s": summary(d, name), "g": parts_for(d)})
    print(json.dumps(rnd(out), separators=(",", ":")))
