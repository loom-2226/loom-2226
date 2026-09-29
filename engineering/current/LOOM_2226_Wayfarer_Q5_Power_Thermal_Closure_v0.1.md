# LOOM 2226 — Wayfarer Q5 Power & Thermal Closure v0.1

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`

## 0. Authority boundary

This study does not alter CANON II. It establishes first-principles power/thermal constraints that every final propulsion card must satisfy.

## 1. Radiative rejection anchor

At 900 K, ideal blackbody radiative flux is approximately 37.2 kW/m². At emissivity 0.9 the usable flux is approximately 33.5 kW/m².

Representative radiator areas at 900 K, emissivity 0.9:

- 25 MW waste heat -> ~746 m²;
- 50 MW -> ~1,493 m²;
- 100 MW -> ~2,986 m²;
- 1 GW -> ~29,860 m²;
- 100 GW -> ~2.99 million m².

Immediate consequence: a multi-TW propulsion system cannot dump percent-level source power into ordinary ship radiators. Torch architecture must keep ship-coupled waste heat in the tens-to-low-hundreds of MW class or use bounded transient storage/open-loop rejection. This is a design requirement, not yet a measured torch coefficient.

## 2. Torch implication

The current ideal jet-power card spans roughly 5.1–12.8 TW. Therefore:

- 100 MW of ship-coupled heat at 12 TW corresponds to a coupling fraction of ~8.3e-6;
- 50 MW corresponds to ~4.2e-6.

The final torch must therefore behave primarily as a direct energy-to-directed-exhaust system, with only a few-parts-per-million to few-parts-per-ten-million of the multi-TW jet power appearing as steady ship-coupled heat if radiator area is to remain spacecraft-scale.

This does not prove such a torch exists. It defines the thermal performance the fictional mature 2226 torch must earn in the setting.

## 3. RCS power trade

For a momentum thruster:

`Pjet = 0.5 * F * ve`

For one 25 kN candidate RCS thruster:

- 20 km/s exhaust -> 250 MW jet power;
- 50 km/s -> 625 MW;
- 100 km/s -> 1.25 GW.

For 100 kN aggregate normal translation:

- 20 km/s -> 1.0 GW jet power;
- 50 km/s -> 2.5 GW;
- 100 km/s -> 5.0 GW.

This demonstrates that the high-authority RCS should not automatically be designed for extreme exhaust velocity. RCS mission delta-v is small; power and impulse control may matter more than remass economy.

## 4. Candidate RCS operating philosophy

Carry into Q5.2 a variable-performance maneuvering architecture:

### Precision / stationkeeping mode

- deeply throttled thrust;
- minimum impulse bit prioritized;
- low disturbance;
- internal momentum storage preferred for pure attitude hold;
- electrically supplied plasma or electrothermal operation acceptable if bus load closes.

### Translation / slew mode

- use only the number of 25 kN units required by geometry;
- favor moderate exhaust velocity, initially screen 20–50 km/s;
- accept higher remass consumption because total maneuver delta-v is small;
- short-duty operation can use thermal buffering if Q5.3 closes transient energy.

### Abort mode

- up to ~200 kN aggregate candidate thrust;
- explicitly time-limited;
- may consume working fluid aggressively;
- must remain independent of main-torch ignition for close-proximity safety.

## 5. Electrical-bus firewall

Do not equate torch jet power with electrical bus power.

The final architecture must distinguish at least:

- fusion/reaction source power;
- direct torch-channel power;
- electrical generation capacity;
- pulse-bank capacity;
- RCS electrical or direct-thermal feed;
- avionics/habitat hotel load;
- relational plant load;
- cryogenic load.

A propulsion system may have TW-class directed jet power while the electrical bus remains orders of magnitude smaller.

## 6. Metric coexistence

Governing canon states that major torch operation and high metric operation are mutually exclusive thermal/field states. Preserve that rule during qualification.

RCS and fine attitude control, however, must remain available during metric acquisition/collapse unless a specific field-interference model forbids a subset of units. Q5/Q6 must define the allowed maneuvering authority in each metric state.

## 7. Thermal-buffer requirement

The final standard must carry an explicit thermal buffer rather than using an unbounded 'short burn' assumption.

Required quantities for Q5.2/Q5.3:

- usable buffer energy, GJ;
- maximum charge/discharge power, MW or GW;
- high-loop temperature limit;
- radiator recovery rate;
- permitted burst duration for each RCS/torch mode;
- mandatory recovery/cooldown interval.

Until those values are tied to a physical mass/working-fluid model, burst claims remain CANDIDATE.

## 8. Feedstock connection back to Q2

The feedstock matrix should not be finalized solely on ionization energy. Q5 must add species-dependent penalties for:

- radiation losses;
- recombination/deposition;
- plasma-conditioner efficiency;
- nozzle interaction;
- required tank refrigeration;
- conditioning waste heat.

Thus Q2 and Q5 close together.

## 9. Q5 v0.1 disposition

Supported now:

- steady torch ship-coupled heat must be tiny relative to jet power;
- RCS high-authority thrust is plausible only as a moderate-exhaust-velocity, duty-limited system unless a very large electrical/direct-power path is qualified;
- 20–50 km/s is the current RCS exhaust-velocity screening range for high-thrust translation/slew;
- internal momentum storage should perform most zero-translation attitude holding;
- all propulsion cards require explicit radiator/buffer closure.

Still open:

1. final physical radiator area and emissivity;
2. thermal-buffer mass/energy;
3. electrical generation and pulse-bank limits;
4. direct-vs-electrical RCS power architecture;
5. torch ship-coupled heat coefficient;
6. RCS efficiency and waste-heat fraction;
7. species-dependent conditioning losses;
8. continuous/burst duty limits by mode.

**Q5 remains OPEN, but v0.1 establishes the key thermal firewall and narrows high-authority RCS toward moderate exhaust velocity rather than maximum-Isp operation.**
