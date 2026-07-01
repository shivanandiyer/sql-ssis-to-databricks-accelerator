# Using the Claude Skills on Their Own

The `skills/` directory contains 15 prompt files you can paste directly into
a Claude Code session to build or extend a modernisation accelerator from
scratch — without running any Python, cloning any repo, or reading this
codebase first.

Each file is a self-contained instruction prompt. Paste it into Claude Code,
let Claude respond, then paste the next one. The sequence below is the same
one used to build this entire repo.

---

## What are the skills?

Each skill is a markdown file with a detailed prompt that tells Claude Code
exactly what to build. Together they walk through the full pipeline:

| Skill | What it builds |
|-------|---------------|
| `00_overview.md` | Sets the project goal and ground rules for the session |
| `01_set_role_and_rules.md` | Establishes Claude's role and core output requirements |
| `02_runtime_input_interface.md` | Scaffolds the project folder structure |
| `03_implement_parsers.md` | Implements SQL and SSIS source parsers |
| `04_implement_analyzers.md` | Builds inventory, dependency graph, and impact analysis |
| `05_convert_sql_objects.md` | Implements the SQL → Databricks SQL / PySpark converter |
| `06_convert_ssis_packages.md` | Implements the SSIS → Databricks Workflows converter |
| `07_documentation_generators.md` | Builds the current-state and target-state doc generators |
| `08_deployment_generator.md` | Generates the Databricks Asset Bundle |
| `09_test_matrix_and_fixtures.md` | Creates the test matrix and fixture files |
| `10_automated_tests.md` | Writes the full pytest suite |
| `11_end_to_end_validation.md` | Builds `run_validation.py` |
| `12_adversarial_review.md` | Runs a self-critical review of all conversion outputs |
| `13_github_push.md` | Creates the GitHub repo and pushes the accelerator |
| `14_architecture_override.md` | Adds support for non-medallion architectures |

---

## Quick start — rebuilding or extending the accelerator

### Option A: Use the existing repo (most common)

If you already have this repo cloned, use the skills to extend or re-run
individual pipeline stages without starting fresh.

1. Open Claude Code in the repo directory.
2. Pick the skill for the stage you want (e.g. `skills/05_convert_sql_objects.md`).
3. Open the file, copy the full contents, and paste into Claude Code.
4. Review Claude's response and files created, then paste the next skill.

The skills are designed to be resumable — you don't need to paste all 15 in
one session. Start at any step that's relevant.

### Option B: Building the accelerator from scratch on a new repo

1. Create a new empty directory and open Claude Code in it.
2. Paste `skills/00_overview.md` first — this sets the context for the
   whole session.
3. Paste `skills/01_set_role_and_rules.md` — this locks in Claude's role
   and output requirements.
4. Paste `skills/02_runtime_input_interface.md` — **before pasting, edit
   the GitHub URL and folder names at the top to point at your own source
   repo** (see the note at the bottom of that file).
5. Continue pasting skills in order (03 → 04 → ... → 13).
6. Paste `skills/14_architecture_override.md` only if you want a
   non-medallion architecture.

---

## Adapting skills for your own source repo

### Step 2 (runtime input interface)

`02_runtime_input_interface.md` contains a hardcoded reference to the
Wide World Importers sample corpus. Before pasting it into a fresh session,
replace these three lines:

```
Use this GitHub sample as the source corpus:
https://github.com/microsoft/sql-server-samples/.../wide-world-importers

Important folders:
- wwi-ssdt     = SQL Server OLTP database project
- wwi-dw-ssdt  = SQL Server DW project
- wwi-ssis     = SSIS ETL project
```

with the equivalent for your own repo:

```
Use this local path as the source corpus:
/path/to/your/sql-ssis-repo

Important folders:
- YourOLTP/     = SQL Server OLTP database project (.sqlproj here)
- YourDW/       = SQL Server DW project (.sqlproj here)
- YourETL/      = SSIS ETL project (.dtsx files here)
```

Everything else in the skill sequence works unchanged — the rest of the skills
don't refer to WWI by name.

### Steps 0 and 1 (overview and role)

These are general enough to paste verbatim for any project. No edits needed.

### Steps 3–13

These build the accelerator itself (parsers, converters, tests, etc.) and don't
reference the source corpus by path — they work against whatever corpus you
pointed step 2 at. Paste them as-is.

---

## Using individual skills in isolation

You don't have to run the full sequence. Individual skills are useful on their
own:

