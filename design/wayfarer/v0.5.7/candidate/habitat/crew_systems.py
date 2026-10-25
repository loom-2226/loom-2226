"""Crew systems close-out checks, v0.5.6 (+ v0.5.7 berth viewports) -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Closed-form checks for the L1 and habitat close-out:
  1. flight-deck columns at 5 g x 1.5 (stress, buckling, plus a 0.5 g side load);
  2. couch and berth hard points and the upper-berth posts;
  3. every deck floor carrying its deck at 5 g x 1.5, and floor L4 as a 1 bar bulkhead (L5 depressurised);
  4. the casualty route at 0 g (doors, ladder shaft, the exit from the port shaft into the medical bay);
  5. the crew acceleration doctrine (4 g cap, [V2 6113] time on the back);
  6. the storm shelter's 72 h stored backup;
  7. docking view and window assemblies.
Reads inputs/wayfarer_v05_inputs.json, inputs/cert_criteria_v0.1.json and out/wayfarer_v05_geometry.json.
Writes habitat/crew_systems_results.json. certify.py turns the results into gate checks (G5, G7, G9).
Usage: python habitat/crew_systems.py   (standard library only)"""
import json, math, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build_v05 as B
G0 = 9.80665


def load():
    I = json.loads((ROOT / "inputs/wayfarer_v05_inputs.json").read_text())
    C = json.loads((ROOT / "inputs/cert_criteria_v0.1.json").read_text())
    G = json.loads((ROOT / "out/wayfarer_v05_geometry.json").read_text())
    return I, C, G


def tube(od, wall):
    di = od - 2 * wall
    A = math.pi / 4 * (od ** 2 - di ** 2)
    Im = math.pi / 64 * (od ** 4 - di ** 4)
    return A, Im, Im / (od / 2)


def columns(I, C, G):
    CL = I["habitat"]["decks"][0]["command_layout"]
    fd, c, ld = CL["flight_deck"], CL["flight_deck"]["columns"], CL["flight_deck"]["loads"]
    P = {p["id"]: p for p in G["parts"]}
    W_t = P["flight_deck"]["mass_t"] + 2 * (ld["couch_t"] + ld["occupant_t"]) + ld["displays_t"]
    n = len(c["positions_yz_m"])
    ult = C["G5"]["design_g"] * C["G5"]["ultimate_factor"]
    Pax = W_t * 1e3 * G0 * ult / n
    A, Im, S = tube(c["od_m"], c["wall_m"])
    L = I["habitat"]["decks"][0]["x_m"][1] - fd["x_m"][1]
    E, fy = c["e_gpa"] * 1e9, c["yield_mpa"] * 1e6
    Pcr = math.pi ** 2 * E * Im / L ** 2                       # pinned-pinned: conservative for bolted ends
    V = W_t * 1e3 * G0 * ld["lateral_g"] * C["G5"]["ultimate_factor"] / n
    M = V * L / 2                                              # sway of fixed-base columns
    sig_ax, sig_comb = Pax / A, Pax / A + M / S
    return {"carried_t": round(W_t, 3), "columns": n, "length_m": round(L, 3), "ultimate_g": ult,
            "axial_kn": round(Pax / 1e3, 2), "stress_mpa": round(sig_ax / 1e6, 1), "buckling_kn": round(Pcr / 1e3, 1),
            "buckling_margin": round(Pcr / Pax, 2), "side_load_combined_mpa": round(sig_comb / 1e6, 1), "yield_mpa": c["yield_mpa"],
            "ok_stress": sig_comb <= fy, "ok_buckling": Pcr / Pax >= C["G5"]["buckling_factor"]}


