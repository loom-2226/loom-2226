"""Pure functions for the lean Earth biosynthetic successor experiment."""

from __future__ import annotations

import math


def interpolate_anchors(anchors, year: int) -> float:
    """Piecewise-linear interpolation with endpoint clamping."""
    points = sorted((int(item[0]), float(item[1])) for item in anchors)
    if year <= points[0][0]:
        return points[0][1]
    if year >= points[-1][0]:
        return points[-1][1]
    for (y0, v0), (y1, v1) in zip(points, points[1:]):
        if y0 <= year <= y1:
            weight = (year - y0) / (y1 - y0)
            return v0 + weight * (v1 - v0)
    raise AssertionError("unreachable interpolation interval")


def interpolate_records(records: list[dict], year: int, field: str) -> float:
    return interpolate_anchors([[row["year"], row[field]] for row in records], year)


def schedule_by_age(schedule, age: float) -> float:
    """Linearly interpolate a compact age schedule."""
    return interpolate_anchors(schedule, age)


def fertility_kernel(tfr: float, mean_age: float, sd_age: float, age_starts) -> dict[int, float]:
    """Return annual ASFR per woman for five-year age groups.

    The returned rates integrate to the requested TFR when multiplied by the
    five-year width. This keeps fertility level separate from timing.
    """
    if tfr < 0 or sd_age <= 0:
        raise ValueError("invalid fertility parameters")
    ages = tuple(sorted(int(age) for age in age_starts))
    raw = {
        age: math.exp(-0.5 * (((age + 2.5) - mean_age) / sd_age) ** 2)
        for age in ages
    }
    total = sum(raw.values())
    if total <= 0:
        raise ValueError("empty fertility kernel")
    return {age: (tfr / 5.0) * raw[age] / total for age in ages}


def medicine_access(year: int, parameters: dict) -> dict[str, float]:
    medicine = parameters["medicine"]
    return {
        "broad": interpolate_anchors(medicine["broad_access"], year),
        "high_end": interpolate_anchors(medicine["high_end_access"], year),
        "extreme": interpolate_anchors(medicine["extreme_access"], year),
    }


def medicine_progress(year: int, parameters: dict) -> dict[str, float]:
    """Return diffusion progress relative to the WPP 2100 mortality boundary."""
    current = medicine_access(year, parameters)
    medicine = parameters["medicine"]
    result = {}
    for name, key in (("broad", "broad_access"), ("high_end", "high_end_access"),
                      ("extreme", "extreme_access")):
        baseline = float(medicine[key][0][1])
        result[name] = max(0.0, (current[name] - baseline) / max(1e-12, 1.0 - baseline))
    return result


def medicine_mortality_multiplier(age: int, year: int, parameters: dict) -> float:
    """Population-average mortality factor from nested access mixtures."""
    medicine = parameters["medicine"]
    access = medicine_progress(year, parameters)
    broad_treated = schedule_by_age(medicine["broad_mortality_multiplier_by_age"], age)
    broad = 1.0 - access["broad"] * (1.0 - broad_treated)
    high = 1.0
    if age >= 65:
        high = 1.0 - access["high_end"] * (
            1.0 - float(medicine["high_end_mortality_multiplier_age_65_plus"])
        )
    extreme = 1.0
    if age >= 100:
        extreme = 1.0 - access["extreme"] * (
            1.0 - float(medicine["extreme_mortality_multiplier_age_100_plus"])
        )
    result = broad * high * extreme
    if not 0 < result <= 1:
        raise ValueError("invalid medicine mortality multiplier")
    return result


