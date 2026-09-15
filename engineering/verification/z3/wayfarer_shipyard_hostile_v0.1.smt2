; Computational Shipyard slice 1 — deliberately impossible integrated configuration.
(set-option :produce-unsat-cores true)
(include "wayfarer_shipyard_constraints_v0.1.smt2")

(declare-const launch LaunchState)
(declare-const radiators RadiatorState)
(declare-const torch TorchState)
(declare-const high-metric Bool)

(assert (! (= launch EXTRACTING) :named H_LAUNCH_EXTRACTING))
(assert (! (= radiators STOWED) :named H_RADIATORS_STOWED))
(assert (! (= torch TORCH_ACTIVE) :named H_TORCH_ACTIVE))
(assert (! high-metric :named H_HIGH_METRIC_ACTIVE))
(assert (! (configuration-valid launch radiators torch high-metric) :named H_CONFIGURATION_VALID))
(check-sat)
(get-unsat-core)
