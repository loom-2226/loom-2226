# LOOM 2226 — Earth Demographic & Social Propagation Model v0.3

**Date:** 15 August 2026  
**Status:** PROVISIONAL / PROPAGATION DESIGN CANDIDATE — **not locked canon**  
**Scope:** Earth-origin biological-human demography, 2100–2226 social-demographic modifiers, and the interface required to propagate real cohorts into off-Earth Solar-System settlements.  
**Supersedes for current demographic work:** *LOOM 2226 — Earth Demographic Model v0.2*.  
**Review lineage:** v0.1 working model → Gemini red-team → Claude adversarial reconstruction → v0.2 cohort engine → Claude v0.2 CSV audit → v0.3 social/demographic integration.

> **Core discipline:** social change may alter fertility, migration, family formation, labor geography, medical access, and settlement attractiveness; it does not receive arbitrary population multipliers. If a social factor matters demographically, it must enter through an explicit mechanism.

---

## 1. Executive status

The v0.2 numerical engine survives independent CSV-level audit with no bookkeeping defects. Its current closed-humanity central benchmark remains:

> **8.442 billion biological humans in 2226**

under the central fertility and longevity scenario, before explicit off-Earth migration is propagated.

Central 2226 demographic outputs remain:

- median age: **52.7**;
- aged 65+: **38.95%**;
- aged 80+: **24.36%**;
- aged 100+: **7.66%** (~646M);
- aged 120+: **0.60%** (~50.9M);
- aged 150+: **0.0033%** (~282,000);
- TFR: **1.88**;
- births: ~**75.3M/year**;
- deaths: ~**81.3M/year**;
- natural change: ~**−5.9M/year**.

The central population is therefore still slowly declining in 2226.

### 1.1 What v0.3 changes

v0.3 does **not** invent a new population endpoint. It accepts v0.2 as the current numerical control case and adds the social architecture needed before off-Earth propagation:

1. makes near-universal broad advanced medicine on Earth an explicit setting assumption rather than an interpolation accident;
2. separates biological sex, legal/social gender, reproductive capability, morphology, lineage, and personhood;
3. adopts a jurisdictionally divergent sex/gender regime, with the technological frontier slowly moving toward post-sex reproduction without assuming universal post-sex biology;
4. permits extensive somatic morphology modification while keeping true new biological species rare, deliberate, and consequential;
5. adds ubiquitous immersive XR/VR and robotic telepresence as demographic and settlement variables;
6. distinguishes resident population, transient population, remote effective workforce, synthetic persons, and non-person automation;
7. makes family structure and age of parenthood explicit outputs;
8. specifies the state variables that must be carried when cohorts are propagated from Earth to Luna, Mars, habitats, asteroids, and the outer system.

### 1.2 What remains unfinished

Before production propagation, the engine should still receive:

- the exact UN WPP 2024 single-age × sex 2100 ledger;
- a two-sex biological cohort implementation;
- exact 2100 CBR calibration rather than the current ~1% residual;
- machine-readable outputs for all fertility/longevity sensitivity scenarios, not only the central case.

None of those items currently overturns the ~8.44B control result. They are **production-quality gates**, not evidence that the present trajectory is wrong.

---

## 2. Empirical boundary and model boundary

### 2.1 Empirical launch point

The demographic engine continues to use UN World Population Prospects 2024 as its authoritative boundary condition through 2100.

Current 2100 anchors:

| Quantity | 2100 anchor |
|---|---:|
| Total population | **10.180160751B** |
| TFR | **1.838** |
| Life expectancy at birth | **81.7342 yr** |
| Crude birth rate | **10.808 / 1,000** |
| Crude death rate | **12.075 / 1,000** |
| Median age | **43.1 yr** |
| Population under 15 | **16.5%** |
| Population 65+ | **23.9%** |
| Mean age of childbearing | **~30.21 yr** |

**Primary source:** United Nations Population Division, *World Population Prospects 2024* — https://population.un.org/wpp/

