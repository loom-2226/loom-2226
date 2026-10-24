"""Wayfarer design search v0.3 -- ALL bodies. ALL sponsors. 2026-2226.

UNCONSTRAINED: canon set aside, physics kept. Hull options from design_space.json,
radiator options from radiators_v3.json, masses from the repo seed ledger.
New in v0.3: radiator placement (aft root band vs hull strakes, four wings vs two
flat wings), mechanism (accordion / roll-out / rigid), reject temperature, and a 2D
view-factor model so wings that see each other or the hull lose rejection.

Usage: python optimize_v3.py REPO_DIR [--reference]
"""
import itertools, json, math, random, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = json.loads((HERE / "design_space.json").read_text())
RV = json.loads((HERE / "radiators_v3.json").read_text())
RAD1 = json.loads((HERE / "radiators.json").read_text())
G0, SIGMA, HULL = 9.80665, 5.670374419e-8, S["fixed_modules"]["hull_r"]
MODES = ["NORMAL", "FAST", "EXPEDITE", "HARD"]


def seed_ledger(repo):
    db = sqlite3.connect(":memory:")
    db.executescript((Path(repo) / "geometry/wayfarer_geometry_seed.sql").read_text())
    return {i: m for i, m in db.execute("SELECT id, mass_t FROM mass_elements")}


def up(x, step=0.5):
    return math.ceil(x / step - 1e-9) * step


def heat_mw(mode, T):
    mh = RAD1["metric_heat_from_canon"]
    tc = mh["cold_temperature_k"]
    return mh["cold_load_kw"][mode] / 1000 + mh["cryo_electrical_mw_at_900K"][mode] * (T - tc) / (900 - tc)


# ---------------- view factors (2D Monte Carlo, cached) ----------------
_VF = {}


def view_factors(wings, spacing_deg, span):
    """Fraction of one wing face's emission reaching space and the hull."""
    key = (wings, spacing_deg, round(span, 2))
    if key in _VF:
        return _VF[key]
    if span <= 0:
        return (1.0, 0.0)
    rng = random.Random(1)
    a, n = HULL, RV["view_factor"]["rays_per_span"]
    az = [math.radians(i * spacing_deg) for i in range(wings)]
    segs = [((a * math.cos(t), a * math.sin(t)), ((a + span) * math.cos(t), (a + span) * math.sin(t))) for t in az[1:]]
    space = hull = 0
    for _ in range(n):
        r = a + rng.random() * span
        px, py = r, 1e-6                      # wing 0 lies on +x; emit from its +y face
        phi = math.asin(2 * rng.random() - 1)  # cosine-weighted about +y
        dx, dy = math.sin(phi), math.cos(phi)
        best, what = float("inf"), "space"
        b = px * dx + py * dy                 # ray-circle
        c = px * px + py * py - a * a
        disc = b * b - c
        if disc >= 0:
            t = -b - math.sqrt(disc)
            if t > 1e-9:
                best, what = t, "hull"
        for (x1, y1), (x2, y2) in segs:       # ray-segment
            ex, ey = x2 - x1, y2 - y1
            den = dx * ey - dy * ex
            if abs(den) < 1e-12:
                continue
            t = ((x1 - px) * ey - (y1 - py) * ex) / den
            u = ((x1 - px) * dy - (y1 - py) * dx) / den
            if t > 1e-9 and 0 <= u <= 1 and t < best:
                best, what = t, "wing"
        if what == "space":
            space += 1
        elif what == "hull":
            hull += 1
    _VF[key] = (space / n, hull / n)
    return _VF[key]


