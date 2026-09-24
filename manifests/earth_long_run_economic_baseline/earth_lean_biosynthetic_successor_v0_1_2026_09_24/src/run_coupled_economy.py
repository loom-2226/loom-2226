#!/usr/bin/env python3
"""Resume the promoted v4 economy at 2100 with explicit labor composition."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

from model import (
    blended_normalized_weights,
    bounded_weighted_allocation,
    machine_task_step,
    synthetic_step,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_ndjson(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def load_engine(v4_root: Path):
    run_manifest = load_json(v4_root / "RUN_MANIFEST.json")
    record = run_manifest["inherited_code_dependencies"]["v3_runner.py"]
    path = Path(record["path"])
    if sha256(path) != record["sha256"]:
        raise ValueError("v4 engine hash mismatch")
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("promoted_v4_engine", path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    engine.ALPHA_CEILING = 0.60
    engine.ALPHA_CEILING_ID = "0.60"
    candidate = load_json(v4_root / "CANDIDATE_2060_MANIFEST.json")
    engine.POLICY_FINGERPRINT = candidate["economic_policy"]["ordered_vector_sha256"]
    return engine, path, run_manifest


def load_checkpoint(engine, engine_path: Path, checkpoint: Path):
    compatibility, constants = engine._checkpoint_io.compatibility(engine.__dict__, str(engine_path))
    state, manifest = engine._checkpoint_io.load(checkpoint, compatibility, constants)
    if manifest["current_year"] != 2100 or manifest["next_year"] != 2101:
        raise ValueError("economic checkpoint is not the complete 2100 boundary")
    return state, manifest


def load_biological_paths(root: Path, economic_isos: set[str]):
    country = defaultdict(dict)
    for row in load_ndjson(root / "biological_country_2100_2226.ndjson"):
        if row["iso3"] in economic_isos:
            country[row["year"]][row["iso3"]] = row
    labor = defaultdict(dict)
    for row in load_ndjson(root / "biological_labor_80_2100_2226.ndjson"):
        labor[row["year"]][row["iso3"]] = row
    summary = {row["year"]: row for row in load_json(root / "annual_biological_summary.json")}
    expected_years = set(range(2100, 2227))
    if set(country) != expected_years or set(labor) != expected_years or set(summary) != expected_years:
        raise ValueError("biological annual coverage incomplete")
    if any(set(country[year]) != economic_isos or set(labor[year]) != economic_isos
           for year in expected_years):
        raise ValueError("biological economic-80 coverage incomplete")
    return country, labor, summary


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def run(parameters, v4_root: Path, checkpoint: Path, demographic_root: Path,
        output_root: Path, summary_only: bool = False):
    output_root.mkdir(parents=True, exist_ok=False)
    engine, engine_path, promoted_manifest = load_engine(v4_root)
    restored, checkpoint_manifest = load_checkpoint(engine, engine_path, checkpoint)
    isos = tuple(restored["isos"])
    if len(isos) != 80:
        raise ValueError("expected qualified economic 80")
    iso_set = set(isos)
    bio_country, bio_labor, bio_summary = load_biological_paths(demographic_root, iso_set)

    base = restored["base"]
    state = restored["state"]
    asset_state = restored["asset_state"]
    asset_dep = restored["asset_dep"]
    labor_shares = restored["labor_shares"]
    investment_shares = restored["investment_shares"]
    current_tfp = restored["current_tfp"]
    current_gap = restored["current_gap"]
    baseline_trade = restored["baseline_trade"]
    current_trade = restored["current_trade"]
    tfp_calibration = restored["tfp_calibration"]
    base_go60 = restored["base_go60"]
    base_va60 = restored["base_va60"]
    base_inv60 = restored["base_inv60"]
    prev_country_va = restored["prev_country_va"]
    prev_country_inv = restored["prev_country_inv"]
    prev_global_va = restored["prev_global_va"]

    sectors = tuple(engine.SECTORS)
    assets = tuple(engine.ASSETS)
    eps = engine.EPS
    synthetic_settings = parameters["synthetic_persons"]
    allocation_repair = parameters.get("allocation_repair")
    machine_ratio = {(iso, sector): 0.0 for iso in isos for sector in sectors}

    # Reinterpret the 2100 labor boundary while preserving every economic level.
    compute_capacity_2100 = {}
    energy_per_bio_2100 = {}
    automation_per_bio_2100 = {}
    for iso in isos:
        bio = bio_labor[2100][iso]["effective_biological_labor"]
        compute_capacity_2100[iso] = (
            asset_state[(iso, "COMPUTE", "machinery")]["capital"]
            + asset_state[(iso, "COMPUTE", "other_assets")]["capital"]
        )
        energy_per_bio_2100[iso] = state[(iso, "ENERGY")]["gross_output"] / max(eps, bio)
        for sector in sectors:
            sector_bio = bio * labor_shares[iso][sector]
            auto = (asset_state[(iso, sector, "machinery")]["capital"]
                    + asset_state[(iso, sector, "transport_equipment")]["capital"])
            automation_per_bio_2100[(iso, sector)] = auto / max(eps, sector_bio)

    initial_synthetic_global = (
        bio_summary[2100]["population"]
        * float(synthetic_settings["initial_population_share_of_biological_2100"])
    )
    if allocation_repair:
        absolute_weight = float(allocation_repair["absolute_capacity_weight"])
        boundary_intensity = {
            iso: math.sqrt(
                max(eps, compute_capacity_2100[iso] / bio_labor[2100][iso]["effective_biological_labor"])
                * max(eps, energy_per_bio_2100[iso])
            ) for iso in isos
        }
        boundary_weights = blended_normalized_weights(
            compute_capacity_2100, boundary_intensity, absolute_weight)
        boundary_seed_rule = "NORMALIZED_75_ABSOLUTE_25_INTENSITY_GEOMETRIC_BLEND"
    else:
        compute_total = sum(compute_capacity_2100.values())
        boundary_weights = {iso: compute_capacity_2100[iso] / compute_total for iso in isos}
        boundary_seed_rule = "BIOLOGICAL_POPULATION_X_EXPLICIT_SEED_SHARE_ALLOCATED_BY_COMPUTE_CAPITAL"
    if allocation_repair:
        economic_bio_2100 = sum(bio_country[2100][iso]["population"] for iso in isos)
        dispersion_bound = float(synthetic_settings["support_index_bounds"][1])
        seed_caps = {
            iso: (dispersion_bound * initial_synthetic_global / economic_bio_2100
                  * bio_country[2100][iso]["population"])
            for iso in isos
        }
        synthetic_stock = bounded_weighted_allocation(
            initial_synthetic_global, boundary_weights, seed_caps)
        boundary_seed_rule += "_WITH_GENERIC_2X_GLOBAL_PERSON_RATIO_BOUND"
    else:
        synthetic_stock = {iso: initial_synthetic_global * boundary_weights[iso] for iso in isos}
    participation_2100 = engine.sf(synthetic_settings["labor_participation"][0][1])
    capacity_2100 = engine.sf(synthetic_settings["effective_labor_per_participant"][0][1])
    boundary_rebase = []
    for iso in isos:
        bio_total = bio_labor[2100][iso]["effective_biological_labor"]
        synthetic_total = synthetic_stock[iso] * participation_2100 * capacity_2100
        for sector in sectors:
            node = (iso, sector)
            legacy_employment = state[node]["employment"]
            bio_sector = bio_total * labor_shares[iso][sector]
            synthetic_sector = synthetic_total * labor_shares[iso][sector]
            effective = bio_sector + synthetic_sector
            old_a = state[node]["A"]
            alpha = base[iso]["alpha"]
            new_a = state[node]["value_added"] / (
                current_tfp[iso] * state[node]["capital"] ** alpha
                * effective ** (1.0 - alpha)
            )
            state[node]["A"] = new_a
            state[node]["employment"] = bio_sector
            state[node]["effective_labor"] = effective
            boundary_rebase.append({
                "iso3": iso, "sector": sector,
                "legacy_biological_labor": legacy_employment,
                "selected_biological_labor": bio_sector,
                "synthetic_labor": synthetic_sector,
                "machine_task_capacity": 0.0,
                "effective_labor": effective,
                "old_A": old_a, "rebased_A": new_a,
                "value_added_preserved": state[node]["value_added"],
            })

    country_path = output_root / "countries_2100_2226.ndjson"
    sector_path = output_root / "country_sectors_2100_2226.ndjson"
    asset_path = output_root / "country_sector_assets_2100_2226.ndjson"
    annual_synthetic = []
    annual_labor = []
    annual_economic = []
    max_gates = {
        "capital_stock_flow_relative_residual": 0.0,
        "country_sector_reconciliation_relative_residual": 0.0,
        "sector_asset_reconciliation_relative_residual": 0.0,
        "production_equation_relative_residual": 0.0,
        "labor_composition_relative_residual": 0.0,
        "annual_labor_share_move": 0.0,
        "annual_investment_share_move": 0.0,
        "annual_trade_total_variation_move": 0.0,
        "annual_country_va_growth_abs": 0.0,
    }
    country_endpoint = []
    sector_endpoint = []
    asset_endpoint = []

    def emit_year(year, country_rows, sector_rows, asset_rows, synthetic_flow):
        nonlocal country_endpoint, sector_endpoint, asset_endpoint
        if not summary_only:
            for row in country_rows:
                country_file.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            for row in sector_rows:
                sector_file.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            for row in asset_rows:
                asset_file.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
        bio_l = sum(row["biological_labor"] for row in country_rows)
        syn_l = sum(row["synthetic_labor"] for row in country_rows)
        machine = sum(row["machine_task_capacity"] for row in country_rows)
        effective = sum(row["effective_labor_input"] for row in country_rows)
        total_va = sum(row["value_added"] for row in country_rows)
        total_cap = sum(row["capital"] for row in country_rows)
        total_inv = sum(row["investment"] for row in country_rows)
        annual_synthetic.append({"year": year, **synthetic_flow})
        annual_labor.append({
            "year": year, "biological_labor": bio_l, "synthetic_labor": syn_l,
            "machine_task_capacity": machine, "total_effective_labor": effective,
            "biological_share": bio_l / effective, "synthetic_share": syn_l / effective,
            "machine_share": machine / effective,
        })
        annual_economic.append({
            "year": year, "value_added": total_va, "capital": total_cap,
            "investment": total_inv, "capital_output_ratio": total_cap / total_va,
            "investment_output_ratio": total_inv / total_va,
        })
        if year == 2226:
            country_endpoint, sector_endpoint, asset_endpoint = country_rows, sector_rows, asset_rows

    with country_path.open("w", encoding="utf-8") as country_file, \
            sector_path.open("w", encoding="utf-8") as sector_file, \
            asset_path.open("w", encoding="utf-8") as asset_file:
        # Explicit 2100 boundary after factor reinterpretation and A rebase.
        boundary_country_rows = []
        boundary_sector_rows = []
        boundary_asset_rows = []
        for iso in isos:
            bio_total = bio_labor[2100][iso]["effective_biological_labor"]
            syn_total = synthetic_stock[iso] * participation_2100 * capacity_2100
            for sector in sectors:
                node = (iso, sector)
                bio_sector = bio_total * labor_shares[iso][sector]
                syn_sector = syn_total * labor_shares[iso][sector]
                effective = bio_sector + syn_sector
                boundary_sector_rows.append({
                    "iso3": iso, "sector": sector, "year": 2100,
                    "capital": state[node]["capital"], "investment": state[node]["investment"],
                    "value_added": state[node]["value_added"], "gross_output": state[node]["gross_output"],
                    "biological_labor": bio_sector, "employment": bio_sector,
                    "synthetic_labor": syn_sector, "synthetic_persons": synthetic_stock[iso] * labor_shares[iso][sector],
                    "machine_task_capacity": 0.0, "effective_labor_input": effective,
                    "A": state[node]["A"], "capital_share_alpha": base[iso]["alpha"],
                    "labor_exponent_effective": 1.0 - base[iso]["alpha"],
                    "country_tfp_multiplier": current_tfp[iso],
                    "labor_share_of_country": labor_shares[iso][sector],
                    "investment_share_of_country": investment_shares[iso][sector],
                    "automation_enabling_index": 1.0,
                })
                for asset in assets:
                    boundary_asset_rows.append({
                        "iso3": iso, "sector": sector, "asset_class": asset, "year": 2100,
                        "capital": asset_state[(iso, sector, asset)]["capital"],
                        "investment": asset_state[(iso, sector, asset)]["investment"],
                        "asset_depreciation_rate": asset_dep[(iso, sector, asset)],
                    })
            boundary_country_rows.append({
                "iso3": iso, "year": 2100,
                "biological_population": bio_country[2100][iso]["population"],
                "synthetic_population": synthetic_stock[iso],
                "recognized_person_population": bio_country[2100][iso]["population"] + synthetic_stock[iso],
                "biological_labor": bio_total, "synthetic_labor": syn_total,
                "machine_task_capacity": 0.0, "effective_labor_input": bio_total + syn_total,
                "labor_capable_biological_population": bio_labor[2100][iso]["labor_capable_population"],
                "age_20_64": bio_labor[2100][iso]["age_20_64"],
                "value_added": prev_country_va[iso], "capital": sum(state[(iso, s)]["capital"] for s in sectors),
                "investment": prev_country_inv[iso],
            })
        emit_year(2100, boundary_country_rows, boundary_sector_rows, boundary_asset_rows, {
            "population": sum(synthetic_stock.values()), "additions": 0.0,
            "retirements_losses": 0.0, "net_migration": 0.0,
            "effective_labor": sum(row["synthetic_labor"] for row in boundary_country_rows),
            "boundary_seed_rule": boundary_seed_rule,
        })

        for year in range(2101, 2227):
            prev_go_ratio = {node: engine.calibrated_ratio(row["gross_output"], base_go60[node])
                             for node, row in state.items()}
            prev_country_va_ratio = {iso: engine.calibrated_ratio(prev_country_va[iso], base_va60[iso]) for iso in isos}
            prev_country_inv_ratio = {iso: engine.calibrated_ratio(prev_country_inv[iso], base_inv60[iso]) for iso in isos}
            global_va_ratio = max(eps, prev_global_va / sum(base_va60.values()))
            demand_factor = {}
            for node in state:
                new_weights, _, tv_move, factor = engine.rewire_supplier_weights(
                    baseline_trade[node], current_trade[node], prev_go_ratio,
                    prev_country_va_ratio, prev_country_inv_ratio, global_va_ratio)
                current_trade[node] = new_weights
                demand_factor[node] = factor
                max_gates["annual_trade_total_variation_move"] = max(
                    max_gates["annual_trade_total_variation_move"], tv_move)

            context = {}
            support_weights = {}
            for iso in isos:
                bio_total = bio_labor[year][iso]["effective_biological_labor"]
                capital = {}
                asset_capital = {}
                for sector in sectors:
                    capital[sector] = 0.0
                    for asset in assets:
                        previous = asset_state[(iso, sector, asset)]
                        depreciation = asset_dep[(iso, sector, asset)]
                        value = (1.0 - depreciation) * previous["capital"] + previous["investment"]
                        identity = (1.0 - depreciation) * previous["capital"] + previous["investment"]
                        residual = abs(value - identity) / max(1.0, abs(identity))
                        max_gates["capital_stock_flow_relative_residual"] = max(
                            max_gates["capital_stock_flow_relative_residual"], residual)
                        asset_capital[(sector, asset)] = value
                        capital[sector] += value
                compute = asset_capital[("COMPUTE", "machinery")] + asset_capital[("COMPUTE", "other_assets")]
                compute_index = (compute / max(eps, bio_total)) / max(
                    eps, compute_capacity_2100[iso] / bio_labor[2100][iso]["effective_biological_labor"])
                energy_index = (state[(iso, "ENERGY")]["gross_output"] / max(eps, bio_total)) / max(
                    eps, energy_per_bio_2100[iso])
                support = math.sqrt(max(eps, compute_index) * max(eps, energy_index))
                support_weights[iso] = compute * support
                context[iso] = {
                    "bio_total": bio_total, "capital": capital, "asset_capital": asset_capital,
                    "compute_index": compute_index, "energy_index": energy_index, "support": support,
                }

            if allocation_repair:
                synthetic_weights = blended_normalized_weights(
                    {iso: context[iso]["asset_capital"][("COMPUTE", "machinery")]
                          + context[iso]["asset_capital"][("COMPUTE", "other_assets")]
                     for iso in isos},
                    {iso: context[iso]["support"] for iso in isos},
                    float(allocation_repair["absolute_capacity_weight"]),
                )
            else:
                allocation_total = sum(support_weights.values())
                synthetic_weights = {iso: support_weights[iso] / allocation_total for iso in isos}
            if not math.isclose(sum(synthetic_weights.values()), 1.0, rel_tol=1e-12):
                raise ValueError("synthetic allocation weights fail normalization")
            global_stock_before = sum(synthetic_stock.values())
            support_global = sum(context[iso]["support"] * synthetic_weights[iso] for iso in isos)
            synthetic_flow = synthetic_step(global_stock_before, bio_summary[year]["population"],
                                             support_global, year, parameters)
            retained_stock = {
                iso: synthetic_stock[iso]
                * (1.0 - float(synthetic_settings["annual_retirement_loss_rate"]))
                for iso in isos
            }
            if allocation_repair:
                economic_bio = sum(bio_country[year][iso]["population"] for iso in isos)
                dispersion_bound = float(synthetic_settings["support_index_bounds"][1])
                final_caps = {
                    iso: (dispersion_bound * synthetic_flow["population"] / economic_bio
                          * bio_country[year][iso]["population"])
                    for iso in isos
                }
                addition_room = {
                    iso: max(0.0, final_caps[iso] - retained_stock[iso]) for iso in isos
                }
                additions_by_iso = bounded_weighted_allocation(
                    synthetic_flow["additions"], synthetic_weights, addition_room)
            else:
                additions_by_iso = {
                    iso: synthetic_flow["additions"] * synthetic_weights[iso] for iso in isos
                }
            for iso in isos:
                synthetic_stock[iso] = retained_stock[iso] + additions_by_iso[iso]
                if synthetic_stock[iso] < 0:
                    raise ValueError(f"negative synthetic stock {iso}/{year}")
            if not math.isclose(sum(synthetic_stock.values()), synthetic_flow["population"], rel_tol=1e-12):
                raise ValueError("synthetic stock reconciliation failed")

            # Compute labor shares and the existing machine mechanism first, then
            # repair only its geography while preserving its global capacity.
            year_labor = {}
            raw_machine = {}
            machine_absolute = {}
            machine_intensity = {}
            machine_caps = {}
            for iso in isos:
                ctx = context[iso]
                bio_total = ctx["bio_total"]
                synthetic_total = (synthetic_stock[iso] * synthetic_flow["labor_participation"]
                                   * synthetic_flow["effective_labor_per_participant"])
                pressure = {}
                for sector in sectors:
                    node = (iso, sector)
                    desired_go = base_go60[node] * demand_factor[node]
                    pressure[sector] = max(eps, desired_go / max(eps, state[node]["gross_output"]))
                labor_productivity = {
                    sector: state[(iso, sector)]["value_added"]
                    / max(eps, state[(iso, sector)]["effective_labor"])
                    for sector in sectors
                }
                desired = engine.desired_labor_shares(labor_shares[iso], pressure, labor_productivity)
                new_labor_share = engine.blend_shares(
                    labor_shares[iso], desired, engine.LABOR_ADJUST_SPEED, sectors)
                biological_sector = {}
                synthetic_sector = {}
                automation_index = {}
                for sector in sectors:
                    node = (iso, sector)
                    biological_sector[sector] = bio_total * new_labor_share[sector]
                    synthetic_sector[sector] = synthetic_total * new_labor_share[sector]
                    auto = (ctx["asset_capital"][(sector, "machinery")]
                            + ctx["asset_capital"][(sector, "transport_equipment")])
                    intensity = auto / max(eps, biological_sector[sector])
                    automation_index[sector] = intensity / max(eps, automation_per_bio_2100[node])
                    raw = machine_task_step(machine_ratio[node], automation_index[sector],
                                            biological_sector[sector], parameters)
                    raw_machine[node] = raw["capacity"]
                    machine_absolute[node] = auto
                    machine_intensity[node] = intensity
                    machine_caps[node] = (biological_sector[sector]
                                          * float(parameters["nonperson_machine_tasks"]
                                                  ["maximum_machine_to_biological_task_ratio"]))
                year_labor[iso] = {
                    "synthetic_total": synthetic_total,
                    "pressure": pressure,
                    "new_labor_share": new_labor_share,
                    "biological_sector": biological_sector,
                    "synthetic_sector": synthetic_sector,
                    "automation_index": automation_index,
                }
            if allocation_repair:
                machine_weights = blended_normalized_weights(
                    machine_absolute, machine_intensity,
                    float(allocation_repair["absolute_capacity_weight"]),
                )
                raw_machine_total = sum(raw_machine.values())
                global_biological_tasks = sum(
                    value for iso in year_labor.values()
                    for value in iso["biological_sector"].values()
                )
                dispersion_bound = float(synthetic_settings["support_index_bounds"][1])
                local_ratio_bound = min(
                    float(parameters["nonperson_machine_tasks"]
                          ["maximum_machine_to_biological_task_ratio"]),
                    dispersion_bound * raw_machine_total / max(eps, global_biological_tasks),
                )
                repaired_caps = {
                    node: min(machine_caps[node],
                              local_ratio_bound
                              * year_labor[node[0]]["biological_sector"][node[1]])
                    for node in machine_caps
                }
                machine_allocation = bounded_weighted_allocation(
                    raw_machine_total, machine_weights, repaired_caps)
            else:
                machine_allocation = raw_machine
            for node, capacity in machine_allocation.items():
                bio_node = year_labor[node[0]]["biological_sector"][node[1]]
                machine_ratio[node] = capacity / max(eps, bio_node)

            new_state = {}
            country_rows = []
            sector_rows = []
            asset_rows = []
            new_country_va = {}
            new_country_inv = {}
            for iso in isos:
                ctx = context[iso]
                bio_total = ctx["bio_total"]
                pre = year_labor[iso]
                synthetic_total = pre["synthetic_total"]
                gap_before = current_gap[iso]
                tfp_growth = engine.transition_tfp_growth(
                    base[iso]["tfp_start_growth"], tfp_calibration["frontier_growth_log"],
                    tfp_calibration["catchup_speed"], year - 2060, gap_before)
                current_tfp[iso] *= 1.0 + tfp_growth
                current_gap[iso] = max(0.0, gap_before * math.exp(-tfp_calibration["catchup_speed"]))
                next_alpha = engine.effective_alpha(base[iso]["alpha_2060"], year)

                pressure = pre["pressure"]
                new_labor_share = pre["new_labor_share"]
                for sector in sectors:
                    max_gates["annual_labor_share_move"] = max(
                        max_gates["annual_labor_share_move"],
                        abs(new_labor_share[sector] - labor_shares[iso][sector]))

                value_added = {}
                gross_output = {}
                biological_sector = pre["biological_sector"]
                synthetic_sector = pre["synthetic_sector"]
                machine_sector = {}
                effective_sector = {}
                automation_index = pre["automation_index"]
                for sector in sectors:
                    node = (iso, sector)
                    machine_sector[sector] = machine_allocation[node]
                    effective_sector[sector] = biological_sector[sector] + synthetic_sector[sector] + machine_sector[sector]
                    previous = state[node]
                    previous["A"], _ = engine.rebase_A(
                        previous["A"], base[iso]["alpha"], next_alpha,
                        ctx["capital"][sector], effective_sector[sector])
                    value_added[sector] = engine.production(
                        previous["A"], ctx["capital"][sector], effective_sector[sector],
                        next_alpha, current_tfp[iso])
                    gross_output[sector] = value_added[sector] * previous["go_va_ratio"]
                    reconstructed = biological_sector[sector] + synthetic_sector[sector] + machine_sector[sector]
                    max_gates["labor_composition_relative_residual"] = max(
                        max_gates["labor_composition_relative_residual"],
                        abs(effective_sector[sector] - reconstructed) / max(1.0, effective_sector[sector]))
                    equation = engine.production(previous["A"], ctx["capital"][sector],
                                                 effective_sector[sector], next_alpha, current_tfp[iso])
                    max_gates["production_equation_relative_residual"] = max(
                        max_gates["production_equation_relative_residual"],
                        abs(value_added[sector] - equation) / max(1.0, value_added[sector]))

                country_va = sum(value_added.values())
                country_go = sum(gross_output.values())
                depreciation_need = sum(
                    asset_dep[(iso, sector, asset)] * ctx["asset_capital"][(sector, asset)]
                    for sector in sectors for asset in assets)
                country_inv = engine.investment_budget(
                    year, base[iso]["investment_rate"], country_va, prev_country_va[iso],
                    sum(ctx["capital"].values()), depreciation_need)
                base[iso]["alpha"] = next_alpha
                capital_productivity = {sector: value_added[sector] / max(eps, ctx["capital"][sector])
                                        for sector in sectors}
                (investment, investment_asset, new_investment_share, replacement_need,
                 replacement_funded, expansion_sector, expansion_asset,
                 replacement_coverage) = engine.allocate_asset_replacement_and_expansion(
                    country_inv, ctx["asset_capital"],
                    {(sector, asset): asset_dep[(iso, sector, asset)] for sector in sectors for asset in assets},
                    investment_shares[iso], pressure, capital_productivity)
                for sector in sectors:
                    max_gates["annual_investment_share_move"] = max(
                        max_gates["annual_investment_share_move"],
                        abs(new_investment_share[sector] - investment_shares[iso][sector]))
                growth = country_va / prev_country_va[iso] - 1.0
                max_gates["annual_country_va_growth_abs"] = max(
                    max_gates["annual_country_va_growth_abs"], abs(growth))

                for sector in sectors:
                    node = (iso, sector)
                    previous = state[node]
                    sector_rows.append({
                        "iso3": iso, "sector": sector, "year": year,
                        "capital": ctx["capital"][sector], "investment": investment[sector],
                        "value_added": value_added[sector], "gross_output": gross_output[sector],
                        "biological_labor": biological_sector[sector], "employment": biological_sector[sector],
                        "synthetic_labor": synthetic_sector[sector],
                        "synthetic_persons": synthetic_stock[iso] * new_labor_share[sector],
                        "machine_task_capacity": machine_sector[sector],
                        "effective_labor_input": effective_sector[sector],
                        "A": previous["A"], "capital_share_alpha": next_alpha,
                        "labor_exponent_effective": 1.0 - next_alpha,
                        "country_tfp_multiplier": current_tfp[iso], "country_tfp_growth": tfp_growth,
                        "labor_share_of_country": new_labor_share[sector],
                        "investment_share_of_country": new_investment_share[sector],
                        "automation_enabling_index": automation_index[sector],
                        "machine_to_biological_task_ratio": machine_ratio[node],
                        "replacement_coverage_ratio": replacement_coverage,
                        "io_demand_factor": demand_factor[node], "io_demand_pressure": pressure[sector],
                    })
                    new_state[node] = {
                        "capital": ctx["capital"][sector], "investment": investment[sector],
                        "employment": biological_sector[sector], "effective_labor": effective_sector[sector],
                        "value_added": value_added[sector], "gross_output": gross_output[sector],
                        "A": previous["A"], "A_historical_2026": previous["A_historical_2026"],
                        "go_va_ratio": previous["go_va_ratio"],
                    }
                    for asset in assets:
                        asset_rows.append({
                            "iso3": iso, "sector": sector, "asset_class": asset, "year": year,
                            "capital": ctx["asset_capital"][(sector, asset)],
                            "investment": investment_asset[(sector, asset)],
                            "replacement_need": replacement_need[(sector, asset)],
                            "replacement_funded": replacement_funded[(sector, asset)],
                            "expansion_investment": expansion_asset[(sector, asset)],
                            "replacement_coverage_ratio": replacement_coverage,
                            "asset_depreciation_rate": asset_dep[(iso, sector, asset)],
                        })
                        asset_state[(iso, sector, asset)] = {
                            "capital": ctx["asset_capital"][(sector, asset)],
                            "investment": investment_asset[(sector, asset)],
                        }

                sector_va = sum(row["value_added"] for row in sector_rows if row["iso3"] == iso)
                sector_cap = sum(row["capital"] for row in sector_rows if row["iso3"] == iso)
                sector_inv = sum(row["investment"] for row in sector_rows if row["iso3"] == iso)
                max_gates["country_sector_reconciliation_relative_residual"] = max(
                    max_gates["country_sector_reconciliation_relative_residual"],
                    abs(sector_va - country_va) / max(1.0, country_va),
                    abs(sector_cap - sum(ctx["capital"].values())) / max(1.0, sum(ctx["capital"].values())),
                    abs(sector_inv - country_inv) / max(1.0, country_inv))
                for sector in sectors:
                    asset_cap_sum = sum(
                        ctx["asset_capital"][(sector, asset)] for asset in engine.ASSETS
                    )
                    max_gates["sector_asset_reconciliation_relative_residual"] = max(
                        max_gates["sector_asset_reconciliation_relative_residual"],
                        abs(asset_cap_sum - ctx["capital"][sector]) / max(1.0, ctx["capital"][sector]))

                capable = bio_labor[year][iso]["labor_capable_population"]
                if bio_total > capable + 1e-6 or bio_total > bio_country[year][iso]["population"] + 1e-6:
                    raise ValueError(f"biological labor exceeds people/capability {iso}/{year}")
                country_rows.append({
                    "iso3": iso, "year": year,
                    "biological_population": bio_country[year][iso]["population"],
                    "synthetic_population": synthetic_stock[iso],
                    "recognized_person_population": bio_country[year][iso]["population"] + synthetic_stock[iso],
                    "biological_labor": bio_total, "synthetic_labor": synthetic_total,
                    "machine_task_capacity": sum(machine_sector.values()),
                    "effective_labor_input": bio_total + synthetic_total + sum(machine_sector.values()),
                    "labor_capable_biological_population": capable,
                    "age_20_64": bio_labor[year][iso]["age_20_64"],
                    "value_added": country_va, "gross_output": country_go,
                    "capital": sum(ctx["capital"].values()), "investment": country_inv,
                    "real_value_added_growth": growth, "country_tfp_multiplier": current_tfp[iso],
                    "country_tfp_growth": tfp_growth, "replacement_coverage_ratio": replacement_coverage,
                })
                new_country_va[iso] = country_va
                new_country_inv[iso] = country_inv
                labor_shares[iso] = new_labor_share
                investment_shares[iso] = new_investment_share

            state = new_state
            prev_country_va = new_country_va
            prev_country_inv = new_country_inv
            prev_global_va = sum(new_country_va.values())
            emit_year(year, country_rows, sector_rows, asset_rows, {
                **synthetic_flow,
                "population": sum(synthetic_stock.values()),
                "effective_labor": sum(row["synthetic_labor"] for row in country_rows),
            })

    write_json(output_root / "boundary_factor_rebase_2100.json", boundary_rebase)
    write_json(output_root / "annual_synthetic_summary.json", annual_synthetic)
    write_json(output_root / "annual_labor_composition.json", annual_labor)
    write_json(output_root / "annual_economic_summary.json", annual_economic)
    write_json(output_root / "countries_2226.json", country_endpoint)
    write_json(output_root / "country_sectors_2226.json", sector_endpoint)
    write_json(output_root / "country_sector_assets_2226.json", asset_endpoint)

    boundary_va = annual_economic[0]["value_added"]
    checkpoint_va = sum(restored["prev_country_va"].values())
    if not math.isclose(boundary_va, checkpoint_va, rel_tol=1e-12):
        raise ValueError("2100 economic level discontinuity")
    if max_gates["capital_stock_flow_relative_residual"] > 1e-12:
        raise ValueError("capital stock-flow identity failed")
    if max_gates["country_sector_reconciliation_relative_residual"] > 1e-10:
        raise ValueError("country-sector reconciliation failed")
    if max_gates["sector_asset_reconciliation_relative_residual"] > 1e-10:
        raise ValueError("sector-asset reconciliation failed")
    if max_gates["production_equation_relative_residual"] > 1e-12:
        raise ValueError("production equation failed")
    if max_gates["labor_composition_relative_residual"] > 1e-12:
        raise ValueError("labor composition failed")

    report = {
        "status": "COUPLED_SUCCESSOR_COMPLETE_PENDING_INDEPENDENT_VALIDATION",
        "baseline": "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24",
        "checkpoint": str(checkpoint), "checkpoint_sha256": sha256(checkpoint),
        "engine": str(engine_path), "engine_sha256": sha256(engine_path),
        "economic_country_count": len(isos), "start_year": 2100, "end_year": 2226,
        "summary_only": summary_only,
        "allocation_method": (allocation_repair or {}).get("method", "V0_LEGACY"),
        "economic_level_continuity_2100": True,
        "boundary_value_added_2100": boundary_va,
        "terminal_value_added_2226": annual_economic[-1]["value_added"],
        "terminal_synthetic_population_2226": annual_synthetic[-1]["population"],
        "terminal_labor_2226": annual_labor[-1],
        "max_residuals_and_movements": max_gates,
        "category_boundaries": {
            "biological_persons_are_synthetic_persons": False,
            "synthetic_persons_are_machine_tasks": False,
            "machine_tasks_counted_as_population": False,
        },
        "selected_outputs": {
            "countries": str(country_path), "sectors": str(sector_path), "assets": str(asset_path),
            "annual_synthetic": str(output_root / "annual_synthetic_summary.json"),
            "annual_labor": str(output_root / "annual_labor_composition.json"),
            "annual_economic": str(output_root / "annual_economic_summary.json"),
        },
    }
    write_json(output_root / "economic_report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--v4-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--demographic-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    report = run(load_json(args.parameters), args.v4_root, args.checkpoint,
                 args.demographic_root, args.output_root, args.summary_only)
    print(json.dumps({"status": report["status"], "value_added_2226": report["terminal_value_added_2226"],
                      "synthetic_population_2226": report["terminal_synthetic_population_2226"]}, sort_keys=True))


if __name__ == "__main__":
    main()
