# LOOM 2226 — Rabbit-Hole Priority Table v1.3

**Date:** 21 August 2026  
**Status:** COMPANION RESEARCH REGISTER — NOT CANON  
**Governing baseline:** LOOM 2226 Canon Baseline v2.3  
**Research basis:** Technical Paper Series v1.0 + current operational/test artifacts

> **Purpose:** Maintain a reproducible queue of the questions worth spending real design, modeling, validation and playtest effort on after the v2.3 xenoarchaeology promotion and the Technical Paper Series v1.0 review. A rabbit hole is not automatically a defect. Closed questions are retired; intentionally unresolved questions are protected rather than “solved” for completeness.

---

# 1. Authority and supersession rule

The v2.3 three-volume canon and v2.3 Manifest govern this refresh.

- **CANON I v2.3** governs world/history/frontier claims.
- **CANON II v2.3** governs engineering/ships/operations.
- **CANON III v2.3** governs hidden truth, continuity, GM state and the hidden Loom graph.
- **Xenoarchaeology & Terminal Mobilization Canon v1.0** is a promoted governing source.
- **Technical Paper Series v1.0** is a research/validation program. It may expose open seams but does not silently rewrite canon.
- Uploaded older files — especially **Foundational Canon v1.5**, **Institutions Register v1.2**, **Canon Manifest v1.0**, **v2.1.1 hashes**, and older embedded engineering values inside the Courier Compendium — are provenance where v2.3 conflicts with them.

The v2.3 freeze materially changes world history and xenoarchaeology but explicitly leaves the certified propulsion stack, hidden Loom physical edge set, Solar census and six-system frontier scale unchanged.

---

# 2. Status and review-depth vocabulary

## 2.1 Research/canon status

| Status | Meaning |
|---|---|
| **OPEN** | Explicit research space inside current canon boundaries. |
| **PROVISIONAL** | A usable working calibration exists, but exact closure remains open. |
| **EXPERIMENTAL** | Exists in test/play/campaign work but is not general canon. |
| **STANDING TARGET** | Explicitly retained by governing canon or the technical validation program for future certification/research. |
| **DERIVATION PROGRAM** | Downstream worldbuilding should be regenerated from frozen upstream physics rather than used to retune it. |
| **CAMPAIGN-DEPENDENT** | Valuable only when the campaign reaches the relevant evidence or situation. |
| **INTENTIONALLY UNRESOLVED** | Premature closure damages the setting. Preserve ambiguity unless play or explicit canon amendment resolves it. |
| **RETIRED / SUPERSEDED / MERGED** | Substantially closed, overtaken by later governing work, or absorbed into another stable RH entry. |

## 2.2 Review depth

| Depth | Meaning |
|---|---|
| **UNREVIEWED** | Mostly a named question or qualitative assumption. |
| **CALIBRATED** | A working numerical/structural calibration exists. |
| **MODELLED** | A reproducible model, ledger or causal framework exists, though assumptions remain attackable. |
| **TEST-EXPOSED** | Flight/play/integration testing has exercised the assumption and revealed constraints. |
| **ADVERSARIALLY FRAMED** | The technical papers/red-team process identify explicit failure conditions, sensitivities or hard kills. |
| **DATASET MISSING** | Exact calibration is deliberately withheld because the required dataset does not yet exist. |

Review depth is independent of canon strength. An OPEN problem can be heavily studied; a LOCKED rule can still rest on an explicit fictional bridge.

---

# 3. Reproducible priority method

Each active rabbit hole receives five ratings from 0–4:

- **C — Consequence if wrong:** how much engineering, world structure or canon-facing derivation moves if the current assumption fails.
- **L — Cross-document leverage:** how many other systems depend on the answer.
- **R — Closure readiness:** how tractable the next useful model/test is now.
- **U — Utility:** engineering, gameplay, worldbuilding or campaign payoff.
- **M — Mystery cost:** how much premature closure would damage intentional ambiguity.

## Priority score

