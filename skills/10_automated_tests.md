<!-- Step 10: Automated Tests — paste this prompt directly into Claude Code -->

Generate Python automated tests for the accelerator.

Test categories:
- Parser tests
- Metadata extraction tests
- Dependency graph tests
- SQL conversion tests
- SSIS mapping tests
- Architecture recommendation tests
- Deployment bundle generation tests
- Regression tests for known edge cases

Testing requirements:
- Use pytest
- Include fixtures from the WideWorldImporters sample
- Snapshot test generated outputs where useful
- Validate deterministic outputs for supported objects
- Validate graceful failure for unsupported objects
- Compare lineage before and after conversion
- Assert that all source objects receive a disposition:
  converted / partial / manual

Outputs:
- tests/
- fixtures/
- golden_outputs/
- pytest.ini
- test_report_template.md
