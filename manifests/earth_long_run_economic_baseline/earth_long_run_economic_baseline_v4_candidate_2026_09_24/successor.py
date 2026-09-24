"""Small, read-only source adapters for the unpromoted Earth successor.

This module does not run the economic simulation. Financial values are model
proxy units, never physical capacity or observed 2226 purchasing-power USD.
"""
import copy
import math
import statistics

REPAIR_METHOD = "PYP_2024_VA_GO_RATIO_X_MODELED_2026_GO_COUNTRY_TOTAL_PRESERVED"


def wpp_identity(rows):
    """Use WPP Medium 2026 Jan-1 Country/Area rows, not WDI aggregates."""
    universe = {}
    world = None
    for row in rows:
        if row.get("Time") != "2026" or row.get("Variant") != "Medium":
            continue
        kind = row.get("LocTypeName")
        if kind == "World" and row.get("Location") == "World":
            if world is not None:
                raise ValueError("duplicate WPP World row")
            world = float(row["TPopulation1Jan"]) * 1000
        if kind != "Country/Area":
            continue
        iso = row.get("ISO3_code", "").strip()
        if not iso:
            raise ValueError("WPP Country/Area without ISO3")
        if iso in universe:
            raise ValueError(f"duplicate WPP identity {iso}")
        pop = float(row["TPopulation1Jan"]) * 1000
        if not math.isfinite(pop) or pop <= 0:
            raise ValueError(f"invalid WPP Jan-1 population {iso}")
        universe[iso] = {
            "iso3": iso,
            "name": row["Location"],
            "population_2026": pop,
            "population_time_basis": "TPopulation1Jan",
            "population_source": "UN_WPP_2024_MEDIUM_2026",
            "wpp_location_type": kind,
        }
    if world is None:
        raise ValueError("WPP World Jan-1 denominator absent")
    if not math.isclose(sum(r["population_2026"] for r in universe.values()), world, rel_tol=1e-8):
        raise ValueError("WPP Country/Area rows do not reconcile to World")
    return dict(sorted(universe.items())), world


def demographic_tail(population, working_age_share, pop_half_life, share_half_life, end_year,
                     min_share=0.20, max_share=0.80):
    """Same central formula as v3; alternate half-lives change sensitivity only."""
    if min(pop_half_life, share_half_life) <= 0:
        raise ValueError("tail half-lives must be positive")
    pop = copy.deepcopy(population)
    share = copy.deepcopy(working_age_share)
    isos = set(pop[2100])
    if isos != set(share[2100]):
        raise ValueError("population and working-age universes differ")
    for year in range(2091, 2101):
        if set(pop[year]) != isos or set(share[year]) != isos:
            raise ValueError(f"missing 2091-2100 anchor {year}")
    anchors = {}
    for iso in sorted(isos):
        growth = [math.log(pop[y][iso] / pop[y-1][iso]) for y in range(2092, 2101)]
        deltas = [share[y][iso] - share[y-1][iso] for y in range(2092, 2101)]
        anchors[iso] = (statistics.median(growth), statistics.median(deltas))
    for year in range(2101, end_year + 1):
        n = year - 2100
        pop[year], share[year] = {}, {}
        for iso in sorted(isos):
            growth, delta = anchors[iso]
            pop[year][iso] = pop[year-1][iso] * math.exp(growth * math.exp(-math.log(2) * n / pop_half_life))
            share[year][iso] = min(max_share, max(min_share,
                share[year-1][iso] + delta * math.exp(-math.log(2) * n / share_half_life)))
    return pop, share


def qualifying_nodes(source, sectors):
    """Find active modeled zeros caused by signed current-price VA semantics."""
    found = []
    for node, row in sorted(sectors.items()):
        obs = source.get(node)
        if obs is None:
            continue
        values = (obs.get("current_va"), obs.get("current_go"), obs.get("pyp_va"), obs.get("pyp_go"),
                  row.get("gross_output"), row.get("employment"), row.get("value_added"))
        if any(v is None or not math.isfinite(float(v)) for v in values):
            continue
        if (obs["current_va"] <= 0 and obs["current_go"] > 0 and
                obs["pyp_va"] > 0 and obs["pyp_go"] > 0 and
                row["gross_output"] > 0 and row["employment"] > 0 and
                row["value_added"] <= 0):
            found.append(node)
    return found


