"""Research-bounded selection envelope; does not select Wayfarer remass."""
import json

def build_envelope():
 return {"schema":"LOOM.Wayfarer.TorchWorkingFluidSelectionEnvelope","schema_version":"0.1","status":"PASS","authority_claim":"E1_TORCH_WORKING_FLUID_RESEARCH_BOUNDED_SELECTION_ENVELOPE_ONLY","campaign_state_mutation":"ZERO","llm_calculation_authority":"ZERO","canon_changed":False,"certified":False,
 "normal_remass_t":250.0,"protected_water_reserve_t":50.0,"normal_remass_may_assume_protected_water":False,
 "required_mass_flow_kg_s_range":[1.1361004025,284.025100625],"required_effective_exhaust_velocity_km_s_range":[300.0,3000.0],
 "leading_research_family":"LIGHT_HYDROGENIC_OR_HELIUM_CLASS","leading_family_status":"TOPOLOGY_ANALOG_ONLY_NOT_SELECTION","selected_working_fluid":None,
 "research_bounded_order":["LIGHT_HYDROGENIC_OR_HELIUM_CLASS","INERT_LIGHT_GAS_CLASS","WATER_DERIVED","METALLIC_OR_HIGH_Z"],
 "scale_gap":"PUBLISHED_AUGMENTED_DFD_ANALOGS_DO_NOT_VALIDATE_WAYFARER_300_TO_3000_KM_S_ENVELOPE",
 "selection_gates":["STORAGE_STATE_DENSITY_TANKAGE_MASS_VOLUME","PEAK_284_KG_S_FEED_DELIVERY_AND_CONTROL","CONDITIONING_IONIZATION_ENERGY","FUSION_PRODUCT_TO_REMASS_TRANSFER_EFFICIENCY_BY_MODE","MAGNETIC_NOZZLE_DETACHMENT_DIVERGENCE_INTERCEPTION_BY_SPECIES","EROSION_DEPOSITION_PERMEATION_EMBRITTLEMENT_CORROSION_ACTIVATION","CENTER_OF_MASS_MIGRATION","FAULT_ISOLATION_AND_RESERVE_FIREWALL"],
 "qualified_next_step":"TORCH_LIGHT_REMASS_STORAGE_FEED_AND_NOZZLE_COUPLING_ENVELOPE"}

if __name__=="__main__": print(json.dumps(build_envelope(),indent=2,sort_keys=True))