def stations(I, C):
    SL = I["habitat"]["crew_systems"]["station_loads"]
    ult = C["G5"]["design_g"] * C["G5"]["ultimate_factor"]
    hp = (SL["couch_t"] + SL["occupant_t"]) * 1e3 * G0 * ult / SL["hard_points_per_station"]
    bp = SL["berth_post"]
    A, Im, S = tube(bp["od_m"], bp["wall_m"])
    Ppost = (SL["berth_pan_t"] + SL["occupant_t"]) * 1e3 * G0 * ult / 4
    Pcr = math.pi ** 2 * bp["e_gpa"] * 1e9 * Im / bp["length_m"] ** 2
    return {"hard_point_kn": round(hp / 1e3, 2), "requirement": f"each couch or berth hard point rated >= {math.ceil(hp / 1e3)} kN ultimate",
            "berth_post_kn": round(Ppost / 1e3, 2), "berth_post_buckling_kn": round(Pcr / 1e3, 1), "berth_post_margin": round(Pcr / Ppost, 1),
            "berth_post_stress_mpa": round(Ppost / A / 1e6, 1), "ok": Pcr / Ppost >= C["G5"]["buckling_factor"] and Ppost / A <= bp["yield_mpa"] * 1e6}


def floor_need(q_pa, I, A_m2):
    """mass of a sandwich floor (CFRP faces, honeycomb core) that carries pressure q over the trunk-to-hull span."""
    SL = I["habitat"]["crew_systems"]["station_loads"]["floor"]
    mat = I["materials"]
    h_eff = SL["depth_m"] * 0.93
    M = q_pa * SL["span_m"] ** 2 / 8
    tf = M / (mat["cfrp_allowable_mpa"] * 1e6 * h_eff)
    m = (2 * tf * mat["cfrp_density_t_m3"] + SL["core_t_m3"] * SL["depth_m"]) * A_m2
    tau = q_pa * SL["span_m"] / 2 / h_eff
    return tf, m, tau


def floors(I, C, G):
    hab = I["habitat"]
    ult = C["G5"]["design_g"] * C["G5"]["ultimate_factor"]
    P = {p["id"]: p for p in G["parts"]}
    skip_pre = ("armor", "pressure_vessel", "core_trunk", "core_racks", "bow_sensors", "floor_", "aft_bulkhead", "nose_window_frame",
                "window_", "hatch_", "trunk_plug", "skin_", "longeron", "frame_", "rcs_")
    lw = hab["ladderways"]
    A = math.pi * (hab["usable_r_m"] ** 2 - hab["core_r_m"] ** 2) - sum(l["size_m"] ** 2 for l in lw)
    fluids = G["fluids_by_state"]["S1"]
    out = []
    for d in hab["decks"][:-1]:
        x0, x1 = d["x_m"]
        m = sum(p["mass_t"] for p in G["parts"] if x0 <= p["centroid_m"][0] < x1 and not p["id"].startswith(skip_pre))
        m += sum(p["mass_t"] for p in fluids if x0 <= p["centroid_m"][0] < x1)
        people = sum(r.get("couches", 0) or 0 for r in d["rooms"]) * hab["crew_systems"]["station_loads"]["occupant_t"]
        m += people
        q = m * 1e3 * G0 * ult / A
        tf, need, tau = floor_need(q, I, A)
        have = P[f"floor_{d['id']}"]["mass_t"]
        out.append({"deck": d["id"], "carried_t": round(m, 2), "people_t": round(people, 2), "pressure_kpa": round(q / 1e3, 1),
                    "face_mm": round(tf * 1e3, 2), "needed_t": round(need, 2), "floor_t": round(have, 3), "core_shear_mpa": round(tau / 1e6, 3),
                    "ok": need <= have and tau / 1e6 <= hab["crew_systems"]["station_loads"]["floor"]["core_shear_mpa"]})
    iso = hab["crew_systems"]["l4_l5_isolation"]
    q = iso["pressure_kpa"] * 1e3 * iso["burst_factor"]
    tf, need, tau = floor_need(q, I, A)
    have = P["floor_L4"]["mass_t"]
    bulk = {"pressure_kpa": iso["pressure_kpa"], "factor": iso["burst_factor"], "face_mm": round(tf * 1e3, 2), "needed_t": round(need, 2),
            "floor_t": round(have, 3), "core_shear_mpa": round(tau / 1e6, 2), "core_shear_allow_mpa": hab["crew_systems"]["station_loads"]["floor"]["core_shear_mpa"],
            "hatches": len(iso["hatches"]), "trunk_plug": any(p["id"] == "trunk_plug_L4L5" for p in G["parts"]),
            "ok": need <= have and tau / 1e6 <= hab["crew_systems"]["station_loads"]["floor"]["core_shear_mpa"]}
    return out, bulk


