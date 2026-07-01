<!-- Step 8: Deployment Generator — paste this prompt directly into Claude Code -->

Generate deployment artifacts for Databricks.

Include:
- Folder structure
- Databricks Asset Bundle (DAB) configuration
- Environment parameterisation for dev / test / prod
- Secret references
- Cluster or serverless recommendations
- Workflow definitions
- SQL deployment scripts
- Notebook/module packaging
- Unit/integration test hooks

Outputs:
- bundle/
- conf/
- deploy/
- README.md

The deployment design must support:
- Repeatable deployment
- Object-level idempotency
- Promotion across environments
- Rollback notes per object class
