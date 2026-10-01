# Phase 4F estimated-relative closure

Status: governed low-authority state products. These are not direct ephemerides and not validated physical propagation.

The purpose is to provide explicit nominal game/visualization states where no defensible direct 2226–2250 ephemeris exists, while preserving uncertainty large enough to prevent precision interpretation.

## Proteus

Direct authority remains JPL/NAIF NEP098 through 2199. Current JPL satellite tables continue to associate Proteus (808) with the inner-Neptune solution family and publish mean orbital geometry/period, while warning that mean elements are not intended for ephemeris computation. The Phase-4F product therefore anchors continuously to the final direct NEP098 state and advances a nominal circular relative orbit using the published 1.122315-day mean period. Declared uncertainty is one nominal orbital diameter (~235,527 km).

Research:
- https://ssd.jpl.nasa.gov/sats/elem/
- https://ssd.jpl.nasa.gov/sats/ephem/
- https://nssdc.gsfc.nasa.gov/planetary/factsheet/neptuniansatfact.html

## Dactyl

No accepted independent long-horizon SPK target exists. Galileo-era NASA material establishes Dactyl as Ida's satellite at roughly 90 km observed separation; historical period estimates are approximate. The game-epoch phase is not treated as known. The nominal relative product uses a LOOM synthetic SPK target ID, never a NAIF identity, with 180 km declared positional uncertainty.

Research:
- https://www.jpl.nasa.gov/images/pia00298-dactyl-dark-side-illuminated-by-idashine/
- https://ntrs.nasa.gov/citations/19950042090

## Selam

NASA Lucy observations establish Selam as Dinkinesh's contact-binary satellite, with mission material giving approximately 3.1 km separation and a ~53-hour synchronous orbit. No game-epoch phase authority is claimed. The nominal product uses a LOOM synthetic SPK target ID with 6.2 km declared positional uncertainty.

Research:
- https://science.nasa.gov/solar-system/asteroids/dinkinesh/
- https://soma.larc.nasa.gov/stp/dynamic/pdf_files/DYNAMIC_PI-Led_Team_Masters_Forum_3_PI_Lessons_Learned_2.pdf

At 2226-01-01 TDB, the governed Inspector resolves 106/110 objects: 90 DIRECT, 13 PROPAGATED, 3 ESTIMATED_RELATIVE, 4 unresolved Pluto small moons pending the separately validated six-body continuation.