def casualty(I, G):
    hab = I["habitat"]
    CS = hab["crew_systems"]
    Lt, Wt, Dt, mg = (CS["litter"][k] for k in ("length_m", "width_m", "depth_m", "margin_m"))
    res = {"doctrine": CS["casualty_doctrine"]}
    res["axial_fits_deck"] = {"need_m": Lt + mg, "clear_height_m": hab["clear_height_m"], "ok": Lt + mg <= hab["clear_height_m"]}
    doors = [(r["id"], r["door"]) for d in hab["decks"] for r in d["rooms"] if "door" in r]
    hmin = min(dr.get("height_m", 0) for _, dr in doors)
    wmin = min(dr["clear_width_m"] for _, dr in doors)
    res["doors"] = {"count": len(doors), "min_height_m": hmin, "min_width_m": wmin, "need_height_m": Lt + mg, "need_width_m": Wt + 2 * mg,
                    "ok": hmin >= Lt + mg - 1e-9 and wmin >= Wt + 2 * mg - 1e-9}
    sh = CS["ladder_shafts"]["clear_m"]
    need = sorted([Wt + 2 * mg, Dt + 2 * mg], reverse=True)
    res["shaft"] = {"clear_m": sh, "need_m": need, "rungs_on": CS["ladder_shafts"]["rungs_on"],
                    "ok": sorted(sh, reverse=True)[0] >= need[0] and sorted(sh, reverse=True)[1] >= need[1]}
    # port shaft (theta 180) runs L1 to L4: the ladderways are the same on every floor
    port = next(l for l in hab["ladderways"] if l["theta_deg"] == 180)
    med = next(r for d in hab["decks"] for r in d["rooms"] if r["kind"] == "medical")
    e = med["entrance"]
    half = math.degrees(e["clear_width_m"] / 2 / e["at_r_m"])
    a0, a1 = e["center_deg"] - half, e["center_deg"] + half
    # the litter (axis along x) leaves the shaft radially; its plan section is Dt (tangential) x Wt (radial); centred on the shaft
    yz = []
    for s in (-1, 1):
        t = s * (Dt / 2 + mg)                                 # tangential half-width with margin
        r = e["at_r_m"]
        ang = 180 - math.degrees(math.asin(t / r))
        yz.append(ang)
    lo, hi = min(yz), max(yz)
    edge_margin_m = min(lo - a0, a1 - hi) * math.pi / 180 * e["at_r_m"]
    inside_room = a0 >= med["theta_deg"][0] - 1e-9 and a1 <= med["theta_deg"][1] + 1e-9
    res["shaft_to_medical"] = {"shaft_theta_deg": port["theta_deg"], "entrance_deg": [round(a0, 1), round(a1, 1)],
                               "litter_crosses_deg": [round(lo, 1), round(hi, 1)], "edge_margin_m": round(edge_margin_m, 2),
                               "entrance_inside_medical_wall": inside_room, "ok": edge_margin_m >= 0.1 and inside_room}
    # treatment couch lying radially in the bay at the entrance centre
    rr = math.hypot(1.95 + Lt, Wt / 2)
    res["bay_fits_litter"] = {"outer_corner_r_m": round(rr, 3), "room_r_m": hab["usable_r_m"], "ok": rr <= hab["usable_r_m"]}
    res["ok"] = all(v["ok"] for k, v in res.items() if isinstance(v, dict))
    return res


