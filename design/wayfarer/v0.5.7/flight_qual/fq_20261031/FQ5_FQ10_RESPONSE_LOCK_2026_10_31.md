# Wayfarer FQ5/FQ10 recovery assessment, 2026-10-31

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING. PR #435 draft/HOLD. No physical flight certificate.**

This report supersedes the FQ5, FQ8 and FQ10 dispositions in the earlier FQ campaign report. Prior empty-tank and unmitigated stuck-TVC failures remain as deliberate historical counterfactuals.

**Locked geometry SHA256:** ea1fcb59f1e0a127cd48dc4e0321e7d42247e3f2e445cf89893bdefadb793266. No rebuild, no mass change, and no modifications to nozzle mounts, pressure hull, crown or L1 occurred during these reruns. Only the isolated conventional flight laboratory and the kT decision record were changed.

## Explicit decisions

1. **TVC safing:** torque-authority-based throttle reduction; cut torch if RCS remains saturated or measured angular error/rate exceeds bounds. Bench-only detector delay 0.20s; instantaneous torch throttle/cut actuator response in laboratory; physical sensing and actuators unqualified. The older approximate 56% CRUISE and 14% HARD are upper estimates, not enforced as safe fixed setpoints.
2. **RCS reserve:** ring-fence 5.000t in the existing 250t unprotected remass inventory. The torch must stop at that floor, while RCS is allowed to spend it. Protected 50t water reservoir remains excluded from propulsion. No extra storage or dry mass was added.
3. **Heating:** A, ship plant on demand, declared architecture, no power closure. At 1.96km/s, one 25kN RCS jet requires at least 57.663MW (2.6MJ/kg conditioning plus 0.5ve² ideal jet kinetic energy). At 1.00km/s: 77.500MW. B hot-water store is OPTION, not baseline. PR #436 draft propulsion cards were NOT adopted or modified.

## FQ5 at exactly 5t remaining

| Case | Water used | Left | Verdict |
|---|---:|---:|---|
| Torch CRUISE commanded, 30s | 0kg | 5,000kg | CORRECTLY INHIBITED, no torch burn |
| RCS 180 pitch flip, 120s | 456.926kg | 4543.074kg | PASS |
| RCS 180 roll flip, 120s | 106.575kg | 4893.425kg | PASS |
| RCS 180 yaw flip, 120s | 459.783kg | 4540.217kg | PASS |
| Three consecutive flips, one state | 1023.191kg | 3976.809kg | PASS |

The simulator marks the torch-at-floor propulsion state as a physical FAIL, which is a desired interlock, not a failure of the RCS reserve. At both 0.4s and 0.2s numerical steps, four associated reserve/torch interlock checks (three axes plus torch inhibit) produced eight matching PASS verdicts.

## FQ8 new torch cutoff
Continuous CRUISE command 43249.99s, consuming 245000.000kg; final unprotected remass 5000.000kg, plus the separate untouched protected 50t. The earlier burn to zero usable remass is no longer dispatch doctrine. Continuous thermal endurance and plant response remain unqualified.

## FQ10 1 degree stuck TVC @60s

| Mode | Unmitigated final error / rate | Mitigated peak error | Mitigated peak rate | Throttle limit; cut time |
|---|---|---:|---:|---|
| CRUISE | 21.32 degrees / 81.39 deg/s | 0.108 degrees | 0.194 deg/s | 48.5% at 60.20s; cut at 60.65s |
| HARD | 15.78 degrees / 365.82 deg/s | 0.605 degrees | 1.009 deg/s | 12.1% at 60.20s; cut at 60.20s |

CRUISE had calculated RCS torque allocation fraction 0.5388 and commanded a 0.4849 cap; allocation saturation led to cut at 60.65s. HARD had fraction 0.1343 and capped at 0.1209; the 0.5deg/s rate threshold triggered immediate cut at detection (60.20s). Both returned to near-zero attitude/rate by 120s, but neither demonstrated sustained limp-on operation. Unmitigated cases passed through large angles; final orientation is NOT their peak error.

These are conditional numerical FQ10 recoveries with an ideal detector. The actual sensing, actuator shutoff lag, safing logic and plant MW are NOT qualified. A 1-second or missed response was not proven safe.

## Cluster lost while actively demanded
During a nominal pitch flip, cluster A+Z generated 58252.3 N*s in the 20-30s window; it was disabled at t=25s. Terminal error was 0.00000005 degrees, terminal rate 0.000000073 deg/s; PASS within 0.25 degrees and 0.05deg/s. This is a genuine manoeuvring loss case, not the prior near-idle case.

## Consolidated FQ1-FQ10

| FQ | Current status | Boundary |
|---|---|---|
| FQ1 | PASS, prior | three-axis 180 flips <=240s |
| FQ2 | PASS, prior | 24 cluster-loss flips full/half remass |
| FQ3 | PASS, prior | +/- X, Y, Z translation |
| FQ4 | PASS, prior | all six torch modes, <=4g and trim |
| FQ5 | PASS, revised | 5t torch floor retained; three RCS flips including one continuous three-flip case |
| FQ6 | PASS numerical parity | 93 earlier paired cases, plus eight paired reserve-floor checks; NOT detector hardware convergence |
| FQ7 | PASS, prior | tank water consumption counted; feed and power OPEN |
| FQ8 | PASS, revised | stops at 5t RCS remass floor; protected 50t unchanged |
| FQ9 | PASS, prior | one-state mass ledger closed; original geometry unchanged |
| FQ10 | PASS conditional numerical recovery | controlled CRUISE/HARD TVC events and active cluster loss; FDIR and actuator validation OPEN |

**Overall:** conventional numerical FQ1-FQ10 screening now has bounded PASS evidence under these policies. This is NOT a physical flight certificate, particularly because TVC fault detection/control, on-demand heater delivery, thermal duty and the unresolved G12 render provenance remain HOLD.

## Replay and no-go boundary

Model: faultlab_safing.py, non-governing sandbox-only adaptation of Rev7 flightlab.py. Run scripts and output JSONs are preserved alongside this document. Geometry input is pinned to the SHA above; build source and the Rev7 archive PR remain unchanged. PR #435 stays draft/HOLD, no merge to main, no renders, Navigator, Metric, repo migration or PR #436 changes.
