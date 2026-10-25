"""Wayfarer G10 v0.2: basic flight dynamics of RCS, torch, Metric and Loom -- ALL bodies. ALL sponsors. 2026-2226.

NON-GOVERNING engineering tests (class:engineering). They do not fly missions and produce no canon flight outputs.
Built on existing LOOM code (main 19377b85; see G10_SOURCE_MAP.md), fed with the Wayfarer v0.5.7 card:
  src/wayfarer_rcs_closed_loop_gnc.py           quaternion PD controller, gains and gates (reused as is)
  src/wayfarer_rcs_time_domain_mount_coupling   translation response law and test velocities (reused constants)
  src/wayfarer_torch_mode_cards.py              exact torch working card: mdot and ve per mode (reused as is)
  src/wayfarer_e1_metric_frontier_closure.py    metric ramp times, cold loads, electrical demand, operating rules
New here (the gaps in the source map): card loader and conformance, RCS authority from the ship's thruster layout,
time-stepped torch burn with a crew g cap and centre-of-mass migration, Metric and Loom mode sequences.
Canon limits kept: no metric delta-v or remass (CANON II s20), no Loom domain-fit claim (PR #356 indeterminate).
Usage, from the repository root:  python design/wayfarer/v0.5.7/g10/g10_flight_dynamics.py"""
import json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REV = HERE.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REV))

import src.wayfarer_rcs_closed_loop_gnc as GNC
import src.wayfarer_rcs_time_domain_mount_coupling as COUP
import src.wayfarer_torch_mode_cards as TORCH
import src.wayfarer_e1_metric_frontier_closure as METRIC
import certify as CT                                   # rev 6 thruster layout and couple search (the code G3 uses)

G0 = 9.80665
I, C, G = CT.load()
CARD = json.loads((REV / "out/wayfarer_v05_card.json").read_text())
STATES = list(CARD["states"])

MISALIGN_DEG = 0.5            # ENGINEERING_ASSUMPTION (structure review A): torch thrust-vector error; not a demonstrated disturbance history
SEGMENT_MAX_MIN = 165.0       # longest continuous burn before a coast break ([V2 6113])
COAST_MIN = 15.0              # ENGINEERING_ASSUMPTION: length of each coast break (free space: changes elapsed time, not delta-v)
CREW_G = CARD["torch"]["accel_cap_g"]
STRUCT_G = C["G5"]["design_g"]
RESERVE_T = CARD["dispatch_q7"]["protected_optimizer_reserve_t"]
P_CEIL = CARD["torch"]["jet_power_ceiling_tw"] * 1e12      # heat-rejection ceiling on jet power
TVC_DEG = CARD["torch"].get("tvc_authority_deg") or 0.0


def torch_force(mode, mass_kg, cap_g=CREW_G):
    """thrust this ship runs: working card mdot ve, held to the jet-power ceiling and the g cap."""
    mdot, ve, F, _ = (float(x) for x in TORCH.mode_outputs(mode))
    return min(F, 2 * P_CEIL / ve, cap_g * G0 * mass_kg), ve
SOURCES = {"main_commit": "19377b854c529e74afc61202d9eb2e780c5b4884",
           "rcs_controller": "src/wayfarer_rcs_closed_loop_gnc.py:_torque_command, gains and gates",
           "translation_law": "src/wayfarer_rcs_time_domain_mount_coupling.py:TRANSLATION_RESPONSE_RATE_S_INV, VELOCITY_GATE_M_S, _CASES",
           "torch_card": "src/wayfarer_torch_mode_cards.py:MODE_CARDS, mode_outputs",
           "metric_card": "src/wayfarer_e1_metric_frontier_closure.py:build_metric_closure",
           "ship_card": "design/wayfarer/v0.5.7/out/wayfarer_v05_card.json"}


def chk(name, value, limit, ok, unit="", note=""):
    return {"name": name, "value": value, "limit": limit, "pass": bool(ok), "unit": unit, "note": note}