**Re-run a single stage after making changes:**
```
Paste skills/05_convert_sql_objects.md
→ Asks Claude to re-implement or fix the SQL converter
```

**Add architecture support after the fact:**
```
Paste skills/14_architecture_override.md
→ Adds lakehouse / lambda / kappa support without touching anything else
```

**Regenerate tests after changing a converter:**
```
Paste skills/10_automated_tests.md
→ Asks Claude to write or update tests for the current state of the code
```

**Run a fresh adversarial review:**
```
Paste skills/12_adversarial_review.md
→ Asks Claude to look for silent failures, naive translations, hidden
  dependencies, and missed edge cases in the current output
```

---

## Tips for pasting skills into Claude Code

- **Paste the whole file.** Each skill file is a complete prompt — don't
  summarise or excerpt it. Claude uses every line.

- **Wait for a summary before moving on.** Each skill ends with an instruction
  telling Claude to summarise what it did and wait. Read that summary before
  pasting the next skill — it's your checkpoint.

- **If Claude gets stuck**, add a clarification in the same message window
  before pasting the next skill. You don't need to restart.

- **Skills 07 and 13 are two-part.** The file says "Paste Part 1 first,
  review the output, then paste Part 2." Follow this — Part 2 depends on
  what Part 1 produced.

- **The MCP server is a complement, not a replacement.** The MCP tools
  (`mcp/server.py`) call the same pipeline stages the skills build —
  they're different ways to drive the same code. Use skills to build or
  extend the code; use the MCP server to run it interactively from an
  AI agent.

---

## Skill file reference

### `skills/00_overview.md` — Overview

Sets the full project scope: what the accelerator does, all supported source
types (SSIS, SQL tables, views, procedures, functions, triggers, connection
managers), the default medallion target architecture, and the core output
contract (A–J outputs every run must produce). Also establishes the
"step by step, wait for instruction" working mode.

**When to use:** Paste this first in any fresh Claude Code session before
pasting any other skill. Also useful as a quick briefing if you hand the
session to someone else.

---

### `skills/01_set_role_and_rules.md` — Role and Rules

Identical to `00_overview.md` in content — paste either one as the session
opener. The duplication is intentional: `00` is the project overview,
`01` locks in Claude's role and output format for the build sequence.

**When to use:** Paste at the start of a session where you're building the
accelerator (as opposed to just running it).

---

### `skills/02_runtime_input_interface.md` — Project Scaffold

Points Claude at the source corpus and asks it to scaffold the Python project
folder structure (`accelerator/parsers/`, `analyzers/`, `converters/`,
`deploy/`, `docs/`, `tests/`). Does **not** implement any logic — only creates
empty files and directories.

**When to use:** Step 2 of a fresh build. Edit the source path before pasting
(see "Adapting skills" above).

---

### `skills/03_implement_parsers.md` — Parsers

Implements `accelerator/parsers/sql_project_parser.py` and
`accelerator/parsers/ssis_parser.py`. These are the only files that read the
source repo — everything downstream consumes their output.

**Key output:** classified SQL objects (type, schema, name, dependencies,
complexity signals) and parsed SSIS packages (tasks, connections, variables).

**When to use:** After scaffolding (step 2), or standalone to re-implement
or extend the parser for a new SQL construct.

---

### `skills/04_implement_analyzers.md` — Analyzers

Implements `inventory_builder.py`, `dependency_graph.py`, and
`impact_analysis.py`. Takes the parser output and produces:
- `inventory.json` — all objects classified and scored
- `dependencies.json` — DAG with topological order
- `impact_analysis.md` + `object_complexity_scores.json` — 12-dimension
  risk scores and lift-and-shift / rewrite / manual classification

**When to use:** After parsers, or standalone when adding a new risk dimension
or classification rule.

---

### `skills/05_convert_sql_objects.md` — SQL Converter

Implements `accelerator/converters/sql_converter.py`. Converts tables, views,
procedures, and functions to Databricks SQL or PySpark, with explicit
`needs_review` flags and `review_required/` output files for any construct it
can't cleanly convert.

**Key principle the skill enforces:** never silently guess. Any `CURSOR`,
`FOR XML`, `geography` column, dynamic SQL, or temporal table query goes to
`review_required/` with the original DDL and a suggested approach.

**When to use:** After analyzers, or standalone to add support for a new SQL
Server construct.

---

### `skills/06_convert_ssis_packages.md` — SSIS Converter