WPP provides age- and sex-disaggregated projections through 2100, including single-year age datasets. The current v0.2 start structure remains a constrained reconstruction until the exact 2100 bulk ledger is ingested.

### 2.2 Model boundary

Everything after the 2100 empirical state is classified as one of:

- **MODEL-DERIVED** — falls out of explicit equations;
- **SETTING-CALIBRATION** — future assumption chosen for testing;
- **CANON-CONSTRAINT** — already established in LOOM;
- **PROPAGATION-DEPENDENT** — cannot be finalized until off-Earth migration and destination demography are simulated.

---

## 3. Numerical demographic kernel retained from v0.2

The annual biological-human cohort engine remains conceptually:

\[
P_{a+1,t+1}=P_{a,t}(1-q_{a,t})
\]

with births:

\[
P_{0,t+1}=B_t
\]

and:

\[
B_t=F_t\sum_a P_{a,t}f_{a,t}
\]

where fertility level and fertility timing are independent controls.

The central scenario remains a modest fertility recovery combined with widening/postponement of childbearing and calendar-time diffusion of longevity medicine.

### 3.1 Central fertility path retained

| Year | TFR | Mean childbearing age | Fertility spread (SD) |
|---:|---:|---:|---:|
| 2100 | 1.838 | 30.21 | 7.0 |
| 2125 | 1.802 | 31.33 | 7.31 |
| 2150 | 1.790 | 32.75 | 7.88 |
| 2175 | 1.815 | 34.63 | 8.81 |
| 2200 | 1.846 | 36.74 | 9.44 |
| 2226 | **1.880** | **39.0** | **10.0** |

These remain **setting calibrations**, not forecasts.

### 3.2 Parenthood-age tail

The central 2226 fertility kernel implies approximately:

- **~11.9% of births** to parents aged 50–60;
- **~1.8% of births** to parents aged 60–75.

This should be treated as a visible setting consequence, not a buried mathematical artifact.

By 2226 it is therefore socially ordinary for:

- first-time parents to be in their 50s;
- substantial sibling age gaps to exist;
- active parents also to be grandparents or great-grandparents;
- inheritance and family succession to be delayed well beyond 21st-century norms.

The exact percentages remain sensitive to the fertility kernel and should be rerun after sex-disaggregation.

---

## 4. Medical-access regime — explicit Earth decision

The v0.2 model drove the `ordinary` medical-access tier to zero by 2226. v0.3 makes the intended interpretation explicit rather than leaving it as an interpolation artifact.

### 4.1 Earth 2226 assumption

> **Broad advanced medicine is effectively universal infrastructure for recognized Earth residents by 2226.**

This means routine access to the mature baseline stack — advanced diagnostics, organ/tissue replacement, programmable immunity, regenerative medicine, sophisticated trauma care, and ordinary neurorepair — is not the principal axis of medical poverty on mature Earth.

### 4.2 Inequality remains substantial

Universal broad medicine does **not** imply equal longevity.

The economically and politically meaningful medical hierarchy shifts upward:

1. **Broad advanced medicine** — effectively universal baseline;
2. **High-end longevity medicine** — unequal access, repeated systemic rejuvenation, premium neural and vascular maintenance;
3. **Extreme sustained rejuvenation** — rare, expensive, invasive, institutionally concentrated.

Thus the earlier LOOM principle survives:

> **material deprivation falls sharply; access deprivation persists.**

The deprived person of 2226 is less likely to lack antibiotics or an organ transplant and more likely to lack repeated premium rejuvenation, elite medical continuity, high-priority intervention, or jurisdictional access.

People outside broad medicine because of deliberate refusal, isolation, religious practice, illegal status, or extreme institutional breakdown should be treated as **exceptional social states**, not as the normal economic `ordinary medicine` tier.

---

## 5. Sex, gender, reproduction, and demographic accounting

LOOM adopts a **jurisdictionally divergent regime** rather than a universal ideological settlement.

### 5.1 Core separation

By 2226 one field cannot usefully represent all of the following:

