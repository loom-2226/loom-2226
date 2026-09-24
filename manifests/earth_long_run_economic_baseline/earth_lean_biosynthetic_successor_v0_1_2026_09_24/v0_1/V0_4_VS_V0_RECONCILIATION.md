# Recovered v0.4 versus v0 reconciliation

Recovered v0.4 central ends near 8.669B; v0 ends at 6.991B. Their 2226 fertility
anchor is the same (`TFR 1.88`, mean age 39, SD 10), so fertility endpoints do
not explain the 1.678B difference.

- **Starting population:** recovered v0.4 records 10.180B at 2100; v0 uses the
  current WPP country/sex files and starts at 10.187B. The +6.45M v0 difference
  has the wrong sign and is negligible.
- **Medical timing and efficacy:** moving from exact v0 medicine to the bounded
  high case adds 473.8M people by 2226. This explains about 28% of the endpoint
  gap, while showing that v0 is meaningfully sensitive to medicine.
- **Mortality baseline:** v0 calibrates country mortality to WPP 2100 deaths and
  derives age/sex survival from WPP 2095→2100. Its 2226 deaths are 87.16M versus
  82.35M in recovered v0.4. This persistent survival difference is the dominant
  evidenced source of the remaining gap.
- **Cohort implementation:** v0 uses country × sex × five-year WPP shares. The
  recovered record describes v0.4's 2100 structure as a constrained, uniform
  within-band reconstruction without sex disaggregation. That changes exposure
  to age-specific fertility and mortality, but the archived summary does not
  support a unique numerical decomposition.
- **Fertility implementation:** v0 uses a normalized two-sex five-year fertility
  kernel. It yields 70.05M births in 2226 versus 78.50M in v0.4. The recovered
  record also notes an approximately 1% CBR calibration residual and parent-age
  tail limitation. Annual v0.4 ledgers/code are unavailable here, so its
  cumulative contribution cannot be isolated without inventing precision.

The defensible conclusion is that the difference is mostly mortality/cohort
semantics, with medical timing explaining a material minority and the starting
total explaining virtually none. The bounded pass does not retrofit v0 to v0.4.
