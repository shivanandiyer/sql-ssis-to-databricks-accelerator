---
name: Feature request
about: Suggest an enhancement to the accelerator
title: "[FEATURE] "
labels: enhancement
assignees: ""
---

## What problem does this solve

Describe the gap. If this came up while migrating a real source repo,
context about what you were trying to do (and what the accelerator did
instead) is more useful than an abstract description.

## Proposed approach

If you have one — which module(s) would this touch?

- [ ] Parser (`accelerator/parsers/`)
- [ ] Inventory / dependency graph (`accelerator/analyzers/`)
- [ ] Impact analysis scoring (`accelerator/analyzers/impact_analysis.py`)
- [ ] Target-state design (`accelerator/docs/target_state_design.py`)
- [ ] SQL conversion (`accelerator/converters/sql_converter.py`)
- [ ] SSIS conversion (`accelerator/converters/ssis_converter.py`)
- [ ] Deployment tooling (`bundle/`, `conf/`, `deploy/`)
- [ ] Test infrastructure (`tests/`, `fixtures/`, `golden_outputs/`)
- [ ] Documentation
- [ ] Other

## Alternatives considered

Is there a workaround today (e.g. manual post-processing of generated
output)? Why isn't that sufficient?

## Would this require a new dependency?

This project is deliberately pure-standard-library for the core pipeline
(see README) — if your proposal needs a third-party package, say so here;
that raises the bar for acceptance and needs explicit discussion before a PR.

## Additional context

Anything else — links to relevant Databricks/SQL Server documentation,
related issues, etc.
