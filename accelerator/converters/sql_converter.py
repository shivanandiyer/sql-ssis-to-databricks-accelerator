"""
sql_converter.py
Converts SQL Server/Synapse source objects (tables, views, materialized views,
stored procedures, functions) into Databricks-compatible assets.

Rule of thumb applied throughout: preserve semantics first, syntax second.
Where a construct has no direct Databricks equivalent, this module emits a
best-effort skeleton with explicit TODO comments rather than silently
dropping behaviour.

Consumes:
    outputs/inventory.json
    outputs/object_complexity_scores.json   (classification per object)
    outputs/medallion_mapping.csv           (target catalog/schema/table per data object)

Produces, under a given output_root:
    databricks_sql/<layer>/<schema>__<name>.sql
    pyspark/<schema>__<name>.py
    review_required/<schema>__<name>.md
    conversion_manifest.json
    conversion_decisions.md
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Type mapping: SQL Server -> Delta/Spark SQL
# ---------------------------------------------------------------------------

TYPE_MAP: list[tuple[str, str, str | None]] = [
    # (sql_server_base_type_regex, databricks_type, review_note or None)
    (r"^NVARCHAR$|^VARCHAR$|^NCHAR$|^CHAR$|^TEXT$|^NTEXT$", "STRING", None),
    (r"^INT$", "INT", None),
    (r"^BIGINT$", "BIGINT", None),
    (r"^SMALLINT$", "SMALLINT", None),
    (r"^TINYINT$", "TINYINT", None),
    (r"^BIT$", "BOOLEAN", None),
    (r"^DECIMAL$|^NUMERIC$", "DECIMAL", None),
    (r"^MONEY$|^SMALLMONEY$", "DECIMAL(19,4)", None),
    (r"^FLOAT$", "DOUBLE", None),
    (r"^REAL$", "FLOAT", None),
    (r"^DATE$", "DATE", None),
    (r"^DATETIME2$|^DATETIME$|^SMALLDATETIME$", "TIMESTAMP", None),
    (r"^DATETIMEOFFSET$", "TIMESTAMP",
     "DATETIMEOFFSET preserves an explicit UTC offset per row; Spark TIMESTAMP does not — "
     "verify timezone handling is acceptable or store the offset in a separate column."),
    (r"^TIME$", "STRING",
     "No native TIME type in Spark SQL; stored as STRING (HH:MM:SS.fffffff). "
     "Consider STRING or cast to TIMESTAMP with a fixed date if arithmetic is required."),
    (r"^UNIQUEIDENTIFIER$", "STRING", None),
    (r"^VARBINARY$|^BINARY$|^IMAGE$", "BINARY", None),
    (r"^XML$", "STRING",
     "XML has no native Spark type; stored as STRING. If queried with .value()/.nodes() in "
     "T-SQL, those XPath operations must be reimplemented with Spark's xpath_* functions."),
    (r"^SYS\.GEOGRAPHY$|^GEOGRAPHY$", "STRING",
     "No native geospatial type in Delta Lake. Recommend storing as WKT STRING and adding an "
     "H3 index column, or adopting a geospatial library (Databricks Mosaic / Apache Sedona) "
     "for spatial predicates. MANUAL REVIEW REQUIRED."),
    (r"^SYS\.GEOMETRY$|^GEOMETRY$", "STRING",
     "Same as geography — no native Spark type. MANUAL REVIEW REQUIRED."),
    (r"^HIERARCHYID$", "STRING",
     "No native hierarchical type; store the materialised path as STRING and reimplement "
     "ancestor/descendant queries as string-prefix matches. MANUAL REVIEW REQUIRED."),
    (r"^SQL_VARIANT$", "STRING",
     "No equivalent dynamic type in Spark; values must be normalised to a single type or "
     "stored as STRING with an accompanying type-tag column. MANUAL REVIEW REQUIRED."),
    (r"^ROWVERSION$|^TIMESTAMP$", "BINARY",
     "SQL Server auto-incrementing row version has no Delta equivalent; replace with a "
     "Delta-native change feed (`TBLPROPERTIES (delta.enableChangeDataFeed = true)`) instead "
     "of relying on this column for change detection."),
]


def _map_type(raw_type: str) -> tuple[str, str | None]:
    """Map a SQL Server type string (e.g. 'NVARCHAR (50)') to a Databricks type."""
    cleaned = raw_type.strip().upper()
    cleaned = cleaned.replace("[", "").replace("]", "")
    # Extract base type token (before any '(' and before trailing modifiers)
    base_match = re.match(r"^([A-Z_\.]+)", cleaned)
    base = base_match.group(1) if base_match else cleaned
    # Extract precision/scale if present, e.g. NVARCHAR(50) -> (50), DECIMAL(18,2) -> (18,2)
    precision_match = re.search(r"\((\s*\d+\s*(?:,\s*\d+\s*)?)\)", cleaned)
    precision = precision_match.group(1).replace(" ", "") if precision_match else None

    for pattern, target, note in TYPE_MAP:
        if re.match(pattern, base):
            if target == "STRING" and precision and "VARCHAR" in base or "CHAR" in base:
                return "STRING", note  # Spark STRING has no length bound; length is dropped intentionally
            if target == "DECIMAL" and precision:
                return f"DECIMAL({precision})", note
            return target, note
    return "STRING", f"Unrecognised SQL Server type '{raw_type}' — defaulted to STRING. MANUAL REVIEW REQUIRED."


# ---------------------------------------------------------------------------
# Column / DDL parsing (more robust than the inventory's lightweight extractor —
# needed here because correctness of type mapping is the whole point of this step)
# ---------------------------------------------------------------------------

def _split_top_level(body: str) -> list[str]:
    """Split a CREATE TABLE column-list body on top-level commas (respecting parens)."""
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in body:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current))
    return [p.strip() for p in parts if p.strip()]


def _extract_table_body(raw_ddl: str) -> str | None:
    m = re.search(r"CREATE\s+TABLE\s+[\[\w\]\.]+\s*\((.*)\)\s*(?:WITH|;|\Z)", raw_ddl,
                  re.IGNORECASE | re.DOTALL)
    if not m:
        m = re.search(r"CREATE\s+TABLE\s+[\[\w\]\.]+\s*\((.*)\)", raw_ddl, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    body = m.group(1)
    # Trim trailing content after the matching close-paren of the column list itself.
    depth = 1
    for i, ch in enumerate(body):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return body[:i]
    return body


_CONSTRAINT_KEYWORDS = ("CONSTRAINT", "PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK", "PERIOD FOR")


def parse_table_columns(raw_ddl: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (columns, constraint_lines) parsed directly from raw DDL."""
    body = _extract_table_body(raw_ddl)
    if not body:
        return [], []
    columns: list[dict[str, Any]] = []
    constraints: list[str] = []
    for item in _split_top_level(body):
        stripped = item.strip()
        upper = stripped.upper()
        if any(upper.startswith(kw) for kw in _CONSTRAINT_KEYWORDS):
            constraints.append(stripped)
            continue
        # Column definition: [Name] TYPE ... or Name TYPE ...
        # TYPE may be schema-qualified and bracketed per-segment, e.g. [sys].[geography].
        m = re.match(
            r"^\[?([\w\s]+?)\]?\s+((?:\[?\w+\]?\.)*\[?\w+\]?(?:\s*\(\s*\d+\s*(?:,\s*\d+)?\s*\))?)(.*)$",
            stripped, re.DOTALL,
        )
        if not m:
            continue
        name = m.group(1).strip()
        col_type = m.group(2).strip()
        rest = m.group(3).strip()
        is_nullable = "NOT NULL" not in rest.upper()
        is_system_versioned = bool(re.search(r"GENERATED\s+ALWAYS\s+AS\s+ROW", rest, re.IGNORECASE))
        has_default = bool(re.search(r"\bDEFAULT\b", rest, re.IGNORECASE))
        is_identity = bool(re.search(r"\bIDENTITY\b|\bNEXT\s+VALUE\s+FOR\b", rest, re.IGNORECASE))
        columns.append({
            "name": name,
            "sql_type": col_type,
            "nullable": is_nullable,
            "system_versioned": is_system_versioned,
            "has_default": has_default,
            "is_identity_like": is_identity,
        })
    return columns, constraints


