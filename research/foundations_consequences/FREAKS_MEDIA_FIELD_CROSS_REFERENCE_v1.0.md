# LOOM 2226 — Freaks Media / Field Roster Cross-Reference v1.0

**Status:** ACTIVE RESEARCH CROSS-REFERENCE — NON-CANON — NON-RUNTIME  
**Date:** 7 September 2026

## Non-endorsement

George Knapp, Jeremy Corbell, Greg Newkirk and Dana Newkirk are not represented as endorsing LOOM, knowing about LOOM, reviewing LOOM, or agreeing with any LOOM interpretation. This document maps publicly available work to LOOM research/design questions. Any extension is LOOM's responsibility.

## Why these four are being added

They add two methodological modes that the current Freaks roster underrepresented:

1. **journalistic / documentary provenance and public-release ecology** — Knapp + Corbell;
2. **participatory / longitudinal high-strangeness fieldwork and meaning-making** — Greg + Dana Newkirk.

Neither mode is scientific evidence for exotic ontology. Both are directly useful to LOOM's evidence architecture.

---

# 1. George Knapp — investigative provenance / long-duration journalist seat

## Public body of work sampled

- KLAS-TV reporting on Bob Lazar / Area 51 beginning in 1989; KLAS's archived 1989 interview remains a primary provenance node.
- **Hunt for the Skinwalker** (2005), with Colm Kelleher.
- **Skinwalkers at the Pentagon** (2021), with James Lacatski and Colm Kelleher.
- long-duration reporting on Area 51, Skinwalker Ranch, UAP and related institutional claims.
- current co-host of **Weaponized** with Jeremy Corbell.

## Source basis

- Weaponized official bio: https://www.weaponizedpodcast.com/about
- KLAS 1989 archival interview: https://www.youtube.com/watch?v=uLPFzdPvEvM
- Simon & Schuster, *Hunt for the Skinwalker*: https://www.simonandschuster.com/books/Hunt-for-the-Skinwalker/Colm-A-Kelleher/9781416505211
- WorldCat, *Skinwalkers at the Pentagon*: https://search.worldcat.org/title/1280415885

## Current LOOM contribution

Knapp is useful less as an ontology referee than as a **provenance-chain specialist by practice**. His career exposes the full lifecycle of a high-impact anomalous claim:

`source -> journalist -> corroboration attempts -> broadcast/publication -> institutional response -> later retellings -> documentary reuse -> community prior`

The Lazar case is especially valuable because Knapp is not merely commenting decades later; he is part of the historical source chain.

## Potential future construction

- P1 `source_chain` / `intermediary_chain` schema;
- journalist/source-protection role objects;
- claim chronology with contemporaneous versus retrospective assertions;
- classified-program / unverifiable-source handling;
- contradiction and corroboration ledgers;
- public-release events as first-class epistemic events;
- F5 institutions: investigative media, secrecy, whistleblower ecosystems, classified-program rumor markets;
- P5 historical-case reconstruction.

## Boundary

A journalist's access to a witness or source does not authenticate the witness's interpretation. Longevity of a claim is not independent replication.

---

# 2. Jeremy Corbell — documentary release / media-artifact lifecycle seat

## Public body of work sampled

- documentary work including **Bob Lazar: Area 51 & Flying Saucers** and other UAP / anomalous-subject films;
- current co-host of **Weaponized** with George Knapp;
- acquisition and public release of UAP-related imagery/video and associated claims;
- 2021 release of USS Omaha footage that the Pentagon later confirmed was recorded by Navy personnel and included in UAPTF examinations.

## Source basis

- Weaponized official bio and show description: https://www.weaponizedpodcast.com/about
- Pentagon-confirmation reporting on USS Omaha footage: https://thedebrief.org/pentagon-confirms-leaked-video-showing-transmedium-ufo-is-authentic/

## Current LOOM contribution

Corbell adds a distinct layer that LOOM had not modeled explicitly enough: **an evidence artifact can have authentic provenance while the interpretation attached to it remains uncertain**.

For the USS Omaha example, Pentagon confirmation supports the proposition that the footage was taken by Navy personnel and examined by the UAP Task Force. It does not, by itself, establish the nature, capability or origin of the object. That distinction is almost a perfect P1 teaching case.

Corbell also makes the transformation layer visible:

`raw/source artifact -> selected excerpt -> caption/context -> documentary/podcast framing -> public inference -> derivative retellings`

## Potential future construction

- `artifact_authenticity` separated from `interpretation_confidence`;
- edit/crop/context provenance;
- release-timestamp and pre/post-publication contamination tracking;
- audience-amplification / belief propagation;
- evidence-package UI for player investigations;
- source-redaction and protected-source mechanics;
- F5 disclosure-media institutions.

