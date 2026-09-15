; LOOM 2226 — three-segment torch configuration synthesis v0.1
; Engineering verification only. Exact linear segment accounting; no trajectory integration.
(include "wayfarer_torch_mode_envelope_v0.1.smt2")

(declare-const mode2 TorchMode)
(declare-const mode3 TorchMode)
(declare-const mdot2 Real)
(declare-const mdot3 Real)
(declare-const thrust2 Real)
(declare-const thrust3 Real)
(declare-const power2 Real)
(declare-const power3 Real)
(declare-const d1 Real)
(declare-const d2 Real)
(declare-const d3 Real)
(declare-const r1 Real)
(declare-const r2 Real)
(declare-const r3 Real)

; Reuse mode as segment 1. Bind later segments to the same earned card table.
(define-fun bind-card ((m TorchMode) (flow Real) (f Real) (p Real)) Bool
  (or
    (and (= m OFF) (= flow 0) (= f 0) (= p 0))
    (and (= m ECON) (= flow (/ 11361004025 10000000000)) (= f (* flow 3000000)) (= p (* (/ 1 2) flow 3000000 3000000)))
    (and (= m CRUISE) (= flow (/ 56805020125 10000000000)) (= f (* flow 2000000)) (= p (* (/ 1 2) flow 2000000 2000000)))
    (and (= m EXPEDITE) (= flow (/ 2272200805 100000000)) (= f (* flow 1000000)) (= p (* (/ 1 2) flow 1000000 1000000)))
    (and (= m FAST) (= flow (/ 4869001725 100000000)) (= f (* flow 700000)) (= p (* (/ 1 2) flow 700000 700000)))
    (and (= m HARD) (= flow (/ 2272200805 18000000)) (= f (* flow 450000)) (= p (* (/ 1 2) flow 450000 450000)))
    (and (= m LIMIT) (= flow (/ 2272200805 8000000)) (= f (* flow 300000)) (= p (* (/ 1 2) flow 300000 300000))))

(assert (! (bind-card mode2 mdot2 thrust2 power2) :named M_BIND_SEGMENT_2))
(assert (! (bind-card mode3 mdot3 thrust3 power3) :named M_BIND_SEGMENT_3))
(assert (! (and (> d1 0) (> d2 0) (> d3 0)) :named M_POSITIVE_DURATIONS))
(assert (! (= r1 (- 250 (/ (* mdot_kg_s d1) 1000))) :named M_REMASS_AFTER_1))
(assert (! (= r2 (- r1 (/ (* mdot2 d2) 1000))) :named M_REMASS_AFTER_2))
(assert (! (= r3 (- r2 (/ (* mdot3 d3) 1000))) :named M_REMASS_AFTER_3))
(assert (! (and (>= r1 0) (>= r2 0) (>= r3 0)) :named M_REMASS_NONNEGATIVE))

; Mission-shaped requirements, not trajectory propagation:
; 5 min high-thrust departure, 20 min efficient middle segment, 5 min high-thrust arrival.
(assert (! (= d1 300) :named Q_SEG1_300_S))
(assert (! (= d2 1200) :named Q_SEG2_1200_S))
(assert (! (= d3 300) :named Q_SEG3_300_S))
(assert (! (>= thrust_N 30000000) :named Q_SEG1_MIN_30_MN))
(assert (! (<= jet_power_W 12000000000000) :named Q_SEG1_MAX_12_TW))
(assert (! (>= thrust2 10000000) :named Q_SEG2_MIN_10_MN))
(assert (! (<= power2 11500000000000) :named Q_SEG2_MAX_11P5_TW))
(assert (! (>= thrust3 30000000) :named Q_SEG3_MIN_30_MN))
(assert (! (<= power3 12000000000000) :named Q_SEG3_MAX_12_TW))
(assert (! (>= r3 180) :named Q_FINAL_RESERVE_180_T))
(check-sat)
(get-model)
