"""Bottom-up mass estimate of the radiator manifold for the existing arrangement (Sol review of PR #557).
NON-CANON research screen. ALL bodies. ALL sponsors. 2026-2226.

Arrangement (existing): four 1,300 K accordion strakes, x 14-32.3, on 40/140/220/320 deg, fed by pumped
loops from the manifold ring (x 32.3-34.3) and fore heat sources. Hot fins have their own 4 x 1 t root loops
(hotfin_root_*), NOT counted here. The plant's 900 K hot-end exchanger (3 t, plant-booked, move HELD) is NOT counted.
Duty comes from the operating-state ledger (results/out/ship_power_budget.json), not from capacities.
Metric HARD is taken at the 4 m strake span kT approved on 2026-11-16 (2 m cannot reject 57 MW).

Every range is an ASSUMPTION (Claude). Uniform sampling. Writes manifold_bottom_up.json."""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, '..', '..')
I = json.load(open(os.path.join(W, 'config', 'wayfarer_v05_inputs.json')))
PB = json.load(open(os.path.join(W, 'results', 'out', 'ship_power_budget.json')))
ST = {s['state']: s for s in PB['states']}
R = I['radiators']

duty = {k: ST[k]['heat_rejected_mw'] for k in ('pulsed_torch_burn', 'Metric_HARD', 'fast_40s_flip', 'one_unit_failed_torch_magnets')}
Q = max(duty.values())                      # 66.134 MW worst modelled simultaneous load (torch burn)
N_LOOP = len(R['azimuths_deg'])             # one pumped loop per strake
Q_LOOP = Q / (N_LOOP - 1)                   # one loop/strake lost: the other three carry it (G4 strake-lost)
CHORD = R['x_m'][1] - R['x_m'][0]           # 18.3 m strake root

rng = np.random.default_rng(2026); S = 200000
U = lambda lo, hi: rng.uniform(lo, hi, S)
# lithium coolant near 1,300 K (PUBLISHED_PHYSICS, rounded)
CP, RHO = 4200.0, 470.0
dT = U(100, 200); v = U(2.0, 4.0)
mdot = Q_LOOP * 1e6 / (CP * dT)                         # kg/s per loop
d = np.sqrt(4 * mdot / (RHO * v) / math.pi)             # m inner diameter
L = (2 * CHORD + 2 * U(3, 6) + 2 * U(2, 5)) * U(1.1, 1.3)   # header pair + manifold feeders + fore branch, routing factor
p = U(0.5, 1.0) * 1e6; sig = U(20e6, 40e6)              # Pa design pressure; allowable creep stress, refractory alloy at ~1,300 K
t = np.maximum(1.5e-3, p * d / (2 * sig))
RHO_W = U(8570, 10200)                                  # Nb-1Zr .. Mo
pipe = N_LOOP * math.pi * d * t * RHO_W * L / 1e3       # t
li_pipe = N_LOOP * RHO * math.pi * d ** 2 / 4 * L / 1e3
insul = N_LOOP * L * U(2, 5) / 1e3
dp = U(0.2e6, 0.6e6); eta = U(0.2, 0.4)
pump_kwe = N_LOOP * (mdot / RHO) * dp / eta / 1e3
pumps = pump_kwe * U(1.0, 4.0) / 1e3                    # 1-4 kg per kWe EM pump incl. power conditioning
hx = Q * 1e3 * U(0.02, 0.08) / 1e3                      # source-side liquid-metal exchangers, kg/kW of duty
li_hx = hx * U(0.15, 0.3)                               # coolant hold-up in exchangers
roots = N_LOOP * U(0.1, 0.3)                            # header-to-strake heat-pipe interface blocks
valves = (pipe + pumps) * U(0.10, 0.20)                 # isolation, cross-connects, instrumentation
thaw = (pipe + li_pipe + pumps) * U(0.05, 0.10)         # accumulators, freeze/thaw trace heating (Li melts at 454 K)
struct = U(2.0, 6.0)                                    # canon II s13.2 load-transfer region for 4 strakes (to 7.5 g)
parts = dict(pipes=pipe, lithium=li_pipe + li_hx, insulation=insul, pumps=pumps, exchangers=hx, strake_root_interfaces=roots,
             valves_crossties=valves, accumulators_thaw=thaw, load_transfer_structure=struct)
