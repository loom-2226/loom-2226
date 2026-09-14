# E1 Neptune continuous atmosphere-profile feasibility v0.1

**Classification:** engineering research / source feasibility audit only  
**Canon:** NON-CANON  
**Runtime authority:** ZERO  
**Campaign mutation:** NONE

## Question

Do the currently identified authoritative Voyager/NASA/PDS sources earn a reproducible continuous historical Neptune pressure/temperature profile that LOOM can encode without inventing data?

## Result

**NO — not from the currently located source set.**

The literature establishes that Voyager 2 radio-occultation analysis produced vertical atmospheric profiles. Lindal et al. (1990) describes vertical temperature and composition profiles over approximately 250 km. Lindal (1992) describes Neptune vertical structure from radio occultation measurements spanning an approximately 5000 km measurement interval and supplies specific reference values including the 1-bar and tropopause anchors already qualified separately.

However, this audit did **not** locate an authoritative reduced Neptune table containing the continuous pressure/temperature profile in a form that can be reproduced directly inside LOOM. NASA/PDS exposes Neptune archive lineage and Voyager RSS references, but the searchable reduced radio-occultation table product located during this audit is for **Triton**, not Neptune.

## Hard boundary

`PUBLISHED_CONTINUOUS_PROFILE_EXISTS != REPRODUCIBLE_TABULATED_PROFILE_IN_HAND`

Therefore LOOM may **not**:

- digitize a plotted figure and call it source data;
- interpolate between the two qualified anchors and call the result Voyager data;
- extrapolate beyond measured anchors;
- derive a density law from the two anchors alone;
- substitute Triton reduced data for Neptune;
- propagate the 1989 state to 2226 without a separately qualified evolution/model layer.

## Sources reviewed

- Lindal, G. F. (1992), *The atmosphere of Neptune — An analysis of radio occultation data acquired with Voyager 2*, Astronomical Journal 103; NASA NTRS 19920044002.
- Lindal et al. (1990), *The atmosphere of Neptune — Results of radio occultation measurements with the Voyager 2 spacecraft*, Geophysical Research Letters 17; NASA NTRS 19900065496.
- NASA Planetary Data System Neptune Data Archive, including Voyager 2 RSS lineage.
- NASA PDS Voyager 2 Triton Radio Occultation Reduced Data V1.0, reviewed only as a contrast showing what a genuinely archived reduced tabular occultation product looks like.

## Current earned state

LOOM has:

1. body-level Neptune atmosphere classification;
2. navigation-grade Neptune-relative reference geometry;
3. two source-backed historical atmospheric anchors;
4. an explicit negative qualification that a continuous profile is not yet earned.

## Next admissible work

Search for primary/reduced Neptune occultation data not surfaced by the current PDS/NTRS paths. If none is recoverable, any continuous atmosphere representation must be introduced as a **separately qualified physical/model reconstruction** with explicit assumptions, provenance, validity domain, and uncertainty. It must never be labelled direct Voyager profile data.
