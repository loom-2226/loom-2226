"""Wayfarer design search v0.2 -- ALL bodies. ALL sponsors. 2026-2226.

UNCONSTRAINED: canon set aside, physics kept. Options and assumptions come from
design_space.json; masses come from the repo's Wayfarer seed ledger.
v0.2 adds heat-rejection options (partial main-radiator deployment, fins moved
to the fore block, mixed), midship extension and a forward bay position, and
turns plant-fin / main-radiator overlap into a hard reject.

Step 1 scores base hulls (no drop tanks) for the courier role.
Step 2 sizes the drop-tank kit for the best hull.

Usage: python optimize.py REPO_DIR [--reference]
"""
import itertools, json, math, sqlite3, sys
from pathlib import Path

G0 = 9.80665
HERE = Path(__file__).resolve().parent
S = json.loads((HERE / "design_space.json").read_text())
V2 = S["search_v0_2"]


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


def panel_area(mode):
    PF = S["plant_fins"]
    return PF["equivalent_area_m2_at_900K"][mode] / (2 if PF["two_sided"] else 1)


def build(ledger, lay_key, plant, heat, size, ext, bay_pos, drop_t=0, drop_d=3.0, reference=False):
    F, lay, sh = S["fixed_modules"], S["layouts"][lay_key], S["shuttle"]
    hull_r = F["hull_r"]
    need = (S["fluids"]["remass_t"] + S["fluids"]["protected_water_t"]) / S["fluids"]["water_t_per_m3"] \
        * (1 + S["fluids"]["ullage_fraction"])
    notes = []
    if plant not in lay["plant_allowed"]:
        return None, f"plant {plant} has no room in {lay_key}"
    if heat in ("FINS_FORE", "FINS_FORE_MAIN_PARTIAL") and plant != "SPLIT":
        return None, "fore-fin options need a split plant"
    # tanks and midship
    per_m = {"four_cyl": 4 * math.pi * lay.get("tank_r", 0) ** 2,
             "two_cyl": 2 * math.pi * lay.get("tank_r", 0) ** 2}.get(lay["tank"], lay.get("area_m2_per_m"))
    Lt = 14.0 if reference else up(need / per_m)
    Lm = (lay["bay_section_m"] + Lt) if lay_key == "T4_bay" else max(Lt, lay.get("min_midship_m", 0))
    Lm = 14.0 if reference else Lm + ext
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
        yy = [i * (bw / 2) / 400 for i in range(401)]
        if lay["tank"] == "four_cyl":
            c, r = lay["tank_centre_r"] * math.sin(math.radians(45)), lay["tank_r"]
            top = max(c + math.sqrt(r * r - (y - c) ** 2) for y in yy if abs(y - c) <= r)
        else:
            r, ty = lay["tank_r"], lay["tank_y"]
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
        if bay_pos == "forward":
            bx0 = xm0 + 0.25
        else:
            bx0 = xm0 + Lm / 2 - bl / 2
        bx1 = bx0 + bl
        bay = (bx0, bx1, 0.0, 0.0)
        shuttle_c = ((bx0 + bx1) / 2, 0.0)
    # plant blocks: (mass, x_centre, z, x0, x1)
    P = S["plant"]
    pm = P["mass_t"]
    vmin = pm / P["density_t_m3"][1]
    axis_blocked_by_bay = lay["shuttle"] in ("on_axis", "flush_section")
    round_tanks = lay["tank"] != "c_wrap"
    blocks = []
    if plant == "AXIS":
        blocks = [(pm, sum(tank_x) / 2, 0.0, tank_x[0], tank_x[1])]
    elif plant == "KEEL":
        kx0, kx1 = (bx0, bx1) if lay["shuttle"] != "top_recessed" else tank_x
        blocks = [(pm, (kx0 + kx1) / 2, lay["keel_z"], kx0, kx1)]
        if lay_key == "CWRAP":
            kv = lay["keel_volume_m3_per_m_of_bay"] * bl
            if kv < vmin:
                return None, "keel too small even for dense plant"
            if kv < pm / P["density_t_m3"][0]:
                notes.append(f"keel holds {kv:.0f} m3: fits only if the plant is dense")
    else:
        f0, f1 = P["fore_block_x"]
        if axis_blocked_by_bay:
            f1 = min(f1, bx0 - 0.25)
        if round_tanks:
            f1 = min(f1, tank_x[0] - 0.25)
        a_lo = xm0
        if axis_blocked_by_bay:
            a_lo = max(a_lo, bx1 + 0.25)
        if round_tanks:
            a_lo = max(a_lo, tank_x[1] + 0.25)
        if xm1 - a_lo >= 3.0:          # room for the aft block ahead of the radiator manifold
            a0, a1 = max(a_lo, xm1 - 5.25), xm1
        else:                          # otherwise it spills into the manifold, as in v0.1
            a0, a1 = max(a_lo, xm1 - 1.25), xm1 + 4.0
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
    # heat rejection for Metric
    PF, MR = S["plant_fins"], V2["main_radiator"]
    chord, clr = PF["chord_m"], V2["fin_root_clearance_m"]
    main_full = MR["span_m"]

    def main_partial_span(area):
        return area / (MR["count"] * MR["chord_m"])

    fin_sets = []    # (x0, x1, span)
    fin_area = 0.0
    radius = {}
    if heat in ("FINS_BLOCKS", "FINS_FORE", "FINS_FORE_MAIN_PARTIAL"):
        A_s = panel_area(size)
        if heat == "FINS_BLOCKS":
            sets = [(b, A_s / len(blocks)) for b in blocks]
        elif heat == "FINS_FORE":
            sets = [(blocks[0], A_s)]
            notes.append("aft half's heat is piped forward past the bay to the fore fins")
        else:
            sets = [(blocks[0], A_s / 2)]
        for b, area in sets:
            span = area / (4 * chord)
            c = b[1]
            fx0, fx1 = c - chord / 2, c + chord / 2
            limit = roots[0] - clr
            if fx1 > limit:
                fx1 = limit
                fx0 = fx1 - chord
            if abs((fx0 + fx1) / 2 - c) > V2["max_fin_offset_m"]:
                return None, "plant fins can't clear the main radiators"
            fin_sets.append((fx0, fx1, span))
            fin_area += area
    for mode in ("NORMAL", "FAST"):
        A_m = panel_area(mode)
        if heat == "SHARED":
            spans = [main_full]
        elif heat == "SHARED_PARTIAL":
            spans = [min(main_partial_span(A_m), main_full)]
        elif S["plant_fins"]["options"].index(mode) <= S["plant_fins"]["options"].index(size):
            k = A_m / panel_area(size)          # fins deploy only as far as this mode needs
            spans = [s * k for _, _, s in fin_sets]
            if heat == "FINS_FORE_MAIN_PARTIAL":
                spans.append(min(main_partial_span(A_m / 2), main_full))
        else:
            spans = [main_full]
        radius[mode] = hull_r + max(spans)
    # mass model (dry, shuttle docked, drop tanks off)
    lg = ledger
    struct = lg["structure"] if reference else S["mass_rules"]["structure_t_per_m_of_length"] * L
    mid = 0.491 * L
    items = [
        (lg["armor_fixed_shield"], 9.5, 0), (lg["habitation_life_support"], 8.0, 0),
        (lg["avionics_sensors_comms"], 12.0, 0), (lg["mission_courier_systems"], 17.0, 0),
        (lg["rcs_docking_service"], mid, 0), (lg["engineering_reserve"], mid, 0),
        (lg["thermal_radiators"], xm1 + 3.0, 0), (lg["electrical"], xm1 - 1.0, 0),
        (lg["propulsion"], xm1 + 14.5, 0), (lg["planetary_launch"], shuttle_c[0], shuttle_c[1]),
    ] + [(m, x, z) for m, x, z, _, _ in blocks]
    if lay_key == "CWRAP":
        items.append((lay["c_tank_penalty_t"]["value"], sum(tank_x) / 2, 0))
    fin_mass = fin_area * PF["areal_mass_kg_m2"]["value"] / 1000
    for fx0, fx1, _ in fin_sets:
        items.append((fin_mass / len(fin_sets), (fx0 + fx1) / 2, 0))
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
    wet = dry + S["fluids"]["remass_t"] + S["fluids"]["protected_water_t"]
    m0 = wet + (drop["water_t"] + drop["shell_t"] if drop else 0)
    ve = S["torch"]["ve_km_s"]
    base = {k: v * math.log(wet / (wet - S["fluids"]["remass_t"])) for k, v in ve.items()}
    s1 = {k: (v * math.log(m0 / (m0 - drop["water_t"])) if drop else 0.0) for k, v in ve.items()}
    ar = F["aft_radii_m"]
    secs = [(0, xm1 + A["manifold"], hull_r),
            (xm1 + A["manifold"], xm1 + A["manifold"] + A["shield"], ar["shield"]),
            (xm1 + A["manifold"] + A["shield"], L - A["nozzle"], ar["reactor"]),
            (L - A["nozzle"], L, ar["nozzle"])]
    extent = max(2 * hull_r + sum(h for _, _, h in protr), 2 * (drop["y"] + drop["r"]) if drop else 0)
    label = heat if heat in ("SHARED", "SHARED_PARTIAL") else f"{heat}/{size}"
    main_metric_span = {m: (min(main_partial_span(panel_area(m)), main_full) if heat == "SHARED_PARTIAL" else
                            (min(main_partial_span(panel_area(m) / 2), main_full) if heat == "FINS_FORE_MAIN_PARTIAL" and
                             S["plant_fins"]["options"].index(m) <= S["plant_fins"]["options"].index(size) else
                             (0.0 if heat.startswith("FINS") and S["plant_fins"]["options"].index(m) <=
                              S["plant_fins"]["options"].index(size) else main_full)))
                        for m in ("NORMAL", "FAST")}
    return {
        "id": f"{lay_key}|{plant}|{label}|ext{ext}|{bay_pos}|{drop_t}|{drop_d if drop_t else '-'}",
        "layout": lay_key, "layout_label": lay["label"], "plant": plant, "heat": heat, "size": size,
        "ext_m": ext, "bay_pos": bay_pos, "drop_t": drop_t, "drop_d": drop_d if drop_t else None,
        "length_m": L, "extent_m": extent, "tank_len_m": Lt, "tank_vol_m3": per_m * Lt, "need_m3": need,
        "dry_t": dry, "start_t": m0,
        "dv_base_econ": base["ECON"], "dv_total_econ": base["ECON"] + s1["ECON"],
        "dv_total_cruise": base["CRUISE"] + s1["CRUISE"],
        "accel_g": S["torch"]["cruise_thrust_kn"] * 1000 / (m0 * 1000 * G0),
        "surface_m2": surface(secs, protr), "com_x": cx, "com_z": cz, "balance": abs(cz), "inertia": inertia,
        "metric_radius_normal": radius["NORMAL"], "metric_radius_fast": radius["FAST"],
        "notes": notes,
        "geom": {"xm0": xm0, "xm1": xm1, "L": L, "tank_x": tank_x, "bay": bay, "shuttle": shuttle_c,
                 "blocks": [(b[3], b[4], b[2]) for b in blocks], "fin_sets": fin_sets,
                 "fast_scale": (panel_area("FAST") / panel_area(size)) if heat.startswith("FINS") and
                 S["plant_fins"]["options"].index("FAST") <= S["plant_fins"]["options"].index(size) else None,
                 "main_metric_span": main_metric_span, "drop": drop, "roots": roots},
    }, None


