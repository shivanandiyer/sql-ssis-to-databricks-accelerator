#!/usr/bin/env bash
# Pre-deploy test hook. Run before every `databricks bundle deploy`.
# Exits non-zero on any failure, which CI/CD must treat as a hard stop —
# never deploy past a failing test.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== Accelerator pipeline test suite =="
python3 -m pytest tests/ -v --tb=short

echo ""
echo "== Deployment runtime package tests =="
(cd bundle/src && python3 -m pytest tests/ -v --tb=short)

echo ""
echo "All pre-deploy tests passed."
