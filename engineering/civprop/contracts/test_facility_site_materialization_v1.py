"""Hostile tests for CIVPROP Facility/Site Materialization V1."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from .facility_site_materialization_v1 import (
    FacilitySiteMaterializerV1,
    load_facility_site_materialization_package,
)
from .infrastructure_v1 import load_infrastructure_catalog


HERE = Path(__file__).resolve().parent
PARAMETERS = HERE / "facility_site_materialization_v1.json"
INFRASTRUCTURE = HERE / "infrastructure_archetypes_v1.json"


def _caps(**kwargs):
    base = dict(
        power=0.0,
        resource=0.0,
        industrial=0.0,
        habitat=0.0,
        shipyard=0.0,
        transport=0.0,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def _facility(
    fid,
    archetype,
    location,
    *,
    owner="AUS",
    committed=2028,
    commissioned=2030,
    status="ACTIVE",
    **capacities,
):
    return SimpleNamespace(
        facility_id=fid,
        project_archetype_id=archetype,
        location_id=location,
        owner_actor_id=owner,
        committed_year=committed,
        commissioned_year=commissioned,
        status=status,
        capital=1.0,
        capacities=_caps(**capacities),
    )


def _locations():
    return (
        SimpleNamespace(
            location_id="EARTH_ORBIT",
            parent_body_id="EARTH",
            placement="ORBITAL",
            capital=0.0,
            capacities=_caps(),
        ),
        SimpleNamespace(
            location_id="LUNA_SURFACE",
            parent_body_id="MOON",
            placement="SURFACE",
            capital=0.0,
            capacities=_caps(),
        ),
        SimpleNamespace(
            location_id="CISLUNAR_FREE_SPACE",
            parent_body_id=None,
            placement="FREE_SPACE",
            capital=0.0,
            capacities=_caps(),
        ),
    )


def _package_with_binding(
    facility_ids,
    *,
    site_key="LUNA_BASE_1",
    name=None,
    operator_actor_ids=(),
    spatial=None,
):
    raw = json.loads(PARAMETERS.read_text())
    raw["site_bindings"] = [
        {
            "binding_id": "BIND-1",
            "site_key": site_key,
            "facility_ids": list(facility_ids),
            "operator_actor_ids": list(operator_actor_ids),
            "spatial_authority": spatial
            or {
                "status": "LOCATION_CLASS_ONLY",
                "surface_latitude_deg": None,
                "surface_longitude_deg": None,
                "orbital_semimajor_axis_km": None,
                "orbital_eccentricity": None,
                "orbital_inclination_deg": None,
                "provenance_refs": ["test:spatial"],
            },
            "provenance_refs": ["test:binding"],
        }
    ]
    if name is not None:
        raw["presentation_names"] = [
            {
                "site_key": site_key,
                "display_name": name,
                "provenance_refs": ["test:name"],
            }
        ]
    return load_facility_site_materialization_package(raw)


class FacilitySiteMaterializationV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_infrastructure_catalog(INFRASTRUCTURE)

    def test_default_policy_is_explicit_colocation_and_no_legacy_answer_sheet(self):
        package = load_facility_site_materialization_package(
            json.loads(PARAMETERS.read_text())
        )
        self.assertEqual(package.colocation_policy, "EXPLICIT_ONLY")
        self.assertEqual(package.naming_policy, "PRESENTATION_ONLY")
        self.assertEqual(package.site_bindings, ())
        self.assertEqual(
            package.initial_state_policy.status,
            "UNQUALIFIED_COMPATIBILITY",
        )
        self.assertEqual(
            package.initial_state_policy.materialization_policy,
            "NEVER_MATERIALIZE_WITHOUT_MODULE_PROVENANCE",
        )
        self.assertNotIn(
            "STRATEGIC_PORT",
            package.atlas_type_rules.allowed_outputs,
        )

    def test_initial_compatibility_state_is_exposed_but_never_materialized(self):
        locations = list(_locations())
        locations[0] = SimpleNamespace(
            location_id="EARTH_ORBIT",
            parent_body_id="EARTH",
            placement="ORBITAL",
            capital=15.0,
            capacities=_caps(
                power=5.0,
                habitat=50.0,
                industrial=200.0,
                transport=800.0,
            ),
        )
        materializer = FacilitySiteMaterializerV1(
            load_facility_site_materialization_package(
                json.loads(PARAMETERS.read_text())
            ),
            self.catalog,
            tuple(locations),
        )
        result = materializer.materialize(())
        self.assertEqual(len(result.compatibility_states), 3)
        state = next(
            x
            for x in result.compatibility_states
            if x.location_id == "EARTH_ORBIT"
        )
        self.assertEqual(state.location_id, "EARTH_ORBIT")
        self.assertEqual(state.status, "UNQUALIFIED_COMPATIBILITY")
        self.assertEqual(state.capacities["power"], 5.0)
        self.assertEqual(state.capacities["transport"], 800.0)
        self.assertEqual(result.sites, ())
        self.assertEqual(result.facilities, ())
        self.assertEqual(result.atlas_facilities, ())

    def test_unbound_modules_do_not_colocate_just_because_location_owner_match(self):
        materializer = FacilitySiteMaterializerV1(
            load_facility_site_materialization_package(
                json.loads(PARAMETERS.read_text())
            ),
            self.catalog,
            _locations(),
        )
        facilities = (
            _facility(
                "PORT-1",
                "SURFACE_PORT",
                "LUNA_SURFACE",
                transport=1000,
            ),
            _facility(
                "RESOURCE-1",
                "RESOURCE_PLANT",
                "LUNA_SURFACE",
                resource=100,
                industrial=25,
            ),
        )
        result = materializer.materialize(facilities)
        self.assertEqual(len(result.sites), 2)
        self.assertEqual(
            {x.colocation_basis for x in result.sites},
            {"UNBOUND_SINGLE_MODULE"},
        )

    def test_explicit_binding_colocates_and_preserves_module_identity(self):
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(("PORT-1", "RESOURCE-1")),
            self.catalog,
            _locations(),
        )
        facilities = (
            _facility(
                "PORT-1",
                "SURFACE_PORT",
                "LUNA_SURFACE",
                transport=1000,
            ),
            _facility(
                "RESOURCE-1",
                "RESOURCE_PLANT",
                "LUNA_SURFACE",
                resource=100,
                industrial=25,
            ),
        )
        result = materializer.materialize(facilities)
        self.assertEqual(len(result.sites), 1)
        self.assertEqual(len(result.facilities), 1)
        self.assertEqual(len(result.modules), 2)
        site = result.sites[0]
        self.assertEqual(
            site.module_facility_ids,
            ("PORT-1", "RESOURCE-1"),
        )
        self.assertEqual(site.owner_actor_ids, ("AUS",))
        self.assertEqual(site.operator_actor_ids, ())
        self.assertEqual(site.placement, "SURFACE")
        self.assertEqual(site.parent_body_id, "MOON")

    def test_surface_resource_port_is_derived_from_composition(self):
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(("PORT-1", "RESOURCE-1")),
            self.catalog,
            _locations(),
        )
        result = materializer.materialize(
            (
                _facility("PORT-1", "SURFACE_PORT", "LUNA_SURFACE"),
                _facility("RESOURCE-1", "RESOURCE_PLANT", "LUNA_SURFACE"),
            )
        )
        projected = result.atlas_facilities[0]
        self.assertEqual(projected.facility_type_status, "KNOWN")
        self.assertEqual(
            projected.facility_type,
            "SURFACE_RESOURCE_PORT",
        )

    def test_surface_inbody_port_is_derived_from_composition(self):
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(("PORT-1", "IND-1")),
            self.catalog,
            _locations(),
        )
        result = materializer.materialize(
            (
                _facility("PORT-1", "SURFACE_PORT", "LUNA_SURFACE"),
                _facility("IND-1", "INDUSTRIAL_WORKSHOP", "LUNA_SURFACE"),
            )
        )
        self.assertEqual(
            result.atlas_facilities[0].facility_type,
            "SURFACE_INBODY_PORT",
        )

    def test_orbital_habitat_port_is_derived_from_composition(self):
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(("LOG-1", "HAB-1"), site_key="EO-1"),
            self.catalog,
            _locations(),
        )
        result = materializer.materialize(
            (
                _facility("LOG-1", "LOGISTICS_NODE", "EARTH_ORBIT"),
                _facility("HAB-1", "HABITAT", "EARTH_ORBIT"),
            )
        )
        self.assertEqual(
            result.atlas_facilities[0].facility_type,
            "ORBITAL_HABITAT_PORT",
        )
        self.assertEqual(len(result.orbitals), 1)

    def test_orbital_shipyard_is_derived_but_strategic_port_never_is(self):
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(("LOG-1", "YARD-1"), site_key="EO-YARD"),
            self.catalog,
            _locations(),
        )
        result = materializer.materialize(
            (
                _facility("LOG-1", "LOGISTICS_NODE", "EARTH_ORBIT"),
                _facility("YARD-1", "SHIPYARD", "EARTH_ORBIT"),
            )
        )
        self.assertEqual(
            result.atlas_facilities[0].facility_type,
            "ORBITAL_SHIPYARD",
        )
        self.assertNotEqual(
            result.atlas_facilities[0].facility_type,
            "STRATEGIC_PORT",
        )

    def test_unknown_composition_does_not_invent_atlas_type(self):
        materializer = FacilitySiteMaterializerV1(
            load_facility_site_materialization_package(
                json.loads(PARAMETERS.read_text())
            ),
            self.catalog,
            _locations(),
        )
        result = materializer.materialize(
            (
                _facility("POWER-1", "POWER_PLANT", "LUNA_SURFACE"),
            )
        )
        self.assertEqual(
            result.atlas_facilities[0].facility_type_status,
            "UNKNOWN",
        )
        self.assertIsNone(
            result.atlas_facilities[0].facility_type,
        )

    def test_name_is_presentation_only_and_does_not_change_identity(self):
        facilities = (
            _facility("PORT-1", "SURFACE_PORT", "LUNA_SURFACE"),
            _facility("RESOURCE-1", "RESOURCE_PLANT", "LUNA_SURFACE"),
        )
        a = FacilitySiteMaterializerV1(
            _package_with_binding(
                ("PORT-1", "RESOURCE-1"),
                name="Lunar Base Alpha",
            ),
            self.catalog,
            _locations(),
        ).materialize(facilities)
        b = FacilitySiteMaterializerV1(
            _package_with_binding(
                ("PORT-1", "RESOURCE-1"),
                name="Kevin's Extremely Serious Moon Warehouse",
            ),
            self.catalog,
            _locations(),
        ).materialize(facilities)
        self.assertEqual(a.sites[0].site_id, b.sites[0].site_id)
        self.assertEqual(
            a.facilities[0].materialized_facility_id,
            b.facilities[0].materialized_facility_id,
        )
        self.assertEqual(
            a.atlas_facilities[0].facility_type,
            b.atlas_facilities[0].facility_type,
        )
        self.assertNotEqual(
            a.sites[0].display_name,
            b.sites[0].display_name,
        )

    def test_surface_coordinates_require_explicit_spatial_authority(self):
        spatial = {
            "status": "EXACT_SURFACE_COORDINATES",
            "surface_latitude_deg": -89.5,
            "surface_longitude_deg": 42.0,
            "orbital_semimajor_axis_km": None,
            "orbital_eccentricity": None,
            "orbital_inclination_deg": None,
            "provenance_refs": ["test:surveyed"],
        }
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(
                ("PORT-1",),
                spatial=spatial,
            ),
            self.catalog,
            _locations(),
        )
        result = materializer.materialize(
            (_facility("PORT-1", "SURFACE_PORT", "LUNA_SURFACE"),)
        )
        site = result.sites[0]
        self.assertEqual(site.spatial_status, "EXACT_SURFACE_COORDINATES")
        self.assertEqual(site.surface_latitude_deg, -89.5)
        self.assertEqual(site.surface_longitude_deg, 42.0)

    def test_orbital_elements_require_explicit_authority(self):
        spatial = {
            "status": "EXACT_ORBITAL_ELEMENTS",
            "surface_latitude_deg": None,
            "surface_longitude_deg": None,
            "orbital_semimajor_axis_km": 7000.0,
            "orbital_eccentricity": 0.01,
            "orbital_inclination_deg": 28.5,
            "provenance_refs": ["test:orbit"],
        }
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(
                ("LOG-1",),
                site_key="EO-1",
                spatial=spatial,
            ),
            self.catalog,
            _locations(),
        )
        result = materializer.materialize(
            (_facility("LOG-1", "LOGISTICS_NODE", "EARTH_ORBIT"),)
        )
        orbital = result.orbitals[0]
        self.assertEqual(orbital.spatial_status, "EXACT_ORBITAL_ELEMENTS")
        self.assertEqual(orbital.semimajor_axis_km, 7000.0)
        self.assertEqual(orbital.eccentricity, 0.01)
        self.assertEqual(orbital.inclination_deg, 28.5)

    def test_binding_cannot_colocate_facilities_across_locations(self):
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(("PORT-1", "LOG-1")),
            self.catalog,
            _locations(),
        )
        with self.assertRaises(ValueError):
            materializer.materialize(
                (
                    _facility("PORT-1", "SURFACE_PORT", "LUNA_SURFACE"),
                    _facility("LOG-1", "LOGISTICS_NODE", "EARTH_ORBIT"),
                )
            )

    def test_operator_is_not_inferred_from_owner(self):
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(
                ("PORT-1",),
                operator_actor_ids=("OPS",),
            ),
            self.catalog,
            _locations(),
        )
        result = materializer.materialize(
            (_facility("PORT-1", "SURFACE_PORT", "LUNA_SURFACE"),)
        )
        self.assertEqual(result.sites[0].owner_actor_ids, ("AUS",))
        self.assertEqual(result.sites[0].operator_actor_ids, ("OPS",))

        default = FacilitySiteMaterializerV1(
            load_facility_site_materialization_package(
                json.loads(PARAMETERS.read_text())
            ),
            self.catalog,
            _locations(),
        ).materialize(
            (_facility("PORT-2", "SURFACE_PORT", "LUNA_SURFACE"),)
        )
        self.assertEqual(default.sites[0].owner_actor_ids, ("AUS",))
        self.assertEqual(default.sites[0].operator_actor_ids, ())

    def test_habitat_creates_candidate_not_demographic_settlement_claim(self):
        materializer = FacilitySiteMaterializerV1(
            _package_with_binding(("HAB-1",)),
            self.catalog,
            _locations(),
        )
        result = materializer.materialize(
            (_facility("HAB-1", "HABITAT", "LUNA_SURFACE"),)
        )
        self.assertEqual(len(result.settlements), 1)
        settlement = result.settlements[0]
        self.assertEqual(
            settlement.settlement_status,
            "HABITAT_INFRASTRUCTURE_CANDIDATE",
        )
        self.assertEqual(
            settlement.demographic_status,
            "DEFERRED_GAP_014",
        )


if __name__ == "__main__":
    unittest.main()