# ---------------- radiator set evaluation ----------------
def radiator_set(placement, mech, T, chord, recess, wings, spacing):
    m = RV["mechanisms"][mech]
    eps = m["emissivity"]
    flux = eps * SIGMA * T ** 4
    prot = 0.0
    if mech == "ACCORDION":
        pleats = min(m["max_pleats"], int(recess / m["pleat_stack_m"] + 1e-9))
        if pleats < 1:
            return None, "no room to stow even one pleat"
        spans = [m["pleat_m"] * k for k in range(1, pleats + 1)]
    elif mech == "ROLLOUT":
        spans = [0.25 * k for k in range(1, int(m["max_span_m"] / 0.25) + 1)]
        prot = max(0.0, m["drum_m"] - recess)
    else:
        if m.get("root_only") and placement.startswith("STRAKE"):
            return None, "rigid panels can't be strakes"
        spans = [m["max_span_m"]]
        prot = 0.15

    HC = RV["hull_coating"]

    def net(s):
        fs, fh = view_factors(wings, spacing, s)
        e = 2 * wings * chord * s * flux
        escaped = fs + fh * (1 - HC["absorptivity"]) * HC["reflected_escape_fraction"]
        return e * escaped / 1e6, e * fh * HC["absorptivity"] / 1e6

    return {"spans": spans, "net": net, "max_span": spans[-1], "prot": prot, "g": m["torch_g_limit"],
            "areal": m["areal_kg_m2"], "chord": chord, "wings": wings, "spacing": spacing}, None


def deploy_for(rs, q_mw):
    for s in rs["spans"]:
        n, h = rs["net"](s)
        if n + 1e-9 >= q_mw:
            return s, h
    return None, None


