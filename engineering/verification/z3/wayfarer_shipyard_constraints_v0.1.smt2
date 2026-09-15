; LOOM Wayfarer Computational Shipyard — configuration constraints v0.1
; ENGINEERING VERIFICATION ONLY / NON-CANON / NON-CERTIFICATION.
; Governing/current values are separated from candidate packaging constraints.

; Current vehicle identities.
(define-fun dry-mass-t () Real 858.5)
(define-fun working-fluid-t () Real 300.0)
(define-fun wet-mass-t () Real (+ (dry-mass-t) (working-fluid-t)))
(define-fun normal-remass-t () Real 250.0)
(define-fun protected-water-t () Real 50.0)

; Current structural grammar.
(define-fun current-grammar-valid ((tanks Int) (longerons Int) (radiators Int) (torch-count Int)) Bool
  (and (= tanks 4) (= longerons 4) (= radiators 4) (= torch-count 1)))

; Candidate dry-mass ledger from the non-governing Wayfarer candidate specification.
; These values are verification inputs, not canon promotion.
(define-fun candidate-ledger-total-t
 ((structure Real) (armor Real) (hab Real) (relational Real) (thermal Real)
  (propulsion Real) (electrical Real) (launch Real) (avionics Real)
  (rcs-service Real) (mission Real) (reserve Real)) Real
 (+ structure armor hab relational thermal propulsion electrical launch avionics rcs-service mission reserve))

(define-fun candidate-ledger-valid
 ((structure Real) (armor Real) (hab Real) (relational Real) (thermal Real)
  (propulsion Real) (electrical Real) (launch Real) (avionics Real)
  (rcs-service Real) (mission Real) (reserve Real)) Bool
 (= (candidate-ledger-total-t structure armor hab relational thermal propulsion electrical launch avionics rcs-service mission reserve)
    (dry-mass-t)))

; Candidate broad axial packaging only. Adjacent envelopes may touch but not overlap.
(define-fun ordered-envelope ((a0 Real) (a1 Real) (b0 Real) (b1 Real)) Bool
  (and (<= 0.0 a0) (<= a0 a1) (<= a1 b0) (<= b0 b1) (<= b1 57.0)))

(define-fun aft-torch-packaging-valid
 ((shield0 Real) (shield1 Real) (reactor0 Real) (reactor1 Real) (nozzle0 Real) (nozzle1 Real)) Bool
 (and (ordered-envelope shield0 shield1 reactor0 reactor1)
      (ordered-envelope reactor0 reactor1 nozzle0 nozzle1)
      (= shield0 38.0) (= shield1 43.0)
      (= reactor0 43.0) (= reactor1 50.0)
      (= nozzle0 50.0) (= nozzle1 57.0)))

; Configuration-state compatibility. Candidate vocabulary, verification use only.
(declare-datatypes () ((LaunchState DOCKED EXTRACTING ABSENT)))
(declare-datatypes () ((RadiatorState STOWED DEPLOYING DEPLOYED)))
(declare-datatypes () ((TorchState TORCH_OFF TORCH_SAFE TORCH_ACTIVE)))

; Current recovered thermal/field exclusion plus candidate physical interference rules.
(define-fun configuration-valid
 ((launch LaunchState) (radiators RadiatorState) (torch TorchState) (high-metric Bool)) Bool
 (and
   (not (and (= torch TORCH_ACTIVE) high-metric))
   ; launch extraction is not treated as a normal high-energy propulsion state
   (not (and (= launch EXTRACTING) (= torch TORCH_ACTIVE)))
   ; active torch requires radiators in their operational deployed state for this candidate check
   (=> (= torch TORCH_ACTIVE) (= radiators DEPLOYED))))