def accel(I, G):
    AD = I["habitat"]["crew_systems"]["accel_doctrine"]
    P = I["torch"]["jet_power_tw"] * 1e12
    ve = I["canon"]["torch_ve_km_s"]
    M0 = G["states"]["S1"]["mass_t"] * 1e3
    rem = I["states"]["S1"]["remass_t"] * 1e3
    cap = AD["sustained_cap_g"]

    def allowed_min(g):        # OCHMO evidence: 2 g >= 24 h, 4 g >= 60 min; log-linear between, conservative at the burn's peak
        if g <= 2.0:
            return 1440.0
        return 1440.0 * math.exp(-math.log(1440.0 / 60.0) * (min(g, 4.0) - 2.0) / 2.0)

    rows = []
    for m, v in ve.items():
        F = 2 * P / (v * 1e3)
        t, mm, peak, n = 0.0, M0, 0.0, 4000
        dm = rem / n
        for _ in range(n):
            a = min(F / mm, cap * G0)
            mdot = mm * a / (v * 1e3)
            t += dm / mdot
            peak = max(peak, a / G0)
            mm -= dm
        a0 = min(F / M0, cap * G0) / G0
        couch = peak > AD["couch_above_g"]
        tmin = t / 60
        row = {"mode": m, "ve_km_s": v, "accel_start_g": round(a0, 2), "accel_peak_g": round(peak, 2), "capped": F / (M0 - rem) / G0 > cap,
               "full_remass_burn_min": round(tmin, 1), "in_couches": couch}
        if couch:
            row["ochmo_allowed_min"] = round(allowed_min(peak), 0)
            row["split_needed"] = tmin > AD["on_back_nominal_min"]
            row["longest_couch_period_min"] = round(min(tmin, AD["on_back_nominal_min"]), 1)
            row["ok"] = tmin <= allowed_min(peak) and row["longest_couch_period_min"] <= AD["on_back_limit_min"]
        rows.append(row)
    return {"cap_g": cap, "rows": rows, "ok": all(r.get("ok", True) for r in rows),
            "note": "Full usable remass (S1) in one burn at full jet power, throttled to the crew cap. OCHMO allowed time interpolated log-linearly between its two +Gx evidence points (2 g >= 24 h, 4 g >= 60 min) at the burn's peak acceleration."}


def shelter(I, G):
    S = I["habitat"]["crew_systems"]["shelter_backup"]
    days = S["hours"] / 24
    o2 = S["people"] * days * S["o2_kg_per_person_day"]
    co2 = S["people"] * days * S["co2_kg_per_person_day"]
    lioh = co2 * S["lioh_kg_per_kg_co2"] / S["lioh_utilisation"]
    food = S["people"] * days * S["food_kg_per_person_day"]
    water = S["people"] * days * S["drink_kg_per_person_day"]
    batt = S["essential_load_kw"] * S["battery_hours"] / S["battery_kwh_per_kg"]
    mass = o2 * S["o2_tank_factor"] + lioh * S["canister_factor"] + food * S["food_packaging_factor"] + batt + S["fans_sensors_t"] * 1e3
    jacket = G["protected_water"]["shelter_jacket_t"]
    heat = S["people"] * S["heat_per_person_kw"] + S["essential_load_kw"]
    return {"o2_kg": round(o2, 1), "co2_kg": round(co2, 1), "lioh_kg": round(lioh, 1), "food_kg": round(food, 1), "drink_water_kg": round(water, 1),
            "battery_kg": round(batt, 1), "stored_mass_t": round(mass / 1e3, 3), "allotted_t": S["mass_t"],
            "water_from_jacket_fraction": round(water / 1e3 / jacket, 4), "heat_kw": round(heat, 2), "ok": mass / 1e3 <= S["mass_t"]}


