# PR427 price-only flight-limit sensitivity

**TEST_ONLY / NON-CANON. No economic campaign run.** 90-body/20-sponsor world, 2026–2226 campaign context. This prices only the 33 previously unstarted bodies, with the held-2026 departure rule.

Authored scenario: `scenario.json`; SHA-256 `cda27da39d9f02bfb8fddca9ac41d3e797111389034af2a305cb029b73d37b9d`. Limits: 1,400 / 3,000 / 5,000 / 8,000 days.
Clean input prices SHA-256: `49fbd0f1015268d24e931b9e1d7083cb8a0cd3f6c02a4942a130d0885695922f`.
Fixed-cost floor: 0.7 model units; **fail on violation, never clamp**. All 42 priced rows passed.

**Important coverage distinction:** The 1,400-day rows reuse the accepted complete-cost-layer 2026 quotes, rather than recomputing them. The 3,000-day rows are new cost-layer calculations where existing validated position tables cover the full requested flight window. A `NO DATA` row means the **existing position table** does not cover the listed required date, not that no suitable kernel exists anywhere on the VM. No kernel-derived tables were created in this job. Thus 5,000/8,000-day prices remain unresolved, not economically ruled out.

## Prices and missing data

| Body | Limit days | Price (model units) | Flight days | Braking km/s | Status / exact missing position |
|---|---:|---:|---:|---:|---|
| ARROKOTH | 1400 | 9021850532.03038 | 1400.0 | 52.1257155 | PRICED_EXISTING_2026 |
| ARROKOTH | 3000 | — | — | — | NO DATA: ARROKOTH 2034-05-04 |
| ARROKOTH | 5000 | — | — | — | NO DATA: ARROKOTH 2039-10-25 |
| ARROKOTH | 8000 | — | — | — | NO DATA: ARROKOTH 2048-01-11 |
| ATLAS3I | 1400 | 18806254.98086541 | 1400.0 | 13.0972932 | PRICED_EXISTING_2026 |
| ATLAS3I | 3000 | — | — | — | NO DATA: ATLAS3I 2034-05-04 |
| ATLAS3I | 5000 | — | — | — | NO DATA: ATLAS3I 2039-10-25 |
| ATLAS3I | 8000 | — | — | — | NO DATA: ATLAS3I 2048-01-11 |
| BORISOV | 1400 | 1.971397548868517E+18 | 1272.75 | 60.7913339 | PRICED_EXISTING_2026 |
| BORISOV | 3000 | — | — | — | NO DATA: BORISOV 2034-05-04 |
| BORISOV | 5000 | — | — | — | NO DATA: BORISOV 2039-10-25 |
| BORISOV | 8000 | — | — | — | NO DATA: BORISOV 2048-01-11 |
| CHARON | 1400 | 38263924.680126136 | 1400.0 | 42.45840979585875 | PRICED_EXISTING_2026 |
| CHARON | 3000 | 45.0417852384064 | 2779.5 | 20.26388449645816 | PRICED_NEW |
| CHARON | 5000 | — | — | — | NO DATA: PLUTO 2039-10-25 |
| CHARON | 8000 | — | — | — | NO DATA: PLUTO 2048-01-11 |
| CHIRON | 1400 | 18.67059879597077 | 1387.0 | 20.2658801 | PRICED_EXISTING_2026 |
| CHIRON | 3000 | — | — | — | NO DATA: CHIRON 2034-05-04 |
| CHIRON | 5000 | — | — | — | NO DATA: CHIRON 2039-10-25 |
| CHIRON | 8000 | — | — | — | NO DATA: CHIRON 2048-01-11 |
| COMET_HALLEY | 1400 | 36908661.171130264 | 1400.0 | 42.3721633 | PRICED_EXISTING_2026 |
| COMET_HALLEY | 3000 | — | — | — | NO DATA: COMET_HALLEY 2034-05-04 |
| COMET_HALLEY | 5000 | — | — | — | NO DATA: COMET_HALLEY 2039-10-25 |
| COMET_HALLEY | 8000 | — | — | — | NO DATA: COMET_HALLEY 2048-01-11 |
| DACTYL | 1400 | — | — | — | UNPRICED_EXISTING |
| DACTYL | 3000 | — | — | — | NO DATA: IDA 2034-05-04 |
| DACTYL | 5000 | — | — | — | NO DATA: IDA 2039-10-25 |
| DACTYL | 8000 | — | — | — | NO DATA: IDA 2048-01-11 |
| ERIS | 1400 | 6.028392693349309E+34 | 1357.0 | 121.5809423 | PRICED_EXISTING_2026 |
| ERIS | 3000 | — | — | — | NO DATA: ERIS 2034-05-04 |
| ERIS | 5000 | — | — | — | NO DATA: ERIS 2039-10-25 |
| ERIS | 8000 | — | — | — | NO DATA: ERIS 2048-01-11 |
| GONGGONG | 1400 | 2.309352311713559E+31 | 1392.5 | 111.4510572 | PRICED_EXISTING_2026 |
| GONGGONG | 3000 | — | — | — | NO DATA: GONGGONG 2034-05-04 |
| GONGGONG | 5000 | — | — | — | NO DATA: GONGGONG 2039-10-25 |
| GONGGONG | 8000 | — | — | — | NO DATA: GONGGONG 2048-01-11 |
| HAUMEA | 1400 | 25727721638697.34 | 1398.0 | 60.7948692 | PRICED_EXISTING_2026 |
| HAUMEA | 3000 | — | — | — | NO DATA: HAUMEA 2034-05-04 |
| HAUMEA | 5000 | — | — | — | NO DATA: HAUMEA 2039-10-25 |
| HAUMEA | 8000 | — | — | — | NO DATA: HAUMEA 2048-01-11 |
| HYDRA | 1400 | 40998324.28823179 | 1400.0 | 42.55244328407277 | PRICED_EXISTING_2026 |
| HYDRA | 3000 | 44.41529466812526 | 2791.5 | 20.264246487206155 | PRICED_NEW |
| HYDRA | 5000 | — | — | — | NO DATA: PLUTO 2039-10-25 |
| HYDRA | 8000 | — | — | — | NO DATA: PLUTO 2048-01-11 |
| HYPERION | 1400 | — | — | — | UNPRICED_EXISTING |
| HYPERION | 3000 | — | — | — | NO DATA: HYPERION 2034-05-04 |
| HYPERION | 5000 | — | — | — | NO DATA: HYPERION 2039-10-25 |
| HYPERION | 8000 | — | — | — | NO DATA: HYPERION 2048-01-11 |
| IXION | 1400 | 626762446.5797112 | 1400.0 | 45.1827727 | PRICED_EXISTING_2026 |
| IXION | 3000 | — | — | — | NO DATA: IXION 2034-05-04 |
| IXION | 5000 | — | — | — | NO DATA: IXION 2039-10-25 |
| IXION | 8000 | — | — | — | NO DATA: IXION 2048-01-11 |
| KERBEROS | 1400 | 40795122.84260992 | 1400.0 | 42.54570420732687 | PRICED_EXISTING_2026 |
| KERBEROS | 3000 | 44.49650753609123 | 2791.0 | 20.267225900439097 | PRICED_NEW |
| KERBEROS | 5000 | — | — | — | NO DATA: PLUTO 2039-10-25 |
| KERBEROS | 8000 | — | — | — | NO DATA: PLUTO 2048-01-11 |
| MAKEMAKE | 1400 | 7771504290314557 | 1400.0 | 64.5476265 | PRICED_EXISTING_2026 |
| MAKEMAKE | 3000 | — | — | — | NO DATA: MAKEMAKE 2034-05-04 |
| MAKEMAKE | 5000 | — | — | — | NO DATA: MAKEMAKE 2039-10-25 |
| MAKEMAKE | 8000 | — | — | — | NO DATA: MAKEMAKE 2048-01-11 |
| MIRANDA | 1400 | 22.30041972032444 | 1400.0 | 16.786843464205315 | PRICED_EXISTING_2026 |
| MIRANDA | 3000 | 0.8520693987502494 | 2967.0 | 5.858946054578736 | PRICED_NEW |
| MIRANDA | 5000 | — | — | — | NO DATA: URANUS 2039-10-25 |
| MIRANDA | 8000 | — | — | — | NO DATA: URANUS 2048-01-11 |
| MS4 | 1400 | 5958957321423.906 | 1286.75 | 60.7984727 | PRICED_EXISTING_2026 |
| MS4 | 3000 | — | — | — | NO DATA: MS4 2034-05-04 |
| MS4 | 5000 | — | — | — | NO DATA: MS4 2039-10-25 |
| MS4 | 8000 | — | — | — | NO DATA: MS4 2048-01-11 |
| NEREID | 1400 | 309438.4505641659 | 1400.0 | 34.70560007449134 | PRICED_EXISTING_2026 |
| NEREID | 3000 | 2.9056242727543764 | 3000.0 | 14.015478055240788 | PRICED_NEW |
| NEREID | 5000 | — | — | — | NO DATA: NEPTUNE 2039-10-25 |
| NEREID | 8000 | — | — | — | NO DATA: NEPTUNE 2048-01-11 |
| NIX | 1400 | 40469065.53304545 | 1400.0 | 42.534810428013415 | PRICED_EXISTING_2026 |
| NIX | 3000 | 44.4972815701033 | 2790.5 | 20.265869147798828 | PRICED_NEW |
| NIX | 5000 | — | — | — | NO DATA: PLUTO 2039-10-25 |
| NIX | 8000 | — | — | — | NO DATA: PLUTO 2048-01-11 |
| ORCUS | 1400 | 6766198740267.5 | 1342.5 | 61.1860527 | PRICED_EXISTING_2026 |
| ORCUS | 3000 | — | — | — | NO DATA: ORCUS 2034-05-04 |
| ORCUS | 5000 | — | — | — | NO DATA: ORCUS 2039-10-25 |
| ORCUS | 8000 | — | — | — | NO DATA: ORCUS 2048-01-11 |
| OUMUAMUA | 1400 | 1.6743653968179588E+21 | 1292.0 | 70.9261381 | PRICED_EXISTING_2026 |
| OUMUAMUA | 3000 | — | — | — | NO DATA: OUMUAMUA 2034-05-04 |
| OUMUAMUA | 5000 | — | — | — | NO DATA: OUMUAMUA 2039-10-25 |
| OUMUAMUA | 8000 | — | — | — | NO DATA: OUMUAMUA 2048-01-11 |
| PLUTO | 1400 | 44669372.4284115 | 1400.0 | 42.6680285 | PRICED_EXISTING_2026 |
| PLUTO | 3000 | 43.71390690940746 | 2805.0 | 20.2633915 | PRICED_NEW |
| PLUTO | 5000 | — | — | — | NO DATA: PLUTO 2039-10-25 |
| PLUTO | 8000 | — | — | — | NO DATA: PLUTO 2048-01-11 |
| PROTEUS | 1400 | 13751.150534916129 | 1361.25 | 30.41833258735411 | PRICED_EXISTING_2026 |
| PROTEUS | 3000 | 1.3516260263376758 | 3000.0 | 10.887199409514743 | PRICED_NEW |
| PROTEUS | 5000 | — | — | — | NO DATA: NEPTUNE 2039-10-25 |
| PROTEUS | 8000 | — | — | — | NO DATA: NEPTUNE 2048-01-11 |
| QUAOAR | 1400 | 4326292220.68595 | 1400.0 | 51.7945418 | PRICED_EXISTING_2026 |
| QUAOAR | 3000 | — | — | — | NO DATA: QUAOAR 2034-05-04 |
| QUAOAR | 5000 | — | — | — | NO DATA: QUAOAR 2039-10-25 |
| QUAOAR | 8000 | — | — | — | NO DATA: QUAOAR 2048-01-11 |
| SALACIA | 1400 | 19430952428802.71 | 1279.75 | 60.7973368 | PRICED_EXISTING_2026 |
| SALACIA | 3000 | — | — | — | NO DATA: SALACIA 2034-05-04 |
| SALACIA | 5000 | — | — | — | NO DATA: SALACIA 2039-10-25 |
| SALACIA | 8000 | — | — | — | NO DATA: SALACIA 2048-01-11 |
| SEDNA | 1400 | 1.7750730243491295E+28 | 1400.0 | 101.7881848 | PRICED_EXISTING_2026 |
| SEDNA | 3000 | — | — | — | NO DATA: SEDNA 2034-05-04 |
| SEDNA | 5000 | — | — | — | NO DATA: SEDNA 2039-10-25 |
| SEDNA | 8000 | — | — | — | NO DATA: SEDNA 2048-01-11 |
| SELAM | 1400 | — | — | — | UNPRICED_EXISTING |
| SELAM | 3000 | — | — | — | NO DATA: DINKINESH 2034-05-04 |
| SELAM | 5000 | — | — | — | NO DATA: DINKINESH 2039-10-25 |
| SELAM | 8000 | — | — | — | NO DATA: DINKINESH 2048-01-11 |
| STYX | 1400 | 40199382.82647385 | 1400.0 | 42.52572439767574 | PRICED_EXISTING_2026 |
| STYX | 3000 | 44.50403420557258 | 2790.0 | 20.2648312012379 | PRICED_NEW |
| STYX | 5000 | — | — | — | NO DATA: PLUTO 2039-10-25 |
| STYX | 8000 | — | — | — | NO DATA: PLUTO 2048-01-11 |
| SWIFTTUTTLE | 1400 | 423040047892.73605 | 1384.5 | 52.9314191 | PRICED_EXISTING_2026 |
| SWIFTTUTTLE | 3000 | — | — | — | NO DATA: SWIFTTUTTLE 2034-05-04 |
| SWIFTTUTTLE | 5000 | — | — | — | NO DATA: SWIFTTUTTLE 2039-10-25 |
| SWIFTTUTTLE | 8000 | — | — | — | NO DATA: SWIFTTUTTLE 2048-01-11 |
| TITANIA | 1400 | 38.39863858088452 | 1305.0 | 20.263334448501205 | PRICED_EXISTING_2026 |
| TITANIA | 3000 | 0.8649662027318891 | 2967.0 | 6.078028292088739 | PRICED_NEW |
| TITANIA | 5000 | — | — | — | NO DATA: URANUS 2039-10-25 |
| TITANIA | 8000 | — | — | — | NO DATA: URANUS 2048-01-11 |
| TRITON | 1400 | 46413.558897984664 | 1400.0 | 31.92918092120751 | PRICED_EXISTING_2026 |
| TRITON | 3000 | 1.6321948322056522 | 3000.0 | 11.887396143333733 | PRICED_NEW |
| TRITON | 5000 | — | — | — | NO DATA: NEPTUNE 2039-10-25 |
| TRITON | 8000 | — | — | — | NO DATA: NEPTUNE 2048-01-11 |
| UMBRIEL | 1400 | 42.54870973230616 | 1272.5 | 20.26657207304608 | PRICED_EXISTING_2026 |
| UMBRIEL | 3000 | 0.8540041777896454 | 2967.0 | 5.893424857957794 | PRICED_NEW |
| UMBRIEL | 5000 | — | — | — | NO DATA: URANUS 2039-10-25 |
| UMBRIEL | 8000 | — | — | — | NO DATA: URANUS 2048-01-11 |
| VARUNA | 1400 | 113462389221.14295 | 1400.0 | 53.7775094 | PRICED_EXISTING_2026 |
| VARUNA | 3000 | — | — | — | NO DATA: VARUNA 2034-05-04 |
| VARUNA | 5000 | — | — | — | NO DATA: VARUNA 2039-10-25 |
| VARUNA | 8000 | — | — | — | NO DATA: VARUNA 2048-01-11 |

