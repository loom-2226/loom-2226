"""Couple explicit energy partition to source-mass feasibility for Wayfarer E1."""
import json, math
JET={"ECON":5112451811250.0,"CRUISE":11361004025000.0,"EXPEDITE":11361004025000.0,"FAST":11929054226250.0,"HARD":12781129528125.0,"LIMIT":12781129528125.0}

def build_envelope():
 return {"schema":"LOOM.Wayfarer.TorchEnergyPartitionMassFeasibilityEnvelope","schema_version":"0.1","status":"PASS",
 "authority":{"claim":"E1_TORCH_ENERGY_PARTITION_AND_SOURCE_MASS_FEASIBILITY_ONLY","campaign_state_mutation":"ZERO","llm_calculation_authority":"ZERO","canon_changed":False,"partition_certified":False,"source_mass_certified":False,"component_architecture_frozen":False},
 "candidate_inputs":{"directed_fraction":None,"deposition_fraction":None,"escaping_neutral_fraction":None,"other_loss_fraction":None,"source_specific_power_W_kg":None},
 "candidate_propulsion_allocation_t":160.0,"allocation_firewall":"160_T_IS_A_CANDIDATE_TOTAL_PROPULSION_ALLOCATION_NOT_A_CERTIFIED_FUSION_SOURCE_MASS_BUDGET",
 "external_research_context":{"status":"EXTERNAL_RESEARCH_SYNTHESIS_NOT_WAYFARER_PARAMETER","present_DFD_specific_power_kW_kg_range":[0.3,1.5],"ambitious_study_specific_power_kW_kg_range":[25.0,100.0],"interpretation":"USE_AS_SCALE_DIAGNOSTIC_ONLY"},
 "required_partition_channels":["directed_exhaust","vehicle_deposition","escaping_neutral_radiation","other_accounted_loss"],
 "derived_requirements":["ENERGY_PARTITION_MUST_CLOSE_TO_UNITY","SOURCE_MASS_FEASIBILITY_MUST_USE_PHYSICALLY_BOUNDED_SOURCE_SPECIFIC_POWER","VEHICLE_DEPOSITION_POWER_MUST_FEED_THERMAL_AND_SHIELDING_CLOSURE","TOTAL_PROPULSION_ALLOCATION_CANNOT_BE_SILENTLY_ASSIGNED_TO_FUSION_SOURCE"],
 "kill_criteria":["NO_PHYSICAL_PARTITION_CLOSES","SOURCE_MASS_EXCEEDS_EARNED_PROPULSION_MASS_BUDGET","DEPOSITION_BREAKS_THERMAL_OR_SHIELDING_LIMITS","ESCAPING_RADIATION_BREAKS_CREW_OR_HARDWARE_LIMITS","REQUIRED_SPECIFIC_POWER_HAS_NO_DEFENSIBLE_2226_DEVELOPMENT_PATH"],
 "qualified_next_step":"TORCH_SOURCE_ARCHITECTURE_BREAKTHROUGH_REQUIREMENTS_AND_ALTERNATIVES_TRADE"}

def evaluate_candidate(mode,directed_fraction,deposition_fraction,escaping_neutral_fraction,other_loss_fraction,source_specific_power_W_kg):
 if mode not in JET: raise ValueError("unknown mode")
 vals=[directed_fraction,deposition_fraction,escaping_neutral_fraction,other_loss_fraction]
 if any((not math.isfinite(x) or x<0 or x>1) for x in vals) or directed_fraction<=0: raise ValueError("fractions must be physical and directed fraction positive")
 s=sum(vals)
 if abs(s-1.0)>1e-9: raise ValueError("partition must close to unity")
 if not math.isfinite(source_specific_power_W_kg) or source_specific_power_W_kg<=0: raise ValueError("specific power must be positive")
 p=JET[mode]/directed_fraction
 return {"mode":mode,"partition_sum":s,"required_source_power_W":p,"source_mass_kg":p/source_specific_power_W_kg,"vehicle_deposition_W":p*deposition_fraction,"escaping_neutral_radiation_W":p*escaping_neutral_fraction,"other_accounted_loss_W":p*other_loss_fraction,"certified":False,"status":"SENSITIVITY_ONLY_EXPLICIT_INPUTS"}

if __name__=="__main__": print(json.dumps(build_envelope(),indent=2,sort_keys=True))
