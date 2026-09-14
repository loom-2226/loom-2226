# LOOM 2226 — E1 Electric-Sail / HERTS Propulsion Option v0.1

**Status:** ACTIVE E1 ENGINEERING WORKPLAN ADDENDUM / NON-CANON  
**Date:** 2026-09-15  
**Primary class:** `class:engineering`  
**Runtime effect:** none in this document  
**Canon effect:** none  
**Active engineering priority changed:** NO — RCS hardware/coupled-flight closure remains first  

## Purpose

Experience One must include a third ordinary-space propulsion option between local RCS maneuvering and the fictional torch/metric regimes:

**NASA-derived Electric Sail / Heliopause Electrostatic Rapid Transit System (HERTS) style solar-wind propulsion.**

The purpose is to give Wayfarer a low-thrust, propellantless ordinary-space cruise mode that does not consume torch remass and does not require metric transport.

This is an E1 propulsion-regime requirement, not a demand to interrupt the active RCS qualification lane.

## Provenance note

A search of current indexed `loom-2226/loom-2226` and `loom-2226/loom-research-lab` did not recover a preserved internal file explicitly named for HERTS, E-Sail, electric sail, or electrostatic sail. This addendum therefore does **not** claim recovery of an authoritative prior LOOM artifact.

It reconstructs the intended option from Kevin's stated prior design intent and NASA primary-source material, and records it now so it cannot fall out of the E1 plan again.

Primary external technical lineage:

- NASA/MSFC, **Heliopause Electrostatic Rapid Transit System (HERTS)**, NIAC Phase I/II work led by Bruce Wiegmann.
- NASA Technical Reports Server, **The Heliopause Electrostatic Rapid Transit System (HERTS) Design, Trades, and Analyses Performed in a Two Year NASA Investigation of Electric Sail Propulsion Systems**, NTRS 20170008977 / related 20170008928.
- NASA Technical Reports Server, **Electric Sail Propulsion for Deep Space Missions**, NTRS 20190032324.
- NASA/MSFC, **NASA Begins Testing of Revolutionary E-Sail Technology**.
- NASA Technical Reports Server, **Electric Sail Design Sensitivities**, NTRS 20240005161.

These sources are external established/research knowledge inputs. They do not promote a specific Wayfarer implementation to canon or engineering authority by themselves.

## Physical principle retained for E1

The E-Sail extracts momentum from the natural solar wind rather than expending onboard propellant.

The NASA HERTS concept uses multiple very long, positively biased conductive tethers. The electric fields around the tethers deflect solar-wind protons; the corresponding momentum exchange produces spacecraft thrust.

Engineering consequences retained for E1:

- onboard propellant/remass expenditure for the propulsion mechanism: **ZERO**;
- thrust source: solar-wind momentum flux;
- operation is heliosphere/environment dependent rather than a free-space constant-thrust engine;
- thrust direction is constrained relative to the solar-wind/Sun line rather than arbitrary like an ideal thruster;
- thrust is low and persistent rather than torch-like high acceleration;
- deployment state, tether attitude/spin, tether voltage/current, electron management, solar-wind state and tether health are first-class operating variables;
- this is conventional momentum exchange, not reactionless propulsion and not metric physics.

NASA HERTS reference concepts used approximately 10–30 km scale charged tethers and slow spacecraft rotation to maintain deployment. Those values are **research ancestry**, not automatically Wayfarer design values.

## E1 propulsion hierarchy

The E1 flight stack is amended to include four distinct propulsion/control regimes:

1. **RCS / local-flight control**  
   Proximity operations, docking, collision avoidance, attitude control, small translations and transition setup.

2. **E-Sail / HERTS-derived propellantless cruise**  
   Low-thrust ordinary-space cruise using solar-wind momentum; no torch remass consumption. Best suited to long-duration heliocentric transfer segments where deployment and solar-wind geometry permit useful thrust.

3. **Torch / remass propulsion**  
   High-acceleration ordinary-space propulsion with explicit remass depletion, feed, thermal, plume and structural consequences.

4. **Metric transport**  
   Separate fictional transport regime governed by metric-domain eligibility/certification and transition semantics.

These regimes must never be collapsed into one generic `drive_mode` calculation with hidden state changes.

## E1 sequencing

Current active sequence is explicitly preserved:

1. finish RCS hardware / actuator / plume / structural / coupled-flight closure;
2. qualify the E-Sail ordinary-space propulsion contract and mission-role envelope;
3. qualify torch spacecraft interfaces and remass/feed behavior;
4. close metric transition/domain behavior;
5. demonstrate deterministic regime handoffs across Navigator / GIS / HUD.

Documentation of the E-Sail requirement is bounded enabling work and does not preempt the active RCS engineering lane.

## Required E-Sail engineering closure for E1

E1 does **not** need a complete 2226 materials program for electrostatic tethers. It does need enough deterministic physics and hardware-state discipline to use the mode honestly in a Wayfarer mission.

Minimum closure:

### 1. Environmental force model

- heliocentric position and epoch;
- solar-wind radial velocity / density or a governed environmental approximation with uncertainty;
- electric-sail effective force model tied to tether bias and deployed geometry;
- radial-distance scaling appropriate to the adopted E-Sail model;
- explicit validity envelope and fail-closed behavior outside it.

