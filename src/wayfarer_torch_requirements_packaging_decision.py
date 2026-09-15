"""Governed disposition after source realizability and requirements/mass trades."""
import json

def build_review():
 return {"schema":"LOOM.Wayfarer.TorchRequirementsPackagingDecisionReview","schema_version":"0.1","status":"PASS",
 "authority":{"claim":"E1_TORCH_REQUIREMENTS_AND_SOURCE_PACKAGING_DECISION_REVIEW_ONLY","campaign_state_mutation":"ZERO","llm_calculation_authority":"ZERO","canon_changed":False,"component_architecture_frozen":False},
 "decision":{"disposition":"PRESERVE_CURRENT_VEHICLE_REQUIREMENTS_AND_CARRY_SOURCE_REALIZABILITY_AS_EXPLICIT_TECHNOLOGY_HOLD","reduce_performance_cards":False,"increase_propulsion_mass_allocation":False,"select_source_architecture":False,"reason":"NO_EARNED_PHYSICAL_BOUND_JUSTIFIES_MUTATING_VEHICLE_REQUIREMENTS_OR_MASS_LEDGER_TO_MAKE_A_SOURCE_FIT"},
 "preserved_requirements":{"torch_count":1,"normal_remass_t":250.0,"protected_water_t":50.0,"performance_modes":["ECON","CRUISE","EXPEDITE","FAST","HARD","LIMIT"],"direct_jet_power_W_range":[5112451811250.0,12781129528125.0]},
 "technology_hold":{"source_realizability":"OPEN","preferred_research_direction":"D_HE3_OR_RELATED_LOW_NEUTRON_HIGH_BETA_FRC_CLASS_WITH_SEPARATE_REMASS_AUGMENTATION","preferred_direction_status":"RESEARCH_DIRECTION_ONLY_NOT_SOURCE_SELECTION","required_breakthrough_domains":["SOURCE_SYSTEM_SPECIFIC_POWER","PHYSICAL_ENERGY_PARTITION","FUSION_GAIN_AND_RECIRCULATING_POWER","REMASS_COUPLING","MAGNETIC_NOZZLE_EFFICIENCY_AND_DETACHMENT","RADIATION_THERMAL_AND_LIFETIME"]},
 "packaging":{"status":"NON_GOVERNING_CANDIDATE_CLEARANCE_ENVELOPE_ONLY","candidate_reactor_station_m":[43.0,50.0],"candidate_nozzle_station_m":[50.0,57.0],"candidate_propulsion_allocation_kg":160000.0,"earned_source_mass_budget_kg":None,"rule":"CANDIDATE_TOTAL_PROPULSION_MASS_AND_GEOMETRY_DO_NOT_CERTIFY_SOURCE_FIT"},
 "component_freeze_readiness":"NOT_READY",
 "blocking_holds":["SOURCE_REALIZABILITY","PHYSICAL_DEPOSITION_PARTITION_BOUNDS","WORKING_FLUID_IDENTITY_AND_FEED_PATH","NOZZLE_DETACHMENT_DIVERGENCE_INTERCEPTION","PHYSICAL_PLUME_BY_MODE","SHIELD_MAGNET_THERMAL_STRUCTURE_LIFETIME"],
 "qualified_next_step":"TORCH_WORKING_FLUID_IDENTITY_AND_FEED_PATH_TRADE"}

if __name__=="__main__": print(json.dumps(build_review(),indent=2,sort_keys=True))
