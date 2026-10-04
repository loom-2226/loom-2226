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
    SponsorProjectDecisionRequest, SponsorProjectDecision,
    OperatingCycleRequest, OperatingCycleDecision,
    SaleDecisionRequest, SaleDecision,
    SurplusDistributionRequest, SurplusDistributionDecision,
    SettlementSupportRequest, SettlementSupportDecision,
    ScenarioResource, Observation, ColonyState, PopulationLedger, RuntimeObjectClass, AgentKind,
    ActionKind, FinancingDecisionOutcome, FinancingReasonCode, ExplorationDecisionOutcome, ExplorationReasonCode,
    PublicationDecisionOutcome, PublicationReasonCode,
    SponsorProjectDecisionOutcome, SponsorProjectReasonCode,
    OperatingCycleDecisionOutcome, OperatingCycleReasonCode,
    SaleDecisionOutcome, SaleReasonCode,
    SurplusDistributionDecisionOutcome, SurplusDistributionReasonCode,
    SettlementSupportDecisionOutcome, SettlementSupportReasonCode,
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
from .project_lifecycle import (
    ProjectDevelopmentPlan, DevelopmentStageRecord, DevelopmentResolutionRecord,
    DevelopmentStageOutcome, DevelopmentResolutionOutcome,
)
from .surface_prospecting import (
    SurfaceProspectingModel, SurfaceProspectingWorldRecord,
    ObservationBeliefUpdateRecord,
)
from .operating import OperatingCostRecord, ExtractionResolutionRecord
from .enterprise import (
    EnterpriseReviewRequest, EnterpriseReviewDecision, EnterpriseReviewRecord,
    EnterpriseReviewDecisionOutcome, EnterpriseReviewReasonCode,
)
from .market import CommodityMarketEnvelope, MarketClearingRecord
from .distribution import FinancingReturnClaim, OwnerDistributionAllocation, SurplusDistributionRecord
from .settlement import (
    SettlementInfrastructurePlan, SettlementInfrastructureRecord,
    SettlementStageRecord, SettlementSupportExecutionRecord,
)
from .transport import (
    TechnologyCapabilityState, TransportRelationship, TransportQualificationRecord,
    TransportSettlementRequest, TransportSettlementDecision,
    PassengerTransportDepartureRecord, PassengerTransportArrivalRecord,
    TransportSettlementDecisionOutcome, TransportSettlementReasonCode,
)
from .project_activity import (
    ProjectActivity, ProjectActivityTransitionRecord, ProjectActivityInformationRecord,
    SponsorPortfolioDecisionRequest, SponsorPortfolioDecision,
    ProjectActivityStatus, SponsorPortfolioDecisionOutcome, SponsorPortfolioReasonCode,
)
from .project_study import (
    ProjectStudyState,ProjectStudyPlan,ProjectActivityExpenseRecord,ProjectStudyResultRecord,
    ProjectStudyReviewRequest,ProjectStudyReviewDecision,ProjectStudyReviewExecutionRecord,
    ProjectStudyMaturity,ProjectStudyResultStanding,ProjectStudyReviewOutcome,
    ProjectStudyReviewReasonCode,
)
from .policies.manifest import (PolicyParameter, FinancierPolicyManifest, PolicyParameterStatus, ObservationKnowledgeRelation)
from .policy_runner import PolicyExecutionResult

ODD_SCHEMA_REGISTRY_VERSION='ODD_SCHEMA_REGISTRY_0_18'