def docking_and_windows(I, G):
    W = [f for f in G["features"] if f["kind"] == "window"]
    cams = [f for f in G["features"] if f["kind"] == "camera"]
    ves = [f for f in W if f["room"].endswith("vestibule")]
    wparts = [p for p in G["parts"] if p["id"] == "nose_window_frame" or p["id"].startswith("window_")]
    draw = I["ledger"]["reserve_draws_v056"]["windows_t"] + sum(I["ledger"].get("reserve_draws_v057", {}).get(k, 0.0) for k in ("berth_viewports_t", "habitat_viewports_t", "nose_windows_removed_t", "observation_windows_removed_t"))
    nberth = len([f for f in W if f.get("berth")])
    return {"windows": len(W), "window_assembly_t": round(sum(p["mass_t"] for p in wparts), 3), "ledger_windows_t": draw,
            "cameras": len(cams), "vestibule_window": bool(ves), "bore_splay_deg": (G.get("window_bore") or {}).get("splay_deg"),
            "berth_viewports": nberth, "ok": 10 <= len(W) - nberth <= 16 and len(cams) >= 2 and bool(ves) and abs(sum(p["mass_t"] for p in wparts) - draw) < 0.01}


def hab_scene(I, G):
    """render input: berths, doors, ladder shafts, medical doors and the casualty route, from the inputs and geometry."""
    hab = I["habitat"]
    CS = hab["crew_systems"]
    SL = CS["station_loads"]
    tier_h = SL["berth_post"]["length_m"]
    bunks = []
    for r in G["rooms"]:
        for b in r.get("bunks", []):
            for t in range(b["tiers"]):
                bunks.append({"room": r["id"], "angle_deg": b["angle_deg"], "radial_m": b["radial_m"], "width_m": b["width_m"],
                              "pan_x": r["x_m"][1] - 0.25 - tier_h * t, "tier": t + 1, "tiers": b["tiers"]})
    doors = [{"room": r["id"], "center_deg": r["door"]["center_deg"], "width_m": r["door"]["clear_width_m"], "height_m": r["door"].get("height_m", 2.0),
              "floor_x": r["x_m"][1], "at_r_m": hab["corridor_r_m"][1]} for r in G["rooms"] if r.get("door")]
    med = next(r for r in G["rooms"] if r["kind"] == "medical")
    e = med["entrance"]
    decks = [{"id": d["id"], "x_m": d["x_m"]} for d in hab["decks"]]
    port = next(l for l in hab["ladderways"] if l["theta_deg"] == 180)
    py, pz = port["r_m"] * math.cos(math.radians(180)), 0.0
    l1_floor = hab["decks"][0]["x_m"][1]
    l4 = next(d for d in hab["decks"] if d["id"] == "L4")
    th = math.radians(180)
    route = [[l1_floor - 1.2, py, pz], [l1_floor, py, pz], [l4["x_m"][1] - 1.0, py, pz], [l4["x_m"][1] - 0.5, py, pz],
             [l4["x_m"][1] - 0.5, 3.0 * math.cos(th), 3.0 * math.sin(th)]]
    lit = CS["litter"]
    return {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "VISUAL REFERENCE input: habitat crew systems (NON-GOVERNING)",
            "bunks": bunks, "doors": doors, "decks": decks, "ladderways": hab["ladderways"], "floor_t_m": hab["floor_thickness_m"],
            "medical": {"center_deg": e["center_deg"], "width_m": e["clear_width_m"], "at_r_m": e["at_r_m"], "x_m": med["x_m"]},
            "litter": {"length_m": lit["length_m"], "width_m": lit["width_m"], "pose": {"theta_deg": 180, "r_m": [1.95, 1.95 + lit["length_m"]], "x": l4["x_m"][1] - 0.6}},
            "route": route, "rungs_on": "inboard"}


