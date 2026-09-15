; Hostile candidate-ledger check: preserve all listed allocations but inflate propulsion.
(set-option :produce-unsat-cores true)
(include "wayfarer_shipyard_constraints_v0.1.smt2")
(assert (! (candidate-ledger-valid 150.0 105.0 45.0 88.0 90.0 170.0 55.0 33.0 20.0 25.0 20.0 67.5) :named H_LEDGER_MUST_CLOSE))
(check-sat)
(get-unsat-core)
