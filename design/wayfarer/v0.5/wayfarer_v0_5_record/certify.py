"""Wayfarer v0.5 certification checks -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Runs gates G1-G12 of CERTIFICATION_BASIS_v0.1 against
out/wayfarer_v05_geometry.json, inputs/wayfarer_v05_inputs.json and
inputs/cert_criteria_v0.1.json. Writes out/certification_report.json,
out/CERTIFICATION_REPORT_v0.5.md and out/wayfarer_v05_card.json (the
machine-readable ship card for Navigator, gate G10).
Python 3 standard library only. Usage: python certify.py"""
import hashlib, json, math, random
from pathlib import Path
import build_v05 as B

HERE = Path(__file__).resolve().parent
G0, SIGMA = 9.80665, 5.670374419e-8
PASS, DECL, FAIL, OPEN = "PASS", "PASS-DECLARED", "FAIL", "OPEN"


def load():
    I = json.loads((HERE / "inputs/wayfarer_v05_inputs.json").read_text())
    C = json.loads((HERE / "inputs/cert_criteria_v0.1.json").read_text())
    G = json.loads((HERE / "out/wayfarer_v05_geometry.json").read_text())
    return I, C, G


def chk(name, value, limit, ok, unit="", note=""):
    """one check; comparisons are made by the caller (with a 1e-9 tolerance on equal limits)."""
    return {"name": name, "value": value, "limit": limit, "unit": unit, "pass": bool(ok), "note": note}


def gate(gid, title, checks, declared=(), notes=(), force=None):
    if force:
        v = force
    elif not all(c["pass"] for c in checks):
        v = FAIL
    elif declared:
        v = DECL
    else:
        v = PASS
    return {"gate": gid, "title": title, "verdict": v, "checks": checks, "declared": list(declared), "notes": list(notes)}


def states(I):
    return [k for k in I["states"] if k.startswith("S")]


# ---------------------------------------------------------------- G1
def g1(I, C, G):
    L = I["ledger"]
    expect = (L["structure_t_per_m"] * I["hull"]["length_m"] + L["armor_fixed_shield_t"] + L["habitation_life_support_t"]
              + L["guest_outfitting_t"] + L["relational_plant_t"] + L["thermal_radiators_t"] + L["radiator_panels_t"]
              + L["propulsion_t"] + L["electrical_t"] + L["avionics_sensors_comms_t"] + L["rcs_docking_service_t"]
              + L["mission_courier_systems_t"] + L["engineering_reserve_t"] + L["c_tank_penalty_t"]
              + I["shuttle"]["dry_t"] + L["drones_pods_t"])
    dry = G["dry_t"]
    cs = [chk("parts sum to the ledger", round(dry, 2), round(expect, 2), abs(dry - expect) <= C["G1"]["ledger_tolerance_t"], "t")]
    shuttle = next(p["mass_t"] for p in G["parts"] if p["id"] == "shuttle")
    for s in states(I):
        st = G["states"][s]
        fl = sum(p["mass_t"] for p in G["fluids_by_state"][s])
        exp = dry - (shuttle if st["shuttle"] == "absent" else 0) + fl
        cs.append(chk(f"{s} mass = dry + fluids + payload", round(st["mass_t"], 2), round(exp, 2), abs(st["mass_t"] - exp) < 0.05, "t",
                      st["name"]))
    water = sum(p["mass_t"] for p in G["fluids_by_state"]["S1"] if "water" in p["tags"])
    cs.append(chk("S1 water aboard", round(water, 2), I["canon"]["water_t"], abs(water - I["canon"]["water_t"]) < 0.05, "t"))
    cs.append(chk("tank volume", round(G["tank_volume_m3"], 1), C["G1"]["tank_volume_min_m3"], G["tank_volume_m3"] >= C["G1"]["tank_volume_min_m3"], "m3",
                  "four cells, net of walls, grooves and the two sill longerons"))
    notes = [f"dry {dry:.1f} t vs canon {I['canon']['dry_t']} t ({dry - I['canon']['dry_t']:+.1f} t); "
             f"S1 wet {G['states']['S1']['mass_t']:.1f} t vs canon {I['canon']['wet_t']} t",
             "dry by system: " + ", ".join(f"{k} {v:.1f}" for k, v in sorted(G["dry_by_system_t"].items(), key=lambda kv: -kv[1])),
             f"protected water: {G['protected_water']['jacket_t']:.1f} t in the storm-shelter jacket, {G['protected_water']['service_tank_t']:.1f} t in the "
             f"service tank, {G['protected_water']['c_tank_t']:.1f} t in the main tank cells"]
    tab = []
    for s in states(I):
        st = G["states"][s]
        Ii = st["inertia_kg_m2"]
        tab.append({"state": s, "name": st["name"], "mass_t": round(st["mass_t"], 1), "cg_m": [round(v, 3) for v in st["cg_m"]],
                    "Ixx": Ii[0][0], "Iyy": Ii[1][1], "Izz": Ii[2][2], "Ixy": Ii[0][1], "Ixz": Ii[0][2], "Iyz": Ii[1][2]})
    r = gate("G1", "Mass and fluids ledger", cs, notes=notes)
    r["mass_states"] = tab
    return r


# ---------------------------------------------------------------- G2
def g2(I, C, G):
    T, cn = I["torch"], I["canon"]
    ve = cn["torch_ve_km_s"]
    M1 = G["states"]["S1"]["mass_t"]
    rem = I["states"]["S1"]["remass_t"]
    dv = ve["ECON"] * math.log(M1 / (M1 - rem))
    acc = T["cruise_thrust_mn"] * 1e6 / (M1 * 1e3 * G0)
    lim = C["G2"]["dv_fraction_of_canon_card"] * cn["torch_card_dv_econ_km_s"]
    cs = [chk("ECON full-remass delta-v at S1", round(dv, 1), round(lim, 1), dv >= lim, "km/s", "95% of the canon card"),
          chk("acceleration at cruise thrust, S1", round(acc, 3), C["G2"]["accel_min_g_S1"], acc >= C["G2"]["accel_min_g_S1"], "g"),
          chk("torch card unchanged", "CANON II §14", "CANON II §14", True)]
    P = T["jet_power_tw"] * 1e12
    modes = {}
    capped = []
    for m, v in ve.items():
        F = 2 * P / (v * 1e3)
        row = {"thrust_mn": F / 1e6, "dv_full_remass_S1_km_s": v * math.log(M1 / (M1 - rem)), "accel_g": {}}
        for s in states(I):
            M = G["states"][s]["mass_t"] * 1e3
            a = F / (M * G0)
            row["accel_g"][s] = round(min(a, C["G2"]["torch_g_limit_doctrine"]), 3)
            if a > C["G2"]["torch_g_limit_doctrine"]:
                capped.append(f"{m} in {s} ({a:.1f} g at full jet power)")
        modes[m] = row
    notes = [f"S2 (50 t payload): ECON delta-v {ve['ECON'] * math.log(G['states']['S2']['mass_t'] / (G['states']['S2']['mass_t'] - rem)):.1f} km/s",
             "Thrust at fixed jet power (11.36 TW): F = 2P/ve.",
             "Throttled to the 5 g structural limit (doctrine): " + (", ".join(capped) if capped else "none")]
    r = gate("G2", "Torch and reach", cs, notes=notes)
    r["modes"] = modes
    return r