\[
\textbf{Priority} = 5C + 3L + 2R + U - 3M
\]

Maximum score = 44.  
Sort order = **Priority descending → C descending → L descending → stable RH ID**.

This answers **“what is worth working on next?”**, not “what is most metaphysically important?” A lower-ranked foundational question can still be more profound than a higher-ranked tractable engineering problem.

---

# 4. Ranked active queue

| Rank | ID | Rabbit hole | Status | Review depth | C | L | R | U | M | Score |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | **RH-002** | Loom coherence, large-domain scaling, and absolute lattice throughput | **OPEN / STANDING TARGET** | MODELLED + TEST-EXPOSED | 4 | 4 | 3 | 4 | 0 | **42** |
| 2 | **RH-005** | Mc-299m production physics, industrial pathway, aging, and cycle life | **OPEN / STANDING TARGET** | CALIBRATED + ADVERSARIALLY FRAMED | 4 | 4 | 3 | 3 | 0 | **41** |
| 3 | **RH-003** | Torch plasma/radiation/nozzle deposition microphysics | **OPEN / STANDING TARGET** | SHIP-BUDGET CLOSED; MICROPHYSICS OPEN | 4 | 3 | 4 | 4 | 0 | **41** |
| 4 | **RH-004** | Mc-299m / NRE metric-coupling constitutive law beyond point calibration | **OPEN DEEP ENGINEERING** | CALIBRATED + ADVERSARIALLY FRAMED | 4 | 4 | 2 | 3 | 0 | **39** |
| 5 | **RH-017** | Reference ship ecology and propulsion scaling across vessel classes | **DERIVATION PROGRAM** | COURIER VALIDATED; MULTI-CLASS SET MISSING | 3 | 4 | 4 | 4 | 0 | **39** |
| 6 | **RH-007** | Metric environmental interaction, null/geodesic/caustic certification, and collapse safety | **OPEN / STANDING TARGET** | MODELLED; CERTIFICATION DETAIL OPEN | 4 | 3 | 3 | 3 | 0 | **38** |
| 7 | **RH-006** | Conserved Solar demography and habitat-capital closure | **DERIVATION PROGRAM** | PARTLY MODELLED; COHORT/CAPITAL ENGINE MISSING | 3 | 4 | 3 | 4 | 0 | **37** |
| 8 | **RH-025** | 2226 input-output, ownership, labor-share, and price model | **OPEN DERIVATION** | STRUCTURE MODELLED; ECONOMETRIC CLOSURE OPEN | 3 | 4 | 3 | 4 | 0 | **37** |
| 9 | **RH-009** | Strategic-material geography, substitution, stockpiles, and corporate concentration | **OPEN RESEARCH** | STRUCTURE MODELLED + ADVERSARIALLY FRAMED | 3 | 3 | 4 | 4 | 0 | **36** |
| 10 | **RH-018** | Door-to-door transport, route-flow, packet, and port-throughput engine | **DERIVATION PROGRAM** | PARTLY MODELLED | 3 | 3 | 4 | 4 | 0 | **36** |
| 11 | **RH-026** | Relational-node reliability, correlated failure clusters, and certification statistics | **OPEN / STANDING TARGET** | FAILURE DOCTRINE MODELLED; DATASET MISSING | 3 | 3 | 4 | 4 | 0 | **36** |
| 12 | **RH-022** | Full 4D finite-RSET metric-ramp benchmark | **STANDING TARGET** | SCREENED; FULL BENCHMARK MISSING | 4 | 3 | 2 | 2 | 0 | **35** |
| 13 | **RH-024** | M1/M2 parent-theory seam: bounded domains and causal-sector orientation without hidden M3 | **OPEN DEEP THEORY** | EFFECTIVE THEORY MODELLED | 4 | 4 | 1 | 3 | 1 | **34** |
| 14 | **RH-008** | Topology spectroscopy, engineered perturbation, mis-translation observables, and external Loom forensics | **EXPERIMENTAL / REVISION-OPEN** | TEST-EXPOSED + DATASET MISSING | 3 | 4 | 3 | 4 | 1 | **34** |
| 15 | **RH-010** | Synthetic-person individuation, staffing, migration, and heliocentric population closure | **PROVISIONAL** | CALIBRATED; AUDIT/MODEL MISSING | 3 | 3 | 3 | 4 | 0 | **34** |
| 16 | **RH-020** | Insurance/risk pricing tied to certification, topology, rescue access, and causal delay | **OPEN INSTITUTIONAL DERIVATION** | CONCEPT MODELLED | 2 | 3 | 4 | 4 | 0 | **31** |
| 17 | **RH-019** | Crew certification, human factors, degraded-operation, and error attribution | **OPEN ENGINEERING / GAMEPLAY** | ENGINEERING STACK MODELLED + TEST-EXPOSED | 2 | 3 | 3 | 4 | 0 | **29** |
| 18 | **RH-027** | TMP comparative xenoarchaeology, selection-bias control, and falsification cases | **PROTECTED RESEARCH / INTENTIONALLY UNRESOLVED CORE** | THREE-LINEAGE MODEL + GM COUNTEREXAMPLE | 3 | 3 | 3 | 4 | 2 | **28** |
| 19 | **RH-012** | Exact maneuver-node engineering and control-authority closure | **PROVISIONAL** | TEST-EXPOSED | 2 | 2 | 4 | 4 | 0 | **28** |
| 20 | **RH-021** | Mis-translation resolution calibration and failure-family fairness | **EXPERIMENTAL / PLAYTEST-CLOSED STRUCTURE** | TEST-EXPOSED | 2 | 3 | 3 | 4 | 1 | **26** |
| 21 | **RH-011** | Living first-contact data security, disclosure, custody, and governance | **CAMPAIGN-DEPENDENT** | ARCHAEOLOGICAL CUSTODY MODELLED; LIVING CONTACT OPEN | 2 | 2 | 3 | 4 | 1 | **23** |
| 22 | **RH-014** | A06/anomaly synthetic dataset and detection calibration | **PARKED EXPERIMENTAL** | DATASET MISSING | 1 | 2 | 4 | 3 | 0 | **22** |
| 23 | **RH-015** | Exact Earth political bloc / constitutional succession map | **OPEN DETAIL** | STRUCTURE SUFFICIENT; DETAIL OPEN | 1 | 2 | 2 | 3 | 0 | **18** |
| 24 | **RH-016** | Detailed military/security orders of battle | **OPEN DETAIL** | STRUCTURE SUFFICIENT; DETAIL OPEN | 1 | 2 | 2 | 3 | 0 | **18** |
| 25 | **RH-013** | Gas-giant ³He / light-isotope economics | **PROVISIONAL / NON-LOAD-BEARING** | CALIBRATED | 1 | 1 | 3 | 2 | 0 | **16** |

