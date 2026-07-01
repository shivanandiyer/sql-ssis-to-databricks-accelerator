<!-- Step 7: Documentation Generators — paste this prompt directly into Claude Code -->

This step covers both documentation generators: current-state documentation and
target-state architecture design. Paste Part 1 first, review the output, then
paste Part 2.

## Part 1 — Current-State Documentation

Using the extracted metadata, generate current-state documentation for the
SQL Server/Synapse + SSIS solution.

Document sections:
1.  Business overview inferred from object model
2.  Source platform overview
3.  Schema inventory
4.  ETL/orchestration overview
5.  Object taxonomy:
    - tables
    - views
    - materialized views
    - stored procedures
    - functions
    - SSIS packages
6.  Dependency map
7.  Data domains
8.  Load patterns
9.  Operational assumptions
10. Technical debt / migration hotspots

Output requirements:
- Generate a concise executive summary
- Generate a technical deep dive
- Produce markdown plus machine-readable summaries
- Add confidence level per section

Outputs:
- current_state_documentation.md
- current_state_summary.json

## Part 2 — Target-State Architecture Design

Propose a target-state Databricks design for this workload.

Default assumption:
- Medallion architecture (Bronze/Silver/Gold)

But:
- If the source workload suggests a better architecture, recommend an alternative
  and explain why
- Allow architecture override from user input at runtime

Design tasks:
1. Map source OLTP and DW objects into Bronze/Silver/Gold layers
2. Separate ingestion, transformation, serving, and orchestration concerns
3. Recommend Unity Catalog structure:
   - catalog
   - schema
   - table naming conventions
4. Recommend file/layout strategy:
   - Delta tables
   - partitioning
   - liquid clustering if justified
5. Recommend orchestration mapping:
   - SSIS control flow -> Databricks Workflows tasks
6. Recommend code mapping:
   - T-SQL -> Databricks SQL and/or PySpark
7. Recommend observability:
   - audit logging
   - lineage
   - data quality checks
8. Recommend CI/CD and environment promotion strategy

Outputs:
- target_state_architecture.md
- target_state_mappings.json
- medallion_mapping.csv
- orchestration_design.md

For each recommendation:
- Explain rationale
- Explain tradeoffs
- Note assumptions
