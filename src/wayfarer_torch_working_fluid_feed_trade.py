"""Requirements-first trade for Wayfarer torch remass working fluid and feed path."""
import json, math

def build_trade():
 return {"schema":"LOOM.Wayfarer.TorchWorkingFluidFeedTrade","schema_version":"0.1","status":"PASS",
 "authority":{"claim":"E1_TORCH_WORKING_FLUID_AND_FEED_PATH_TRADE_ONLY","campaign_state_mutation":"ZERO","llm_calculation_authority":"ZERO","canon_changed":False,"working_fluid_selected":False,"feed_architecture_selected":False},
 "candidate_inputs":{"working_fluid":None,"storage_state":None,"feed_architecture":None,"fluid_density_kg_m3":None,"feed_pressure_MPa":None,"usable_tank_fraction":None},
 "requirements":{"normal_remass_t":250.0,"protected_water_t":50.0,"mass_flow_kg_s_range":[1.1361004025,284.025100625],"effective_exhaust_velocity_km_s_range":[300.0,3000.0]},
 "separation_rule":"NORMAL_REMASS_WORKING_FLUID_IDENTITY_IS_NOT_SILENTLY_EQUATED_TO_PROTECTED_WATER_RESERVE",
 "trade_families":[{"family":"LIGHT_CRYOGENIC_FLUID","examples":"HYDROGEN_OR_HELIUM_CLASS","status":"OPEN","primary_holds":["TANK_VOLUME","CRYOGENIC_STORAGE","PERMEATION","FEED_RATE","PLASMA_COUPLING"]},{"family":"WATER_OR_STEAM_DERIVED","examples":"WATER_CLASS","status":"OPEN","primary_holds":["HEATING_DISSOCIATION_IONIZATION","NOZZLE_COUPLING","CORROSION_MATERIAL_COMPATIBILITY","RESERVE_FIREWALL"]},{"family":"INERT_OR_NOBLE_GAS","examples":"HELIUM_NEON_ARGON_CLASS","status":"OPEN","primary_holds":["STORAGE_MASS_VOLUME","IONIZATION_ENERGY","AVAILABILITY","NOZZLE_COUPLING"]},{"family":"METALLIC_OR_HIGH_Z_FLUID","examples":"LITHIUM_OR_OTHER_METAL_CLASS","status":"HIGH_RISK","primary_holds":["RADIATION","EROSION_DEPOSITION","MATERIAL_COMPATIBILITY","RECOVERY_CONTAMINATION"]}],
 "feed_requirements":["SPAN_1P136_TO_284P025_KG_S_WITH_CONTROL_AUTHORITY","ISOLATE_STORAGE_FROM_FUSION_SOURCE_AND_NOZZLE_TRANSIENTS","CLOSE_PRESSURE_DROP_CAVITATION_OR_TWO_PHASE_BEHAVIOR","CLOSE_VALVE_RESPONSE_AND_LIFETIME","CLOSE_THERMAL_CONDITIONING_AND_IONIZATION_PATH","CLOSE_TANKAGE_VOLUME_MASS_AND_CENTER_OF_MASS_SHIFT"],
 "kill_criteria":["CANNOT_DELIVER_LIMIT_FLOW_WITH_EARNED_TANKAGE_AND_FEED_MASS","UNBOUNDED_STORAGE_OR_CONDITIONING_POWER","PLASMA_OR_NOZZLE_COUPLING_FAILS","MATERIAL_EROSION_DEPOSITION_OR_ACTIVATION_UNACCEPTABLE","PROTECTED_WATER_RESERVE_MUST_BE_CONSUMED_TO_CLOSE_NORMAL_REMASS"],
 "qualified_next_step":"TORCH_WORKING_FLUID_RESEARCH_AND_MATERIAL_COMPATIBILITY_BOUND"}

def evaluate_candidate(name,density_kg_m3,feed_pressure_MPa,usable_tank_fraction):
 if not name: raise ValueError("working fluid identity must be explicit")
 vals=[density_kg_m3,feed_pressure_MPa,usable_tank_fraction]
 if any(v is None or not math.isfinite(v) or v<=0 for v in vals): raise ValueError("candidate properties must be explicit and positive")
 if usable_tank_fraction>1: raise ValueError("usable tank fraction must be <=1")
 volume=250000.0/density_kg_m3/usable_tank_fraction
 return {"working_fluid":name,"required_usable_volume_m3":volume,"feed_pressure_MPa":feed_pressure_MPa,"status":"SENSITIVITY_ONLY_EXPLICIT_INPUTS","certified":False}

if __name__=="__main__": print(json.dumps(build_trade(),indent=2,sort_keys=True))
