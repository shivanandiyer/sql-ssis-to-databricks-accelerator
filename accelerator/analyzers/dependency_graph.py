"""
dependency_graph.py
Builds a directed dependency graph from the inventory, performs topo-sort,
cycle detection, and produces dependencies.json + source_summary.md.
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph(inventory: dict[str, Any]) -> dict[str, Any]:
    """
    Build a dependency graph from the inventory.

    Nodes: every inventory object (keyed by id).
    Edges: directed "X depends on Y" (X → Y).

    Edge sources:
    1. SQL references extracted by sql_project_parser (FROM/JOIN/EXEC)
    2. SSIS precedence constraints (task → task)
    3. SSIS data-flow: Extract task writes to staging, MigrateStaged reads from staging → DW
    4. SSIS SQL task bodies that call stored procs
    """
    objects = inventory.get("objects", [])

    # Build id lookup: canonical_ref → id
    # Canonical ref: "schema.name" (case-insensitive)
    ref_to_id: dict[str, str] = {}
    for obj in objects:
        schema = obj.get("schema", "dbo") or "dbo"
        name   = obj.get("name",   "UNKNOWN")
        ref_to_id[f"{schema}.{name}".lower()] = obj["id"]
        # Also register bare name for single-part refs
        ref_to_id[name.lower()] = obj["id"]

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    for obj in objects:
        nodes[obj["id"]] = {
            "id":              obj["id"],
            "name":            obj.get("name"),
            "schema":          obj.get("schema"),
            "object_type":     obj.get("object_type"),
            "source_project":  obj.get("source_project"),
            "medallion_layer": obj.get("medallion_layer"),
            "complexity_band": obj.get("complexity_band"),
            "risk":            obj.get("risk"),
            "fan_in":          0,
            "fan_out":         0,
        }

    def resolve(ref: str) -> str | None:
        return ref_to_id.get(ref.lower())

    def add_edge(from_id: str, to_id: str, edge_type: str, label: str = "") -> None:
        if from_id == to_id:
            return
        edges.append({
            "from":      from_id,
            "to":        to_id,
            "edge_type": edge_type,
            "label":     label,
        })

    # ── Pass 1: SQL object references ────────────────────────────────────────
    for obj in objects:
        src_id = obj["id"]
        refs   = obj.get("references") or {}
        for ref in refs.get("tables", []) + refs.get("procedures", []):
            target_id = resolve(ref)
            if target_id and target_id != src_id:
                add_edge(src_id, target_id, "SQL_REFERENCE", ref)
        for ref in refs.get("functions", []):
            target_id = resolve(ref)
            if target_id and target_id != src_id:
                add_edge(src_id, target_id, "FUNCTION_CALL", ref)

    # ── Pass 2: SSIS precedence constraints ──────────────────────────────────
    for obj in objects:
        if obj.get("object_type") != "SSIS_PACKAGE":
            continue
        pkg_name = obj.get("name")
        for task in obj.get("objects", []):   # not present here — use all_tasks
            pass
    # SSIS tasks are flattened as separate inventory items; link via constraints
    for obj in objects:
        if not obj.get("object_type", "").startswith("SSIS_"):
            continue
        pkg_name = obj.get("parent_package", "")
        for constraint in obj.get("constraints", []):
            from_ref = f"SSIS:{pkg_name}:{_last_segment(constraint.get('from',''))}"
            to_ref   = f"SSIS:{pkg_name}:{_last_segment(constraint.get('to',''))}"
            from_id  = ref_to_id.get(from_ref) or _find_ssis_task(nodes, from_ref)
            to_id    = ref_to_id.get(to_ref)   or _find_ssis_task(nodes, to_ref)
            if from_id and to_id:
                condition = constraint.get("condition", "SUCCESS")
                add_edge(from_id, to_id, f"SSIS_CONTROL_FLOW_{condition}", condition)

    # ── Pass 3: SSIS data movement paths ─────────────────────────────────────
    for obj in objects:
        if obj.get("object_type") != "SSIS_PACKAGE":
            continue
        for path_item in obj.get("movement_paths", []):
            src_table  = path_item.get("source_table")
            dst_table  = path_item.get("dest_table")
            task_name  = path_item.get("task_name", "")
            task_id    = ref_to_id.get(f"SSIS:{obj['name']}:{task_name}".lower())
            src_tbl_id = resolve(src_table) if src_table else None
            dst_tbl_id = resolve(dst_table) if dst_table else None
            if src_tbl_id and dst_tbl_id:
                add_edge(dst_tbl_id, src_tbl_id, "DATA_FLOW", path_item.get("movement_type",""))
            if task_id and src_tbl_id:
                add_edge(task_id, src_tbl_id, "READS_FROM", "")
            if task_id and dst_tbl_id:
                add_edge(task_id, dst_tbl_id, "WRITES_TO", "")

    # ── Pass 4: SSIS SQL tasks calling known procs ────────────────────────────
    for obj in objects:
        if not obj.get("object_type", "").startswith("SSIS_EXECUTE_SQL"):
            continue
        sql = obj.get("sql_body") or ""
        import re
        for m in re.finditer(r"EXEC\s+(\w+)\.(\w+)", sql, re.IGNORECASE):
            proc_ref = f"{m.group(1)}.{m.group(2)}"
            proc_id  = resolve(proc_ref)
            if proc_id:
                add_edge(obj["id"], proc_id, "CALLS_PROC", proc_ref)

    # ── Compute fan-in / fan-out ──────────────────────────────────────────────
    for edge in edges:
        if edge["from"] in nodes:
            nodes[edge["from"]]["fan_out"] += 1
        if edge["to"] in nodes:
            nodes[edge["to"]]["fan_in"] += 1

    graph = {
        "nodes":      nodes,
        "edges":      edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }
    return graph


# ---------------------------------------------------------------------------
# Topological sort (Kahn's algorithm)
# ---------------------------------------------------------------------------

def topological_sort(graph: dict[str, Any]) -> list[str]:
    """
    Return node IDs in safe deployment order (dependencies before dependants).
    Nodes in cycles or with no path are appended at the end.
    """
    nodes = graph["nodes"]
    edges = graph["edges"]

    # Edge semantics are "from depends on to" (e.g. Fact -> Dimension). Safe
    # deployment order needs dependencies (the "to" side) processed before
    # dependants (the "from" side), so Kahn's algorithm runs over the
    # *reversed* adjacency: an edge from->to becomes "to enables from".
    in_degree: dict[str, int] = {nid: 0 for nid in nodes}
    adj: dict[str, list[str]] = defaultdict(list)

    for edge in edges:
        frm, to = edge["from"], edge["to"]
        if frm in nodes and to in nodes:
            adj[to].append(frm)
            in_degree[frm] += 1

    queue = deque(nid for nid, deg in in_degree.items() if deg == 0)
    order: list[str] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in adj[node]:
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    # Append any remaining nodes (cycle members)
    remaining = [n for n in nodes if n not in set(order)]
    return order + remaining


# ---------------------------------------------------------------------------
# Cycle detection (DFS)
# ---------------------------------------------------------------------------

def detect_cycles(graph: dict[str, Any]) -> list[list[str]]:
    """Return list of cycles; empty list means the graph is a DAG."""
    nodes = graph["nodes"]
    edges = graph["edges"]

    adj: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if edge["from"] in nodes and edge["to"] in nodes:
            adj[edge["from"]].append(edge["to"])

    WHITE, GRAY, BLACK = 0, 1, 2
    colour = {n: WHITE for n in nodes}
    cycles: list[list[str]] = []
    path:   list[str] = []

    def dfs(node: str) -> None:
        colour[node] = GRAY
        path.append(node)
        for neighbour in adj[node]:
            if colour[neighbour] == GRAY:
                # found a cycle — capture it
                idx = path.index(neighbour)
                cycles.append(path[idx:] + [neighbour])
            elif colour[neighbour] == WHITE:
                dfs(neighbour)
        path.pop()
        colour[node] = BLACK

    for node in nodes:
        if colour[node] == WHITE:
            dfs(node)

    return cycles


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

def export_dot(graph: dict[str, Any], output_path: Path) -> None:
    """Write a Graphviz DOT file."""
    lines = ["digraph WWI {", "  rankdir=LR;", "  node [shape=box fontsize=10];"]
    layer_colours = {
        "BRONZE": "burlywood", "SILVER": "lightblue",
        "GOLD": "gold", "SHARED": "lightgreen",
    }
    for nid, node in graph["nodes"].items():
        colour = layer_colours.get(node.get("medallion_layer", ""), "white")
        label  = f"{node['schema']}.{node['name']}" if node.get("schema") else node.get("name", nid)
        lines.append(f'  "{nid}" [label="{label}" fillcolor="{colour}" style=filled];')
    for edge in graph["edges"]:
        label = edge.get("label", "")
        lines.append(f'  "{edge["from"]}" -> "{edge["to"]}" [label="{label}"];')
    lines.append("}")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def export_mermaid(graph: dict[str, Any], output_path: Path) -> None:
    """Write a Mermaid flowchart file (top-down)."""
    lines = ["```mermaid", "flowchart TD"]
    for nid, node in graph["nodes"].items():
        safe_id = nid.replace(":", "_").replace(".", "_").replace(" ", "_")
        label   = f"{node.get('schema','')}.{node.get('name','')}"
        lines.append(f"  {safe_id}[\"{label}\"]")
    for edge in graph["edges"]:
        frm = edge["from"].replace(":", "_").replace(".", "_").replace(" ", "_")
        to  = edge["to"].replace(":", "_").replace(".", "_").replace(" ", "_")
        lines.append(f"  {frm} --> {to}")
    lines.append("```")
    output_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Identify source-to-target data movement paths
# ---------------------------------------------------------------------------

def extract_etl_lineage(graph: dict[str, Any], inventory: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Trace complete ETL lineage chains:
    OLTP source table → Integration proc (Get*Updates) → SSIS Extract task
    → Integration staging table → MigrateStagedXxx proc → Dimension/Fact table.
    """
    lineage_chains: list[dict[str, Any]] = []
    nodes = graph["nodes"]
    edges = graph["edges"]

    # Build adjacency for forward traversal
    forward: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        forward[edge["from"]].append(edge["to"])

    # Find all Dimension and Fact tables as terminal nodes
    terminal_ids = {
        nid for nid, node in nodes.items()
        if node.get("medallion_layer") in ("SILVER", "GOLD")
        and node.get("object_type") == "TABLE"
    }

    for term_id in terminal_ids:
        node = nodes[term_id]
        lineage_chains.append({
            "target":          term_id,
            "target_name":     f"{node.get('schema')}.{node.get('name')}",
            "target_layer":    node.get("medallion_layer"),
            "upstream_count":  nodes[term_id].get("fan_in", 0),
        })

    return lineage_chains


