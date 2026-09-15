# Wayfarer E1 Torch — Source, Energy, Thermal and Radiator Envelope v0.1

**Status:** WORKING ENGINEERING INTERFACE / NON-CANON / NON-HARDWARE-CERTIFICATION

Yes: E1 ultimately needs the radiator requirement sized. But radiator area is a **downstream consequence of earned vehicle heat deposition**, not a fraction of the 5–13 TW direct kinetic jet power chosen by convenience.

## Current authority

- four major radiator assemblies;
- 900 K high-drive reject interface;
- torch and high-metric operation mutually exclusive;
- direct kinetic jet power from the earned six torch cards.

Existing metric-drive equivalent radiator areas are not reused as a torch solution. Archived courier torch-deposition ppm, 50–60 GJ transient capacity, 1,600 m2 high-temperature area and 3,600–4,000 m2 total effective area remain sensitivity/history only until re-earned.

## Power chain

When the required physical inputs exist:

`P_source = P_jet / f_directed`

`P_driver = P_source / Q` when the applicable Q definition/value is supplied.

`m_source = P_source / specific_power` when source specific power is supplied.

`P_vehicle_deposition = P_source * f_vehicle_deposition`

No missing quantity receives a default.

## Radiator sizing

For an explicitly supplied vehicle heat-rejection load, radiator temperature and emissivity, the ideal emitting area is:

`A = P_reject / (epsilon * sigma * T^4)`

The executable T2 interface uses the current 900 K reject interface and requires emissivity explicitly. It reports total ideal emitting area and ideal area per each of the four radiator assemblies.

This is **not yet physical radiator geometry**. Physical sizing must additionally close view factors, two-sided versus one-sided emitting convention, coolant/transport temperature drops, manifold/plumbing losses, deployment/stowage, structural mass, micrometeoroid tolerance, plume interception and external clearance.

## What blocks a governing Wayfarer radiator area today

1. source directed fraction is OPEN;
2. vehicle deposition fraction and its photon/neutron/plasma/interception partition are OPEN;
3. radiator emissivity/material system is OPEN;
4. transient buffer credit is OPEN;
5. physical geometry/view factor/plume-clearance closure is OPEN.

Therefore T2 earns the **sizing equation and dependency chain**, not a fake square-metre answer.

## Why this matters

At terawatt jet powers, tiny deposition fractions dominate the thermal design. A 10 ppm deposition against a ~10 TW scale is ~100 MW scale before correcting for source directed fraction. That is why the archived ppm values are useful as sensitivity cases but cannot be promoted merely because they produce plausible radiator sizes.

## E1 closure rule

E1 may qualify this interface with the radiator area unresolved if all unresolved physical inputs remain explicit technology holds and no runtime behavior assumes a radiator area. A physical radiator design/freeze requires those inputs to be earned separately.
