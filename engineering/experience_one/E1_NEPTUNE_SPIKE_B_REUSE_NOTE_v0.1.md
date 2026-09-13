# E1 Neptune — Tested Spike B reuse note v0.1

The existing E1.0 Spike B disposable-campaign harness on PR #109 is the currently tested continuity harness for Navigator campaign execution. Its captured empirical run proves the existing authority path can produce `FLIGHT_COMMITTED`, `FLIGHT_ARRIVED`, restart persistence at `NEPTUNE_SYSTEM`, and replay while leaving the live campaign bit-identical.

The captured run was **MARS → NEPTUNE_SYSTEM**, not Ceres → Neptune. Therefore it is evidence that the execution/persistence seam is bounded, but it is not by itself the Experience One Ceres departure proof.

For PR #112 we will reuse that harness logic unchanged wherever possible and change only the disposable starting campaign so it is created by Navigator's own `_new_state(...)`, whose governed baseline starts at `CERES / READY_HOLD`.

No claim of Ceres → Neptune PASS is made until that empirical run exists.