# ---------------------------------------------------------------------------
# Table conversion
# ---------------------------------------------------------------------------

def convert_table(obj: dict[str, Any], target_fqn: str) -> dict[str, Any]:
    raw_ddl = obj.get("raw_ddl") or ""
    columns, constraints = parse_table_columns(raw_ddl)
    warnings: list[str] = []
    col_lines: list[str] = []

    for col in columns:
        if col["system_versioned"]:
            warnings.append(
                f"Column `{col['name']}` is a SQL Server system-versioning period column "
                "(GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta "
                "Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's "
                "semantics — Time Travel returns the whole table's state at a commit, while this "
                "column tracks each row's own validity window independent of write/commit history. "
                "Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an "
                "explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR "
                "valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not "
                "replaced with Delta Time Travel. MANUAL REVIEW REQUIRED."
            )
            continue
        target_type, note = _map_type(col["sql_type"])
        if note:
            warnings.append(f"Column `{col['name']}` ({col['sql_type']} -> {target_type}): {note}")
        nullability = "" if col["nullable"] else " NOT NULL"
        comment = f" COMMENT 'source type: {col['sql_type']}'" if note else ""
        col_lines.append(f"    {_safe_ident(col['name'])} {target_type}{nullability}{comment}")
        if col["is_identity_like"]:
            warnings.append(
                f"Column `{col['name']}` used IDENTITY/NEXT VALUE FOR in the source — replace with "
                "a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step "
                "in the loading pipeline (see target_state_architecture.md, Unity Catalog section)."
            )

    is_temporal = any(re.search(r"PERIOD\s+FOR\s+SYSTEM_TIME", c, re.IGNORECASE) for c in constraints)
    is_memory_optimized = "MEMORY_OPTIMIZED" in obj.get("table_features", [])
    is_partitioned = "PARTITIONED" in obj.get("table_features", [])

    fks = [c for c in constraints if c.upper().startswith("FOREIGN KEY") or "FOREIGN KEY" in c.upper()]
    for fk in fks:
        warnings.append(f"Foreign key not enforced by Delta Lake (informational only): {fk.strip()[:120]}")
    if is_memory_optimized:
        warnings.append(
            "Source table was MEMORY_OPTIMIZED (SQL Server In-Memory OLTP) — no Delta Lake "
            "equivalent. Converted to a standard Delta table; if sub-millisecond OLTP-style "
            "access was relied upon, this workload may not be a good fit for Delta and should "
            "be redesigned (see manual_intervention_list.md)."
        )
    if is_temporal:
        warnings.append(
            "Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive "
            "table). Recommended replacement: enable `delta.enableChangeDataFeed` and query "
            "history via `TIMESTAMP AS OF` / `VERSION AS OF`, or `table_changes()`. The paired "
            "_Archive table is converted separately and should be reconciled with this table's "
            "Delta history rather than kept as a second physical table long-term."
        )

    layer = obj.get("medallion_layer", "BRONZE")
    ddl_lines = [
        f"-- Source: {obj['id']}  ({obj.get('source_file', '')})",
        "-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses",
        "-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or",
        "-- flagged below rather than silently dropped.",
        "",
        f"CREATE TABLE IF NOT EXISTS {target_fqn} (",
    ]
    ddl_lines.append(",\n".join(col_lines))
    ddl_lines.append(")")
    ddl_lines.append("USING DELTA")
    if is_partitioned:
        ddl_lines.append("-- TODO: confirm partition column from source PARTITION SCHEME before enabling:")
        ddl_lines.append("-- PARTITIONED BY (<date_or_period_column>)")
    ddl_lines.append(f"COMMENT 'Converted from {obj['id']}'")
    ddl_lines.append("TBLPROPERTIES (")
    ddl_lines.append("  'delta.enableChangeDataFeed' = 'true'")
    ddl_lines.append(");")
    ddl_lines.append("")
    if warnings:
        ddl_lines.append("-- Conversion notes:")
        for w in warnings:
            for wrapped in _wrap_comment(w):
                ddl_lines.append(f"-- {wrapped}")

    sql_text = "\n".join(ddl_lines)
    needs_review = is_memory_optimized or any("MANUAL REVIEW REQUIRED" in w for w in warnings)
    return {"sql": sql_text, "warnings": warnings, "needs_review": needs_review, "layer": layer}


