# Box 3 PR A: 2040 regional observation proof

**RESEARCH / OPT-IN / NON-CANON.** Executed only against disposable PostgreSQL.
Base: `c194a7d7b5987cea0b81940ac17c456995052977`. No Build 7,
kernel, existing WORLD, baselines, pinned results, or placeholders changed.

## Executed scope and honest limits

One **2026-generated** sealed WORLD. The previous database was not used as
the source of a row-by-row copy: the existing frozen generator was used at
epoch **2026**, with the already established test seed
`BUILD7-I5-QUAL-POSITIVE-V3`. No WORLD was generated at 2040.
This followed the authorized generator fallback, but does not establish that
copying the existing authoritative database was impossible.

The sealed scientific input was the committed
`LOOM_SOLAR_WORLD_SCIENCE_LAB_v0_1.sqlite3`, SHA-256
`72ddfab0eb35fb5a86ecfd50d4bc939a982ffc1fe3362108036082298a57b777`.
World Authority reopened the 90 realizations and checked their complete
generator digests against the admitted 90-body catalog and seed. Recomputed
sealed-WORLD digest:
`064b6cb6e797ee3a0d0e13b587f0344fadb47a1959d5a302fc17411c4e0b1cd8`.
The private instance contained 90 realizations and 5,850 hidden-state rows.
These hashes verify deterministic 2026 generation and private reopen, **not**
byte equality to a separately persisted historical WORLD copy.

The existing Build 7 2026 prospecting initiation created:
- Project `PROSPECT:MOON:BUILD7_PROSPECTING_REGION_10`;
- Location `f31d09e3-44d6-5602-9dd2-109246567555`;
- Status `EXPLORING`; separate project cash account with 2 MODEL_CURRENCY;
- One genuine 2026 country-capital disbursement. No study initialized yet.

The study was legitimately authorized and started in **2039** because its
frozen planned duration is one year. It was **paid, measured, completed and
admitted in 2040**. Neither the Build 7 annual conductor nor its 2035 extension
was invoked.

## 2040 synthetic proof inputs (NOT economic forecasts)

- `SYNTHETIC_2026_PROJECT_CAPITAL = 2 MODEL_CURRENCY`. This is an existing
  authored high-sensitivity fictional Build 7 scenario amount, *actually*
  disbursed in 2026 and retained until 2040. There was no invented 2040
  injection of cash.
- `SYNTHETIC_2040_STUDY_SUPPLY_CLAIM = 2 MODEL_SUPPLY_CLAIM_CURRENCY`.
  This explicitly labeled **study consumption claim** was checked against
  the existing 2040 Earth-reference capacity (6,312.373897515541).
  **The capacity itself was not replaced with synthetic data.** The two-unit
  claim was reserved and immediately consumed into `spent` by the frozen
  exploration-WIP kernel transition; final `reserved = 0`, `spent = 2`.
- The test does not predict actual 2040 terrestrial production, supply,
  financial markets, or cost levels. No hidden governor or filtering introduced.

## PASS table, observed values

| Requirement | Result |
|---|---|
| Cash debited once | Project cash **2 -> 0**, one study expense **2** |
| Supplier credited once | Supplier cash **0.614154 -> 2.614154**, transfer **2** |
| 2040 Earth supply actually consumed | `reserved +2 -> 0`, `spent 0 -> 2` |
| Read hidden truth only through World Authority | Frozen REGION handler calls `load_run_region_material_truth` on authorized project/location binding; no truth passed as sponsor input |
| Direct truth access by SPN | SQL denied: `permission denied for schema wa_world` |
| Observation visibility | Four region results admitted to SPN, all `public=False`; none admitted to PUB or FIN |
| Belief change | Volatiles, metals, carbonaceous: **0.5 -> 0.2** on NEGATIVE; silicates/rock: **0.5 -> 0.8** on POSITIVE |
| Negative remains evidence, not closure | Three negative results, all posterior beliefs > 0; project still `EXPLORING`; **zero** study-review execution records |
| Other actors | PUB and FIN belief dictionaries unchanged |
| Reopen/replay | 32/32 epoch statuses `ALREADY_MATCHED`; serialized report, ledger, evidence, beliefs, causal head identical |
| Final causal head | `causal:SOLAR_MATERIAL_0f6ad0ea1f03881a7a67b3b1:e05fb17d7276b5d2:58` |

The overall study standing was `SUPPORTS_ADVANCE` because one material-family
signal was positive. **A fully all-negative study was not observed.** The
consumer never invokes `execute_project_study_review`, regardless of the
standing; it makes no post-study sponsor-choice claim.

Replay fingerprints:
- Ledger: `4d9a27cce14b8ba58867e2cf4f4a031c43ede25a791d25d3a93dd9586b820203`
- Observation: `0dce05bd8047bbe66487c195f05a6db6d1441ab330bc86cb4c7fb6d5d7e66683`
- Sponsor beliefs: `34b1d0f9232855d31e884936103a9da7e2990acd7b87e942f7429d2671279986`

## Same-year measurement and limits

The governed regional observation key contains year, actor, body, region and
material family, but not attempt number. A second call with that **same key**
in the same year repeats the same draw. This is an existing limitation, not
a proof of measurement independence. No repeat-study or multipayer support
was added.

## Private PostgreSQL and qualification evidence

The exact cached `postgres@sha256:5a5a84b19854a9ffaa54082c166ff4ec27473a361e496e5ea167f298f2da9722`
image ran PostgreSQL **18.6**, `pgcrypto 1.4`, on
`127.0.0.1:55947` in a disposable container using its own ephemeral
host-mounted data directory. Both committed migrations 001 and 002 were loaded
**unchanged**. Seven temporary application logins had only locally created
role grants. Every connection in the test used a newly created temporary
`PGSERVICEFILE` that pointed exclusively at `box3_proof`. The Build 8
consumer itself refuses service files outside its private scratch path and
refuses any database/principal other than `box3_proof`/`box3_runtime`.

The remote agent needed `sg docker` to activate Docker group membership,
which kT had already granted. Docker privileges were used to create, inspect,
stop and remove only the private test container and its scratch-data
ownership. The other 14 containers were not managed. No existing DB service,
system setting, terminal restriction, LXD snap, source file or pin was
modified. The private container, scratch directory, credentials and service
file were removed after testing.

## Tests and further limits

- Offline unit: four tests **PASS**, persisted test skipped by design.
- Opt-in private PG: five tests **PASS**, no skips (includes real two-reopen
  comparison against the isolated 2040 run).
- Existing Build 8 CI fast suite is separately fixed at ten unrelated tests.
- No 2040+ annual opportunity model, repeat study, second sponsor, alternate
  payer ownership, post-study investment decision, calibrated geology,
  realistic grades, or full historical WORLD row-copy validation is claimed.

The source is a narrowly scoped experiment. Do not run it with an existing
authoritative service or generalize its synthetic supply claim into LOOM canon.
