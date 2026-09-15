# Wayfarer E1 Primary Torch — Interface Contract v0.1

**Status:** WORKING ENGINEERING INTERFACE / NON-CANON / NON-HARDWARE-CERTIFICATION  
**Executable contract:** `src/wayfarer_e1_torch_interface.py`  
**Exact card source:** `src/wayfarer_torch_mode_cards.py`

## Boundary

This contract states what E1 may ask of the primary remass-consuming torch interface using already-earned vehicle/card authority. It deliberately does not manufacture a reactor, nozzle, shield, magnet, feed system or working-fluid selection.

## Required inputs

For ACTIVE operation:

- selected earned mode: `ECON | CRUISE | EXPEDITE | FAST | HARD | LIMIT`;
- current positive vehicle mass;
- current normal-remass inventory, bounded `0..250,000 kg`;
- protected-water inventory fixed at `50,000 kg` at this interface;
- torch state;
- high-metric active state.

OFF/SAFE operation carries no performance mode and returns zero thrust, mdot and direct kinetic jet power.

## Derived outputs

The exact card source supplies `mdot` and `ve`. The interface derives, rather than separately stores:

- `thrust = mdot * ve`;
- `direct_kinetic_jet_power = 0.5 * mdot * ve^2`;
- `acceleration = thrust / current_vehicle_mass`.

These are exact rational calculations in the executable interface. Rounded human-readable card values are presentation, not independent formal truth.

## Earned invariants

1. Normal torch remass cannot exceed the 250 t allowance.
2. The 50 t protected-water reserve is not normal torch remass.
3. ACTIVE torch and high-metric operation are mutually exclusive.
4. ACTIVE torch requires an earned performance mode and positive normal remass.
5. OFF/SAFE torch cannot carry an active performance card.

## Explicitly OPEN physical closure

The executable contract carries these fields as `None` unless a later governed increment supplies them:

- source directed fraction;
- fusion gain/Q;
- source specific power;
- neutron deposition fraction;
- photon deposition fraction;
- intercepted-particle fraction;
- nozzle efficiency;
- selected remass species;
- feed hardware.

Absence is meaningful. No value may be inferred from `None`, and no downstream calculation may silently substitute a convenient default.

## Power firewall

`direct_kinetic_jet_power_w` is the kinetic power in the directed exhaust represented by the earned card equations. It is **not** automatically:

- fusion source output;
- external driver/input power;
- onboard electrical load;
- vehicle waste heat.

Those relationships belong to T2 and require explicit physical-closure inputs.

## Qualification meaning

Passing this contract demonstrates that the E1 software/engineering interface preserves the earned torch cards, mass/remass boundary and operating exclusions. It does not demonstrate physical realizability of the 2226 reactor/nozzle hardware.

## Downstream revalidation

This is an executable propulsion-interface addition. Revalidate torch numerical/card tests, formal torch invariants, mission/remass consumers, and Pixel qualification before promotion. No campaign state or 3D geometry is mutated by this increment.