# ---------------------------------------------------------------------------
# View conversion (also covers "materialized view" requirement — see note)
# ---------------------------------------------------------------------------

_SYNTAX_REWRITES: list[tuple[str, str]] = [
    (r"\bISNULL\s*\(", "COALESCE("),
    (r"\bGETDATE\s*\(\s*\)", "current_timestamp()"),
    (r"\bGETUTCDATE\s*\(\s*\)", "current_timestamp()"),
    (r"\bLEN\s*\(", "LENGTH("),
    (r"\bTOP\s+\((\d+)\)", r"LIMIT \1"),  # best-effort; correct LIMIT placement needs manual check
    (r"\[(\w+)\]", r"`\1`"),  # bracket identifiers -> backtick identifiers
]

_UNSUPPORTED_VIEW_PATTERNS = [
    (r"\bFOR\s+XML\b", "FOR XML has no Spark SQL equivalent — reimplement with to_json()/struct() or move to PySpark."),
    (r"\bFOR\s+JSON\b", "FOR JSON has no direct Spark SQL equivalent — reimplement with to_json(struct(...))."),
    (r"\bPIVOT\b|\bUNPIVOT\b", "PIVOT/UNPIVOT syntax differs in Spark SQL — rewrite using Spark's PIVOT (supported but with different aggregate-function placement) or melt-style PySpark code."),
    (r"\bOPENROWSET\b|\bOPENDATASOURCE\b|\bLINKED\s+SERVER\b", "Cross-server queries have no equivalent — replace with a Delta table read or Lakehouse Federation connection."),
    (r"\bFOR\s+SYSTEM_TIME\b", "Temporal AS OF queries map to Delta `VERSION AS OF`/`TIMESTAMP AS OF` with different syntax — rewrite required."),
    (r"\bAPPLY\b", "CROSS/OUTER APPLY has a Spark SQL LATERAL VIEW equivalent but requires restructuring — manual rewrite required."),
]