# ---------------- hull + plant + radiators ----------------
def build(ledger, lay_key, plant, place, mech, T, ext, bay_pos, drop_t=0, drop_d=3.0, reference=False):
    F, lay, sh = S["fixed_modules"], S["layouts"][lay_key], S["shuttle"]
    P = RV["placements"][place]
    notes = []
    if plant not in lay["plant_allowed"]:
        return None, f"plant {plant} has no room in {lay_key}"
    need = (S["fluids"]["remass_t"] + S["fluids"]["protected_water_t"]) * (1 + S["fluids"]["ullage_fraction"])
    per_m = {"four_cyl": 4 * math.pi * lay.get("tank_r", 0) ** 2,
             "two_cyl": 2 * math.pi * lay.get("tank_r", 0) ** 2}.get(lay["tank"], lay.get("area_m2_per_m"))
    Lt = 14.0 if reference else up(need / per_m)
    Lm = (lay["bay_section_m"] + Lt) if lay_key == "T4_bay" else max(Lt, lay.get("min_midship_m", 0))
    Lm = 14.0 if reference else Lm + ext
    xm0 = F["service_x"][1]
    xm1 = xm0 + Lm
    A = F["aft_block_m"]
    man = P["manifold_m"]
    shield0 = xm1 + man
    L = shield0 + A["shield"] + A["reactor"] + A["nozzle"]
    tank_x0 = xm0 + (lay["bay_section_m"] if lay_key == "T4_bay" else 0)
    tank_x = (tank_x0, tank_x0 + Lt)
    # bay
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
        if bx1 > shield0 - 0.5:
            return None, "bay runs into the aft block"
        h = floor + bd - HULL
        if h > 0:
            protr.append((bl, bw, h))
        bay = (bx0, bx1, 0.0, floor + bd / 2)
        shuttle_c = ((bx0 + bx1) / 2, floor + sh["height_m"] / 2)
    elif lay["shuttle"] == "flush_section":
        bx0, bx1 = xm0, xm0 + bl
        bay = (bx0, bx1, 0.0, lay["bay_floor_z"] + bd / 2)
        shuttle_c = ((bx0 + bx1) / 2, lay["bay_floor_z"] + sh["height_m"] / 2)
    else:
        bx0 = xm0 + 0.25 if bay_pos == "forward" else xm0 + Lm / 2 - bl / 2
        bx1 = bx0 + bl
        bay = (bx0, bx1, 0.0, 0.0)
        shuttle_c = ((bx0 + bx1) / 2, 0.0)
    # plant
    PL = S["plant"]
    pm, vmin = PL["mass_t"], PL["mass_t"] / PL["density_t_m3"][1]
    blocked = lay["shuttle"] in ("on_axis", "flush_section")
    round_tanks = lay["tank"] != "c_wrap"
    if plant == "AXIS":
        blocks = [(pm, sum(tank_x) / 2, 0.0, tank_x[0], tank_x[1])]
    elif plant == "KEEL":
        kx0, kx1 = (bx0, bx1) if lay["shuttle"] != "top_recessed" else tank_x
        blocks = [(pm, (kx0 + kx1) / 2, lay["keel_z"], kx0, kx1)]
        if lay_key in ("CWRAP", "CWRAP_G"):
            kv = lay["keel_volume_m3_per_m_of_bay"] * bl
            if kv < vmin:
                return None, "keel too small even for dense plant"
            if kv < pm / PL["density_t_m3"][0]:
                notes.append(f"keel holds {kv:.0f} m3: fits only if the plant is dense")
    else:
        f0, f1 = PL["fore_block_x"]
        if blocked:
            f1 = min(f1, bx0 - 0.25)
        if round_tanks:
            f1 = min(f1, tank_x[0] - 0.25)
        a_lo = xm0
        if blocked:
            a_lo = max(a_lo, bx1 + 0.25)
        if round_tanks:
            a_lo = max(a_lo, tank_x[1] + 0.25)
        a_hi = min(xm1 + 4.0, shield0)        # never into the shadow shield
        a0, a1 = max(a_lo, a_hi - 5.25), a_hi
        fv = math.pi * (2.9 ** 2 - 1.0 ** 2) * (f1 - f0)
        av = math.pi * 2.9 ** 2 * max(0.0, a1 - a0)
        if plant == "SPLIT":
            if min(fv, av) < vmin / 2:
                return None, "split blocks too small"
            blocks = [(pm / 2, (f0 + f1) / 2, 0.0, f0, f1), (pm / 2, (a0 + a1) / 2, 0.0, a0, a1)]
        else:
            if av < vmin:
                return None, "aft block too small"
            blocks = [(pm, (a0 + a1) / 2, 0.0, a0, a1)]
    # radiators
    strake = place.startswith("STRAKE")
    if strake:
        chord = xm1 - P["chord_from_x"]
        recmap = RV["strake_recess_m_by_layout"] if P["wings"] == 4 else RV["strake_side_recess_m_by_layout"]
        recess = recmap[lay_key]
        root_x = (P["chord_from_x"], xm1)
    else:
        chord, recess = P["chord_m"], P["recess_m"]
        root_x = (xm1 + 1.0, xm1 + 1.0 + chord)
    main, why = radiator_set(place, mech, T, chord, recess, P["wings"], P["spacing_deg"])
    if not main:
        return None, why
    fore = None
    if not strake:   # fore plant fins for the fore half (accordion at the same temperature, diagonals)
        if plant == "SPLIT":
            fore, why = radiator_set("ROOT_QUAD", "ACCORDION", T, 5.0, 0.5, 4, 90)
    radius, hull_load, spans = {}, {}, {}
    for mode in MODES:
        q = heat_mw(mode, T)
        if fore:
            sm, hm = deploy_for(main, q / 2)
            sf, hf = deploy_for(fore, q / 2)
            ok = sm is not None and sf is not None
            r = HULL + max(sm or 0, sf or 0) if ok else None
            hl = (hm or 0) + (hf or 0) if ok else None
            spans[mode] = (sm, sf)
        else:
            sm, hm = deploy_for(main, q)
            r = HULL + sm if sm is not None else None
            hl = hm
            spans[mode] = (sm, None)
        radius[mode], hull_load[mode] = r, hl
    if radius["HARD"] is None:
        notes.append("cannot reject HARD Metric heat")
    cap, cap_hull = main["net"](main["max_span"])
    panel_mass = main["wings"] * main["chord"] * main["max_span"] * main["areal"] / 1000
    if fore:
        panel_mass += fore["wings"] * fore["chord"] * fore["max_span"] * fore["areal"] / 1000
    if main["g"] < 7.5:
        notes.append(f"main radiators must retract for torch burns above {main['g']:.0f} g")
    # drop tanks
    D = S["drop_tanks"]
    drop = None
    # mass model
    lg = ledger
    struct = lg["structure"] if reference else S["mass_rules"]["structure_t_per_m_of_length"] * L
    mid = 0.491 * L
    items = [
        (lg["armor_fixed_shield"], 9.5, 0), (lg["habitation_life_support"], 8.0, 0),
        (lg["avionics_sensors_comms"], 12.0, 0), (lg["mission_courier_systems"], 17.0, 0),
        (lg["rcs_docking_service"], mid, 0), (lg["engineering_reserve"], mid, 0),
        (lg["thermal_radiators"], xm1 + man / 2, 0), (lg["electrical"], xm1 - 1.0, 0),
        (lg["propulsion"], shield0 + 8.5, 0), (lg["planetary_launch"], shuttle_c[0], shuttle_c[1]),
        (panel_mass, sum(root_x) / 2, 0),
    ] + [(m, x, z) for m, x, z, _, _ in blocks]
    if lay_key in ("CWRAP", "CWRAP_G"):
        items.append((lay["c_tank_penalty_t"]["value"], sum(tank_x) / 2, 0))
    if reference:
        items = [it for it in items if it[0] != panel_mass]
    dry = struct + sum(m for m, _, _ in items)
    cx = (struct * mid + sum(m * x for m, x, _ in items)) / dry
    cz = sum(m * z for m, _, z in items) / dry
    inertia = struct * L ** 2 / 12 + struct * (mid - cx) ** 2 + sum(m * (x - cx) ** 2 for m, x, _ in items)
    if drop_t:
        r = drop_d / 2
        vol = drop_t / 2 * (1 + S["fluids"]["ullage_fraction"])
        dl = vol / (math.pi * r * r)
        lo = D["forward_limit_x"]
        hi = (root_x[0] - D["clearance_m"]) if P["drop_clear_roots"] else (shield0 - D["clearance_m"])
        if hi - lo < dl:
            return None, "drop tanks can't fit"
        c = min(max(cx, lo + dl / 2), hi - dl / 2)
        sides = P["drop_tank_azimuths"] == "sides"
        drop = {"x0": c - dl / 2, "x1": c + dl / 2, "r": r, "rad": HULL + r + D["radial_gap_m"],
                "az": [0, 180] if sides else [225, 315], "shell_t": drop_t * D["shell_fraction"], "water_t": drop_t}
    wet = dry + S["fluids"]["remass_t"] + S["fluids"]["protected_water_t"]
    m0 = wet + (drop["water_t"] + drop["shell_t"] if drop else 0)
    ve = S["torch"]["ve_km_s"]
    base = ve["ECON"] * math.log(wet / (wet - S["fluids"]["remass_t"]))
    s1 = ve["ECON"] * math.log(m0 / (m0 - drop["water_t"])) if drop else 0.0
    ar = F["aft_radii_m"]
    secs = [(0, shield0, HULL), (shield0, shield0 + A["shield"], ar["shield"]),
            (shield0 + A["shield"], L - A["nozzle"], ar["reactor"]), (L - A["nozzle"], L, ar["nozzle"])]
    surf = surface(secs, protr) + main["wings"] * main["chord"] * (2 * main["prot"] + (0.5 if main["prot"] else 0))
    extent = 2 * HULL + sum(hh for _, _, hh in protr)
    if drop:
        extent = max(extent, 2 * (drop["rad"] + drop["r"]))
    return {
        "id": f"{lay_key}|{plant}|{place}|{mech}|{T}K|ext{ext}|{bay_pos}|{drop_t}",
        "layout": lay_key, "layout_label": lay["label"], "plant": plant, "place": place, "place_label": P["label"],
        "mech": mech, "mech_label": RV["mechanisms"][mech]["label"], "T": T, "ext_m": ext, "bay_pos": bay_pos,
        "drop_t": drop_t, "length_m": L, "extent_m": extent, "dry_t": dry, "start_t": m0,
        "dv_base_econ": base, "dv_total_econ": base + s1,
        "accel_g": S["torch"]["cruise_thrust_kn"] * 1000 / (m0 * 1000 * G0),
        "surface_m2": surf, "com_z": cz, "balance": abs(cz), "inertia": inertia,
        "metric_radius": radius, "hull_heat_mw": hull_load,
        "metric_radius_fast": radius["FAST"] if radius["FAST"] else 40.0,
        "metric_radius_hard": radius["HARD"] if radius["HARD"] else 40.0,
        "hull_heat_hard": hull_load["HARD"] if hull_load["HARD"] is not None else 99.0,
        "torch_capacity_mw": cap, "torch_capacity_5g": cap if main["g"] >= 5.0 else 0.0,
        "water_warming_k_per_h_hard": (hull_load["HARD"] or 0) * 1e6 * 3600 / (RV["water_heat_context"]["water_t"] * 1000 * RV["water_heat_context"]["cp_kj_kg_k"] * 1000), "torch_capacity_ppm": cap * 1e6 / (RV["torch_check"]["cruise_jet_power_tw"] * 1e12) * 1e6,
        "cryo_power_hard": heat_mw("HARD", T), "panel_mass_t": panel_mass, "torch_g": main["g"],
        "stowed_protrusion_m": main["prot"], "notes": notes,
        "geom": {"xm0": xm0, "xm1": xm1, "L": L, "shield0": shield0, "tank_x": tank_x, "bay": bay, "shuttle": shuttle_c,
                 "blocks": [(b[3], b[4], b[2]) for b in blocks], "root_x": root_x, "wing_az": P["azimuths_deg"],
                 "max_span": main["max_span"], "spans": spans, "fore": bool(fore),
                 "fore_max": fore["max_span"] if fore else 0, "drop": drop},
    }, None


