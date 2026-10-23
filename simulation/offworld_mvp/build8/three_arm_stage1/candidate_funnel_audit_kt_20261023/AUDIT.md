# All-body candidate funnel: PR #427 existing-evidence audit

Read-only analysis of `sponsor_refill_sweep_kt_20261023/share_0_price_x1_sales_4_report.json`, `general_project_rule_kt_20261022/price_provenance_audit.json`, and source code. **No simulation was run.**

## 1. Funnel by body

| Stage | Distinct bodies |
|---|---:|
| Studied at least once (positive A1 review observed) | 90 |
| Positive A1 review | 90 |
| Supported 2026 rendezvous quote | 66 |
| Became quote-eligible project candidate | 66 |
| Started project | 42 |

The report exposes annual positive-review counts, not individual A1 review records. The 90 positive A1 review events (51, 20, 12, 4, 2, 1 from 2037–2042) coincide with exactly 90 body-specific first candidate/unpriced records. This supports 90 distinct positive bodies; it does not establish the number of negative/repeat studies.

| Terminal stage | Bodies |
|---|---:|
| UNPRICED | 24 |
| QUOTED_CANDIDATE_NOT_STARTED | 24 |
| STARTED | 42 |

**UNPRICED (24)**
ARIEL, CALLISTO, DACTYL, DIONE, ENCELADUS, EUROPA, GANYMEDE, HYPERION, IAPETUS, IO, MIMAS, MIRANDA, MOON, NEREID, OBERON, PHOEBE, PROTEUS, RHEA, SELAM, TETHYS, TITAN, TITANIA, TRITON, UMBRIEL.

**QUOTED_CANDIDATE_NOT_STARTED (24)**
ARROKOTH, ATLAS3I, BORISOV, CHARON, CHIRON, COMET_HALLEY, ERIS, GONGGONG, HAUMEA, HYDRA, IXION, KERBEROS, MAKEMAKE, MS4, NIX, ORCUS, OUMUAMUA, PLUTO, QUAOAR, SALACIA, SEDNA, STYX, SWIFTTUTTLE, VARUNA.

**STARTED (42)**
AMUN, APOPHIS, ASTEROID_6178, BENNU, BORRELLY, BRAILLE, CERES, COMET_67P, DAVIDA, DEIMOS, DIDYMOS, DINKINESH, DONALDJOHANSON, EROS, EURYBATES, GASPRA, HARTLEY2, HYGIEA, IDA, INTERAMNIA, ITOKAWA, JUNO, KLEOPATRA, LEUCUS, LUTETIA, MARS, MATHILDE, MERCURY, ORUS, PALLAS, PATROCLUS, PHOBOS, POLYMELE, PSYCHE, RYUGU, STEINS, TEMPEL1, THEMIS, TOUTATIS, VENUS, VESTA, WILD2.

## 2. 24 bodies without 2026 rendezvous quotes

The price provenance audit gives underlying reasons. The sweep report itself collapses them into a generic no-supported-quote message.

| Source reason | Count | Bodies |
|---|---:|---|
| `NO_59_BODY_TABLE_QUOTE` | 1 | HYPERION |
| `PARENT_GM_MISSING` | 2 | DACTYL, SELAM |
| `PARENT_NO_FLYBY_QUOTE` | 21 | ARIEL, CALLISTO, DIONE, ENCELADUS, EUROPA, GANYMEDE, IAPETUS, IO, MIMAS, MIRANDA, MOON, NEREID, OBERON, PHOEBE, PROTEUS, RHEA, TETHYS, TITAN, TITANIA, TRITON, UMBRIEL |

The source labels `PARENT_GM_MISSING` (2) as missing gravitational parameter; `NO_59_BODY_TABLE_QUOTE` (1) as absent saved price-table coverage; `PARENT_NO_FLYBY_QUOTE` (21) as missing parent flyby quote. The last is **not** proven to be a missing state table. The source audit does not separately assign a `NO_STATE_TABLE` reason to any of the 24.

## 3. Who studies what, when, how often?

`route1_all_body_campaign_pr3b.py:60-70, 100-112` loads all 90 eligible solid bodies and the sponsor roster/order. `:115-128` gives a sponsor its previously claimed A2 body first, then the first unclaimed/uncompleted A1 body in sorted body order. `:245-268` cycles through all 20 sponsors repeatedly in the same annual callback; each sponsor can win one funded stage per round. There is no artificial stages-per-sponsor/year limit. `route1_body_campaign.py:218-240, 280-293` charges the selected sponsor for an executor service, creates the receipt and records its body claim.

`route1_all_body_campaign_pr3b.py:27-38, 130-160, 162-216` permits A1 retries after `INSUFFICIENT` or `NO_RESULT` review, from the next annual decision. Each paid retry has a numbered deterministic draw; the A1 retry limit is `None`. `:115-128` prevents duplicate A1 study within a year. An advancing positive A1 body remains claimed and is not restudied as A1; A2 can follow.

Positive A1 review events in the existing report: **2037: 51; 2038: 20; 2039: 12; 2040: 4; 2041: 2; 2042: 1; after 2042: 0.** The last positive does **not** mean the annual study callback stops: annual policy callbacks persist to 2226. With all 90 bodies positively reviewed by 2042, no unclaimed/reopenable A1 body remains to generate another positive A1 result. `route1_all_body_campaign_pr3b.py:115-128, 209-216, 245-268`; `sponsor_refill_v3_kt_20261023/run_multi_project.py:160-183, 267-288`.

`box3_d1_repeat_attempts.py:73-128` independently demonstrates numbered paid attempts with a belief-based expected-net hurdle and budget check. It is **not wired** into this campaign. Merely wiring it in would not guarantee studies after 2042: it operates on a separate synthetic region/material/project and would require an actual eligible sponsor decision to repeat a study, as well as campaign integration. PR3B already supports retries of inconclusive A1 studies; it does not automatically re-study positive bodies.

## 4. Why one project per body?

`route1_body_campaign.py:290-293` records an A1 claim by **body**, and `route1_all_body_campaign_pr3b.py:115-128` allows only one active claimant for that body. A2 follows the existing claimant. `sponsor_refill_v3_kt_20261023/run_multi_project.py:160-166` suppresses a new candidate for an already-started `(body,sponsor)` pair; `:271-288` retains deferred candidates by that pair and removes them on start. `:128-132` creates a project ID from body index, body, and sponsor.

Therefore **one project per body is an emergent consequence of the single-claim A1 study pipeline in this scenario**, not a global kernel invariant forbidding multiple projects on a body. The portfolio-level duplicate check is per `(body,sponsor)`, not body alone. Allowing multiple regions/projects per body would require a distinct candidate/claim model; the current template does not provide one.

## Interpretation

The 42 starts are not the total number of candidate bodies. **66 bodies became candidates, 24 of those never started**, and 24 more positive-study bodies lack a supported 2026 rendezvous quote. More treasury refill cannot create additional A1 study outcomes or missing price quotes.
