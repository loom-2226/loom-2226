; LOOM 2226 — fixed-duration torch segment constraints v0.1
; engineering verification artifact; exact rational arithmetic; non-canon.
(include "wayfarer_torch_mode_envelope_v0.1.smt2")

(declare-const segment_duration_s Real)
(declare-const segment_remass_used_t Real)
(declare-const segment_start_remass_t Real)
(declare-const segment_end_remass_t Real)

(assert (! (>= segment_duration_s 0) :named S_DURATION_NONNEGATIVE))
(assert (! (and (>= segment_start_remass_t 0) (<= segment_start_remass_t 250)) :named S_START_REMASS_BOUNDS))
(assert (! (= segment_remass_used_t (/ (* mdot_kg_s segment_duration_s) 1000)) :named S_SEGMENT_REMASS_IDENTITY))
(assert (! (= segment_end_remass_t (- segment_start_remass_t segment_remass_used_t)) :named S_SEGMENT_BALANCE))
(assert (! (>= segment_end_remass_t 0) :named S_END_REMASS_NONNEGATIVE))
; Keep segment accounting tied to the vehicle inventory state.
(assert (! (= normal_remass_consumed_t (- 250 segment_end_remass_t)) :named S_VEHICLE_REMASS_BINDING))
