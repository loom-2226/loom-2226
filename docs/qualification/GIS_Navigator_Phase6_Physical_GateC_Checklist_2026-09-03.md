# GIS/Navigator Phase-6 Physical Gate-C Checklist — 2026-09-03

Status: OPEN pending Pixel completion.

## Already physically observed

- Mars -> Ceres discovery succeeded in Termux-hosted Pixel GIS.
- HARD/CRUISE candidate rendered authoritative duration and remass; inapplicable holonomy/confidence rendered as em dash.
- Commit did not mutate campaign location.
- Execute arrived at CERES and advanced campaign to REV 3.
- Execute control returned to disabled/no-committed-route state.

## Remaining physical acceptance

1. Reload corrected live-vehicle-state renderer against existing CERES / REV 3 state. Do not create another flight.
2. Confirm live ship marker is at CERES and is not derived from historical Mars departure state.
3. Confirm historical Mars -> Ceres route/anchors remain available without fabricating sampled trajectory geometry.
4. Issue one duplicate execute request with no committed route and confirm HTTP 400/rejection.
5. Confirm location remains CERES, revision remains 3, remass unchanged, and no second FLIGHT_ARRIVED event exists.
6. Run same-head regression stack green.

Phase 7 remains blocked until all items above pass.