## Boundary

Confirmed origin of a photo/video is not confirmation of the strongest interpretation applied to the depicted object. Documentary framing is itself an epistemic transformation and must be recorded.

---

# 3. Greg Newkirk — participatory high-strangeness / cross-category field seat

## Public body of work sampled

- co-founder of Planet Weird and the Traveling Museum of the Paranormal & Occult;
- co-creator / executive producer / investigator in **Hellier**;
- producer/investigator in **The Unbinding**;
- long-running field work across paranormal, cryptozoological, UFO and occult cases;
- explicit interest in recurring archetypal myth, folklore, synchronicity and initiatory experience.

## Source basis

- Greg Newkirk official profile: https://gregorynewkirk.com/
- Planet Weird / Hellier background: https://www.planetweird.tv/about
- Hellier project page: https://gregorynewkirk.com/projects/hellier-seasons-1-2/
- The Unbinding project page: https://gregorynewkirk.com/projects/the-unbinding/
- academic discussion of Hellier's synchronicity/meaning-making methodology: https://www.supernaturalstudies.com/previous-journal-issues/vol-11-issue-1/gitzen

## Current LOOM contribution

Greg's strongest contribution is not validation of paranormal claims. It is a **stress case for participant-observer research** in which investigators follow cross-category leads, meaningful coincidences and recursive feedback from their own publication.

Hellier is unusually useful to LOOM precisely because the investigators acknowledge that the documentary itself became part of the case: publication generated new reports and leads, which then changed the subsequent investigation.

That is a first-class epistemic contamination / feedback problem.

## Potential future construction

- `investigator_participation` and `reflexivity` fields in P1;
- pre-observation hypothesis / post-hoc connection distinction;
- synchronicity and motif registry with explicit multiple-comparison / selection controls;
- cross-category case-link graphs that preserve *possible connection* separately from *common cause*;
- public-feedback loops where media publication changes incoming witness reports;
- F4/F5 Patternist and anomalous-investigation cultures;
- player-facing rabbit-hole mechanics where investigator attention changes the evidence environment without implying physics does.

## Boundary

Meaningful coincidence to an investigator is phenomenological data about the investigation; it is not automatically evidence of external acausal coordination. Hellier is therefore as valuable as a **selection/reflexivity warning** as it is as a high-strangeness corpus.

---

# 4. Dana Newkirk — artifact curation / ritual-context / human-meaning field seat

## Public body of work sampled

- co-founder of Planet Weird with Greg Newkirk;
- co-founder and head curator of the Traveling Museum of the Paranormal & Occult;
- executive producer / investigator in **Hellier**;
- investigator / executive producer in **The Unbinding**;
- long-running paranormal fieldwork plus practical occult / ritual traditions explicitly carried into interpretation.

## Source basis

- Planet Weird official cast/crew profile: https://www.planetweird.tv/about
- Planet Weird home/project index: https://www.planetweird.tv/
- The Unbinding official page: https://www.planetweird.tv/the-unbinding
- interview on the long-duration Crone investigation: https://bloody-disgusting.com/exclusives/3778251/greg-and-dana-newkirk-discuss-the-unbinding-and-the-unnerving-case-of-the-crone-interview/

## Current LOOM contribution

Dana adds two underrepresented dimensions:

1. **object provenance / curation** — anomalous claims can attach to physical objects with ownership, custody, story and expectation histories;
2. **ritual / interpretive context** — the investigator's worldview and intervention can be part of the causal *claim*, even when it is not accepted as the actual physical cause.

For LOOM this is valuable because a proper anomaly database must store both the physical object and the claims, rituals, handlers, transfers and expectations surrounding it.

## Potential future construction

- anomalous-object custody and ownership graph;
- object story / prior-exposure / expectation metadata;
- intervention/ritual events recorded without presuming efficacy;
- handler-specific report histories;
- human-object attachment / salience models;
- museum/archive institutions and contested-object mechanics;
- richer xeno-artifact interpretation sociology while preserving the xeno↔paranormal firewall.

## Boundary

Occult practice, ritual interpretation or a claimed haunted-object effect is not evidence for a physical mechanism merely because it is documented longitudinally.

---

# 5. Re-cross-reference against the other squads

## Squad A — Adults With Red Pens

### What changed
No new physics evidence was added.

The four additions instead sharpen what Red-Pen review must demand from anomaly work:

- provenance-chain integrity;
- separation of artifact authenticity from interpretation;
- pre/post-publication contamination;
- investigator participation and reflexivity;
- preregistration before motif/synchronicity mining;
- explicit multiple-testing and selection accounting;
- chain-of-custody for physical and media artifacts.

