"""Evidence-fed chemical vehicle performance gate for GAP-016.

The solver owns equations, not vehicle parameters. Missing dry mass, propellant,
Isp, payload or required maneuver delta-v remains UNKNOWN. No timeline value or
Lambert geometry is silently converted into vehicle performance.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Mapping

G0_M_S2=9.80665

@dataclass(frozen=True)
class ChemicalVehicleAssessmentV03:
 status:str
 available_delta_v_km_s:float|None
 required_delta_v_km_s:float|None
 initial_mass_kg:float|None
 final_mass_kg:float|None
 propellant_mass_kg:float|None
 payload_mass_kg:float|None
 power_constraint_status:str
 infrastructure_status:str
 actor_access_status:str
 limiting_constraints:tuple[str,...]
 provenance_refs:tuple[str,...]

def assess_chemical_vehicle(*,required_delta_v_km_s:float|None,
    vehicle:Mapping[str,object],payload_mass_kg:float|None,
    infrastructure_status:str,actor_access_status:str)->ChemicalVehicleAssessmentV03:
 refs=tuple(str(x) for x in vehicle.get('provenance_refs',()))
 missing=[]
 dry=vehicle.get('dry_mass_kg'); prop=vehicle.get('usable_propellant_mass_kg'); isp=vehicle.get('specific_impulse_s')
 if dry is None: missing.append('DRY_MASS_UNKNOWN')
 if prop is None: missing.append('USABLE_PROPELLANT_MASS_UNKNOWN')
 if isp is None: missing.append('SPECIFIC_IMPULSE_UNKNOWN')
 if payload_mass_kg is None: missing.append('PAYLOAD_MASS_UNKNOWN')
 if required_delta_v_km_s is None: missing.append('REQUIRED_MANEUVER_DELTA_V_UNKNOWN')
 if not refs: missing.append('VEHICLE_PROVENANCE_MISSING')
 if actor_access_status not in {'ACCESS','OPERATIONAL'}: missing.append('ACTOR_ACCESS_NOT_USABLE')
 if infrastructure_status!='AVAILABLE': missing.append('REQUIRED_INFRASTRUCTURE_NOT_AVAILABLE')
 if missing:
  return ChemicalVehicleAssessmentV03('UNKNOWN',None,required_delta_v_km_s,None,None,None,payload_mass_kg,
   'NOT_APPLICABLE_CHEMICAL_IMPULSIVE',infrastructure_status,actor_access_status,tuple(missing),refs)
 dry=float(dry); prop=float(prop); isp=float(isp); payload=float(payload_mass_kg); req=float(required_delta_v_km_s)
 if min(dry,prop,isp,payload,req)<0 or dry<=0 or isp<=0:
  raise ValueError('invalid chemical vehicle parameter')
 m0=dry+prop+payload; mf=dry+payload
 dv=G0_M_S2*isp*math.log(m0/mf)/1000.0
 constraints=() if dv>=req else ('INSUFFICIENT_DELTA_V_MARGIN',)
 return ChemicalVehicleAssessmentV03('FEASIBLE' if not constraints else 'INFEASIBLE',dv,req,m0,mf,prop,payload,
  'NOT_APPLICABLE_CHEMICAL_IMPULSIVE',infrastructure_status,actor_access_status,constraints,refs)