- biological sex characteristics;
- legal sex classification;
- gender identity;
- reproductive capability;
- current endocrine state;
- current anatomy;
- gestational capability;
- gamete availability;
- morphology;
- biological lineage;
- legal personhood.

The model therefore keeps these concepts separate.

### 5.2 Social direction

On mature Earth, gender transition and substantial somatic modification are medically routine in many jurisdictions and socially unremarkable in much of metropolitan society. Other jurisdictions deliberately preserve stronger biological-sex classifications, traditional family institutions, or restrictions on reproductive and germline intervention.

Mars and some frontier jurisdictions are expected to be more permissive about bodily autonomy, germline intervention, and reproductive engineering, but this is a **regional history variable**, not a universal Martian stereotype to hard-code.

The 21st-century sex/gender debate therefore does not have one global winner. It fractures into questions of:

- bodily sovereignty;
- medical relevance;
- family and parentage law;
- reproductive infrastructure;
- germline intervention;
- sport and other narrow biological classifications;
- jurisdictional authority over bodies.

### 5.3 Demographic implementation

For the production cohort engine, **biological sex remains a necessary accounting variable at the start of the propagation period**, because reproduction in 2100 remains strongly sex-linked.

However, destination fertility should not ultimately be modeled as simply:

> female cohort × age-specific birth rate.

The long-run structure should move toward a reproductive-capability model containing at minimum:

- ova/gamete availability;
- sperm/gamete availability;
- gestational capacity;
- preserved or manufactured gametes;
- assisted-reproduction access;
- family-formation preferences;
- reproductive policy;
- age-specific desire and timing of parenthood.

The degree to which those variables decouple from birth sex is **technology- and jurisdiction-dependent**.

### 5.4 Post-sex frontier — not universal canon

LOOM does **not yet canonize** universal artificial gestation, universal somatic-gamete manufacture, or complete reproductive independence from sex.

Instead:

- mature reproductive technology progressively weakens biological constraints;
- some jurisdictions and frontier institutions may approach genuinely post-sex reproduction;
- the demographic engine retains biological constraints unless a specific technology/history state removes them.

This allows the setting to drift toward post-sex reproduction without assuming the entire species arrived there simultaneously.

---

## 6. Morphology, species identity, and lineage

LOOM permits substantial bodily modification without turning 2226 into a casual landscape of newly evolved fantasy species.

### 6.1 Somatic morphology

By 2226, mature somatic modification can plausibly alter:

- pigmentation;
- hair and eye characteristics;
- facial and skeletal morphology;
- body proportions;
- dentition;
- sensory capability;
- skin and thermal characteristics;
- nonessential appendages or deliberately engineered cosmetic structures;
- selected physiological adaptations.

A person may identify culturally or aesthetically with a nonhuman form and may modify their phenotype accordingly.

That does **not** automatically create a new biological species.

### 6.2 Demographic classification

The population model distinguishes:

- **baseline/ordinary Homo sapiens**;
- **modified Homo sapiens / engineered human lineages**;
- **true reproductively distinct human-derived lineages**, if any are deliberately created;
- **synthetic persons**;
- **non-person automated systems**.

Social identity does not by itself alter biological lineage classification.

### 6.3 True species divergence

A genuinely reproductively isolated human-derived species is possible technologically but should remain:

> **rare, intentional, historically consequential, and canon-significant.**

If such a lineage appears, it must have an explicit origin event, engineering rationale, reproductive compatibility status, legal history, and population ledger. It is not generated casually from aesthetic body modification.

### 6.4 Settlement relevance

Engineered human lineages may become important off Earth where adaptation has a concrete environmental purpose — gravity, radiation, atmospheric chemistry, temperature, circadian cycles, or developmental constraints.

This becomes a **destination-local technology/policy choice** in the propagation engine rather than an Earth-wide population assumption.

---

## 7. Synthetic persons — separate population accounting

Synthetic persons must not be hidden inside either the automation or biological-human population tables.

The propagation model therefore uses at least three top-level population classes:

