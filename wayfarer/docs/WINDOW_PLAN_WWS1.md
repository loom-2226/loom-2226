# Wayfarer WWS-1 window plan, cost, node conflicts (DRAFT)

ALL bodies. ALL sponsors. 2026–2226.

**Basis:** stacked on PR #460, Wayfarer geometry 2f29d3dabc0014050b0a385417974457987f9b607e04a8d68087c5cadd09e6fe. NON-CANON / NON-QUALIFICATION.

## Ordered plan

1. Upgrade the original 22 viewports and the existing L2 band to WWS-1, except close both L4 storm-shelter openings: 20 round windows remain.
2. Preserve **one per berth** (10). Upper tier shifts from x6.45 to x6.70 to clear an existing Metric face, no node moved.
3. Enlarge galley and exercise windows as **full-height (1.6m) segments of the existing L2 panoramic band**, retaining the 1.6m observation section and 0.6m wardroom section. Galley/exercise already had the narrow band; no gratuitous second holes.
4. Enlarge the two medical ports to **0.75m** and move to x9.10m clear of the x10 principal frame and provisional x10.25 node ring. L4 shelter windows are **zero**.

## Every round port (20 total)

| Room / berth | x m | azimuth ° | diameter m | glass m² | WWS mass t¹ | reserve uplift t | nearest axial frame edge m |
|---|---:|---:|---:|---:|---:|---:|---:|
| L1-command | 1.25 | 45.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.500 |
| L1-command | 1.25 | 135.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.500 |
| L1-command | 1.25 | 225.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.500 |
| L1-command | 1.25 | 315.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.500 |
| L4-medical | 9.85 | 187.5 | 0.75 | 0.4418 | 0.1834 | 0.0780 | -0.225 |
| L4-medical | 9.85 | 232.5 | 0.75 | 0.4418 | 0.1834 | 0.0780 | -0.225 |
| L5-suits | 12.45 | 50.0 | 0.45 | 0.1590 | 0.1172 | 0.0318 | 0.225 |
| L5-workshop | 12.45 | 102.5 | 0.45 | 0.1590 | 0.1172 | 0.0318 | 0.225 |
| L5-workshop | 12.45 | 147.5 | 0.45 | 0.1590 | 0.1172 | 0.0318 | 0.225 |
| L5-vestibule | 12.45 | 270.0 | 0.40 | 0.1257 | 0.1094 | 0.0294 | 0.250 |
| L3-CAPT / lower | 7.55 | 15.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.200 |
| L3-CA / lower | 7.55 | 75.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.200 |
| L3-CA / upper | 6.70 | 75.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.450 |
| L3-GUEST / lower | 7.55 | 169.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.200 |
| L3-GUEST / upper | 6.70 | 169.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.450 |
| L3-GUEST / lower | 7.55 | 221.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.200 |
| L3-GUEST / upper | 6.70 | 221.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.450 |
| L3-CB / lower | 7.55 | 259.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.200 |
| L3-CB / upper | 6.70 | 259.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.450 |
| L3-CB / lower | 7.55 | 311.0 | 0.50 | 0.1963 | 0.1260 | 0.0205 | 0.200 |

¹ WWS bare stack net of local replaced armour/hull plus retained existing window mounting/frame allowance; only uplift above existing booked legacy hardware draws released structural allocation. Local frame loads, large pane pressure and shutter proof OPEN. The two removed storm-shelter frames total 0.16t and are reused as shell restoration: no free credit.

## L2 WWS band

| Area | X range m | angles ° | glazed m² |
|---|---|---|---:|
| Galley | 3.60–5.20 | 300.0–360.0 | 7.2047 |
| Galley | 3.60–5.20 | 0.0–30.0 | 3.6024 |
| Wardroom | 3.90–4.50 | 30.0–150.0 | 5.4035 |
| Observation | 3.60–5.20 | 150.0–210.0 | 7.2047 |
| Exercise | 3.60–5.20 | 210.0–270.0 | 7.2047 |

Original band area 19.360 m²; new 30.620056 m². New complete net-stack + retained/scaled frame model 10.731307 t; previously booked band 5.867 t; additional draw 4.864307 t.
L2 band crosses original x4m hull frame; G5 existing Osteon load-path is retained and recalculated, while real local cutout/transom fatigue remains OPEN.

## Budget (tonnes)

| Ledger | Before | Draw | After |
|---|---:|---:|---:|
| Engineering reserve | 9.163470 | 0.000000 | 9.163470 |
| Released structural allocation, zero radiation credit | 19.657000 | 5.432216 | 14.224784 |
| **Combined uncommitted** | **28.820470** | **5.432216** | **23.388254** |

Window retrofit draw: 4.864307 t L2 band + 0.567909 t round ports = **5.432216 t**, versus **12.0 t** released draw limit and **13.7 t** total ceiling.
Engineering reserve **9.163470 >= 5.0 t** and combined uncommitted **23.388254 >= 15.0 t**. Retired old ledger.venus_kit_t=1.7t was an unbooked annotation, giving **ZERO reclaimed mass**. v1 Venus kit remains 50t payload.

## Metric node and hull frame conflicts

**Window overlaps after plan: 0**. PR #184 remains a face-placement HOLD. Existing 208 nodes unchanged.
The original PR #460 geometry had one window collision: node ring 1, theta 225°, against an upper berth window at x6.45. The *window* moved 0.25m to x6.70, not the node.
- Unchanged node-face hold (not a window conflict): faces_dust_flow_bow_first, 16 faces
- Unchanged node-face hold (not a window conflict): on_bay_door, 12 faces
- Unchanged node-face hold (not a window conflict): on_torch_chain, 80 faces
- Unchanged node-face hold (not a window conflict): overlaps_camera, 1 faces
- Unchanged node-face hold (not a window conflict): overlaps_hold_door, 2 faces
- Unchanged node-face hold (not a window conflict): under_stowed_strake, 20 faces
Round port axial-frame clearances are shown individually above; expanded L2 intentionally bridges x4m frame plane. No window cutout moves a fixed Metric face.

## Shuttle-specific minimal viewports

No shuttle hull windows, cameras only. Three closed-cover pod ports per-seat Ø0.15–0.20m; 92bar external-pressure DESIGN target only. Mass 0.09–0.24t total assumed within existing pod fittings/seals range, not extra core mass; design/buckling/thermal seals still OPEN. See shuttle_wws1_port_inputs.json.

## G1–G12 and render results

**NOT RECERTIFIED:** latest certificate geometry hash does not match new source. Hold all G1–G12 assertions until full execution.

Renders: wayfarer/render/wws1/before_ext_hab_viewports.png versus after_ext_hab_viewports.png, likewise ext_closed and ext_skin. After images count only if generated by current geometry. WWS-1 OPEN glazing and CLOSED armour states required.
**Physical holds:** direct G6 particle/dose and shutter seam transport, AOI independent fracture response, actual per-cutout G5 frame reinforcement, G4 window thermal/dust survival, pod 92bar thick ports. No G1–G12 criteria relaxed.
