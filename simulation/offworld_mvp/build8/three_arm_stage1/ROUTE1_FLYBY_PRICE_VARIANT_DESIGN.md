# Route 1 A1 flyby-price variant (draft, TEST_ONLY)

Scope: opt-in beside the original 201-year, 90-body Route 1 campaign. No historical runner, kernel, frozen input, or other PR edits. Control is the original campaign with an identical stable-content fingerprint; reject any difference.

* A1 purchase amount: pinned `A_VEHICLE_MISSION_PAIRS.csv` `lowest_price_usd` for `(body, source_year, baseline, flyby)`, divided by the existing authored `1,000,000,000 USD / MODEL_CURRENCY`. A2 and all other service prices remain unchanged.
* Source-year rule: use the requested year when present (2026 or 2027); otherwise use the **authored held year 2026**. Label each A1 attempt `TABLE` or `HELD_2026`, and hash the rule and pinned table into variant identity. This is a held price, **not** a valid 2036 departure window.
* The table has only 25 bodies, whereas Route 1 admits 90. **No invented prices**: absent, infeasible, or unpriced A1 entries must be explicitly blocked, not replaced with a generic price. Report their counts separately. This retains 90 body-year states, not 90 guaranteed fundable bodies.
* Keep sponsor account, ceiling, financier decision, executor category selection, commitment, disbursement and supplier-payment chain. Existing selected RUN executor receives the full A1 amount via the same project-cash to supplier transfer; it is not a vendor bid or physical-delivery proof.
* Preserve synthetic A1 review and A2 logic, explicitly labeled. Report by year the funded body counts, supplier spend, and sponsor-ceiling blocks for control and variant, including zeros. Do not tune ceilings.
* Require exact stable control replay, sponsor-year conservation and supplier-payment identities. Stop on any failure. No B/C/D.

* Flyby variant defaults `ceilings_enabled=False` because the authored, unsourced request ceilings were the binding limit under flyby prices; Route 1 control retains its own default.