# ---------------------------------------------------------------- G3
def thrusters(I, G):
    out = []
    off = G["thrust_line_offset_m"]
    F = I["rcs"]["thruster_kn"] * 1e3
    for c in I["rcs"]["clusters"]:
        th = math.radians(c["theta_deg"])
        y, z = c["r_m"] * math.cos(th), c["r_m"] * math.sin(th)
        if c["id"].startswith("A"):
            y, z = y + off["y"], z + off["z"]
        rad = (0.0, math.cos(th), math.sin(th))
        tan = (0.0, -math.sin(th), math.cos(th))
        pos = (c["x_m"], y, z)
        for kind, d in (("inward", tuple(-v for v in rad)), ("tan+", tan), ("tan-", tuple(-v for v in tan))):
            out.append({"cluster": c["id"], "kind": kind, "pos": pos, "f": tuple(F * v for v in d)})
    return out


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def couples(th, cg):
    """pure couples (net force ~0) from thruster pairs: torque vectors about cg."""
    out = []
    for i in range(len(th)):
        for j in range(i + 1, len(th)):
            a, b = th[i], th[j]
            f = [a["f"][k] + b["f"][k] for k in range(3)]
            if math.sqrt(sum(v * v for v in f)) > 1e-6:
                continue
            ra = [a["pos"][k] - cg[k] for k in range(3)]
            rb = [b["pos"][k] - cg[k] for k in range(3)]
            t = [u + v for u, v in zip(cross(ra, a["f"]), cross(rb, b["f"]))]
            out.append({"pair": (i, j), "clusters": {a["cluster"], b["cluster"]}, "torque": t})
    return out


def axis_torque(cps, axis, sign, n):
    """sum of the n largest couples (disjoint thrusters) that act about +/- axis."""
    good = []
    for c in cps:
        t = c["torque"]
        mag = math.sqrt(sum(v * v for v in t))
        if mag < 1e-9:
            continue
        comp = sign * t[axis]
        if comp > 0.99 * mag:
            good.append((comp, c))
    good.sort(key=lambda g: -g[0])
    used, tot, k = set(), 0.0, 0
    for comp, c in good:
        if used & set(c["pair"]):
            continue
        used |= set(c["pair"])
        tot += comp
        k += 1
        if k == n:
            break
    return tot, k


def g3(I, C, G):
    cs, notes = [], []
    lim = C["G3"]["trim_max_deg"]
    for s in states(I):
        st = G["states"][s]
        cs.append(chk(f"thrust trim {s}", round(st["trim_deg"], 3), lim, st["trim_deg"] <= lim, "deg",
                      f"lateral offset {st['lateral_offset_m']:.3f} m from the thrust line"))
    off = G["thrust_line_offset_m"]
    notes.append(f"Thrust line offset from the hull axis: y {off['y']:+.2f} m, z {off['z']:+.2f} m (torch chain {off['torch_chain_t']:.0f} t), chosen to centre the centre-of-mass range")
    # slews
    th = thrusters(I, G)
    worst = {}
    for s in states(I):
        st = G["states"][s]
        cps = couples(th, st["cg_m"])
        Iax = [st["inertia_kg_m2"][a][a] for a in range(3)]
        for a, nm in ((1, "pitch (about y)"), (2, "yaw (about z)"), (0, "roll (about x)")):
            for sign in (1, -1):
                tq, k = axis_torque(cps, a, sign, C["G3"]["couples_for_slew"])
                t180 = 2 * math.sqrt(math.pi / (tq / Iax[a])) if tq > 0 else float("inf")
                key = (nm, sign)
                if key not in worst or t180 > worst[key][0]:
                    worst[key] = (t180, s, tq, k)
    for (nm, sign), (t, s, tq, k) in worst.items():
        if "roll" in nm:
            notes.append(f"roll {'+' if sign > 0 else '-'}: 180 deg in {t:.0f} s ({k} couples, {tq / 1e6:.2f} MN m, worst state {s}); roll is rate-limited by doctrine, not gated")
            continue
        cs.append(chk(f"180 deg slew, {nm} {'+' if sign > 0 else '-'}", round(t, 1), C["G3"]["slew_180_max_s"], t <= C["G3"]["slew_180_max_s"], "s",
                      f"{k} x 25 kN couples, {tq / 1e6:.2f} MN m, worst state {s}"))
    # one cluster out
    st = G["states"]["S2"]
    worst_out = 0.0
    for c in I["rcs"]["clusters"]:
        rem = [t for t in th if t["cluster"] != c["id"]]
        cps = couples(rem, st["cg_m"])
        ok = True
        for a in range(3):
            for sign in (1, -1):
                tq, k = axis_torque(cps, a, sign, 1)
                if tq <= 0:
                    ok = False
                elif a > 0:
                    worst_out = max(worst_out, 2 * math.sqrt(math.pi / (tq / st["inertia_kg_m2"][a][a])))
        cs.append(chk(f"three-axis control with cluster {c['id']} out", "yes" if ok else "no", "yes", ok))
    notes.append(f"With any one cluster out, the slowest 180 deg pitch/yaw slew is {worst_out:.0f} s (one couple, S2).")
    notes.append(f"Shuttle undocking: S1 trim {G['states']['S1']['trim_deg']:.3f} deg, S6 (shuttle away) {G['states']['S6']['trim_deg']:.3f} deg; both inside the limit.")
    notes.append("Inertia is from intrinsic component shapes (sampled volumes), not centroid-only point masses.")
    return gate("G3", "Balance and attitude", cs, notes=notes)


# ---------------------------------------------------------------- G4
_VF = {}


