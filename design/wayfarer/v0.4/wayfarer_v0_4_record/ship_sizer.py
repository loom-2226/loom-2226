"""LOOM ship sizer v0.1 -- ALL bodies. ALL sponsors. 2026-2226.

NON-GOVERNING SANDBOX. Wayfarer is the calibration ship. Every coefficient is
derived at run time from the repo's Wayfarer seed ledger and torch mode cards;
the only authored choices live in ship_rules.json (what each ledger line scales
with). The LLM proposes a hull file; this code is the only place math happens.

Usage:
    python ship_sizer.py REPO_DIR hulls/my_hull.json [--json]
"""
import hashlib
import importlib.util
import json
import math
import sqlite3
import sys
from pathlib import Path

G0 = 9.80665  # standard gravity, m/s^2 (structural constant)
HERE = Path(__file__).resolve().parent
RULES_PATH = HERE / "ship_rules.json"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_reference(repo):
    """Read Wayfarer's seed ledger and torch cards straight from the repo."""
    rules = json.loads(RULES_PATH.read_text())
    src = rules["sources"]
    seed_path = Path(repo) / src["seed"]
    cards_path = Path(repo) / src["mode_cards"]

    db = sqlite3.connect(":memory:")
    db.executescript(seed_path.read_text())
    params = {k: v for k, v in db.execute(
        "SELECT key, value_real FROM geometry_parameters")}
    ledger = {k: m for k, m in db.execute("SELECT id, mass_t FROM mass_elements")}

    spec = importlib.util.spec_from_file_location("mode_cards", cards_path)
    cards_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cards_mod)
    cards = {}
    for mode in cards_mod.MODE_CARDS:
        mdot, ve, thrust, _ = cards_mod.mode_outputs(mode)
        cards[mode] = {"mdot_kg_s": float(mdot), "ve_m_s": float(ve),
                       "thrust_n": float(thrust)}

    missing = set(ledger) ^ set(rules["ledger_scaling"])
    if missing:
        raise ValueError(f"ledger lines and scaling rules disagree: {sorted(missing)}")

    provenance = {
        "rules_sha256": sha256(RULES_PATH),
        "seed_sha256": sha256(seed_path),
        "mode_cards_sha256": sha256(cards_path),
    }
    return rules, params, ledger, cards, provenance


def coefficients(rules, params, ledger):
    """Turn Wayfarer's ledger into per-driver coefficients."""
    ref = rules["reference_ship"]
    dry_ref = params["mass.dry_reference_t"]
    wet_ref = params["mass.wet_reference_t"] + ref["payload_aboard_t"]["value"]
    driver_ref = {
        "crew": ref["crew"]["value"],
        "payload_capacity": ref["payload_capacity_t"]["value"],
        "wet_mass": wet_ref,
        "torch_scale": 1.0,
        "per_hull": 1.0,
        "metric_capable": 1.0 if ref["metric_capable"]["value"] else None,
        "carries_launch": 1.0 if ref["carries_launch"]["value"] else None,
        "reserve_fraction_of_dry": dry_ref,
    }
    coef = {}
    for line, rule in rules["ledger_scaling"].items():
        base = driver_ref[rule["driver"]]
        if base is None:
            raise ValueError(f"{line}: reference ship lacks driver {rule['driver']}")
        coef[line] = (rule["driver"], ledger[line] / base)
    water_ref = params[ref["protected_water_seed_key"]]
    water_coef = water_ref / ref["crew"]["value"]
    return coef, water_coef


