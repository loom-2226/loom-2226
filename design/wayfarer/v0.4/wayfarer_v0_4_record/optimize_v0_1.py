"""Wayfarer design search v0.1 -- ALL bodies. ALL sponsors. 2026-2226.

UNCONSTRAINED: canon set aside, physics kept. Options and assumptions come from
design_space.json; masses come from the repo's Wayfarer seed ledger. This script
generates every combination, rejects ones that don't fit, scores the rest, and
finds the Pareto set (no design beats it on every objective at once).

Usage: python optimize.py REPO_DIR [--reference] [--export PICKS_JSON]
"""
import itertools, json, math, sqlite3, sys
from pathlib import Path

G0 = 9.80665
HERE = Path(__file__).resolve().parent
S = json.loads((HERE / "design_space.json").read_text())


def seed_ledger(repo):
    db = sqlite3.connect(":memory:")
    db.executescript((Path(repo) / "geometry/wayfarer_geometry_seed.sql").read_text())
    return {i: m for i, m in db.execute("SELECT id, mass_t FROM mass_elements")}


def up(x, step=0.5):
    return math.ceil(x / step - 1e-9) * step


def surface(sections, protrusions):
    a = math.pi * sections[0][2] ** 2 + math.pi * sections[-1][2] ** 2
    for i, (x0, x1, r) in enumerate(sections):
        a += 2 * math.pi * r * (x1 - x0)
        if i:
            a += abs(math.pi * r ** 2 - math.pi * sections[i - 1][2] ** 2)
    for L, w, h in protrusions:
        a += L * w + 2 * L * h + 2 * w * h
    return a


