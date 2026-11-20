# Shuttle v3, step 2: propulsion and power (screen)
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON engineering screen for kT. Script `step2_propulsion.py` → `step2_propulsion.json`, picture `step2_propulsion.png`. Mission targets R1–R8 as proposed (kT "Go step 2", 2026-11-20).

## Findings

1. **Earth sea-to-orbit closes on the 23.1 t tank** with the 7.7 GW torch: 18.0 t for the whole sortie (40 t dry, 6 pax + 2 t, 50 km/s top exhaust speed); 14.7–23.0 t over 36.5–45 t dry at 50 km/s. It does **not** close if the top exhaust speed is only 25 km/s and dry reaches 45 t (31.5 t). Liftoff ≈ 60 t, ~800 kN, exhaust ~19 km/s.
2. **Keep 7.7 GW.** A bigger torch saves water but adds engine mass about one for one (dry + water 57–58 t from 7.7 to 12 GW, worse above).
3. **Venus sizes the water, not Earth:** 30 t (26–47 t) because the kit adds 15 t. Under decision 5 the Venus kit carries its own extra water (~8–13 t mid). Titan, Mars, Moon and Europa need 2–13 t.
4. **Radiation is the hard one.** Scaled from the Wayfarer torch model, an ordinary pulse shell leaks ~10 MW of neutrons: lethal at the cabin in seconds. In air a shadow shield doesn't save you, because neutrons scatter round it (mean free path ~100 m at sea level). The fix is physics we already have: the shuttle's low exhaust speed means a lot of remass per pulse, so the shell around each pulse can be **thick enough to be the shield**. Conservative case: **≥ 55 kg per pulse (~600 g/cm² compressed)** → ≈1 mSv to the cabin over a 15-min ascent with no shadow shield. That sets ~0.7 Hz at full power in air (ve ~20 km/s).
5. **Heat:** burn heat leaves with the exhaust; the ~1 MW that stays (Wayfarer S4 ratio) warms the water tank a few kelvin per burn. No burn radiators. Surface-stay radiators are step 5.

## Constraints added (P-series)

| Id | Class | Constraint |
|---|---|---|
| P1 | CANDIDATE | Torch 7.7 GW jet, exhaust 10–50 km/s variable, engine ~7 t |
| P2 | HARD (physics) | Torch must light in sea-level air for Earth sea-to-orbit; nothing else closes on carried water (H2/O2 at 4.2 km/s needs a mass ratio ~9) |
| P3 | HARD (physics) | Atmosphere mode: pulse shell ≥ 55 kg (conservative), ve ≤ ~20 km/s, ~0.7 Hz. Vacuum mode may thin the shell behind a shadow shield of protected water |
| P4 | HARD (design) | Shell dopant boron, not lithium: lithium-6 capture makes tritium in the exhaust |
| P5 | POLICY (kT) | Torch liftoff is a rocket-launch event (7.7 GW ≈ 0.7 × a Falcon 9 liftoff jet power, pulsed): km-scale exclusion zone. "Leave anywhere" = taxi or hop clear, then light |
| P6 | HARD (physics) | Docked water 23.1 t core tank; Venus kit adds its own tank |
| P7 | kT-settled | Belly thrusters and RCS: H2/O2 (stage 3 baseline, electrolysed on Wayfarer). Earth and Titan landings glide and float (no propellant); Moon, Mars, icy moons: torch braking, belly for the last ~100 m |

## Open, carried forward
Exhaust tritium from D-D side reactions per Earth ascent; per-pulse shock loads at high ve (55 kg × 50 km/s every ~9 s needs a shock absorber); magnetic-nozzle behaviour at 1 bar (2226 capability claim); bystander dose map.
