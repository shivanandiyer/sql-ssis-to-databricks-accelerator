<!-- Step 9: Test Matrix and Fixtures — paste this prompt directly into Claude Code -->

Create a comprehensive test matrix for the accelerator.

Test dimensions:
- Object type:    table, view, MV, proc, function, SSIS task, workflow
- Complexity:     low, medium, high
- Load style:     full, incremental, CDC-like window, SCD
- Source pattern: OLTP, DW, hybrid
- Target layer:   Bronze, Silver, Gold
- Conversion mode: SQL, PySpark, Workflow
- Confidence band: high, medium, low

Cover these scenarios:
1.  Pure DDL conversion
2.  View translation
3.  Stored proc with set-based SQL only
4.  Stored proc with procedural branching
5.  Function conversion
6.  Fact/dimension ETL
7.  SSIS control flow with sequencing
8.  SSIS data flow with transformations
9.  Incremental watermark logic
10. Failure recovery / rerun logic
11. Dependency ordering
12. Unsupported feature detection
13. User-driven architecture override

Outputs:
- test_matrix.csv
- test_strategy.md
- coverage_gaps.md
