# PR #427 2035 time-lattice discriminator and numeric rebuild

CLASS: TEST_ONLY / NON-CANON / NON-RUNTIME.

- UTC lattice: 2026-02-15T00:00:00Z through 2035-12-31T00:00:00Z, 0.25-day ticks, 14,425 epochs.
- Pinned LSK `naif0012.tls` SHA-256: `678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b`.
- Text `str2et` versus numeric UTC seconds + `deltet`: maximum absolute difference `2.384185791015625e-7 s` = `2^-22 s` = one ULP at these ET magnitudes; 1,660/14,425 ticks differed bitwise.
- Numeric ET `et2utc(..., 'ISOC', 0)` exactly reproduced the intended tick strings at all 14,425 epochs: zero failures.
- Accuracy discriminator: **PASS** under the agreed <=1 ULP rule, although not bitwise equal. The previously computed Mars/Pluto/Neptune pilot is no longer provisional on epoch-accuracy grounds. Maximum epoch displacement corresponds to approximately 7 mm at 30 km/s; this is a scale illustration, not a measured orbit-position residual.
- Numeric-path rebuild motivation: identical ET keys for exact-ET table joins/lookups, not improvement of astronomical accuracy.
- Numeric rebuild: all nine pinned planetary/Pluto tables complete, 14,425 rows x 6 state columns each, bitwise direct-SPICE validation at every ET. Earth/Mercury/Venus resumed after full verification; Mars/Jupiter/Saturn/Uranus/Neptune/Pluto created via fsync-and-rename. Separate output directory, originals preserved.
- Numeric manifest SHA-256: `1a1b3686cf76b985f006a652e1833e2708da847bf560059b55d47ee722cffcb7`.
- Detached rebuild exit status: 0; elapsed 75.3695 s; peak RSS 1,309,507,584 bytes. Log and exit file reside beside the numeric tables.
- Accepted assumption: no additional leap seconds after the last entry in the pinned LSK through 2035.
- Independent Astropy UTC->TDB oracle: **NOT RUN**; Astropy absent from existing interpreter, and no new environment or install was authorized.
- Still open: shared UTC->ET lattice function, migration of all table builders to that function, CI prohibition of `str2et` in table builders, and lattice-equality test. These require separate changes to existing builders/CI paths, outside the present new-files-only scope.
- Recovered small-body kernels remain excluded beyond their 2031-12-31 qualification window. No full 63-body run performed.
