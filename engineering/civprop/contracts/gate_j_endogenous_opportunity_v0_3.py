from dataclasses import dataclass
@dataclass(frozen=True)
class EndogenousOpportunity:
 opportunity_id:str; year:int; status:str; reason_codes:tuple[str,...]; required_capacity:float; observed_capacity:float|None; provenance_refs:tuple[str,...]
def detect_capacity_opportunity(*,states,year,required_capacity):
 if required_capacity<=0: raise ValueError("required_capacity must be positive")
 rows=[x for x in states if x.year==year]
 if len(rows)!=1: return EndogenousOpportunity(f"OPP-{year}",year,"BLOCKED",("CAPACITY_STATE_NOT_UNIQUE",),required_capacity,None,("GATE_J_DERIVED",))
 x=rows[0]
 if x.usable_capacity is None: return EndogenousOpportunity(f"OPP-{year}",year,"BLOCKED",("CAPACITY_UNKNOWN",),required_capacity,None,x.provenance_refs)
 if x.usable_capacity<required_capacity: return EndogenousOpportunity(f"OPP-{year}",year,"BLOCKED",("INSUFFICIENT_PHYSICAL_CAPACITY",),required_capacity,x.usable_capacity,x.provenance_refs)
 return EndogenousOpportunity(f"OPP-{year}",year,"ELIGIBLE",(),required_capacity,x.usable_capacity,x.provenance_refs+("STATE_DELTA_DERIVATION",))
