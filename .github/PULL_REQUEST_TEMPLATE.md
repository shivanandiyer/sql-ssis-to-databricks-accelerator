## What changed

<!-- One or two sentences. What does this PR do, and why? -->

## Which area

- [ ] Parser (`accelerator/parsers/`)
- [ ] Inventory / dependency graph (`accelerator/analyzers/`)
- [ ] Impact analysis scoring
- [ ] Target-state design / architecture recommendation
- [ ] SQL conversion
- [ ] SSIS conversion
- [ ] Deployment tooling (`bundle/`, `conf/`, `deploy/`)
- [ ] Tests / fixtures
- [ ] Documentation only

## Testing

- [ ] Added/updated tests in `tests/` covering this change
- [ ] `pytest tests/` passes locally
- [ ] If this changes deterministic conversion output: golden snapshots
      under `golden_outputs/` were deliberately regenerated
      (`REGENERATE_GOLDEN=1`) and the diff was reviewed, not blindly accepted
- [ ] If this touches `accelerator/parsers/`, `accelerator/analyzers/`, or
      `accelerator/converters/`: ran `python run_validation.py` end-to-end
      against the real source repo and it passes (or any new
      PARTIAL/FAIL is explained below)

## Does this fix a silent-wrong-output bug?

If yes — describe what was silently wrong before, and confirm a regression
test was added to `tests/test_regression_edge_cases.py`'s bug log (see that
file's module docstring for the expected format). Silent-wrong-output bugs
are the highest-priority class of issue in this codebase (see
`docs/example-run/adversarial_review.md`) — a fix without a pinning test is
incomplete.

## New dependencies

- [ ] This PR adds no new third-party dependency
- [ ] This PR adds a dependency: `___` — justification:

(The core pipeline is deliberately pure-standard-library — see README. New
dependencies need explicit justification.)

## Checklist

- [ ] Coding conventions in CONTRIBUTING.md followed (no silent fallbacks,
      specific warnings naming the construct and a concrete rewrite,
      deterministic output, type hints)
- [ ] CHANGELOG.md updated under `[Unreleased]` (add the section if it
      doesn't exist yet)
- [ ] Documentation updated if user-facing behavior changed (README,
      CONTRIBUTING.md, or `docs/`)