def build(ledger, lay_key, plant, fins, drop_t, drop_d, reference=False):
    F, lay, sh = S["fixed_modules"], S["layouts"][lay_key], S["shuttle"]
    hull_r = F["hull_r"]
    need = (S["fluids"]["remass_t"] + S["fluids"]["protected_water_t"]) / S["fluids"]["water_t_per_m3"] \
        * (1 + S["fluids"]["ullage_fraction"])
    warn, parts = [], []
    # tanks
    if lay["tank"] == "four_cyl":
        per_m = 4 * math.pi * lay["tank_r"] ** 2
    elif lay["tank"] == "two_cyl":
        per_m = 2 * math.pi * lay["tank_r"] ** 2
    else:
        per_m = lay["area_m2_per_m"]
    Lt = 14.0 if reference else up(need / per_m)
    tank_vol = per_m * Lt
    # midship
    if lay_key == "T4_bay":
        Lm = lay["bay_section_m"] + Lt
    else:
        Lm = max(Lt, lay.get("min_midship_m", 0))
    if reference:
        Lm = 14.0
    xm0 = F["service_x"][1]
    xm1 = xm0 + Lm
    A = F["aft_block_m"]
    L = xm1 + A["manifold"] + A["shield"] + A["reactor"] + A["nozzle"]
    roots = (xm1 + F["radiator_root_offset_m"][0], xm1 + F["radiator_root_offset_m"][1])
    tank_x0 = xm0 + (lay["bay_section_m"] if lay_key == "T4_bay" else 0)
    tank_x = (tank_x0, tank_x0 + Lt)
    # shuttle and bay
    bl, bw, bd = sh["bay"]["length_m"], sh["bay"]["width_m"], sh["bay"]["depth_m"]
    protr = []
    if lay["shuttle"] == "top_recessed":
        if lay["tank"] == "four_cyl":
            c = lay["tank_centre_r"] * math.sin(math.radians(45))
            r = lay["tank_r"]
            yy = [i * (bw / 2) / 400 for i in range(401)]
            top = max(c + math.sqrt(r * r - (y - c) ** 2) for y in yy if abs(y - c) <= r)
        else:
            r, ty = lay["tank_r"], lay["tank_y"]
            yy = [i * (bw / 2) / 400 for i in range(401)]
            top = max(math.sqrt(r * r - (ty - y) ** 2) for y in yy if abs(ty - y) <= r)
        floor = max(lay["bay_floor_z"], top + 0.15)
        bx0 = xm0 + lay["bay_x_offset_from_midship"]
        bx1 = bx0 + bl
        if bx1 > roots[0] - 0.5:
            return None, "bay runs into the radiator roots"
        h = floor + bd - hull_r
        if h > 0:
            protr.append((bl, bw, h))
        bay = (bx0, bx1, 0.0, floor + bd / 2)
        shuttle_c = ((bx0 + bx1) / 2, floor + sh["height_m"] / 2)
    elif lay["shuttle"] == "flush_section":
        bx0, bx1 = xm0, xm0 + bl
        bay = (bx0, bx1, 0.0, lay["bay_floor_z"] + bd / 2)
        shuttle_c = ((bx0 + bx1) / 2, lay["bay_floor_z"] + sh["height_m"] / 2)
    else:  # on_axis
        cx = xm0 + Lm / 2
        bx0, bx1 = cx - bl / 2, cx + bl / 2
        bay = (bx0, bx1, 0.0, 0.0)
        shuttle_c = (cx, 0.0)
    # plant
    if plant not in lay["plant_allowed"]:
        return None, f"plant {plant} has no room in {lay_key}"
    P = S["plant"]
    pm = P["mass_t"]
    vmin = pm / P["density_t_m3"][1]
    blocks = []
    if plant == "AXIS":
        blocks = [(pm, (tank_x[0] + tank_x[1]) / 2, 0.0, tank_x[0], tank_x[1])]
    elif plant == "KEEL":
        kx0, kx1 = (bx0, bx1) if lay["shuttle"] != "top_recessed" else tank_x
        blocks = [(pm, (kx0 + kx1) / 2, lay["keel_z"], kx0, kx1)]
        if lay_key == "CWRAP":
            kv = lay["keel_volume_m3_per_m_of_bay"] * bl
            if kv < vmin:
                return None, "keel too small even for dense plant"
            if kv < pm / P["density_t_m3"][0]:
                warn.append(f"keel holds {kv:.0f} m3: fits only if the plant is dense")
    if plant in ("SPLIT", "AFT"):
        f0, f1 = P["fore_block_x"]
        a0 = xm1 + P["aft_block_rel_midship_end"][0]
        a1 = xm1 + P["aft_block_rel_midship_end"][1]
        if lay["shuttle"] in ("on_axis", "flush_section"):
            f1 = min(f1, bx0 - 0.25)
            a0 = max(a0, bx1 + 0.25)
        if lay["tank"] != "c_wrap":  # round tanks crowd the axis, so blocks must clear the tank ends
            f1 = min(f1, tank_x[0] - 0.25)
            a0 = max(a0, tank_x[1] + 0.25)
        fv = math.pi * (2.9 ** 2 - 1.0 ** 2) * (f1 - f0)
        av = math.pi * 2.9 ** 2 * (a1 - a0)
        if plant == "SPLIT":
            if min(fv, av) < vmin / 2:
                return None, "split blocks too small"
            blocks = [(pm / 2, (f0 + f1) / 2, 0.0, f0, f1), (pm / 2, (a0 + a1) / 2, 0.0, a0, a1)]
        else:
            if av < vmin:
                return None, "aft block too small"
            blocks = [(pm, (a0 + a1) / 2, 0.0, a0, a1)]
    # dedicated plant fins on the diagonals
    PF = S["plant_fins"]
    fin_mass, fin_span, fin_list = 0.0, 0.0, []
    if fins != "SHARED":
        panel = PF["equivalent_area_m2_at_900K"][fins] / (2 if PF["two_sided"] else 1)
        n = 4 * len(blocks)
        fin_span = panel / n / PF["chord_m"]
        fin_mass = panel * PF["areal_mass_kg_m2"]["value"] / 1000
        for b in blocks:
            fx0, fx1 = b[1] - PF["chord_m"] / 2, b[1] + PF["chord_m"] / 2
            fin_list.append((fx0, fx1))
            if fx1 > roots[0] and fx0 < roots[1]:
                warn.append("plant fins sit beside the main radiator roots (they see each other)")
    # mass model (dry, shuttle docked, drop tanks off)
    lg = ledger
    struct = S["mass_rules"]["structure_t_per_m_of_length"] * L if not reference else lg["structure"]
    mid = 0.491 * L
    items = [
        (lg["armor_fixed_shield"], 9.5, 0), (lg["habitation_life_support"], 8.0, 0),
        (lg["avionics_sensors_comms"], 12.0, 0), (lg["mission_courier_systems"], 17.0, 0),
        (lg["rcs_docking_service"], mid, 0), (lg["engineering_reserve"], mid, 0),
        (lg["thermal_radiators"], xm1 + 3.0, 0), (lg["electrical"], xm1 - 1.0, 0),
        (lg["propulsion"], xm1 + 14.5, 0), (lg["planetary_launch"], shuttle_c[0], shuttle_c[1]),
    ] + [(m, x, z) for m, x, z, _, _ in blocks]
    if lay_key == "CWRAP":
        items.append((lay["c_tank_penalty_t"]["value"], (tank_x[0] + tank_x[1]) / 2, 0))
    for fx0, fx1 in fin_list:
        items.append((fin_mass / len(fin_list), (fx0 + fx1) / 2, 0))
    dry = struct + sum(m for m, _, _ in items)
    cx = (struct * mid + sum(m * x for m, x, _ in items)) / dry
    cz = sum(m * z for m, _, z in items) / dry
    inertia = struct * L ** 2 / 12 + struct * (mid - cx) ** 2 + sum(m * (x - cx) ** 2 for m, x, _ in items)
    # drop tanks on the sides
    D = S["drop_tanks"]
    drop = None
    if drop_t:
        r = drop_d / 2
        vol = drop_t / 2 * (1 + S["fluids"]["ullage_fraction"]) / S["fluids"]["water_t_per_m3"]
        dl = vol / (math.pi * r * r)
        lo, hi = D["forward_limit_x"], roots[0] - D["clearance_m"]
        if hi - lo < dl:
            return None, "drop tanks can't clear the radiators"
        c = min(max(cx, lo + dl / 2), hi - dl / 2)
        drop = {"x0": c - dl / 2, "x1": c + dl / 2, "r": r, "y": hull_r + r + D["radial_gap_m"],
                "shell_t": drop_t * D["shell_fraction"], "water_t": drop_t}
    # performance
    wet = dry + S["fluids"]["remass_t"] + S["fluids"]["protected_water_t"]
    m0 = wet + (drop["water_t"] + drop["shell_t"] if drop else 0)
    ve = S["torch"]["ve_km_s"]
    base = {k: v * math.log(wet / (wet - S["fluids"]["remass_t"])) for k, v in ve.items()}
    s1 = {k: (v * math.log(m0 / (m0 - drop["water_t"])) if drop else 0.0) for k, v in ve.items()}
    accel = S["torch"]["cruise_thrust_kn"] * 1000 / (m0 * 1000 * G0)
    ar = F["aft_radii_m"]
    secs = [(0, xm1 + A["manifold"], hull_r),
            (xm1 + A["manifold"], xm1 + A["manifold"] + A["shield"], ar["shield"]),
            (xm1 + A["manifold"] + A["shield"], L - A["nozzle"], ar["reactor"]),
            (L - A["nozzle"], L, ar["nozzle"])]
    surf = surface(secs, protr)
    extent = max(2 * hull_r + sum(h for _, _, h in protr), 2 * (drop["y"] + drop["r"]) if drop else 0)
    return {
        "id": f"{lay_key}|{plant}|{fins}|{drop_t}|{drop_d if drop_t else '-'}",
        "layout": lay_key, "layout_label": lay["label"], "plant": plant, "fins": fins,
        "drop_t": drop_t, "drop_d": drop_d if drop_t else None,
        "length_m": L, "extent_m": extent, "tank_len_m": Lt, "tank_vol_m3": tank_vol, "need_m3": need,
        "dry_t": dry, "start_t": m0,
        "dv_base_econ": base["ECON"], "dv_total_econ": base["ECON"] + s1["ECON"],
        "dv_total_cruise": base["CRUISE"] + s1["CRUISE"],
        "accel_g": accel, "surface_m2": surf, "com_x": cx, "com_z": cz, "inertia": inertia,
        "fin_span_m": fin_span, "metric_folded_up_to": None if fins == "SHARED" else fins,
        "metric_radius_normal": hull_r + (fin_span if fins in ("NORMAL", "FAST", "HARD") else S["metric_fold"]["main_radiator_span_m"]),
        "metric_radius_fast": hull_r + (fin_span if fins in ("FAST", "HARD") else S["metric_fold"]["main_radiator_span_m"]),
        "warnings": warn,
        "geom": {"xm0": xm0, "xm1": xm1, "L": L, "tank_x": tank_x, "bay": bay, "shuttle": shuttle_c,
                 "blocks": [(b[3], b[4], b[2]) for b in blocks], "fins": fin_list, "fin_span": fin_span,
                 "drop": drop, "roots": roots},
    }, None


