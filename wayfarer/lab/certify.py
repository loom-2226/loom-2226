"""Wayfarer v0.5 certification checks -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Runs gates G1-G12 of CERTIFICATION_BASIS.md (v0.2) against
out/wayfarer_v05_geometry.json, inputs/wayfarer_v05_inputs.json and
inputs/cert_criteria.json. Writes out/certification_report.json,
out/CERTIFICATION_REPORT_v0.5.md and out/wayfarer_v05_card.json (the
machine-readable ship card for Navigator, gate G10).
Python 3 standard library only. Usage: python certify.py"""
import hashlib, json, math, random, sys
from pathlib import Path
import build_v05 as B

HERE = Path(__file__).resolve().parent
G0, SIGMA = 9.80665, 5.670374419e-8
PASS, DECL, FAIL, OPEN = "PASS", "PASS-DECLARED", "FAIL", "OPEN"


def torch_budget():
    """Step S4 of the torch heat model in torch/ (standard library only)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("torch_heat_budget", HERE / "torch/torch_heat_budget.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    st = m.I["steps"][-1]
    r = m.step(st)
    r["burn_to_face_m"] = st["burn_to_face_m"]
    return r


_CREW = {}


def crew_results():
    """habitat/crew_systems.py (v0.5.6 crew systems), run once per certify call (standard library only)."""
    if "r" not in _CREW:
        import importlib.util
        spec = importlib.util.spec_from_file_location("crew_systems", HERE / "habitat/crew_systems.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _CREW["r"] = m.run()
        (HERE / "habitat/crew_systems_results.json").write_text(json.dumps(_CREW["r"], indent=1))
        I_, C_, G_ = m.load()
        (HERE.parent / "render/out/hab_scene.json").write_text(json.dumps(m.hab_scene(I_, G_), indent=1))
    return _CREW["r"]


def load():
    I = json.loads((HERE.parent / "config/wayfarer_v05_inputs.json").read_text())
    C = json.loads((HERE.parent / "config/cert_criteria.json").read_text())
    G = json.loads((HERE.parent / "results/out/wayfarer_v05_geometry.json").read_text())
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
              + I["shuttle"]["dry_t"] + L["drones_pods_t"] + L.get("torch_hot_fins_t", 0.0) + L.get("crew_systems_v056_t", 0.0) + L.get("crew_systems_v057_t", 0.0)
              + L.get("rcs_axial_t", 0.0) + L.get("reserve_draws_rev7", {}).get("total_t", 0.0)
              + L.get("i4_carryover_t", 0.0) + L.get("aoi_crown_t",0.0) + L.get("aoi_aft_bulkhead_reinforcement_t",0.0)
               + L.get("crown_option_c_additions_t",0.0) + L.get("l3_berth_shield_liner_t",0.0))
    AOI = I["habitat"]["decks"][0].get("command_layout",{}).get("crown_dome",{}).get("adaptive_optogel")
    dry = G["dry_t"]
    cs = [chk("parts sum to the ledger", round(dry, 2), round(expect, 2), abs(dry - expect) <= C["G1"]["ledger_tolerance_t"], "t")]
    if AOI:
        two = {p["id"]:p["mass_t"] for p in G["parts"] if p["id"] in ("crown_backup_pressure_dome","crown_adaptive_optogel")}
        cs.append(chk("AOI filled interspace has explicit 3.000t physical mass",
                      round(two.get("crown_adaptive_optogel",0),6),AOI["mass_t"],
                      abs(two.get("crown_adaptive_optogel",0)-AOI["mass_t"])<1e-8,"t"))
        cs.append(chk("independent backup pressure dome separately charged to reserve",
                      round(two.get("crown_backup_pressure_dome",0),6),AOI["backup_pressure_dome_mass_t"],
                      abs(two.get("crown_backup_pressure_dome",0)-AOI["backup_pressure_dome_mass_t"])<1e-8,"t"))
        cs.append(chk("AOI and backup dome entirely drawn from positive existing reserve",
                      round(L["engineering_reserve_t"],3),0.,L["engineering_reserve_t"]>=0.,"t",
                      "adds no dry mass outside original ship engineering ledger"))
    OC=I["habitat"]["decks"][0]["command_layout"]["crown_dome"].get("shell_option_c")
    if OC:
        m=OC["mass_ledger"];byid={x["id"]:x["mass_t"] for x in G["parts"]}
        for name,pid,expect in [("added 50-degree gore area","crown_c_additional_strata_gore",m["gore_extra_t"]),
          ("independent outward retainers","crown_c_outward_retainers",m["retain_t"]),
          ("one centre and six annular spare panes","crown_c_seven_spare_panes",m["spares_t"])]:
            cs.append(chk("Option C actual physical "+name,round(byid.get(pid,0),6),expect,
                          abs(byid.get(pid,0)-expect)<1e-7,"t"))
        hs=sum(byid.get("hatch_L1L2_"+str(j),0) for j in range(2))
        cs.append(chk("two L1/L2 real pressure hatch masses each 0.15t",round(hs,6),.3,abs(hs-.3)<1e-7,"t"))
        # Option C was charged through three ledger buckets. All 5.834795t
        # must reconcile, including 0.540125t panes booked to I4 and 0.6t liner.
        prior_reserve=17.786216  # frozen immediately prior to Option C, PR #439 / 25bae1ce
        expected_draw=m["reserve_draw_total_t"]
        actual_draw=prior_reserve-L["engineering_reserve_t"]
        pane_delta=I["i4_carryover"]["crown_increment_from_reserve_t"]-.347738-m.get("dome_primary_delta_t",0.0)
        cs.append(chk("Option C explicit reserve draw reconciles (including dome change)",
            round(actual_draw,6),round(expected_draw,6),
            abs(actual_draw-expected_draw)<1e-6,"t",
            "4.694670t Option-C hardware +0.540125t pane area + dome deepening + physical L3 liner (if justified)"))
        cs.append(chk("Option C pane incremental mass booked under existing I4 carryover",
            round(pane_delta,6),round(m["pane_delta_t"],6),
            abs(pane_delta-m["pane_delta_t"])<1e-6,"t"))
        cs.append(chk("Option C subledger equals physical reserve draws",
            round(m["gore_extra_t"]+m["retain_t"]+m["spares_t"]+m["hatches_t"]+m["pane_delta_t"]+m.get("dome_deepening_t",0.0)+L["l3_berth_shield_liner_t"],6),
            round(actual_draw,6),
            abs(m["gore_extra_t"]+m["retain_t"]+m["spares_t"]+m["hatches_t"]+m["pane_delta_t"]+m.get("dome_deepening_t",0.0)+L["l3_berth_shield_liner_t"]-actual_draw)<1e-6,"t"))
        cs.append(chk("Option C engineering growth floor preserved",round(L["engineering_reserve_t"],6),5.0,L["engineering_reserve_t"]>=5.0,"t"))
        li=next((x["mass_t"] for x in G["parts"] if x["id"]=="l3_berth_dry_shield_liner"),0.)
        cs.append(chk("Option C physically charged L3 liner agrees with active zero-or-positive reserve allocation",
                      round(li,6),L.get("l3_berth_shield_liner_t",0),
                      abs(li-L.get("l3_berth_shield_liner_t",0))<1e-7,"t"))
        cs.append(chk("Option C gross 27g/cm2 coverage accounts extra faceted area",
           round(OC["gores"]["gross_full_coverage_t"],6),
           round(OC["gores"]["existing_projected_coverage_t"]+m["gore_extra_t"],6),
           abs(OC["gores"]["gross_full_coverage_t"]-OC["gores"]["existing_projected_coverage_t"]-m["gore_extra_t"])<1e-6,"t"))
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
                  "four cells, net of walls, grooves and the longeron tubes that pass through the tank"))
    notes = [f"dry {dry:.1f} t vs canon {I['canon']['dry_t']} t ({dry - I['canon']['dry_t']:+.1f} t); "
             f"S1 wet {G['states']['S1']['mass_t']:.1f} t vs canon {I['canon']['wet_t']} t",
             "dry by system: " + ", ".join(f"{k} {v:.1f}" for k, v in sorted(G["dry_by_system_t"].items(), key=lambda kv: -kv[1])),
             f"protected water: {G['protected_water'].get('shelter_jacket_t', G['protected_water']['jacket_t']):.1f} t in the storm-shelter jacket, "
             f"{G['protected_water'].get('berth_shield_t', 0):.2f} t in the L3 berth shield ring, {G['protected_water']['service_tank_t']:.1f} t in the "
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
    P = T["jet_power_ceiling_tw"] * 1e12
    modes = {}
    capped, heat_held = [], []
    for m, v in ve.items():
        md = T["mode_cards"]["modes"][m]
        assert md["ve_km_s"] == v, f"working card ve differs from canon in {m}"
        Fc = md["mdot_kg_s"] * v * 1e3                 # working card (main src/wayfarer_torch_mode_cards.py)
        F = min(Fc, 2 * P / (v * 1e3))                  # held to the heat-rejection ceiling
        if F < Fc - 1:
            heat_held.append(f"{m} {Fc / 1e6:.2f} -> {F / 1e6:.2f} MN")
        row = {"thrust_mn": F / 1e6, "card_thrust_mn": Fc / 1e6, "card_jet_power_tw": 0.5 * Fc * v * 1e3 / 1e12, "dv_full_remass_S1_km_s": v * math.log(M1 / (M1 - rem)), "accel_g": {}}
        for s in states(I):
            M = G["states"][s]["mass_t"] * 1e3
            a = F / (M * G0)
            row["accel_g"][s] = round(min(a, C["G2"]["torch_g_limit_doctrine"]), 3)
            if a > C["G2"]["torch_g_limit_doctrine"]:
                capped.append(f"{m} in {s} ({a:.1f} g at full jet power)")
        modes[m] = row
    notes = [f"S2 (50 t payload): ECON delta-v {ve['ECON'] * math.log(G['states']['S2']['mass_t'] / (G['states']['S2']['mass_t'] - rem)):.1f} km/s",
             "Thrust from the working card (main src/wayfarer_torch_mode_cards.py, kT 2026-10-26): F = mdot ve, held to the 11.361 TW jet-power ceiling the heat rejection is sized for: " + ("; ".join(heat_held) or "none") + ".",
             "Throttled to the 5 g structural limit (doctrine): " + (", ".join(capped) if capped else "none"),
             "Crew doctrine (v0.5.6): sustained thrust capped at 4 g with people aboard (NASA OCHMO: +Gx 4 g tolerable up to at least 60 min); 5 g stays the structural rating, for emergencies. The cap changes burn times, not delta-v."]
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
        if c.get("axial"):   # rev 6: axial thruster, canted outward (force has a small inward component)
            ca = math.radians(c["axial"]["cant_out_deg"])
            d = (c["axial"]["sign"] * math.cos(ca), -math.sin(ca) * rad[1], -math.sin(ca) * rad[2])
            out.append({"cluster": c["id"], "kind": "axial", "pos": pos, "f": tuple(F * v for v in d)})
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
    q_hab_base_kw = q_hab_kw
    hh = I["habitat_heat"]["radiator"]
    aoi = I["habitat"]["decks"][0].get("command_layout",{}).get("crown_dome",{}).get("adaptive_optogel")
    glazing = None
    if aoi:
        r = I["habitat"]["decks"][0]["command_layout"]["crown_dome"]["i4_crown_option_B"]["inner_diameter_m"]/2
        area = math.pi * r*r
        # Zero benefit claimed from unmeasured electrochromic/NIR switching.
        # Worst-case all incident light entering the aperture becomes heat.
        solar_kw = hh["worst_sun_w_m2"] * area / 1000.
        inner_area = I["habitat"]["decks"][0]["command_layout"]["crown_dome"]["panes"]["inner_area_m2"]
        longwave_kw = SIGMA * hh["temperature_k"]**4 * inner_area / 1000.
        glazing={"open_projected_area_m2":area,"worst_case_solar_kw":solar_kw,
                 "uncredited_blackbody_longwave_kw":longwave_kw,
                 "ir_control_benefit_credited_kw":0.,
                 "gores_closed_solar_direct_kw":0.,
                 "absorbed_solar_heat_path":"habitat strakes while open; outer-skin re-radiation not claimed",
                 "emissivity_opaque_gore_note":"normal full shielding when gores closed; no optogel impact/thermal proof"}
        q_hab_kw += solar_kw

    tc = hh["temperature_k"]
    w_hp = q_hab_kw * (T / tc - 1) / C["G4"]["heat_pump_carnot_fraction"]
    q_hab_main = (q_hab_kw + w_hp) / 1000.0
    if glazing:
        cs.append(chk("AOI open crown worst-case sunlight explicitly enters G4 heat balance",
           round(glazing["worst_case_solar_kw"],3),round(hh["worst_sun_w_m2"]*glazing["open_projected_area_m2"]/1000,3),
           glazing["worst_case_solar_kw"]>0., "kW",
           "no optical IR credit; the solar load is passed to the habitat heat pump and strakes"))
        cs.append(chk("AOI IR/glare switching does not invent cooling or a pressure seal",
           glazing["ir_control_benefit_credited_kw"],0.,glazing["ir_control_benefit_credited_kw"]==0.,
           "kW",f"blackbody longwave outward envelope {glazing['uncredited_blackbody_longwave_kw']:.2f}kW not relied upon for cold-running cooling"))
        decl.append(("aoi_optical_ir",
            "kT declares AOI-2226 refractive-index matching and independently switchable clear/glare/dark plus visible/NIR modulation. NOT demonstrated at full scale. Zero numeric optical/IR cooling performance credited; worst Venus solar aperture heat explicitly included. Transparent dome and AOI thermal expansion/differential heat flux remain OPEN."))
    spans = {}
    for m in ("NORMAL", "FAST", "EXPEDITE", "HARD"):
        q = metric_heat(I, m, T) + q_hab_main * (1 + C["G4"]["hab_heat_margin"])
        s = span_for(I, C, q, azs)
        spans[m] = s
        cs.append(chk(f"Metric {m} heat + habitat rejected", s if s else "no", f"<= {R['max_span_m']} m span", s is not None, "m span",
                      f"{metric_heat(I, m, T):.1f} MW Metric + {q_hab_main:.2f} MW habitat via heat pump (x1.25); field geometry radius {R['root_r_m'] + (s or 0):.1f} m"))
    # torch burns (v0.5.2 torch heat package, kT 2026-10-25): heat model in torch/, hot fins aft, strakes carry coil cryo only
    tb = torch_budget()
    HF = I["hot_fins"]
    fspan = HF["pleat_m"] * HF["pleats"]
    fchord = HF["x_m"][1] - HF["x_m"][0]
    ffs, ffh = view_factor(HF["azimuths_deg"], fspan, HF["root_r_m"], C["G4"]["view_factor_rays"])
    fcap = 2 * len(HF["azimuths_deg"]) * fchord * fspan * HF["emissivity"] * SIGMA * HF["temperature_k"] ** 4 * ffs / 1e9
    cs.append(chk(f"torch burn: heat on hot structure rejected by the hot fins at {HF['temperature_k']} K", round(fcap, 3), round(tb["ship_heat_gw"], 3),
                  fcap >= tb["ship_heat_gw"], "GW",
                  f"{len(HF['azimuths_deg'])} fins {fspan:.0f} m x {fchord:.0f} m on the strake lines, view factor to space {ffs:.2f} (torch chain taken as a {HF['root_r_m']} m cylinder, conservative); "
                  f"heat = light {tb['parts_gw']['light']:.2f} + neutrons {tb['parts_gw']['neutrons']:.2f} + plume contact {tb['parts_gw']['plume contact']:.2f} GW"))
    q_burn = tb["cryo_reject_mw"] + q_hab_main * (1 + C["G4"]["hab_heat_margin"])
    s_burn = span_for(I, C, q_burn, azs)
    cs.append(chk("torch burn: magnet-coil cryo heat + habitat rejected by the strakes", s_burn if s_burn else "no", f"<= {R['torch_span_m']} m span",
                  s_burn is not None and s_burn <= R["torch_span_m"] + 1e-9, "m span",
                  f"{tb['coil_heat_mw']:.2f} MW of neutron heating in the coils -> {tb['cryo_reject_mw']:.0f} MW at {T} K, + {q_hab_main:.2f} MW habitat (x1.25)"))
    fl = C["G4"]["torch_wall_flux_max_mw_m2"]
    cs.append(chk("torch burn: light on the reactor's aft face", round(tb["wall_flux_mw_m2"], 2), fl, tb["wall_flux_mw_m2"] <= fl + 1e-9, "MW/m2",
                  f"burn {tb['burn_to_face_m']:.0f} m aft of the face; ITER divertor class"))
    lim_ppm = fl * 1e6 * 4 * math.pi * tb["burn_to_face_m"] ** 2 / (tb["fusion_tw"] * 1e12) * 1e6
    decl.append(("torch_heat", f"Torch heat package (kT, 2026-10-25): each pellet is wrapped in a shell of remass that soaks up the burn and leaves as exhaust. The shell must let no more than "
                f"~{lim_ppm:.0f} ppm of the burn's energy escape as light, counting its own glow (the reactor face's {fl:.0f} MW/m2 limit); the design value is {tb['light_ppm_of_fusion']:.0f} ppm. "
                f"With the model's other assumptions (torch/torch_heat_inputs.json: light 40% of fusion energy; He3-rich, spin-polarised fuel with 0.76% neutrons, 85% absorbed by the shell; "
                f"plume contact 1e-4 of charged energy; coil shield transmission 1e-3), {tb['ship_heat_gw']:.2f} GW reaches hot structure and {tb['coil_heat_mw']:.2f} MW the magnet coils at "
                f"{tb['fusion_tw']:.1f} TW of fusion. These are assumptions, not results. Replaces v0.5.1's 387 MW (34 ppm) torch-leak gap."))
    decl.append(("torch_fin_temperature", f"Hot fins run for life at {HF['temperature_k']} K. Lithium heat pipes have run in lab tests to ~1,500 K and briefly ~1,800 K; years at "
                f"{HF['temperature_k']} K with burn cycling and neutron exposure is an engineering extrapolation (a technology milestone), not new physics. Fallback: 1,500 K fins, ~49 m span, ~30 t, still inside the reserve."))
    cap, hull_hit = rad_net_mw(I, C, R["torch_span_m"], azs)
    fullcap = rad_net_mw(I, C, R["max_span_m"], azs)[0]
    e_hard = I["canon"]["metric_cryo_electrical_mw_at_900K"]["HARD"] * (T - 20) / 880
    decl.append(("plant_power", f"Plant electrical: Metric HARD at a {T} K reject temperature needs {e_hard:.1f} MW of cryo-chain electrical power, against canon's "
                f"23.9 MW at 900 K. The relational plant must supply this (canon amendment), or the cryo chain must reject through a 900 K loop."))
    # passive habitat skin radiators as backup
    sun = hh["worst_sun_w_m2"] * hh["absorptivity"] / math.pi
    net = hh["emissivity"] * SIGMA * tc ** 4 - sun
    area = 2 * math.pi * I["hull"]["outer_r_m"] * (I["hull"]["habitat_shell_x_m"][1] - I["hull"]["bow_cap_depth_m"]) * 0.8
    backup = net * area / 1000
    # Passive-backup is viable only with the Strata crown gores CLOSED:
    # 100 kW open-aperture sunlight would overwhelm the 57 kW skin radiator.
    emergency_hab_kw = q_hab_base_kw if glazing else q_hab_kw
    cs.append(chk("habitat passive skin backup with crown GORES CLOSED (heat pump failed)",
                  round(backup, 1), round(emergency_hab_kw, 1), backup >= emergency_hab_kw, "kW",
                  f"{area:.0f} m2 of skin at {tc} K. AOI optical control receives zero thermal credit; with open gores +{glazing['worst_case_solar_kw']:.1f} kW at worst sun, passive backup is NOT sufficient" if glazing else f"{area:.0f} m2 of habitat skin at {tc} K, Venus-orbit sun"))
    if glazing:
        decl.append(("aoi_gore_thermal_doctrine", "At worst-case sunlight, the open crown adds ~100 kW of solar heating to habitat. In heat-pump-failed or cold-running passive backup the 16 Strata gores MUST CLOSE; clear/glare/dark AOI states may not be credited as heat rejection or solar exclusion. Solar absorption/IR-band partition and AOI switching performance are not physically qualified."))
    cs.append(chk("major torch burn and high Metric never required together", "doctrine", "CANON II §14", True))
    CR, SK = I.get("cold_running"), I.get("skin")
    if CR and SK:   # rev 7 (Sol qualification 2): cold running holds heat in; it does not remove it
        md = SK["flanks"]["modes"]
        hr = I["habitat_heat"]["radiator"]
        a_sk = 2 * math.pi * I["hull"]["outer_r_m"] * (hr["x_m"][1] - hr["x_m"][0]) * hr["share_of_skin"]
        leak = md["cold_running"]["emissivity"] * SIGMA * hr["temperature_k"] ** 4 * a_sk / 1000
        q_in = (q_hab_kw - (glazing["worst_case_solar_kw"] if glazing else 0.)) * (1 + C["G4"]["hab_heat_margin"])
        e_buf = I["canon"]["protected_water_t"] * 1000 * CR["water_cp_kj_kg_k"] * CR["buffer_dT_k"]
        ideal_hrs = e_buf / max(q_in - leak, 1e-9) / 3600
        p_standby = CR.get("plant_standby_kw",0.0)
        cryo_standby = CR.get("cryo_standby_kw",0.0)
        hrs = e_buf / max(q_in + p_standby + cryo_standby - leak, 1e-9) / 3600
        ratio = md["cold_running"]["emissivity"] / md["normal"]["emissivity"]
        decl.append(("cold_running", f"Cold running (rev 7, F5 provisional item F5-TE-01): the tunable flanks drop from emissivity {md['normal']['emissivity']} to "
                     f"{md['cold_running']['emissivity']}, so at the same skin temperature they radiate {ratio * 100:.0f}% as much. Heat is held, not removed: habitat heat "
                     f"{q_in:.1f} kW (x1.25), plus plant standby {p_standby:.1f} kW and cryo standby {cryo_standby:.1f} kW, less {leak:.1f} kW still leaking through {a_sk:.0f} m2 of low-e skin at {hr['temperature_k']} K warms the "
                     f"{I['canon']['protected_water_t']:.0f} t of protected water by {CR['buffer_dT_k']:.0f} K in about {hrs:.1f} h (ideal no-standby ceiling {ideal_hrs:.1f} h). {CR.get('standby_prov','')}. Then the ship must open the strakes "
                     f"or switch the flanks back to normal. {CR['not_modelled']}. The metallic look in the viewer is a proposed optical property."))
        r_cold = {"hours": hrs, "ideal_no_standby_hours": ideal_hrs, "leak_kw": leak, "habitat_kw": q_in, "plant_standby_kw":p_standby, "cryo_standby_kw":cryo_standby, "in_kw":q_in+p_standby+cryo_standby,"area_m2": a_sk,"provenance":CR.get("standby_prov")}
    else:
        r_cold = None
    notes.append(f"Habitat heat {q_hab_kw:.1f} kW for {n} people; heat pump to {T} K needs {w_hp:.0f} kW (Carnot fraction {C['G4']['heat_pump_carnot_fraction']}).")
    notes.append(f"Torch burns: strakes open to {R['torch_span_m']} m ({cap:.0f} MW); full 24 m span ({fullcap:.0f} MW) is no longer needed for the torch. At {R['torch_span_m']} m they shine {hull_hit:.2f} MW onto the hull coating.")
    notes.append(f"Torch heat model (torch/, non-governing): same 11.36 TW jet from {tb['fusion_tw']:.1f} TW of fusion, pulsed at about 1-10 Hz (0.3-3 kt per pulse). Light escape the face can take: ~{lim_ppm:.0f} ppm; model {tb['light_ppm_of_fusion']:.0f} ppm. Hot-fin capacity is computed here with certify's own 2D view factor; torch/fin_layout.py (numpy, 3.0 m body) gives a slightly higher figure.")
    r = gate("G4", "Power and heat", cs, declared=decl, notes=notes)
    r["spans_m"] = spans
    if glazing:
        r["aoi_glazing_heat_kw"] = glazing
    r["cold_running"] = r_cold
    r["torch_strake_capacity_mw"] = cap
    r["hot_fin_capacity_gw"] = fcap
    r["torch_budget"] = tb
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
    cs, notes, decl = [], [], []
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
    SSl = I["ledger"]["structure_split"]
    real_area = "released_to_reserve" in SSl     # rev 5: area from the structure line's material, not part mass (which carries the spread reserve)
    for p, it in zip(lparts, lo["items"]):
        A = SSl["longerons"] / 1.10 / (rho * Llon) / n if real_area else p["mass_t"] / (rho * Llon)
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
    if real_area:   # rev 5 (structure review A): axial plus bending from the thrust line's offset and a 0.5 deg thrust error
        items_f = [parts[pid] for pid in st["parts"] if pid in parts and "torch_chain" not in parts[pid]["tags"] and pid != "thrust_cone" and parts[pid]["centroid_m"][0] < lo["x_m"][1]]
        items_f += G["fluids_by_state"][worst_state]
        cgf = [sum(q["mass_t"] * q["centroid_m"][k] for q in items_f) / fwd for k in range(3)]
        off = G["thrust_line_offset_m"]
        Mb = F * math.hypot(cgf[1] - off["y"], cgf[2] - off["z"]) + F * math.sin(math.radians(0.5)) * (lo["x_m"][1] - cgf[0])
        Ar = SSl["longerons"] / 1.10 / (rho * Llon) / n
        zz = [it["z_m"] for it in lo["items"]]
        sb = Mb * max(abs(z) for z in zz) / sum(Ar * z * z for z in zz)
        s_comb = per / Ar + sb
        cs.append(chk("longerons: axial + bending at 5 g x 1.5 (thrust-line offset and 0.5 deg thrust error), real material area", round(s_comb / 1e6, 1), 250.0, s_comb <= 250e6, "MPa",
                      f"{Mb / 1e6:.1f} MN m; area {Ar:.4f} m2 from the structure line (part mass includes the spread reserve); limit = the 250 MPa design stress (400 MPa floor x 0.62)"))
    # one longeron out at 1 g limit
    F1 = fwd * 1e3 * C["G9"]["one_longeron_out_g"] * G0 / (n - 1)
    A_min = (SSl["longerons"] / 1.10 / (rho * Llon) / n) if real_area else min(p["mass_t"] / (rho * Llon) for p in lparts)
    sig1 = F1 / A_min
    one_out = chk("one longeron lost: the others at 1 g limit load", round(sig1 / 1e6, 1), mat["cfrp_allowable_mpa"], sig1 <= sall, "MPa")
    # bending first mode (longerons only), free-free beam
    pos = []
    for it in lo["items"]:
        if it["kind"] == "tube":
            pos.append((it["y_m"], it["z_m"]))
        else:
            rm = sum(it["r_m"]) / 2
            th = math.radians(it["theta_deg"])
            pos.append((rm * math.cos(th), rm * math.sin(th)))
    As = [(SSl["longerons"] / 1.10 / (rho * Llon) / n) if real_area else p["mass_t"] / (rho * Llon) for p in lparts]
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
    # tank internal structure (tie-webs, baffles, slot walls, bulkheads) sized by build_v05.tank_structure
    TSd = G["tank_structure"]
    cs.append(chk("tank structure mass needed at 5 g x 1.5 + ullage", round(TSd["mass_needed_t"], 1), round(shells, 1), TSd["mass_needed_t"] <= shells, "t",
                  f"ultimate pressure {TSd['ultimate_pressure_mpa']:.2f} MPa; allocated = tank shell share of structure + 8 t non-round penalty"))
    cs.append(chk("tank walls: axial stress carrying the water's inertia", round(TSd["axial_wall_stress_mpa"], 1), mat["cfrp_allowable_mpa"],
                  TSd["axial_wall_stress_mpa"] <= mat["cfrp_allowable_mpa"], "MPa"))
    cs.append(chk("tank wall panels: buckling margin in axial compression", round(TSd["panel_buckling_mpa"] / TSd["axial_wall_stress_mpa"], 1), M5["buckling_factor"],
                  TSd["panel_buckling_mpa"] / TSd["axial_wall_stress_mpa"] >= M5["buckling_factor"], "x"))
    for rr in TSd["panels"]:
        notes.append(f"Tank {rr['item']}: {rr['t_mm']:.1f} mm, {rr['mass_t']:.2f} t, displaces {rr['displaced_m3']:.2f} m3 ({rr['note']})" if rr["note"]
                     else f"Tank {rr['item']}: {rr['t_mm']:.1f} mm, {rr['mass_t']:.2f} t, displaces {rr['displaced_m3']:.2f} m3")
    CR = crew_results()
    fc = CR["flight_deck_columns"]
    cs.append(chk("flight-deck columns: stress at 5 g x 1.5 plus a 0.5 g side load", fc["side_load_combined_mpa"], fc["yield_mpa"], fc["ok_stress"], "MPa",
                  f"{fc['columns']} aluminium tubes carry {fc['carried_t']} t; axial {fc['axial_kn']} kN each ({fc['stress_mpa']} MPa)"))
    cs.append(chk("flight-deck columns: buckling margin", fc["buckling_margin"], C["G5"]["buckling_factor"], fc["ok_buckling"], "x",
                  f"Euler, pinned ends (conservative), {fc['length_m']} m"))
    if I["habitat"]["decks"][0].get("command_layout",{}).get("i4_lock"):
        cs.append(chk("I4 terrace columns: nominal assembly mass inside reserved allowance",
                      round(fc["required_column_mass_t"],5),round(fc["allowed_mass_t"],5),fc["mass_ok"],"t",
                      "Member mass only; structural mounts/footprints still HOLD"))
        decl.append(("i4_terrace_mounts",
                     "I4 terrace 4 columns sized as 7075-T6 76mm OD x 3mm at 0.49m. "
                     "5g x1.5 ultimate +0.5g lateral member screen, no joint, deck bearing, vibration, fatigue, "
                     "swept-body or 3D egress qualification. HOLLOW: closed only for column members, not system."))
    OC=I["habitat"]["decks"][0]["command_layout"]["crown_dome"].get("shell_option_c")
    if OC:
        cs.append(chk("Option C gross overall ship envelope 54.5m",OC["overall_ship_length_m"],54.5,
                      abs(OC["overall_ship_length_m"]-54.5)<.001,"m"))
        decl.append(("crown_option_c_load_paths","Full faceted nose 1.2m ahead of old bow and gore hinges at 50deg break; actual retaining loads, impact, thermal cycling, 5g attachment paths and shutter transition mechanics UNSHOWN."))
        decl.append(("l1_l2_pressure_hatches","Two 0.15t pressure hatches normally OPEN aft of L1/L2 ladder plane x=3m; L2-to-L1 (-x) pressure outflow passively pushes each leaf toward an L2-side seat, differential pressure reinforces closure. No sensor/power/actuation needed; seal proof, hinge moments, reverse-flow isolation and 4g crew passage NOT demonstrated."))
    stn = CR["stations"]
    cs.append(chk("upper berth posts: buckling margin at 5 g x 1.5", stn["berth_post_margin"], C["G5"]["buckling_factor"], stn["ok"], "x",
                  f"{stn['berth_post_kn']} kN per post; couch and berth hard points {stn['hard_point_kn']} kN each ({stn['requirement']})"))
    for f in CR["floors"]:
        cs.append(chk(f"floor {f['deck']}: carries its deck at 5 g x 1.5", f["needed_t"], f["floor_t"], f["ok"], "t needed vs allotted",
                      f"{f['carried_t']} t on the floor ({f['pressure_kpa']} kPa); CFRP faces {f['face_mm']} mm; core shear {f['core_shear_mpa']} MPa"))
    bk = CR["l4_l5_bulkhead"]
    cs.append(chk("floor L4 as a pressure bulkhead (L5 at vacuum), factor 2.0", bk["needed_t"], bk["floor_t"], bk["ok"], "t needed vs allotted",
                  f"CFRP faces {bk['face_mm']} mm; core shear {bk['core_shear_mpa']} MPa (allowable {bk['core_shear_allow_mpa']}); {bk['hatches']} ladderway hatches and a trunk plug"))
    vb = CR.get("viewport_band")
    if vb:
        cs.append(chk("L2 viewport band: Osteon mullions carry the axial load across the band", vb["mullion_stress_mpa"], vb["allow_mpa"],
                      vb["mullion_stress_mpa"] <= vb["allow_mpa"] and vb["mullion_buckling_margin"] >= C["G5"]["buckling_factor"], "MPa",
                      f"{vb['mullions']} titanium mullions {vb['mullion_section_m'][0] * 100:.0f} x {vb['mullion_section_m'][1] * 100:.0f} cm; worst of 5 g x 1.5 on {vb['mass_ahead_t']} t ahead "
                      f"({vb['axial_load_thrust_mn']} MN) and 2 x the pressure end load ({vb['axial_load_pressure_mn']} MN); buckling margin {vb['mullion_buckling_margin']}"))
        lp = vb.get("load_path")
        if lp:   # rev 4: habitat/viewport_band_study.py
            r3, s4, j5, p2 = lp["3_rings"], lp["4_shell_at_ring"], lp["5_mullion_root_joint"], lp["2_panes_check"]
            cs.append(chk("L2 band edge rings: hoop across the band + beam between mullions", r3["with_lounge_hoop_mpa"], r3["allow_mpa"], r3["ok"], "MPa",
                          f"Ti {r3['ring_section_cm'][0]:.0f} x {r3['ring_section_cm'][1]:.0f} cm sill and head rings, full circle; {r3['ring_moment_knm']} kN m between mullions"))
            cs.append(chk("L2 band: pressure shell next to the rings (discontinuity bending + axial)", s4["axial_plus_bending_mpa"], s4["allow_mpa"], s4["ok"], "MPa",
                          f"rigid-ring bound; dies out within {s4['decay_length_m']} m"))
            cs.append(chk("L2 band: mullion root joints", j5["margin"], 1.5, j5["ok"], "x", f"{j5['load_kn']} kN each; 4 x M16 Ti bolts in double shear"))
            th = lp.get("6_thermal")
            if th:
                cs.append(chk("L2 band rings: Ti/CFRP thermal mismatch taken by flexure fingers (fatigue)", th["finger_bending_mpa"], th["fatigue_allow_mpa"], th["ok"], "MPa",
                              f"{th['radial_mismatch_mm']} mm radial over {th['dT_K']} K; fingers {th['finger']}; plus {th['finger_axial_mpa']} MPa static from the shear flow (allow 600)"))
            cs.append(chk("L2 band panes as plates (2226 ceramic), lounge with its transom", p2["lounge_need_mm"], p2["lounge_spec_mm"], p2["ok"], "mm needed vs specified",
                          f"general band {p2['general_need_mm']} mm needed, {p2['general_spec_mm']} specified; the glass is not trusted to pass hoop tension through its edges"))
    notes.append("Crew stations and floors (v0.5.6): closed-form strip and column checks in habitat/crew_systems.py; floors are 0.3 m sandwich panels spanning trunk to hull.")
    notes.append(f"Worst state {worst_state}: {fwd:.0f} t ahead of the thrust cone, {F / 1e6:.1f} MN at {M5['design_g'] * M5['ultimate_factor']:.1f} g ultimate, shared by {n} longerons.")
    notes.append("Bay doors are not counted as structure. Materials: 2026 high-modulus CFRP as a conservative floor (400 MPa, 150 GPa, 1.6 t/m3).")
    notes.append("Method: closed-form plate theory (Navier series for simply supported panels, which is conservative against clamped edges) plus closed-cell equilibrium with tie-webs. A finite-element shell model is the next level of fidelity; the basis does not require it.")
    r = gate("G5", "Structure and loads", cs + [one_out], declared=decl, notes=notes)
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


def committed_shield_fraction(I, G):
    """Fraction of each spread dry part actually committed to hardware, not growth reserve.
    The mass/CG inventory still carries the growth allowance; radiation never gets its credit.
    """
    spread=[p for p in G["parts"] if p["dry"] and "from_reserve" not in p["tags"]]
    gross=sum(p["mass_t"] for p in spread)
    uncommitted=I["ledger"]["engineering_reserve_t"]+I["ledger"]["structure_split"].get("released_to_reserve",0.0)
    assert 0 < uncommitted < gross
    return (gross-uncommitted)/gross


def committed_shield_mass(p, spread_fraction):
    # Gel function is optical, not qualified for shielding; do not invent mass attenuation.
    if p["id"] == "crown_adaptive_optogel":
        return 0.0
    return p["mass_t"]*spread_fraction if p["dry"] and "from_reserve" not in p["tags"] else p["mass_t"]


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


class _OpenBores:
    """rev 7 sensitivity: the armour with every node face on the habitat as an open bore (worst case only)."""

    def __init__(self, sh, faces, depth):
        self.sh, self.faces, self.depth = sh, faces, depth

    def bbox(self):
        return self.sh.bbox()

    def contains(self, x, y, z):
        if not self.sh.contains(x, y, z):
            return False
        for f in self.faces:
            if abs(x - f["pos"][0]) > 0.6:
                continue
            d = (x - f["pos"][0], y - f["pos"][1], z - f["pos"][2])
            n = f["normal"]
            a = d[0] * n[0] + d[1] * n[1] + d[2] * n[2]
            if -self.depth - 0.02 <= a <= 0.02:
                q = (d[0] - a * n[0], d[1] - a * n[1], d[2] - a * n[2])
                if q[0] ** 2 + q[1] ** 2 + q[2] ** 2 < (f["d_m"] / 2) ** 2:
                    return False
        return True


def _open_bores(sh, faces, depth):
    return _OpenBores(sh, faces, depth)


def _is_armor(sh):
    return isinstance(sh, B.DomeCyl) and abs(sh.xc - 14.0) < 1e-6 and abs(sh.R - 4.5) < 1e-6 and abs(sh.t - 0.2) < 1e-6 and sh.xa == 0.0


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
    notes.append(f"Shadow cone: shield front face x {x_f} m, radius {R} m; neutron source: the pellet burn, {a} m across, anywhere in x {xs[0]}-{xs[1]} m (worst case used). "
                 "Radiator strakes and the hot fins sit outside the cone (the fins edge-on to the burn), take neutron heating and are out of bounds for EVA during burns.")
    # storm shelter
    shelter = next(r for r in G["rooms"] if r["kind"] == "shelter")
    ssh = B.shape_from_spec(shelter["shape"])
    n = I["decisions"]["people"]["crew"] + I["decisions"]["people"]["guests"]
    cs.append(chk("storm shelter volume per person", round(shelter["volume_m3"] / n, 2), c6["shelter_m3_per_person_min"],
                  shelter["volume_m3"] / n >= c6["shelter_m3_per_person_min"], "m3", f"{shelter['volume_m3']:.1f} m3 for {n} people"))
    s_state = c6["shelter_state"]
    items = []
    spread_fraction = committed_shield_fraction(I,G)
    for p in G["parts"] + G["fluids_by_state"][s_state]:
        if "shuttle" in p["tags"] and I["states"][s_state]["shuttle"] == "absent":
            continue
        if p["volume_m3"] <= 0:
            continue
        m=committed_shield_mass(p,spread_fraction)
        if m <= 0: continue
        sh=B.shape_from_spec(p["shape"])
        items.append((sh, m/p["volume_m3"], sh.bbox()))
    notes.append(f"Shielding credits committed material only; uncommitted distributed growth allowance is zero radiation mass, AOI gel zero radiation credit (fraction {spread_fraction:.6f} on spread dry parts).")
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
    BV = I["habitat"].get("crew_systems", {}).get("berth_viewports")
    if BV:
        nb = len([f for f in G["features"] if f.get("berth")])
        decl.append(("berth_viewports", f"Berth viewports (v0.5.7): {nb} x {BV['d_m']} m viewports keep the berth screen because acrylic plugs carry at least the g/cm2 they replace "
                     f"(armour {BV['plug']['g_cm2']} vs 27.0, ring {BV['insert']['g_cm2']} vs 8.0), so the ray screen, which treats the hull as continuous, is unchanged. "
                     "Rev 3: the same plug kit is in every opening below the crown, including the L2 viewport band, and continues through the storm-shelter jacket (17 cm more acrylic for the 20 cm of water). Not yet shown: the dose. Acrylic is ~8% hydrogen by mass against water's 11%, so per g/cm2 it may stop cosmic-ray secondaries slightly less well; a transport check may ask for a thicker plug. Encapsulated for fire."))
    CD = I["habitat"]["decks"][0].get("command_layout", {}).get("crown_dome", {})
    if CD.get("adopted") and CD.get("i4_crown_option_B"):
        B2=CD["i4_crown_option_B"]
        pressure=B2["inner_areal_g_cm2"]
        outer=B2["outer_areal_g_cm2"]
        aoi=CD.get("adaptive_optogel")
        backup=(B2.get("backup_dome_areal_g_cm2",0.) if aoi else 0.)
        protected=pressure+backup+outer+B2["closed_gore_g_cm2"]
        prior=B2["replaced_pressure_hull_comparator_g_cm2"]+B2["replaced_armor_g_cm2"]
        cs.append(chk("I4 monolithic inner pressure dome exceeds replaced shell areal mass",
            round(pressure,3),B2["replaced_pressure_hull_comparator_g_cm2"],pressure>=B2["replaced_pressure_hull_comparator_g_cm2"],"g/cm2",
            "material areal equivalent, NOT pressure-buckling or high-energy radiation proof"))
        if aoi:
            cs.append(chk("AOI backup pressure shell individually meets old shell areal mass",
                round(backup,3),B2["replaced_pressure_hull_comparator_g_cm2"],
                backup>=B2["replaced_pressure_hull_comparator_g_cm2"],"g/cm2",
                "thickness proxy only, not independent differential/impulse/failure survival"))
            cs.append(chk("AOI 3.023 m3 interlayer mass logged, no impact credit",
                aoi["volume_m3"],3.023,abs(aoi["volume_m3"]-3.023)<1e-7,"m3",
                "near-water-density gel, optically switchable; no shock-fracture reduction credited"))
            cs.append(chk("AOI cannot be counted as a structural pressure boundary",
                aoi["pressure_boundary"],False,not aoi["pressure_boundary"] and not aoi["pressure_seal"],
                note="both 7m shells independently pressure capable; actual failure independence remains untested"))
        cs.append(chk("I4 closed Strata gores plus dome pair and outer ceramic restore old areal mass",
            round(protected,3),prior,protected>=prior,"g/cm2",
            "27 g/cm2 Rev7 gores, separate from 37 outer panes; shelter transport not re-qualified by simple areal sum"))
        OC=CD.get("shell_option_c")
        if OC:
            shell=OC["outer_tile_layer"]
            cs.append(chk("Option C nose flat to 2m, then 50-degree slope",
                   [OC["flat_to_r_m"],OC["slope_deg"]],[2.,50.],
                   OC["flat_to_r_m"]==2 and OC["slope_deg"]==50))
            cs.append(chk("Option C 1 cm ceramic outer areal mass 3.75 g/cm2",
                   shell["areal_mass_kg_m2"],37.5,
                   abs(shell["areal_mass_kg_m2"]-37.5)<.001,"kg/m2"))
            cs.append(chk("Option C gross closed gore coverage 27g/cm2 over entire faceted surface",
                round(OC["gores"]["gross_full_coverage_t"],4),
                round(OC["outer_area_m2"]*.27,4),
                abs(OC["gores"]["gross_full_coverage_t"]-OC["outer_area_m2"]*.27)<1e-5,"t"))
            decl.append(("crown_option_c_gore_fairing",
               "16 Strata tambour gores cover the full r<=3.5m faceted external 50deg profile at 27g/cm2 when closed; 2m flat/slope hinge transition and shoulder fairing have no measured shock/seam/drive failure qualification."))
            if I["ledger"].get("l3_berth_shield_liner_t",0):
                decl.append(("l3_shield_liner_material",
                   "Observed G6 two rays at 39.86g/cm2 corrected by reserve-funded 0.6t continuous L3 dry foamed high-hydrogen liner (x5.9-8.2,r4.18-4.25). No water moved and no gel radiation credited. g/cm2 mass/geometry screen only: polymer composition, actual charged-particle transport, structural attachment, fire and dose remain UNSHOWN."))
            decl.append(("crown_option_c_tiles",
                "37 independent ceramic 1cm sacrificial tiles, outward-removable retainers while L1 pressure stays sealed. Four types, seven spares in hold. Cupola precedent establishes separable outer debris panes, NOT service tool loads or 2226 particle impact protection."))
        cs.append(chk("I4 source 37-pane radial boundaries preserved exactly",
            CD["panes"]["ring_boundaries_m"],[0,.75,2.,2.75,3.5],
            CD["panes"]["ring_boundaries_m"]==[0,.75,2.,2.75,3.5]))
        cs.append(chk("I4 outermost ring stagger pi/12 preserved",
            round(CD["panes"].get("outermost_band_stagger_rad",0),6),round(math.pi/12,6),
            abs(CD["panes"].get("outermost_band_stagger_rad",0)-math.pi/12)<1e-8))
        cs.append(chk("I4 outer protection 37 separate panes [1,12,12,12]",
            B2["outer_count"],37,B2["outer_count"]==37))
        cs.append(chk("I4 segmented pane outer chord max 1.9m",
            round(CD["panes"]["maximum_outer_circumferential_edge_m"],3),1.9,
            CD["panes"]["maximum_outer_circumferential_edge_m"]<=1.9,"m",
            "maximum hoop chord, not longest corner-to-corner diagonal"))
        decl.append(("crown_dome","Rev7 16 closing Strata gores and opening doctrine are retained; their original acceptance applied only to the earlier segmented 2.3m pressure panes, not the new 7m seamless dome."))
        DP=CD.get("shell_option_c",{}).get("deep_pressure_domes",{})
        decl.append(("crown_monolith_7m",
            f"kT adopted deeper pair: TWO independent full-pressure ~7m transparent ceramic domes, each 28mm nominal, primary apex X={DP.get('primary_apex_x_m',.2):.2f}m, backup X={DP.get('backup_apex_x_m',.08):.2f}m, at unchanged rim. Meridional shape {CD['panes']['inner_shape']}. Ideal apex thin-shell stress {DP.get('stress_after_apex_ideal_mpa',0):.2f}MPa vs {DP.get('stress_before_mpa',0):.2f}MPa prior; not real pressure test. Both must survive loss of the other; 37 outer nonpressure panes +16 closure gores unchanged. Monolith production, boundary loads, fracture/gel pulse and optics UNSHOWN."))
        if aoi:
            decl.append(("aoi_failure_independence",
                "AOI-2226 ~3.023m3 (~3t) gel between two separately sealed pressure domes, gap min normal 5.973cm with backup axial offset ~12cm. Neither pressure-bearing nor a pressure seal. Each independent dome MUST withstand full 101.3kPa after other's failure while optogel is present, WITHOUT shock, fracture, crack bridging or fast pressure-pulse coupling. The research has NO measured high-rate response or independent-shell survival test; do not credit impact damping. Rim slip/contact interfaces and >=56L illustrative thermal-expansion compliance still require engineering."))
    elif CD.get("adopted"):
        decl.append(("crown_dome", f"Crown dome (v0.5.7): {CD['glazed_area_m2']:.0f} m2 of glazing inside r {CD['r_m']} m replaces the 8 nose windows. Assumes (1) proof-tested transparent ceramic panes up to "
                     f"{CD['central_pane_m']} m across (2026's largest are ~0.76 m), a 2226 materials milestone like the 1,750 K fins (rev 4: the L2 viewport band's 16-18 mm plate panes rely on the same ceramic; 2026 ALON would need 25-29 mm); (2) tambour gores of armour-equivalent Strata laminate (Builder-derived, MHL-22) that restore "
                     f"{CD['gores']['closed_restores_g_cm2']} g/cm2 when closed and stow in the brow ring; (3) the operating rule: {CD['doctrine']} With the gores open, L1 loses the armour over the crown (glass 2-9 g/cm2); L1 is not a shelter."))
    SK, NF = I.get("skin"), G.get("node_faces")
    if SK:
        decl.append(("strata_armour", f"Habitat armour face (rev 7, kT 2026-10-26): {SK['armour_face']['material']}. {SK['armour_face']['status']}. Bow x {SK['bow']['x_m'][0]}-{SK['bow']['x_m'][1]} m: {SK['bow']['finish']}."))
    if NF:
        hp = HERE / "habitat/hab_overlay_results.json"
        ho = json.loads(hp.read_text()) if hp.exists() else {}
        fresh = ho.get("geometry_sha256") == G["_sha"]
        dz = ho.get("radiation", {}).get("minimum_g_cm2") if fresh else None
        ob = ho.get("radiation_node_faces_open", {}) if fresh else {}
        faces = [f for f in G["features"] if f["kind"] == "node_face" and f["pos"][0] <= H["habitat_shell_x_m"][1]]
        items_ob = [(_open_bores(sh, faces, H["outer_r_m"] - H["pressure_r_m"]) if _is_armor(sh) else sh, rho, bb) for sh, rho, bb in items]
        sh_open = min(min(ray_density(o, d, items_ob, c6["ray_step_m"], c6["ray_max_m"]) for d in dirs) for o in pts)
        fl = ", ".join(f"{v} {k.replace('_', ' ')}" for k, v in sorted(NF["flags"].items()))
        cs.append(chk("berth screen with node faces armour-equivalent (design case)", dz if dz is not None else "not run", c6["shelter_min_g_cm2"],
                      dz is not None and dz >= c6["shelter_min_g_cm2"], "g/cm2", "habitat/hab_overlay_checks.py, 600 directions, 2 cm steps, state S5, includes the rev 7 equipment"))
        decl.append(("node_faces", f"Metric node faces (rev 7, kT 2026-10-26; Sol: AGREE, placement HOLD): {NF['count']} visible flush or recessed faces, 13 rings x 16 at 22.5 deg "
                     f"(rev 5 longeron-study layout). {NF['clear']} are clear; the rest are flagged: {fl}. The design case assumes every face carries at least the armour's "
                     f"g/cm2 it replaces, like the berth-viewport plugs. Sensitivity, faces as open bores through the armour: berth screen "
                     f"{ob.get('minimum_g_cm2', 'not run')} g/cm2 ({ob.get('below_40', '?')} of {ob.get('points', '?')} berth points below 40) and storm shelter {sh_open:.1f} g/cm2. "
                     "So a face must be armour-equivalent: materials, cover, seal and mount stay OPEN, and no dust check exists in the basis yet "
                     "(faces flagged 'faces dust flow' meet the flow when coasting bow-first). Node stations are not moved for the look; PR #184 stays OPEN."))
    decl.append(("shelter_life_support", f"Storm shelter life support: {c6['shelter_life_support_h']} h for {n} people from the life-support room on the same deck (design provision, not computed)."))
    yr = c6["gcr_msv_per_day_2026"] * 365
    days = c6["career_limit_msv"] / c6["gcr_msv_per_day_2026"]
    decl.append(("gcr", f"Galactic cosmic rays: at 2026 free-space rates ({c6['gcr_msv_per_day_2026']} mSv/day, ~{yr:.0f} mSv/yr) a crew member reaches NASA's "
                f"{c6['career_limit_msv']} mSv career limit after ~{days:.0f} days in deep space. Hull shielding barely changes this. Long careers aboard rely on canon's "
                "off-Earth MED-MOD-RADIATION milestone and crew time-in-space rules; this is a canon question, not something the hull can close."))
    decl.append(("torch_neutrons", "Torch neutrons and gammas: the shadow shield must attenuate the torch's neutron and gamma output so the dose rate inside the habitat during burns stays "
                "within crew limits. The v0.5.2 heat model puts neutrons at ~0.76% of the burn's energy with 85% absorbed by the remass shell; the dose itself is not computed here, only the shadow geometry is checked."))
    r = gate("G6", "Radiation", cs, declared=decl, notes=notes)
    r["shelter_min_g_cm2"] = shelter_min
    return r


# ---------------------------------------------------------------- G7
def g7(I, C, G):
    c7 = C["G7"]
    hab = I["habitat"]
    n_c, n_g = I["decisions"]["people"]["crew"], I["decisions"]["people"]["guests"]
    n = n_c + n_g
    decl = []
    OC=I["habitat"]["decks"][0]["command_layout"]["crown_dome"].get("shell_option_c")
    if OC:
        limit=OC["visible_open_policy"]
        decl.append(("crown_option_c_open_limit", "Crown uses Whipple-like stand-off, not physically impact-qualified: 37 removable 10mm ceramic bumper tiles, vacuum gap that varies approximately 0.39–1.16m axially to backup shell on the adopted deeper dome, then two independent full-pressure ceramic domes. No hypervelocity shielding strength claimed; AOI shielding credit zero. Crown-open speed and bow/flow-angle controls remain visibly UNQUALIFIED. Governing doctrine still low speed OR bow away from dust flow; closed for torch, radiation and Metric. Actual safe numeric thresholds and sensor/failure logic OPEN."))
    rooms = G["rooms"]
    nhv = sum(r["nhv_m3"] for r in rooms)
    cs = [chk("people aboard", n, f"{n_c} crew + {n_g} guests", True),
          chk("net habitable volume per person", round(nhv / n, 1), c7["nhv_min_m3_per_person"], nhv / n >= c7["nhv_min_m3_per_person"], "m3",
              f"{nhv:.0f} m3 total")]
    target = n_c * c7["nhv_target_m3_per_crew"] + n_g * c7["nhv_target_m3_per_guest"]
    cab = [r for r in rooms if r["kind"] == "cabin"]
    crew_cab = [r for r in cab if r["who"] == "crew"]
    guest_cab = [r for r in cab if r["who"] == "guest"]
    if c7.get("quarters_rule") == "berth_per_person":
        cb = sum(r.get("occupancy", 1) for r in crew_cab)
        gb = sum(r.get("occupancy", 1) for r in guest_cab)
        cs.append(chk("a cabin berth for every person (kT 2026-10-25: shared cabins)", f"{cb} crew + {gb} guest", f"{n_c} + {n_g}", cb >= n_c and gb >= n_g, "",
                      f"{len(cab)} cabins; berths 2.10 x 0.70 m on 5 g hard points (G5)"))
    else:
        cs.append(chk("private quarters", f"{len(crew_cab)} crew + {len(guest_cab)} guest", f"{n_c} + {n_g}", len(crew_cab) >= n_c and len(guest_cab) >= n_g))
    occ = [r for r in cab if r.get("occupancy")]
    g7_occ_note = None
    if occ:
        g7_occ_note = ("Cabins by occupancy (v0.5.3, Sol's candidate): " + ", ".join(f"{r['name']} {r['occupancy']} ({r['volume_m3'] / r['occupancy']:.1f} m3 each)" for r in occ)
                       + f"; {sum(r['occupancy'] for r in occ)} berths in {len(occ)} cabins. Private cabins removed by kT on 2026-10-25 (basis change, Sol to agree).")
    if c7.get("quarters_rule") == "berth_per_person":
        mv = min(r["volume_m3"] / r.get("occupancy", 1) for r in cab)
        cs.append(chk("smallest cabin volume per occupant", round(mv, 2), c7["quarter_min_m3"], mv >= c7["quarter_min_m3"], "m3"))
    else:
        mv = min(r["volume_m3"] for r in cab)
        cs.append(chk("smallest private quarter", round(mv, 2), c7["quarter_min_m3"], mv >= c7["quarter_min_m3"], "m3"))
    couches = sum(r["couches"] for r in rooms)
    cs.append(chk("acceleration couches", couches, n, couches >= n, "", "a 5 g berth for every person in the cabins plus 6 station couches on the command deck" if occ else "a couch-bunk in every cabin plus 6 station couches on the command deck"))
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
    CR = crew_results()
    cr = CR["casualty_route"]
    cs.append(chk("casualty route at 0 g: litter along the ship's axis through every door", f"{cr['doors']['min_height_m']} x {cr['doors']['min_width_m']} m",
                  f">= {cr['doors']['need_height_m']} x {cr['doors']['need_width_m']} m", cr["doors"]["ok"] and cr["axial_fits_deck"]["ok"], "",
                  f"{cr['doors']['count']} doors; deck clear height {cr['axial_fits_deck']['clear_height_m']} m"))
    cs.append(chk("casualty route: litter down the port ladder shaft", f"{cr['shaft']['clear_m'][0]} x {cr['shaft']['clear_m'][1]} m clear",
                  f">= {cr['shaft']['need_m'][0]:.2f} x {cr['shaft']['need_m'][1]:.2f} m", cr["shaft"]["ok"], "", f"rungs on the {cr['shaft']['rungs_on']}"))
    sm = cr["shaft_to_medical"]
    cs.append(chk("casualty route: out of the shaft straight into the medical bay", sm["edge_margin_m"], 0.1, sm["ok"], "m clear of the opening's edge",
                  f"opening {sm['entrance_deg'][0]}-{sm['entrance_deg'][1]} deg; litter crosses {sm['litter_crosses_deg'][0]}-{sm['litter_crosses_deg'][1]} deg"))
    ac = CR["acceleration"]
    worst = min((r for r in ac["rows"] if r["in_couches"]), key=lambda r: r["ochmo_allowed_min"] / max(r["full_remass_burn_min"], 1e-9))
    cs.append(chk("sustained acceleration within the +Gx evidence (4 g cap)", f"{worst['mode']}: {worst['full_remass_burn_min']} min at up to {worst['accel_peak_g']} g",
                  f"<= {worst['ochmo_allowed_min']:.0f} min", ac["ok"], "", "worst mode shown; " + ac["note"]))
    ex = [r for r in ac["rows"] if r.get("split_needed")]
    cs.append(chk("time on the back per couch period ([V2 6113] 3 h 15 min, nominal 2 h 45 min)", max(r["longest_couch_period_min"] for r in ac["rows"] if r["in_couches"]),
                  I["habitat"]["crew_systems"]["accel_doctrine"]["on_back_nominal_min"], True, "min",
                  ("burns over 2 h 45 min are split by a 30 min coast break: " + ", ".join(f"{r['mode']} full-remass burn {r['full_remass_burn_min']} min" for r in ex)) if ex else ""))
    sb = CR["shelter_backup"]
    cs.append(chk("storm shelter: 72 h stored backup for 10 people", sb["stored_mass_t"], sb["allotted_t"], sb["ok"], "t",
                  f"O2 {sb['o2_kg']} kg, LiOH {sb['lioh_kg']} kg for {sb['co2_kg']} kg CO2, food {sb['food_kg']} kg, battery {sb['battery_kg']} kg (24 h); "
                  f"drinking water {sb['drink_water_kg']} kg from the shelter jacket ({sb['water_from_jacket_fraction'] * 100:.1f}%); {sb['heat_kw']} kW of heat"))
    dw = CR["docking_and_windows"]
    cs.append(chk("docking view: cameras at the collar and a vestibule window", f"{dw['cameras']} cameras, window {'yes' if dw['vestibule_window'] else 'no'}",
                  ">= 2 cameras and a window", dw["cameras"] >= 2 and dw["vestibule_window"]))
    if hab["decks"][0].get("command_layout",{}).get("i4_lock"):
        l1p = HERE / "command/l1_i4_results.json"
        if l1p.exists():
            L1R=json.loads(l1p.read_text())
            fresh=L1R.get("geometry_sha256")==G.get("_sha")
            cs.append(chk("I4 human-factors source geometry hash", L1R.get("geometry_sha256"),G.get("_sha"), fresh))
            for name,ok in L1R.get("checks",{}).items():
                cs.append(chk("I4 human factors: "+name, ok,True, fresh and ok, "",
                              "bounded L1 source-frame check; G7 is not certified until 3D/4g human-swept fit, sightline occlusions and ladder access closed"))
            decl.append(("i4_human_factors",
                         "I4 source-frame check rerun against current geometry. Scene seat length 1.58m <2.10m source crew envelope; "
                         "2D seat/ladder/walkways and bare dome clearances NOT physical 3D access or 4g qualification. "
                         "Crown sightlines are optimistic upper bounds only. All three annulus-floor couches now clear the rectangular terrace in a conservative 3D axis-aligned box test; S4 is moved +0.20m outboard with 0.0541m clearance. This is not occupant-swept collision testing. Optional terrace chamfer NOT BUILT."))
        else:
            cs.append(chk("I4 human-factors check exists for new geometry","missing",G.get("_sha"),False))
    else:
        l1p = HERE / "command/l1_study_results.json"
        if l1p.exists():
            L1R = json.loads(l1p.read_text())
            okl = L1R.get("geometry_sha256") == G.get("_sha") and all(L1R["checks"].values())
            cs.append(chk("L1 command deck (layout D, adopted): human-factors checks", f"{sum(L1R['checks'].values())}/{len(L1R['checks'])}",
                          "all, on this geometry", okl, "", "command/l1_study.py: couches, views through the armour bores, walkways, displays, sensors"))
    per_deck = {}
    for r in rooms:
        per_deck.setdefault(r["deck"], 0.0)
        per_deck[r["deck"]] += r["nhv_m3"]
    windows = len([f for f in G["features"] if f["kind"] == "window"])
    nberth = len([f for f in G["features"] if f.get("berth")])
    if nberth:
        nb_need = sum(r.get("occupancy", 0) for r in rooms if r.get("kind") == "cabin")
        cs.append(chk("berth viewports: one per berth (v0.5.7)", nberth, nb_need, nberth == nb_need, "",
                      "0.35 m, at the outer end of each berth; acrylic shield plug and insert keep the berth screen (G6 declared item berth_viewports)"))
    notes = [f"Target {target:.0f} m3 ({c7['nhv_target_m3_per_crew']:.0f} per crew, {c7['nhv_target_m3_per_guest']:.0f} per guest): reached {nhv / target * 100:.0f}%. "
             "A sixth deck (+2.6 m of habitat) would reach the target.",
             "Net habitable volume by deck: " + ", ".join(f"{k} {v:.0f} m3" for k, v in per_deck.items()),
             (f"Windows: the crown dome over L1 (25 m2), a panoramic viewport band round L2 ({(CR.get('viewport_band') or {}).get('glazed_area_m2', 0):.1f} m2, 1.6 m tall in the lounge), {windows - nberth} round viewports (4 shoulder on L1; L4 medical 2, storm shelter 2; L5 suits 1, workshop 2, vestibule 1) and {nberth} berth viewports (0.5 m) on L3. "
              f"With every shutter open about {(CR.get('viewport_band') or {}).get('heat_loss_kw_all_open', 0)} kW radiates through the low-e glazing; shutters close for night. "
              "The canon candidate suggests 10-16 windows; amendment v2.4f proposes more (kT's call). Below the crown every window has four panes, a dust shutter, a 12 deg armour splay and an acrylic shield plug"
              if nberth else f"Windows: {windows} (canon candidate suggests 10-16): 8 nose and 4 shoulder on L1, 2 in the observation lounge, 1 in the L5 vestibule; each with four panes, a shutter and a 12 deg armour splay"),
             "Casualties move at 0 g (coast on the captain's order); under thrust they are treated in their couch or berth.",
             "Decks are perpendicular to the thrust axis; under thrust, aft is down. Above ~1.5 g everyone rides in a couch."]
    if g7_occ_note:
        notes.append(g7_occ_note)
    r = gate("G7", "Compartments and crew space", cs, declared=decl, notes=notes)
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
    HF = I.get("hot_fins")
    if HF:
        worst = min(abs((HF["root_r_m"] + a_) * math.cos(math.radians(az)) - sd * HF["stowed_stack_thickness_m"] / 2 * math.sin(math.radians(az)))
                    for az in HF["azimuths_deg"] if math.sin(math.radians(az)) > 0
                    for a_ in (0.0, HF["pleat_m"], HF["pleat_m"] * HF["pleats"]) for sd in (-1, 1))
        cl = worst - Bay["slot_half_width_m"]
        cs.append(chk("hot fins clear the shuttle corridor (carried aft of the bay on +Z)", round(cl, 2), c8["corridor_clearance_m"],
                      cl >= c8["corridor_clearance_m"] - 1e-9, "m from the slot edge line",
                      f"fins at x {HF['x_m'][0]}-{HF['x_m'][1]} m, {HF['x_m'][0] - Bay['x_m'][1]:.2f} m aft of the bay; a shuttle that drifts aft on leaving or arriving still meets no fin"))
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
    HF = I.get("hot_fins")
    if HF and r4.get("torch_budget"):
        fspan = HF["pleat_m"] * HF["pleats"]
        fchord = HF["x_m"][1] - HF["x_m"][0]
        need = r4["torch_budget"]["ship_heat_gw"]
        worst = 1.0
        for lost in HF["azimuths_deg"]:
            azs = [a for a in HF["azimuths_deg"] if a != lost]
            fs_, _ = view_factor(azs, fspan, HF["root_r_m"], C["G4"]["view_factor_rays"])
            capl = 2 * len(azs) * fchord * fspan * HF["emissivity"] * SIGMA * HF["temperature_k"] ** 4 * fs_ / 1e9
            worst = min(worst, capl / need)
        jf = min(1.0, worst)
        cs.append(chk("one hot fin lost: torch still runs", f"{jf * 100:.0f}% jet power", f">= {C['G9']['one_fin_lost_min_jet_fraction'] * 100:.0f}%",
                      jf >= C["G9"]["one_fin_lost_min_jet_fraction"], "",
                      f"the torch throttles so its heat matches three fins; CRUISE at canon mass then gives about {jf:.2f} g"))
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
    bk = crew_results()["l4_l5_bulkhead"]
    cs.append(chk("L5 depressurised: the rest of the habitat stays pressurised", "isolated" if bk["ok"] and bk["trunk_plug"] and bk["hatches"] == 2 else "no",
                  "isolated", bk["ok"] and bk["trunk_plug"] and bk["hatches"] == 2, "", "floor L4 is a bulkhead; two ladderway hatches close on a pressure drop; a plug seals the trunk"))
    notes.append("Torch failure after departure is a Q6/Q7 degraded-mission case (survival possible, completion not assumed).")
    decl = []
    EE = G.get("external_equipment")
    if EE:   # rev 7 external equipment inventory (draft requirement; Sol: AGREE with the review's corrections)
        res = G["ledger_reserve_t"]
        cs.append(chk("engineering reserve after the rev 7 equipment", round(res, 2), "> 0", res > 0, "t",
                      f"{EE['new_from_reserve_t']:.2f} t of new hardware drawn; {EE['located_t']:.2f} t located inside existing ledger lines (no new mass)"))
        ext = [p for p in G["parts"] if "external" in p["tags"]]
        nfs = [f for f in G["features"] if f["kind"] == "node_face"]
        others = [f for f in G["features"] if f["kind"] != "node_face"]
        hits = []

        def rect(f):   # feature footprint: (x0, x1, a0, a1) in m and deg on the hull
            x, y, z = f["pos"]
            rr = math.hypot(y, z) or 1.0
            th = math.degrees(math.atan2(z, y)) % 360
            ax, ac = (f["size_m"][0], f["size_m"][1]) if f.get("size_m") else (f["d_m"], f["d_m"])
            da = math.degrees(ac / 2 / rr)
            return x - ax / 2, x + ax / 2, th - da, th + da

        def arcs_meet(a0, a1, b0, b1, pad):
            for k in (-360, 0, 360):
                if a0 - pad <= b1 + k and b0 + k <= a1 + pad:
                    return True
            return False
        for p in ext:
            sp = p["shape"]
            for f in nfs + others:
                fx0, fx1, fa0, fa1 = rect(f)
                pad = math.degrees(0.03 / sp["r1"])
                if sp["x0"] - 0.03 <= fx1 and fx0 <= sp["x1"] + 0.03 and arcs_meet(sp["a0"], sp["a1"], fa0, fa1, pad):
                    hits.append(f"{p['id']}/{f['kind']}")
                    break
        cs.append(chk("external equipment clear of node faces, windows, hatches and doors", len(hits), 0, not hits, "overlaps", ", ".join(hits[:6])))
        nb = "; ".join(f"{d['id']} {d['status']}" for d in EE["not_built"])
        decl.append(("external_equipment", f"External equipment (rev 7, ENGINEERING_ASSUMPTION): {len(ext)} parts from the inventory's 13 item types. Items with a ledger line are located "
                     f"inside it (sensor turrets in mission systems, RF arrays, laser terminals and aft trackers in the avionics racks, forward trackers in the bow sensor ring, "
                     f"service ports in the service arm, vents in life support, the docking target in the collar): {EE['located_t']:.2f} t, no new mass. New hardware "
                     f"(crawler docks and points, grapple fixtures, EVA rails): {EE['new_from_reserve_t']:.2f} t from the reserve. Not built: {nb}. Masses are 2026-analogue allowances to be sized."))
    return gate("G9", "Failures and reserves", cs, declared=decl, notes=notes)


# ---------------------------------------------------------------- G10 card
def card(I, G, r2):
    st = {}
    for s in states(I):
        v = G["states"][s]
        st[s] = {"name": v["name"], "mass_t": round(v["mass_t"], 2), "remass_usable_t": round(v["usable_remass_t"], 2),
                 "shuttle": v["shuttle"], "payload_t": v["payload_t"], "cg_m": [round(c, 4) for c in v["cg_m"]],
                 "inertia_tensor_kg_m2": [[round(x) for x in row] for row in v["inertia_kg_m2"]],
                 "principal_moments_kg_m2": [round(x) for x in v["principal_kg_m2"]],
                 "principal_axes": [[round(x, 6) for x in row] for row in v["principal_axes"]],
                 "thrust_trim_deg": round(v["trim_deg"], 4)}
        fd = v.get("fins_deployed")
        if fd:
            st[s]["hot_fins_deployed"] = {"inertia_tensor_kg_m2": [[round(x) for x in row] for row in fd["inertia_kg_m2"]],
                                          "principal_moments_kg_m2": [round(x) for x in fd["principal_kg_m2"]],
                                          "principal_axes": [[round(x, 6) for x in row] for row in fd["principal_axes"]],
                                          "note": "torch burns: hot fins unfolded (same mass and centre of mass)"}
    return {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING SANDBOX ship card for Navigator (gate G10)",
            "ship": f"Wayfarer v{I['version']}", "geometry_sha256": G["_sha"], "dry_t": round(G["dry_t"], 2),
            "fluids": {"water_t": I["canon"]["water_t"], "remass_t": I["canon"]["remass_t"], "protected_water_t": I["canon"]["protected_water_t"]},
            "torch": {"ve_km_s": I["canon"]["torch_ve_km_s"],
                      "mode_cards": I["torch"]["mode_cards"]["modes"], "mode_cards_source": I["torch"]["mode_cards"]["prov"],
                      "card_thrust_mn_by_mode": {m: round(v["card_thrust_mn"], 3) for m, v in r2["modes"].items()},
                      "jet_power_ceiling_tw": I["torch"]["jet_power_ceiling_tw"],
                      "thrust_mn_by_mode": {m: round(v["thrust_mn"], 3) for m, v in r2["modes"].items()},
                      "thrust_note": "thrust_mn_by_mode is what this ship can run: the working card held to its heat-rejection ceiling; the crew cap may throttle further",
                      "tvc_authority_deg": I["torch"]["tvc"]["authority_deg"],
                      "accel_cap_g": 4.0, "accel_cap_note": "crew doctrine v0.5.6: 4 g sustained with people aboard; 5 g is the structural rating (emergencies)", "thrust_line_offset_m": G["thrust_line_offset_m"], "thrust_point_x_m": I["torch"]["thrust_point_x_m"],
                      "architecture": "pulsed remass-shell torch (v0.5.2 heat package)",
                      "slew_rule": "fold the hot fins before large slews; inertia with fins out is given per state"},
            "hot_fins": G.get("hot_fins"),
            "dispatch_q7": {"normal_dispatch_remass_t": 150, "minimum_dispatch_remass_t": 100, "protected_optimizer_reserve_t": 50},
            "frame": "ship body axes: x from the bow toward the nozzle, y starboard, z toward the shuttle slot; origin at the bow datum; inertia about each state's centre of mass",
            "states": st,
            "missions_to_fly": ["E1 Ceres to Neptune", "FR-01B-R Ceres to Phobos", "MV-01 Ceres to Phoebe to Ganymede"],
            "pass_rule": "arrival remass >= 50 t protected optimizer reserve (Q7)"}


# ---------------------------------------------------------------- G11
def g11(I, C, G, r4):
    cn = I["canon"]
    dep = [
        ("Tanks", "4 major working-fluid tanks in quadrature (CANON II §13.2)", "one C-shaped wrap-around tank in 4 isolatable cells around an on-axis bay"),
        ("Longerons", "4 axial longerons", ("4 CFRP tubes in an X (v0.5.7): the upper pair edge the bay slot, the lower pair in the tank's lower cells; matches canon"
                                             if len(I["longerons"]["items"]) == 4 else f"{len(I['longerons']['items'])} longerons")),
        ("Length", f"~{cn['main_body_m'][0]} m main body", f"{I['hull']['length_m']} m"),
        ("Dry mass", f"~{cn['dry_t']} t", f"{G['dry_t']:.1f} t (includes 6 t for 4 guest berths)"),
        ("Wet mass", f"~{cn['wet_t']} t", f"{G['states']['S1']['mass_t']:.1f} t"),
        ("Launch bay", f"semi-recessed, reservation x {cn['bay_reservation_x_m'][0]}-{cn['bay_reservation_x_m'][1]} m", f"on-axis bore inside the tank, x {I['bay']['x_m'][0]}-{I['bay']['x_m'][1]} m, lateral exit through a 4.8 m slot on +Z"),
        ("Radiators", "4 assemblies in quadrature, 900 K equivalent card", f"4 accordion strakes at {I['radiators']['azimuths_deg']} deg (mirror-symmetric, not exactly 90 deg apart), {I['radiators']['temperature_k']} K"),
        ("Metric HARD electrical", "~23.9 MW at 900 K", f"{I['canon']['metric_cryo_electrical_mw_at_900K']['HARD'] * (I['radiators']['temperature_k'] - 20) / 880:.1f} MW at {I['radiators']['temperature_k']} K"),
        ("Torch axis", "1 axial torch", f"axial, with its thrust line offset {math.hypot(G['thrust_line_offset_m']['y'], G['thrust_line_offset_m']['z']):.2f} m from the hull centreline to pass through the centre of mass"),
        ("People", "6 normal crew", "6 crew (unchanged) + 4 guest berths"),
        ("Protected water", "50 t in the tanks", f"{G['protected_water'].get('shelter_jacket_t', G['protected_water']['jacket_t']):.1f} t storm-shelter jacket, {G['protected_water'].get('berth_shield_t', 0):.2f} t L3 berth shield ring, {G['protected_water']['service_tank_t']:.1f} t service tank, {G['protected_water']['c_tank_t']:.1f} t in the tank cells"),
        ("Shuttle", "candidate 30-35 t launch, ~10.5 m (not canon)", f"rover-drop shuttle {I['shuttle']['dry_t']} t empty, {I['shuttle']['length_m']} m"),
        ("Torch internals", "axial fusion torch / magnetic nozzle; internals not stated", "pulsed: each He3-rich, spin-polarised D-He3 pellet is wrapped in a shell of remass that becomes the exhaust; burn 6 m aft of the reactor face (x 52.3 m)"),
        ("Hot fins", "none", f"4 hot fins at {I['hot_fins']['temperature_k']} K aft of the shield on the strake lines, {I['hot_fins']['pleat_m'] * I['hot_fins']['pleats']:.0f} m, {I['ledger']['torch_hot_fins_t']:.1f} t paid from the engineering reserve"),
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
    man = HERE.parent / "render" / "out" / "manifest.json"
    if not man.exists():
        return gate("G12", "Images", [chk("images generated from the hashed geometry", "not yet", "all four sets", False)], force=OPEN)
    M = json.loads(man.read_text())
    srcsha=G["_sha"]
    files=M.get("files",[])
    cs=[chk("render manifest matches locked geometry",M.get("geometry_sha256"),srcsha,M.get("geometry_sha256")==srcsha)]
    mismatch=[e["file"] for e in files if e.get("geometry_sha256")!=srcsha or not (HERE.parent/"render"/"out"/e["file"]).is_file()]
    cs.append(chk("all indexed images and viewer have current hash and exist",len(mismatch),0,not mismatch))
    for kind, need in (("exterior",4),("cutaway",2),("deckplan",len(I["habitat"]["decks"])),("viewer",1)):
        n=sum(1 for f in files if f["kind"]==kind and f.get("geometry_sha256")==srcsha and (HERE.parent/"render"/"out"/f["file"]).exists())
        cs.append(chk(f"{kind} current-geometry artifacts",n,need,n>=need))
    OC=I["habitat"]["decks"][0]["command_layout"]["crown_dome"].get("shell_option_c")
    if OC:
        section=[f for f in files if f["file"]=="deck_crown_option_c_section.png" and f["geometry_sha256"]==srcsha]
        svg=HERE.parent/"render/out/deck_crown_option_c_section.svg"
        cs.append(chk("Option C 1:1 metric crown section current-hash PNG plus source SVG",
                      bool(section) and svg.exists(),True,bool(section) and svg.exists()))
        n_exteriors=sum(f["kind"]=="exterior" for f in files)
        cs.append(chk("Option C all previously dropped exterior views rerendered",n_exteriors,10,n_exteriors>=10))
        viewers=HERE.parent/"render/research"
        docs=HERE.parent/"docs/nose_research"
        n_docs=len(list(docs.glob("NOSE_*.md")))
        n_views=len(list(viewers.glob("*.html")))
        cs.append(chk("Original NOSE research and viewer assets preserved under wayfarer/",
                      [n_docs,n_views],[21,28],n_docs>=21 and n_views>=28))
    import struct
    glb=HERE.parent/"render"/"out"/f"wayfarer_I4_in_out_{srcsha[:8]}.glb"
    glb_valid=False
    if glb.exists():
        raw=glb.read_bytes()
        if len(raw)>=20 and raw[:4]==b"glTF":
            jlen,jtyp=struct.unpack_from("<II",raw,12)
            if jtyp==0x4e4f534a and 20+jlen<=len(raw):
                desc=json.loads(raw[20:20+jlen])
                glb_valid=(desc.get("extras",{}).get("geometry_sha256")==srcsha and len(desc.get("scenes",[]))>=2)
    cs.append(chk("one GLB with exterior and I4 interior scenes stamped with current hash",glb_valid,True,glb_valid))
    note=["Manifest hash + current files + 2-scene GLB verified; full 64-character SHA stamped by source render templates.",
          "G12 visuals remain NON-GOVERNING pending kT aesthetic/geometry interpretation review; screenshot existence does not qualify hardware, pressure crown or humans."]
    return gate("G12","Images",cs,declared=[("kT_visual_acceptance","Required before treating rendered representation as accepted design evidence; generated images meet source/hash coverage only")],notes=note)


# ---------------------------------------------------------------- report

# ---------------------------------------------------------------- G10 v0.2 flight dynamics
def g10(r4, scr):
    """G10 v0.2 (CERTIFICATION_BASIS.md): flight-dynamics tests of RCS, torch, Metric and Loom
    in g10/g10_flight_dynamics.py, built on main's src/ modules. Navigator missions are follow-up validation, not gating."""
    g10_dir = HERE / "g10"
    try:
        sys.path.insert(0, str(g10_dir))
        import g10_flight_dynamics as FD
        r = FD.run(r4["checks"])
    except Exception as e:   # outside the loom-2226 repo the main src/ modules are absent
        return gate("G10", "Flight dynamics", [chk("G10 v0.2 tests run", f"not run: {e}", "run", False)], force=OPEN,
                    notes=["G10 v0.2 needs the loom-2226 repository root (src/ modules on main). " + "; ".join(scr)])
    (g10_dir / "g10_results.json").write_text(json.dumps(r, indent=1))
    checks = [dict(c, name=f"{grp.split('_')[0]}: {c['name']}") for grp, cs in r["checks"].items() for c in cs]
    I = json.loads((HERE.parent / "config/wayfarer_v05_inputs.json").read_text())
    decl = [("torch_tvc", f"Torch thrust-vector control: the magnetic nozzle steers the thrust line by up to {I['torch']['tvc']['authority_deg']} deg (asymmetric coil current). "
                          f"Needed: trim plus an assumed {FD.MISALIGN_DEG} deg thrust error ({r['detail']['rcs']['tvc_needed_deg']} deg). The error is an engineering assumption, not a measured disturbance history; the authority is not a qualified nozzle capability."),
            ("rcs_axial_plumes", "Axial RCS: one 25 kN thruster per cluster, canted 10 deg outward (bow ones exhaust forward, aft ones aft). Assumes the plumes clear the crown glazing, hull, hot fins and torch chain; plume impingement is not yet modelled."),
            ("g10_burn_coasts", f"Long torch burns split into segments of at most {FD.SEGMENT_MAX_MIN:.0f} min ([V2 6113]) with {FD.COAST_MIN:.0f} min coasts (engineering assumption; in free space the coasts change elapsed time, not delta-v).")]
    if I["habitat"]["decks"][0]["command_layout"]["crown_dome"].get("shell_option_c"):
        decl.append(("crown_option_c_axial_rcs_plumes",
             "External nose shifted 1.2m forward with flat 2m crown and 50deg face. Old accepted G10 axial RCS plume direction/impingement declaration predates the extended nose; no new plume clearance proof performed. The existing RCS nozzle geometry is unchanged, but plume impingement on Option C gores/ceramic/retainers remains HOLD."))
    return gate("G10", "Flight dynamics: RCS, torch, Metric, Loom", checks, declared=decl,
                notes=[f"{r['passed']}/{r['total']} checks pass. Sources: main {r['sources']['main_commit'][:8]}; see g10/G10_SOURCE_MAP.md.",
                       "Basis v0.2, agreed by Sol 2026-10-26. Not computed by design: Metric delta-v and remass (CANON II s20); Loom domain fit (PR #356).",
                       "Follow-up validation, not gating: " + "; ".join(r["deferred_not_gating"]),
                       "Screening only (ideal rocket equation at CRUISE from the S1 mass): " + "; ".join(scr) + "."])

