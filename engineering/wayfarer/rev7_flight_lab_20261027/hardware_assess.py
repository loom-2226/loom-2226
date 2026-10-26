"""Per-installation, NON-CANON hardware demand assessment over flightlab traces.

PASS/FAIL applies only to a stated numerical comparison. This tool has no means
of validating physical hardware or certificates; its hardware decision is HOLD.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from flightlab import G0, exhaust_velocity, mass_properties, source_hash, unit, vec
from lab import load, save_run

ROOT = Path(__file__).resolve().parent
REV7 = 'source/design/wayfarer/v0.5.7/'
CARD = REV7 + 'out/wayfarer_v05_card.json'
GEOMETRY = REV7 + 'out/wayfarer_v05_geometry.json'
CERT = REV7 + 'out/certification_report.json'
PRIORITY = 'source/engineering/current/LOOM_2226_Wayfarer_RCS_Torch_Metric_Geometry_Priority_v0.1.md'


def write_json(path, value):
    """Keep all companion outputs inside the scratch workspace, outside sources."""
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT) or path.is_relative_to(ROOT / 'source'):
        raise ValueError('hardware output must stay in the scratch workspace, outside source/')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def rating(table, engine_id):
    return {**table.get('default', {}), **table.get('by_id', {}).get(engine_id, {})}


def finite_cone_sphere_clearance(apex, direction, length, half_angle, center, radius):
    """Signed distance to a finite solid cone minus a coarse sphere radius.

    Axisymmetric reduction: distance to the triangle (0,0),(L,0),(L,L*tan(a))
    in axial/radial coordinates. No sampling along the plume or mesh engine.
    """
    if not (math.isfinite(length) and length > 0 and
            math.isfinite(half_angle) and 0 <= half_angle < 89 and radius >= 0):
        raise ValueError('finite positive plume length, 0..89 deg angle and nonnegative sphere radius required')
    d = vec(center) - vec(apex)
    axial = float(d @ unit(vec(direction)))
    radial = float(np.linalg.norm(d - axial * unit(vec(direction))))
    slope = math.tan(math.radians(half_angle))
    p = np.array([axial, radial])
    if 0 <= axial <= length and radial <= axial * slope:
        return -float(radius)
    vertices = [np.array([0., 0.]), np.array([length, 0.]), np.array([length, length * slope])]
    distances = []
    for a, b in zip(vertices, vertices[1:] + vertices[:1]):
        edge = b - a
        u = np.clip((p - a) @ edge / max(float(edge @ edge), 1e-30), 0, 1)
        distances.append(float(np.linalg.norm(p - a - u * edge)))
    return min(distances) - float(radius)


def wayfarer_envelopes(deployment):
    """Explicit conservative Rev7 hull/torch cylinder covers and panel spheres.

    A sphere chain covers cylinders; each panel uses one circumsphere. These
    are exclusion envelopes, not CAD or exact surface collision geometry.
    """
    if deployment not in ('stowed', 'torch', 'metric'):
        return []
    geom = load(ROOT / GEOMETRY)
    envelopes = []

    def cylinder(name, x0, x1, radius, yz=(0, 0)):
        n = math.ceil((x1 - x0) / .5)
        dx = (x1 - x0) / n
        for i in range(n):
            envelopes.append({'id': name + ':' + str(i),
                              'center_m': [x0 + (i + .5) * dx, *yz],
                              'radius_m': math.hypot(radius, dx / 2)})

    # Armour's maximum 4.5 m radius; bounding cylinder includes the crown.
    cylinder('hull', 0, 34.3, 4.5)
    for part in geom['parts']:
        s = part['shape']
        if part['id'] in ('shield', 'reactor', 'nozzle'):
            cylinder(part['id'], s['x0'], s['x1'], max(s['r0'], s['r1']), s.get('offset_yz', [0, 0]))
        if part['id'].startswith(('strake_', 'hotfin_')) and s['k'] == 'panel':
            span = s['span']
            if part['id'].startswith('strake_') and deployment != 'stowed':
                span = 4. if deployment == 'torch' else 2.
            if part['id'].startswith('hotfin_') and not part['id'].startswith('hotfin_root_') and deployment == 'torch':
                span = geom['hot_fins']['span_m']
            a = math.radians(s['a'])
            r = s['r0'] + span / 2
            envelopes.append({'id': part['id'],
                              'center_m': [(s['x0'] + s['x1']) / 2, r * math.cos(a), r * math.sin(a)],
                              'radius_m': math.sqrt(((s['x1'] - s['x0']) / 2)**2 + (span / 2)**2 + (s['t'] / 2)**2)})
    return envelopes


def assess(ship, experiment, result, trace, assumptions=None, evidence=None):
    """Read a run; never alter its state, inputs, fuel ledger or qualification."""
    assumptions = assumptions or {}
    evidence = evidence or {'config': 'in-memory config', 'experiment': 'in-memory experiment',
                            'run': 'in-memory run', 'trace': 'in-memory trace',
                            'assumptions': 'no hardware assumptions supplied'}
    if result['ship_sha256'] != source_hash(ship) or result['experiment_sha256'] != source_hash(experiment):
        raise ValueError('run/config/experiment hashes differ; rerun the specified installation')
    if not trace or any('engine_samples' not in t or 'step_s' not in t for t in trace):
        raise ValueError('complete per-step hardware evidence missing; rerun with current lab.py')
    if any(p['kind'] == 'metric' for p in result['phases']):
        raise ValueError('hardware assessor accepts conventional traces only; metric physical propagation is unresolved')

    rows = []
    def row(key, category, demand, capacity, source, explanation, status=None, scope='conditional numerical model'):
        for value in (demand, capacity):
            if isinstance(value, (int, float)) and not math.isfinite(value):
                raise ValueError('nonfinite demand or rating: ' + key)
        if status is None:
            status = 'HOLD' if demand is None or capacity is None else ('PASS' if demand <= capacity + 1e-9 * max(1, abs(capacity)) else 'FAIL')
        record = dict(requirement=key, category=category, status=status, demand=demand,
                      capacity=capacity, evidence=source, scope=scope, explanation=explanation)
        if isinstance(demand, (int, float)) and isinstance(capacity, (int, float)):
            record['margin'] = capacity - demand
        rows.append(record)

    config_ev = evidence['config']
    trace_ev = evidence['trace']
    hyp_ev = evidence['assumptions']
    wayfarer = ship.get('provenance', {}).get('card') == CARD
    engines = {e['id']: (kind, e) for kind in ('rcs', 'torch') for e in ship.get(kind, [])}
    inventory = {}
    for eid, (kind, e) in engines.items():
        inventory[eid] = dict(id=eid, kind=kind, pos_m=e['pos_m'], direction=e['direction'],
            enabled=e.get('enabled', True), rated_thrust_N=e.get('max_N'), modes=e.get('modes'),
            installed_mass_kg=e.get('installed_mass_kg'),
            installed_inertia_kg_m2=e.get('installed_inertia_kg_m2'),
            tank=e.get('tank'), ve_m_s=exhaust_velocity(e) if kind == 'rcs' else None,
            gimbal=e.get('gimbal'), peak_command_N=0., peak_actual_average_N=0.,
            peak_actuator_endpoint_N=0., impulse_Ns=0., peak_flow_kg_s=0.,
            peak_gimbal_angle_deg=0., peak_gimbal_rate_deg_s=0.)

    # A mount here means a common application point, including co-located
    # original and additional engines. Local attachment geometry is unknown.
    mount_of = {eid: ','.join(format(float(x), '.9g') for x in e['pos_m']) for eid, (_, e) in engines.items()}
    mounts = {k: dict(engine_ids=[eid for eid in engines if mount_of[eid] == k],
                     peak_force_N=0., peak_force_vector_N=[0., 0., 0.],
                     time_s=None, peak_moment_about_cg_Nm=0., scalar_force_bound_N=0.) for k in set(mount_of.values())}
    force_peak = moment_peak = force_bound = moment_bound = 0.
    peak_flow = 0.; unknown_flow = set(); tank_peak = defaultdict(float); tank_requested = defaultdict(float)
    tank_consumed = defaultdict(float); total_energy = 0.; torch_power = torch_g = torch_angle = 0.
    torch_mode_ratios = defaultdict(float)
    previous_angles = {e['id']: vec(e['gimbal'].get('initial_angles_deg', [0, 0]))
                       for e in ship.get('rcs', []) if 'gimbal' in e}
    last_end = float(result['phases'][0]['t_start_s'])
    for t in trace:
        if not math.isclose(t['t_s'], last_end, abs_tol=1e-7):
            raise ValueError('trace has a time gap or overlap')
        last_end = t['t_s'] + t['step_s']
        forces = defaultdict(lambda: np.zeros(3)); endforces = defaultdict(lambda: np.zeros(3))
        moments = defaultdict(lambda: np.zeros(3)); sums = defaultdict(float)
        flow = 0.; flows = defaultdict(float)
        ff = np.zeros(3); tt = np.zeros(3); sb = mb = 0.
        for s in t['engine_samples']:
            eid = s['id']; kind, e = engines[eid]; inv = inventory[eid]; mid = mount_of[eid]
            f = s['actual_N']; endpoint = s['actuator_end_N']; peak = max(f, endpoint)
            inv['peak_command_N'] = max(inv['peak_command_N'], s['command_N'])
            inv['peak_actual_average_N'] = max(inv['peak_actual_average_N'], f)
            inv['peak_actuator_endpoint_N'] = max(inv['peak_actuator_endpoint_N'], endpoint)
            inv['impulse_Ns'] += f * t['step_s']
            fv = vec(s['force_body_N']); tv = vec(s['torque_body_Nm'])
            forces[mid] += fv; endforces[mid] += endpoint * vec(s['direction']); moments[mid] += tv; sums[mid] += peak
            ff += fv; tt += tv; sb += peak
            mb += np.linalg.norm(vec(e['pos_m']) - vec(t['cg_m'])) * peak
            ve = s['ve_m_s']; tank = e.get('tank')
            if peak > 0 and (ve is None or tank is None):
                unknown_flow.add(eid); inv['peak_flow_kg_s'] = None
            if ve is not None and tank is not None:
                flow += peak / ve; flows[tank] += peak / ve
                inv['peak_flow_kg_s'] = max(inv['peak_flow_kg_s'] or 0., peak / ve)
                tank_requested[tank] += s['before_tank_N'] / ve * t['step_s']
                tank_consumed[tank] += f / ve * t['step_s']
            if kind == 'torch' and f > 0:
                torch_mode_ratios[s['mode']] = max(torch_mode_ratios[s['mode']], peak / e['modes'][s['mode']]['max_N'])
                torch_g = max(torch_g, peak / (t['mass_kg'] * G0))
                torch_angle = max(torch_angle, math.degrees(math.acos(float(np.clip(unit(vec(e['direction'])) @ vec(s['direction']), -1, 1)))))
                if ve is not None:
                    torch_power = max(torch_power, .5 * peak * ve)
                    total_energy += .5 * f * ve * t['step_s']
        if not np.allclose(ff, t['force_body_N'], atol=1e-6) or not np.allclose(tt, t['torque_body_Nm'], atol=1e-5):
            raise ValueError('per-engine trace does not close realized wrench')
        force_peak = max(force_peak, float(np.linalg.norm(ff))); moment_peak = max(moment_peak, float(np.linalg.norm(tt)))
        force_bound = max(force_bound, sb); moment_bound = max(moment_bound, mb)
        for mid in forces:
            # Gimbal direction is held per solver step; endpoints bound the
            # throttle excursion. Tank factors are the solver's step average.
            fvec = max((forces[mid], endforces[mid]), key=np.linalg.norm)
            norm = float(np.linalg.norm(fvec)); m = mounts[mid]
            if norm > m['peak_force_N']:
                m.update(peak_force_N=norm, peak_force_vector_N=fvec.tolist(), time_s=t['t_s'])
            m['peak_moment_about_cg_Nm'] = max(m['peak_moment_about_cg_Nm'], float(np.linalg.norm(moments[mid])))
            m['scalar_force_bound_N'] = max(m['scalar_force_bound_N'], sums[mid])
        peak_flow = max(peak_flow, flow)
        for tank, f in flows.items(): tank_peak[tank] = max(tank_peak[tank], f)
        for eid, angles in t['gimbal_angles_deg'].items():
            inv = inventory[eid]; a = vec(angles)
            inv['peak_gimbal_angle_deg'] = max(inv['peak_gimbal_angle_deg'], float(np.max(abs(a))), float(np.max(abs(previous_angles[eid]))))
            inv['peak_gimbal_rate_deg_s'] = max(inv['peak_gimbal_rate_deg_s'], float(np.max(abs(a - previous_angles[eid]))) / t['step_s'])
            previous_angles[eid] = a
    if not math.isclose(last_end, result['final_state']['time_s'], abs_tol=1e-7):
        raise ValueError('trace does not cover the full run')
    for kind in ('rcs', 'torch'):
        impulse = sum(v['impulse_Ns'] for v in inventory.values() if v['kind'] == kind)
        if not math.isclose(impulse, result[kind + '_impulse_Ns'], abs_tol=1e-5, rel_tol=1e-9):
            raise ValueError('trace impulse differs from run: ' + kind)

    turns = []
    for i, (p, requested) in enumerate(zip(result['phases'], experiment['phases'])):
        if p['kind'] == 'rcs_turn':
            turns.append({k: p[k] for k in ('duration_s', 'at_target_time', 'gate_entry_s', 'post_hold_s', 'at_end', 'sustained_gate_duration_s')})
            turns[-1]['angle_deg'] = requested.get('angle_deg', 180.)
            for key, limit in [('attitude_error_deg', requested.get('gate_attitude_deg', .25)),
                               ('rate_deg_s', requested.get('gate_rate_deg_s', .05))]:
                row(f'turn.{i}.target.{key}', 'dynamics', p['at_target_time'][key], limit,
                    [evidence['experiment'], evidence['run']], 'Target-time numerical gate; later settling is recorded separately.')
    rcs_ratios = [max(v['peak_command_N'], v['peak_actual_average_N'], v['peak_actuator_endpoint_N']) / engines[eid][1]['max_N']
                  for eid, v in inventory.items() if v['kind'] == 'rcs']
    row('rcs.configured_force_limits', 'propulsion', max(rcs_ratios, default=0.), 1., [config_ev, trace_ev],
        'Commands and realized force remain within configured ratings; these ratings do not validate engines.')
    for eid, inv in inventory.items():
        kind, e = engines[eid]
        r = rating(assumptions.get('engine_ratings', {}), eid)
        row('engine.' + eid + '.physical_thrust_N', 'propulsion', max(inv['peak_actual_average_N'], inv['peak_actuator_endpoint_N']),
            r.get('thrust_N'), [hyp_ev, trace_ev], 'An applicable independently measured thrust/duty rating is required.', scope='HYPOTHETICAL declared rating' if r else 'physical evidence missing')
        if 'gimbal' in e:
            for field, cap in [('angle', e['gimbal']['limit_deg']), ('rate', e['gimbal']['rate_deg_s'])]:
                measured = inv['peak_gimbal_angle_deg'] if field == 'angle' else inv['peak_gimbal_rate_deg_s']
                row('gimbal.' + eid + '.' + field, 'dynamics', measured, cap, [config_ev, trace_ev],
                    'Per-axis kinematic limit only; loaded actuator torque, bandwidth, life and power remain untested.')
    row('gimbal.loaded_actuator_qualification', 'propulsion', None, None, [config_ev, hyp_ev],
        'Supply loaded steering torque/rate/lag, valve dynamics, power, pointing errors and endurance test evidence.')

    levels = {t['id']: float(t.get('initial_kg', t['capacity_kg'])) for t in ship.get('tanks', [])}
    m0, c0, i0 = mass_properties(ship, levels)
    end = result['final_state']
    no_install = dict(ship, rcs=[{k: v for k, v in e.items() if not k.startswith('installed_')} for e in ship.get('rcs', [])],
                      torch=[{k: v for k, v in e.items() if not k.startswith('installed_')} for e in ship.get('torch', [])])
    bm, bc, bi = mass_properties(no_install, levels)
    mass_response = dict(start_mass_kg=m0, start_cg_m=c0.tolist(), start_inertia_kg_m2=i0.tolist(),
        end_mass_kg=end['mass_kg'], end_cg_m=end['cg_m'], end_inertia_kg_m2=end['inertia_kg_m2'],
        added_declared_engine_mass_kg=m0 - bm, engine_cg_delta_m=(c0 - bc).tolist(),
        engine_inertia_delta_kg_m2=(i0 - bi).tolist(),
        depletion_inertia_delta_kg_m2=(vec(end['inertia_kg_m2']) - i0).tolist(),
        missing_engine_masses=[eid for eid, v in inventory.items() if v['installed_mass_kg'] is None])
    if wayfarer:
        mass_response['legacy_aggregate_rcs_allocation_kg'] = sum(p['mass_t'] * 1000 for p in load(ROOT / GEOMETRY)['parts'] if p['system'] == 'rcs')
    complete_mass = not mass_response['missing_engine_masses'] and all(v['installed_inertia_kg_m2'] is not None for v in inventory.values())
    row('mass.installation_model', 'mass_propellant', len(mass_response['missing_engine_masses']), 0,
        [config_ev, CARD if wayfarer else hyp_ev],
        'Legacy aggregate RCS mass is not a per-engine/upgrade ledger; hardware centroids, tensors and attachments must be supplied.',
        status='PASS' if complete_mass else 'HOLD', scope='declared mass model only')
    row('mass.physical_inertia', 'mass_propellant', None, None, [PRIORITY, CARD] if wayfarer else [hyp_ev],
        'Rev7 S1/S4 tensor response is conditional; current complete-vehicle inertia is OPEN.' if wayfarer else
        'Declared fixture tensors exercise fuel and installation response; measured configuration-aware inertia and slosh/flux evidence is absent.')
    known_used = sum(tank_consumed.values())
    row('mass.known_ledger_closure_kg', 'mass_propellant', abs((m0 - end['mass_kg']) - known_used), 1e-5,
        [trace_ev, evidence['run']], 'Closure checks only modeled tank loss; missing propellant and installation mass are excluded.')
    missing_feed = [eid for eid, (kind, e) in engines.items() if e.get('tank') is None or
                    (exhaust_velocity(e) is None if kind == 'rcs' else any(exhaust_velocity(v) is None for v in e['modes'].values()))]
    row('feed.exhaust_and_source', 'mass_propellant', missing_feed, None, [config_ev, trace_ev, PRIORITY] if wayfarer else [config_ev, trace_ev],
        'Supply authorized exhaust speed/Isp, per-nozzle fuel identity and inlet/feed architecture; unknown consumption is null.',
        status='HOLD' if missing_feed else 'PASS', scope='declared fuel model only')
    tanks = {}
    for t in ship.get('tanks', []):
        tid = t['id']; cap = rating(assumptions.get('feed_ratings', {}), tid)
        tanks[tid] = dict(initial_kg=levels[tid], remaining_kg=end['tanks_kg'][tid],
            known_used_kg=tank_consumed[tid], requested_kg=tank_requested[tid], peak_flow_kg_s=tank_peak[tid])
        row('tank.' + tid + '.known_demand_kg', 'mass_propellant', tank_requested[tid], levels[tid], [config_ev, trace_ev],
            'Known assigned feed demand only; bulk storage does not select an RCS feed or prove delivered inlet state.')
        row('feed.' + tid + '.flow_kg_s', 'mass_propellant', tank_peak[tid], cap.get('peak_flow_kg_s'), [hyp_ev, trace_ev],
            'Scalar flow from declared exhaust speed; pump, pressure drop, fluid state and transient-duty integration need evidence.',
            scope='HYPOTHETICAL rating' if cap else 'physical evidence missing')
    # Protected water belongs to base mass in existing Wayfarer configs. The
    # assessor never creates or consumes a tank for it, even if RCS is unknown.
    protected = None
    if wayfarer:
        usable = load(ROOT / CARD)['fluids']['remass_t'] * 1000
        protected_kg = load(ROOT / CARD)['fluids']['protected_water_t'] * 1000
        def is_protected(t):
            label = (t['id'] + ' ' + t.get('fuel_source', '')).lower()
            return t.get('protected', False) or 'protected' in label or 'reserve' in label
        tank_by_id = {t['id']: t for t in ship.get('tanks', [])}
        forbidden = [e['id'] for _, e in engines.values() if e.get('tank') and is_protected(tank_by_id[e['tank']])]
        excess = sum(t['capacity_kg'] for t in ship.get('tanks', []) if t['id'] == 'remass') - usable
        assigned_protected = {e['tank'] for _, e in engines.values() if e['id'] in forbidden}
        protected_allocation = sum(tank_by_id[tid]['capacity_kg'] for tid in assigned_protected)
        unknown_extra = [t['id'] for t in ship.get('tanks', []) if t['id'] != 'remass' and
                         not is_protected(t) and not t.get('fuel_source')]
        protected = dict(protected_water_kg=protected_kg, usable_remass_kg=usable,
                         engineering_reserve_kg=load(ROOT / GEOMETRY)['ledger_reserve_t'] * 1000,
                         forbidden_engine_assignments=forbidden,
                         unresolved_additional_tank_sources=unknown_extra,
                         accounting='50 t protected water remains in base; no RCS fuel authorization inferred')
        row('protected_water.excluded', 'mass_propellant', max(0., excess, protected_allocation), 0., [config_ev, CARD],
            'Protected 50 t cannot feed propulsion; additional tanks need explicit fuel_source provenance, and Q7 reserve is not a new tank.',
            status='FAIL' if forbidden or excess > 1e-6 else ('HOLD' if unknown_extra else 'PASS'),
            scope='configuration exclusion only; physical RCS consumption unresolved')

    for mid, m in sorted(mounts.items()):
        cap = rating(assumptions.get('mount_ratings', {}), mid)
        factor = cap.get('dynamic_factor')
        if factor is not None and (not math.isfinite(factor) or factor <= 0):
            raise ValueError('positive finite declared dynamic factor required')
        demand = m['peak_force_N'] * (factor if factor is not None else 1.)
        row('mount.' + mid + '.force_N', 'structure', demand, cap.get('force_N'), [trace_ev, hyp_ev],
            'Realized force at a common application point; declared dynamic factor applied only when supplied, no bracket stress inferred.',
            scope='HYPOTHETICAL force rating' if cap else 'time-step load demand; capacity unknown')
    row('structure.integration_and_life', 'structure', None, None, [hyp_ev, CERT] if wayfarer else [hyp_ev],
        'Supply bracket geometry/eccentricity, reinforcement/load path, fasteners, finite-temperature allowables, dynamic factors and fatigue duty; G5 longeron stress is inapplicable to local brackets.')

    plume = assumptions.get('plume', {})
    geometry = assumptions.get('geometry', {})
    envelopes = wayfarer_envelopes(geometry.get('deployment')) if wayfarer else geometry.get('sphere_envelopes', [])
    screen = dict(tested_firing_samples=0, minimum_clearance_m=None, witness=None,
                  envelope_count=len(envelopes), deployment=geometry.get('deployment'),
                  source=GEOMETRY if wayfarer else hyp_ev,
                  convention='exhaust opposite realized force, apex at configured application point; sphere exclusion envelopes')
    ready = all(plume.get(k) is not None for k in ('half_angle_deg', 'length_m')) and bool(envelopes)
    if ready:
        direction_cache = {}
        for t in trace:
            for s in t['engine_samples']:
                if s['actual_N'] <= 1e-9: continue
                e = engines[s['id']][1]
                key = (s['id'], *s['direction'])
                if key not in direction_cache:
                    direction_cache[key] = min((finite_cone_sphere_clearance(e['pos_m'], -vec(s['direction']), plume['length_m'],
                        plume['half_angle_deg'], envelope['center_m'], envelope['radius_m']), envelope['id']) for envelope in envelopes)
                distance, envelope_id = direction_cache[key]
                if screen['minimum_clearance_m'] is None or distance < screen['minimum_clearance_m']:
                    screen.update(minimum_clearance_m=distance, witness=dict(engine=s['id'], time_s=t['t_s'], envelope=envelope_id))
                screen['tested_firing_samples'] += 1
    row('plume.coarse_clearance', 'plume', None if screen['minimum_clearance_m'] is None else -screen['minimum_clearance_m'], 0., [trace_ev, screen['source'], hyp_ev],
        'No cone/deployment evidence supplied.' if not ready else 'Finite-cone exclusion-envelope screen; intersection rejects this stated coarse assumption, not proof of surface impingement.',
        status='HOLD' if screen['minimum_clearance_m'] is None else ('FAIL' if screen['minimum_clearance_m'] <= 0 else 'PASS'),
        scope='coarse geometry only; demand is signed penetration in metres (negative means separation)')
    row('plume.physical_clearance', 'plume', None, None, [hyp_ev, CERT] if wayfarer else [hyp_ev],
        'Require nozzle exit/apex geometry, measured divergence/finite plume length, exhaust composition, all deployment/door states, impingement and thermal-clearance evidence; axial Rev7 clearance is AWAITING.')

    for name, demand_key, cap_key in [('temperature_K', 'peak_K', 'rating_K'), ('rejection_W', 'load_W', 'capacity_W')]:
        values = [(eid, rating(assumptions.get('thermal', {}), eid)) for eid in engines]
        missing = [eid for eid, v in values if v.get(demand_key) is None or v.get(cap_key) is None]
        margins = [(v[cap_key] - v[demand_key], eid, v) for eid, v in values if v.get(demand_key) is not None and v.get(cap_key) is not None]
        worst = min(margins) if margins else None
        row('thermal.engine.' + name, 'thermal', None if worst is None else worst[2][demand_key],
            None if worst is None else worst[2][cap_key], [hyp_ev],
            ('Missing temperature/load/rating evidence for: ' + ', '.join(missing)) if missing else
            'Direct declared demand/rating comparison, worst engine ' + worst[1] + '; no temperature is inferred from thrust.',
            status='FAIL' if worst and worst[0] < 0 else ('HOLD' if missing else 'PASS'), scope='HYPOTHETICAL supplied thermal comparison')
    row('thermal.engine_life', 'thermal', None, None, [hyp_ev],
        'Supply cooling integration, erosion/nozzle wall histories, thermal cycling and endurance tests for this installed engine and duty.')

    torch_summary = dict(peak_jet_power_W=torch_power, jet_energy_J=total_energy,
                         peak_accel_g=torch_g, peak_actual_tvc_deg=torch_angle,
                         fired=any(v['kind'] == 'torch' and v['impulse_Ns'] > 0 for v in inventory.values()))
    for mode, utilization in torch_mode_ratios.items():
        row('torch.configured_mode_force.' + mode, 'torch', utilization, 1., [config_ev, trace_ev],
            'Actual thrust relative to this installed engine mode rating; power/crew caps may lower the force further.')
    if torch_summary['fired']:
        row('torch.integrated_energy_J', 'torch', total_energy, None, [trace_ev, config_ev],
            'Integrated jet energy from realized force and declared exhaust velocity; no installed fuel-energy/endurance capacity is supplied.')
    if wayfarer:
        card = load(ROOT / CARD); cert = load(ROOT / CERT)
        torch_summary['source_modes'] = card['torch']
        if torch_summary['fired']:
            for key, demand, cap in [('jet_power_W', torch_power, card['torch']['jet_power_ceiling_tw'] * 1e12),
                                     ('crew_g', torch_g, card['torch']['accel_cap_g']), ('structural_g', torch_g, 5.),
                                     ('actual_tvc_deg', torch_angle, card['torch']['tvc_authority_deg'])]:
                row('torch.' + key, 'torch', demand, cap, [trace_ev, CARD, REV7 + 'SPEC.md'],
                    'Rev7 scalar operating envelope only; declared hardware authority and full local load paths remain unverified.')
            trim = max(p['max_ideal_tvc_trim_deg'] for p in result['phases'])
            row('torch.trim_plus_assumed_error_deg', 'torch', trim + .5, card['torch']['tvc_authority_deg'],
                [evidence['run'], CERT + '#torch_tvc'], 'Ideal CG trim plus source assumed 0.5 degree disturbance; not a measured disturbance or nozzle test.')
            heat = next(g for g in cert['gates'] if g['gate'] == 'G4')
            budget = heat['torch_budget']
            for key, demand, capacity in [('hot_fins_W', budget['ship_heat_gw'] * 1e9, heat['hot_fin_capacity_gw'] * 1e9),
                                          ('strakes_W', (budget['cryo_reject_mw'] + .37) * 1e6, heat['torch_strake_capacity_mw'] * 1e6),
                                          ('reactor_face_W_m2', budget['wall_flux_mw_m2'] * 1e6, 10e6)]:
                row('torch.declared_heat.' + key, 'torch', demand, capacity, [CERT + '#G4'],
                    'Full Rev7 heat-package design comparison, requiring 28 m hot fins at 1750 K and 4 m strakes at 1300 K; flight trace does not measure these loads.',
                    scope='legacy PASS-DECLARED design budget only')
        else:
            row('torch.flight_loads', 'torch', None, card['torch']['jet_power_ceiling_tw'] * 1e12, [trace_ev, CARD],
                'Torch did not fire in this maneuver; run burn120 for the sourced operating-load comparison.')
        row('torch.physical_installation', 'torch', None, None, [CERT, PRIORITY],
            'Require selected feed hardware, verified jet/heat partition, cooling/deployment and finite-temperature endurance, loaded TVC angle/rate and constituent-property evidence.')
    row('physical_evidence.acceptance', 'evidence', None, None, [hyp_ev, CERT] if wayfarer else [hyp_ev],
        'No independently validated supplier, material, assembly, acceptance or installed-duty test evidence is admitted; declarations cannot issue a hardware certificate.')

    legacy = None
    if wayfarer:
        cert = load(ROOT / CERT)
        legacy = dict(certified=cert['certified'], evidence=CERT,
            gates={g['gate']: g['verdict'] for g in cert['gates']},
            awaiting=[d['key'] for d in cert['declared_for_kT'] if d['kT'] == 'AWAITING'],
            recovered_priority=dict(evidence=PRIORITY, mounting='ENGINEERING_CANDIDATE_NON_CANON',
                feed='NOT SELECTED', complete_inertia='WAYFARER_INERTIA_OPEN_NOT_QUALIFIED',
                relation='separate current priority; Rev7 conditional tensor is not current rotational authority'))
    return dict(scope='NON-CANON hardware assessment; PASS/FAIL only for each stated numerical requirement',
        hardware_qualified='HOLD', hardware_certificate=False,
        reason='Independent physical evidence is missing; supplied declarations and numerical passes cannot certify hardware.',
        ship=ship['name'], experiment=experiment.get('name'), evidence=evidence,
        input_hashes=dict(ship=result['ship_sha256'], experiment=result['experiment_sha256'], assumptions=source_hash(assumptions)),
        counts=dict(Counter(r['status'] for r in rows)), requirements=rows,
        installation=list(inventory.values()), mounts=mounts, mass_response=mass_response,
        propellant=dict(total_used_kg=None if unknown_flow else known_used, known_used_kg=known_used,
            peak_total_flow_kg_s=None if unknown_flow else peak_flow, known_peak_flow_bound_kg_s=peak_flow,
            unknown_nozzles=sorted(unknown_flow), tanks=tanks, protected_reserve=protected),
        loads=dict(peak_resultant_average_N=force_peak, peak_moment_about_cg_average_Nm=moment_peak,
            peak_scalar_force_bound_N=force_bound, peak_scalar_moment_bound_Nm=moment_bound,
            scope='time-step averages plus actuator-endpoint force envelope; no ignition shock, flex or bracket bending model'),
        turns=turns, saturation=[{k: p[k] for k in ('kind', 'allocation_limit_steps', 'slew_limit_steps', 'thrust_limit_steps', 'gimbal_limit_steps', 'minimum_allocated_fraction')} for p in result['phases']],
        gimbal_initialization=result['gimbal_initialization'], plume_screen=screen, torch=torch_summary, legacy=legacy)


def assess_files(shipfile, expfile, dest, assumptionsfile=None, resultfile=None, dt=.02):
    dest = Path(dest).resolve()
    if not dest.is_relative_to(ROOT) or dest.is_relative_to(ROOT / 'source'):
        raise ValueError('output must remain in scratch workspace, outside source/')
    tag = Path(shipfile).stem + '__' + Path(expfile).stem
    if resultfile is None:
        save_run(shipfile, expfile, dest / 'runs', dt, .1)
        resultfile = dest / 'runs' / (tag + '.json')
    resultfile = Path(resultfile)
    tracefile = resultfile.with_suffix('.rcs_trace.json')
    def relative(p):
        p = Path(p).resolve()
        return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
    evidence = dict(config=relative(shipfile), experiment=relative(expfile), run=relative(resultfile),
                    trace=relative(tracefile), assumptions=relative(assumptionsfile) if assumptionsfile else 'not supplied')
    report = assess(load(shipfile), load(expfile), load(resultfile), load(tracefile),
                    load(assumptionsfile) if assumptionsfile else None, evidence)
    report['evidence_sha256'] = {relative(p): hashlib.sha256(Path(p).read_bytes()).hexdigest()
                               for p in (shipfile, expfile, resultfile, tracefile, assumptionsfile,
                                         ROOT / 'hardware_assess.py', ROOT / 'flightlab.py', ROOT / 'lab.py') if p}
    path = dest / (tag + '.assessment.json')
    write_json(path, report)
    print(f'{tag}: hardware=HOLD; {report["counts"]}; {relative(path)}', flush=True)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('ship', nargs='?'); p.add_argument('experiment', nargs='?')
    p.add_argument('--assumptions'); p.add_argument('--result', help='existing current lab.py run JSON; matching .rcs_trace.json required')
    p.add_argument('--out', default='hardware_results'); p.add_argument('--dt', type=float, default=.02)
    p.add_argument('--examples', action='store_true', help='exercise the four installations plus baseline 10 s, cold-start and torch auxiliary runs')
    args = p.parse_args()
    if args.examples:
        cases = [('baseline25', 'reference_baseline25_40s', 'reference_baseline25_40s', None),
                 ('baseline25_10s', 'reference_baseline25_10s', 'reference_baseline25_10s', None),
                 ('fixed300', 'reference_fixed300_pitch', 'reference_fixed300_pitch', None),
                 ('gimbals_prepositioned', 'wayfarer_gimbal_reference', 'gimbal12', None),
                 ('gimbals_cold', 'wayfarer_gimbal_cold', 'gimbal12', None),
                 ('scout_hypothetical', 'hardware/fixtures/scout_hardware', 'scout_gimbal_turn', 'hardware/fixtures/scout_ratings.json'),
                 ('torch_CRUISE', 'wayfarer', 'burn120', None)]
        comparison = []
        for label, ship, exp, assumption in cases:
            shipfile = ROOT / (ship + '.json') if '/' in ship else ROOT / 'configs' / (ship + '.json')
            r = assess_files(shipfile, ROOT / 'experiments' / (exp + '.json'), args.out,
                             ROOT / assumption if assumption else None, dt=args.dt)
            turn = r['turns'][0] if r['turns'] else {}
            comparison.append(dict(case=label, hardware='HOLD', counts=r['counts'],
                target=turn.get('at_target_time'), gate_entry_s=turn.get('gate_entry_s'),
                peak_mount_N=max(m['peak_force_N'] for m in r['mounts'].values()),
                propellant_kg=r['propellant']['total_used_kg'],
                peak_resultant_N=r['loads']['peak_resultant_average_N'],
                assessment=str(Path(args.out) / (shipfile.stem + '__' + exp + '.assessment.json'))))
        write_json(Path(args.out) / 'comparison.json', comparison)
        lines = ['| Case | Target error, deg | Target rate, deg/s | Final gate, s | Peak common mount, kN | Fuel, kg | Hardware |',
                 '|---|---:|---:|---:|---:|---:|---|']
        for c in comparison:
            target = c['target'] or {}
            def number(v): return 'unknown' if v is None else f'{v:.9g}'
            lines.append('| ' + ' | '.join([c['case'], number(target.get('attitude_error_deg')),
                number(target.get('rate_deg_s')), number(c['gate_entry_s']), number(c['peak_mount_N'] / 1000),
                number(c['propellant_kg']), 'HOLD']) + ' |')
        # Parent and resolved path were checked by write_json immediately above.
        (Path(args.out) / 'comparison.md').write_text('\n'.join(lines) + '\n')
    elif args.ship and args.experiment:
        assess_files(args.ship, args.experiment, args.out, args.assumptions, args.result, args.dt)
    else:
        p.error('supply ship and experiment, or --examples')


if __name__ == '__main__':
    main()