1. **biological / biologically derived persons**;
2. **synthetic persons**;
3. **non-person automated systems**.

### 7.1 Synthetic population change

Synthetic-person population does not use biological births and deaths by default.

It requires its own processes:

- instantiation;
- continuity rules;
- copying/forking law;
- merger/divergence rules if recognized;
- substrate loss;
- voluntary cessation;
- migration between substrates/bodies;
- legal recognition.

A synthetic instance is not counted as a new person merely because software was copied unless LOOM personhood law says continuity has actually diverged into a new recognized person.

### 7.2 Why this matters for Solar-System population

A habitat may contain:

- 50,000 biological residents;
- 8,000 synthetic persons;
- 2 million non-person industrial agents;
- 200,000 Earth/Mars-based remote operators who are **not residents at all**.

Those categories must never be conflated.

---

## 8. Immersive XR/VR and telepresence

By 2226, immersive extended reality is assumed to be ubiquitous mature infrastructure.

LOOM does **not** assume that most humans abandon physical life. The more useful setting principle is:

> **copyable experience becomes abundant; physical presence, physical agency, and unique location remain scarce.**

### 8.1 Technology layers

The setting allows three broad levels:

1. **Ambient XR** — ordinary visual/auditory informational augmentation integrated into daily life;
2. **full immersive virtuality** — highly convincing multisensory social, educational, work, entertainment, and intimate environments;
3. **deep neural embodiment** — real but more invasive, regulated, and specialized rather than a universal consumer default.

### 8.2 Demographic effects on Earth

VR/XR does not receive a direct fertility multiplier. It enters through explicit behavioral channels:

- relationship formation across physical distance;
- reduced need to migrate for education or knowledge work;
- reduced physical floor-area demand for offices/entertainment;
- increased ability of older or disabled people to maintain active social/professional lives;
- potentially stronger postponement of physical family formation in some cultures;
- increased value of physical authenticity, location, and in-person status goods.

These effects may push fertility in opposite directions and therefore remain scenario-dependent.

### 8.3 Telepresence and industrial population

This factor **does** materially change off-Earth settlement.

A remote specialist may inhabit the sensorium of a robot operating in an asteroid refinery, lunar tunnel, orbital dock, or hazardous reactor complex without physically living there.

The body model must therefore distinguish:

- **resident workforce**;
- **transient/rotational workforce**;
- **remote effective workforce**;
- **autonomous non-person machine capacity**.

This reinforces a major LOOM economic conclusion:

> **industrial output can be enormous while resident population remains small.**

### 8.4 Light-delay constraint

VR does not erase interplanetary geography.

Earth–Moon social presence can be effectively synchronous. Earth–Mars and outer-system interaction cannot be synchronous across ordinary light-speed communications at most configurations.

Consequently, settlements develop distinct social practices around:

- asynchronous presence;
- delayed conversation;
- local synthetic mediation;
- cached shared environments;
- local decision authority.

This gives physical settlement an enduring cultural consequence even when visual/sensory presence is excellent.

### 8.5 Physical authenticity and migration

Cheap virtual experience may reduce some migration motivated only by work or entertainment, while increasing the prestige value of actually living in unique physical places.

Accordingly, the propagation model should never assume that excellent telepresence either:

- eliminates settlement; or
- leaves migration unchanged.

It enters the migration utility function as both a **substitute for physical relocation** and a **multiplier of physical-location prestige/scarcity**.

---

## 9. Family structure in 2226

Long life, delayed childbearing, reproductive technology, gender flexibility, and virtual sociality jointly produce family structures that differ substantially from 2026.

### 9.1 Expected features

The model should allow:

- first parenthood well into the 50s and sometimes later;
- very large sibling age gaps;
- simultaneous parenting and grandparenthood;
- delayed inheritance;
- long-lived multigenerational households or kin networks;
- blended families spanning a century of adult life;
- parentage defined separately as genetic, gestational, social, and legal;
- long-distance relationships sustained virtually without immediate relocation;
- jurisdictional variation in recognition of nontraditional family forms.