### Highest A-side connections
- **French/Hyman/Truzzi-style controls** become more important inside P1/P4.
- **Loeb/Strand instrument-first approaches** provide a useful contrast to documentary/participant-observer streams.
- formal A workstreams S1/S3/S4/S5 receive **no evidentiary boost** from these additions.

## Squad B — Respectably Unsupervised

### What changed
Greg/Dana materially deepen the *phenomenological ancestry* of questions already associated with Pauli/Jung, James, Whitehead, Bohm and Atmanspacher:

- meaningful coincidence;
- participant/observer boundaries;
- mind/world interpretation;
- event versus meaning;
- cross-category pattern construction.

This is **convergence of questions**, not independent evidence for psychophysical causation.

Knapp/Corbell also strengthen F5/social-epistemic questions about secrecy, institutional authority, source access and public belief formation, but they do not add foundational-physics content.

## Squad C — Freaks With Clipboards

### What changed
The squad now spans a more complete anomaly-information lifecycle:

`witness / event`
→ `field investigator`
→ `instrument / artifact`
→ `journalist / source intermediary`
→ `documentary / edited package`
→ `public release`
→ `audience feedback / new witnesses`
→ `archive / historical case`
→ `skeptical reanalysis`

This substantially improves P1 and P5 and exposes the contamination pathways that P4 must control.

---

# 6. Convergence rerun

## Independence clustering

These additions SHALL NOT count as four independent convergence votes.

### Cluster C-MEDIA-PROV
**George Knapp + Jeremy Corbell**

Shared mode: source access, investigative/documentary release, public UAP information ecology.

### Cluster C-PARTICIPANT-HS
**Greg Newkirk + Dana Newkirk**

Shared mode: longitudinal participatory high-strangeness investigation, object/case curation, synchronicity/meaning and publication feedback.

Within each cluster apply existing diminishing-return rules.

## Portfolio effects

### P1 — Anomaly Registry & Evidence Taxonomy
**Impact: MATERIAL INCREASE.**

New mandatory schema concepts:
- source/intermediary chain;
- raw versus edited artifact;
- artifact authenticity versus interpretation confidence;
- publication/release events;
- pre/post-publication witness contamination;
- investigator participation/reflexivity;
- object custody / handler chain;
- intervention/ritual event as a reported action, not assumed mechanism;
- audience-feedback / new-lead generation.

### P4 — Cross-Domain Correlation
**Impact: CONVERGENCE DEPTH INCREASE; STILL BLOCKED.**

Hellier/Newkirk material increases the importance of selection, synchronicity mining, investigator participation and recursive feedback. This makes the methodological gate stricter, not easier.

### P5 — Historical Case Reanalysis / GHOST
**Impact: MATERIAL INCREASE.**

Knapp/Lazar supplies an unusually rich longitudinal source/intermediary case. Corbell supplies later documentary reactivation. This allows LOOM to model how a claim changes as it moves through decades and media forms.

### F5 — Institutions, Regulation & Radical Science
**Impact: MATERIAL INCREASE.**

Media, source protection, classified claims, disclosure movements, paranormal museums, self-funded documentary communities and feedback between investigators/audiences become explicit institutional design ancestry.

### F3 / F4 / F6
**Impact: MODEST INCREASE.**

Useful for interpretation sociology, ritual/meaning systems and operational weirdness. No xeno or physics shortcut is created.

### S1 / S2 / S3 / S4 / S5
**Impact: NO DIRECT EVIDENTIARY INCREASE.**

At most these four generate questions, analogies or methodological cautions. They do not alter scientific qualification scores or fictional-postulate calibration.

---

# 7. Net conclusion

The additions improve LOOM because they fill a missing layer between **an event** and **what a civilization eventually believes happened**.

Before this addition, the Freaks roster was strongest at classification, laboratory analysis, psychology, field instrumentation, anomalous-experience research and cultural history.

After this addition, it also explicitly covers:

- investigative source chains;
- protected/confidential sources;
- documentary framing;
- media-artifact release;
- authenticity-versus-interpretation separation;
- participant-observer research;
- publication feedback;
- anomalous-object curation;
- ritual/expectation context;
- decades-long myth/provenance evolution.

That is a real architectural improvement for the Rabbit Hole and P1 evidence model.

It is **not** an increase in the probability that UFOs, ghosts, cryptids, synchronicities or any other anomalous ontology are real.

> **The new members make LOOM better at tracking how weird claims become evidence, stories, institutions and priors. They do not make the weird claims truer.**