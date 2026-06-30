#!/usr/bin/env bash
# Promote the accelerator's deployment from one environment to the next.
#
# Usage:
#   ./deploy/promote.sh dev test
#   ./deploy/promote.sh test prod
#
# This does NOT copy data between catalogs — promotion means deploying the
# same bundle/code state to the next environment's already-existing catalog
# structure. Each environment's Bronze layer is independently fed by its own
# source connection (see conf/<env>.yml secrets.scope) and its own watermark
# state (catalog.ops.etl_watermark), so promoting code never promotes data.
set -euo pipefail
cd "$(dirname "$0")/.."

FROM="${1:?Usage: promote.sh <from-env> <to-env>}"
TO="${2:?Usage: promote.sh <from-env> <to-env>}"

VALID_PATHS="dev:test test:prod"
if [[ ! " $VALID_PATHS " =~ " $FROM:$TO " ]]; then
  echo "Error: unsupported promotion path '$FROM -> $TO'. Valid paths: dev->test, test->prod." >&2
  exit 1
fi

echo "=== Promoting $FROM -> $TO ==="

if [[ "$TO" == "prod" ]]; then
  echo ""
  echo "Pre-prod-promotion checklist (see conf/test.yml required_before_promotion_to_prod):"
  echo "  [ ] test_matrix.csv Tier 1-3 cases pass against the test catalog"
  echo "  [ ] reconciliation row counts match within tolerance for all 14 dimension/fact targets"
  echo "  [ ] manual sign-off recorded for every object in manual_intervention_list.md"
  echo ""
  read -p "All checklist items confirmed complete? [y/N] " confirm
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted — complete the checklist before promoting to prod."
    exit 1
  fi
fi

# Record the exact commit being promoted, for rollback reference.
COMMIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo 'unknown — not a git repo')"
echo "Promoting commit: $COMMIT_SHA"
echo "$COMMIT_SHA" > "deploy/.last_promoted_to_${TO}"

./deploy/deploy.sh "$TO"

echo ""
echo "Promotion $FROM -> $TO complete (commit $COMMIT_SHA)."
echo "Rollback reference saved to deploy/.last_promoted_to_${TO} — see deploy/rollback.md."
