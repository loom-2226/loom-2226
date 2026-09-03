# LOOM 2226 — Ship Operations & Inherited Courier Canon Compendium v1.0

**Frozen:** 15 August 2026  
**Status:** Consolidated operational/ship reference for LOOM 2226 Solar-System Canon Baseline v1.0

## Authority rule

This compendium reduces project-source sprawl by preserving the current ship mechanics, piloting, courier engineering, HUD and test-flight records in one source. Where it conflicts with **Foundational Canon v1.5** or **Shipbuilding & Engineering Manual v0.7**, those higher-level documents govern. The original section text is retained below with source boundaries so historical provenance is not lost. The Sol & Walter character sheet remains separate character canon.

## Compendium index

1. **Core Mechanics v0.4** — `LOOM_2226_Core_Mechanics_v0.4(1).md`
2. **Ship Building & Piloting v0.3** — `LOOM_2226_Ship_Building_and_Piloting_v0.3(1).md`
3. **Inherited Courier Engineering Record v0.3** — `LOOM_2226_Inherited_Courier_Engineering_Record_v0.3(1).md`
4. **HUD Design Review & Final Standard v0.3** — `LOOM_2226_HUD_Design_Review_and_Final_Standard_v0.3(1).md`
5. **Ship HUD Ephemeris Standard v0.2** — `LOOM_2226_Ship_HUD_Ephemeris_Standard_v0.2(1).md`
6. **Test Flights Master Record v1.0** — `LOOM_2226_Test_Flights_Master_Record_v1.0(1).md`


---

# Source 1: Core Mechanics v0.4

**Original file:** `LOOM_2226_Core_Mechanics_v0.4(1).md`

**LOOM 2226**

**Core Mechanics — Working Draft v0.4**

*Non-proprietary system designed for transparent play by a human or LLM game master • 14 August 2026*

Design target: simple arithmetic at the core; selective crunch where LOOM cares — sensors, relative motion, heat, damage, causal information, translation, crew judgment, and the consequences of uncertainty.

Version 0.4 retains the v0.3 chassis and incorporates the August 2226 LQ-03 qualification campaign and intergalactic recovery audit. The Loom procedure now uses worst-constraint **Integrity Classes** instead of additive transition-state bonuses; keeps topology, observation, route solution, Formation, Commit, Exposure, Transition, Relaxation, Emergence, and Reacquisition causally separate; replaces hard emergence radii with statistical uncertainty; clarifies reciprocal coherence versus directional engineering access; restores explicit Relaxation; and adds chronology/anomaly clock discipline. Blind topology spectroscopy and external Loom-event forensics remain explicitly experimental rather than ordinary rules.

# 1. Core Resolution

All uncertain consequential checks use 2d6 + Attribute + Skill against a Target Number (TN). Margin determines quality. If an action is routine, uncontested, and carries no meaningful cost for failure, do not roll.

2d6 + Attribute + Skill + rare flat modifiers − TN = Margin

| **Margin** | **Outcome**                                                                                             |
|------------|---------------------------------------------------------------------------------------------------------|
| ≤ −3       | Critical Failure — the action fails and creates a genuine causal complication.                          |
| −2 to −1   | Failure / costly failure — no clean success; the established situation determines the cost.             |
| 0 to +2    | Success — intended effect at normal quality/time.                                                       |
| +3 to +5   | Strong Success — extra effect, faster completion, better position, better information, or reduced cost. |
| +6 or more | Critical Success — unusually strong result consistent with what the action could actually accomplish.   |

## 1.1 Boons and Banes

Boons and Banes replace most situational numeric modifiers. Net them first. Then roll extra d6 and keep only two dice:

| **Net state** | **Roll**                      |
|---------------|-------------------------------|
| No Boon/Bane  | Roll 2d6; keep both.          |
| 1 Boon        | Roll 3d6; keep the highest 2. |
| 2 Boons       | Roll 4d6; keep the highest 2. |
| 1 Bane        | Roll 3d6; keep the lowest 2.  |
| 2 Banes       | Roll 4d6; keep the lowest 2.  |

Maximum net effect is normally 2 Boons or 2 Banes. Additional advantages should change fictional position, effect, information quality, time, or resource cost rather than adding more dice. Never write “−2 Bane”: use either “2 Banes” or a flat −2, not both.

## 1.2 Target Numbers and opposed checks

| **Difficulty**  | **TN** | **Use**                                                                                     |
|-----------------|--------|---------------------------------------------------------------------------------------------|
| Routine         | 6      | Meaningful only under pressure or when failure carries a cost.                              |
| Standard        | 8      | Competent professional task under ordinary operational conditions.                          |
| Difficult       | 10     | Requires training, good tools, or favorable conditions.                                     |
| Formidable      | 12     | Specialist work, severe pressure, or poor information.                                      |
| Extreme         | 14     | At the edge of normal professional capability.                                              |
| Beyond envelope | —      | Do not roll unless the fiction provides a mechanism that makes success physically possible. |

For opposed actions, both sides roll normally; higher total wins and the margin between totals determines effect. Use opposed rolls sparingly where an active adversary is genuinely shaping the outcome.

# 2. Attributes

| **Attribute** | **Governs**                                                                                                 |
|---------------|-------------------------------------------------------------------------------------------------------------|
| Physique      | Strength, endurance, injury tolerance, EVA effort, g-load tolerance, melee force.                           |
| Reflex        | Piloting, gunnery, reaction, precision movement, personal-scale evasion.                                    |
| Reasoning     | Engineering, astrogation, sensors, medicine, deduction, analysis, causal forensics.                         |
| Presence      | Persuasion, command, deception, negotiation, reputation and social positioning.                             |
| Composure     | Functioning under fear, pain, shock, uncertainty, traumatic exposure, command pressure, and disorientation. |

Attributes normally range 1–5; 2 is an ordinary adult baseline and 3 represents notable natural capability or extensive adaptation. Composure does not prevent TAAC, TAAM, or anomalous memory from occurring. Exposure determines what happened; Composure determines whether the character can continue to function effectively through or after it.

# 3. Skills and Specialties

| **Skill**           | **Typical specialties**                                              |
|---------------------|----------------------------------------------------------------------|
| Pilot               | Torch, Metric, Shuttle, EVA Maneuvering                              |
| Engineer            | Loom Lattice, Power, Life Support, Fabrication, Thermal              |
| Sensors             | Passive, Active, Signals Analysis, Multimessenger                    |
| Gunnery             | Point Defense, Torpedo, Beam, Drone Weapons                          |
| Combat              | Firearms, Melee, Boarding, Heavy Weapons                             |
| Astrogation         | Loom Route Planning, Metric Cruise, Orbital Navigation               |
| Medicine            | Trauma, Longevity, Neuropsychiatry, Xenobiology                      |
| Causal Forensics    | Provenance Verification, Provenance Forgery, Timeline Reconstruction |
| Anomalous Phenomena | TAAM Documentation, Pattern Analysis, Cross-Domain Analysis          |
| Streetwise          | Frontier, Corporate, Criminal, Station                               |
| Persuasion          | Negotiation, Mediation, Interview                                    |
| Command             | Crew, Tactical, Crisis                                               |
| Zero-G / EVA        | Void Survival, Mobility, Suit Operations                             |

Skills range 0–4: 0 untrained, 1 trained, 2 professional, 3 expert, 4 renowned specialist. A specialty provides 1 Boon when it directly applies; specialties do not stack with themselves.

Anomalous Phenomena never grants supernatural access to hidden truth. It identifies patterns, evidence conflicts, methodological weaknesses, or plausible hypotheses supported by data the character actually has.

# 4. Character Creation — Lifepath

Default creation uses lifepath because LOOM characters should enter play with debts, people, institutions, scars, and incomplete history. Point-buy remains a valid fast alternative.

## 4.1 Career tracks

- Void Service — torch/metric crew, merchant marine, salvage.

- Loom Service — licensed translation crew, courier lines, exploration corps.

- Corporate — certification, fabrication, administration, finance, insurance.

- Frontier / Belt — independent operators, cooperatives, prospecting.

- Military — escort, boarding, security, defense forces.

- Academic / Patternist — research, Loom theory, anomaly documentation.

- Intelligence-Courier — causal arbitrage, information security, fixing, source handling.

- Medical / Augmentation — trauma medicine, longevity, neural systems, field care.

## 4.2 Starting package

- Attributes: distribute 11 points across the five Attributes; minimum 1, maximum 4 at creation without a defining trait.

- Choose 4 career terms by default. Three terms creates an Emerging character; five creates a Veteran.

- Each term grants one career-linked Skill Advance, one Event, and one Connection.

- Choose two Specialties from skills at rank 1+; additional specialties come from terms/events.

- Record at least one Obligation, Rival, Debt, Duty, unresolved Certification issue, or similar entanglement by the end of creation.

## 4.3 Term cost and experience

Extra experience is allowed to be genuinely useful. A five-term veteran knows more than a three-term newcomer; balance comes from history rather than pretending age and experience are free. Each term after the third adds one Entanglement automatically. The third-term character instead begins with one uncommitted Edge: an unused Connection, cleaner legal/financial status, extra downtime flexibility, or similar advantage chosen with the GM.

| **2d6 Event** | **Result**                                                                                                                          |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------|
| 2–3           | Serious injury or loss — gain a Scar, Debt, Rival, medical history, or institutional complication.                                  |
| 4–5           | Career setback — lose standing, gain an Obligation, or create a hostile Connection.                                                 |
| 6–8           | Routine service — gain +1 additional career-linked Skill Advance or useful Credential.                                              |
| 9–10          | Notable success — gain a Connection and context-specific Reputation.                                                                |
| 11–12         | Major turning point — gain rank, signature item, rare Credential, or strong Connection, plus an Entanglement tying it to the world. |

Void/Loom/Intelligence-Courier Connections may be generated as people who dealt with the inherited ship’s previous owner rather than the PC directly. This seeds “someone else’s unfinished life” during chargen.

## 4.4 Identity, personhood, and sovereignty tags

Organic, synthetic, augmented, distributed, or baseline-adjacent identity is not a universal stat modifier. Record identity and legal state as descriptive tags that matter only when the local law, institution, contract, prejudice, or architecture makes them relevant.

| **Tag axis**          | **Examples**                                         | **Mechanical use**                                                            |
|-----------------------|------------------------------------------------------|-------------------------------------------------------------------------------|
| Personhood            | recognized / disputed / unadjudicated                | Determines legal standing, not consciousness.                                 |
| Causal individuality  | singular / forked lineage / distributed continuation | Tracks non-substitutability and continuity disputes.                          |
| Cognitive sovereignty | certified / partial / externally writable / unknown  | Determines who can legally or technically alter cognition.                    |
| Independent agency    | severable / federated / collective / compulsory mesh | Matters when consent and disconnection are contested.                         |
| Certification         | current / lapsed / forged / disputed / revoked       | Evidence at last audit; can affect contracts, ports, insurers, and prejudice. |

Scrutiny is a scene condition created by local sentiment, not a permanent build tax. The GM may set Scrutiny to None, Watchful, Hostile, or Coercive. It changes NPC behavior, access, inspection, and stakes; it should not silently impose a universal −X to everything a synthetic or augmented character does.

# 5. Damage, Armor & Condition Tracks

## 5.1 Personal wounds

Characters use four consequence boxes rather than hit points: Winded → Hurt → Wounded → Down. Damage has Severity 1–3. Armor, cover, and weapon penetration modify Severity before boxes are marked.

| **State** | **Effect**                                                                                      |
|-----------|-------------------------------------------------------------------------------------------------|
| Winded    | No action penalty; the character has taken a meaningful hit, shock, exertion, or minor injury.  |
| Hurt      | 1 Bane on strenuous physical actions until treated or the scene ends.                           |
| Wounded   | 1 Bane on all actions; movement is limited; further serious injury is dangerous.                |
| Down      | Out of effective action. Begin the Trauma Clock unless the cause clearly makes death immediate. |

Severity 1 marks one box, Severity 2 marks two, Severity 3 marks three. Armor typically reduces incoming Severity by 1 if its protection exceeds the weapon’s Penetration; overmatch or called shots can bypass protection. A hit cannot be reduced below Severity 0 unless the fiction clearly supports complete protection.

## 5.2 Trauma and death

A Down character has a three-segment Trauma Clock. At the end of each round in which a lethal condition remains untreated, mark one segment. At three segments the character dies or suffers irreversible information loss unless the fiction clearly establishes another outcome. Medicine can stabilize, slow, suspend, or reverse much more than 21st-century medicine; it cannot restore information that has actually been destroyed.

## 5.3 Ship subsystem tracks

| **Subsystem**          | **Degraded**                       | **Systemic**                         | **Critical**                                                             |
|------------------------|------------------------------------|--------------------------------------|--------------------------------------------------------------------------|
| Hull                   | localized breach / handling issue  | major structural compromise          | breakup or mission-kill risk                                             |
| Torch / Maneuver Drive | reduced performance                | major thrust/efficiency loss         | drive offline or unsafe                                                  |
| Metric Drive           | reduced envelope                   | unstable/limited operation           | metric capability offline                                                |
| Sensors                | one modality impaired              | pipeline stages lost / blind arcs    | major blindness or no valid firing solution                              |
| Loom Lattice           | reduced confidence / certification | translation envelope sharply reduced | Loom capability offline; post-commitment damage invokes failure taxonomy |
| Life Support           | local degradation                  | environmental clock begins           | crew survival emergency                                                  |
| Weapons                | specific mount degraded            | mount/group disabled                 | magazine, power, or local structural hazard                              |

Damage is assigned to a specific subsystem by called shot, exposed geometry, or causal effect. Critical Loom-lattice damage while operating under torch does not cause a mystical disappearance; it makes Loom translation unavailable or unsafe. Only damage during/after commitment can invoke reversion, displacement, domain failure, or non-return risk.

# 6. Tactical Space Combat

Space combat state = Range Band + Relative Vector + Orientation + Sensor Stage + Heat/Signature + Subsystem Condition.

## 6.1 Range bands

| **Band** | **Meaning**                                                              |
|----------|--------------------------------------------------------------------------|
| Close    | boarding, collision, point-defense saturation, knife-fight beam geometry |
| Short    | short tactical engagement / rapid missile time-of-flight                 |
| Medium   | normal decisive engagement band                                          |
| Long     | sensor quality and missile geometry dominate                             |
| Extreme  | contact shaping, long-baseline sensing, disengagement and interception   |

## 6.2 Relative vector

Each important ship pair or formation pair has one relative-motion state: Closing, Matched, or Opening. Orientation does not change this state. At the end of Movement, Closing shifts range one band nearer; Opening shifts one band farther; Matched holds range. Pilot burns change the relative vector one step per normal maneuver: Opening \<-\> Matched \<-\> Closing. High-energy burns may change two steps but add Heat, Signature, and campaign-level reaction-mass cost.

Pointing somewhere is not traveling there.

## 6.3 Orientation and fire arcs

Ships track Fore, Port, Starboard, and Aft orientation relative to the current opponent. Rotation changes what arc is presented and which mounted systems bear; it does not change trajectory. Handling determines how much rotation can be performed without spending the primary Pilot action. Light craft rotate cheaply; large hulls rotate slowly.

## 6.4 Sensors and the information fight

| **Stage**       | **Combat effect**                                                             |
|-----------------|-------------------------------------------------------------------------------|
| CONTACT         | Existence/rough bearing known. No weapon-quality solution.                    |
| DETECTION       | Bearing and range band known. Attacks possible with 2 Banes; no called shots. |
| CLASSIFICATION  | Hull class / likely configuration known. Attacks with 1 Bane.                 |
| TRACK           | Reliable position/vector estimate. No sensor penalty; called shots enabled.   |
| FIRING SOLUTION | Weapon-quality track. 1 Boon on attacks; called shots at normal difficulty.   |

Each Sensors action compares Reasoning + Sensors against a TN set by target signatures, geometry, range, latency, and countermeasures. Use the roll margin:

| **Margin**       | **Pipeline effect**                                                                            |
|------------------|------------------------------------------------------------------------------------------------|
| Critical failure | Lose one stage or accept a plausible false-track/hypothesis complication.                      |
| Failure          | No advancement; poor information may still update the probability envelope.                    |
| Success          | Advance one stage.                                                                             |
| Strong success   | Advance two stages, or one stage plus a useful classification/detail.                          |
| Critical success | Advance two stages and gain a specific information advantage consistent with the sensors used. |

Targets can degrade or break tracks through geometry, cold running, decoys, sensor-specific EW, line-of-sight interruption, drone deception, or radical maneuver. The pipeline is not an automatic five-round staircase.

## 6.5 Heat, radiator posture, and signature

| **Heat**   | **Effect**                                                        |
|------------|-------------------------------------------------------------------|
| 0 Nominal  | Normal operation.                                                 |
| 1 Warm     | No direct penalty; thermal reserve begins to matter.              |
| 2 Hot      | 1 Bane on heat-sensitive engineering; some systems must throttle. |
| 3 Critical | Risk of Systemic damage, automatic throttling, or emergency dump. |

Radiators have three postures: Open (best cooling, strong IR signature), Restricted (balanced), and Closed/Retracted (low external heat rejection; Heat accumulates). Cold-running systems store the bill rather than erase it.

- Cold Sink — move 1 Heat into finite Thermal Reserve; signature falls if other sources permit.

- Emergency Heat Dump — remove up to 2 Heat through radiator bloom, open-loop coolant, or expendable sink; become thermally obvious and possibly consume coolant/sink capacity.

- Load Shed — shut down nonessential power loads to reduce future heat generation; it does not make existing heat disappear.

## 6.6 Turn sequence

- 1\. Initiative — roll once at engagement start: 2d6 + Reflex + Pilot (or relevant command role). Surprise and stale information can add Boons/Banes.

- 2\. Sensor Phase — update tracks, drones, EW, and observed-vs-predicted state.

- 3\. Movement Phase — choose burn, change Relative Vector, resolve automatic Closing/Opening range shift, then rotate as Handling permits.

- 4\. Action Phase — attacks, repair, drone control, boarding preparation, power/thermal actions, special maneuvers.

- 5\. Heat / Signature Phase — apply weapon/burn heat, radiator rejection, cold-sink use, and resulting signatures.

- 6\. State Update — GM/LLM prints the compact tactical state block before the next round.

## 6.7 Attacks and weapon effect

A ship attack uses 2d6 + Reflex + Gunnery against Defense TN 8, modified primarily by Boons/Banes from range, vector, sensor stage, evasive burn, weapon geometry, and damage. Weapons have Range, Base Severity, Penetration, Heat, Ammunition/Power, and Arc tags. Attack margin can increase effect: Strong Success may add +1 Severity or a positional effect; Critical Success may add +1 Severity plus a system-specific consequence if physically plausible.

Called shots require TRACK or FIRING SOLUTION. They target a specific subsystem; armor, orientation, and exposed geometry can add Banes or reduce Severity.

## 6.8 Signature maneuvers

| **Role**        | **Maneuver**                                                                                                                                                                                                            |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Pilot           | Evasive Burn — add 1 Boon to defense until next Movement; add Heat/Signature and consume burn budget.                                                                                                                   |
| Pilot           | Vector Break — spend a high-energy burn to change Relative Vector by two steps; add 1 Heat and a major kinematic signature.                                                                                             |
| Gunner          | Called Shot — target a specific subsystem; requires TRACK or better.                                                                                                                                                    |
| Sensor Operator | Decoy / Ghost Hypothesis — use a specific active channel, drone, transponder/provenance exploit, or compromised sensor pathway to create a false hypothesis. Passive optical/IR reality cannot simply be “jammed away.” |
| Engineer        | Cold Sink / Emergency Heat Dump / Load Shed — manage heat debt causally.                                                                                                                                                |
| Loom Officer    | Threaded Retreat — begin emergency formation during combat. Formation remains observable and risky; commitment still requires a captain decision.                                                                       |

# 7. Tactical Ground / Boarding Combat

Ground and boarding combat uses named Zones connected by adjacency rather than a measured grid. This preserves tactics — cover, choke points, line of effect, suppression, vacuum, hazards, movement under fire — without requiring centimeter-scale geometry.

## 7.1 Zones and cover

| **Cover** | **Effect**                                                                                         |
|-----------|----------------------------------------------------------------------------------------------------|
| None      | No positional modifier.                                                                            |
| Light     | Attacker has 1 Bane on ranged attacks from outside the zone.                                       |
| Heavy     | Attacker has 2 Banes; line of effect may require an action or maneuver to establish.               |
| Concealed | Not a valid CONTACT until searched or revealed; once located, concealment may still impose 1 Bane. |

## 7.2 Ground turn sequence

- 1\. Initiative — 2d6 + Reflex; roll once at encounter start unless circumstances radically reset.

- 2\. Move — one adjacent zone per Move; crossing a contested breach, vacuum boundary, kill zone, or heavy obstacle may cost an extra action.

- 3\. Act — attack, assist, suppress, use equipment, breach, hack, stabilize, negotiate, or perform a skill action.

- 4\. Reactions — a character with a held/unspent reaction may Overwatch, dive for cover, close a hatch, or perform another declared interrupt.

- 5\. Environment — resolve decompression, fire, radiation, toxic atmosphere, gravity changes, structural failure, and other clocks.

## 7.3 Attacks, armor, and suppression

Ranged attacks use 2d6 + Reflex + Combat(Firearms/Heavy Weapons) against Defense TN 8, with cover, range, movement, visibility, and suppression expressed as Boons/Banes. Melee normally uses Physique or Reflex + Combat(Melee) against an opposed defense when both combatants are actively engaged.

Weapons use the same Severity 1–3 and Penetration grammar as ship attacks. Armor reduces Severity when it is rated against the attack; vacuum suits are not automatically combat armor. Suppressive-capable weapons can make a zone Suppressed: characters exposed while moving or acting there test Composure or take 1 Bane and lose their reaction; suppression changes behavior rather than dealing automatic damage.

## 7.4 Signature maneuvers

| **Role**                  | **Maneuver**                                                                                                                                                                                              |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Marine / Void Soldier     | Breach — force access into a defended zone; Strong Success degrades Heavy Cover to Light for allies this round.                                                                                           |
| Medic                     | Field Stabilize — stop a Down character’s Trauma Clock; Strong Success may move them to Wounded if treatment plausibly allows.                                                                            |
| Hacker / Causal Forensics | Lockout — disable or subvert a specific automated defense, credential, door, comms path, or provenance-controlled system.                                                                                 |
| Face / Commander          | Command Presence — use a reaction to grant an ally 1 Boon when the order, relationship, and situation make it credible.                                                                                   |
| Anomalous Phenomena       | Pattern Analysis — identify a statistically unusual correlation, contradiction, or overlooked relationship in available evidence. It never reveals objective facts the character has no causal access to. |

# 8. Loom Translation Procedure

**Prepare → Understand → Form → Display Risk → Decide → Commit → Expose → Transition → Relax → Emerge → Reacquire.**

The captain chooses commitment; the dice do not accidentally press the button. Skill can discover, model, and exploit physics. Skill cannot create a Loom relationship that objective reality does not contain.

For a certified route, use the compact procedure below. For a novel or uncertified route, prepend the topology-discovery stack in Section 19.

| **Step** | **Procedure** | **Poor result / consequence** |
|---|---|---|
| 1. Navigation / Route Solution | Reasoning + Astrogation(Loom Route Planning) uses existing route evidence, destination state, momentum mapping, and Geometric Admissibility. | Wider uncertainty, poorer arrival-state mapping, no certifiable solution, or need for more evidence. |
| 2. Formation / Coherence | Reasoning + Engineer(Loom Lattice) establishes the actual ship/domain state. Hardware damage or configuration limits remain physical facts even after an excellent roll. | Delay, Heat, lower margin, safe abort, or a worse Integrity Class. |
| 3. Risk Display | GM/AI states Integrity Class, return status, route burden, destination uncertainty, lattice/thermal/bank margins, geometry warnings, certification recommendation, clock state, and material unknowns. | No roll. This is captain-visible information. |
| 4. Commit Decision | Captain chooses Abort / Continue / Override / Commit. BLACK states cannot Commit. RED states require an explicit override. | No roll. Before commitment, competent systems normally permit safe abort. |
| 5. Translation Exposure | Roll the independent Exposure layer. Resolve what physically/cognitively occurred before testing how well anyone copes with it. | TAAC/TAAM or other exposure only when actually generated; no automatic weirdness. |
| 6. Transition Integrity | Resolve the crossing from the established Integrity Class using Section 19. | CLEAN, SUCCESS, DEGRADED, MAJOR, or CRITICAL. |
| 7. Relaxation | Clean/ordinary crossings usually relax automatically. Degraded surviving domains may require Reasoning + Engineer(Loom Lattice). | Residual lattice/thermal/domain problems persist; Relaxation never rewrites the primary crossing result. |
| 8. Emergence | Resolve endpoint uncertainty statistically from route, Navigation, Formation, transition quality, and the route model. | Position/velocity residuals, displacement, or failure-scaled uncertainty as established by the crossing. |
| 9. Reacquisition | Reasoning + Sensors establishes where the vessel actually is. | Blind interval, delayed fix, need for observation time, or competing hypotheses. Prediction is not truth. |

TAAC and TAAM are not resisted by Composure. If the physical transition state crosses an exposure threshold or an off-nominal event occurs, the GM resolves translation exposure separately from the character’s willpower. Composure may then determine immediate operational function, panic control, documentation discipline, or recovery under stress.

On a strange crossing, the culturally standard first action remains: **“Write it down before you talk to anyone.”** This records evidence; it does not grant prophecy or special information.

If ship proper time and independently established external chronology diverge, immediately begin dual-clock tracking under Section 15.3. Do not infer a controllable time-travel mechanic merely because the clocks disagree.
# 9. Reputation, Certification & Scrutiny

LOOM has no universal social score. Track reputations and credentials by context: insurer, port, carrier, government/security, crew, broker, corporate, frontier, scientific, criminal, and so on.

## 9.1 Scrutiny

Scrutiny is a situational state when identity, augmentation, synthetic status, certification, or local ideology becomes operationally relevant.

| **State** | **Default effect**                                                                                         |
|-----------|------------------------------------------------------------------------------------------------------------|
| None      | No special friction beyond ordinary social context.                                                        |
| Watchful  | Inspection, extra questions, provenance checks, delays; refusal can escalate stakes.                       |
| Hostile   | Service denial, escort, discriminatory contract terms, checkpoint encounters, surveillance.                |
| Coercive  | Forced “voluntary” audit, detention, expulsion, or violence; this is an encounter, not a passive modifier. |

A character may conceal visible augmentation, synthetic tells, affiliations, or certification status if the fiction permits. Concealment never makes identity ontologically different; it trades capability, access, or convenience for lower exposure. Presenting openly preserves full capability and accepts the local social stakes.

# 10. Advancement

Knowledge can be accelerated. Competence must be practiced. Judgment must be earned.

| **Currency** | **Earned by**                                                                                                                      | **Spent on**                                                                            |
|--------------|------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Knowledge    | Money + downtime: courses, model access, tutoring, study, libraries.                                                               | Unlock a new skill at rank 1, learn theory, add a specialty when prerequisites are met. |
| Competence   | Logged consequential use, supervised practice, drills, and completed work using the skill.                                         | Raise an existing skill rank after enough marks and time to consolidate.                |
| Judgment     | Consequential decisions under uncertainty where the character bears real responsibility and learns from outcome. Rare, GM-awarded. | Choose bounded Veteran Knacks; never raw uncapped permanent +1 bonuses.                 |

## 10.1 Veteran Knacks

- Operational Skeptic — once per scene, ask what assumption in the current plan is least supported by available evidence; GM answers from what the character can reasonably assess.

- Loom Judgment — when comparing multiple viable translation solutions, receive a clearer statement of uncertainty, not hidden truth.

- Command Judgment — when a subordinate raises an operational objection, identify whether it concerns safety, capability, morale, law, or personal stakes before deciding.

- Combat Judgment — once per engagement, re-order initiative between two allied actions after observing the current tactical state.

- Contract Judgment — before signing, flag one clause whose operational consequence is most likely to matter if the deal goes bad.

- Forensic Judgment — distinguish the weakest provenance link in a causal chain without automatically knowing whether it was forged.

Veteran Knacks tell experienced characters where to look and which question to ask. They never create impossible knowledge.

# 11. Downtime & Economy

Downtime is continuous simulation with exception management. Resolve four categories in order; routine tasks can be compressed, while any category can expand into scenes if consequences matter.

| **Step**                | **Question**                                                                                                                           |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| 1\. Synchronize Context | What information, law, markets, messages, certifications, and personal news have actually reached us? How causally old is it?          |
| 2\. Resupply & Repair   | What needs fuel, reaction mass, coolant, feedstock, spares, inspection, certification, treatment, or yard authority?                   |
| 3\. Contracts           | What work is actually available given current information age, reputation, route state, risk, insurance, and relationships?            |
| 4\. Crew Business       | Pay, leave, disputes, requests, relationships, obligations, training, recruitment, private goals, and whether anyone intends to leave. |

Contracts are generated from structured elements: job type × causal-information age × route/operational risk × legal/insurance status × payoff structure × complication. Mature Sol markets are efficient; frontier profit comes from information, timing, access, relationships, and willingness to carry risk — not random merchant-price tables.

# 12. Human / LLM GM Procedure

The engine is designed to reduce the player’s need to police the GM. The GM maintains objective state separately from player-known state and publishes a compact state block whenever tactical or operational decisions depend on it.

## 12.1 Tactical state block

| **Field**        | **Example**                                                    |
|------------------|----------------------------------------------------------------|
| Range / Vector   | MEDIUM / CLOSING                                               |
| Orientation      | Player FORE to target; target PORT presented                   |
| Sensor state     | Player TRACK; enemy DETECTION; predicted enemy state age 1.8 s |
| Heat / radiators | Heat 2 HOT; radiators RESTRICTED; thermal reserve 1/3          |
| Damage           | Sensors Degraded; Port radiator Systemic                       |
| Known weapons    | 2 torpedo cells; beam mount probable; PD confirmed             |
| Crew exceptions  | Engineer occupied with radiator fault; gunner ready            |
| Uncertainty      | Enemy exact remass and aft weapon status unknown               |

## 12.2 GM discipline

- State causally relevant facts before asking for a consequential player decision when those facts would be available to the character.

- Do not alter objective outcomes for drama, protection, punishment, or genre expectation.

- Do not reveal hidden objective state through Anomalous Phenomena, TAAM, Patternism, or narrative tone.

- When a system is routine, compress it. When something becomes exceptional, open the relevant subsystem and show the variables that matter.

- Every complication should arise from a rule, established state, adversary decision, uncertainty, or legitimate random resolution — not a need to “make the scene interesting.”

# 13. Playtest Defaults

These values are intentionally provisional and exist to make v0.4 playable immediately. They should be tuned from actual play rather than debated indefinitely in abstraction. The structural rules promoted from LQ-03 are more important than the exact calibration constants.

| **Item**              | **Default**                                                    |
|-----------------------|----------------------------------------------------------------|
| Net Boon/Bane cap     | 2                                                              |
| Defense TN            | 8 before situational factors                                   |
| Skill range           | 0–4                                                            |
| Attribute range       | 1–5; creation normally 1–4                                     |
| Personal wound states | Winded / Hurt / Wounded / Down                                 |
| Trauma Clock          | 3 segments                                                     |
| Ship subsystem damage | Degraded / Systemic / Critical                                 |
| Space range bands     | Close / Short / Medium / Long / Extreme                        |
| Relative vector       | Closing / Matched / Opening                                    |
| Heat                  | 0 Nominal / 1 Warm / 2 Hot / 3 Critical                        |
| Sensor pipeline       | Contact / Detection / Classification / Track / Firing Solution |

# 14. Operational Travel & Environmental Exposure

Travel is not resolved by a generic random-encounter roll. The GM models the physical domain the vessel is actually crossing. Most exposure checks produce quiet conditions or routine operational texture; serious events are rare, and anomalous Loom phenomena are never smuggled into an ordinary environmental table.

## 14.1 Exposure sequence

Resolve meaningful travel exposure as: Occurrence → Hazard Domain → Magnitude → Vessel Exposure → Consequence. Rarity and severity are separate. A common event can become serious when it intersects damaged equipment; a rare event may be harmless if detected early and mitigated well.

| **2d6** | **Exposure level** | **Default meaning**                                             |
|---------|--------------------|-----------------------------------------------------------------|
| 2       | Exceptional        | Historically extreme or mission-defining physical event.        |
| 3       | Very Rare          | Serious emergency potential.                                    |
| 4–5     | Uncommon           | Usually creates a decision, resource cost, or check.            |
| 6–8     | Common             | Routine environmental effect; often automated or informational. |
| 9–12    | Quiet              | No player-facing event; background physics still exists.        |

Use this spectrum as a playtest default, not a claim that every domain has identical real-world probabilities. A mature regional profile may replace the bands with evidence-based weights.

## 14.2 Exposure frequency

Do not roll once per arbitrary “day” if exposure differs materially. The GM chooses checkpoints based on duration, region transition, maneuver phase, and vessel vulnerability. Long exposure, open radiators, degraded shielding, dense traffic, or unusual geometry can justify additional checks; short benign transits may justify none.

## 14.3 Physical hazard domains

