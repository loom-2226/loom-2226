; Negative fixture: CCR v2.5 245.39043171108221 t normal-remass limit plus forced 251 t consumption.
(set-option :produce-unsat-cores true)
(declare-const normal_remass_initial_t Real)
(declare-const normal_remass_consumed_t Real)
(assert (! (= normal_remass_initial_t 245.39043171108221) :named A_NORMAL_REMASS_V25_T))
(assert (! (<= normal_remass_consumed_t normal_remass_initial_t) :named A_REMASS_CONSUMPTION_LIMIT))
(assert (! (= normal_remass_consumed_t 251) :named X_FORCE_251_T_CONSUMPTION))
(check-sat)
(get-unsat-core)
