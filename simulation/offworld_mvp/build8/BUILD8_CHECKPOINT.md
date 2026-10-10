# Build 8 multi-organization / 80-economy checkpoint

Status: active Build 8 development baseline, **not canon or qualification**. Do not regress to Build 7's three representative Agents (`PUB`, `FIN`, `SPN`) as the Build 8 population.

## Retained implementation

- `opening.py` admits 80 national 2026-2035 investment-capacity envelopes into a disposable Build 8 opening. Country investment is a bounded financing input, not an actor budget or free cash.
- `sponsor_executor_network_trial.py` represents 20 named public/private Sponsors and 16 executor roles, with overlapping organizations counted once. Awards remain pending physical plans; awards are not deliveries or earned executor revenue.
- `country_sponsor_allocation_trial.py` exercises bounded national-to-Sponsor allocation and conservation.
- `all_agents_country_trial.py` exercises all 80 economy envelopes and the existing 20-Sponsor/16-executor authored network. It is a trial of organization participation and account allocations, **not** evidence that 32 independent kernel Agents made decisions. Do not silently promote its roster, country preferences, or appetite to canonical world identity or policy.
- `all_agents_controls_trial.py` checks appetite extremes, equal allocation weights, competing commitments, and non-interference when a Sponsor is removed.

## Reproduced observations (2026-10-11, quantifactus)

With `PYTHONPATH=src:simulation/offworld_mvp/phase3b/kernel:.`:

- `python3 -m simulation.offworld_mvp.build8.all_agents_country_trial`: PASS and deterministic replay; 80 economies, 20 Sponsors, 16 executor roles, 32 unique organizations, 41 allocations, 57 economies without eligible Sponsors. Mobilized 25.10396510558080532339 and allocated 10.55502917702657340999999999 fictional capital units.
- `python3 -m simulation.offworld_mvp.build8.all_agents_controls_trial`: PASS; 0%/100% appetite, equal weights, competing commitment rejection without mutation, and unchanged allocations in 79 economies when Interlune is excluded.

These results validate the narrow experimental behavior only, not autonomous decision-making or a full-world epoch.

## Known gaps and next executable objective

The Build 8 opening currently inherits the three generic Build 7 Agents from `_build_kernel`; the network trial registers organization accounts and allocates money but does not make each named organization an independent Agent with information-bounded policy decisions. World Authority records actor references, snapshots, beliefs and decisions, but an exhaustive world-to-Offworld Agent population path has not been demonstrated. Preserve the 80-economy and multi-organization baseline while connecting actual existing Offworld Agent decisions to capital and project consequences. Do not introduce a CIVPROP dependency or another actor registry to achieve this.

Next: exercise one Build 8 epoch with the existing multi-organization economy and capability-limited Agent decisions, preserving identity, observation access, financial conservation, and replay. Stop and report any actual missing world/Agent authority rather than inventing actors, revenues, capabilities or physical deliveries.

This checkpoint does not authorize promotion to canon, qualification, or merging to main.
