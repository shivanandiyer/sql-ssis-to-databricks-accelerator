"""
Shared environment/secret/watermark resolution helpers.

Every generated task under output/pyspark/ and output/ssis_tasks/ receives
`environment` and `catalog` as Workflow task base_parameters (see
bundle/resources/wwi_daily_etl_main.job.yml). These helpers centralize the
naming conventions so they're defined once, not copy-pasted into 60+ files.
"""

from __future__ import annotations

from datetime import datetime, timezone


def get_secret_scope(environment: str) -> str:
    """Per-environment secret scope name for the source SQL Server connection.
    See conf/secrets.md for the scope-creation commands."""
    return f"wwi-source-db-{environment}"


def get_catalog(environment: str) -> str:
    """Per-environment Unity Catalog catalog name (wwi_dev / wwi_test / wwi_prod)."""
    return f"wwi_{environment}"


def get_watermark(spark, catalog: str, entity: str) -> str | None:
    """Read the last successful cutoff timestamp for `entity` from the
    ops.etl_watermark Delta table (replaces the source's Integration.ETL
    Cutoff SQL table — see orchestration_design.md's watermark design note).
    Returns None on first run (no prior watermark row), in which case the
    caller should perform a full initial load rather than fail or skip.
    """
    table = f"{catalog}.ops.etl_watermark"
    rows = (
        spark.sql(f"SELECT last_cutoff_ts FROM {table} WHERE entity = '{entity}'")
        .collect()
    )
    return rows[0]["last_cutoff_ts"] if rows else None


def advance_watermark(spark, catalog: str, entity: str, new_cutoff_ts: str) -> None:
    """Advance the watermark for `entity` — call only after the corresponding
    MERGE/load task has committed successfully, so the watermark advance is
    atomic with the data write per entity (never advance speculatively)."""
    table = f"{catalog}.ops.etl_watermark"
    spark.sql(f"""
        MERGE INTO {table} AS target
        USING (SELECT '{entity}' AS entity, '{new_cutoff_ts}' AS last_cutoff_ts) AS source
        ON target.entity = source.entity
        WHEN MATCHED THEN UPDATE SET target.last_cutoff_ts = source.last_cutoff_ts
        WHEN NOT MATCHED THEN INSERT (entity, last_cutoff_ts) VALUES (source.entity, source.last_cutoff_ts)
    """)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
