-- Converted from SSIS Execute SQL Task: Truncate TransactionType_Staging
-- Original: DELETE FROM Integration.TransactionType_Staging;
-- Idempotent by construction: DELETE-based staging clears are safe to
-- re-run; if migrating to Delta overwrite-mode loads, this step can be
-- dropped entirely (see target_state_architecture.md, Bronze staging note).

DELETE FROM Integration.TransactionType_Staging;