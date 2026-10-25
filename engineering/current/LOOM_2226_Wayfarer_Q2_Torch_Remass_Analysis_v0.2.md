# LOOM 2226 — Wayfarer Q2 Torch Remass Analysis v0.2

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`  
**Purpose:** Advance Q2 from qualitative ranking to a screening matrix that separates ideal momentum closure from storage, plasma-conditioning, materials and logistics constraints.

---

## 0. Authority boundary

This document does not alter CANON II. Current governing torch physics remains ordinary momentum exchange. The existing 300 t working-fluid/water inventory and 250 t normal-remass allowance remain the comparison baseline until Q6/Q7 derive a replacement.

The screening below is intentionally not a final `CERTIFIED / DERATED / CONTINGENCY / PROHIBITED` matrix. The fictional fusion-torch materials/plasma constitutive model is not yet sufficiently specified to support honest per-mode certification. This document instead records which feeds advance to detailed qualification and what must be measured/modelled next.

---

## 1. Empirical ancestry relevant to multi-feed operation

NASA/Marshall and Princeton tested a microwave-assisted inductive plasma accelerator with multiple propellant species including **argon, water and ammonia**, specifically because electrode-less inductive coupling can isolate vulnerable hardware from reactive propellants. That is strong empirical ancestry for LOOM's decision to test a conditioned multi-feed plasma interface rather than assume one chemically unique working fluid.

NASA also tested a **MW-class flex-propellant arcjet** on both hydrogen and simulated ammonia, showing that high-power plasma propulsion can be deliberately designed around more than one feed chemistry, while performance and thermal efficiency remain species-dependent.

These systems operate many orders of magnitude below the Wayfarer torch and do not validate its performance. They support only the architecture claim that multi-feed plasma propulsion is physically reasonable enough to investigate.

NIST fluid-property data reinforce the storage distinction: nitrogen boils near 77.34 K and argon near 87.3 K at normal boiling conditions, while methane is near 111.7 K. CO2 has a triple point near 216.58 K and 5.185 bar, so ordinary low-pressure liquid storage is not available; pressure/temperature state management matters.

---

## 2. Governing ideal-momentum result

At fixed ship mass `m`, acceleration `a`, and certified exhaust velocity `ve`:

`F = m a`

`mdot = F / ve`

`Pjet = 0.5 F ve`

Therefore species identity does **not** enter the ideal momentum closure directly. It enters through achievable `ve`, nozzle efficiency, radiative losses, ionization state, erosion, conditioning power, storage and handling.

This is now a design rule for Q2: **do not invent a species-specific exhaust-velocity card without a species-specific plasma/nozzle model.**

---

## 3. Q2 screening matrix

Screening disposition meanings:

- `ADVANCE_PRIMARY` — strongest candidate for normal Wayfarer carriage.
- `ADVANCE_ALTERNATE` — credible alternate worth full plasma/material qualification.
- `ADVANCE_SPECIAL` — useful only where a mission or regional supply case justifies dedicated handling.
- `ADVANCE_CONTINGENCY` — retain as a frontier/emergency option but expect derating or maintenance penalty.
- `DEFER` — insufficient advantage to justify priority testing.

| Feed | Storage class | Plasma / materials concern | Logistics value | Screening disposition | Why |
|---|---|---|---|---|---|
| **H2O** | dense, moderate-temperature liquid | oxygen-bearing dissociation products; oxide/erosion/radiation behaviour must be tested | excellent; life support, shielding, thermal and industrial utility | **ADVANCE_PRIMARY** | best multifunction mass even if not the easiest plasma |
| **NH3** | dense liquid under manageable refrigeration/pressure | toxic/corrosive handling; N/H plasma and dissociation chemistry | strong in volatile-rich regions | **ADVANCE_ALTERNATE** | directly supported by flex-propellant plasma ancestry and good bulk storage |
| **Ar** | cryogenic liquid ~87 K | low chemical reactivity; simple monatomic plasma | weaker bulk abundance; depot/specialized supply | **ADVANCE_ALTERNATE** | excellent plasma-control candidate; likely clean reference feed |
| **N2** | cryogenic liquid ~77 K | simple molecular/atomic nitrogen plasma; radiation/material response still required | regionally abundant and industrially common | **ADVANCE_ALTERNATE** | useful clean-ish elemental comparison feed with broader sourcing than Ar |
| **CO2** | pressurized/refrigerated; triple point 216.58 K / 5.185 bar | carbon/oxygen species; possible deposition/oxide burden | excellent in Mars/CO2-rich logistics chains | **ADVANCE_ALTERNATE** | regional abundance may outweigh conditioning penalty |
| **H2** | deep cryogenic ~20 K class; very low volumetric density | excellent light-ion feed if nozzle/reaction physics benefits | difficult bulk storage and tankage | **ADVANCE_SPECIAL** | retain only if species-dependent coupling raises attainable ve or efficiency |
| **O2** | cryogenic liquid ~90 K class | oxidizer/fire/material burden pre-ionization; oxygen plasma erosion | producible from water/oxides | **ADVANCE_CONTINGENCY** | useful because it may be locally produced, but poor normal shipboard choice |
| **CH4** | cryogenic liquid ~111.7 K | carbon deposition / dissociation products | strong outer-system availability in some environments | **ADVANCE_CONTINGENCY** | plausible frontier feed if conditioner prevents carbon fouling |
| **CO** | deeply refrigerated liquid/gas handling | toxic; carbon/oxygen contamination without CO2's storage/logistics advantages | regional only | **DEFER** | dominated by CO2 for most intended logistics cases |

---

## 4. Per-mode screening rule

No candidate is yet honestly `CERTIFIED` for any Wayfarer torch mode because the following fictional-engine quantities remain open:

1. allowable impurity fraction;
2. minimum ionization fraction entering the magnetic nozzle;
3. species-dependent radiative loss fraction;
4. charge-state distribution at nozzle entry;
5. wall/nozzle erosion rate versus species and mass flow;
6. recombination / condensation risk during expansion;
7. magnetic-nozzle efficiency versus atomic/molecular composition;
8. maximum conditioner throughput;
9. transient response during feed switching;
10. contamination-clearing / purge requirement.

Accordingly the honest current matrix is:

| Feed | ECON | CRUISE | EXPEDITE | FAST | HARD | LIMIT |
|---|---|---|---|---|---|---|
| H2O | TEST | TEST | TEST | TEST | TEST | TEST |
| NH3 | TEST | TEST | TEST | TEST | TEST | TEST |
| Ar | TEST | TEST | TEST | TEST | TEST | TEST |
| N2 | TEST | TEST | TEST | TEST | TEST | TEST |
| CO2 | TEST | TEST | TEST | TEST | TEST | TEST |
| H2 | SPECIAL TEST | SPECIAL TEST | SPECIAL TEST | SPECIAL TEST | SPECIAL TEST | SPECIAL TEST |
| O2 | CONTINGENCY TEST | CONTINGENCY TEST | CONTINGENCY TEST | CONTINGENCY TEST | CONTINGENCY TEST | CONTINGENCY TEST |
| CH4 | CONTINGENCY TEST | CONTINGENCY TEST | CONTINGENCY TEST | CONTINGENCY TEST | CONTINGENCY TEST | CONTINGENCY TEST |
| CO | DEFER | DEFER | DEFER | DEFER | DEFER | DEFER |

This is deliberately conservative. Final per-mode ratings wait for Q5-compatible plasma/material closure.

---

## 5. Working feed-interface architecture

The most defensible 2226 design direction is a **conditioned-fluid torch interface** with three physical layers:

1. **tank/feed layer** — accepts approved liquids/gases under species-specific pressure/temperature limits;
2. **conditioner layer** — meters, vaporizes, dissociates and ionizes feed to a bounded plasma-entry state;
3. **torch/nozzle layer** — receives plasma only inside a qualified composition/charge/temperature envelope.

The torch should not ingest raw regolith, slurry or arbitrary dirty volatiles. Frontier material must first be refined into an approved feed specification.

This preserves optionality without granting magical universal-fuel behaviour.

---

## 6. Tank doctrine implication

The current four-tank arrangement should remain under qualification, but not all four tanks need identical mission loading.

Recommended design direction:

- normal dispatch: majority H2O;
- protected potable/medical/life-support water kept behind a separate cleanliness boundary and not treated as routine propellant;
- at least one tank/feed train capable of alternate TF-A feed after purge/recertification;
- cryogenic alternate feeds require dedicated conditioning/insulation modules and do not automatically share the relational plant's precision 20 K cryogenic hardware;
- a tank previously exposed to toxic or carbon-bearing feed is not automatically returned to potable service.

---

## 7. Q2 provisional doctrine

Current engineering recommendation, still non-canon:

`PRIMARY_REMASS_CANDIDATE = H2O`

`ALTERNATE_REMASS_CANDIDATES = NH3, Ar, N2, CO2`

`SPECIALIZED_FEED = H2`

`CONTINGENCY_FEEDS = O2, CH4`

`DEFERRED = CO`

This preserves both operational realism and optionality.

---

## 8. Q2 exit status

**Q2-A/B/D/E: materially advanced.**

**Q2-C final per-mode certification: BLOCKED ON Q5-compatible plasma/material constitutive assumptions.**

The blocking issue is not chemical energy. It is the missing species-to-plasma-to-nozzle/material response model.

Therefore Q2 should now hand forward two artifacts:

1. the feedstock screening matrix;
2. the required interface variables that Q5 must close.

Q4 can proceed in parallel because the current mass-properties work only requires tank mass/location and candidate inventory envelopes, not final plasma chemistry.

---

## 9. External evidence provenance

Empirical ancestry used in this pass:

- NASA NTRS, Hallock & Polzin, *Thrust Stand Measurements Using Alternative Propellants in the Microwave Assisted Discharge Inductive Plasma Accelerator* (2011): tested argon, water and ammonia; supports multi-feed inductive-plasma feasibility at laboratory scale.
- NASA NTRS, Litchford, *High Power Flex-Propellant Arcjet Performance* (2011): MW-class tests on hydrogen and simulated ammonia; supports high-power multi-feed plasma-propulsion ancestry.
- NIST Chemistry WebBook / thermophysical-fluid references: storage and phase-property anchors for N2, Ar, CH4 and CO2.

These sources do not establish Wayfarer-scale torch performance and are not treated as such.
