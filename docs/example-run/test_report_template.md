# WWI Modernisation Accelerator — Test Run Report

> **Run date:** {{DATE}}
> **Run by:** {{AUTHOR}}
> **Command:** `pytest -v --tb=short`
> **pytest version:** {{PYTEST_VERSION}}
> **Python version:** {{PYTHON_VERSION}}
> **Git commit / branch:** {{COMMIT_SHA}}

---

## 1. Summary

| Metric | Value |
|---|---|
| Total tests collected | {{TOTAL}} |
| Passed | {{PASSED}} |
| Failed | {{FAILED}} |
| Skipped | {{SKIPPED}} |
| Errors | {{ERRORS}} |
| Duration | {{DURATION}} |

**Overall result:** {{PASS_FAIL_BANNER}}

---

## 2. Coverage by Category

| Category | Module | Tests | Passed | Failed | Skipped |
|---|---|---|---|---|---|
| Parser tests | `test_parsers.py` | | | | |
| Metadata extraction tests | `test_metadata_extraction.py` | | | | |
| Dependency graph tests | `test_dependency_graph.py` | | | | |
| SQL conversion tests | `test_sql_conversion.py` | | | | |
| SSIS mapping tests | `test_ssis_mapping.py` | | | | |
| Architecture recommendation tests | `test_architecture_recommendation.py` | | | | |
| Deployment bundle tests | `test_deployment_bundle.py` | | | | |
| Regression / edge case tests | `test_regression_edge_cases.py` | | | | |

---

## 3. Skipped Tests

Tests in this suite skip automatically (rather than fail) when the upstream
pipeline outputs they depend on (`outputs/inventory.json`,
`outputs/dependencies.json`, `output/conversion_manifest.json`,
`output/workflow_spec.json`) haven't been generated yet. List any skips here
with their reason, and whether that's expected for this run:

| Test | Reason | Expected? |
|---|---|---|
| | | |

---

## 4. Failures

For each failure, capture enough to triage without re-running:

### {{TEST_ID}}

- **Module:** 
- **Assertion:** 
- **Traceback summary:** 
- **Suspected cause:** product bug / test bug / fixture drift / environment
- **Linked issue / follow-up:** 

---

## 5. New Regressions Found This Run

Use this section only when a test in `test_regression_edge_cases.py` fails
for the first time, or when a new bug is found while extending the suite.
Follow the bug-log format already established in that module's docstring:

```
N. <module>.<function>: <one-line description of the wrong behaviour>.
   Found via: <test name>.
   Fix: <one-line description, or "not yet fixed — tracked as known gap">.
```

---

## 6. Golden Snapshot Changes

If any `golden_outputs/*.sql` file was regenerated this run
(`REGENERATE_GOLDEN=1`), list it here with the reason — golden file changes
must always be a deliberate, reviewed decision, never an accidental side
effect of a fixture or converter change:

| Golden File | Reason for Change | Reviewed By |
|---|---|---|
| | | |

---

## 7. Disposition Audit (converted / partial / manual)

Required by the accelerator: every source object must resolve to exactly one
of `converted`, `partial`, or `manual`. Confirm via
`test_deployment_bundle.py::TestRealDeploymentBundle::test_real_manifest_every_object_has_a_disposition`:

| Disposition | Object Count | % of Total |
|---|---|---|
| converted | | |
| partial | | |
| manual | | |
| **undefined (should always be 0)** | | |

---

## 8. Action Items

- [ ] 
- [ ] 

---

_Generated from `test_report_template.md`. Fill in `{{PLACEHOLDERS}}` after each test run; do not edit the template's structure without updating this header comment._
