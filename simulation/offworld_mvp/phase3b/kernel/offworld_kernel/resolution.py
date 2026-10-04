from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Tuple
from .kernel import InvariantError
from .model import AccountKind, D

class ExposureSelectionBasis(str,Enum):
    VALIDATION_FIXTURE_STABLE_ID='VALIDATION_FIXTURE_STABLE_ID'
    EXPLICIT_AUTHORIZED_ID='EXPLICIT_AUTHORIZED_ID'
    EVIDENCE_RULE='EVIDENCE_RULE'

class ExposureAllocationBasis(str,Enum):
    EQUAL_MEMBER_PRO_RATA='EQUAL_MEMBER_PRO_RATA'
    EXPLICIT_AUTHORIZED_SHARE='EXPLICIT_AUTHORIZED_SHARE'
    EVIDENCE_DERIVED_SHARE='EVIDENCE_DERIVED_SHARE'

@dataclass(frozen=True,slots=True)
class ResolutionExposurePlan:
    plan_id: str
    aggregate_id: str
    selected_agent_id: str
    members_exposed: int
    selection_basis: ExposureSelectionBasis
    selection_ref: str
    allocation_basis: ExposureAllocationBasis
    allocation_ref: str
    explicit_share: D|None=None

    def validate_and_fraction(self,aggregate_member_count:int)->D:
        if not self.plan_id or not self.aggregate_id or not self.selected_agent_id:
            raise InvariantError('resolution exposure plan identity missing')
        if not self.selection_ref:
            raise InvariantError('resolution selection basis requires source/authorization reference')
        if not self.allocation_ref:
            raise InvariantError('resolution allocation basis requires source/authorization reference')
        if self.members_exposed<=0 or aggregate_member_count<=0 or self.members_exposed>aggregate_member_count:
            raise InvariantError('invalid represented member exposure count')

        if self.allocation_basis==ExposureAllocationBasis.EQUAL_MEMBER_PRO_RATA:
            if self.explicit_share is not None:
                raise InvariantError('equal-member allocation may not also supply explicit share')
            return D(self.members_exposed)/D(aggregate_member_count)

        if self.explicit_share is None:
            raise InvariantError('explicit/evidence share allocation requires share')
        share=D(self.explicit_share)
        if not D('0')<share<=D('1'):
            raise InvariantError('resolution exposure share out of bounds')
        return share

@dataclass(frozen=True,slots=True)
class ResolutionExposureRecord:
    plan_id: str
    resolution_id: str
    aggregate_id: str
    agent_id: str
    members_exposed: int
    selection_basis: str
    selection_ref: str
    allocation_basis: str
    allocation_ref: str
    allocation_fraction: D

@dataclass(frozen=True,slots=True)
class ResolutionInvariantTotals:
    represented_cash: D
    source_cash: D
    all_non_boundary_cash: D
    represented_members: int
    resource_totals: Tuple[Tuple[str,D],...]
    claim_totals: Tuple[Tuple[str,D],...]
    live_ownership_totals: Tuple[Tuple[str,D],...]
    value_paid_to_representation: D

def resolution_invariant_totals(kernel,aggregate_id,source_account_id)->ResolutionInvariantTotals:
    if aggregate_id not in kernel.aggregates:
        raise InvariantError('aggregate missing for resolution-invariant totals')
    agg=kernel.aggregates[aggregate_id]
    exposed=[r for r in kernel.resolution_exposure_records if r.aggregate_id==aggregate_id]
    agent_ids=[r.agent_id for r in exposed]

    represented_cash=kernel.state.accounts[agg.account_id].balance
    represented_members=agg.member_count
    resources=dict(agg.resource_holdings)
    claims=dict(agg.claim_holdings)

    for r in exposed:
        a=kernel.agents[r.agent_id]
        represented_cash+=kernel.state.accounts[a.account_id].balance
        represented_members+=r.members_exposed
        for key,value in a.resource_holdings.items():
            resources[key]=resources.get(key,D('0'))+D(value)
        for key,value in a.claim_holdings.items():
            claims[key]=claims.get(key,D('0'))+D(value)

    participant_accounts={agg.account_id}|{kernel.agents[x].account_id for x in agent_ids}
    paid=sum((tx.amount for tx in kernel.state.transactions if tx.src_account==source_account_id and tx.dst_account in participant_accounts),D('0'))
    all_cash=sum((a.balance for a in kernel.state.accounts.values() if a.kind!=AccountKind.EARTH_BOUNDARY),D('0'))

    vehicles=sorted({s.vehicle_id for s in kernel.ownership_stakes})
    ownership=tuple((v,sum((s.share for s in kernel.ownership_stakes if s.vehicle_id==v),D('0'))) for v in vehicles)

    return ResolutionInvariantTotals(
        represented_cash,
        kernel.state.accounts[source_account_id].balance,
        all_cash,
        represented_members,
        tuple(sorted((k,D(v)) for k,v in resources.items())),
        tuple(sorted((k,D(v)) for k,v in claims.items())),
        ownership,
        paid)
