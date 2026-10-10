# Build 7 | Rendered as-built atlas

**Source authority:** pinned Build 7 commit `66c641d25e641e0aff77940a8cadbf1653247113`. Generated-world annual pathway, 2026–2035. Source register: [README](README.md). [Exact Agent policy gates](DECISIONS.md). Placeholder and abstraction register: [ABSTRACTIONS](ABSTRACTIONS.md). These diagrams render directly on GitHub in Markdown.

**Notation:** solid links describe source-supported relationships; dashed links are contextual, conditional, or registered capabilities and must not be treated as exercised decisions. A diagram edge may abbreviate a documented call chain.

## World Overview

```mermaid
flowchart TD
 subgraph Inputs
 CAT["90-body catalog"] --> CAND["Public mission candidates"]
 SCREEN["Annual accessibility screen"] --> CAND
 COST["Provisional mission cost"] --> CHOOSE["PUB least-cost eligible choice"]
 CAND --> CHOOSE
 ECON["USA investment proxy + authored economics"] --> MOB["Capital mobilization"]
 end
 subgraph World
 SEED["World seed + priors"] --> GEN["Generated world"]
 GEN --> TRUTH["Sealed body and region material truth"]
 end
 subgraph Agents
 CHOOSE --> PUB{"PUB authorization"}
 PUB --> REM["Paid remote observation"]
 TRUTH -->|"WORLD_SIM only"| REM
 REM --> BEL["PUB belief update"]
 BEL --> PUBLISH{"PUB publication policy"}
 PUBLISH --> SPNBEL["SPN independent beliefs"]
 SPNBEL --> OPP["Region opportunities"]
 MOB --> SPN{"SPN financing and study choices"}
 OPP --> SPN
 end
 subgraph Consequences
 SPN --> PROJECT["Project / study / review"]
 TRUTH -->|"WORLD_SIM only"| PROJECT
 PROJECT --> STATE["Persistent world and causal trace"]
 STATE --> YEAR["Annual conductor"]
 YEAR --> CHOOSE
 YEAR --> SPN
 end
 FIN["FIN registered; no independent annual decision evidenced"] -.-> SPN
```

## Data Provenance

```mermaid
flowchart TD
 CAT["BUILD7_SOLAR_BODY_CATALOG_V1"] --> LOAD["Visible-input hash and shape checks"]
 REF["BUILD7_SOLAR_ACCESSIBILITY_REFERENCE_V1"] --> LOAD
 SCR["BUILD7_SOLAR_ACCESSIBILITY_SCREEN_V1: 900 rows"] --> LOAD
 LOAD --> CAND["derive_mission_candidates"]
 COST["Provisional mission-cost CSV"] --> COSTL["MissionCostLookup: missing / NO_TRAJECTORY unavailable"]
 COSTL --> PUB["PUB cost-minimizing eligible choice"]
 CAND --> PUB
 CONFIG["BUILD7_GENERATED_CAMPAIGN_V1: policy seed + structural parameters"] --> K["Kernel build and run identity"]
 EARTH["BUILD7_EARTH_USA_2026_2045_V1"] --> K
 TIMELINE["BUILD7_TIMELINE_SNAPSHOT_V1"] -.-> K
 ECON["BUILD7_PROSPECTING_ECONOMICS_V1"] --> K
 SEED["World seed"] --> GEN["generate_solar_system"]
 CAT --> GEN
 GEN --> HIDDEN["Sealed material truth"]
 HIDDEN -->|"authorized WORLD_SIM"| OBS["Remote or regional observation"]
 OBS --> PUBBEL["PUB or SPN belief update"]
 PUBBEL --> WA["World Authority persisted epochs"]
 K --> WA
```

## World And Knowledge

```mermaid
flowchart TD
  I["Authored catalog, accessibility, Earth, economics, timeline"] --> G["Build 7 genesis and visible mission candidates"]
  SEED["World seed and material priors"] --> W["Sealed generated world truth"]
  G --> PUB["PUB candidates, capability, affordability"]
  PUB --> CH{"PUB remote choice and policy authorization"}
  CH --> OBS["Paid remote observation"]
  W -->|"WORLD_SIM only"| OBS
  OBS --> B["PUB belief update"]
  B --> P{"PUB publication policy"}
  P --> INFO["Published information"]
  INFO --> SB["SPN information and independent beliefs"]
  SB --> OPP["Region prospecting opportunities"]
  I --> OPP
  T["Timeline: read-only context"] -.-> G
```

## Agent Decisions

