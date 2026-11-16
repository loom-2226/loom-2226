"""Torch chain mass screen: re-size the 90 t radiator manifold to the duty it now carries.
NON-CANON research screen. ALL bodies. ALL sponsors. 2026-2226.

Why: the 90 t manifold is a seed ledger mass. The largest duty on record for the strake/manifold
system is v0.5.1, when ~387 MW of torch heat reached the ship and the strakes could open to 24 m
(radiators.torch_capacity_mw 387.7). kT's v0.5.2 torch-heat package (2026-10-25) sends the 1.40 GW of
hot-structure heat to the four 1,750 K hot fins on their own root loops (hotfin_root_*, 4 x 1 t), and the
strakes now run at 4 m in burns (73 MW) and 2 m in Metric. The manifold's duty fell ~4-5x.
Performance is untouched: jet power 11.361 TW, fins, strakes, shield, reactor, nozzle unchanged.

Mass model (ASSUMPTION, Claude): m(Q) = M0 * (f + (1 - f) * (Q / Q0) ** n)
  f  = share that does not scale with duty (headers, structure, redundancy, load-transfer region canon II s13.2)
  n  = scaling exponent of pumps, heat exchangers and piping with duty
Sampled uniformly; the saving quoted for booking is the p5 (conservative) value.
Writes manifold_resize_screen.json."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, '..', '..')
I = json.load(open(os.path.join(W, 'config', 'wayfarer_v05_inputs.json')))
PB = json.load(open(os.path.join(W, 'results', 'out', 'ship_power_budget.json')))

M0 = I['ledger']['thermal_radiators_t']                  # 90 t seed
Q0 = I['radiators']['torch_capacity_mw']                 # 387.7 MW, largest duty on record (v0.5.1)
Q_TORCH = PB['thermal']['torch_strake_capacity_mw']      # 73.0 MW: strakes at 4 m in burns (v0.5.2)
# Metric HARD: canon II s5 719 m2 at 900 K equivalent (~24 MW) + house-reactor waste (2 x 50 MW net at 75% direct
# conversion -> ~33 MW) + habitat: below the torch case, so the torch case sets the duty.
Q_METRIC = 719 * 0.9 * 5.670374e-8 * 900 ** 4 / 1e6 + 2 * 50 * (1 / 0.75 - 1) + 1.0
Q_DESIGN = [max(Q_TORCH, Q_METRIC), 1.35 * max(Q_TORCH, Q_METRIC)]   # +35% design margin at the top
F = [0.25, 0.50]
N = [0.60, 1.00]

rng = np.random.default_rng(2026); S = 200000
q = rng.uniform(*Q_DESIGN, S); f = rng.uniform(*F, S); n = rng.uniform(*N, S)
m = M0 * (f + (1 - f) * (q / Q0) ** n)
save = M0 - m
pc = lambda a: {k: round(float(np.percentile(a, p)), 2) for k, p in (('p5', 5), ('mid', 50), ('p95', 95))}
NACELLE_GAP = 4.69                                       # PR #556, Sol-reviewed, zero credits

out = dict(
 header='ALL bodies. ALL sponsors. 2026-2226.',
 status='NON-CANON research screen; mass model and ranges are ASSUMPTIONS; nothing booked',
 performance='unchanged: jet power 11.361 TW, ECON ve, fins 1,750 K, strake spans, shield, reactor, nozzle',
 manifold_seed_t=M0, duty_on_record_mw=Q0,
 duty_now_mw=dict(torch=round(Q_TORCH, 1), metric_hard=round(Q_METRIC, 1), design_range=[round(x, 1) for x in Q_DESIGN]),
 duty_ratio=round(Q_DESIGN[1] / Q0, 3),
 model='m = M0*(f + (1-f)*(Q/Q0)^n)', fixed_share=F, exponent=N, samples=S, seed=2026,
 manifold_after_t=pc(m), saving_t=pc(save),
 conservative_saving_t=round(float(np.percentile(save, 5)), 1),
 nacelle_gap_t=NACELLE_GAP,
 after_funding_nacelles_t=round(float(np.percentile(save, 5)) - NACELLE_GAP, 1),
 cross_check='after-resize specific mass ~0.4-0.8 kg/kW of duty for loops, pumps and HX without panels; same order as 2020s NEP heat-rejection trunk/HX studies (not a hardware qualification)',
 not_counted=['coil temperature 20 K -> 40-77 K would cut the 47.5 MW cryo duty further but may add coil mass',
              'electrical 49 t: sized to ~270 MW RCS peaks via flywheels; no clear slack',
              'reactor 85 t, nozzle 30 t: performance-linked, unsized; no defensible lever',
              'shield 45 t: protected'],
 open=['bottom-up manifold sizing (loops, pumps, HX, headers) to replace the seed', 'thermal transients after burns (fin-root soak)',
       'plant 900 K hot end moving into the manifold ring (approved direction, held) uses volume not new duty'],
)
json.dump(out, open(os.path.join(HERE, 'manifold_resize_screen.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
