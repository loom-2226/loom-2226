"""Step 7.6: quarantine legacy machinery-test authority from causal production.

This module does not delete or rewrite the historical fixtures.  It constructs a
runtime view in which authored machinery-test futures cannot become world facts.
Promoted/external authority (for example Earth demographic authority) is untouched.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from .actor_state_v1 import ActorBudget, ActorFactSet, SpendableAllocation
from .mission_knowledge_v1 import DecisionValue

PURGE_ID = "CIVPROP_LEGACY_AUTHORITY_PURGE_V0_3"
_MACHINERY_MARKERS = (
    "MACHINERY_TEST", "actor_bridge_parameters_v0_1",
    "actor_machinery_test_baseline_v0_1", "actor_earth_support_v0_1",
    "NON_CANON_SOLAR_V03_PROPAGATION_TEST", "EXPLICIT_PLACEHOLDER:GAP-016",
)

@dataclass(frozen=True)
class AuthorityDispositionV03:
    authority_surface: str
    classification: str
    count: int
    action: str
    rationale: str

@dataclass(frozen=True)
class PurgedBundleV03:
    bundle: object
    inventory: tuple[AuthorityDispositionV03, ...]


def _fixture_ref(values: Iterable[str]) -> bool:
    text="|".join(str(x) for x in values)
    return any(marker in text for marker in _MACHINERY_MARKERS)


def _purge_factset(facts):
    kept=tuple(x for x in facts.records if not _fixture_ref(x.provenance_refs))
    if kept:
        return replace(facts, records=kept, status="KNOWN_RECORDS")
    if facts.records:
        return ActorFactSet(status="UNKNOWN", records=())
    return facts


def purge_legacy_authority(bundle) -> PurgedBundleV03:
    """Return a causal-runtime view with legacy authored authority quarantined.

    Rules are deliberately provenance based.  The source bundle remains unchanged.
    2026 is not magical: a 2026 value sourced only from a machinery-test assumption
    is still an assumption, while promoted authority may legitimately provide future
    exogenous boundary conditions.
    """
    s=bundle.scenario
    inv=[]

    # Global technology frontier dates have no per-record provenance and include
    # authored future unlocks.  They are reference/test machinery, not causal authority.
    if s.technology_frontier:
        future=sum(x.frontier_year>s.start_year for x in s.technology_frontier)
        initial=len(s.technology_frontier)-future
        inv.append(AuthorityDispositionV03("technology_frontier","LEGACY_UNPROVENANCED_GLOBAL_UNLOCK",len(s.technology_frontier),"QUARANTINE",
            f"{future} future-dated and {initial} start-boundary frontier records lack causal authority provenance"))
    technology_frontier=()

    actor_state=s.actor_state_v1
    if actor_state is not None:
        actors=[]
        budget_count=cap_count=access_count=experience_count=0
        for a in actor_state.actors:
            spend=a.budget.spendable_allocation
            if _fixture_ref(spend.provenance_refs):
                budget_count+=1
                spend=SpendableAllocation(status="UNKNOWN",amount=None,unit=None,scope=spend.scope,
                    provenance_refs=(PURGE_ID+":QUARANTINED_MACHINERY_TEST_BUDGET",))
            installed=_purge_factset(a.installed_capability)
            provider=_purge_factset(a.provider_service_access)
            experience=_purge_factset(a.experience)
            cap_count += len(a.installed_capability.records)-len(installed.records)
            access_count += len(a.provider_service_access.records)-len(provider.records)
            experience_count += len(a.experience.records)-len(experience.records)
            actors.append(replace(a,budget=ActorBudget(spend,a.budget.committed_funds),
                                  installed_capability=installed,provider_service_access=provider,
                                  experience=experience))
        kept_events=tuple(e for e in actor_state.events
                          if not _fixture_ref((e.provenance_class,e.provenance_ref)))
        removed_events=len(actor_state.events)-len(kept_events)
        actor_state=replace(actor_state,actors=tuple(actors),events=kept_events)
        for surface,count,why in (
            ("actor_initial_spendable_budget",budget_count,"derived from authored allocation fractions, not spendable-budget authority"),
            ("actor_installed_capability",cap_count,"machinery-test capability bridge is not observed/earned actor state"),
            ("actor_provider_service_access",access_count,"generic machinery-test access is not a physical/service entitlement"),
            ("actor_exploration_priority",experience_count,"authored behavior weight is test policy, not actor authority"),
            ("actor_future_events",removed_events,"scripted future budget/capability events cannot drive causal history")):
            if count: inv.append(AuthorityDispositionV03(surface,"NON_CANON_MACHINERY_TEST",count,"QUARANTINE",why))

    access=s.accessibility_v1
    if access is not None:
        kept=tuple(x for x in access.service_paths if not _fixture_ref(x.provenance_refs))
        removed=len(access.service_paths)-len(kept)
        if removed: inv.append(AuthorityDispositionV03("accessibility_service_paths","NON_CANON_OR_PLACEHOLDER_SERVICE",removed,"QUARANTINE",
            "generic/placeholder service paths are not earned physical transport services"))
        access=replace(access,service_paths=kept)

    demand=s.demand_pressure_v1
    if demand is not None:
        kept=tuple(x for x in demand.strategic_requirements if not _fixture_ref(x.provenance_refs))
        removed=len(demand.strategic_requirements)-len(kept)
        if removed: inv.append(AuthorityDispositionV03("strategic_requirements","NON_CANON_MACHINERY_TEST",removed,"QUARANTINE",
            "authored 2026-2035 bootstrap demand is not endogenous demand"))
        demand=replace(demand,strategic_requirements=kept)

    mission=s.mission_knowledge_v1
    if mission is not None:
        # Scenario priors are not observations.  Remove binary questions whose
        # 2026 belief is explicitly scenario-authored, plus their dependent mission
        # and decision machinery.  Solar characterization questions already carry
        # UNKNOWN priors and remain available as blocked opportunities.
        bad_questions={q.question_id for q in mission.questions
                       if "SCENARIO" in q.prior_status.upper()}
        if bad_questions:
            bad_missions={m.mission_archetype_id for m in mission.missions
                          if m.target_question_id in bad_questions}
            kept_missions=tuple(m for m in mission.missions if m.mission_archetype_id not in bad_missions)
            used_models={m.observation_model_id for m in kept_missions if m.observation_model_id is not None}
            mission=replace(mission,
                questions=tuple(q for q in mission.questions if q.question_id not in bad_questions),
                missions=kept_missions,
                decision_models=tuple(dm for dm in mission.decision_models if dm.mission_archetype_id not in bad_missions),
                observation_models=tuple(o for o in mission.observation_models if o.observation_model_id in used_models))
            inv.append(AuthorityDispositionV03("mission_scenario_prior","SCENARIO_AUTHORED_2026_BELIEF",len(bad_questions),"QUARANTINE",
                "scenario prior is not observed actor knowledge and cannot seed causal mission EV"))
        decisions=[]; removed_values=0
        for dm in mission.decision_models:
            sv=dm.success_value
            if sv.status=="SCENARIO_ASSUMPTION" or _fixture_ref(sv.provenance_refs):
                removed_values+=1
                sv=DecisionValue(status="UNKNOWN",value=None,unit=sv.unit,
                    provenance_refs=(PURGE_ID+":NO_EARNED_SUCCESS_VALUE",))
            decisions.append(replace(dm,success_value=sv))
        if removed_values: inv.append(AuthorityDispositionV03("mission_success_value","SCENARIO_ASSUMPTION",removed_values,"QUARANTINE",
            "authored follow-on value cannot create positive mission EV"))
        mission=replace(mission,decision_models=tuple(decisions))

    # Legacy actor_capability is a parallel scenario mechanism. Actor State is the
    # typed authority boundary in the causal runtime; do not silently fall through.
    if s.actor_capability:
        inv.append(AuthorityDispositionV03("legacy_actor_capability","LEGACY_PARALLEL_AUTHORITY",len(s.actor_capability),"QUARANTINE",
            "causal runtime must not fall back to legacy capability fixtures"))
    # Explicitly distinguish retained model/boundary inputs from authority that can
    # autonomously unlock future facts. Retention here is not promotion to canon.
    inv.append(AuthorityDispositionV03("location_initial_state","2026_START_BOUNDARY_INPUT",len(s.locations),"RETAIN",
        "start-state input remains a boundary condition; it does not authorize future changes by date"))
    if s.project_economics_v1 is not None:
        inv.append(AuthorityDispositionV03("project_economics_v1","MODEL_PARAMETER_CONTRACT",1,"RETAIN",
            "cost/lag model parameters may evaluate causal choices but are not scheduled future world facts"))
    if demand is not None:
        inv.append(AuthorityDispositionV03("demand_pressure_channels","UNCALIBRATED_CAUSAL_MODEL_PARAMETER",len(demand.channels),"RETAIN",
            "state-derived pressure parameters remain explicit model machinery, not authored annual demand"))
    if access is not None:
        inv.append(AuthorityDispositionV03("qualified_accessibility_evidence","EVIDENCE_BACKED_SERVICE_OR_GEOMETRY",len(access.service_paths),"RETAIN",
            "only service paths surviving provenance quarantine remain in the typed accessibility boundary"))

    scenario=replace(s,technology_frontier=technology_frontier,actor_capability=(),
                     actor_state_v1=actor_state,accessibility_v1=access,
                     demand_pressure_v1=demand,mission_knowledge_v1=mission)
    clean=replace(bundle,scenario=scenario)
    inv.append(AuthorityDispositionV03("demographic_authority_v1","PROMOTED_EXTERNAL_BOUNDARY",
        0 if s.demographic_authority_v1 is None else 1,"RETAIN",
        "future exogenous Earth demography is explicitly governed authority, not a machinery-test future"))
    return PurgedBundleV03(clean,tuple(inv))
