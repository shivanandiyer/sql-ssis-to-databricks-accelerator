# Converted from SSIS Data Flow Task: Extract Updated Stock Item Data to Staging
# Source: EXEC-based OLE DB Source -> OLE DB Destination, no in-pipeline transforms detected.

from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()


def run(entity: str, last_cutoff: str, new_cutoff: str, environment: str, catalog: str) -> None:
    """Extract changed rows and land them in the Bronze staging table.

    Original source query:
        'EXEC Integration.GetStockItemUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [WWI Stock Item ID] int, \n        [Stock Item] nvarchar(100), \n        Color nvarchar(20), \n        [Selling Package] nvarchar(50), \n        [Buying Package] nvarchar(50), \n        Brand nvarchar(50), \n        Size nvarchar(20), \n        [Lead Time Days] int, \n        [Quantity Per Outer] int, \n        [Is Chiller Stock] bit, \n        Barcode nvarchar(50), \n        [Tax Rate] decimal(18,3), \n        [Unit Price] decimal(18,2), \n        [Recommended Retail Price] decimal(18,2), \n        [Typical Weight Per Unit] decimal(18,3), \n        Photo varbinary(max), \n        [Valid From] datetime2(7), \n        [Valid To] datetime2(7)\n    )\n);'
    Original destination table: Integration.StockItem_Staging

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
        .option("query", 'EXEC Integration.GetStockItemUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [WWI Stock Item ID] int, \n        [Stock Item] nvarchar(100), \n        Color nvarchar(20), \n        [Selling Package] nvarchar(50), \n        [Buying Package] nvarchar(50), \n        Brand nvarchar(50), \n        Size nvarchar(20), \n        [Lead Time Days] int, \n        [Quantity Per Outer] int, \n        [Is Chiller Stock] bit, \n        Barcode nvarchar(50), \n        [Tax Rate] decimal(18,3), \n        [Unit Price] decimal(18,2), \n        [Recommended Retail Price] decimal(18,2), \n        [Typical Weight Per Unit] decimal(18,3), \n        Photo varbinary(max), \n        [Valid From] datetime2(7), \n        [Valid To] datetime2(7)\n    )\n);' if False else "<TODO: parameterise with last_cutoff/new_cutoff>")
        .load()
    )
    target_fqn = f"{catalog}.bronze.integration_stockitem_staging"
    df.write.format("delta").mode("overwrite").saveAsTable(target_fqn)