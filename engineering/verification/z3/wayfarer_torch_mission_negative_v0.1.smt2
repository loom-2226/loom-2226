; Hostile mission contradiction: LIMIT burn from insufficient normal remass while
; demanding a larger final reserve. Expected UNSAT with named core.
(set-option :produce-unsat-cores true)
(include "wayfarer_torch_mission_constraints_v0.1.smt2")
(declare-const m TorchMode)
(declare-const r Real)
(assert (! (= m LIMIT) :named H_FORCE_LIMIT))
(assert (! (= r (remass-after-t 20.0 m 120.0)) :named H_REMASS_ACCOUNTING))
(assert (! (remass-valid 20.0 r) :named H_NONNEGATIVE_REMASS))
(assert (! (>= r 10.0) :named H_FINAL_RESERVE))
(check-sat)
(get-unsat-core)
