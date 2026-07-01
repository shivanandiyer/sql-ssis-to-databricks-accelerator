# Converted from SSIS Data Flow Task: Extract Updated Employee Data to Staging
# Source: EXEC-based OLE DB Source -> OLE DB Destination, no in-pipeline transforms detected.

from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()


def run(entity: str, last_cutoff: str, new_cutoff: str, environment: str, catalog: str) -> None:
    """Extract changed rows and land them in the Bronze staging table.

    Original source query:
        'EXEC Integration.GetEmployeeUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [WWI Employee ID] int,\n        Employee nvarchar(50),\n        [Preferred Name] nvarchar(50),\n        [Is Salesperson] bit,\n        Photo varbinary(max),\n        [Valid From] datetime2(7),\n        [Valid To] datetime2(7)\n    )\n);'
    Original destination table: Integration.Employee_Staging

    `environment` and `catalog` are passed as Workflow task base_parameters
    (see conf/<env>.yml and bundle/databricks.yml `variables.catalog`) — the
    secret scope name is derived from environment, never hardcoded, so the
    same module works unmodified across dev/test/prod.
    """
    secret_scope = f"wwi-source-db-{environment}"
    # TODO: parameterise the query below with last_cutoff/new_cutoff.
    df = (
        spark.read.format("jdbc")
        .option("url", dbutils.secrets.get(secret_scope, "jdbc_url"))
        .option("user", dbutils.secrets.get(secret_scope, "username"))
        .option("password", dbutils.secrets.get(secret_scope, "password"))
        .option("query", 'EXEC Integration.GetEmployeeUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [WWI Employee ID] int,\n        Employee nvarchar(50),\n        [Preferred Name] nvarchar(50),\n        [Is Salesperson] bit,\n        Photo varbinary(max),\n        [Valid From] datetime2(7),\n        [Valid To] datetime2(7)\n    )\n);' if False else "<TODO: parameterise with last_cutoff/new_cutoff>")
        .load()
    )
    target_fqn = f"{catalog}.bronze.integration_employee_staging"
    df.write.format("delta").mode("overwrite").saveAsTable(target_fqn)