# ---------------------------------------------------------------------------
# Persist and return
# ---------------------------------------------------------------------------

def build_and_save_graph(
    inventory: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    """Build graph, detect cycles, topo-sort, persist dependencies.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    graph  = build_graph(inventory)
    cycles = detect_cycles(graph)
    order  = topological_sort(graph)
    etl_lineage = extract_etl_lineage(graph, inventory)

    output = {
        "node_count":      graph["node_count"],
        "edge_count":      graph["edge_count"],
        "has_cycles":      len(cycles) > 0,
        "cycles":          cycles,
        "topological_order": order,
        "etl_lineage":     etl_lineage,
        "nodes":           graph["nodes"],
        "edges":           graph["edges"],
    }

    (output_dir / "dependencies.json").write_text(
        json.dumps(output, indent=2, default=str), encoding="utf-8"
    )
    export_dot(graph, output_dir / "dependency_graph.dot")
    export_mermaid(graph, output_dir / "dependency_graph.md")

    return output


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _last_segment(ref_id: str) -> str:
    """Extract task name from a SSIS refId like 'Package\\Load City Dimension\\Truncate City_Staging'."""
    return ref_id.split("\\")[-1].strip()


def _find_ssis_task(nodes: dict[str, dict], search_key: str) -> str | None:
    """Case-insensitive partial match against node ids."""
    key_lower = search_key.lower()
    for nid in nodes:
        if key_lower in nid.lower():
            return nid
    return None
