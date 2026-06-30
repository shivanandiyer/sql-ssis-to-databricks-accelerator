# Adversarial Review — WWI Modernisation Accelerator

> **Reviewer stance:** assume the accelerator's own confidence scores, risk
> labels, and `needs_review` flags are wrong until independently verified
> against the real source DDL and real generated output. Every finding below
> is grounded in either the actual WWI source corpus, the actual generated
> `output/` artifacts, or the actual accelerator source code — not
> hypothetical concerns.
>
> **Generated:** 2026-06-30
> **Scope:** `accelerator/` (parsers/analyzers/converters), `outputs/`,
> `output/` as of the current pipeline run (431 inventory objects, 279
> converted SQL objects, 81 SSIS Workflow tasks).

---

## Fix status (updated 2026-06-30, post-remediation)

12 of 15 findings have been fixed in code and verified by re-running the full
pipeline (`run_analysis.py` → `run_impact_analysis.py` →
`run_target_state_design.py` → `run_conversion.py` → `run_ssis_conversion.py`
→ `pytest tests/` → `run_validation.py`, all green); 1 was fixed via
documentation (an architectural/operational risk, not a code defect); 2 were
deliberately left unfixed per their own `CONTINUE` stance (no confirmed
instance of harm in this corpus). Full per-finding status, verification
evidence, and the exact code changes are in `remediation_backlog.csv`'s
`status`/`verification` columns. Headline results:

- **F1/F2 (OPENJSON, the CRITICAL finding):** all 38 affected procedures now
  correctly show `needs_review: True`, `classification: MANUAL_REDESIGN`,
  route to PySpark with the original T-SQL preserved — verified directly
  against the regenerated `output/conversion_manifest.json`.
- **F6 (the other CRITICAL/STOP finding — false Time Travel equivalence):**
  retracted from both `impact_analysis.py` and `sql_converter.py`'s
  generated warnings; as a side effect, 9 previously-unflagged temporal
  tables now correctly require review.
- **F4 (shared-variable race hazard):** the new automated detector caught
  not just the originally-cited `TableName` (13 writers) but also
  `TargetETLCutoffTime` (2 writers) — a hazard the original manual review
  missed.
- **F3 (temp-table regex bug):** fixed in both places it appeared
  (`sql_project_parser.py` and `impact_analysis.py` had independently
  duplicated the same `\b#\w+\b` bug).

Each finding's section below is unchanged from the original review (so the
diagnosis stays intact as a record); status is in the table at the end and
in `remediation_backlog.csv`.

---

## Severity legend

| Severity | Meaning |
|---|---|
| **CRITICAL** | Silently produces wrong output with no flag raised; would reach prod undetected |
| **HIGH** | Produces wrong/incomplete output, but is at least partially observable (empty file, exception, etc.) |
| **MEDIUM** | Degrades quality/maintainability/performance but the functional result is still correct |
| **LOW** | Cosmetic or low-probability; worth tracking, not blocking |

## Automation-stance legend

| Stance | Meaning |
|---|---|
| **STOP** | Automation must halt and force manual resolution before continuing — wrong output is worse than no output |
| **WARN** | Automation may proceed but must surface the issue (review flag, log, report entry) — current accelerator behavior often fails this |
| **CONTINUE** | Safe to proceed silently — automation correctly handles this case today |

---

## Finding 1 — OPENJSON: a completely undetected unsupported-function class (CRITICAL)

**What was found:** 38 procedures (all `WebApi.Insert*FromJson` / `WebApi.Update*FromJson`) use `OPENJSON` to parse a JSON parameter into a relational rowset — a core T-SQL JSON-ingestion pattern with **no equivalent anywhere in the accelerator's pattern lists** (`_COMPLEXITY_PATTERNS`, `_DIALECT_PATTERNS`, `_UNSUPPORTED_VIEW_PATTERNS` in `sql_converter.py`/`sql_project_parser.py` all omit it).

**Impact:** All 38 procedures are classified `PARTIAL_AUTOMATION`, converted with `needs_review: False`, and zero warnings. Inspecting the actual generated output confirms the damage:

