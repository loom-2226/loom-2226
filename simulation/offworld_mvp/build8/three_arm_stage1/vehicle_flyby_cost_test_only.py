"""KT-authored flyby vehicle cost, non-canon; no changes to existing runtime."""
import math
from decimal import Decimal as D

def price(vinf, a):
 v=float(vinf);mu=float(a['earth_mu_km3_s2']);r=float(a['earth_mean_radius_km'])+float(a['parking_orbit_altitude_km']);ve=float(a['hydrolox_exhaust_velocity_km_s']);eps=float(a['dry_mass_fraction_dry_over_dry_plus_propellant']);payload=float(a['payload_kg'])
 dv=math.sqrt(v*v+2*mu/r)-math.sqrt(mu/r)
 # For n serial identical stages with optimal equal stage delta-v, the
 # payload multiplier per stage is R*(1-eps)/(1-eps*R).
 # n must make each individual stage physically feasible.
 n=max(1,math.floor(dv/(ve*math.log(1/eps)))+1)
 while True:
  R=math.exp(dv/(n*ve))
  if eps*R<1:break
  n+=1
 factor=R*(1-eps)/(1-eps*R)
 mass=payload*factor**n
 launch=mass*float(a['launch_cost_usd_per_kg_leo'])
 total=launch+float(a['fixed_mission_cost_usd'])
 return {'departure_vinf_km_s':v,'leo_injection_delta_v_km_s':dv,'stages':n,'mass_in_leo_kg':mass,'launch_cost_usd':launch,'fixed_mission_cost_usd':float(a['fixed_mission_cost_usd']),'total_usd':total,'model_units':str(D(str(total))/D(1000000000))}

def hand_tests(a):
 return [{'vinf_km_s':v,'expected_stage_count':n,'expected_mass_kg_approx':m,'actual':price(v,a),'stage_count_matches':price(v,a)['stages']==n,'mass_ratio_actual_to_expected':price(v,a)['mass_in_leo_kg']/m} for v,n,m in [(10,1,3600),(20,2,50000),(30,3,1360000)]]