def surface(sections, protrusions):
    a = math.pi * sections[0][2] ** 2 + math.pi * sections[-1][2] ** 2
    for i, (x0, x1, r) in enumerate(sections):
        a += 2 * math.pi * r * (x1 - x0)
        if i:
            a += abs(math.pi * r ** 2 - math.pi * sections[i - 1][2] ** 2)
    for L, w, h in protrusions:
        a += L * w + 2 * L * h + 2 * w * h
    return a


def pareto(ds, keys):
    return [a for a in ds if not any(all(s * b[k] >= s * a[k] - 1e-9 for k, s in keys) and
                                     any(s * b[k] > s * a[k] + 1e-9 for k, s in keys) for b in ds if b is not a)]


def score(pool, weights, fields, tag):
    for key, (field, sign) in fields.items():
        vals = [d[field] for d in pool]
        lo, hi = min(vals), max(vals)
        for d in pool:
            d.setdefault("_n", {})[key] = ((d[field] - lo) / (hi - lo) if sign > 0 else (hi - d[field]) / (hi - lo)) if hi > lo else 1.0
    for d in pool:
        d[tag] = sum(w * d["_n"][k] for k, w in weights.items())
        del d["_n"]
    return sorted(pool, key=lambda d: -d[tag])


FIELDS = {"field_wrap": ("surface_m2", -1), "metric_radius_fast": ("metric_radius_fast", -1),
          "metric_radius_hard": ("metric_radius_hard", -1), "torch_capacity_5g": ("torch_capacity_5g", 1),
          "hull_heat_hard": ("hull_heat_hard", -1), "agility": ("accel_g", 1), "balance": ("balance", -1),
          "inertia": ("inertia", -1), "dry": ("dry_t", -1), "cryo_power_hard": ("cryo_power_hard", -1)}


