# Wayfarer crown and WWS-1 true-solid mass discrepancies, REPORT ONLY

ALL bodies. ALL sponsors. 2026–2226.

**Scope:** PR #475 / proposed canon v2.5.1 glazing-view geometry. **This is a separate engineering discrepancy note, not a mass-ledger change, not a new design decision, not hardware qualification.**

- Governing `canon-v2.5` source geometry SHA256: `88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1`.
- Booked v2.5 dry mass: **868.192255264 t**. No v2.5 source mass entry, dry ledger, G1 inventory, or certified velocity has been edited.
- Original ECON Δv: **707.845455 km/s** (display **707.845**). This remains the booked/declared value, **not** a measured new physical mass-model reach after cutouts.
- The CAD render replaces `no_render` source allocations by true solids for viewing. Do **not** add their geometric masses to the already-booked allocations.

## Measured candidate discrepancies, not charged

1. **Brow-seat material model:** the full nominal 1 m radial × 0.22 m axial annular *solid* has measured BRep volume **5.529203070 m³**, equivalent to **24.494369602 t** if fully solid titanium at the screen's 4.43 t/m³ nominal alloy density. The source's frame/seat allocation does **not** describe a solid titanium block; this is a real geometric-material mismatch in that *candidate representation*, **not proof of an overweight engineered frame**. Physical Osteon member sections are unspecified; do not infer a new mass or redesign an approved frame to make the number match.
2. **Existing outer spares:** seven BRep pane volumes at source ceramic density imply **0.373367100 t**, against **0.385772 t booked**, difference **−0.012404900 t**. Use kT's first screened forward lower bay-wall rack for the visual placement. Keep the source booking unchanged.
3. **Crown AOI volume:** true candidate BRep cavity **2.488661198 m³**, against source allocated **3.023000000 m³**, difference **−0.534338802 m³**. At its booked effective density, the unfilled difference is **approximately 0.537523 t**; **3.04101485 t remains booked**. Fit/fill is not physically closed.
4. **Crown pressure-vessel/armour displacement before WWS side cutouts:** original measured PV cut **1.492234857 m³**, armour **9.642552212 m³**, totaling **14.797317964 t equivalent** at *legacy effective* bookkeeping densities. This quantity is **not a debit** under the required mass-neutral drawing instruction; a physical replacement mass reconciliation is outstanding.
5. **Previously published physical-material sensitivity:** `wayfarer/results/out/crown_solid_mass_modes_screen.json` reports option A a **+21.351478426 t** dry difference and ECON **693.542241 km/s** (−14.303215), **if** all existing crown proxies and cut hull material were retired and replaced with this candidate's volumetric material estimates. This is a non-governing *screen*, dominated by modeling unsupported solid-frame/track assumptions. **Do not substitute these values for canon.**

## Scope and status boundary

WWS-1's **21** round ports and **five** L2 band sectors are source-booked, including restoration with **zero L4 storm-shelter windows**. No AOI optical/cooling or radiation transport credit is created by visual panes. G1–G12 on unchanged source can remain green while newly rendered cut-shell material, pressure interfaces and local shielding still require appropriate evidence. A visually complete scene is **not** a hardware or source-geometry recertification.

If the combined candidate D9 all-pair geometry scan or per-part exports fail, report the failure explicitly. If they pass, report those results as **candidate geometry only**. **No merge and no invented mass correction.**
