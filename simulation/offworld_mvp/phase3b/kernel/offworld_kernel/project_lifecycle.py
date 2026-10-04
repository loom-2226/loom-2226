from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D
from enum import Enum

class DevelopmentStageOutcome(str, Enum):
    SPENT='SPENT'
    BLOCKED_PROJECT_CASH='BLOCKED_PROJECT_CASH'
    BLOCKED_SUPPLY='BLOCKED_SUPPLY'

class DevelopmentResolutionOutcome(str, Enum):
    OPERATING='OPERATING'
    FAILED='FAILED'

@dataclass(frozen=True)
class ProjectDevelopmentPlan:
    id: str
    project_id: str
    wip_id: str
    asset_id: str
    supplier_account_id: str
    asset_node_id: str
    required_cost: D
    stage_schedule: tuple[tuple[int,D],...]
    completion_year: int
    commissioned_capacity: D
    source_ref: str
    plan_version: str='PROJECT_DEVELOPMENT_PLAN_V1'

    def validate(self):
        if not self.id or not self.project_id or not self.wip_id or not self.asset_id:
            raise ValueError('development plan identity incomplete')
        if not self.supplier_account_id or not self.asset_node_id or not self.source_ref:
            raise ValueError('development plan supplier/location/source incomplete')
        cost=D(self.required_cost)
        capacity=D(self.commissioned_capacity)
        if cost<=0 or capacity<0:
            raise ValueError('development plan cost/capacity invalid')
        if not self.stage_schedule:
            raise ValueError('development plan requires explicit stage schedule')
        years=[]
        total=D('0')
        for year,amount in self.stage_schedule:
            year=int(year); amount=D(amount)
            if year<0 or amount<=0:
                raise ValueError('development stage invalid')
            years.append(year); total+=amount
        if len(set(years))!=len(years):
            raise ValueError('development plan stage years must be unique')
        if tuple(years)!=tuple(sorted(years)):
            raise ValueError('development plan stages must be ordered')
        if total!=cost:
            raise ValueError('development plan stages must reconcile required cost')
        if int(self.completion_year)<max(years):
            raise ValueError('development completion precedes construction stage')
        return self

@dataclass(frozen=True)
class DevelopmentStageRecord:
    plan_id: str
    project_id: str
    year: int
    planned_amount: D
    outcome: DevelopmentStageOutcome
    reason: str
    transaction_id: str=''
    event_id: str=''
    record_version: str='DEVELOPMENT_STAGE_RECORD_V1'

@dataclass(frozen=True)
class DevelopmentResolutionRecord:
    plan_id: str
    project_id: str
    year: int
    outcome: DevelopmentResolutionOutcome
    required_cost: D
    accumulated_cost: D
    commissioned: D
    written_off: D
    asset_id: str=''
    reason: str=''
    event_id: str=''
    record_version: str='DEVELOPMENT_RESOLUTION_RECORD_V1'