# ------------------------------------------------------------------ C. card conformance (new: the card loader)
def card_conformance():
    cs = []
    import hashlib
    sha = hashlib.sha256((REV / "out/wayfarer_v05_geometry.json").read_bytes()).hexdigest()
    cs.append(chk("card names the geometry it was made from", CARD["geometry_sha256"][:12], sha[:12], CARD["geometry_sha256"] == sha))
    worst = 0.0
    for s in STATES:
        cst, gst = CARD["states"][s], G["states"][s]
        worst = max(worst, abs(cst["mass_t"] - gst["mass_t"]), max(abs(a - b) for a, b in zip(cst["cg_m"], gst["cg_m"])),
                    max(abs(cst["inertia_tensor_kg_m2"][i][j] - gst["inertia_kg_m2"][i][j]) / gst["inertia_kg_m2"][i][i] for i in range(3) for j in range(3)))
    cs.append(chk("card mass, CG and inertia match the geometry in every state", round(worst, 6), 0.01, worst <= 0.01, "max abs / rel"))
    rows, worst_t = [], 0.0
    for m in TORCH.MODE_CARDS:
        mdot, ve, F, P = (float(x) for x in TORCH.mode_outputs(m))
        cf = CARD["torch"]["card_thrust_mn_by_mode"][m]
        d = (cf - F / 1e6) / (F / 1e6)
        worst_t = max(worst_t, abs(d))
        rows.append({"mode": m, "ve_km_s": ve / 1e3, "card_ve_km_s": CARD["torch"]["ve_km_s"][m], "mdot_kg_s": round(mdot, 4),
                     "working_card_thrust_mn": round(F / 1e6, 3), "ship_card_thrust_mn": cf, "diff_pct": round(100 * d, 1), "working_card_jet_power_tw": round(P / 1e12, 3),
                     "ship_available_thrust_mn": CARD["torch"]["thrust_mn_by_mode"][m]})
    ve_ok = all(abs(r["ve_km_s"] - r["card_ve_km_s"]) < 1e-9 for r in rows)
    cs.append(chk("torch exhaust velocities match the working card (src/wayfarer_torch_mode_cards.py)", "all" if ve_ok else "differ", "all", ve_ok))
    cs.append(chk("torch thrust by mode: ship card carries the working card (kT 2026-10-26: the working card governs)", round(100 * worst_t, 3), 1.0, worst_t <= 0.01, "% worst"))
    held = [r["mode"] for r in rows if r["ship_available_thrust_mn"] < r["working_card_thrust_mn"] - 1e-3]
    over = [r["mode"] for r in rows if 0.5 * r["ship_available_thrust_mn"] * 1e6 * r["ve_km_s"] * 1e3 > P_CEIL * 1.0001]
    cs.append(chk("torch: the ship runs no mode above its heat-rejection ceiling", len(over), 0, not over, "modes over",
                  f"ceiling {P_CEIL / 1e12:.3f} TW; held below the working card: " + (", ".join(held) or "none")))
    return cs, rows


# ------------------------------------------------------------------ R. RCS (reuses the main controller)
TH = CT.thrusters(I, G)


def rcs_limits(state, thrusters=None, n=None):
    """Axis torque authority (roll, pitch, yaw) about the state's CG: weaker of the two signs, n couples (G3's rule)."""
    cps = CT.couples(thrusters or TH, G["states"][state]["cg_m"])
    n = n or C["G3"]["couples_for_slew"]
    lim = []
    for a in range(3):
        lim.append(min(CT.axis_torque(cps, a, sg, n)[0] for sg in (1, -1)))
    return {"roll": lim[0], "pitch": lim[1], "yaw": lim[2]}


