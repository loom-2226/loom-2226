"""Weave manoeuvring - operations model: module scale, cold budget, frost charges, cooldown, bank-paid height, mission closure.
NON-CANON prototype lane (rules W1-W4 in weave_cycle.py). ALL bodies. ALL sponsors. 2026-2226.
Labels: CANON (cited), BASELINE (Weave engineering doc), CANDIDATE (L^2 size law, CANON II §6.2 'candidate fit, not canon'),
ASSUMPTION (lane value, editable), UNKNOWN (left open)."""
import sys, os, json, math, io, contextlib
H = os.path.dirname(os.path.abspath(__file__)); X = os.path.join(H, '..', 'exp2'); sys.path.insert(0, X); sys.path.insert(0, os.path.join(H, '..', '..', 'explorer'))
with contextlib.redirect_stdout(io.StringIO()):
    import exp2_w1 as W1X            # adds fold / camber wildcards
    import exp2_w2 as W2X            # departure scenario model
import engine as E
G = 9.81
# ---------------------------------------------------------------- CANON anchors (CANON II §3, §5)
CANON = dict(plant_t=88.0, mc_kg=10.0, nodes=208, bank_GJ=2.0, cryo_lift_kW=150.0,
             card={'NORMAL': (0.268, 10, 20.0, 3.5, 106), 'FAST': (0.437, 12, 38.1, 6.7, 202), 'EXPEDITE': (0.519, 15, 63.5, 11.2, 336), 'HARD': (0.595, 30, 136.0, 23.9, 719)})
W_PER_W = 3.5e6 / 20e3                                    # cryo electrical per watt of 20 K cold load (NORMAL card): 175
ramp_cold_MJ = {k: round(v[2] * v[1] / 1e3, 2) for k, v in CANON['card'].items()}   # cold load x ramp time (Wayfarer)
# ---------------------------------------------------------------- shuttle module, L^2 CANDIDATE (envelope 284 m^2 vs 1,900 m^2)
f = 284 / 1900
MOD = dict(fraction=round(f, 3), plant_t=round(88 * f, 1), mc_kg=round(10 * f, 2), nodes=round(208 * f), bank_GJ=round(2 * f, 2),
           cryo_lift_kW=round(150 * f, 1), cryo_electric_MW=round(150 * f * 1e3 * W_PER_W / 1e6, 2),
           hot_side='atmosphere: air heat exchanger, full cryo rate; vacuum: radiator-limited [ASSUMPTION]', label='CANDIDATE (L^2 is not canon)')
RAD_VAC_M2 = 16.0                                          # shuttle radiator for vacuum ops [ASSUMPTION ~ L^2-scaled NORMAL area]
reject_vac_W = RAD_VAC_M2 * 0.9 * 5.67e-8 * 900 ** 4
lift_vac_kW = reject_vac_W / (W_PER_W + 1) / 1e3
# ---------------------------------------------------------------- cold budget per dash [ASSUMPTION anchored to CANON ramp cold energies x scale x environment]
Q = dict(low=0.25, central=1.0, high=4.0)                  # MJ at 20 K per dash (shuttle, near-body, sub-second)
Q_basis = 'Wayfarer certified ramps deposit %s MJ cold (NORMAL..HARD, CANON II §5). x%.2f for domain size, x3-10 for near-body correction (CANON II §6.3, unquantified) -> 0.25-4 MJ.' % (ramp_cold_MJ, f)
BUFFER_MJ = 1.5                                            # allowable node-structure heat before HOLD (ASSUMPTION: ~1 central dash)
LH2_LATENT = 0.446                                         # MJ/kg at ~20 K (physical constant)
CHARGE_LH2_KG, CHARGE_DRY_KG = 3.0, 3.0                    # one frost charge [ASSUMPTION]
N_CHARGES = 12
def ops(q):
    per_charge = CHARGE_LH2_KG * LH2_LATENT / q
    return dict(Q_dash_MJ=q, free_dashes_from_buffer=round(BUFFER_MJ / q, 1), dashes_per_frost_charge=round(per_charge, 2),
                dashes_from_12_charges=round(N_CHARGES * per_charge + BUFFER_MJ / q, 1),
                cooldown_per_dash_s_air=round(q * 1e6 / (MOD['cryo_lift_kW'] * 1e3)), cooldown_per_dash_s_vacuum=round(q * 1e6 / (lift_vac_kW * 1e3)))
cold = {k: ops(v) for k, v in Q.items()}
# ---------------------------------------------------------------- bank-paid height (rule W2) and reactor-sustained climb
fans_MWe = 29.4
height = {}
for body, g in (('Earth', 9.81), ('Mars', 3.71), ('Titan', 1.352), ('Moon', 1.62)):
    m = 61e3
    height[body] = dict(bank_only_height_m=round(MOD['bank_GJ'] * 1e9 / (m * g)), reactor_climb_ms=round((fans_MWe - MOD['cryo_electric_MW']) * 1e6 / (m * g), 1),
                        descent_absorb_MJ_per_100m=round(m * g * 100 / 1e6, 1))
