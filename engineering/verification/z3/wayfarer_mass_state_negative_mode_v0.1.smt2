; Negative fixture: force both mutually-exclusive operating states active.
(set-option :produce-unsat-cores true)
(declare-const torch_active Bool)
(declare-const high_metric_thermal_field_active Bool)
(assert (! (not (and torch_active high_metric_thermal_field_active)) :named A_TORCH_METRIC_MUTUAL_EXCLUSION))
(assert (! torch_active :named X_FORCE_TORCH_ACTIVE))
(assert (! high_metric_thermal_field_active :named X_FORCE_HIGH_METRIC_ACTIVE))
(check-sat)
(get-unsat-core)
