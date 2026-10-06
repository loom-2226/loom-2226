"""Build 6E's fixed named-location/scoped-WORLD composition.

World Authority remains the only durable store.  This module contains the
Offworld-specific compiler and typed bindings; it is not a second repository,
ORM, generator framework, or database writer.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import uuid
from typing import Any, Mapping

from loom_world_authority import store
from loom_world_authority.etl import SOURCE_SHA, canonical

CONTRACT = "BUILD6E_NAMED_WORLD_V1"
AUTHORIZATION = "BUILD6E_IMPLEMENTATION_AUTHORIZATION_001_NAMED_WORLD"
USE_CONTRACT = "BUILD6E_SCOPED_AUTHORING_INPUT_V1"
FIXTURE_AUTHORIZATION = "WA-OWNER-2026-10-06-01:BUILD6E_QUALIFICATION_FIXTURE"
IDENTITY_AUTHORITY = "LOOM_BUILD6E_NAMED_WORLD_V1"
MODEL_FAMILY = "AUTHOR_FIXED_SCOPED_REALIZATION_V1"
INPUT = Path(__file__).resolve().parent / "inputs" / "BUILD6E_NAMED_WORLD_V1.json"


class NamedWorldBlocked(RuntimeError):
    """A declared 6E input is absent, out of scope, or conflicts with authority."""


@dataclass(frozen=True, slots=True)
class NamedLocationBinding:
    """Typed run-private references; never included in an Agent snapshot."""

    body_id: Any
    parent_location_id: Any
    authored_site_id: Any
    local_feature_id: Any
    scenario_id: Any
    model_id: Any
    policy_id: Any
    world_id: Any
    world_site_id: Any
    deposit_id: Any
    assertion_id: Any
    support_id: Any
    admission_id: Any
    site_node_id: str
    resource_id: str


def load_manifest(path: Path = INPUT) -> dict[str, Any]:
    """Load and validate the one closed, authored 6E input profile."""
    raw = path.read_bytes()
    doc = json.loads(raw)
    if doc.get("schema") != CONTRACT or doc.get("contract") != CONTRACT:
        raise NamedWorldBlocked("BLOCKED_6E_MANIFEST_PROFILE")
    if doc.get("authorization") != AUTHORIZATION:
        raise NamedWorldBlocked("BLOCKED_6E_AUTHORIZATION")
    if doc["accepted_source"].get("sqlite_sha256") != SOURCE_SHA:
        raise NamedWorldBlocked("BLOCKED_SOURCE_SNAPSHOT_HASH")
    if doc["metadata"]["parent_required_kind"] != "SITE" or doc["metadata"]["parent_required_original_region_type"] != "LOCAL_SITE":
        raise NamedWorldBlocked("BLOCKED_CABEUS_CATALOG_KIND")
    if doc["accepted_source"]["scope"] != "LOCAL_SITE" or doc["accepted_source"]["support_location_key"] != "CABEU":
        raise NamedWorldBlocked("BLOCKED_SCIENCE_SCOPE")
    if doc["accepted_source"]["initial_standing"] != "CANDIDATE":
        raise NamedWorldBlocked("BLOCKED_INITIAL_STANDING")
    if doc["fixture_admission"]["standing"] != "ADMITTED" or doc["fixture_admission"]["use_contract_ref"] != USE_CONTRACT:
        raise NamedWorldBlocked("BLOCKED_SCOPED_ADMISSION_PROFILE")
    if doc["world_generation"]["algorithm"] != MODEL_FAMILY or doc["world_generation"]["seed_use_policy"] != "NO_GENERATION_DRAWS":
        raise NamedWorldBlocked("BLOCKED_GENERATION_ALGORITHM")
    vectors = doc["world_generation"]["scenarios"]
    if set(vectors) != {"NULL", "SPARSE", "RICH"}:
        raise NamedWorldBlocked("BLOCKED_COMPARISON_VECTOR_SET")
    for vector in vectors.values():
        values = tuple(Decimal(vector[k]) for k in ("in_situ", "accessible", "recoverable"))
        if any(not x.is_finite() or x < 0 for x in values) or not values[2] <= values[1] <= values[0]:
            raise NamedWorldBlocked("BLOCKED_RESOURCE_HIERARCHY")
    if doc["runtime"]["opening_effective_time"] != "2" or int(doc["runtime"]["time_offset"]) != 1:
        raise NamedWorldBlocked("BLOCKED_OPENING_TIME_PROFILE")
    return doc


def authored_metadata_manifest(doc: Mapping[str, Any]) -> dict[str, str]:
    m = doc["metadata"]
    return {
        "profile": doc["metadata_profile"],
        "authorization_ref": doc["metadata_authorization_ref"],
        "identity_authority": doc["identity_authority"],
        "body_key": m["body_key"],
        "parent_location_key": m["parent_location_key"],
        "site_key": m["site_key"],
        "site_name": m["site_name"],
        "feature_key": m["feature_key"],
        "feature_name": m["feature_name"],
        "unit_key": m["unit_key"],
    }


def fixture_admission_manifest(doc: Mapping[str, Any]) -> dict[str, Any]:
    s, a = doc["accepted_source"], doc["fixture_admission"]
    return {
        "profile": a["profile"],
        "assertion_id": s["assertion_id"],
        "assertion_metadata_sha256": s["assertion_metadata_sha256"],
        "support_id": s["support_id"],
        "source_snapshot_sha256": s["source_snapshot_sha256"],
        "initial_standing": s["initial_standing"],
        "use_contract_ref": a["use_contract_ref"],
        "authorization_ref": a["authorization_ref"],
        "decision_ordinal": a["decision_ordinal"],
        "standing": a["standing"],
        "effective_availability_lexeme": a["effective_availability_lexeme"],
        "time_support": dict(a["time_support"]),
    }


def onboard_metadata(science_writer, doc: Mapping[str, Any]) -> tuple[str, Any, Any]:
    """Use only the frozen V1.1 bounded owner-authorized metadata operations."""
    status, site_id, feature_id = store.install_authored_site_metadata(
        science_writer, authored_metadata_manifest(doc)
    )
    time_status = store.install_fixture_time_support(science_writer, fixture_admission_manifest(doc))
    return status + "/TIME_" + time_status, site_id, feature_id


def record_scoped_admission(science_governor, doc: Mapping[str, Any]) -> str:
    """A separate authenticated governor action; never part of ETL/runtime."""
    return store.record_fixture_admission(science_governor, fixture_admission_manifest(doc))


def admitted_constraint(reference_reader, doc: Mapping[str, Any]) -> Mapping[str, Any]:
    """Read the admitted input only at its exact persisted LOCAL_SITE support."""
    s = doc["accepted_source"]
    rows = store.read_admitted_constraints(
        reference_reader,
        [uuid.UUID(s["assertion_id"])], 1, USE_CONTRACT, [uuid.UUID(s["support_id"])],
        consumer=CONTRACT, context="REAL", perspective="GOVERNANCE",
    )
    if len(rows) != 1:
        raise NamedWorldBlocked("BLOCKED_ASSERTION_CARDINALITY")
    row = rows[0]
    expected = {
        "semantic_key": s["assertion_key"],
        "initial_standing": "CANDIDATE",
        "standing": "ADMITTED",
        "use_contract_ref": USE_CONTRACT,
        "scope_kind": "LOCAL_SITE",
        "support_resolution": "IDENTIFIED",
        "representativeness_lexeme": "SITE_ONLY",
        "property_code": "WATER_ICE_WT_PERCENT",
        "value_numeric": Decimal("5.6"),
        "unit_key": s["unit_key"],
        "uncertainty_text": "±2.9",
        "support_id": s["support_id"],
        "metadata_sha256": s["assertion_metadata_sha256"],
        "snapshot_id": s["source_snapshot_id"],
        "source_byte_sha256": None,
        "custody_kind": "REMOTE_REFERENCE_ONLY",
        "source_artifact_id": None,
        "knowledge_time_id": None,
        "valid_time_id": None,
    }
    uuid_fields = {"support_id", "location_id", "snapshot_id"}
    for key, value in expected.items():
        actual = str(row.get(key)) if key in uuid_fields and row.get(key) is not None else row.get(key)
        expected_value = str(value) if key in uuid_fields and value is not None else value
        if actual != expected_value:
            raise NamedWorldBlocked("BLOCKED_SOURCE_PROVENANCE_OR_SCOPE:" + key)
    if row.get("extrapolation_warrant_id") is not None:
        raise NamedWorldBlocked("BLOCKED_UNDECLARED_EXTRAPOLATION")
    return row


def _sha(value: bytes) -> str:
    return sha256(value).hexdigest()


def _uuid(kind: str, semantic_key: str, version: str):
    return store.stable_uuid(kind, IDENTITY_AUTHORITY, semantic_key, version)


def compile_world_rows(doc: Mapping[str, Any], source_row: Mapping[str, Any], world_name: str,
                       *, site_id, feature_id, parent_id, world_seed: str | None = None):
    """Compile one fully declared partial WORLD into fixed V1 tables, no RNG."""
    if world_name not in ("NULL", "SPARSE", "RICH"):
        raise NamedWorldBlocked("BLOCKED_WORLD_VARIANT")
    src = doc["accepted_source"]
    if str(source_row["support_id"]) != src["support_id"] or source_row["location_id"] != parent_id:
        raise NamedWorldBlocked("BLOCKED_SCIENCE_SUPPORT_NOT_CATALOG_PARENT")
    if source_row["scope_kind"] != "LOCAL_SITE" or source_row["extrapolation_warrant_id"] is not None:
        raise NamedWorldBlocked("BLOCKED_SCIENTIFIC_SCOPE_WIDENING")
    if source_row["initial_standing"] != "CANDIDATE" or source_row["standing"] != "ADMITTED":
        raise NamedWorldBlocked("BLOCKED_CANDIDATE_STATUS_MUTATION")

    gen = doc["world_generation"]
    vector = gen["scenarios"][world_name]
    # The POLICY stream is excluded from every initial WORLD identity and byte.
    definition = {"fixture": "BUILD6E_NAMED_WORLD_V1", "body": doc["metadata"]["body_key"],
                  "parent": doc["metadata"]["parent_location_key"], "site": doc["metadata"]["site_key"],
                  "feature": doc["metadata"]["feature_key"], "world": world_name,
                  "model": gen["model_key"], "model_version": gen["model_version"],
                  "policy": gen["policy_key"], "policy_version": gen["policy_version"],
                  "vector": vector, "source_id": src["assertion_id"],
                  "support_id": src["support_id"], "admission_use": USE_CONTRACT,
                  "world_seed": world_seed or gen["world_seed"], "seed_use": gen["seed_use_policy"]}
    defh = _sha(canonical(definition))
    scenario_key = "BUILD6E_MOON_CABEU_" + world_name
    scenario_id = _uuid("SCENARIO", scenario_key, "1")
    model_id = _uuid("GENERATION_MODEL", gen["model_key"], gen["model_version"])
    policy_id = _uuid("GENERATION_POLICY", gen["policy_key"], gen["policy_version"])
    world_semantic = scenario_key + ":" + (world_seed or gen["world_seed"])
    world_id = _uuid("WORLD_REALIZATION", world_semantic, "1")
    site_private_id = _uuid("WORLD_SITE", str(world_id) + ":" + doc["metadata"]["site_key"], "1")
    deposit_id = _uuid("WORLD_DEPOSIT", str(world_id) + ":" + doc["metadata"]["feature_key"], "1")
    q = Decimal(vector["in_situ"])
    constraint_digest = _sha(canonical({"assertion_id": src["assertion_id"], "admission_use": USE_CONTRACT,
        "metadata_sha256": src["assertion_metadata_sha256"], "source_snapshot_sha256": src["source_snapshot_sha256"],
        "support_id": src["support_id"], "scope": "LOCAL_SITE", "value": src["value_lexeme"],
        "unit": src["unit_lexeme"], "uncertainty": src["uncertainty_lexeme"], "vector": vector}))
    point_id = _uuid("HIDDEN_STATE", str(world_id) + ":" + str(parent_id) + ":WATER_ICE_WT_PERCENT", "1")
    unknown_grade_id = _uuid("HIDDEN_STATE", str(world_id) + ":" + str(feature_id) + ":WATER_ICE_WT_PERCENT", "1")
    state_rows = []
    for prop, value, unit_key, derivation, provenance in (
        ("WATER_ICE_WT_PERCENT", Decimal("5.6"), "SRC_UNIT:47a59c5378d25095254e9a429e50da63e1adfcf9e530ae7439291c98f1e5542a",
         "SCENARIO_STIPULATION_AT_EXACT_REAL_SUPPORT", "SOURCE_UNCERTAINTY_TEXT:±2.9"),
        ("WATER_ICE_WT_PERCENT", None, None, "NO_SUPPORTED_LOCAL_GRADE_INFERENCE", "UNKNOWN_LOCAL_FEATURE_GRADE"),
        ("R_IN_SITU", q, gen["model_unit_key"], "AUTHOR_FIXED_SCOPED_REALIZATION_V1", "EXPLICIT_FIXTURE_VECTOR"),
        ("R_ACCESSIBLE", Decimal(vector["accessible"]), gen["model_unit_key"], "EXPLICIT_STRUCTURAL_ACCESS_ASSUMPTION", "NOT_EMPIRICAL_ACCESSIBILITY"),
        ("R_RECOVERABLE", Decimal(vector["recoverable"]), gen["model_unit_key"], "EXPLICIT_STRUCTURAL_CAPABILITY_ASSUMPTION", "NOT_RESERVE"),
        ("R_RESERVE", None, None, "NO_GOVERNED_RESERVE_CONVERSION", "UNKNOWN_RESERVE"),
    ):
        location = parent_id if prop == "WATER_ICE_WT_PERCENT" and value is not None else feature_id
        sid = point_id if location == parent_id else unknown_grade_id if prop == "WATER_ICE_WT_PERCENT" else _uuid("HIDDEN_STATE", str(world_id) + ":" + str(feature_id) + ":" + prop, "1")
        payload = {"world_id": str(world_id), "body_id": str(source_row["body_id"]), "location_id": str(location),
                   "property_code": prop, "value_state": "UNKNOWN" if value is None else "KNOWN",
                   "numeric_value": None if value is None else str(value), "unit_key": unit_key,
                   "model_family_ref": MODEL_FAMILY, "uncertainty_ref": provenance, "derivation_ref": derivation}
        state_rows.append(("wa_world.hidden_state", dict(state_id=sid, world_id=world_id, body_id=source_row["body_id"],
            location_id=location, property_code=prop, value_state="UNKNOWN" if value is None else "KNOWN",
            numeric_value=value, text_value=None, unit_key=unit_key, model_family_ref=MODEL_FAMILY,
            uncertainty_ref=provenance, derivation_ref=derivation, value_sha256=_sha(canonical(payload)),
            original_provenance_lexeme=provenance)))

    policy_obj = {"algorithm": MODEL_FAMILY, "world": world_name, "vector": vector,
                  "source_constraint": src["assertion_id"], "scope": "LOCAL_SITE", "support_id": src["support_id"],
                  "source_nominal_is_not_deposit_grade": True, "policy_seed_used": False}
    policy_bytes = canonical(policy_obj)
    rows = [
        ("wa_world.scenario", dict(scenario_id=scenario_id, semantic_key=scenario_key, version="1",
            definition_sha256=defh, authorization_ref=doc["fixture_authorization_ref"],
            definition_locator="simulation/offworld_mvp/build6e/inputs/BUILD6E_NAMED_WORLD_V1.json", world_context="SCENARIO")),
        ("wa_world.generation_model", dict(model_id=model_id, semantic_key=gen["model_key"], version=gen["model_version"],
            name="Fixed scoped structural realization", status_lexeme="AUTHORIZED_STRUCTURAL_FIXTURE",
            implementation_sha256=defh, implementation_locator="simulation/offworld_mvp/build6e/named_world.py",
            model_family_ref=MODEL_FAMILY, uncertainty_contract_ref="SOURCE_TEXT_PRESERVED_NO_DISTRIBUTION",
            parameter_schema_ref="BUILD6E_NAMED_WORLD_V1")),
        ("wa_world.generation_policy", dict(policy_id=policy_id, model_id=model_id, semantic_key=gen["policy_key"], version=gen["policy_version"],
            body_id=source_row["body_id"], property_code=gen["resource_family"], policy_type_lexeme="AUTHOR_FIXED_STRUCTURAL_VECTOR",
            parameters=policy_obj, parameter_schema_ref="BUILD6E_NAMED_WORLD_V1", original_parameter_lexeme=None,
            policy_bytes=policy_bytes, policy_sha256=_sha(policy_bytes), authorization_ref=doc["fixture_authorization_ref"],
            notes="STRUCTURAL_ONLY; no empirical stock, grade or reserve inference")),
        ("wa_world.realization", dict(world_id=world_id, scenario_id=scenario_id, model_id=model_id, policy_id=policy_id,
            body_id=source_row["body_id"], semantic_key=world_semantic, world_seed_lexeme=world_seed or gen["world_seed"],
            seed_lineage_ref="COMPARISON_CONTROL:" + gen["comparison_group"], scientific_cutoff_ordinal=1,
            random_algorithm_ref=gen["random_algorithm"], key_schema_ref=gen["key_schema"], constraints_digest=constraint_digest,
            generator_output_sha256=defh, status_lexeme="PARTIAL_STRUCTURAL_NOT_EMPIRICALLY_VALIDATED",
            created_time_lexeme="2", initial_epoch_id=None, world_context="SCENARIO")),
        ("wa_world.physical_property", dict(property_code="WATER_ICE_WT_PERCENT", value_domain="NUMBER",
            physical_semantics_ref="LOCAL_MASS_FRACTION_PERCENT_REPORTED", schema_ref="BUILD6E_NAMED_WORLD_V1")),
        ("wa_world.physical_property", dict(property_code="R_IN_SITU", value_domain="NUMBER", physical_semantics_ref="IN_SITU_STOCK", schema_ref="BUILD6E_NAMED_WORLD_V1")),
        ("wa_world.physical_property", dict(property_code="R_ACCESSIBLE", value_domain="NUMBER", physical_semantics_ref="ACCESSIBLE_STOCK", schema_ref="BUILD6E_NAMED_WORLD_V1")),
        ("wa_world.physical_property", dict(property_code="R_RECOVERABLE", value_domain="NUMBER", physical_semantics_ref="RECOVERABLE_STOCK", schema_ref="BUILD6E_NAMED_WORLD_V1")),
        ("wa_world.physical_property", dict(property_code="R_RESERVE", value_domain="NUMBER", physical_semantics_ref="ECONOMIC_RESERVE_UNKNOWN", schema_ref="BUILD6E_NAMED_WORLD_V1")),
        ("wa_world.constraint_binding", dict(world_id=world_id, body_id=source_row["body_id"], binding_key="R_MOON_CAB_WATER_AT_EXACT_SUPPORT",
            assertion_id=src["assertion_id"], admission_id=source_row["admission_id"], target_support_id=src["support_id"],
            extrapolation_warrant_id=None, assertion_metadata_sha256=src["assertion_metadata_sha256"],
            binding_role="REAL_CONSTRAINT_EXACT_SOURCE_SUPPORT", use_contract_ref=USE_CONTRACT)),
        ("wa_world.site", dict(site_id=site_private_id, world_id=world_id, body_id=source_row["body_id"], location_id=site_id,
            semantic_key=doc["metadata"]["site_key"], name=doc["metadata"]["site_name"], status_lexeme="AUTHORED_FICTIONAL_SITE",
            refinement_model_ref=MODEL_FAMILY, refinement_seed_lineage_ref="NO_GENERATION_DRAWS", realization_sha256=defh)),
        ("wa_world.deposit", dict(deposit_id=deposit_id, world_id=world_id, body_id=source_row["body_id"], site_id=site_private_id,
            location_id=feature_id, resource_class=gen["resource_family"], geometry_class_lexeme="UNKNOWN",
            initial_in_situ_state="KNOWN", initial_in_situ_quantity=q, unit_key=gen["model_unit_key"],
            concentration_state="UNKNOWN", concentration_value=None, concentration_unit_key=None, vertical_id=None,
            phase_ref="UNCHARACTERIZED", physical_form_ref="UNCHARACTERIZED",
            original_accessibility_lexeme="SCENARIO_STIPULATION_FULLY_ACCESSIBLE_STRUCTURAL_WITNESS",
            provenance_ref=doc["fixture_authorization_ref"] + ":" + defh)),
        *state_rows,
    ]
    binding = NamedLocationBinding(
        body_id=source_row["body_id"], parent_location_id=parent_id, authored_site_id=site_id, local_feature_id=feature_id,
        scenario_id=scenario_id, model_id=model_id, policy_id=policy_id, world_id=world_id,
        world_site_id=site_private_id, deposit_id=deposit_id, assertion_id=src["assertion_id"],
        support_id=src["support_id"], admission_id=source_row["admission_id"],
        site_node_id=doc["runtime"]["node_id"], resource_id=gen["resource_id"],
    )
    return binding, tuple(rows)


def install_compiled_world(world_writer, doc, source_row, world_name, *, site_id, feature_id, parent_id, world_seed=None):
    binding, rows = compile_world_rows(doc, source_row, world_name, site_id=site_id, feature_id=feature_id,
                                      parent_id=parent_id, world_seed=world_seed)
    result = store.install_exact_world(world_writer, rows)
    return result, binding


def prepare_named_world(*, science_writer, science_governor, reference_reader,
                        world_writer, doc: Mapping[str, Any], world_name: str,
                        world_seed: str | None = None):
    """Perform the fixed governed 6E bootstrap through V1.1 store operations.

    The source dataset remains candidate; the returned source row is a separate
    use-scoped admission. Cabeus must resolve as the preserved empirical SITE.
    No SQL or Build 6E-owned persistence path is used here.
    """
    site_status, site_id, feature_id = onboard_metadata(science_writer, doc)
    catalog = store.read_catalog_location(reference_reader, doc['metadata']['body_key'],
                                            doc['metadata']['parent_location_key'])
    if catalog is None:
        raise NamedWorldBlocked('BLOCKED_CABEUS_NOT_EMPIRICAL_SITE')
    # V1.2 deliberately returns a fixed tuple, not a caller-shaped SQL row.
    columns=('body_id','body_key','body_name','body_class','body_original_ref',
             'location_id','location_key','location_name','location_kind','origin_kind',
             'geometry_id','source_ref')
    if len(catalog)!=len(columns):
        raise NamedWorldBlocked('BLOCKED_CATALOG_READER_PROFILE')
    parent=dict(zip(columns,catalog,strict=True))
    if parent['location_kind'] != 'SITE' or parent['origin_kind'] != 'EMPIRICALLY_IDENTIFIED':
        raise NamedWorldBlocked('BLOCKED_CABEUS_NOT_EMPIRICAL_SITE')
    expected_parent = store.stable_uuid('LOCATION', 'LOOM_LOCATION_V1',
        store.length_prefixed(doc['metadata']['body_key'], doc['metadata']['parent_location_key']).decode(),
        'IDENTITY_V1')
    if parent['location_id'] != expected_parent:
        raise NamedWorldBlocked('BLOCKED_CATALOG_LOCATION_IDENTITY')
    admission_status = record_scoped_admission(science_governor, doc)
    source_rows = store.read_admitted_constraints(
        reference_reader, [uuid.UUID(doc['accepted_source']['assertion_id'])], 1,
        USE_CONTRACT, [uuid.UUID(doc['accepted_source']['support_id'])], consumer=CONTRACT,
        context='REAL', perspective='GOVERNANCE')
    if len(source_rows) != 1:
        raise NamedWorldBlocked('BLOCKED_ASSERTION_CARDINALITY')
    source = source_rows[0]
    if source['location_id'] != parent['location_id'] or source['scope_kind'] != 'LOCAL_SITE' or source.get('extrapolation_warrant_id') is not None:
        raise NamedWorldBlocked('BLOCKED_SCIENTIFIC_SCOPE_WIDENING')
    validate_source = admitted_constraint(reference_reader, doc)
    if validate_source != source:
        raise NamedWorldBlocked('BLOCKED_SOURCE_ROW_DRIFT')
    world_status, binding = install_compiled_world(
        world_writer, doc, source, world_name, site_id=site_id,
        feature_id=feature_id, parent_id=parent['location_id'], world_seed=world_seed)
    return {'metadata_status': site_status, 'admission_status': admission_status,
            'world_status': world_status, 'parent': parent, 'source': source,
            'binding': binding}


def safe_named_location_fact(doc: Mapping[str, Any]) -> tuple[str, str]:
    """Agent-safe real catalog label only; private WORLD identifiers are excluded."""
    return "Moon — Cabeus crater", "REAL_CATALOG_LOCATION_IDENTITY"


def _runtime_epoch_rows(kernel, binding: NamedLocationBinding, *, first: bool, start_index: int, epoch_id: str):
    """Encode one completed original kernel epoch in the fixed V1 row profile."""
    from dataclasses import fields
    from offworld_kernel.causal_trace import canonical as trace_canonical
    envelopes = kernel.causal_envelopes
    if not envelopes:
        raise NamedWorldBlocked('BLOCKED_EPOCH_WITHOUT_CAUSAL_ENVELOPE')
    if any(e.epoch_id != epoch_id for e in envelopes[start_index:]):
        raise NamedWorldBlocked('BLOCKED_EPOCH_ENVELOPE_ID_MISMATCH')
    def raw(value):
        return trace_canonical(value).encode('utf8')
    def digest(value):
        return sha256(value).hexdigest()
    rows = []
    manifest = kernel.boundary_manifest
    if first:
        identity = raw(kernel.run_identity)
        boundary = raw(manifest)
        rows.append(('wa_run.execution', dict(run_id=manifest.run_id,
            scenario_id=binding.scenario_id, original_run_identity=identity,
            identity_sha256=digest(identity), code_contract=manifest.contract_version,
            code_tree_sha256=__import__('offworld_kernel.provenance', fromlist=['source_tree_hash']).source_tree_hash(),
            input_snapshot_ref=manifest.input_snapshot_id,
            boundary_manifest_bytes=boundary, boundary_manifest_sha256=digest(boundary),
            policy_seed_lexeme=dict(manifest.comparison_parameters)['policy_seed'],
            world_seed_manifest_ref='WORLD_SEED:'+manifest.scenario_id,
            world_seed_lexeme=dict(manifest.comparison_parameters)['world_seed'],
            comparison_group_ref=dict(manifest.comparison_parameters)['comparison_group'],
            comparison_key_schema_ref=dict(manifest.comparison_parameters)['key_schema'],
            random_algorithm_ref=dict(manifest.comparison_parameters)['algorithm'],
            decimal_precision=int(dict(manifest.comparison_parameters)['decimal_precision']),
            decimal_rounding_ref=dict(manifest.comparison_parameters)['decimal_rounding'],
            clock_mapping_ref=manifest.clock_mapping_ref,
            qualification_protocol_ref=manifest.qualification_protocol_ref[0])))
        rows.append(('wa_run.world_binding', dict(run_id=manifest.run_id,
            scenario_id=binding.scenario_id, world_id=binding.world_id,
            body_id=binding.body_id, binding_key=manifest.parameter('site_binding_key'))))
    if start_index < 0 or start_index >= len(envelopes):
        raise NamedWorldBlocked('BLOCKED_EPOCH_ENVELOPE_RANGE')
    all_unique=[]
    for ordinal, e in enumerate(envelopes[start_index:], start=start_index):
        artifact_refs = tuple(e.artifact_refs)
        unique = tuple(dict.fromkeys(artifact_refs))
        all_unique.extend(ref for _, ref in unique)
        for kind, ref in unique:
            stored = kernel.causal_artifacts.get(ref)
            if stored is None or stored[0] != kind:
                raise NamedWorldBlocked('BLOCKED_TRACE_ARTIFACT_MISSING')
            payload = stored[1].encode('utf8')
            if ref != kind+':'+digest(payload):
                raise NamedWorldBlocked('BLOCKED_TRACE_ARTIFACT_HASH')
            rows.append(('wa_run.artifact', dict(run_id=manifest.run_id,
                artifact_ref=ref, record_kind=kind,
                serializer_ref='OFFWORLD_CAUSAL_TRACE_CANONICAL_V1',
                payload_bytes=payload, payload_sha256=digest(payload))))
        envelope_bytes = raw(e)
        material = raw(tuple((f.name, getattr(e, f.name)) for f in fields(e) if f.name != 'envelope_hash'))
        rows.append(('wa_run.causal_envelope', dict(run_id=e.run_id,
            envelope_id=e.envelope_id, event_ordinal=ordinal,
            record_version=e.record_version, scheduled_event_id=e.scheduled_event_id,
            epoch_id=e.epoch_id, actor_ref=e.actor_id, process_ref=e.process_id,
            action_ref=e.action, world_context=e.world_context, context_id=e.context_id,
            perspective=e.perspective, time_basis=e.time_basis,
            effective_time=Decimal(e.effective_time),
            decision_time=None if e.decision_time is None else Decimal(e.decision_time),
            authorization_time=None if e.authorization_time is None else Decimal(e.authorization_time),
            realized_time=Decimal(e.realized_time),
            effective_time_lexeme=e.effective_time, decision_time_lexeme=e.decision_time,
            authorization_time_lexeme=e.authorization_time,
            realized_time_lexeme=e.realized_time, reason_code=e.reason_code,
            original_envelope_bytes=envelope_bytes, original_envelope_sha256=digest(envelope_bytes),
            original_hash_material=material, envelope_hash=e.envelope_hash,
            previous_trace_hash=e.previous_trace_hash, pre_domain_hash=e.pre_domain_hash,
            post_domain_hash=e.post_domain_hash)))
        for artifact_ordinal, (kind, ref) in enumerate(artifact_refs):
            rows.append(('wa_run.trace_artifact_edge', dict(run_id=e.run_id,
                envelope_id=e.envelope_id, edge_role=kind, edge_ordinal=artifact_ordinal,
                artifact_ref=ref)))
        for parent in e.parent_envelope_refs:
            rows.append(('wa_run.trace_parent', dict(run_id=e.run_id,
                child_envelope_id=e.envelope_id, parent_envelope_id=parent)))
        resource = kernel.resources[binding.resource_id]
        depleted = resource.recoverable - resource.remaining
        if depleted < 0 or depleted > resource.in_situ:
            raise NamedWorldBlocked('BLOCKED_RESOURCE_CONSERVATION')
        physical_ref = next((ref for kind, ref in artifact_refs if kind == 'REALIZED_EVENT'), unique[0][1])
        rows.append(('wa_run.stock_state', dict(run_id=e.run_id, world_id=binding.world_id,
            body_id=binding.body_id, deposit_id=binding.deposit_id, event_id=e.envelope_id,
            remaining_state='KNOWN', remaining_in_situ=resource.in_situ-depleted,
            cumulative_extracted=depleted, unit_key='MODEL_RESOURCE_UNIT_BY_FAMILY',
            original_physical_state_ref=physical_ref)))
    latest = envelopes[-1]
    terminals = tuple(dict.fromkeys(ref for _, ref in latest.artifact_refs))[:2]
    if len(terminals) != 2:
        raise NamedWorldBlocked('BLOCKED_EPOCH_TERMINAL_ORIGINALS')
    return tuple(rows), terminals


def execute_persisted_epoch(*, service_name: str, kernel, binding: NamedLocationBinding,
                            epoch_id: str, effective_time: Decimal | str | int, execute):
    """Run one original kernel epoch inside World Authority's V1.2 scope.

    Runtime results are returned only after successful COMMIT. Any raised error
    abandons the caller's working kernel; the caller must reconstruct it.
    """
    m = kernel.boundary_manifest
    from loom_world_authority import store
    from offworld_kernel.provenance import source_tree_hash
    from offworld_kernel.causal_trace import validate_trace
    with store.run_epoch(service_name, m.run_id) as session:
        head = session.head
        prefix = session.read_replay_prefix(input_snapshot_ref=m.input_snapshot_id,
            code_contract=m.contract_version, code_tree_sha256=source_tree_hash())
        if prefix is None and head is not None:
            raise NamedWorldBlocked('BLOCKED_RUN_HEAD_WITHOUT_EXECUTION')
        expected = None if head is None else tuple(head[:2])
        if prefix is not None:
            stored = tuple(prefix['envelopes'])
            matching = [r for r in stored if r['epoch_id'] == epoch_id]
            if matching:
                first_ordinal = min(r['event_ordinal'] for r in matching)
                prior = [r for r in stored if r['event_ordinal'] < first_ordinal]
                expected = None if not prior else (prior[-1]['envelope_id'], prior[-1]['envelope_hash'])
            if head is not None and not matching:
                physical = session.load_bound_world(m.parameter('site_binding_key'),
                    context='REALIZED', effective_time=Decimal(effective_time))
                history = physical['stock_history']
                prior_stock = history[-1] if history else None
                if prior_stock is not None:
                    resource = kernel.resources[binding.resource_id]
                    expected_in_situ = resource.in_situ-(resource.recoverable-resource.remaining)
                    if Decimal(prior_stock['remaining_in_situ']) != expected_in_situ:
                        raise NamedWorldBlocked('BLOCKED_PINNED_PHYSICAL_HEAD_MISMATCH')
        start_index = len(kernel.causal_envelopes)
        result = execute()
        validate_trace(kernel.causal_envelopes, kernel.causal_artifacts)
        first = not bool(prefix)
        rows, terminals = _runtime_epoch_rows(kernel, binding, first=first,
            start_index=start_index, epoch_id=epoch_id)
        session.stage_epoch(epoch_id, expected, rows, terminals)
    if session.status not in ('COMMITTED', 'ALREADY_MATCHED'):
        raise NamedWorldBlocked('BLOCKED_EPOCH_NOT_COMMITTED')
    return result, session.status
