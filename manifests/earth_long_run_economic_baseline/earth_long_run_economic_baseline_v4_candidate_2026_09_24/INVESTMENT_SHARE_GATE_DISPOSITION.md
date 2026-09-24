# 2031–2060 investment-share gate disposition

**Class: data. Decision: HOLD / REVIEW remains open.** This is a read-only audit of the existing v4 candidate and v3 control. No model, threshold, source artifact, baseline pointer or candidate trajectory was changed. The complete ranked top 20 and source/report hashes are in `INVESTMENT_SHARE_GATE_AUDIT.json`; `audit_investment_share_gate.py` regenerates it offline from pinned local stage outputs.

## Exact excursion

The independent scan covered 23,200 country-sector annual moves. Maximum: **CIV / SERVICES, 2031→2032, −4.009355027507 percentage points**. SERVICES investment falls from **6,517,882,039.777055** to **5,954,888,222.669354** model proxy units, while total CIV investment rises from **22,522,676,310.871113** to **23,886,584,737.201862**. Its share falls from **28.939198653896%** to **24.929843626389%**. Twelve moves exceed 3 points; the ranked top 20 are all SERVICES in 2031→2032. The largest subsequent annual move is 1.727572365 points (2032→2033); from 2034→2035 onward it is at most 0.489481756 point.

The frozen v3 source stage has the **same** CIV/SERVICES 2031 and 2032 investment and share values, the same 4.009355-point maximum, and the same top-20 identities. The v4 Taiwan repair did not create this excursion. The candidate's source rows reproduce the stage report's recorded maximum, and the report's own hashes match the inspected country, sector and asset bytes.

## Causal trace

The country's 2032 investment envelope is its frozen 2031 investment/VA rate multiplied by modeled 2032 country VA. At the first post-boundary year the calibrated IO demand pressure for CIV/SERVICES is effectively **1.0**. Its capital productivity and prior investment share enter the generic expansion score. The score gives a desired SERVICES expansion share of **26.1977493581%**; 12% blending with the prior **28.9391986539%** share yields **28.6102247384%** of expansion investment.

Replacement-first accounting allocates **12,924,600,012.385761** of the **23,886,584,737.201862** country envelope to asset depreciation replacement, with full coverage. The remainder, **10,961,984,724.816101**, is competitive expansion. SERVICES receives **2,818,639,757.110165** replacement and **3,136,248,465.559188** expansion. The sum exactly reproduces its 2032 investment. Replacement makes up **54.1081956863%** of country investment and allocates only **21.8083325937%** of its budget to SERVICES. Decomposed against the prior share, replacement contributes **−3.858382962 pp** and smoothed expansion **−0.150972066 pp**. The total is **−4.009355028 pp**.

## Classification and governance

**LEGITIMATE_MODEL_DYNAMICS** means internally valid dynamics under the inherited model, not evidence that the real CIV economy will follow them. The inherited 2031 seed allocation and the 2032 replacement-first rule differ. Expansion is smoothed; mandatory asset replacement is not. The resulting total-sector share movement is therefore larger than the expansion-share adjustment. This is a systematic first-transition effect, not a v4 regression, arithmetic bug, unexplained country exception or failed conservation identity.

The 3-point REVIEW check measures *total* sector investment shares. Its failure is a valid warning about that modeled transition; it must not be relabeled PASS merely because its cause is explained. The inherited stage code explicitly requires `max_investment_share_move <= 0.03` for `qualification.passed`, and emits `REVIEW` otherwise. Current change control permits review risk acceptance only when the applicable rule allows it and records the decision; it provides no automatic conversion of this numerical failure into PASS. No bounded candidate-local mechanism change is justified by this audit: capping realized shares would override the existing replacement/expansion allocation, while rewriting the frozen 2031 boundary would invalidate upstream dependencies. Either approach would introduce a new modeling assumption solely to satisfy the gate.

The stage's new maximum remains **4.009355027507 pp** because model behavior is unchanged. Its qualification remains `REVIEW`, so v4 is **HOLD**, not promotion-ready. A governed decision to accept this explicit REVIEW, or to revise the criterion with a separately authorized modeling/qualification change, is needed before promotion. This audit itself grants neither exception nor promotion authority.

## Effects and checks

Since no numerical input or code in the model chain changed, the 2060 and 2226 outputs are byte-identical to the pinned v4 candidate. The existing v4 versus v3 controlled difference remains: at 2060, global 80-economy VA is **3,885,964,509.90625 proxy units lower** (−0.001953%); at 2226 it is **881,047,102.25 higher** (+0.000268%). These differences come from the previously documented Taiwan repair and its interactions, not from this disposition. Existing country investment conservation, country/sector/asset reconciliation, capital stock-flow, operative production and TWN/ENERGY repair validations remain applicable; they are not replaced by this audit.
