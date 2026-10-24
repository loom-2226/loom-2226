"""Deployable UAV design search v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Reads uav_space.json. Sweeps airframe, gross mass,
battery share and power source; flies each design on Mars, Titan, the Venus
cloud deck and Earth against four roles; sizes a drop pod for release from
Wayfarer; and prices carrying it in the shuttle. Writes uav_results.json."""
import json, math, itertools, copy, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
U = json.loads((HERE / "uav_space.json").read_text())
G0 = 9.80665
W = U["worlds"]


def design(air, m, fb, popt, U=U, dl=1e9):
    R, Wg, M, P = U["rotor"], U["wing"], U["mass"], U["power"]
    W = U["worlds"]
    # rotor disc sized on the world where weight per unit of rotor thrust is worst (Mars when it is in the set)
    def dlmax(w):
        return w["rho"] * (R["tip_mach"] * w["sound_m_s"]) ** 2 * R["solidity"] * R["ct_over_sigma"]
    A = max(m * w["g"] / min(dl, R["disk_loading_use"] * dlmax(w)) for w in W.values())
    S = 0.0
    if air == "HYBRID":
        thin = min(W.values(), key=lambda w: w["rho"] / w["g"])
        S = 2 * m * thin["g"] / (thin["rho"] * Wg["mars_cruise_m_s"] ** 2 * Wg["cl"])
    perf = {}
    for k, w in W.items():
        wt = m * w["g"]
        ph = wt ** 1.5 / math.sqrt(2 * w["rho"] * A) / w["fm"] + M["idle_w"]
        v_r = w["rotor_cruise_m_s"]
        e_km_rotor = R["cruise_power_fraction"] * ph / v_r * 1000 / 3600  # Wh per km
        p_loiter = ph
        e_km, v, mode = e_km_rotor, v_r, "rotor"
        v_hold = v_r
        if S:
            v_min = math.sqrt(2 * wt / (w["rho"] * S * Wg["cl"]))
            v_w = max(1.3 * v_min, v_r)
            e_km_wing = wt / (Wg["ld"][k] * Wg["prop_eff"]) * 1000 / 3600 + M["idle_w"] / v_w * 1000 / 3600
            if e_km_wing < e_km_rotor:
                e_km, v, mode = e_km_wing, v_w, "wing"
            p_loiter = min(ph, Wg["loiter_power_fraction"] * wt * 1.3 * v_min / (Wg["ld"][k] * Wg["prop_eff"]) + M["idle_w"])
            v_hold = max(v_r, 2.5 * v_min)
        perf[k] = {"hover_w": ph, "wh_per_km": e_km, "cruise_m_s": v, "mode": mode, "loiter_w": p_loiter, "top_speed_m_s": v_hold}
    p_peak = 1.3 * max(p["hover_w"] for p in perf.values())
    motors = p_peak / (M["motor_kw_per_kg"] * 1e3)
    rotor = R["kg_per_m2_disc"] * A
    wing = Wg["kg_per_m2"] * S
    bat = fb * m
    E = bat * P["battery_wh_per_kg"] * P["battery_usable"]
    # one survey day: 20 km plus two take-offs, plus standby
    sv = U["roles"]["survey"]
    e_day = {k: p["wh_per_km"] * sv["km_per_day"] + 2 * p["hover_w"] * 60 / 3600 + M["idle_w"] * 24 for k, p in perf.items()}
    rps = solar_m2 = beam = 0.0
    if "RPS" in popt:
        rps = max(e_day.values()) / 24 / P["rps_w_per_kg"]
    if "SOLAR" in popt:
        need = {k: e_day[k] / (W[k]["insolation_wh_m2_day"] * P["solar_eff"]) for k in W}
        solar_m2 = min(P["solar_max_m2"], max(need.values()))
    if "BEAM" in popt:
        beam = max(perf[k]["hover_w"] for k in W if W[k]["beam_ok"]) / (P["beam_receiver_kw_per_kg"] * 1e3)
    solar = solar_m2 * P["solar_kg_per_m2"]
    thermal = max(w["thermal_fraction"] for w in W.values()) * m
    fixed = M["avionics_kg"] + M["avionics_fraction"] * m + M["sensor_kit_kg"]
    struct = M["structure_fraction"] * m
    parts = {"rotors": rotor, "motors": motors, "wing": wing, "battery": bat, "rps": rps, "solar": solar, "beam_receiver": beam,
             "thermal": thermal, "avionics_sensors": fixed, "structure": struct}
    empty = sum(parts.values()) * (1 + M["growth_margin"])
    payload = m - empty
    roles = {}
    rq = U["roles"]
    for k, p in perf.items():
        rng = E / p["wh_per_km"]
        hours = E / p["loiter_w"]
        beam_here = "BEAM" in popt and W[k]["beam_ok"]
        sustain = False
        if rps:
            sustain = rps * P["rps_w_per_kg"] * 24 >= e_day[k] * 0.999
        if solar_m2:
            sustain = sustain or solar_m2 * W[k]["insolation_wh_m2_day"] * P["solar_eff"] >= e_day[k] * 0.999
        day_flight = p["wh_per_km"] * sv["km_per_day"] + 2 * p["hover_w"] * 60 / 3600
        roles[k] = {
            "scout": rng >= rq["scout"]["range_km"],
            "overwatch": hours >= rq["overwatch"]["hours"] or beam_here,
            "fetch": payload >= rq["fetch"]["payload_kg"] and rng >= rq["fetch"]["range_km"],
            "survey": sustain and E >= day_flight,
            "range_km": rng, "hours": hours, "beam": beam_here, "holds_60_m_s": p["top_speed_m_s"] >= 60,
        }
    # three coaxial pairs on folding arms (Y6); blades fold back along the arms
    d_rot = math.sqrt(4 * A / 3 / math.pi)
    stow = [d_rot * U["rotor"]["fold_factor"] + 0.6, d_rot * U["rotor"]["fold_factor"] + 0.3, 0.35 + 0.08 * m ** (1 / 3)]
    if S:
        span = math.sqrt(S * 8)
        stow[0] = max(stow[0], span / 3 + 0.3)
        stow[2] += 0.15
    fits = all(a <= b for a, b in zip(sorted(stow, reverse=True), sorted(U["stowage"]["max_m"], reverse=True)))
    return {"airframe": air, "mass_kg": m, "battery_fraction": fb, "power": popt, "disc_m2": A, "rotor_d_m": d_rot, "wing_m2": S,
            "wing_span_m": math.sqrt(S * 8) if S else 0, "battery_wh": E, "rps_w": rps * P["rps_w_per_kg"], "solar_m2": solar_m2,
            "payload_kg": payload, "parts": parts, "empty_kg": empty, "perf": perf, "roles": roles, "stow_m": stow, "fits_shuttle": fits,
            "e_day_wh": e_day}


