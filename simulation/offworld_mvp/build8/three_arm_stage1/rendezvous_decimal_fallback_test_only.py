"""Unmodified float stage mass first; Decimal(60) only after OverflowError."""
import math
from decimal import Decimal as D,localcontext
from simulation.offworld_mvp.build8.three_arm_stage1 import rendezvous_cost_test_only as old

COUNTS={'float_samples':0,'decimal_samples':0,'float_stage_calls':0,'decimal_stage_calls':0,'first_failure':None,'lowest_failure':None}

def stack(dv,payload,a):
 COUNTS['float_stage_calls']+=1
 try:
  if isinstance(payload,D):raise OverflowError('upstream Decimal mass requires Decimal continuation')
  return old.stack(dv,payload,a),'FLOAT'
 except OverflowError:
  COUNTS['decimal_stage_calls']+=1
  with localcontext() as ctx:
   ctx.prec=60
   v=D(str(dv));p=D(str(payload));ve=D(str(a['hydrolox_exhaust_velocity_km_s']));eps=D(str(a['dry_mass_fraction_dry_over_dry_plus_propellant']))
   n=max(1,int((v/(ve*(D(1)/eps).ln())).to_integral_value(rounding='ROUND_FLOOR'))+1)
   while True:
    R=(v/(D(n)*ve)).exp()
    if eps*R<D(1):break
    n+=1
   factor=R*(D(1)-eps)/(D(1)-eps*R)
   return (n,p*factor**n),'DECIMAL60'

def rendezvous(dep,arr,days,a,auth,moon=False,body='',year=None):
 mu=float(a['earth_mu_km3_s2']);r=float(a['earth_mean_radius_km'])+float(a['parking_orbit_altitude_km'])
 dv_dep=math.sqrt(dep*dep+2*mu/r)-math.sqrt(mu/r)
 if moon:
  pmu=float(auth['parent_gm_km3_s2']);pr=float(auth['orbit_radius_km']);dv_arr=math.sqrt(arr*arr+2*pmu/pr)-math.sqrt(pmu/pr)
 else:dv_arr=arr
 (nb,brake),path1=stack(dv_arr,float(a['payload_kg']),a)
 (nd,mass),path2=stack(dv_dep,brake,a)
 decimal=path1=='DECIMAL60' or path2=='DECIMAL60'
 if decimal:
  with localcontext() as ctx:
   ctx.prec=60
   mass=D(str(mass)) if not isinstance(mass,D) else mass
   launch=mass*D(str(a['launch_cost_usd_per_kg_leo']))
   operating=D(str(auth['operating_cost_usd_per_year_of_flight']))*D(str(days))/D('365.25')
   total=launch+D(str(auth['rendezvous_fixed_mission_cost_usd']))+operating
  COUNTS['decimal_samples']+=1
  failure={'body':body,'year':year,'departure_vinf_km_s':dep,'arrival_vinf_km_s':arr,'flight_days':days}
  if COUNTS['first_failure'] is None:COUNTS['first_failure']=failure
  if COUNTS['lowest_failure'] is None or max(dep,arr)<max(COUNTS['lowest_failure']['departure_vinf_km_s'],COUNTS['lowest_failure']['arrival_vinf_km_s']):COUNTS['lowest_failure']=failure
 else:
  launch=mass*float(a['launch_cost_usd_per_kg_leo']);operating=float(auth['operating_cost_usd_per_year_of_flight'])*days/365.25
  total=launch+float(auth['rendezvous_fixed_mission_cost_usd'])+operating
  COUNTS['float_samples']+=1
 # FLOAT path retains every arithmetic operation and the result types of old.rendezvous.
 return dict(departure_vinf_km_s=dep,arrival_vinf_km_s=arr,departure_delta_v_km_s=dv_dep,arrival_braking_delta_v_km_s=dv_arr,departure_stages=nd,braking_stages=nb,braking_stack_mass_kg=brake,mass_in_leo_kg=mass,launch_cost_usd=launch,operating_cost_usd=operating,total_usd=total,model_units=str(D(str(total))/D(1000000000)),calculation_path='DECIMAL60' if decimal else 'FLOAT')

def test(a,auth):
 import struct
 # bit identity on all tested in-range results, including two stage cases.
 bit_checks=[]
 for dep,arr,days in [(10.,3.,365.25),(20.,5.,365.25),(30.,3.,900.),(6.,1.,45.)]:
  oldp=old.rendezvous(dep,arr,days,a,auth);new=rendezvous(dep,arr,days,a,auth)
  for k,v in oldp.items():
   w=new[k]
   if isinstance(v,float):assert struct.pack('!d',v)==struct.pack('!d',w),(k,v,w)
   else:assert v==w,(k,v,w)
  bit_checks.append((dep,arr,days))
 # Assert overflow on original float path and finite Decimal mass in fallback.
 try:old.rendezvous(10.,2000.,365.25,a,auth)
 except OverflowError:pass
 else:raise AssertionError('FLOAT_2000_ARRIVAL_MUST_OVERFLOW')
 p=rendezvous(10.,2000.,365.25,a,auth)
 assert p['calculation_path']=='DECIMAL60' and isinstance(p['mass_in_leo_kg'],D) and p['mass_in_leo_kg'].is_finite()
 return {'float_bit_identical_cases':bit_checks,'arrival_2000_float_overflow':True,'arrival_2000_decimal_mass_finite':True,'arrival_2000_decimal_mass':str(p['mass_in_leo_kg'])}
