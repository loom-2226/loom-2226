# Full-clock 8,000-day destination extension: checkpoint

Classification: TEST_ONLY / NON-CANON. **Not completed or qualified.**

Required position horizon: 2026-01-01 through **2248-11-25** (8,000 days after 2226-12-31).

Registry-only screening covered all 90 bodies: 83 have a qualified source registered at both endpoints; seven have an endpoint gap. Endpoint presence is **not** proof of continuous SPK object coverage, kernel integrity, numerical correctness, or an independently qualified table.

Endpoint registry gaps:
- DACTYL: no qualified source at start or end.
- SELAM: no qualified source at start or end.
- HYDRA, KERBEROS, NIX, PROTEUS, STYX: no qualified source at the required end date.

These bodies require existing-kernel coverage evidence, a different qualified kernel already on the VM, or, if unavailable, an explicitly authorized download (not undertaken). No ephemerides may be fabricated.

The initial stronger kernel/SPICE check was interrupted after 18 bodies. It revealed source-switching at the endpoints and a SHA-256 mismatch for at least DAVIDA and ARROKOTH. It also encountered an unparsed SPICE time and was killed under resource pressure. These are unresolved and **not** independent check passes. See `coverage_partial.json` and `coverage_retry.log`.

No new position table has been built or passed the independent oracle. Therefore steps 2–4 cannot yet produce scientifically valid full-sweep results. No repricing or campaign was run in this checkpoint.

Route 1 control was not rerun here; previous PR427 control result must not be presented as a fresh run. Database read-only and no pre-existing file intentionally edited by this job.
