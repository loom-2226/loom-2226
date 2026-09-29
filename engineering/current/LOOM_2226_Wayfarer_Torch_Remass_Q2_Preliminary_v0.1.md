# LOOM 2226 — Wayfarer Torch Remass Q2 Preliminary v0.1

**Status:** ENGINEERING ANALYSIS / NON-CANON / PRELIMINARY  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`

---

## 0. BLUF

The current torch exhaust-velocity range is so energetic that **bulk exhaust kinetic energy dominates ordinary molecular chemistry by orders of magnitude**. Therefore the first-order remass question is not "which chemical fuel has enough energy?" The fusion plant supplies the energy. Q2 should instead qualify whether a candidate feed can be stored, conditioned into an acceptable plasma, accelerated through the magnetic-nozzle system, and tolerated by the materials / contamination / thermal architecture.

This materially supports a **multi-feed torch interface** without yet proving that every candidate species is usable.

Water remains a strong primary candidate, but it should not be frozen as the only acceptable remass.

---

## 1. Current working torch card

Current engineering/Navigator working card:

| Mode | Acceleration card | Exhaust velocity |
|---|---:|---:|
| ECON | 0.30 g | 3000 km/s |
| CRUISE | 1.00 g | 2000 km/s |
| EXPEDITE | 2.00 g | 1000 km/s |
| FAST | 3.00 g | 700 km/s |
| HARD | 5.00 g | 450 km/s |
| LIMIT | 7.50 g | 300 km/s |

Reference current wet mass: **1,158.5 t**.

For ideal directed kinetic exhaust:

`F = m_dot * v_e`

`P_jet = 0.5 * m_dot * v_e^2 = 0.5 * F * v_e`

At the reference wet mass, the implied first-order values are:

| Mode | Thrust | Mass flow | Ideal jet power | Remass/hour |
|---|---:|---:|---:|---:|
| ECON | 3.408 MN | 1.136 kg/s | 5.112 TW | 4.09 t/h |
| CRUISE | 11.361 MN | 5.681 kg/s | 11.361 TW | 20.45 t/h |
| EXPEDITE | 22.722 MN | 22.722 kg/s | 11.361 TW | 81.80 t/h |
| FAST | 34.083 MN | 48.690 kg/s | 11.929 TW | 175.28 t/h |
| HARD | 56.805 MN | 126.233 kg/s | 12.781 TW | 454.44 t/h |
| LIMIT | 85.208 MN | 284.025 kg/s | 12.781 TW | 1,022.49 t/h |

These are reference-mass instantaneous values, not final mode-card locks. As remass is expended, constant-g operation changes thrust/mass-flow requirements.

---

## 2. Energy-per-kilogram regime

The exhaust kinetic energy per kg is:

`E_k/kg = 0.5 * v_e^2`

Therefore:

| Exhaust velocity | Kinetic energy per kg |
|---:|---:|
| 300 km/s | 45 GJ/kg |
| 450 km/s | 101.25 GJ/kg |
| 700 km/s | 245 GJ/kg |
| 1000 km/s | 500 GJ/kg |
| 2000 km/s | 2.0 TJ/kg |
| 3000 km/s | 4.5 TJ/kg |

This establishes the relevant scale for feed conditioning.

---

## 3. Water conditioning order-of-magnitude check

NIST Chemistry WebBook gives an evaluated first ionization energy for gas-phase H2O of approximately **12.621 eV per molecule**. Converted to a specific energy, that is approximately **67.6 MJ/kg** for one ionization per intact water molecule.

This value is not a complete plasma-conditioning model; dissociation, higher ionization states, heating, inefficiency and species chemistry must still be included. It is used only as an order-of-magnitude comparison.

Even **67.6 MJ/kg** is:

- ~0.15% of the 45 GJ/kg LIMIT exhaust kinetic energy;
- ~0.067% of the 101.25 GJ/kg HARD exhaust kinetic energy;
- ~0.0015% of the 4.5 TJ/kg ECON exhaust kinetic energy.

Thus ordinary first-stage ionization energy is not the dominant energy term in the present torch regime.

Source: NIST Chemistry WebBook, Water, evaluated ionization energy 12.621 ± 0.002 eV, https://webbook.nist.gov/cgi/cbook.cgi?Name=water&Units=CAL&cIC=on&cIE=on&cTG=on&cTR=on

NASA historical propulsion literature also demonstrates that water has been deliberately considered as spacecraft propellant in systems designed for broad propellant compatibility. This is evidence only that water is a legitimate spacecraft working-fluid candidate; it does **not** establish compatibility with the fictional LOOM fusion torch.

Source: NASA-TM-100110 / IAF-87-259, *Water-propellant resistojets for man-tended platforms*, NTRS document 19870016702.

---

## 4. Consequence for Q2

The torch feedstock qualification should be organized around the following hierarchy:

### First-order

1. Can the feed be delivered to the engine at required kg/s?
2. Can it be converted to the required plasma / charge state?
3. Can the magnetic nozzle couple to that plasma with acceptable efficiency?
4. Can the feed / byproducts be tolerated by reactor/nozzle materials?
5. Can the system sustain the required mass flow without unacceptable erosion or deposition?

### Second-order

6. How much conditioning energy is required relative to jet power?
7. What additional ship-coupled waste heat is generated?
8. What storage volume / tank mass is required?
9. What hazards and maintenance burdens arise?
10. How available is the feedstock in the 2226 logistics network?

This is more defensible than choosing a chemical species because of conventional rocket-fuel intuition.

---

## 5. Candidate disposition — preliminary only

No candidate is yet `CERTIFIED`.

| Feed | Preliminary reason to retain | Key unresolved issue | Current disposition |
|---|---|---|---|
| H2O | dense, simple storage, multifunctional ship resource, demonstrated historical spacecraft-propellant use | dissociation/plasma chemistry, oxygen-rich erosion/contamination, nozzle coupling | STUDY / PRIMARY CANDIDATE |
| H2 | very low particle mass, clean plasma, high-performance precedent in fusion/plasma concepts | cryogenic/low-density storage; frontier acquisition still infrastructure-heavy | STUDY |
| NH3 | dense storable volatile, H-rich | decomposition products, nitrogen plasma/material effects | STUDY |
| CH4 | dense relative to H2, common volatile candidate | carbon deposition / contamination | STUDY |
| CO2 | potentially useful local volatile in some environments | oxygen/carbon chemistry, heavier plasma, material effects | STUDY |
| CO | volatile feed option | toxicity/handling, carbon/oxygen material effects | STUDY |
| N2 | stable and readily handled | plasma coupling and nitrogen material interactions | STUDY |
| Ar | inert, simple plasma species | sourcing/storage volume and higher particle mass | STUDY |
| O2 | potentially easy to derive from water/oxides | aggressive oxygen plasma/material compatibility | STUDY / CONTINGENCY CANDIDATE |

The table deliberately avoids pretending that chemical identity alone determines achievable exhaust velocity. In this architecture the engine supplies the energy and the nozzle/field interaction determines whether a species can actually realize a mode card.

---

## 6. Working hypothesis to test

**H-Q2-1:** A mature 2226 magnetic-nozzle fusion torch can support more than one certified remass species because the kinetic-energy requirement at 300–3000 km/s dominates ordinary feed-conditioning chemistry, provided the feed system and plasma-facing materials are engineered for multiple species.

This hypothesis is **not canon** and must be falsified if nozzle-coupling, erosion, contamination, charge-state, reactor-interface or thermal constraints make multi-feed operation impractical.

---

## 7. Next calculations

Q2.1 — define required charge state / plasma parameters for the canonical nozzle concept.  
Q2.2 — derive species-specific mass-flow / particle-flow rates at each torch card.  
Q2.3 — estimate complete conditioning burden for H2O, H2, NH3, CH4, CO2, N2 and Ar.  
Q2.4 — screen plasma-facing-material compatibility and contamination.  
Q2.5 — derive tank volume/mass impact at Wayfarer quantities.  
Q2.6 — source Solar-System availability/logistics separately from engine physics.  
Q2.7 — produce the `CERTIFIED / DERATED / CONTINGENCY / PROHIBITED` matrix.

Until Q2.7 closes, current 250 t normal-remass allocation remains the governing comparison baseline.