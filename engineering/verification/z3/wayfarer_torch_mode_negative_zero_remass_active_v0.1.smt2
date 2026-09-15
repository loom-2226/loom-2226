; Boundary probe: inventory exhaustion alone does not prove instantaneous torch infeasibility.
; This is intentionally SAT: the current earned model has no minimum feed-duration assertion.
(include "wayfarer_torch_mode_envelope_v0.1.smt2")
(assert (! (= normal_remass_remaining_t 0) :named H_ZERO_REMASS_REMAINING))
(assert (! (= mode LIMIT) :named H_REQUIRE_LIMIT))
(check-sat)
(get-model)