def viewport_band(I, C, G):
    """v0.5.7 rev 3: the L2 panoramic band. Mullions carry the axial load across the band (5 g x 1.5 of everything ahead,
    depressurised; or the pressure end load x 2.0 at 1 g); curved panes carry cabin pressure as hoop membranes."""
    VB = I["habitat"].get("crew_systems", {}).get("viewport_band")
    if not VB:
        return None
    H = I["hull"]
    Rp = H["pressure_r_m"]
    x0 = min(sg["x_m"][0] for sg in VB["segments"])
    ahead = 0.0
    for p in G["parts"]:
        if p["id"] in ("armor", "pressure_vessel"):   # shells that span the band: count the share ahead of it
            pts = B.shape_from_spec(p["shape"]).sample(random.Random(3), 4000)
            ahead += p["mass_t"] * sum(1 for q in pts if q[0] < x0) / len(pts)
        elif p["centroid_m"][0] < x0:
            ahead += p["mass_t"]
    g0 = 9.80665
    F_thrust = ahead * 1e3 * C["G5"]["design_g"] * C["G5"]["ultimate_factor"] * g0
    p = 101.325e3
    F_press = 2.0 * p * math.pi * Rp ** 2 - ahead * 1e3 * g0
    span = sum(sg["theta_deg"][1] - sg["theta_deg"][0] for sg in VB["segments"])
    n = int(round(span / VB["mullion_spacing_deg"])) + 1
    t, w = 0.05, 0.20                       # titanium blade, 5 cm thick (sideways), 20 cm deep (radially, inside the armour depth)
    A = t * w
    allow = 600e6                           # Ti-6Al-4V ultimate design (900 MPa UTS, knocked down for joints)
    E = 114e9
    worst = max(F_thrust, F_press)
    sig = worst / (n * A)
    Lm = max(sg["x_m"][1] - sg["x_m"][0] for sg in VB["segments"])
    Imin = w * t ** 3 / 12
    Pcr = math.pi ** 2 * E * Imin / Lm ** 2            # pinned, conservative (the forked ends are built in)
    buck = Pcr / (F_thrust / n)
    pane_mm = max(6.0, 2.0 * p * Rp / 70e6 * 1e3)    # hoop membrane, ALON 2026 at 70 MPa, proof factor 2
    area = VB["glazed_area_m2"]
    others = sum(math.pi * (f["d_m"] / 2) ** 2 for f in G["features"] if f["kind"] == "window")
    crown = I["habitat"]["decks"][0].get("command_layout", {}).get("crown_dome", {}).get("glazed_area_m2", 0.0)
    glazing = area + others + crown
    return {"glazed_area_m2": area, "mass_ahead_t": round(ahead, 1), "mullions": n, "mullion_section_m": [t, w],
            "axial_load_thrust_mn": round(F_thrust / 1e6, 2), "axial_load_pressure_mn": round(F_press / 1e6, 2),
            "mullion_stress_mpa": round(sig / 1e6, 1), "allow_mpa": allow / 1e6, "mullion_buckling_margin": round(buck, 1), "tallest_mullion_m": Lm,
            "pane_mm_each": round(pane_mm, 1), "pane_mm_assumed": 16,
            "glazing_total_m2": round(glazing, 1), "heat_loss_kw_all_open": round(glazing * 42 / 1000, 2),
            "ok": sig <= allow and buck >= C["G5"]["buckling_factor"] and pane_mm <= 16}


def run():
    I, C, G = load()
    fl, bulk = floors(I, C, G)
    return {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING closed-form checks, v0.5.6 crew systems",
            "flight_deck_columns": columns(I, C, G), "stations": stations(I, C), "floors": fl, "l4_l5_bulkhead": bulk,
            "casualty_route": casualty(I, G), "acceleration": accel(I, G), "shelter_backup": shelter(I, G),
            "docking_and_windows": docking_and_windows(I, G), "viewport_band": viewport_band(I, C, G)}


if __name__ == "__main__":
    r = run()
    (ROOT / "habitat/crew_systems_results.json").write_text(json.dumps(r, indent=1))
    I, C, G = load()
    (ROOT / "render/out/hab_scene.json").write_text(json.dumps(hab_scene(I, G), indent=1))
    print(json.dumps(r, indent=1))
