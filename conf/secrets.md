# Secret References

This accelerator's converted assets reference exactly one external credential
set per environment: the source SQL Server (`WideWorldImporters`) connection.
The destination is Unity Catalog itself, which uses Databricks-native
identity (service principals / OAuth) — no secret needed there.

## Required secret scopes

| Environment | Scope name | Keys |
|---|---|---|
| dev | `wwi-source-db-dev` | `jdbc_url`, `username`, `password` |
| test | `wwi-source-db-test` | `jdbc_url`, `username`, `password` |
| prod | `wwi-source-db-prod` | `jdbc_url`, `username`, `password` |

## Creating the scopes (one-time, per environment)

```bash
databricks secrets create-scope wwi-source-db-dev
databricks secrets put-secret wwi-source-db-dev jdbc_url
databricks secrets put-secret wwi-source-db-dev username
databricks secrets put-secret wwi-source-db-dev password
```

Repeat for `wwi-source-db-test` and `wwi-source-db-prod` against their
respective workspaces. Use a secrets manager-backed scope (Azure Key Vault or
AWS Secrets Manager-backed scope) in test/prod rather than a
Databricks-managed scope, so rotation doesn't require a bundle redeploy.

## How generated code references these secrets

Every PySpark extract module under `output/ssis_tasks/extract_*.py` derives
the scope name from the `environment` Workflow task parameter (set per
target in `bundle/databricks.yml` / `conf/<env>.yml`) — never hardcoded:

```python
def run(entity: str, last_cutoff: str, new_cutoff: str, environment: str, catalog: str) -> None:
    secret_scope = f"wwi-source-db-{environment}"
    df = (
        spark.read.format("jdbc")
        .option("url", dbutils.secrets.get(secret_scope, "jdbc_url"))
        .option("user", dbutils.secrets.get(secret_scope, "username"))
        .option("password", dbutils.secrets.get(secret_scope, "password"))
        ...
    )
```

The same module therefore works unmodified across dev/test/prod — only the
`environment` base parameter changes, which `bundle/resources/wwi_daily_etl_main.job.yml`
already passes through from `${bundle.target}`.

## Never

- Never commit secret *values* to this repository — `conf/*.yml` files
  contain scope/key *names* only.
- Never reuse the dev secret scope's underlying credential in test/prod —
  each environment must have its own source-system service account with the
  minimum read-only grants needed for the 14 entities this pipeline extracts.
