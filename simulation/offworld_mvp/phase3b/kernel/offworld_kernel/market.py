from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D
from hashlib import sha256
import json


@dataclass(frozen=True)
class CommodityMarketEnvelope:
    id: str
    year: int
    resource_id: str
    buyer_account_id: str
    unit_price: D
    demand_quantity: D
    currency_unit: str
    quantity_unit: str
    source_ref: str
    epistemic_status: str
    envelope_version: str='COMMODITY_MARKET_ENVELOPE_V1'

    def validate(self):
        if not self.id or not self.resource_id or not self.buyer_account_id:
            raise ValueError('market envelope identity incomplete')
        if int(self.year)<0:
            raise ValueError('market envelope year invalid')
        if D(self.unit_price)<0 or D(self.demand_quantity)<0:
            raise ValueError('market envelope price/demand cannot be negative')
        if not self.currency_unit or not self.quantity_unit:
            raise ValueError('market envelope unit contract missing')
        if not self.source_ref or not self.epistemic_status:
            raise ValueError('market envelope provenance/standing missing')
        return self

    def fingerprint(self):
        payload={
            'id':self.id,'year':int(self.year),'resource_id':self.resource_id,
            'buyer_account_id':self.buyer_account_id,'unit_price':str(self.unit_price),
            'demand_quantity':str(self.demand_quantity),'currency_unit':self.currency_unit,
            'quantity_unit':self.quantity_unit,'source_ref':self.source_ref,
            'epistemic_status':self.epistemic_status,'envelope_version':self.envelope_version,
        }
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class MarketClearingRecord:
    year: int
    market_state_id: str
    actor_id: str
    decision_id: str
    project_id: str
    resource_id: str
    offered_quantity: D
    demand_before: D
    cleared_quantity: D
    demand_after: D
    unit_price: D
    transaction_value: D
    local_inventory_before: D
    local_inventory_after: D
    market_inventory_before: D
    market_inventory_after: D
    transaction_id: str
    event_id: str
    record_version: str='MARKET_CLEARING_RECORD_V1'
