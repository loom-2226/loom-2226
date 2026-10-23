# PR427 paired replay validation (TEST_ONLY, NON-CANON)

- Python: offworld-runtime-b7 virtual environment, NumPy 2.5.3.
- Replay uses saved 3,731 sampled-departure records; **no trajectory geometry was rerun**.
- Original flyby CSV SHA-256: `2a36b2ef103480c7b8624b86d6910becd69472ad78913ec2ea60141e64643b73`.
- 118/118 flyby body-year minima match original saved flyby geometry minima exactly.
- Recomputed six numeric flyby cost fields for each of 118 rows: **zero string-level differences**.
- Control hash reproduced: `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430`.
- Rendezvous replay matches original funded stages (114), bodies (43), model units spent (75.8627822051335949), and all blocker counts.
- Rendezvous stable projection hash **does not match** the original: original `c7fc6355ab7e3da436e903b5575f092adcf7dd9d7f76085a014d34b0ad5a1338`; replay `3d94a53fcec4004d1e7600d1d3dc31b6411d800a0c23408e1dac9518bf300450`. Replay passes the literal identity label `A1_RENDEZVOUS` to CostCampaign, rather than the original geometry run identity `6fbdffa97af212acff861d54dc3b408518a7878707d24eaa1dabbaf44ef4e1b4`. That label is present in campaign reporting and therefore affects the stable hash. Do **not** claim bit-identical rendezvous projection.
- Flyby parent pricing is an economic parent-price substitution for moons, **not** a physical moon transfer calculation.
- Historical 31 and 23 sets are distinct reference cohorts and can overlap in interpretation; they are not additive funding counts.
- Frozen paths `simulation/offworld_mvp/phase3b`, `src`, and `data` had clean git status after replay.
- SQLite `data/LOOM_2226.sqlite3` SHA-256 before and after: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- Outputs are non-canon simulation experiments; results are not authority changes.
