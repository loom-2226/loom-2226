# Build 7 | Executable as-built atlas

**View the rendered diagrams: [ATLAS.md](ATLAS.md).** **Read the [assumptions and abstractions register](ABSTRACTIONS.md)** and **[exact Agent policy gates](DECISIONS.md)**.

**Pinned source authority:** [Build 7 at `66c641d25e641e0aff77940a8cadbf1653247113`](https://github.com/loom-2226/loom-2226/tree/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7). The diagrams are source-derived, not copied from [reference PR #372](https://github.com/loom-2226/loom-2226/pull/372). Scope is the **generated-world 2026–2035 annual campaign**, not the separate targeted qualification path.

## Navigation

The rendered atlas has ten views: world overview, data provenance, world/knowledge, Agent decisions, observations/epistemics, Agent consequences, economics/projects, annual time/persistence, and abstraction boundaries. [ATLAS.md](ATLAS.md) is the mobile-friendly visual entry point; individual `.mmd` files are editable sources.

## Evidence and exact entry points

| Topic | Source authority |
|---|---|
| Genesis: catalog installation, seeded hidden WORLD, kernel construction, persistence | [generated_campaign.py 659–675](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L659-L675) |
| Visible candidate derivation, 90-body/900-row checks | [opportunities.py 47–120](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/opportunities.py#L47-L120) |
| **PUB choice: eligible, unresolved, affordable, minimum modeled cost; SHA256 exact tie-break** | [exploration_choice.py 23–54](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/exploration_choice.py#L23-L54) |
| PUB policy, paid remote observation, belief update and publication | [generated_campaign.py 702–807](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L702-L807) |
| SPN-visible regional opportunities and annual candidates | [generated_campaign.py 808–849](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L808-L849) |
| Opening SPN prospecting, mobilization, project creation, commitment and disbursement | [generated_campaign.py 908–997](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L908-L997) |
| Annual conductor, all-project study loop, conditional annual investment | [generated_campaign.py 998–1154](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L998-L1154) |
| Decision snapshots, policy worker and persisted policy epoch | [runtime_flow.py 194–232](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/runtime_flow.py#L194-L232) |
| System transition, protected WORLD_SIM physical reads, accounting audit and persistence | [runtime_flow.py 233–375](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/runtime_flow.py#L233-L375) |
| Structural assumptions and economic scenario inputs | [Build 7 config](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/inputs/BUILD7_GENERATED_CAMPAIGN_V1.json), [prospecting economics](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/inputs/BUILD7_PROSPECTING_ECONOMICS_V1.json), [mission cost normalization](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/mission_costs.py) |

## Reading rules

**Agent vs system:** PUB and SPN make policy decisions; conductor, scheduler, kernel and World Authority perform other roles. FIN registration is not evidence of recurring independent FIN decisions.

**Truth vs knowledge:** Hidden generated material truth enters only authorized WORLD_SIM observations; Agents receive observations, publications and their own beliefs, not sealed world facts.

**Decision vs consequence:** Choosing an action is not executing it. Kernel transitions perform project creation, disbursement, study and review effects.

**Configured vs exercised:** Underlying kernel methods include markets, extraction, transport, settlement and distribution; the generated-world annual conductor does not establish those pathways as active.

**NO_ACTION vs WAIT:** A conductor summary can say NO_ACTION without an Agent having issued WAIT.

**Observation vs generalization:** One completed console campaign at this pinned commit had two lunar projects and 193 persisted epochs. That does not prove every eligible branch or independent replay validation.

## Review / replacement rule

This is a **source-grounded documentation revision**, not a completed independent exhaustive verification of every Mermaid edge or a qualification artifact. Every causal edge should be checked against its linked code before promotion from draft. Keep PR #372 until the replacement is accepted. Changes to Build 7 require re-pinning and reviewing affected relationships, not silently mixing revisions.
