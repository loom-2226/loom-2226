; Synthesis query: let Z3 choose a card satisfying an imposed operating envelope.
(include "wayfarer_torch_mode_envelope_v0.1.smt2")
(assert (! torch_active :named Q_TORCH_REQUIRED))
(assert (! (>= thrust_N 30000000) :named Q_MIN_THRUST_30_MN))
(assert (! (<= jet_power_W 12000000000000) :named Q_MAX_JET_POWER_12_TW))
(assert (! (>= normal_remass_remaining_t 100) :named Q_KEEP_100_T_REMASS))
(check-sat)
(get-model)