def main():
    I, C, G = load()
    G["_sha"] = hashlib.sha256((HERE.parent / "results/out/wayfarer_v05_geometry.json").read_bytes()).hexdigest()
    r1, r2, r3 = g1(I, C, G), g2(I, C, G), g3(I, C, G)
    r4 = g4(I, C, G)
    r5 = g5(I, C, G)
    r6 = g6(I, C, G)
    r7, r8 = g7(I, C, G), g8(I, C, G)
    r9 = g9(I, C, G, r3, r4, r5)
    cd = card(I, G, r2)
    (HERE.parent / "results/out/wayfarer_v05_card.json").write_text(json.dumps(cd, indent=1))
    M1 = G["states"]["S1"]["mass_t"]
    vc = I["canon"]["torch_ve_km_s"]["CRUISE"]
    scr = []
    for dv in (50, 100, 200, 300):
        used = M1 * (1 - math.exp(-dv / vc))
        scr.append(f"{dv} km/s: {used:.1f} t ({'within' if 150 - used >= 50 else 'beyond'} 150 t dispatch less the 50 t reserve)")
    r10 = g10(r4, scr)
    r11, r12 = g11(I, C, G, r4), g12(I, C, G)
    gates = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12]
    kd_path = HERE.parent / "config/kt_decisions.json"
    KD = json.loads(kd_path.read_text()) if kd_path.exists() else {"decisions": {}}
    for g in gates:
        g["declared"] = [{"key": k, "text": txt, "kT": KD["decisions"].get(k, {"decision": "AWAITING"}).get("decision"),
                          "as": KD["decisions"].get(k, {}).get("as", ""), "date": KD["decisions"].get(k, {}).get("date")}
                         for k, txt in g["declared"]]
    summary = {g["gate"]: g["verdict"] for g in gates}
    rep = {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING SANDBOX certification run",
           "basis": "CERTIFICATION_BASIS.md v0.2 (agreed by Claude and Sol; PROPOSED to kT)", "geometry_sha256": G["_sha"], "inputs_sha256": G["inputs_sha256"],
           "criteria_sha256": hashlib.sha256((HERE.parent / "config/cert_criteria.json").read_bytes()).hexdigest(),
           "summary": summary, "gates": gates,
           "declared_for_kT": [d for g in gates for d in g["declared"]],
           "kt_decisions_sha256": hashlib.sha256(kd_path.read_bytes()).hexdigest() if kd_path.exists() else None,
           "certified": all(g["verdict"] in (PASS, DECL) for g in gates) and all(d["kT"] == "ACCEPTED" for g in gates for d in g["declared"]),
           "certified_rule": "every gate PASS or PASS-DECLARED and every declared assumption ACCEPTED by kT; then both reviewers sign and loom-gate passes",
           "qualification_scope": {
               "certified_flag_meaning": "kT-accepted declared G1-G12 conventional Wayfarer laboratory certification basis ONLY; not independent reviewer signatures, Metric arrival or hardware flightworthiness",
               "conventional_lab_scope": "G1-G12 conventional numerical and declared source-geometry evidence",
               "metric_arrival": "HOLD: arrival dynamics, remass and arrival state not qualified",
               "navigator": "EXCLUDED: no runtime or mission/card integration",
               "rcs_power_source": "OPEN: idle torch reactor versus dedicated supply; no ship-wide budget",
               "rcs_power_option_B": "hot-water store OPTION, not baseline",
               "required_final_authority": "separate reviewer signatures and loom-gate per existing basis",
               "geometry_sha256": G["_sha"],
           }}
    (HERE.parent / "results/out/certification_report.json").write_text(json.dumps(rep, indent=1, default=str))
    (HERE.parent / "results/out/CERTIFICATION_REPORT_v0.5.md").write_text(markdown(rep, G))
    for g in gates:
        bad = [c["name"] for c in g["checks"] if not c["pass"]]
        print(f"{g['gate']:4} {g['verdict']:14} {g['title']}" + (f"   fails: {bad}" if bad and g["verdict"] == FAIL else ""))