---

# 5. The major priority changes from v1.2

## 5.1 RH-003 is reactivated and promoted to #3

v1.2 deprioritized torch thermal closure because the **ship-level** heat budget had been repaired. Paper II makes the distinction sharper: the system-level ppm requirement is usable, but the reactor/plasma/nozzle pathway that achieves it is not microphysically closed. Paper II explicitly identifies torch deposition sensitivity as one of the highest-value remaining technical targets.

**Next useful artifact:** a radiation/plasma/nozzle deposition model that separately budgets photons, neutrons/side reactions, magnet/nozzle interception, charged-particle leakage, secondary heating and mode dependence against the existing ppm envelope.

## 5.2 RH-006 and RH-018 are no longer “build the economy from scratch”

Paper III now supplies a coherent economic geography: generalized transport cost, certification friction, packet information, route shocks, strategic-material chains, capital concentration, demographic controls, counterfactual hard kills and sensitivity ordering.

The remaining work is narrower and more testable:

- **RH-006:** cohort-conserving biological demography + habitat-capital formation;
- **RH-025:** input-output + ownership/distribution/prices;
- **RH-018:** route-flow + packet frequency + fleet capacity + port throughput;
- **RH-020:** insurance/legal enforceability as a derived risk-price layer.

That moves “economics/demographics” from a vague top-level gap to a set of actual model-building tasks.

