<!-- Step 11: End-to-End Validation — paste this prompt directly into Claude Code -->

Perform an end-to-end validation of the accelerator against the sample repository.

Validation steps:
1.  Parse source repo
2.  Extract object inventory
3.  Build dependency graph
4.  Produce documentation
5.  Produce impact analysis
6.  Recommend target architecture
7.  Convert SQL objects
8.  Convert SSIS packages
9.  Build deployment artifacts
10. Run automated tests
11. Compare outputs with expected golden results
12. Produce final validation summary

Required outputs:
- validation_summary.md
- validation_results.json
- failed_cases.json
- recommended_backlog.md

In the summary include:
- What passed
- What partially passed
- What failed
- Why it failed
- Whether failure is due to unsupported source semantics, ambiguous intent, or
  an implementation bug
- What must be fixed before accelerator release
