"""Authored pair evaluator. No geometry construction or body-specific logic."""
import hashlib,json
from decimal import Decimal as D

def identity(experiment, manifest_sha, config_sha):
 return hashlib.sha256(json.dumps({'experiment':experiment,'table_manifest_sha256':manifest_sha,'config_sha256':config_sha},sort_keys=True,separators=(',',':')).encode()).hexdigest()

def pairs(experiment):
 classes={c['class_id']:c for c in experiment['vehicle_classes']}
 missions={m['mission_type_id']:m for m in experiment['mission_types']}
 return [(classes[c],missions[m]) for c in experiment['selected_vehicle_classes'] for m in experiment['selected_mission_types']]

def evaluate(geometry,vehicle,mission,experiment):
 rows=geometry['trajectories'];lo,hi=map(lambda v:D(str(v)),experiment['sampling']['flight_range_days']);dl=D(vehicle['departure_limit_km_s']);al=D(vehicle['arrival_limit_km_s']);rate=D(experiment['price_rate_usd_millions_per_km_s'])
 def speeds(r):return D(str(r['departure_vinf_km_s'])),D(str(r['arrival_vinf_km_s']))
 def metric(r):return sum(D(str(r[k])) for k in mission['charged_speed_terms'])
 allowed=[r for r in rows if lo<=D(str(r['flight_days']))<=hi and speeds(r)[0]<=dl and (not mission['enforce_arrival_limit'] or speeds(r)[1]<=al)]
 best=min(allowed,key=lambda r:(rate*metric(r),D(str(r['flight_days'])))) if allowed else None
 bounds=experiment['price_calibration_bounds_km_s']
 priced=[r for r in allowed if bounds is None or D(str(bounds[0]))<=metric(r)<=D(str(bounds[1]))]
 quoted=min(priced,key=lambda r:(rate*metric(r),D(str(r['flight_days'])))) if priced else None
 return {'status':'INFEASIBLE' if not allowed else 'UNPRICED' if quoted is None else 'PRICED_TEST_ONLY' if bounds is None else 'PRICED','price':str(rate*metric(quoted)) if quoted else None,'flight_days':quoted['flight_days'] if quoted else None,'feasible':bool(allowed),'unpriced':bool(allowed) and quoted is None}
