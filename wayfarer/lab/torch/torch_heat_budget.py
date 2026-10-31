"""Torch heat budget explorer v0.2 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX. Jet power fixed at 11.36 TW (no performance loss). For each cumulative step it
finds the fusion power needed, where the heat lands (hot structure or cold coils), the peak wall flux,
and whether it fits: main strakes 387 MW, hot fins inside the 67.5 t reserve, ITER-class wall flux.
Inputs: torch_heat_inputs.json. Python 3 standard library only."""
import json, math
from pathlib import Path
HERE = Path(__file__).parent
I = json.loads((HERE / "torch_heat_inputs.json").read_text())
SIG = 5.670374419e-8
S, R, C = I["source_split"], I["radiators"], I["coil"]
eta = I["nozzle_efficiency"]["value"]


def fin_capacity_gw(T):
    flux = R["emissivity"] * SIG * T ** 4 * R["view_factor"]
    return flux * R["budget_t"] * 1000 / R["hot_fin_kg_per_m2_face"] / 1e9, flux


def step(st):
    fn = S["neutrons_" + st["neutrons"]]
    fl = S["light"]
    fc = 1 - fn - fl
    # Energy that ends up in the exhaust: charged products always; trapped light and neutrons only with a shell.
    trapped = fl * (1 - st["light_escape"]) + fn * (1 - st["neutron_escape"]) if st["light_escape"] < 1 else 0.0
    absorbed = fc + trapped
    rerad = st["rerad"] * absorbed
    jet_frac = eta * (absorbed - rerad - st["plume_contact"] * fc)
    Pf = I["jet_power_tw"] * 1e12 / jet_frac
    light_out = (fl * st["light_escape"] + rerad) * Pf
    n_out = fn * st["neutron_escape"] * Pf
    g = st["intercept"]
    hot = {"light": g * light_out, "neutrons": g * n_out, "plume contact": st["plume_contact"] * fc * Pf}
    cold = C["band_fraction"] * n_out * C["shield_transmission"] if st["id"] != "S0" else 0.02 * g * n_out
    flux = light_out / (4 * math.pi * st["burn_to_face_m"] ** 2) / 1e6
    return {"id": st["id"], "name": st["name"], "what": st["what"], "fusion_tw": Pf / 1e12,
            "light_escaping_gw": light_out / 1e9, "neutrons_escaping_gw": n_out / 1e9,
            "ship_heat_gw": sum(hot.values()) / 1e9, "parts_gw": {k: v / 1e9 for k, v in hot.items()},
            "coil_heat_mw": cold / 1e6, "cryo_reject_mw": cold * C["cryo_w_per_w"] / 1e6, "wall_flux_mw_m2": flux,
            "light_ppm_of_fusion": (fl * st["light_escape"] + rerad) * 1e6}


def run(verbose=True):
    """All steps, fin capacity and mode table; prints when verbose. Returns the results dict."""
    _p = print if verbose else (lambda *a, **k: None)
    fins = {T: fin_capacity_gw(T) for T in R["hot_fin_temperatures_k"]}
    rows = [step(s) for s in I["steps"]]
    lim = I["face_flux_limit_mw_m2"]["steady"]
    _p("Hot fins inside the", R["budget_t"], "t reserve:", {T: f"{c:.1f} GW ({c * 1e9 / f:,.0f} m2 of face)" for T, (c, f) in fins.items()})
    _p(f"Main strakes: {R['main_strakes_mw']} MW at {R['main_temperature_k']} K\n")
    for r in rows:
        fit = [T for T, (c, _) in fins.items() if r["ship_heat_gw"] <= c]
        r["fins_fit_at_k"] = fit[0] if fit else None
        r["cryo_ok"] = r["cryo_reject_mw"] <= R["main_strakes_mw"]
        r["flux_ok"] = r["wall_flux_mw_m2"] <= lim
        _p(f"{r['id']} {r['name']:30} fusion {r['fusion_tw']:5.1f} TW | ship heat {r['ship_heat_gw']:9.2f} GW "
              f"(fins fit at {r['fins_fit_at_k'] or 'none'} K) | coils {r['coil_heat_mw']:8.2f} MW -> {r['cryo_reject_mw']:8.0f} MW {'ok' if r['cryo_ok'] else 'OVER'} "
              f"| wall {r['wall_flux_mw_m2']:9.1f} MW/m2 {'ok' if r['flux_ok'] else 'OVER'} | light out {r['light_ppm_of_fusion']:8.0f} ppm")
        _p("     ", {k: round(v, 2) for k, v in r["parts_gw"].items()})
    # What light escape the wall can take, by burn distance
    need = {d: lim * 1e6 * 4 * math.pi * d ** 2 / (rows[-1]["fusion_tw"] * 1e12) * 1e6 for d in (4, 6, 7)}
    _p("\nlight escape the reactor face can take at 10 MW/m2:", {f"{d} m": f"{v:.0f} ppm" for d, v in need.items()})
    # Mode by mode: how hot the remass must get, and what regenerative cooling can carry
    _p("\nmode     ve km/s  remass kg/s  keV per nucleon  regen MW")
    modes = {}
    for m, ve in I["modes_ve_km_s"].items():
        P = I["jet_power_tw"] * 1e12 * I["mode_power_fraction"][m]
        md = 2 * P / (ve * 1e3) ** 2
        kev = 0.5 * 1.66054e-27 * (ve * 1e3) ** 2 / 1.602e-16
        reg = md * I["regen"]["mj_per_kg"]
        modes[m] = {"ve": ve, "remass_kg_s": md, "kev_per_nucleon": kev, "regen_mw": reg}
        _p(f"{m:8} {ve:6}  {md:10.1f}  {kev:14.2f}  {reg:8.0f}")
    return {"steps": rows, "fins_gw": {T: c for T, (c, _) in fins.items()},
            "light_ppm_allowed_by_wall": need, "modes": modes}


if __name__ == "__main__":
    r = run()
    (HERE / "torch_heat_results.json").write_text(json.dumps(r, indent=1))
