"""Export chosen designs from search_results.json (v0.2) as 3D parts -- ALL bodies. ALL sponsors. 2026-2226.
Presentation only: every number comes from optimize.py.
Usage: python export_picks.py REPO_DIR "Name=ID" ...   (ID 'REF' = today's Wayfarer)"""
import json, sys
from pathlib import Path
import optimize as op

HERE = Path(__file__).resolve().parent
res = json.loads((HERE / "search_results.json").read_text())
by_id = {d["id"]: d for d in res["designs"] + res["kits"]}
S = op.S
HEAT = {"SHARED": "plant shares the main radiators, fully out for Metric",
        "SHARED_PARTIAL": "main radiators deploy only partway for Metric",
        "FINS_BLOCKS": "own fins at both plant blocks",
        "FINS_FORE": "all plant fins at the fore block",
        "FINS_FORE_MAIN_PARTIAL": "fore fins for the fore half, main radiators partway out for the aft half"}
PLANT = {"AXIS": "plant on the axis", "SPLIT": "plant split fore and aft", "AFT": "plant in one aft block",
         "KEEL": "plant in the keel"}


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
        P.append({"k": "ctank", "role": "tank", "x0": t0, "x1": t1, "r_in": lay["r_in"], "r_out": lay["r_out"],
                  "hw": lay["slot_half_width"]})
    bx0, bx1, by, bz = g["bay"]
    sh = S["shuttle"]
    P.append({"k": "box", "role": "bay", "x0": bx0, "x1": bx1, "y": by, "z": bz,
              "dy": sh["bay"]["width_m"], "dz": sh["bay"]["depth_m"]})
    sx, sz = g["shuttle"]
    P.append({"k": "box", "role": "shuttle", "x0": sx - sh["length_m"] / 2, "x1": sx + sh["length_m"] / 2,
              "y": 0, "z": sz, "dy": sh["width_m"], "dz": sh["height_m"]})
    for x0, x1, z in g["blocks"]:
        if d["plant"] == "AXIS":
            P.append({"k": "cyl", "role": "plant", "x0": x0, "x1": x1, "r": 0.9, "y": 0, "z": 0})
        elif d["plant"] == "KEEL":
            P.append({"k": "box", "role": "plant", "x0": x0, "x1": x1, "y": 0, "z": z, "dy": 3.0, "dz": 1.0})
        else:
            P.append({"k": "cyl", "role": "plant", "x0": x0, "x1": x1, "r": 2.0, "y": 0, "z": 0})
    scale = g["fast_scale"] or 0
    for x0, x1, span in g["fin_sets"]:
        P.append({"k": "fins", "x0": x0, "x1": x1, "fast": span * scale, "root_r": F["hull_r"]})
    r0, r1 = g["roots"]
    P.append({"k": "rad", "x0": r0, "x1": r1, "root_r": F["hull_r"], "full": S["search_v0_2"]["main_radiator"]["span_m"],
              "fast": g["main_metric_span"]["FAST"]})
    xm1, A, ar = g["xm1"], F["aft_block_m"], F["aft_radii_m"]
    a = xm1 + A["manifold"]
    P.append({"k": "cyl", "role": "torch", "x0": a, "x1": a + A["shield"], "r": ar["shield"], "y": 0, "z": 0})
    P.append({"k": "cyl", "role": "torch", "x0": a + A["shield"], "x1": a + A["shield"] + A["reactor"],
              "r": ar["reactor"], "y": 0, "z": 0})
    n0 = a + A["shield"] + A["reactor"]
    P.append({"k": "nozzle", "x0": n0, "x1": n0 + A["nozzle"], "r0": ar["reactor"], "r1": ar["nozzle"]})
    if g["drop"]:
        dr = g["drop"]
        for y in (dr["y"], -dr["y"]):
            P.append({"k": "cyl", "role": "droptank", "x0": dr["x0"], "x1": dr["x1"], "r": dr["r"], "y": y, "z": 0})
    return {"L": g["L"], "skin": [0, xm1 + A["manifold"]], "parts": P}


def summary(d, name):
    return {"name": name, "id": d["id"], "desc": f"{d['layout_label']}, {PLANT[d['plant']]}, {HEAT[d['heat']]}"
            + (f" (sized for {d['size']})" if d["size"] else "") + (f", hull +{d['ext_m']} m" if d["ext_m"] else ""),
            "length_m": d["length_m"], "extent_m": d["extent_m"], "dry_t": d["dry_t"], "dv_econ": d["dv_total_econ"],
            "dv_base_econ": d["dv_base_econ"], "accel_g": d["accel_g"], "surface_m2": d["surface_m2"],
            "mr_normal": d["metric_radius_normal"], "mr_fast": d["metric_radius_fast"], "com_z": d["com_z"],
            "notes": d["notes"]}


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
            d, _ = op.build(ledger, "T4_top", "AXIS", "SHARED", None, 0, "-", reference=True)
        else:
            d = by_id[did]
        out.append({"s": summary(d, name), "g": parts_for(d)})
    print(json.dumps(rnd(out), separators=(",", ":")))