def convert_view(obj: dict[str, Any], target_fqn: str) -> dict[str, Any]:
    raw_ddl = obj.get("raw_ddl") or ""
    body_match = re.search(r"CREATE\s+(?:OR\s+ALTER\s+)?VIEW\s+[\[\w\]\.]+\s*(?:\([^)]*\)\s*)?AS\s*(.*)",
                            raw_ddl, re.IGNORECASE | re.DOTALL)
    body = body_match.group(1).strip() if body_match else raw_ddl

    warnings: list[str] = []
    for pattern, note in _UNSUPPORTED_VIEW_PATTERNS:
        if re.search(pattern, body, re.IGNORECASE):
            warnings.append(note)

    # Only warn about TOP/LIMIT non-determinism when TOP is actually present
    # without an ORDER BY — previously this caveat was printed unconditionally
    # on every converted view, training reviewers to ignore it as boilerplate.
    has_top = bool(re.search(r"\bTOP\s*\(", body, re.IGNORECASE))
    has_order_by = bool(re.search(r"\bORDER\s+BY\b", body, re.IGNORECASE))
    if has_top and not has_order_by:
        warnings.append(
            "TOP(n) used without an ORDER BY — both T-SQL TOP and Spark LIMIT are "
            "non-deterministic without one; add an explicit ORDER BY if row selection must be stable."
        )

    converted_body = body
    for pattern, repl in _SYNTAX_REWRITES:
        converted_body = re.sub(pattern, repl, converted_body, flags=re.IGNORECASE)
    converted_body = re.sub(r";\s*$", "", converted_body.strip())

    needs_review = len(warnings) > 0
    sql_lines = [
        f"-- Source: {obj['id']}  ({obj.get('source_file', '')})",
        "-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax",
        "-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),",
        "-- TOP(n)->LIMIT n).",
        "",
        f"CREATE OR REPLACE VIEW {target_fqn} AS",
        converted_body,
        ";",
    ]
    if warnings:
        sql_lines.append("")
        sql_lines.append("-- UNRESOLVED — manual rewrite required:")
        for w in warnings:
            for wrapped in _wrap_comment(w):
                sql_lines.append(f"-- {wrapped}")

    return {"sql": "\n".join(sql_lines), "warnings": warnings, "needs_review": needs_review,
            "layer": obj.get("medallion_layer", "GOLD")}


