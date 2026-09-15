; LOOM 2226 — Wayfarer torch mode + remass constraint model v0.1
; class: engineering verification artifact; non-canon; non-qualification by itself
; Exact rational arithmetic. SI units for propulsion variables; tonnes for inventory.
; This file intentionally contains constraints only. Query fixtures include it and
; issue their own check-sat/get-model/get-unsat-core commands.
(set-option :produce-models true)
(set-option :produce-unsat-cores true)

(declare-datatypes () ((TorchMode OFF ECON CRUISE EXPEDITE FAST HARD LIMIT)))
(declare-const mode TorchMode)
(declare-const torch_active Bool)
(declare-const high_metric_thermal_field_active Bool)
(declare-const mdot_kg_s Real)
(declare-const ve_m_s Real)
(declare-const thrust_N Real)
(declare-const jet_power_W Real)
(declare-const normal_remass_initial_t Real)
(declare-const normal_remass_consumed_t Real)
(declare-const normal_remass_remaining_t Real)
(declare-const protected_water_initial_t Real)
(declare-const protected_water_consumed_t Real)

(assert (! (= normal_remass_initial_t 250) :named A_NORMAL_REMASS_250_T))
(assert (! (= protected_water_initial_t 50) :named A_PROTECTED_WATER_50_T))
(assert (! (= normal_remass_remaining_t (- normal_remass_initial_t normal_remass_consumed_t)) :named A_REMASS_BALANCE))
(assert (! (and (>= normal_remass_consumed_t 0) (<= normal_remass_consumed_t normal_remass_initial_t)) :named A_REMASS_BOUNDS))
(assert (! (= protected_water_consumed_t 0) :named A_PROTECTED_WATER_FIREWALL))
(assert (! (not (and torch_active high_metric_thermal_field_active)) :named A_TORCH_METRIC_EXCLUSION))
(assert (! (= torch_active (not (= mode OFF))) :named A_MODE_ACTIVITY_BINDING))

; Exact recovered working-card points from the earned torch performance envelope.
(assert (!
  (or
    (and (= mode OFF) (= mdot_kg_s 0) (= ve_m_s 0) (= thrust_N 0) (= jet_power_W 0))
    (and (= mode ECON) (= mdot_kg_s (/ 11361004025 10000000000)) (= ve_m_s 3000000) (= thrust_N 3408300) (= jet_power_W 5112450000000))
    (and (= mode CRUISE) (= mdot_kg_s (/ 56805020125 10000000000)) (= ve_m_s 2000000) (= thrust_N 11361000) (= jet_power_W 11361000000000))
    (and (= mode EXPEDITE) (= mdot_kg_s (/ 2272200805 100000000)) (= ve_m_s 1000000) (= thrust_N 22722000) (= jet_power_W 11361000000000))
    (and (= mode FAST) (= mdot_kg_s (/ 4869001725 100000000)) (= ve_m_s 700000) (= thrust_N 34083000) (= jet_power_W 11929050000000))
    (and (= mode HARD) (= mdot_kg_s (/ 2272200805 18000000)) (= ve_m_s 450000) (= thrust_N 56805000) (= jet_power_W 12781125000000))
    (and (= mode LIMIT) (= mdot_kg_s (/ 2272200805 8000000)) (= ve_m_s 300000) (= thrust_N 85207500) (= jet_power_W 12781125000000)))
  :named A_MODE_CARD_TABLE))

; Independent physical identities. If a card drifts, the table and identities become inconsistent.
(assert (! (= thrust_N (* mdot_kg_s ve_m_s)) :named A_THRUST_IDENTITY))
(assert (! (= jet_power_W (* (/ 1 2) mdot_kg_s ve_m_s ve_m_s)) :named A_JET_POWER_IDENTITY))
(assert (! (and (>= mdot_kg_s 0) (>= ve_m_s 0) (>= thrust_N 0) (>= jet_power_W 0)) :named A_PROPULSION_NONNEGATIVE))
