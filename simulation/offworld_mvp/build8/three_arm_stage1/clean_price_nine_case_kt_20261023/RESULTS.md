# Clean price: nine-case sponsor refill sensitivity

TEST_ONLY / NON-CANON. All 90 bodies; 20 sponsors; 2026–2226. Rendezvous, high buyer budget, four-sale cap. No existing source files edited.

Clean price SHA-256: `49fbd0f1015268d24e931b9e1d7083cb8a0cd3f6c02a4942a130d0885695922f`. Strict floor check passes on all campaign-used rendezvous prices; 205 unused below-floor flyby rows are not modified.

## Nine-case results

| Treasury share | Material price | Starts | Sponsors | Bodies | Last start | Committed | Returned | Refilled |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 57 | 20 | 57 | 2139 | 119.4807108013423935 | 9.12000 | 0 |
| 0 | 3 | 57 | 20 | 57 | 2139 | 119.4807108013423935 | 27.36000 | 0 |
| 0 | 10 | 57 | 20 | 57 | 2139 | 119.4807108013423935 | 91.20000 | 0 |
| 0.5 | 1 | 57 | 20 | 57 | 2139 | 119.4807108013423935 | 9.12000 | 3.990000 |
| 0.5 | 3 | 57 | 20 | 57 | 2138 | 119.4807108013423935 | 27.36000 | 11.970000 |
| 0.5 | 10 | 57 | 20 | 57 | 2135 | 119.4807108013423935 | 91.20000 | 39.900000 |
| 1 | 1 | 57 | 20 | 57 | 2138 | 119.4807108013423935 | 9.12000 | 7.98000 |
| 1 | 3 | 57 | 20 | 57 | 2137 | 119.4807108013423935 | 27.36000 | 23.94000 |
| 1 | 10 | 57 | 20 | 57 | 2131 | 119.4807108013423935 | 91.20000 | 79.80000 |

## Previously unstarted 33: first case that starts

Order: treasury share 0, 0.5, 1; within each share material price x1, x3, x10. “NEVER” means no start in any of these nine cases.

| Body | Group | Price (model units) | First case | Start year |
|---|---|---:|---|---:|
| ARROKOTH | earlier outer 24 | 9021850532.03038 | NEVER | — |
| ATLAS3I | earlier outer 24 | 18806254.98086541 | NEVER | — |
| BORISOV | earlier outer 24 | 1.971397548868517E+18 | NEVER | — |
| CHARON | earlier outer 24 | 38263924.680126136 | NEVER | — |
| CHIRON | earlier outer 24 | 18.67059879597077 | NEVER | — |
| COMET_HALLEY | earlier outer 24 | 36908661.171130264 | NEVER | — |
| ERIS | earlier outer 24 | 6.028392693349309E+34 | NEVER | — |
| GONGGONG | earlier outer 24 | 2.309352311713559E+31 | NEVER | — |
| HAUMEA | earlier outer 24 | 25727721638697.34 | NEVER | — |
| HYDRA | earlier outer 24 | 40998324.28823179 | NEVER | — |
| IXION | earlier outer 24 | 626762446.5797112 | NEVER | — |
| KERBEROS | earlier outer 24 | 40795122.84260992 | NEVER | — |
| MAKEMAKE | earlier outer 24 | 7771504290314557 | NEVER | — |
| MS4 | earlier outer 24 | 5958957321423.906 | NEVER | — |
| NIX | earlier outer 24 | 40469065.53304545 | NEVER | — |
| ORCUS | earlier outer 24 | 6766198740267.5 | NEVER | — |
| OUMUAMUA | earlier outer 24 | 1.6743653968179588E+21 | NEVER | — |
| PLUTO | earlier outer 24 | 44669372.4284115 | NEVER | — |
| QUAOAR | earlier outer 24 | 4326292220.68595 | NEVER | — |
| SALACIA | earlier outer 24 | 19430952428802.71 | NEVER | — |
| SEDNA | earlier outer 24 | 1.7750730243491295E+28 | NEVER | — |
| STYX | earlier outer 24 | 40199382.82647385 | NEVER | — |
| SWIFTTUTTLE | earlier outer 24 | 423040047892.73605 | NEVER | — |
| VARUNA | earlier outer 24 | 113462389221.14295 | NEVER | — |
| MIRANDA | six additional moons | 22.30041972032444 | NEVER | — |
| NEREID | six additional moons | 309438.4505641659 | NEVER | — |
| PROTEUS | six additional moons | 13751.150534916129 | NEVER | — |
| TITANIA | six additional moons | 38.39863858088452 | NEVER | — |
| TRITON | six additional moons | 46413.558897984664 | NEVER | — |
| UMBRIEL | six additional moons | 42.54870973230616 | NEVER | — |
| DACTYL | unpriced | UNPRICED | NEVER | — |
| HYPERION | unpriced | UNPRICED | NEVER | — |
| SELAM | unpriced | UNPRICED | NEVER | — |

**Never started in any case: 33 of the original 33.**
Cheapest priced body among them: **CHIRON at 18.67059879597077 model units**.

## Controls

- Route 1 control hash: `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430` PASS.
- Ceres equivalence: PASS (no lifecycle source changed).
- Database SHA-256 before and after: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- Study retry rules unchanged.
- No installs, downloads or pre-existing file edits.
