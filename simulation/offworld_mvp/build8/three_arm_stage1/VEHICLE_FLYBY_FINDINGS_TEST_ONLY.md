# kT-authored vehicle flyby experiment: TEST ONLY

All input values authored by kT. Earth mu and radius are from `src/loom_solar_gis.py:93`, provisional engineering references, NOT kernel constants. No speed or stage cap. Existing 45–1400-day flight window remains.

Authored SHA-256: `1a45564a1efb9f6bb134f00d43d05aa763ce71f99a34a9ee79029f0e97eae167`. Run identity SHA-256: `5006160050f4257a49e808f6fab033dd4bdeb27d4f88b5ac27271f3b1cf7c4e1`.

Geometry: 118 body-years, 3731 sampled departures, 652.725 s. Differences in speed/date against old priced quotes: 0.

The full 118-row speed/date/flight/stage/mass/price/proxy comparison is in `VEHICLE_FLYBY_GEOMETRY_TEST_ONLY.csv`; condensed pricing is in `VEHICLE_FLYBY_PRICES_TEST_ONLY.csv`.

Route 1 control: `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430` PASS. Variant: `577d1616ecfc1912052b3746b4f1d20c16dc3f435f24b067c68b26d1b6a62c5a`. Funded stages 211, funded bodies 78, spent 434.5350141392697338 model units.

Blockers: {'ACTUAL_SPONSOR_CASH': 52222, 'FINANCIER_CONCENTRATION': 218}. Never funded: ATLAS3I, BORISOV, ERIS, GONGGONG, HAUMEA, MAKEMAKE, MS4, ORCUS, OUMUAMUA, SALACIA, SEDNA, SWIFTTUTTLE. All never-funded bodies encountered sponsor cash blocks.

## Previously BLOCK-excluded bodies

| Body | First year | Sponsor | Model units | If never: blocker |
|---|---:|---|---:|---|
| ARROKOTH | 2083 | ISRO | 58.94722875612214 | — |
| ATLAS3I | Never | — | — | ACTUAL_SPONSOR_CASH |
| BORISOV | Never | — | — | ACTUAL_SPONSOR_CASH |
| CHIRON | 2036 | ISRO | 0.7367757682668307 | — |
| COMET_HALLEY | 2036 | CNSA | 13.19879642094347 | — |
| ERIS | Never | — | — | ACTUAL_SPONSOR_CASH |
| EURYBATES | 2036 | Blue Origin | 0.7173753497988874 | — |
| GONGGONG | Never | — | — | ACTUAL_SPONSOR_CASH |
| HAUMEA | Never | — | — | ACTUAL_SPONSOR_CASH |
| IXION | 2057 | CNSA | 19.80271318938942 | — |
| LEUCUS | 2036 | Axiom | 0.7155239178650713 | — |
| MAKEMAKE | Never | — | — | ACTUAL_SPONSOR_CASH |
| MS4 | Never | — | — | ACTUAL_SPONSOR_CASH |
| ORCUS | Never | — | — | ACTUAL_SPONSOR_CASH |
| OUMUAMUA | Never | — | — | ACTUAL_SPONSOR_CASH |
| PATROCLUS | 2036 | SpaceX | 0.8330802883265386 | — |
| PLUTO | 2045 | CNSA | 12.86980601199592 | — |
| POLYMELE | 2036 | CNSA | 0.7177800661723777 | — |
| QUAOAR | 2067 | CNSA | 37.10085593530952 | — |
| SALACIA | Never | — | — | ACTUAL_SPONSOR_CASH |
| SEDNA | Never | — | — | ACTUAL_SPONSOR_CASH |
| SWIFTTUTTLE | Never | — | — | ACTUAL_SPONSOR_CASH |
| VARUNA | 2171 | ISRO | 169.74371720827765 | — |

## Hand checks

| v-infinity | Stages | Mass in LEO | Hand target | Difference |
|---:|---:|---:|---:|---:|
| 10 km/s | 1 | 3.607 t | 3.6 t | +0.191% |
| 20 km/s | 2 | 49.919 t | 50.0 t | -0.162% |
| 30 km/s | 3 | 1,357.951 t | 1,360.0 t | -0.151% |

## Time, memory and hashes

Geometry 652.725 s, variant 26.847 s, total including control 695.582 s, peak RSS 552390656 bytes.

Geometry CSV SHA-256 `41b96b0d0376fc7742287890bbb779ce5679c6053d639a6a00167b7e7943f759`. Prices CSV SHA-256 `2a36b2ef103480c7b8624b86d6910becd69472ad78913ec2ea60141e64643b73`.

The JSON report embeds the exact authored input, its hash, the source hashes, and the run identity. This idealized staging model is not a complete or calibrated mission design; astronomical masses and prices are retained rather than capped.
