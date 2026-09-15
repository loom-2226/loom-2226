# Wayfarer E1 Torch — Source, Energy and Thermal-Deposition Envelope v0.2

**Status:** WORKING ENGINEERING INTERFACE / NON-CANON / NON-HARDWARE-CERTIFICATION

E1 carries torch heat deposition forward as a **working output variable**. The torch layer does not require that deposited heat be rejected immediately by radiators.

## Current authority

- four major radiator assemblies exist in the vehicle grammar;
- 900 K is the current high-drive reject interface;
- torch and high-metric operation are mutually exclusive;
- direct kinetic jet power comes from the earned six torch cards.

Existing metric-drive equivalent radiator areas are not reused as a torch solution. Archived courier torch-deposition ppm, 50–60 GJ transient capacity, 1,600 m2 high-temperature area and 3,600–4,000 m2 total effective area remain sensitivity/history only until re-earned.

## Torch power chain

When the required physical inputs exist:

`P_source = P_jet / f_directed`

`P_driver = P_source / Q` when the applicable Q definition/value is supplied.

`m_source = P_source / specific_power` when source specific power is supplied.

`P_heat = P_source * f_vehicle_deposition`

`P_heat` is the torch layer's thermal output to the later ship-wide power/thermal architecture. No missing quantity receives a default.

## Downstream radiator sensitivity only

The implementation retains a radiator sensitivity helper so a later thermal architecture can evaluate an explicitly supplied heat-rejection load:

`A = P_reject / (epsilon * sigma * T^4)`

This is **not a requirement that P_heat == P_reject at the same instant**. Heat may later be transported, stored, recovered, reused or rejected according to the ship-wide energy/thermal architecture. Conservation must close over the complete duty cycle, but that closure is downstream of the torch layer.

Physical radiator sizing additionally requires view factors, emitting-surface convention, coolant/transport temperature drops, manifold/plumbing losses, deployment/stowage, structural mass, micrometeoroid tolerance, plume interception and external clearance.

## Open torch physical inputs

1. source directed fraction;
2. vehicle deposition fraction and photon/neutron/plasma/interception partition;
3. applicable source Q and source specific power;
4. source/field/shield lifetime behavior.

Radiator emissivity, thermal storage capacity and thermal disposal strategy are downstream thermal-system holds, not prerequisites for calculating torch heat deposition.

## E1 closure rule

E1 may qualify the torch interface with `P_heat` unresolved or parametrically evaluated provided unresolved physical inputs remain explicit technology holds and no runtime behavior silently assumes their values. The downstream power/thermal chain consumes `P_heat` later.
