"""KT test-only rendezvous, no runtime integration."""
import math
from decimal import Decimal as D
from simulation.offworld_mvp.build8.three_arm_stage1.vehicle_flyby_cost_test_only import price as flyby_price

def stack(dv,payload,a):
 ve=float(a['hydrolox_exhaust_velocity_km_s']);eps=float(a['dry_mass_fraction_dry_over_dry_plus_propellant'])
 n=max(1,math.floor(dv/(ve*math.log(1/eps)))+1)
 while True:
  ratio=math.exp(dv/(n*ve))
  if eps*ratio<1:break
  n+=1
 factor=ratio*(1-eps)/(1-eps*ratio)
 return n,payload*factor**n

def rendezvous(dep,arr,days,a,auth,moon=False):
 mu=float(a['earth_mu_km3_s2']);r=float(a['earth_mean_radius_km'])+float(a['parking_orbit_altitude_km'])
 dv_dep=math.sqrt(dep*dep+2*mu/r)-math.sqrt(mu/r)
 if moon:
  pmu=float(auth['parent_gm_km3_s2']);pr=float(auth['orbit_radius_km']);dv_arr=math.sqrt(arr*arr+2*pmu/pr)-math.sqrt(pmu/pr)
 else:dv_arr=arr
 nb,brake=stack(dv_arr,float(a['payload_kg']),a);nd,mass=stack(dv_dep,brake,a)
 launch=mass*float(a['launch_cost_usd_per_kg_leo']);operating=float(auth['operating_cost_usd_per_year_of_flight'])*days/365.25
 total=launch+float(auth['rendezvous_fixed_mission_cost_usd'])+operating
 return dict(departure_vinf_km_s=dep,arrival_vinf_km_s=arr,departure_delta_v_km_s=dv_dep,arrival_braking_delta_v_km_s=dv_arr,departure_stages=nd,braking_stages=nb,braking_stack_mass_kg=brake,mass_in_leo_kg=mass,launch_cost_usd=launch,operating_cost_usd=operating,total_usd=total,model_units=str(D(str(total))/D(1000000000)))
