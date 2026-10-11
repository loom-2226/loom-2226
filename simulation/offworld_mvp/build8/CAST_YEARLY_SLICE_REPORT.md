# Build 8 cast-selected yearly world: first slice

**Class:** `class:engineering`. Noncanon, disposable screened experiment.

## What changed

`run_yearly(selection='legacy_usa')` now obtains sponsors, source country,
BUILD/LAND executors, private-observation owner and disclosure recipient, and
sponsor policy-input motives from a named, validated cast selection. The
legacy selection preserves the existing screened replay. No changes to
`run_screened`, Build 7, canon, the master cast, or frozen snapshots.

The existing sponsor-prospecting and test-only financier policies, evidence
transitions, capacity reservations, contract terms, chronological settlement,
knowledge and subcontract rules are reused. Cast roles/capabilities are
validated; no actor is assigned a role the cast does not contain.

## Additional configuration: `japan_lunar`

- Sponsors: Axiom and ispace (both `private_sponsor` in the cast).
- Country source: JPN, using its existing 2026/2027 Earth v4 investment
  capacities and the existing country-capital mobilization rule. Both sponsors
  have explicit **authored** JPN funding participation in the existing
  `named_sponsor_trial.ROUTES` (Axiom 0.25, ispace 0.75). These are NOT audited
  ownership or investment commitments; this screened path does not apply those
  weights to the funding envelope.
- BUILD: Thales Alenia Space; LAND: ispace. Both capabilities are SOURCED in
  the candidate cast. Their selection is **authored**, not a procurement win.
- Sponsor motives/info values are **AUTHORED** scenario inputs: Axiom
  LUNAR_INFRASTRUCTURE/2.20; ispace RESOURCE_RETURN/2.00. No claim is made
  about actual company motives.
- To fit the smaller JPN mobilized envelope without fictitious money, BUILD
  base cost 1.20 and LAND base cost 1.50 are **AUTHORED MODEL QUOTES**, not
  actual prices or bids. Existing markups/durations remain unchanged. The
  2.00/4.00 financing ceiling remains **AUTHORED** and is capped by available
  mobilized cash for nonlegacy selections. No cast capacity index is scored.
- The private observation remains owned by Axiom, a selected sponsor with
  EXPLORE capability in this synthetic fixture. ispace receives it only when
  `share_private=True`. The 2026 authored stamp/epoch-2 exception is preserved.
- The financier is still the explicitly synthetic `SCREEN_FINANCIER`, using
  the existing **test-only** policy manifest; this is **not** a claim that
  any real Japanese financial institution made these decisions.

### Observed result

Both sponsor policies initiated projects; both financier screenings approved.
ispace funded 2026; Axiom funded 2027. Four stages delivered:

| Sponsor | BUILD | LAND |
| --- | --- | --- |
| ispace | 2026–2028 | 2028–2030 |
| Axiom | 2027–2029 | 2029–2031 |

The kernel invariants hold, the knowledge years are non-decreasing, and the
new configuration repeats deterministically. The three frozen legacy yearly
acceptance replays remain unchanged.

## Where it broke / needed authoring

The first attempt with original USA-style 2.00 upfront finance failed because
JPN 2026 mobilized cash was only 1.325135751324722. Capping the envelope to
actual mobilized cash then caused sponsor WAIT under the original 1.525
project requirement. An intermediate authored quote totaling 1.06875 still
failed the existing financier policy. The explicitly authored 1.20/1.50 base
quotes yield 0.825 total project price and passed **the existing** policies.
No policy was bypassed or invented to make the run pass.

Limits: this remains a synthetic two-sponsor screened experiment, not an
80-country clearing system or an actual Japan financier. Country choice is a
named authored source, not a rule deriving each sponsor's capital from its
home-country or funding-route weights. The supplier revenue accounts are
placed at the selected financing-country node even for a foreign-home
executor; this is a simplified settlement location, not a claim of a Japanese
establishment. Prices, sponsor motives, disclosure relevance and funding
ceilings are authored. Capacity index remains null/unscored.

**Stop:** No broadening to multiple capital sources, new policy, bidding,
capacity scores, cast-wide race or governance machinery in this PR.

## Internal delivery audit marker (follow-up)

The Japan selection has one same-owner sponsor/executor payment: **ispace**
LAND, 2030, `tx-000056`, **0.450000 authored model units** from
`screen:cash:ispace` to `screen:revenue:LAND`. Both accounts are owned by
ispace. The yearly path now adds a `BUILD8_INTERNAL_DELIVERY` audit event
with the project, category, sponsor, executor, year, transaction ID and amount.
It is an observation of existing account ownership, **not** a new payment,
policy decision, deduction, or contract term. The existing 0.3750 modeled
expense and 0.075 margin on this stage remain unchanged. No frozen legacy
scenario contains a same-owner sponsor/executor transfer, so none emits this
audit marker; their event multisets remain unchanged.

**Consolidated accounting for vertically integrated firms is a future step,
not implemented here.** The current accounts and economics remain separate,
even when owned by the same legal actor.