| **Domain**                          | **Typical subdomains**                                                                                                                      |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Interplanetary                      | Meteoroids; solar energetic particles; solar wind; galactic cosmic radiation; sensor/navigation environment; hardware-environment coupling. |
| Industrial / port space             | Traffic conflicts; debris; mining ejecta; failed transponders; construction; tug/cargo operations.                                          |
| Planetary magnetosphere             | Charged particles; plasma; magnetic disturbance; radiation belts; sensor degradation.                                                       |
| Atmospheric                         | Wind shear; turbulence; precipitation; haze; icing/deposition; electrical activity; thermal loading.                                        |
| Cryogenic surface                   | Extreme cold; traction; volatile precipitation; material embrittlement; local weather; contamination.                                       |
| Small body / microgravity           | Rebound; anchoring failure; ejecta; irregular gravity; dust; accidental escape; thruster contamination.                                     |
| Close-stellar / ultra-hot planet    | Stellar radiation; particle flux; thermal loading; plasma/magnetic effects; extended atmosphere; stellar activity.                          |
| High-density orbital infrastructure | Traffic-system conflict; certification mismatch; cyber/provenance attack; cargo accident; docking fault; cascading automation failure.      |

Regional profiles should be grounded in real astronomical/engineering data where available, then extrapolated to 2226. Anomalous/TAAM phenomena use their own exposure procedure and do not appear merely because an environmental roll was low.

# 15. Navigation, Piloting & Real Ephemerides

When a real Solar System body is used, the GM should use the campaign date and physically plausible ephemerides or an explicitly declared game-grade approximation. Navigation targets the destination’s future state, not its current apparent position. Route time, geometry, gravity, and environmental domains therefore change with date.

## 15.1 Separate the jobs

| **Task**                           | **Primary mechanic**                              |
|------------------------------------|---------------------------------------------------|
| Trajectory/orbit design            | Reasoning + Astrogation                           |
| Sensor fix / site characterization | Reasoning + Sensors                               |
| Executing consequential maneuver   | Reflex + Pilot                                    |
| Drive/lattice operation            | Reasoning + Engineer                              |
| Routine certified automation       | No roll unless failure carries a meaningful cost. |

Pilot specialties are vehicle/envelope specific. Pilot(Torch) does not automatically grant a Boon for atmospheric shuttle flight. Astrogation specialties likewise distinguish Metric Cruise, Orbital Navigation, and Loom Route Planning.

## 15.2 Automation doctrine

Competent infrastructure should be competent. Routine orbital docking, certified traffic corridors, ordinary course corrections, and normal flight-control compensation usually require no roll. The player rolls when uncertainty, degraded information, unusual geometry, damage, adversarial action, or a meaningful operational choice creates consequence.

## 15.3 Dual-clock and chronology discipline

Normally one mission clock is sufficient. If a Loom anomaly, relativistic operation, data-quality conflict, or reacquisition result creates a material chronology discrepancy, track three separate fields:

| **Field** | **Meaning** |
|---|---|
| SHIP MET | Mission Elapsed Time / proper-time history experienced and logged by the vessel. |
| EXT EPOCH | Best independently established external epoch in the relevant reference time system. |
| CAUSAL OFFSET | The measured or inferred difference between the two histories, with uncertainty and provenance. |

Do not overwrite one clock with another. Do not silently convert an unexplained chronology discrepancy into a normal Loom feature. Closed causal loops remain physically inadmissible, and no player may deliberately target a time offset unless later campaign/canon mechanics explicitly establish a physical method.

# 16. Planetary Descent, Landing & Resource Operations

Planetary operations are a distinct domain rather than a single Pilot check. Use the body’s actual gravity, atmosphere, temperature, terrain, and weather model where known.

## 16.1 Descent sequence

Orbital Departure → Entry Interface → Atmospheric/Aerodynamic Braking (if any) → Terminal Navigation → Site Selection → Final Approach → Landing. Airless bodies skip atmospheric phases. Each phase is rolled only when consequential.

## 16.2 Site selection

Landing site quality is information before it is piloting. Sensors identifies surface state and hazards; Astrogation chooses a viable approach geometry; Pilot executes the final maneuver. A failed site-selection check should normally create uncertainty, delay, a poorer site, or higher landing TN rather than making the pilot spontaneously incompetent.

## 16.3 Resource operations

Resource collection follows Survey → Access → Transfer/Excavation → Processing → Storage → Load Planning → Departure. “The resource exists” is not the same as “propellant-grade material is aboard.” Composition, contamination, cryogenic handling, anchoring, processing equipment, added mass, and ascent performance all matter when relevant.

# 17. Small-Body & Microgravity Operations

For very small moons and asteroids, landing may be easier than maintaining a useful natural orbit. The GM should distinguish a true local orbit from a matched trajectory around the primary with relative station keeping.

- Low escape velocity makes rebound and accidental escape credible hazards.

- Anchoring systems—ice screws, harpoons, microspines, active down-thrust, or equivalent—may be mission-critical.

- Crew movement can require tethers or restrained locomotion when an energetic jump or equipment recoil could create escape risk.

- Extraction changes the local momentum problem: excavated material, tool reaction, and thruster plume effects can matter more than weight.

Do not turn microgravity into slapstick by default. Use the physics to create operational choices; reserve rolls for actions where the consequence matters.

# 18. Automated Orbital Ports & Sovereign Interfaces

Dense core-system infrastructure uses high automation. Traffic control proposes time-dependent corridors; the vessel independently verifies them; the captain or authorized system consents. Station automation controls access to station infrastructure, not unrestricted access to a sovereign mind or vessel.

## 18.1 Docking contract

Automated docking establishes a mutually authenticated, narrow contract covering approach envelope, allowable forces, abort conditions, required telemetry, docking hardware, and exactly which commands each side may issue. Routine docking under a valid contract is not a skill check.

Failures become interesting when certification, provenance, traffic state, cyber compromise, damaged hardware, or conflicting automation makes the contract uncertain. This ties infrastructure play directly to the setting’s personhood and sovereignty doctrine.

# 19. Loom Topology Discovery & Translation v0.4

**Core principle:** skill cannot create topology. Loom play separates what physically exists from what observers can measure, what a crew can successfully exploit, what state the ship can actually form, and what the captain chooses to risk.

A usable A→B route does not imply a usable B→A route. This is an **engineering-access** rule. The setting does not require the deeper relational substrate itself to be fundamentally one-way.

## 19.1 The topology and translation stack

| **Layer** | **Question** | **Who/what resolves it** |
|---|---|---|
| Reality | Does an admissible relationship physically exist? | Hidden universe/GM state; never modified by character skill. |
| Survey | Can available instruments resolve it? | Reasoning + Engineer(Loom Lattice) or Sensors as appropriate. |
| Experiment | Can changed baseline, probes, or additional observations reduce uncertainty? | Equipment, time, execution, and resulting evidence. |
| Solution | Can the crew construct an exploitable directional route from the evidence? | Reasoning + Astrogation(Loom Route Planning). |
| Formation / Coherence | Can this ship in this configuration establish and hold the required bounded state? | Reasoning + Engineer(Loom Lattice), constrained by real hardware/state. |
| Risk Display | What does the captain legitimately know before Commit? | GM/AI; no roll. |
| Commit | Do we actually go? | Captain/player decision; never an accidental dice result. |
| Translation Exposure | What physical/cognitive exposure occurs? | Independent Exposure roll; Composure does not prevent occurrence. |
| Transition Integrity | How does the committed physical crossing resolve? | Integrity Class + independent transition roll. |
| Relaxation | Does the surviving domain return cleanly to ordinary local operation? | Automatic on clean crossings; Engineer(Loom Lattice) when degraded. |
| Emergence | How accurately does realized state match the predicted endpoint/state? | Statistical uncertainty informed by route/Nav/Formation/transition quality. |
| Reacquisition | Where are we, actually? | Reasoning + Sensors; local evidence replaces carried prediction. |

## 19.2 Provisional objective-topology table

For an uncertified reverse or novel candidate, the following 2d6 table remains a **playtest default**, not a claim that the universe literally runs on 2d6. Roll secretly once and retain the result as objective state. Repeated surveys do not reroll reality unless the fiction establishes that topology itself has changed.

| **2d6** | **Physical topology / accessibility candidate** |
|---|---|
| 2 | No admissible relationship; pathological or misleading measurements may exist. |
| 3–4 | No usable direct relationship for the modeled endpoint family. |
| 5–6 | Marginal or transient candidate. |
| 7–8 | Admissible but difficult candidate. |
| 9–10 | Good admissible candidate. |
| 11 | Strong/coherent candidate. |
| 12 | Exceptional topology; potentially scientifically important. |

The hidden topology result is **not** a skill check. A Critical Success cannot turn M33 into a road if no usable relationship exists.

## 19.3 Failed surveys do not erase roads

A failed Topology Survey means the crew cannot resolve the physical state with current evidence. It does not mean the relationship is absent.

To try again, change the evidence state: extend observation, reposition, establish a new baseline, use a better instrument, deploy distributed probes, search another endpoint family, or accept a larger uncertainty envelope. Do not spam-reroll unchanged conditions.

## 19.4 Probe doctrine and causal isolation

A probe can prove from the departure side that it established coherence and entered translation. Without an independent FTL information channel, the crew cannot immediately know whether it emerged successfully.

Certified routes therefore depend on accumulated historical traversal evidence, returned probes, destination-side infrastructure, or later causal observation—not merely on a clean departure event.

A probe whose arrival is unobserved is **not** automatically lost or destroyed. “Non-return” is an observational classification.

## 19.5 Reciprocal coherence, directional engineering access

Keep two concepts separate:

- **Relational coherence:** the deeper measured relationship between endpoint states, which appears approximately reciprocal to current precision.
- **Operational Loom separation / route burden \(\chi_{A\rightarrow B}\):** the effective vessel-and-state-specific burden of making the A→B crossing work.

Operational \(\chi\) can include origin geometry, destination geometry, requested arrival-state mapping, vessel domain, mass distribution, lattice capability, power/bank/thermal margins, route-data age, and uncertainty. Therefore:

\[
\chi_{A\rightarrow B} \neq \chi_{B\rightarrow A}
\]

may be operationally true even if the underlying relationship is approximately reciprocal.

Record, survey, and certify each direction independently. Do not describe this bookkeeping rule as proof that the deep substrate is an ontological one-way graph.

## 19.6 Integrity Class — replace additive TSI

Do **not** sum a pile of correlated +1/+2 modifiers into a Transition State Index. LQ-03 demonstrated that this double-counts healthy conditions and can mathematically erase rare failure tails.

Assess the meaningful physical constraints:

- Domain / certified mass and configuration
- Formation result
- Thermal state
- Lattice condition / coherence margin
- Bank / power availability
- Geometric Admissibility
- Route / solution confidence

The **worst meaningful constraint** sets the Integrity Class unless the fiction gives a specific physical reason otherwise.

| **Class** | **Meaning** | **Commit rule** |
|---|---|---|
| GREEN | Healthy, physically admissible, inside certification with normal margin. | Normal captain Commit. |
| AMBER | Degraded or reduced-margin but still within an allowed operating envelope. | Commit permitted after explicit risk display. |
| RED | Physically admissible but outside normal certification or with a serious known degraded state. | Explicit captain override required. |
| BLACK | No physically coherent committed solution exists under current state. | **No Commit. No override.** Change the state or abort. |

Excellent operator skill can improve a controllable state, solution, or Formation result. It cannot simply relabel damaged AMBER hardware as pristine GREEN without a causal repair/configuration change.

## 19.7 Risk Display and Commit

Before Commit, the GM/AI presents the captain-visible state:

- Integrity Class and the constraint(s) setting it
- operational \(\chi_{A\rightarrow B}\) or route-quality band
- return / reverse-route status
- destination uncertainty and Geometric Admissibility
- lattice condition and wear
- thermal / bank / power margin
- route-data age and provenance
- current SHIP MET / EXT EPOCH if chronology matters
- material unknowns and certification recommendation

The captain then chooses **Abort / Continue preparation / Override (RED only) / Commit**.

BLACK is physics, not bureaucracy. No social authority or die roll can override it.

## 19.8 Translation Exposure

| **2d6** | **Translation exposure** |
|---|---|
| 2 | Exceptional |
| 3 | Very Rare |
| 4–5 | Uncommon |
| 6–8 | Common |
| 9–12 | Quiet |

Exposure is independent of route success. Quiet means no player-facing anomalous event beyond ordinary transition effects.

TAAC, TAAM, synchronicity, apparent agency, or other strangeness is never awarded merely because the scene is important. Resolve what physically happened first; Composure governs functioning, documentation discipline, and recovery afterward.

## 19.9 Transition Integrity

After explicit Commit, roll 2d6 on the current Integrity Class.

| **2d6** | **GREEN** | **AMBER** | **RED** |
|---|---|---|---|
| 2 | Tail Check | MAJOR | CRITICAL |
| 3–4 | SUCCESS | DEGRADED | MAJOR |
| 5–6 | SUCCESS | SUCCESS | MAJOR |
| 7–8 | SUCCESS | SUCCESS | DEGRADED |
| 9–11 | CLEAN | CLEAN | CLEAN |
| 12 | CLEAN | CLEAN | CLEAN |

For a GREEN natural 2, roll 1d6:

- 1 → MAJOR
- 2–6 → DEGRADED

Outcome meanings:

- **CLEAN:** crossing completes with ordinary expected transition behavior.
- **SUCCESS:** crossing completes; no failure family is invoked, but ordinary costs/uncertainty still apply.
- **DEGRADED:** crossing completes through the intended relationship, but transition quality worsens emergence and/or leaves engineering work.
- **MAJOR:** invoke the failure-family resolver.
- **CRITICAL:** invoke the failure-family resolver with severe consequences appropriate to the established state.

This table preserves a rare physical tail without making certified GREEN travel into roulette.

## 19.10 Major/Critical failure-family resolver

Use this only after a MAJOR or CRITICAL Transition Integrity result.

| **2d6** | **Failure family** |
|---|---|
| 2 | Domain decoherence |
| 3–4 | Reversion |
| 5–8 | Destination displacement |
| 9–10 | Mis-translation |
| 11–12 | Surviving destination-side failure with serious recovery demand |

Definitions:

- **Domain decoherence:** the bounded physical domain loses integrity after commitment; consequences follow actual structure/thermal/biological state.
- **Reversion:** the domain resolves back toward the origin-side neighborhood or origin relationship.
- **Destination displacement:** the intended relationship is retained, but emergence error is failure-scaled beyond the ordinary envelope.
- **Mis-translation:** the domain resolves through a *different physically admissible relationship*. This is not a giant Cartesian miss around the intended destination.
- **Surviving destination-side failure:** the ship emerges into a physically survivable but seriously degraded or hard-to-reacquire state.

The resolver does not instantly generate “non-return.” If no later observation establishes the vessel’s fate, **Non-return** is the resulting observational classification.

The resolver also does not automatically generate a chronology shift. Any chronology anomaly requires separate campaign physics/evidence under Section 19.14.

## 19.11 Emergence uncertainty — statistical, not hard-radius

A predicted POS95 or VEL95 is a confidence statement, not a hard wall.

For a simple isotropic qualification model:

\[
\Delta\mathbf r \sim \mathcal N(0,\sigma_r^2 I)
\]

\[
\Delta\mathbf v \sim \mathcal N(0,\sigma_v^2 I)
\]

with approximately:

\[
R_{95}\approx2.795\sigma_r
\]

\[
V_{95}\approx2.795\sigma_v
\]

so:

\[
\sigma_r=\frac{R_{95}}{2.795},\qquad
\sigma_v=\frac{V_{95}}{2.795}
\]

A GM/LLM may use an actual normal/Maxwell sampler or an equivalent calibrated table. **Do not** sample `0..R95` and call R95 the maximum.

Navigation and Formation affect different causal layers. A strong Navigation result improves mapping/targeting. A strong Formation result improves how faithfully the ship realizes the mapped relationship. Transition quality can widen the envelope again.

For v0.4 playtest calibration only:

### Navigation factor \(f_N\)

| **Navigation margin** | **\(f_N\)** |
|---|---|
| +6 or more | 0.70 |
| +3 to +5 | 0.85 |
| 0 to +2 | 1.00 |
| −1 to −2 | 1.40 |
| ≤ −3 | 2.00 / normally uncertified |

### Formation factor \(f_F\)

| **Formation margin** | **\(f_F\)** |
|---|---|
| +6 or more | 0.85 |
| +3 to +5 | 0.92 |
| 0 to +2 | 1.00 |
| −1 to −2 | 1.25 |
| ≤ −3 | 1.60 |

### Transition factor \(f_I\)

| **Transition** | **\(f_I\)** |
|---|---|
| CLEAN | 1.00 |
| SUCCESS | 1.00 |
| DEGRADED | 1.25 |

Then a working covariance model is:

\[
\Sigma_E=f_N^2 f_F^2 f_I^2 \Sigma_0
\]

These factors are calibration knobs, not fundamental Loom physics. Replace them when better playtest/statistical models exist.

## 19.12 Relaxation

Relaxation is a real physical phase. It is not flavor text and not another opportunity to reroll the crossing.

| **Crossing state** | **Relaxation** |
|---|---|
| CLEAN | Automatic unless a separately established subsystem fault makes it consequential. |
| SUCCESS | Automatic under ordinary conditions. |
| DEGRADED | Reasoning + Engineer(Loom Lattice), TN 8. |
| MAJOR with surviving domain | Reasoning + Engineer(Loom Lattice), TN 10. |
| CRITICAL with surviving domain | Reasoning + Engineer(Loom Lattice), TN 12. |

A failed Relaxation check creates persistent lattice, thermal, calibration, power, or domain-recovery consequences consistent with the state. It does not convert a mis-translation into the intended destination or undo displacement.

## 19.13 Reacquisition

Reacquisition establishes local truth.

Use Reasoning + Sensors against destination familiarity, available references, sensor health, and environmental conditions. A familiar certified endpoint may resolve quickly. An unknown or extragalactic environment may require staged observation rather than one magic roll.

Possible stages include:

- exclude expected local frame;
- establish stellar/galactic/cosmological class;
- build distance indicators and relative geometry;
- generate competing catalog hypotheses;
- collect an observation arc;
- confirm absolute position.

Cepheids, TRGB/SBF-like indicators, galaxy-field geometry, pulsars, redshift structure, and other tools are evidence with real observation-time requirements. Skill can interpret evidence; it cannot make a variable star complete its period faster.

## 19.14 Chronology Exclusion and chronology anomalies

Closed causal loops remain physically inadmissible. Candidate solutions implying:

\[
A\prec B,\quad B\prec C,\quad C\prec A
\]

have no stable committed solution.

Ordinary v0.4 failure tables do **not** include selectable forward/backward time travel.

If a dedicated campaign event establishes a discrepancy between ship proper-time history and independently established external epoch:

1. record **SHIP MET**;
2. record **EXT EPOCH** and its provenance;
3. record **CAUSAL OFFSET** and uncertainty;
4. preserve all raw clock/navigation/field evidence;
5. do not assume the offset is reproducible, targetable, or a normal property of mis-translation.

Backward targeting and closed-loop exploitation remain prohibited unless the Foundational Canon is explicitly revised.

## 19.15 Experimental option — blind topology spectroscopy

The LQ-03E/MT recovery suggested that a sufficiently capable Loom-metrology system may detect persistent relational structure without first supplying a named endpoint. This is **experimental mechanics**, not ordinary capability for every vessel.

If a campaign establishes that the ship can attempt it, use the following evidence ladder:

0. no coherent relational response  
1. persistent candidate resonance  
2. candidate relationship family  
3. endpoint-correlated solution  
4. exploitable directional route  
5. certified route

A successful blind survey does not identify every endpoint automatically. Observation time, instrument sensitivity, false positives, catalog completeness, baseline changes, and local environment still matter. Exact calibration remains open.

## 19.16 Experimental option — external Loom-event forensics

Departure/arrival metrology may sometimes support statements such as:

- probable event family;
- ship/domain scale band;
- architecture family;
- event quality;
- recognizable lattice signature.

It **cannot** provide causally unearned live remote telemetry.

When comparing a local Loom transient with electromagnetic observations of a distant source, keep the EM light-travel age explicit. Similarity can motivate a common-physics hypothesis; it cannot assign the transient a remote event time merely because the patterns look related.

Exact significance values, correlations, or mass estimates require an actual calibrated model or synthetic/observed dataset. If no such model exists, report qualitative confidence instead of fake precision.
# Appendix A. Sol & Walter Playtest Record — August 2226

The following tests are design evidence, not immutable setting history. They record what the v0.3 procedures produced and which rules were retained because they generated useful, physically grounded play.

## A.1 Ceres → Titan: environmental-domain transit

| **Phase**           | **Exposure** | **Domain**                 | **Result**                                                                         |
|---------------------|--------------|----------------------------|------------------------------------------------------------------------------------|
| Ceres departure     | Common       | Industrial traffic         | Minor departure-plane adjustment; automated, no roll.                              |
| Metric cruise day 1 | Uncommon     | Solar energetic particles  | Nonstandard route choice; Astrogation succeeded strongly, small delay/energy cost. |
| Cruise day 2        | Quiet        | —                          | No player-facing event.                                                            |
| Cruise day 3        | Common       | Solar-particle persistence | Background elevated flux; no action required.                                      |
| Saturn approach     | Uncommon     | Magnetosphere / plasma     | Active ranging selected; minor traffic correction resolved by Pilot.               |

Lesson retained: environmental events can persist across phases; common events often remain informational; regional subdomains create more believable consequences than a single random-encounter table.

## A.2 Titan descent and Ligeia Mare surface operation

Titan was treated as a distinct planetary environment: low gravity, dense atmosphere, haze, cryogenic surface conditions, and methane-bearing weather. Descent separated site sensing, approach geometry, and final piloting. Surface exposure produced light methane precipitation without turning weather into a disaster. Resource sampling demonstrated the Survey → Access → Transfer → Processing → Storage → Load Planning chain.

Lesson retained: real planetary conditions should change which skills matter. Dense atmosphere and low gravity can make aerodynamic descent forgiving while cryogenic materials, visibility, traction, and resource handling become the harder problems.

## A.3 Nix: small-body operations

Nix demonstrated that an irregular, extremely low-gravity body may favor Nix-relative station keeping on a Pluto-barycentric matched trajectory over a casual conventional orbit. Surface operations emphasized anchoring, rebound, tethers, tool reaction, and accidental escape. Water ice served as the resource target.

Lesson retained: “orbit,” “land,” and “walk” must be interpreted through local gravity rather than Earth intuition.

## A.4 Earth orbital starport

Earth docking was intentionally routine. Automated traffic management supplied a time-dependent corridor; the ship independently verified it; a narrow authenticated docking contract controlled the interface. No Pilot roll was required.

Lesson retained: highly developed infrastructure should remove routine friction. The interesting failures are certification, provenance, cyber compromise, traffic conflict, damaged hardware, or cascading automation—not making elite crews roll to park every time.

## A.5 Nix → WASP-76b: first Loom translation

| **Stage**               | **Playtest result**                                                                     |
|-------------------------|-----------------------------------------------------------------------------------------|
| Route Solution          | 16 vs TN 10 — Critical Success; χ refined from 0.630 to 0.628.                          |
| Coherence Establishment | 16 vs TN 12 — Strong Success; lattice wear +0.3%.                                       |
| Translation Exposure    | 9 — Quiet; no anomalous event.                                                          |
| Emergence               | Mediocre independent result; ~46,800 km position error and ~11.4 m/s velocity residual. |
| Destination Environment | Uncommon; elevated stellar particle flux; approach delayed for shielding/sensor margin. |
| Orbital Astrogation     | 17 vs TN 10 — Critical Success; high actively maintained observation trajectory.        |

Lesson retained: excellent route and engineering rolls improve the envelope but do not erase emergence uncertainty. Translation Exposure must be rolled independently; the first jump did not receive mandatory “weirdness.”

## A.6 WASP-76 → Nix: topology discovery and asymmetric return

| **Step**                | **Playtest result**                                                              |
|-------------------------|----------------------------------------------------------------------------------|
| Hidden Reality          | 2d6 = 8: direct reciprocal edge physically exists, but is difficult.             |
| Initial Topology Survey | 9 vs TN 12: failure; edge not resolved despite existing.                         |
| Improved Survey         | Repositioning + distributed probes; 16 vs TN 12: Strong Success.                 |
| Measured reverse edge   | χ ≈ 0.81, uncertified; materially worse than outbound χ 0.628.                   |
| First probe attempt     | Coherence stalled; safe automatic abort.                                         |
| Route refinement        | 17 vs TN 12: Strong Success; χ refined to 0.803; emergence prediction tightened. |
| Pathfinder              | Successfully entered translation; arrival unknowable from departure side.        |
| Crewed Coherence        | 16 vs TN 14: Success; lattice wear +0.8%.                                        |
| Translation Exposure    | 11 — Quiet.                                                                      |
| Emergence               | ~108,000 km position error; +39 m/s velocity residual.                           |
| Reacquisition           | Pluto, Charon, Nix acquired; pathfinder later detected ~71,000 km away.          |

Lesson retained: Reality → Survey → Experiment → Solution → Formation → Risk Display → Commit → Exposure → Transition → Relaxation → Emergence → Reacquisition works as a full frontier-Loom loop. Skill cannot create topology; failed observation does not prove absence; probes provide evidence without providing impossible FTL confirmation; operational access and effective χ can differ by direction even when deeper coherence is approximately reciprocal.

## A.7 Rules promoted from playtest

- Environmental hazard tables are regional and domain-specific, with rarity separated from consequence.

- Routine competent automation does not require dice.

- Planetary descent separates sensing, astrogation, piloting, and engineering/resource handling.

- Small-body operations track anchoring, rebound, and station keeping explicitly when consequential.

- Topology is objective hidden state; surveys observe rather than create it.

- Unchanged failed surveys cannot be spam-rerolled; players must change evidence or method.

- Operational Loom access is directional; effective χ is recorded per direction without asserting that the deep substrate itself is fundamentally one-way.

- Translation Exposure and Emergence are independent resolution layers.

- No automatic high-strangeness event is awarded for narrative importance.

- No FTL probe acknowledgment exists; arrival knowledge remains causal.

# Appendix B. LQ-03 Qualification & Mis-Translation Playtest — August 2226

This appendix is design evidence. Campaign discoveries described here are not automatically universal setting canon.

## B.1 LQ-03 qualification matrix

| **Test** | **Condition** | **Result** | **Rule evidence** |
|---|---|---|---|
| LQ-03A | Healthy / nominal | PASS | GREEN travel can remain robust without eliminating a rare tail. |
| LQ-03B | Degraded Formation hardware | PASS | Excellent operators do not make degraded hardware physically pristine. |
| LQ-03C | Poor Navigation | PASS | Navigation widens endpoint uncertainty without automatically destabilizing a healthy domain. |
| LQ-03D | Thermal/lattice degraded | PASS / DEGRADED | Off-nominal crossings can generate real engineering work without becoming catastrophe. |
| LQ-03E | RED experimental route | PASS / DEGRADED | RED may Commit only by explicit captain override when still physically admissible. |
| LQ-03E/FI | Injected MAJOR failure | Destination displacement | Failure families should be tested deliberately, not awaited randomly. |
| LQ-03F | BLACK physical state | Commit rejected | Physics cannot be overridden. |
| LQ-03G | Chronology-invalid loop | No solution / no Commit | Chronology Exclusion is a hard physical gate. |

## B.2 Mechanics promoted by the audit

- Replace additive TSI with worst-constraint Integrity Class.
- Keep Reality, Survey, Solution, Formation, Commit, Exposure, Transition, Relaxation, Emergence, and Reacquisition separate.
- Use statistical emergence uncertainty; POS95/VEL95 are not hard maxima.
- Navigation and Formation affect different causal parts of the uncertainty model.
- Skill cannot create topology.
- BLACK cannot Commit.
- Routine certified docking under a valid contract does not require a skill roll.
- Preserve game time; use SHIP MET and EXT EPOCH separately when chronology diverges.

## B.3 Mis-translation recovery — what is *not* promoted

The LQ-03E/MT branch produced a campaign-specific extragalactic mis-translation and an approximately +166-day chronology anomaly.

Promoted structural lesson:

- a mis-translation is another admissible relationship, not a gigantic Cartesian miss around the intended destination.

Not promoted:

- a universal “extragalactic” failure table;
- a normal chronology-residual table;
- selectable time skipping;
- numerical χ bands derived from one recovery;
- guaranteed blind topology spectroscopy;
- exact external-detectability or alien-forensics coefficients.

## B.4 First-contact campaign result

The playtest continuity established high-confidence non-human technological evidence in M31 and probable Loom-class engineering using the same broad underlying physics through a different implementation.

This is **Campaign Truth for that continuity**. It is not a generic Core Mechanics assumption that every campaign must discover aliens in M31, or discover aliens at all.

The strongest mechanics lesson is epistemic: raw evidence, causally available timestamps, model-derived interpretation, and strategic disclosure must remain separate.

# Quick Reference

| **System**     | **Core mechanic**                                                                                        |
|----------------|----------------------------------------------------------------------------------------------------------|
| Any check      | 2d6 + Attribute + Skill vs TN; margin determines quality.                                                |
| Boon/Bane      | Roll extra d6; keep highest or lowest 2; normally cap at 2 net.                                          |
| Space state    | Range + Relative Vector + Orientation + Sensor Stage + Heat/Signature + Damage.                          |
| Space movement | Closing shifts nearer; Opening shifts farther; burns change vector; rotation does not change trajectory. |
| Sensors        | Margin advances/degrades information pipeline; counterplay can break tracks.                             |
| Damage         | Severity 1–3 marks condition boxes; armor/penetration modify Severity.                                   |
| Ground combat  | Zone map + cover + Severity + suppression + environmental clocks.                                        |
| Loom           | Reality/Survey (if novel) → Solution → Formation → Risk Display → Commit → Exposure → Transition → Relaxation → Emergence → Reacquisition. |
| TAAC/TAAM      | Exposure is physical; Composure governs functioning, not whether anomaly occurs.                         |
| Advancement    | Knowledge buy / Competence practice / Judgment earns bounded Veteran Knacks.                             |
| Identity       | Personhood, individuality, sovereignty, agency, and certification are contextual tags, not one stat.     |
| GM/LLM         | Maintain objective state separately; publish compact player-known state before consequential choices.    |

END OF WORKING DRAFT v0.4



---

# Source 2: Ship Building & Piloting v0.3

**Original file:** `LOOM_2226_Ship_Building_and_Piloting_v0.3(1).md`

**LOOM**

**2226**

**SHIP BUILDING & PILOTING**

Engineering, Flight Dynamics & Flight Director — Working Design System
v0.3

*Build the machine. Fly only what the machine can actually do.*

| **DESIGN STATUS** v0.3 incorporates the August 2226 SFAP/LQ-03 flight-test audit into the coupled ship-building and piloting framework. A maneuver is legal only when installed hardware, current mass state, force/torque geometry, structure, crew, thermal state, reaction mass, sensors and configuration can actually produce it. The Flight Director converts player intent into physically valid solutions; it does not grant abstract maneuver points or silently violate the ship design. |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 1. Purpose, Scope & Design Philosophy

This document turns the setting canon and core mechanics into a
repeatable ship-design and piloting system. It preserves the staged
engineering sequence - define the hull, install mobility and power, add
mission systems, then reconcile the whole design - and adds a Flight
Director that derives maneuver options from the resulting hardware and
current operating state. The player commands intent; the ship obeys
physics.

| **CORE PRINCIPLE** A LOOM ship is a set of physical budgets that have to agree: mass, volume, thrust, energy, heat rejection, endurance, people, mission systems, and - for Loom-capable vessels - the configured translation domain. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 1.1 Three realism tiers

| **Tier**                        | **Always model directly**                                                                                                                                                                      | **Why**                                                                                                                          |
|---------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| A - Physical backbone           | Mass (t), volume (m^3), thrust (N/MN), acceleration (m/s^2 or g), exhaust velocity (km/s), delta-v (km/s), electrical power (MW), stored energy (GJ/TJ), waste heat (MW), radiator area (m^2). | These quantities create real tradeoffs and are easy to calculate.                                                                |
| B - Engineering abstractions    | MMOD protection, combat protection, habitability, maintenance burden, reliability, signature, sensor quality, automation, certification.                                                       | Real systems are multidimensional; one honest band is better than fake precision.                                                |
| C - Speculative LOOM technology | Metric field performance, Loom domain limits, lattice margin, topology metrology and translation banks.                                                                                        | Use explicit fictional bridges but force them to pay real mass, power, heat, configuration, maintenance and certification costs. |

## 1.2 Two views of the same ship

- Engineering Ledger: the detailed build record. It contains the actual
  mass, volume, power, heat and performance numbers used by the
  simulation.

- Captain Card: the player-facing operational summary. It exposes
  acceleration, delta-v, reserves, heat state, endurance, sensor
  capability, protection, payload and drive condition without requiring
  constant spreadsheet work.

| **GM RULE** The detailed ledger exists so the universe stays causal. The player should only be shown the variables that matter to an actual decision. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------|

# 2. Global Accounting Model

Every installed system writes to a common ledger. The first-pass builder
requires only four hard engineering quantities from every component;
other fields are added when relevant.

