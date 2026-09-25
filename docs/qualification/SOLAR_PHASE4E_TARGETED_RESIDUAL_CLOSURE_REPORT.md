# Solar Phase 4E — targeted residual closure

The merged Phase 4E ledger contained exactly 12 residuals: seven natural
satellites and five spacecraft. No additional cohort member was introduced.

Closure result:

- Pioneer 10, Pioneer 11, Voyager 1, Voyager 2: explicit empirical extensions
  from official mission SPKs through `2251-01-01T00:00:00Z`.
- New Horizons: official PDS/NAIF `nh_pred_alleph_od164.bsp` direct coverage
  through `2033-01-01T11:58:51Z`, then explicit empirical extension through
  `2251-01-01T00:00:00Z`.
- Nix, Hydra, Kerberos and Styx: still partial under PLU060, whose actual
  object-level coverage ends `2199-12-29T23:58:50.816Z`. The available NAIF
  archive and Horizons support did not provide a later independent solution.
- Proteus: catalog-only. `nep101xl`, `nep104` and `nep105` do not contain NAIF
  808; Horizons provides satellite orbital metadata but no independent SPK
  suitable for governed 2250 state authority.
- Dactyl and Selam: catalog-only. Targeted Horizons/NAIF/PDS searches found no
  independent authoritative state product or sufficiently constrained orbit
  solution for defensible 2250 propagation. They remain explicit companions of
  Ida and Dinkinesh respectively.

Propagation uses the existing Solar RK4 architecture with ECLIPJ2000,
km/km/s, solar gravity, differential DE440 planetary perturbations, and a
pinned 86400-second step. All derived states are uncertainty-bearing and
`navigation_grade=false`.

Held-out validation is recorded in
`SOLAR_PHASE4E_TARGETED_RESIDUAL_PROPAGATION_VALIDATION.json`. Voyager and New
Horizons remain comparatively bounded over their available withheld intervals;
Pioneer errors are multi-billion-kilometre scale, so their declared uncertainty
is conservatively `1e12 km` and the result must not be read as navigation
authority.