## 5.3 RH-021 drops because the test program already solved the structural mechanics problem

Core Mechanics/Test Flights now provide Integrity Class, transition/failure-family resolution, formation/navigation separation, and a mis-translation branch that resolves into another physically admissible relationship rather than an arbitrary Cartesian miss.

What remains is **calibration and fairness**, not invention of the mechanic from zero.

## 5.4 RH-019 drops because certification is now infrastructure, not a blank page

Paper II provides a concrete multi-layer certification stack covering material, tile, array, boundary, Loom route, metric geometry, thermal, power, conservation and operational state. Core mechanics and flight tests also distinguish operator skill from objective topology/hardware state.

Remaining work is human-factors engineering: training pipelines, recurrency, authority transfer, procedural error rates, degraded-state decision doctrine, and how investigators attribute failure among crew, maintenance, environment, route state and correlated hardware faults.

## 5.5 RH-011 is narrowed rather than deleted

The v2.3 xenoarchaeology package substantially closes **archaeological** custody/governance through Artifact Acceleration, the Custody Partition, provenance separation, Attention Intelligence and Composite Reconstruction controls.

The open campaign seam is now **living or active first contact**: data security, disclosure authority, quarantine/containment, cognition/personhood questions, jurisdiction under causal delay and who is allowed to speak for humanity.

## 5.6 Three new entries are promoted

- **RH-024 — M1/M2 parent-theory seam.** Paper I exposes the theoretical vulnerability cleanly: natural bounded domains and causal-sector orientation are not yet derived from a microscopic parent model. This is high consequence but deliberately low closure-readiness; do not turn “solve quantum gravity” into a prerequisite for play.
- **RH-025 — 2226 input-output/ownership model.** Paper III makes this a discrete, tractable economic program rather than a sub-bullet inside demographics.
- **RH-026 — correlated node reliability.** Paper II explicitly retains manufactured node topology and correlated-cluster failure statistics as a standing research/certification target.
- **RH-027 — TMP comparative xenoarchaeology.** v2.3 makes selection/survivorship bias a first-class constraint. The research goal is not to “solve the Great Filter”; it is to design falsifying cases, counterexamples and sampling logic that prevent TMP from becoming an all-purpose precursor answer.

## 5.7 RH-023 is merged into RH-007

The former “external gravitational perturbation during metric operation” question is now best treated as part of the broader metric-environment certification problem: massive/null trajectory maps, bright-source geometry, geodesic/caustic behavior, wave optics and safe collapse. Keeping a separate RH entry would double-count the same standing target.

---

# 6. Top-priority work packages

## RH-002 — Loom coherence / domain scaling

**Why #1:** It is the key bridge between the one well-closed courier and every larger ship, habitat module, cargo domain or future colony-scale ambition. CANON III also leaves numerical coherence values and translated-volume ceilings deliberately open.

**Questions to close next**

1. What state variable best represents domain coherence: phase-dispersion norm, boundary error, condition number, correlation length, or a coupled vector?
2. How do node count, baseline length, boundary area, mass distribution, moving internal masses and structural-state uncertainty enter the scaling?
3. What makes long/thin domains worse or different from compact domains at equal mass?
4. What limits certified translated volume: physics, metrology, computation, hardware count, proof time, or all of them?
5. What sets **absolute 2226 lattice throughput**: Mc supply, NRE fabrication, node yield, calibration time or certification bottlenecks?

**Exit criterion:** a bounded scaling family that reproduces the courier, predicts materially different vessel classes and does not accidentally make colony-scale Loom transport trivial.

## RH-005 — Mc production / aging

**Why #2:** This touches physics, strategic geography, fleet growth, certification, refurbishment, corporate concentration and xenoarchaeological ancestry without requiring the alien hardware to equal human technology.

**Questions to close next**

