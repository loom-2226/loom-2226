# Build 8 Experiment A: abstraction register

**Standing:** implementation-facing research/experiment register, not canon, qualification, or a license to broaden the runtime. Extends the 14-entry Build 7 as-built register in draft PR #377, which is based on pinned Build 7 executable commit `66c641d25e641e0aff77940a8cadbf1653247113`. Build 7's A01–A14 remain unchanged. This file records only the differences that matter to Experiment A.

| ID / standing | Build 8 abstraction | What it can change | What it cannot establish | Current implementation |
|---|---|---|---|---|
| B8-A01 **Active input** | The promoted Earth v4 economic projection is read as 80 ISO3 investment capacities for each year 2026–2035. | Country-specific scale of *potential* finance. | Cash, credit, willingness to invest, sovereign budget, private ownership or actual investment. | `country_capital_input.py`: 800 read-only records with file hashes. |
| B8-A02 **Active input choice** | The 2031 overlap between the qualified 2026–2031 and staged 2031–2060 files is resolved in favor of the qualified input. | Continuity and numerical identity at the boundary. | A demonstrated economic discontinuity or a reconciled historical observation. | `country_capital_input.py`; provenance reports rule. |
| B8-A03 **Active preview, not runtime** | Apply Build 7's existing binary `derive_mobilization` gate separately to each country-year, with common scenario parameters and opportunity state. | Counterfactual national contribution and total potential mobilization. | 80-country account transfers, market-clearing, a calibrated national propensity, or committed financing. | `capital_preview.py`, read-only. |
| B8-A04 **Existing runtime invariant / pending** | Country mobilization requires matching Earth investment assertions, country-scoped boundary account, matching destination account and an actual ledger transfer. | Whether country-origin funds can be admitted as real simulation finance. | Permission to credit Sponsor accounts directly from forecast values. | Build 7 kernel enforces it; Build 8 runtime admission not connected. |
| B8-A05 **Deferred** | Finite country financing pools and competing Sponsors will be evaluated using existing account, commitment and policy concepts before adding behavioral characteristics. | Financing rejection, displacement, persistent differences in project selection. | Competitive behavior merely from having 80 projections; genuine competition without independent decisions. | No independent FIN or second Sponsor yet. |
| B8-A06 **Deferred** | Country strategic pressure is fixed at zero for Experiment A; no country Agents. | A clean economic-capacity baseline against which later pressure experiments can be compared. | Country preferences, geopolitical motives, policy response or endogenous strategic pressure. | Existing `base_salience=0`, `race_pressure=0`. |
| B8-A07 **Existing temporal limit** | Build 7's yearly conductor and its separation of decision, commitment, disbursement and completed evidence remain the working approximation. | Ordering, delayed consequences and finite exposure. | Continuous asynchronous operations or instant return on prospecting. | No new scheduler. |

## Causal boundary

`Earth v4 modeled investment capacity -> admitted country investment assertion -> Build 7 activation gate -> country-scoped ledger transfer -> available finance -> actor-visible decision -> commitment -> disbursement -> persistent project outcome`.

Only the **input** and a **non-mutating preview of the activation gate** are implemented so far. The later arrows must not be described as active Build 8 behavior.

Hidden deposit truth remains unavailable to Agent decision policies. Country capacity cannot be treated as an Agent belief, account balance, or realized investment without the relevant admission/transaction step.

## Smallest next experiment

1. Establish a fresh reproducible Build 7 database-backed control run in an isolated, correctly configured service environment.
2. Supply country-specific investment assertions and matching country-origin accounts for a Build 8-only conductor, preserving the existing kernel check and the unchanged mobilization formula.
3. Demonstrate a real country-origin transaction and conservation for two countries first; only then exercise all 80.
4. Stop before adding new Sponsor personalities, government Agents, finance markets or strategic-pressure formulas. Competition is a subsequent increment, after this boundary works.

**Escalation rule:** revise an abstraction only if a run demonstrates that it materially prevents the desired country-capital or Sponsor competition behavior. Do not promote a research suggestion into runtime merely because it exists.

## Experiment A two-country observation (isolated trial)

B8-A04 is now **demonstrated in an in-memory kernel trial for USA and AUS**, not in a governed Build 8 campaign: the existing transition enforces country-scoped Earth assertions and accounts, and produces matching debit/credit ledger movements. The trial constructs temporary manifest assertions and accounts; it is not a qualified genesis or persistent run. This is a proof that the existing kernel can express the country boundary without modifying its transaction rules.