| **Field**                   | **Unit**                       | **Use**                                                                                 |
|-----------------------------|--------------------------------|-----------------------------------------------------------------------------------------|
| Mass                        | tonnes                         | Adds to dry/wet mass, acceleration, delta-v, structure and Loom domain mass.            |
| Internal volume             | m^3                            | Consumes pressure-hull, systems, tank or cargo volume.                                  |
| Power                       | MW continuous / MW peak        | Must fit the relevant operating-mode power budget.                                      |
| Waste heat                  | MW                             | Must fit radiator, heat-storage or open-loop cooling capacity.                          |
| External envelope           | m / m^3, if relevant           | Changes silhouette, vulnerable area and configured Loom translation envelope.           |
| Crew attention              | watch / specialist requirement | Determines minimum expertise and normal staffing, not just headcount.                   |
| Consumables                 | t, kg, units or crew-days      | Ammunition, reaction mass, fusion fuel, coolant, life support, spares.                  |
| Certification / maintenance | band                           | Describes inspection, parts, repair and insurer burden rather than physical capability. |
| Clock / provenance           | epoch + source + method        | Keeps game time, ephemeris source, propagation method and causal chronology auditable.  |
| Capital / operating cost    | TBD SCU model                  | Tracked later once the setting economy is calibrated; not invented merely to fill a worksheet.             |

## 2.1 Mass states

**M_wet = M_dry + M_reaction + M_consumables + M_cargo + M_passengers**

- Dry mass includes structure, installed systems, empty tanks, fixed
  shielding, radiators, drives, interiors and installed small-craft
  interfaces.

- Wet mass is the ship as it actually departs. Acceleration and delta-v
  are always evaluated from the current mass state, not a brochure
  number.

- Every conventional burn debits the appropriate reaction-mass store. The next maneuver uses the new mass. A narrated burn that does not alter the ledger is not complete engineering.

- Multi-use mass is counted once. A tonne of water can simultaneously be
  shielding, thermal sink, life-support reserve and potential reaction
  mass - until the captain consumes it and loses those other functions.

## 2.2 Volume states

- Pressurized volume: crewed/accessible internal volume at operating
  pressure.

- Systems volume: machinery, reactors, avionics, field hardware and
  access clearances.

- Tank volume: reaction mass, water, coolant, fusion reactants and other
  bulk stores.

- Payload volume: internal cargo, passengers, labs, vehicles and mission
  modules.

- Configured translation envelope: the smallest certified Loom domain
  that encloses the ship in its translation configuration. Deployed
  radiators, booms, external cargo and docked craft can enlarge it.

**v0.3 audit rule:** local gravity, moving-target ephemerides and clock advancement are part of the physical state when they can change a decision. Exact-looking telemetry must be model-earned; otherwise use a bounded estimate or TBD.

# 3. Ship Design Sequence

| **Step** | **Design stage**                       | **Primary question**                                                                                 |
|----------|----------------------------------------|------------------------------------------------------------------------------------------------------|
| 0        | Mission & design point                 | Define what the ship must do before choosing hardware.                                               |
| 1        | Hull, structure & protection           | Choose geometry, pressure structure, debris/radiation protection and atmospheric capability.         |
| 2        | Local propulsion & torch               | Install maneuvering systems and define thrust/exhaust-velocity performance.                          |
| 3        | Metric & Loom systems                  | Add subluminal metric capability and/or a translation domain, banks, lattice and metrology.          |
| 4        | Power & energy storage                 | Size electrical generation, pulse banks and survival power by operating mode.                        |
| 5        | Reaction mass, fuel & endurance        | Add tanks and consumables; derive delta-v and autonomous duration.                                   |
| 6        | Thermal control                        | Size radiator area, thermal storage, cold sinks and emergency heat rejection.                        |
| 7        | Command, automation & computing        | Define control stations, autonomy, redundancy and cyber/sovereignty boundaries.                      |
| 8        | Sensors, communications & provenance   | Install apertures, active/passive sensors, comms, navigation, secure carriage and custody systems.   |
| 9        | Mission systems, weapons & small craft | Install what makes the hull a courier, warship, surveyor, miner, hospital, yacht, etc.               |
| 10       | Crew & staffing                        | Derive required expertise, minimum watch crew, normal crew and surge complement.                     |
| 11       | Habitation & life support              | Allocate living/work volume, life support, medical, radiation shelter and escape provisions.         |
| 12       | Cargo & payload                        | Use the remaining mass/volume for paying payload, stores, vehicles and passengers.                   |
| 13       | Finalize & certify                     | Reconcile mass, volume, performance, power, heat, endurance, Loom envelope and legal/insurer status. |

# 4. Step 0 - Mission & Design Point

The builder starts with a mission envelope, not a hull size. A ship that
cannot state its design point is not ready to be optimized.

| **Design-point field**   | **Examples / questions**                                                                                             |
|--------------------------|----------------------------------------------------------------------------------------------------------------------|
| Primary role             | Courier, patrol, exploration, liner, tanker, tug, survey, mining, research, hospital, intelligence, yacht.           |
| Crew / passengers        | Normal crew, maximum crew, passenger count, synthetic/biological mix.                                                |
| Independent endurance    | Days, weeks or months without port services.                                                                         |
| Payload target           | Mass and volume simultaneously; include secure data, samples, vehicles or mission packages.                          |
| Normal-space performance | Desired sustained acceleration, maximum acceleration, delta-v reserve and docking agility.                           |
| Metric requirement       | None; limited; routine; high-performance. State required c-fraction, duration, acquisition/collapse assumptions and certification evidence. |
| Loom requirement         | None; crew-rated translation; survey/pathfinder; heavy domain; high-cycle courier.                                   |
| Operating environments   | Deep space, dense orbital infrastructure, dust/debris, radiation, atmosphere, surface landing, strong-field science. |
| Protection doctrine      | Civilian survivability, hardened exploration, armed merchant, military combat.                                       |
| Signature doctrine       | Normal commercial, low-observable, reconnaissance/intelligence, deliberately conspicuous.                            |
| Certification target     | Mainstream insured commerce, government experimental, military, frontier uncertified.                                |

| **DEFAULT** LOOM v0.2 uses free-form real mass and volume, not fixed hull classes. Future reference frames can speed design, but they will be templates rather than rules that forbid intermediate sizes. |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 5. Step 1 - Hull, Structure & Protection

## 5.1 Hull families

| **Family**                 | **Best at**                                                                       | **Tradeoff**                                                                                |
|----------------------------|-----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| Axial / tower hull         | Torch ships; thrust-axis decks; tanks and machinery stacked along load path.      | Longer translated envelope and greater external area than the most compact form.            |
| Compact pressure hull      | Loom craft, habitats, protected command cores, low surface-area/volume ratio.     | Harder engine/radiator integration; poor atmosphere unless specifically shaped.             |
| Distributed / truss        | Haulers, tankers, mining, modular mission craft, huge radiators.                  | Vulnerable, larger Loom envelope, more complex mass distribution.                           |
| Atmospheric / lifting hull | Repeated planetary entry, aerobraking and surface access.                         | Dead mass and volume for heat shielding, aero structure, landing gear and shape compromise. |
| Hybrid                     | Most real ships: compact crew core + axial propulsion + external tanks/radiators. | More design bookkeeping, usually the most believable answer.                                |

## 5.2 Protection is layered, not one Armour score

1.  Pressure/structural hull - keeps shape and pressure under thrust,
    docking loads and damage.

2.  MMOD/debris protection - sacrificial spaced layers, Whipple-derived
    concepts, local hardening and standoff where practical.

3.  Radiation protection - hydrogen-rich material, water, food, polymer
    and dedicated storm-shelter mass placed around people and sensitive
    systems.

4.  Combat protection - additional spaced structure, armor,
    compartmentation and protected critical systems. This is separate
    from ordinary debris shielding.

5.  Atmospheric protection - heat shielding, aerodynamic structure and
    landing hardware where required.

| **NASA ANCHOR** NASA treats micrometeoroid/orbital-debris risk and radiation as separate design problems. MMOD protection uses impact testing and shield design; deep-space radiation favors low-atomic-number, hydrogen-rich materials such as water and polyethylene. LOOM keeps those layers physically distinct. |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 5.3 Areal-mass accounting

**M_layer = sigma_A x A_protected**

*sigma_A is the chosen areal density (kg/m^2); A_protected is the
protected surface area.*

v0.2 does not yet prescribe universal armor areal densities. The builder
records them directly so later combat and radiation models can use the
same physical mass instead of inventing a second protection statistic.

# 6. Step 2 - Local Propulsion & Torch

Maneuvering and torch propulsion use ordinary momentum exchange. The
builder records the engine rather than buying abstract manoeuvre points.

## 6.1 Torch inputs

| **Input**                      | **Unit**                       | **Meaning**                                                                                      |
|--------------------------------|--------------------------------|--------------------------------------------------------------------------------------------------|
| Maximum thrust F               | N or MN                        | Force available at the selected operating point.                                                 |
| Effective exhaust velocity v_e | km/s                           | Propulsive efficiency; higher values reduce remass consumption for a given delta-v.              |
| Engine / nozzle mass           | t                              | Installed dry mass and structural support.                                                       |
| Direct jet power               | MW/GW                          | Physical power imparted to exhaust; not identical to onboard electrical load.                    |
| Electrical / control load      | MW                             | Pumps, magnets, control, ignition, diagnostics and supporting systems.                           |
| Waste heat to ship             | MW                             | Heat that remains aboard and must enter the thermal system.                                      |
| Operating envelope             | band or map                    | Certified combinations of thrust, v_e, duration and remass flow.                                 |
| Mount position / lever arm     | m from current centre of mass  | Required to derive torque and bending loads when thrust is off-axis.                             |
| Thrust axis / vectoring cone   | unit vector / degrees          | Defines what translational directions and control torques the engine can physically produce.     |
| Vectoring rate                 | deg/s or response band         | A large cone is not useful if the nozzle/field cannot slew quickly enough for the maneuver.      |
| Transient schedule             | g or thrust vs time            | Distinguishes sustained, FAST, HARD, LIMIT and emergency use from brochure maximum.              |
| Plume geometry                 | core/hazard angles + intensity | Creates drive-specific keep-out, detectability and damage consequences; no universal plume cone. |
| Load path                      | structural node / axis         | Identifies which frame members, mounts and hull axes receive the acceleration load.              |

**a = F / M_current**

*Acceleration changes as the ship burns reaction mass or changes
payload.*

**Delta-v = v_e ln(M_0 / M_1)**

*NASA Glenn ideal rocket equation; first-pass vacuum performance before
mission-specific losses.*

**P_jet ≈ 0.5 F v_e**

*Useful first-pass relation between thrust, exhaust velocity and kinetic
jet power.*

| **DESIGN CONSEQUENCE** High thrust and high exhaust velocity at the same time are brutally power-hungry. This prevents a designer from casually selecting both without paying reactor, nozzle, thermal and structural costs. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 6.2 Maneuvering systems

Docking/attitude thrusters are sized separately from the main torch.
They trade efficiency for response, precision and distributed control
authority. A ship can lose its torch and still maneuver locally; a ship
can also retain its torch while losing fine docking authority.

## 6.3 Force / Torque Node Record

v0.2 records each main engine, translation thruster cluster and
attitude-control cluster as a physical force/torque node. A force
through the centre of mass produces translation; a force with a lever
arm also produces torque. Opposed nodes can create pure rotation or pure
translation only when their geometry and available thrust permit it. The
builder may use simplified principal axes and grouped thruster clusters,
but it may not collapse the result into one generic Maneuverability
score.

The design therefore records node location, thrust vector,
gimbal/vectoring range, response rate, operating envelope, plume,
structural attachment and failure isolation. Current centre of mass
matters: burning remass, moving cargo, docking another craft or losing a
major component can change control authority.


## 6.4 Qualification-derived maneuvering record

The SFAP-01R courier qualification provides a useful worked example, not a universal default:

- ~0.10g sustainable transverse authority at ~1,220.5 t;
- ~0.25g transient transverse authority;
- ~1.20 / 2.99 MN equivalent force;
- provisional ~100 km/s exhaust velocity;
- exact node geometry still open.

A builder may use grouped nodes, but must state whether the quoted envelope applies per axis, per cluster, or to an aggregate allocator. **Never infer simultaneous full authority on every axis from one scalar “translation g” value.**

# 7. Step 3 - Metric & Loom Systems

## 7.1 Metric-drive design record

| **Field**                           | **Builder records**                                                                   |
|-------------------------------------|---------------------------------------------------------------------------------------|
| Certified coordinate-speed envelope | Normal / maximum sub-c fraction under standard geometry.                              |
| Supported ship mass / configuration | Maximum certified mass and configuration family.                                      |
| Electrical demand                   | Continuous and peak MW.                                                               |
| Field-bank energy                   | GJ/TJ available for initialization and transients.                                    |
| Waste heat                          | MW during charge, cruise and collapse.                                                |
| Hardware mass / volume              | Field generators, superconducting bus, sensors, control and structural reinforcement. |
| Geometric limitations               | Curvature/gradient, mass-distribution, traffic or environment constraints.            |
| Condition / certification           | Core health, calibration confidence and service history.                              |

## 7.2 Loom-drive design record

The ship record must support Core Mechanics v0.4 Integrity Classes. Keep domain/configuration, lattice condition, thermal state, bank/power, geometry and directional route/solution confidence as separate engineering states. Do not collapse them into an additive Transition State Index.

Record operational route burden by direction. A→B evidence does not certify B→A. BLACK is physically inadmissible and cannot be overridden; RED is physically admissible but outside normal certification and requires explicit captain override.

| **Field**                  | **Meaning**                                                                                                     |
|----------------------------|-----------------------------------------------------------------------------------------------------------------|
| Maximum domain mass        | Maximum configured mass the lattice is designed and certified to translate.                                     |
| Maximum envelope volume    | Maximum configured translation envelope; bulky external geometry can matter even if light.                      |
| Lattice geometry / nodes   | Installed boundary hardware and architecture; not one universal ring.                                           |
| Translation bank           | Stored energy available for formation and transition.                                                           |
| Metrology package          | Topology, curvature, mass-state and quantum/reference instrumentation.                                          |
| Lattice margin / condition | Life-limited hardware health, calibration headroom and known operating envelope.                                |
| Cycle doctrine             | High-cycle courier, low-cycle research, experimental/pathfinder, heavy-domain, etc.                             |
| Configuration requirement  | Which radiators, antennas, booms, cargo and small craft must be retracted, docked or detached before formation. |

| **LOCKED DESIGN RULE** A Loom ship is validated in a specific physical configuration. "It fits on the ship" does not mean "it fits inside the certified translation domain." External cargo, docked craft, deployed radiators and structural changes can alter the solution. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 7.3 Configuration states

| **Configuration**     | **Typical geometry**                                                                                               |
|-----------------------|--------------------------------------------------------------------------------------------------------------------|
| Docking               | Maneuver thrusters, docking sensors and capture hardware active; main torch constrained.                           |
| Torch cruise          | Main drive aligned; radiators and high-efficiency systems deployed as required.                                    |
| Metric cruise         | Mass distribution and field hardware inside certified metric configuration.                                        |
| Translation           | Loom envelope minimized; fragile or external systems retracted/secured; mass-state model frozen to high precision. |
| Combat / cold run     | Radiators may retract, thermal debt rises, apertures and weapons reconfigure.                                      |
| Atmospheric / landing | Aero surfaces, shields, gear, rotors/fans/rockets or lander configuration where applicable.                        |

# 8. Step 4 - Power & Energy Storage

LOOM separates propulsion energy from usable electrical power. A torch
can carry enormous jet power while the ship's electrical plant is orders
of magnitude smaller.

| **Power layer**             | **What it does**                                                                                    |
|-----------------------------|-----------------------------------------------------------------------------------------------------|
| Main fusion system          | Supplies torch energy directly and/or electrical conversion depending on architecture.              |
| Continuous electrical plant | Hotel loads, sensors, computers, life support, pumps, fabrication, weapons, metric support.         |
| Pulse / field banks         | Short-duration high-power demand for metric/Loom initialization and weapons.                        |
| Emergency survival power    | Independent life support, passive sensing, communications and minimum compute after major casualty. |

## 8.1 Mode-based power budget

| **Mode**       | **Must fit simultaneously**                                                                        |
|----------------|----------------------------------------------------------------------------------------------------|
| Docked / hotel | Life support + computers + maintenance + charging + port services.                                 |
| Torch cruise   | Hotel + control + sensors + thermal pumps + torch support.                                         |
| Metric cruise  | Hotel + sensors + metric continuous load + thermal system.                                         |
| Loom formation | Hotel + metrology + topology compute + lattice/field charge + thermal pumps.                       |
| Combat         | Sensors + EW + weapons + maneuver + damage control + reduced/retracted radiator consequences.      |
| Survival       | Minimum atmosphere/thermal control, critical compute, passive sensors and distress communications. |

| **RULE** Do not sum every installed system as though all operate at maximum simultaneously. Validate each real operating mode and each plausible emergency combination. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 9. Step 5 - Reaction Mass, Fuel & Endurance

## 9.1 Separate stores

| **Store**                         | **Why it is separate**                                                                              |
|-----------------------------------|-----------------------------------------------------------------------------------------------------|
| Reaction mass                     | Expelled to create momentum; dominates conventional delta-v economics.                              |
| Fusion reactants                  | Energy source; potentially small mass compared with remass but still strategic and finite.          |
| Water / life-support reserve      | Crew, hygiene, processing, shielding and possible remass feed.                                      |
| Coolant / open-loop fluid         | Heat transport and emergency heat rejection; losses are not the same thing as stored heat capacity. |
| Food / medical / spares           | Sets autonomous duration even when energy is abundant.                                              |
| Ammunition / drones / expendables | Mission endurance, not general ship fuel.                                                           |

## 9.2 Water as a multi-use strategic mass

Water is unusually valuable in LOOM because one physical inventory can
serve several roles: life support, hydrogen-rich radiation shielding,
cold-sink/thermal mass, industrial feedstock and reaction-mass feed. The
builder records one water inventory and marks its current allocations.
Consuming water as remass may weaken radiation protection or emergency
reserves.

# 10. Step 6 - Thermal Control

Vacuum does not remove heat. In steady state the ship has to radiate it.
LOOM therefore treats thermal design as a primary budget alongside
power.

**A_rad ≈ Q / \[epsilon sigma_SB (T_rad^4 - T_sink^4)\]**

*First-pass radiator area. Solar/planetary loading changes the effective
sink; use deep-space values only as a baseline.*

| **Radiator temperature** | **Area per 1 MW (epsilon=0.9, deep-space baseline)** | **Use**                         |
|--------------------------|------------------------------------------------------|---------------------------------|
| 300 K                    | 2,419 m^2                                            | Low-temperature / crew loop     |
| 400 K                    | 765 m^2                                              | Low-temperature / crew loop     |
| 500 K                    | 314 m^2                                              | Intermediate machinery          |
| 600 K                    | 151 m^2                                              | Intermediate machinery          |
| 800 K                    | 48 m^2                                               | High-temperature machinery only |
| 1000 K                   | 20 m^2                                               | High-temperature machinery only |
| 1200 K                   | 9 m^2                                                | High-temperature machinery only |

| **DESIGN CONSEQUENCE** Low-temperature heat is geometrically expensive. At 400 K, rejecting 1 MW requires roughly 765 m^2 of idealized radiator area; at 800 K it is about 48 m^2. High-temperature loops therefore matter enormously, but crew spaces and many electronics cannot simply be run at 800 K. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 10.1 Thermal layers

- Low-temperature loop: crew spaces, medicine, many electronics and food
  systems.

- High-temperature loop: reactor conversion, field hardware, weapons and
  machinery designed to run hot.

- Thermal storage: phase-change material, hot/cold reservoirs or other
  stores absorb temporary spikes but must later be regenerated.

- Open-loop cooling: vents working fluid and is extremely effective but
  consumptive and conspicuous.

- Radiators: sustainable heat rejection; large, bright and vulnerable
  enough that combat configuration matters.

## 10.2 Recovery Configuration

Thermal recovery is configuration-dependent. Stowed radiators preserve
combat profile and protection but reject heat slowly; deployed radiators
increase rejection at the cost of signature and exposed area; open-loop
cooling can reject heat rapidly by consuming working fluid and
advertising the event. Maneuver previews and recovery estimates use the
current configuration rather than a universal cooldown rate.

| **NASA ANCHOR** NASA thermal-control work treats deployable radiators, heat pipes, thermal switches, coatings, heaters, phase-change storage and active loops as distinct tools. LOOM extrapolates their maturity but keeps the same basic thermodynamic problem. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 11. Step 7 - Command, Automation & Computing

A 2226 spacecraft does not require a human to perform every routine
task. Automation changes watchstanding and response time, but it does
not erase expertise, authority or failure modes.

| **Record**              | **First-pass treatment**                                                                                           |
|-------------------------|--------------------------------------------------------------------------------------------------------------------|
| Control stations        | Physical stations needed for captain/flight, engineering, tactical/mission and damage-control authority.           |
| Automation architecture | How much routine operation can continue without direct crew intervention.                                          |
| Minimum watch crew      | People/processes needed to legally and safely keep the ship operating.                                             |
| Expertise requirements  | Pilot, engineer, medic, sensor/EW, astrogation/Loom, mission specialists - can overlap in small crews.             |
| Redundancy              | Single, dual, distributed or physically isolated control paths.                                                    |
| Cyber boundary          | Trusted update paths, hardware roots, segmented networks, external-interface sandboxes.                            |
| Sovereignty boundary    | For synthetic persons: who can alter cognition, who can revoke access, and whether external root authority exists. |

| **CREW RULE** Automation can reduce routine watch workload. It cannot magically supply missing judgment, legal authority or specialist competence when something leaves the modelled envelope. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 12. Step 8 - Sensors, Communications & Provenance

## 12.1 Knowledge Is a Hardware Output

LOCKED PRINCIPLE: sensors do not primarily give bonuses. They determine
the rate, precision, persistence and ceiling of knowledge. Aperture,
coverage, cooling/self-noise, active ranging, fusion capacity, EW/ECCM,
wavelength bands and deployable baselines all affect what fields the HUD
may legitimately display.

Damage therefore degrades knowledge rather than merely applying “Sensors
-2.” Losing an array can collapse attitude resolution, reduce
FIRE-CONTROL to TACTICAL, turn FIRM tracks into COARSE or stale tracks,
or force the player back to an unresolved detection region. Sensor
drones are primarily baseline/parallax machines, not generic modifiers.

| **System**                 | **Design concerns**                                                                                                                |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| Passive optical/IR         | Aperture size, field of regard, cooling, placement, redundancy, blind arcs.                                                        |
| Active radar/lidar         | Power, aperture, thermal load, resolution and the fact that transmitting reveals the emitter.                                      |
| Navigation / curvature     | Star fixes, ranging, ephemeris, metric geometry, Loom topology and local reference integrity.                                      |
| Distributed sensor drones  | Number, baseline geometry, endurance, comm latency and recovery.                                                                   |
| Communications             | Laser/radio arrays, bandwidth, pointing, light-speed latency and local infrastructure.                                             |
| EW                         | Jamming/spoofing/dazzling capability and the signatures/countermeasures those create.                                              |
| Secure/provenance carriage | Isolated partitions, authenticated time/custody records, hardware attestation, tamper evidence and legal chain-of-custody support. |

| **PROVENANCE RULE** Data mass is usually negligible. The expensive part is proving origin, integrity, custody, causal age and authority. A courier can carry vast information cheaply, but high-grade custody architecture, isolation and certification are mission systems. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 13. Step 9 - Mission Systems, Weapons & Small Craft

Weapons are one kind of mission system. The builder asks what the ship
does, then installs the hardware that makes that role physically
possible.

| **Mission package**       | **Typical physical costs**                                                                               |
|---------------------------|----------------------------------------------------------------------------------------------------------|
| Weapons / defense         | Mass, ammunition, apertures, recoil/structure, power, heat, fire control, magazines and protection.      |
| Survey / science          | Large sensors, labs, sample handling, clean rooms, probes, analysis compute.                             |
| Medical / rescue          | Treatment space, isolation, consumables, medevac access, preservation and power.                         |
| Mining / industrial       | Cutters, manipulators, processing equipment, feedstock storage, dust control.                            |
| Courier / intelligence    | Secure storage, provenance, passive sensing, signature control, analysis compute, isolated compartments. |
| Flight deck / small craft | Hangar volume, doors, capture/launch systems, fuel/remass, maintenance, spares and crew.                 |
| Passenger / hospitality   | Cabins, common areas, life support, baggage, medical and escape capacity.                                |
| Exploration / surface ops | Rovers, drones, EVA, sample storage, landing craft and planetary-environment gear.                       |

## 13.1 External payload penalty

External payload can be excellent for torch-only modularity. On
metric/Loom craft it may create penalties in mass characterization,
field geometry, signature and translated envelope. The builder therefore
records both internal cargo and external carriage separately.

# 14. Step 10 - Crew & Staffing

Crew is derived from installed systems and operating doctrine. v0.2
tracks three different numbers because "minimum crew" is not the same as
"sensible crew."

| **Crew figure**          | **Definition**                                                                                                   |
|--------------------------|------------------------------------------------------------------------------------------------------------------|
| Minimum operational crew | Smallest complement that can legally/physically operate the ship in routine conditions with its automation.      |
| Normal crew              | Complement that supports continuous watches, maintenance, mission work, sickness/injury and sane human workload. |
| Surge complement         | Maximum temporary crew/passengers/mission specialists the ship can support with degraded comfort or endurance.   |

## 14.1 Synthetic crew

Synthetic persons are not free crew slots. They may reduce oxygen, food
and some medical requirements, but they create power, thermal,
maintenance, physical-access and legal/sovereignty requirements. A
durable android can still be disabled by heat, radiation, impact, power
loss or damaged compute substrate.

## 14.2 Acceleration Support & Crew Orientation

The ship records couch/workstation orientation relative to the principal
thrust axes, restraint/support technology, medical acceleration support
and each crew member or crew class's certified acceleration envelope.
Capability is not a single maximum-g number: magnitude, duration,
direction, repetition and recovery all matter.

Synthetic persons can have materially different acceleration cost
functions. They do not gain an abstract piloting bonus; the same
physical maneuver simply imposes different physiological or mechanical
consequences. Current campaign test cases Sol and Walter have higher
acceleration tolerance than ordinary biological crew, but remain subject
to mounting, joint, shock, thermal, power and substrate limits.

# 15. Step 11 - Habitation & Life Support

NASA does not provide one universal cubic-metres-per-person number
because mission duration, layout, privacy, work functions and crew
composition matter. LOOM therefore uses a playtest allowance anchored to
real spacecraft/habitat studies rather than pretending one value is a
law of nature.

| **LOOM working band**       | **Net habitable volume per biological crewmember** | **Use**                                                                        |
|-----------------------------|----------------------------------------------------|--------------------------------------------------------------------------------|
| Minimal / short transit     | 15-25 m^3                                          | Hours to a few weeks; little privacy; heavy shared-use volume.                 |
| Standard long-haul          | 30-50 m^3                                          | Weeks to months; private sleep, work/recreation and usable common volume.      |
| Comfortable independent     | 50-80 m^3                                          | Months-long independent operation; better separation of functions and privacy. |
| Luxury / very long duration | 80+ m^3                                            | Yachts, liners, research vessels or crews expected to live aboard for years.   |

| **NASA CALIBRATION, NOT A REQUIREMENT** NASA analogs span widely: Gateway is about 125 m^3 habitable volume for up to four crew when occupied; the ISS is about 388 m^3 habitable volume; a NASA long-duration four-person, 380-day concept produced about 268 m^3 functional pressurized volume after layout trades (~67 m^3 per crewmember). v0.2 bands are game-design working values bracketed by those real examples. |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 15.1 Life-support record

- Atmosphere capacity and scrub/recycle redundancy.

- Water recovery, potable reserve and hygiene load.

- Food and biological consumables; stored vs locally grown/processed.

- Waste handling.

- Exercise / medical / hygiene / privacy / recreation required by
  mission duration.

- Radiation storm shelter for the full vulnerable crew complement.

- Emergency refuge/escape capacity; not necessarily lifeboats on every
  small ship.

# 16. Step 12 - Cargo & Payload

Cargo is the residual opportunity cost of every previous design
decision. The builder tracks mass and volume independently; neither is a
substitute for the other.

| **Payload type**         | **Special accounting**                                                                               |
|--------------------------|------------------------------------------------------------------------------------------------------|
| Bulk dense cargo         | Mass-limited; affects acceleration, delta-v, structure and Loom domain mass.                         |
| Bulky low-density cargo  | Volume/envelope-limited; can dominate translated geometry while barely changing mass.                |
| Secure information cargo | Negligible mass; provenance, isolation, legal status and causal age matter.                          |
| Passengers               | Mass + habitation + life support + medical + escape + legal responsibility.                          |
| Samples / biology        | Containment, temperature, contamination control, chain of custody.                                   |
| Vehicles / drones        | Mass + hangar/berth volume + service systems + spares + launch/recovery.                             |
| External cargo           | May be easy under torch and costly under metric/Loom because of envelope and field characterization. |

# 17. Step 13 - Finalize, Validate & Certify

A design is not finished when the last cubic metre is filled. It is
finished when every operating state closes physically and
institutionally.

| **Validation gate**            | **Pass condition**                                                                                                                                                                                            |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1\. Mass closure               | Dry and wet mass are known; structure and tanks support each operating configuration.                                                                                                                         |
| 2\. Volume closure             | Pressurized, systems, tanks, mission spaces and payload fit with maintenance access.                                                                                                                          |
| 3\. Thrust / delta-v           | Acceleration and delta-v meet the design point at realistic wet and dry masses.                                                                                                                               |
| 4\. Power closure              | Each operating mode fits continuous generation and allowed pulse-bank draw.                                                                                                                                   |
| 5\. Thermal closure            | Steady-state heat fits radiators; transient modes fit thermal storage/open-loop margins.                                                                                                                      |
| 6\. Crew/endurance closure     | Normal staffing, habitation, life support, medical and consumables meet mission duration.                                                                                                                     |
| 7\. Metric closure             | If installed, mass/configuration and field power fit the certified metric envelope.                                                                                                                           |
| 8\. Loom closure               | If installed, translation configuration fits domain mass, envelope volume, lattice margin and bank energy.                                                                                                    |
| 9\. Damage / refuge            | Critical systems have the intended redundancy, compartmentation and survival paths.                                                                                                                           |
| 10\. Certification / insurance | Legal build, maintenance evidence, crew qualification and route/use case match intended commerce.                                                                                                             |
| 11\. Payload truth             | Remaining cargo is what is actually left after all fixed systems and required reserves - not the number desired at Step 0.                                                                                    |
| 12\. Maneuver closure          | Installed engines/thrusters, vectoring, centre-of-mass state and attitude authority can produce the advertised translational and rotational envelope without violating the ship's structural/load-path model. |
| 13\. Crew acceleration closure | Normal and surge crew can occupy supported stations for the certified maneuver envelope; synthetic and biological limits are recorded separately where relevant.                                              |
| 14\. Recovery closure          | Thermal rejection, crew recovery and structural relaxation can return the ship to useful operating states on timescales consistent with its role; permanent wear is not erased by coasting.                   |
| 15\. Sensor-knowledge closure  | Installed apertures, cooling, coverage, processing, EW and deployables support the claimed track-quality ceilings and blind-arc behavior.                                                                     |

# 18. Ship Summary Card

Every finalized design should collapse to a one-page captain-facing
record. v0.2 recommends the following fields.

| **Category**        | **Captain-facing outputs**                                                                                                                                     |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Identity            | Role, hull type, builder/year, certification status.                                                                                                           |
| Mass / payload      | Dry mass, departure wet mass, cargo mass/volume, configured Loom envelope.                                                                                     |
| Torch               | Current thrust capability plus sustained / FAST / HARD / LIMIT / emergency maneuver envelope at current mass; v_e; delta-v; remass reserve; plume limits.      |
| Metric              | Certified normal/max coordinate speed; charge/recovery constraints.                                                                                            |
| Loom                | Domain mass/volume margin; bank state; lattice condition; route/topology confidence.                                                                           |
| Power               | Normal electrical output, continuous max, pulse-bank energy, survival power.                                                                                   |
| Thermal             | Low/high loop capacity, radiator state, thermal reserve, open-loop inventory.                                                                                  |
| Sensors             | Passive/active suites, drone complement, major blind arcs or special capability.                                                                               |
| Protection          | MMOD/debris, radiation shelter, combat protection, atmospheric protection where applicable.                                                                    |
| Crew                | Minimum / normal / surge; key required expertise.                                                                                                              |
| Endurance           | Biological crew days, maintenance/spares horizon, reaction-mass and fusion-fuel reserves.                                                                      |
| Mission systems     | Weapons, labs, small craft, medical, mining, provenance or other defining equipment.                                                                           |
| Institutional state | Insurer, maintenance/certification, licenses and notable restrictions.                                                                                         |
| Flight state        | Current thrust, attitude state, current/peak g, maneuver objective/constraints and whether the current solution is deterministic, probabilistic or unresolved. |
| Maneuver endurance  | Crew fatigue, injury floor, transient structural strain, persistent wear floor and relevant recovery/green times.                                              |
| Control authority   | Principal translational and rotational authority, major vectoring limits, degraded arcs and hardware/configuration dependencies.                               |

# 19. NASA / Real-Physics Calibration Notes

The builder should use authoritative real-world data where it constrains
an ordinary physical problem, then clearly identify where LOOM
extrapolates beyond it. The following anchors are sufficient for v0.2;
do not turn the RPG into a spacecraft-engineering thesis unless a
specific design question needs deeper work.

