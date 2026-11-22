"""Reactorless Builder Tic Tac: one manoeuvre and its reverse (fiction-first, NON-CANON). ALL bodies. ALL sponsors. 2026-2226.

Hypothesis (kT/Sol, 2026-11-22): the continuous active hull is an M2-compatible interface to relational topography. It
alters the vehicle's ordinary motion by changing its relational configuration rho; the complete physical/relational system
changes correspondingly; local energy/thermal cost is NOT reactor accounting. Requirement: bounded flight behaviour without
free-work cycles. RT used as inspiration only (RT-C1 control geometry, RT-B1 route dependence, RT-D1/D3 common action).
No fuel substitute imposed by hand.

Minimal model. State: vehicle height h, speed v (ordinary physics); relational configuration rho (abstract; no units yet).
Operations:
  F(+d): field climb by d       F(-d): field descent by d (the exact reverse)
  X: field off, fall, and extract the fall energy with a turbine/brake (ordinary physics, any external work extraction)
Question: run F(+d), X, F(+d), X, ... Is the extracted work bounded, and what has not returned?
Two candidate laws for how F couples to rho:
  L0 (no ledger): F changes h and changes rho along a route, but rho's accessibility does not depend on the physical work done.
  L1 (ledger):    reachable rho depends on the physical record: F(+d) moves rho by dW/kappa where dW is the ordinary work
                  the field did on the vehicle (frame: the environment's rest frame); the range of rho is bounded, |rho| <= rho_max.
"""
import os, json
H = os.path.dirname(os.path.abspath(__file__))
m, g, d = 48.5e3, 9.81, 2000.0                     # Tic Tac (torchless mass from the ascent screen), one 2 km climb
dW = m * g * d
def cycle(law, n, kappa=1.0, rho_max=None):
    rho, W_out, log = 0.0, 0.0, []
    for k in range(n):
        if law == 'L0':
            rho = (rho + 1.0) % 1.0                    # any route; climb then field-free fall leaves rho re-usable (no record)
            W_out += dW
        else:
            if abs(rho + dW / kappa) > rho_max: log.append(f'cycle {k}: climb refused, rho would leave the accessible range'); break
            rho += dW / kappa; W_out += dW             # X dissipates/extracts the energy physically; rho keeps the record
        log.append(f'cycle {k}: extracted {W_out / 1e9:.2f} GJ, rho = {rho:.3g}')
    return W_out, rho, log
W0, _, _ = cycle('L0', 1000)
kappa = 1.0; rho_max = 2.0e12                          # illustrative: an accessible range worth 2 TJ of physical work
W1, rho1, log1 = cycle('L1', 10000, kappa, rho_max)
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__,
  manoeuvre_and_reverse=dict(
    field_up_then_field_down='h returns, v returns, rho returns, no heat required: fully reversible (both laws)',
    field_up_then_fall_and_brake='h returns, v returns, the environment holds the energy as heat/extracted work. Under L0 rho is re-usable: nothing records the work. Under L1 rho does NOT return: it holds the record of the work done'),
  L0_no_ledger=dict(extracted_after_1000_cycles_TJ=round(W0 / 1e12, 1), verdict='FREE-WORK CYCLE: unbounded extraction with the relational state reusable. Excluded by the requirement (and by sec. 7.3).'),
  L1_ledger=dict(extracted_TJ=round(W1 / 1e12, 2), cycles_before_refusal=len([l for l in log1 if 'extracted' in l]), final_rho=rho1,
                 verdict='Bounded: total net work the vehicle can leave in the world is limited by the accessible range of rho; reversing by field restores rho exactly'),
  result=[
    'Theorem-like finding (for any restorable rho coupled to ordinary motion against an effectively infinite environment): '
    'excluding free-work cycles REQUIRES rho to carry a record that changes in exact proportion to the net ordinary work done, '
    'in the environment\'s rest frame. Whatever it is called (tension, debt, displacement), it is commensurate with joules at a '
    'fixed exchange rate kappa. That is forced by the no-free-work requirement, not added as fuel.',
    'It is not a reactor and not heat: climbing stores the work as a relational displacement; descending by field gives it back, '
    'cool. Only physical dissipation (falling and braking, aerobraking, drag) leaves rho displaced.',
    'Limits come from the ACCESSIBLE RANGE of rho (RT-C1 style control geometry), not fuel: she can hold up to kappa*rho_max of '
    'net ordinary work "on credit". Orbit (1.56 TJ) is a position in rho; landing by field returns it; aerobraking spends it.',
    'Route dependence (RT-B1): two routes to the same physical state can leave different rho if one dissipated on the way. '
    'That is the "what does not return".',
    'The ledger selects a frame (the environment\'s rest frame). Which environment is still undetermined: the partner question '
    'reappears as "in whose frame is the record kept", not as an energy source.'],
  open_gap='Restoring a displaced rho: if only the reverse field manoeuvre restores it, every aerobraked landing permanently '
           'consumes range (a finite lifetime budget). If the environment can restore it (relaxation), that process must itself '
           'be paid physically or it re-opens the free-work cycle. Nothing in RT decides which; this is the conceptual gap.',
  for_flight='Operating picture: she climbs and accelerates without propellant or reactor heat; she must come home by field '
             '(unwinding) to keep her range; every time she sheds energy into the world (aerobraking, braking, drag), that '
             'much range is spent until restored. Total range kappa*rho_max is the one Builder parameter.')
json.dump(out, open(os.path.join(H, 'builder_cycle_screen.json'), 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('L0_no_ledger', 'L1_ledger')}, indent=1)); print(log1[-1])
