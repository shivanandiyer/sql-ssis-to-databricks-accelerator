"""
sql_project_parser.py
Walks an SSDT .sqlproj directory and classifies every .sql file by object type.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Regex patterns to classify the first meaningful DDL statement in a file.
# Tried in order; first match wins.
_CLASSIFIERS: list[tuple[str, str]] = [
    # Object types: check more specific patterns before generic TABLE
    (r"CREATE\s+OR\s+ALTER\s+PROCEDURE|CREATE\s+PROCEDURE",            "PROCEDURE"),
    (r"ALTER\s+PROCEDURE",                                              "PROCEDURE"),
    (r"CREATE\s+OR\s+ALTER\s+FUNCTION|CREATE\s+FUNCTION",              "FUNCTION"),
    (r"ALTER\s+FUNCTION",                                               "FUNCTION"),
    (r"CREATE\s+OR\s+ALTER\s+VIEW|CREATE\s+VIEW",                      "VIEW"),
    (r"ALTER\s+VIEW",                                                   "VIEW"),
    (r"CREATE\s+OR\s+ALTER\s+TRIGGER|CREATE\s+TRIGGER",                "TRIGGER"),
    (r"ALTER\s+TRIGGER",                                                "TRIGGER"),
    (r"CREATE\s+TABLE",                                                 "TABLE"),
    (r"ALTER\s+TABLE",                                                  "TABLE"),
    (r"CREATE\s+SCHEMA",                                                "SCHEMA"),
    (r"CREATE\s+SEQUENCE",                                              "SEQUENCE"),
    (r"CREATE\s+PARTITION\s+FUNCTION",                                  "PARTITION_FUNCTION"),
    (r"CREATE\s+PARTITION\s+SCHEME",                                    "PARTITION_SCHEME"),
    (r"CREATE\s+FILEGROUP|ALTER\s+DATABASE.*ADD\s+FILEGROUP",           "FILEGROUP"),
    (r"CREATE\s+TYPE",                                                   "USER_DEFINED_TYPE"),
    (r"CREATE\s+(UNIQUE\s+)?(CLUSTERED\s+|NONCLUSTERED\s+)?INDEX",      "INDEX"),
    (r"GRANT|DENY|REVOKE|CREATE\s+ROLE|CREATE\s+USER|ALTER\s+ROLE",    "SECURITY"),
    (r"EXECUTE\s+sp_addextendedproperty",                               "EXTENDED_PROPERTY"),
    (r"INSERT|UPDATE|DELETE|EXEC|DECLARE",                              "SCRIPT"),
]

# Function sub-types
_FUNC_SUBTYPES: list[tuple[str, str]] = [
    (r"RETURNS\s+TABLE",                                                "TVF_INLINE"),
    (r"RETURNS\s+@\w+\s+TABLE",                                        "TVF_MULTI"),
    (r"RETURNS\s+\w",                                                   "SCALAR_FUNCTION"),
]

# Table sub-types
_TABLE_FEATURES: list[tuple[str, str]] = [
    (r"WITH\s*\(\s*SYSTEM_VERSIONING\s*=\s*ON",                        "TEMPORAL"),
    (r"WITH\s*\(\s*MEMORY_OPTIMIZED\s*=\s*ON",                         "MEMORY_OPTIMIZED"),
    (r"COLUMNSTORE",                                                    "COLUMNSTORE"),
    (r"PARTITION\s+SCHEME|ON\s+\[?PS_",                               "PARTITIONED"),
]

# Columns that signal incremental / change-tracking patterns
_INCREMENTAL_SIGNALS = re.compile(
    r"\b(ValidFrom|ValidTo|LastEditedWhen|ModifiedDate|RowVersion"
    r"|WatermarkColumn|ETLCutoff|ChangeVersion)\b",
    re.IGNORECASE,
)
_SCD_SIGNALS = re.compile(
    r"\b(Valid\s*From|Valid\s*To|Is\s*Current|Current\s*Flag"
    r"|Effective\s*Date|Expiry\s*Date|SCD|Type\s*2)\b",
    re.IGNORECASE,
)

# Complexity scoring weights
_COMPLEXITY_PATTERNS: list[tuple[str, int]] = [
    (r"\bCURSOR\b",                5),
    (r"\bsp_executesql\b|\bEXEC\s*\(",  4),
    (r"\bDYNAMIC\s+SQL\b",        4),
    (r"\bFOR\s+XML\b|\bFOR\s+JSON\b", 3),
    (r"\bOPENJSON\b",              4),  # no Spark SQL equivalent; requires from_json()/explode() with an explicit schema
    (r"\bPIVOT\b|\bUNPIVOT\b",   3),
    (r"\bMERGE\b",                 2),
    (r"\bOPENROWSET\b|\bOPENDATASOURCE\b|\bLINKED\s+SERVER\b", 5),
    (r"\bFOR\s+SYSTEM_TIME\b",    3),
    (r"#\w+",                      1),  # temp table (no leading \b: '#' is non-word, so \b before it never matches)
    (r"\b@\w+\s+TABLE\b",         1),  # table variable
    (r"\bTRY\b.*\bCATCH\b",       1),
    (r"\bWHILE\b",                 1),
]

_SCORE_BANDS = [(0, "LOW"), (3, "LOW"), (6, "MEDIUM"), (10, "HIGH"), (999, "VERY_HIGH")]


def _score_complexity(sql: str) -> tuple[str, int, list[str]]:
    factors: list[str] = []
    score = 0
    for pattern, weight in _COMPLEXITY_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            score += weight
            label = pattern.replace("\\b", "").split("|")[0].strip()
            factors.append(f"{label}(+{weight})")
    band = "LOW"
    for threshold, label in _SCORE_BANDS:
        if score >= threshold:
            band = label
    return band, score, factors


def _extract_object_name(sql: str, obj_type: str) -> tuple[str, str]:
    """Return (schema, name) from a CREATE/ALTER DDL statement."""
    patterns = {
        "TABLE":     r"CREATE\s+TABLE\s+\[?(\w+)\]?\.\[?(\w+)\]?",
        "VIEW":      r"CREATE\s+(?:OR\s+ALTER\s+)?VIEW\s+\[?(\w+)\]?\.\[?(\w+)\]?",
        "PROCEDURE": r"CREATE\s+(?:OR\s+ALTER\s+)?PROCEDURE\s+\[?(\w+)\]?\.\[?(\w+)\]?",
        "FUNCTION":  r"CREATE\s+(?:OR\s+ALTER\s+)?FUNCTION\s+\[?(\w+)\]?\.\[?(\w+)\]?",
        "TRIGGER":   r"CREATE\s+(?:OR\s+ALTER\s+)?TRIGGER\s+\[?(\w+)\]?\.\[?(\w+)\]?",
        "SEQUENCE":  r"CREATE\s+SEQUENCE\s+\[?(\w+)\]?\.\[?(\w+)\]?",
        "USER_DEFINED_TYPE": r"CREATE\s+TYPE\s+\[?(\w+)\]?\.\[?(\w+)\]?",
    }
    # Function subtypes are refined after classification but must resolve via
    # the same CREATE FUNCTION pattern as the base type.
    patterns["SCALAR_FUNCTION"] = patterns["FUNCTION"]
    patterns["TVF_INLINE"] = patterns["FUNCTION"]
    patterns["TVF_MULTI"] = patterns["FUNCTION"]
    pat = patterns.get(obj_type)
    if pat:
        m = re.search(pat, sql, re.IGNORECASE)
        if m:
            return m.group(1), m.group(2)
    # Fallback: single-part name
    single = re.search(r"CREATE\s+\w+(?:\s+\w+)?\s+\[?(\w+)\]?", sql, re.IGNORECASE)
    return "dbo", single.group(1) if single else "UNKNOWN"


def _extract_references(sql: str) -> dict[str, list[str]]:
    """Extract FROM/JOIN/EXEC object references from SQL body."""
    tables: list[str] = []
    procs:  list[str] = []
    funcs:  list[str] = []

    # FROM and JOIN references: [schema].[name] or schema.name
    for m in re.finditer(
        r"(?:FROM|JOIN)\s+\[?(\w+)\]?\.\[?(\w+)\]?", sql, re.IGNORECASE
    ):
        ref = f"{m.group(1)}.{m.group(2)}"
        if ref not in tables:
            tables.append(ref)

    # EXEC / EXECUTE references
    for m in re.finditer(
        r"EXEC(?:UTE)?\s+\[?(\w+)\]?\.\[?(\w+)\]?", sql, re.IGNORECASE
    ):
        ref = f"{m.group(1)}.{m.group(2)}"
        if ref not in procs:
            procs.append(ref)

    # Function calls: schema.name(
    for m in re.finditer(
        r"\b(\w+)\.(\w+)\s*\(", sql, re.IGNORECASE
    ):
        ref = f"{m.group(1)}.{m.group(2)}"
        if ref not in funcs and ref not in procs:
            funcs.append(ref)

    return {"tables": tables, "procedures": procs, "functions": funcs}


def _extract_columns(sql: str) -> list[dict[str, str]]:
    """Very lightweight column extractor from CREATE TABLE DDL."""
    columns: list[dict[str, str]] = []
    in_table_body = False
    for line in sql.splitlines():
        stripped = line.strip()
        if re.match(r"CREATE\s+TABLE", stripped, re.IGNORECASE):
            in_table_body = True
            continue
        if in_table_body:
            if stripped.startswith(("CONSTRAINT", ")")):
                continue
            m = re.match(r"\[?(\w[\w\s]*?)\]?\s+(\w[\w\s\(\),]*?)(?:\s+(?:NOT\s+NULL|NULL|IDENTITY|DEFAULT|CONSTRAINT).*)?$", stripped, re.IGNORECASE)
            if m:
                columns.append({"name": m.group(1).strip(), "type": m.group(2).strip()})
    return columns


def classify_sql_file(path: Path, source_project: str = "UNKNOWN") -> dict[str, Any]:
    """
    Read a single .sql file and return a canonical SourceObject dict.
    """
    try:
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as exc:
        return {"id": str(path), "error": str(exc), "object_type": "UNREADABLE"}

    # Strip comments for classification (keep raw DDL intact)
    clean = re.sub(r"--[^\n]*", "", raw)
    clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL)

    obj_type = "UNKNOWN"
    for pattern, otype in _CLASSIFIERS:
        if re.search(pattern, clean, re.IGNORECASE):
            obj_type = otype
            break

    # Refine function sub-type
    if obj_type == "FUNCTION":
        for pat, subtype in _FUNC_SUBTYPES:
            if re.search(pat, clean, re.IGNORECASE):
                obj_type = subtype
                break
        else:
            obj_type = "SCALAR_FUNCTION"

    # Refine table features
    table_features: list[str] = []
    if obj_type == "TABLE":
        for pat, feat in _TABLE_FEATURES:
            if re.search(pat, clean, re.IGNORECASE):
                table_features.append(feat)

    schema, name = _extract_object_name(clean, obj_type)
    refs = _extract_references(clean)
    complexity_band, complexity_score, complexity_factors = _score_complexity(clean)

    # ETL semantic detection
    etl_semantics: list[str] = []
    if _INCREMENTAL_SIGNALS.search(clean):
        etl_semantics.append("INCREMENTAL")
    if _SCD_SIGNALS.search(clean):
        etl_semantics.append("SCD2")
    if re.search(r"\bMERGE\b", clean, re.IGNORECASE):
        etl_semantics.append("MERGE_PATTERN")
    if re.search(r"TRUNCATE\s+TABLE", clean, re.IGNORECASE):
        etl_semantics.append("FULL_LOAD")
    if re.search(r"\bGetLastETLCutoffTime\b|\bETL\s+Cutoff\b|\bCutoffTime\b", clean, re.IGNORECASE):
        etl_semantics.append("CUTOFF_WINDOW")

    # Folder-derived conventions
    parts = path.parts
    folder_schema = None
    for p in parts:
        if p in ("Tables", "Views", "Stored Procedures", "Functions", "Sequences",
                 "User Defined Types", "Security"):
            folder_schema = p
            break

    obj_id = f"{source_project}:{schema}.{name}"

    return {
        "id":                 obj_id,
        "name":               name,
        "schema":             schema,
        "object_type":        obj_type,
        "source_project":     source_project,
        "source_file":        str(path),
        "raw_ddl":            raw,
        "references":         refs,
        "table_features":     table_features,
        "etl_semantics":      etl_semantics,
        "complexity_band":    complexity_band,
        "complexity_score":   complexity_score,
        "complexity_factors": complexity_factors,
        "columns":            _extract_columns(clean) if obj_type == "TABLE" else [],
        "folder_type":        folder_schema,
        "folder_path":        str(path.parent.relative_to(path.parents[4]) if len(path.parts) > 4 else path.parent),
    }


def parse_sqlproj(project_dir: Path, source_project: str = "UNKNOWN") -> list[dict[str, Any]]:
    """
    Walk a .sqlproj project directory, classify every .sql file,
    and return a list of canonical object dicts.
    """
    objects: list[dict[str, Any]] = []
    seen_index: dict[str, int] = {}

    for sql_path in sorted(project_dir.rglob("*.sql")):
        obj = classify_sql_file(sql_path, source_project)
        # Deduplicate by id (same object may appear via ALTER + CREATE). Found
        # by adversarial review: silently discarding the second file means a
        # future source repo that splits CREATE/ALTER across files would lose
        # schema changes with zero trace anywhere. The first file processed
        # (alphabetical) is kept as the canonical definition; any further
        # files for the same id are recorded on it (not silently dropped) so
        # the gap is at least visible in inventory.json.
        if obj["id"] in seen_index:
            kept = objects[seen_index[obj["id"]]]
            kept.setdefault("duplicate_definition_files", []).append(str(sql_path))
            continue
        seen_index[obj["id"]] = len(objects)
        objects.append(obj)

    return objects
