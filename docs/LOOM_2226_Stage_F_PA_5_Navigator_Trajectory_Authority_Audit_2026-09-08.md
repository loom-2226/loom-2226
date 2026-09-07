# LOOM 2226 — Stage F-PA-5 Navigator / Trajectory Authority Audit

Date: 2026-09-08
Status: **F-PA-5 audit — feature branch / NON-CANON until governed merge**
Parent: `docs/LOOM_2226_Stage_F_PA_Physical_Authority_Audit_2026-09-08.md`

## Scope

This audit maps the current Navigator / Sequence-B trajectory payload into simulator telemetry needs. It does not change trajectory physics, campaign persistence, route selection, endpoint authority, canon, or vehicle engineering constants.

All documentary findings below are from live GitHub artifacts on the governed F-PA feature branch.

## Exact current Sequence-B sample surface

`src/loom/navigation/route_layer.py` promotes 25 sample fields from the decoded Sequence-B timeline:

- sample/time/phase: `sample_index`, `flight_t_s`, `epoch_utc`, `phase_code`, `phase_progress`, `eta_s`;
- semantics: `position_semantics_code`, `relational_progress`, `ordinary_state_kind_code`;
- ordinary 6D state components: `ordinary_pos_x_km`, `ordinary_pos_y_km`, `ordinary_pos_z_km`, `ordinary_vel_x_km_s`, `ordinary_vel_y_km_s`, `ordinary_vel_z_km_s`;
- engineering scalars: `ordinary_speed_km_s`, `ordinary_accel_g`, `target_range_km`, `target_delta_v_km_s`, `metric_beta_current`, `wet_mass_t`, `remass_remaining_t`;
- propulsion/thermal state codes: `metric_state_code`, `torch_state_code`, `thermal_state_code`.

The route adapter explicitly labels the promoted trajectory frame `J2000_ECLIPTIC`.

## Authority-preserving promotion behavior

`src/loom/navigation/trajectory_solution_adapter.py` promotes a canonical `SpatialState` only when one Sequence-B row contains a complete ordinary XYZ **and** VXYZ state plus epoch. It performs no interpolation, propagation, trajectory math, or campaign mutation. Metric/relational rows are retained as source metadata without invented ordinary-space position.

`src/loom/navigation/trajectory_time_state.py` returns exact authoritative ordinary samples unchanged. Between two ordinary samples within one segment it may linearly interpolate for runtime/playback use, but the interpolated `SpatialState` is explicitly `navigation_grade=False`. It performs no extrapolation. Metric/relational phases without a valid ordinary bracket return no ordinary state.

`src/loom/navigation/trajectory_visual_sampling.py` is explicitly visualization-only and delegates to the time-state evaluator. It cannot promote presentation samples to navigation authority.

## Simulator telemetry coverage matrix

| Simulator need | Current status | Current evidence / limitation |
|---|---|---|
| trajectory epoch / phase | PRESENT | UTC epoch, flight-relative time, phase and ETA fields |
| ordinary 3D position | PRESENT WHERE SEQUENCE-B DECLARES ORDINARY OCCUPANCY | XYZ in J2000 ecliptic |
| ordinary 3D velocity | PRESENT WHERE SEQUENCE-B DECLARES ORDINARY OCCUPANCY | VXYZ |
| metric relational state | PRESENT, NO ORDINARY OCCUPANCY | relational progress, metric state, beta; ordinary XYZ must not be invented |
| acceleration vector | MISSING | only scalar `ordinary_accel_g` exists |
| attitude / orientation | MISSING | no quaternion/Euler/attitude state in trajectory samples |
| angular rate | MISSING | no body-rate vector |
| thrust vector / actuator command | MISSING | `torch_state_code` is state semantics, not a thrust vector or control command |
| wet mass / remass | PARTIAL | sampled wet mass and remass remaining exist |
| remass flow rate | MISSING | no per-sample mass-flow state |
| quantitative thermal state | MISSING | `thermal_state_code` is qualitative only |
| quantitative power state | MISSING | no electrical/reactor/bus/radiator power telemetry surface here |
| target-relative state | PARTIAL | range and delta-v magnitudes only; no relative position/velocity vector |
| navigation uncertainty / covariance | MISSING | no covariance/uncertainty in Sequence-B sample surface |
| sensor measurements | MISSING | no measurement layer |
| estimated navigation state | MISSING | current trajectory samples are Python-authored route truth, not estimator output |
| guidance command state | MISSING | no guidance target/command vector state |
| control / actuator state | MISSING | no commanded or achieved actuator state |
| docking / proximity state | MISSING | no hold-point, corridor, docking-port or relative docking state |
| traffic clearance state | MISSING | no clearance/reservation/no-burn state in trajectory samples |

## Critical epistemic boundary

The current Navigator trajectory packet is substantially stronger than a display polyline: where Sequence-B declares ordinary occupancy it can carry explicit time-stamped XYZ+VXYZ, plus useful propulsion/mass/thermal/target scalars and relational metric semantics.

It is **not yet a complete simulator telemetry packet**. In particular, scalar acceleration, target range/delta-v magnitudes, state codes, wet mass and remass cannot be silently expanded into vectors, attitude, actuator commands, thermal energy, power, uncertainty, sensor measurements or docking geometry.

The absence of ordinary XYZ during metric transit is intentional authority preservation, not missing rendering data to be filled by interpolation.

## F-PA-5 verdict

**CORE NAVIGATOR / TRAJECTORY TELEMETRY AUDIT COMPLETE.**

The current route/trajectory stack provides a usable authoritative trajectory truth boundary for ordinary 6D samples plus explicit relational metric phases, with strict anti-fabrication behavior in E1/E2/E3. It does not yet provide the full true-state → sensor → estimate → guidance → control telemetry hierarchy required by the physical-authority amendment.

The next audit stage is F-PA-6: Wayfarer / vehicle engineering authority against runtime dynamics requirements.
