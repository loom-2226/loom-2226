"""Shuttle requirement costs and checks v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Uses shuttle_search.py and its cached tables.
1. what each requirement costs: lightest closing design per requirement set
2. Venus strategies and heat shields side by side for the chosen engine
3. re-flies the winner's hardest ascents at its own mass and shape
4. sensitivity of the winner to the softest authored numbers
Writes shuttle_checks.json."""
import json, math, copy, itertools
from pathlib import Path
import shuttle_search as ss
import shuttle_physics as sp

HERE = Path(__file__).resolve().parent
S = ss.S
tab = json.loads(ss.TABLES.read_text())
JOBS = list(S["jobs"])
ENTRIES = [k for k, v in S["entry"].items() if isinstance(v, dict) and k != "PROPULSIVE"]
CAP = S["design_caps"]["wet_t_max"]


def best_for(required, refuel=(), engines=None, entries=None, rovers=None, venus=None):
    best = None
    for c in itertools.product(engines or ss.ENGINES, entries or ENTRIES, rovers or list(S["rovers"]), venus or list(S["venus_strategies"]),
                               S["geometry"]["elongation_options"]):
        if "Venus surface" not in required and c[3] != "NONE":
            continue
        if "Venus surface" in required and c[3] == "NONE":
            continue
        if "Venus surface" not in required and c[2] in ("VENUS", "CABIN_DRIVE"):
            pass
        d = ss.size_design(tab, *c[:4], list(required), refuel=[j for j in required if j in refuel], elong=c[4])
        if not all(d["jobs"][j]["ok"] for j in required) or d["wet_t"] > CAP:
            continue
        if best is None or d["wet_t"] < best["wet_t"]:
            best = d
    return best


def brief(d):
    if d is None:
        return None
    return {"key": f"{d['engine']}|{d['entry']}|{d['rover']}|{d['venus']}|e{d['elong']}", "wet_t": round(d["wet_t"], 1), "dry_t": round(d["dry_t"], 1),
            "prop_t": round(d["prop_cap_t"], 1), "dims_m": [round(x, 1) for x in d["dims_m"]], "bay_m": [round(x, 1) for x in d["bay_m"]],
            "torch_gw": round(d["torch_gw"], 1) if d["torch_gw"] else None}