### 9.2 Demographic consequence

Family complexity is not itself a population variable. It affects:

- desired completed fertility;
- timing of births;
- household formation;
- migration propensity;
- inheritance timing;
- childcare burden;
- settlement retention.

Those are the channels that should be parameterized regionally.

---

## 10. Revised uncertainty map

The dominant uncertainties now fall into two groups.

### 10.1 Numerical demography

1. fertility preferences after 2100;
2. age-specific fertility timing;
3. diffusion and efficacy of rejuvenation;
4. exact age × sex starting ledger;
5. sex composition of migration streams;
6. destination-specific mortality and reproduction.

### 10.2 Social/institutional modifiers

1. regional reproductive law and family norms;
2. degree of reproductive decoupling from sex;
3. attractiveness of physical migration under excellent telepresence;
4. settlement policy and habitat subsidies;
5. degree of human adaptation / lineage engineering;
6. synthetic-person reproduction/instantiation law;
7. longevity inequality and wealth/institutional entrenchment.

None of these receives an unearned universal point estimate.

---

## 11. Earth 2226 working interpretation

Under the central v0.3 interpretation, Earth in 2226 is:

- home to the overwhelming majority of biological humanity unless propagation proves otherwise;
- old by 21st-century standards but demographically active;
- slowly declining in population under the central closed-system control case;
- characterized by hundreds of millions of centenarians but only hundreds of thousands of 150+ persons under the central medical chronology;
- effectively universal in broad advanced medicine but highly unequal in premium longevity access;
- culturally heterogeneous on sex, gender, reproduction, family, augmentation, and germline policy;
- highly permissive in some jurisdictions and deliberately conservative in others;
- saturated with immersive virtuality without surrendering the economic importance of physical place;
- increasingly able to separate reproduction from traditional biological constraints, but not uniformly post-sex;
- tolerant of extensive somatic modification while treating true species divergence as a major engineered event;
- increasingly shaped by long-lived capital holders and institutional actors whose control may persist for a century or more.

---

# PART II — OFF-EARTH PROPAGATION ARCHITECTURE

## 12. Principle: conserve persons

The Solar-System model must generate actual Earth, Mars, Luna, Belt, and outer-system populations from one conserved ledger.

For biological humans:

\[
P^{Earth}_{a,s,t+1}
=
Survivors^{Earth}_{a,s,t}
+Births^{Earth}_{a,s,t}
-\sum_j M^{Earth\rightarrow j}_{a,s,t}
+\sum_j M^{j\rightarrow Earth}_{a,s,t}
\]

For destination body/habitat \(j\):

\[
P^j_{a,s,t+1}
=
Survivors^j_{a,s,t}
+Births^j_{a,s,t}
+\sum_k M^{k\rightarrow j}_{a,s,t}
-\sum_k M^{j\rightarrow k}_{a,s,t}
\]

System conservation requires every migrant to be debited from one location and credited to another.

**No destination population is ever added on top of the Earth control case.**

---

## 13. Population classes carried by every developed body

Every body/location must be able to carry separate stocks for:

### 13.1 Biological / derived-human residents

- age;
- sex/reproductive-state variables;
- lineage / modification class where relevant;
- longevity-access tier;
- permanent vs transient status.

### 13.2 Synthetic-person residents

- recognized person count;
- continuity/lineage identifier;
- substrate/location;
- permanent vs transient status.

### 13.3 Non-person automation

- industrial agents;
- maintenance systems;
- autonomous transport;
- local AI systems.

These are capacity, not population.

### 13.4 Remote effective workforce

Track separately:

- number of remote human/synthetic operators;
- origin location;
- latency class;
- effective full-time-equivalent contribution.

Remote operators contribute to local economic activity but **not to local population, life-support demand, or births**.

---

## 14. Destination-local demographic state

Each developed body or habitat receives its own annual state vector.

### 14.1 Core demographics

