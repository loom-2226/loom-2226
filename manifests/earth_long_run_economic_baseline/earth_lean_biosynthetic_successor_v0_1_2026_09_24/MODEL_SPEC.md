# Model specification

## Biological demography

The 2100 state is UN WPP 2024 Medium, country × sex × five-year age group.
Annual propagation uses a uniform-within-bin five-year cohort transition. Female
births are distributed by a normalized Gaussian fertility kernel using the saved
LOOM TFR, mean-age, and standard-deviation anchors. Fertility anchors are linearly
interpolated by year.

The baseline age/sex mortality shape is recovered from WPP world 2095→2100
cohort survival. Country scaling uses WPP 2100 life expectancy. A scalar then
reconciles each country's modeled 2100 deaths to its WPP 2100 death total.
Post-2100 medical access modifies age-specific mortality; it does not multiply
population. Biological migration is zero.

## Labor

Biological effective labor is the cohort sum of population × functional health ×
participation × paid-hours weight. Children under 20 contribute zero. Healthy
older adults remain eligible under declining schedules. Country factors are
calibrated at 2100 against the v4 boundary, subject to the hard constraint that
labor cannot exceed health-capable persons.

The v4 boundary violates that constraint for ARE: v4 employment is 20,011,174
while health-capable biological population is 17,909,350. The candidate caps ARE
at capability and records the repair. It does not create synthetic persons to
fill the difference.

## Synthetic persons and machine tasks

Synthetic persons obey a stock equation with explicit additions, losses, and
zero net migration. Synthetic labor is stock × participation × effective labor
per participant. Non-person machine tasks are a separate capacity state driven
by the inherited v4 automation-enabling capital index. Neither category is used
as an economic target-closing residual.

## Economic coupling

The v4 trajectory is reproduced exactly through 2100 from its governed 2060
checkpoint. The resulting 2100 country, sector, and asset rows match the promoted
v4 artifacts exactly. At the handoff, sector production `A` is rebased once so
that the selected biological plus synthetic labor composition reproduces the
existing 2100 sector value added exactly. Capital, investment, assets, TFP,
sector allocation, and trade state are retained.

For 2101–2226 the existing v4 engine advances capital accumulation, replacement
and expansion investment, sector and asset structure, TFP catch-up, and trade
topology. The only replaced interface is labor. No 2226 GDP or value-added row is
rescaled.