```sql
-- output/databricks_sql/silver/webapi__insertcitiesfromjson.sql
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

-- TODO: no top-level DML auto-extracted; review source body.
```

This file is **empty of executable logic** and is marked as needing no review. If deployed, it silently does nothing — the JSON-ingestion API endpoint these procedures back would appear to succeed while writing zero rows, with no signal anywhere in the accelerator's own output that anything is wrong.

**Why this happened:** `OPENJSON` doesn't match any CURSOR/WHILE/dynamic-SQL pattern, so `_extract_core_dml`'s regex-based statement extraction finds nothing (the actual DML is inside the `OPENJSON(...) WITH (...)` clause structure it doesn't recognize), and the object is never routed to manual review because nothing flagged it as risky in the first place.

**Mitigation:**
1. Add an `OPENJSON` detection pattern to both `_COMPLEXITY_PATTERNS` (scoring) and a new "unsupported function" check in `convert_procedure`/`convert_view` that forces `needs_review = True` regardless of what `_extract_core_dml` finds.
2. Target mapping: `OPENJSON(@json) WITH (...)` → PySpark `spark.read.json()` / `from_json()` with an explicit schema, or Databricks SQL `variant`/`from_json` functions (DBR 15+) — requires a human to translate the `WITH` clause's column/type list per procedure, not a mechanical rewrite.
3. Re-audit every object whose conversion produced a file with **no executable SQL above the warnings/comments block** — that pattern (this finding's root symptom) likely indicates other undetected unsupported constructs beyond just OPENJSON, and should become a standing automated check (see Finding 9).

**Automation stance: STOP.** An empty-bodied "successful" conversion is the single most dangerous failure mode this review found — worse than an exception, because it looks done.

---

## Finding 2 — Temp-table detection regex never matches (HIGH)

**What was found:** `_COMPLEXITY_PATTERNS` in `sql_project_parser.py` includes `r"\b#\w+\b"` to detect SQL Server temp tables (`#TableName`). This pattern **can never match** — `\b` requires a word/non-word transition, but `#` is itself a non-word character, so `\b` immediately before `#` only matches if the preceding character is a word character (never true; temp table names are always preceded by whitespace or punctuation, also non-word).

```python
>>> re.search(r"\b#\w+\b", "CREATE TABLE #CityChanges (x int)")
None
>>> re.search(r"#\w+", "CREATE TABLE #CityChanges (x int)")
<re.Match object; span=(13, 25), match='#CityChanges'>
```

**Impact:** Verified against real data — 10 objects in the corpus actually use temp tables; the complexity scorer counted **0**. Of those 10, 2 (`Sequences.ReseedSequenceBeyondTableValues` in both OLTP and DW) have no other risk-pattern overlap (no CURSOR/WHILE/dynamic SQL), so they are the objects most likely to have their complexity silently underscored as a direct result of this bug. For the other 8 (including `GetCityUpdates`), CURSOR/WHILE already pushed the score to HIGH, so the net classification happened to be right for the wrong reason — but that's luck, not correctness.

**Mitigation:** Fix the pattern to `r"#\w+"` (drop the leading `\b`). Re-run `run_analysis.py` and `run_impact_analysis.py` after the fix; expect `Sequences.ReseedSequenceBeyondTableValues` (both projects) to move from their current classification toward `REWRITE_REQUIRED` or `MANUAL_REDESIGN`.

**Automation stance: WARN today, should be STOP-on-discovery once fixed** — i.e., the fixed pattern should force these 2 objects into manual review rather than silently reclassifying them and moving on.

---

## Finding 3 — Shared mutable SSIS variable (`TableName`) breaks under the accelerator's own parallelization recommendation (HIGH)

**What was found:** The SSIS package variable `User::TableName` is a single, package-scoped, mutable string that gets reassigned 13 times — once per entity, immediately before that entity's `Get Lineage Key` task reads it (`Set TableName to City`, `Set TableName to Customer`, ... `Set TableName to Transaction Type`). This works in SSIS only because the 13 Sequence Containers execute **strictly sequentially** by default.

**Impact:** `target_state_architecture.md` (from an earlier accelerator step) explicitly recommends running independent entity loads **in parallel** on Databricks Workflows ("lets entity loads run in parallel where the dependency graph allows it ... instead of SSIS's single-threaded sequential container execution"). Combined with this finding, that recommendation is unsafe as written: if `TableName`-equivalent state were naively carried over as a single shared variable (e.g. a job-level parameter mutated by one task and read by another), parallel entity loads would race on it — City's `Get Lineage Key` task could read `"Customer"` if the Customer container's "Set TableName" task happened to run concurrently.

The current SSIS converter avoids this specific failure mode by design (it maps `TableName` to a `Workflow job parameter, templated into each per-entity job run` per-entity, not a single shared mutable value — see `map_variables` in `ssis_converter.py`) — but this is correct *by accident of the chosen target design*, not because anything in the accelerator detected and flagged the race condition. Nothing audits "is this SSIS variable read by a different task than the one that wrote it, and could those tasks run concurrently in the target design?"

**Mitigation:** Add an explicit cross-check between `target_state_architecture.md`'s parallelization recommendation and `ssis_converter.py`'s variable-scoping model — document (as this review now does) that the per-entity-job-parameter design is a **required** mitigation for `TableName`-style shared state, not an optional implementation detail, so a future change to either side doesn't silently reintroduce the race.

**Automation stance: WARN.** Flag any SSIS variable written by more than one distinct task and read by a task other than its own writer as a parallelization hazard requiring explicit scoping review — currently undetected by any accelerator step.

---

## Finding 4 — `MERGE` against a table variable with compound `+=` assignment has no Spark MERGE INTO equivalent (HIGH)

**What was found:** `DataLoadSimulation.PickStockForCustomerOrders` runs:

```sql
MERGE @StockAlreadyAllocated AS saa
USING (VALUES (@StockItemID, @Quantity)) AS sa(StockItemID, Quantity)
ON saa.StockItemID = sa.StockItemID
WHEN MATCHED THEN
    UPDATE SET saa.QuantityAllocated += sa.Quantity
WHEN NOT MATCHED THEN
    INSERT (StockItemID, QuantityAllocated) VALUES (sa.StockItemID, sa.Quantity);
```

Two compounding issues: (a) the MERGE target is a **table variable**, not a persistent table — Spark SQL's `MERGE INTO` only operates on Delta tables, no equivalent for a procedure-local mutable rowset; (b) `UPDATE SET col += val` (compound assignment) has no direct Spark MERGE INTO syntax — it must be rewritten as `col = target.col + source.val`.

**Impact:** `convert_procedure`'s `_PROCEDURAL_PATTERNS` correctly flags `\b@\w+\s+TABLE\b` (table variable) for this object, so it is routed to manual review — this one is **not** silently broken. But the review-required output doesn't call out *why* the MERGE specifically is hard (table-variable target + compound assignment), so a reviewer re-deriving this from the warning text alone (`"Temp table — replace with a PySpark DataFrame..."`) would reasonably reach for a literal MERGE INTO translation and hit the `+=` syntax wall mid-implementation rather than up front.

**Mitigation:** Add a `MERGE` + table-variable/temp-table combination check that emits a specific warning: *"MERGE target is non-persistent (table variable/temp table) — must be re-expressed as an in-memory accumulation pattern (e.g. `groupBy().agg(sum())` over the per-row allocations) rather than a literal Delta MERGE INTO, since there is no persistent Delta table to merge into."* Also flag compound assignment operators (`+=`, `-=`) inside any MERGE/UPDATE as requiring explicit expansion.

**Automation stance: WARN (already correctly routed to manual review; this finding upgrades the *quality* of that warning, not the routing decision).**

---

## Finding 5 — `FOR SYSTEM_TIME AS OF` is not equivalent to Delta `VERSION/TIMESTAMP AS OF` — the accelerator's own design doc asserts otherwise (HIGH)

**What was found:** `GetCityUpdates` (and the analogous procedure for every other temporal-tracked entity) uses `FOR SYSTEM_TIME AS OF @ValidFrom` **inside a CURSOR loop**, re-evaluated once per historical change event, to get the row that was valid *at that specific past instant* (9 separate AS OF clauses across the procedure, each parameterized by a different loop-iteration timestamp). This is a **per-row point-in-time lookup against bitemporal row validity**.

`target_state_architecture.md` (Load Patterns section) and `conversion_decisions.md` both recommend replacing temporal queries with "Delta Time Travel (`TIMESTAMP AS OF`) / Change Data Feed" as if it's a drop-in equivalent. It is not: Delta `TIMESTAMP AS OF`/`VERSION AS OF` returns **the entire table's contents at a given commit**, not "the version of each row that was valid at an arbitrary, per-row timestamp." SQL Server's temporal table semantics are row-grained validity windows (`ValidFrom`/`ValidTo` per row, independent of when the table itself was last written); Delta time travel is table-grained commit-history semantics. These coincide only if every row change is its own Delta commit — never true for a batch-loaded Bronze/Silver table.

**Impact:** Any naive 1:1 translation of `FOR SYSTEM_TIME AS OF @ts` to `TIMESTAMP AS OF @ts` would silently return the wrong rows (the whole table's state at the nearest preceding *batch load*, not the row's actual historical validity window) — a correctness bug that would be very hard to detect by inspection, since the query would run successfully and return plausible-looking data.

**Mitigation:** The correct target pattern is **not** Delta time travel — it's a direct point-in-time filter against the row-validity columns that already exist on the converted Silver table: `WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`. This requires the Bronze/Silver layer to actually preserve full row-version history (every `_Archive`-paired row, not just the current row) as regular queryable rows with their `ValidFrom`/`ValidTo` columns intact — which the current table-conversion design already does (these columns are kept as ordinary `TIMESTAMP` columns, not dropped) — but no converted query anywhere actually rewrites a `FOR SYSTEM_TIME AS OF` clause into this filter form. Every occurrence is currently left as literal, uncommented-on T-SQL syntax inside a manual-review file.

**Automation stance: STOP.** Update `target_state_architecture.md` and `conversion_decisions.md` to retract the "Delta Time Travel" equivalence claim for this specific pattern before any human reviewer acts on that guidance; flag every `FOR SYSTEM_TIME AS OF` occurrence with the correct point-in-time-filter target pattern instead of a generic "needs rewrite" note.

---

## Finding 6 — Hidden dependencies via dynamic SQL: none found in this corpus, but the static dependency graph has no defense if they existed (MEDIUM)

**What was found:** Verified — **zero** objects in this corpus use `sp_executesql` or dynamic `EXEC(@sql)`. This category is currently a non-issue for WWI specifically.

**Impact (forward-looking, not active today):** `dependency_graph.py`'s `build_graph` extracts references via static regex over `FROM`/`JOIN`/`EXEC` clauses in `raw_ddl`. Any table or procedure name composed at runtime inside a dynamic SQL string (`EXEC('SELECT * FROM ' + @table)`) is structurally invisible to this extraction — it would silently produce an **incomplete** dependency graph (missing edges), which would then silently produce a wrong topological deployment order and a wrong blast-radius calculation in `impact_analysis.md`, with no error anywhere.

**Mitigation:** Add a standing check (independent of this corpus) — any object containing `sp_executesql` or dynamic `EXEC(` should have its dependency edges explicitly marked `"resolved": false` in the graph and excluded from blast-radius confidence claims, rather than silently contributing zero edges as if it has no dependencies.

**Automation stance: CONTINUE for this corpus (no instances exist); WARN required before this accelerator is reused on a different source repo that does use dynamic SQL** — call this out explicitly in any "porting this accelerator to a new source" documentation.

---

## Finding 7 — Restartability: cross-entity atomicity gap (MEDIUM)

**What was found:** `unsupported_ssis_features.md` (from an earlier step) correctly documents single-task idempotency (overwrite/MERGE) and recommends Databricks Workflows' repair-run feature as the SSIS-checkpoint-restart equivalent. It does **not** address a different, real gap: the 13 entity loads are independent Workflow task chains with **no cross-entity transaction boundary**. If the job fails after entities A–F have fully completed (data + watermark advanced) but entity G fails mid-load, a "repair run" correctly resumes only G — but any downstream consumer (a Gold-layer report joining multiple entities) that ran between the partial failure and the repair would see a **point-in-time-inconsistent** snapshot: A–F at their new watermark, G and H–M at their old watermark.

**Impact:** This is a real cross-entity consistency gap inherited from the source design itself (SSIS's single package also has this exposure — a mid-package failure leaves some entities updated and others not) — the accelerator doesn't make it worse, but it also doesn't flag it as something the target design should consider improving (e.g. a "all entities succeed before any Gold view becomes visible" pattern, via Delta's `REPLACE TABLE` + view-swap or a Liquid/shallow-clone staging catalog).

**Mitigation:** Document this as an explicit operational risk in `rollback.md` / `orchestration_design.md`: downstream consumers of Gold-layer tables should be aware that mid-failure windows can expose inconsistent cross-entity state, and should query via a designated "last fully-consistent run" watermark/tag if point-in-time consistency across entities matters for their use case.

**Automation stance: WARN.** Not a defect introduced by conversion, but currently undocumented as an inherited risk — should be surfaced, not silently inherited.

---

## Finding 8 — Schema drift: `parse_sqlproj`'s dedup-by-id silently drops same-named files with no log (MEDIUM, latent)

**What was found:** `parse_sqlproj` dedups by canonical object ID: `if obj["id"] in seen_ids: continue`. In this corpus, zero objects are defined across more than one file (verified: no standalone `ALTER TABLE` script files exist), so this code path never actually triggers today.

**Impact (latent):** If a future version of this source repo (or a different SSDT project) ever splits an object's definition across a `CREATE` file and a separate `ALTER` migration file — a common SSDT pattern for incremental schema changes — `parse_sqlproj` would silently process whichever file `sorted(project_dir.rglob("*.sql"))` happens to visit first and **silently discard** the other, with no warning, no log line, nothing in `unsupported_objects.json`. The resulting inventory would reflect a schema that never actually existed at any single point in time (some columns from the CREATE, missing the ALTER's changes, or vice versa depending on alphabetical file ordering).

**Mitigation:** Change the dedup branch to at minimum log a warning (`unsupported_objects.json` entry: `"id": ..., "reason": "duplicate definition found, only first processed"`), and ideally merge ALTER-derived column changes into the base object rather than discarding them.

**Automation stance: WARN required (currently silent — this is a real gap, just not yet triggered by this specific corpus).**

---

## Finding 9 — Unity Catalog naming: no active collisions, but the naming convention has an unguarded asymmetry (LOW, structural)

**What was found:** Verified — `medallion_mapping.csv`'s 112 `target_fqn` values are **all unique** today (`build_medallion_mapping`'s naming convention: OLTP tables get `schema__name`, DW tables get bare `name`). No active collision exists in this corpus.

