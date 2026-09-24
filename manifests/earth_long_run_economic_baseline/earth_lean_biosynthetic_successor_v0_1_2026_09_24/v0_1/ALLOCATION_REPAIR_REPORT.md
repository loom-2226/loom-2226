# Geographic allocation repair

## Formula

For each country or country-sector node, compute normalized shares:

`a_i = absolute enabling capacity_i / total absolute enabling capacity`

`q_i = capacity intensity_i / total capacity intensity`

The unnormalized support is:

`w_i = a_i^0.75 × q_i^0.25`

and final weights are `w_i / Σw`. Synthetic capacity uses compute-enabling
capital and the compute/energy intensity signal. Machine capacity uses machinery
plus transport-equipment capital and its biological-worker intensity.

The existing v0 support bound supplies a generic absorption rule. A country or
sector cannot receive more than twice the contemporaneous global synthetic-person
or machine-task ratio through allocation. Excess is redistributed by the same
normalized weights. This preserves global stock/capacity and contains no country
identifier, political score, desired rank, or fitted endpoint.

## Selected-case concentration

| Metric | v0 synthetic | v0.1 synthetic | v0 automation | v0.1 automation |
|---|---:|---:|---:|---:|
| Top country share | 37.28% | 36.51% | 38.43% | 26.93% |
| Top-five share | 80.90% | 72.94% | 87.05% | 56.63% |
| HHI | 0.2166 | 0.1808 | 0.2312 | 0.1063 |
| Maximum local labor share | 23.62% | 2.12% | 21.21% | 6.67% |

The remaining aggregate concentration is in large-capacity economies: India,
Pakistan, and the United States lead synthetic stock; India and the United States
lead machine capacity. Ireland, Malaysia, Angola, and Pakistan no longer dominate
because of small denominators.
