# Build 7 executable atlas: as built

**Authority:** [Build 7 source at 66c641d25e641e0aff77940a8cadbf1653247113](https://github.com/loom-2226/loom-2226/tree/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7). Scope: **generated-world opening and 2026–2035 annual campaign**. Not a qualification, proposed design, or account of the separate targeted path. [PR #372](https://github.com/loom-2226/loom-2226/pull/372) is reference only, not source authority.

## Maps

- [World and knowledge](01_world_and_knowledge.mmd)
- [Agents and consequences](02_agents_and_consequences.mmd)
- [Time and persistence](03_time_and_persistence.mmd)

Solid arrows represent source-supported dependencies or consequences; dashed arrows denote context, orchestration, or registered capability **not necessarily exercised**. Arrows abbreviate call chains, not literal function-to-function calls.

## Source register

| Executable fact | Code authority |
|---|---|
| Genesis installs catalogs, generates seeded hidden world, attaches persistence | [generated_campaign.py 659–675](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L659-L675) |
| PUB visible mission choice, policy, paid remote observations, belief updates and publication to SPN | [generated_campaign.py 688–807](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L688-L807), [exploration_choice.py](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/exploration_choice.py), [opportunities.py](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/opportunities.py) |
| Opening 2026 SPN opportunity, capital mobilization, policy, project creation, commitment and disbursement | [generated_campaign.py 908–997](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L908-L997) |
| SPN-visible candidate generation and annual investment | [generated_campaign.py 816–907](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L816-L907) |
| Annual PUB choice, all-project study lifecycle, conditional SPN opportunity and subsequent project creation | [generated_campaign.py 998–1154](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/generated_campaign.py#L998-L1154) |
| Decision epochs build admitted snapshots and execute policies | [runtime_flow.py 194–232](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/runtime_flow.py#L194-L232) |
| System epochs execute kernel methods and audit accounting; World Authority wrapper persists epochs | [runtime_flow.py 233–375](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/runtime_flow.py#L233-L375) |
| Kernel method registry includes broader market, settlement, transport, financing and extraction operations | [runtime_flow.py 24–95](https://github.com/loom-2226/loom-2226/blob/66c641d25e641e0aff77940a8cadbf1653247113/simulation/offworld_mvp/build7/runtime_flow.py#L24-L95) |

## Semantic boundaries

1. **Agent ≠ system.** PUB and SPN choose; conductor, policy runner, kernel and World Authority orchestrate/execute. FIN is registered, but an independent recurring FIN underwriting choice is not evidenced in this annual path.
2. **Hidden truth ≠ Agent information.** Sealed generated truth affects WORLD_SIM observations, not directly Agent choices. PUB publication and SPN belief update are distinct steps.
3. **Decision ≠ consequence.** Authorization and actual spending, observation, project creation and review are separate epochs.
4. **NO_ACTION ≠ Agent WAIT.** An annual summary can report no action without a policy decision in that branch.
5. **Financing is coarse.** USA investment is a proxy mapped to model-currency F/X; it is not spendable national cash or a calibrated valuation. Accessibility is preliminary screening, not flight qualification; the technology timeline is read-only context.
6. **Implemented ≠ exercised.** The underlying kernel exposes extraction, trade/markets, settlement and transport capabilities, but this atlas does not claim the generated-world annual campaign executes them.

**Observed example, not universal proof:** campaign seed `B7-TEXT-CONSOLE-20261010-165713-247930` at this commit completed through 2035 with two lunar projects and 193 persisted epochs. Independent replay validation was not run in that test.

**Maintenance:** Pin each atlas revision to a Build 7 source commit. Verify affected arrows against code before updating; do not silently mix revisions.