### 2. Propulsion state

At minimum:

- `ESAIL_STOWED`
- `ESAIL_DEPLOYING`
- `ESAIL_DEPLOYED_UNCHARGED`
- `ESAIL_ACTIVE`
- `ESAIL_DERATED`
- `ESAIL_RETRACTING` if retraction is physically retained
- `ESAIL_FAULT`

No thrust may appear merely because a UI mode selector says E-Sail.

### 3. Deployment / geometry

The implementation must model or explicitly bound:

- tether count;
- tether deployed length;
- deployment plane and spin state if retained;
- keep-out envelope;
- relationship to RCS plumes, radiators, docking/launch hardware, torch nozzle/plume and metric-node hardware;
- tether severance/degradation state at the fidelity needed for E1.

Exact NASA HERTS tether count/length is not automatically adopted.

### 4. Force-vector authority

The model must preserve the basic HERTS/E-Sail fact that thrust direction is constrained by solar-wind geometry.

A preliminary research ancestry value of roughly a 30-degree steering cone may be used only as a candidate input until an E1 engineering model adopts and qualifies its own bound.

Navigator must not treat E-Sail as an arbitrary 3-axis thrust vector.

### 5. Power / charge management

E-Sail is propellantless, not power-free.

E1 must account for:

- tether high-voltage bias;
- electron-management hardware / current burden at the adopted model level;
- spacecraft electrical load;
- thermal burden where material;
- loss-of-power / loss-of-charge thrust collapse semantics.

### 6. Attitude / RCS coupling

E-Sail deployment and steering are configuration changes.

The model must specify:

- permitted RCS use while deploying/deployed;
- whether the slow spin/deployment architecture is retained, replaced or actively controlled;
- mass/CoM/inertia changes due to deployed tethers and deployment hardware where material;
- attitude-control interaction with the sail force and deployment geometry.

The currently qualified E1 RCS wet/docked tensor does not automatically remain the flight tensor in a deployed E-Sail configuration.

### 7. Astrodynamics

E-Sail propagation is continuous low-thrust ordinary-space dynamics.

Navigator/E1 must support:

- finite continuous acceleration rather than an impulsive burn substitute;
- force direction tied to the solar-wind frame;
- integration with solar gravity and other material forces;
- long-duration state propagation;
- deterministic handoff to/from RCS and torch regimes.

### 8. Operational exclusions / interlocks

Until separately qualified, E-Sail operation is presumptively unavailable during:

- docking/proximity operations;
- atmospheric operation;
- launch-bay deployment/recovery activity;
- torch firing;
- metric transition/transport;
- any geometry state where tether/radiator/RCS/metric hardware interference is unresolved.

A later qualification may relax these restrictions; E1 may not assume compatibility in advance.

## E1 mission-role requirement

E1 must expose the E-Sail as a real Navigator propulsion option where physically admissible.

A route/planning response should be able to distinguish at least:

- **RCS/local** — precise, small-delta-v maneuvering;
- **E-Sail** — remass-free but low-thrust and geometry/environment constrained;
- **Torch** — fast ordinary-space flight with remass/thermal cost;
- **Metric** — fastest/separate regime with metric certification constraints.

The purpose is not necessarily to make E-Sail optimal for Ceres → Neptune. The purpose is to make it a physically coherent alternative that Navigator can accept, reject or rank based on the actual mission state rather than because the mode was omitted from the model.

## Required Navigator/HUD semantics

Navigator owns deterministic route/trajectory calculation within the governed contract.

HUD/GIS presentation should eventually expose, without inventing authority:

- propulsion regime;
- E-Sail deployed/active state;
- solar-wind-relative thrust vector;
- instantaneous acceleration;
- expected long-duration transfer effect;
- electrical burden;
- zero onboard propellant/remass flow for E-Sail thrust;
- deployment/interlock restrictions;
- provenance/qualification status.

## Geometry and Shipyard impact

The E-Sail requirement is likely to require material changes to Wayfarer deployable-hardware design.

Affected consumers:

- deterministic Wayfarer geometry;
- mass / CoM / inertia model;
- RCS plume/interference model;
- radiator configuration;
- Computational Shipyard;
- semantic GLB / 3D representation;
- HUD local-flight visualization;
- metric-domain committed-configuration qualification.

Current compatibility state: `REVIEW_REQUIRED` / likely `ADAPTATION_REQUIRED` once a physical tether/deployer design is selected.

This does not invalidate the current RCS qualification work because E-Sail deployment is a distinct later configuration state.

## Does not establish

This addendum does not establish:

- final Wayfarer tether length/count/material;
- final E-Sail thrust level;
- a fixed 30-degree Wayfarer steering cone;
- a final solar-wind model;
- final deploy/retract architecture;
- final power-system design;
- canon adoption;
- compatibility with torch, radiator, metric or RCS hardware while deployed;
- that E-Sail is the preferred Ceres → Neptune route.

It establishes only that **E1 must include and eventually qualify a NASA/HERTS-derived propellantless solar-wind electric-sail propulsion option, after current RCS closure and before E1 propulsion-regime convergence is considered complete.**
