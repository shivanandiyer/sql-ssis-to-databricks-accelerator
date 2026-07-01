# Unsupported / Not-Present SSIS Features

> **Generated:** 2026-06-30 04:57 UTC

This document covers two categories: (a) features the converter explicitly cannot automate even though they're present in the source, and (b) features in the required handling scope that were **not found** in this particular package — included so the mapping rule is documented for any future SSIS package that does use them.

## Found in source — partially automated, manual completion required

| Feature | Found? | Status |
|---|---|---|
| Sequence containers | Yes (13) | Mapped to Workflow task dependency chains — automated. |
| Execute SQL task | Yes (53) | Mapped to SQL/Python tasks — automated where the body is a simple EXEC/DELETE; manual completion needed where it calls a CURSOR-based procedure (see conversion_decisions.md from the SQL conversion layer). |
| Data flow task | Yes (13) | Mapped to PySpark extract tasks — automated (all 13 are simple OLE DB Source -> Destination with no in-pipeline transforms). |
| Cutoff-time / watermark logic | Yes | Mapped to an `ops.etl_watermark` Delta table pattern — automated design, manual implementation of the read/advance logic required. |
| Precedence constraints (Success only) | Yes | Mapped to Workflow `depends_on` — automated. |
| Expressions | Yes (15) | Mapped to Python task parameters — automated detection, manual translation of expression syntax required (no SSIS expression-language interpreter is implemented). |

## Required handling scope — not present in this source package

| Feature | Found? | Mapping rule (for future packages that do use it) |
|---|---|---|
| Foreach Loop containers | No | Map to a Databricks Workflow `for_each_task` (native For Each task type) iterating over a Python list/array task parameter, or a parameterised job run via the Jobs API for each iteration value. |
| Conditional branching (expression-based precedence constraints) | No — all 130 precedence constraints in this package use plain SUCCESS conditions | Map an SSIS expression-based precedence constraint to a Workflow task `condition_task`, branching to different downstream `depends_on` sets based on a prior task's output value. |
| Row count transformation | No | Map to a `df.count()` call captured into a notebook return value (`dbutils.notebook.exit(json.dumps({...}))`) or a Lakehouse Monitoring metric, then referenced by a downstream `condition_task` if used for branching. |
| Flat file ingestion | No — both connection managers are OLE DB (SQL Server) | Map to Databricks Auto Loader (`cloudFiles` format) reading from a Unity Catalog volume, with the SSIS Flat File connection manager's column/format definition translated to an explicit Auto Loader schema. |
| Event handlers (OnError, OnTaskFailed, etc.) | No — `DailyETLMain.dtsx` defines no `<DTS:EventHandlers>` blocks | Map to Databricks Workflow task-level `on_failure` webhook notifications and a dedicated cleanup/compensation task wired via `depends_on` with `run_if: AT_LEAST_ONE_FAILED`. |

## Restartability

SSIS's package-level restart-from-checkpoint behaviour has no direct Workflow equivalent. The recommended replacement, already reflected in `workflow_spec.json`, is: (1) make every task idempotent (Delta overwrite/MERGE rather than INSERT-only), so any task can be safely re-run; (2) rely on Databricks Workflows' native "repair run" feature, which re-runs only the failed/skipped tasks in a job's most recent run rather than the whole job — this is a closer and lower-effort equivalent to SSIS checkpoint restart than building custom checkpoint logic.

## Error Handling

No `OnError` event handlers exist in the source package — the implicit behaviour is SSIS's default (fail the task, propagate failure up the container chain, package fails). This is mapped to Workflow tasks' default `run_if: ALL_SUCCESS` dependency behaviour plus the job-level `email_notifications.on_failure` setting already present in `workflow_spec.json` — no custom error-handling tasks were needed for a 1:1 behavioural match.