ODD_SCHEMA_TYPES=(
    Node,Account,Transaction,Commitment,Project,Asset,FixedCapitalFormationEvent,EarthImpactLedger,KernelState,
    SystemState,AggregateState,EntityAssetRef,AgentState,FinancingRequest,FinancingDecision,ExplorationRequest,ExplorationDecision,
    PublicationRequest,PublicationDecision,PublicInformationArtifact,SponsorProjectDecisionRequest,SponsorProjectDecision,OperatingCycleRequest,OperatingCycleDecision,SaleDecisionRequest,SaleDecision,SurplusDistributionRequest,SurplusDistributionDecision,SettlementSupportRequest,SettlementSupportDecision,ScenarioResource,Observation,
    ColonyState,PopulationLedger,SnapshotFact,DecisionSnapshot,PolicyContext,ScheduledEvent,CouplingSpec,
    UnderwritingInput,UnderwritingTable,ResolutionExposurePlan,ResolutionExposureRecord,
    ReplayProvenance,ScheduledRunResult,DecisionEpochRecord,ProjectDevelopmentPlan,DevelopmentStageRecord,DevelopmentResolutionRecord,
    SurfaceProspectingModel,SurfaceProspectingWorldRecord,ObservationBeliefUpdateRecord,
    OperatingCostRecord,ExtractionResolutionRecord,EnterpriseReviewRequest,EnterpriseReviewDecision,EnterpriseReviewRecord,CommodityMarketEnvelope,MarketClearingRecord,FinancingReturnClaim,OwnerDistributionAllocation,SurplusDistributionRecord,SettlementInfrastructurePlan,SettlementInfrastructureRecord,SettlementStageRecord,SettlementSupportExecutionRecord,
    TechnologyCapabilityState,TransportRelationship,TransportQualificationRecord,
    TransportSettlementRequest,TransportSettlementDecision,
    PassengerTransportDepartureRecord,PassengerTransportArrivalRecord,
    ProjectActivity,ProjectActivityTransitionRecord,ProjectActivityInformationRecord,
    SponsorPortfolioDecisionRequest,SponsorPortfolioDecision,
    ProjectStudyState,ProjectStudyPlan,ProjectActivityExpenseRecord,ProjectStudyResultRecord,
    ProjectStudyReviewRequest,ProjectStudyReviewDecision,ProjectStudyReviewExecutionRecord,
    PolicyParameter,FinancierPolicyManifest,PolicyExecutionResult,
)