# ---------------------------------------------------------------------------
# Function conversion
# ---------------------------------------------------------------------------

def convert_function(obj: dict[str, Any], target_fqn: str) -> dict[str, Any]:
    raw_ddl = obj.get("raw_ddl") or ""
    otype = obj.get("object_type")
    warnings: list[str] = []

    declare_count = len(re.findall(r"\bDECLARE\b", raw_ddl, re.IGNORECASE))
    has_procedural = bool(re.search(
        r"\bWHILE\b|\bCURSOR\b|\bIS_ROLEMEMBER\b|\bEXEC(?:UTE)?\s*\(|\bIF\b|\bSET\b",
        raw_ddl, re.IGNORECASE,
    )) or declare_count > 1

    if otype == "SCALAR_FUNCTION" and not has_procedural:
        body_match = re.search(r"\bRETURN\s+(.*?);?\s*END\s*;?\s*\Z", raw_ddl, re.IGNORECASE | re.DOTALL)
        expr = body_match.group(1).strip() if body_match else None
        if expr:
            converted_expr = expr
            for pattern, repl in _SYNTAX_REWRITES:
                converted_expr = re.sub(pattern, repl, converted_expr, flags=re.IGNORECASE)
            sql_lines = [
                f"-- Source: {obj['id']}  ({obj.get('source_file', '')})",
                "-- Converted: SCALAR_FUNCTION -> Databricks SQL UDF (single-expression RETURN body).",
                "",
                f"CREATE OR REPLACE FUNCTION {target_fqn}(<TODO: parameter list from source>)",
                "RETURNS STRING -- TODO: confirm return type mapping from source RETURNS clause",
                "RETURN",
                f"  {converted_expr};",
            ]
            warnings.append("Parameter list and return type were not auto-extracted — fill in from source DDL before deploying.")
            return {"sql": "\n".join(sql_lines), "warnings": warnings, "needs_review": True,
                    "layer": obj.get("medallion_layer", "SILVER")}

    # Procedural function (uses control flow, security functions, IS_ROLEMEMBER, etc.)
    # or an inline TVF with a non-trivial body -> PySpark UDF stub.
    if has_procedural:
        warnings.append("Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, "
                         "WHILE, CURSOR) with no SQL UDF equivalent — converted to a PySpark UDF "
                         "stub requiring manual implementation of the equivalent access-control or "
                         "looping logic using Unity Catalog row/column-level security or PySpark "
                         "control flow.")
    py_lines = [
        f"# Source: {obj['id']}  ({obj.get('source_file', '')})",
        f"# Converted: {otype} -> PySpark function (registered as a UDF where needed).",
        "# Original T-SQL body is reproduced as a comment for reference; logic must be",
        "# re-implemented in Python below.",
        "#",
        "# --- original T-SQL ---",
    ]
    for line in raw_ddl.strip().splitlines():
        py_lines.append(f"# {line}")
    py_name = _py_ident(obj['name'])
    py_lines += [
        "# --- end original T-SQL ---",
        "",
        "# NOTE: the source function's callers invoke it inline inside T-SQL SELECT",
        "# statements (not as a separate batch step) — registering it as a SQL UDF",
        "# (not just a DataFrame-API udf object) preserves that inline-SQL-callable",
        "# shape. Found by adversarial review: a bare `udf(...)` object is only",
        "# usable from PySpark DataFrame code, which would force every original",
        "# inline-SQL caller to be rewritten as a separate join/precompute step.",
        "from pyspark.sql import SparkSession",
        "from pyspark.sql.functions import udf",
        "from pyspark.sql.types import StringType",
        "",
        "spark = SparkSession.getActiveSession()",
        "",
        "",
        f"def {py_name}(*args):",
        "    \"\"\"TODO: implement equivalent logic to the source T-SQL function above.\"\"\"",
        "    raise NotImplementedError('Manual conversion required — see source T-SQL above.')",
        "",
        "",
        f"{py_name}_udf = udf({py_name}, StringType())  # TODO: confirm return type from source RETURNS clause",
        f"spark.udf.register({obj['name']!r}, {py_name}, StringType())  # makes it callable from Databricks SQL as {obj['name']}(...)",
    ]
    warnings.append(
        f"Original function is called inline from T-SQL SELECT statements — registered via "
        f"spark.udf.register('{obj['name']}', ...) so it remains SQL-callable after conversion, "
        f"rather than only usable from PySpark DataFrame code."
    )
    return {"pyspark": "\n".join(py_lines), "warnings": warnings, "needs_review": True,
            "layer": obj.get("medallion_layer", "SILVER")}


