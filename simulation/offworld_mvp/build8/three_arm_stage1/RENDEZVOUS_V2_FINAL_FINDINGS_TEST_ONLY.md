# Rendezvous V2 final findings (TEST_ONLY, NON-CANON)

Saved evidence audit: COMPLETED. Eight saved input/output SHA-256 values independently rechecked against local bytes. No geometry rerun.

Geometry: 3731 departure samples, 10891908 trajectories; 132 priced / 48 unpriced of 180 body-years; zero departure-lattice mismatches.
Evaluation paths excluding hand tests: 11812731 float and 107735 Decimal60. Counters include additional stage calls and do not equal unique geometry trajectories.
Lowest recorded overflow: {'arrival_vinf_km_s': 445.7804017, 'body': 'ARROKOTH', 'departure_vinf_km_s': 446.8774816, 'flight_days': 163.25, 'year': 2026}. Synthetic 2000 km/s arrival: float overflow; finite Decimal mass 1.24723279292575059785440512531892447705091502838487391716102E+620 kg.
Independent float bitwise checks: 132; independent Decimal winning-quote checks: 0.
Control SHA-256: 4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430.
Route 1: 114 stages; 43 bodies; 75.8627822051335949 USD-billion model units; 180278 blocked attempts ({'ACTUAL_SPONSOR_CASH': 88453, 'FINANCIER_CONCENTRATION': 145, 'UNPRICED_NO_PARENT_QUOTE_OR_PHYSICAL_PARAMETER': 91680}).
Elapsed 704.289 s; geometry 664.327 s; peak RSS 764649472 bytes.

## Previously unfunded 31 bodies

| Body | Funded | First year | Sponsor | Cost (USD billions) | Unfunded reason |
|---|---|---|---|---|---|
| ARIEL | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| CALLISTO | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| CHARON | NO |  |  |  | Not funded; no specific reason recorded |
| DACTYL | NO |  |  |  | PARENT_GM_MISSING |
| DEIMOS | YES | 2036 | JAXA | 0.7068700388855866 | Not funded; no specific reason recorded |
| DIONE | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| ENCELADUS | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| EUROPA | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| GANYMEDE | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| HYDRA | NO |  |  |  | Not funded; no specific reason recorded |
| HYPERION | NO |  |  |  | NO_59_BODY_TABLE_QUOTE |
| IAPETUS | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| IO | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| KERBEROS | NO |  |  |  | Not funded; no specific reason recorded |
| MIMAS | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| MIRANDA | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| MOON | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| NEREID | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| NIX | NO |  |  |  | Not funded; no specific reason recorded |
| OBERON | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| PHOBOS | YES | 2036 | LandSpace | 0.7068327485786549 | Not funded; no specific reason recorded |
| PHOEBE | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| PROTEUS | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| RHEA | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| SELAM | NO |  |  |  | PARENT_GM_MISSING |
| STYX | NO |  |  |  | Not funded; no specific reason recorded |
| TETHYS | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| TITAN | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| TITANIA | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| TRITON | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |
| UMBRIEL | NO |  |  |  | PARENT_NO_FLYBY_QUOTE |

## Limitations

- Audit verifies saved hashes and 132 independently compared float-winning quotes, not all 11.8 million float evaluations individually.
- No independently recomputed Decimal-winning quote was recorded. Decimal fallback is tested synthetically, but full Decimal numerical accuracy is not independently certified.
- The 31-body first-funding report is derived from the saved Route 1 JSON, not a new simulation.
- Missing parent quotes and physical parameters remain UNPRICED; no substitutes invented.
- This is a test-only, non-canon experiment, not a propulsion or economic forecast.
