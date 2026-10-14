"""OFFLINE NON-RUNTIME travel-window pilot. No imports from simulation conductors.

Qualified state source: existing Solar SPICE adapter and Build 7 source manifests.
Transfer model: existing lamberthub Izzo zero-rev prograde heliocentric screen,
extended to moving origins and continuous flight-time minima.
Prices: explicit, non-empirical 2026 Build 7 proportional-burden proxy, held flat.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from collections import defaultdict
import csv
import json
import math
import time as clock

from simulation.offworld_mvp.build7 import compile_solar_accessibility as legacy
from src.loom_spice_ephemeris_adapter import (
    SolarEphemerisRegistry, SpiceEphemerisAdapter, registry_from_manifest)

ROOT = Path(__file__).resolve().parents[4]
ANCHORS = ROOT / 'simulation/offworld_mvp/build7/inputs/BUILD7_MISSION_COSTS_2026_2035_PROVISIONAL_V1.csv'
ASSET_ROOT = Path('/home/ubuntu/loom_solar_assets')
PILOT_PAIRS = (('EARTH', 'MERCURY'), ('EARTH', 'MARS'), ('MARS', 'CERES'))
SERVICE = 'ORBITAL_RECON'
TECHNOLOGY = 'IMPULSIVE_ORBITAL_RECON_2T_PROVISIONAL'
WAIT_DEFAULT_MONTHS = 12
# Vehicle-class capability is authored, not inferred from prices or from
# the technology timeline. Heavier payloads/ships need separately authored rows.
TECHNOLOGY_TABLE = (
    dict(id=TECHNOLOGY, from_year=2026, to_year=2226,
         service_type=SERVICE, payload_tonnes=2,
         max_departure_vinf_km_s=10.0, max_arrival_vinf_km_s=10.0,
         standing='TEST_ONLY_PROVISIONAL_AUTHORED_2026_VEHICLE_CLASS_NOT_CANON',
         reason='kT-selected candidate B: hypothetical 2-tonne orbital recon reference ship; '
                'both endpoint hyperbolic excess speeds must satisfy 10.0 km/s on one transfer; '
                'not a physical vehicle qualification; heavier ships require their own row',
         source='AUTHORED_KT_CANDIDATE_B_NOT_DERIVED_FROM_BUILD7_PRICES'),
)
# Numeric optimization intervals are brackets, NOT discrete TOF candidates.
# 45 days minimum; 1400 days maximum; dense flight-time scan and
# local continuous refinement only INSIDE discovered feasible intervals.
TOF_SCAN_DAYS = 2.0
CLOSED_AUDIT_SCAN_DAYS = 0.25
TOF_BRACKETS = ((45.0, 180.0), (180.0, 520.0), (520.0, 1400.0))
DEPARTURE_STEP_DAYS = 7
REFINE_NEAR_MINIMUM_DAYS = 14
MOON_LOCAL_LEG_DAYS = 5  # BUILD7 lunar ORBITAL_RECON 2026 proxy, mirrored for Moon -> Earth.
MOON_LOCAL_FLYBY_DAYS = 3
SOURCE_CLASS = ('DIRECT', 'PROPAGATED', 'MISSING')


def _iso(d):
    return d.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def _day(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, time(), timezone.utc)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError('date must have timezone')
        return value.astimezone(timezone.utc)
    parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def _add_months(d, count):
    y = d.year + (d.month - 1 + count) // 12
    m = (d.month - 1 + count) % 12 + 1
    import calendar
    return d.replace(year=y, month=m, day=min(d.day, calendar.monthrange(y, m)[1]))


def price_table():
    """Every service rate is the 2026 median(Build 7 cost / v_inf burden).

    Prices are in the exact existing USD_MILLIONS authoring units; the
    2026 2-tonne orbital recon proxy is NOT a real route, carrier, or launch quote.
    No later-year market improvement/inflation/adoption is inferred.
    """
    with ANCHORS.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    ratios = defaultdict(list)
    moon = None
    for r in rows:
        if r['year'] != '2026' or not r['one_way_cost_usd_millions']:
            continue
        if r['body_id'] == 'MOON':
            if r['mission_type'] == SERVICE:
                moon = r
            continue
        if r['method'] not in ('REFINED_GROUPED_LAMBERT_GRID',
                                'EXISTING_SCREEN_SINGLE_CANDIDATE'):
            continue
        burden = float(r['departure_vinf_km_s']) + float(r['arrival_vinf_km_s'])
        if burden > 0:
            ratios[r['mission_type']].append(float(r['one_way_cost_usd_millions']) / burden)
    if not ratios.get(SERVICE) or moon is None:
        raise ValueError('2026 Build 7 mission price anchor unavailable')
    # Median rather than regress a physical fixed/variable cost split the
    # Build 7 source never claims. Explicitly a modelling assumption.
    import statistics
    table = {}
    for yr in range(2026, 2227):
        for service, values in sorted(ratios.items()):
            table[(yr, service)] = {
                'year': yr, 'service_type': service,
                'usd_millions_per_km_s_burden': round(statistics.median(values), 9),
                'anchor_count_2026': len(values),
                'basis': 'median(2026 Build 7 one_way_cost_usd_millions / '
                         '(departure_vinf + arrival_vinf)) among non-Moon priced rows',
                'standing': 'HELD_AT_2026_LEVEL_BY_ASSUMPTION_NOT_EMPIRICAL',
                'source_sha256': sha256(ANCHORS.read_bytes()).hexdigest()
            }
    lunar = dict(year=2026, service_type=SERVICE,
                 usd_millions=float(moon['one_way_cost_usd_millions']),
                 flight_days=MOON_LOCAL_LEG_DAYS,
                 source='BUILD7_2026_EARTH_TO_MOON_ORBITAL_RECON_REVERSED_PROXY',
                 standing='PROVISIONAL_NOT_A_QUALIFIED_MOON_TO_EARTH_SERVICE',
                 source_sha256=sha256(ANCHORS.read_bytes()).hexdigest())
    return table, lunar


def state_registry(asset_root=ASSET_ROOT):
    """Merge selected existing governed sources; no new celestial-state authority."""
    sources, _ = legacy._source_index(asset_root)
    ref = json.loads(legacy.INPUT.read_text())
    bodies = {}; identifiers = {}; by_source = {}; coverage = {}
    for body in ('EARTH', 'MERCURY', 'MARS', 'CERES'):
        record = next((r for r in ref['records'] if r['body_id'] == body), None)
        if record is None:  # Earth is not necessarily a destination reference row
            record = {'body_id':'EARTH','canonical_name':'Earth','body_class':'PLANET',
                      'active_naif_ids':['399'],'ephemeris_sources':['DE440']}
        reg = legacy._registry_for(record, sources)
        bodies.update(reg.bodies)
        for r in reg.identifiers:
            identifiers[(r.body_id, r.identifier_value)] = r
        for sid, r in reg.sources.items():
            old = by_source.get(sid)
            if old and old.sha256 != r.sha256:
                raise ValueError('conflicting qualified Solar asset ' + sid)
            by_source[sid] = r
        for r in reg.coverage:
            coverage[(r.ephemeris_source_id, r.body_id, r.valid_from, r.valid_until)] = r
    # Bennu's 2140 seam must come from current Phase 4D authority, not the
    # older Build 7 2026 direct-only reference.
    breg = registry_from_manifest(
        ROOT/'manifests/solar/SOLAR_PHASE4D_STRATEGIC_BODIES_V1.json', asset_root)
    bodies['BENNU'] = breg.bodies['BENNU']
    for r in breg.identifiers:
        if r.body_id == 'BENNU':
            identifiers[(r.body_id,r.identifier_value)] = r
    for r in breg.coverage:
        if r.body_id == 'BENNU':
            source = breg.sources[r.ephemeris_source_id]
            by_source[r.ephemeris_source_id] = source
            coverage[(r.ephemeris_source_id,r.body_id,r.valid_from,r.valid_until)] = r
    return SolarEphemerisRegistry(
        bodies.values(), identifiers.values(), by_source.values(), coverage.values())


class TravelPilot:
    def __init__(self, *, asset_root=ASSET_ROOT, allow_approximation=False):
        self.adapter = SpiceEphemerisAdapter(state_registry(asset_root))
        self.allow_approximation = allow_approximation
        self.price_by_year, self.lunar = price_table()
        self.solve_count = 0
        self.sample_seconds = 0.0
        self.options = {}
        self._state_cache = {}

    def state_class(self, body, epoch):
        try:
            source, _ = self.adapter.registry.source_for(body, _iso(_day(epoch)))
        except Exception:
            return 'MISSING'
        return 'DIRECT' if source.navigation_grade else 'PROPAGATED'

    def _state(self, body, epoch):
        utc = _iso(epoch)
        kind = self.state_class(body, epoch)
        if kind == 'MISSING':
            raise ValueError('UNKNOWN_EPHEMERIS_MISSING:' + body + ':' + utc)
        if kind == 'PROPAGATED' and not self.allow_approximation:
            raise ValueError('UNKNOWN_EPHEMERIS_PROPAGATED:' + body + ':' + utc)
        key = (body, utc)
        if key not in self._state_cache:
            self._state_cache[key] = self.adapter.resolve(body, utc)
        return self._state_cache[key], kind

    def _solve(self, origin, destination, departure, tof_days):
        import numpy as np
        from lamberthub import izzo2015
        arrival = departure + timedelta(days=float(tof_days))
        s1, q1 = self._state(origin, departure)
        s2, q2 = self._state(destination, arrival)
        t0 = clock.perf_counter()
        v1, v2 = izzo2015(legacy.SUN_GM_KM3_S2,
                           np.asarray(s1.position_km), np.asarray(s2.position_km),
                           float(tof_days)*86400, M=0, prograde=True, low_path=True)
        self.solve_count += 1
        self.sample_seconds += clock.perf_counter()-t0
        dep = float(np.linalg.norm(v1 - np.asarray(s1.velocity_km_s)))
        arr = float(np.linalg.norm(v2 - np.asarray(s2.velocity_km_s)))
        if not all(math.isfinite(x) for x in (dep,arr)):
            raise ValueError('NONFINITE_TRANSFER')
        return dict(origin=origin, destination=destination,
                    departure=_iso(departure), arrival=_iso(arrival),
                    flight_days=round(float(tof_days),5),
                    departure_vinf_km_s=round(dep,7), arrival_vinf_km_s=round(arr,7),
                    transfer_burden_km_s=round(dep+arr,7),
                    c3_km2_s2=round(dep**2,7),
                    state_class_origin=q1, state_class_destination=q2,
                    source_origin=s1.provenance['ephemeris_source_id'],
                    source_destination=s2.provenance['ephemeris_source_id'],
                    asset_sha256_origin=s1.provenance['asset_sha256'],
                    asset_sha256_destination=s2.provenance['asset_sha256'],
                    standing=('SCENARIO_APPROXIMATION_NOT_EXECUTABLE_AUTHORITY'
                              if 'PROPAGATED' in (q1,q2) else
                              'DIRECT_PRELIMINARY_LAMBERT_NOT_MISSION_DESIGN'))

    @staticmethod
    def _admitted(result, tech=TECHNOLOGY_TABLE[0]):
        # Both physical endpoints on the SAME candidate; no price penalties.
        return (result['departure_vinf_km_s'] <= tech['max_departure_vinf_km_s']
                and result['arrival_vinf_km_s'] <= tech['max_arrival_vinf_km_s'])

    def _scan(self, origin, destination, departure, *, step_days, keep_samples):
        """Enumerate all brackets without artificial cost penalties.

        Explicit NO_TRAJECTORY only means none observed at the stated TOF
        resolution. No finite discrete scan proves absence between samples.
        """
        from scipy.optimize import minimize_scalar
        departure = _day(departure)
        rate = self.price_by_year[(departure.year, SERVICE)]
        feasible = []
        attempted = 0
        for a, b in TOF_BRACKETS:
            n = math.ceil((b-a)/step_days)
            times = [a + i*step_days for i in range(n)] + [b]
            times = sorted(set(min(float(b),t) for t in times))
            points = []
            for tof in times:
                try:
                    row = self._solve(origin, destination, departure, tof)
                    valid = self._admitted(row)
                except (ValueError, RuntimeError):
                    row, valid = None, False
                attempted += 1
                points.append((tof,row,valid))
                if valid:
                    feasible.append(row)
            if not keep_samples:
                continue
            # Refine the minima of contiguous sampled admissible segments.
            # Cost is optimized ONLY inside found feasible regions. Boundary
            # outcomes are checked, not assigned huge synthetic cost values.
            groups=[]
            running=[]
            for point in points:
                if point[2]:
                    running.append(point)
                elif running:
                    groups.append(running)
                    running=[]
            if running:
                groups.append(running)
            for group in groups:
                if len(group)<2:
                    continue
                low, high = group[0][0], group[-1][0]
                if high-low <= 0.1:
                    continue
                def burden(tof):
                    r=self._solve(origin,destination,departure,tof)
                    if not self._admitted(r):
                        raise ValueError('continuous minimum outside sampled feasible interval')
                    return r['transfer_burden_km_s']
                # minimize_scalar bounded requires valid sample bracket; explicit
                # feasibility verified on every sampled and returned trajectory.
                try:
                    m=minimize_scalar(burden,method='bounded',
                                      bounds=(low, high),options={'xatol':.05,'maxiter':55})
                    r=self._solve(origin,destination,departure,float(m.x))
                    if self._admitted(r):
                        feasible.append(r)
                except (ValueError, RuntimeError):
                    # Retain feasible scan points even if local interval is
                    # non-convex or an intermediate continuous trial is invalid.
                    pass
        if not keep_samples:
            return dict(checked=attempted, feasible_samples=len(feasible),
                        first_feasible=(feasible[0] if feasible else None),
                        scan_step_days=step_days)
        for result in feasible:
            result.update(service_type=SERVICE,technology=TECHNOLOGY,
                          cost_usd_millions=round(
                              rate['usd_millions_per_km_s_burden'] *
                              result['transfer_burden_km_s'],6),
                          cost_standing=rate['standing'],
                          price_anchor_sha256=rate['source_sha256'])
        feasible.sort(key=lambda r:(r['flight_days'],r['cost_usd_millions']))
        frontier=[]
        best_price=float('inf')
        for result in feasible:
            if result['cost_usd_millions'] < best_price-1e-6:
                frontier.append(result)
                best_price=result['cost_usd_millions']
        if len(frontier)>4:
            indices={0,len(frontier)-1}
            indices.update(round(i*(len(frontier)-1)/3) for i in range(1,3))
            frontier=[frontier[i] for i in sorted(indices)]
        return frontier

    def candidates(self, origin, destination, departure, *, technology=TECHNOLOGY):
        if technology != TECHNOLOGY:
            raise ValueError('UNKNOWN_TECHNOLOGY')
        dep=_day(departure)
        if not (2026 <= dep.year <= 2226):
            raise ValueError('YEAR_OUTSIDE_PRICE_TABLE')
        return self._scan(origin,destination,dep,
                          step_days=TOF_SCAN_DAYS,keep_samples=True)

    def audit_closed_week(self, origin, destination, departure):
        """Independent 8x-denser audit at one weekly sample departure date.

        Gives flight-duration sample-bound evidence at that departure date,
        not closure of a full calendar week or a mathematical certificate.
        """
        return self._scan(origin,destination,departure,
                          step_days=CLOSED_AUDIT_SCAN_DAYS,keep_samples=False)

    def generate_route(self, origin, destination, first='2026-01-01', last='2031-12-31'):
        start=_day(first)
        stop=_day(last)
        grid=[]
        day=start
        while day<=stop:
            grid.append(day)
            day+=timedelta(days=DEPARTURE_STEP_DAYS)
        outputs={}
        for day in grid:
            outputs[day.date().isoformat()] = self.candidates(origin,destination,day)

        # Challenge every coarse-closed weekly sample date with the 0.25-day
        # flight-time grid. A rescued date receives actual feasible candidates,
        # not just a changed availability flag. This precedes weekly minima
        # and the existing ±14 calendar-day refinement.
        coarse_closed=[day for day in grid if not outputs[day.date().isoformat()]]
        fine_confirmed_closed=[]
        fine_reopened=[]
        fine_samples=0
        for day in coarse_closed:
            audit=self.audit_closed_week(origin,destination,day)
            fine_samples+=audit['checked']
            if audit['feasible_samples']:
                options=self._scan(origin,destination,day,
                                   step_days=CLOSED_AUDIT_SCAN_DAYS,keep_samples=True)
                if not options:
                    raise ValueError('fine scan found witness but recovered no options: '+_iso(day))
                outputs[day.date().isoformat()]=options
                fine_reopened.append(day.date().isoformat())
            else:
                fine_confirmed_closed.append(day.date().isoformat())
        weekly_options=[(day, min(outputs[day.date().isoformat()],
                                  key=lambda x:x['cost_usd_millions']))
                        for day in grid if outputs[day.date().isoformat()]]
        feasible_weekly=len(weekly_options)
        weekly_cheapest=(min(weekly_options,key=lambda x:x[1]['cost_usd_millions'])[1]
                         if weekly_options else None)
        weekly_costliest=(max(weekly_options,key=lambda x:x[1]['cost_usd_millions'])[1]
                          if weekly_options else None)
        # Re-evaluate up to 14 days on either side of a local weekly cost
        # minimum, but do not interpolate fictitious opportunity prices.
        def best(d):
            rows=outputs.get(d.date().isoformat(),())
            return min((x['cost_usd_millions'] for x in rows),default=float('inf'))
        lows=[day for i,day in enumerate(grid) if 0<i<len(grid)-1
              and math.isfinite(best(day))
              and best(day) <= best(grid[i-1])
              and best(day) <= best(grid[i+1])]
        refinements=set()
        for center in lows:
            for offset in range(-REFINE_NEAR_MINIMUM_DAYS,REFINE_NEAR_MINIMUM_DAYS+1):
                day=center+timedelta(days=offset)
                if start<=day<=stop:
                    refinements.add(day)
        for day in sorted(refinements):
            key=day.date().isoformat()
            if key not in outputs:
                outputs[key]=self.candidates(origin,destination,day)
        self.options[(origin,destination)] = tuple(
            r for day in sorted(outputs) for r in outputs[day])
        return dict(origin=origin,destination=destination,
                    weekly_departures=len(grid),
                    flight_time_scan_days=TOF_SCAN_DAYS,
                    closed_week_check_scan_days=CLOSED_AUDIT_SCAN_DAYS,
                    coarse_feasible_weekly_departures=len(grid)-len(coarse_closed),
                    coarse_closed_weekly_departures=len(coarse_closed),
                    fine_checked_coarse_closed_week_dates=[day.date().isoformat()
                                                           for day in coarse_closed],
                    fine_confirmed_closed_week_dates=fine_confirmed_closed,
                    fine_reopened_week_dates=fine_reopened,
                    fine_scan_duration_samples=fine_samples,
                    feasible_weekly_departures=feasible_weekly,
                    unavailable_weekly_departures=len(grid)-feasible_weekly,
                    refined_unique_departures=len(outputs)-len(grid),
                    candidate_count=len(self.options[(origin,destination)]),
                    local_minima=len(lows),
                    weekly_cheapest_sample=weekly_cheapest,
                    weekly_costliest_sample=weekly_costliest,
                    options=tuple(self.options[(origin,destination)]))

    def travel_option(self, origin, destination, ready_date, technology=TECHNOLOGY,
                      wait_limit_months=WAIT_DEFAULT_MONTHS):
        """Cheapest among stored pilot options inside the authored wait limit.

        This is not an on-demand daily departure scan. A future on-demand
        lookup should scan daily dates inside the requested wait limit.
        """
        ready=_day(ready_date)
        if not isinstance(wait_limit_months,int) or not 0<wait_limit_months<=60:
            raise ValueError('INVALID_WAIT_LIMIT_MONTHS')
        deadline=_add_months(ready,wait_limit_months)
        local=origin=='MOON'
        source_origin='EARTH' if local else origin
        choices=self.options.get((source_origin,destination),())
        if not choices:
            return dict(status='WAIT_LIMIT_EXHAUSTED',reason='NO_PILOT_ROUTE_DATA',
                        ready_date=_iso(ready), deadline=_iso(deadline),
                        policy='CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED')
        due=timedelta(days=MOON_LOCAL_LEG_DAYS if local else 0)
        valid=[r for r in choices if r['technology']==technology and
               ready < _day(r['departure'])-due <= deadline]
        if not valid:
            return dict(status='WAIT_LIMIT_EXHAUSTED',reason='NO_ADMITTED_DEPARTURE_IN_WINDOW',
                        ready_date=_iso(ready), deadline=_iso(deadline),
                        policy='CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED')
        selected=min(valid,key=lambda r:(r['cost_usd_millions']+
                     (self.lunar['usd_millions'] if local else 0),
                     _day(r['departure']),r['flight_days']))
        output=dict(selected)
        if local:
            local_start=_day(selected['departure'])-due
            output.update(origin='MOON',departure=_iso(local_start),
                          transfer_departure_earth=selected['departure'],
                          flight_days=round(selected['flight_days']+MOON_LOCAL_LEG_DAYS,5),
                          cost_usd_millions=round(selected['cost_usd_millions']+
                                                  self.lunar['usd_millions'],6),
                          local_leg=dict(from_body='MOON',to_body='EARTH',
                                         days=MOON_LOCAL_LEG_DAYS,
                                         cost_usd_millions=self.lunar['usd_millions'],
                                         standing=self.lunar['standing'],
                                         source_sha256=self.lunar['source_sha256']))
        output.update(status='AVAILABLE_PROVISIONAL_NOT_EXECUTABLE_AUTHORITY',
                      policy='CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED',
                      ready_date=_iso(ready), wait_limit_months=wait_limit_months,
                      wait_days=round((_day(output['departure'])-ready).total_seconds()/86400,5),
                      deadline=_iso(deadline),
                      elapsed_days_ready_to_arrival=round((_day(output['arrival'])-ready).total_seconds()/86400,5))
        return output


def write_summary(pilot, path):
    from importlib import metadata
    routes=[]
    for o,d in PILOT_PAIRS:
        result=pilot.generate_route(o,d)
        # Keep compact reproducible *pilot result*, not all sampled options.
        options=result.pop('options')
        if not options:
            routes.append({**result,'status':'NO_FEASIBLE_WINDOW_AT_SCAN_RESOLUTION'})
            continue
        price_min=min(options,key=lambda r:r['cost_usd_millions'])
        price_max=max(options,key=lambda r:r['cost_usd_millions'])
        routes.append({**result,'status':'FEASIBLE_WINDOWS_AT_SCAN_RESOLUTION',
                       'cheapest_sample':price_min,
                       'costliest_sample':price_max,
                       'first_sample':options[0],
                       'last_sample':options[-1]})
    earth_mars=pilot.travel_option('EARTH','MARS','2027-01-15',wait_limit_months=12)
    earth_mars_30=pilot.travel_option('EARTH','MARS','2027-01-15',wait_limit_months=30)
    moon_mars=pilot.travel_option('MOON','MARS','2027-01-15',wait_limit_months=30)
    rates={name:pilot.price_by_year[(2026,name)] for name in sorted(
        {r['service_type'] for r in pilot.price_by_year.values()})}
    # Eight coarse Mercury weekly-sample witnesses plus two rescued dates.
    witnesses=('2026-04-23','2026-04-30','2026-05-07','2027-04-15',
               '2027-04-22','2031-05-15','2031-05-22','2031-05-29')
    mercury=pilot.options[('EARTH','MERCURY')]
    rescued=('2026-05-14','2031-05-08')
    missing=[day for day in (*witnesses,*rescued)
             if not any(r['departure'].startswith(day) for r in mercury)]
    if missing:
        raise ValueError('known Mercury windows not rediscovered: '+repr(missing))
    # Preserve the previous nine-date sample as a historical note; they
    # are now members of the exhaustive, per-route 0.25-day closed checks.
    audit_dates={
        ('EARTH','MERCURY'):('2026-01-01','2028-01-06','2030-08-01'),
        ('EARTH','MARS'):('2026-01-01','2029-12-13','2030-01-10'),
        ('MARS','CERES'):('2028-03-09','2031-08-07','2031-12-11'),
    }
    closure=[]
    for route in routes:
        pair=(route['origin'],route['destination'])
        confirmed=set(route['fine_confirmed_closed_week_dates'])
        if route['coarse_closed_weekly_departures'] != (
                len(confirmed)+len(route['fine_reopened_week_dates'])):
            raise ValueError('fine check failed to cover every coarse-closed date: '+str(pair))
        for date in audit_dates[pair]:
            if date not in confirmed:
                raise ValueError('historical closure audit reopened: '+str(pair)+':'+date)
            closure.append(dict(origin=pair[0],destination=pair[1],
                                departure=date,checked_flight_durations=5423,
                                dense_step_days=CLOSED_AUDIT_SCAN_DAYS,
                                feasible_samples=0,
                                conclusion='NO_FEASIBLE_SAMPLED_TRANSFER_NOT_CONTINUOUS_PROOF'))
    result=dict(schema='LOOM_TRAVEL_PILOT_RESULT_V1',standing='ENGINEERING_PROVISIONAL_NOT_RUNTIME',
                route_summaries=routes,ready_date_examples=[earth_mars,earth_mars_30,moon_mars],
                known_mercury_weekly_witnesses=witnesses,
                known_rescued_mercury_weekly_witnesses=rescued,
                superseded_coarse_weekly_feasible_counts={
                    'EARTH->MERCURY':8,'EARTH->MARS':212,'MARS->CERES':192},
                exhaustive_closed_week_check=True,
                dense_closure_audits=closure,
                flight_time_scan_days=TOF_SCAN_DAYS,
                dense_closure_scan_days=CLOSED_AUDIT_SCAN_DAYS,
                previous_price_anchor_maxima_historical_only=dict(
                    departure_vinf_km_s=73.430819,arrival_vinf_km_s=56.091356,
                    status='HISTORICAL_PRICE_ANCHOR_LIMITS_NO_LONGER_IN_EFFECT'),
                rate_2026_by_service=rates,pricing_2036_2226='HELD_AT_2026_LEVEL_BY_ASSUMPTION_NOT_EMPIRICAL',
                lunar_provisional=pilot.lunar,
                technology_table=TECHNOLOGY_TABLE,
                solve_count=pilot.solve_count,
                source_manifests=list(legacy.MANIFESTS),
                solver='lamberthub.izzo2015 zero revolution, prograde, Sun-centered',
                dependencies={x:metadata.version(x) for x in
                              ('lamberthub','spiceypy','numpy','scipy')},
                no_simulation_consumers=True,
                weekly_sample_date_interpretation=(
                    'Open/closed counts refer to 313 weekly sample dates '
                    '(one departure every 7 days), not full calendar weeks. '
                    'A window narrower than the 7-day departure sampling step '
                    'may be missed, especially for Mercury. On-demand lookup '
                    'should scan daily departure dates inside the requested wait limit.'))
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,
                    default=Path(__file__).with_name('pilot_result.json'))
    ap.add_argument('--asset-root',type=Path,default=ASSET_ROOT)
    ap.add_argument('--print-summary',action='store_true',
                    help='Print committed route counts and SHA-256; no recalculation')
    args=ap.parse_args()
    if args.print_summary:
        raw=args.output.read_bytes()
        result=json.loads(raw)
        for row in result['route_summaries']:
            print(f"{row['origin']}->{row['destination']}: "
                  f"{row['feasible_weekly_departures']} open / "
                  f"{row['unavailable_weekly_departures']} closed "
                  f"({row['weekly_departures']} weekly sample dates)")
        print('sha256:',sha256(raw).hexdigest())
        raise SystemExit(0)
    from .batch import BatchTravelPilot
    x=BatchTravelPilot(asset_root=args.asset_root)
    out=write_summary(x,args.output)
    # Timing is process-specific telemetry, deliberately excluded from the
    # deterministic, source-backed artifact.
    solver_seconds=x.sample_seconds+x.batch_seconds
    print(json.dumps({
        'solve_count':x.solve_count,
        'batched_lambert_seconds':round(x.batch_seconds,4),
        'scalar_refinement_seconds':round(x.sample_seconds,4),
        'combined_solver_seconds':round(solver_seconds,4),
        'solver_only_solve_rate_per_second':round(x.solve_count/solver_seconds,2),
    },indent=2))