if __name__ == "__main__":
    out = {"header": S["header"]}
    airless = ["Moon", "Mercury", "Ceres", "Callisto"]
    sets = {
        "all nine": JOBS,
        "all but Earth surface": [j for j in JOBS if j != "Earth"],
        "all but Venus surface": [j for j in JOBS if j != "Venus surface"],
        "all but Earth and Venus surface": [j for j in JOBS if j not in ("Earth", "Venus surface")],
        "airless + Mars + Titan": airless + ["Mars", "Titan"],
        "airless only": airless,
    }
    req = {}
    for name, js in sets.items():
        exp = best_for(js)
        port = best_for(js, refuel=S["refuel_ports"]["jobs"])
        chem = best_for(js, refuel=S["refuel_ports"]["jobs"], engines=["METHALOX", "HYDROLOX"])
        req[name] = {"expedition": brief(exp), "port": brief(port), "chemical_port": brief(chem)}
        print(f"{name:34s} expedition {brief(exp)}\n{'':34s} port       {brief(port)}\n{'':34s} chem+port  {brief(chem)}")
    out["requirements"] = req

    # Venus strategies with the winner's engine and shield, Venus surface job alone
    W = ("TORCH100", "DEPLOYABLE_800", "VENUS", "DROP_CITY")
    WE = 1.25
    ven = {}
    for v in ["DIRECT", "FLY_UP", "BALLOON", "DROP_CITY", "DROP_FLOAT"]:
        rov = "CABIN_DRIVE" if v in ("DIRECT", "FLY_UP", "BALLOON") else "VENUS"
        rows = {}
        for eng in ["TORCH100", "TORCH200"]:
            d = ss.size_design(tab, eng, "DEPLOYABLE_800", rov, v, ["Venus surface"], elong=WE)
            j = d["jobs"]["Venus surface"]
            rows[eng] = {"ok": j["ok"] and d["wet_t"] <= CAP, "wet_t": round(d["wet_t"], 1), "why": j.get("why") or ("over cap" if d["wet_t"] > CAP else ""),
                         "kits": {k: {kk: round(vv, 2) for kk, vv in val.items() if isinstance(vv, (int, float))} for k, val in d["venus_info"].items()}}
        ven[v] = rows
        print("Venus", v, rows)
    out["venus_strategies"] = ven
    fans = {}
    for label, ld, planform in (("no wings (umbrella body)", 1.0, 14.9 * 4.3 * 0.8), ("lifting-body wings", 4.0, 14.9 * 4.3 * 0.85)):
        fk = ss.fan_kit(70.0, 14.9 * 4.3 * 3.5 * 0.55, planform, ld, "TORCH100", 7e9)
        fans[label] = {"peak_mw": round(fk["peak_mw"], 1), "fan_t": round(fk["fan_t"], 1), "share_of_70t": round(fk["fan_t"] / 70, 2), "energy_gj": round(fk["energy_gj"])}
    out["fly_up_fans_at_70t"] = fans
    print("fans at 70 t", fans)

    # heat shields with the winner's engine, rover and Venus plan, all nine jobs
    shields = {}
    for e in ENTRIES:
        d = min((ss.size_design(tab, "TORCH100", e, "VENUS", "DROP_CITY", JOBS, elong=x) for x in S["geometry"]["elongation_options"]),
                key=lambda q: q["wet_t"] + (0 if all(q["jobs"][j]["ok"] for j in JOBS) else 1e6))
        okall = all(d["jobs"][j]["ok"] for j in JOBS) and d["wet_t"] <= CAP
        b = d["breakdown_t"]
        mars = d["jobs"]["Mars"]
        shields[e] = {"ok": okall, "wet_t": round(d["wet_t"], 1), "shield_t": round(b["heat_shield"], 2), "aero_t": round(b["aero_surfaces"], 2),
                      "beta": round(d["beta_kg_m2"]) if d["beta_kg_m2"] else None, "dims_m": [round(x, 1) for x in d["dims_m"]]}
        for body in ("Earth", "Venus", "Mars"):
            beta = d["beta_kg_m2"] or 1000
            en = ss.lerp_entry(tab, body, e, beta)
            shields[e][body] = {"heat_load_j_cm2": round(en["heat_load_j_cm2"]), "q_peak_w_cm2": round(en["q_peak_w_cm2"], 1),
                                "g_peak": round(en["g_peak"], 2), "landing_speed_m_s": round(en["v_at_stop_m_s"])}
        if S["entry"][e]["kind"] == "deployable":
            area = (d["jobs"]["Earth"]["entry_t"] or d["wet_t"]) * 1e3 / (S["entry"][e]["cd"] * S["entry"][e]["beta_target"])
            shields[e]["umbrella_d_m"] = round(math.sqrt(4 * area / math.pi), 1)
        print("shield", e, shields[e])
    out["heat_shields"] = shields

    # the winner, in full
    win = ss.size_design(tab, *W, JOBS, elong=WE)
    out["winner"] = ss.rnd(win)
    print("winner", brief(win), {k: round(v, 2) for k, v in win["breakdown_t"].items()})

    # re-fly: hardest ascents at the winner's own mass and cross-section
    L, Wd, H = win["dims_m"]
    refly = {}
    for job in ("Earth", "Venus clouds", "Mercury", "Mars"):
        jj = win["jobs"][job]
        m0 = jj["liftoff_t"] * 1e3
        P = 100 * 1e3 * win["wet_t"] * 1e3
        start = ss.STARTS[jj["start"]]
        r = sp.best_ascent(start[0], lambda: sp.Torch(P), m0, start_km=start[1], v0=start[2], front_m2=Wd * H * 0.8,
                           vol_m3=L * Wd * H * 0.55, t_max=20000)
        t_mr = tab["ascent"][jj["start"]]["TORCH100"]["mass_ratio"]
        refly[job] = {"table_mass_ratio": round(t_mr, 3), "own_mass_ratio": round(r["mass_ratio"], 3) if r else None,
                      "own_dv_km_s": round(r["dv_km_s"], 2) if r else None, "liftoff_t": round(m0 / 1e3, 1)}
        print("refly", job, refly[job])
    out["refly"] = refly

    # sensitivity: rebuild with one authored number changed
    sens = {}
    base_space = copy.deepcopy(S)
    tests = [("torchlet 0.5 GW per tonne", ("propulsion", "TORCH", "gw_per_t"), 0.5),
             ("torchlet 2 GW per tonne", ("propulsion", "TORCH", "gw_per_t"), 2.0),
             ("heat shield 50% heavier per m2", ("tps_model", "areal_coeff"), 0.1365 * 1.5),
             ("umbrella ribs 15 kg/m2", ("tps_model", "deployable", "rib_kg_m2"), 15.0),
             ("growth margin 25%", ("growth_margin",), 0.25),
             ("rover sortie 48 h", ("hardening", "sortie_h_drop"), 48),
             ("4 crew instead of 6", ("cabin", "crew"), 4)]
    for name, path, val in tests:
        node = S
        for p in path[:-1]:
            node = node[p]
        old = node[path[-1]]
        node[path[-1]] = val
        d = ss.size_design(tab, *W, JOBS, elong=WE)
        ok = all(d["jobs"][j]["ok"] for j in JOBS)
        sens[name] = {"wet_t": round(d["wet_t"], 1), "closes": ok}
        node[path[-1]] = old
        print("sens", name, sens[name])
    out["sensitivity"] = sens
    (HERE / "shuttle_checks.json").write_text(json.dumps(out, indent=1))
