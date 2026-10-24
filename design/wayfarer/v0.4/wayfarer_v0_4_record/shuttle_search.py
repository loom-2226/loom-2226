"""Shuttle design search v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Reads shuttle_space.json, flies every ascent and entry
once (shuttle_tables.json), then sizes every combination of engine, entry
shape, rover and Venus strategy against nine round trips from the mothership's
parking orbit. Writes shuttle_results.json.
Usage: python shuttle_search.py [--rebuild]"""
import json, math, sys, itertools
from multiprocessing import Pool
from pathlib import Path
import shuttle_physics as sp

HERE = Path(__file__).resolve().parent
S = sp.S
G0 = 9.80665
TABLES = HERE / "shuttle_tables.json"
REFUEL_RESERVE = 0.10
JR = S["job_rules"]
TP = S["propulsion"]["TORCH"]
ENGINES = ["METHALOX", "HYDROLOX", "NTR"] + [f"TORCH{s}" for s in TP["specific_power_kw_kg"]]
STARTS = {"Moon": ("Moon", 0, 0), "Mercury": ("Mercury", 0, 0), "Ceres": ("Ceres", 0, 0), "Callisto": ("Callisto", 0, 0),
          "Mars": ("Mars", 0, 0), "Earth": ("Earth", 0, 0), "Titan": ("Titan", 0, 0),
          "Venus@0": ("Venus", 0, 0), "Venus@40": ("Venus", 40, 10), "Venus@55": ("Venus", 55, 0)}
ENTRY_BODIES = ["Mars", "Earth", "Titan", "Venus"]
BETAS = [100, 300, 1000, 3000, 6000]
M_REF = S["ascent_reference"]["m0_t"] * 1e3


def E_KIND(etype):
    return S["entry"][etype].get("kind")


def torch_s(eng):
    return int(eng[5:]) if eng.startswith("TORCH") else None


def make_engine(eng, body, start_km, m0=M_REF):
    atm = sp.Atmosphere(body)
    if eng.startswith("TORCH"):
        P = torch_s(eng) * 1e3 * m0
        return (lambda: sp.Torch(P))
    pa, _ = atm.state(start_km * 1e3)
    fv = sp.Chemical.f_vac_for(eng, pa, JR["liftoff_tw"] * m0 * max(G0, atm.g(start_km * 1e3)))
    if not math.isfinite(fv):
        return None
    return (lambda: sp.Chemical(eng, fv))


def _asc(args):
    start, eng = args
    body, h0, v0 = STARTS[start]
    mk = make_engine(eng, body, h0)
    if mk is None:
        return start, eng, None
    return start, eng, sp.best_ascent(body, mk, M_REF, start_km=h0, v0=v0, t_max=20000)


def _ent(args):
    body, etype, beta = args
    e = S["entry"][etype]
    if E_KIND(etype) == "deployable":
        d = math.sqrt(4 * M_REF / (math.pi * e["cd"] * beta))
        rn = e["nose_r_fraction_of_d"] * d
    else:
        rn = e["nose_r_m"]
    stop = JR["landing_burn_alt_km"][body]
    r = sp.entry(body, beta, e["ld"], rn, stop_km=stop, checkpoints_km=(55,) if body == "Venus" else ())
    return body, etype, beta, r


def build_tables():
    jobs_a = [(s, e) for s in STARTS for e in ENGINES]
    jobs_e = [(b, t, beta) for b in ENTRY_BODIES for t in ("LIFTING_BODY", "BICONIC", "CAPSULE") for beta in BETAS]
    jobs_e += [(b, k, v["beta_target"]) for b in ENTRY_BODIES for k, v in S["entry"].items() if isinstance(v, dict) and v.get("kind") == "deployable"]
    with Pool(2) as p:
        A = p.map(_asc, jobs_a)
        E = p.map(_ent, jobs_e)
    tab = {"ascent": {}, "entry": {}}
    for s, e, r in A:
        tab["ascent"].setdefault(s, {})[e] = r
    for b, t, beta, r in E:
        tab["entry"].setdefault(b, {}).setdefault(t, {})[str(beta)] = r
    TABLES.write_text(json.dumps(tab, indent=1))
    return tab


# ---------------------------------------------------------------- helpers
def ve_vac(eng):
    return TP["ve_max_km_s"] if eng.startswith("TORCH") else S["propulsion"][eng]["ve_vac_km_s"]


def ve_at(eng, pa, tw=None, s=None, g=G0):
    """effective exhaust speed (km/s) for a hard burn at ambient pa"""
    if eng.startswith("TORCH"):
        tq = sp.Torch(1.0)
        f = tq.f(pa)
        if f <= 0:
            return 0.0, 0.0
        tw_av = 2 * s * 1e3 * f / (TP["ve_min_km_s"] * 1e3 * g)
        tw_use = min(tw or JR["landing_tw"], tw_av)
        ve_set = min(TP["ve_max_km_s"], max(TP["ve_min_km_s"], 2 * s * f / (tw_use * g)))
        return f * ve_set, tw_use
    e = sp.Chemical(eng, 1.0)
    return e.ve(pa) / 1e3, tw or JR["landing_tw"]


