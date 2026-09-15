; Instantaneous active-at-zero-remass remains intentionally representable elsewhere.
; A positive-duration LIMIT segment starting empty cannot satisfy remass accounting.
(include "wayfarer_torch_segment_constraints_v0.1.smt2")
(assert (! (= mode LIMIT) :named H_REQUIRE_LIMIT))
(assert (! (= segment_duration_s 1) :named H_REQUIRE_POSITIVE_DURATION))
(assert (! (= segment_start_remass_t 0) :named H_REQUIRE_EMPTY_START))
(check-sat)
(get-unsat-core)