def drop_pod(m, U=U, jetpack=True, min_d=0.0):
    D = dict(U["drop_pod"])
    if not jetpack:
        D["mars_jetpack_ratio"] = 0.0
    pod = 0.0
    for _ in range(40):
        entry = m + pod
        area = max(entry / (D["cd"] * D["beta_target"]), math.pi * min_d ** 2 / 4)
        umb = D["umbrella_kg_m2"] * area
        jet = D["mars_jetpack_ratio"] * m
        chute = D["chute_fraction"] * m
        dry = umb + D["structure_fraction"] * m + jet + chute
        kick = (m + dry) * (math.exp(D["deorbit_km_s"] * 1e3 / (D["kick_isp_s"] * G0)) - 1)
        new = dry + kick
        if abs(new - pod) < 1e-6:
            break
        pod = new
    return {"pod_kg": pod, "entry_kg": m + pod, "umbrella_d_m": math.sqrt(4 * area / math.pi), "jetpack_kg": jet,
            "per_slot": int(D["wayfarer_slot_t"] * 1e3 // (m + pod))}


def feasible(d, need_stow=True):
    return d["payload_kg"] >= U["roles"]["fetch"]["payload_kg"] and (d["fits_shuttle"] or not need_stow) and \
        all(all(r[x] for x in ("scout", "overwatch", "fetch", "survey")) for r in d["roles"].values())


def search(U_=U):
    out = []
    masses = list(range(15, 60, 5)) + list(range(60, 200, 10)) + list(range(200, 420, 20))
    for air, m, fb, po, dl in itertools.product(U_["airframes"], masses, [0.08, 0.1, 0.12, 0.15, 0.18, 0.2, 0.25, 0.3, 0.35],
                                                U_["power_options"], [15, 25, 40, 70, 120, 250, 1e9]):
        d = design(air, m, fb, po, U_, dl)
        d["disk_loading_cap"] = dl
        d["ok"] = feasible(d)
        d["ok_any_stow"] = feasible(d, False)
        out.append(d)
    return out


def shuttle_growth():
    """tonnes of shuttle per tonne carried, both Venus plans, by finite difference"""
    try:
        import shuttle_search as ss
    except Exception:
        return None
    tab = json.loads(ss.TABLES.read_text())
    J = list(ss.S["jobs"])
    res = {}
    for name, key, el in (("rover drop (70 t)", ("TORCH100", "DEPLOYABLE_800", "VENUS", "DROP_CITY"), 1.25),
                          ("shuttle lands (balloon)", ("TORCH100", "DEPLOYABLE_800", "CABIN_DRIVE", "BALLOON"), 1.0)):
        base = ss.size_design(tab, *key, J, elong=el)["wet_t"]
        ss.S["systems_t"] += 0.2
        plus = ss.size_design(tab, *key, J, elong=el)["wet_t"]
        ss.S["systems_t"] -= 0.2
        res[name] = {"base_t": base, "t_per_t": (plus - base) / 0.2}
    return res


def rnd(o):
    if isinstance(o, float):
        return round(o, 3)
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, list):
        return [rnd(v) for v in o]
    return o


if __name__ == "__main__":
    allx = search()
    ok = [d for d in allx if d["ok"]]
    growth = shuttle_growth()
    gf = growth["rover drop (70 t)"]["t_per_t"] if growth else 2.0
    mat = U["score"]["maturity"]
    for d in ok:
        d["pod"] = drop_pod(d["mass_kg"])
        tr = mat[d["airframe"]] * min(mat[p] for p in d["power"].split("+"))
        d["score"] = 0
        d["_trl"] = tr
    if ok:
        mmin = min(d["mass_kg"] for d in ok)
        for d in ok:
            d["score"] = (U["score"]["weights"]["mass"] * mmin / d["mass_kg"] + U["score"]["weights"]["shuttle_growth"] * mmin / d["mass_kg"]
                          + U["score"]["weights"]["margin"] * min(1, d["payload_kg"] / 15) + U["score"]["weights"]["maturity"] * d["_trl"])
        ok.sort(key=lambda d: -d["score"])
    print(f"{len(allx)} designs, {len(ok)} do all four jobs on all four worlds and fit the shuttle")
    best_by = {}
    for d in ok:
        k = (d["airframe"], d["power"])
        if k not in best_by or d["mass_kg"] < best_by[k]["mass_kg"]:
            best_by[k] = d
    for k, d in sorted(best_by.items(), key=lambda kv: kv[1]["mass_kg"]):
        print(f"  {k[0]:7s} {k[1]:15s} {d['mass_kg']:4d} kg  bat {d['battery_fraction']:.2f}  rotor d {d['rotor_d_m']:.2f} m x6  "
              f"payload {d['payload_kg']:.1f} kg  pod {d['pod']['entry_kg']:.0f} kg  score {d['score']:.3f}")
    # why the cheap ones fail
    fails = {}
    for d in allx:
        if d["ok"]:
            continue
        for k, r in d["roles"].items():
            for x in ("scout", "overwatch", "fetch", "survey"):
                if not r[x]:
                    fails[(d["power"], k, x)] = fails.get((d["power"], k, x), 0) + 1
    win = ok[0] if ok else None
    if win:
        print("WINNER", win["airframe"], win["power"], win["mass_kg"], "kg", {k: round(v, 1) for k, v in win["parts"].items()})
        for k, r in win["roles"].items():
            p = win["perf"][k]
            print(f"   {k:12s} range {r['range_km']:6.0f} km  on-station {r['hours']:5.1f} h  hover {p['hover_w'] / 1e3:5.1f} kW  cruise {p['cruise_m_s']:.0f} m/s ({p['mode']})  beam {r['beam']}  holds 60 m/s {r['holds_60_m_s']}")
        print("   pod", {k: round(v, 1) if isinstance(v, float) else v for k, v in win["pod"].items()}, "stow", [round(x, 2) for x in win["stow_m"]])
    print("growth", growth)
    # sensitivity on the winner's family
    sens = {}
    if win:
        for name, path, val in (("2026 batteries 300 Wh/kg", ("power", "battery_wh_per_kg"), 300),
                                ("today's RTG 2.5 W/kg", ("power", "rps_w_per_kg"), 2.5),
                                ("Mars air 0.012 kg/m3 (high site)", ("worlds", "Mars", "rho"), 0.012)):
            U2 = copy.deepcopy(U)
            node = U2
            for p in path[:-1]:
                node = node[p]
            node[path[-1]] = val
            best = None
            for d in search(U2):
                if d["ok"] and d["airframe"] == win["airframe"] and d["power"] == win["power"]:
                    if best is None or d["mass_kg"] < best["mass_kg"]:
                        best = d
            sens[name] = best["mass_kg"] if best else None
            print("sens", name, sens[name])
    res = {"header": U["header"], "status": U["status"], "n": len(allx), "n_ok": len(ok),
           "best_by_family": [rnd({k: v for k, v in d.items() if not k.startswith("_")}) for d in best_by.values()],
           "winner": rnd({k: v for k, v in win.items() if not k.startswith("_")}) if win else None,
           "shuttle_growth": growth, "sensitivity": sens,
           "fail_counts": {"|".join(k): v for k, v in sorted(fails.items(), key=lambda kv: -kv[1])[:30]}}
    (HERE / "uav_results.json").write_text(json.dumps(res, indent=1))
