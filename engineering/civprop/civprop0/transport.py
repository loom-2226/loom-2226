"""Narrow offline adapter: governed state context plus explicit surface-mission scenario.

FEASIBLE means feasible under the declared launch/transfer/landing assumptions,
never a validated trajectory. Endpoint distance is context, not delta-v or a path.
"""
from datetime import datetime
import math
from .model import Opportunity, Scenario

LIENS = ('No qualified Earth surface-to-orbit trajectory consumed',
         'Five-day transfer and polar landing success are scenario assumptions',
         'No site coordinates, terrain, delta-v, payload or propulsion sizing qualified')


def assess_mission(inputs: dict, scenario: Scenario) -> Opportunity:
    s = scenario
    duration = (datetime.fromisoformat(s.arrival.replace('Z', '+00:00')) -
                datetime.fromisoformat(s.departure.replace('Z', '+00:00'))).total_seconds()
    status, distance = 'UNKNOWN', None
    states = {(r['entity_id'], r['epoch_utc']): r for r in inputs['states']}
    required = [(b, t) for b in ('EARTH', s.body_id) for t in (s.departure, s.arrival)]
    if s.technology is False:
        status = 'INFEASIBLE'
    elif s.technology is True and duration == 5*86400 and all(k in states for k in required):
        rows = [states[k] for k in required]
        if all(r['navigation_grade'] and r['reference_frame'] == 'J2000/ECLIPTIC' and
               r['provenance']['units'] == 'km,km/s' for r in rows):
            a, b = states[('EARTH', s.departure)], states[(s.body_id, s.departure)]
            distance = math.dist(a['position_km'], b['position_km'])
            status = 'FEASIBLE'
    return Opportunity(status, s.departure, s.arrival, duration, distance, LIENS)
