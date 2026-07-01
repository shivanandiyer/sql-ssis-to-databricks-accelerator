<!-- Step 4: Implement Analyzers — paste this prompt directly into Claude Code -->

Perform an impact analysis for migrating this SQL Server/Synapse + SSIS solution
to Databricks.

Assess:
- SQL dialect conversion complexity
- T-SQL procedural logic complexity
- SSIS control flow conversion complexity
- SSIS data flow conversion complexity
- Dependency criticality
- Ordering constraints
- Data type mapping risks
- Performance risks
- Security / access model changes
- Operational scheduling changes
- Testing complexity
- Rollback complexity

Classify each object as:
- lift-and-shift friendly
- rewrite required
- partial automation possible
- manual redesign required

Produce:
- impact_analysis.md
- migration_risk_register.csv
- object_complexity_scores.json
- manual_intervention_list.md

Include:
- Blast radius by object
- Downstream dependency impacts
- Likely semantic drift risks
- Recommended test depth by object class