def _with_v55(r):
    r = dict(r)
    r["v55"] = r.get("v_at_m_s", {}).get("55")
    return r


def lerp_entry(tab, body, etype, beta):
    t = tab["entry"][body][etype]
    if E_KIND(etype) == "deployable":
        return _with_v55(list(t.values())[0])
    bs = sorted(int(b) for b in t)
    beta = min(max(beta, bs[0]), bs[-1])
    for b0, b1 in zip(bs, bs[1:]):
        if beta <= b1:
            f = math.log(beta / b0) / math.log(b1 / b0)
            r0, r1 = t[str(b0)], t[str(b1)]
            out = {}
            for k in ("heat_load_j_cm2", "q_peak_w_cm2", "g_peak", "v_at_stop_m_s", "dv_deorbit_km_s"):
                out[k] = math.exp(math.log(max(r0[k], 1e-9)) + f * (math.log(max(r1[k], 1e-9)) - math.log(max(r0[k], 1e-9))))
            out["v55"] = None
            if r0["v_at_m_s"].get("55"):
                out["v55"] = r0["v_at_m_s"]["55"] + f * (r1["v_at_m_s"]["55"] - r0["v_at_m_s"]["55"])
            return out
    return _with_v55(t[str(bs[-1])])


def areal_tps(q_j_cm2):
    T = S["tps_model"]
    return T["areal_coeff"] * max(q_j_cm2, 1.0) ** T["exponent"]


def tps_mass(etype, q_stag, entry_t, planform, frontal, side=0.0):
    """heat shield mass (t) from the worst stagnation heat load and the heated areas"""
    E = S["entry"][etype]
    T = S["tps_model"]
    if E["kind"] == "rigid" and etype in ("LIFTING_BODY", "BICONIC"):
        L_ = T["lifting"]
        return (L_["edge_factor"] * areal_tps(q_stag * E["acreage_factor"]) * planform
                + L_["leeward_kg_m2"] * L_["leeward_area_factor"] * planform) / 1e3
    if etype == "CAPSULE":
        C_ = T["capsule"]
        a = math.pi * (max(frontal, 1.0) ** 0.5) ** 2 / 4 * 4 / math.pi  # frontal box area
        return (C_["shield_factor"] * areal_tps(q_stag) * a + C_["backshell_kg_m2"] * a) / 1e3
    if E["kind"] == "deployable":
        D_ = T["deployable"]
        area = entry_t * 1e3 / (E["cd"] * E["beta_target"])
        return ((areal_tps(q_stag) + D_["rib_kg_m2"]) * area + D_["body_kg_m2"] * frontal
                + D_.get("side_kg_m2", 0.0) * D_.get("side_share", 0.0) * side) / 1e3
    return 0.0


def ti_sphere(volume_m3, shape=1.0):
    """hardened cabin: titanium sphere sized against buckling at the Venus surface"""
    H = S["hardening"]
    ti = H["titanium"]
    p_surf = sp.Atmosphere("Venus").state(0)[0]
    R = (3 * volume_m3 / (4 * math.pi)) ** (1 / 3)
    coef = ti["knockdown"] * 2 * ti["e_gpa_hot"] * 1e9 / math.sqrt(3 * (1 - ti["poisson"] ** 2))
    t = R * math.sqrt(ti["safety"] * p_surf / coef)
    hull_t = 4 * math.pi * R ** 2 * t * ti["density"] * shape / 1e3
    ins = H["insulation"]
    ro = R + t
    ins_t = 4 * math.pi * ro ** 2 * ins["thickness_m"] * ins["density"] * shape / 1e3
    T_out = sp.Atmosphere("Venus").temperature(0)
    leak_kw = ins["k_w_mk"] * (T_out - 295) * 4 * math.pi * (ro + ins["thickness_m"]) ** 2 * shape / ins["thickness_m"] / 1e3
    stress = p_surf * R / (2 * t) / 1e6
    return {"R_m": R, "wall_mm": t * 1e3, "hull_t": hull_t, "insulation_t": ins_t, "leak_kw": leak_kw,
            "od_m": 2 * (ro + ins["thickness_m"]), "stress_mpa": stress}


def venus_rover(sortie_h):
    r = S["rovers"]["VENUS"]
    H = S["hardening"]
    c = ti_sphere(r["cabin_m3"])
    heat_kw = c["leak_kw"] + H["internal_heat_kw_base"] + r["crew"] * H["internal_heat_kw_per_crew"]
    ice_t = heat_kw * 3600 * sortie_h / (H["ice_sink_mj_per_kg"] * 1e3) / 1e3
    life_t = 0.3
    m = c["hull_t"] + c["insulation_t"] + ice_t + r["chassis_t"] + r["battery_t"] + r["hatch_skirt_t"] + life_t + 0.1 * r["crew"]
    od = c["od_m"]
    dims = [S['rovers']['VENUS']['length_m'], max(2.6, od + 0.3), od + 0.3]
    return {"mass_t": m, "dims_m": dims, "cabin": c, "heat_kw": heat_kw, "ice_t": ice_t, "crew": r["crew"]}