def propagate_one_year(
    cohorts: dict[str, dict[int, float]],
    mortality: dict[str, dict[int, float]],
    tfr: float,
    mean_age: float,
    sd_age: float,
    male_birth_share: float,
) -> dict:
    """Advance two-sex five-year cohorts by one year with exact mass accounting."""
    if set(cohorts) != {"M", "F"} or not 0 < male_birth_share < 1:
        raise ValueError("invalid cohort sexes or birth sex ratio")
    ages = tuple(sorted(cohorts["M"]))
    if ages != tuple(sorted(cohorts["F"])) or any(b - a != 5 for a, b in zip(ages, ages[1:])):
        raise ValueError("cohort ages must be aligned five-year groups")
    if any(set(mortality[sex]) != set(ages) for sex in ("M", "F")):
        raise ValueError("mortality coverage differs from cohorts")

    fertile = [age for age in ages if 15 <= age <= 70]
    asfr = fertility_kernel(tfr, mean_age, sd_age, fertile)
    births = sum(cohorts["F"][age] * asfr[age] for age in fertile)

    next_cohorts = {sex: {age: 0.0 for age in ages} for sex in ("M", "F")}
    deaths = 0.0
    terminal = ages[-1]
    for sex in ("M", "F"):
        for age in ages:
            population = float(cohorts[sex][age])
            q = float(mortality[sex][age])
            if population < 0 or not 0 <= q <= 1:
                raise ValueError("invalid population or mortality probability")
            died = population * q
            survivors = population - died
            deaths += died
            if age == terminal:
                next_cohorts[sex][age] += survivors
            else:
                advancing = survivors / 5.0
                next_cohorts[sex][age] += survivors - advancing
                next_cohorts[sex][age + 5] += advancing

    next_cohorts["M"][0] += births * male_birth_share
    next_cohorts["F"][0] += births * (1.0 - male_birth_share)
    return {"cohorts": next_cohorts, "births": births, "deaths": deaths}


def labor_from_cohorts(
    cohorts: dict[str, dict[int, float]],
    year: int,
    parameters: dict,
    calibration: float,
) -> dict[str, float]:
    """Compute biological effective labor from health, participation, and hours."""
    labor = parameters["biological_labor"]
    access = medicine_progress(year, parameters)
    recovery = float(labor["medical_health_recovery_fraction"]) * min(
        1.0, access["broad"] + 0.5 * access["high_end"] + 0.1 * access["extreme"]
    )
    effective = 0.0
    capable = 0.0
    under_20_labor = 0.0
    for sex in ("M", "F"):
        for age, population in cohorts[sex].items():
            midpoint = age + 2.5
            base_health = schedule_by_age(labor["baseline_functional_health_by_age"], midpoint)
            health = min(1.0, base_health + (1.0 - base_health) * recovery)
            participation = (0.0 if age < 20 else
                             schedule_by_age(labor["participation_by_age"], midpoint))
            hours = (0.0 if age < 20 else
                     schedule_by_age(labor["paid_hours_by_age"], midpoint))
            contribution = population * health * participation * hours * calibration
            effective += contribution
            if age >= 20:
                capable += population * health
            else:
                under_20_labor += contribution
    if calibration < 0 or effective < 0 or effective > capable + 1e-6:
        raise ValueError("biological labor exceeds plausible capability")
    return {
        "effective_biological_labor": effective,
        "labor_capable_population": capable,
        "under_20_labor": under_20_labor,
        "calibration": calibration,
    }


def synthetic_step(
    stock: float,
    biological_population: float,
    support_index: float,
    year: int,
    parameters: dict,
) -> dict[str, float]:
    """Advance the recognized synthetic-person stock without biological analogies."""
    synthetic = parameters["synthetic_persons"]
    if min(stock, biological_population, support_index) < 0:
        raise ValueError("negative synthetic driver")
    lower, upper = map(float, synthetic["support_index_bounds"])
    support = min(upper, max(lower, support_index))
    legal = interpolate_anchors(synthetic["legal_access"], year)
    additions = (
        biological_population
        * float(synthetic["annual_instantiation_per_biological_person"])
        * legal
        * support ** float(synthetic["support_index_exponent"])
    )
    losses = stock * float(synthetic["annual_retirement_loss_rate"])
    migration = float(synthetic["net_global_migration"])
    population = stock + additions - losses + migration
    if population < 0:
        raise ValueError("synthetic population became negative")
    participation = interpolate_anchors(synthetic["labor_participation"], year)
    capacity = interpolate_anchors(synthetic["effective_labor_per_participant"], year)
    effective_labor = population * participation * capacity
    if population == 0 and effective_labor != 0:
        raise ValueError("synthetic labor without synthetic persons")
    return {
        "population": population,
        "additions": additions,
        "retirements_losses": losses,
        "net_migration": migration,
        "labor_participation": participation,
        "effective_labor_per_participant": capacity,
        "effective_labor": effective_labor,
        "support_index": support,
        "legal_access": legal,
    }