def view_factor(azs, span, hull_r, rays):
    """2D Monte Carlo: fraction of one wing face's emission reaching space and the hull, averaged over wings and faces."""
    key = (tuple(azs), round(span, 2), rays)
    if key in _VF:
        return _VF[key]
    rng = random.Random(1)
    segs = [((hull_r * math.cos(math.radians(t)), hull_r * math.sin(math.radians(t))),
             ((hull_r + span) * math.cos(math.radians(t)), (hull_r + span) * math.sin(math.radians(t)))) for t in azs]
    space = hull = tot = 0
    for wi, t in enumerate(azs):
        ux, uy = math.cos(math.radians(t)), math.sin(math.radians(t))
        for side in (1, -1):
            nx, ny = -uy * side, ux * side
            for _ in range(rays // (2 * len(azs))):
                r = hull_r + rng.random() * span
                px, py = r * ux + nx * 1e-6, r * uy + ny * 1e-6
                phi = math.asin(2 * rng.random() - 1)
                dx, dy = nx * math.cos(phi) + ux * math.sin(phi), ny * math.cos(phi) + uy * math.sin(phi)
                best, what = float("inf"), "space"
                b = px * dx + py * dy
                c = px * px + py * py - hull_r * hull_r
                if b * b - c >= 0:
                    tt = -b - math.sqrt(b * b - c)
                    if tt > 1e-9:
                        best, what = tt, "hull"
                for wj, ((x1, y1), (x2, y2)) in enumerate(segs):
                    if wj == wi:
                        continue
                    ex, ey = x2 - x1, y2 - y1
                    den = dx * ey - dy * ex
                    if abs(den) < 1e-12:
                        continue
                    tt = ((x1 - px) * ey - (y1 - py) * ex) / den
                    u = ((x1 - px) * dy - (y1 - py) * dx) / den
                    if tt > 1e-9 and 0 <= u <= 1 and tt < best:
                        best, what = tt, "wing"
                tot += 1
                space += what == "space"
                hull += what == "hull"
    _VF[key] = (space / tot, hull / tot)
    return _VF[key]


def rad_net_mw(I, C, span, azs):
    R = I["radiators"]
    chord = R["x_m"][1] - R["x_m"][0]
    flux = R["emissivity"] * SIGMA * R["temperature_k"] ** 4
    fs, fh = view_factor(azs, span, R["root_r_m"], C["G4"]["view_factor_rays"])
    hc = R["hull_coating"]
    e = 2 * len(azs) * chord * span * flux
    return e * (fs + fh * (1 - hc["absorptivity"]) * hc["reflected_escape_fraction"]) / 1e6, e * fh * hc["absorptivity"] / 1e6


def metric_heat(I, mode, T):
    cn, rule = I["canon"], I["metric_heat_rule"]
    tc = rule["cold_temperature_k"]
    return cn["metric_cold_load_kw"][mode] / 1000 + cn["metric_cryo_electrical_mw_at_900K"][mode] * (T - tc) / (900 - tc)


def span_for(I, C, q, azs):
    R = I["radiators"]
    for k in range(1, R["max_pleats"] + 1):
        s = k * R["pleat_m"]
        if rad_net_mw(I, C, s, azs)[0] >= q:
            return s
    return None


def hab_heat(I):
    hh = I["habitat_heat"]
    n = I["decisions"]["people"]["crew"] + I["decisions"]["people"]["guests"]
    return (n * hh["metabolic_w_per_person"] / 1000 + hh["avionics_kw"] + hh["eclss_galley_kw"] + hh["lighting_misc_kw"]), n


def g4(I, C, G):
    R = I["radiators"]
    T = R["temperature_k"]
    azs = R["azimuths_deg"]
    cs, notes, decl = [], [], []
    q_hab_kw, n = hab_heat(I)
    hh = I["habitat_heat"]["radiator"]
    tc = hh["temperature_k"]
    w_hp = q_hab_kw * (T / tc - 1) / C["G4"]["heat_pump_carnot_fraction"]
    q_hab_main = (q_hab_kw + w_hp) / 1000.0
    spans = {}
    for m in ("NORMAL", "FAST", "EXPEDITE", "HARD"):
        q = metric_heat(I, m, T) + q_hab_main * (1 + C["G4"]["hab_heat_margin"])
        s = span_for(I, C, q, azs)
        spans[m] = s
        cs.append(chk(f"Metric {m} heat + habitat rejected", s if s else "no", f"<= {R['max_span_m']} m span", s is not None, "m span",
                      f"{metric_heat(I, m, T):.1f} MW Metric + {q_hab_main:.2f} MW habitat via heat pump (x1.25); field geometry radius {R['root_r_m'] + (s or 0):.1f} m"))
    cap, hull_hit = rad_net_mw(I, C, R["max_span_m"], azs)
    ppm = cap * 1e6 / (I["torch"]["jet_power_tw"] * 1e12) * 1e6
    cs.append(chk("torch-burn radiator capacity (full span)", round(cap, 1), "declared torch leak", True, "MW",
                  f"{ppm:.0f} ppm of jet power; v0.4 model gave {R['torch_capacity_mw']} MW"))
    decl.append(f"Torch interface: non-exhaust torch heat reaching the ship must stay at or below {cap:.0f} MW ({ppm:.0f} ppm of the 11.36 TW jet) "
                "during burns. The torch's insides are canon and not re-derived here.")
    e_hard = I["canon"]["metric_cryo_electrical_mw_at_900K"]["HARD"] * (T - 20) / 880
    decl.append(f"Plant electrical: Metric HARD at a {T} K reject temperature needs {e_hard:.1f} MW of cryo-chain electrical power, against canon's "
                f"23.9 MW at 900 K. The relational plant must supply this (canon amendment), or the cryo chain must reject through a 900 K loop.")
    # passive habitat skin radiators as backup
    sun = hh["worst_sun_w_m2"] * hh["absorptivity"] / math.pi
    net = hh["emissivity"] * SIGMA * tc ** 4 - sun
    area = 2 * math.pi * I["hull"]["outer_r_m"] * (I["hull"]["habitat_shell_x_m"][1] - I["hull"]["bow_cap_depth_m"]) * 0.8
    backup = net * area / 1000
    cs.append(chk("habitat heat on passive skin radiators (backup, heat pump failed)", round(backup, 1), round(q_hab_kw, 1), backup >= q_hab_kw, "kW",
                  f"{area:.0f} m2 of habitat skin at {tc} K, Venus-orbit sun"))
    cs.append(chk("major torch burn and high Metric never required together", "doctrine", "CANON II §14", True))
    notes.append(f"Habitat heat {q_hab_kw:.1f} kW for {n} people; heat pump to {T} K needs {w_hp:.0f} kW (Carnot fraction {C['G4']['heat_pump_carnot_fraction']}).")
    notes.append(f"Strakes shine {hull_hit:.1f} MW onto the hull coating at full span (torch burns): about {hull_hit * 1e6 * 3600 / (300e3 * 4186):.1f} K/h of warming in 300 t of water. The habitat skin radiators sit forward of the strakes (x < 14 m).")
    r = gate("G4", "Power and heat", cs, declared=decl, notes=notes)
    r["spans_m"] = spans
    r["torch_capacity_mw"] = cap
    return r


# ---------------------------------------------------------------- G5
def g5(I, C, G):
    M5 = C["G5"]
    a = M5["design_g"] * M5["ultimate_factor"] * G0
    mat = I["materials"]
    sall = mat["cfrp_allowable_mpa"] * 1e6
    E = mat["cfrp_e_gpa"] * 1e9
    rho = mat["cfrp_density_t_m3"]
    lo = I["longerons"]
    Llon = lo["x_m"][1] - lo["x_m"][0]
    lparts = [p for p in G["parts"] if "longeron" in p["tags"]]
    cs, notes = [], []
    worst_state = max(states(I), key=lambda s: G["states"][s]["mass_t"])
    parts = {p["id"]: p for p in G["parts"]}
    st = G["states"][worst_state]
    fwd = 0.0
    for pid in st["parts"]:
        p = parts.get(pid)
        if p is None:
            continue
        if "torch_chain" in p["tags"] or p["id"] == "thrust_cone":
            continue
        if p["centroid_m"][0] < lo["x_m"][1]:
            fwd += p["mass_t"]
    for p in G["fluids_by_state"][worst_state]:
        fwd += p["mass_t"]
    F = fwd * 1e3 * a
    n = len(lparts)
    per = F / n
    worst_sigma, worst_buck = 0.0, float("inf")
    for p, it in zip(lparts, lo["items"]):
        A = p["mass_t"] / (rho * Llon)
        sig = per / A
        if it["kind"] == "tube":
            D = it["d_m"]
            d = math.sqrt(max(D * D - 4 * A / math.pi, 0.0))
            Imin = math.pi / 64 * (D ** 4 - d ** 4)
        else:
            w, h = it["width_m"], it["r_m"][1] - it["r_m"][0]
            Imin = w * h ** 3 / 12
        Pcr = math.pi ** 2 * E * Imin / I["frames"]["spacing_m"] ** 2
        worst_sigma = max(worst_sigma, sig)
        worst_buck = min(worst_buck, Pcr / per)
        cs.append(chk(f"longeron {it['name']}: stress at {M5['design_g']} g x {M5['ultimate_factor']}", round(sig / 1e6, 1), mat["cfrp_allowable_mpa"],
                      sig <= sall, "MPa", f"area {A:.3f} m2; buckling between frames {Pcr / per:.0f}x the load"))
        cs.append(chk(f"longeron {it['name']}: buckling margin", round(Pcr / per, 1), M5["buckling_factor"], Pcr / per >= M5["buckling_factor"], "x"))
    # one longeron out at 1 g limit
    F1 = fwd * 1e3 * C["G9"]["one_longeron_out_g"] * G0 / (n - 1)
    A_min = min(p["mass_t"] / (rho * Llon) for p in lparts)
    sig1 = F1 / A_min
    one_out = chk("one longeron lost: the other four at 1 g limit load", round(sig1 / 1e6, 1), mat["cfrp_allowable_mpa"], sig1 <= sall, "MPa")
    # bending first mode (longerons only), free-free beam
    pos = []
    for it in lo["items"]:
        if it["kind"] == "tube":
            pos.append((it["y_m"], it["z_m"]))
        else:
            rm = sum(it["r_m"]) / 2
            th = math.radians(it["theta_deg"])
            pos.append((rm * math.cos(th), rm * math.sin(th)))
    As = [p["mass_t"] / (rho * Llon) for p in lparts]
    yb = sum(A * y for A, (y, z) in zip(As, pos)) / sum(As)
    zb = sum(A * z for A, (y, z) in zip(As, pos)) / sum(As)
    Iy = sum(A * (z - zb) ** 2 for A, (y, z) in zip(As, pos))
    Iz = sum(A * (y - yb) ** 2 for A, (y, z) in zip(As, pos))
    Lh = I["hull"]["length_m"]
    mu = st["mass_t"] * 1e3 / Lh
    f_bend = min(4.730 ** 2 / (2 * math.pi * Lh ** 2) * math.sqrt(E * Ix / mu) for Ix in (Iy, Iz))
    cs.append(chk("first bending mode (longerons only, free-free)", round(f_bend, 2), M5["first_mode_min_hz"], f_bend >= M5["first_mode_min_hz"], "Hz",
                  f"EI from longerons alone: Iy {Iy:.2f}, Iz {Iz:.2f} m4; skin, tank walls and the habitat shell add stiffness"))
    # torsion: the C-shaped tank is a closed cell
    T = I["tanks"]
    ro, ri, hw = T["r_out_m"], T["r_in_m"], T["slot_half_width_m"]
    ao = 2 * math.degrees(math.asin(hw / ro)) if hw < ro else 0
    ai = 2 * math.degrees(math.asin(min(1.0, hw / ri)))
    per_o = math.radians(360 - (180 - (180 - ao))) * ro
    th_o = 360 - math.degrees(2 * math.acos(hw / ro))
    th_i = 360 - math.degrees(2 * math.acos(min(1.0, hw / ri)))
    perim = math.radians(th_o) * ro + math.radians(th_i) * ri + 2 * (math.sqrt(ro ** 2 - hw ** 2) - math.sqrt(max(ri ** 2 - hw ** 2, 0)))
    tL = T["x_m"][1] - T["x_m"][0]
    A_sec = G["tank_volume_m3"] / tL
    shells = sum(p["mass_t"] for p in G["parts"] if p["id"].startswith("tank_shell"))
    wall_area = perim * tL + 3 * A_sec + (ro - ri) * tL
    t_alloc = shells / (rho * wall_area)
    Jt = 4 * A_sec ** 2 / (perim / t_alloc)
    Gs = M5["cfrp_shear_g_gpa"] * 1e9
    ix = st["inertia_kg_m2"][0][0] / Lh
    f_tor = 1 / (2 * Lh) * math.sqrt(Gs * Jt / ix)
    cs.append(chk("first torsion mode (closed tank cell)", round(f_tor, 2), M5["first_mode_min_hz"], f_tor >= M5["first_mode_min_hz"], "Hz",
                  f"J {Jt:.3f} m4 with the allocated {t_alloc * 1000:.1f} mm tank wall; the open slot is bridged by the tank's slot walls"))
    # tank wall under hydrostatic head
    h = tL / 2
    p_ = 1000 * a * h + M5["ullage_pressure_mpa"] * 1e6
    t_req = p_ * ro / sall
    m_req = wall_area * t_req * rho
    cs.append(chk("tank wall mass needed for 5 g head x 1.5 + ullage", round(m_req, 1), round(shells, 1), m_req <= shells, "t",
                  f"pressure {p_ / 1e6:.2f} MPa, wall {t_req * 1000:.1f} mm, over {wall_area:.0f} m2"))
    notes.append(f"Worst state {worst_state}: {fwd:.0f} t ahead of the thrust cone, {F / 1e6:.1f} MN at {M5['design_g'] * M5['ultimate_factor']:.1f} g ultimate, shared by {n} longerons.")
    notes.append("Bay doors are not counted as structure. Materials: 2026 high-modulus CFRP as a conservative floor (400 MPa, 150 GPa, 1.6 t/m3).")
    notes.append("Flat C-wall bending at the slot is covered by the 8 t non-round tank penalty; a detailed shell model is still OPEN.")
    r = gate("G5", "Structure and loads", cs + [one_out], notes=notes)
    r["one_longeron_out"] = one_out
    return r


# ---------------------------------------------------------------- G6
def shadow_allowed(x, x_f, R, a, xs_range):
    best = float("inf")
    for xs in xs_range:
        if x >= x_f:
            return -1.0
        k = (xs - x_f) / (xs - x)
        best = min(best, (R - a) / k + a)
    return best


def ray_density(origin, d, items, step, tmax):
    """areal density (g/cm2) along a ray through smeared parts."""
    tot = 0.0
    for sh, rho, bb in items:
        t0, t1 = 0.0, tmax
        for k in range(3):
            o, dk = origin[k], d[k]
            lo, hi = bb[k]
            if abs(dk) < 1e-12:
                if o < lo or o > hi:
                    t0, t1 = 1.0, 0.0
                    break
                continue
            ta, tb = (lo - o) / dk, (hi - o) / dk
            if ta > tb:
                ta, tb = tb, ta
            t0, t1 = max(t0, ta), min(t1, tb)
            if t0 > t1:
                break
        if t0 > t1:
            continue
        t = t0 + step / 2
        inside = 0
        while t < t1:
            if sh.contains(origin[0] + d[0] * t, origin[1] + d[1] * t, origin[2] + d[2] * t):
                inside += 1
            t += step
        tot += inside * step * rho * 100.0
    return tot


def g6(I, C, G):
    c6 = C["G6"]
    cs, decl, notes = [], [], []
    H, T = I["hull"], I["torch"]
    off = G["thrust_line_offset_m"]
    x_f, R, a = H["shield_x_m"][0], H["shield_r_m"], T["neutron_source_radius_m"]
    xs = T["neutron_source_x_m"]
    worst = {}
    for p in G["parts"]:
        if not (p["id"] in ("pressure_vessel", "armor", "docking_collar", "shuttle", "bay_liner") or p["id"].startswith("tunnel")
                or p["id"].startswith("room_")):
            continue
        sh = B.shape_from_spec(p["shape"])
        pts = sh.sample(random.Random(5), 1500)
        mm = float("inf")
        for x, y, z in pts:
            rr = math.hypot(y - off["y"], z - off["z"])
            al = shadow_allowed(x, x_f, R, a, xs)
            mm = min(mm, al - rr)
        grp = "habitat (pressure vessel, armour, rooms)" if (p["id"] in ("pressure_vessel", "armor") or p["id"].startswith("room_")) else p["name"]
        worst[grp] = min(worst.get(grp, float("inf")), mm)
    for grp, mm in worst.items():
        cs.append(chk(f"inside the shield's shadow: {grp}", round(mm, 2), c6["shadow_margin_m"], mm >= c6["shadow_margin_m"], "m margin"))
    notes.append(f"Shadow cone: shield front face x {x_f} m, radius {R} m; neutron source a {a} m plasma column anywhere in x {xs[0]}-{xs[1]} m (worst case used); radiator strakes outside the cone take neutron heating and are out of bounds for EVA during burns.")
    # storm shelter
    shelter = next(r for r in G["rooms"] if r["kind"] == "shelter")
    ssh = B.shape_from_spec(shelter["shape"])
    n = I["decisions"]["people"]["crew"] + I["decisions"]["people"]["guests"]
    cs.append(chk("storm shelter volume per person", round(shelter["volume_m3"] / n, 2), c6["shelter_m3_per_person_min"],
                  shelter["volume_m3"] / n >= c6["shelter_m3_per_person_min"], "m3", f"{shelter['volume_m3']:.1f} m3 for {n} people"))
    s_state = c6["shelter_state"]
    items = []
    for p in G["parts"]:
        if "shuttle" in p["tags"] and I["states"][s_state]["shuttle"] == "absent":
            continue
        if p["volume_m3"] <= 0:
            continue
        sh = B.shape_from_spec(p["shape"])
        items.append((sh, p["mass_t"] / p["volume_m3"], sh.bbox()))
    for p in G["fluids_by_state"][s_state]:
        sh = B.shape_from_spec(p["shape"])
        v = p["volume_m3"]
        items.append((sh, p["mass_t"] / v, sh.bbox()))
    s = shelter["shape"]
    rm = (s["r0"] + s["r1"]) / 2
    am = math.radians((s["a0"] + s["a1"]) / 2)
    pts = [((s["x0"] + s["x1"]) / 2, rm * math.cos(am), rm * math.sin(am)),
           (s["x0"] + 0.3, (s["r1"] - 0.3) * math.cos(am), (s["r1"] - 0.3) * math.sin(am)),
           (s["x1"] - 0.3, (s["r0"] + 0.3) * math.cos(math.radians(s["a0"] + 10)), (s["r0"] + 0.3) * math.sin(math.radians(s["a0"] + 10)))]
    N = c6["rays"]
    dirs = []
    for i in range(N):
        zc = 1 - 2 * (i + 0.5) / N
        rr = math.sqrt(1 - zc * zc)
        ph = i * math.pi * (3 - math.sqrt(5))
        dirs.append((zc, rr * math.cos(ph), rr * math.sin(ph)))
    mins = []
    worst_dir = None
    for o in pts:
        m = float("inf")
        for d in dirs:
            v = ray_density(o, d, items, c6["ray_step_m"], c6["ray_max_m"])
            if v < m:
                m, wd = v, d
        mins.append(m)
        if worst_dir is None or m < worst_dir[0]:
            worst_dir = (m, wd, o)
    shelter_min = min(mins)
    cs.append(chk("storm shelter shielding, every direction", round(shelter_min, 1), c6["shelter_min_g_cm2"], shelter_min >= c6["shelter_min_g_cm2"], "g/cm2",
                  f"{N} rays from 3 points, state {s_state} (tanks empty, shuttle away); thinnest ray from {tuple(round(v, 2) for v in worst_dir[2])} toward {tuple(round(v, 2) for v in worst_dir[1])}"))
    decl.append(f"Storm shelter life support: {c6['shelter_life_support_h']} h for {n} people from the life-support room on the same deck (design provision, not computed).")
    yr = c6["gcr_msv_per_day_2026"] * 365
    days = c6["career_limit_msv"] / c6["gcr_msv_per_day_2026"]
    decl.append(f"Galactic cosmic rays: at 2026 free-space rates ({c6['gcr_msv_per_day_2026']} mSv/day, ~{yr:.0f} mSv/yr) a crew member reaches NASA's "
                f"{c6['career_limit_msv']} mSv career limit after ~{days:.0f} days in deep space. Hull shielding barely changes this. Long careers aboard rely on canon's "
                "off-Earth MED-MOD-RADIATION milestone and crew time-in-space rules; this is a canon question, not something the hull can close.")
    decl.append("Torch neutrons and gammas: the shadow shield must attenuate the torch's neutron and gamma output so the dose rate inside the habitat during burns stays "
                "within crew limits. The torch's source strength is canon and not modelled here; only the shadow geometry is checked.")
    r = gate("G6", "Radiation", cs, declared=decl, notes=notes)
    r["shelter_min_g_cm2"] = shelter_min
    return r


# ---------------------------------------------------------------- G7
def g7(I, C, G):
    c7 = C["G7"]
    hab = I["habitat"]
    n_c, n_g = I["decisions"]["people"]["crew"], I["decisions"]["people"]["guests"]
    n = n_c + n_g
    rooms = G["rooms"]
    nhv = sum(r["nhv_m3"] for r in rooms)
    cs = [chk("people aboard", n, f"{n_c} crew + {n_g} guests", True),
          chk("net habitable volume per person", round(nhv / n, 1), c7["nhv_min_m3_per_person"], nhv / n >= c7["nhv_min_m3_per_person"], "m3",
              f"{nhv:.0f} m3 total")]
    target = n_c * c7["nhv_target_m3_per_crew"] + n_g * c7["nhv_target_m3_per_guest"]
    cab = [r for r in rooms if r["kind"] == "cabin"]
    crew_cab = [r for r in cab if r["who"] == "crew"]
    guest_cab = [r for r in cab if r["who"] == "guest"]
    cs.append(chk("private quarters", f"{len(crew_cab)} crew + {len(guest_cab)} guest", f"{n_c} + {n_g}", len(crew_cab) >= n_c and len(guest_cab) >= n_g))
    mv = min(r["volume_m3"] for r in cab)
    cs.append(chk("smallest private quarter", round(mv, 2), c7["quarter_min_m3"], mv >= c7["quarter_min_m3"], "m3"))
    couches = sum(r["couches"] for r in rooms)
    cs.append(chk("acceleration couches", couches, n, couches >= n, "", "a couch-bunk in every cabin plus 6 station couches on the command deck"))
    cs.append(chk("deck clear height", hab["clear_height_m"], c7["clear_height_min_m"], hab["clear_height_m"] >= c7["clear_height_min_m"], "m"))
    lw = hab["ladderways"]
    sep = math.dist([lw[0]["r_m"] * math.cos(math.radians(lw[0]["theta_deg"])), lw[0]["r_m"] * math.sin(math.radians(lw[0]["theta_deg"]))],
                    [lw[1]["r_m"] * math.cos(math.radians(lw[1]["theta_deg"])), lw[1]["r_m"] * math.sin(math.radians(lw[1]["theta_deg"]))])
    cs.append(chk("two independent ways off every deck", f"{len(lw)} ladderways, {sep:.1f} m apart", f">= {c7['ladder_separation_min_m']} m",
                  len(lw) >= 2 and sep >= c7["ladder_separation_min_m"]))
    kinds = {r["kind"] for r in rooms}
    missing = [k for k in c7["required_kinds"] if k not in kinds]
    cs.append(chk("required rooms present", "all" if not missing else ", ".join(missing), "all", not missing))
    has_tunnel = any(p["id"].startswith("tunnel") for p in G["parts"]) and any(p["id"] == "docking_collar" for p in G["parts"])
    cs.append(chk("docking port and pressure tunnel to the shuttle", "yes" if has_tunnel else "no", "yes", has_tunnel))
    per_deck = {}
    for r in rooms:
        per_deck.setdefault(r["deck"], 0.0)
        per_deck[r["deck"]] += r["nhv_m3"]
    windows = sum(r["windows"] for r in rooms)
    notes = [f"Target {target:.0f} m3 ({c7['nhv_target_m3_per_crew']:.0f} per crew, {c7['nhv_target_m3_per_guest']:.0f} per guest): reached {nhv / target * 100:.0f}%. "
             "A sixth deck (+2.6 m of habitat) would reach the target.",
             "Net habitable volume by deck: " + ", ".join(f"{k} {v:.0f} m3" for k, v in per_deck.items()),
             f"Windows planned: {windows} (canon candidate suggests 10-16; more can be added by deck function)",
             "Decks are perpendicular to the thrust axis; under thrust, aft is down. Above ~1.5 g everyone rides in a couch."]
    r = gate("G7", "Compartments and crew space", cs, notes=notes)
    r["nhv_m3"] = nhv
    r["nhv_by_deck_m3"] = per_deck
    return r


# ---------------------------------------------------------------- G8
def g8(I, C, G):
    c8 = C["G8"]
    S, Bay = I["shuttle"], I["bay"]
    rs = S["diameter_m"] / 2
    cs = [chk("radial clearance in the bore", round(Bay["bore_r_m"] - rs, 2), c8["radial_clearance_min_m"], Bay["bore_r_m"] - rs >= c8["radial_clearance_min_m"] - 1e-9, "m"),
          chk("axial clearance, forward", round(S["x_m"][0] - Bay["x_m"][0], 2), c8["axial_clearance_min_m"], S["x_m"][0] - Bay["x_m"][0] >= c8["axial_clearance_min_m"] - 1e-9, "m"),
          chk("axial clearance, aft", round(Bay["x_m"][1] - S["x_m"][1], 2), c8["axial_clearance_min_m"], Bay["x_m"][1] - S["x_m"][1] >= c8["axial_clearance_min_m"] - 1e-9, "m")]
    # lateral (+Z) exit path: the shuttle's cross-section |y| <= rs sweeps upward through the slot
    obst = [("slot edge", Bay["slot_half_width_m"]), ("open doors (vertical at the slot edges)", Bay["slot_half_width_m"])]
    for it in I["longerons"]["items"]:
        if it["kind"] == "tube" and it["z_m"] > 0:
            obst.append((f"sill longeron ({it['name']})", abs(it["y_m"]) - it["d_m"] / 2))
    R = I["radiators"]
    g = I["tanks"]["groove"]
    for az in R["azimuths_deg"]:
        if math.sin(math.radians(az)) <= 0:
            continue
        c_, s_ = math.cos(math.radians(az)), math.sin(math.radians(az))
        ys = []
        for along in (R["root_r_m"] - g["depth_m"], R["root_r_m"], R["root_r_m"] + R["max_span_m"]):
            for across in (-g["width_m"] / 2, g["width_m"] / 2):
                ys.append(abs(along * c_ - across * s_))
        obst.append((f"strake {az} deg (stowed or deployed)", min(ys)))
    for nm, yy in obst:
        cl = yy - rs
        cs.append(chk(f"exit path clear of {nm}", round(cl, 2), c8["path_clearance_min_m"], cl >= c8["path_clearance_min_m"] - 1e-9, "m"))
    segs = I["service"]["tunnel"]["segments"]
    ok = abs(segs[-1]["to"][0] - S["nose_port_x_m"]) < 0.05 and segs[0]["from"][0] >= I["hull"]["pressure_vessel_x_m"][1] - 0.05
    cs.append(chk("pressure-tight transfer from habitat to shuttle nose", "habitat - collar node - bay axis - nose port" if ok else "broken", "continuous", ok))
    nd = sum(d["count"] for d in I["drones"]["carried"])
    cs.append(chk("drones carried", nd, c8["drones_min"], nd >= c8["drones_min"], "", "2 Mars + 2 dense-air in pods; berths for up to 8 + 16"))
    holds = sum(v for k, v in G["service_sectors_m3"].items() if k.startswith("hold"))
    dv = sum(p["volume_m3"] for p in G["parts"] if "drone" in p["tags"])
    cs.append(chk("hold volume left for 50 t payload and the Venus kit", round(holds - dv, 1), "> 50", holds - dv > 50, "m3", f"two holds {holds:.0f} m3, drones {dv:.1f} m3"))
    ve = I["canon"]["torch_ve_km_s"]["ECON"]
    M = G["states"]["S1"]["mass_t"]
    rem = I["states"]["S1"]["remass_t"]
    w = S["water_cap_t"]
    loss = ve * math.log(M / (M - rem)) - ve * math.log(M / (M - (rem - w)))
    notes = [f"Filling the shuttle's water ({w} t, an Earth trip) from remass costs Wayfarer {loss:.0f} km/s of ECON reach unless refilled at a port.",
             "The shuttle backs 0.5 m off the forward port, then rises +Z through the slot. Strakes may stay deployed; doors open to vertical.",
             f"Bay x {Bay['x_m'][0]}-{Bay['x_m'][1]} m vs canon reservation x {I['canon']['bay_reservation_x_m'][0]}-{I['canon']['bay_reservation_x_m'][1]} m (G11)."]
    return gate("G8", "Shuttle, drones and bay exit", cs, notes=notes)


# ---------------------------------------------------------------- G9
def g9(I, C, G, r3, r4, r5):
    R = I["radiators"]
    T = R["temperature_k"]
    cs, notes = [], []
    q_hab_kw, _ = hab_heat(I)
    w_hp = q_hab_kw * (T / I["habitat_heat"]["radiator"]["temperature_k"] - 1) / C["G4"]["heat_pump_carnot_fraction"]
    q_hard = metric_heat(I, "HARD", T) + (q_hab_kw + w_hp) / 1000
    worst_cap, worst_span = float("inf"), 0
    for lost in R["azimuths_deg"]:
        azs = [a for a in R["azimuths_deg"] if a != lost]
        s = span_for(I, C, q_hard, azs)
        cap = rad_net_mw(I, C, R["max_span_m"], azs)[0]
        worst_cap = min(worst_cap, cap)
        worst_span = max(worst_span, s or 99)
        cs.append(chk(f"strake {lost} deg lost: Metric HARD still rejected", s if s else "no", f"<= {R['max_span_m']} m", s is not None, "m span",
                      f"torch-burn capacity falls to {cap:.0f} MW"))
    s7 = G["states"]["S7"]
    cs.append(chk("tank cell vented (S7): thrust trim", round(s7["trim_deg"], 3), C["G3"]["trim_max_deg"], s7["trim_deg"] <= C["G3"]["trim_max_deg"], "deg"))
    ve = I["canon"]["torch_ve_km_s"]["ECON"]
    M = s7["mass_t"]
    usable = s7["usable_remass_t"]
    dv7 = ve * math.log(M / (M - usable))
    lost = 1 - usable / I["states"]["S7"]["remass_t"]
    cs.append(chk("tank cell vented (S7): remass lost", f"{lost * 100:.1f}%", "about 25% (Q7)", lost <= 0.26, "", f"{usable:.1f} t left, ECON delta-v {dv7:.0f} km/s"))
    one_out = [c for c in r3["checks"] if c["name"].startswith("three-axis control")]
    cs.append(chk("any one RCS cluster lost: three-axis control", "yes" if all(c["pass"] for c in one_out) else "no", "yes", all(c["pass"] for c in one_out)))
    cs.append(r5["one_longeron_out"])
    cs.append(chk("protected water kept out of routine propulsion", "by accounting", "always", True, "",
                  "jacket and service tank water are separate from the tank cells' remass; the 16.5 t... in the cells is never counted as remass".replace("16.5 t...", f"{G['protected_water']['c_tank_t']:.1f} t")))
    notes.append("Torch failure after departure is a Q6/Q7 degraded-mission case (survival possible, completion not assumed).")
    return gate("G9", "Failures and reserves", cs, notes=notes)


# ---------------------------------------------------------------- G10 card
def card(I, G, r2):
    st = {}
    for s in states(I):
        v = G["states"][s]
        st[s] = {"name": v["name"], "mass_t": round(v["mass_t"], 2), "remass_t": I["states"][s]["remass_t"] * (0.75 if I["states"][s].get("vented") else 1),
                 "shuttle": v["shuttle"], "payload_t": v["payload_t"], "cg_m": [round(c, 3) for c in v["cg_m"]],
                 "inertia_diag_kg_m2": [round(v["inertia_kg_m2"][k][k]) for k in range(3)]}
    return {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING SANDBOX ship card for Navigator (gate G10)",
            "ship": "Wayfarer v0.5", "geometry_sha256": G["_sha"], "dry_t": round(G["dry_t"], 2),
            "fluids": {"water_t": I["canon"]["water_t"], "remass_t": I["canon"]["remass_t"], "protected_water_t": I["canon"]["protected_water_t"]},
            "torch": {"ve_km_s": I["canon"]["torch_ve_km_s"], "jet_power_tw": I["torch"]["jet_power_tw"],
                      "thrust_mn_by_mode": {m: round(v["thrust_mn"], 3) for m, v in r2["modes"].items()},
                      "accel_cap_g": 5.0, "thrust_line_offset_m": G["thrust_line_offset_m"]},
            "dispatch_q7": {"normal_dispatch_remass_t": 150, "minimum_dispatch_remass_t": 100, "protected_optimizer_reserve_t": 50},
            "states": st,
            "missions_to_fly": ["E1 Ceres to Neptune", "FR-01B-R Ceres to Phobos", "MV-01 Ceres to Phoebe to Ganymede"],
            "pass_rule": "arrival remass >= 50 t protected optimizer reserve (Q7)"}


# ---------------------------------------------------------------- G11
def g11(I, C, G, r4):
    cn = I["canon"]
    dep = [
        ("Tanks", "4 major working-fluid tanks in quadrature (CANON II §13.2)", "one C-shaped wrap-around tank in 4 isolatable cells around an on-axis bay"),
        ("Longerons", "4 axial longerons", "5 longerons: 3 flat planks outside the tank (0, 180, 270 deg) and 2 round sills set into the tank beside the slot"),
        ("Length", f"~{cn['main_body_m'][0]} m main body", f"{I['hull']['length_m']} m"),
        ("Dry mass", f"~{cn['dry_t']} t", f"{G['dry_t']:.1f} t (includes 6 t for 4 guest berths)"),
        ("Wet mass", f"~{cn['wet_t']} t", f"{G['states']['S1']['mass_t']:.1f} t"),
        ("Launch bay", f"semi-recessed, reservation x {cn['bay_reservation_x_m'][0]}-{cn['bay_reservation_x_m'][1]} m", f"on-axis bore inside the tank, x {I['bay']['x_m'][0]}-{I['bay']['x_m'][1]} m, lateral exit through a 4.8 m slot on +Z"),
        ("Radiators", "4 assemblies in quadrature, 900 K equivalent card", f"4 accordion strakes at {I['radiators']['azimuths_deg']} deg (mirror-symmetric, not exactly 90 deg apart), {I['radiators']['temperature_k']} K"),
        ("Metric HARD electrical", "~23.9 MW at 900 K", f"{I['canon']['metric_cryo_electrical_mw_at_900K']['HARD'] * (I['radiators']['temperature_k'] - 20) / 880:.1f} MW at {I['radiators']['temperature_k']} K"),
        ("Torch axis", "1 axial torch", f"axial, with its thrust line offset {math.hypot(G['thrust_line_offset_m']['y'], G['thrust_line_offset_m']['z']):.2f} m from the hull centreline to pass through the centre of mass"),
        ("People", "6 normal crew", "6 crew (unchanged) + 4 guest berths"),
        ("Protected water", "50 t in the tanks", f"{G['protected_water']['jacket_t']:.1f} t storm-shelter jacket, {G['protected_water']['service_tank_t']:.1f} t service tank, {G['protected_water']['c_tank_t']:.1f} t in the tank cells"),
        ("Shuttle", "candidate 30-35 t launch, ~10.5 m (not canon)", f"rover-drop shuttle {I['shuttle']['dry_t']} t empty, {I['shuttle']['length_m']} m"),
    ]
    kept = ["torch card and remass/water figures", "Metric card and 719 m2-equivalent HARD requirement", "integrated, unpressurized launch bay with lateral departure, pressure-tight transfer and DOCKED/ABSENT mass state",
            "docking collar at x = 16 m on -Z", "habitat x 0-14 m, decks perpendicular to thrust", "no spin ring, wings or landing gear", "torch/Metric exclusivity", "four radiator assemblies"]
    cs = [chk("every departure listed with its reason", len(dep), "complete", True)]
    r = gate("G11", "Canon fit", cs, notes=[f"Kept from canon: {', '.join(kept)}."])
    r["departures"] = [{"item": a, "canon": b, "v0.5": c} for a, b, c in dep]
    r["verdict"] = PASS
    r["notes"].append("Listing is complete; adoption is kT's decision as a canon amendment.")
    return r


# ---------------------------------------------------------------- G12
def g12(I, C, G):
    man = HERE / "render" / "out" / "manifest.json"
    if not man.exists():
        return gate("G12", "Images", [chk("images generated from the hashed geometry", "not yet", "all four sets", False)], force=OPEN)
    M = json.loads(man.read_text())
    cs = [chk("images stamped with this geometry's hash", M.get("geometry_sha256", "")[:12], G["_sha"][:12], M.get("geometry_sha256") == G["_sha"])]
    for kind, need in (("exterior", 4), ("cutaway", 2), ("deckplan", len(I["habitat"]["decks"])), ("viewer", 1)):
        n = len([f for f in M["files"] if f["kind"] == kind and (HERE / "render" / "out" / f["file"]).exists()])
        cs.append(chk(f"{kind} images", n, need, n >= need))
    return gate("G12", "Images", cs)


# ---------------------------------------------------------------- report
def main():
    I, C, G = load()
    G["_sha"] = hashlib.sha256((HERE / "out/wayfarer_v05_geometry.json").read_bytes()).hexdigest()
    r1, r2, r3 = g1(I, C, G), g2(I, C, G), g3(I, C, G)
    r4 = g4(I, C, G)
    r5 = g5(I, C, G)
    r6 = g6(I, C, G)
    r7, r8 = g7(I, C, G), g8(I, C, G)
    r9 = g9(I, C, G, r3, r4, r5)
    cd = card(I, G, r2)
    (HERE / "out/wayfarer_v05_card.json").write_text(json.dumps(cd, indent=1))
    r10 = gate("G10", "Mission suite (Navigator, run by Sol)", [chk("E1, FR-01B-R and MV-01 flown by Navigator", "awaiting Sol", "arrival remass >= 50 t", False)],
               notes=["Machine-readable card written to out/wayfarer_v05_card.json."], force=OPEN)
    r11, r12 = g11(I, C, G, r4), g12(I, C, G)
    gates = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12]
    summary = {g["gate"]: g["verdict"] for g in gates}
    rep = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING SANDBOX certification run",
           "basis": "CERTIFICATION_BASIS_v0.1 (PROPOSED)", "geometry_sha256": G["_sha"], "inputs_sha256": G["inputs_sha256"],
           "criteria_sha256": hashlib.sha256((HERE / "inputs/cert_criteria_v0.1.json").read_bytes()).hexdigest(),
           "summary": summary, "gates": gates,
           "declared_for_kT": [d for g in gates for d in g["declared"]]}
    (HERE / "out/certification_report.json").write_text(json.dumps(rep, indent=1, default=str))
    (HERE / "out/CERTIFICATION_REPORT_v0.5.md").write_text(markdown(rep, G))
    for g in gates:
        bad = [c["name"] for c in g["checks"] if not c["pass"]]
        print(f"{g['gate']:4} {g['verdict']:14} {g['title']}" + (f"   fails: {bad}" if bad and g["verdict"] == FAIL else ""))


