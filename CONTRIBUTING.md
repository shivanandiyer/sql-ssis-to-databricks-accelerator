# Contributing

Thanks for considering a contribution. This project is a static-analysis
and code-generation accelerator — the most valuable contributions are
usually "I pointed this at a real source repo and found a construct it
doesn't handle," backed by a fixture and a test. This guide covers the four
most common contribution shapes plus general coding conventions.

## Before you start

- Open an issue first for anything beyond a small fix — use the
  [unsupported object type](.github/ISSUE_TEMPLATE/unsupported_object_type.md)
  template if you found a T-SQL or SSIS construct the accelerator doesn't
  recognize.
- Every change to `accelerator/parsers/`, `accelerator/analyzers/`, or
  `accelerator/converters/` should come with a test. Untested pattern
  additions are the easiest way to reintroduce a silent-wrong-output bug —
  see `docs/example-run/adversarial_review.md` for what that looks like in
  practice (the OPENJSON finding) and why it matters.
- Run `python run_validation.py` before opening a PR if you touched the
  parsers, analyzers, or converters — it's the only check that exercises
  the full pipeline against the real WWI source repo end-to-end, not just
  fixtures.

## How to add support for a new SQL Server object type

Object types are classified in `accelerator/parsers/sql_project_parser.py`'s
`_CLASSIFIERS` list (regex → type name, tried in order, most specific
first). To add one:

1. Add a regex to `_CLASSIFIERS` (or a sub-type table like `_FUNC_SUBTYPES`
   if it's a refinement of an existing type, e.g. a new function shape).
2. If the construct affects conversion complexity or risk, add a pattern to
   `_COMPLEXITY_PATTERNS` in the same file **and** to the corresponding list
   in `accelerator/analyzers/impact_analysis.py` (`_DIALECT_PATTERNS`,
   `_PROCEDURAL_PATTERNS`, or `_DATA_TYPE_PATTERNS` as appropriate) — these
   two files have historically drifted out of sync (see the temp-table
   regex bug in `docs/example-run/adversarial_review.md`, Finding 3, which
   existed in *both* files independently), so update both or write a test
   that would catch future drift.
3. Add a conversion path in `accelerator/converters/sql_converter.py`. If
   the construct has no Databricks equivalent, **do not** let it fall
   through to a generic "safe" conversion — explicitly detect it and force
   `needs_review = True` with a warning describing the gap and a suggested
   rewrite pattern. The OPENJSON fix is the reference example: a procedural-
   factor pattern was added, which routes the object to a PySpark stub with
   the original T-SQL preserved, rather than silently emitting an empty
   "converted" file.
4. Add a real fixture under `fixtures/sql/` — prefer a genuine excerpt from
   a real source repo over a synthetic example (see "How to add test
   fixtures" below).
5. Add tests in `tests/test_parsers.py` (classification), `tests/test_sql_conversion.py`
   (conversion behavior), and `tests/test_regression_edge_cases.py` if the
   change fixes a previously-silent bug — pin the regression so it can't
   silently reappear.

## How to add a new SSIS task mapping

SSIS task handling lives in `accelerator/converters/ssis_converter.py`.

1. Confirm the task type is parsed by `accelerator/parsers/ssis_parser.py`
   first — if it's a wholly new SSIS executable type, add parsing there
   (see `_TASK_TYPE_MAP` / `_COMPONENT_MAP`).
2. Add a confidence/target-mapping branch in `_confidence_and_target()` and
   a test recommendation in `_test_recommendation()`.
3. If the task needs generated code, add a branch to
   `generate_python_module()` (for PySpark/notebook tasks) or
   `generate_sql_task_file()` (for inline-SQL Execute SQL tasks).
4. Add the mapping rule to `build_workflow_spec()` if it needs a new
   Databricks Workflow task type (e.g. `condition_task` for expression-based
   branching, `for_each_task` for Foreach Loops — see
   `unsupported_ssis_features.md` in a generated run for the documented-but-
   unimplemented mapping rules for constructs not present in the bundled
   sample).
5. **Add a real fixture.** `fixtures/ssis/minimal_package.dtsx` is a real
   SSIS sequence container (byte-for-byte excerpt from the bundled sample's
   `DailyETLMain.dtsx`) re-wrapped in a minimal package envelope so it
   parses standalone for fast unit tests — follow that pattern rather than
   hand-writing synthetic DTSX XML, which is easy to get subtly wrong.
6. Add tests in `tests/test_ssis_mapping.py`.

## How to add test fixtures

- **Prefer real excerpts over synthetic examples.** Every fixture under
  `fixtures/sql/` today is a real file copied from the Wide World Importers
  corpus, chosen to represent a specific pattern (simple lift-and-shift
  table, geography+temporal table, CURSOR-driven procedure, FOR JSON view,
  multi-statement scalar function, set-based procedure). A synthetic
  example can accidentally simplify away the exact edge case you're trying
  to test.
- For SSIS, prefer extracting a real, complete construct (a full sequence
  container, a full data flow) over hand-authoring DTSX XML — SSIS's XML
  schema has enough structural nuance (namespaces, refId path conventions)
  that hand-written fixtures tend to silently not match real packages.
- **Golden snapshot files** (`golden_outputs/`) must only change as a
  deliberate, reviewed decision. Regenerate with
  `REGENERATE_GOLDEN=1 pytest tests/test_sql_conversion.py`, then review the
  diff like you would any other code change before committing it — never
  regenerate "to make the test pass" without understanding why the output
  changed.
- If your fixture demonstrates a bug fix, also add it to
  `tests/test_regression_edge_cases.py`'s bug log docstring (at the top of
  the file) — that log is the project's record of "this exact thing broke
  once, here's the test that prevents it from breaking silently again."

## Coding conventions

- **Python 3.10+, standard library only** for everything under
  `accelerator/`. The pipeline's zero-dependency design is deliberate (see
  README) — if you need a third-party package, raise it in an issue first
  rather than adding it directly; the bar is high.
- **No silent fallbacks.** If a code path can't determine something
  confidently, it should set `needs_review = True` and explain why, not
  guess. This is the single most important convention in this codebase —
  most of the bugs found in `docs/example-run/adversarial_review.md` were
  exactly this pattern (a construct fell through to a generic path that
  looked successful but wasn't).
- **Every generated warning should name the specific construct and suggest
  a concrete rewrite**, not just say "manual review required." Compare a
  good example (`sql_converter.py`'s geography-type warning, which names
  the exact WKT/Mosaic/Sedona rewrite options) against a vague one before
  writing a new one.
- **Type hints** on all new functions; this codebase uses
  `from __future__ import annotations` throughout for forward-reference-
  friendly hints.
- **No docstrings that restate the code** — see the project's existing
  module docstrings for the expected style (state the *why*, not the
  *what*; the code already shows the what).
- **Determinism.** Anything that touches the same input twice must produce
  byte-identical output (no wall-clock timestamps inside generated SQL/
  Python, no non-deterministic dict/set iteration relied upon for output
  order). Several tests assert this explicitly
  (`test_*_is_deterministic` across the suite) — match that pattern for new
  generators.
- Run `ruff` and `mypy` per `pyproject.toml`'s configuration before
  submitting (`pip install ruff mypy` — these are dev-only, not runtime
  dependencies).

## Pull requests

See [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) for
what to include. In short: what changed, why, what tests cover it, and
whether you ran `run_validation.py`.