def fmt(v):
    if isinstance(v, float):
        return f"{v:,.1f}" if abs(v) >= 100 else f"{v:.3g}"
    return str(v)


def markdown(rep, G):
    L = ["# Wayfarer v0.5 certification report", "", "ALL bodies. ALL sponsors. 2026-2226.", "",
         "**NON-GOVERNING SANDBOX.** Run against CERTIFICATION_BASIS.md v0.2 (agreed by Claude and Sol; proposed to kT). Generated by `certify.py`; do not edit by hand.", "",
         f"Geometry sha256 `{rep['geometry_sha256']}`", f"Inputs sha256 `{rep['inputs_sha256']}`", f"Criteria sha256 `{rep['criteria_sha256']}`", "",
         "## Summary", "", "| Gate | Verdict |", "|---|---|"]
    for g in rep["gates"]:
        L.append(f"| {g['gate']} {g['title']} | {g['verdict']} |")
    L += ["", "## Conventional certification scope and explicit HOLDS", "",
          f"Script certified flag: {str(rep['certified']).lower()}; kT-declared conventional G1-G12 lab acceptance only. Not a physical flightworthiness certificate, Metric arrival authority or replacement for reviewer signatures and loom-gate.", "",
          f"Locked geometry: {rep['geometry_sha256']}.", "",
          "Metric arrival: HOLD. No qualified arrival remass, trajectory or state.", "",
          "Navigator: EXCLUDED. No runtime card integration or missions.", "",
          "RCS power source: OPEN. Idle torch reactor or dedicated supply; no ship-wide bus/thermal budget. Routine flips 120s, fast flips emergency-only; hot-water store OPTION B.", "",
          "## Declared assumptions and kT's decisions", ""]
    for d in rep["declared_for_kT"]:
        L.append(f"- **{d['kT']}{' by kT ' + d['date'] if d['date'] else ''}.** {d['text']}" + (f" Decision: {d['as']}" if d["as"] else ""))
    L += ["", f"Script verdict on certification: {'all computable gates pass and every declared assumption is accepted' if rep['certified'] else 'NOT YET: at least one gate is OPEN or FAIL, or a declared assumption awaits kT'}. Sign-off still needs both reviewers and loom-gate."]
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
