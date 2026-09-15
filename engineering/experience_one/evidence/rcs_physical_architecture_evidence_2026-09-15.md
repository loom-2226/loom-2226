# E1 RCS physical architecture evidence — 2026-09-15

CLASS: ENGINEERING EVIDENCE
CANON: NO
HARDWARE QUALIFICATION: NO

## Purpose
Provide traceable evidence for the physical RCS architecture trade without promoting present-day demonstrator values into 2226 Wayfarer hardware specifications.

## Evidence anchors

### Electronically controlled variable-thrust liquid propulsion / movable pintle
ESA, *Promising early tests for variable-thrust landing engine* (2024): https://www.esa.int/Enabling_Support/Space_Transportation/Future_space_transportation/Promising_early_tests_for_variable-thrust_landing_engine

ESA reports a throttleable liquid propulsion demonstrator using electronically controlled valves and a movable pintle injector. The demonstrator was designed for a broad throttle range. This supports the existence of a controllable liquid-propulsion architecture family combining electronic valve control and variable injection geometry. It does **not** establish Wayfarer working fluid, thrust, MIB, response, life, or scale.

### Secondary-injection / fluidic thrust-vector control
NASA NTRS 19690045572, *Secondary-injection thrust vector control systems*: https://ntrs.nasa.gov/citations/19690045572

NASA NTRS 19730024028, *Omni-axis secondary injection thrust vector control system*: https://ntrs.nasa.gov/citations/19730024028

NASA NTRS 20060022557, *Design Enhancements of the Two-Dimensional, Dual Throat Fluidic Thrust Vectoring Nozzle Concept*: https://ntrs.nasa.gov/citations/20060022557

These establish secondary-injection/fluidic TVC as a real experimentally and analytically investigated mechanism family, including omni-axis control concepts and tested dual-throat nozzle concepts. They support retaining fluidic/secondary-injection vectoring in the Wayfarer trade. They do **not** establish compatibility with the eventual Wayfarer propellant cycle or the required 45-degree force cone.

### MIB and response are coupled propulsion/GNC quantities
NASA NTRS document 19720015146, section 4.1 *Pulsed Operation*: https://ntrs.nasa.gov/api/citations/19720015146/downloads/19720015146.pdf

The report explicitly describes minimum impulse bit as dependent on valve actuation time, supply/system response, reaction process time, and thruster design constraints, and discusses valve-command/delivered-impulse timing and rise time. Its particular historical thruster numbers are **not** Wayfarer requirements. The useful evidence is architectural: MIB and response cannot be selected independently of valve, feed, thruster physics, thermal state, and GNC.

## Governed interpretation
1. The compound coarse/fine mount remains a credible architecture family, not selected hardware.
2. Electronically controlled valves plus variable injection geometry are evidence-backed mechanisms worth trading.
3. Fluidic/secondary-injection TVC is evidence-backed and may avoid moving the whole engine, but its achievable vector cone and response must be demonstrated for the selected cycle.
4. Mechanical gimbal remains an allowed fallback; no evidence currently closes its required response/life for Wayfarer.
5. No cited source justifies inserting a Wayfarer working fluid, exhaust velocity, MIB, valve latency, cycle life, or vector slew value.
6. Therefore numerical hardware downselection remains blocked pending a governed extrapolation/model or recovered LOOM authority.
