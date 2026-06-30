# Rollback Notes

Rollback has two independent parts — **code/job definition** and **data** —
because Databricks Asset Bundles version the former but not the latter.
Decide which one actually needs reverting before acting.

## 1. Code / job definition rollback

The bundle (`bundle/databricks.yml`, `bundle/resources/*.yml`) is fully
declarative and tracked in git. To roll back a bad deploy:

```bash
git log --oneline -- bundle/  # find the last-known-good commit
git checkout <good-commit-sha> -- bundle/ output/
./deploy/deploy.sh <env>
```

`deploy/promote.sh` records the promoted commit SHA in
`deploy/.last_promoted_to_<env>` on every promotion — read that file to find
exactly what was last known-good for a given environment:

```bash
cat deploy/.last_promoted_to_prod
```

Because `databricks bundle deploy` is idempotent, redeploying an older bundle
state is safe and simply overwrites the job/warehouse definitions back to
that state — no manual cleanup of the newer job definition is needed.

## 2. Data rollback

Every converted table is Delta with Change Data Feed enabled
(`TBLPROPERTIES (delta.enableChangeDataFeed = true)` — see
`accelerator/converters/sql_converter.py`'s table DDL template), so Delta's
native time travel is the rollback mechanism:

```sql
-- Inspect history to find the version/timestamp before the bad run
DESCRIBE HISTORY wwi_prod.silver.city;

-- Restore to the version before the bad run
RESTORE TABLE wwi_prod.silver.city TO VERSION AS OF 41;
-- or
RESTORE TABLE wwi_prod.silver.city TO TIMESTAMP AS OF '2026-06-29T02:00:00Z';
```

**Order matters for multi-table rollback.** Restore in *reverse* dependency
order (Gold first, then Silver, then Bronze) — restoring a Dimension table
without first restoring the Facts that reference it can leave Facts pointing
at surrogate keys that briefly don't exist. Use
`outputs/dependencies.json`'s `topological_order`, reversed, as the
restore sequence (mirrors `deploy/sql_deploy.py`'s deploy order, inverted).

## 3. Watermark rollback

If a bad run advanced `<catalog>.ops.etl_watermark` past data that is being
rolled back, the watermark must be rolled back too, or the next run will
skip the now-missing data on its next incremental extract:

```sql
-- Use the same RESTORE TABLE approach on the watermark table itself —
-- it's a regular Delta table.
RESTORE TABLE wwi_prod.ops.etl_watermark TO VERSION AS OF 12;
```

**This is the step most likely to be forgotten.** A data-only restore
without a matching watermark restore produces a pipeline that silently
believes it already processed data it no longer has.

## 4. Full pipeline rollback runbook

1. Pause the job (`pause_status: PAUSED` in `conf/<env>.yml`, redeploy) so no
   new run starts mid-rollback.
2. Identify the bad run's start timestamp from the Workflow run history.
3. Restore tables in reverse topological order (Gold → Silver → Bronze),
   each `TO TIMESTAMP AS OF` just before the bad run started.
4. Restore `ops.etl_watermark` to the same timestamp.
5. Roll back the bundle/code if the bad run was caused by a bad deploy, not
   bad source data (see Section 1).
6. Unpause the job and trigger a single manual run to confirm the watermark
   correctly resumes from the restored point before re-enabling the schedule.

## 5. Cross-entity consistency during partial failures (not a rollback per se)

The 13 entity loads are independent task chains with no cross-entity
transaction boundary. If the job fails after entities A–F complete (data +
watermark advanced) but entity G fails, a Workflow **repair run** correctly
resumes only G — but any downstream consumer that queried between the
failure and the repair (e.g. a Gold-layer report joining multiple entities)
would have seen a **point-in-time-inconsistent** snapshot: A–F at their new
watermark, G–M at their old one. This is inherited from the source design
(SSIS's single package has the same exposure) — the accelerator doesn't make
it worse, but it's also not something a rollback fixes after the fact, since
by the time you'd roll back, the inconsistent read has already happened.

**Mitigation for consumers who need point-in-time consistency** across
entities: query Gold-layer tables via a "last fully-consistent run" tag
rather than always reading the live table — e.g. write a
`wwi_<env>.ops.last_consistent_run_ts` row only after *all* 13 entity chains
in a run succeed, and have consistency-sensitive consumers filter
(`TIMESTAMP AS OF`) against that tag instead of reading current state
unconditionally.

## 6. What rollback does NOT cover

- **Source-system changes already extracted and acted upon downstream of
  this pipeline** (e.g. a BI dashboard cached query results) — out of scope;
  notify downstream consumers separately.
- **Unity Catalog grant changes** — these aren't versioned by Delta history;
  if a bad deploy altered permissions, that must be reverted manually via
  `GRANT`/`REVOKE` or by redeploying the bundle's `permissions:` block.