- synthesis chain and precursor inventory;
- plausible isomer population and separation strategy;
- flight-grade yield versus gross production;
- half-life/passive heat/daughter accumulation;
- lattice damage, resonator drift and refurbishment cycle;
- production-site shares and why those sites stay concentrated;
- how much primary Mc flow versus recovered/refurbished Mc supports the 2226 fleet.

**Exit criterion:** a mass-flow/industrial ledger from precursor feed to certified active material to retirement/recovery, with uncertainty bands and explicit strategic chokepoints.

## RH-003 — Torch microphysics

**Why #3:** The current heat budget only works if the solid-hardware deposition fraction stays brutally low. The arithmetic is closed; the physical pathway producing that arithmetic is not.

**Exit criterion:** a mode-by-mode deposition budget that makes the existing ppm calibration physically intelligible, identifies the dominant failure channel, and predicts what changes across ship classes.

## RH-004 — M2 constitutive law

**Why #4:** The effective law is good enough for engineering, but the deeper constitutive response still controls scaling, saturation, material aging and whether the setting can defend “two miracles, not three.”

**Do not overreach:** the goal is a stronger empirical/phenomenological law with bounded validity and falsifiers, not a claim that current physics predicts Mc/NRE.

## RH-017 — reference ship ecology

**Why #5 despite being the best first execution project:** It is not the deepest uncertainty, but it is the best **experimental platform** for the top four. A reference fleet forces courier-specific assumptions to reveal themselves.

**Recommended first class:** Belt utility/salvage workboat, followed by a small military/security craft, a packet courier variant, a bulk metric freighter and a large non-Loom habitat/transport comparison case.

---

# 7. Protected mysteries — research without forced closure

The following are **not ordinary solve-the-equation rabbit holes**. Work on them should improve evidence design, competing hypotheses and falsifiability while preserving uncertainty:

- ultimate microscopic ontology beneath M1/M2 beyond what is needed to prevent a hidden M3;
- why Chronology Exclusion exists at the deepest level;
- consciousness having privileged access to topology;
- Pauli/Jung-style relational-consciousness hypotheses;
- whether non-return cases share a cause;
- whether anything can “notice” humanity manipulating relational structure;
- Builder home system/self-name/morphology where canon marks them unresolved;
- TID initiator and motive;
- whether TID and terminal mobilization share a cause;
- whether Reef/Kite descendants survived;
- whether TMP has one common cause or any Great Filter exists at all;
- any automatic connection between xenoarchaeology and High Strangeness.

**Rule:** mystery work should usually create **better discriminating observations**, not a hidden answer inserted for completeness.

---

# 8. Retired / superseded / merged entries

| ID | Prior rabbit hole | v1.3 disposition |
|---|---|---|
| **RH-001** | Metric-drive energy / thermal / bank / wear closure | **RETIRED AS A GENERAL COURIER GAP.** v2.3 preserves the certified propulsion stack and Paper II closes the current courier as a coherent ship-level engineering object. Remaining metric-environment certification is RH-007; finite-RSET is RH-022; constitutive-response depth is RH-004. Do not resurrect older test-record “TBD power” language over the later governing baseline. |
| **RH-023** | External gravitational perturbation during metric operation | **MERGED INTO RH-007.** It is one case of the route/environment/trajectory/caustic certification problem. |

### Not retired, but materially narrowed

- **RH-003:** ship-level torch thermal closure is closed; reactor/nozzle microphysics remains open and is now high priority.
- **RH-011:** archaeological custody is substantially modelled by v2.3; living-contact governance remains campaign-open.
- **RH-018:** basic transport economics now exists; route-flow/throughput calibration remains.
- **RH-019:** certification architecture exists; human-factors closure remains.
- **RH-021:** structural mis-translation mechanics exist; calibration/fairness remains.

---

# 9. Immediate execution sequence

The ranked queue measures intrinsic research value. **Execution order may differ when one tractable work package generates test cases for several higher-ranked questions.**

