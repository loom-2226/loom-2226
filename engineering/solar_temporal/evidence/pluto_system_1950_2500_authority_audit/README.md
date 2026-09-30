# Pluto system 1950–2500 authority-gate evidence

This evidence records the fail-closed authority audit performed before attempting a 1950–2500 continuous-function compilation for Pluto, Charon, Styx, Nix, Kerberos, and Hydra.

Result: no requested body demonstrated governed coverage at all required probe epochs, so compilation correctly did not run and no viewer state was fabricated.

Follow-up inventory established:

- local DE440 asset exists at `kernels/spk/de440.bsp` (119,799,808 bytes);
- local PLU060 exists at `kernels/spk/phase4b/plu060.bsp` (135,207,936 bytes), SHA-256 `dfbb102491a26ed41ae08ca3f8963f22f0219df1d8f265ab87b9ad825a826fc6`;
- native governed PLU060 coverage is ET `-6311304000.0` through `6311217600.0`, approximately 1800-01-01 through 2199-12-29, for Pluto, Charon, Styx, Nix, Kerberos, and Hydra;
- Pluto and Charon additionally have qualified LOOM propagated coverage from ET `6311217600.0` through `7920763270.0`, ending 2251-01-01;
- Styx, Nix, Kerberos, and Hydra have no qualified continuation after native PLU060 coverage in the current authority ledger;
- DE440 supplies `PLUTO_SYSTEM_BARYCENTER` in the governed architecture but does not by itself provide individual Pluto-system satellite states.

This is an authority/coverage finding, not a failure of the Chebyshev state-function compiler. Any 1950–2500 Pluto-system campaign requires a separately governed long-horizon satellite model or explicit propagated/estimated continuation with provenance and uncertainty.