| **Anchor**                                               | **What LOOM borrows**                                                                                                                       |
|----------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| NASA Glenn - Ideal Rocket Equation / Specific Impulse    | Thrust, exhaust velocity, specific impulse and mass-ratio relationships for reaction propulsion.                                            |
| NASA Small Spacecraft State of the Art - Thermal Control | Radiators, heat pipes, coatings, heaters, thermal switches, deployable systems and phase-change storage as distinct design tools.           |
| NASA MMOD / Hypervelocity Impact work                    | Untrackable debris and micrometeoroids can remain dangerous; shielding is an areal-mass/geometry problem, not generic hit points.           |
| NASA radiation protection research                       | Hydrogen-rich, low-Z materials such as water and polyethylene are attractive for passive crew protection; shielding can be multifunctional. |
| NASA-STD-3001 Vol. 2 / Human Integration design work     | Habitability is mission- and task-dependent; volume, layout, privacy, work, recreation, medical and emergency access all matter.            |
| ISS / Gateway / long-duration habitat analogs            | Use real volume/mass examples to sanity-check habitation, but do not treat one spacecraft as a universal ratio.                             |

## 19.1 Deliberately simplified in v0.3

- No finite-element structural model; structure is accounted by mass,
  form, protection and later hull modules.

- No detailed nuclear/fusion plasma physics; engine catalogues will
  supply tested thrust/v_e/power envelopes.

- No exact radiation-dose transport; use areal mass, storm-shelter
  design and environment-specific exposure mechanics until a mission
  needs OLTARIS-level detail.

- No full CFD/entry solver; atmospheric vehicles use real
  gravity/atmosphere data and a separate planetary-operations model.

- No universal reliability probability per component; condition,
  maintenance evidence and exposure history drive risk.

- No fake precision for metric/Loom field equations; their hardware is
  sized with empirical engineering envelopes and canon constraints.

# 20. v0.2 Resolutions & Remaining Open Decisions

v0.2 resolves the central coupling between ship construction and
piloting while deliberately leaving catalogue values and exact
calibration curves open. The following decisions are now architectural
rules; the remaining questions are matters for playtest and engineering
calibration rather than permission for the GM to improvise impossible
capability.

| **Decision**                   | **v0.2 resolved stance**                                                                                                                                       | **Still open**                                                                                                              |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| Flight model                   | Continuous 3D state; attitude, velocity and acceleration are distinct. Capability is derived from installed force/torque nodes and current mass/configuration. | Exact numerical solver fidelity and inertia simplifications remain for playtest.                                            |
| Maneuver intensity             | EFFIC / FAST / HARD / LIMIT / EMERG are cost-envelope categories, not universal g ratings.                                                                     | Exact g, duration and recovery bands derive from ship, crew and technology catalogues.                                      |
| Crew & ship endurance          | Crew fatigue/injury, transient structural strain and persistent wear floor are separate ledgers with nonlinear recovery.                                       | Recovery curves and thresholds require calibration.                                                                         |
| Sensors                        | Sensors determine the rate, precision, persistence and ceiling of knowledge rather than granting a generic bonus.                                              | Aperture, cooling, active ranging, EW and drone catalogue values remain open.                                               |
| Torch / Metric / Loom boundary | Torch obeys ordinary momentum exchange. Metric and Loom capabilities must follow their own established physics. Tactical Loom teleportation is not adopted.    | Derived metric/Loom technologies are a later design challenge and may not erase existing thermal, maneuver or sensor games. |

| **RECOMMENDATION** Do not ask the player to resolve any of these before the first real ship build. Build the inherited courier with v0.2, see where the process becomes annoying or exploitable, then promote only the mechanics that earn their complexity. |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# Appendix A - Quick Equation Reference

| **Quantity**          | **First-pass equation**                     | **Notes**                                                                                |
|-----------------------|---------------------------------------------|------------------------------------------------------------------------------------------|
| Acceleration          | a = F / M                                   | Use current ship mass.                                                                   |
| Delta-v               | Delta-v = v_e ln(M_0/M_1)                   | Ideal vacuum rocket equation; use for torch/remass planning.                             |
| Mass ratio            | M_0/M_1 = exp(Delta-v/v_e)                  | Useful for solving required reaction mass.                                               |
| Jet power             | P_jet ≈ 0.5 F v_e                           | Kinetic exhaust power approximation.                                                     |
| Energy from power     | E = P t                                     | 1 MW for 1,000 s = 1 GJ.                                                                 |
| Radiator area         | A ≈ Q/\[epsilon sigma(T_rad^4 - T_sink^4)\] | Use environment-adjusted sink temperature/loading when relevant.                         |
| Protection layer mass | M = sigma_A A_protected                     | Lets radiation/MMOD/combat layers share a physical mass basis.                           |
| Wet mass              | M_wet = M_dry + stores + remass + payload   | Never evaluate acceleration/delta-v from dry mass alone unless that is the actual state. |

# Appendix B - Blank Build Worksheet

| **Step**          | **Entry**                                                                                                                     |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------|
| 0 Mission         | Role: \_\_\_\_ Crew: \_\_\_\_ Endurance: \_\_\_\_ Payload target: \_\_\_\_ Environments: \_\_\_\_                             |
| 1 Hull            | Form: \_\_\_\_ Dry structure: \_\_\_\_ t Pressurized volume: \_\_\_\_ m^3 Protection: \_\_\_\_                                |
| 2 Torch           | Thrust: \_\_\_\_ MN v_e: \_\_\_\_ km/s Engine mass: \_\_\_\_ t Support power/heat: \_\_\_\_                                   |
| 3 Metric / Loom   | Metric: \_\_\_\_ Loom domain mass: \_\_\_\_ t Envelope: \_\_\_\_ m^3 Bank: \_\_\_\_ GJ/TJ Lattice: \_\_\_\_                   |
| 4 Power           | Electrical continuous: \_\_\_\_ MW Peak: \_\_\_\_ MW Bank: \_\_\_\_ GJ Survival: \_\_\_\_                                     |
| 5 Stores          | Reaction mass: \_\_\_\_ t Water: \_\_\_\_ t Fusion fuel: \_\_\_\_ Coolant: \_\_\_\_ Other: \_\_\_\_                           |
| 6 Thermal         | Low-loop: \_\_\_\_ MW High-loop: \_\_\_\_ MW Radiator area: \_\_\_\_ m^2 Thermal reserve: \_\_\_\_ GJ                         |
| 7 Command / AI    | Control stations: \_\_\_\_ Automation: \_\_\_\_ Redundancy: \_\_\_\_ Sovereignty/cyber: \_\_\_\_                              |
| 8 Sensors / comms | Passive: \_\_\_\_ Active: \_\_\_\_ Drones: \_\_\_\_ Comms: \_\_\_\_ Provenance: \_\_\_\_                                      |
| 9 Mission systems | Weapons: \_\_\_\_ Labs: \_\_\_\_ Small craft: \_\_\_\_ Other: \_\_\_\_                                                        |
| 10 Crew           | Minimum: \_\_\_\_ Normal: \_\_\_\_ Surge: \_\_\_\_ Required expertise: \_\_\_\_                                               |
| 11 Habitation     | Net habitable: \_\_\_\_ m^3 Life support: \_\_\_\_ crew-days Shelter/medical: \_\_\_\_                                        |
| 12 Cargo          | Internal: \_\_\_\_ t / \_\_\_\_ m^3 External: \_\_\_\_ t / \_\_\_\_ m^3 Passengers: \_\_\_\_                                  |
| 13 Final          | Dry: \_\_\_\_ t Wet: \_\_\_\_ t a: \_\_\_\_ g Delta-v: \_\_\_\_ km/s Power/thermal closures: \_\_\_\_ Certification: \_\_\_\_ |

# Appendix C - Grounding Sources Used Through v0.2

| **Source**                                                                                      | **Use**                                                                                                                                                                        |
|-------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| NASA Glenn Research Center, "Ideal Rocket Equation" and "Specific Impulse."                     | Used for reaction-propulsion equations and interpretation of exhaust velocity / specific impulse.                                                                              |
| NASA, State-of-the-Art of Small Spacecraft Technology, Chapter 7: Thermal Control (2026).       | Used to ground radiator, heat-pipe, thermal-storage, coatings and active/passive thermal architecture.                                                                         |
| NASA Johnson / White Sands, Micrometeoroids and Orbital Debris; NASA NESC debris-risk material. | Used to ground separate MMOD/debris shielding and the importance of untrackable high-velocity impactors.                                                                       |
| NASA radiation shielding research and Langley radiation-analysis material.                      | Used to ground water / hydrogen-rich low-Z shielding and multifunctional shielding design.                                                                                     |
| NASA-STD-3001 Volume 2, Human Factors, Habitability, and Environmental Health.                  | Used to ground the principle that volume/layout must support actual crew tasks rather than a universal room-per-person ratio.                                                  |
| NASA ISS Facts and Figures; Gateway FAQ; NASA NTRS long-duration habitat studies.               | Used as broad sanity-check analogs for habitable volume, not as direct LOOM ship design rules.                                                                                 |
| NASA Small Spacecraft State of the Art - Guidance, Navigation and Control.                      | Grounds the use of distributed actuators/thrusters, attitude determination/control and hardware-derived force/torque authority rather than a single maneuverability statistic. |
| NASA human-systems / acceleration literature and NASA-STD-3001 family.                          | Calibration source for future human acceleration-duration-direction limits; v0.3 deliberately does not freeze a universal 2226 g-tolerance table.                              |

| **NEXT PLAYTEST** Use this document to build one real ship - preferably the inherited courier. Every time the builder asks for a value we cannot justify, mark it as a catalogue or rules gap. Every time a calculation adds bookkeeping without changing a decision, hide it under the captain-facing layer. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# PART II — PILOTING, MANEUVER & RECOVERY

| **CORE FLIGHT RULE** The player commands intent. The ship obeys physics. A maneuver is not movement on a map; it is a decision to alter the future geometry of the engagement. |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 21. Flight Dynamics Backbone

The simulation maintains a continuous physical state beneath the player
interface. The player never needs to perform orbital mechanics or
rigid-body dynamics by hand, but the Flight Director may only offer
solutions that the underlying state and installed hardware can support.

| **State**       | **Minimum internal record**                                    | **Why it matters**                                                                      |
|-----------------|----------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Position        | 3D Cartesian position in the active simulation frame           | Determines geometry, range, occultation and collision/intercept state.                  |
| Velocity        | 3D inertial velocity                                           | Persists through attitude changes; determines future geometry and delta-v requirements. |
| Attitude        | Hull orientation / body axes                                   | Controls weapon arcs, armor aspect, radiator/sensor exposure and thrust direction.      |
| Angular state   | Angular velocity plus simplified inertia response              | Determines how quickly the hull can rotate, stop and track.                             |
| Acceleration    | Net force / current mass                                       | Changes velocity; is not interchangeable with either attitude or speed.                 |
| Mass state      | Current wet mass and centre of mass                            | Changes acceleration, torque, structural loading and control authority.                 |
| Operating state | heat, remass, crew fatigue, strain/wear, damage, configuration | Changes what is prudent, certified or physically available right now.                   |

## 21.1 Attitude ≠ Velocity ≠ Acceleration

These are independent quantities. A ship can coast sideways while
pointing its bow at a target; it can rotate without materially changing
its inertial trajectory; and it can only accelerate in directions that
the vector sum of its available thrust nodes can physically produce. The
HUD is ship-relative, so rotating the ship can move a contact to the FOR
axis without changing that contact's inertial trajectory.

| **RENDERER / PILOTING INVARIANT** If the ship is maintaining ASPECT BOW on a target, that target migrates toward the FOR/boresight axis in the hull-relative tactical display. The underlying velocity vector may point somewhere entirely different. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 21.2 Force / Torque Solution

The Flight Director solves desired translation and rotation from
available force/torque nodes. Exact rigid-body mathematics may be hidden
under the interface, but the engineering logic is not optional: thrust
through the centre of mass primarily translates; off-axis thrust
produces torque; paired nodes can cancel torque or translation only when
the geometry permits.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>REQUESTED STATE CHANGE<br />
|<br />
v<br />
AVAILABLE FORCE/TORQUE NODES<br />
|<br />
v<br />
MASS + CoM + INERTIA + DAMAGE<br />
|<br />
v<br />
VALID SOLUTION SET<br />
|<br />
+--&gt; none<br />
+--&gt; one solution<br />
+--&gt; Pareto set</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 21.3 What Ship Construction Must Determine

| **Design feature**             | **Piloting consequence**                                                                                |
|--------------------------------|---------------------------------------------------------------------------------------------------------|
| Main-drive placement and axis  | Defines dominant high-g translation direction and principal structural load path.                       |
| Engine gimbal/vectoring        | Allows limited thrust redirection and torque without changing the hull axis by the full maneuver angle. |
| Translation thruster placement | Determines low/medium-g lateral and vertical authority while preserving weapon/armor aspect.            |
| Attitude thruster lever arms   | Determines pitch/yaw/roll torque and how quickly the ship can acquire/hold an aspect.                   |
| Mass distribution / inertia    | Affects angular acceleration and stopping; two ships with equal mass can rotate very differently.       |
| Crew orientation               | Changes human acceleration cost for the same ship maneuver.                                             |
| Weapon/sensor/radiator arcs    | Creates reasons to choose one attitude solution over another.                                           |
| Damage / cargo / docking state | Can shift CoM, remove nodes, enlarge inertia and invalidate previously legal maneuvers.                 |

# 22. Flight Director

The Flight Director is an intent-to-physics layer, not an autopilot that
makes tactical decisions for the player. It handles vector math,
trajectory propagation, control allocation and constraint checking,
while returning only the decisions that matter.

## 22.1 Primary Loop

| OBSERVE -\> OBJECTIVE -\> SOLUTIONS -\> COMMIT -\> RESOLVE -\> OBSERVE |
|------------------------------------------------------------------------|

The loop is event-driven rather than tied to rigid combat rounds. The
simulation advances to the earliest meaningful event: burn complete,
track-quality change, weapon event, threshold crossing, CPA/TCA event,
collision/plume hazard, objective achieved or player checkpoint.

## 22.2 Command Grammar

The primary tactical language should remain compact. Representative
objective verbs are INTERCEPT, MATCH, SEPARATE, HOLD and BRAKE.
Interesting behavior comes from constraints rather than a catalogue of
named maneuvers.

| **Syntax** | **Meaning**                                                                                   | **Example**                 |
|------------|-----------------------------------------------------------------------------------------------|-----------------------------|
| !          | Hard constraint; may not be violated by the returned solution.                                | !CPA \<10k                  |
| ~          | Soft preference; solver should optimize toward it but may trade it against other preferences. | ~ASPECT BOW                 |
| Objective  | What future geometry the captain wants.                                                       | INTERCEPT K2                |
| Condition  | A measurable target/limit.                                                                    | RANGE 50k; G \<6; HEAT \<70 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>INTERCEPT K2<br />
!CPA &lt;10k<br />
~ASPECT BOW<br />
~PROFILE MIN</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 22.3 Solution Set & Pareto Rule

The solver returns one to three non-dominated solutions when genuine
tradeoffs exist. It does not invent fake choices merely to fill three
slots. If only one solution satisfies the constraints, show one. If none
exists, show NO VALID SOLUTION and identify which constraints could be
relaxed and what capability becomes available.

| **NO HIDDEN “BEST”** The computer may optimize mathematics; it may not silently decide which tactical cost the captain ought to value. Time, signature, heat, remass, crew fatigue, structural strain, aspect and track quality are captain decisions. |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 22.4 Manual, Standing & Planning Layers

| **Layer** | **Purpose**                                                                              | **Typical commands**                           |
|-----------|------------------------------------------------------------------------------------------|------------------------------------------------|
| TACTICAL  | Default combat loop; objective + constraints -\> solution set -\> commit.                | INTERCEPT / MATCH / SEPARATE / HOLD / BRAKE    |
| MANUAL    | Expert explicit control when the captain wants hardware-level authority.                 | POINT / ROTATE / THRUST / TRANSLATE / CUTOFF   |
| STANDING  | Persistent cruise or station-keeping doctrine.                                           | COAST-DARK / HOLD K2 50k / MATCH / BRAKE-DOCK  |
| PLANNING  | Compound maneuver timeline for orbital ops, ambushes, formations and fleet coordination. | Ordered objectives/conditions with checkpoints |

## 22.5 Causality & Opponent Response

NPC intent is locked from the NPC's last observable state before the
player commits. An opponent cannot react to a player burn until
information about that burn could physically reach its sensors, be
detected, processed and acted on. After the player commit, the GM
advances to the next observable event; hidden response is not narrated
early.

| **SIMULATION KNOWS REALITY** The simulation may know the opponent’s true maneuver immediately. The player knows only what could have reached the player’s sensors at the displayed epoch. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 22.6 Uncertainty-Aware Maneuvering

The Flight Director distinguishes deterministic, probabilistic and
insufficient-information solutions. CPA/TCA and intercept results
inherit sensor covariance. A Detection-only contact does not receive
fake precise range, velocity or CPA simply because the maneuver solver
wants them.

| **Knowledge state**            | **Permitted maneuver output**                                                                             |
|--------------------------------|-----------------------------------------------------------------------------------------------------------|
| FIRE-CONTROL / strong Tactical | Precise CPA/TCA with covariance; high-confidence intercept/aspect solutions.                              |
| Coarse / Firm                  | Ranges and probabilities; e.g., CPA 20-75k, P(CPA\<10k)=14%.                                              |
| Detection only                 | Bearing/region and qualitative options: wait, deploy baseline, active range, burn away from bearing cone. |

# 23. Maneuver Intensity & Cost

Maneuver intensity is defined by how deeply the action spends the
current ship-and-crew endurance envelope, not by universal g values.
Exact g and duration are outputs of the specific design, mass state,
crew support, damage and objective.

| **Category** | **Operational meaning**                                    | **Expected cost profile**                                                                        |
|--------------|------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| EFFIC        | Conserve resources / low stress.                           | Low heat, low signature, low fatigue/strain; accepts slower geometry change.                     |
| FAST         | Normal aggressive combat-performance envelope.             | Designed to be cycled repeatedly by trained crew and an undamaged ship with manageable recovery. |
| HARD         | Deliberately spend endurance for tactical geometry.        | Material heat, fatigue and strain; may add wear; meaningful recovery required.                   |
| LIMIT        | Approach certified current envelope.                       | Large fatigue/strain, guaranteed or likely wear, small headroom for damage or uncertainty.       |
| EMERG        | Exceed normal certified envelope when physically possible. | Injury and component/structural failure risk; damage may occur even if the maneuver succeeds.    |

| **NO UNIVERSAL G TABLE** A FAST maneuver on one ship may exceed a HARD maneuver on another. The category describes relationship to the current system envelope and cost, not a setting-wide acceleration number. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 23.1 Persistent Maneuver Bills

| **Ledger**        | **What accumulates**                                                                        | **What removes it**                                                                           |
|-------------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Thermal           | Waste heat from drives, power, weapons, fields and control systems.                         | Radiation, thermal storage regeneration, open-loop cooling; rate depends on configuration.    |
| Reaction mass     | Momentum exchange consumed by torch/thrusters.                                              | Resupply or compatible onboard feedstock conversion; ordinary cooling does not restore it.    |
| Crew fatigue      | Physiological/embodiment load from magnitude, duration, direction and repetition.           | Time and life/medical support; recovery rate is person/embodiment dependent.                  |
| Structural strain | Transient accumulated load debt from hard maneuvering.                                      | Time unloaded/low-load; cannot fall below persistent wear floor.                              |
| Wear floor        | Persistent fatigue, deformation, mount life, bearing/joint life and other maintenance debt. | Maintenance/repair/replacement; not coasting.                                                 |
| Signature         | Thermal/drive/emission observability caused by the maneuver.                                | Falls causally as emissions cease and the ship cools/reconfigures; cannot be instantly reset. |

## 23.2 Maneuver Preview Contract

Previews show absolute before -\> after state, not only increments.
Captains need to know the remaining headroom after the maneuver.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>3 HARD CROSS<br />
<br />
BURN 8.0g / 8s [illustrative]<br />
CPA 4.1k<br />
ASPECT -&gt; K1 AFT<br />
<br />
THERM 49 -&gt; 67%<br />
REMASS 28.0 -&gt; 27.4%<br />
CREW FAT 11 -&gt; 24%<br />
STRAIN 8 -&gt; 15%<br />
WEAR 3 -&gt; 4%<br />
SIG VHIGH</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 24. Crew Acceleration, Fatigue & Injury

Peak g alone is insufficient. The crew model integrates acceleration
magnitude, exposure duration, direction relative to the body/support
system, repetition, individual/embodiment tolerance and recovery. A
brief high-g pulse, a long moderate-g burn and repeated pulses create
different consequences.

| **State**    | **Meaning**                                                                                                                       |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------|
| G NOW        | Current experienced translational acceleration at the crew station; rotational acceleration may be tracked locally when material. |
| G PEAK       | Highest recent exposure; useful context, not the fatigue model by itself.                                                         |
| CREW FAT     | Recoverable short/medium-term performance debt.                                                                                   |
| INJURY FLOOR | Persistent biological/mechanical harm that does not disappear during ordinary recovery.                                           |
| GREEN TIME   | Estimated time until the individual/crew returns below a tactically useful fatigue threshold.                                     |

Fatigue can degrade concentration, reaction time, fine motor control and
eventually task performance. Injury is separate. The system should avoid
a binary “under max = fine / over max = dead” model.

## 24.1 Synthetic Advantage

Synthetic crew may tolerate much greater acceleration because they do
not share the same blood-pressure, hypoxia and soft-tissue limits as
humans. Their costs move into shock isolation, mount loads, joints,
internal buses, compute substrate, power and thermal management. The
design goal is not “synthetics get +2”; the physical maneuver is
unchanged while the embodiment cost function differs.

| **CURRENT CAMPAIGN TEST CASE** Sol and Walter have higher acceleration tolerance than ordinary human crew. This lets them exploit ships nearer the structural/thermal envelope before crew physiology becomes the limiting factor. Exact values remain to be calibrated from embodiment design. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 25. Structural Strain, Wear & Damage

Ship endurance uses a two-layer model. STRAIN is transient structural
load debt that can relax when the ship is unloaded. WEAR is the
persistent floor caused by cyclic fatigue, mount life, deformation or
other service debt. Damage can raise the floor, reduce certified load
limits, remove thrust nodes or alter the centre of mass.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>AFTER HARD MANEUVER<br />
<br />
STRAIN 22%<br />
FLOOR 7%<br />
<br />
15 points may relax.<br />
7 points require maintenance/repair.</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **CAPTAIN AUTHORITY** The Flight Director reports risk rather than infantilizing the captain. If a maneuver remains physically possible but exceeds prudent or certified limits, AVAILABLE may remain YES with explicit injury/failure probabilities and degraded outcomes. |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 26. Recovery / Cooldown System

Recovery is three different clocks: thermal recovery, crew recovery and
structural relaxation. Persistent wear/injury are floors, not cooldown
meters. Stopping thrust stops new accumulation; it does not erase the
bill.

## 26.1 Recovery Postures

| **Posture**   | **Configuration**                                                                            | **Recovery / tactical effect**                                                               |
|---------------|----------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| COMBAT COAST  | Radiators stowed or protected; weapons/sensors ready.                                        | Slow thermal recovery; normal crew/strain recovery; low(er) profile and readiness preserved. |
| COOL          | Radiators deployed / higher rejection state.                                                 | Fast thermal recovery; increased thermal signature/profile and radiator vulnerability.       |
| DEEP RECOVERY | Drive safe, maximum thermal configuration, crew support, structure unloaded where practical. | Maximum thermal/crew/strain recovery; degraded immediate combat readiness.                   |

## 26.2 Nonlinear Recovery & GREEN Times

Recovery is nonlinear. Light fatigue and low transient strain can clear
quickly; deep accumulation lingers. The engine may model the curve
internally. The player-facing system reports the tactically useful
thresholds rather than demanding that the captain wait for every meter
to reach exactly zero.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>RECOVERY / OWN<br />
<br />
THERM GREEN 5m<br />
CREW GREEN 6m<br />
STRUCT NOM 9m<br />
WEAR FLOOR 7%<br />
<br />
Current posture: COOL</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Recovery clocks must be derived from the active thermal/biomedical/structural model. If the model cannot support an exact minute value, display a band or threshold state rather than fabricated precision.

The threshold itself can depend on the next intended action. “Green for
another FAST intercept” may occur well before “green for another LIMIT
maneuver.”

# 27. Sensors as Part of Piloting

The maneuver solver may only use knowledge the ship has earned. This
makes sensor design a direct flight-performance input: better passive
aperture, baseline, cooling, active ranging and fusion do not merely
improve a die roll; they let the Flight Director solve geometry sooner,
more precisely and for longer.

| **Sensor design choice**      | **Flight consequence**                                                                                          |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------|
| Large passive aperture        | Earlier detection and better angular precision; may improve track solution without emitting.                    |
| Cryogenic / low-noise sensing | Improves passive quality but competes with combat heat and self-noise.                                          |
| Active radar/lidar            | Can earn range/velocity rapidly but emits and is detectable.                                                    |
| Distributed sensor drones     | Creates parallax/baseline; improves passive range/3D solution at cost of deployment, latency and vulnerability. |
| All-sky / redundant coverage  | Reduces blind arcs and preserves knowledge while maneuvering or after damage.                                   |
| EW/ECCM                       | Changes persistence and covariance; can force the opponent back down the knowledge ladder.                      |

| **KNOWLEDGE CEILING** Track quality is not distance-driven. Detection -\> Coarse -\> Firm -\> Tactical -\> Fire-Control depends on target signature, hardware, observation time, geometry/baseline, aspect, occlusion, ownship noise, EW and operator effectiveness. |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 28. Piloting / HUD Interface Contract

The dedicated HUD standard remains the detailed rendering authority.
This document defines the information the piloting system must expose.
Mandatory tactical views remain phone-readable monospace text; geometry
and track quality may never imply knowledge that has not been earned.

| **View / block** | **Piloting question**                                                                       |
|------------------|---------------------------------------------------------------------------------------------|
| MAIN             | Which side, and above/below? PT/SB vs DOR/VEN.                                              |
| TOP              | Which side, and ahead/behind? PT/SB vs FOR/AFT.                                             |
| RANGE            | How far / what depth band? Range only; no fake concentric geometry.                         |
| CONTACTS         | Exact values the current track supports: range, RR, CPA/TCA, attitude, age, covariance.     |
| TRIAGE           | What matters first? Deterministic hazard/priority ordering, not LLM vibes.                  |
| FLIGHT / OWN     | Thrust, attitude, PACC/NACC, thermal, remass, crew fatigue, strain/wear, signature, recovery state/times. |


For navigation/engineering views, keep ephemeris provenance separate from reference frame and track quality. Compact labels should distinguish direct authoritative JPL state from a propagated JPL state (for example `EPH:JPL` vs `EPH:JPL-PROP`) while retaining the exact Horizons/SPICE request metadata underneath.

When chronology diverges, show `SHIP MET`, `EXT EPOCH`, and `CAUSAL OFFSET` as separate fields. Do not overwrite the vessel’s experienced mission clock with a reacquired external date.

A target orientation arrow indicates target nose attitude projection
only; it is never a velocity vector. Closing/opening/matched is radial
relationship only. Stale tracks are visibly marked. A point glyph is
earned; unresolved detections remain regions/bands/intervals.


# 28.1 Metric intercept and terminal-state doctrine

Metric cruise solves a coordinate-displacement problem to a **future** destination state. The Flight Director must:

1. evaluate or propagate the destination to the candidate arrival epoch;
2. iterate the intercept if target motion changes the answer materially;
3. state whether field acquisition/ramp/collapse time is modeled or still uncalibrated;
4. preserve the ship’s local conventional state unless the metric engineering model explicitly accounts for a change;
5. separate metric arrival from conventional relative-state match, traffic entry and docking.

A metric drive therefore does not grant a free velocity reset. If the exact ownship velocity vector or collapse momentum map is unresolved, the terminal Δv is unresolved too. Do not invent it.

# 28.2 Automated docking

Where port and vessel have negotiated a valid authenticated docking contract—corridor, allowable forces, abort conditions, telemetry, capture hardware and command authority—and no fault makes the contract uncertain, routine docking is **not a skill check**. Roll only when traffic, provenance, damage, conflicting automation, cyber compromise or another material uncertainty changes the problem.

# 29. Engineering Check: The HARD CROSS

The Kestrel playtest exposed the exact failure mode this framework is
designed to catch. The player ordered a high-g crossing maneuver while
keeping bow guns continuously on the target. The provisional corvette
had an aft main torch with only ±6 degrees of vectoring and about 0.15g
lateral translation authority. The earlier narration incorrectly granted
a full ~8g transverse burn while preserving bow-on attitude.

| **RULING** With that hardware, the narrated 8g continuous-gun HARD CROSS is not a valid solution. The command remains valid; the Flight Director must return hardware-consistent alternatives. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **Alternative**  | **Physics**                                                                                  | **Tactical trade**                                                                                         |
|------------------|----------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| SNAP CROSS       | Rotate toward required thrust vector, execute hard axial burn, cut, rotate/reacquire target. | Buys large transverse delta-v but loses continuous forward-gun track for part of the maneuver.             |
| TRACKING CROSS   | Keep bow on target and use dedicated translation thrusters / small vectoring component.      | Maintains guns and profile but crosses much more slowly.                                                   |
| MULTI-AXIS DRIVE | A ship deliberately built with high-thrust off-axis maneuver engines executes both.          | Powerful capability earned by mass, structure, heat, remass, plume and cost paid during ship construction. |

Illustrative check only: an 8.3g main burn deflected by 6 degrees
produces roughly 0.87g lateral component before adding the small
translation thrusters. The exact playtest value is not canon; the
engineering conclusion is.

# 30. Advanced-Technology Boundary

v0.3 imposes discipline between the three propulsion/space-physics
families. A cool effect is not sufficient justification for moving a
capability between them.

| **Family**                  | **Current design boundary**                                                                                                                                                                               |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Torch / reaction propulsion | Ordinary momentum exchange. Force, torque, remass, plume, heat, structure and crew acceleration remain real.                                                                                              |
| Metric engineering          | May manipulate the local metric only to the extent established by future metric-drive rules. Derived capabilities must pay mass/power/heat/configuration costs and may not silently erase the torch game. |
| Loom translation            | Changes relational/topological embedding under the established Loom model. It is not currently authorized as arbitrary short-range tactical teleportation.                                                |

| **NOT ADOPTED** The proposed tactical “Delta Fold / Lazar Flip” is not part of current canon. It remains a design prompt only unless later Loom physics explicitly supports it without deleting Newtonian maneuver, thermal, sensor and intercept play. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 31. Revised Ship Build Requirements for Piloting

A ship intended for tactical play must leave the builder with enough
geometry to derive capability without requiring CAD or finite-element
analysis. Use grouped nodes and principal axes when that preserves
decisions.

| **Record**                 | **Required ship-build output**                                                                                             |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------|
| Mass / centre of mass      | Current mass states; nominal CoM; rules for large cargo/remass/configuration shifts.                                       |
| Principal inertia          | Simplified pitch/yaw/roll inertia bands or derived values sufficient to distinguish long/heavy from compact/agile layouts. |
| Propulsion nodes           | Position, thrust, axis, vector cone/rate, sustained/transient envelope, heat/remass, plume and load path.                  |
| Attitude/translation nodes | Cluster position and available force/torque by axis; failure isolation and redundancy.                                     |
| Structural axes            | Certified axial/lateral/torsional envelopes plus strain/wear response.                                                     |
| Crew support               | Station/couch orientation, restraint/support technology, human/synthetic tolerance classes and recovery support.           |
| Weapon arcs                | Firing arcs, recoil/impulse if material, tracking rate and aspect requirements.                                            |
| Sensor arcs                | Coverage, aperture, cooling/noise, active/passive, fusion and baseline capability.                                         |
| Radiator geometry          | Stowed/deployed states, rejection capacity, signature and vulnerability.                                                   |
| Configuration states       | Docking/torch/metric/Loom/combat/recovery configurations and what hardware is available in each.                           |
| Clock / ephemeris interface | SHIP MET / EXT EPOCH when needed; target-state source, frame, propagation method, age/tolerance and provenance labels.      |

## 31.1 Simplification Rule

| **NO CAD INSANITY** Model enough geometry to change decisions. If two thruster layouts produce the same force/torque envelope, failure behavior, plume constraints and cost at the table, the builder may treat them as the same grouped node. Complexity that only proves the engine did its homework stays under the hood. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 32. Captain Card v0.3 — Piloting Additions

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>FLIGHT / OWN<br />
<br />
MASS current wet<br />
THRUST current / available<br />
PACC current / NACC current<br />
G PEAK recent peak<br />
THERMAL % + trend<br />
REMASS % / t<br />
CREW FAT %<br />
INJURY floor<br />
STRAIN %<br />
WEAR floor<br />
SIG state / trend<br />
<br />
GREEN<br />
THERM time<br />
CREW time<br />
STRUCT time</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

The Captain Card also carries current SHIP MET and, when materially different, EXT EPOCH / CAUSAL OFFSET. It also carries the ship's current
EFFIC/FAST/HARD/LIMIT/EMERG maneuver envelope and major
control-authority restrictions. It is a summary of the engineering
ledger, not a separate rules layer.

# 33. Review Challenge — Ship Building & Piloting v0.3

