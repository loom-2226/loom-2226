; Wayfarer E1 composable torch mission constraints v0.1
; Engineering verification only / non-canon / non-certification.
; Uses exact generated working-card functions; no new physical parameters.
(include "wayfarer_torch_generated_cards_v0.1.smt2")

; Segment-local accounting helpers. Duration is seconds; remass is tonnes.
(define-fun remass-use-t ((m TorchMode) (duration-s Real)) Real
  (/ (* (mode-mdot m) duration-s) 1000.0))
(define-fun remass-after-t ((start-t Real) (m TorchMode) (duration-s Real)) Real
  (- start-t (remass-use-t m duration-s)))

; Requirement predicates compose mission/configuration questions without
; duplicating the mode-card numeric truth.
(define-fun segment-meets ((m TorchMode) (min-thrust-n Real) (max-pjet-w Real)) Bool
  (and (mode-torch-active m)
       (>= (mode-thrust m) min-thrust-n)
       (<= (mode-pjet m) max-pjet-w)))

(define-fun remass-valid ((start-t Real) (end-t Real)) Bool
  (and (>= start-t 0.0) (>= end-t 0.0) (<= end-t start-t)))

; Recovered vehicle interface: torch and high-metric operation are mutually exclusive.
(define-fun propulsion-state-valid ((torch-active Bool) (high-metric-active Bool)) Bool
  (not (and torch-active high-metric-active)))
