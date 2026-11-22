"""Specialist families and the FTL daughtercraft: smallest supporting numbers. ALL bodies. ALL sponsors. 2026-2226.
Uses the explorer engine (same models) plus CANON II v2.5 constants. Non-canon screen."""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'explorer'))
import engine as E
out = {}
# 1. Vacuum-only utility craft: B5 core without wings, fans, floats, desal and entry TPS (never enters an atmosphere)
p = dict(E.B5, wing='none', fan_m2=0, floats_m3=0, desal=False)
r = E.evaluate(p); m = r['mass_t']
vac_dry = r['dry_t'] - m['entry_tps']
pay = 2.6
def dv(dry, water, ve=50.0): return ve * math.log((dry + pay + water) / (dry + pay))
out['vacuum_utility'] = dict(dry_t=round(vac_dry, 2), basis='B5 core minus wings, fans, floats, desal, entry TPS (hull kept)',
    dv_kms_23t_ve50=round(dv(vac_dry, 23.1), 1), moon_round_trip_water_t=E.water_chk(vac_dry, pay, [(1900, 1.0, 1.62), (1900, 1.4, 1.62), (400, .1, 1)])[0],
    europa_round_trip_water_t=E.water_chk(vac_dry, pay, [(1500, 1.0, 1.31), (1500, 1.4, 1.31), (400, .1, 1)])[0])
# 2. Independent interplanetary courier: B5 with a full tank, top exhaust speed 25/50/100 km/s (step 2 projection range)
b5 = E.evaluate(dict(E.B5))
out['interplanetary_courier'] = dict(dry_t=b5['dry_t'], dv_kms={f've{v}': round(dv(b5['dry_t'], 23.1, v), 1) for v in (25, 50, 100)},
    note='impulsive budget with the 23.1 t tank; slow (months) transfers fit, Wayfarer-class transit (hundreds of km/s) does not; the 3-day hop cabin, consumables and radiation, not propulsion, limit range')
# 3. FTL daughtercraft (Loom), from CANON II v2.5
plant_t, mc_kg, mc_flow_kg_yr = 88.0, 10.0, 1200.0
dc = dict(relational_plant_t=plant_t, mc_kg=mc_kg, share_of_world_serviceable_mc_per_year_pct=round(100 * mc_kg / mc_flow_kg_yr, 2),
          cryo='150 kW-class at 20 K; metric NORMAL needs 3.5 MW cryo electrical and 106 m2 of 900 K radiator (HARD 23.9 MW, 719 m2)',
          shared_bank='2 GJ reversible field bank', nodes=208, loom_boundary_m2='~1,900 normal for the reference courier',
          momentum_matching='ordinary torch / external exchange (needs its own torch and remass)',
          rarity='Loom-capable ships: a few dozen worldwide (CANON I 2.2, 5.4)')
# daughtercraft mass estimate (ASSUMPTION): plant + torch + structure/hab/thermal + momentum-matching water
for label, struct in (('lean', 60.0), ('practical', 110.0)):
    dry = plant_t + 7.0 + struct; water = dry * (math.exp(20.0 / 50.0) - 1)      # 20 km/s matching budget at ve 50 (assumption)
    dc[f'{label}_dry_t'] = round(dry); dc[f'{label}_wet_t'] = round(dry + water)
WET_S1, DRY_S1 = 1167.532686975091, 1167.532686975091 - 245.39043171108221
for label in ('lean', 'practical'):
    wet = dc[f'{label}_wet_t']
    dc[f'{label}_wayfarer_econ_dv_kms'] = round(3000 * math.log((WET_S1 + wet) / (DRY_S1 + wet)), 1)
dc['wayfarer_econ_dv_today_kms'] = round(3000 * math.log(WET_S1 / DRY_S1), 1)
dc['verdict'] = ('Not a shuttle: the only certified relational plant is ~88 t with 10 kg Mc; canon gives no smaller design and calls the '
                 'legacy smaller sizings non-governing. A daughtercraft is a second Loom-capable ship (~0.2-0.3 kt), too big for any bay option; '
                 'carried externally it costs Wayfarer ~18-23% of ECON delta-v and joins Wayfarer\'s Loom domain (configuration lock). '
                 'Plausible as a separate second ship acquired in play, not as Wayfarer equipment.')
out['ftl_daughtercraft'] = dc
# 4. Metric-assisted landing / manoeuvre ("tic-tac")
out['metric_manoeuvre'] = dict(verdict='Blocked by canon', reasons=[
    'metric is long-baseline: one NORMAL ramp is ~0.40 million km of metric path (CANON II 9.1); Earth-Moon cannot fit a full cycle (9.3)',
    'metric is not a close-combat dodge; torch owns tactical vector change (18A)',
    'wake used as commandable reactionless thrust is a hard kill (21); FTL metric is a hard kill (5)',
    'the plant is ~88 t and shared with Loom (3)'],
    closest_legal='Osteon-light airframe + full-power torch with steerable magnetic nozzle (T/W up to ~2.5) and quiet electric fans; agile but never invisible: sensor primacy (18A) applies')
json.dump(dict(header='ALL bodies. ALL sponsors. 2026-2226.', model_version=E.MODEL_VERSION, results=out), open(os.path.join(HERE, 'families.json'), 'w'), indent=1)
print(json.dumps(out, indent=1)[:3000])
