---
name: Bug report
about: Something produces incorrect, incomplete, or inconsistent output
title: "[BUG] "
labels: bug
assignees: ""
---

## Describe the bug

A clear description of what's wrong. If the accelerator silently produced
*plausible-looking but incorrect* output (the most dangerous failure mode —
see `docs/example-run/adversarial_review.md` for examples like the OPENJSON
finding), say so explicitly; that's a higher-priority class of bug than a
crash.

## Which pipeline step

- [ ] `run_analysis.py` (parsing / inventory / dependency graph / docs)
- [ ] `run_impact_analysis.py`
- [ ] `run_target_state_design.py`
- [ ] `run_conversion.py` (SQL conversion)
- [ ] `run_ssis_conversion.py`
- [ ] `run_test_matrix.py`
- [ ] `run_validation.py`
- [ ] `deploy/` scripts
- [ ] Test suite (`tests/`)
- [ ] Other / not sure

## To reproduce

1. Source object/file involved (paste the relevant DDL/DTSX excerpt if you
   can — a real excerpt is much more useful than a paraphrase):
   ```sql
   -- paste here
   ```
2. Command run:
   ```bash
   python run_...
   ```
3. Actual output (paste the relevant generated file/log):
   ```
   ...
   ```

## Expected behavior

What should have happened instead — correct conversion, or (if the
construct genuinely has no safe automated path) a `needs_review` flag with
an explanatory warning rather than silent success.

## Environment

- Python version:
- OS:
- Commit / version:

## Additional context

Anything else relevant — e.g. did `run_validation.py` pass before this was
noticed? Does a similar construct convert correctly elsewhere (helps narrow
down whether this is a pattern-matching gap vs. a logic bug)?
