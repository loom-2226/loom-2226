"""CIVPROP Asset Lifecycle V1.

Deterministic lifecycle projection for commissioned facilities. Lifecycle facts are
explicit inputs: the contract never invents service lives, depreciation rates,
maintenance schedules, failures, retirements, abandonments, or replacement spend.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Sequence

ACTIVE='ACTIVE'; UNKNOWN='UNKNOWN'; FAILED='FAILED'; RETIRED='RETIRED'; ABANDONED='ABANDONED'

@dataclass(frozen=True)
class LifecyclePolicyV1:
    project_archetype_id: str
    annual_depreciation_rate: Optional[float] = None
    maintenance_interval_years: Optional[int] = None
    maintenance_cost_fraction: Optional[float] = None
    service_life_years: Optional[int] = None

    def __post_init__(self):
        if self.annual_depreciation_rate is not None and not 0 <= self.annual_depreciation_rate <= 1:
            raise ValueError('annual_depreciation_rate must be in [0,1]')
        if self.maintenance_interval_years is not None and self.maintenance_interval_years <= 0:
            raise ValueError('maintenance_interval_years must be positive')
        if self.maintenance_cost_fraction is not None and self.maintenance_cost_fraction < 0:
            raise ValueError('maintenance_cost_fraction must be nonnegative')
        if self.service_life_years is not None and self.service_life_years <= 0:
            raise ValueError('service_life_years must be positive')

@dataclass(frozen=True)
class LifecycleEventV1:
    year: int
    facility_id: str
    event_type: str
    replacement_capital: Optional[float] = None

    def __post_init__(self):
        if self.event_type not in {'FAILURE','RETIREMENT','ABANDONMENT','RESTORE','REPLACEMENT'}:
            raise ValueError('unsupported lifecycle event')
        if self.replacement_capital is not None and self.replacement_capital < 0:
            raise ValueError('replacement_capital must be nonnegative')
        if self.event_type != 'REPLACEMENT' and self.replacement_capital is not None:
            raise ValueError('replacement_capital is only valid for REPLACEMENT')

@dataclass(frozen=True)
class AssetLifecycleStateV1:
    year: int; facility_id: str; age_years: int; status: str
    usable_capacity_fraction: Optional[float]
    opening_gross_productive_capital: float
    depreciation: Optional[float]
    maintenance_required: Optional[bool]
    maintenance_requirement: Optional[float]
    replacement_investment: float
    growth_investment: float
    closing_gross_productive_capital: float
    event_types: tuple[str,...]

class AssetLifecycleRuntimeV1:
    def __init__(self, policies: Sequence[LifecyclePolicyV1], events: Sequence[LifecycleEventV1]=()):
        self.policies={p.project_archetype_id:p for p in policies}
        if len(self.policies)!=len(tuple(policies)): raise ValueError('duplicate lifecycle policy')
        self.events=tuple(events)

    def project(self, facilities, start_year:int, end_year:int):
        out=[]
        for f in sorted(facilities,key=lambda x:x.facility_id):
            p=self.policies.get(f.project_archetype_id)
            status=ACTIVE; capital=float(f.capital)
            for year in range(max(start_year,f.commissioned_year),end_year+1):
                age=year-f.commissioned_year
                ev=[e for e in self.events if e.facility_id==f.facility_id and e.year==year]
                types=[e.event_type for e in ev]
                # Explicit service life is a deterministic retirement authority.
                if p and p.service_life_years is not None and age >= p.service_life_years and status==ACTIVE:
                    types.append('RETIREMENT')
                for t in types:
                    if t=='FAILURE': status=FAILED
                    elif t=='RETIREMENT': status=RETIRED
                    elif t=='ABANDONMENT': status=ABANDONED
                    elif t in {'RESTORE','REPLACEMENT'}: status=ACTIVE
                replacement=sum((e.replacement_capital or 0.0) for e in ev if e.event_type=='REPLACEMENT')
                opening=capital
                depreciation=None
                if p and p.annual_depreciation_rate is not None:
                    depreciation=opening*p.annual_depreciation_rate if status==ACTIVE else 0.0
                maintenance_required=None; maintenance_requirement=None
                if p and p.maintenance_interval_years is not None:
                    maintenance_required=age>0 and age%p.maintenance_interval_years==0 and status==ACTIVE
                    if p.maintenance_cost_fraction is not None:
                        maintenance_requirement=(opening*p.maintenance_cost_fraction if maintenance_required else 0.0)
                capital=max(0.0,opening-(depreciation or 0.0)+replacement)
                availability = (1.0 if status==ACTIVE else (None if status==UNKNOWN else 0.0))
                if p is None and age > 0 and not types and status in {ACTIVE, UNKNOWN}:
                    status=UNKNOWN; availability=None
                out.append(AssetLifecycleStateV1(
                    year,f.facility_id,age,status,availability,
                    opening,depreciation,maintenance_required,maintenance_requirement,
                    replacement,0.0,capital,tuple(types)))
        return tuple(out)

def to_dicts(states): return [asdict(x) for x in states]

def load_asset_lifecycle_data(raw):
    raw=dict(raw)
    if raw.get('format')!='CIVPROP_ASSET_LIFECYCLE_V1': raise ValueError('invalid asset lifecycle format')
    if raw.get('contract_version')!='1.0.0': raise ValueError('unsupported asset lifecycle contract version')
    policies=tuple(LifecyclePolicyV1(**x) for x in raw.get('policies',[]))
    events=tuple(LifecycleEventV1(**x) for x in raw.get('events',[]))
    # Construction triggers dataclass validation and fail-closed parameter checks.
    AssetLifecycleRuntimeV1(policies, events)
    return policies, events, raw

def load_asset_lifecycle_package(path):
    import json
    from pathlib import Path
    return load_asset_lifecycle_data(json.loads(Path(path).read_text()))

@dataclass(frozen=True)
class LifecycleProductionProjectionV1:
    year: int
    facility_id: str
    lifecycle_status: str
    usable_capacity_fraction: Optional[float]
    pre_lifecycle_output_status: str
    pre_lifecycle_output_quantity: Optional[float]
    post_lifecycle_output_status: str
    post_lifecycle_output_quantity: Optional[float]
    basis: str = 'LIFECYCLE_CAPACITY_GATE_POST_ENGINE'

def project_production_through_lifecycle(production_states, lifecycle_states):
    lifecycle={(x.year,x.facility_id):x for x in lifecycle_states}
    rows=[]
    for p in production_states:
        l=lifecycle.get((int(p.year),str(p.facility_id)))
        if l is None:
            continue
        if l.usable_capacity_fraction is None:
            status='UNKNOWN'; quantity=None
        elif l.usable_capacity_fraction == 0:
            status='KNOWN'; quantity=0.0
        elif p.physical_output_quantity is None:
            status=p.physical_output_status; quantity=None
        else:
            status=p.physical_output_status
            quantity=float(p.physical_output_quantity)*l.usable_capacity_fraction
        rows.append(LifecycleProductionProjectionV1(
            int(p.year),str(p.facility_id),l.status,l.usable_capacity_fraction,
            p.physical_output_status,p.physical_output_quantity,status,quantity))
    return tuple(rows)
