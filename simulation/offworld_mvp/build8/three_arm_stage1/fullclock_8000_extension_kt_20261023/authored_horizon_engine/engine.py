"""Test-only copied flight-grid validator. All other engine logic inherited unchanged."""
import hashlib,json,math
from pathlib import Path
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
class AuthoredHorizonTravel(OnDemandTravel):
 def __init__(self,*,scenario_path,**kw):
  self.scenario_path=Path(scenario_path);data=self.scenario_path.read_bytes();self.scenario_sha256=hashlib.sha256(data).hexdigest();self.authored_scenario=json.loads(data);self.max_flight_days=float(self.authored_scenario['maximum_flight_days']);assert math.isfinite(self.max_flight_days) and self.max_flight_days>0
  print('AUTHORED_MAX_FLIGHT_DAYS',self.max_flight_days,'SCENARIO_SHA256',self.scenario_sha256,flush=True);super().__init__(**kw)
 def _times(self,step,flight_range_days=None):
  if not 0<step<=5000:raise ValueError('INVALID_FLIGHT_STEP')
  if flight_range_days is not None:
   if (len(flight_range_days)!=2 or not 0<float(flight_range_days[0])<float(flight_range_days[1])<=self.max_flight_days):raise ValueError('INVALID_FLIGHT_RANGE')
   brackets=(tuple(map(float,flight_range_days)),)
  else:
   from simulation.offworld_mvp.build8.travel_pilot.pilot import TOF_BRACKETS
   brackets=TOF_BRACKETS
  times=set()
  for lo,hi in brackets:
   n=math.ceil((hi-lo)/step)
   times.update(round(min(hi,lo+i*step),8) for i in range(n))
   times.add(hi)
  return sorted(times)