def pareto(ds, keys):
    front = []
    for a in ds:
        if not any(all(s * b[k] >= s * a[k] - 1e-9 for k, s in keys) and
                   any(s * b[k] > s * a[k] + 1e-9 for k, s in keys) for b in ds if b is not a):
            front.append(a)
    return front


def score(pool, weights, fields, tag):
    for key, (field, sign) in fields.items():
        vals = [d[field] for d in pool]
        lo, hi = min(vals), max(vals)
        for d in pool:
            v = ((d[field] - lo) / (hi - lo) if sign > 0 else (hi - d[field]) / (hi - lo)) if hi > lo else 1.0
            d.setdefault("_n", {})[key] = v
    for d in pool:
        d[tag] = sum(w * d["_n"][k] for k, w in weights.items())
        del d["_n"]
    return sorted(pool, key=lambda d: -d[tag])


def main():
    repo = sys.argv[1]
    ledger = seed_ledger(repo)
    if "--reference" in sys.argv:
        d, _ = build(ledger, "T4_top", "AXIS", "SHARED", None, 0, "-", reference=True)
        print(json.dumps({k: v for k, v in d.items() if k != "geom"}, indent=1))
        return
    heat_combos = [("SHARED", None), ("SHARED_PARTIAL", None)] + \
        [(h, s) for h in ("FINS_BLOCKS", "FINS_FORE", "FINS_FORE_MAIN_PARTIAL") for s in V2["fin_sizes"]]
    base, rejects = [], {}
    for lay_key, lay in S["layouts"].items():
        bay_opts = V2["bay_positions_on_axis"] if lay["shuttle"] == "on_axis" else ["-"]
        for plant, (heat, size), ext, bp in itertools.product(["AXIS", "KEEL", "SPLIT", "AFT"], heat_combos,
                                                              V2["extend_midship_m"], bay_opts):
            d, why = build(ledger, lay_key, plant, heat, size, ext, bp)
            if d:
                base.append(d)
            else:
                rejects[why] = rejects.get(why, 0) + 1
    cf = {"field_wrap": ("surface_m2", -1), "metric_radius_fast": ("metric_radius_fast", -1),
          "agility": ("accel_g", 1), "balance": ("balance", -1), "inertia": ("inertia", -1), "dry": ("dry_t", -1)}
    ranked = score(base, S["roles"]["courier"]["weights"], cf, "courier_score")
    front = pareto(base, [(f, s) for f, s in cf.values()])
    for d in base:
        d["pareto"] = any(d is f for f in front)
    best = ranked[0]
    kits = []
    for dt, dd in itertools.product(S["drop_tanks"]["water_t_options"], S["drop_tanks"]["diameter_m_options"]):
        if dt == 0 and dd != S["drop_tanks"]["diameter_m_options"][0]:
            continue
        d, why = build(ledger, best["layout"], best["plant"], best["heat"], best["size"], best["ext_m"],
                       best["bay_pos"], dt, dd)
        if d:
            kits.append(d)
    kits = score(kits, S["roles"]["long_haul"]["weights"],
                 {"reach": ("dv_total_econ", 1), "agility": ("accel_g", 1), "extent": ("extent_m", -1)}, "kit_score")
    best_by_layout, best_by_heat = {}, {}
    for d in ranked:
        best_by_layout.setdefault(d["layout"], d)
        best_by_heat.setdefault(d["heat"], d)
    (HERE / "search_results.json").write_text(json.dumps(
        {"version": S["version"], "n_base": len(base), "rejected": rejects, "n_pareto": len(front),
         "ranked": [d["id"] for d in ranked], "best_by_layout": {k: v["id"] for k, v in best_by_layout.items()},
         "best_by_heat": {k: v["id"] for k, v in best_by_heat.items()},
         "designs": base, "kits": kits}, indent=1))

    def line(d, t="courier_score"):
        return (f" {d[t]:.3f} {d['id']:46s} L {d['length_m']:.1f} surf {d['surface_m2']:.0f} "
                f"mR {d['metric_radius_normal']:.1f}/{d['metric_radius_fast']:.1f} dv {d['dv_total_econ']:.0f} "
                f"a {d['accel_g']:.3f} z {d['com_z']:+.2f} I {d['inertia']/1e3:.0f}k dry {d['dry_t']:.0f} {d['notes']}")
    print(f"base hulls {len(base)}, Pareto {len(front)}, rejected {sum(rejects.values())}: {rejects}")
    print("TOP 10"); [print(line(d)) for d in ranked[:10]]
    print("BEST PER LAYOUT"); [print(line(d)) for d in best_by_layout.values()]
    print("BEST PER HEAT OPTION"); [print(line(d)) for d in best_by_heat.values()]
    print("KITS"); [print(line(d, "kit_score")) for d in kits]


if __name__ == "__main__":
    main()
