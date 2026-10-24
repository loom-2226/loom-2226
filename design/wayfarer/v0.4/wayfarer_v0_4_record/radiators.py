"""Collapsible radiator trade v0.1 -- ALL bodies. ALL sponsors. 2026-2226.
UNCONSTRAINED EXPLORATION (canon set aside, physics kept). Inputs: radiators.json.
Heat per Metric mode comes from canon's cold load and cryo electrical, with the
cryo power rescaled for reject temperature. Usage: python radiators.py [--table]"""
import json, math, sys
from pathlib import Path

SIGMA = 5.670374419e-8
R = json.loads((Path(__file__).resolve().parent / "radiators.json").read_text())
LAY, MH, EPS = R["layout"], R["metric_heat_from_canon"], R["emission"]["effective_emissivity"]
MODES = ["NORMAL", "FAST", "EXPEDITE", "HARD"]
N, CHORD, HULL = LAY["assemblies"], LAY["root_chord_m"], LAY["hull_r_m"]
SIDES = 2 if LAY["two_sided"] else 1


def heat_mw(mode, T):
    tc = MH["cold_temperature_k"]
    return MH["cold_load_kw"][mode] / 1000 + MH["cryo_electrical_mw_at_900K"][mode] * (T - tc) / (900 - tc)


def flux(T):
    return EPS * SIGMA * T ** 4


def span_needed(mode, T, share=1.0):
    a_emit = heat_mw(mode, T) * 1e6 * share / flux(T)
    return a_emit / SIDES / N / CHORD


def deployed(mech, s):
    m = R["mechanisms"][mech]
    if s > m["max_span_m"] + 1e-9:
        return None
    if m["partial"] == "none":
        return m["max_span_m"]
    if m["partial"] == "stepwise":
        return min(m["max_span_m"], math.ceil(s / m["step_m"] - 1e-9) * m["step_m"])
    return s


def evaluate(mech, T):
    m = R["mechanisms"][mech]
    smax = m["max_span_m"]
    panel = N * CHORD * smax
    cap = panel * SIDES * flux(T) / 1e6
    out = {"mech": mech, "label": m["label"], "T": T, "max_span_m": smax,
           "panel_area_m2": panel, "mass_t": panel * m["areal_kg_m2"] / 1000,
           "capacity_mw": cap, "capacity_ppm_of_cruise_jet": cap * 1e6 / (R["torch"]["cruise_jet_power_tw"] * 1e12) * 1e6,
           "stowed_protrusion_m": m["stowed_protrusion_m"], "partial": m["partial"], "torch_g_limit": m["torch_g_limit"],
           "modes": {}}
    for mode in MODES:
        need = span_needed(mode, T)
        need_shared = span_needed(mode, T, 0.5) if mode in ("NORMAL", "FAST") else need
        d, ds = deployed(mech, need), deployed(mech, need_shared)
        out["modes"][mode] = {"heat_mw": heat_mw(mode, T), "span_needed_m": need, "deployed_m": d,
                              "radius_m": HULL + d if d is not None else None,
                              "winner_aft_half_deployed_m": ds,
                              "winner_radius_m": HULL + ds if ds is not None else None}
    return out


def table(mech, T, steps=20):
    m = R["mechanisms"][mech]
    rows = []
    for i in range(steps + 1):
        f = i / steps
        s = f * m["max_span_m"]
        if m["partial"] == "stepwise":
            s = math.floor(s / m["step_m"] + 1e-9) * m["step_m"]
        working = m["partial"] != "none" or i == steps
        area = N * CHORD * s * SIDES if working else 0.0
        cap = area * flux(T) / 1e6
        top = None
        for mode in MODES:
            if cap + 1e-9 >= heat_mw(mode, T):
                top = mode
        rows.append({"f": f, "span": s, "area": area, "cap_mw": cap, "top_mode": top, "radius": HULL + s})
    return rows


if __name__ == "__main__":
    res = [evaluate(m, T) for m in R["mechanisms"] for T in R["temperatures_k"]]
    # check against canon at 900 K
    for mode in MODES:
        a = heat_mw(mode, 900) * 1e6 / flux(900)
        print(f"check {mode}: {a:.0f} m2 emitting at 900 K vs canon {MH['canon_equivalent_area_m2_at_900K'][mode]}")
    print()
    for r in res:
        ms = r["modes"]
        hard = ms["HARD"]["deployed_m"]
        print(f"{r['label']:20s} {r['T']}K  max {r['max_span_m']:4.1f} m  mass {r['mass_t']:5.1f} t  cap {r['capacity_mw']:6.1f} MW "
              f"({r['capacity_ppm_of_cruise_jet']:5.1f} ppm)  FAST span {ms['FAST']['span_needed_m']:4.2f}->{ms['FAST']['deployed_m']}  "
              f"HARD span {ms['HARD']['span_needed_m']:5.2f}->{hard}  winner FAST aft-half {ms['FAST']['winner_aft_half_deployed_m']}")
    (Path(__file__).resolve().parent / "radiator_results.json").write_text(json.dumps(
        {"designs": res, "tables": {f"{m}|{T}": table(m, T) for m in R["mechanisms"] for T in R["temperatures_k"]}}, indent=1))
