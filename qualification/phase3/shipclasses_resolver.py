from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Tuple

from shipclasses_geometry_resolver import resolve_mass_centroids_B

Vector3 = Tuple[float, float, float]


class PhysicalContractError(ValueError):
    pass


@dataclass(frozen=True)
class MassContribution:
    source_id: str
    mass_kg: float
    centroid_B_m: Vector3
    authority_status: str


def _state(instance_state: Optional[Mapping[str, str]], domain: str, default: str) -> str:
    return str((instance_state or {}).get(domain, default))


def _validate_state(conn: sqlite3.Connection, domain: str, state: str) -> None:
    row = conn.execute(
        "SELECT 1 FROM configuration_state WHERE configuration_domain_id=? AND state_code=?",
        (domain, state),
    ).fetchone()
    if row is None:
        raise PhysicalContractError(f"Illegal/unknown configuration state {domain}={state}")


def resolve_active_components(conn: sqlite3.Connection, instance_state: Optional[Mapping[str, str]] = None) -> Dict[str, bool]:
    domains = {
        r[0]: _state(instance_state, r[0], r[1])
        for r in conn.execute("SELECT configuration_domain_id,initial_state FROM configuration_domain")
    }
    for domain, state in domains.items():
        _validate_state(conn, domain, state)

    active: Dict[str, bool] = {r[0]: True for r in conn.execute("SELECT component_id FROM physical_component")}
    rules = conn.execute(
        "SELECT component_id,configuration_domain_id,state_code,active FROM component_state_rule"
    ).fetchall()
    for component_id, domain, state_code, is_active in rules:
        if domains[domain] == state_code:
            active[component_id] = bool(is_active)
    return active


def _store_centroid(row: sqlite3.Row) -> Vector3:
    model = row["centroid_model_type"]
    payload = json.loads(row["centroid_model_json"] or "{}")
    if model != "FIXED" or "centroid_B_m" not in payload:
        raise PhysicalContractError(f"Unsupported store centroid model for {row['store_id']}: {model}")
    values = tuple(float(v) for v in payload["centroid_B_m"])
    if len(values) != 3 or not all(math.isfinite(v) for v in values):
        raise PhysicalContractError(f"Invalid centroid for {row['store_id']}")
    return values  # type: ignore[return-value]


def resolve_mass_contributions(
    conn: sqlite3.Connection,
    instance_state: Optional[Mapping[str, str]] = None,
    store_quantities_kg: Optional[Mapping[str, float]] = None,
) -> Iterable[MassContribution]:
    conn.row_factory = sqlite3.Row
    active = resolve_active_components(conn, instance_state)
    transformed_centroids = resolve_mass_centroids_B(conn)

    for row in conn.execute(
        "SELECT mass_element_id,component_id,reference_mass_kg,authority_status FROM mass_element"
    ):
        if not active.get(row["component_id"], False):
            continue
        mass = float(row["reference_mass_kg"])
        if mass < 0 or not math.isfinite(mass):
            raise PhysicalContractError(f"Invalid mass for {row['mass_element_id']}")
        yield MassContribution(
            row["mass_element_id"],
            mass,
            transformed_centroids[row["mass_element_id"]],
            row["authority_status"],
        )

    for row in conn.execute(
        "SELECT store_id,component_id,capacity_kg,reference_quantity_kg,minimum_protected_quantity_kg,centroid_model_type,centroid_model_json,authority_status FROM mutable_store"
    ):
        if not active.get(row["component_id"], False):
            continue
        quantity = float((store_quantities_kg or {}).get(row["store_id"], row["reference_quantity_kg"]))
        capacity = float(row["capacity_kg"])
        if not math.isfinite(quantity) or quantity < 0 or quantity > capacity:
            raise PhysicalContractError(f"Store quantity out of bounds for {row['store_id']}: {quantity}")
        protected = row["minimum_protected_quantity_kg"]
        if protected is not None and quantity < float(protected):
            raise PhysicalContractError(f"Store quantity violates protected minimum for {row['store_id']}: {quantity}")
        if quantity == 0:
            continue
        yield MassContribution(row["store_id"], quantity, _store_centroid(row), row["authority_status"])


def compute_mass_properties(
    conn: sqlite3.Connection,
    instance_state: Optional[Mapping[str, str]] = None,
    store_quantities_kg: Optional[Mapping[str, float]] = None,
) -> Dict[str, object]:
    contributions = list(resolve_mass_contributions(conn, instance_state, store_quantities_kg))
    total = sum(c.mass_kg for c in contributions)
    if total <= 0 or not math.isfinite(total):
        raise PhysicalContractError("Resolved spacecraft mass must be finite and positive")
    com = tuple(sum(c.mass_kg * c.centroid_B_m[i] for c in contributions) / total for i in range(3))
    return {
        "mass_kg": total,
        "center_of_mass_B_m": list(com),
        "contribution_count": len(contributions),
        "contributions": [
            {
                "source_id": c.source_id,
                "mass_kg": c.mass_kg,
                "centroid_B_m": list(c.centroid_B_m),
                "authority_status": c.authority_status,
            }
            for c in contributions
        ],
    }


def validate_configuration_transition(conn: sqlite3.Connection, domain: str, from_state: str, to_state: str) -> Dict[str, object]:
    _validate_state(conn, domain, from_state)
    _validate_state(conn, domain, to_state)
    row = conn.execute(
        "SELECT transition_mode,duration_s,transition_model_version FROM configuration_transition WHERE configuration_domain_id=? AND from_state=? AND to_state=?",
        (domain, from_state, to_state),
    ).fetchone()
    if row is None:
        raise PhysicalContractError(f"Transition not admitted: {domain} {from_state}->{to_state}")
    return {"allowed": True, "transition_mode": row[0], "duration_s": row[1], "transition_model_version": row[2]}