def machine_task_step(
    previous_ratio: float,
    automation_index: float,
    biological_labor: float,
    parameters: dict,
) -> dict[str, float]:
    """Convert incremental automation capacity into non-person task capacity."""
    settings = parameters["nonperson_machine_tasks"]
    if min(previous_ratio, automation_index, biological_labor) < 0:
        raise ValueError("negative machine-task driver")
    target = min(
        float(settings["maximum_machine_to_biological_task_ratio"]),
        float(settings["task_ratio_elasticity_above_2100_index"])
        * max(0.0, automation_index - 1.0),
    )
    speed = float(settings["annual_adjustment_speed"])
    ratio = previous_ratio + speed * (target - previous_ratio)
    capacity = biological_labor * ratio
    return {
        "ratio": ratio,
        "target_ratio": target,
        "capacity": capacity,
        "counted_as_population": False,
    }


def blended_normalized_weights(
    absolute_capacity: dict,
    intensity: dict,
    absolute_weight: float = 0.75,
) -> dict:
    """Blend normalized absolute capacity and intensity without country exceptions."""
    if set(absolute_capacity) != set(intensity) or not absolute_capacity:
        raise ValueError("allocation signals must have identical non-empty keys")
    if not 0.0 <= absolute_weight <= 1.0:
        raise ValueError("absolute allocation weight outside [0, 1]")
    if any(float(value) < 0.0 for value in (*absolute_capacity.values(), *intensity.values())):
        raise ValueError("negative allocation signal")
    epsilon = 1e-30
    absolute_total = sum(float(value) for value in absolute_capacity.values())
    intensity_total = sum(float(value) for value in intensity.values())
    if absolute_total <= 0.0 or intensity_total <= 0.0:
        raise ValueError("allocation signal has no positive support")
    intensity_weight = 1.0 - absolute_weight
    raw = {
        key: (max(epsilon, float(absolute_capacity[key]) / absolute_total) ** absolute_weight)
        * (max(epsilon, float(intensity[key]) / intensity_total) ** intensity_weight)
        for key in absolute_capacity
    }
    total = sum(raw.values())
    return {key: value / total for key, value in raw.items()}


def bounded_weighted_allocation(total: float, weights: dict, capacities: dict) -> dict:
    """Allocate a global total by weights while respecting generic node capacities."""
    if total < 0.0 or set(weights) != set(capacities) or not weights:
        raise ValueError("invalid bounded allocation")
    if any(float(value) < 0.0 for value in (*weights.values(), *capacities.values())):
        raise ValueError("negative weight or capacity")
    if total > sum(float(value) for value in capacities.values()) + 1e-9:
        raise ValueError("global total exceeds aggregate capacity")
    result = {key: 0.0 for key in weights}
    remaining = float(total)
    active = set(weights)
    while remaining > max(1e-9, total * 1e-14) and active:
        weight_total = sum(float(weights[key]) for key in active)
        if weight_total <= 0.0:
            weight_total = float(len(active))
            shares = {key: 1.0 / weight_total for key in active}
        else:
            shares = {key: float(weights[key]) / weight_total for key in active}
        distributed = 0.0
        saturated = set()
        for key in sorted(active):
            room = float(capacities[key]) - result[key]
            addition = min(room, remaining * shares[key])
            result[key] += addition
            distributed += addition
            if room - addition <= max(1e-12, float(capacities[key]) * 1e-14):
                saturated.add(key)
        remaining -= distributed
        active -= saturated
        if distributed <= 0.0:
            break
    if remaining > max(1e-6, total * 1e-12):
        raise ValueError("bounded allocation failed to conserve total")
    return result