def pareto(ds, keys):
    """keys: list of (field, +1 maximise / -1 minimise)."""
    front = []
    for a in ds:
        dominated = False
        for b in ds:
            if b is a:
                continue
            ge = all(sign * b[k] >= sign * a[k] - 1e-9 for k, sign in keys)
            gt = any(sign * b[k] > sign * a[k] + 1e-9 for k, sign in keys)
            if ge and gt:
                dominated = True
                break
        if not dominated:
            front.append(a)
    return front


def main():
    repo = sys.argv[1]
    ledger = seed_ledger(repo)
    if "--reference" in sys.argv:
        d, why = build(ledger, "T4_top", "AXIS", "SHARED", 0, 3.0, reference=True)
        print(json.dumps({k: v for k, v in d.items() if k != "geom"}, indent=1))
        return
    designs, rejects = [], {}
    for lay in S["layouts"]:
        for plant, fins, dt, dd in itertools.product(["AXIS", "KEEL", "SPLIT", "AFT"], S["plant_fins"]["options"],
                                                      S["drop_tanks"]["water_t_options"],
                                                      S["drop_tanks"]["diameter_m_options"]):
            if dt == 0 and dd != S["drop_tanks"]["diameter_m_options"][0]:
                continue
            d, why = build(ledger, lay, plant, fins, dt, dd)
            if d:
                designs.append(d)
            else:
                rejects[why] = rejects.get(why, 0) + 1
    for d in designs:
        d["balance"] = abs(d["com_z"])
    def score(pool, weights, fields):
        for role_key, (field, sign) in fields.items():
            vals = [d[field] for d in pool]
            lo, hi = min(vals), max(vals)
            for d in pool:
                v = ((d[field] - lo) / (hi - lo) if sign > 0 else (hi - d[field]) / (hi - lo)) if hi > lo else 1.0
                d.setdefault("_n", {})[role_key] = v
        for d in pool:
            d["_s"] = sum(w * d["_n"][k] for k, w in weights.items())
        return sorted(pool, key=lambda d: -d["_s"])
    R = S["roles"]
    base = [d for d in designs if d["drop_t"] == 0]
    cf = {"field_wrap": ("surface_m2", -1), "metric_radius_fast": ("metric_radius_fast", -1), "agility": ("accel_g", 1),
          "balance": ("balance", -1), "inertia": ("inertia", -1), "dry": ("dry_t", -1)}
    ranked = score(base, R["courier"]["weights"], cf)
    for d in ranked:
        d["courier_score"] = d.pop("_s"); d.pop("_n")
    front = pareto(base, [(f, sg) for f, sg in cf.values()])
    best = ranked[0]
    kit_pool = [d for d in designs if (d["layout"], d["plant"], d["fins"]) == (best["layout"], best["plant"], best["fins"])]
    kf = {"reach": ("dv_total_econ", 1), "agility": ("accel_g", 1), "extent": ("extent_m", -1)}
    kits = score(kit_pool, R["long_haul"]["weights"], kf)
    for d in kits:
        d["kit_score"] = d.pop("_s"); d.pop("_n")
    best_by_layout = {}
    for d in ranked:
        best_by_layout.setdefault(d["layout"], d)
    out = {"n_designs": len(designs), "rejected": rejects, "n_base": len(base), "n_base_pareto": len(front),
           "base_ranked": [d["id"] for d in ranked], "best_by_layout": {k: v["id"] for k, v in best_by_layout.items()},
           "kits_for_best": [d["id"] for d in kits], "designs": designs}
    (HERE / "search_results.json").write_text(json.dumps(out, indent=1))
    print(f"feasible {len(designs)} (base hulls {len(base)}, base Pareto {len(front)}); rejected {sum(rejects.values())}")
    print("TOP BASE HULLS (courier weights)")
    for d in ranked[:8]:
        print(f" {d['courier_score']:.3f} {d['id']:26s} L {d['length_m']:.1f} surf {d['surface_m2']:.0f} mR {d['metric_radius_normal']:.1f}/{d['metric_radius_fast']:.1f} "
              f"dv {d['dv_base_econ']:.0f} a {d['accel_g']:.3f} z {d['com_z']:+.2f} I {d['inertia']/1e3:.0f}k dry {d['dry_t']:.0f} span {d['fin_span_m']:.1f} {d['warnings']}")
    print("BEST PER LAYOUT")
    for k, d in best_by_layout.items():
        print(f" {k:7s} {d['id']:26s} score {d['courier_score']:.3f} L {d['length_m']:.1f} surf {d['surface_m2']:.0f} mR {d['metric_radius_fast']:.1f} z {d['com_z']:+.2f} dry {d['dry_t']:.0f}")
    print("DROP KITS FOR BEST HULL (long-haul weights)")
    for d in kits:
        print(f" {d['kit_score']:.3f} {d['id']:26s} dv {d['dv_total_econ']:.0f} a {d['accel_g']:.2f} ext {d['extent_m']:.1f}")


if __name__ == "__main__":
    main()
