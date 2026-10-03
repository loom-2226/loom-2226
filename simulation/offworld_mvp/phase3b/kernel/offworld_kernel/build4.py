from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from .build3 import Build3Kernel, RunIdentity
from .kernel import InvariantError
from .model import *

@dataclass
class OwnershipStake:
    vehicle_id: str
    owner_id: str
    owner_domicile: str
    share: D

@dataclass
class ConstructionWIP:
    id: str
    project_id: str
    node_id: str
    accumulated_cost: D = D('0')
    commissioned: D = D('0')

@dataclass
class SupplyCapacity:
    node_id: str
    year: int
    capacity: D
    used: D = D('0')
    @property
    def available(self): return self.capacity-self.used

@dataclass
class CarryReservation:
    id: str
    node_id: str
    project_id: str
    amount: D
    reserved_year: int
    expiry_year: int
    spent: D = D('0')
    lapsed: D = D('0')
    @property
    def outstanding(self): return self.amount-self.spent-self.lapsed

class Build4Kernel(Build3Kernel):
    def __init__(self, run_identity: RunIdentity, *args, **kwargs):
        super().__init__(run_identity, *args, **kwargs)
        self.ownership_stakes = []
        self.wip = {}
        self.supply = {}
        self.carry_reservations = {}
        self.boundary_net = {}
        self.asset_depreciation = {}
        self.knowledge_amortization = {}
        self.event_log = []

    def audit(self, kind, year, **data):
        cooked = {k: str(v) if isinstance(v,D) else v for k,v in data.items()}
        self.event_log.append({'seq':len(self.event_log)+1,'kind':kind,'year':year,**cooked})