# ---------------------------------------------------------------- manoeuvre card (rules W1-W4)
card = [
 dict(move='Dash (level)', energy='free (ENERGY-B, partner frame)', cold='Q_dash', other='wear; WCS may return infeasible near terrain', looks='no plume, no g; boundary/air effect UNKNOWN (H1 bang / H2 bang or silent / H3 vacuum only)'),
 dict(move='Stop (end of dash)', energy='free: the ship never gained kinetic speed', cold='included in dash', other='-', looks='dead stop'),
 dict(move='Hover', energy='holding power only', cold='hold load (UNKNOWN; air: cryo keeps up; vacuum: radiator-limited)', other='-', looks='~%.1f MW of waste heat' % MOD['cryo_electric_MW']),
 dict(move='Climb', energy='paid m g h from bank, then reactor', cold='hold + correction', other='bank covers ~%d m on Earth' % height['Earth']['bank_only_height_m'], looks='silent rise'),
 dict(move='Descend', energy='returns m g h: arrive faster (ENERGY-B) or absorb into bank', cold='-', other='absorbing needs bank headroom', looks='silent drop'),
 dict(move='Change real velocity', energy='NOT by Weave (rule W3): torch or fans', cold='-', other='keeps the torch economy intact', looks='torch plume'),
 dict(move='Dodge', energy='dash', cold='Q_dash dumped into a frost charge', other='charge vented / ejected', looks='brief cold vapour puff; optional glowing decoy brick'),
 dict(move='Cooldown', energy='-', cold='cryo removes heat', other='air ~%d s per central dash; vacuum ~%d s' % (cold['central']['cooldown_per_dash_s_air'], cold['central']['cooldown_per_dash_s_vacuum']), looks='radiators hot / heat exchanger plume'),
]
# ---------------------------------------------------------------- mission closure: hot extraction with the module aboard (reuse experiment-2 departure model)
VEH = dict(W1X.G2643, wildcard='osteon_cautious+fold+camber', span=17.0, chord=1.8, water_t=18.0)   # leading adaptive shuttle (variant E)
mod_total = MOD['plant_t'] + N_CHARGES * (CHARGE_LH2_KG + CHARGE_DRY_KG) / 1e3 + 0.5         # + hot-side exchanger [ASSUMPTION 0.5 t]
closure = {}
for label, mt in (('no module', 0.0), ('L^2 Weave module %.1f t' % mod_total, mod_total), ('half-mass module %.1f t' % (mod_total / 2), mod_total / 2)):
    rows = {}
    for nm, ng, h, tw in (('torch lift-off', 0, 0, 2.5), ('Weave lift to 200 m', 0.25, 200, 2.0), ('Weave lift to 2 km', 0.25, 2000, 1.4)):
        s = W2X.scenario(nm, VEH, ng, h, tw, mod_t=mt, eta=0.9, E_est=0.0, P_up=MOD['cryo_electric_MW'] * 1e6)
        rows[nm] = dict(dry_t=s['dry_t'], storage_t=s['storage_t'], water_need_t=s['hot_water_t'], carried_t=s['carried_t'], thrust_short=s['thrust_short'], closes=bool(s['water_ok'] and not s['thrust_short'] and s['dry_ok']))
    closure[label] = rows
ceiling = {}
for nm, ng, h, tw in (('Weave lift to 200 m', 0.25, 200, 2.0), ('Weave lift to 2 km', 0.25, 2000, 1.4)):
    best = None
    for mt in [x * 0.5 for x in range(0, 41)]:
        s = W2X.scenario(nm, VEH, ng, h, tw, mod_t=mt, eta=0.9, E_est=0.0, P_up=MOD['cryo_electric_MW'] * 1e6)
        if s['water_ok'] and not s['thrust_short'] and s['dry_ok']: best = mt
        else: break
    ceiling[nm] = best
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) Weave manoeuvring - operations', model_version=E.MODEL_VERSION,
           canon_anchors=dict(plant=CANON, ramp_cold_MJ=ramp_cold_MJ, cryo_W_per_W=W_PER_W), module=MOD, vacuum_cryo_lift_kW=round(lift_vac_kW, 2),
           cold_budget=dict(basis=Q_basis, buffer_MJ=BUFFER_MJ, frost_charge=dict(lh2_kg=CHARGE_LH2_KG, dry_kg=CHARGE_DRY_KG, absorbs_MJ=round(CHARGE_LH2_KG * LH2_LATENT, 2), carried=N_CHARGES), cases=cold),
           height=height, manoeuvre_card=card, hot_extraction_closure=closure, module_ceiling_t=ceiling,
           wear='Mc tile wear per dash UNKNOWN; shuttle tiles are its own (1.5 kg CANDIDATE); Wayfarer\'s tiles are shared with Loom (CANON II §3). Track as campaign wear points, not invented numbers.')
json.dump(out, open(os.path.join(H, 'weave_ops.json'), 'w'), indent=1)
if __name__ == '__main__':
    print(MOD, 'vacuum lift kW', round(lift_vac_kW, 2)); print(ramp_cold_MJ); print(json.dumps(cold, indent=0)); print(height)
    for k, v in closure.items(): print(k, v)
    print('ceiling', ceiling)