def lift_kit(mass_t, displaced_m3, areal, rho_ratio_at=55.0, margin=1.1, dewar_frac=0.3, rigging=0.0, at_surface=True):
    """hydrogen balloon: gas and envelope (sized at the float height) to lift mass_t"""
    atm = sp.Atmosphere("Venus")
    lift_ratio = S["lift_gas"]["h2_lift_kg_per_kg"]
    rho_surf = atm.state(0)[1] if at_surface else atm.state(rho_ratio_at * 1e3)[1]
    rho_float = atm.state(rho_ratio_at * 1e3)[1]
    rho_h2 = rho_float / (lift_ratio + 1)
    env = 0.0
    for _ in range(30):
        need = (mass_t * 1e3 + env * 1e3 + rigging * 1e3 - rho_surf * displaced_m3) * margin
        gas = max(0.0, need) / lift_ratio
        V = gas / rho_h2
        r = (3 * V / (4 * math.pi)) ** (1 / 3)
        env_new = 4 * math.pi * r * r * areal / 1e3
        if abs(env_new - env) < 1e-4:
            break
        env = env_new
    return {"gas_t": gas / 1e3, "envelope_t": env, "rigging_t": rigging, "dewar_t": dewar_frac * gas / 1e3,
            "radius_m": r, "dropped_t": gas / 1e3 + env + rigging}


def fan_kit(mass_t, displaced_m3, planform_m2, fly_ld, eng, P_jet_w):
    """climb 0 -> 40 km on electric fans (flying on the body's lift where it has some)"""
    V = S["venus_strategies"]["FLY_UP"]
    atm = sp.Atmosphere("Venus")
    vc, eta, cl = V["climb_m_s"], V["fan_efficiency"], V["cl"]
    a_fan = V["fan_disc_fraction_of_planform"] * planform_m2
    E = Pk = 0.0
    for hk in range(0, V["rocket_from_km"]):
        pa, rho = atm.state(hk * 1e3 + 500)
        g = atm.g(hk * 1e3)
        w = max(1.0, (mass_t * 1e3 - rho * displaced_m3) * g)
        if fly_ld > 1:
            v_l = math.sqrt(2 * w / (rho * planform_m2 * cl))
            P = w * (vc + v_l / fly_ld) / eta
        else:
            P = w * vc / eta + w ** 1.5 / math.sqrt(2 * rho * a_fan) / eta
        Pk = max(Pk, P)
        E += P * 1000 / vc
    fan_t = Pk / (V["fan_kw_per_kg"] * 1e3) / 1e3
    if eng.startswith("TORCH"):
        ok = TP["electric_fraction"] * P_jet_w >= Pk
        return {"peak_mw": Pk / 1e6, "energy_gj": E / 1e9, "fan_t": fan_t, "power_t": 0.0, "reactant_t": 0.0, "power_ok": ok}
    return {"peak_mw": Pk / 1e6, "energy_gj": E / 1e9, "fan_t": fan_t, "power_t": Pk / (V["fuel_cell_kw_per_kg"] * 1e3) / 1e3,
            "reactant_t": E / (V["fuel_cell_mj_per_kg"] * 1e6) / 1e3, "power_ok": True}


# ---------------------------------------------------------------- one design
def geometry(etype, need_m3, rover_dims, elong=1.0):
    G = S["geometry"]
    a0 = S["entry"][etype]["aspect_lwh"]
    asp = [a0[0] * elong, a0[1] / math.sqrt(elong), a0[2] / math.sqrt(elong)]
    vbox = need_m3 / S["entry"][etype].get("packing", G["packing"])
    k = (vbox / (asp[0] * asp[1] * asp[2])) ** (1 / 3)
    L, W, H = asp[0] * k, asp[1] * k, asp[2] * k
    if rover_dims:
        pad = 2 * (G["rover_clearance_m"] + G["wall_m"])
        W = max(W, rover_dims[1] + pad)
        H = max(H, rover_dims[2] + pad)
        L = max(vbox / (W * H), rover_dims[0] + pad + 3.0)
    bay = [L + G["bay_margin_m"][0], W + G["bay_margin_m"][1], H + G["bay_margin_m"][2]]
    return [L, W, H], bay