# ---------------------------------------------------------------------------
# Stored procedure conversion — including orchestration/logic split (rule 4)
# ---------------------------------------------------------------------------

_ORCHESTRATION_SEMANTICS = {"CUTOFF_WINDOW", "STAGING_TO_DW", "LINEAGE_TRACKING", "ORCHESTRATION"}


def _is_orchestration_heavy(obj: dict[str, Any]) -> bool:
    return bool(set(obj.get("etl_semantics", [])) & _ORCHESTRATION_SEMANTICS) or obj.get("schema") == "Integration"


def _extract_core_dml(raw_ddl: str) -> list[str]:
    """Best-effort extraction of top-level SELECT/INSERT/UPDATE/DELETE/MERGE statements."""
    body_match = re.search(r"\bAS\b\s*BEGIN(.*)END\s*;?\s*\Z", raw_ddl, re.IGNORECASE | re.DOTALL)
    body = body_match.group(1) if body_match else raw_ddl
    statements: list[str] = []
    for stmt_match in re.finditer(
        r"((?:INSERT|UPDATE|DELETE|MERGE)\b.*?;)", body, re.IGNORECASE | re.DOTALL
    ):
        statements.append(stmt_match.group(1).strip())
    return statements


def convert_procedure(obj: dict[str, Any], classification: str, target_fqn: str) -> dict[str, Any]:
    raw_ddl = obj.get("raw_ddl") or ""
    warnings: list[str] = []
    procedural_factors = []
    for pattern, label in [
        (r"\bCURSOR\b", "CURSOR — row-by-row processing; rewrite as a set-based DataFrame "
                         "transformation (groupBy/window functions) or, if truly row-oriented, a "
                         "Python loop over a collected (small) result set."),
        (r"\bWHILE\b", "WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating "
                        "a small fixed list (e.g. years), a Python for-loop generating one MERGE "
                        "per iteration."),
        (r"\bsp_executesql\b|\bEXEC\s*\(", "Dynamic SQL — rewrite using PySpark/Python string "
                        "templating with parameter binding, or Databricks SQL parameter markers; "
                        "never string-concatenate untrusted input."),
        (r"#\w+", "Temp table — replace with a PySpark DataFrame (if used only within the procedure "
                  "body) or a Delta table in a scratch/staging schema (if state must persist across steps)."),
        (r"\bTRY\b.*\bCATCH\b", "TRY/CATCH — replace with Python try/except in the PySpark task, or "
                                 "Workflow task-level retry/failure handling."),
        (r"\bOPENJSON\b", "OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() "
                           "against an explicit schema derived from the source's WITH clause column list. "
                           "MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL."),
    ]:
        if re.search(pattern, raw_ddl, re.IGNORECASE | re.DOTALL):
            procedural_factors.append(label)

    # MERGE targeting a non-persistent rowset (table variable / temp table) has
    # no Delta MERGE INTO equivalent at all — flag this combination specifically
    # rather than letting the generic "Temp table" warning above imply a literal
    # MERGE INTO translation is viable.
    merge_target_match = re.search(r"\bMERGE\s+(@\w+|#\w+)\b", raw_ddl, re.IGNORECASE)
    if merge_target_match:
        procedural_factors.append(
            f"MERGE against non-persistent target `{merge_target_match.group(1)}` (table variable/temp "
            "table) — there is no Delta table to MERGE INTO. Rewrite as an in-memory accumulation "
            "pattern (e.g. groupBy().agg(sum(...))) over the per-row values, not a literal MERGE INTO."
        )
    if re.search(r"\bUPDATE\s+SET\b[^;]*[+\-*/]=", raw_ddl, re.IGNORECASE):
        procedural_factors.append(
            "Compound assignment operator (+=/-=/etc.) inside UPDATE SET — Spark MERGE INTO has no "
            "compound-assignment syntax; expand to `col = target.col <op> source.val` explicitly."
        )

    is_orchestration_heavy = _is_orchestration_heavy(obj)
    files: dict[str, str] = {}

    if classification in ("LIFT_AND_SHIFT", "PARTIAL_AUTOMATION") and not procedural_factors:
        # Pure set-based logic -> Databricks SQL only.
        core_dml = _extract_core_dml(raw_ddl)
        if not core_dml:
            # Safety net: an "empty" conversion (no statement our regex-based
            # extractor recognised) is never safe to mark needs_review=False —
            # it most likely means an unrecognised construct (e.g. OPENJSON's
            # WITH-clause rowset shape) defeated extraction, not that the
            # procedure has no logic. A silent empty file with no review flag
            # was found, by adversarial review, to produce a deployed no-op.
            warnings.append(
                "No executable SQL statement could be extracted from this procedure's body — "
                "this usually means it uses a construct our extractor doesn't recognise (e.g. "
                "OPENJSON, a non-standard DML shape) rather than that it has no logic. "
                "MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op."
            )
            sql_lines = [
                f"-- Source: {obj['id']}  ({obj.get('source_file', '')})",
                "-- Converted: PROCEDURE -> Databricks SQL — NO EXECUTABLE STATEMENT EXTRACTED.",
                "-- This is NOT a safe empty conversion. See warnings below before deploying.",
                "",
                "-- TODO: no top-level DML auto-extracted; review source body manually.",
                "",
                "-- Conversion notes:",
                f"-- {warnings[-1]}",
            ]
            files["databricks_sql"] = "\n".join(sql_lines)
            layer = obj.get("medallion_layer", "BRONZE")
            return {"files": files, "warnings": warnings, "needs_review": True, "layer": layer,
                    "split": False}

        converted = "\n\n".join(core_dml)
        for pattern, repl in _SYNTAX_REWRITES:
            converted = re.sub(pattern, repl, converted, flags=re.IGNORECASE)
        sql_lines = [
            f"-- Source: {obj['id']}  ({obj.get('source_file', '')})",
            "-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural",
            "-- constructs detected; safe to express as set-based SQL).",
            "",
            converted,
        ]
        files["databricks_sql"] = "\n".join(sql_lines)
        layer = obj.get("medallion_layer", "BRONZE")
        return {"files": files, "warnings": warnings, "needs_review": False, "layer": layer,
                "split": False}

    if is_orchestration_heavy:
        # Rule 4: split into SQL transformation logic + workflow orchestration logic.
        core_dml = _extract_core_dml(raw_ddl)
        body_sql = "\n\n".join(core_dml) if core_dml else "-- TODO: no top-level DML auto-extracted; review source body and CURSOR loop body above."
        converted = body_sql
        for pattern, repl in _SYNTAX_REWRITES:
            converted = re.sub(pattern, repl, converted, flags=re.IGNORECASE)
        sql_lines = [
            f"-- Source: {obj['id']}  ({obj.get('source_file', '')})",
            "-- Split 1 of 2: SQL transformation logic extracted from an orchestration-heavy",
            "-- stored procedure (rule: separate SQL transformation from workflow orchestration).",
            "-- The CURSOR/WHILE control flow that drove row-by-row iteration in the source is",
            "-- NOT reproduced here — see the companion PySpark orchestration file, which expresses",
            "-- the same iteration as a set-based MERGE or a small parameterised loop.",
            "",
            converted if core_dml else f"-- {converted}",
        ]
        files["databricks_sql"] = "\n".join(sql_lines)

        py_lines = [
            f"# Source: {obj['id']}  ({obj.get('source_file', '')})",
            "# Split 2 of 2: Workflow/task orchestration logic for an orchestration-heavy procedure.",
            "# This is the Databricks Workflow task entry point — it owns parameter handling,",
            "# watermark read/advance, and invoking the companion SQL transformation logic.",
            "# See orchestration_design.md for how this fits into the per-entity Workflow job.",
            "",
            "from pyspark.sql import SparkSession",
            "",
            "spark = SparkSession.getActiveSession()",
            "",
            "",
            "def run(last_cutoff: str, new_cutoff: str) -> None:",
            f"    \"\"\"Orchestration entry point for {obj['name']}.",
            "",
            "    TODO: implement the per-row iteration that the source CURSOR/WHILE loop performed,",
            "    either as a single set-based MERGE (preferred) or, if genuinely row-dependent",
            "    (e.g. each iteration depends on the previous one's output), as a bounded Python loop.",
            "    \"\"\"",
            "    # 1. Read watermark range [last_cutoff, new_cutoff) — see ops.etl_watermark table.",
            "    # 2. Execute the companion SQL transformation logic (see databricks_sql output).",
            "    # 3. Advance the watermark only after step 2 succeeds (atomic with the data write).",
            "    raise NotImplementedError('Manual conversion required — see source T-SQL and "
            "design notes above.')",
        ]
        files["pyspark"] = "\n".join(py_lines)
        warnings.extend(procedural_factors)
        warnings.append("Orchestration-heavy procedure split per conversion rule 4: SQL "
                         "transformation logic and workflow orchestration logic are emitted as "
                         "separate files.")
        layer = obj.get("medallion_layer", "BRONZE")
        return {"files": files, "warnings": warnings, "needs_review": True, "layer": layer, "split": True}

    # Rewrite-required / manual-redesign, not orchestration-heavy -> single PySpark stub.
    py_lines = [
        f"# Source: {obj['id']}  ({obj.get('source_file', '')})",
        "# Converted: PROCEDURE -> PySpark (procedural constructs preclude a direct SQL mapping).",
        "# Original T-SQL body is reproduced as a comment for reference.",
        "#",
        "# --- original T-SQL (truncated to 4000 chars) ---",
    ]
    for line in raw_ddl.strip()[:4000].splitlines():
        py_lines.append(f"# {line}")
    py_lines += [
        "# --- end original T-SQL ---",
        "",
        "from pyspark.sql import SparkSession",
        "",
        "spark = SparkSession.getActiveSession()",
        "",
        "",
        f"def {_py_ident(obj['name'])}(*args, **kwargs) -> None:",
        "    \"\"\"TODO: implement equivalent logic to the source T-SQL procedure above.",
        "",
        "    Procedural constructs detected in source requiring manual redesign:",
    ]
    for factor in procedural_factors:
        py_lines.append(f"    - {factor}")
    py_lines += [
        "    \"\"\"",
        "    raise NotImplementedError('Manual conversion required — see source T-SQL above.')",
    ]
    files["pyspark"] = "\n".join(py_lines)
    warnings.extend(procedural_factors)
    layer = obj.get("medallion_layer", "BRONZE")
    return {"files": files, "warnings": warnings, "needs_review": True, "layer": layer, "split": False}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _safe_ident(name: str) -> str:
    return f"`{name}`" if re.search(r"\s|[^\w]", name) else name


def _py_ident(name: str) -> str:
    s = re.sub(r"[^\w]+", "_", name).strip("_")
    return s.lower() or "converted_function"


def _wrap_comment(text: str, width: int = 100) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 > width:
            lines.append(current)
            current = w
        else:
            current = f"{current} {w}".strip()
    if current:
        lines.append(current)
    return lines
