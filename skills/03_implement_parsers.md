<!-- Step 3: Implement Parsers — paste this prompt directly into Claude Code -->

Now implement the source analysis layer.

Use the source directories established in step 2:
- OLTP dir  — the transactional SQL Server database project
- DW dir    — the data warehouse project (if configured; skip if blank)
- SSIS dir  — the SSIS ETL project (if configured; skip if blank)

Tasks:
1. Crawl all supported source files under the configured directories
2. Build an inventory of:
   - schemas
   - tables
   - views
   - materialized views if present
   - stored procedures
   - functions
   - SSIS packages
   - related ETL assets
3. Detect object categories, naming patterns, and folder conventions
4. Extract dependencies between SQL objects and SSIS tasks
5. Identify source-to-target data movement paths
6. Detect ETL semantics such as:
   - full loads
   - incremental loads
   - SCD logic
   - dimension/fact loading order
   - cutoff-window logic

Outputs required:
- inventory.json
- dependencies.json
- source_summary.md
- unsupported_objects.json

Rules:
- Do not convert anything yet
- Normalise findings into a canonical metadata model
- Tag each object with source type, schema, dependency type, and conversion complexity
- Objects from OLTP dir → tag source_project = "OLTP"
- Objects from DW dir → tag source_project = "DW" (used downstream for Bronze vs Silver/Gold layer assignment)
- If a directory was left blank in step 2, skip it gracefully — do not error
