"""GAP-014 technology-sensitive demography bridge.
NON_CANON / MACHINERY TEST. Technology timeline rows are consideration anchors,
not demographic effects. Effects require explicit actor/site access and a
separately authorized demographic modifier.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class DemographicTechnologyExposureV1:
 person_or_cohort_id:str
 location_id:str
 technology_id:str
 year:int
 technology_exists:bool
 actor_access:bool
 intervention_received:bool
 provenance_refs:tuple[str,...]

@dataclass(frozen=True)
class DemographicModifierV1:
 technology_id:str
 effect_kind:str
 multiplier:float|None
 provenance_refs:tuple[str,...]
 authority_class:str="AUTHORED_DEMOGRAPHIC_TECH_EFFECT"

_ALLOWED=frozenset({"MORTALITY","FERTILITY","MORBIDITY","REPRODUCTIVE_VIABILITY",
                    "HEALTHY_LIFESPAN","BIOLOGICAL_VIABILITY"})

def exposure_gate(exposure):
 if not exposure.provenance_refs: raise ValueError("MISSING_EXPOSURE_PROVENANCE")
 if not exposure.technology_exists: return "TECHNOLOGY_NOT_ACHIEVED"
 if not exposure.actor_access: return "NO_ACTOR_ACCESS"
 if not exposure.intervention_received: return "INTERVENTION_NOT_RECEIVED"
 return "EXPOSED"

def apply_demographic_modifier(*,baseline_rate,exposure,modifier):
 if modifier.effect_kind not in _ALLOWED: raise ValueError("UNSUPPORTED_DEMOGRAPHIC_EFFECT")
 if modifier.technology_id!=exposure.technology_id: raise ValueError("TECHNOLOGY_EFFECT_MISMATCH")
 if exposure_gate(exposure)!="EXPOSED": return baseline_rate
 if modifier.multiplier is None: return None
 if not modifier.provenance_refs: raise ValueError("MISSING_EFFECT_PROVENANCE")
 if modifier.multiplier<0: raise ValueError("NEGATIVE_EFFECT_MULTIPLIER")
 if baseline_rate is None: return None
 return baseline_rate*modifier.multiplier

def timeline_row_is_demographic_effect(row):
 # Hard firewall: a frontier/threshold row by itself never changes demography.
 return False
