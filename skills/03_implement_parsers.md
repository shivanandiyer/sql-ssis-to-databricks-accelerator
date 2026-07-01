<!-- Step 3: Implement Parsers — paste this prompt directly into Claude Code -->

Now implement the source analysis layer.

Tasks:
1. Crawl all supported source files in:
   - wwi-ssdt
   - wwi-dw-ssdt
   - wwi-ssis
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
