"""
ssis_parser.py
Parses SSIS .dtsx packages and .conmgr connection manager files into
canonical dicts consumed by inventory_builder and dependency_graph.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# XML namespace used throughout .dtsx files
DTS_NS = "www.microsoft.com/SqlServer/Dts"
SQL_NS = "www.microsoft.com/sqlserver/dts/tasks/sqltask"
NS = {"DTS": DTS_NS, "SQLTask": SQL_NS}

# SSIS ExecutableType → normalised task category
_TASK_TYPE_MAP: dict[str, str] = {
    "Microsoft.Pipeline":        "DATA_FLOW",
    "Microsoft.ExecuteSQLTask":  "EXECUTE_SQL",
    "Microsoft.ExpressionTask":  "EXPRESSION",
    "Microsoft.BulkInsertTask":  "BULK_INSERT",
    "Microsoft.ScriptTask":      "SCRIPT",
    "Microsoft.SendMailTask":    "SEND_MAIL",
    "Microsoft.FileSystemTask":  "FILE_SYSTEM",
    "Microsoft.FtpTask":         "FTP",
    "Microsoft.WebServiceTask":  "WEB_SERVICE",
    "STOCK:SEQUENCE":            "SEQUENCE_CONTAINER",
    "STOCK:FORLOOP":             "FOR_LOOP",
    "STOCK:FOREACH":             "FOREACH_LOOP",
    "Microsoft.Package":         "PACKAGE",
}

# OLE DB component class IDs → friendly names
_COMPONENT_MAP: dict[str, str] = {
    "Microsoft.OLEDBSource":       "OLE_DB_SOURCE",
    "Microsoft.OLEDBDestination":  "OLE_DB_DESTINATION",
    "Microsoft.DerivedColumn":     "DERIVED_COLUMN",
    "Microsoft.ConditionalSplit":  "CONDITIONAL_SPLIT",
    "Microsoft.Lookup":            "LOOKUP",
    "Microsoft.Aggregate":         "AGGREGATE",
    "Microsoft.Sort":              "SORT",
    "Microsoft.DataConversion":    "DATA_CONVERSION",
    "Microsoft.MergeJoin":         "MERGE_JOIN",
    "Microsoft.UnionAll":          "UNION_ALL",
    "Microsoft.ScriptComponent":   "SCRIPT_COMPONENT",
    "Microsoft.RowCount":          "ROW_COUNT",
    "Microsoft.Multicast":         "MULTICAST",
    "Microsoft.FuzzyLookup":       "FUZZY_LOOKUP",
    "Microsoft.FuzzyGrouping":     "FUZZY_GROUPING",
    "Microsoft.OLEDBCommand":      "OLE_DB_COMMAND",
    "Microsoft.FlatFileSource":    "FLAT_FILE_SOURCE",
    "Microsoft.FlatFileDestination": "FLAT_FILE_DESTINATION",
    "Microsoft.SlowlyChangingDimension": "SCD",
}

# Patterns that must be flagged as unsupported or HIGH-risk
_UNSUPPORTED_COMPONENTS = {"SCRIPT_COMPONENT", "FUZZY_LOOKUP", "FUZZY_GROUPING", "SCD"}
_MANUAL_TASK_TYPES = {"SCRIPT", "FTP", "WEB_SERVICE", "SEND_MAIL"}


def _tag(local: str) -> str:
    return f"{{{DTS_NS}}}{local}"


def _attr(el: ET.Element, local: str) -> str:
    return el.get(f"{{{DTS_NS}}}{local}", "")


def parse_conmgr(path: Path) -> dict[str, Any]:
    """Parse a .conmgr file → connection manager dict."""
    tree = ET.parse(path)
    root = tree.getroot()
    obj_data = root.find(f"{{{DTS_NS}}}ObjectData/{{{DTS_NS}}}ConnectionManager")
    conn_str = obj_data.get(f"{{{DTS_NS}}}ConnectionString", "") if obj_data is not None else ""

    # Extract Initial Catalog and Data Source from OLE DB connection string
    catalog = re.search(r"Initial Catalog=([^;]+)", conn_str)
    server  = re.search(r"Data Source=([^;]+)", conn_str)

    return {
        "id":              _attr(root, "ObjectName"),
        "guid":            _attr(root, "DTSID"),
        "type":            _attr(root, "CreationName"),          # e.g. "OLEDB"
        "connection_string": conn_str,
        "server":          server.group(1).strip() if server else None,
        "database":        catalog.group(1).strip() if catalog else None,
        "source_file":     str(path),
    }


def _parse_data_flow(pipeline_el: ET.Element, task_ref_id: str) -> dict[str, Any]:
    """Extract components from a <pipeline> element inside a Data Flow Task."""
    components = []
    unsupported: list[str] = []

    for comp in pipeline_el.findall(".//component"):
        class_id   = comp.get("componentClassID", "")
        # strip leading namespace prefix if present (e.g. "{...}Microsoft.OLEDBSource")
        short_id   = class_id.split("}")[-1] if "}" in class_id else class_id
        cat        = _COMPONENT_MAP.get(short_id, f"UNKNOWN:{short_id}")
        name       = comp.get("name", "")
        ref_id     = comp.get("refId", "")

        # Collect table/openrowset references
        tables: list[str] = []
        sql_cmds: list[str] = []
        for prop in comp.findall(".//property"):
            prop_name = prop.get("name", "")
            if prop_name in ("OpenRowset",) and prop.text:
                tables.append(prop.text.strip("[]").replace("].[", "."))
            if prop_name == "SqlCommand" and prop.text:
                sql_cmds.append(prop.text)

        entry: dict[str, Any] = {
            "ref_id":       ref_id,
            "name":         name,
            "class_id":     short_id,
            "category":     cat,
            "tables":       tables,
            "sql_commands": sql_cmds,
        }

        if cat in _UNSUPPORTED_COMPONENTS:
            unsupported.append(f"{cat}:{name}")

        components.append(entry)

    return {
        "components":  components,
        "unsupported": unsupported,
    }


def _parse_executable(el: ET.Element, depth: int = 0) -> dict[str, Any]:
    """Recursively parse a DTS:Executable element."""
    exe_type   = _attr(el, "ExecutableType")
    obj_name   = _attr(el, "ObjectName")
    ref_id     = _attr(el, "refId")
    dts_id     = _attr(el, "DTSID")
    task_cat   = _TASK_TYPE_MAP.get(exe_type, f"UNKNOWN:{exe_type}")

    task: dict[str, Any] = {
        "ref_id":      ref_id,
        "dts_id":      dts_id,
        "name":        obj_name,
        "exe_type":    exe_type,
        "task_category": task_cat,
        "depth":       depth,
        "children":    [],
        "sql_body":    None,
        "expression":  None,
        "data_flow":   None,
        "connections": [],
        "unsupported": [],
        "manual_flag": task_cat in _MANUAL_TASK_TYPES,
    }

    # SQL body for Execute SQL Task
    if task_cat == "EXECUTE_SQL":
        obj_data = el.find(f"{{{DTS_NS}}}ObjectData")
        if obj_data is not None:
            sql_data = obj_data.find(f"{{{SQL_NS}}}SqlTaskData")
            if sql_data is not None:
                task["sql_body"] = sql_data.get(f"{{{SQL_NS}}}SqlStatementSource")
                conn_ref = sql_data.get(f"{{{SQL_NS}}}Connection")
                if conn_ref:
                    task["connections"].append(conn_ref)

    # Expression for Expression Task
    if task_cat == "EXPRESSION":
        obj_data = el.find(f"{{{DTS_NS}}}ObjectData")
        if obj_data is not None:
            expr_el = obj_data.find("ExpressionTask")
            if expr_el is not None:
                task["expression"] = expr_el.get("Expression")

    # Data flow internals
    if task_cat == "DATA_FLOW":
        obj_data = el.find(f"{{{DTS_NS}}}ObjectData")
        if obj_data is not None:
            pipeline_el = obj_data.find("pipeline")
            if pipeline_el is not None:
                task["data_flow"] = _parse_data_flow(pipeline_el, ref_id)

    # Connection references in child connection elements
    for conn_el in el.findall(f".//{{{DTS_NS}}}connection"):
        mgr_ref = conn_el.get("connectionManagerRefId", "")
        if mgr_ref and mgr_ref not in task["connections"]:
            task["connections"].append(mgr_ref)

    # Precedence constraints  → child tasks + edges
    constraints: list[dict[str, Any]] = []
    pc_coll = el.find(f"{{{DTS_NS}}}PrecedenceConstraints")
    if pc_coll is not None:
        for pc in pc_coll.findall(f"{{{DTS_NS}}}PrecedenceConstraint"):
            from_id = _attr(pc, "From")
            to_id   = _attr(pc, "To")
            value   = _attr(pc, "Value")          # 0=Failure,1=Success,2=Completion
            eval_op = _attr(pc, "EvalOp")         # 1=Constraint,2=Expression,3=Both
            expr    = _attr(pc, "Expression")
            constraints.append({
                "from": from_id, "to": to_id,
                "condition": {0: "FAILURE", 1: "SUCCESS", 2: "COMPLETION"}.get(int(value) if value else 1, "SUCCESS"),
                "eval_op":   eval_op,
                "expression": expr or None,
            })
    task["constraints"] = constraints

    # Recurse into nested Executables (Sequence Containers, For Loops, etc.)
    child_coll = el.find(f"{{{DTS_NS}}}Executables")
    if child_coll is not None:
        for child in child_coll.findall(f"{{{DTS_NS}}}Executable"):
            task["children"].append(_parse_executable(child, depth + 1))

    return task


def parse_dtsx(path: Path) -> dict[str, Any]:
    """Parse a .dtsx file → canonical package dict."""
    tree   = ET.parse(path)
    root   = tree.getroot()

    pkg_name = _attr(root, "ObjectName")
    pkg_guid = _attr(root, "DTSID")
    version  = _attr(root, "LastModifiedProductVersion")

    # Package-level variables
    variables: list[dict[str, Any]] = []
    for var_el in root.findall(f".//{{{DTS_NS}}}Variable"):
        val_el = var_el.find(f"{{{DTS_NS}}}VariableValue")
        variables.append({
            "name":      _attr(var_el, "ObjectName"),
            "namespace": _attr(var_el, "Namespace"),
            "data_type": val_el.get(f"{{{DTS_NS}}}DataType") if val_el is not None else None,
            "value":     val_el.text if val_el is not None else None,
        })

    # Top-level tasks
    tasks: list[dict[str, Any]] = []
    exe_coll = root.find(f"{{{DTS_NS}}}Executables")
    if exe_coll is not None:
        for child in exe_coll.findall(f"{{{DTS_NS}}}Executable"):
            tasks.append(_parse_executable(child, depth=1))

    # Flatten all tasks for quick lookup
    all_tasks = _flatten_tasks(tasks)

    # Derive source-to-target data movement paths
    movement_paths = _extract_movement_paths(all_tasks)

    unsupported = [
        item
        for t in all_tasks
        for item in (t.get("unsupported") or [])
        + ([f"MANUAL_TASK:{t['task_category']}:{t['name']}"] if t.get("manual_flag") else [])
    ]

    return {
        "id":              f"SSIS:{pkg_name}",
        "object_type":     "SSIS_PACKAGE",
        "source_project":  "SSIS",
        "name":            pkg_name,
        "guid":            pkg_guid,
        "ssis_version":    version,
        "source_file":     str(path),
        "variables":       variables,
        "tasks":           tasks,
        "all_tasks_flat":  all_tasks,
        "movement_paths":  movement_paths,
        "unsupported":     list(dict.fromkeys(unsupported)),  # dedupe preserving order
    }


def _flatten_tasks(tasks: list[dict]) -> list[dict]:
    """Depth-first flatten of nested task tree."""
    result: list[dict] = []
    for t in tasks:
        result.append(t)
        if t.get("children"):
            result.extend(_flatten_tasks(t["children"]))
    return result


def _extract_movement_paths(all_tasks: list[dict]) -> list[dict[str, Any]]:
    """Derive source-db → staging → dimension/fact movement paths from task names and SQL."""
    paths: list[dict[str, Any]] = []
    for t in all_tasks:
        if t["task_category"] == "DATA_FLOW" and t.get("data_flow"):
            df = t["data_flow"]
            sources = [c for c in df["components"] if c["category"] == "OLE_DB_SOURCE"]
            dests   = [c for c in df["components"] if c["category"] == "OLE_DB_DESTINATION"]
            for src in sources:
                for dst in dests:
                    paths.append({
                        "task_name":    t["name"],
                        "source_table": src["tables"][0] if src["tables"] else None,
                        "dest_table":   dst["tables"][0] if dst["tables"] else None,
                        "movement_type": "INCREMENTAL_TO_STAGING",
                    })
        if t["task_category"] == "EXECUTE_SQL" and t.get("sql_body"):
            sql = t["sql_body"]
            migrate_match = re.search(r"EXEC\s+Integration\.Migrate(\w+)", sql, re.IGNORECASE)
            if migrate_match:
                entity = migrate_match.group(1).replace("Staged", "").replace("Data", "")
                paths.append({
                    "task_name":    t["name"],
                    "source_table": f"Integration.{entity}_Staging",
                    "dest_table":   f"Dimension.{entity}" if "Dimension" in t["name"] else f"Fact.{entity}",
                    "movement_type": "STAGING_TO_DW",
                    "etl_proc":     f"Integration.Migrate{migrate_match.group(1)}",
                })
    return paths


def parse_project(project_dir: Path) -> list[dict[str, Any]]:
    """Walk a .dtproj directory, parse all .dtsx and .conmgr files."""
    packages: list[dict[str, Any]] = []

    conmgrs: dict[str, dict] = {}
    for conmgr_path in project_dir.rglob("*.conmgr"):
        cm = parse_conmgr(conmgr_path)
        conmgrs[cm["id"]] = cm

    for dtsx_path in project_dir.rglob("*.dtsx"):
        pkg = parse_dtsx(dtsx_path)
        pkg["connection_managers"] = conmgrs
        packages.append(pkg)

    return packages