def repair_seed(source, sectors, assets, countries):
    """Reconstruct modeled 2026 sectors; never write into signed observations.

    Capital and investment are allocated at the country's existing K/VA and
    I/VA ratios. Other sectors surrender proportional shares. Asset class
    distribution uses that country's positive 2026 asset-capital proportions.
    """
    state = copy.deepcopy(sectors)
    asset_state = copy.deepcopy(assets)
    trace = []
    keys = ("value_added", "gross_output", "capital", "investment", "employment")
    for iso, sector in qualifying_nodes(source, state):
        node = (iso, sector)
        # The four-asset reconstruction, rather than the earlier macro-sector
        # scalar capital allocation, is the qualified input to the bridge.
        # Recover its sector totals before redistributing the country envelope.
        for (i, s), row in state.items():
            if i == iso:
                row["capital"] = sum(a["capital"] for (j, t, _), a in asset_state.items()
                                     if j == iso and t == s)
        if not math.isclose(sum(row["capital"] for (i, _), row in state.items() if i == iso),
                            countries[iso]["capital"], rel_tol=1e-10):
            raise ValueError(f"asset-backed national capital mismatch {iso}")
        country, old = countries[iso], state[node]
        if min(country[k] for k in keys) <= 0:
            raise ValueError(f"invalid country total for {node}")
        obs = source[node]
        va = old["gross_output"] * obs["pyp_va"] / obs["pyp_go"]
        new = {
            "value_added": va,
            "gross_output": old["gross_output"],
            "capital": va * country["capital"] / country["value_added"],
            "investment": va * country["investment"] / country["value_added"],
            "employment": old["employment"],
        }
        if min(new.values()) <= 0 or any(new[k] >= country[k] for k in keys):
            raise ValueError(f"reconstruction exceeds positive country totals {node}")
        others = [r for (i, s), r in state.items() if i == iso and s != sector]
        for key in keys:
            old_sum = sum(r[key] for r in others)
            residual = country[key] - new[key]
            if old_sum <= 0 or residual <= 0:
                raise ValueError(f"no positive residual {node} {key}")
            factor = residual / old_sum
            for r in others:
                r[key] *= factor
        old.update(new)
        local_assets = {k: r for k, r in asset_state.items() if k[0] == iso}
        class_cap = {}
        for (_, _, cls), r in local_assets.items():
            class_cap[cls] = class_cap.get(cls, 0) + r["capital"]
        total_class_cap = sum(class_cap.values())
        if total_class_cap <= 0:
            raise ValueError(f"no qualified 2026 asset proportions {iso}")
        classes = sorted(class_cap)
        for srow in [r for (i, _), r in state.items() if i == iso]:
            s = srow["sector"]
            rows = {cls: asset_state.get((iso, s, cls)) for cls in classes}
            existing = sum((r["capital"] if r else 0) for r in rows.values())
            for cls in classes:
                # The qualifying node's old assets are epsilon placeholders,
                # not an observed class mix. Use country asset-class proportions
                # for it and retain each donor sector's established proportions.
                fraction = (class_cap[cls] / total_class_cap if s == sector else
                            rows[cls]["capital"] / existing if existing > 0 and rows[cls] else
                            class_cap[cls] / total_class_cap)
                if rows[cls] is None:
                    rows[cls] = {"iso3": iso, "sector": s, "asset_class": cls}
                    asset_state[(iso, s, cls)] = rows[cls]
                rows[cls]["capital"] = srow["capital"] * fraction
                rows[cls]["investment"] = srow["investment"] * fraction
            alpha = country["capital_share_alpha"]
            labor = srow["employment"]
            if srow["value_added"] > 0 and srow["capital"] > 0 and labor > 0:
                srow["operative_A_2026"] = srow["value_added"] / (
                    country["country_tfp_multiplier"] * srow["capital"] ** alpha * labor ** (1-alpha))
        for cls in classes:
            observed = sum(a["capital"] for (i, _, c), a in asset_state.items() if i == iso and c == cls)
            if not math.isclose(observed, class_cap[cls], rel_tol=1e-10, abs_tol=1e-6):
                raise ValueError(f"national asset-class capital changed {iso} {cls}")
        for key in keys:
            actual = sum(r[key] for (i, _), r in state.items() if i == iso)
            if not math.isclose(actual, country[key], rel_tol=1e-10, abs_tol=1e-6):
                raise ValueError(f"country accounting failed {iso} {key}")
        trace.append({"iso3": iso, "sector": sector, "method_id": REPAIR_METHOD,
                      "source_current_va_2024": obs["current_va"],
                      "source_pyp_va_2024": obs["pyp_va"],
                      "source_pyp_go_2024": obs["pyp_go"],
                      "old_modeled_va_2026": sectors[node]["value_added"],
                      "reconstructed_modeled_va_2026": va,
                      "reconstructed_operative_A_2026": state[node]["operative_A_2026"],
                      "country_totals_preserved": True})
    return state, asset_state, trace
