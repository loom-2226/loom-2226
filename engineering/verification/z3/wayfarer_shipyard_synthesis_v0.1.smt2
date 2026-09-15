; Computational Shipyard slice 1 — valid integrated configuration synthesis.
(set-option :produce-unsat-cores true)
(include "wayfarer_shipyard_constraints_v0.1.smt2")

(declare-const launch LaunchState)
(declare-const radiators RadiatorState)
(declare-const torch TorchState)
(declare-const high-metric Bool)

(assert (! (current-grammar-valid 4 4 4 1) :named CURRENT_GRAMMAR))
(assert (! (= (wet-mass-t) 1158.5) :named CURRENT_WET_MASS_IDENTITY))
(assert (! (= (+ (normal-remass-t) (protected-water-t)) (working-fluid-t)) :named CURRENT_FLUID_IDENTITY))

(assert (! (candidate-ledger-valid 150.0 105.0 45.0 88.0 90.0 160.0 55.0 33.0 20.0 25.0 20.0 67.5) :named CANDIDATE_LEDGER))
(assert (! (aft-torch-packaging-valid 38.0 43.0 43.0 50.0 50.0 57.0) :named CANDIDATE_AFT_PACKAGING))

(assert (! (= launch DOCKED) :named CFG_LAUNCH_DOCKED))
(assert (! (= torch TORCH_ACTIVE) :named CFG_TORCH_ACTIVE))
(assert (! (= high-metric false) :named CFG_METRIC_OFF))
(assert (! (configuration-valid launch radiators torch high-metric) :named CFG_VALID))

(check-sat)
(get-value (launch radiators torch high-metric))
