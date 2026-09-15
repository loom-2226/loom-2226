; Five-segment compositional synthesis proof.
; Engineering verification only; fixed-duration mission/configuration constraint exercise.
(include "wayfarer_torch_mission_constraints_v0.1.smt2")

(declare-const m1 TorchMode)
(declare-const m2 TorchMode)
(declare-const m3 TorchMode)
(declare-const m4 TorchMode)
(declare-const m5 TorchMode)
(declare-const r1 Real)
(declare-const r2 Real)
(declare-const r3 Real)
(declare-const r4 Real)
(declare-const r5 Real)

; High-thrust bookends; economical interior; exact card library chooses compatible modes.
(assert (! (segment-meets m1 30000000.0 12000000000000.0) :named S1_REQUIREMENT))
(assert (! (segment-meets m2 3000000.0 6000000000000.0) :named S2_REQUIREMENT))
(assert (! (segment-meets m3 10000000.0 11500000000000.0) :named S3_REQUIREMENT))
(assert (! (segment-meets m4 3000000.0 6000000000000.0) :named S4_REQUIREMENT))
(assert (! (segment-meets m5 30000000.0 12000000000000.0) :named S5_REQUIREMENT))

(assert (! (= r1 (remass-after-t 250.0 m1 300.0)) :named R1_CHAIN))
(assert (! (= r2 (remass-after-t r1 m2 1800.0)) :named R2_CHAIN))
(assert (! (= r3 (remass-after-t r2 m3 1200.0)) :named R3_CHAIN))
(assert (! (= r4 (remass-after-t r3 m4 1800.0)) :named R4_CHAIN))
(assert (! (= r5 (remass-after-t r4 m5 300.0)) :named R5_CHAIN))
(assert (! (and (remass-valid 250.0 r1) (remass-valid r1 r2) (remass-valid r2 r3)
                (remass-valid r3 r4) (remass-valid r4 r5)) :named REMASS_CHAIN_VALID))
(assert (! (>= r5 180.0) :named FINAL_NORMAL_REMASS_RESERVE))
(assert (! (propulsion-state-valid true false) :named TORCH_STATE_VALID))

(check-sat)
(get-value (m1 m2 m3 m4 m5 r5))
