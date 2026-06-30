#!/usr/bin/env bash
# Deploy the WWI Modernisation Accelerator bundle to a target environment.
#
# Usage:
#   ./deploy/deploy.sh dev
#   ./deploy/deploy.sh test
#   ./deploy/deploy.sh prod
#
# Order of operations (repeatable, idempotent — safe to re-run):
#   1. Pre-deploy tests (deploy/run_tests.sh) — hard gate, aborts on failure.
#   2. Regenerate the bundle job resource from the latest conversion output
#      (deploy/generate_deployment_bundle.py) so the bundle never drifts from
#      what the accelerator actually produced.
#   3. databricks bundle validate — catches schema/reference errors before
#      anything is touched in the workspace.
#   4. SQL DDL deploy (deploy/sql_deploy.py) — idempotent CREATE TABLE IF NOT
#      EXISTS / CREATE OR REPLACE VIEW statements, safe to re-run.
#   5. databricks bundle deploy — uploads notebooks/SQL files and
#      creates/updates the Workflow job definition. Asset Bundle deploys are
#      themselves idempotent: re-deploying the same bundle state is a no-op.
#   6. Post-deploy smoke test (deploy/validate_deployment.py).
set -euo pipefail
cd "$(dirname "$0")/.."

TARGET="${1:?Usage: deploy.sh <dev|test|prod>}"

if [[ "$TARGET" != "dev" && "$TARGET" != "test" && "$TARGET" != "prod" ]]; then
  echo "Error: target must be dev, test, or prod (got '$TARGET')" >&2
  exit 1
fi

echo "=== [1/6] Pre-deploy tests ==="
./deploy/run_tests.sh

echo ""
echo "=== [2/6] Regenerating bundle job resource from latest conversion output ==="
python3 deploy/generate_deployment_bundle.py

echo ""
echo "=== [3/6] Validating bundle (target: $TARGET) ==="
(cd bundle && databricks bundle validate -t "$TARGET")

echo ""
echo "=== [4/6] Deploying SQL DDL (idempotent) ==="
python3 deploy/sql_deploy.py --target "$TARGET" --plan-only
read -p "Apply the above DDL plan to '$TARGET'? [y/N] " confirm
if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
  python3 deploy/sql_deploy.py --target "$TARGET" --apply
else
  echo "Skipped SQL DDL apply — re-run with --apply when ready."
fi

echo ""
echo "=== [5/6] Deploying bundle (target: $TARGET) ==="
(cd bundle && databricks bundle deploy -t "$TARGET")

echo ""
echo "=== [6/6] Post-deploy smoke test ==="
python3 deploy/validate_deployment.py --target "$TARGET"

echo ""
echo "Deployment to '$TARGET' complete."