def size_design(tab, eng, etype, rover, venus, jobs, refuel=(), elong=1.0, kits_per_trip=False, trip_payload=None):
    """size one design for a set of jobs; returns dict with per-job results"""
    E = S["entry"][etype]
    H = S["hardening"]
    C = S["cabin"]
    s = torch_s(eng)
    vv = ve_vac(eng)
    lands_venus = S["venus_strategies"][venus]["shuttle_lands"] and "Venus surface" in jobs
    drop = venus.startswith("DROP") and "Venus surface" in jobs
    notes = []
    # rover and cabin
    cabin_t = C["crew"] * C["t_per_crew"]
    cab_hard = None
    rov = None
    if rover == "VENUS":
        rov = venus_rover(H["sortie_h_drop"] if drop else H["surface_stay_h"])
        rover_t, rover_dims = rov["mass_t"], rov["dims_m"]
    elif rover == "CABIN_DRIVE":
        rover_t, rover_dims = S["rovers"]["CABIN_DRIVE"]["chassis_t"], None
    else:
        rover_t, rover_dims = S["rovers"][rover]["mass_t"], S["rovers"][rover]["dims_m"]
    cabin_hardened = lands_venus or (drop and rover == "CABIN_DRIVE")
    if cabin_hardened:
        cab_hard = ti_sphere(C["crew"] * C["m3_per_crew"], S["hardening"]["shape_factor_noncabin_sphere"])
    # state
    m_p = 15.0
    f_vac = 0.0
    entry_max = 0.0
    land_max = 0.0
    kit = {"dropped": 0.0, "kept": 0.0}
    res = {}
    for it in range(120):
        # ---- dry mass build-up (tonnes)
        fixed = cabin_t + C["crew_and_kit_t"] + S["systems_t"] + rover_t
        hard_t = 0.0
        sink_t = 0.0
        if cab_hard:
            hard_t = cab_hard["hull_t"] + cab_hard["insulation_t"]
        tanks = S["propulsion"]["TORCH" if s else eng]["tank_fraction"] * m_p
        if s:
            engine = 0.0  # set after wet mass known
        else:
            engine = f_vac / (S["propulsion"][eng]["engine_tw"] * G0) / 1e3
        kit_in_dry = 0.0 if kits_per_trip else kit["kept"] + kit["dropped"]
        base = fixed + hard_t + tanks + engine + kit_in_dry
        legs = S["legs_fraction"] * land_max
        aero = E.get("aero_fraction", 0.0) * base
        tps = 0.0
        if res.get("_q_max") and res.get("_areas"):
            tps = tps_mass(etype, res["_q_max"], entry_max, *res["_areas"])
        rest_hard = H["rest_of_ship_fraction"] * (base - fixed - hard_t) if lands_venus else 0.0
        if s:
            wet_guess = res.get("_wet", 40.0)
            engine = (s * wet_guess / 1e3) / TP["gw_per_t"] + TP["fixed_t"]   # s kW/kg x wet t = MW; /1e3 -> GW
        sub = base + engine + legs + aero + tps + rest_hard + sink_t
        dry = sub * (1 + S["structure_fraction"]) * (1 + S["growth_margin"])
        breakdown = {"cabin_crew_systems": cabin_t + C["crew_and_kit_t"] + S["systems_t"], "rover": rover_t, "hardened_cabin": hard_t,
                     "tanks": tanks, "engine": engine, "legs": legs, "aero_surfaces": aero, "heat_shield": tps,
                     "venus_kits": kit["kept"] + kit["dropped"], "venus_hardening_rest": rest_hard,
                     "structure": sub * S["structure_fraction"], "growth_margin": sub * (1 + S["structure_fraction"]) * S["growth_margin"]}
        dropped = kit["dropped"]
        # ---- geometry (volume budget)
        dens = S["propulsion"]["TORCH" if s else eng]["bulk_density"]
        need = (C["crew"] * C["m3_per_crew"] if not cab_hard else (math.pi / 6) * cab_hard["od_m"] ** 3 * H["shape_factor_noncabin_sphere"])
        need += (rover_dims[0] + 0.6) * (rover_dims[1] + 0.6) * (rover_dims[2] + 0.6) if rover_dims else 3.0
        need += m_p * 1e3 / dens * 1.08 + engine * S["geometry"]["engine_m3_per_t"] + S["geometry"]["systems_m3"]
        need += kit.get("stow_m3", 0.0)
        dims, bay = geometry(etype, need, rover_dims, elong)
        L, W, Hh = dims
        planform = L * W * E.get("planform_fill", 0.8)
        disp = L * W * Hh * 0.55
        a_ref = planform if etype in ("LIFTING_BODY", "BICONIC") else (math.pi * W * W / 4)
        perim = math.pi * (3 * (W / 2 + Hh / 2) - math.sqrt((3 * W / 2 + Hh / 2) * (W / 2 + 3 * Hh / 2)))
        res["_areas"] = (planform, W * Hh, perim * L)
        # ---- per-job chains
        jr_prev = res.get("_jr", {})
        jr = {}
        new_entry = new_land = new_fvac_need = 0.0
        q_max = 0.0
        kit_new = {"dropped": 0.0, "kept": 0.0, "stow_m3": 0.0}
        venus_info = {}
        for job in jobs:
            body = S["jobs"][job]["body"]
            atm = sp.Atmosphere(body)
            g_l = atm.g(0)
            phases = []
            ok, why = True, ""
            site = S["jobs"][job].get("site_km", 0)
            # ascent start and its table
            if job == "Venus surface":
                if venus == "NONE":
                    jr[job] = {"ok": False, "why": "no Venus surface strategy"}
                    continue
                if rover in ("OPEN", "PRESS"):
                    jr[job] = {"ok": False, "why": "rover cannot work at 92 bar and 735 K"}
                    continue
                if drop and rover == "VENUS" or drop and rover == "CABIN_DRIVE" or lands_venus:
                    pass
                start = {"DIRECT": "Venus@0", "FLY_UP": "Venus@40", "BALLOON": "Venus@55"}.get(venus, "Venus@55")
            elif job == "Venus clouds":
                start = "Venus@55"
            else:
                start = body
            A = tab["ascent"][start][eng]
            if A is None:
                jr[job] = {"ok": False, "why": f"cannot reach orbit from {start}"}
                continue
            mr_asc = A["mass_ratio"] ** (1 + JR["dv_margin_fraction"])
            if s:
                st_body, st_h, _ = STARTS[start]
                st_atm = sp.Atmosphere(st_body)
                f_amb = sp.Torch(1.0).f(st_atm.state(st_h * 1e3)[0])
                buoy = st_atm.state(st_h * 1e3)[1] * disp * st_atm.g(st_h * 1e3)
                m_lo = jr_prev.get(job, {}).get("liftoff_t", res.get("_wet", 40))
                tw0 = 2 * s * 1e3 * res.get("_wet", 40) * 1e3 * f_amb / (TP["ve_min_km_s"] * 1e3) / max(1.0, (m_lo * 1e3 * st_atm.g(st_h * 1e3) - buoy))
                if tw0 < 1.15:
                    jr[job] = {"ok": False, "why": f"torchlet lift-off thrust/weight {tw0:.2f}"}
                    continue
            # descent
            if atm.a is None:
                phases.append(("burn", mr_asc * math.exp(JR["hover_km_s"] / vv)))
            elif etype == "PROPULSIVE":
                Ad = tab["ascent"][body if body != "Venus" else "Venus@55" if site else "Venus@0"][eng]
                if Ad is None:
                    jr[job] = {"ok": False, "why": "cannot brake down without a heat shield"}
                    continue
                phases.append(("burn", Ad["mass_ratio"] ** (1 + JR["dv_margin_fraction"])))
            else:
                ent_m = res.get("_entry_mass_" + job, 40.0)
                beta = ent_m * 1e3 / (E["cd"] * a_ref) if E_KIND(etype) != "deployable" else E["beta_target"]
                en = lerp_entry(tab, body, etype, beta)
                phases.append(("burn", math.exp(en["dv_deorbit_km_s"] * (1 + JR["dv_margin_fraction"]) / vv)))
                phases.append(("mark_entry", 0))
                q_max = max(q_max, en["heat_load_j_cm2"])
                if E_KIND(etype) == "deployable" and en["q_peak_w_cm2"] > E["q_limit_w_cm2"]:
                    ok, why = False, "deployable shield over its heat-flux limit"
                if job == "Venus clouds" or (job == "Venus surface" and drop):
                    v_site = en["v55"] or 150
                    pa_site = atm.state(55e3)[0]
                    dv_land = JR["hover_km_s"]  # glide in and get caught by the city / float
                else:
                    v_site = en["v_at_stop_m_s"]
                    pa_site = atm.state(JR["landing_burn_alt_km"][body] * 1e3)[0]
                    vel, tw = ve_at(eng, pa_site, s=s, g=g_l)
                    if vel <= 0 or tw <= 1.05:
                        if body == "Venus" and v_site <= 15:
                            dv_land = 0.0
                            notes.append("Venus touchdown on drag alone (Venera style)")
                        else:
                            jr[job] = {"ok": False, "why": "engine cannot land at this ambient pressure"}
                            continue
                    else:
                        dv_land = v_site / 1e3 * (1 + 1 / (tw - 1)) + JR["hover_km_s"]
                vel, _ = ve_at(eng, pa_site, s=s, g=g_l)
                if dv_land > 0:
                    phases.append(("burn", math.exp(dv_land * (1 + JR["dv_margin_fraction"]) / max(vel, 0.1))))
            phases.append(("mark_surface", 0))
            # Venus surface: kits and drops
            if job == "Venus surface":
                if venus in ("DIRECT", "FLY_UP", "BALLOON"):
                    if venus == "FLY_UP":
                        phases.append(("drop", kit_new.get("reactant", 0.0)))
                    if venus == "BALLOON":
                        phases.append(("drop", res.get("_balloon_drop", 0.0)))
                elif drop:
                    phases.append(("drop", res.get("_roverkit_drop", 0.0) + res.get("_float_drop", 0.0)))
            phases.append(("mark_liftoff", 0))
            phases.append(("burn", mr_asc))
            phases.append(("burn", math.exp(JR["rendezvous_km_s"] / vv)))
            # backward pass; per-trip kits ride only on the trip that uses them
            dry_j = dry
            if kits_per_trip and job == "Venus surface":
                dry_j += (kit["kept"] + kit["dropped"]) * (1 + S["growth_margin"])
            if trip_payload:
                dry_j += trip_payload.get(job, trip_payload.get("default", 0.0))
            m_end = dry_j - sum(p[1] for p in phases if p[0] == "drop")
            m = m_end
            marks = {}
            for kind, val in reversed(phases):
                if kind == "burn":
                    m *= val
                elif kind == "drop":
                    m += val
                else:
                    marks[kind] = m
            m_start = m
            need_p = m_start - dry_j
            if job in refuel and "mark_surface" in marks:
                # tanks topped up at the surface port: size the larger of the two legs
                dry_surf = dry - sum(p[1] for p in phases if p[0] == "drop")
                up = marks["mark_liftoff"] - dry_surf
                m_d = dry * (1 + REFUEL_RESERVE)
                passed = False
                for kind, val in reversed(phases):
                    if kind == "mark_surface":
                        passed = True
                        continue
                    if passed and kind == "burn":
                        m_d *= val
                    if passed and kind == "mark_entry":
                        marks["mark_entry"] = m_d
                down = m_d - dry
                need_p = max(up, down)
                m_start = dry + down
                marks["mark_liftoff"] = dry_surf + up
            if need_p > 20 * dry or not math.isfinite(need_p):
                ok, why = False, "propellant need runs away"
            jr[job] = {"ok": ok, "why": why, "prop_t": need_p, "start_t": m_start,
                       "liftoff_t": marks.get("mark_liftoff", m_start), "surface_t": marks.get("mark_surface", m_start),
                       "entry_t": marks.get("mark_entry"), "ascent_dv": A["dv_km_s"], "start": start}
            if ok:
                if marks.get("mark_entry"):
                    new_entry = max(new_entry, marks["mark_entry"])
                    res["_entry_mass_" + job] = marks["mark_entry"]
                new_land = max(new_land, marks.get("mark_surface", 0))
                # engine thrust needed (chemical): lift-off and landing at the site's ambient
                if not s:
                    pa0 = atm.state(site * 1e3 if job != "Venus surface" or venus not in ("FLY_UP", "BALLOON") else
                                    S["venus_strategies"][venus]["rocket_from_km"] * 1e3)[0]
                    f1 = sp.Chemical.f_vac_for(eng, pa0, JR["liftoff_tw"] * marks["mark_liftoff"] * 1e3 * max(G0, g_l))
                    f2 = sp.Chemical.f_vac_for(eng, atm.state(site * 1e3)[0], JR["landing_tw"] * marks["mark_surface"] * 1e3 * g_l) if atm.a is not None or True else 0
                    new_fvac_need = max(new_fvac_need, f1, f2 if math.isfinite(f2) else 0)
                # Venus kits sized from the surface mass
                if job == "Venus surface":
                    ms = marks["mark_surface"]
                    if venus == "FLY_UP":
                        fk = fan_kit(ms, disp, planform, E["fly_ld"], eng, (s or 0) * 1e3 * res.get("_wet", 40) * 1e3)
                        kit_new["kept"] += fk["fan_t"] + fk["power_t"]
                        kit_new["reactant"] = fk["reactant_t"]
                        kit_new["dropped"] += fk["reactant_t"]
                        if not fk["power_ok"]:
                            jr[job].update(ok=False, why="torchlet electric output below fan power")
                        venus_info["fans"] = fk
                    if venus == "BALLOON":
                        V = S["venus_strategies"]["BALLOON"]
                        lk = lift_kit(ms, disp, V["envelope_kg_m2"], margin=V["lift_margin"], dewar_frac=V["dewar_fraction"], rigging=V["rigging_t"])
                        res["_balloon_drop"] = lk["dropped_t"]
                        kit_new["kept"] += lk["dewar_t"]
                        kit_new["dropped"] += lk["dropped_t"]
                        kit_new["stow_m3"] += lk["envelope_t"] / 0.3 + lk["gas_t"] * 1e3 / 71 * 1.2
                        venus_info["balloon"] = lk
                    if drop:
                        V = S["venus_strategies"][venus]
                        r_mass = rover_t if rover == "VENUS" else (cabin_t + C["crew_and_kit_t"] + rover_t + (cab_hard["hull_t"] + cab_hard["insulation_t"]))
                        r_disp = (rover_dims[0] * rover_dims[1] * rover_dims[2] * 0.6) if rover_dims else ((math.pi / 6) * cab_hard["od_m"] ** 3 * 1.3)
                        rk = lift_kit(r_mass, r_disp, V["rover_envelope_kg_m2"], margin=V["lift_margin"], dewar_frac=V["dewar_fraction"])
                        res["_roverkit_drop"] = rk["dropped_t"]
                        kit_new["kept"] += rk["dewar_t"]
                        kit_new["dropped"] += rk["dropped_t"]
                        kit_new["stow_m3"] += rk["envelope_t"] / 0.3 + rk["gas_t"] * 1e3 / 71 * 1.2
                        venus_info["rover_balloon"] = rk
                        if venus == "DROP_FLOAT":
                            fk = lift_kit(ms - r_mass, disp, V["float_envelope_kg_m2"], margin=1.0, dewar_frac=V["dewar_fraction"],
                                          rigging=V["rigging_t"], at_surface=False)
                            res["_float_drop"] = fk["dropped_t"]
                            kit_new["kept"] += fk["dewar_t"]
                            kit_new["dropped"] += fk["dropped_t"]
                            kit_new["stow_m3"] += fk["envelope_t"] / 0.3 + fk["gas_t"] * 1e3 / 71 * 1.2
                            venus_info["float"] = fk
        okjobs = [j for j in jobs if jr[j]["ok"]]
        mp_new = max([jr[j]["prop_t"] for j in okjobs], default=0.0)
        wet = max([jr[j]["start_t"] for j in okjobs], default=dry)
        conv = abs(mp_new - m_p) < 1e-3 and abs(kit_new["dropped"] + kit_new["kept"] - kit["dropped"] - kit["kept"]) < 1e-3
        m_p = 0.5 * m_p + 0.5 * mp_new
        kit = kit_new
        entry_max, land_max, f_vac = new_entry, new_land, new_fvac_need
        res["_q_max"] = q_max
        res["_wet"] = wet
        res["_jr"] = jr
        if wet > 10 * S["design_caps"]["wet_t_max"]:
            for j in jr:
                if jr[j]["ok"]:
                    jr[j].update(ok=False, why="mass runs away (no closed design)")
            break
        if conv and it > 3:
            break
    # cabin heat sink on the Venus surface
    sink_note = None
    if cab_hard and lands_venus and jr.get("Venus surface", {}).get("ok"):
        heat_kw = cab_hard["leak_kw"] + H["internal_heat_kw_base"] + C["crew"] * H["internal_heat_kw_per_crew"]
        need_mj = heat_kw * 3600 * H["surface_stay_h"] / 1e3
        if s:
            water_t = jr["Venus surface"]["liftoff_t"] - dry
            cap_mj = water_t * 1e3 * 4.18e-3 * H["water_sink_max_rise_k"]
            sink_note = f"ascent water soaks up {need_mj:,.0f} MJ of {cap_mj:,.0f} MJ it can hold"
        else:
            sink_note = f"needs {need_mj / H['ice_sink_mj_per_kg'] / 1e3:.1f} t of ice"
    out = {"engine": eng, "entry": etype, "rover": rover, "venus": venus, "elong": elong, "dry_t": dry, "breakdown_t": breakdown, "prop_cap_t": m_p, "wet_t": res.get("_wet"),
           "dims_m": dims, "bay_m": bay, "beta_kg_m2": (entry_max * 1e3 / (E.get("cd", 1) * a_ref)) if E_KIND(etype) == "rigid" and entry_max else (E.get("beta_target") if E_KIND(etype) == "deployable" else None),
           "heat_load_j_cm2": res.get("_q_max"), "jobs": jr, "kit": kit, "venus_info": venus_info, "cabin_hardened": bool(cab_hard),
           "cab_hard": cab_hard, "venus_rover": rov, "sink_note": sink_note, "torch_gw": (s * res.get("_wet", 0) / 1e3) if s else None,
           "f_vac_kn": f_vac / 1e3 if not s else None, "notes": sorted(set(notes)), "iterations": it}
    return out