**Impact (structural):** The convention is asymmetric by design (documented in `target_state_architecture.md`'s Unity Catalog section as a deliberate tradeoff) — DW objects drop their schema prefix because Dimension/Fact/Integration schemas map 1:1 onto Silver/Gold/Bronze. This is safe only as long as no two *different* DW schemas mapped to the *same* target layer ever share a table name (e.g. if a future DW schema addition introduced a second "staging"-style schema alongside `Integration`, both targeting Bronze, with an overlapping table name). Nothing in `build_medallion_mapping` actually checks for this — it would silently produce a duplicate `target_fqn` and the second `CREATE TABLE IF NOT EXISTS` would silently become a no-op against the first object's table, merging two unrelated source objects into one target table.

**Mitigation:** Add an explicit uniqueness assertion to `build_medallion_mapping` (or a post-generation check in `run_target_state_design.py`) that fails loudly if any two source objects resolve to the same `target_fqn`, rather than relying on "it happens not to collide today."

**Automation stance: CONTINUE today (verified no collisions); STOP if a future regeneration ever produces one** — currently unguarded, should become a hard assertion.

---

## Finding 10 — Mismatched medallion placement: Sequences and pass-through WebApi CRUD procedures (MEDIUM)

**What was found two distinct sub-cases:**

**10a. Sequences (34 objects) mapped to BRONZE.** `_assign_layer` falls through to the default `"BRONZE"` for `SEQUENCE` objects (no entry for `SEQUENCE` object type anywhere in the layer-assignment logic — it's incidental, not deliberate). A SQL Server `SEQUENCE` is a surrogate-key generator, not a data object with a medallion lifecycle at all — `target_state_architecture.md`'s own code-mapping table separately (and correctly) recommends `GENERATED ALWAYS AS IDENTITY` instead of porting the sequence object itself, making its Bronze-layer placement in `medallion_mapping.csv` actively misleading (it implies a 34-object Bronze migration scope that shouldn't exist as stated).

**10b. `WebApi`/`Website` schema objects (74 procedures + views) mapped to SILVER.** These are thin CRUD pass-through procedures over OLTP Bronze tables (e.g. `WebApi.Cities` is `SELECT ... FROM Application.Cities` with no joins, no conformance, no business-rule transformation). Labeling them "Silver" implies the conformed/cleansed semantics Silver carries elsewhere in this same design (e.g. `Dimension.City`'s actual SCD2 conformance) — a reviewer skimming `medallion_mapping.csv` would reasonably expect WebApi.Cities to have undergone real transformation, when it's actually a serving-layer view that happens to sit one layer up.

**Impact:** Both are naming/classification noise that could mislead a migration team's effort estimation (treating 34 trivial sequence "migrations" and 74 "Silver conformance" objects as real layer-appropriate work, when they're each a different, smaller category of work).

**Mitigation:** (a) Exclude `SEQUENCE` objects from `medallion_mapping.csv` entirely, or add a 4th pseudo-layer `INFRASTRUCTURE` distinct from Bronze/Silver/Gold; (b) split WebApi/Website into their own labeled category ("Silver — Serving Pass-Through") distinct from true conformed-Silver objects like the Dimension tables, so effort estimates don't conflate the two.

**Automation stance: WARN.** Not wrong enough to block conversion (the actual DDL conversion of these objects is unaffected), but wrong enough to distort planning if taken at face value.

---

## Finding 11 — Objects that should remain serving-layer SQL, not become PySpark modules (MEDIUM)

**What was found:** `Website.CalculateCustomerPrice` (and similarly-shaped scalar functions) is a per-row pricing calculation designed to be called **inline inside SQL SELECT statements** across many OLTP/WebApi queries (it computes a customer-and-item-specific price by joining `Sales.SpecialDeals`/`Warehouse.StockItems` and applying discount logic). After Bug Fix #5 from the prior session, this correctly routes to a PySpark stub (its multi-statement DECLARE/IF body isn't expressible as a single SQL expression) — but PySpark is the wrong **target shape** for this object's actual usage pattern, even though it's the right target for its *complexity*.

**Impact:** A standalone PySpark function (`def calculatecustomerprice(*args): raise NotImplementedError`) cannot be called inline from a Databricks SQL query the way the original was called inline from T-SQL `SELECT` statements — every caller site would need to be rewritten to either (a) pre-compute prices in a separate batch step and join the result, or (b) wrap the PySpark logic as a registered SQL UDF (`spark.udf.register`), which the current converter output doesn't do or even mention as an option.

**Mitigation:** For functions whose complexity forces a PySpark implementation *but* whose original call sites are inline-SQL, the conversion should additionally emit a `spark.udf.register("calculate_customer_price", calculatecustomerprice)` registration block and document that the function becomes a registered SQL UDF, not a notebook-only Python function — preserving the "callable from SQL" shape the business logic actually needs.

**Automation stance: WARN.** Currently the converter doesn't distinguish "complexity forces non-SQL implementation" from "the object should still be SQL-callable" — both collapse into the same generic PySpark stub today.

---

## Finding 12 — Naive `ISNULL` → `COALESCE` rewrite changes type-coercion behavior (LOW, latent)

**What was found:** `_SYNTAX_REWRITES` in `sql_converter.py` blindly rewrites `ISNULL(` → `COALESCE(`. These are not type-equivalent: T-SQL `ISNULL(a, b)` returns a value typed as `a`'s type (truncating/coercing `b` to match); ANSI `COALESCE(a, b)` returns the **highest-precedence** type among all arguments. For most simple cases (matching types) this is invisible; for mixed-precision numeric or string-length arguments it can silently change the result's effective precision/length where the source relied on `ISNULL`'s truncating behavior.

**Impact:** No confirmed instance of this actually changing behavior was found in spot-checked conversions (the WWI corpus's `ISNULL` usages are mostly matched-type), but the rewrite is applied **mechanically and silently** with no warning regardless of argument types — there is no check for whether the two arguments' types actually match before applying the substitution.

**Mitigation:** Add a warning whenever `ISNULL` is rewritten and its two arguments have visually different literal types/lengths (e.g. one is a string literal, the other a column reference) — can't fully resolve types statically, but a heuristic flag is better than silent rewriting.

**Automation stance: CONTINUE for now (no confirmed instance of actual harm in this corpus); WARN recommended as a low-cost improvement.**

---

## Finding 13 — `TOP(n)` → `LIMIT n` rewrite already flagged, but the warning is generic — verified one concrete instance (LOW)

**What was found:** Already partially covered by existing converter warnings ("T-SQL TOP without ORDER BY is non-deterministic and so is Spark LIMIT"). Verified this applies concretely to at least one real view; the warning text is correct but generic — it doesn't identify *which* converted view actually lacks the ORDER BY (it's emitted unconditionally on every view, whether or not `TOP` was even used), training reviewers to ignore it as boilerplate.

**Mitigation:** Make the warning conditional — only emit it on views that actually contain `TOP(` without a corresponding `ORDER BY`, so its presence is a genuine signal rather than constant noise.

**Automation stance: CONTINUE.** Functionally fine; this is a signal-to-noise quality issue, not a correctness one.

---

## Remediation priority summary

| # | Finding | Severity | Stance | Status |
|---|---|---|---|---|
| 1 | OPENJSON undetected, 38 procedures convert to empty files | CRITICAL | STOP | **FIXED** |
| 5 | `FOR SYSTEM_TIME AS OF` ≠ Delta time travel, design doc asserts false equivalence | HIGH | STOP | **FIXED** |
| 2 | Temp-table regex never matches (`\b#\w+\b` bug) | HIGH | WARN→STOP after fix | **FIXED** |
| 3 | Shared mutable SSIS variable vs. parallelization recommendation | HIGH | WARN | **FIXED** |
| 4 | MERGE against table variable + compound assignment | HIGH | WARN (already routed, improve message) | **FIXED** |
| 7 | Cross-entity restart consistency gap | MEDIUM | WARN | **FIXED (documentation)** |
| 8 | Silent dedup drops duplicate-defined objects | MEDIUM | WARN | **FIXED** |
| 10 | Sequences/WebApi medallion mislabeling | MEDIUM | WARN | **FIXED** |
| 11 | PySpark-only functions lose SQL-callable shape | MEDIUM | WARN | **FIXED** |
| 6 | Dynamic SQL hidden-dependency exposure (none active) | MEDIUM | CONTINUE / WARN if reused | Not fixed (by design — no active instance) |
| 9 | UC naming collision (none active, unguarded) | LOW | CONTINUE / STOP if triggered | **FIXED** (guard added) |
| 12 | ISNULL→COALESCE type coercion | LOW | CONTINUE | Not fixed (by design — no confirmed harm) |
| 13 | Generic TOP/LIMIT warning noise | LOW | CONTINUE | **FIXED** |

_Full structured detail for each finding, including verification evidence, is in `remediation_backlog.csv`._
