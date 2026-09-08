from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

SYNTH = Path(__file__).resolve().parents[1] / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from manufacturing_functional_regions import (  # noqa: E402
    FUNCTIONAL_REGION_AUTHORITY,
    MANUFACTURING_CONTEXT_AUTHORITY,
    FunctionalRegion,
    ManufacturingCapabilityContext,
    ManufacturingProcessCapability,
    ManufacturingRegionError,
    MaterialSystemCapability,
    content_hash,
    validate_context,
    validate_region,
)


def fixture_context() -> ManufacturingCapabilityContext:
    return ManufacturingCapabilityContext(
        context_id="CERES_YARD_2210",
        context_date="2210-01-01",
        industrial_context_hash="a" * 64,
        material_systems=(
            MaterialSystemCapability(
                material_system_id="MS-NI-FE-LATTICE",
                status="AVAILABLE",
                manufacturing_class="BULK_CONSTRUCTION",
                feedstock_classes=("IRON_NICKEL",),
                provenance_refs=("PROV-MAT-001",),
            ),
            MaterialSystemCapability(
                material_system_id="MS-GRADED-TI-CERAMIC",
                status="OPEN",
                manufacturing_class="PRECISION_STRUCTURAL",
                feedstock_classes=("TITANIUM", "CERAMIC_PRECURSOR"),
                provenance_refs=("PROV-MAT-002",),
            ),
        ),
        processes=(
            ManufacturingProcessCapability(
                process_id="PROC-LARGE-LATTICE-AM",
                status="AVAILABLE",
                manufacturing_class="BULK_CONSTRUCTION",
                max_build_envelope_m=(40.0, 20.0, 20.0),
                minimum_feature_m=0.01,
                material_grading_supported=False,
                multimaterial_supported=False,
                embedded_channels_supported=True,
                embedded_sensing_supported=None,
                in_situ_heat_treatment_supported=False,
                inspection_resolution_m=0.001,
                repair_processes=("ROBOTIC_CUT_AND_REDEPOSIT",),
                certified_process_families=("LATTICE_PRIMARY_STRUCTURE",),
                precision_cost_class="BULK_LOW",
                provenance_refs=("PROV-PROC-001",),
            ),
            ManufacturingProcessCapability(
                process_id="PROC-GRADED-PRECISION-AM",
                status="OPEN",
                manufacturing_class="PRECISION_STRUCTURAL",
                max_build_envelope_m=(6.0, 6.0, 6.0),
                minimum_feature_m=0.001,
                material_grading_supported=True,
                multimaterial_supported=True,
                embedded_channels_supported=True,
                embedded_sensing_supported=True,
                in_situ_heat_treatment_supported=True,
                inspection_resolution_m=0.0001,
                repair_processes=("LOCAL_REDEPOSITION",),
                certified_process_families=("PRESSURE_ADJACENT_STRUCTURE",),
                precision_cost_class="PRECISION_HIGH",
                provenance_refs=("PROV-PROC-002",),
            ),
        ),
        provenance_refs=("PROV-CONTEXT-001",),
    )


def fixture_region() -> FunctionalRegion:
    return FunctionalRegion(
        region_id="AFT-MULTIFUNCTION-001",
        required_functions=(
            "CARRY_PRIMARY_THRUST_LOAD",
            "SUPPORT_REMASS_TANKS",
            "ROUTE_PRIMARY_COOLANT",
            "ROUTE_PRIMARY_POWER",
        ),
        load_interfaces=("THRUST_FRAME", "REMASS_TANK_CLUSTER"),
        thermal_interfaces=("PRIMARY_COOLANT_LOOP",),
        fluid_interfaces=("REMASS_FEED", "PRIMARY_COOLANT_LOOP"),
        electrical_interfaces=("PRIMARY_POWER_BUS",),
        pressure_boundary_role="NOT_A_PRIMARY_PRESSURE_BOUNDARY",
        material_system_candidates=("MS-NI-FE-LATTICE", "MS-GRADED-TI-CERAMIC"),
        manufacturing_process_candidates=("PROC-LARGE-LATTICE-AM", "PROC-GRADED-PRECISION-AM"),
        repairability_requirement="REPLACE_OR_REDEPOSIT_DAMAGED_SUBREGIONS",
        inspection_requirement="FULL_AS_BUILT_VOLUMETRIC_INSPECTION_REQUIRED",
        replaceable_interfaces=("THRUST_INTERFACE_INSERT",),
        embedded_sensor_requirement="STRUCTURAL_STATE_SENSING_REQUIRED_BUT_IMPLEMENTATION_OPEN",
        provenance_refs=("PROV-REGION-001",),
    )


class ManufacturingFunctionalRegionTests(unittest.TestCase):
    def test_context_and_region_validate_without_granting_engineering_authority(self):
        context = fixture_context()
        region = fixture_region()
        validate_context(context)
        validate_region(region, context)
        self.assertEqual(context.authority_status, MANUFACTURING_CONTEXT_AUTHORITY)
        self.assertEqual(region.authority_status, FUNCTIONAL_REGION_AUTHORITY)
        self.assertEqual(len(content_hash(context)), 64)
        self.assertEqual(len(content_hash(region)), 64)

    def test_open_capabilities_remain_explicit_and_are_not_promoted(self):
        context = fixture_context()
        region = fixture_region()
        validate_region(region, context)
        materials = {row.material_system_id: row.status for row in context.material_systems}
        processes = {row.process_id: row.status for row in context.processes}
        self.assertEqual(materials["MS-GRADED-TI-CERAMIC"], "OPEN")
        self.assertEqual(processes["PROC-GRADED-PRECISION-AM"], "OPEN")
        self.assertIn("MS-GRADED-TI-CERAMIC", region.material_system_candidates)
        self.assertIn("PROC-GRADED-PRECISION-AM", region.manufacturing_process_candidates)

    def test_unknown_material_or_process_reference_fails_closed(self):
        context = fixture_context()
        with self.assertRaises(ManufacturingRegionError):
            validate_region(
                replace(fixture_region(), material_system_candidates=("MS-NOT-GOVERNED",)),
                context,
            )
        with self.assertRaises(ManufacturingRegionError):
            validate_region(
                replace(fixture_region(), manufacturing_process_candidates=("PROC-NOT-GOVERNED",)),
                context,
            )

    def test_authority_escalation_fails_closed(self):
        context = fixture_context()
        region = fixture_region()
        with self.assertRaises(ManufacturingRegionError):
            validate_context(replace(context, authority_status="ENGINEERING_PASS"))
        with self.assertRaises(ManufacturingRegionError):
            validate_region(replace(region, authority_status="CANON"), context)

    def test_context_requires_existing_industrial_context_hash(self):
        with self.assertRaises(ManufacturingRegionError):
            validate_context(replace(fixture_context(), industrial_context_hash="not-a-hash"))

    def test_precision_is_explicit_data_not_inferred_from_manufacturing_class(self):
        context = fixture_context()
        bulk = context.processes[0]
        precision = context.processes[1]
        self.assertEqual(bulk.precision_cost_class, "BULK_LOW")
        self.assertEqual(precision.precision_cost_class, "PRECISION_HIGH")
        self.assertNotEqual(bulk.minimum_feature_m, precision.minimum_feature_m)


if __name__ == "__main__":
    unittest.main()