def evaluate(tab, eng, etype, rover, venus, refuel=(), elong=1.0):
    jobs = list(S["jobs"])
    single = {}
    for j in jobs:
        r = size_design(tab, eng, etype, rover, venus, [j], refuel=[j] if j in refuel else [], elong=elong)
        jj = r["jobs"][j]
        single[j] = jj["ok"] and r["wet_t"] is not None and r["wet_t"] <= S["design_caps"]["wet_t_max"]
        if jj["ok"] and not single[j]:
            r["jobs"][j]["why"] = f"needs a {r['wet_t']:.0f} t shuttle"
        single[j + "_why"] = r["jobs"][j].get("why", "") if not single[j] else ""
        single[j + "_wet"] = r["wet_t"] if jj["ok"] else None
    cover = [j for j in jobs if single[j]]
    full = size_design(tab, eng, etype, rover, venus, cover, refuel=[j for j in cover if j in refuel], elong=elong) if cover else None
    if full and full["wet_t"] > S["design_caps"]["wet_t_max"]:
        full["over_cap"] = True
    return {"key": f"{eng}|{etype}|{rover}|{venus}|e{elong}", "cover": cover, "single": single, "design": full}


def score(feasible):
    W = S["score"]["weights"]
    P = S["score"]["ops_penalties"]
    G = S["geometry"]
    cur_bay = G["current_bay_m"][0] * G["current_bay_m"][1] * G["current_bay_m"][2]
    wmin = min(f["design"]["wet_t"] for f in feasible)
    trl_v = {k: v.get("trl", 1.0) for k, v in S["venus_strategies"].items()}
    for f in feasible:
        d = f["design"]
        b = d["bay_m"]
        bay_vol = b[0] * b[1] * b[2]
        fits_slot = b[1] <= G["slot_max_cross_m"][0] and b[2] <= G["slot_max_cross_m"][1]
        bay_fit = min(1.0, G["current_bay_m"][0] / b[0]) * (1.0 if fits_slot else 0.4)
        eng_key = "TORCH" if d["engine"].startswith("TORCH") else d["engine"]
        trl = (S["propulsion"][eng_key]["trl"] * S["entry"][d["entry"]]["trl"] * trl_v[d["venus"]]) ** (1 / 3)
        ops = 1.0
        if eng_key in ("TORCH", "NTR"):
            ops -= P["plume_near_settlements"]
        if d["entry"] == "CAPSULE":
            ops -= P["ablative_refurbish"]
        if S["entry"][d["entry"]].get("kind") == "deployable":
            ops -= P["deployable_fabric"]
        if d["venus"] in ("BALLOON", "DROP_CITY", "DROP_FLOAT"):
            ops -= P["single_use_envelope"]
        if d["venus"] == "DROP_CITY":
            ops -= P["needs_cloud_city"]
        if d["venus"].startswith("DROP") and d["rover"] == "VENUS":
            ops -= P["only_two_reach_venus_surface"]
        parts = {"wet_mass": wmin / d["wet_t"], "bay_fit": bay_fit, "maturity": trl, "operations": max(0.0, ops)}
        f["score"] = sum(W[k] * parts[k] for k in W)
        f["score_parts"] = parts
        f["fits_slot"] = fits_slot


