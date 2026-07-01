# Converted from SSIS Data Flow Task: Extract All Stock Holding Data to Staging
# Source: EXEC-based OLE DB Source -> OLE DB Destination, no in-pipeline transforms detected.

from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()


def run(entity: str, last_cutoff: str, new_cutoff: str, environment: str, catalog: str) -> None:
    """Extract changed rows and land them in the Bronze staging table.

    Original source query:
        'EXEC Integration.GetStockHoldingUpdates\nWITH RESULT SETS\n(\n    (\n        [Quantity On Hand] int,\n        [Bin Location] nvarchar(20),\n        [Last Stocktake Quantity] int,\n        [Last Cost Price] int,\n        [Reorder Level] int,\n        [Target Stock Level] int,\n        [WWI Stock Item ID] int\n    )\n);'
    Original destination table: Integration.StockHolding_Staging

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
        .option("query", 'EXEC Integration.GetStockHoldingUpdates\nWITH RESULT SETS\n(\n    (\n        [Quantity On Hand] int,\n        [Bin Location] nvarchar(20),\n        [Last Stocktake Quantity] int,\n        [Last Cost Price] int,\n        [Reorder Level] int,\n        [Target Stock Level] int,\n        [WWI Stock Item ID] int\n    )\n);' if False else "<TODO: parameterise with last_cutoff/new_cutoff>")
        .load()
    )
    target_fqn = f"{catalog}.bronze.integration_stockholding_staging"
    df.write.format("delta").mode("overwrite").saveAsTable(target_fqn)