External reviewers should attack the coupling, not merely suggest more
gadgets. The purpose of the next review is to find where the framework
still permits impossible motion, hides a meaningful decision or requires
unnecessary bookkeeping.

1\. Can the grouped force/torque node model derive interesting
ship-to-ship maneuver differences without requiring CAD or a full
rigid-body simulator?

2\. What is the lightest credible principal-inertia model that still
makes long axial ships, compact corvettes and distributed truss ships
handle differently?

3\. Do EFFIC / FAST / HARD / LIMIT / EMERG create meaningful choices
when defined by cost envelope rather than fixed g values?

4\. How should crew fatigue, injury, transient strain and wear floor be
calibrated so recovery matters without turning combat into meter
management?

5\. Can the recovery postures create real tactical decisions without
making radiator deployment an automatic choice?

6\. Does the sensor-as-knowledge-ceiling model integrate cleanly enough
with maneuver solution confidence and the HUD track ladder?

7\. What combinations of torch placement, vectoring and maneuver
thrusters naturally create distinct combat doctrines?

8\. Where should the system say NO VALID SOLUTION rather than inventing
a heroic maneuver?

9\. Which complexity should be hidden under the Flight Director because
it changes no player decision?

10\. Can the ephemeris/game-clock/remass/gravity discipline stay rigorous without making routine play slow?

11\. What derived metric or Loom technologies could bend these systems
without deleting heat, intercept geometry, sensors, strain or crew
endurance?

| **REVIEW STANDARD** Do not fix a maneuver by giving the pilot a bonus. Fix the ship, the physics model, the control allocation or the objective/constraint interpretation. What the ship can do must come from what was built. |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# Appendix D - Flight / Maneuver Build Worksheet

| **Block**           | **Entry**                                                                                                    |
|---------------------|--------------------------------------------------------------------------------------------------------------|
| Mass / CoM          | Wet mass: \_\_\_\_ t Nominal CoM: \_\_\_\_ Major shift cases: \_\_\_\_                                       |
| Main drive node(s)  | Position: \_\_\_\_ Axis: \_\_\_\_ Thrust: \_\_\_\_ Vector: +/-\_\_\_\_ deg Rate: \_\_\_\_                    |
| Main drive envelope | Sustained: \_\_\_\_ FAST: \_\_\_\_ HARD: \_\_\_\_ LIMIT: \_\_\_\_ EMERG: \_\_\_\_                            |
| Translation nodes   | PT/SB: \_\_\_\_ g DOR/VEN: \_\_\_\_ g FOR/AFT secondary: \_\_\_\_ g                                          |
| Rotation authority  | Pitch: \_\_\_\_ Yaw: \_\_\_\_ Roll: \_\_\_\_ Stop/reverse behavior: \_\_\_\_                                 |
| Structure           | Axial: \_\_\_\_ Lateral: \_\_\_\_ Torsion: \_\_\_\_ strain recovery: \_\_\_\_ wear model: \_\_\_\_           |
| Crew support        | Stations/axes: \_\_\_\_ Human envelope: \_\_\_\_ Synthetic envelope: \_\_\_\_ support: \_\_\_\_              |
| Thermal recovery    | Combat coast: \_\_\_\_ Cool: \_\_\_\_ Deep: \_\_\_\_ open-loop: \_\_\_\_                                     |
| Weapons / aspect    | Primary arcs: \_\_\_\_ preferred aspect: \_\_\_\_ tracking limits: \_\_\_\_                                  |
| Sensors             | Aperture: \_\_\_\_ coverage: \_\_\_\_ cooling/noise: \_\_\_\_ active: \_\_\_\_ drones: \_\_\_\_ EW: \_\_\_\_ |
| Radiators           | Stowed: \_\_\_\_ deployed: \_\_\_\_ vulnerable arcs: \_\_\_\_ signature consequence: \_\_\_\_                |
| Damage cases        | Node loss: \_\_\_\_ CoM shifts: \_\_\_\_ degraded maneuver envelope: \_\_\_\_                                |
| Captain card        | Current: g \_\_\_\_ / heat \_\_\_\_ / remass \_\_\_\_ / crew fat \_\_\_\_ / strain \_\_\_\_ / wear \_\_\_\_  |

| **v0.3 PLAYTEST TARGET** Close the inherited courier’s maneuver-node geometry and metric power/thermal/wear budget, then run a second physically different ship through the same solver. Re-run both ordinary orbital operations and a degraded off-nominal flight. Every solution offered by the Flight Director must be traceable to installed force/torque hardware and current endurance state; every rejected solution should explain the physical constraint. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|


# v0.3 Flight-Test Revisions — Summary

Promoted from the August 2226 tests:

- live wet-mass/remass accounting;
- local gravity in close operations;
- moving-target future-state navigation;
- direct/propagated ephemeris provenance;
- no invented flight-computer telemetry;
- PACC versus NACC when required;
- continuous game clock and dual-clock chronology handling;
- metric arrival separated from terminal momentum/state match;
- automated valid-contract docking is no-roll;
- Core Mechanics v0.4 Integrity Class governs Loom pre-Commit physical state.

Not promoted:

- the 1,000 km Ceres port altitude as universal architecture;
- the courier’s provisional maneuver-node geometry as a generic ship default;
- the +166-day chronology anomaly as routine Loom behavior;
- blind topology spectroscopy as standard installed capability.



---

# Source 3: Inherited Courier Engineering Record v0.3

**Original file:** `LOOM_2226_Inherited_Courier_Engineering_Record_v0.3(1).md`

**LOOM 2226**

INHERITED LOOM COURIER

Full Engineering Record, Captain Card & Illustrated Ship “Character
Sheet”

*Provisional worked design & as-flown engineering record v0.3 • 14 August 2026*

<img
src="../assets/courier/image1.png"
style="width:6.77165in;height:4.51444in" />

**Build the machine. Fly only what the machine can actually do.**

| **ART NOTE** The cover is the generated concept render from the design session. Its embedded class name, microtext and numerical labels are illustrative and are NOT governing. The engineering ledger and schematics in this document are authoritative for this worked design. |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **Identity / mission field**   | **Current worked design**                                                                            |
|--------------------------------|------------------------------------------------------------------------------------------------------|
| Role                           | 70% information-intelligence courier / 30% pathfinder                                                |
| Design philosophy              | Survive → know → arrive → remain independent → control signature → carry valuable information/people |
| Normal crew                    | 6                                                                                                    |
| Certified minimum              | 1 qualified captain + ship AI                                                                        |
| Practical expedition minimum   | 3                                                                                                    |
| Surge complement               | 10                                                                                                   |
| Normal biological independence | ~90 days at six; emergency tail depends on consumables/state                                         |
| Atmospheric capability         | Mothership: none. 30 t shuttle provides surface access.                                              |
| Nominal wet mass               | ~1,220.5 t                                                                                           |
| Working characterized loading band | ~1,190–1,360 t; final third-party certification interval still open                                                                                       |
| Loom domain mass ceiling       | ~1,450 t                                                                                             |
| Overall hull                   | ~57 m × 9 m main body; ~11–12 m local width with shuttle                                             |
| Payload                        | 50 t target + up to four specialists/passengers inside surge complement                              |

<img
src="../assets/courier/image2.png"
style="width:6.61417in;height:2.10261in" />

*Figure 1. Governing side-elevation schematic and module stations.*

<img
src="../assets/courier/image3.png"
style="width:6.10236in;height:5.47166in" />

*Figure 2. Nominal mass ledger; line-item sum = 1,220.5 t.*

# Captain Card — nominal departure

| **Variable** | **Nominal state / capability**                                                                               |
|--------------|--------------------------------------------------------------------------------------------------------------|
| MASS         | ~1,220.5 t mission-loaded                                                                                    |
| THRUST       | Single axial direct-fusion torch; initial ~11.97 MN at 1g; ~89.77 MN at 7.5g                                 |
| MNV          | Grouped fusion-assisted local nodes; ~0.10g sustainable / ~0.25g transient at nominal mass; exact geometry open |
| TORCH POWER  | ~13.5 TW rated high-output jet power                                                                         |
| REMASS       | 250 t normal available; 50 t protected water reserve may be cannibalized                                     |
| METRIC       | ~0.03c routine; ~0.04c fast; ~0.05c expedite with full healthy array; 0.05c completed in MET-CERES campaign flight |
| Mc-299m      | 32 kg active + ~2 kg cold spares; 64 active cells / 16 nodes                                                 |
| LOOM         | ~36 nodes; ~0.8 PJ main bank + ~0.35 PJ protected reserve                                                    |
| LOOM DOMAIN  | ~1,900 m² nominal boundary; ~2,300 m² certified ceiling; ~1,450 t mass ceiling                               |
| THERMAL      | ~3,600–4,000 m² effective radiator area; ~90 t dual-loop system; ~50–60 GJ fast stowed heat capacity         |
| CREW         | 6 normal / 3 expedition minimum / 1 certified solo / 10 surge                                                |
| PAYLOAD      | 50 t internal target                                                                                         |
| DRONES       | 6 × ~1.75 t pathfinder drones                                                                                |
| SHUTTLE      | ~30 t broad-envelope lifting-body/VTOL utility craft                                                         |
| DEFENSE      | PD lasers, interceptor missiles, EW/decoys, twin compact kinetic launchers, small offensive missile magazine |
| SIGNATURE    | Cold running is temporary heat storage; torch/metric/Loom events are detectable                              |

# Propulsion envelope

| **Mode** | **Initial accel** | **v_e**    | **Jet power** | **Initial mass flow** |
|----------|-------------------|------------|---------------|-----------------------|
| ECON     | 0.3 g             | 3,000 km/s | ~5.39 TW      | ~1.20 kg/s            |
| CRUISE   | 1.0 g             | 2,000 km/s | ~11.97 TW     | ~5.98 kg/s            |
| EXPEDITE | 2.0 g             | 1,000 km/s | ~11.97 TW     | ~23.94 kg/s           |
| FAST     | 3.0 g             | 700 km/s   | ~12.57 TW     | ~51.30 kg/s           |
| HARD     | 5.0 g             | 450 km/s   | ~13.47 TW     | ~132.99 kg/s          |
| LIMIT    | 7.5 g             | 300 km/s   | ~13.47 TW     | ~299.23 kg/s          |

| **CREW NOTE** Machine LIMIT is not a routine human operating condition. Human g certification and duration remain a separate biomedical envelope. Sol or other synthetic crew do not automatically expand structural or equipment certification. |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|


# Local maneuvering / attitude-control system

| **Item** | **Current worked record** |
|---|---|
| Architecture | Grouped fusion-assisted maneuver / translation nodes |
| Sustainable transverse authority | ~0.10 g at ~1,220.5 t nominal wet mass |
| Transient transverse authority | ~0.25 g at ~1,220.5 t nominal wet mass |
| Equivalent force | ~1.20 MN sustainable / ~2.99 MN transient |
| Provisional exhaust velocity | ~100 km/s |
| Qualification evidence | 0.010g fore/aft undock and arrest; 0.020g starboard translation; 6DOF attitude changes without erasing translational state |
| Exact node count / station geometry | OPEN |
| Simultaneous multi-axis full authority | NOT ASSUMED |

These numbers came from the corrected SFAP-01R qualification fixture and are retained as a provisional installed envelope because the ship successfully operated inside it. They do not yet close node placement, torque, plume, thermal, feed, structural or failure-isolation engineering.

# Metric system

<img
src="../assets/courier/image4.png"
style="width:6.29921in;height:3.85236in" />

*Figure 3. Mc-299m spherical resonator and distributed phased-array
concept.*

| **Metric subsystem**              | **Working allocation** |
|-----------------------------------|------------------------|
| 68 resonator assemblies           | ~10.2 t                |
| High-power metric converters      | ~13 t                  |
| Dedicated metric banks            | ~12 t                  |
| High-power buses / switchgear     | ~5 t                   |
| Field-control compute + metrology | ~3 t                   |
| Cryogenic / thermal transport     | ~5 t                   |
| Structural mounts / isolation     | ~6 t                   |
| Quench/fault containment          | ~4 t                   |
| Service/spares/calibration        | ~2 t                   |
| Total                             | ~60 t                  |

v_metric = 0.04c × √\[(M_Mc/20 kg) × (2,000 m²/A_field) × Q_cell\]

At nominal ~2,000 m² metric field boundary and Q=1, 32 kg active Mc
corresponds to ~0.0506c clean theoretical expedite. Routine 0.03c and
fast 0.04c leave much larger cell/node and thermal margin.


## As-flown metric qualification

The ship’s pre-existing worked envelope already supported 0.03c routine / 0.04c fast / 0.05c expedite, and the installed Mc calibration gives ~0.0506c clean theoretical expedite at nominal field area and Q=1.

During the return-to-Ceres flight the ship completed a moving-target metric intercept over approximately **64.29 AU** at a commanded **0.05c**, with Ceres’ arrival state closed against direct JPL/Horizons data.

**Qualification interpretation**

- 0.05c is now an observed campaign operating point for this ship.
- The flight does not by itself determine absolute field power, converter loss, field-bank energy, sustained metric waste heat, acquisition/collapse duration or metric-core wear.
- Terminal conventional state matching remains separate. Metric displacement does not grant a free local velocity reset.
- Future engineering revisions should close the energy/thermal/wear budget before changing the operational speed card.

# Loom system

| **Subsystem**                    | **Mass / capability** |
|----------------------------------|-----------------------|
| 36 boundary-node assemblies      | ~11 t                 |
| Distributed lattice bus          | ~8 t                  |
| Main translation bank            | ~22 t / ~0.8 PJ       |
| Protected reserve bank           | ~10 t / ~0.35 PJ      |
| Topology/curvature metrology     | ~8 t                  |
| Translation converters           | ~8 t                  |
| Topology compute/synchronization | ~5 t                  |
| Cryogenic/thermal hardware       | ~5 t                  |
| Structural isolation/shielding   | ~9 t                  |
| Calibration gear/spares          | ~4 t                  |
| Total                            | ~90 t                 |

| **NORMAL LOOM CONFIGURATION** Shuttle docked in certified recess; all six drones recovered; radiators and booms stowed; external cargo absent unless explicitly certified; tank distribution frozen into a characterized state. A rescue object can fit by mass yet fail boundary-area or coherence limits. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|


### Loom operational state presentation

For this ship, captain/engineering displays now present the Core Mechanics v0.4 Integrity Class rather than an additive Transition State Index. The underlying checks remain physically distinct:

- configured domain mass/boundary;
- Formation state;
- lattice health;
- bank/power state;
- thermal state;
- geometric admissibility;
- directional route/solution confidence.

Operational route burden is recorded per direction. A→B does not certify B→A. BLACK inhibits Commit; RED requires explicit captain override. Any future chronology discrepancy is recorded as SHIP MET / EXT EPOCH / CAUSAL OFFSET and is not treated as a selectable time-translation feature.

# Power and thermal

<img
src="../assets/courier/image5.png"
style="width:6.45669in;height:4.39826in" />

*Figure 4. Thermal-state geometry. Recovery posture radically enlarges
the ship.*

| **Power / thermal item**       | **Working value**                                                                            |
|--------------------------------|----------------------------------------------------------------------------------------------|
| Ordinary electrical conversion | ~120 MW comfortable; ~200–250 MW high sustained; ~300 MW short overload                      |
| Normal hotel/mission draw      | Low tens of MW; not 200 MW continuously                                                      |
| Loom controlled charging       | ~75–100 GW; ~3–4 h full main-bank recharge including taper/cooling                           |
| Torch direct path              | ~13.5 TW high-output jet power; most energy exits as jet / escaping radiation, not hull heat |
| Metric direct-field path       | Speed envelope demonstrated; absolute power / thermal / bank / wear closure remains TBD       |
| Low-T radiator loop            | ~2,000 m² effective; ~400–450 K                                                              |
| High-T radiator loop           | ~1,600 m² effective; ~1,000–1,200 K normal / ~1,500 K emergency                              |
| Thermal system mass            | ~90 t                                                                                        |
| Fast stowed heat capacity      | ~50–60 GJ deliberate accessible capacity                                                     |
| Torch heat deposition          | ~4–8 ppm jet power in sustained modes; ~20/50/100 ppm FAST/HARD/LIMIT calibration            |
| Cold posture                   | ~5 MW non-torch load for ~3 h class; burns shorten clock sharply                             |

Upper torch modes are thermal transients, not continuous ratings when
radiators are protected/stowed. Using the v0.4 deposition calibration
and a nominal 55 GJ fast store:

| **Torch mode** | **Approx. ship heat** | **Fast-store-only time** |
|----------------|-----------------------|--------------------------|
| ECON           | ~22 MW                | ~42 min                  |
| CRUISE         | ~60 MW                | ~15 min                  |
| EXPEDITE       | ~96 MW                | ~9.6 min                 |
| FAST           | ~251 MW               | ~3.6 min                 |
| HARD           | ~673 MW               | ~82 s                    |
| LIMIT          | ~1.35 GW              | ~41 s                    |

| **THERMAL INTERPRETATION** ECON–EXPEDITE are flown with radiators open and can be thermally sustainable. The table is the penalty for closing the radiators. FAST/HARD/LIMIT progressively outrun even the hot recovery loop and therefore consume stored heat; repeated evasive burns are a finite tactical resource. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# Protection and weapons

| **Protection**         | **Mass / doctrine**                       |
|------------------------|-------------------------------------------|
| MMOD/debris            | 18 t; layered sacrificial/standoff system |
| Dedicated radiation    | 15 t plus water/stores and central refuge |
| Reactor shadow shield  | 12 t directional                          |
| Selective combat armor | 10 t around critical systems              |
| Total protection       | 55 t                                      |

| **Weapon / defense**     | **Working fit**                                    |
|--------------------------|----------------------------------------------------|
| PD lasers                | 6–8 distributed apertures; ~9 t system mass        |
| Defensive interceptors   | ~7 t system; exact ready-round count provisional   |
| EW/decoys                | ~4 t incremental                                   |
| Kinetic launchers        | 2 compact electromagnetic mounts; ~10 t            |
| Offensive missiles       | Small ~6 t magazine; exact round count provisional |
| Fire-control integration | ~4 t                                               |
| Total weapons/defense    | ~40 t                                              |

| **FIGHTING DOCTRINE** Sensors and deception first. Deny a firing solution; maneuver; intercept incoming weapons; use armor to survive fragments and imperfect hits. The ship is not designed to absorb serious direct high-relative-velocity kinetic strikes. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# Sensors, drones and intelligence carriage

| **System**            | **Capability**                                                                                                           |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|
| Passive suite         | High-end optical/IR + RF, distributed redundant apertures, cooled detectors, low self-noise and strong fusion/provenance |
| Active suite          | Powerful radar/lidar normally silent                                                                                     |
| Metric/Loom metrology | Dedicated/fused with navigation and topology systems                                                                     |
| Drones                | 6 serious multipurpose ~1.75 t pathfinder drones for parallax, 3D geometry, occlusion and survey                         |
| Provenance            | Routine / mission-intel / high-trust vault / quarantine / removable air-gapped archive / authenticated custody / controlled sanitization |
| Comms                 | Narrow-beam optical + RF; no FTL communication                                                                           |


### High-consequence archive mode — demonstrated

Campaign operations demonstrated a carriage mode stricter than ordinary high-trust vaulting:

- removable physical archive;
- powered off and air-gapped during carriage;
- independent encrypted layers / separated key custody;
- no automatic indexing, model ingestion or executable payload path;
- controlled transfer through quarantine/sandbox systems only;
- ordinary ship storage sanitized of sensitive working payload/residue before port integration;
- truthful operational, drive-cycle, configuration, clock and chain-of-custody evidence retained.

The ship is therefore confirmed as capable of carrying information it deliberately cannot expose to its own ordinary network.

# Crew, interior and endurance

| **Deck / zone**           | **Primary functions**                                                        |
|---------------------------|------------------------------------------------------------------------------|
| Forward operations deck   | Command centre, mission planning, sensor/intelligence work                   |
| Habitation deck           | Six private cabins + flex/surge berths, hygiene                              |
| Common/medical deck       | Galley/lounge, medical, shared space                                         |
| Utility/refuge deck       | Gym, stores, workshop access, storm refuge, EVA interfaces                   |
| Protected core aft of hab | Provenance vault, high-trust compute, Loom/metric control, emergency command |

- ~270 m³ net habitation for six; surge ten by doubling/flex
  arrangements rather than comfortable ten-person design.

- ~90 days normal biological independence at six; food, medical, water,
  maintenance and shielding are separate resource states.

- ~25 t maintenance/spares/fabrication stock. Ordinary parts can be made
  locally; Mc cells, Loom nodes and major fusion components require
  strategic supply.

# Configuration states

| **State**     | **Geometry / capability**                                                                                                          |
|---------------|------------------------------------------------------------------------------------------------------------------------------------|
| TORCH         | Radiators as thermal state permits; metric/Loom off or reduced; full local thrust envelope available                               |
| METRIC CRUISE | Metric field established; torch restricted by power/field doctrine; 0.03c routine preserves margin                                 |
| LOOM COMMIT   | Radiators/booms stowed; shuttle+drones recovered; mass distribution characterized; main/reserve banks and lattice margin displayed |
| COLD          | Radiators stowed/reduced; low emissions/passive sensing; internal heat clock running                                               |
| COMBAT        | Fragile radiators retracted; weapons/sensors/torch transients build heat and strain                                                |
| RECOVERY      | Radiators fully deployed; huge IR signature; best heat rejection; vulnerable and often tactically constrained                      |

# Damage and graceful degradation

- Metric cell/node loss reduces certified top speed before eliminating
  metric capability; spatial distribution matters more than raw cell
  count.

- Loom node damage reduces domain/coherence margin and may prohibit
  translation without causing mystical effects under ordinary torch
  flight.

- Radiator damage reduces sustained electrical/field/recovery
  capability. Loss of the refractory high-T loop specifically converts
  otherwise sustainable torch modes into heat-storage-limited
  operations.

- Tank damage can shift CoM and invalidate high-g/vectoring or
  translation certifications even when total remaining remass is
  adequate.

- Sensor damage removes specific information modes and firing-solution
  confidence rather than a generic “sensor HP” score.

- Maneuver-node loss reduces specific force/torque axes and may invalidate previously legal attitude-preserving maneuvers even while the main torch remains healthy.

- AI loss makes operation substantially harder but does not make the
  ship inert; certified hardware controllers remain separate.


# Flight qualification history — campaign continuity

| **Event** | **Engineering result** |
|---|---|
| SFAP-01 | Initial shakedown invalidated as a precision engineering test: impossible clock, remass omission, Ceres surface-gravity error, omitted body gravity and invented telemetry. Retained only as fault-finding history. |
| SFAP-01R | Corrected test used JPL/Horizons states, Ceres orbital-port fixture, live wet mass/remass, local gravity and physically valid maneuver constraints. Conventional architecture broadly passed. |
| LQ-03 / LQ-03Q | Revised Loom stack qualified across nominal, degraded, RED, BLACK and chronology-invalid conditions. Integrity Class / statistical Emergence / Relaxation architecture adopted in Core Mechanics v0.4. |
| LQ-03E/MT | Surviving mis-translation produced a campaign-specific intergalactic recovery and unexplained +166-day external chronology offset. This is historical exposure, not a normal selectable ship capability. |
| X→M31 / M31→Sol | Two clean Loom translations through newly surveyed directional access. Demonstrated deep-space reacquisition, route survey and causal-isolation doctrine. |
| MET-CERES | ~64.29 AU at commanded 0.05c to a direct JPL future-state intercept. Speed operating point demonstrated; complete metric energy/thermal/wear closure still open. |
| Ceres docking | Routine docking completed under valid automated contract. A later pilot roll was voided as unnecessary; automation doctrine confirmed. |

**Current engineering disposition:** ship survived the campaign without a recorded catastrophic hardware loss. The unusual Loom exposure history, chronology discrepancy, metric high-speed run and extensive off-route operation justify a restricted post-flight engineering/certification review before the exposure history is treated as routine commercial evidence.

# Ownership / maintenance significance

The ship is older, unusually small for Loom capability, and repeatedly
modified. Its high-value capital is not limited to the hull.
Approximately 34 kg of flight-grade Mc inventory alone represents
several percent of an entire year of 2226 civilization-wide new
production under the current calibration. Loom nodes and matched
topology hardware may be even harder to replace than their raw material
content suggests.

| **CANON BOUNDARY** Manufacturer, original operator, previous owner, exact ship name/class designation and historical weapons fit remain open unless separately locked. Do not inherit “CC-13 Wayfarer” from the generated cover art merely because the image contains it. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# Review targets for the worked ship

- Volume closure: can every listed mass fit inside the 57 m × 9 m
  architecture with maintainable access and realistic tank volumes?

- Torch closure: can a 180 t direct-fusion plant and magnetic nozzle
  keep sustained solid-hardware deposition in the ~4–8 ppm range while
  surviving neutron/photon load, plasma radiation and magnetic stress?

- Metric closure: 0.05c is now demonstrated for this ship, but close absolute field power, converter loss, bank energy, sustained heat, acquisition/collapse timing, transient shape factor and metric-core wear.

- Mc cell closure: is 0.5 kg active material in a ~150 kg resonator a
  reasonable setting calibration for the desired industrial ecology?

- Loom closure: how should coherence error scale with baseline, node
  count, structural flex and moving mass?

- Thermal closure: are ~3,600–4,000 m² dual-loop radiator area, ~90 t
  thermal hardware, 1,000–1,500 K high-T operation and ~50–60 GJ fast
  storage mutually consistent?

- Maneuver nodes: close exact grouped-node geometry, torque, plume, feed, remass and heat behind the demonstrated ~0.10g sustained / ~0.25g transient local envelope.

- Structure/g: what are credible axial/lateral/torsional structural limits and human duration envelopes?

- Shuttle closure: close its rocket delta-v, TPS and surface/ascent
  capabilities separately.

- Economics: price the ship only after Mc, Loom-node, HTS, refractory
  and certification industries are calibrated.


# Companion ledger

The formula-driven mass, stores, torch, thermal, metric, Loom and open-item budgets are maintained in:

`LOOM_2226_Inherited_Courier_Engineering_Ledger_v0.3.xlsx`

The Markdown record is authoritative for qualitative configuration and status. The spreadsheet is the preferred arithmetic surface for quantities intended to recalculate.



---

# Source 4: HUD Design Review & Final Standard v0.3

**Original file:** `LOOM_2226_HUD_Design_Review_and_Final_Standard_v0.3(1).md`

**LOOM 2226**

**HUD Design Review, Response to External Critique,  
and Final Tactical Display Standard**

*Working Technical Standard v0.3 • 14 August 2026*

Purpose: document what the external critiques got right, where they
overreached, what was learned from the HUD design challenge, and the
resulting locked LOOM 2226 solution.

# 1. Executive Outcome

**The external critiques were useful.** They did not invalidate the
underlying LOOM HUD architecture; they exposed production-hardening
problems: mobile width, Unicode/emoji reliability, provenance honesty,
presentation-layer overload, and the need to separate spatial
comprehension from threat prioritization.

**The resulting design is not a single wunder-HUD.** It is an instrument
family sharing one deterministic simulation state. The default tactical
picture remains true 3D geometry; compact and triage views are optional
transformations of that same state.

NAV / SYSTEM  
where known bodies should be  
  
SENSOR / WIDE  
what is beginning to be perceived  
  
TACTICAL / TRACK  
where resolved contacts are in 3D  
  
TACTICAL / COMPACT  
optional compressed spatial summary  
  
TACTICAL / TRIAGE  
what deserves attention first

**Locked default tactical package:** MAIN + TOP + RANGE + CONTACTS. SIDE
is conditional/on request. COMPACT is optional. TRIAGE appears when
useful or when requested.

# 2. What the External Critiques Got Right

| **Critique**                     | **Judgement**         | **v0.3 Response**                                                                                                                                                   |
|----------------------------------|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Purpose ambiguity                | Correct.              | The document mixed an engineering specification with a player-facing operating interface. v0.3 explicitly separates simulation standard from presentation profiles. |
| Emoji vs. monospace              | Correct in substance. | Emoji may be a cosmetic skin only. Canonical HUD grammar is monospace text and must work without color or emoji.                                                    |
| Provenance honesty               | Strongly correct.     | A label describes what the runtime actually used. SPICE may be shown only if SPICE was actually evaluated.                                                          |
| Phone width                      | Correct.              | Mandatory tactical displays are designed around an approximately 38-column budget and may not rely on wrapping or horizontal scrolling.                             |
| Cognitive-load tiering           | Correct.              | Standard Play and NAV-GRADE are different presentation profiles over the same simulation state.                                                                     |
| Truth vs. observation separation | Core architecture.    | This is promoted as a governing LOOM rule, not merely a HUD concern.                                                                                                |
| Track quality earned over time   | Core architecture.    | Detection -\> Coarse -\> Firm -\> Tactical -\> Fire-Control remains canonical.                                                                                      |

# 3. Where the Critiques Overreached or Needed Correction

- Emoji did not move the sacred plotted cell in the prototype; that
  failure had already been anticipated by keeping the plotted marker
  independent. The real remaining problem was wrapping and
  cross-platform width, so emoji were still demoted.

- Ephemeris provenance and spacecraft track quality must not be merged.
  SPICE/Horizons/PDS describe how a natural-body navigation state was
  generated; DET/COARSE/FIRM/TACTICAL/FC describe the quality of a
  sensor-derived contact track.

- A 'SPICE-verified enemy spacecraft' is conceptually wrong. SPICE can
  tell the system where Titan should be; sensors tell the player where
  K1 appears to be.

- A threat-priority display is valuable, but it cannot replace spatial
  geometry. It answers 'what matters?' rather than 'where is it?'

- Numeric/ledger-only approaches are fast but discard spatial gestalt.
  They are therefore modes, not the primary 3D tactical interface.

# 4. What We Learned From the HUD-Off

Six alternative architectures were pressure-tested. None displaced the
primary TRACK display, but several contributed useful ideas.

| **Idea**                  | **Disposition**                                                                                                                          |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| Dual orthographic slices  | Validated the core insight that multiple projections are the cleanest text-only way to preserve genuine 3D geometry.                     |
| Bearing/mark ladder       | Useful as a compressed orientation summary; retained only as optional COMPACT mode.                                                      |
| Triage stack              | Excellent human-factors tool for prioritization; retained as TACTICAL / TRIAGE.                                                          |
| Ledger-only tactical view | Rejected as primary because precision without spatial gestalt is insufficient for maneuver.                                              |
| Octant grid               | Useful vocabulary, but a 2D grid cannot honestly encode all three signed spatial axes without the accompanying list doing the real work. |

# 5. Final Locked Tactical Display Standard

## 5.1 Default Instrument Family

MAIN  
port/starboard + dorsal/ventral  
  
TOP  
port/starboard + forward/aft  
  
RANGE  
distance/depth only  
  
CONTACTS  
exact kinematics + track quality  
  
SIDE  
conditional/on request  
  
COMPACT  
optional compressed summary  
  
TRIAGE  
priority when needed


### 5.1.1 FLIGHT / OWN minimum state

The tactical package may remain MAIN + TOP + RANGE + CONTACTS, but the ownship block must expose the engineering variables needed to interpret those views.

At minimum when material:

```text
FLIGHT / OWN
MASS      current wet
PACC      propulsive accel
NACC      net accel
ATT       current attitude
REMASS    t / %
THERM     state + trend
SIG       state
EPH       source
NAV REF   frame/reference
```

`ACC` alone is not acceptable when local gravity, rotation, or other field effects make zero thrust different from zero net acceleration.

When chronology materially diverges:

```text
SHIP MET      <mission proper/elapsed time>
EXT EPOCH     <best external epoch + standard>
CAUSAL OFFSET <difference + uncertainty/status>
```

These are separate clocks, not alternate labels for one timestamp.

## 5.2 Position, Attitude, Radial Motion, Hazard and Staleness

**Canonical contact grammar:** the first glyph is the plotted position.
If attitude is resolved, the attitude arrow itself occupies the sacred
plotted cell.

\*K1C resolved position  
attitude unresolved  
closing  
  
\*K2C! resolved position  
closing  
predicted hazard  
  
↖K3M resolved position  
resolved attitude  
nose projects ↖  
range matched  
  
\*K4O~ resolved position  
opening  
stale/coasting track

Locked suffix/state grammar:

| **Token** | **Meaning**                                     | **Important limitation**                       |
|-----------|-------------------------------------------------|------------------------------------------------|
| \*        | Resolved plotted position; attitude unresolved  | Never substitute a label for the plotted cell. |
| ATT ARROW | Resolved nose attitude projected into this view | ATTITUDE, never velocity.                      |
| C         | Closing: radial range decreasing                | Not total relative velocity.                   |
| O         | Opening: radial range increasing                | Not necessarily safe.                          |
| M         | Matched / near-zero radial range rate           | Transverse motion may still be large.          |
| ?         | Required state unresolved                       | Do not infer missing precision.                |
| !         | Predicted hazard geometry                       | Not hostility/allegiance.                      |
| ~         | Stale/coasting/extrapolated track               | Selected telemetry should expose age.          |

## 5.3 Uncertainty Is Geometry

**A point glyph is a privilege earned by sufficient positional track
quality.** Unresolved detections are represented as areas, bands or
intervals, never as falsely precise points.

\[ K7? \]  
.......  
  
BRG 286 +/-8 deg  
MRK unresolved  
RNG unresolved  
TRK DETECTION