Implements `accelerator/converters/ssis_converter.py`. Maps SSIS control flow
(Sequence Containers, Execute SQL Tasks, Data Flow Tasks, Foreach Loops) to
Databricks Workflow tasks, and SSIS variables / connection managers to
Workflow job parameters and Unity Catalog External Locations.

**Output:** `output/workflow_spec.json` — the Databricks Workflow job
specification consumed by the bundle generator.

**When to use:** After SQL conversion, or standalone to add support for an
SSIS task type your source repo uses.

---

### `skills/07_documentation_generators.md` — Documentation (two parts)

**Part 1:** Implements `accelerator/docs/current_state_doc.py` — generates
`outputs/current_state_documentation.md` from the inventory and dependency
graph.

**Part 2:** Implements `accelerator/docs/target_state_design.py` — generates
`outputs/target_state_architecture.md` and `outputs/medallion_mapping.csv`
with the Unity Catalog naming design and per-object Bronze/Silver/Gold
assignment.

Paste Part 1, review the generated `current_state_documentation.md`, then
paste Part 2.

---

### `skills/08_deployment_generator.md` — Deployment Bundle

Implements `deploy/generate_deployment_bundle.py` and the `bundle/` directory
structure (Databricks Asset Bundle YAML, `conf/dev.yml`, `conf/test.yml`,
`conf/prod.yml`).

**Output:** a complete DAB ready for `databricks bundle deploy --target dev`.

---

### `skills/09_test_matrix_and_fixtures.md` — Test Matrix

Implements `accelerator/docs/test_matrix.py` and the `fixtures/` directory.
Produces `outputs/test_matrix.csv`, `outputs/test_strategy.md`, and
`outputs/coverage_gaps.md`.

Also creates the SQL fixture files (`fixtures/sql/`) used by the pytest suite.

---

### `skills/10_automated_tests.md` — pytest Suite

Writes the full `tests/` directory: unit tests for parsers, analyzers,
converters, and the architecture recommender, plus golden snapshot tests
(`golden_outputs/`) for deterministic converter output.

**Key detail:** tests use `pytest.skip` (not `pytest.fail`) when the real
pipeline outputs aren't present, so `pytest tests/ -v` always runs cleanly
even without a full pipeline run.

---

### `skills/11_end_to_end_validation.md` — Validation Script

Implements `run_validation.py`: a 12-step end-to-end validation that re-parses
the source repo from scratch, runs every pipeline stage, diffs golden snapshots,
runs pytest, and produces `docs/example-run/validation_summary.md` with a
PASS / PARTIAL / FAIL verdict per step.

---

### `skills/12_adversarial_review.md` — Adversarial Review

Asks Claude to act as an adversary and find problems in its own output:
- Silent failures (constructs converted without flagging issues)
- Naive translations (patterns that look right but break at runtime)
- Hidden dependencies (objects that look standalone but aren't)
- Missing edge cases

Output: `docs/example-run/adversarial_review.md`. Use this after running the
pipeline on a new source repo to surface issues before handing off to engineers.

---

### `skills/13_github_push.md` — GitHub Publishing (two parts)

**Part 1:** Creates the GitHub repo, commits all files, and pushes.

**Part 2:** Tags the first release (`v1.0.0`) and creates a GitHub Release
with a changelog.

Edit the repo name, description, and GitHub username before pasting.

---

### `skills/14_architecture_override.md` — Architecture Override (optional)

Adds `--architecture` support to the pipeline: lakehouse (single unified
layer), lambda (speed + batch layers), or kappa (stream-first). Only paste
this if your source repo's characteristics justify a non-medallion design.

The skill documents when each alternative is appropriate:
- **Lakehouse**: source has no clear staging layer, < 50 objects
- **Lambda**: source has both real-time and batch paths
- **Kappa**: source is stream-first with no meaningful batch history

---

## The full sequence at a glance

```
00  Set project scope
01  Lock in role and rules
02  Scaffold project (edit source path first)
 ↓
03  Parsers (SQL + SSIS)
04  Analyzers (inventory, dependencies, impact)
05  SQL converter
06  SSIS converter
07  Documentation (Part 1 → review → Part 2)
08  Deployment bundle
 ↓
09  Test matrix + fixtures
10  Automated tests (pytest)
11  End-to-end validation
12  Adversarial review
 ↓
13  GitHub push (Part 1 → review → Part 2)
14  Architecture override (optional)
```

Each arrow is a natural checkpoint — the output of one group feeds the next.
You can stop at any checkpoint and resume in a new session by pasting
`00_overview.md` to re-brief Claude, then jumping to whichever step you're on.