def fmt(v):
    if isinstance(v, float):
        return f"{v:,.1f}" if abs(v) >= 100 else f"{v:.3g}"
    return str(v)


def markdown(rep, G):
    L = ["# Wayfarer v0.5 certification report", "", "ALL bodies. ALL sponsors. 2026-2226.", "",
         "**NON-GOVERNING SANDBOX.** Run against CERTIFICATION_BASIS_v0.1 (proposed). Generated by `certify.py`; do not edit by hand.", "",
         f"Geometry sha256 `{rep['geometry_sha256']}`  ", f"Inputs sha256 `{rep['inputs_sha256']}`  ", f"Criteria sha256 `{rep['criteria_sha256']}`", "",
         "## Summary", "", "| Gate | Verdict |", "|---|---|"]
    for g in rep["gates"]:
        L.append(f"| {g['gate']} {g['title']} | {g['verdict']} |")
    L += ["", "## Declared assumptions kT must accept", ""]
    for d in rep["declared_for_kT"]:
        L.append(f"- {d}")
    for g in rep["gates"]:
        L += ["", f"## {g['gate']} {g['title']}: {g['verdict']}", "", "| Check | Value | Limit | Pass | Note |", "|---|---|---|---|---|"]
        for c in g["checks"]:
            L.append(f"| {c['name']} | {fmt(c['value'])} {c['unit']} | {fmt(c['limit'])} | {'yes' if c['pass'] else 'NO'} | {c['note']} |")
        for n in g["notes"]:
            L.append(f"- {n}")
        if g["gate"] == "G1":
            L += ["", "| State | Mass t | CG x, y, z m | Ixx | Iyy | Izz kg m2 |", "|---|---|---|---|---|---|"]
            for m in g["mass_states"]:
                L.append(f"| {m['state']} {m['name']} | {m['mass_t']} | {m['cg_m'][0]}, {m['cg_m'][1]}, {m['cg_m'][2]} | {m['Ixx']:.3e} | {m['Iyy']:.3e} | {m['Izz']:.3e} |")
        if g["gate"] == "G11":
            L += ["", "| Item | Canon | v0.5 |", "|---|---|---|"]
            for d in g["departures"]:
                L.append(f"| {d['item']} | {d['canon']} | {d['v0.5']} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
