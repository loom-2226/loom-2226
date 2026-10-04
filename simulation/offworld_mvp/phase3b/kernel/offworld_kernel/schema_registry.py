from __future__ import annotations
from dataclasses import fields, is_dataclass
from enum import Enum
import json

from .model import (
    Node, Account, Transaction, Commitment, Project, Asset, FixedCapitalFormationEvent,
    EarthImpactLedger, KernelState, NodeKind, AccountKind, TxPurpose, AssetKind,
)
from .mvp_state import (
    SystemState, AggregateState, EntityAssetRef, AgentState, FinancingRequest, FinancingDecision,
    ExplorationRequest, ExplorationDecision, PublicationRequest, PublicationDecision, PublicInformationArtifact,
    ScenarioResource, Observation, ColonyState, PopulationLedger, RuntimeObjectClass, AgentKind,
    ActionKind, FinancingDecisionOutcome, FinancingReasonCode, ExplorationDecisionOutcome, ExplorationReasonCode,
    PublicationDecisionOutcome, PublicationReasonCode,
    SponsorProjectDecisionOutcome, SponsorProjectReasonCode,
)
from .policy import SnapshotFact, DecisionSnapshot, PolicyContext, FactState
from .scheduler import ScheduledEvent, CouplingSpec, Phase
from .underwriting import (
    UnderwritingInput, UnderwritingTable, UnderwritingInputKind, UnderwritingInputStatus,
)
from .resolution import (
    ResolutionExposurePlan, ResolutionExposureRecord, ExposureSelectionBasis, ExposureAllocationBasis,
)
from .ensemble import AxisKind, SpreadMeaning
from .validation import VerificationLevel, ValidationLevel, OutOfSampleStatus
from .provenance import ReplayProvenance
from .runtime import ScheduledRunResult
from .methodology import DecisionEpochRecord
from .policies.manifest import (PolicyParameter, FinancierPolicyManifest, PolicyParameterStatus, ObservationKnowledgeRelation)
from .policy_runner import PolicyExecutionResult

ODD_SCHEMA_REGISTRY_VERSION='ODD_SCHEMA_REGISTRY_0_7'

ODD_SCHEMA_TYPES=(
    Node,Account,Transaction,Commitment,Project,Asset,FixedCapitalFormationEvent,EarthImpactLedger,KernelState,
    SystemState,AggregateState,EntityAssetRef,AgentState,FinancingRequest,FinancingDecision,ExplorationRequest,ExplorationDecision,
    PublicationRequest,PublicationDecision,PublicInformationArtifact,SponsorProjectDecisionRequest,SponsorProjectDecision,ScenarioResource,Observation,
    ColonyState,PopulationLedger,SnapshotFact,DecisionSnapshot,PolicyContext,ScheduledEvent,CouplingSpec,
    UnderwritingInput,UnderwritingTable,ResolutionExposurePlan,ResolutionExposureRecord,
    ReplayProvenance,ScheduledRunResult,DecisionEpochRecord,PolicyParameter,FinancierPolicyManifest,PolicyExecutionResult,
)

ODD_ENUM_TYPES=(
    NodeKind,AccountKind,TxPurpose,AssetKind,
    RuntimeObjectClass,AgentKind,ActionKind,FinancingDecisionOutcome,FinancingReasonCode,ExplorationDecisionOutcome,ExplorationReasonCode,
    PublicationDecisionOutcome,PublicationReasonCode,SponsorProjectDecisionOutcome,SponsorProjectReasonCode,
    FactState,Phase,UnderwritingInputKind,UnderwritingInputStatus,
    ExposureSelectionBasis,ExposureAllocationBasis,AxisKind,SpreadMeaning,
    VerificationLevel,ValidationLevel,OutOfSampleStatus,PolicyParameterStatus,ObservationKnowledgeRelation,
)

