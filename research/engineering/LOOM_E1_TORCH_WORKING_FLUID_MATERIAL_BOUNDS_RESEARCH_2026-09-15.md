# LOOM E1 Torch Working-Fluid / Material Bounds Research — 2026-09-15

Status: EXTERNAL_RESEARCH_SYNTHESIS / NON-CANON / NON-QUALIFICATION

## Purpose
Bound the open Wayfarer normal-remass working-fluid trade using real fusion-propulsion analogs without selecting a 2226 propellant or importing present-day performance as Wayfarer capability.

## Wayfarer requirement interface
The governed engineering lane currently requires 250 t normal remass, a mode span of about 1.136–284.025 kg/s, and effective exhaust velocity 300–3000 km/s. The protected 50 t water reserve is separate and may not be silently consumed to close normal remass.

## Research findings

### 1. Light propellant is the strongest topology analog
Princeton Satellite Systems' Direct Fusion Drive description states that propellant gases such as deuterium and helium can be introduced into a gas box, weakly ionized, heated by fusion products in the scrape-off-layer, and expelled through a magnetic nozzle. PSS also describes this as thrust augmentation: adding propellant trades exhaust velocity for thrust. NASA historical fusion-propulsion work likewise describes additional hydrogen reaction mass mixed with charged fusion plasma for thrust augmentation.

Implication for LOOM: a light hydrogenic/helium-class normal remass is the best-supported research topology ancestor for a continuously augmented magnetic-nozzle torch. This is NOT a Wayfarer propellant selection.

### 2. Magnetic-nozzle performance remains a first-order physical hold
NASA magnetic-nozzle studies identify plasma expansion/detachment from magnetic field lines as a major unresolved propulsion issue and explicitly call for experiments across propellant choice, density, magnetic field, velocity distribution, and injection. Historical experimental planning used helium initially and hydrogen later to mimic fusion exhaust plasma.

Implication: working-fluid selection cannot be separated from nozzle detachment, divergence, interception, ionization state, and energy-transfer efficiency.

### 3. Water is not supported as the default direct analog
The sources reviewed support gaseous/light propellant injection, particularly hydrogenic and helium-class species. They do not establish water/steam as the normal augmented propellant for PFRC/DFD-class magnetic-nozzle operation.

Implication: water-derived remass remains an engineering trade family, but there is no research basis here to promote it above the light-gas family. The protected Wayfarer water reserve remains firewalled.

### 4. High-Z / metallic remass carries materially different risks
Fusion-driven rocket concepts can use lithium in pulsed liner architectures, but that is a materially different source/remass topology from the steady FRC/direct-fusion direction. High-Z or metallic species therefore cannot be imported merely because they appear in another fusion-propulsion architecture.

Implication: metallic/high-Z remass stays HIGH_RISK for the current topology because radiation, deposition/erosion, activation, injection, and magnetic-nozzle behavior require separate closure.

### 5. The Wayfarer exhaust-velocity envelope is beyond the cited augmented DFD examples
PSS descriptions discuss augmented exhaust velocities in the tens of km/s; NIAC DFD work reports roughly 10,000 s specific impulse (~98 km/s effective exhaust velocity). Historical fusion concepts discuss hydrogen augmentation at >=10^4 s. Wayfarer requires 300–3000 km/s.

Implication: the real literature supports the topology of energy transfer to added light remass, but does NOT validate Wayfarer's velocity/flow envelope. That scale gap remains an explicit 2226 breakthrough requirement.

## Research-bounded ranking
1. LIGHT_HYDROGENIC_OR_HELIUM_CLASS — LEADING TOPOLOGY ANALOG; physical storage/feed/coupling not closed.
2. INERT_LIGHT_GAS_CLASS — USEFUL NOZZLE/PLASMA ANALOG; mission-scale storage and coupling not closed.
3. WATER_DERIVED — OPEN ALTERNATIVE; no reviewed DFD/PFRC basis for promotion to default.
4. METALLIC_OR_HIGH_Z — HIGH RISK / ARCHITECTURE-DEPENDENT; do not import from pulsed liner concepts.

## Required engineering closure before selection
- storage state, density, tankage volume and mass;
- conditioning, ionization and injection energy;
- feed pressure, response, stability and 284 kg/s peak delivery;
- fusion-product/remass energy-transfer efficiency by mode;
- magnetic-nozzle detachment/divergence/interception by species;
- erosion, deposition, permeation, embrittlement, corrosion and activation;
- center-of-mass migration across 250 t consumption;
- reserve isolation and fault containment;
- compatibility with aft shield, magnets, thermal hardware and thrust structure.

## Decision
RETAIN_LIGHT_HYDROGENIC_OR_HELIUM_CLASS_AS_LEADING_RESEARCH_ANALOG_ONLY.

No working fluid is selected or certified. No present-day DFD number is a Wayfarer input. Convergence raises research priority, not truth.

## Sources
- Princeton Satellite Systems, Direct Fusion Drive / Starfire technology overview and thrust-augmentation descriptions.
- Princeton Satellite Systems, Fusion-Enabled Pluto Orbiter and Lander, NIAC Phase I final report.
- NASA Technical Reports Server, Magnetic-Nozzle Studies for Fusion Propulsion Applications: Gigawatt Plasma Source Operation and Magnetic Nozzle Analysis.
- NASA historical fusion-propulsion studies describing hydrogen reaction-mass augmentation and magnetic-nozzle experiments.
- NASA Fusion Driven Rocket studies for contrast with pulsed lithium-liner architectures.
