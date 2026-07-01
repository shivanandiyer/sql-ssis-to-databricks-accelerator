<!-- Step 5: Convert SQL Objects — paste this prompt directly into Claude Code -->

Now implement the SQL object conversion layer.

Convert these source object types into Databricks-compatible assets:
- tables
- views
- materialized views
- stored procedures
- functions

Rules:
1. Preserve semantics first, syntax second
2. Map SQL Server types to Databricks-compatible types
3. Replace unsupported procedural constructs with equivalent Databricks patterns
4. Where stored procedures are orchestration-heavy, split them into:
   - SQL transformation logic
   - workflow/task orchestration logic
5. For warehouse objects:
   - facts/dimensions map to Gold unless the architecture mapping says otherwise
6. Emit:
   - converted SQL
   - PySpark where SQL is insufficient
   - comments explaining non-trivial rewrites
   - unresolved items flagged for manual review

Output folders:
- output/databricks_sql/
- output/pyspark/
- output/review_required/

Also produce:
- conversion_manifest.json
- conversion_decisions.md