- age × sex/reproductive structure;
- births;
- deaths;
- fertility level;
- fertility timing;
- mortality schedule;
- longevity-access distribution;
- immigration;
- emigration;
- transient population.

### 14.2 Social regime

- gender/legal-sex regime;
- reproductive-technology regime;
- family-law regime;
- germline/augmentation regime;
- synthetic-person regime;
- migration/citizenship regime;
- medical-access regime;
- settlement-growth policy.

### 14.3 Physical capacity

- rated habitat capacity;
- emergency capacity;
- pressure volume;
- radiation shielding;
- food capacity;
- water/volatile capacity;
- power capacity;
- thermal-rejection capacity;
- medical capacity;
- annual construction increment.

Population is constrained by infrastructure:

\[
P^j_t \leq H^j_t
\]

where \(H^j_t\) is sustainable rated habitat capacity.

---

## 15. Migration decision model

Migration should be produced procedurally from competing attractions and costs, not assigned from a desired population target.

A destination's migration pull should depend on a vector rather than one magic score:

### 15.1 Physical/economic factors

- travel burden;
- transport capacity;
- habitat availability;
- employment/ownership opportunity;
- resource boom or industrial role;
- wages/dividends/land access;
- safety;
- environment/gravity;
- medical capability;
- cost of family formation.

### 15.2 Social/political factors

- jurisdictional rights;
- reproductive freedom;
- family policy;
- augmentation/germline freedom;
- synthetic-person recognition;
- taxation/ownership regime;
- cultural fit;
- prestige/frontier identity;
- political/religious community.

### 15.3 Virtuality/telepresence factors

- whether the economic role can be performed remotely;
- communications latency;
- quality of remote embodiment;
- prestige value of physical presence;
- requirement for local legal authority or accountability.

### 15.4 Demographic selection

Migration is age- and sex/reproductive-structure-selective.

Early settlements may have strongly skewed populations. Mature settlements may actively recruit families or underrepresented reproductive cohorts to stabilize local demography.

The propagation engine must therefore move **cohorts**, not just headcounts.

---

## 16. Settlement lifecycle

Population growth should follow the procedural body-development model rather than precede it.

A typical location may pass through:

1. catalogued / remotely characterized;
2. robotic survey;
3. robotic resource operation;
4. permanent automated installation;
5. transient crew support;
6. permanent staffed station;
7. family-capable habitat;
8. established settlement;
9. major port / industrial node;
10. regional population center.

Different axes remain independent. A body may be heavily exploited yet have no residents, or highly populated with little extractive industry.

### 16.1 Population gate

A location does not receive endogenous family growth merely because people visit it.

Permanent births become meaningful only after:

- stable habitation exists;
- pregnancy/child medical care exists;
- long-duration radiation exposure is controlled;
- food/life-support capacity exists;
- residents expect continuity rather than rotation.

This transition should be an explicit historical event.

---

## 17. Interaction with the Solar-System body database

The previously designed body model provides the physical and economic opportunity structure.

### 17.1 Observed layer

JPL / NASA / PDS / USGS data provide:

- identity and orbit;
- size, mass, gravity, rotation;
- atmosphere/environment;
- composition evidence;
- resource probability;
- surface/landing characteristics;
- scientific value.

### 17.2 Derived layer

LOOM derives:

- accessibility;
- industrial suitability;
- habitat suitability;
- logistics value;
- scientific value;
- strategic value;
- hazard;
- competition/substitution from nearby bodies.

### 17.3 Historical layer

Technology era + actor incentives + network effects generate:

- surveys;
- mining;
- infrastructure;
- ports;
- settlement;
- jurisdiction;
- habitat construction.

### 17.4 Demographic layer

Only after habitat/infrastructure history exists does the population engine decide:

- who moves there;
- who stays;
- whether families form;
- how local fertility diverges;
- whether residents adapt biologically;
- how many people can physically be supported.

This preserves the LOOM causal chain:

> **physics → engineering → economics → institutions → migration → demography → history.**

---

## 18. Propagation start date

