from pathlib import Path
from .solar_object_location_bridge_v0_3 import build_solar_candidate_locations
FORMAT='CIVPROP_PLACEHOLDER_TRANSPORT_OPPORTUNITY_SURFACE_V0_3'; VALUE=1.0; UNIT='dimensionless_test_index'
def build_placeholder_surface(nav_path:Path,start_year=2026,end_year=2226):
 loc=build_solar_candidate_locations(nav_path); seen=set(); rows=[]
 for x in loc['locations']:
  b=x['body_id']
  if x['placement']!='ORBITAL' or x['candidate_status']!='NAV1_CANDIDATE' or b in {'EARTH','MOON'} or b in seen: continue
  seen.add(b); rows.append({'origin_body_id':'EARTH','destination_body_id':b,'valid_from_year':start_year,'valid_to_year':end_year,'transport_opportunity':VALUE,'unit':UNIT,'status':'EXPLICIT_PLACEHOLDER','provenance_refs':['SOLAR_OBJECT_LOCATION_BRIDGE_V0_3','GAP-016_TRANSPORT_OPPORTUNITY_SURFACE']})
 return {'format':FORMAT,'version':'0.3.0','classification':'NON_CANON_PROPAGATION_TEST_PLACEHOLDER','gap':'GAP-016','start_year':start_year,'end_year':end_year,'placeholder_transport_opportunity':VALUE,'unit':UNIT,'semantics':{'independent_of_spice':True,'independent_of_distance':True,'independent_of_propulsion':True,'independent_of_actor_capability':True,'not_physical_accessibility':True,'not_cost':True,'not_travel_time':True,'not_prediction':True,'must_be_replaced_for_production':True},'rows':rows}