def slew(state, axis, angle_deg, limits):
    """main's simulate_axis_slew loop, with the ship's inertia tensor and torque authority."""
    tensor = CARD["states"][state]["inertia_tensor_kg_m2"]
    inv_i = GNC._inv3(tensor)
    tq = GNC._axis_angle_q(GNC._AXIS_INDEX[axis], math.radians(angle_deg))
    q, w, t, gate, peak = [1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 0.0, 0.0, 0.0
    lim = [limits["roll"], limits["pitch"], limits["yaw"]]
    if min(lim) <= 0:
        return {"duration_s": None, "pass": False}
    while t < GNC.MAX_TIME_S:
        torque, raw = GNC._torque_command(tensor, q, tq, w, limits)
        peak = max(peak, max(abs(torque[j]) / lim[j] for j in range(3)))
        iw = GNC._matvec(tensor, w)
        a = GNC._matvec(inv_i, [torque[j] - GNC._cross(w, iw)[j] for j in range(3)])
        w = [w[j] + a[j] * GNC.DT_S for j in range(3)]
        qd = GNC._qmul(q, [0.0, *w])
        q = GNC._qnorm([q[j] + 0.5 * qd[j] * GNC.DT_S for j in range(4)])
        t += GNC.DT_S
        err, rate = GNC._attitude_error_deg(q, tq), math.degrees(math.sqrt(GNC._dot(w, w)))
        if err <= GNC.ATTITUDE_GATE_DEG and rate <= GNC.RATE_GATE_DEG_S:
            gate += GNC.DT_S
            if gate + 1e-12 >= GNC.HOLD_TIME_S:
                break
        else:
            gate = 0.0
    ok = gate + 1e-12 >= GNC.HOLD_TIME_S and peak <= 1.0 + 1e-9
    return {"duration_s": round(t, 1), "pass": ok}


def rcs_tests():
    cs, rows = [], []
    worst = {}
    for s in STATES:
        lim = rcs_limits(s)
        for ax in ("roll", "pitch", "yaw"):
            r = slew(s, ax, 180.0, lim)
            rows.append({"state": s, "axis": ax, "torque_mnm": round(lim[ax] / 1e6, 3), **r})
            if ax not in worst or not r["pass"] or (r["duration_s"] or 1e9) > (worst[ax]["duration_s"] or 0):
                if ax not in worst or worst[ax]["pass"]:
                    worst[ax] = {"state": s, **r}
    for ax in ("roll", "pitch", "yaw"):
        w = worst[ax]
        cs.append(chk(f"RCS 180 deg {ax} slew settles (main controller gates, {GNC.MAX_TIME_S:.0f} s budget), worst state", w["duration_s"], GNC.MAX_TIME_S, w["pass"], "s", f"worst {w['state']}"))
    # one cluster out (G3's worst state S2), 180 deg on every axis, one couple per axis
    out_fail = []
    for c in I["rcs"]["clusters"]:
        rem = [t for t in TH if t["cluster"] != c["id"]]
        lim = rcs_limits("S2", rem, n=1)
        for ax in ("roll", "pitch", "yaw"):
            r = slew("S2", ax, 180.0, lim)
            if not r["pass"]:
                out_fail.append(f"{c['id']}:{ax}")
    cs.append(chk("RCS 180 deg slews on all axes with any one cluster out (S2)", len(out_fail), 0, not out_fail, "failures", ", ".join(out_fail)))
    # attitude hold against the torch: disturbance = thrust x (trim offset + 0.5 deg error) about the CG
    hold = []
    for s in STATES:
        st = CARD["states"][s]
        m = st["mass_t"] * 1e3
        lever = CARD["torch"]["thrust_point_x_m"] - st["cg_m"][0]
        for mode in TORCH.MODE_CARDS:
            F = torch_force(mode, m)[0]
            dist = F * lever * math.sin(math.radians(st["thrust_trim_deg"] + MISALIGN_DEG))
            resid = F * lever * math.sin(math.radians(max(0.0, st["thrust_trim_deg"] + MISALIGN_DEG - TVC_DEG)))
            hold.append({"state": s, "mode": mode, "thrust_mn": round(F / 1e6, 2), "disturbance_mnm": round(dist / 1e6, 2), "after_tvc_mnm": round(resid / 1e6, 3)})
    full = min(rcs_limits(s, n=99)["pitch"] for s in STATES)
    worst_h = max(hold, key=lambda h: h["disturbance_mnm"])
    tvc_need = max(CARD["states"][s]["thrust_trim_deg"] for s in STATES) + MISALIGN_DEG
    tvc_have = CARD["torch"].get("tvc_authority_deg")
    worst_r = max(hold, key=lambda h: h["after_tvc_mnm"])
    cs.append(chk("attitude held against torch thrust error: torch TVC first, RCS takes the rest (all RCS couples)", worst_r["after_tvc_mnm"], round(full / 1e6, 2),
                  worst_r["after_tvc_mnm"] * 1e6 <= full, "MN m",
                  f"left for the RCS after {TVC_DEG} deg TVC; without TVC the worst is {worst_h['disturbance_mnm']} MN m ({worst_h['state']} {worst_h['mode']}), beyond the RCS alone"))
    cs.append(chk(f"torch thrust-vector authority covers trim + an ASSUMED {MISALIGN_DEG} deg error", tvc_have if tvc_have is not None else "not declared", round(tvc_need, 3),
                  tvc_have is not None and tvc_have >= tvc_need, "deg", f"requirement conditional on the {MISALIGN_DEG} deg assumption; the {tvc_have} deg authority is declared (kT 2026-10-26), not a qualified nozzle capability"))
    # translation: main's response law and test velocities, the ship's thruster forces
    tr = []
    vmax = [max(abs(v[j]) for v in (c["target_velocity_m_s"] for c in COUP._CASES.values())) for j in range(3)]
    for s in ("S1", "S5"):
        m = CARD["states"][s]["mass_t"] * 1e3
        for j, ax in enumerate("xyz"):
            fpos = sum(t["f"][j] for t in TH if t["f"][j] > 1e-6)
            fneg = -sum(t["f"][j] for t in TH if t["f"][j] < -1e-6)
            need = m * COUP.TRANSLATION_RESPONSE_RATE_S_INV * vmax[j]
            tr.append({"state": s, "axis": ax, "force_kn_pos": round(fpos / 1e3, 1), "force_kn_neg": round(fneg / 1e3, 1), "needed_kn": round(need / 1e3, 1),
                       "ok": min(fpos, fneg) >= need})
    bad = [f"{t['axis']} ({t['state']}: {min(t['force_kn_pos'], t['force_kn_neg'])} of {t['needed_kn']} kN)" for t in tr if not t["ok"]]
    cs.append(chk("RCS translation on all three axes meets main's response law and test velocities", len(bad), 0, not bad, "axes short", "; ".join(bad)))
    return cs, {"slews": rows, "torch_disturbance": hold, "translation": tr, "tvc_needed_deg": round(tvc_need, 3), "rcs_full_pitch_mnm": round(full / 1e6, 2)}


# ------------------------------------------------------------------ T. torch burn (new: time-stepped, crew cap, CG migration)
def interp_state(frac):
    """CG and trim between full tanks (S1) and burnt out (S4) by the remaining remass fraction."""
    a, b = CARD["states"]["S1"], CARD["states"]["S4"]
    cg = [b["cg_m"][k] + (a["cg_m"][k] - b["cg_m"][k]) * frac for k in range(3)]
    return cg, b["thrust_trim_deg"] + (a["thrust_trim_deg"] - b["thrust_trim_deg"]) * frac


def burn(mode, cap_g, dt=1.0):
    mdot0, ve, _, _ = (float(x) for x in TORCH.mode_outputs(mode))
    m0 = CARD["states"]["S1"]["mass_t"] * 1e3
    usable = (CARD["states"]["S1"]["remass_usable_t"]) * 1e3
    m, t, dv, peak_g, peak_trim, burned = m0, 0.0, 0.0, 0.0, 0.0, 0.0
    seg, segs, coast_t, longest = 0.0, 1, 0.0, 0.0        # burn segments separated by simulated coasts (no thrust, no flow)
    while burned < usable - 1e-6:
        if seg >= SEGMENT_MAX_MIN * 60 - 1e-9:
            coast_t += COAST_MIN * 60                       # coast: thrust off, mass and velocity unchanged in free space
            longest, seg, segs = max(longest, seg), 0.0, segs + 1
        F = torch_force(mode, m, cap_g)[0]             # working card, held to the heat ceiling and the g cap (mdot reduced at fixed ve)
        mdot = F / ve
        step = min(dt, (usable - burned) / mdot, SEGMENT_MAX_MIN * 60 - seg)
        a = F / m
        dv += a * step
        m -= mdot * step
        burned += mdot * step
        t += step
        seg += step
        peak_g = max(peak_g, a / G0)
        peak_trim = max(peak_trim, interp_state(1 - burned / usable)[1])
    rocket = ve * math.log(m0 / (m0 - usable))
    return {"mode": mode, "cap_g": cap_g, "burn_min": round(t / 60, 1), "dv_km_s": round(dv / 1e3, 2), "rocket_eq_km_s": round(rocket / 1e3, 2),
            "error_pct": round(100 * (dv - rocket) / rocket, 3), "peak_g": round(peak_g, 3), "peak_trim_deg": round(peak_trim, 3),
            "segments": segs, "coast_breaks": segs - 1, "longest_segment_min": round(max(longest, seg) / 60, 1),
            "elapsed_with_coasts_min": round((t + coast_t) / 60, 1)}


def torch_tests():
    rows = [burn(m, CREW_G) for m in TORCH.MODE_CARDS]
    cs = [chk("torch: integrated delta-v agrees with the rocket equation (all modes, full usable remass)", max(abs(r["error_pct"]) for r in rows), 0.1,
              all(abs(r["error_pct"]) <= 0.1 for r in rows), "% worst"),
          chk(f"torch: peak acceleration within the {CREW_G:.0f} g crew cap and the {STRUCT_G:.0f} g structural rating", max(r["peak_g"] for r in rows), CREW_G,
              max(r["peak_g"] for r in rows) <= CREW_G + 1e-6, "g"),
          chk("torch: trim stays within the G3 limit as the tanks drain", max(r["peak_trim_deg"] for r in rows), C["G3"]["trim_max_deg"],
              max(r["peak_trim_deg"] for r in rows) <= C["G3"]["trim_max_deg"], "deg", "CG interpolated between S1 (full) and S4 (burnt out)")]
    long = [f"{r['mode']} {r['burn_min']} min burning in {r['segments']} segments, {r['elapsed_with_coasts_min']} min elapsed" for r in rows if r["coast_breaks"]]
    worst_seg = max(r["longest_segment_min"] for r in rows)
    cs.append(chk(f"torch: interrupted burns simulated, no segment over {SEGMENT_MAX_MIN:.0f} min ([V2 6113]); delta-v unchanged by the coasts",
                  worst_seg, SEGMENT_MAX_MIN, worst_seg <= SEGMENT_MAX_MIN + 1e-6, "min", f"coast {COAST_MIN:.0f} min each (ASSUMPTION). " + "; ".join(long)))
    return cs, rows


# ------------------------------------------------------------------ M. Metric mode sequence (new state machine; canon numbers from main)
ALLOWED = {"COAST": {"TORCH", "METRIC_PREP", "LOOM_PREP"}, "TORCH": {"COAST"}, "METRIC_PREP": {"METRIC_RAMP", "COAST"},
           "METRIC_RAMP": {"METRIC_TRANSPORT", "METRIC_COLLAPSE"}, "METRIC_TRANSPORT": {"METRIC_COLLAPSE"},
           "METRIC_COLLAPSE": {"NRE_RELAXATION"}, "NRE_RELAXATION": {"COAST", "LOOM_FORMATION"},
           "LOOM_PREP": {"LOOM_FORMATION", "COAST"}, "LOOM_FORMATION": {"LOOM_TRANSLATION", "COAST"}, "LOOM_TRANSLATION": {"ARRIVAL"}, "ARRIVAL": {"COAST", "TORCH"}}


def run_sequence(seq):
    for a, b in zip(seq, seq[1:]):
        if b not in ALLOWED.get(a, ()):
            return False, f"{a} -> {b}"
    return True, ""


def metric_tests(g4_checks=None):
    mc = METRIC.build_metric_closure()
    rules = mc["operating_rules"]
    plant = mc["plant"]
    cs = []
    ok, why = run_sequence(["COAST", "METRIC_PREP", "METRIC_RAMP", "METRIC_TRANSPORT", "METRIC_COLLAPSE", "NRE_RELAXATION", "COAST"])
    cs.append(chk("Metric: nominal sequence (prep, ramp, transport, collapse, relaxation) is valid", "valid" if ok else why, "valid", ok))
    bad, _ = run_sequence(["COAST", "TORCH", "METRIC_RAMP"])
    cs.append(chk("Metric: torch to Metric ramp without a coast is refused (torch and high Metric exclusive)", "refused" if not bad else "allowed", "refused",
                  (not bad) and rules["torch_high_metric_mutually_exclusive"]))
    rows = []
    for name, md in mc["modes"].items():
        rows.append({"mode": name, "ramp_s": float(md["ramp_s"]), "cold_load_kw": float(md["cold_load_w"]) / 1e3,
                     "upstream_electrical_mw": round(float(md["required_upstream_electrical_w"]) / 1e6, 2), "canon_900k_area_m2": float(md["canon_900k_equivalent_area_m2"])})
    worst_cold = max(r["cold_load_kw"] for r in rows)
    cs.append(chk("Metric: cold load within the cryoplant class in every mode", worst_cold, float(plant["cryoplant_class_w"]) / 1e3, worst_cold * 1e3 <= float(plant["cryoplant_class_w"]), "kW"))
    if g4_checks is None:
        g4_checks = [c for g in json.loads((REV / "out/certification_report.json").read_text())["gates"] if g["gate"] == "G4" for c in g["checks"]]
    g4 = [c for c in g4_checks if c["name"].startswith("Metric")]
    cs.append(chk("Metric: heat of every mode rejected (G4)", sum(c["pass"] for c in g4), len(g4), all(c["pass"] for c in g4) and len(g4) == 4, "modes"))
    cs.append(chk("Metric: ramps within canon's 10-30 s", f"{min(r['ramp_s'] for r in rows):.0f}-{max(r['ramp_s'] for r in rows):.0f}", "10-30",
                  all(10 <= r["ramp_s"] <= 30 for r in rows), "s"))
    return cs, {"modes": rows, "not_computed": "metric delta-v and remass (CANON II s20: no exact values without a calibrated U^M_gamma and terminal solver)",
                "physics_validation_holds": list(mc["physics_validation_holds"])}


# ------------------------------------------------------------------ L. Loom configuration and sequence (new)
def find(o, key):
    """first dict stored under key anywhere in the inputs (the crown_dome block sits inside the L1 deck)."""
    if isinstance(o, dict):
        if isinstance(o.get(key), dict):
            return o[key]
        o = list(o.values())
    if isinstance(o, list):
        for v in o:
            r = find(v, key)
            if r:
                return r
    return {}


def loom_tests():
    mc = METRIC.build_metric_closure()
    cs = []
    ok, why = run_sequence(["COAST", "METRIC_PREP", "METRIC_RAMP", "METRIC_TRANSPORT", "METRIC_COLLAPSE", "NRE_RELAXATION", "LOOM_FORMATION", "LOOM_TRANSLATION", "ARRIVAL"])
    cs.append(chk("Loom: metric collapse -> NRE relaxation -> Loom formation sequence is valid", "valid" if ok else why, "valid", ok))
    direct, _ = run_sequence(["COAST", "METRIC_PREP", "METRIC_RAMP", "METRIC_TRANSPORT", "LOOM_FORMATION"])
    cs.append(chk("Loom: direct mid-field Metric -> Loom is refused (not crew-rated)", "refused" if not direct else "allowed", "refused",
                  (not direct) and not mc["operating_rules"]["direct_midfield_metric_to_loom_crew_rated"]))
    # configuration lock: E1 committed configuration (PR #179): launch DOCKED, external attachment FREE, deployables STOWED
    # each item passes only if the card or inputs declare it; nothing is assumed
    span = I["radiators"].get("span_by_mode_m", {})
    lock = {"shuttle docked in the translating states (S1 to S4, S7)": all(CARD["states"][s]["shuttle"] == "docked" for s in ("S1", "S2", "S3", "S4", "S7")),
            "hot fins folded outside torch burns": "folded" in I["hot_fins"]["deployed"] and "torch burns only" in I["hot_fins"]["deployed"],
            "strakes stowed for Loom (a LOOM entry with span 0)": span.get("LOOM") == 0,
            "crown gores closed for Loom (crown_dome doctrine names Loom)": "loom" in str(find(I, "crown_dome").get("doctrine", "")).lower(),
            "docking collar free of external attachments (a declared collar state)": "state" in I["service"]["docking_collar"] or "loom_state" in I["service"]["docking_collar"]}
    missing = [k for k, v in lock.items() if not v]
    cs.append(chk("Loom: E1 configuration lock (DOCKED / FREE / STOWED) is declared in the card", sum(lock.values()), len(lock), not missing, "items",
                  ("not declared: " + "; ".join(missing)) if missing else "all declared"))
    # arrival: Loom gives no free velocity reset; the torch must close the arrival mismatch above the 50 t reserve
    st = CARD["states"]["S3"]
    m0 = st["mass_t"] * 1e3
    spend = (st["remass_usable_t"] - RESERVE_T) * 1e3
    cap = {mode: round(float(TORCH.mode_outputs(mode)[1]) * math.log(m0 / (m0 - spend)) / 1e3, 1) for mode in ("ECON", "CRUISE", "EXPEDITE")}
    cs.append(chk("Loom: torch delta-v available at arrival above the 50 t reserve (normal dispatch, ECON)", cap["ECON"], "reported", cap["ECON"] > 0, "km/s",
                  f"CRUISE {cap['CRUISE']}, EXPEDITE {cap['EXPEDITE']} km/s; the arrival mismatch itself comes from the natural transport map (not computed)"))
    return cs, {"arrival_dv_km_s": cap, "configuration_lock": lock,
                "not_computed": "Loom domain fit: PR #356 INDETERMINATE_NOT_CERTIFIABLE; route topology and the natural transport map"}


def run(g4_checks=None):
    c1, torch_rows = card_conformance()
    r1, rcs = rcs_tests()
    t1, burns = torch_tests()
    m1, met = metric_tests(g4_checks)
    l1, loom = loom_tests()
    groups = {"C_card": c1, "R_rcs": r1, "T_torch": t1, "M_metric": m1, "L_loom": l1}
    allc = [c for g in groups.values() for c in g]
    return {"header": "ALL bodies. ALL sponsors. 2026-2226.", "status": "NON-GOVERNING G10 v0.2 flight-dynamics tests (engineering); not mission results, not canon outputs",
            "geometry_sha256": CARD["geometry_sha256"], "sources": SOURCES, "checks": groups,
            "passed": sum(c["pass"] for c in allc), "total": len(allc), "verdict": all(c["pass"] for c in allc),
            "detail": {"torch_cards": torch_rows, "rcs": rcs, "burns": burns, "metric": met, "loom": loom},
            "deferred_not_gating": ["E1, FR-01B-R and MV-01 flown in Navigator: no executable fixtures, no ship-card import, and canon II s20 bars exact remass/delta-v outputs until U^M_gamma and a terminal solver exist",
                                    "Loom translation-domain fit: PR #356"]}


if __name__ == "__main__":
    r = run()
    (HERE / "g10_results.json").write_text(json.dumps(r, indent=1))
    for g, cs in r["checks"].items():
        print("==", g)
        for c in cs:
            print(f"  {'PASS' if c['pass'] else 'FAIL'}  {c['name']}: {c['value']} vs {c['limit']} {c['unit']}  {c['note']}")
    print(f"{r['passed']}/{r['total']} pass")