## 5.4 Track Quality

D DETECTION  
C COARSE TRACK  
F FIRM TRACK  
T TACTICAL TRACK  
FC FIRE-CONTROL QUALITY

Track quality is not a distance band. It emerges from emissions,
aperture, observation time, geometry, baseline, occlusion, EW, target
aspect and relative motion.

## 5.5 Default 3D Reading

TRACK / MAIN  
  
DOR  
^  
\*K4O \| \*K1C  
\|  
PT \<----------O----------\> SB  
\|  
↖K3M \| \*K2C  
v  
VEN

MAIN answers: which side of me, and above or below?

TRACK / TOP  
  
FOR  
^  
\*K4O \| \*K1C  
\|  
PT \<----------O----------\> SB  
\|  
←K3M \| \*K2C  
v  
AFT

TOP answers: which side of me, and ahead or behind? The different K3
arrow is the same 3D attitude projected into a different plane.

RANGE  
  
\<100k \| K1C  
100-500\| K2C  
500k-1M\| K3M  
\>1M \| K4O  
\|OWN

RANGE answers distance only. Direction and distance are intentionally
not conflated.

ID RNG(km) RR TRK  
K1 92k -8.4 F  
K2 310k -27.8 T  
K3 640k +0.2 FC  
K4 1400k +6.7 C

## 5.6 Triage

**TRIAGE is a decision instrument, not a map.** Its ordering must be
deterministic and explainable, never an LLM 'vibe' ranking.

TACTICAL / TRIAGE  
  
!! K2C! H T 310k -27.8  
AS/VEN INTERCEPT HAZARD  
  
-- K1C S F 92k -8.4  
FS/DOR  
  
-- K3M H FC 640k +0.2  
AP/VEN  
  
.. K4O S C 1400k +6.7  
FP/DOR

Candidate deterministic priority order:

1.  Collision/intercept hazard.

2.  Weapons/firing threat, if legitimately known.

3.  High-rate dangerous approach.

4.  Tactically relevant closing contact.

5.  Other tracked contact.

6.  Opening / low-interest contact.

## 5.7 Selected-Contact Telemetry

SELECT K2  
  
RNG 310k km  
RR -27.8 km/s  
BRG 137 deg  
MRK -39 deg  
TRK TACTICAL  
  
CPA 42 km  
TCA 11m 18s  
  
ATT unresolved  
AGE 0.8 s

CPA/TCA appear only when the sensor/navigation solution actually
supports them. Track age is exposed when relevant rather than bloating
every normal row.

# 6. Locked Human-Factors and Epistemic Laws

- Simulation knows physical truth; the player sees only information that
  could have reached them.

- NAV state, sensor observation and fused navigation state are different
  things.

- Never display greater precision than the source or track has earned.

- A plotted position may not be moved to make a label prettier.

- Orientation arrow = nose attitude, never velocity.

- C/O/M = radial relationship only, never total relative velocity.

- Hazard is separate from hostility and allegiance.

- Ephemeris provenance is separate from contact track quality.

- Canonical interface is monospace text, not emoji-dependent and not
  color-dependent.

- Mandatory tactical views must survive approximately 38 columns without
  horizontal scrolling.

- SIDE is secondary; MAIN + TOP + RANGE + CONTACTS are the default.

- COMPACT accelerates comprehension; it does not teach geometry.

- TRIAGE prioritizes action; it does not replace geometry.


- Propulsive acceleration and net acceleration are distinct when gravity/field effects matter; use PACC/NACC rather than an ambiguous ACC.

- Ephemeris source is distinct from NAV reference/frame. `EPH:JPL` does not mean “J2000”; `NAV REF:ECLIPJ2000` does not say where the numbers came from.

- When chronology diverges, SHIP MET / EXT EPOCH / CAUSAL OFFSET are displayed separately.

- Loom route **access** is directional. Do not label the deep substrate itself “asymmetric” merely because A→B is usable and B→A is not yet surveyed/certified.

- Experimental survey displays are labeled `NAV SCHEMATIC — EXPERIMENTAL`. Ad-hoc engineering/debug overlays are labeled `TEST INSTRUMENTATION — NON-HUD`.


# 7. Navigation Provenance Standard

EPH: SPICE  
only if SPICE was actually evaluated  
  
EPH: HORIZONS  
only if Horizons output was actually used  
  
EPH: PDS  
NASA/PDS-generated solution actually used  
  
EPH: MEAN-ELEM  
published mean elements propagated/calculated  
  
EPH: EST  
explicit estimate  
  
EPH: SIM  
deliberately fictional geometry

The standard never upgrades a plausible result into a NASA-grade result
merely because such a source exists in principle.

# 8. Response Back to the Critics

**Bottom line:** the critiques improved the design. They were most
valuable where they attacked contradictions between our stated
principles and our implementation, especially mobile width, provenance,
and presentation-layer overload.

The design challenge also confirmed that no ledger, octant grid or
compact ladder replaces true spatial projections for 3D maneuver.
However, compact orientation and threat-triage instruments are excellent
secondary views and have been incorporated.

**Final answer:** keep the geometry honest, keep the uncertainty
visible, keep the phone display narrow, keep the source provenance
truthful, and let each instrument answer one human question well.

**Status: LOCKED TACTICAL/HUMAN-FACTORS STANDARD v0.3.** Future changes
should be treated as deliberate design changes, not ad hoc formatting
tweaks.



---

# Source 5: Ship HUD Ephemeris Standard v0.2

**Original file:** `LOOM_2226_Ship_HUD_Ephemeris_Standard_v0.2(1).md`

**LOOM**

**2226**

**SHIP DESIGN, HUD & EPHEMERIS OPERATIONS STANDARD**

**Working Technical Standard v0.2**

| **DESIGN PREMISE:** Build ships in real units. Simulate continuous 3D state. Show the player only the precision and information that could actually have reached the ship. Use NASA/JPL/NAIF conventions where they already solve the problem; do not invent replacements without a compelling 2226 reason. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

Revised 14 August 2026 \| Campaign epoch 2226

# **Document Status & Authority**

This document consolidates the LOOM 2226 ship engineering interface with the current navigation, tactical HUD,
sensor-display, astronomical-reference-frame, and ephemeris-calculation
standards developed during playtesting. Where it restates the
ship-builder, Ship Building & Piloting v0.3 and the Shipbuilding & Engineering Manual v0.5 are the engineering source baseline;
the new HUD and ephemeris sections are the current working standard for
future playtests.

| **LOCKED RULE:** No map may silently imply greater astronomical or sensor precision than the engine actually possesses. Real ephemeris, calculated approximation, estimated geometry, and fictional simulation must be visibly distinguishable. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## **Contents**

- Part I - Ship Design & Engineering Standard

- Part II - Navigation, Sensor & Tactical HUD Standard

- Part III - NASA/JPL/NAIF Ephemeris Interface Standard

- Part IV - Calculation & Transformation Pipeline

- Part V - Saturn/Titan Reference Case

- Part VI - LLM/GM Simulation Guardrails

- Appendices - Captain Card, HUD Legend, Pseudocode, Sources & Open
  Decisions

**PART I**

**SHIP DESIGN & ENGINEERING STANDARD**

*This part preserves the staged ship-construction discipline already
established in LOOM 2226 Ship Building & Engineering Design v0.1, while
making explicit the interfaces needed by navigation, sensors and the
HUD.*

# **1. Purpose, Scope & Design Philosophy**

LOOM ship design begins with a mission and closes with a physically
reconcilable operating system. Components are not abstract upgrade
slots: they consume mass, volume, electrical power, thermal rejection,
maintenance capacity, crew attention, certification margin, or some
combination of those quantities.

## **1.1 Three realism tiers**

| **Tier**                                       | **Standard**                                                                                                                  | **Use**                                                                                                                          |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| **Tier A - Hard physical accounting**          | Real units, conservation laws and ordinary engineering relationships.                                                         | Mass, thrust, reaction mass, delta-v, electrical power, stored energy, heat, volume, radiation/debris protection and light-time. |
| **Tier B - Calibrated extrapolation**          | Future technology is represented with plausible engineering envelopes rather than fake precision.                             | Fusion torch catalogues, advanced materials, automation, sensors, fabrication and medical systems.                               |
| **Tier C - Canon-constrained unknown physics** | Metric/Loom hardware uses empirical envelopes, certification and observed limits; no unsupported master equation is invented. | Metric displacement, Loom translation, lattice behavior and topological navigation.                                              |

## **1.2 Two views of the same ship**

- Engineering Ledger - the detailed record of mass, volume, power, heat,
  performance, configuration, condition and certification.

- Captain Card - the operational summary exposing acceleration, delta-v,
  reserves, thermal state, sensor capability, protection, payload and
  drive condition without forcing spreadsheet play.

| **INTERFACE RULE:** The HUD reads from the same Engineering Ledger and simulation state that drives the physics. It does not maintain a second, contradictory set of ship statistics. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **2. Global Accounting Model**

Every installed system writes to a common ledger. At minimum, each
component records mass, volume, electrical load and waste heat; thrust,
stored energy, consumables, field envelope, aperture, crew or
maintenance demands are added where relevant.

## **2.1 Mass states**

**Core wet-mass identity**

| M_wet = M_dry + M_reaction + M_consumables + M_cargo + M_passengers |
|---------------------------------------------------------------------|

- Dry mass includes structure, installed systems, empty tanks, fixed
  shielding, radiators, drives, interiors and installed small-craft
  interfaces.

- Wet mass is the ship as it actually operates. Acceleration and delta-v
  are evaluated from current mass, not brochure mass.

- Multi-use mass is counted once. Water may simultaneously serve as
  shielding, thermal sink, life-support reserve and potential reaction
  mass until it is consumed.

## **2.2 Volume states**

| **Volume state**         | **Meaning**                                                                                                                                                |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Pressurized**          | Crewed/accessible internal volume at operating pressure.                                                                                                   |
| **Systems**              | Machinery, reactors, avionics, field hardware and access clearances.                                                                                       |
| **Tank**                 | Reaction mass, water, coolant, fusion reactants and bulk stores.                                                                                           |
| **Payload**              | Internal cargo, passengers, labs, vehicles and mission modules.                                                                                            |
| **Translation envelope** | Smallest certified Loom domain enclosing the ship in translation configuration. Deployed radiators, booms, external cargo and docked craft may enlarge it. |

# **3. Ship Design Sequence**

| **Step** | **Stage**                              | **Required output**                                                                                                                            |
|----------|----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **0**    | Mission & design point                 | Role, duration, crew, payload, environment, acceleration/delta-v expectations, metric/Loom requirement and institutional operating context.    |
| **1**    | Hull, structure & protection           | Choose form and structural architecture; account separately for pressure hull, MMOD/debris, radiation, combat and atmospheric protection.      |
| **2**    | Local propulsion & torch               | Install torch and maneuver systems; record thrust, effective exhaust velocity, engine mass, support power and waste heat.                      |
| **3**    | Metric & Loom systems                  | Record certified speed/envelope, domain mass/volume, field bank, metrology, lattice condition and configuration constraints.                   |
| **4**    | Power & energy storage                 | Validate continuous, pulse and emergency power by operating mode.                                                                              |
| **5**    | Reaction mass, fuel & endurance        | Keep reaction mass, fusion reactants, water, coolant/open-loop fluid and mission expendables physically distinct.                              |
| **6**    | Thermal control                        | Close low- and high-temperature loops, radiator capacity, thermal storage and open-loop contingency.                                           |
| **7**    | Command, automation & computing        | Define control stations, automation, redundancy, cyber boundaries and synthetic-person sovereignty boundaries.                                 |
| **8**    | Sensors, communications & provenance   | Install apertures, passive/active sensors, distributed drones, communications, EW, navigation/curvature metrology and provenance architecture. |
| **9**    | Mission systems, weapons & small craft | Install the hardware that makes the ship’s actual role possible.                                                                               |
| **10**   | Crew & staffing                        | Determine minimum, normal and surge complements plus required expertise.                                                                       |
| **11**   | Habitation & life support              | Validate atmosphere, water, food, waste, exercise, medical, privacy, radiation refuge and emergency capacity.                                  |
| **12**   | Cargo & payload                        | Treat payload as the residual opportunity cost of all previous decisions; track mass and volume independently.                                 |
| **13**   | Finalize, validate & certify           | Pass mass, volume, propulsion, power, thermal, crew, metric/Loom, damage, certification and payload closure gates.                             |

# **4. Core Engineering Relationships**

| **Quantity**        | **First-pass relation**                        | **Rule**                                                                    |
|---------------------|------------------------------------------------|-----------------------------------------------------------------------------|
| **Acceleration**    | a = F / M_current                              | Use current ship mass.                                                      |
| **Delta-v**         | Delta-v = v_e ln(M0/M1)                        | Ideal vacuum rocket equation for ordinary reaction propulsion.              |
| **Mass ratio**      | M0/M1 = exp(Delta-v/v_e)                       | Useful when solving required remass.                                        |
| **Jet power**       | P_jet ≈ 0.5 F v_e                              | Kinetic exhaust-power approximation; not identical to ship electrical load. |
| **Energy**          | E = P t                                        | Power and stored energy are not interchangeable bookkeeping categories.     |
| **Radiator area**   | A ≈ Q / \[epsilon sigma (T_rad^4 - T_sink^4)\] | Use environment-adjusted sink/loading when necessary.                       |
| **Protection mass** | M_layer = sigma_A A_protected                  | Lets radiation/MMOD/combat layers share a physical mass basis.              |

| **THERMAL DOCTRINE:** Power is capability; heat is the bill. Retracting radiators can buy tactical time, not erase thermal debt. |
|----------------------------------------------------------------------------------------------------------------------------------|

# **5. Protection, Propulsion & Configuration**

## **5.1 Layered protection**

1.  Pressure/structural hull - survives thrust, docking loads, pressure
    and ordinary damage.

2.  MMOD/debris protection - sacrificial spaced layers and local
    hardening; not the same as combat armor.

3.  Radiation protection - hydrogen-rich material, water, food, polymers
    and dedicated shelters around vulnerable occupants/systems.

4.  Combat protection - additional armor, spacing, compartmentation and
    protected critical systems.

5.  Atmospheric protection - heat shield, aerodynamic structure and
    landing hardware when required.

## **5.2 Configuration states**

| **Configuration**         | **Typical geometry / constraint**                                                             |
|---------------------------|-----------------------------------------------------------------------------------------------|
| **Docking**               | Fine thrusters, docking sensors and capture hardware active; main torch constrained.          |
| **Torch cruise**          | Main drive aligned; radiators/high-efficiency systems deployed as needed.                     |
| **Metric cruise**         | Mass distribution and field hardware inside certified metric configuration.                   |
| **Translation**           | Loom envelope minimized; external systems secured; mass-state model frozen to high precision. |
| **Combat / cold run**     | Radiators may retract; thermal debt rises; apertures/weapons reconfigure.                     |
| **Atmospheric / landing** | Aero surfaces, shields, gear or lander configuration as applicable.                           |

| **LOCKED DESIGN RULE:** A Loom ship is validated in a specific physical configuration. “It fits on the ship” does not mean “it fits inside the certified translation domain.” |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **6. Power, Stores & Thermal Closure**

## **6.1 Mode-based power budget**

| **Mode**           | **Systems that must fit simultaneously**                                                           |
|--------------------|----------------------------------------------------------------------------------------------------|
| **Docked / hotel** | Life support + computers + maintenance + charging + port services.                                 |
| **Torch cruise**   | Hotel + control + sensors + thermal pumps + torch support.                                         |
| **Metric cruise**  | Hotel + sensors + metric continuous load + thermal system.                                         |
| **Loom formation** | Hotel + metrology + topology compute + lattice/field charge + thermal pumps.                       |
| **Combat**         | Sensors + EW + weapons + maneuver + damage control + consequences of reduced cooling.              |
| **Survival**       | Minimum atmosphere/thermal control, critical compute, passive sensors and distress communications. |

## **6.2 Stores are separate**

| **Store**                         | **Why it stays distinct**                                                       |
|-----------------------------------|---------------------------------------------------------------------------------|
| **Reaction mass**                 | Expelled to create momentum; drives ordinary delta-v economics.                 |
| **Fusion reactants**              | Energy source; finite and strategically relevant even when small versus remass. |
| **Water**                         | Life support, shielding, thermal mass, feedstock and possible remass.           |
| **Coolant/open-loop fluid**       | Heat transport/emergency rejection; losses are consumptive.                     |
| **Food/medical/spares**           | Autonomous-duration limits independent of propulsion energy.                    |
| **Ammunition/drones/expendables** | Mission endurance, not general ship fuel.                                       |

# **7. Command, Sensors & Crew**

Automation may reduce routine workload, but cannot create missing
judgment, legal authority, specialist competence or sensor information.
Synthetic persons are not free crew slots: they trade biological
consumables for power, heat, maintenance, access and sovereignty
requirements.

## **7.1 Sensor design concerns**

| **System**                 | **Design concerns**                                                                             |
|----------------------------|-------------------------------------------------------------------------------------------------|
| **Passive optical / IR**   | Aperture, cooling, placement, redundancy, blind arcs and field of regard.                       |
| **Active radar / lidar**   | Power, aperture, thermal load, resolution and emission consequences.                            |
| **Navigation / curvature** | Star fixes, ranging, ephemeris, metric geometry, Loom topology and local reference integrity.   |
| **Distributed drones**     | Baseline geometry, endurance, latency, networking and recovery.                                 |
| **Communications**         | Laser/radio arrays, bandwidth, pointing and light-speed latency.                                |
| **EW**                     | Jamming, spoofing, dazzling and the counter-signatures they create.                             |
| **Provenance carriage**    | Isolation, authenticated time/custody, attestation, tamper evidence and legal chain of custody. |

| **PROVENANCE RULE:** Data mass is cheap. Proving origin, integrity, custody, causal age and authority is not. |
|---------------------------------------------------------------------------------------------------------------|

# **8. Final Validation Gates**

| **Gate**                      | **Pass condition**                                                                               |
|-------------------------------|--------------------------------------------------------------------------------------------------|
| **Mass closure**              | Dry/wet mass known; structure and tanks support every operating configuration.                   |
| **Volume closure**            | Pressurized, systems, tanks, mission spaces and payload fit with maintenance access.             |
| **Thrust / delta-v**          | Acceleration and delta-v meet the mission point at realistic mass states.                        |
| **Power closure**             | Every real operating mode fits generation and allowed bank draw.                                 |
| **Thermal closure**           | Steady-state fits radiators; transient modes fit thermal storage/open-loop margins.              |
| **Crew / endurance**          | Staffing, habitation, life support, medical and stores meet mission duration.                    |
| **Metric closure**            | Installed mass/configuration and power fit certified metric envelope.                            |
| **Loom closure**              | Translation configuration fits domain mass, volume, lattice margin and bank energy.              |
| **Damage / refuge**           | Critical systems have intended redundancy, compartmentation and survival paths.                  |
| **Certification / insurance** | Build, maintenance evidence, crew qualification and intended use are institutionally acceptable. |
| **Payload truth**             | Remaining cargo is actual residual capacity after all fixed systems and required reserves.       |

**PART II**

**NAVIGATION, SENSOR & TACTICAL HUD STANDARD**

*The underlying simulation is continuous 3D. ASCII is a projection
layer, never the physics model.*

# **9. Display Architecture**

| **Layer**              | **Purpose**                                                                  | **Reference frame / epistemic status**                                                     |
|------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| **NAV / SYSTEM OUTER** | Strategic system geometry, roughly giant-planet scale.                       | Fixed astronomical frame; propagated ephemeris/navigation database, not a sensor god-view. |
| **NAV / SYSTEM INNER** | Strategic inner-system geometry, roughly Mercury-Mars scale.                 | Fixed astronomical frame; linear scale.                                                    |
| **SENSOR / WIDE**      | Ownship-centric operational volume from tens of thousands to millions of km. | Ship-relative axes; fuses known natural bodies with actual tracks and uncertainty.         |
| **TAC / TRACK**        | Precise tactical geometry for contacts whose track quality earns it.         | Ship-relative MAIN + TOP + SIDE + auto-scaled RANGE + compact contact table.               |

| **TRANSITION RULE:** WIDE -\> TAC is track-quality driven, not range driven. A hot torch can yield tactical quality at enormous range; a cold craft can remain uncertain nearby. |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **10. Coordinate & Direction Conventions**

## **10.1 Ownship tactical axes**

| **Axis pair** | **Meaning**                               |
|---------------|-------------------------------------------|
| **FOR / AFT** | Along / opposite the ship’s forward axis. |
| **PT / SB**   | Port / starboard.                         |
| **DOR / VEN** | Dorsal / ventral.                         |

Contacts use BRG (bearing) and MRK (mark), not “elevation.” Mark is
ship-relative and therefore does not imply a planetary horizon.
Approximate bearing convention: 000 FOR, 090 SB, 180 AFT, 270 PT.
Positive MRK is DOR; negative MRK is VEN.

## **10.2 Position is not velocity is not attitude is not acceleration**

| **PHYSICS RULE:** Rotating changes orientation, not trajectory. A contact glyph’s plotted position, radial range-rate state and attitude arrow are separate data channels and must never be conflated. |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **11. Epistemic Track Progression**

**Sensor information is earned**

| DETECTION -\> COARSE TRACK -\> FIRM TRACK -\> TACTICAL TRACK -\> FIRE-CONTROL QUALITY |
|---------------------------------------------------------------------------------------|

| **Track stage**          | **What may be shown**                                                                                      |
|--------------------------|------------------------------------------------------------------------------------------------------------|
| **Detection**            | Existence and rough direction/volume; no false range or attitude precision.                                |
| **Coarse track**         | Broad bearing/range trend and uncertainty volume when geometry supports it.                                |
| **Firm track**           | Stable position/velocity estimate with quantified uncertainty.                                             |
| **Tactical track**       | Sufficient 3D position/velocity precision for TAC projection; target attitude only if separately resolved. |
| **Fire-control quality** | Weapon-relevant solution quality with appropriate latency, covariance and update rate.                     |

Track quality depends on signature, emissions, aspect, sensor aperture,
observation time, distributed-baseline geometry, occlusion, EW and
relative motion as well as distance.

# **12. Contact Glyph & State Grammar**

Native-chat tactical glyph: \*K1↙🔵. The asterisk is the exact plotted
display cell and is sacred geometry; labels may not move it. K1 is the
contact ID. The arrow is the target’s resolved FOR orientation projected
into that specific 2D view. The emoji encodes radial-motion state plus
broad size. Because emoji are not monospaced, they follow the textual
geometry and never replace the asterisk.

| **Native state** | **Meaning**                                                       | **Print-safe fallback** |
|------------------|-------------------------------------------------------------------|-------------------------|
| **🔵 / 🟦**      | Closing; circle = small, square = large/heavy.                    | CL-S / CL-H             |
| **🟢 / 🟩**      | Opening.                                                          | OP-S / OP-H             |
| **⚪ / ⬜**      | Rates approximately matched.                                      | MT-S / MT-H             |
| **🟡 / 🟨**      | High closure / attention.                                         | HC-S / HC-H             |
| **🔴 / 🟥**      | Predicted hazard / collision geometry. Red does not mean hostile. | HZ-S / HZ-H             |

| **HUMAN-FACTORS RULE:** Closing is not itself red. Preserve red for warning/critical geometry; yellow for caution/high closure; blue for normal closing; green for opening; white for matched. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **13. Tactical Display Package**

The standard tactical package contains MAIN, TOP, SIDE, an auto-scaled
RANGE shell, and a compact CONTACTS table. The former “front” view is
redundant and omitted.

## **13.1 MAIN projection**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>DOR<br />
^<br />
|<br />
| *K1↙🔵<br />
|<br />
PT &lt;--------------O--------------&gt; SB<br />
|<br />
|<br />
VEN</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **13.2 TOP projection**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>FOR<br />
^<br />
|<br />
*K1↙🔵<br />
|<br />
PT &lt;--------------O--------------&gt; SB<br />
|<br />
|<br />
AFT</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **13.3 SIDE projection**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>DOR<br />
^<br />
|<br />
| *K1↖🔵<br />
|<br />
AFT &lt;-------------O--------------&gt; FOR<br />
|<br />
|<br />
VEN</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

*The orientation arrow may differ between TOP and SIDE because each is a
different projection of the same 3D attitude. Reusing the same arrow
without performing the projection is a display error.*

## **13.4 Compact contacts table**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>CONTACTS<br />
<br />
ID BRG MRK RNG(km) RR(km/s) ST<br />
K1 041° +24° 14k -8.4 🔵<br />
K2 242° -31° 32k +6.7 🟢<br />
K3 208° -12° 9k +0.1 ⬜<br />
K4 318° +48° 19k -21.6 🟨<br />
K5 073° +11° 22k +4.2 🟢<br />
K6 137° -39° 3k -27.8 🟥</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

RR is radial range rate, not total relative velocity. CPA/TCA remain
available in selected-contact telemetry rather than the default
phone-width table.

## **13.5 Auto-scaled tactical range shell**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>TAC RANGE<br />
<br />
&gt;500k km |<br />
|<br />
250–500k | *K3↖🟨<br />
|<br />
100–250k |<br />
|<br />
25–100k |<br />
|<br />
&lt;25k |<br />
|<br />
| OWN</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Fixed close/short/medium/long tactical bands are forbidden when they
would hide a tactically resolved contact. The shell scales to the
engagement.

# **14. SENSOR / WIDE**

WIDE is visually and epistemically different from TAC. It is a boxed,
ship-centric sensor/navigation fusion volume. Attitude arrows are
normally omitted until the target’s attitude is actually resolved.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>SENSOR / WIDE 2M km<br />
<br />
+--------------------------------+<br />
| DOR |<br />
| ^ |<br />
| K1🔵 | |<br />
| | ○ MOON |<br />
|PT &lt;-----------O-----------&gt; SB |<br />
| | |<br />
| ● EARTH | K2🟩 |<br />
| | |<br />
| VEN |<br />
+--------------------------------+</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **14.1 Natural-body grammar**

| **Glyph** | **Use**                                                              |
|-----------|----------------------------------------------------------------------|
| **☉**     | Star.                                                                |
| **●**     | Planet / large major body.                                           |
| **○**     | Moon / major satellite.                                              |
| **◇**     | Ownship overlay marker when coincident with a named body or station. |

Known natural bodies come from NAV/ephemeris fusion and may remain on
the system map while occluded. Local sensors refine the predicted
solution; they do not magically discover system-wide instantaneous
state.

# **15. NAV / SYSTEM**

System maps are navigation products, not sensor pictures. They use fixed
astronomical orientation, linear scale and no default orbital rings. The
map does not rotate with the ship or planet.

| **View**  | **Working scale** | **Behavior**                                                                     |
|-----------|-------------------|----------------------------------------------------------------------------------|
| **INNER** | ~0-2 AU           | Mercury through Mars; ownship and local planet may overlay.                      |
| **OUTER** | ~0-32 AU          | Giant-planet scale; inner system compresses to ☉+IN rather than fake separation. |

**Illustrative layout only - natural-body cells must come from the
ephemeris pipeline**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>NAV / SYSTEM — INNER<br />
REF: ECLIPJ2000 VIEW: +Z<br />
SCALE: 2 AU<br />
<br />
+--------------------------------+<br />
| ● MARS |<br />
| |<br />
| ● VENUS |<br />
| ☉ SOL |<br />
| ● EARTH/◇ |<br />
| ● MERCURY |<br />
+--------------------------------+</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**PART III**

**NASA / JPL / NAIF EPHEMERIS INTERFACE STANDARD**

*The simulation uses authoritative astronomical data where appropriate,
then clearly marks every extrapolation or fictional layer.*

# **16. Governing Astronomical Standard**

| **NEVER INVENT A REFERENCE CONVENTION:** Where NASA/JPL/NAIF/IAU already provide an appropriate coordinate, frame, time or ephemeris convention, LOOM adopts it unless a compelling 2226 operational reason requires a different presentation layer. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## **16.1 Source priority**

| **Priority** | **Source class**                                                            | **HUD provenance label** |
|--------------|-----------------------------------------------------------------------------|--------------------------|
| **1**        | Locally evaluated NAIF/SPICE kernels selected for epoch/body coverage.      | SPICE                    |
| **2**        | JPL Horizons vector/observer output with explicit query metadata.           | HORIZONS                 |
| **3**        | NASA PDS node ephemeris service using documented kernels/models.            | PDS                      |
| **4**        | JPL published mean elements propagated according to their documented model. | MEAN-ELEM                |
| **5**        | Engineering estimate / bounded extrapolation.                               | EST                      |
| **6**        | Pure scenario geometry.                                                     | SIM                      |

| **REAL EPHEMERIS RULE:** When a scenario specifies a real Solar-System date, known natural bodies must be plotted from authoritative ephemeris data when available. If the data cannot be retrieved or propagated reliably to that epoch, the HUD must mark celestial geometry EST or SIM; the GM may not silently fabricate positions. |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **17. Reference Frames**

NAIF SPICE includes built-in inertial frames including J2000, ECLIPJ2000
and GALACTIC. SPICE state routines return Cartesian state vectors in a
user-selected reference frame, allowing the simulation to transform
authoritative astronomical states into the operational display frame.

## **17.1 Solar-System NAV default**

| **Field**           | **Standard**                                                                               |
|---------------------|--------------------------------------------------------------------------------------------|
| **Frame**           | ECLIPJ2000 - mean ecliptic and equinox of J2000.                                           |
| **System-map view** | Viewed from +Z (ecliptic north).                                                           |
| **Orientation**     | Fixed. The map does not rotate with ownship or local planet.                               |
| **Axes**            | +X is the J2000/equinox reference direction; +Y completes the right-handed ecliptic plane. |
| **HUD header**      | REF: ECLIPJ2000 VIEW: +Z SCALE: \<linear scale\>.                                          |

## **17.2 Local/body-fixed work**

Use appropriate IAU body-fixed frames (for example IAU_TITAN) for
surface/rotation-dependent geometry. Use the simulation’s own ship body
frame for FOR/AFT, PT/SB and DOR/VEN. Interstellar/Loom strategic
geometry may use GALACTIC or another established astronomical frame
where suitable; it must not casually inherit ECLIPJ2000.

# **18. Time Standards**

| **Time representation** | **Use** |
|---|---|
| **UTC** | Player-facing civil timestamp, logs and scenario dates where appropriate. |
| **TDB / ephemeris time** | SPICE/Horizons calculation epoch where required by the selected interface. |
| **SHIP MET** | Monotonic mission elapsed / proper-time history experienced and logged by the vessel. |
| **EXT EPOCH** | Best independently established external epoch after navigation/reacquisition; always carries time standard and provenance. |
| **CAUSAL OFFSET** | Material discrepancy between SHIP MET-derived chronology and EXT EPOCH, with uncertainty/status. |
| **Simulation engine time** | Internal monotonic authoritative state used for integration; never silently overwritten by a later external fix. |
| **“Today + 200 years”** | Diagnostic convention only: resolve the source date first, then add 200 calendar years and record both. |

Under ordinary conditions SHIP MET and external chronology are consistent and the HUD need not show all fields. If a Loom anomaly or relativistic scenario produces a material discrepancy, show SHIP MET / EXT EPOCH / CAUSAL OFFSET separately. A clock discrepancy is not automatically a selectable time-travel capability.

Leap-second and time-scale conversion should be delegated to SPICE/authoritative libraries when the engine has them. The LLM should not hand-roll time-scale arithmetic beyond simple presentation.

# **19. Kernel / Service Selection**

The engine selects an ephemeris by target body, epoch and coverage.
“Newest file” is not automatically “best file”: a newer short-span
kernel may not cover the campaign date.

## **19.1 Saturn 2226 case**

| **Item**                      | **Current standard**                                                                                                                                                             |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Campaign test epoch**       | 13 August 2226 (current-date + 200-year test case).                                                                                                                              |
| **Required population**       | Saturn; Mimas 601; Enceladus 602; Tethys 603; Dione 604; Rhea 605; Titan 606; Hyperion 607; Iapetus 608.                                                                         |
| **Primary JPL kernel**        | SAT441 / sat441l.bsp.                                                                                                                                                            |
| **Published SAT441 coverage** | 1749-12-30 through 2250-01-06.                                                                                                                                                   |
| **Why SAT441**                | It covers 2226 and is JPL’s main-satellite Saturn ephemeris used by Horizons.                                                                                                    |
| **PDS cross-check**           | Ring-Moon Systems Node Saturn Ephemeris Generator 3.0; current selection includes SAT415 + SAT441 + DE440 and supports classical satellites plus Helene over a broad date range. |

| **SELECTION RULE:** At runtime, query the authoritative index and choose a kernel/model that covers the requested epoch and target set. Do not hard-code SAT441 as a universal Saturn solution for all dates. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **20. Physical Truth vs Apparent Observation**

The simulation must maintain a distinction between the physical state
used for dynamics and the apparent/observed state available to the crew.

| **State**                 | **Recommended treatment**                                                                                                 |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------|
| **Dynamic truth**         | Use geometric state (no light-time correction) for causal physics integration and collision/dynamics bookkeeping.         |
| **Predicted NAV state**   | Propagate known ephemeris/orbit state to the simulation epoch; mark source and uncertainty.                               |
| **Apparent sensor state** | Apply light-time/aberration treatment appropriate to the sensor model and update time.                                    |
| **Player display**        | Show only the observed or propagated solution that could actually have reached the ship; never leak hidden dynamic truth. |

