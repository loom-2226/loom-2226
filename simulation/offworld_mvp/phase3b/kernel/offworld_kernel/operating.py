from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D

@dataclass(frozen=True)
class OperatingCostRecord:
    year: int
    actor_id: str
    decision_id: str
    project_id: str
    asset_id: str
    supplier_account_id: str
    planned_quantity: D
    unit_opex: D
    total_opex: D
    transaction_id: str
    event_id: str
    record_version: str='OPERATING_COST_RECORD_V1'

@dataclass(frozen=True)
class ExtractionResolutionRecord:
    year: int
    actor_id: str
    decision_id: str
    project_id: str
    asset_id: str
    resource_id: str
    planned_quantity: D
    actual_extracted: D
    resource_before: D
    resource_after: D
    inventory_before: D
    inventory_after: D
    extraction_event_id: str
    record_version: str='EXTRACTION_RESOLUTION_RECORD_V1'
