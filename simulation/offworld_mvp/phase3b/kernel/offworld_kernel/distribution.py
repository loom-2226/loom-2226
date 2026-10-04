from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D
from hashlib import sha256
import json


@dataclass(frozen=True)
class FinancingReturnClaim:
    id: str
    financier_id: str
    project_id: str
    destination_account_id: str
    maximum_return_amount: D
    source_commitment_ids: tuple[str,...]
    source_ref: str
    epistemic_status: str
    claim_version: str='FINANCING_RETURN_CLAIM_V1'

    def validate(self):
        if not self.id or not self.financier_id or not self.project_id or not self.destination_account_id:
            raise ValueError('financing return claim identity incomplete')
        if D(self.maximum_return_amount)<0:
            raise ValueError('negative financing return claim')
        if not self.source_commitment_ids or len(set(self.source_commitment_ids))!=len(self.source_commitment_ids):
            raise ValueError('financing return claim commitment lineage invalid')
        if not self.source_ref or not self.epistemic_status:
            raise ValueError('financing return claim provenance/standing missing')
        return self

    def fingerprint(self):
        payload={
            'id':self.id,'financier_id':self.financier_id,'project_id':self.project_id,
            'destination_account_id':self.destination_account_id,
            'maximum_return_amount':str(self.maximum_return_amount),
            'source_commitment_ids':self.source_commitment_ids,
            'source_ref':self.source_ref,'epistemic_status':self.epistemic_status,
            'claim_version':self.claim_version,
        }
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class OwnerDistributionAllocation:
    owner_id: str
    destination_account_id: str
    ownership_share: D
    amount: D
    transaction_id: str


@dataclass(frozen=True)
class SurplusDistributionRecord:
    year: int
    project_id: str
    actor_id: str
    decision_id: str
    financing_return_claim_id: str
    opening_project_cash: D
    reserve: D
    financier_return: D
    local_reinvestment: D
    local_reinvestment_account_id: str
    owner_distribution: D
    owner_allocations: tuple[OwnerDistributionAllocation,...]
    closing_project_cash: D
    transaction_ids: tuple[str,...]
    event_id: str
    record_version: str='SURPLUS_DISTRIBUTION_RECORD_V1'

    def validate(self):
        values=tuple(D(v) for v in (
            self.opening_project_cash,self.reserve,self.financier_return,
            self.local_reinvestment,self.owner_distribution,self.closing_project_cash))
        if min(values)<0:
            raise ValueError('negative surplus distribution state')
        if D(self.opening_project_cash)!=(D(self.reserve)+D(self.financier_return)+
                                          D(self.local_reinvestment)+D(self.owner_distribution)):
            raise ValueError('surplus distribution decomposition mismatch')
        if D(self.closing_project_cash)!=D(self.reserve):
            raise ValueError('surplus distribution closing reserve mismatch')
        owner_total=sum((D(a.amount) for a in self.owner_allocations),D('0'))
        if owner_total!=D(self.owner_distribution):
            raise ValueError('owner allocation total mismatch')
        return self
