"""Wayfarer re-run around the 2226 shuttle v0.2 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Re-uses optimize_v3.py unchanged, patching only the
shuttle it carries: a round 4.3 m biconic lander, 14.4 m long, 34.1 t dry,
fuelled from Wayfarer's own water before each trip. The round body lets the
wrap-around tanks keep a round bore instead of a box slot.
Usage: python wayfarer_v4.py REPO_DIR"""
import json, math, sys
from pathlib import Path
import optimize_v3 as op

HERE = Path(__file__).resolve().parent
NEW = {"shuttle_dry_t": 34.1, "drones_pods_t": 1.2, "length_m": 14.4, "diameter_m": 4.3, "clearance_m": 0.25,
       "bay_length_m": 15.4, "venus_kit_t": 12.5,
       "note": "drones: two Mars drones (395 kg each in pods) and two dense-air drones (204 kg each in pods); "
               "Venus balloon kit is hold payload, loaded only for Venus surface trips"}


def patch():
    S = op.S
    sh = S["shuttle"]
    bore_r = NEW["diameter_m"] / 2 + NEW["clearance_m"]
    sh.update({"mass_t": NEW["shuttle_dry_t"], "length_m": NEW["length_m"], "width_m": NEW["diameter_m"], "height_m": NEW["diameter_m"],
               "bay": {"length_m": NEW["bay_length_m"], "width_m": 2 * bore_r, "depth_m": 2 * bore_r}})
    r_out = 4.3
    for key, grooves in (("CWRAP", 0.0), ("CWRAP_G", 4.0)):
        lay = S["layouts"][key]
        r_in = bore_r + 0.05
        area = math.pi * (r_out ** 2 - r_in ** 2) - 2 * bore_r * (r_out - r_in) - 0.5 - grooves
        lay.update({"r_in": round(r_in, 3), "slot_half_width": round(bore_r, 3), "area_m2_per_m": round(area, 2),
                    "min_midship_m": NEW["bay_length_m"] + 0.5})
    S["layouts"]["T4_bay"]["bay_section_m"] = NEW["bay_length_m"] + 0.5
    for key in ("T4_top", "SADDLE"):
        S["layouts"][key]["min_midship_m"] = max(S["layouts"][key].get("min_midship_m", 0), NEW["bay_length_m"] + 0.5)
    return S


if __name__ == "__main__":
    repo = sys.argv[1]
    ledger = op.seed_ledger(repo)
    old = op.build(ledger, "CWRAP_G", "AFT", "STRAKE_QUAD", "ACCORDION", 1300, 0, "centre")[0]
    S = patch()
    ledger["planetary_launch"] = NEW["shuttle_dry_t"] + NEW["drones_pods_t"]
    print("CWRAP_G area per m now", S["layouts"]["CWRAP_G"]["area_m2_per_m"], "r_in", S["layouts"]["CWRAP_G"]["r_in"])
    designs, rejects = [], {}
    import itertools
    for lay_key, lay in S["layouts"].items():
        bays = ["centre", "forward"] if lay["shuttle"] == "on_axis" else ["-"]
        for plant, place, mech, T, ext, bp in itertools.product(["AXIS", "KEEL", "SPLIT", "AFT"], op.RV["placements"],
                                                                op.RV["mechanisms"], op.RV["temperatures_k"], [0, 2, 4], bays):
            d, why = op.build(ledger, lay_key, plant, place, mech, T, ext, bp)
            if d:
                designs.append(d)
            else:
                rejects[why] = rejects.get(why, 0) + 1
    ranked = op.score(designs, op.RV["score"]["weights"], op.FIELDS, "score")
    rated = [d for d in ranked if d["torch_g"] >= op.RV["torch_rating_required_g"]["value"]]
    win = rated[0]
    fam = [op.build(ledger, "CWRAP_G", pl, "STRAKE_QUAD", "ACCORDION", 1300, ex, bp)[0]
           for pl in ("AFT", "SPLIT") for ex in (0, 2, 4) for bp in ("centre", "forward")]
    fam = [d for d in fam if d]
    same = next((d for d in ranked if any(d["id"] == f["id"] for f in fam)), None) or min(fam, key=lambda d: d["length_m"])

    def brief(d):
        r = d["metric_radius"]
        return {"id": d["id"], "length_m": d["length_m"], "dry_t": round(d["dry_t"], 1), "dv_km_s": round(d["dv_base_econ"], 1),
                "accel_g": round(d["accel_g"], 3), "metric_r_fast": r["FAST"], "metric_r_hard": r["HARD"],
                "torch_mw": round(d["torch_capacity_mw"]), "hull_mw_hard": round(d["hull_heat_hard"], 2), "notes": d["notes"],
                "midship_m": round(d["geom"]["xm1"] - d["geom"]["xm0"], 1), "bay": d["geom"]["bay"], "tank_x": d["geom"]["tank_x"]}
    out = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "new_shuttle": NEW,
           "v0_3_winner_with_old_shuttle": brief(old), "same_design_new_shuttle": brief(same), "new_headline_winner": brief(win),
           "top5": [brief(d) for d in rated[:5]], "n": len(designs)}
    for k in ("v0_3_winner_with_old_shuttle", "same_design_new_shuttle", "new_headline_winner"):
        print(k, out[k])
    for d in rated[:5]:
        print("  ", brief(d)["id"], d["length_m"], round(d["dry_t"], 1), round(d["dv_base_econ"]), d["notes"])
    # Venus kit carried in the hold: delta-v cost
    wet = same["start_t"]
    ve = S["torch"]["ve_km_s"]["ECON"]
    dv_kit = ve * math.log((wet + NEW["venus_kit_t"]) / (wet + NEW["venus_kit_t"] - S["fluids"]["remass_t"]))
    out["venus_kit_in_hold_dv_km_s"] = round(dv_kit, 1)
    print("with Venus kit in hold, dv", round(dv_kit, 1))
    (HERE / "wayfarer_v4_results.json").write_text(json.dumps(out, indent=1, default=str))
    # parts for 3D
    import export_v3 as ex
    ex.S = S
    print(json.dumps(ex.rnd([{"s": ex.summary(same, "Wayfarer v0.4"), "g": ex.parts_for(same)}]), separators=(",", ":")))