# These are semantic unit contracts, not a claim that every current logical field has an SI unit.
# "FIELD:<Type>.<field>" means the unit is carried by another declared field.
# "MODEL_*" units remain MVP logical units unless separately qualified.
ODD_UNIT_CONTRACTS={
    'Account.balance':'MODEL_CURRENCY',
    'Transaction.amount':'MODEL_CURRENCY',
    'Transaction.year':'SIM_YEAR',
    'Commitment.amount':'MODEL_CURRENCY',
    'Commitment.committed':'MODEL_CURRENCY',
    'Commitment.disbursed':'MODEL_CURRENCY',
    'Commitment.lapsed':'MODEL_CURRENCY',
    'Project':'NO_INTRINSIC_SCALAR_UNIT',
    'Asset.book_value':'MODEL_CURRENCY',
    'Asset.capacity':'ASSET_CLASS_CAPACITY_UNIT',
    'FixedCapitalFormationEvent.amount':'MODEL_CURRENCY',
    'FixedCapitalFormationEvent.year':'SIM_YEAR',
    'EarthImpactLedger.qualifying_supplied_expenditure':'MODEL_CURRENCY',
    'EarthImpactLedger.terrestrial_fcf_delta':'MODEL_CURRENCY',
    'FinancingRequest.amount':'FIELD:FinancingRequest.currency_unit',
    'FinancingRequest.year':'SIM_YEAR',
    'FinancingDecision.amount':'REQUEST_CURRENCY_UNIT',
    'ExplorationRequest.year':'SIM_YEAR',
    'ExplorationDecision.authorized_cost':'REQUEST_CURRENCY_UNIT',
    'PublicationRequest.year':'SIM_YEAR',
    'SponsorProjectDecisionRequest.year':'SIM_YEAR',
    'SponsorProjectDecision.requested_financing':'REQUEST_CURRENCY_UNIT',
    'PublicInformationArtifact.year':'SIM_YEAR',
    'ScenarioResource.in_situ':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'ScenarioResource.accessible':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'ScenarioResource.recoverable':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'ScenarioResource.remaining':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'Observation.year':'SIM_YEAR',
    'DecisionSnapshot.effective_time':'SIM_TIME',
    'ScheduledEvent.effective_time':'SIM_TIME',
    'UnderwritingInput.value':'FIELD:UnderwritingInput.unit',
    'UnderwritingInput.sensitivity_low':'FIELD:UnderwritingInput.unit',
    'UnderwritingInput.sensitivity_high':'FIELD:UnderwritingInput.unit',
    'UnderwritingInput.basis_year':'SIM_YEAR',
    'UnderwritingInput.valid_from':'SIM_YEAR',
    'UnderwritingInput.valid_to':'SIM_YEAR',
    'ResolutionExposureRecord.allocation_fraction':'DIMENSIONLESS_SHARE',
    'PolicyParameter.value':'FIELD:PolicyParameter.unit',
    'PolicyParameter.sensitivity_low':'FIELD:PolicyParameter.unit',
    'PolicyParameter.sensitivity_high':'FIELD:PolicyParameter.unit',
    'PolicyParameter.local_perturbation':'FIELD:PolicyParameter.unit',
    'FinancierPolicyManifest.world_detection_rate':'PROBABILITY',
    'FinancierPolicyManifest.world_false_positive_rate':'PROBABILITY',
}


def _type_repr(t):
    if isinstance(t,str):
        return t
    return str(t).replace('typing.','')

def executable_schema_registry():
    out={}
    for cls in ODD_SCHEMA_TYPES:
        if not is_dataclass(cls):
            raise TypeError(f'ODD schema type is not dataclass: {cls.__name__}')
        out[cls.__name__]=[
            {'name':f.name,'type':_type_repr(f.type)}
            for f in fields(cls)
        ]
    return dict(sorted(out.items()))

def executable_enum_registry():
    out={}
    for cls in ODD_ENUM_TYPES:
        if not issubclass(cls,Enum):
            raise TypeError(f'ODD enum type is not Enum: {cls.__name__}')
        out[cls.__name__]=[m.value for m in cls]
    return dict(sorted(out.items()))

def executable_unit_registry():
    return dict(sorted(ODD_UNIT_CONTRACTS.items()))

def canonical_registry_payload():
    return {
        'registry_version':ODD_SCHEMA_REGISTRY_VERSION,
        'types':executable_schema_registry(),
        'enums':executable_enum_registry(),
        'units':executable_unit_registry(),
    }

def canonical_registry_json():
    return json.dumps(canonical_registry_payload(),sort_keys=True,separators=(',',':'))
