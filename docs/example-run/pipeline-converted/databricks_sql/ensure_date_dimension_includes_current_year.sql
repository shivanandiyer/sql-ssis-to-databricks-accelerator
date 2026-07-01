-- Converted from SSIS Execute SQL Task: Ensure Date Dimension includes current year
-- Original: DECLARE @YearNumber int =  YEAR(SYSUTCDATETIME());

EXEC Integration.PopulateDateDimensionForYear @YearNumber;
-- Idempotent by construction: DELETE-based staging clears are safe to
-- re-run; if migrating to Delta overwrite-mode loads, this step can be
-- dropped entirely (see target_state_architecture.md, Bronze staging note).

DECLARE @YearNumber int =  YEAR(SYSUTCDATETIME());

EXEC Integration.PopulateDateDimensionForYear @YearNumber;