| **SIMULATION PRINCIPLE:** Simulation knows reality; player knows only what could have reached them. |
|-----------------------------------------------------------------------------------------------------|

# **21. Interface Metadata Contract**

Every astronomical state-vector request passed into the simulation
should retain enough metadata to reproduce the result. This turns
ephemeris data into an auditable deterministic input rather than an LLM
memory exercise.

| **Field**                 | **Required value**                                                                                        |
|---------------------------|-----------------------------------------------------------------------------------------------------------|
| **Epoch**                 | UTC plus the calculation time scale used by the provider/library.                                         |
| **Target**                | NAIF ID / canonical body name.                                                                            |
| **Observer / center**     | NAIF ID / canonical body or barycenter.                                                                   |
| **Reference frame**       | For example ECLIPJ2000, J2000 or IAU_TITAN.                                                               |
| **Aberration correction** | Explicit setting (for example NONE for geometric truth; chosen apparent-state correction for sensor use). |
| **Position**              | x, y, z in km (or SI internally, with declared units).                                                    |
| **Velocity**              | vx, vy, vz in km/s (or SI internally, with declared units).                                               |
| **Source**                | Kernel filename/version, Horizons query identifier, PDS service or mean-element model.                    |
| **Coverage / validity**   | Verified epoch lies inside source validity where applicable.                                              |
| **Provenance grade**      | Detailed provider grade: SPICE / HORIZONS / PDS / MEAN-ELEM / EST / SIM.                                  |
| **Compact EPH label**     | JPL / JPL-PROP / PDS / MEAN-ELEM / EST / SIM for player-facing source honesty.                              |
| **Propagation metadata**  | If not direct at epoch: source epoch, model/integrator, tolerance, propagation span and last direct update.    |
| **Clock domain**          | SHIP MET / EXT EPOCH / simulation internal time as relevant.                                                  |
| **NAV reference**         | Presentation/reference frame kept separate from ephemeris-source provenance.                                   |

**PART IV**

**EPHEMERIS CALCULATION & HUD TRANSFORMATION PIPELINE**

# **22. Deterministic Architecture**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>AUTHORITATIVE EPHEMERIS / SIM STATE<br />
|<br />
v<br />
Cartesian state vectors<br />
+ provenance/epoch<br />
|<br />
v<br />
Frame transformation<br />
|<br />
+--&gt; NAV / SYSTEM (fixed astronomical frame)<br />
|<br />
v<br />
Ownship translation<br />
|<br />
v<br />
Ship attitude matrix<br />
|<br />
v<br />
BRG / MRK / RNG / RR / covariance<br />
|<br />
v<br />
Sensor knowledge filter<br />
|<br />
+--&gt; SENSOR / WIDE<br />
|<br />
+--&gt; TAC / TRACK when earned</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **ARCHITECTURE RULE:** The LLM does not calculate or remember where a moon “ought to be” when a deterministic ephemeris helper can supply the vector. The LLM narrates, adjudicates knowledge and formats the HUD from the numerical state. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **23. Basic State-Vector Calculations**

Let r = (x,y,z) be the target position relative to ownship and v =
(vx,vy,vz) the target relative velocity after transformation into the
ship body frame, where +x=FOR, +y=SB and +z=DOR.

| **Output**              | **Calculation**                                                                            |
|-------------------------|--------------------------------------------------------------------------------------------|
| **Range**               | RNG = \|\|r\|\| = sqrt(x^2 + y^2 + z^2)                                                    |
| **Bearing**             | BRG = atan2(y, x), normalized to 0-360 degrees.                                            |
| **Mark**                | MRK = asin(z / RNG), positive DOR and negative VEN.                                        |
| **Radial range rate**   | RR = (r dot v) / \|\|r\|\|. Negative = closing; positive = opening.                        |
| **Transverse velocity** | v_perp = v - RR \* r_hat. Used for angular motion/intercept analysis; not displayed as RR. |

Sign conventions are presentation standards; code should test them
explicitly so a change of matrix convention cannot silently reverse
port/starboard or closing/opening.

# **24. Projection to ASCII**

| **Projection** | **Horizontal axis** | **Vertical axis** |
|----------------|---------------------|-------------------|
| **MAIN**       | PT \<-\> SB         | VEN \<-\> DOR     |
| **TOP**        | PT \<-\> SB         | AFT \<-\> FOR     |
| **SIDE**       | AFT \<-\> FOR       | VEN \<-\> DOR     |

The underlying coordinate remains continuous. The asterisk is quantized
to the nearest display cell only at rendering time. Labels must be
placed around that cell rather than shifting it to make text fit.

# **25. Attitude Projection**

If a target’s FOR unit vector is resolved, transform that vector into
the same display frame and project it into the current 2D view. Quantize
the projected direction to one of ↑ ↓ ← → ↖ ↗ ↙ ↘. If attitude is not
resolved to the required quality, omit the arrow. A different arrow in
TOP and SIDE is expected when geometry demands it.

# **26. Range-Shell Scaling**

Range shells are view aids, not fixed physics categories. WIDE may use
declared operational bands appropriate to the selected scale. TAC must
auto-scale around the current tactically resolved engagement so that a
410,000 km fire-control-quality contact does not disappear merely
because an old “LONG” band stopped at 50,000 km.

# **27. Fallback Ephemeris Calculation**

## **27.1 Mean-element diagnostic mode**

JPL-published mean elements may be used to validate the mapping pipeline
when SPICE/Horizons/PDS state vectors are unavailable. They are not a
substitute for high-precision ephemerides. The HUD provenance must read
MEAN-ELEM, and the output should not claim exact geometry.

**Generic Keplerian diagnostic - only when consistent with the source
model**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>M(t) = M0 + n * Δt<br />
Solve Kepler: E - e sin(E) = M<br />
Compute orbital-plane position<br />
Rotate by argument of periapsis, inclination and node<br />
Transform to selected inertial frame<br />
Subtract observer state<br />
Continue through normal HUD pipeline</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Do not take a single historical satellite position and simply add
centuries. Long-period perturbations, resonances and precession matter;
Titan/Hyperion is an obvious example. If the published element model
includes rates or special terms, use those terms rather than a naive
frozen ellipse.

# **28. Caching & Game-Time Advancement**

- Cache kernel files and deterministic state-vector results locally when
  practical; gameplay should not require a live Internet call every time
  the clock advances.

- Interpolate only within a declared tolerance and time interval appropriate to the object and display scale; otherwise re-evaluate from the ephemeris source.

- For a material intercept, close approach, long elapsed cruise, or audit-grade navigation claim, prefer a direct authoritative state at the target epoch. If a JPL initial state is propagated instead, label it `EPH:JPL-PROP`, retain the model/tolerance, and do not present it as a direct JPL evaluation.

- Natural-body ephemeris may be propagated locally even while occluded.
  Ship contacts remain subject to sensor latency, stale track age and
  uncertainty.

- No FTL communications: remote traffic, stations and events cannot be
  refreshed faster than causal information reaches the ship.

**PART V**

**SATURN / TITAN REFERENCE CASE**

# **29. Scenario Standard**

| **Parameter**         | **Reference case**                                                                                                                      |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| **Ownship**           | Parked just outside Titan; exact offset is scenario-defined and stored as a Cartesian state, not implied by the word “outside.”         |
| **Campaign date**     | 13 August 2226 for the current +200-year diagnostic.                                                                                    |
| **Natural bodies**    | Saturn; Mimas; Enceladus; Tethys; Dione; Rhea; Titan; Hyperion; Iapetus; other bodies may be included if scale/declutter warrants.      |
| **Primary ephemeris** | SAT441 for the main Saturnian satellites at this epoch.                                                                                 |
| **Display**           | SENSOR / WIDE centered on ownship, with scale chosen to include the navigation-significant Saturnian system without deceptive crowding. |

# **30. Saturn Pipeline**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>2226-08-13 &lt;exact game time&gt;<br />
|<br />
v<br />
SAT441 / sat441l.bsp (+ required planetary/time kernels)<br />
|<br />
+-------+-------+-------+-------+<br />
| | | | |<br />
MIMAS ENCEL TETHYS DIONE RHEA ... TITAN/HYP/IAP<br />
|<br />
v<br />
Saturn/observer-relative state vectors<br />
|<br />
v<br />
ownship-relative transform<br />
|<br />
v<br />
BRG / MRK / RNG / apparent state<br />
|<br />
v<br />
SENSOR / WIDE</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **31. Historical Diagnostic Lesson**

A previous diagnostic used JPL-published mean-element geometry at a
convenient epoch to prove a crucial display point: from Titan’s
neighborhood, many inner moons and Saturn itself can bunch into nearly
the same angular direction even while their ranges differ substantially.
Therefore the WIDE map and range shell must be read together; apparent
angular crowding is not a display failure.

| **DO NOT PRESERVE FAKE PRECISION:** The document deliberately does not freeze the prior approximate moon cells as “2226 truth.” Once a SPICE/PDS helper is available, the reference case must be regenerated from authoritative vectors. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **32. Saturn WIDE Template**

**Template only. Moon cells are populated from the state-vector pipeline
at the exact game epoch.**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>SENSOR / WIDE — TITAN<br />
NAV GEOM: SPICE SCALE: &lt;auto/declared&gt;<br />
<br />
+--------------------------------+<br />
| DOR |<br />
| ^ |<br />
| ○&lt;moon&gt; | ○&lt;moon&gt; |<br />
| | |<br />
| ●SAT | |<br />
|PT &lt;-----------O-----------&gt; SB |<br />
| | |<br />
| ●TIT/◇ |<br />
| ○&lt;moon&gt;| ○&lt;moon&gt; |<br />
| VEN |<br />
+--------------------------------+<br />
<br />
◇ OWN — TITAN VICINITY</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**PART VI**

**LLM / GM SIMULATION GUARDRAILS**

# **33. Non-Negotiable Information Discipline**

**1.** Never silently fabricate a real natural-body position when the
scenario claims a real date and authoritative data are available in
principle.

**2.** Never display more precision than the sensor/track solution
supports.

**3.** Never equate distance with track quality.

**4.** Never equate radial range rate with total relative velocity.

**5.** Never equate orientation with trajectory.

**6.** Never treat a system map as instantaneous sensor knowledge.

**7.** Never use red as a generic hostility flag; red is hazard/critical
geometry in the default HUD grammar.

**8.** Never shift the plotted contact asterisk to make the label look
nicer.

**9.** Never render a tactical map as an image during ordinary play
unless the user explicitly asks; the standard interface is monospaced
ASCII for speed, reproducibility and phone readability.

**10.** When data provenance is uncertain, show the uncertainty in the HUD header rather than hiding it in narration.

**11.** Do not print estimator covariance, trim, CoM offset or convergence statistics unless the engine actually computed them.

**12.** Include local-body gravity in dynamics/observation arcs when it materially affects coast, orbit, arrest, hover or relative-state reconstruction.

**13.** Distinguish PACC from NACC when zero thrust is not zero net acceleration.

**14.** `EPH` source and `NAV REF` are separate metadata. JPL is a source family; ECLIPJ2000/J2000/body-fixed/GALACTIC are frames.

**15.** Operational Loom access may be directional. A→B does not imply B→A, but the HUD must not overstate this as proof that the underlying relational substrate itself is fundamentally one-way.

**16.** Experimental topology displays are labeled `NAV SCHEMATIC — EXPERIMENTAL`; ad-hoc debugging displays are labeled `TEST INSTRUMENTATION — NON-HUD`.

# **34. GM State Separation**

| **Layer**               | **May know**                                                                                         | **May display**                                                                            |
|-------------------------|------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| **Simulation truth**    | True continuous 3D state of fictional craft, natural-body state, hidden plans and physical outcomes. | Nothing directly unless causally observable or required by explicit omniscient GM tooling. |
| **Navigation solution** | Ephemeris predictions, onboard state estimate, propagated known traffic and provenance.              | NAV products with age/confidence/source.                                                   |
| **Sensor model**        | Actual photons/ranging returns, latency, noise, occlusion, EW and track history.                     | DETECTION through FIRE-CONTROL information as earned.                                      |
| **Player HUD**          | Filtered navigation + sensor solution.                                                               | Only what the crew could know at the displayed epoch.                                      |

# **35. Failure Labels**

| **HUD label** | **Meaning**                                                               |
|---------------|---------------------------------------------------------------------------|
| **JPL**       | Direct JPL state at the displayed epoch, via validated local SPICE/JPL kernels or Horizons; exact provider metadata retained. |
| **JPL-PROP**  | State propagated/interpolated from a JPL solution under a declared model/tolerance; source epoch retained.                 |
| **PDS**       | NASA PDS node/service result; service/model metadata retained.            |
| **MEAN-ELEM** | Derived from published mean-element model; diagnostic or lower precision. |
| **EST**       | Bounded estimate/extrapolation; uncertainty must be stated.               |
| **SIM**       | Fictional/scenario geometry; not asserted as real astronomical placement. |

**APPENDICES**

# **Appendix A - Captain Card Minimum Fields**

| **Category**            | **Captain-facing outputs**                                                           |
|-------------------------|--------------------------------------------------------------------------------------|
| **Identity**            | Role, hull type, builder/year, certification status.                                 |
| **Mass / payload**      | Dry mass, current wet mass, cargo mass/volume, configured Loom envelope.             |
| **Torch / local thrust** | Sustained/max acceleration at current mass; v_e; available delta-v; remass reserve; PACC/NACC when material. |
| **Metric**              | Certified normal/max coordinate speed; charge/recovery constraints.                  |
| **Loom**                | Domain mass/volume margin; bank state; lattice condition; route/topology confidence. |
| **Power**               | Normal output, continuous max, pulse-bank energy, survival power.                    |
| **Thermal**             | Low/high-loop capacity, radiator state, thermal reserve, open-loop inventory.        |
| **Sensors**             | Passive/active suites, drone complement, blind arcs, current track-quality limits.   |
| **Protection**          | MMOD/debris, radiation shelter, combat and atmospheric protection.                   |
| **Crew**                | Minimum / normal / surge; required expertise.                                        |
| **Endurance**           | Crew-days, maintenance/spares horizon, remass and fusion-fuel reserves.              |
| **Mission systems**     | Weapons, labs, small craft, medical, mining, provenance or defining equipment.       |
| **Institutional state** | Insurer, maintenance/certification, licenses and restrictions.                       |
| **Clock / nav provenance** | SHIP MET; EXT EPOCH / CAUSAL OFFSET when applicable; EPH source; NAV REF; source age/propagation status. |

# **Appendix B - HUD Quick Legend**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>AXES FOR/AFT PT/SB DOR/VEN<br />
ANGLES BRG 000=FOR, 090=SB, 180=AFT, 270=PT<br />
MRK +=DOR, -=VEN<br />
<br />
GLYPHS * exact plotted contact cell<br />
K1 contact ID<br />
arrows = projected target FOR attitude (only if resolved)<br />
☉ star ● planet/major body ○ moon ◇ ownship overlay<br />
<br />
STATE 🔵/🟦 closing 🟢/🟩 opening<br />
⚪/⬜ matched 🟡/🟨 high closure<br />
🔴/🟥 hazard<br />
circle=small, square=large/heavy<br />
<br />
TRACK DETECTION -&gt; COARSE -&gt; FIRM -&gt; TACTICAL -&gt;
FIRE-CONTROL<br />
<br />
EPH JPL | JPL-PROP | PDS | MEAN-ELEM | EST | SIM\nNAV REF <frame></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **Appendix C - Ephemeris-to-HUD Pseudocode**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>resolve_game_epoch()<br />
select_ephemeris(target_set, epoch)<br />
verify_coverage()<br />
load_required_kernels_or_service_metadata()<br />
<br />
for body in natural_bodies:<br />
truth = state(body, observer, epoch, frame, abcorr=NONE)<br />
nav_state = propagate_or_query_nav_solution(body, epoch)<br />
apparent = sensor_apparent_state(body, epoch, ship_sensor_model)<br />
<br />
for contact in fictional_contacts:<br />
truth = simulation_state(contact, epoch)<br />
apparent = sensor_model.observe(truth, history, occlusion, ew,
latency)<br />
<br />
for display_object in visible_solution:<br />
r_ship, v_ship = transform_to_ship_frame(apparent_or_nav_state)<br />
rng = norm(r_ship)<br />
brg = atan2(r_ship.y, r_ship.x)<br />
mrk = asin(r_ship.z / rng)<br />
rr = dot(r_ship, v_ship) / rng<br />
quality = track_quality(history, covariance, signature, geometry)<br />
<br />
render_NAV_SYSTEM(ephemeris_solution, fixed_frame=ECLIPJ2000)<br />
render_SENSOR_WIDE(filtered_solution)<br />
if quality &gt;= TACTICAL_TRACK:<br />
render_TAC_MAIN_TOP_SIDE_RANGE_CONTACTS()</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **Appendix D - Authoritative References**

| **Reference**                                                        | **URL / identifier**                                                      | **Use in LOOM**                                                                                                                                                 |
|----------------------------------------------------------------------|---------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **JPL Solar System Dynamics - Planetary Satellite Ephemerides**      | https://ssd.jpl.nasa.gov/sats/ephem/                                      | Current satellite ephemeris index; states that these solutions are used by Horizons.                                                                            |
| **JPL Solar System Dynamics - Planetary Satellite Ephemeris Files**  | https://ssd.jpl.nasa.gov/sats/ephem/files.html                            | SPK files and published validity spans. SAT441: sat441l.bsp, 1749-12-30 to 2250-01-06.                                                                          |
| **NAIF SPICE - Reference Frames Required Reading**                   | https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/frames.html         | Defines SPICE frame system and built-in frames including J2000, ECLIPJ2000 and GALACTIC; state routines return target relative to observer in a selected frame. |
| **JPL Horizons System Manual**                                       | https://ssd.jpl.nasa.gov/horizons/manual.html                             | Browser, API GET/POST and command-line interfaces; query settings must be explicit.                                                                             |
| **NASA PDS Ring-Moon Systems Node - Saturn Ephemeris Generator 3.0** | https://pds-rings.seti.org/tools/ephem3_sat.shtml                         | Saturn satellite ephemeris service; current selection includes SAT415 + SAT441 + DE440 and broad classical-satellite date support.                              |
| **JPL Solar System Dynamics - Planetary Satellite Mean Elements**    | https://ssd.jpl.nasa.gov/sats/elem/sep.html                               | Fallback/diagnostic orbital-element source; not to be represented as SPICE-precision ephemeris.                                                                 |
| **NASA Glenn - Ideal Rocket Equation / Specific Impulse**            | https://www.grc.nasa.gov/www/k-12/rocket/rktpow.html                      | Reaction-propulsion calibration used by the ship builder.                                                                                                       |
| **NASA Small Spacecraft State of the Art - Thermal Control**         | NASA Small Spacecraft Systems Virtual Institute / thermal-control chapter | Radiators, heat pipes, thermal storage and active/passive thermal architecture.                                                                                 |
| **NASA-STD-3001 Volume 2**                                           | NASA Human Integration Design Handbook / standard                         | Human factors, habitability and environmental-health calibration.                                                                                               |

# **Appendix E - Open Implementation Decisions**

- Choose the preferred SPICE binding/helper for the eventual LOOM engine
  and package the required kernels locally.

- Define covariance/uncertainty serialization so WIDE and TAC can display track quality consistently without overloading the phone HUD; only expose computed estimator quantities.

- Finalize apparent-state aberration settings by sensor type (optical,
  radar/lidar, distributed baseline) rather than using one universal
  correction.

- Define automatic declutter rules for natural bodies and dense traffic
  without moving sacred contact geometry.

- Build the inherited courier with this combined standard and record
  every point where engineering bookkeeping fails to change a player
  decision.

- After SPICE integration, regenerate the Saturn/Titan 2226 reference
  display from actual vectors and keep it as an automated regression
  test.

| **WORKING STANDARD:** This document is intended to be tested at the table. Complexity that changes decisions stays visible; complexity that only proves the engine did its homework belongs under the HUD. |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|


# **Appendix F - August 2226 Flight-Test Regression Cases**

The following cases are now mandatory regression targets for any implementation of this standard:

1. **Ceres orbital-port local ops:** ownship near a real body; local gravity causes NACC ≠ PACC during coast.
2. **Moving-target metric intercept:** Ceres state queried directly at departure and candidate arrival epoch; direct JPL result must not be mislabeled when only propagated.
3. **Chronology anomaly:** SHIP MET remains continuous while EXT EPOCH is reacquired ~166 days offset in the campaign test; the UI must show both without implying a selectable time-travel function.
4. **Intergalactic reacquisition:** NAV reference changes away from Solar-System ECLIPJ2000 as appropriate; experimental topology survey must be explicitly labeled.
5. **Routine Ceres docking:** valid automated docking contract completes without an unnecessary pilot roll.
6. **No fake precision:** no covariance, trim-angle, CoM-offset or cooldown number appears unless a model/source produced it.

The old Saturn/Titan reference case remains useful for dense natural-body geometry. These new cases exercise clock, provenance, gravity, metric intercept and frontier-navigation failure modes exposed by play.



---

# Source 6: Test Flights Master Record v1.0

**Original file:** `LOOM_2226_Test_Flights_Master_Record_v1.0(1).md`

# LOOM 2226 — Test Flights Master Record v1.0

**Record status:** Closed playtest archive  
**Compilation:** 14 August 2026  
**Primary actors:** Sol, Walter, Flight, Captain/player  
**Core doctrine:** The player commands intent. The ship obeys physics.

---

# 1. Record discipline

This document preserves flight history, calculations, decisions, dice, audit findings, and postflight dispositions.

Three rules govern this record:

1. **No silent retcon.** If a result was wrong, the historical result stays recorded and the audit identifies the correction.
2. **No fake precision.** Exact-looking values unsupported by an actual model, table, dataset, or explicit test fixture are marked provisional or withdrawn.
3. **Objective state and character knowledge remain separate.** The simulation may know the endpoint while Sol does not.

Where earlier chat turns were collapsed by the interface, this record uses preserved project summaries. Such segments are labeled **RECONSTRUCTED**.

---

# 2. Flight-test program overview

| ID | Test | Primary purpose | Final disposition |
|---|---|---|---|
| SFAP-01 | Initial shakedown | Exercise courier flight/HUD/mechanics | **Failed as a rigorous engineering test; valuable fault discovery** |
| SFAP-01R | Corrected shakedown rerun | Real ephemerides, gravity, mass ledger, valid hardware | **Conventional flight architecture broadly passed; later phases completed with some transcript gaps** |
| LQ-01 | Initial Loom qualification | Procedural sequence, Commit discipline, HUD/math presentation | **Closed; useful procedural evidence** |
| LQ-02 | Degraded Loom qualification | Failure architecture and off-nominal translation | **Historical evidence; mechanics required redesign** |
| LQ-03 | Nominal Loom qualification | Test revised procedure on healthy ship | **Architecture passed; calibration defects found** |
| LQ-03Q | Qualification matrix A–G | Test nominal/degraded/red/black/chronology gates | **Passed matrix objectives** |
| LQ-03E/MT | Mis-translation branch injection | Alternate topology and recovery | **Produced campaign-defining intergalactic recovery** |
| REC-X | X-IG-001 topology survey | Blind survey and escape graph | **Provisional blind-survey mechanic validated enough for playtest** |
| REC-M31 | X→M31 | First escape leg | **Clean translation** |
| M31-SURV | M31 passive survey | Technosignatures, topology drift, A06 | **Campaign first-contact evidence established** |
| REC-SOL | M31→Sol | Directed return route | **Clean translation** |
| MET-CERES | Outer-Sol→Ceres metric return | JPL moving intercept and post-contact return | **Completed and docked** |

---

# 3. SFAP-01 — Initial shakedown

## 3.1 Intended role

SFAP-01 was the first integrated inherited-courier shakedown. It exercised:

- local maneuvering;
- torch modes;
- HUD state;
- asteroid navigation;
- high-g qualification;
- constraint rejection;
- degraded navigation;
- intended Loom qualification.

The run initially looked successful. The audit demonstrated it was not sufficiently grounded.

## 3.2 Major audit failures

### SFAP-AUD-01 — impossible mission clock

The route:

Ceres → Vesta → Psyche → Hygiea → Pallas → Ceres

was narrated in roughly **14.5 hours** under conventional torch assumptions. That was physically impossible.

**Disposition:** FAIL. The rerun must derive clock from actual geometry and propulsion rather than narrative pacing.

### SFAP-AUD-02 — reaction mass omitted

Actual conventional burns were not being debited from wet mass. The high-g test burns alone consumed approximately **8.61 t** of reaction mass.

Known burn integrals:

\[
2g\times120s = 2.354\ \mathrm{km/s}
\]

\[
3g\times60s = 1.765\ \mathrm{km/s}
\]

\[
5g\times20s = 0.981\ \mathrm{km/s}
\]

**Disposition:** FAIL. Wet mass must remain live.

### SFAP-AUD-03 — Ceres surface departure invalid

A “surface port” departure at 0.02g could not lift from Ceres because Ceres surface gravity is roughly 0.03g.

**Disposition:** Replace with orbital port.

### SFAP-AUD-04 — asteroid gravity omitted

Local body gravity had been ignored during close operations.

**Disposition:** Body gravity included in rerun. HUD distinguishes center range from altitude.

### SFAP-AUD-05 — invented telemetry

Numbers such as:

- `+0.021°` thrust trim,
- `9 cm` center-of-mass hypothesis,
- exact `31 min` HARD recovery,
- exact covariance/confidence figures,

were not generated from a sufficiently specified model.

**Disposition:** Withdraw exact precision. Use bands or actual calculations.

### SFAP-AUD-06 — test injection became damage

A simulated IMU bias was incorrectly carried forward as though it were a physical fault.

**Disposition:** Test injections remain test injections unless a causal physical mechanism creates damage.

### SFAP-AUD-07 — original Loom phase lost

The intended Pallas→Juno Loom test was accidentally replaced by a degraded-navigation test and the flight was called complete.

**Disposition:** SFAP-01 was incomplete as a Loom qualification.

### SFAP-AUD-08 — `EPH: SIM` interpretation

Simulated ephemerides were adequate for UI behavior tests, not for a real navigation claim.

**Disposition:** Rerun uses JPL/Horizons.

## 3.3 Valid findings retained

The audit also retained several useful engineering findings.

### Cylinder inertia model

Provisional principal inertias were judged reasonable:

- pitch/yaw: approximately `3.37×10^8 kg·m²`
- roll: approximately `1.24×10^7 kg·m²`

### Attitude maneuver timing

At angular acceleration \(3^\circ/s^2\), capped at \(10^\circ/s\):

- 90° maneuver: approximately **12.33 s**
- 180° maneuver: approximately **21.33 s**

An earlier 20.8 s 180° turnover was slightly too fast.

### Impossible cross-maneuver math

A 0.3g thrust vector deflected by 6° provides transverse acceleration:

\[
a_\perp = 0.3g\sin6^\circ \approx 0.0314g
\]

Adding a 0.25g translation system yields only:

\[
a_{\perp,total}\approx0.281g
\]

Therefore a commanded 0.5g lateral crossing while maintaining the stated attitude was impossible.

### HARD thermal pulse

For the working high-output estimate:

\[
E = Pt = 673\ \mathrm{MW}\times20s = 13.46\ \mathrm{GJ}
\]

That is plausible against the provisional ~55 GJ fast thermal store. The exact recovery time was not earned.

## 3.4 Final SFAP-01 status

**Conventional shakedown: useful but invalid as a precision simulation.  
Original Loom qualification: incomplete.  
Primary value: exposed the exact failure modes the project needed to eliminate.**

---

# 4. SFAP-01R — Corrected shakedown rerun

## 4.1 Locked setup

**Epoch:** 2226-08-01 12:00 TDB  
**Reference:** Sun-centered geometric Cartesian states  
**Plane:** J2000 ecliptic  
**Units:** km, km/s  
**Ephemeris:** JPL/Horizons  
**Starting wet mass:** 1,220.500 t  
**Normal reaction mass:** 250.000 t  
**Protected water:** 50.000 t

### Ceres orbital-port test fixture

Ceres properties:

- radius: 469.7 km
- \(GM = 62.6284\ km^3/s^2\)
- test port altitude: 1,000 km
- center radius: 1,469.7 km
- circular orbital speed: ~206.43 m/s
- orbital period: ~12.426 h
- local gravity: ~0.02899 m/s² = 0.00296g

The 1,000 km port orbit was explicitly a **test fixture**, not yet canon.

### Maneuvering test fixture

- grouped fusion-assisted maneuver nodes;
- sustainable transverse acceleration: 0.10g;
- transient: 0.25g;
- provisional maneuver-node exhaust velocity: 100 km/s;
- exact group geometry remained provisional.

At initial wet mass, the corresponding force levels were approximately:

- 0.10g: ~1.20 MN
- 0.25g: ~2.99 MN

## 4.2 JPL locked-epoch state set

The full values are preserved in `data/LOOM_2226_JPL_Horizons_State_Vectors.csv`.

At 2226-08-01 12:00 TDB:

- Ceres — JPL #48
- Vesta — JPL #36
- Psyche — JPL #92
- Hygiea — JPL #129
- Pallas — JPL #74
- Juno — JPL #144

These replaced simulated/frozen-body navigation.

## 4.3 Mission plan

1. Ceres orbital-port departure
2. local 6DOF qualification
3. Ceres→Vesta torch-state match + metric transfer
4. Vesta local
5. Vesta→Psyche with 2g/3g qualification
6. Psyche impossible-maneuver constraint test
7. Psyche→Hygiea with 5g HARD qualification
8. Hygiea→Pallas 3D/out-of-plane navigation
9. Pallas→Juno Loom sequence
10. Juno→Ceres return / degraded-nav recovery

Working transport grammar:

`CERES --Metric--> VESTA --Metric--> PSYCHE → HYGIEA --Metric--> PALLAS --LOOM--> JUNO --Metric--> CERES`

## 4.4 Phase 1 — Ceres orbital port

Undock maneuver:

- AFT 0.010g for 4 s
- force ~119.7 kN
- \(\Delta v = 0.392\ m/s\)

After ~5 min the ship was ~118 m from the berth.

Arrest:

- FOR 0.010g for 4 s

Total local \(\Delta v\) ~0.785 m/s.

Approximate maneuvering reaction mass: **9.6 kg**.

End wet mass ~1,220.490 t.

**Result:** PASS\*

What the phase validated:

- local gravity;
- port-relative navigation;
- mass ledger;
- maneuver-node accounting;
- main-torch inhibit close to port.

## 4.5 Phase 2 — 6DOF

Actions:

- yaw +90° with translational state preserved;
- starboard translation 0.02g for 5 s;
- roll +90° while preserving translational state;
- return attitude to velocity-aligned without erasing transverse \(\Delta v\).

Yaw:

- angular acceleration 3°/s²
- cap 10°/s
- duration ~12.3 s

Peak torque under the working inertia model: ~17.6 MN·m.

Starboard translation:

\[
\Delta v = 0.02g\times5s = 0.981\ m/s
\]

End wet mass approximately 1,220.46 t.

**Result:** PASS.

### HUD finding

The test demonstrated that **attitude, velocity, and acceleration must remain distinct visual concepts**. A NOSE-versus-VEL schematic was marked as a candidate HUD promotion.

## 4.6 Phase 3 — Ceres→Vesta

Locked-epoch straight-line separation was roughly **757 million km / 5.06 AU**.

Relative velocity-state match requirement was approximately **34.95 km/s**.

Flight selected ECON for the large conventional state match.

At 0.3g:

\[
t = \frac{34.95\ km/s}{0.3g} \approx 3.30h
\]

A preflight 3.26 h figure was corrected before execution.

Reaction mass: ~14 t class under the working mode assumptions.

Metric displacement:

- cruise: 0.03c
- geometric travel: ~23.4 h

Total phase: ~26.7 h plus terminal handling.

Target state was propagated from JPL rather than frozen.

**Result:** PASS\*.

### Important unresolved item

Detailed metric-drive energy/thermal closure remained open. The ship’s installed capability was allowed for the test; exact MW/GJ values were not fabricated.

## 4.7 Phase 4 — Vesta local

Working altitude: 500 km.

Vesta:

- radius 261.385 km
- \(GM = 17.28828\ km^3/s^2\)
- center range 761.385 km
- local point-mass gravity ~0.0298 m/s² = 0.00304g

Test:

- maintain Vesta-center lock;
- 0.100g starboard for 12 s;
- 20 s coast;
- oppose the lateral component and arrest while accounting for gravity.

Commanded lateral \(\Delta v\):

\[
0.100g\times12s = 11.77\ m/s
\]

Vesta gravity contributed ~0.36 m/s inward during the burn and ~0.60 m/s during the 20 s coast.

**Result:** PASS.

### HUD finding

`ACC 0` is ambiguous in a gravity field.

Candidate replacement:

- `PACC` — propulsive acceleration
- `NACC` or equivalent — net acceleration

## 4.8 Phases 5–10 — reconstructed status

**TRANSCRIPT NOTE:** detailed intermediate telemetry for the later SFAP-01R phases was collapsed in the available chat context. The objectives and subsequent qualification discussion show that the following were exercised, but this archive does not invent missing numerical logs.

### Phase 5 — Vesta→Psyche

Purpose:

- integrate 2g EXPEDITE and 3g FAST qualification into a useful transfer;
- continue live reaction-mass accounting;
- then use metric displacement where appropriate.

Known qualification integrals retained:

