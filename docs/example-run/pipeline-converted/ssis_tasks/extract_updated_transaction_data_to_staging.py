# Converted from SSIS Data Flow Task: Extract Updated Transaction Data to Staging
# Source: EXEC-based OLE DB Source -> OLE DB Destination, no in-pipeline transforms detected.

from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()


def run(entity: str, last_cutoff: str, new_cutoff: str, environment: str, catalog: str) -> None:
    """Extract changed rows and land them in the Bronze staging table.

    Original source query:
        'EXEC Integration.GetTransactionUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [Date Key] date,\n        [WWI Customer Transaction ID] int,\n        [WWI Supplier Transaction ID] int,\n        [WWI Invoice ID] int,\n        [WWI Purchase Order ID] int,\n        [Supplier Invoice Number] nvarchar(20),\n        [Total Excluding Tax] decimal(18,2),\n        [Tax Amount] decimal(18,2),\n        [Total Including Tax] decimal(18,2),\n        [Outstanding Balance] decimal(18,2),\n        [Is Finalized] bit,\n        [WWI Customer ID] int,\n        [WWI Bill To Customer ID] int,\n        [WWI Supplier ID] int,\n        [WWI Transaction Type ID] int,\n        [WWI Payment Method ID] int,\n        [Last Modified When] datetime2(7)\n    )\n);'
    Original destination table: Integration.Transaction_Staging

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
        .option("query", 'EXEC Integration.GetTransactionUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [Date Key] date,\n        [WWI Customer Transaction ID] int,\n        [WWI Supplier Transaction ID] int,\n        [WWI Invoice ID] int,\n        [WWI Purchase Order ID] int,\n        [Supplier Invoice Number] nvarchar(20),\n        [Total Excluding Tax] decimal(18,2),\n        [Tax Amount] decimal(18,2),\n        [Total Including Tax] decimal(18,2),\n        [Outstanding Balance] decimal(18,2),\n        [Is Finalized] bit,\n        [WWI Customer ID] int,\n        [WWI Bill To Customer ID] int,\n        [WWI Supplier ID] int,\n        [WWI Transaction Type ID] int,\n        [WWI Payment Method ID] int,\n        [Last Modified When] datetime2(7)\n    )\n);' if False else "<TODO: parameterise with last_cutoff/new_cutoff>")
        .load()
    )
    target_fqn = f"{catalog}.bronze.integration_transaction_staging"
    df.write.format("delta").mode("overwrite").saveAsTable(target_fqn)