```mermaid
flowchart TD
 CAND["Visible SCREENED, capable, preliminary-comparable candidates"] --> UNRES["Exclude characterized bodies"]
 UNRES --> AFF["Require finite, affordable mission cost"]
 AFF --> MIN["Choose minimum modeled cost; SHA256 breaks exact ties"]
 MIN --> PUBPOL{"PUB explorer policy"}
 PUBPOL -->|"AUTHORIZE"| REM["Paid remote observation"]
 PUBPOL -->|"not authorized"| WAIT["No remote transition"]
 REM --> PUBBEL["Update PUB belief per material family"]
 PUBBEL --> PUBPUB{"PUB publication policy per signal"}
 PUBPUB -->|"PUBLISH"| SPNBEL["SPN published information and independent belief"]
 SPNBEL --> OPPS["Regional opportunities from observations, beliefs and priors"]
 OPPS --> OPEN{"SPN prospecting policy"}
 OPEN -->|"INITIATE_PROJECT"| FUND["Create project, commitment and disbursement"]
 FUND --> PORT{"SPN portfolio policy"}
 PORT -->|"AUTHORIZE"| STUDY["Authorize, start and spend study"]
 STUDY --> RESULT["Due: region observation, belief update, completion and admission"]
 RESULT --> REVIEW{"SPN study review: ADVANCE / DEFER / ABANDON"}
 REVIEW --> STATE["Persistent project state"]
 STATE --> ANNUAL{"SPN annual opportunity policy after prior review"}
 ANNUAL -->|"CONSIDER_PROSPECTING"| RECHECK["Re-derive opportunity, check drift"]
 RECHECK --> REINV{"SPN prospecting policy"}
 REINV -->|"INITIATE_PROJECT"| FUND
 ANNUAL -->|"not financed"| HOLD["Retain state"]
 FIN["FIN registered, no independent annual decision evidenced"] -.-> HOLD
```

## Agents And Consequences

```mermaid
flowchart TD
  PUB{"PUB remote authorization"} --> REM["System: paid observation, belief, publication"]
  REM --> SPN{"SPN prospecting policy"}
  EARTH["USA investment proxy and authored economics"] --> MOB["System: mobilize country capital"]
  MOB --> SPN
  SPN -->|"INITIATE_PROJECT"| CREATE["System: create project, commitment, disbursement"]
  CREATE --> PROPOSED["Proposed study"]
  PROPOSED --> PORT{"SPN portfolio authorization"}
  PORT -->|"AUTHORIZE"| ACTIVE["System: authorize, start, spend"]
  ACTIVE --> DUE["Due: region observation and SPN belief update"]
  DUE --> RESULT["System: complete and admit study result"]
  RESULT --> REVIEW{"SPN review: advance / defer / abandon"}
  REVIEW --> STATE["Persist study and project state"]
  STATE -->|"review existed at year opening"| ANNUAL{"SPN annual opportunity policy"}
  ANNUAL -->|"consider prospecting"| SPN
  FIN["FIN capability registered, recurring decision not evidenced"] -.-> STATE
```

## Observations And Epistemics

```mermaid
flowchart TD
 SEED["World seed and material priors"] --> GEN["Generated hidden world"]
 GEN --> BODY["Sealed body material presence"]
 GEN --> REGION["Sealed regional material truth"]
 PUBREQ["PUB mission selected and authorized"] --> REM["explore_paid REMOTE"]
 BODY -->|"trusted read after authorization"| REM
 REM --> SIGNAL["Four noisy material-family signals"]
 SIGNAL --> PUBBEL["PUB belief update: detection and false-positive assumptions"]
 PUBBEL --> PUBPUB{"PUB publication policy per observation"}
 PUBPUB -->|"PUBLISH"| INFO["Published information"]
 INFO --> SPNBEL["SPN independently updated beliefs"]
 SPNBEL --> OPP["Sponsor visible opportunity"]
 OPP --> STUDY["Authorized and paid regional study"]
 REGION -->|"trusted read at transition"| STUDY
 STUDY --> ROBS["observe_region_study"]
 ROBS --> CLASS["Classify regional observation"]
 ROBS --> SPNREG["SPN belief update, fixed .80/.20"]
 CLASS --> RESULT["Complete and admit study result"]
 SPNREG --> REVIEW{"SPN review"}
 RESULT --> REVIEW
 BODY -.->|"not a direct Agent input"| PUBREQ
 REGION -.->|"not a direct Agent input"| OPP
```

## Time And Persistence

```mermaid
flowchart TD
  GEN["2026: generated world and opening epoch"] --> OPEN["Opening PUB choice and SPN prospecting"]
  OPEN --> YEAR["Annual loop: 2027–2035"]
  YEAR --> PUB["PUB remote choice each year"]
  PUB --> PROJECTS["Iterate all created projects"]
  PROJECTS --> STATE{"Study activity state"}
  STATE -->|"PROPOSED"| PORT["SPN portfolio policy, authorized actions"]
  STATE -->|"ACTIVE and due"| COMPLETE["Observe, update belief, complete, admit"]
  STATE -->|"COMPLETED and unreviewed"| REVIEW["SPN study review and execution"]
  STATE -->|"otherwise"| NONE["No activity in this branch"]
  PORT --> ELIG{"Study review existed at year's opening?"}
  COMPLETE --> ELIG
  REVIEW --> ELIG
  NONE --> ELIG
  ELIG -->|"yes and opening project exists"| OPP["SPN annual opportunity policy; optional investment"]
  ELIG -->|"no"| NEXT["Next year or finish"]
  OPP --> NEXT
  NEXT -->|"next year"| YEAR
  POLICY["Policy epoch: snapshot, worker, decision"] --> WA["World Authority persisted epoch"]
  SYSTEM["System epoch: transition, accounting audit"] --> WA
  WA --> TRACE["Persisted decisions, state, causal records and replay provenance"]
  YEAR -.-> POLICY
  PROJECTS -.-> SYSTEM
```

