from __future__ import annotations
from dataclasses import fields, is_dataclass
import json
from .model import Node, Account, Transaction, Commitment, Project, Asset, FixedCapitalFormationEvent, EarthImpactLedger, KernelState
from .mvp_state import SystemState, AggregateState, EntityAssetRef, AgentState, FinancingRequest, FinancingDecision, ScenarioResource, Observation, ColonyState, PopulationLedger
from .policy import SnapshotFact, DecisionSnapshot, PolicyContext
from .scheduler import ScheduledEvent, CouplingSpec
from .underwriting import UnderwritingInput, UnderwritingTable
from .resolution import ResolutionExposurePlan, ResolutionExposureRecord

ODD_SCHEMA_REGISTRY_VERSION='ODD_SCHEMA_REGISTRY_0_1'

ODD_SCHEMA_TYPES=(
    Node,Account,Transaction,Commitment,Project,Asset,FixedCapitalFormationEvent,EarthImpactLedger,KernelState,
    SystemState,AggregateState,EntityAssetRef,AgentState,FinancingRequest,FinancingDecision,ScenarioResource,Observation,
    ColonyState,PopulationLedger,SnapshotFact,DecisionSnapshot,PolicyContext,ScheduledEvent,CouplingSpec,
    UnderwritingInput,UnderwritingTable,ResolutionExposurePlan,ResolutionExposureRecord,
)

def executable_schema_registry():
    out={}
    for cls in ODD_SCHEMA_TYPES:
        if not is_dataclass(cls):
            raise TypeError(f'ODD schema type is not dataclass: {cls.__name__}')
        out[cls.__name__]=[f.name for f in fields(cls)]
    return dict(sorted(out.items()))

def canonical_registry_json():
    return json.dumps({
        'registry_version':ODD_SCHEMA_REGISTRY_VERSION,
        'types':executable_schema_registry(),
    },sort_keys=True,separators=(',',':'))
