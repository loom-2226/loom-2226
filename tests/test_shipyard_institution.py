import dataclasses
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qualification" / "synthesis"))

from shipyard_institution import (
    DESIGN_AUTHORITY,
    INSTITUTION_AUTHORITY,
    MEMORY_AUTHORITY,
    DesignLineageEdge,
    HistoricalDesign,
    InstitutionalMemorySnapshot,
    InstitutionContractError,
    ShipbuildingInstitution,
    YardMemoryEvent,
    content_hash,
    institutional_context,
    validate_snapshot,
)


def fixture_snapshot() -> InstitutionalMemorySnapshot:
    institution = ShipbuildingInstitution(
        institution_id="YARD-A",
        founded_date="2180-01-01",
        founding_lineage=("earth-aerospace",),
        cultural_progenitors=("earth",),
        engineering_lineage=("pressure-vessel", "modular-avionics"),
        design_doctrine=("axial-load-paths",),
        preferred_architectures=("spine-freighter",),
        manufacturing_capabilities=("robotic-weld", "large-ring-forge"),
        material_access=("al-li-alloy",),
        automation_profile=("high-automation",),
        component_ecosystem=("supplier-A",),
        risk_tolerance="CONSERVATIVE",
        maintainability_doctrine=("line-replaceable-units",),
        aesthetic_principles=("functional-expressionism",),
        provenance_refs=("prov:charter",),
    )
    parent = HistoricalDesign(
        design_id="D2184",
        institution_id="YARD-A",
        service_date="2184-01-01",
        architecture_family="tug",
        mission_roles=("tug",),
        successful_modules=("power-bus-v1",),
        manufacturing_processes=("ring-weld",),
        supplier_refs=("supplier:A",),
        certification_refs=("cert:1",),
        field_evidence_refs=("field:1",),
        provenance_refs=("prov:d1",),
    )
    child = HistoricalDesign(
        design_id="D2192",
        institution_id="YARD-A",
        service_date="2192-01-01",
        architecture_family="utility-transport",
        mission_roles=("cargo", "tug"),
        successful_modules=("power-bus-v1",),
        manufacturing_processes=("ring-weld",),
        supplier_refs=("supplier:A",),
        certification_refs=("cert:2",),
        field_evidence_refs=("field:2",),
        provenance_refs=("prov:d2",),
    )
    edge = DesignLineageEdge(
        parent_design_id="D2184",
        child_design_id="D2192",
        mechanisms=("MODULE_REUSE", "MANUFACTURING_PROCESS_CONTINUITY"),
        rationale="reused qualified power bus and weld process",
        provenance_refs=("prov:edge",),
    )
    memory = YardMemoryEvent(
        event_id="E1",
        institution_id="YARD-A",
        event_date="2193-01-01",
        memory_kind="FIELD_REPORT",
        design_refs=("D2192",),
        lesson="aft service corridor reduced dock time",
        evidence_refs=("field:2",),
        provenance_refs=("prov:event",),
    )
    return InstitutionalMemorySnapshot(
        institution=institution,
        as_of_date="2195-01-01",
        historical_designs=(child, parent),
        lineage_edges=(edge,),
        memory_events=(memory,),
    )


def test_snapshot_is_valid_and_context_is_deterministically_chronological():
    snapshot = fixture_snapshot()
    validate_snapshot(snapshot)
    context = institutional_context(snapshot)
    assert context.historical_design_refs == ("D2184", "D2192")
    assert context.authority_status == INSTITUTION_AUTHORITY
    assert content_hash(snapshot) == content_hash(snapshot)


def test_lineage_cycle_fails_closed():
    snapshot = fixture_snapshot()
    equal_date_parent = dataclasses.replace(snapshot.historical_designs[1], service_date="2192-01-01")
    snapshot = dataclasses.replace(
        snapshot,
        historical_designs=(snapshot.historical_designs[0], equal_date_parent),
    )
    reverse = DesignLineageEdge(
        parent_design_id="D2192",
        child_design_id="D2184",
        mechanisms=("ARCHITECTURAL_PRECEDENT",),
        rationale="malformed reverse edge",
        provenance_refs=("prov:x",),
    )
    with pytest.raises(InstitutionContractError, match="cycle"):
        validate_snapshot(dataclasses.replace(snapshot, lineage_edges=snapshot.lineage_edges + (reverse,)))


def test_unknown_design_memory_ref_fails_closed():
    snapshot = fixture_snapshot()
    bad = dataclasses.replace(snapshot.memory_events[0], design_refs=("MISSING",))
    with pytest.raises(InstitutionContractError, match="unknown designs"):
        validate_snapshot(dataclasses.replace(snapshot, memory_events=(bad,)))


def test_future_memory_is_not_back_propagated():
    snapshot = fixture_snapshot()
    bad = dataclasses.replace(snapshot.memory_events[0], event_date="2200-01-01")
    with pytest.raises(InstitutionContractError, match="after snapshot date"):
        validate_snapshot(dataclasses.replace(snapshot, memory_events=(bad,)))


def test_authority_escalation_fails_closed():
    snapshot = fixture_snapshot()
    bad = dataclasses.replace(snapshot.institution, authority_status="ENGINEERING_PASS")
    with pytest.raises(InstitutionContractError, match="may not claim"):
        validate_snapshot(dataclasses.replace(snapshot, institution=bad))


def test_parent_may_not_postdate_child():
    snapshot = fixture_snapshot()
    late_parent = dataclasses.replace(snapshot.historical_designs[1], service_date="2194-01-01")
    child = dataclasses.replace(snapshot.historical_designs[0], service_date="2192-01-01")
    with pytest.raises(InstitutionContractError, match="post-date"):
        validate_snapshot(dataclasses.replace(snapshot, historical_designs=(child, late_parent)))


def test_records_are_non_authoritative_by_construction():
    snapshot = fixture_snapshot()
    assert snapshot.institution.authority_status == INSTITUTION_AUTHORITY
    assert all(row.authority_status == DESIGN_AUTHORITY for row in snapshot.historical_designs)
    assert all(row.authority_status == MEMORY_AUTHORITY for row in snapshot.memory_events)
