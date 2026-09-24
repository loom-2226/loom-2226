# Demographic and economic consistency

Independent validation is `PASS`.

- 127 annual states cover 2100–2226 without gaps.
- All 237 demographic identities are unique at 2226.
- All 80 qualified economies are unique in every economic year.
- Biological cohort stocks reconcile with births and deaths.
- Synthetic stocks reconcile with additions, losses, and zero migration.
- Labor composition reconstructs exactly.
- Biological labor never exceeds persons or health-capable population.
- Production equations and capital stock-flow identities have zero reported
  relative residual.
- Maximum country/sector reconciliation residual is `6.73e-16`.
- Maximum sector/asset reconciliation residual is `2.78e-16`.
- Maximum absolute annual country VA growth is 2.371%.
- The exact v4 2100 boundary value added is preserved.

Focused model tests: 8 passed. Independent artifact validator: 1 pass with no
failed checks. The source v4 baseline and promoted demographic bridge remain
read-only.

Two full generations were compared. Eight primary demographic artifacts and ten
primary economic artifacts were byte-identical. Reports containing absolute
output paths were excluded from the byte comparison.
