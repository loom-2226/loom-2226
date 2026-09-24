-- A column's Gate-A qualification applies only within its documented row scope.
ALTER TABLE loom_control.field_semantics
    ADD COLUMN qualified_row_filter text;

COMMENT ON COLUMN loom_control.field_semantics.qualified_row_filter IS
    'Evidence-bound row scope from the pinned Gate-A matrix; prose is not an executable SQL predicate.';
