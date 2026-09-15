; Negative fixture: authoritative 250 t normal-remass limit plus forced 251 t consumption.
(set-option :produce-unsat-cores true)
(declare-const normal_remass_initial_t Real)
(declare-const normal_remass_consumed_t Real)
(assert (! (= normal_remass_initial_t 250) :named A_NORMAL_REMASS_250_T))
(assert (! (<= normal_remass_consumed_t normal_remass_initial_t) :named A_REMASS_CONSUMPTION_LIMIT))
(assert (! (= normal_remass_consumed_t 251) :named X_FORCE_251_T_CONSUMPTION))
(check-sat)
(get-unsat-core)
