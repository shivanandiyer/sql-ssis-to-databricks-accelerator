# Source: DW:Integration.GetLastETLCutoffTime  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/GetLastETLCutoffTime.sql)
# Split 2 of 2: Workflow/task orchestration logic for an orchestration-heavy procedure.
# This is the Databricks Workflow task entry point — it owns parameter handling,
# watermark read/advance, and invoking the companion SQL transformation logic.
# See orchestration_design.md for how this fits into the per-entity Workflow job.

from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()


def run(last_cutoff: str, new_cutoff: str) -> None:
    """Orchestration entry point for GetLastETLCutoffTime.

    TODO: implement the per-row iteration that the source CURSOR/WHILE loop performed,
    either as a single set-based MERGE (preferred) or, if genuinely row-dependent
    (e.g. each iteration depends on the previous one's output), as a bounded Python loop.
    """
    # 1. Read watermark range [last_cutoff, new_cutoff) — see ops.etl_watermark table.
    # 2. Execute the companion SQL transformation logic (see databricks_sql output).
    # 3. Advance the watermark only after step 2 succeeds (atomic with the data write).
    raise NotImplementedError('Manual conversion required — see source T-SQL and design notes above.')