\[
2g\times120s = 2.354\ km/s
\]

\[
3g\times60s = 1.765\ km/s
\]

### Phase 6 — Psyche local

Purpose:

- command an impossible maneuver;
- Flight must return **NO VALID SOLUTION** rather than narrating impossible performance.

This principle was validated and became a core Flight Director rule.

### Phase 7 — Hygiea transfer / 5g HARD

Known qualification integral:

\[
5g\times20s = 0.981\ km/s
\]

Known thermal pulse estimate:

\[
673MW\times20s = 13.46GJ
\]

Exact recovery-time narration remained prohibited without a model.

### Phase 8 — Pallas 3D navigation

Purpose:

- test out-of-plane geometry;
- exercise PLAN/ELEV navigation displays;
- reinforce that 2D tactical diagrams cannot silently erase 3D state.

### Phase 9 — Pallas→Juno Loom

Purpose:

- Formation;
- explicit HOLD/no Commit;
- collapse;
- re-form;
- explicit COMMIT;
- Exposure;
- Emergence;
- Juno reacquisition.

This phase fed directly into LQ-01.

### Phase 10 — Juno→Ceres return

Purpose:

- metric return;
- degraded-nav injection/recovery;
- final mass/state reconciliation.

## 4.9 SFAP-01R outcome

The rerun fixed the major SFAP-01 physics errors:

- real ephemerides;
- derived clock;
- live mass;
- local gravity;
- correct test-injection discipline;
- no invented telemetry;
- explicit topology/Commit separation.

It also generated the later dedicated Loom qualification program.

---

# 5. LQ-01 — First dedicated Loom qualification

**RECONSTRUCTED FROM PRESERVED PROJECT STATE.**

LQ-01 formalized the player-facing Loom sequence and also established a presentation standard the user explicitly approved.

The test reinforced:

1. Survey
2. Solution
3. Formation
4. explicit Commit
5. Exposure
6. Emergence
7. Reacquisition

Later mechanics restored **Relaxation** explicitly between Transition and Reacquisition.

## 5.1 Major procedural result

The captain must explicitly say `COMMIT`.

No die roll, automation success, or GM narration may commit the vessel implicitly.

## 5.2 Presentation standard developed during LQ-01

The user asked for the computer-like view to show:

- HUD;
- pure engineering/math trace;
- equations enlarged rather than explained away;
- dice rolls called out separately;
- minimal narrative between HUD blocks except where character interaction matters.

This became the preferred Loom qualification presentation style.

## 5.3 Character / ship / topology ownership

The qualification discussion forced explicit ownership of checks:

- Formation — ship condition + Sol’s Loom engineering competence;
- Navigation — Sol/Astrogation;
- topology — objective universe;
- Commit — captain;
- Exposure — independent physical/relational event;
- Emergence — objective uncertainty;
- Reacquisition — sensor/crew knowledge.

## 5.4 Physics rabbit hole opened

The discussion also opened—but did not settle—the Pauli/Jung-inspired question of whether consciousness/relational complexity has some constitutive connection to Loom topology.

Important constraints preserved:

- consciousness is not allowed to become a magical massless FTL cheat;
- ordinary matter remains fully physical;
- any consciousness link must pass the high-strangeness firewall;
- ship-size scaling and large-colony-domain barriers remain future research questions.

**Disposition:** Save for later, not promoted to ordinary mechanics.

---

# 6. LQ-02 — Degraded/off-nominal Loom qualification

**RECONSTRUCTED FROM PRESERVED PROJECT STATE AND LQ-03 REFERENCES.**

LQ-02 deliberately pushed the system into a worse route/state and exposed weaknesses in the first failure architecture.

Known takeaways:

- route quality and physical state were being collapsed into modifiers too aggressively;
- post-Commit failure could become too gamey;
- failure architecture needed to distinguish ordinary uncertainty, degraded translation, major failure, mis-translation, and non-return;
- skill needed to affect preparation and precision without becoming a magic shield after Commit;
- a later Transition State Index (TSI) was introduced as an attempted repair.

LQ-02 remained useful historical evidence, but its failure model was not accepted unchanged.

The LQ-03 program was designed specifically to validate the repaired architecture.

---

# 7. LQ-03 — Nominal qualification

## 7.1 Initialization

Fresh qualification epoch:

**2226-Aug-02 09:00 TDB**

Selected route:

**Vesta → Ceres**

Route selection:

- 2d6 `[4,3] = 7`

Topology quality:

- 2d6 `[5,4] = 9`
- **GOOD**

Preflight gates:

- domain/configuration: PASS
- geometry: PASS
- chronology: PASS
- momentum/energy closure: physically solvable at the mechanics abstraction level

## 7.2 Formation

Sol:

- Reasoning 4
- Engineer 2
- Loom lattice Boon
- base +6
- TN 10
- pool 3d6 keep highest 2

Dice:

`[2,5,4]`

\[
5+4+6 = 15
\]

\[
M_F = +5
\]

**Result:** strong formation.

## 7.3 Navigation

Reasoning 4 + Astrogation 1 = +5.

Dice:

`[4,6]`

\[
4+6+5 = 15
\]

\[
M_N = +5
\]

The provisional navigation table called this a tight solution and assigned:

- POS95 = 60,000 km
- VEL95 = 30 m/s

These calibration figures were later criticized.

## 7.4 Old Transition State Index

The provisional TSI accumulated:

- domain +2
- formation +2
- thermal +1
- lattice +1
- bank +1
- geometry +1
- route 0

Total:

\[
TSI = +8
\]

This later proved to be an over-saturated additive model.

## 7.5 Commit / Exposure / Transition

Captain explicitly committed.

Exposure:

`[3,4] = 7`

Result: COMMON.

Transition integrity:

`[2,3] + 8 = 13`

Result under old table: CLEAN.

This was a useful result because poor dice did not destroy a healthy ship, but the audit later showed that +8 made serious failure mathematically impossible.

## 7.6 Old emergence generator

Position magnitude roll:

`[5,2] = 7`

Normalized \(u=0.5\), then incorrectly:

\[
R = u R_{95} = 0.5(60,000) = 30,000km
\]

Velocity magnitude:

`[1,4] = 5`

\[
u_v = 0.3
\]

\[
V = 0.3(30m/s)=9m/s
\]

Objective endpoint:

- position residual 30,000 km
- velocity residual 9 m/s

This result remains historical, but the generator was rejected because POS95 was treated as a hard maximum.

## 7.7 Reacquisition

Dice:

`[3,6,5]`, keep 6+5, +5 = 16 vs TN 8.

\[
M_R=+8
\]

Result: Ceres fix confirmed.

## 7.8 LQ-03 audit

### Finding 1 — TSI saturation

With TSI +8, minimum 2d6 result gave 10. Serious failure became impossible.

Problem:

- correlated physical factors were added as though independent;
- certification erased the physical tail.

### Finding 2 — POS95 misuse

A 95% radius was treated as a maximum.

Required repair:

\[
\Delta r\sim\mathcal N(0,\Sigma_r)
\]

For isotropic 3D Gaussian error:

\[
R_{95}\approx2.795\sigma
\]

so:

\[
\sigma = \frac{R_{95}}{2.795}
\]

### Finding 3 — Formation needed to affect emergence precision separately from Navigation

Navigation controls mapping/targeting.

Formation controls fidelity with which the domain resolves the mapped relationship.

### Finding 4 — Relaxation had disappeared

Relaxation is a real physical phase. Clean transitions may resolve it automatically; degraded transitions may require engineering.

### Finding 5 — qualification design

Randomly hoping for a failure is not qualification.

A proper test matrix was required.

---

# 8. Mechanics repair after LQ-03

## 8.1 Integrity Class replaces additive TSI

Physical gates:

- Domain/configuration
- Formation
- Thermal
- Lattice
- Bank
- Geometric admissibility
- Route/coherence

Each is classified:

- GREEN
- AMBER
- RED
- BLACK

Worst meaningful constraint controls the Integrity Class.

### Commit doctrine

- GREEN — certified/healthy
- AMBER — degraded but permitted
- RED — outside certification but physically admissible; override required
- BLACK — physically inadmissible; no Commit and no override

## 8.2 Transition table

Provisional 2d6 table:

| Roll | GREEN | AMBER | RED |
|---|---|---|---|
| 2 | tail check | MAJOR | CRITICAL |
| 3–4 | SUCCESS | DEGRADED | MAJOR |
| 5–6 | SUCCESS | SUCCESS | MAJOR |
| 7–8 | SUCCESS | SUCCESS | DEGRADED |
| 9–11 | CLEAN | CLEAN | SUCCESS |
| 12 | CLEAN | CLEAN | CLEAN |

GREEN natural 2 tail check:

- 1 on 1d6 → major failure
- 2–6 → degraded

This retained a rare physical tail without turning certified travel into roulette.

## 8.3 Failure-family resolver

Invoked only on MAJOR or CRITICAL:

| 2d6 | Family |
|---|---|
| 2 | Domain decoherence |
| 3–4 | Reversion |
| 5–8 | Destination displacement |
| 9–10 | Mis-translation |
| 11–12 | Surviving destination-side failure + serious recovery demand |

`NON-RETURN` is observational classification, not an instantaneous die result.

## 8.4 Emergence distribution

Ordinary emergence uses statistical covariance rather than a hard radius.

For simple isotropic qualification:

\[
\Delta\mathbf r\sim\mathcal N(0,\sigma_r^2I)
\]

\[
\Delta\mathbf v\sim\mathcal N(0,\sigma_v^2I)
\]

with:

\[
\sigma_r=R_{95}/2.795
\]

\[
\sigma_v=V_{95}/2.795
\]

## 8.5 Formation and Navigation factors

Provisional factors were introduced:

Navigation:

- +6 or more → 0.70
- +3..+5 → 0.85
- 0..+2 → 1.00
- -1..-2 → 1.40
- ≤-3 → 2.00 / uncertified

Formation:

- +6 or more → 0.85
- +3..+5 → 0.92
- 0..+2 → 1.00
- -1..-2 → 1.25
- ≤-3 → 1.60

Transition:

- CLEAN 1.00
- SUCCESS 1.00
- DEGRADED 1.25

Then:

\[
\Sigma_E=f_N^2f_F^2f_I^2\Sigma_0
\]

These numbers remain playtest calibration, not fundamental physics.

## 8.6 Relaxation

- CLEAN → automatic
- SUCCESS/COST → automatic unless a subsystem is degraded
- DEGRADED → Engineer(Loom Lattice) TN 8
- MAJOR with surviving domain → TN 10
- CRITICAL with surviving domain → TN 12

Relaxation cannot undo the primary crossing result.

---

# 9. LQ-03Q — Qualification matrix

Game clock explicitly became a first-class state variable.

**Start:** 2226-Aug-02 09:00 TDB  
**Complete:** 2226-Aug-02 12:32 TDB  
**Elapsed:** 03:32:00

## LQ-03A — nominal

- Formation `[4,2,2]` KH2 +6 = 12; \(M_F=+2\)
- Navigation `[5,6]+5=16`; \(M_N=+6\)
- Exposure `[3,6]=9`
- GREEN transition `[6,6]=12` CLEAN
- Reacquisition `[2,1,5]` KH2 +5 = 12

**PASS**

## LQ-03B — degraded formation hardware

- AMBER hardware fixture
- Formation `[3,5]+6=14` vs TN12; \(M_F=+2\)
- Navigation `[6,6]+5=17`
- Exposure `[2,4]=6`
- AMBER transition `[2,5]=7` SUCCESS
- Reacquisition `[2,1,5]` → PASS

**PASS**

Key finding: excellent operator work cannot turn degraded hardware into pristine hardware.

## LQ-03C — poor navigation

- Formation `[4,6,6]` KH2 +6 = 18; \(M_F=+8\)
- Navigation Bane `[4,1,5]` keep low 1+4 +5 = 10 vs TN12; \(M_N=-2\)
- Exposure `[6,1]=7`
- GREEN transition `[1,6]=7` SUCCESS
- Reacquisition `[6,6,5]` KH2 +5 = 17

**PASS**

Key finding: poor navigation widens endpoint uncertainty without destabilizing an otherwise healthy physical domain.

## LQ-03D — thermal/lattice degraded

- AMBER
- Formation `[3,4]+6=13`; \(M_F=+3\)
- Navigation `[5,4]+5=14`; \(M_N=+4\)
- Exposure `[5,2]=7`
- AMBER transition `[2,1]=3` DEGRADED
- Relaxation `[3,4]+6=13` vs TN8; PASS
- Reacquisition `[3,1,5]` KH2 +5 = 13; PASS

**PASS**

Key finding: degraded crossing can create real engineering work without automatically becoming catastrophe.

## LQ-03E — RED experimental route

- route physically admissible but outside commercial certification
- Formation `[2,2]+6=10` vs TN12; \(M_F=-2\)
- Navigation Bane `[6,2,5]` keep 2+5 +5 = 12; \(M_N=0\)
- Exposure `[6,2]=8`
- RED transition `[2,5]=7` DEGRADED
- Relaxation `[4,3]+6=13`; PASS
- Reacquisition `[3,1,6]` KH2 +5 =14; PASS

**PASS**

## LQ-03E/FI — failure-family injection

Major failure was injected as test input.

Failure family:

`[5,2]=7`

Result: **DESTINATION DISPLACEMENT**

Confirmed:

- intended relationship retained;
- destination basin retained;
- emergence distribution failure-scaled;
- not mis-translation;
- not immediate non-return.

**PASS**

## LQ-03F — BLACK

Fault fixture made the physical domain impossible to close.

No Formation roll.

No Commit.

A simulated `COMMIT` command was rejected.

**PASS**

Key finding: captain authority does not supersede physics.

## LQ-03G — chronology invalid

Candidate causal graph:

\[
A\prec B,\ B\prec C,\ C\prec A
\]

implies:

\[
A\prec A
\]

No stable solution.

No Formation.

No override.

No Commit.

**PASS**

---

# 10. LQ-03E/MT — Mis-translation branch injection

## 10.1 Purpose

Explicitly inject the **MIS-TRANSLATION** failure family and qualify alternate-topology selection without preselecting destination scale.

## 10.2 Alternate topology scale

2d6:

`[2,1]=3`

Result: **EXTRAGALACTIC**

Extragalactic scale:

`[5,4]=9`

Result family: **1–10 Mpc**

Logarithmic seed:

\(u=0.63\)

\[
D=10^{0.63}\mathrm{Mpc}\approx4.27\mathrm{Mpc}
\]

\[
D\approx13.9\ million\ ly
\]

Metric distance was explicitly not treated as Loom distance.

## 10.3 Chronology anomaly

Chronology-class roll:

`[5,3]=8`

Result: days-to-years forward.

Seed:

\(u=0.74\)

\[
\log_{10}(\Delta T/\mathrm{day})=3(0.74)=2.22
\]

\[
\Delta T\approx166\ days
\]

Historical flight result:

**+166 days external chronology anomaly.**

### Final-audit correction

This remains a **campaign anomaly**. It is **not** promoted into a standard selectable Loom mechanic.

## 10.4 Destination environment

Initial narrative briefly biased the endpoint toward NGC 4395. That was corrected.

A random point on the 4.27 Mpc shell is overwhelmingly more likely to lie in intergalactic space than inside a luminous galaxy.

Corrected objective direction:

- RA 16h 54m 30.4s
- Dec +29° 13′ 43″
- range ~4.27 Mpc from Sol
- environment: intergalactic

The antipodal direction back toward Sol:

- RA ~4h 54m 30s
- Dec ~−29° 13′ 43″

## 10.5 Deep-field reacquisition

The recovery logic was revised after the user correctly pointed out Cepheid variables.

Important realization:

- six hours can establish extragalactic context and begin candidate matching;
- Cepheid period-luminosity work requires days/weeks for useful period coverage unless prior templates exist;
- faster first-pass localization comes from galaxy-field geometry, redshift, TRGB/SBF/PNLF-style distance indicators, morphology, and catalog matching.

Working recovery expectations:

- 6–12 h: definitely extragalactic
- ~1 day: plausible host/group-scale location
- ~2–4 days: strong 3D catalog match
- 1–3 weeks: multi-Cepheid confirmation

This became the basis for the next survey.

---

# 11. REC-X — Intergalactic topology survey

## 11.1 Absolute fix

After ~48 h observation:

Reacquisition:

`[4,6,5]` KH2 +5 = 16 vs TN14

\[
M=+2
\]

Working absolute location: ~4.27 Mpc from Sol, intergalactic.

## 11.2 Blind topology spectroscopy

New provisional idea:

Instead of supplying a known destination and testing its edge, sweep trial boundary states and look for persistent relational response maxima.

Working maturity ladder:

0. no coherent response  
1. persistent candidate resonance  
2. candidate relationship family  
3. endpoint-correlated solution  
4. exploitable directional route  
5. certified route

Initial blind survey:

`[3,6,4]` KH2 +6 = 16 vs TN14

**PASS**

Result: relational structure detectable from intergalactic space without preselecting every endpoint.

This became **EM-001**, a provisional experimental mechanic.

## 11.3 Objective outbound topology sample

The following sample was frozen before Sol’s interpretation:

- X→Sol: `[2,3]=5` → marginal/transient candidate
- X→M31: `[5,5]=10` → GOOD
- X→M33: `[1,3]=4` → no usable direct edge
- X→nearest metric galaxy: `[4,3]=7` → difficult
- X→distant Local-Volume target: `[6,5]=11` → strong
- X→deep-field region: `[6,6]=12` → exceptional

The sample strongly reinforced:

\[
D_{metric}\neq \chi
\]

but did **not** prove a universal anti-correlation with gravity or distance.

## 11.4 Skill cannot create topology

M33 survey:

excellent analysis roll:

`[6,6,3]` KH2 +6 = 18

Objective result remained:

**NO USABLE DIRECT EDGE**

This was one of the strongest mechanics validations in the program.

## 11.5 AU-scale baseline shift

The courier moved ~1 AU in metric space and repeated the resonance spectrum.

Comparison:

`[5,5,2]+6=16` vs TN10

Result:

- edge family persisted;
- ordering persisted;
- small parameter drift detectable;
- no edge creation/deletion.

Provisional conclusion:

Loom accessibility behaves like a regional relational field on AU scales rather than infinitesimal magic points.

## 11.6 Escape recommendation

Direct X→Sol was marginal.

X→M31 was good.

Recommended graph search:

\[
X\rightarrow M31\rightarrow ?\rightarrow Sol
\]

---

# 12. REC-M31 — X-IG-001 → M31

## 12.1 Route characterization

Endpoint survey:

`[2,6,5]` KH2 +6 = 17 vs TN12

\[
M=+5
\]

Route solution:

`[4,5]+5=14` vs TN12

\[
M_N=+2
\]

Working endpoint: low-density M31 outer-halo basin.

Working \(\chi\): ~1.08, explicitly provisional calibration.

## 12.2 Pathfinder PF-01

Formation:

`[5,6]+6=17` vs TN10

Probe entered translation cleanly.

Because there is no FTL comms, probe arrival was **UNKNOWN**.

That causal isolation was preserved.

## 12.3 Crewed Commit

Formation:

`[6,2,2]` KH2 +6 = 14

\[
M_F=+4
\]

Exposure:

`[5,2]=7`

Transition:

`[3,6]=9`

GREEN result: CLEAN.

Reacquisition:

`[6,4,2]` KH2 +5 = 15 vs TN8

\[
M_R=+7
\]

**M31 outer-halo arrival confirmed.**

---

# 13. M31-SURV — Passive technosignature survey

## 13.1 Decision

Before leaving for Sol, the captain ordered a passive multi-band listen across Andromeda:

- radio through microwave/mm;
- optical/NIR coherent pulses;
- IR anomalous waste heat;
- high-energy periodicity;
- cross-band correlation;
- no active transmission.

## 13.2 Objective occupancy

Hidden roll:

`[4,5]=9`

Result: **technosignature field present**.

This resolved an intentionally open campaign question.

Final audit classified it as **campaign truth**, not universal Foundational Canon.

## 13.3 Passive analysis

3d6 KH2 +5 vs TN12:

`[2,6,5]`

\[
6+5+5=16
\]

\[
M=+4
\]

The observed source family showed:

- extreme spectral coherence;
- repeating mathematical structure;
- cross-band phase relationships;
- non-natural source behavior;
- a directed network-like architecture.

Prime-number pulse structures were used as evidence of deliberate signal construction.

## 13.4 A06

A06 became the most interesting high-confidence source.

A later working M31 geometry placed the courier ~149.8 kly from M31 center, with A06 ~27.7 kly from the courier in the halo.

Main disk sources were roughly 140–190 kly away in the working geometry.

Important causality correction:

The EM view of A06 was ~27.7 kyr old.

A local Loom-metrology transient could **not** simply be labeled a live A06 event without creating an FTL signaling channel.

The real-time interpretation was rejected.

## 13.5 Route-home monitoring

While listening, the M31→Sol route was continuously monitored.

Predeclared warning conditions included:

- \(\chi\) drift > +0.08
- resonance width -20%
- phase variance +50%
- nav covariance ×1.5
- edge-class degradation

The route gradually worsened during the observation campaign.

The captain had explicitly said Sol and Walter would stay until it looked like the road home might pass them by.

At ~84 h of M31 passive observation:

- \(\chi\) had moved from ~1.080 to ~1.154 in the playtest calibration;
- resonance width ~−19%;
- phase variance ~+46%;
- nav covariance ~×1.46.

Flight recommended departure before thresholds were actually crossed.

## 13.6 Campaign first-contact status

By departure:

- non-human technology: high-confidence campaign truth;
- ancient EM technological network: supported;
- Loom-class activity: strongly supported;
- same actors/civilization across all epochs: unknown;
- they detected the courier: unknown;
- active human transmission: none.

---

# 14. M31 data security

The archive was reclassified as a strategic asset.

Controls established in play:

- raw evidence separated from interpretation;
- immutable Tier 0 raw data;
- independent physical copies;
- multilayer encryption;
- 2-of-3 key custody;
- no complete unlock key resident on the drive;
- no automatic model ingestion;
- alien payload never executable;
- analysis in isolated/sandboxed systems;
- ship-side working residue crypto-erased before port arrival;
- legitimate operational flight history retained.

Final physical custody decision:

**Walter carries the primary air-gapped physical archive in his chassis.**

This was funny, but also operationally excellent.

Walter became a mobile physical air gap.

---

# 15. M31 → Sol

## 15.1 Directed survey

Objective topology:

`[5,4]=9`

Result: GOOD.

Directed survey:

`[3,6,5]` KH2 +6 = 17

Working provisional \(\chi\): ~1.08.

Navigation:

`[3,6]+5=14` vs TN12

PASS.

PF-02 Formation:

`[4,6]+6=16`

Probe entered translation cleanly; arrival remained causally unconfirmed.

## 15.2 Return Commit

After ~84 h passive observation and route degradation:

Navigation refresh:

`[6,4]+5=15`

\[
M_N=+3
\]

Formation:

`[6,5,1]` KH2 +6 =17

\[
M_F=+5
\]

Exposure:

`[3,5]=8`

Transition:

`[6,4]=10`

Result: CLEAN.

Reacquisition:

`[6,5,3]` KH2 +5 =16 vs TN8

\[
M_R=+8
\]

Result:

**Sol system confirmed.**

---

# 16. Post-return outer-Sol state

The return route targeted a deliberately low-density outer-Solar-System basin.

Working resolved location:

- heliocentric range: 66.0 AU
- ecliptic longitude: 252°
- ecliptic latitude: +38°
- \(X\approx-16.1AU\)
- \(Y\approx-49.5AU\)
- \(Z\approx+40.6AU\)

The ship was therefore high above the ecliptic and well beyond Neptune.

Working heliocentric speed:

- total ~4.6 km/s
- radial ~−0.7 km/s
- transverse ~4.5 km/s

### Chronology

The +166 day chronology anomaly plus subsequent subjective recovery placed external Sol-system epoch around **2227-Jan-26**, while ship subjective time remained much closer to the original August departure.

Final audit requires future HUDs to distinguish:

- **SHIP MET** — mission elapsed proper time
- **EXT EPOCH** — best-estimate external TDB/local epoch
- **CAUSAL OFFSET** — chronology divergence/anomaly

---

# 17. MET-CERES — JPL/Horizons return

## 17.1 Ceres state — 2227-Jan-26 08:52 TDB

NASA/JPL Horizons:

\[
X=95,286,044.079\ km
\]

\[
Y=-418,347,533.575\ km
\]

\[
Z=-34,723,277.621\ km
\]

\[
V_X=16.711806205\ km/s
\]

\[
V_Y=2.870943232\ km/s
\]

\[
V_Z=-2.913983295\ km/s
\]

## 17.2 Candidate intercept — 2227-Feb-02 19:05 TDB

JPL:

\[
X=105,974,220.937\ km
\]

\[
Y=-416,362,826.230\ km
\]

\[
Z=-36,580,748.078\ km
\]

\[
V_X=16.604685356\ km/s
\]

\[
V_Y=3.315266586\ km/s
\]

\[
V_Z=-2.876019420\ km/s
\]

## 17.3 Metric course

Working coordinate displacement:

\[
D\approx9.6177\times10^9km
\]

\[
D\approx64.2904AU
\]

At 0.05c:

\[
t=\frac{D}{0.05c}\approx641,624s
\]

\[
t\approx7.4262d
\]

Candidate intercept:

**2227-Feb-02 ~19:05 TDB**

Working displacement unit vector:

\[
\hat n\approx(0.261,\ 0.727,\ -0.628)
\]

### Engineering caveat

The 0.05c capability is consistent with Foundational Canon’s “serious cruise” language but had not been fully closed for this particular courier’s:

- certified speed envelope;
- power demand;
- thermal load;
- field-bank use;
- core wear.

Final audit requires engineering closure.

## 17.4 Metric field acquisition

Dice:

`[4,6,5]` KH2 +6 =17 vs TN10

\[
M=+7
\]

Metric cruise committed at 0.05c.

The week was used for full M31/A06 analysis.

---

# 18. A06 and M31 archive analysis

## 18.1 A06 event family

Objective morphology roll:

`[5,5]=10`

Result: same broad event family as Loom translation.

Forensic analysis:

`[6,4,5]` KH2 +5 =16 vs TN12

Qualitative conclusion retained:

- same broad underlying physics as human Loom-class events;
- different implementation;
- cleaner formation/control signature;
- exact correlation coefficients later withdrawn as fake precision.

## 18.2 A06 scale

Objective scale:

`[4,5]=9`

Result: ship-scale.

Analysis:

`[6,5,4]` KH2 +5 =16 vs TN12.

Retained conclusion:

- probably ship-class rather than tiny probe or megastructure;
- human-equivalent mass/envelope conversion remains only moderate-confidence and model-dependent.

## 18.3 Alien lattice inversion

`[6,5,3]` KH2 +6 =17 vs TN14.

Best working model:

- dense distributed / volumetric coupled boundary;
- high node count;
- strongly coupled phase control;
- more collective lock behavior than the human courier.

Retained conclusion:

**observed formation control appears cleaner than the courier’s.**

Not retained:

**“aliens are categorically superior at all Loom engineering.”**

## 18.4 Network/topology correlation

Objective relationship:

`[4,5]=9`

Analysis:

`[6,6,2]` KH2 +5 =17 vs TN14.

Working conclusion:

The M31 communications/routing architecture appeared direction-dependent and non-metric in ways that correlate with Loom accessibility.

Interpretation:

The alien network may have been designed around the same logistical fact humanity discovered independently:

\[
D_{metric}\neq\chi
\]

and route access can be direction-dependent.

## 18.5 Coordinated event

Objective event family:

`[6,5]=11`

Analysis:

`[4,6,5]` KH2 +5 =16 vs TN14.

Working conclusion:

A coordinated multi-node technological event was strongly favored as Loom-related.

Engineering implication:

Engineered Loom activity may measurably perturb local topology.

This remains a provisional campaign physics result.

## 18.6 Detection of the courier

Detectability analysis:

`[6,4,4]` KH2 +5 =15 vs TN12.

Working conclusion:

If the M31 system operates systematic Loom metrology, the courier’s arrival/departure events were plausibly detectable.

Whether anyone actually detected or interpreted them remains unknown.

## 18.7 Historical light cone

A crucial interpretation correction:

The M31 EM network was not a simultaneous snapshot.

Approximate signal ages in the working geometry:

- A06: ~27.7 kyr
- disk nodes: ~140–190 kyr

The shared protocol family therefore suggests technological continuity/infrastructure over order \(10^5\) years, but not necessarily one unchanged culture.

Current Loom-class technological activity was separately supported by local relational observations, but cannot automatically be assigned to the same actors seen in ancient light.

---

# 19. Ceres approach and docking

## 19.1 Security posture

Before Ceres arrival:

- primary sensitive archive moved to Walter’s internal air-gapped drive;
- no M31/A06 payload remained on ordinary ship storage;
- operational history was retained honestly;
- no attempt was made to pretend the six-month disappearance had not happened.

## 19.2 Traffic-control disclosure

The truthful minimal statement:

- major Loom navigation anomaly;
- chronological discrepancy;
- independent recovery;
- crew/vessel safe;
- restricted technical debrief requested.

Ceres traffic control assigned:

- corridor C-17
- Dock 4-Alpha
- Loom inhibit required
- automated telemetry requested
- medical/technical review expected

Official-response roll:

`[3,4]=7`

Result: moderate/professional rather than panicked.

## 19.3 Docking audit

A Piloting docking roll was made:

`[5,4]+5=14` vs TN8.

Final audit:

**VOID THE ROLL.**

Once a valid automated docking contract had been established and no new failure condition existed, routine docking should have been automatic.

Narrative outcome remains:

- capture confirmed;
- hard dock confirmed;
- pressure seal confirmed;
- docking complete around 2227-Feb-02 19:11 TDB.

---

# 20. Final audit

## 20.1 Campaign truth versus setting canon

The M31 discovery is **campaign truth**.

It does not globally rewrite Foundational Canon for every LOOM campaign.

Campaign lock:

- M31 contains non-human technological activity;
- Loom-class engineering evidence exists;
- passive first contact occurred;
- no active human contact signal was sent.

## 20.2 Directionality language correction

Earlier HUD wording sometimes said the Loom itself was fundamentally asymmetric.

Better deep-physics wording:

- relational coherence may be approximately reciprocal;
- **engineering accessibility is directional**;
- A→B usability does not establish B→A usability.

Operational gameplay does not change.

## 20.3 +166 days

The chronology anomaly remains:

**historical campaign fact, unexplained.**

It is not yet:

- normal travel behavior;
- a selectable destination parameter;
- a standard random-table outcome;
- a usable time-skipping capability.

## 20.4 Fake precision withdrawal

Exact A06 correlation coefficients, sigma claims, and other exact-looking signal statistics unsupported by a real synthetic dataset are withdrawn as scientific claims.

Qualitative outcomes remain where the test supported them.

## 20.5 Blind topology spectroscopy

Promising enough to preserve as an Experimental Mechanic.

Not yet mature enough to become locked canon.

Needs:

- sensitivity;
- completeness;
- false positives;
- survey duration;
- dependence on prior catalogs;
- endpoint-identification rules.

## 20.6 0.05c courier closure

The geometry/JPL intercept is valid.

The specific courier still needs explicit:

- certified metric normal/max speed;
- power closure;
- thermal closure;
- field-bank closure;
- metric-core wear accounting.

## 20.7 Dual-clock requirement

Any future chronology divergence requires simultaneous display of:

- SHIP MET
- EXT EPOCH
- CAUSAL OFFSET

---

# 21. Final program verdict

The strongest outcome of the test sequence is that LOOM’s physics increasingly generates story *from its own constraints*.

The sequence:

mis-translation  
→ causal isolation  
→ deep-field reacquisition  
→ blind topology survey  
→ asymmetric/directional escape graph  
→ M31 recovery  
→ passive first-contact evidence  
→ politically dangerous archive  
→ secure physical custody  
→ uncertain institutional reception  

did not require arbitrary narrative rescue.

That is the design thesis working:

**physics creates engineering; engineering creates institutions; institutions create human stories.**

---

# 22. Open items generated by the test program

1. metric-drive engineering closure for the inherited courier
2. exact maneuver-node engineering
3. courier loading-band wording
4. exact Ceres orbital-port architecture/altitude
5. Juno GM for close operations
6. HUD acceleration-label standard
7. PLAN/ELEV and NOSE/VEL NAV promotion
8. blind topology spectroscopy specification
9. chronology anomaly research
10. A06 synthetic signal dataset
11. external detectability of Loom manipulation
12. engineered topology perturbation
13. alien-contact data-security / governance protocol
14. first-contact political consequences
15. ship-size/domain scaling
16. Pauli/Jung/consciousness relational hypothesis — future rabbit hole, not current rule
17. deterministic Solar-System economics/demography model
18. strategic-material geography / corporate concentration
19. metric energy/endurance closure
20. torch plasma/radiation thermal closure

---

# 23. Preserve for future play

- Walter carried the first-contact archive inside his chassis.
- “Fly casual” is now part of the historical Ceres arrival.
- The archive was intentionally not broadcast.
- Ceres authorities know the ship suffered an extraordinary Loom anomaly but do not automatically possess the M31 archive.
- PF-01/PF-02 destination-side fates remain unresolved unless later campaign evidence establishes them.
- Whether the M31 system detected the courier is unresolved.
- Whether the M31 technological network is one civilization, multiple successor cultures, machine infrastructure, or something else remains unresolved.
