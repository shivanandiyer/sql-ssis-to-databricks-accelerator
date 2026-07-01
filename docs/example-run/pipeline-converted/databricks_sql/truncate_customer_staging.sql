-- Converted from SSIS Execute SQL Task: Truncate Customer_Staging
-- Original: DELETE FROM Integration.Customer_Staging;
-- Idempotent by construction: DELETE-based staging clears are safe to
-- re-run; if migrating to Delta overwrite-mode loads, this step can be
-- dropped entirely (see target_state_architecture.md, Bronze staging note).

DELETE FROM Integration.Customer_Staging;