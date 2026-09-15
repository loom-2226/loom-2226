; Recovered vehicle-interface hostile proof: simultaneous torch/high-metric is forbidden.
(include "wayfarer_torch_mission_constraints_v0.1.smt2")
(declare-const torch-active Bool)
(declare-const high-metric-active Bool)
(assert (! torch-active :named H_TORCH_ACTIVE))
(assert (! high-metric-active :named H_HIGH_METRIC_ACTIVE))
(assert (! (propulsion-state-valid torch-active high-metric-active) :named H_PROPULSION_STATE_VALID))
(check-sat)
(get-unsat-core)
