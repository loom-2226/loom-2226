; GENERATED FILE — DO NOT HAND EDIT.
; Source: src/wayfarer_torch_mode_cards.py
; Engineering verification only / non-canon / non-certification.
(declare-datatypes () ((TorchMode OFF ECON CRUISE EXPEDITE FAST HARD LIMIT)))
(define-fun mode-mdot ((m TorchMode)) Real
  (ite (= m ECON) (/ 454440161 400000000) (ite (= m CRUISE) (/ 454440161 80000000) (ite (= m EXPEDITE) (/ 454440161 20000000) (ite (= m FAST) (/ 194760069 4000000) (ite (= m HARD) (/ 454440161 3600000) (ite (= m LIMIT) (/ 454440161 1600000) 0)))))))
(define-fun mode-ve ((m TorchMode)) Real
  (ite (= m ECON) 3000000 (ite (= m CRUISE) 2000000 (ite (= m EXPEDITE) 1000000 (ite (= m FAST) 700000 (ite (= m HARD) 450000 (ite (= m LIMIT) 300000 0)))))))
(define-fun mode-thrust ((m TorchMode)) Real (* (mode-mdot m) (mode-ve m)))
(define-fun mode-pjet ((m TorchMode)) Real (* (/ 1 2) (mode-mdot m) (mode-ve m) (mode-ve m)))
(define-fun mode-torch-active ((m TorchMode)) Bool (not (= m OFF)))