def main():
    repo = sys.argv[1]
    ledger = seed_ledger(repo)
    if "--reference" in sys.argv:
        d, why = build(ledger, "T4_top", "AXIS", "ROOT_QUAD", "RIGID", 900, 0, "-", reference=True)
        print(json.dumps({k: v for k, v in d.items() if k != "geom"}, indent=1, default=str))
        return
    designs, rejects = [], {}
    for lay_key, lay in S["layouts"].items():
        bays = ["centre", "forward"] if lay["shuttle"] == "on_axis" else ["-"]
        for plant, place, mech, T, ext, bp in itertools.product(["AXIS", "KEEL", "SPLIT", "AFT"], RV["placements"],
                                                                RV["mechanisms"], RV["temperatures_k"], [0, 2, 4], bays):
            d, why = build(ledger, lay_key, plant, place, mech, T, ext, bp)
            if d:
                designs.append(d)
            else:
                rejects[why] = rejects.get(why, 0) + 1
    ranked = score(designs, RV["score"]["weights"], FIELDS, "score")
    for d in ranked:
        d["torch_rated"] = d["torch_g"] >= RV["torch_rating_required_g"]["value"]
    rated = [d for d in ranked if d["torch_rated"]]
    print("BEST TORCH-RATED (headline)")
    for d in rated[:6]:
        r = d["metric_radius"]
        print(f" {d['score']:.3f} {d['id']:52s} L {d['length_m']:.1f} surf {d['surface_m2']:.0f} R N/F/E/H {r['NORMAL'] or 0:.1f}/{r['FAST'] or 0:.1f}/{r['EXPEDITE'] or 0:.1f}/{r['HARD'] or 0:.1f} torch5g {d['torch_capacity_5g']:.0f}MW ({d['torch_capacity_ppm']:.0f}ppm) hullH {d['hull_heat_hard']:.2f}MW water +{d['water_warming_k_per_h_hard']:.1f}K/h dry {d['dry_t']:.0f} {d['notes']}")
    front = pareto(designs, [(f, s) for f, s in FIELDS.values()])
    for d in designs:
        d["pareto"] = any(d is f for f in front)
    best = rated[0]
    kits = []
    for dt in S["drop_tanks"]["water_t_options"]:
        d, why = build(ledger, best["layout"], best["plant"], best["place"], best["mech"], best["T"], best["ext_m"],
                       best["bay_pos"], dt, 3.0)
        kits.append(d if d else {"id": f"kit {dt}", "why": why})
    by = lambda key: {k: next(d for d in ranked if d[key] == k)["id"] for k in sorted({d[key] for d in ranked}, key=str)}
    (HERE / "search_results_v3.json").write_text(json.dumps(
        {"version": "0.3", "n": len(designs), "rejected": rejects, "n_pareto": len(front),
         "ranked_ids": [d["id"] for d in ranked[:50]], "best_by_place": by("place"), "best_by_T": by("T"),
         "best_by_mech": by("mech"), "best_by_layout": by("layout"), "designs": ranked, "kits": kits}, indent=1, default=str))

    def line(d):
        r = d["metric_radius"]
        return (f" {d['score']:.3f} {d['id']:52s} L {d['length_m']:.1f} surf {d['surface_m2']:.0f} "
                f"R N/F/E/H {r['NORMAL'] or 0:.1f}/{r['FAST'] or 0:.1f}/{r['EXPEDITE'] or 0:.1f}/{r['HARD'] or 0:.1f} "
                f"torch {d['torch_capacity_mw']:.0f}MW({d['torch_capacity_ppm']:.0f}ppm) hullH {d['hull_heat_hard']:.1f} "
                f"dry {d['dry_t']:.0f} a {d['accel_g']:.3f} z {d['com_z']:+.2f} {d['notes']}")
    print(f"designs {len(designs)}, Pareto {len(front)}, rejected {sum(rejects.values())}: {rejects}")
    print("TOP 12"); [print(line(d)) for d in ranked[:12]]
    for key in ("place", "mech", "T", "layout"):
        print(f"BEST PER {key.upper()}")
        seen = set()
        for d in ranked:
            if d[key] not in seen:
                seen.add(d[key]); print(line(d))
    print("KITS FOR BEST")
    for d in kits:
        print(f"  {d['id']} " + (f"dv {d['dv_total_econ']:.0f} a {d['accel_g']:.2f} ext {d['extent_m']:.1f}" if "dv_total_econ" in d else d["why"]))


if __name__ == "__main__":
    main()
