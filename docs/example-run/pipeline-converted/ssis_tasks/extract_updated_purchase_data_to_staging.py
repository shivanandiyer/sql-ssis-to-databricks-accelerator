# Converted from SSIS Data Flow Task: Extract Updated Purchase Data to Staging
# Source: EXEC-based OLE DB Source -> OLE DB Destination, no in-pipeline transforms detected.

from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()


def run(entity: str, last_cutoff: str, new_cutoff: str, environment: str, catalog: str) -> None:
    """Extract changed rows and land them in the Bronze staging table.

    Original source query:
        'EXEC Integration.GetPurchaseUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [Date Key] date,\n        [WWI Purchase Order ID] int,\n        [Ordered Outers] int,\n        [Ordered Quantity] int,\n        [Received Outers] int,\n        [Package] nvarchar(50),\n        [Is Order Line Finalized] bit,\n        [WWI Supplier ID] int,\n        [WWI Stock Item ID] int,\n        [Last Modified When] datetime2(7)\n    )\n);'
    Original destination table: Integration.Purchase_Staging

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
        .option("query", 'EXEC Integration.GetPurchaseUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [Date Key] date,\n        [WWI Purchase Order ID] int,\n        [Ordered Outers] int,\n        [Ordered Quantity] int,\n        [Received Outers] int,\n        [Package] nvarchar(50),\n        [Is Order Line Finalized] bit,\n        [WWI Supplier ID] int,\n        [WWI Stock Item ID] int,\n        [Last Modified When] datetime2(7)\n    )\n);' if False else "<TODO: parameterise with last_cutoff/new_cutoff>")
        .load()
    )
    target_fqn = f"{catalog}.bronze.integration_purchase_staging"
    df.write.format("delta").mode("overwrite").saveAsTable(target_fqn)