## Economics And Projects

```mermaid
flowchart TD
 E["USA investment projection: capacity proxy"] --> NORM["Normalize by 1e9 proxy units per model currency"]
 O["Visible commercial opportunity and strategic pressure"] --> GATE["Mobilization activation: m = 0.001 or 0"]
 NORM --> MOB["Mobilize country capital"]
 GATE --> MOB
 MOB --> F["Available F, exposure X, returns R, pressure S"]
 P["Authored region required capital 2, information value 3"] --> SPN{"SPN prospecting policy"}
 F --> SPN
 OBS["SPN visible evidence and beliefs"] --> SPN
 SPN -->|"INITIATE_PROJECT"| CREATE["Create project and cash account"]
 CREATE --> COMMIT["Add commitment"]
 COMMIT --> DISB["Disburse country capital"]
 DISB --> PROJECT["Project cash and financial exposure"]
 PROJECT --> PORT{"SPN portfolio policy"}
 PORT -->|"AUTHORIZE"| SPEND["Start and spend regional study"]
 SPEND --> STUDY["Region result and maturity"]
 STUDY --> REVIEW{"SPN study review"}
 REVIEW --> STATUS["Project status"]
 STATUS --> ANNUAL{"Annual opportunity evaluation"}
 F --> ANNUAL
 ANNUAL -->|"financing unavailable"| HOLD["No new project; retain existing state"]
 FIN["FIN registered; no independent annual underwriting evidenced"] -.-> F
```

## Time And Persistence

```mermaid
flowchart TD
 GEN["2026: world genesis, kernel, opening epoch"] --> OPEN["PUB remote and SPN opening prospecting"]
 OPEN --> Y["Annual loop 2027–2035"]
 Y --> EARTH["Record Earth reference year"]
 EARTH --> PUB["PUB remote choice"]
 PUB --> FLAG["Snapshot: has any study review already occurred?"]
 FLAG --> EACH["For each created project, sorted"]
 EACH --> INIT{"Activity initialized?"}
 INIT -->|"no"| MAKE["Initialize regional study"]
 INIT -->|"yes"| STATUS{"Study status"}
 MAKE --> STATUS
 STATUS -->|"PROPOSED"| PORT["SPN portfolio policy and authorized actions"]
 STATUS -->|"ACTIVE and due"| COMPLETE["Observe region, update belief, complete and admit"]
 STATUS -->|"COMPLETED, unreviewed"| REVIEW["SPN review and execute"]
 STATUS -->|"other"| NONE["No activity action"]
 PORT --> ALT{"Prior review existed AND opening project exists?"}
 COMPLETE --> ALT
 REVIEW --> ALT
 NONE --> ALT
 ALT -->|"yes"| OPP["SPN annual opportunity, optional investment"]
 ALT -->|"no"| NEXT["Next year or finish"]
 OPP --> NEXT
 NEXT -->|"year remains"| Y
 POLICY["policy_epoch: admitted facts, snapshot, worker and decision"] --> PERSIST["execute_persisted_epoch"]
 SYSTEM["system_epoch: kernel transition and accounting audit"] --> PERSIST
 PERSIST --> DB["World Authority epoch, artifacts and causal records"]
 DB --> REPLAY["Run identity and replay provenance"]
 Y -.-> POLICY
 EACH -.-> SYSTEM
```

## Abstraction Boundaries

```mermaid
flowchart LR
 subgraph Physical
 A["Preliminary Lambert screen: not a qualified trajectory"]
 B["Provisional mission costs: modeled affordability"]
 C["Fixed 2026 recovery capability: uncalibrated"]
 D["Generated material priors: fictional realization"]
 E["Noisy four-family sensing: authored likelihoods"]
 F["Ten neutral regions per body"]
 end
 subgraph Economic
 G["USA investment: proxy, not spendable cash"]
 H["1e9 normalization and 0.001 mobilization cap"]
 I["Prospecting capital 2, information value 3"]
 end
 A --> PUB["PUB eligible mission selection"]
 B --> PUB
 C -.-> STUDY["Region study / maturity"]
 D --> OBS["Observations and beliefs"]
 E --> OBS
 F --> STUDY
 G --> SPN["SPN financing decisions"]
 H --> SPN
 I --> SPN
 OBS --> SPN
```