ODD_ENUM_TYPES=(
    NodeKind,AccountKind,TxPurpose,AssetKind,
    RuntimeObjectClass,AgentKind,ActionKind,FinancingDecisionOutcome,FinancingReasonCode,ExplorationDecisionOutcome,ExplorationReasonCode,
    PublicationDecisionOutcome,PublicationReasonCode,SponsorProjectDecisionOutcome,SponsorProjectReasonCode,
    OperatingCycleDecisionOutcome,OperatingCycleReasonCode,EnterpriseReviewDecisionOutcome,EnterpriseReviewReasonCode,SaleDecisionOutcome,SaleReasonCode,SurplusDistributionDecisionOutcome,SurplusDistributionReasonCode,SettlementSupportDecisionOutcome,SettlementSupportReasonCode,
    TransportSettlementDecisionOutcome,TransportSettlementReasonCode,
    ProjectActivityStatus,SponsorPortfolioDecisionOutcome,SponsorPortfolioReasonCode,
    ProjectStudyMaturity,ProjectStudyResultStanding,ProjectStudyReviewOutcome,
    ProjectStudyReviewReasonCode,
    DevelopmentStageOutcome,DevelopmentResolutionOutcome,
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
    'ProjectActivity.earliest_start':'SIM_TIME',
    'ProjectActivity.planned_duration':'SIM_TIME_DURATION',
    'ProjectActivity.capital_commitment':'MODEL_CURRENCY',
    'ProjectActivity.window_open':'SIM_TIME',
    'ProjectActivity.window_close':'SIM_TIME',
    'ProjectActivity.authorized_at':'SIM_TIME',
    'ProjectActivity.actual_start':'SIM_TIME',
    'ProjectActivity.planned_completion':'SIM_TIME',
    'ProjectActivity.actual_completion':'SIM_TIME',
    'ProjectActivityTransitionRecord.effective_time':'SIM_TIME',
    'ProjectActivityInformationRecord.admitted_at':'SIM_TIME',
    'SponsorPortfolioDecisionRequest.effective_time':'SIM_TIME',
    'SponsorPortfolioDecision.reserved_capital':'FIELD:SponsorPortfolioDecisionRequest.currency_unit',
    'ProjectActivityExpenseRecord.amount':'MODEL_CURRENCY',
    'ProjectActivityExpenseRecord.spent_at':'SIM_TIME',
    'ProjectStudyResultRecord.completed_at':'SIM_TIME',
    'ProjectStudyReviewExecutionRecord.effective_time':'SIM_TIME',
    'Asset.book_value':'MODEL_CURRENCY',
    'Asset.capacity':'ASSET_CLASS_CAPACITY_UNIT',
    'FixedCapitalFormationEvent.amount':'MODEL_CURRENCY',
    'FixedCapitalFormationEvent.year':'SIM_YEAR',
    'EarthImpactLedger.qualifying_supplied_expenditure':'MODEL_CURRENCY',
    'EarthImpactLedger.terrestrial_fcf_delta':'MODEL_CURRENCY',
    'EarthImpactLedger.capital_diverted_to_offworld':'MODEL_CURRENCY',
    'EarthImpactLedger.capital_returned_to_earth':'MODEL_CURRENCY',
    'EarthImpactLedger.offworld_purchases_from_earth':'MODEL_CURRENCY',
    'EarthImpactLedger.earth_purchases_from_offworld':'MODEL_CURRENCY',
    'EarthImpactLedger.migration_from_earth':'PEOPLE_EQUIVALENT',
    'EarthImpactLedger.returning_population':'PEOPLE_EQUIVALENT',
    'FinancingRequest.amount':'FIELD:FinancingRequest.currency_unit',
    'FinancingRequest.year':'SIM_YEAR',
    'FinancingDecision.amount':'REQUEST_CURRENCY_UNIT',
    'ExplorationRequest.year':'SIM_YEAR',
    'ExplorationDecision.authorized_cost':'REQUEST_CURRENCY_UNIT',
    'PublicationRequest.year':'SIM_YEAR',
    'SponsorProjectDecisionRequest.year':'SIM_YEAR',
    'SponsorProjectDecision.requested_financing':'REQUEST_CURRENCY_UNIT',
    'OperatingCycleRequest.year':'SIM_YEAR',
    'OperatingCycleDecision.requested_financing':'REQUEST_CURRENCY_UNIT',
    'OperatingCycleDecision.planned_quantity':'FIELD:OperatingCycleRequest.quantity_unit',
    'OperatingCycleDecision.authorized_opex':'FIELD:OperatingCycleRequest.currency_unit',
    'OperatingCostRecord.year':'SIM_YEAR',
    'OperatingCostRecord.planned_quantity':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'OperatingCostRecord.unit_opex':'MODEL_CURRENCY_PER_RESOURCE_UNIT',
    'OperatingCostRecord.total_opex':'MODEL_CURRENCY',
    'ExtractionResolutionRecord.year':'SIM_YEAR',
    'ExtractionResolutionRecord.planned_quantity':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'ExtractionResolutionRecord.actual_extracted':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'ExtractionResolutionRecord.resource_before':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'ExtractionResolutionRecord.resource_after':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'ExtractionResolutionRecord.inventory_before':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'ExtractionResolutionRecord.inventory_after':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'EnterpriseReviewRequest.year':'SIM_YEAR',
    'EnterpriseReviewRecord.year':'SIM_YEAR',
    'EnterpriseReviewRecord.planned_quantity':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'EnterpriseReviewRecord.actual_output':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'SaleDecisionRequest.year':'SIM_YEAR',
    'SaleDecision.offered_quantity':'FIELD:SaleDecisionRequest.quantity_unit',
    'CommodityMarketEnvelope.year':'SIM_YEAR',
    'CommodityMarketEnvelope.unit_price':'MODEL_CURRENCY_PER_RESOURCE_UNIT',
    'CommodityMarketEnvelope.demand_quantity':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'MarketClearingRecord.year':'SIM_YEAR',
    'MarketClearingRecord.offered_quantity':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'MarketClearingRecord.demand_before':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'MarketClearingRecord.cleared_quantity':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'MarketClearingRecord.demand_after':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'MarketClearingRecord.unit_price':'MODEL_CURRENCY_PER_RESOURCE_UNIT',
    'MarketClearingRecord.transaction_value':'MODEL_CURRENCY',
    'MarketClearingRecord.local_inventory_before':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'MarketClearingRecord.local_inventory_after':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'MarketClearingRecord.market_inventory_before':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'MarketClearingRecord.market_inventory_after':'MODEL_RESOURCE_UNIT_BY_FAMILY',
    'SurplusDistributionRequest.year':'SIM_YEAR',
    'SurplusDistributionDecision.reserve':'FIELD:SurplusDistributionRequest.currency_unit',
    'SurplusDistributionDecision.financier_return':'FIELD:SurplusDistributionRequest.currency_unit',
    'SurplusDistributionDecision.local_reinvestment':'FIELD:SurplusDistributionRequest.currency_unit',
    'SurplusDistributionDecision.owner_distribution':'FIELD:SurplusDistributionRequest.currency_unit',
    'FinancingReturnClaim.maximum_return_amount':'MODEL_CURRENCY',
    'OwnerDistributionAllocation.ownership_share':'DIMENSIONLESS_SHARE',
    'OwnerDistributionAllocation.amount':'MODEL_CURRENCY',
    'SurplusDistributionRecord.year':'SIM_YEAR',
    'SurplusDistributionRecord.opening_project_cash':'MODEL_CURRENCY',
    'SurplusDistributionRecord.reserve':'MODEL_CURRENCY',
    'SurplusDistributionRecord.financier_return':'MODEL_CURRENCY',
    'SurplusDistributionRecord.local_reinvestment':'MODEL_CURRENCY',
    'SurplusDistributionRecord.owner_distribution':'MODEL_CURRENCY',
    'SurplusDistributionRecord.closing_project_cash':'MODEL_CURRENCY',
    'PopulationLedger.earth':'PEOPLE_EQUIVALENT',
    'PopulationLedger.offworld':'PEOPLE_EQUIVALENT_BY_NODE',
    'PopulationLedger.in_transit':'PEOPLE_EQUIVALENT_BY_TRANSPORT_BATCH',
    'TechnologyCapabilityState.effective_from':'SIM_TIME',
    'TechnologyCapabilityState.effective_to':'SIM_TIME',
    'TransportRelationship.effective_from':'SIM_TIME',
    'TransportRelationship.effective_to':'SIM_TIME',
    'TransportRelationship.cost_per_passenger':'MODEL_CURRENCY_PER_PERSON',
    'TransportRelationship.travel_time':'SIM_TIME_DURATION',
    'TransportRelationship.energy_per_passenger':'MODEL_ENERGY_PER_PERSON',
    'TransportRelationship.loss_risk':'PROBABILITY',
    'TransportRelationship.capacity':'PEOPLE_EQUIVALENT',
    'TransportQualificationRecord.effective_time':'SIM_TIME',
    'TransportSettlementRequest.departure_time':'SIM_TIME',
    'TransportSettlementRequest.requested_residents':'FIELD:TransportSettlementRequest.population_unit',
    'TransportSettlementRequest.support_cost':'FIELD:TransportSettlementRequest.currency_unit',
    'TransportSettlementDecision.authorized_residents':'REQUEST_POPULATION_UNIT',
    'TransportSettlementDecision.support_amount':'REQUEST_CURRENCY_UNIT',
    'TransportSettlementDecision.transport_amount':'REQUEST_CURRENCY_UNIT',
    'TransportSettlementDecision.departure_time':'SIM_TIME',
    'TransportSettlementDecision.arrival_time':'SIM_TIME',
    'PassengerTransportDepartureRecord.passengers':'PEOPLE_EQUIVALENT',
    'PassengerTransportDepartureRecord.support_amount':'MODEL_CURRENCY',
    'PassengerTransportDepartureRecord.transport_amount':'MODEL_CURRENCY',
    'PassengerTransportDepartureRecord.departure_time':'SIM_TIME',
    'PassengerTransportDepartureRecord.arrival_time':'SIM_TIME',
    'PassengerTransportDepartureRecord.earth_population_before':'PEOPLE_EQUIVALENT',
    'PassengerTransportDepartureRecord.earth_population_after':'PEOPLE_EQUIVALENT',
    'PassengerTransportDepartureRecord.in_transit_before':'PEOPLE_EQUIVALENT',
    'PassengerTransportDepartureRecord.in_transit_after':'PEOPLE_EQUIVALENT',
    'PassengerTransportDepartureRecord.total_population_before':'PEOPLE_EQUIVALENT',
    'PassengerTransportDepartureRecord.total_population_after':'PEOPLE_EQUIVALENT',
    'PassengerTransportDepartureRecord.subsidy_before':'MODEL_CURRENCY',
    'PassengerTransportDepartureRecord.subsidy_after':'MODEL_CURRENCY',
    'PassengerTransportArrivalRecord.passengers':'PEOPLE_EQUIVALENT',
    'PassengerTransportArrivalRecord.arrival_time':'SIM_TIME',
    'PassengerTransportArrivalRecord.in_transit_before':'PEOPLE_EQUIVALENT',
    'PassengerTransportArrivalRecord.in_transit_after':'PEOPLE_EQUIVALENT',
    'PassengerTransportArrivalRecord.offworld_population_before':'PEOPLE_EQUIVALENT',
    'PassengerTransportArrivalRecord.offworld_population_after':'PEOPLE_EQUIVALENT',
    'PassengerTransportArrivalRecord.total_population_before':'PEOPLE_EQUIVALENT',
    'PassengerTransportArrivalRecord.total_population_after':'PEOPLE_EQUIVALENT',
    'ColonyState.population':'PEOPLE_EQUIVALENT',
    'ColonyState.habitat_capacity':'PEOPLE_EQUIVALENT',
    'SettlementSupportRequest.year':'SIM_YEAR',
    'SettlementSupportRequest.requested_residents':'FIELD:SettlementSupportRequest.population_unit',
    'SettlementSupportRequest.support_cost':'FIELD:SettlementSupportRequest.currency_unit',
    'SettlementSupportDecision.authorized_residents':'REQUEST_POPULATION_UNIT',
    'SettlementSupportDecision.support_amount':'REQUEST_CURRENCY_UNIT',
    'SettlementInfrastructurePlan.year':'SIM_YEAR',
    'SettlementInfrastructurePlan.infrastructure_cost':'MODEL_CURRENCY',
    'SettlementInfrastructurePlan.habitat_capacity':'PEOPLE_EQUIVALENT',
    'SettlementInfrastructureRecord.year':'SIM_YEAR',
    'SettlementInfrastructureRecord.cost':'MODEL_CURRENCY',
    'SettlementInfrastructureRecord.habitat_capacity_added':'PEOPLE_EQUIVALENT',
    'SettlementInfrastructureRecord.infrastructure_before':'MODEL_CURRENCY',
    'SettlementInfrastructureRecord.infrastructure_after':'MODEL_CURRENCY',
    'SettlementInfrastructureRecord.habitat_capacity_before':'PEOPLE_EQUIVALENT',
    'SettlementInfrastructureRecord.habitat_capacity_after':'PEOPLE_EQUIVALENT',
    'SettlementStageRecord.year':'SIM_YEAR',
    'SettlementStageRecord.productive_capital':'MODEL_CURRENCY',
    'SettlementStageRecord.production_capacity':'ASSET_CLASS_CAPACITY_UNIT',
    'SettlementStageRecord.population':'PEOPLE_EQUIVALENT',
    'SettlementStageRecord.infrastructure':'MODEL_CURRENCY',
    'SettlementStageRecord.habitat_capacity':'PEOPLE_EQUIVALENT',
    'SettlementStageRecord.external_subsidy':'MODEL_CURRENCY',
    'SettlementSupportExecutionRecord.year':'SIM_YEAR',
    'SettlementSupportExecutionRecord.authorized_residents':'PEOPLE_EQUIVALENT',
    'SettlementSupportExecutionRecord.support_amount':'MODEL_CURRENCY',
    'SettlementSupportExecutionRecord.earth_population_before':'PEOPLE_EQUIVALENT',
    'SettlementSupportExecutionRecord.earth_population_after':'PEOPLE_EQUIVALENT',
    'SettlementSupportExecutionRecord.offworld_population_before':'PEOPLE_EQUIVALENT',
    'SettlementSupportExecutionRecord.offworld_population_after':'PEOPLE_EQUIVALENT',
    'SettlementSupportExecutionRecord.total_population_before':'PEOPLE_EQUIVALENT',
    'SettlementSupportExecutionRecord.total_population_after':'PEOPLE_EQUIVALENT',
    'SettlementSupportExecutionRecord.subsidy_before':'MODEL_CURRENCY',
    'SettlementSupportExecutionRecord.subsidy_after':'MODEL_CURRENCY',
    'ProjectDevelopmentPlan.required_cost':'MODEL_CURRENCY',
    'ProjectDevelopmentPlan.stage_schedule':'SIM_YEAR_AND_MODEL_CURRENCY_SCHEDULE',
    'ProjectDevelopmentPlan.completion_year':'SIM_YEAR',
    'ProjectDevelopmentPlan.commissioned_capacity':'ASSET_CLASS_CAPACITY_UNIT',
    'DevelopmentStageRecord.year':'SIM_YEAR',
    'DevelopmentStageRecord.planned_amount':'MODEL_CURRENCY',
    'DevelopmentResolutionRecord.year':'SIM_YEAR',
    'DevelopmentResolutionRecord.required_cost':'MODEL_CURRENCY',
    'DevelopmentResolutionRecord.accumulated_cost':'MODEL_CURRENCY',
    'DevelopmentResolutionRecord.commissioned':'MODEL_CURRENCY',
    'DevelopmentResolutionRecord.written_off':'MODEL_CURRENCY',
    'SurfaceProspectingModel.world_false_positive':'PROBABILITY',
    'SurfaceProspectingModel.world_false_negative':'PROBABILITY',
    'SurfaceProspectingModel.agent_detection_rate':'PROBABILITY',
    'SurfaceProspectingModel.agent_false_positive_rate':'PROBABILITY',
    'SurfaceProspectingModel.remote_world_false_positive_reference':'PROBABILITY',
    'SurfaceProspectingModel.remote_world_false_negative_reference':'PROBABILITY',
    'SurfaceProspectingWorldRecord.year':'SIM_YEAR',
    'SurfaceProspectingWorldRecord.world_false_positive':'PROBABILITY',
    'SurfaceProspectingWorldRecord.world_false_negative':'PROBABILITY',
    'SurfaceProspectingWorldRecord.deterministic_draw':'UNIT_INTERVAL_DRAW',
    'ObservationBeliefUpdateRecord.year':'SIM_YEAR',
    'ObservationBeliefUpdateRecord.prior':'PROBABILITY',
    'ObservationBeliefUpdateRecord.posterior':'PROBABILITY',
    'ObservationBeliefUpdateRecord.detection_rate':'PROBABILITY',
    'ObservationBeliefUpdateRecord.false_positive_rate':'PROBABILITY',
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