def rnd(o):
    if isinstance(o, float):
        return round(o, 4)
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, list):
        return [rnd(v) for v in o]
    return o


def run(tab, refuel, label):
    combos = [c for c in itertools.product(ENGINES, [k for k, v in S["entry"].items() if isinstance(v, dict)],
                                           list(S["rovers"]), list(S["venus_strategies"]), S["geometry"]["elongation_options"])]
    out = [evaluate(tab, *c[:4], refuel=refuel, elong=c[4]) for c in combos]
    jobs = list(S["jobs"])
    feasible = [o for o in out if o["design"] and set(o["cover"]) == set(jobs) and o["design"]["entry"] != "PROPULSIVE"
                and not o["design"].get("over_cap")]
    if feasible:
        score(feasible)
        feasible.sort(key=lambda f: -f["score"])
    summary = {}
    for o in out:
        e = o["key"].split("|")[0]
        n = len(o["cover"])
        w = o["design"]["wet_t"] if o["design"] else 1e9
        cur = summary.get(e)
        if o["design"] and o["design"]["entry"] == "PROPULSIVE":
            continue
        if cur is None or (n, -w) > (len(cur["cover"]), -cur["wet"]):
            summary[e] = {"cover": o["cover"], "wet": w, "key": o["key"],
                          "missing": {j: o["single"][j + "_why"] for j in jobs if j not in o["cover"]}}
    print(f"\n== {label}: {len(out)} designs, {len(feasible)} close all nine jobs with a heat shield and <= {S['design_caps']['wet_t_max']} t")
    for e, v in summary.items():
        print(f"  {e:10s} best covers {len(v['cover'])}/9  {v['key']:42s} wet {v['wet']:.1f} t   missing: {v['missing']}")
    for f in feasible[:15]:
        d = f["design"]
        print(f"  {f['score']:.3f}  {f['key']:42s} wet {d['wet_t']:6.1f} dry {d['dry_t']:5.1f}  {d['dims_m'][0]:.1f}x{d['dims_m'][1]:.1f}x{d['dims_m'][2]:.1f} m  "
              + " ".join(f"{k}={v:.2f}" for k, v in f["score_parts"].items()))
    return {"label": label, "refuel": list(refuel), "n_designs": len(out), "n_feasible": len(feasible),
            "feasible": [rnd(f) for f in feasible], "engine_summary": rnd(summary),
            "all": [rnd({"key": o["key"], "cover": o["cover"], "wet": o["design"]["wet_t"] if o["design"] else None,
                         "single_wet": {j: o["single"][j + "_wet"] for j in jobs},
                         "missing": {j: o["single"][j + "_why"] for j in jobs if j not in o["cover"]}}) for o in out]}


if __name__ == "__main__":
    if "--rebuild" in sys.argv or not TABLES.exists():
        tab = build_tables()
    else:
        tab = json.loads(TABLES.read_text())
    res = {"header": S["header"], "status": S["status"],
           "expedition": run(tab, (), "EXPEDITION (everything carried from orbit)"),
           "port": run(tab, tuple(S["refuel_ports"]["jobs"]), "PORT RUNS (tanks topped up at settled ports; Venus surface still unsupported)")}
    (HERE / "shuttle_results.json").write_text(json.dumps(res, indent=1))
