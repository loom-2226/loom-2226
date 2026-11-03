# Wayfarer Window Standard WWS-1 (PROPOSED)

ALL bodies. ALL sponsors. 2026–2226.

**Status:** DRAFT / NON-CANON / NON-QUALIFICATION. kT approved window-standard direction on 2026-11-03. Stacked on Wayfarer shuttle integration #460.

## Purpose

Maximise the lived experience of space on a ship occupied for years while preserving the ability to become a genuinely closed, shielded vessel. Every window, including the crown, is closed under the same doctrine. The L4 storm shelter has ZERO windows.

## WWS-1 stack, outside to inside

1. Replaceable ceramic bumper tile, 10 mm, 3750 kg/m³: **37.5 kg/m²**. Non-pressure tile, externally serviceable without depressurising the cabin.
2. Transparent ceramic primary pressure pane, 28 mm, 3750 kg/m³: **105 kg/m²**; independently holds 101.3 kPa differential.
3. AOI-2226 optogel between pressure panes: crown reference mass **3000 kg / 45.037125 m² = 66.611712 kg/m²**. Clear/glare/dark, independently modulated visible/NIR, gel/locked. Not a pressure seal, shield, qualified impact damper or proved heat barrier.
4. Independent backup transparent pressure ceramic, 28 mm, 3750 kg/m³: **105 kg/m²**; independently holds full cabin differential after failure of primary, including with gel present.
5. Strata closing shutter, **27 g/cm² = 270 kg/m²**. Closed, restores local armour areal mass; no open-shutter radiation protection credited.

The numbers above are calculated from the existing crown fields in 'wayfarer/config/wayfarer_v05_inputs.json' (crown_dome.panes, i4_crown_option_B, adaptive_optogel). No substituted external or Claude areal estimate.

## Derived areal budget

| Component | kg/m² |
|---|---:|
| Bumper | 37.500000 |
| Primary pane | 105.000000 |
| AOI-2226 nominal projected column | 66.611712 |
| Independent backup pane | 105.000000 |
| Strata closed shutter | 270.000000 |
| **Gross physical stack** | **584.111712** |
| Less locally replaced armour, 27 g/cm² | −270.000000 |
| Less locally replaced hull, 8 g/cm² | −80.000000 |
| **Net stack** | **234.111712** |

**0.584111712 t/m² gross; 0.234111712 t/m² net** (bare material proxy). Actual installed assemblies also require frames, seals, actuators, mount and load-path reinforcement. Existing band frames and per-port structure allocations are accounted separately by the budget plan. The old hull/armour cannot be counted once as removed and a second time as added hardware.

The closed stack excluding AOI has 3.75 + 10.5 + 10.5 + 27 = **51.75 g/cm²**. Comparator armour plus hull is **35 g/cm²**, or **43 g/cm²** when conservatively adding a berth's 8 g/cm² water insert. This is areal screening only, NOT particle transport/dose or impact/seal proof. AOI receives ZERO shielding and optical/heat credit.

## Doctrine

**Close** for torch burns, Metric/Loom formation or translation, radiation events, dust/speed above crown open limits, or loss of heat pumping. **Open** deliberately for crew viewing only when those restrictions allow. Treat all open glazing as fully sunlit at the worst G4 solar flux; credit zero AOI NIR/glare switching benefit. A shutter stuck open is an operational hold, not a shielded state. Stuck closed is survivable.

The 208 Metric faces must be shown as flush armour-colour covered discs, never dark holes. No window may occupy a face. PR #184 face coordinates remain HOLD and are not moved here.

## Explicit open items

2226 ceramic manufacturing, local cutout frames, pressure pane failure independence, gel crack/shock coupling, seals, thermal cycles and fatigue, per-aperture g/cm² and dose transport, retractable Strata closure behaviour, and genuine worst-sun surface temperatures remain OPEN. This habitat pressure/vacuum standard is **not** a 92-bar shuttle-pod port qualification.

See 'wayfarer/docs/WINDOW_PLAN_WWS1.md' for placement, mass ledger, node-face conflicts and certification evidence. No criterion relaxed.