The full Solar-System population history must start **before 2100**, because LOOM canon already contains permanent cislunar industry and serious Mars settlement in the 2060–2100 period.

Recommended structure:

### Phase A — empirical Earth baseline

Use UN annual Earth/world age × sex data through 2100.

### Phase B — early off-world propagation

Begin debiting real migration cohorts once permanent habitation occurs in canon, likely during the 2060–2100 window.

Migration during this phase is tiny relative to Earth and does not materially alter the UN global total, but it establishes real founding age/sex structures for Luna, Mars, and orbital habitats.

### Phase C — post-2100 endogenous system

From 2100 onward:

- Earth follows the LOOM fertility/mortality engine;
- off-world populations follow destination-local kernels;
- migrants are conserved across locations;
- habitat growth gates settlement growth;
- torch-era transport expands the migration network;
- mature automation/telepresence suppresses resident labor requirements;
- metric travel affects urgency/high-value movement but does not automatically become bulk colonization infrastructure.

---

## 19. Production model tables

The eventual propagation system should minimally contain:

### `population_cohort`

- location_id
- year
- age
- sex/reproductive class
- biological lineage
- longevity tier
- permanent/transient status
- population

### `migration_flow`

- origin_location
- destination_location
- year
- age
- sex/reproductive class
- persons
- migration_type
- actor/program
- cause

### `habitat_capacity`

- location_id
- year
- rated population
- emergency population
- annual construction increment
- limiting subsystem

### `social_regime`

- location_id
- year
- gender/legal-sex regime
- reproductive-tech regime
- germline regime
- family-law regime
- medical-access regime
- synthetic-person regime
- migration policy

### `remote_workforce`

- work_location
- operator_origin
- year
- biological_person_FTE
- synthetic_person_FTE
- latency class
- embodiment mode

### `synthetic_population`

- location_id
- year
- continuity lineage
- recognized persons
- instantiations
- cessations
- migrations

---

## 20. What the model should be able to explain

A successful propagation run must not merely output:

> `Mars population = 43.7M`

It should be able to explain the causal history:

> Mars reached 43.7M because habitat construction accelerated after local pressure-vessel and shielding production became cheap; family immigration replaced early rotational labor migration; Martian reproductive policy raised realized fertility modestly; telepresence kept many industrial specialists off-world-but-nonresident; and the settlement remained constrained by thermal/power/habitat construction rather than by willingness to migrate.

Likewise an asteroid may legitimately end at:

> permanent residents: 86  
> transient crew: 210  
> remote effective workforce: 14,000 FTE  
> autonomous industrial systems: millions  
> annual material throughput: enormous

without contradiction.

---

## 21. Current acceptance envelope

Until propagation is run, use the following only as the **closed-humanity control benchmark**:

| Variable | Current working value |
|---|---:|
| 2226 biological-human population | **8.442B central** |
| modeled current scenario envelope | **~7.7–8.9B** |
| wider longevity sensitivity | **~7.9–9.2B** under central fertility |
| median age | **~52.7** central |
| 100+ population | **~646M** central |
| 150+ population | **~282k** central |
| population direction | **slow decline** |
| broad advanced medicine | **effectively universal on Earth** |
| premium longevity | **unequal** |
| gender/reproductive regime | **jurisdictionally divergent** |
| post-sex reproduction | **frontier / regional, not universal** |
| major somatic modification | **available** |
| true new human species | **rare, deliberate, major historical event** |
| immersive XR/VR | **ubiquitous** |
| remote robotic embodiment | **economically important** |

Do **not** yet state that Earth itself has 8.442B residents in 2226. Off-Earth migration must be debited first.

---

## 22. Promotion gates before Solar-System propagation

### Required

1. ingest exact WPP 2100 single-age × sex ledger;
2. convert biological-human engine to two-sex/reproductive-structure cohorts;
3. close or explicitly document the ~1% CBR calibration residual;
4. export full reproducibility ledgers for all sensitivity cases;
5. establish first permanent off-world population dates from canon chronology;
6. connect the population engine to habitat-capacity outputs from the Solar-System body model.