transport = sum(parts.values()) * U(1.0, 1.25)          # immature-design growth

# Torch magnet cryocooler: 0.4755 MW at ~50 K lifted to 1,300 K at 25% of Carnot -> 47.52 MW input
# (torch_heat_inputs.json coil.prov; ship_power_budget). No mass booking found (Sol re-review of PR #557).
# Benchmark: the plant's 18 t 20 K cryoplant runs the same efficiency class (34.76 MW input for 136 kW at 20 K,
# 256 W/W = 25% of Carnot). Compressor-side hardware scales with INPUT power, so scale by input, not cold load
# (Sol: a 20 K cold-load benchmark does not transfer to 50 K coils). Range x0.8-1.1 for scale economy / 50 K cold end.
plant_in_mw, plant_t, cooler_in_mw = ST['Metric_HARD']['loads_mw']['scaled_cryo'], 18.0, 47.52
cooler_by_input = plant_t * cooler_in_mw / plant_in_mw
cooler = cooler_by_input * U(0.8, 1.1)

pc = lambda a: {k: round(float(np.percentile(a, q)), 2) for k, q in (('p5', 5), ('mid', 50), ('p95', 95))}
M0 = I['ledger']['thermal_radiators_t']
out = dict(
 header='ALL bodies. ALL sponsors. 2026-2226.',
 status='NON-CANON bottom-up screen; all ranges ASSUMPTIONS; nothing booked; savings credited 0 until reviewed',
 duty_mw=dict(states={k: round(v, 3) for k, v in duty.items()}, design=round(Q, 3), per_loop_one_lost=round(Q_LOOP, 3)),
 strake_span_hard_m=4, strake_span_hard_note='kT 2026-11-16: Metric HARD at 4 m (2 m rejects 36.75 MW < 57.01 MW)',
 loop=dict(coolant='lithium', dT_K=[100, 200], velocity_m_s=[2, 4], pipe_id_m=pc(d), run_per_loop_m=pc(L), wall_mm=pc(t * 1e3),
           pump_power_mwe=pc(pump_kwe / 1e3)),
 parts_mid_t={k: round(float(np.median(v)), 2) for k, v in parts.items()},
 transport_t=pc(transport),
 torch_cryocooler=dict(booked=False, t=pc(cooler), benchmark_input_scaled_t=round(cooler_by_input, 1), coil_temperature_K=50, carnot_fraction=0.25,
                       note='0.4755 MW at ~50 K, 47.52 MW input; ownership UNRESOLVED (manifold, nozzle, electrical all unsized; none names it); benchmark = plant 18 t cryoplant scaled by input power'),
 seed_manifold_t=M0,
 case_A_cooler_inside_manifold=dict(total_t=pc(transport + cooler), saving_t=pc(M0 - transport - cooler)),
 case_B_cooler_elsewhere_unbooked=dict(total_t=pc(transport), saving_t=pc(M0 - transport),
                                       warning='if the cooler is not in the 90 t, its owner is unknown; not declared a deficit (Sol: existing unsized allocations may contain it)'),
 not_counted=['hot-fin root loops (4 x 1 t, booked)', 'plant 900 K exchanger (3 t, plant, HELD)', 'strake panels (8.8 t, booked)',
              'habitat heat pump (~0.32 MWe, assumed in ECLSS)'],
 lever_not_counted='coils already modelled at ~50 K; a better cooler (>25% of Carnot) or less heat reaching the coils (shield transmission 1e-3) would shrink cooler and duty',
)
json.dump(out, open(os.path.join(HERE, 'manifold_bottom_up.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
