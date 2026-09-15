; Hostile fixture: CRUISE card cannot simultaneously have 12 TW jet power.
(include "wayfarer_torch_mode_envelope_v0.1.smt2")
(assert (! (= mode CRUISE) :named H_REQUIRE_CRUISE))
(assert (! (= jet_power_W 12000000000000) :named H_REQUIRE_12_TW))
(check-sat)
(get-unsat-core)