### Can remain open during first propagation

- exact synthetic-person population;
- full artificial-gestation adoption;
- true engineered species creation;
- detailed jurisdictional gender/family law;
- exact VR effects on fertility preferences;
- final Mars fertility regime;
- exact premium-longevity access distribution off Earth.

Those variables can initially be scenario bands and promoted only when they materially change population history.

---

## 23. Review targets for the next toaster pass

The next adversarial review should specifically attack:

1. whether the v0.2/v0.3 central 8.44B result survives exact WPP sex-age initialization;
2. whether the 2226 fertility kernel's age tail remains coherent in a two-sex model;
3. whether universal broad medicine is internally consistent with Earth political/economic canon;
4. whether gender/reproductive decoupling needs a quantitative fertility effect before 2226;
5. whether VR/telepresence materially changes migration enough to alter expected off-world populations;
6. whether synthetic-person population accounting can be made conservative without inventing personhood law prematurely;
7. whether lineage engineering should affect mortality/fertility on any off-world body before 2226;
8. whether the migration utility framework risks producing unrealistic self-sorting or runaway settlement cascades;
9. whether habitat construction, transport capacity, and remote labor are sufficient to constrain Mars/Belt populations without arbitrary caps;
10. whether the conserved-cohort bookkeeping remains exact once multiple destinations and return migration are activated.

---

## Appendix A — decisions adopted in v0.3

### A1. Medicine

**Adopt:** near-universal broad advanced medicine on Earth by 2226.  
**Do not adopt:** universal premium longevity.

### A2. Sex/gender

**Adopt:** jurisdictional divergence with widespread bodily autonomy in many mature jurisdictions and stronger biological/traditional classifications in others.  
**Direction of travel:** reproductive biology becomes increasingly separable from gender and eventually partly separable from sex, but not uniformly by 2226.

### A3. Morphology/species

**Adopt:** broad somatic morphological freedom.  
**Do not adopt:** casual widespread creation of new human species.  
**Rule:** true reproductive speciation must be deliberate and historically consequential.

### A4. Virtuality

**Adopt:** ubiquitous immersive XR/VR and mature robotic embodiment.  
**Do not adopt:** universal retreat into virtual existence.  
**Economic rule:** virtual abundance reduces some need for physical relocation while increasing the relative scarcity of authentic physical presence and location.

### A5. Population ontology

**Adopt:** biological humans, synthetic persons, non-person automation, transient people, and remote workers are separate accounting classes.

---

## Appendix B — provenance vocabulary

| Label | Meaning |
|---|---|
| **EMPIRICAL** | Direct present-day or UN projection input |
| **SOURCE-DERIVED** | Reconstructed from published source constraints |
| **CANON-LOCKED** | Existing LOOM setting fact |
| **MODEL-DERIVED** | Output of explicit equations |
| **SETTING-CALIBRATION** | Deliberate future assumption |
| **SOCIAL-REGIME** | Jurisdictional/institutional assumption |
| **REVIEW-OPEN** | Must remain revisable |
| **PROPAGATION-DEPENDENT** | Cannot be finalized until off-Earth history is simulated |

The central **8.442B** value remains **MODEL-DERIVED + SETTING-CALIBRATION + PROPAGATION-DEPENDENT**.

---

## Appendix C — review note

The independent v0.2 CSV audit found no bookkeeping bugs in the delivered central ledgers. It corrected the earlier static interpretation of the 150+ population: calendar-time adoption of extreme rejuvenation makes the central ~282,000 figure more defensible than the earlier stationary-life-table estimates in the millions. The audit also identified the 0% `ordinary medicine` endpoint, ~1% CBR calibration residual, uniform within-band 2100 reconstruction, parent-age tail, incomplete sensitivity CSV export, and lack of sex disaggregation as the remaining refinement items. v0.3 converts the first of these into an explicit setting decision and carries the remainder as production gates.

