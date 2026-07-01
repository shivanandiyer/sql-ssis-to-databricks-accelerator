<!-- Step 12: Adversarial Review — paste this prompt directly into Claude Code -->

Run an adversarial review of the accelerator design and all conversion outputs.

Look for:
- Hidden dependencies
- Dynamic SQL
- Temp tables
- Table variables
- MERGE semantics
- Cursor-like procedural logic
- Unsupported T-SQL functions
- SSIS expression language edge cases
- Variable scoping issues
- Restartability gaps
- Schema drift risks
- Naming collisions in Unity Catalog
- Mismatched medallion placement
- Warehouse objects that should remain serving-layer SQL
- Objects whose semantics are degraded by naive Spark translation

For each issue:
- Classify severity (critical / high / medium / low)
- Explain impact
- Propose mitigation
- Propose whether automation should: stop / warn / continue

Outputs:
- adversarial_review.md
- remediation_backlog.csv