def size(hull, repo):
    rules, params, ledger, cards, prov = load_reference(repo)
    coef, water_coef = coefficients(rules, params, ledger)
    mode = hull["design_mode"]
    card = cards[mode]

    drivers = {
        "crew": hull["crew"],
        "payload_capacity": hull["payload_capacity_t"],
        "per_hull": 1.0,
        "metric_capable": 1.0 if hull["metric_capable"] else 0.0,
        "carries_launch": 1.0 if hull["carries_launch"] else 0.0,
    }
    r = 1.0 - math.exp(-hull["design_dv_km_s"] * 1000.0 / card["ve_m_s"])
    t = hull["design_accel_g"] * G0 * 1000.0 / card["thrust_n"]  # torch scale per tonne of wet mass

    k0 = kw = f_res = 0.0
    for line, (driver, c) in coef.items():
        if driver in drivers:
            k0 += c * drivers[driver]
        elif driver == "wet_mass":
            kw += c
        elif driver == "torch_scale":
            kw += c * t
        elif driver == "reserve_fraction_of_dry":
            f_res = c
    water = water_coef * hull["crew"]
    aboard = hull["payload_aboard_t"]

    denom = 1.0 - kw / (1.0 - f_res) - r
    if denom <= 0:
        return {"hull": hull["name"], "verdict": "CANNOT_CLOSE",
                "reason": "mass grows faster than it can be pushed: structure, torch and remass "
                          "together need more than 100% of wet mass",
                "remass_fraction": r, "growth_fraction": kw / (1.0 - f_res),
                "provenance": prov}
    wet = (k0 / (1.0 - f_res) + water + aboard) / denom
    remass = r * wet
    torch_scale = t * wet
    dry = (k0 + kw * wet) / (1.0 - f_res)

    lines = {}
    for line, (driver, c) in coef.items():
        if driver in drivers:
            lines[line] = c * drivers[driver]
        elif driver == "wet_mass":
            lines[line] = c * wet
        elif driver == "torch_scale":
            lines[line] = c * torch_scale
        else:
            lines[line] = c * dry

    modes = {}
    for m, cd in cards.items():
        thrust = cd["thrust_n"] * torch_scale
        mdot = cd["mdot_kg_s"] * torch_scale
        modes[m] = {
            "dv_km_s": cd["ve_m_s"] * math.log(wet / (wet - remass)) / 1000.0,
            "thrust_kn": thrust / 1000.0,
            "jet_power_gw": 0.5 * mdot * cd["ve_m_s"] ** 2 / 1e9,
            "accel_wet_g": thrust / (wet * 1000.0) / G0,
            "accel_end_g": thrust / ((wet - remass) * 1000.0) / G0,
            "burn_h": remass * 1000.0 / mdot / 3600.0 if mdot else None,
        }
    return {"hull": hull["name"], "verdict": "CLOSES", "inputs": hull,
            "dry_t": dry, "wet_t": wet, "remass_t": remass,
            "protected_water_t": water, "payload_aboard_t": aboard,
            "torch_scale": torch_scale, "ledger_t": lines, "modes": modes,
            "provenance": prov, "status": rules["status"]}


def wayfarer_requirement(repo):
    """Wayfarer's own drivers, so the sizer can be checked against canon."""
    rules, params, _, cards, _ = load_reference(repo)
    ref = rules["reference_ship"]
    mode = ref["design_mode"]["value"]
    wet = params["mass.wet_reference_t"] + ref["payload_aboard_t"]["value"]
    remass = params[ref["remass_seed_key"]]
    dv = cards[mode]["ve_m_s"] * math.log(wet / (wet - remass)) / 1000.0
    return {"name": "Wayfarer (reference)", "crew": ref["crew"]["value"],
            "payload_capacity_t": ref["payload_capacity_t"]["value"],
            "payload_aboard_t": ref["payload_aboard_t"]["value"],
            "metric_capable": ref["metric_capable"]["value"],
            "carries_launch": ref["carries_launch"]["value"],
            "design_mode": mode, "design_accel_g": ref["design_accel_g"]["value"],
            "design_dv_km_s": dv}


def report(res):
    if res["verdict"] != "CLOSES":
        return f"{res['hull']}: {res['verdict']} -- {res['reason']}"
    out = [f"{res['hull']}: CLOSES  (sandbox, non-governing)",
           f"  dry {res['dry_t']:.1f} t | remass {res['remass_t']:.1f} t | water "
           f"{res['protected_water_t']:.1f} t | payload aboard {res['payload_aboard_t']:.1f} t "
           f"| wet {res['wet_t']:.1f} t | torch scale {res['torch_scale']:.3f}"]
    for line, m in sorted(res["ledger_t"].items(), key=lambda kv: -kv[1]):
        out.append(f"    {line:26s} {m:8.1f} t")
    out.append("  mode       dv km/s  accel wet g  burn h   jet GW")
    for m, v in res["modes"].items():
        out.append(f"  {m:9s} {v['dv_km_s']:8.1f} {v['accel_wet_g']:11.2f} "
                   f"{v['burn_h']:7.1f} {v['jet_power_gw']:9.0f}")
    return "\n".join(out)


if __name__ == "__main__":
    repo, hull_path = sys.argv[1], sys.argv[2]
    hull = json.loads(Path(hull_path).read_text())
    result = size(hull, repo)
    result["provenance"]["hull_sha256"] = sha256(hull_path)
    print(json.dumps(result, indent=2) if "--json" in sys.argv else report(result))
