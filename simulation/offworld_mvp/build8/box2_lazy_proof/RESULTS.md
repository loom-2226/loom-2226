# Build 8 Box 2 lazy price proof: measured result

**TEST_ONLY / NON-CANON / NON-RUNTIME. DRAFT. DO NOT MERGE.**

Run identity SHA-256: `4cc7501a2cae9a51812f7095ae320aad8283b5150489d383db60ace05ad28ba7`
Authored input SHA-256: `96a7adff94c6e4c609466ad512857d3a8a64f5436a1edf55c6b927237214f290`
Replay scientific SHA-256: `b8c28a0df28431e07c6d7260385ab0c663df02084b2978448464df80c10f2f7e` (both replays match: True)

## Authored values

```json
{
  "classification": "TEST_ONLY_NONCANON_NONRUNTIME",
  "destinations": [
    "MARS",
    "EROS",
    "VESTA",
    "JUPITER",
    "ARROKOTH",
    "EUROPA"
  ],
  "origin": "EARTH",
  "pricing": {
    "basis": "median of 87 Build7 2026 non-Moon orbital-recon price / endpoint burden observations",
    "caveat": "TEST_ONLY proxy, not market fare; 2026 median rate held numerically flat to 2226 by assumption; no inflation, technology evolution, infrastructure or market response modeled",
    "rate_usd_millions_per_km_s": "72.269449528",
    "source_sha256": "10b351a4c9cbecea86872de2ec7301e0899856dc1093830ceccbc85fb68bcc3e",
    "standing": "HELD_AT_2026_LEVEL_BY_ASSUMPTION_NOT_EMPIRICAL"
  },
  "probe": {
    "asset_root": "/home/ubuntu/loom_solar_assets",
    "cache_mode": "memory_per_replay",
    "cache_requery_each_computed_geometry": true,
    "candidate_policy": "choose lowest priced admissible sampled route; rank sponsor value minus price",
    "date_coverage_policy": "each sampled departure only; not a whole-year closure",
    "replays": 2,
    "required_packages": {
      "lamberthub": "1.0.0",
      "numpy": "2.5.3",
      "spiceypy": "8.2.0"
    },
    "unsupported_policy": "no award and no fallback"
  },
  "sampling": {
    "daily_refinement": true,
    "flight_step_days": 0.25,
    "include_last_day": true,
    "max_transition_brackets_per_body_year": 1,
    "refinement_step_days": 1,
    "start_month_day": "01-01",
    "strategy": "daily",
    "stride_days": 28
  },
  "sponsor": {
    "minimum_surplus_usd_millions": "0",
    "name": "TEST_SPONSOR",
    "values_usd_millions": {
      "ARROKOTH": "2200",
      "EROS": "700",
      "EUROPA": "2000",
      "JUPITER": "1600",
      "MARS": "850",
      "VESTA": "950"
    }
  },
  "vehicle": {
    "arrival_limit_km_s": 10.0,
    "departure_limit_km_s": 10.0,
    "flight_range_days": [
      45.0,
      1400.0
    ],
    "payload_tonnes": 2,
    "service_type": "ORBITAL_RECON",
    "transfer_family": "IZZO2015_M0_PROGRADE_LOW_PATH_HELIOCENTRIC"
  },
  "years": [
    2026,
    2100
  ]
}
```

## Measured rankings

| Year | Body | Minimum sampled price (USD M) | Sponsor value (USD M) | Surplus (USD M) | Award eligible | Coarse / refined dates |
|---|---|---:|---:|---:|---|---|
| 2026 | MARS | 407.7596998991749920 | 850 | 442.2403001008250080 | True | 14 / 27 |
| 2026 | EROS | 608.0252679545277744 | 700 | 91.9747320454722256 | True | 14 / 27 |
| 2026 | VESTA | 769.2998852885798936 | 950 | 180.7001147114201064 | True | 14 / 27 |
| 2026 | JUPITER | 1085.9094528927667736 | 1600 | 514.0905471072332264 | True | 14 / 27 |
| 2026 | ARROKOTH | — | 2200 | — | False | 0 / 0 |
| 2026 | EUROPA | — | 2000 | — | False | 0 / 0 |
| 2100 | MARS | 1060.4433972111634816 | 850 | -210.4433972111634816 | False | 14 / 27 |
| 2100 | EROS | 584.9642817376567000 | 700 | 115.0357182623433000 | True | 14 / 27 |
| 2100 | VESTA | 781.8286399168181712 | 950 | 168.1713600831818288 | True | 14 / 27 |
| 2100 | JUPITER | 1060.7677858623148624 | 1600 | 539.2322141376851376 | True | 14 / 27 |
| 2100 | ARROKOTH | — | 2200 | — | False | 0 / 0 |
| 2100 | EUROPA | — | 2000 | — | False | 0 / 0 |

2026 ranking: Jupiter, Mars, Vesta, Eros. 2100 ranking: Jupiter, Vesta, Eros. Mars 2100 has a priced feasible sample but negative Sponsor surplus and no award. Arrokoth: `UNSUPPORTED: REQUIRED_KERNEL_ASSET_MISSING`. Europa: `UNKNOWN_LOCAL_LEG`, ineligible.

## Replay telemetry (measured, not included in scientific replay hash)

| Replay | Wall time sum (seconds) | New geometry calculations | Geometry cache hits |
|---|---:|---:|---:|
| 1 | 97.337 | 328 | 328 |
| 2 | 91.098 | 328 | 328 |

## Limitations

- These are 14 coarse departure dates per body-year and 27 daily refinement dates in the first observed transition bracket, not a continuous annual window census.
- Only the first observed coarse transition bracket is refined, by authored policy. Other transitions are not resolved.
- The 45–1400-day, 0.25-day-step, zero-revolution prograde heliocentric Lambert search is not mission design or a general outer-system transfer model.
- Price = authored rate × (departure v-infinity + arrival v-infinity). Rate is a 2026 Build 7 87-anchor proxy held numerically constant to 2226, not empirical transport pricing.
- No runtime funding, executor contracting, mission completion, local moon leg or full-clock travel integration was built.
- Source hashes and installed package versions are in RESULT.json; exact departure dates, source failures and timings are recorded per pair.
- The separate 46-file Phase 4E report lists every manifest size, SHA-256, declared source and the limited HEAD-only reachability observations. No assets were downloaded.