1. **RH-017 — Build the reference fleet.** Start with the Belt utility/salvage workboat. Use it to expose scaling assumptions rather than inventing numbers in isolation.
2. **RH-003 — Close torch microphysics enough to explain the ppm envelope** on both the courier and first reference workboat.
3. **RH-005 — Build the Mc production/aging industrial ledger.** This supplies real constraints to fleet growth and strategic-material geography.
4. **RH-002 + RH-004 — Fit large-domain/coherence and constitutive scaling** against multiple vessel geometries and operating modes.
5. **RH-007 + RH-026 — Build the safety/certification attack set:** metric environment, caustics, correlated node failures, degraded-state margins.
6. **RH-018 — Build the route-flow/packet/port engine** using the frozen hidden graph and certified travel mechanics.
7. **RH-006 + RH-025 + RH-009 + RH-020 — Regenerate the civilizational model** from conserved population, habitat capital, input-output flows, strategic materials and risk pricing.
8. **RH-027 — Add xeno comparative falsification cases** only after the physics/economy queue is moving; preserve the Great-Filter/TMP uncertainty rather than solving it.

---

# 10. Reviewed-artifact ledger — all 24 uploaded files

| Uploaded artifact | Authority in this refresh | Rabbit-hole effect |
|---|---|---|
| `LOOM_2226_Core_Mechanics_v0.4(1).md` | Current gameplay working source | Downgrades RH-021 from invention to calibration; supports RH-008/RH-019; blind-survey calibration remains open. |
| `LOOM_2226_HUD_Design_Review_and_Final_Standard_v0.3(1).md` | Final presentation/interaction standard | No major research promotion. It closes several display-language issues and reinforces no-fake-precision doctrine. |
| `LOOM_2226_Test_Flights_Master_Record_v1.0(1).md` | Test/provenance source | Supports RH-008, RH-012, RH-014, RH-019, RH-021 and the protected High-Strangeness seam; older engineering TBDs are superseded where later canon/papers close them. |
| `LOOM_2226_Sol_and_Walter_Character_Sheet_v0.1(1).docx` | Playtest character artifact | No standalone high-priority RH. Its synthetic personhood/chassis/autonomy questions fold into RH-010 and human-factors/gameplay testing. |
| `LOOM_2226_Canon_Baseline_Manifest_v1.0(1).md` | Provenance only where v2.3 differs | No current priority authority. |
| `LOOM_2226_Foundational_Canon_v1.5(1).md` | Superseded foundational provenance | High-Strangeness and Loom unknowns remain useful provenance, but CANON I v2.3 / Foundational v1.6 consolidation governs. |
| `LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.1(1).md` | Current Solar reference subject to v2.3 hierarchy | Supports RH-006 and RH-010; confirms heliocentric synthetic-person allocation remains provisional. |
| `LOOM_2226_Shipbuilding_Engineering_Manual_v0.7(1).md` | Engineering stress-test provenance; later CANON II governs conflicts | Supports RH-002/RH-003/RH-005/RH-009/RH-012; older courier masses/metric TBDs must not override v2.3. |
| `LOOM_2226_Institutions_Organizations_Register_v1.2(1).md` | Older institutional provenance; v2.3 Manifest names v1.3 as promoted source | Supports structural thinking for RH-009/RH-020/RH-015/RH-016, but CANON I v2.3 governs current xeno-era institutional effects. |
| `LOOM_2226_Ship_Operations_Courier_Canon_Compendium_v1.0(1).md` | Operational compilation | Useful for test/mechanics provenance; embedded older technical values are subordinate to CANON II v2.3 and Technical Paper v1.0 conclusions. |
| `LOOM_2226_Baseline_File_Hashes_v2.1.1(1).md` | Provenance/authentication only | No research priority effect. |
| `LOOM_2226_Rabbit_Hole_Priority_Table_v1.2(1).md` | Immediate predecessor | Base IDs retained; v1.3 restores reproducible scoring/review depth and updates priorities. |
| `LOOM_2226_Paper_I_Mathematical_Foundations_Relational_Embedding_v1.0(1).pdf` | Current technical research paper | Creates RH-024; strengthens RH-004; protects the two-miracle budget and makes causal-sector orientation a named theoretical vulnerability. |
| `LOOM_2226_Technical_Paper_Series_Introduction_v1.0(1).pdf` | Current cross-paper research program | Primary source for the refreshed unresolved-target set and dependency direction physics → engineering → economics → institutions. |
| `LOOM_2226_Paper_III_Economic_Geography_and_Civilizational_Dynamics_v1.0(1).pdf` | Current technical/economic research paper | Narrows RH-006/RH-018, creates RH-025, strengthens RH-009/RH-010/RH-020, and provides an explicit sensitivity hierarchy. |
| `LOOM_2226_Paper_II_Engineering_Consequences_of_Relational_Transport_v1.0(1).pdf` | Current technical/engineering research paper | Reactivates RH-003; strengthens RH-002/RH-005/RH-007/RH-022; creates RH-026; confirms ship-level courier closure while exposing remaining microphysics/certification targets. |
| `LOOM_2226_CANON_III_Authority_Continuity_GM_Model_v2.3(1).md` | Governing GM/hidden-model canon | Keeps numerical coherence/volume ceilings, route failure probabilities, synthetic translation interaction and expanded graph detail open; supports RH-002/RH-008/RH-010. |
| `LOOM_2226_Xenoarchaeology_Terminal_Mobilization_Canon_v1.0(1).md` | Promoted governing source | Creates RH-027; narrows RH-011; establishes selection/survivorship bias and a hard firewall against automatic High-Strangeness causation. |
| `LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.3(1).md` | Governing engineering canon | Confirms standing targets for Mc pathway/aging, metric environment/RSET, node statistics and topology forecasting; supports retirement of RH-001 as a general gap. |
| `LOOM_2226_Canon_v2.3_Validation_Report(1).md` | Baseline validation | Confirms the v2.3 xeno promotion leaves propulsion constants, hidden graph, Solar census and frontier scale intact. Prevents false reprioritization from archaeology into propulsion. |
| `LOOM_2226_Baseline_File_Hashes_v2.3(1).md` | Authentication/provenance | Confirms v2.3 package identity; no substantive research priority effect. |
| `LOOM_2226_CANON_I_World_History_Frontier_v2.3(1).md` | Governing world/history/frontier canon | Adds the xeno/TMP/Artifact Economy world baseline, preserves intentionally unresolved Strangeness questions, and supports RH-027 plus protected-mystery rules. |
| `LOOM_2226_Canon_Baseline_Manifest_v2.3(1).md` | Governing baseline manifest | Sets the authority/supersession hierarchy; confirms archaeology changed world history but not certified propulsion; defines explicit provisional/unresolved xeno inventory. |
| `LOOM_2226_Synthetic_Speech_Gameplay_Reference_v0.4(1).md` | Gameplay/voice reference | No major research promotion. It is implementation material rather than a load-bearing physics/economics gap. |

---

# 11. Bottom line

The new documents change the shape of the queue more than they change the top of it.

The project’s most valuable unresolved work is now concentrated in four linked bands:

1. **Scaling and constitutive physics:** RH-002, RH-004, RH-024.
2. **Material/thermal/reliability engineering:** RH-005, RH-003, RH-007, RH-026, RH-022.
3. **Cross-class validation:** RH-017 as the practical test harness for the above.
4. **Derived civilization:** RH-006, RH-025, RH-009, RH-018, RH-020 once the engineering inputs are stable enough.

The strongest v1.3 correction to v1.2 is that **torch microphysics belongs back near the top**, while **mis-translation, crew certification, generic transport economics, and archaeological custody have all moved from “invent the system” toward “calibrate/refine the system.”**

The v2.3 xenoarchaeology promotion adds one important new research obligation: **keep TMP scientifically falsifiable and selection-bias-aware without turning it into a universal Great Filter answer.**