## Below 20 model units

| Body | First limit priced below 20 | Price (model units) |
|---|---:|---:|
| CHIRON | 1400 | 18.67059879597077 |
| MIRANDA | 3000 | 0.8520693987502494 |
| NEREID | 3000 | 2.9056242727543764 |
| PROTEUS | 3000 | 1.3516260263376758 |
| TITANIA | 3000 | 0.8649662027318891 |
| TRITON | 3000 | 1.6321948322056522 |
| UMBRIEL | 3000 | 0.8540041777896454 |

The first six Uranus/Neptune moon rows to cross below 20 are at 3,000 days. CHIRON was already below 20 at 1,400 days. No conclusion is possible for bodies with NO DATA at longer limits.

## Position provenance and independent checks

- No new position tables were built. Therefore no new-table independent comparison was performed: **NOT APPLICABLE**, not a fresh PASS.
- The 3,000-day pricing uses the existing 2035 numeric tables for EARTH and relevant outer planets. Their existing manifest reports 14,425 validation and epoch-roundtrip samples per planet; source SHA-256 and table SHA-256 were checked before lookup.
- Existing recovered 34-body tables end 2031-10-31; existing numeric nine-planet tables end 2035-12-31. The 5,000-day requirement from 2026-02-15 reaches 2039-10-25; 8,000 reaches 2048-01-11.
- A separate text-only asset inventory covers 477 kernel/position-table files under `/home/ubuntu/loom_solar_assets` and `/home/ubuntu/LOOM-output`. File paths, byte sizes, and SHA-256 are recorded in `VM_KERNEL_POSITION_MANIFEST.txt`. No binary assets are committed.
- Manifest SHA-256: `861dfc04d3cbacf63d1fa9bcb9aa92d1915f0565fba449f917fc2261cc5ed454`.

## Controls

- Route 1 replay control: **PASS** `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430`.
- Floor: **PASS** for all priced rows.
- Retry rules: unchanged; no campaign executed.
- Database SHA-256 before and after: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- No downloads, installations, or edits to pre-existing files.
