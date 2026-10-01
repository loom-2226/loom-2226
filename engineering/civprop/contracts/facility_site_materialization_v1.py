"""CIVPROP Facility/Site Materialization V1.

Pure post-engine projection from generated infrastructure modules to stable sites,
materialized facilities, orbital/site projections, habitat settlement candidates,
and Atlas-facing facility classifications.

Materialization is not causal simulation state. Names are presentation-only.
Colocation is explicit-only. Precise coordinates/orbital elements are never invented.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .infrastructure_v1 import InfrastructureCatalog


FORMAT = "CIVPROP_FACILITY_SITE_MATERIALIZATION_V1"
CONTRACT_VERSION = "1.0.0"

COLOCATION_POLICY = "EXPLICIT_ONLY"
NAMING_POLICY = "PRESENTATION_ONLY"

SPATIAL_STATUSES = {
    "LOCATION_CLASS_ONLY",
    "EXACT_SURFACE_COORDINATES",
    "EXACT_ORBITAL_ELEMENTS",
}
ATLAS_TYPES = (
    "ORBITAL_HABITAT_PORT",
    "ORBITAL_SHIPYARD",
    "SURFACE_INBODY_PORT",
    "SURFACE_RESOURCE_PORT",
)


def _sid(prefix: str, *parts: object) -> str:
    payload = json.dumps(
        parts,
        separators=(",", ":"),
        sort_keys=False,
        allow_nan=False,
    ).encode()
    return f"{prefix}-" + hashlib.sha256(payload).hexdigest()[:20]


def _refs(raw: Mapping[str, Any], name: str) -> tuple[str, ...]:
    refs = tuple(str(x) for x in raw.get("provenance_refs", ()))
    if not refs:
        raise ValueError(f"{name} requires provenance")
    return refs


def _finite(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


@dataclass(frozen=True)
class SpatialAuthority:
    status: str
    surface_latitude_deg: Optional[float]
    surface_longitude_deg: Optional[float]
    orbital_semimajor_axis_km: Optional[float]
    orbital_eccentricity: Optional[float]
    orbital_inclination_deg: Optional[float]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class SiteBinding:
    binding_id: str
    site_key: str
    facility_ids: tuple[str, ...]
    operator_actor_ids: tuple[str, ...]
    spatial_authority: SpatialAuthority
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class PresentationName:
    site_key: str
    display_name: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class AtlasTypeRules:
    allowed_outputs: tuple[str, ...]


@dataclass(frozen=True)
class InitialStatePolicy:
    status: str
    materialization_policy: str
    location_ids: tuple[str, ...]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class FacilitySiteMaterializationPackage:
    format: str
    contract_version: str
    package_id: str
    colocation_policy: str
    naming_policy: str
    atlas_type_rules: AtlasTypeRules
    initial_state_policy: InitialStatePolicy
    site_bindings: tuple[SiteBinding, ...]
    presentation_names: tuple[PresentationName, ...]


@dataclass(frozen=True)
class InitialLocationCompatibilityV1:
    compatibility_state_id: str
    location_id: str
    status: str
    materialization_policy: str
    book_capital: float
    capacities: Mapping[str, float]


@dataclass(frozen=True)
class MaterializedModuleV1:
    module_materialization_id: str
    facility_id: str
    site_id: str
    project_archetype_id: str
    location_id: str
    owner_actor_id: str
    committed_year: int
    commissioned_year: int
    lifecycle_status: str
    capital: float
    capacities: Mapping[str, float]


@dataclass(frozen=True)
class MaterializedSiteV1:
    site_id: str
    site_key: str
    location_id: str
    parent_body_id: Optional[str]
    placement: str
    site_kind: str
    colocation_basis: str
    spatial_status: str
    surface_latitude_deg: Optional[float]
    surface_longitude_deg: Optional[float]
    orbital_semimajor_axis_km: Optional[float]
    orbital_eccentricity: Optional[float]
    orbital_inclination_deg: Optional[float]
    module_facility_ids: tuple[str, ...]
    owner_actor_ids: tuple[str, ...]
    operator_actor_ids: tuple[str, ...]
    first_commissioned_year: int
    lifecycle_status: str
    display_name: Optional[str]


@dataclass(frozen=True)
class MaterializedFacilityV1:
    materialized_facility_id: str
    site_id: str
    location_id: str
    parent_body_id: Optional[str]
    placement: str
    module_facility_ids: tuple[str, ...]
    module_archetype_ids: tuple[str, ...]
    owner_actor_ids: tuple[str, ...]
    operator_actor_ids: tuple[str, ...]
    first_commissioned_year: int
    lifecycle_status: str


@dataclass(frozen=True)
class OrbitalSiteV1:
    orbital_site_id: str
    site_id: str
    location_id: str
    parent_body_id: Optional[str]
    spatial_status: str
    semimajor_axis_km: Optional[float]
    eccentricity: Optional[float]
    inclination_deg: Optional[float]


@dataclass(frozen=True)
class SettlementProjectionV1:
    settlement_projection_id: str
    site_id: str
    location_id: str
    settlement_status: str
    demographic_status: str
    habitat_module_facility_ids: tuple[str, ...]


@dataclass(frozen=True)
class AtlasFacilityProjectionV1:
    atlas_facility_id: str
    materialized_facility_id: str
    site_id: str
    location_id: str
    placement: str
    facility_type_status: str
    facility_type: Optional[str]
    derivation_rule: str
    strategic_status: str
    display_name: Optional[str]


@dataclass(frozen=True)
class MaterializationResultV1:
    compatibility_states: tuple[InitialLocationCompatibilityV1, ...]
    modules: tuple[MaterializedModuleV1, ...]
    sites: tuple[MaterializedSiteV1, ...]
    facilities: tuple[MaterializedFacilityV1, ...]
    orbitals: tuple[OrbitalSiteV1, ...]
    settlements: tuple[SettlementProjectionV1, ...]
    atlas_facilities: tuple[AtlasFacilityProjectionV1, ...]


def _spatial(raw: Mapping[str, Any]) -> SpatialAuthority:
    status = str(raw.get("status"))
    if status not in SPATIAL_STATUSES:
        raise ValueError("invalid spatial authority status")

    lat = raw.get("surface_latitude_deg")
    lon = raw.get("surface_longitude_deg")
    sma = raw.get("orbital_semimajor_axis_km")
    ecc = raw.get("orbital_eccentricity")
    inc = raw.get("orbital_inclination_deg")

    if status == "LOCATION_CLASS_ONLY":
        if any(v is not None for v in (lat, lon, sma, ecc, inc)):
            raise ValueError(
                "LOCATION_CLASS_ONLY cannot carry precise spatial values"
            )
        lat_v = lon_v = sma_v = ecc_v = inc_v = None
    elif status == "EXACT_SURFACE_COORDINATES":
        if lat is None or lon is None or any(
            v is not None for v in (sma, ecc, inc)
        ):
            raise ValueError(
                "exact surface authority requires only latitude/longitude"
            )
        lat_v = _finite(lat, "surface latitude")
        lon_v = _finite(lon, "surface longitude")
        if not -90 <= lat_v <= 90 or not -180 <= lon_v <= 180:
            raise ValueError("surface coordinates out of range")
        sma_v = ecc_v = inc_v = None
    else:
        if (
            sma is None
            or ecc is None
            or inc is None
            or lat is not None
            or lon is not None
        ):
            raise ValueError(
                "exact orbital authority requires only orbital elements"
            )
        sma_v = _finite(sma, "semimajor axis")
        ecc_v = _finite(ecc, "eccentricity")
        inc_v = _finite(inc, "inclination")
        if sma_v <= 0 or not 0 <= ecc_v < 1 or not 0 <= inc_v <= 180:
            raise ValueError("orbital elements out of supported range")
        lat_v = lon_v = None

    return SpatialAuthority(
        status=status,
        surface_latitude_deg=lat_v,
        surface_longitude_deg=lon_v,
        orbital_semimajor_axis_km=sma_v,
        orbital_eccentricity=ecc_v,
        orbital_inclination_deg=inc_v,
        provenance_refs=_refs(raw, "spatial authority"),
    )


def load_facility_site_materialization_package(
    data: Mapping[str, Any],
) -> FacilitySiteMaterializationPackage:
    if data.get("format") != FORMAT:
        raise ValueError("unexpected facility/site materialization format")
    if data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected facility/site materialization version")
    if data.get("colocation_policy") != COLOCATION_POLICY:
        raise ValueError("Facility/Site V1 requires EXPLICIT_ONLY colocation")
    if data.get("naming_policy") != NAMING_POLICY:
        raise ValueError("Facility/Site V1 requires PRESENTATION_ONLY naming")

    rules = tuple(
        str(x)
        for x in data["atlas_type_rules"].get(
            "allowed_outputs",
            (),
        )
    )
    if tuple(sorted(rules)) != tuple(sorted(ATLAS_TYPES)):
        raise ValueError(
            "Atlas materialization output vocabulary must be pinned"
        )
    if "STRATEGIC_PORT" in rules:
        raise ValueError(
            "STRATEGIC_PORT is derived-metrics territory, not materialization"
        )

    initial_raw = data["initial_state_policy"]
    if initial_raw.get("status") != "UNQUALIFIED_COMPATIBILITY":
        raise ValueError(
            "initial off-world state must remain visibly unqualified"
        )
    if (
        initial_raw.get("materialization_policy")
        != "NEVER_MATERIALIZE_WITHOUT_MODULE_PROVENANCE"
    ):
        raise ValueError(
            "compatibility initial state may not become facilities"
        )
    initial_locations = tuple(
        sorted(str(x) for x in initial_raw.get("location_ids", ()))
    )
    if not initial_locations:
        raise ValueError(
            "initial compatibility policy requires location scope"
        )

    bindings = []
    seen_facilities: set[str] = set()
    seen_site_keys: set[str] = set()
    for raw in data.get("site_bindings", ()):
        facility_ids = tuple(sorted(str(x) for x in raw["facility_ids"]))
        if not facility_ids:
            raise ValueError("site binding requires facility_ids")
        overlap = seen_facilities.intersection(facility_ids)
        if overlap:
            raise ValueError("facility appears in multiple site bindings")
        seen_facilities.update(facility_ids)
        site_key = str(raw["site_key"])
        if not site_key or site_key in seen_site_keys:
            raise ValueError("site_key must be unique and non-empty")
        seen_site_keys.add(site_key)
        bindings.append(
            SiteBinding(
                binding_id=str(raw["binding_id"]),
                site_key=site_key,
                facility_ids=facility_ids,
                operator_actor_ids=tuple(
                    sorted(str(x) for x in raw.get("operator_actor_ids", ()))
                ),
                spatial_authority=_spatial(raw["spatial_authority"]),
                provenance_refs=_refs(raw, "site binding"),
            )
        )
    if len({x.binding_id for x in bindings}) != len(bindings):
        raise ValueError("duplicate site binding id")

    names = []
    for raw in data.get("presentation_names", ()):
        display_name = str(raw["display_name"]).strip()
        if not display_name:
            raise ValueError("presentation display name cannot be empty")
        names.append(
            PresentationName(
                site_key=str(raw["site_key"]),
                display_name=display_name,
                provenance_refs=_refs(raw, "presentation name"),
            )
        )
    if len({x.site_key for x in names}) != len(names):
        raise ValueError("duplicate presentation name for site_key")

    return FacilitySiteMaterializationPackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        package_id=str(data["package_id"]),
        colocation_policy=COLOCATION_POLICY,
        naming_policy=NAMING_POLICY,
        atlas_type_rules=AtlasTypeRules(allowed_outputs=rules),
        initial_state_policy=InitialStatePolicy(
            status="UNQUALIFIED_COMPATIBILITY",
            materialization_policy=(
                "NEVER_MATERIALIZE_WITHOUT_MODULE_PROVENANCE"
            ),
            location_ids=initial_locations,
            provenance_refs=_refs(
                initial_raw,
                "initial state policy",
            ),
        ),
        site_bindings=tuple(bindings),
        presentation_names=tuple(names),
    )


def load_facility_site_materialization_path(
    path: Path,
) -> FacilitySiteMaterializationPackage:
    return load_facility_site_materialization_package(
        json.loads(Path(path).read_text())
    )


class FacilitySiteMaterializerV1:
    def __init__(
        self,
        package: FacilitySiteMaterializationPackage,
        infrastructure_catalog: InfrastructureCatalog,
        locations: Sequence[Any],
    ):
        self.package = package
        self.catalog = infrastructure_catalog
        self.locations = {x.location_id: x for x in locations}
        self.binding_by_facility = {
            facility_id: binding
            for binding in package.site_bindings
            for facility_id in binding.facility_ids
        }
        self.name_by_site_key = {
            x.site_key: x.display_name
            for x in package.presentation_names
        }

    @staticmethod
    def _capacity_map(capacities: Any) -> dict[str, float]:
        return {
            key: float(getattr(capacities, key))
            for key in (
                "power",
                "resource",
                "industrial",
                "habitat",
                "shipyard",
                "transport",
            )
        }

    def _group_facilities(
        self,
        facilities: Sequence[Any],
    ) -> list[tuple[str, str, tuple[Any, ...]]]:
        grouped: dict[tuple[str, str], list[Any]] = {}
        for facility in sorted(
            facilities,
            key=lambda x: x.facility_id,
        ):
            if facility.location_id not in self.locations:
                raise ValueError(
                    "facility references unknown materialization location"
                )
            binding = self.binding_by_facility.get(facility.facility_id)
            if binding is None:
                site_key = f"UNBOUND:{facility.facility_id}"
                basis = "UNBOUND_SINGLE_MODULE"
            else:
                site_key = binding.site_key
                basis = "EXPLICIT_SITE_BINDING"
            grouped.setdefault((site_key, basis), []).append(facility)
        return [
            (key[0], key[1], tuple(items))
            for key, items in sorted(grouped.items())
        ]

    def _derive_atlas_type(
        self,
        placement: str,
        archetypes: set[str],
    ) -> tuple[str, Optional[str], str]:
        if placement == "SURFACE":
            if {"SURFACE_PORT", "RESOURCE_PLANT"} <= archetypes:
                return (
                    "KNOWN",
                    "SURFACE_RESOURCE_PORT",
                    "SURFACE_PORT_PLUS_RESOURCE_PLANT",
                )
            if {"SURFACE_PORT", "INDUSTRIAL_WORKSHOP"} <= archetypes:
                return (
                    "KNOWN",
                    "SURFACE_INBODY_PORT",
                    "SURFACE_PORT_PLUS_INDUSTRIAL_WORKSHOP",
                )
        elif placement == "ORBITAL":
            if {"LOGISTICS_NODE", "SHIPYARD"} <= archetypes:
                return (
                    "KNOWN",
                    "ORBITAL_SHIPYARD",
                    "LOGISTICS_NODE_PLUS_SHIPYARD",
                )
            if {"LOGISTICS_NODE", "HABITAT"} <= archetypes:
                return (
                    "KNOWN",
                    "ORBITAL_HABITAT_PORT",
                    "LOGISTICS_NODE_PLUS_HABITAT",
                )
        return (
            "UNKNOWN",
            None,
            "NO_QUALIFIED_COMPOSITION_RULE",
        )

    def materialize(
        self,
        facilities: Sequence[Any],
    ) -> MaterializationResultV1:
        compatibility_states: list[
            InitialLocationCompatibilityV1
        ] = []
        for location_id in self.package.initial_state_policy.location_ids:
            location = self.locations.get(location_id)
            if location is None:
                raise ValueError(
                    "initial compatibility policy references unknown location"
                )
            compatibility_states.append(
                InitialLocationCompatibilityV1(
                    compatibility_state_id=_sid(
                        "compat",
                        location_id,
                    ),
                    location_id=location_id,
                    status=self.package.initial_state_policy.status,
                    materialization_policy=(
                        self.package.initial_state_policy.materialization_policy
                    ),
                    book_capital=float(location.capital),
                    capacities=self._capacity_map(
                        location.capacities
                    ),
                )
            )

        modules: list[MaterializedModuleV1] = []
        sites: list[MaterializedSiteV1] = []
        materialized_facilities: list[MaterializedFacilityV1] = []
        orbitals: list[OrbitalSiteV1] = []
        settlements: list[SettlementProjectionV1] = []
        atlas_facilities: list[AtlasFacilityProjectionV1] = []

        for site_key, basis, members in self._group_facilities(facilities):
            location_ids = {x.location_id for x in members}
            if len(location_ids) != 1:
                raise ValueError(
                    "explicit colocation cannot cross runtime locations"
                )
            location_id = next(iter(location_ids))
            location = self.locations[location_id]
            placement = str(location.placement)
            parent_body_id = location.parent_body_id

            for member in members:
                archetype = self.catalog.by_id(
                    member.project_archetype_id
                )
                if placement not in archetype.allowed_placements:
                    raise ValueError(
                        "module placement incompatible with archetype"
                    )

            binding = self.binding_by_facility.get(
                members[0].facility_id
            )
            if binding is None:
                spatial = SpatialAuthority(
                    status="LOCATION_CLASS_ONLY",
                    surface_latitude_deg=None,
                    surface_longitude_deg=None,
                    orbital_semimajor_axis_km=None,
                    orbital_eccentricity=None,
                    orbital_inclination_deg=None,
                    provenance_refs=(
                        "DERIVED:LOCATION_CLASS_ONLY",
                    ),
                )
                operator_actor_ids: tuple[str, ...] = ()
            else:
                # Every member in this group must resolve to the same binding.
                if any(
                    self.binding_by_facility.get(x.facility_id) != binding
                    for x in members
                ):
                    raise ValueError(
                        "site grouping contains inconsistent bindings"
                    )
                spatial = binding.spatial_authority
                operator_actor_ids = binding.operator_actor_ids

            if (
                spatial.status == "EXACT_SURFACE_COORDINATES"
                and placement != "SURFACE"
            ):
                raise ValueError(
                    "surface coordinates require SURFACE placement"
                )
            if (
                spatial.status == "EXACT_ORBITAL_ELEMENTS"
                and placement != "ORBITAL"
            ):
                raise ValueError(
                    "orbital elements require ORBITAL placement"
                )

            site_id = _sid("site", location_id, site_key)
            materialized_facility_id = _sid("mf", site_id)
            module_ids = tuple(
                sorted(x.facility_id for x in members)
            )
            owner_ids = tuple(
                sorted({x.owner_actor_id for x in members})
            )
            archetype_ids = tuple(
                sorted(
                    {
                        x.project_archetype_id
                        for x in members
                    }
                )
            )
            first_commissioned = min(
                int(x.commissioned_year)
                for x in members
            )
            statuses = {str(x.status) for x in members}
            lifecycle_status = (
                next(iter(statuses))
                if len(statuses) == 1
                else "MIXED_MODULE_STATUS"
            )
            display_name = self.name_by_site_key.get(site_key)
            site_kind = {
                "SURFACE": "SURFACE_SITE",
                "ORBITAL": "ORBITAL_SITE",
                "FREE_SPACE": "FREE_SPACE_SITE",
            }[placement]

            sites.append(
                MaterializedSiteV1(
                    site_id=site_id,
                    site_key=site_key,
                    location_id=location_id,
                    parent_body_id=parent_body_id,
                    placement=placement,
                    site_kind=site_kind,
                    colocation_basis=basis,
                    spatial_status=spatial.status,
                    surface_latitude_deg=spatial.surface_latitude_deg,
                    surface_longitude_deg=spatial.surface_longitude_deg,
                    orbital_semimajor_axis_km=(
                        spatial.orbital_semimajor_axis_km
                    ),
                    orbital_eccentricity=(
                        spatial.orbital_eccentricity
                    ),
                    orbital_inclination_deg=(
                        spatial.orbital_inclination_deg
                    ),
                    module_facility_ids=module_ids,
                    owner_actor_ids=owner_ids,
                    operator_actor_ids=operator_actor_ids,
                    first_commissioned_year=first_commissioned,
                    lifecycle_status=lifecycle_status,
                    display_name=display_name,
                )
            )
            materialized_facilities.append(
                MaterializedFacilityV1(
                    materialized_facility_id=materialized_facility_id,
                    site_id=site_id,
                    location_id=location_id,
                    parent_body_id=parent_body_id,
                    placement=placement,
                    module_facility_ids=module_ids,
                    module_archetype_ids=archetype_ids,
                    owner_actor_ids=owner_ids,
                    operator_actor_ids=operator_actor_ids,
                    first_commissioned_year=first_commissioned,
                    lifecycle_status=lifecycle_status,
                )
            )

            for member in sorted(
                members,
                key=lambda x: x.facility_id,
            ):
                modules.append(
                    MaterializedModuleV1(
                        module_materialization_id=_sid(
                            "mm",
                            site_id,
                            member.facility_id,
                        ),
                        facility_id=member.facility_id,
                        site_id=site_id,
                        project_archetype_id=(
                            member.project_archetype_id
                        ),
                        location_id=member.location_id,
                        owner_actor_id=member.owner_actor_id,
                        committed_year=int(member.committed_year),
                        commissioned_year=int(
                            member.commissioned_year
                        ),
                        lifecycle_status=str(member.status),
                        capital=float(member.capital),
                        capacities=self._capacity_map(
                            member.capacities
                        ),
                    )
                )

            if placement == "ORBITAL":
                orbitals.append(
                    OrbitalSiteV1(
                        orbital_site_id=_sid("orb", site_id),
                        site_id=site_id,
                        location_id=location_id,
                        parent_body_id=parent_body_id,
                        spatial_status=spatial.status,
                        semimajor_axis_km=(
                            spatial.orbital_semimajor_axis_km
                        ),
                        eccentricity=(
                            spatial.orbital_eccentricity
                        ),
                        inclination_deg=(
                            spatial.orbital_inclination_deg
                        ),
                    )
                )

            habitat_ids = tuple(
                sorted(
                    x.facility_id
                    for x in members
                    if x.project_archetype_id == "HABITAT"
                )
            )
            if habitat_ids:
                settlements.append(
                    SettlementProjectionV1(
                        settlement_projection_id=_sid(
                            "settlement",
                            site_id,
                        ),
                        site_id=site_id,
                        location_id=location_id,
                        settlement_status=(
                            "HABITAT_INFRASTRUCTURE_CANDIDATE"
                        ),
                        demographic_status="DEFERRED_GAP_014",
                        habitat_module_facility_ids=habitat_ids,
                    )
                )

            type_status, facility_type, rule = (
                self._derive_atlas_type(
                    placement,
                    set(archetype_ids),
                )
            )
            if facility_type == "STRATEGIC_PORT":
                raise ValueError(
                    "STRATEGIC_PORT cannot be materialized directly"
                )
            atlas_facilities.append(
                AtlasFacilityProjectionV1(
                    atlas_facility_id=_sid(
                        "atlasfac",
                        materialized_facility_id,
                    ),
                    materialized_facility_id=(
                        materialized_facility_id
                    ),
                    site_id=site_id,
                    location_id=location_id,
                    placement=placement,
                    facility_type_status=type_status,
                    facility_type=facility_type,
                    derivation_rule=rule,
                    strategic_status="DEFERRED_GAP_015",
                    display_name=display_name,
                )
            )

        return MaterializationResultV1(
            compatibility_states=tuple(compatibility_states),
            modules=tuple(modules),
            sites=tuple(sites),
            facilities=tuple(materialized_facilities),
            orbitals=tuple(orbitals),
            settlements=tuple(settlements),
            atlas_facilities=tuple(atlas_facilities),
        )


__all__ = [
    "ATLAS_TYPES",
    "CONTRACT_VERSION",
    "FORMAT",
    "AtlasFacilityProjectionV1",
    "AtlasTypeRules",
    "FacilitySiteMaterializationPackage",
    "InitialLocationCompatibilityV1",
    "InitialStatePolicy",
    "FacilitySiteMaterializerV1",
    "MaterializationResultV1",
    "MaterializedFacilityV1",
    "MaterializedModuleV1",
    "MaterializedSiteV1",
    "OrbitalSiteV1",
    "PresentationName",
    "SettlementProjectionV1",
    "SiteBinding",
    "SpatialAuthority",
    "load_facility_site_materialization_package",
    "load_facility_site_materialization_path",
]
