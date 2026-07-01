# Converted from SSIS Data Flow Task: Extract Updated Sale Data to Staging
# Source: EXEC-based OLE DB Source -> OLE DB Destination, no in-pipeline transforms detected.

from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()


def run(entity: str, last_cutoff: str, new_cutoff: str, environment: str, catalog: str) -> None:
    """Extract changed rows and land them in the Bronze staging table.

    Original source query:
        'EXEC Integration.GetSaleUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [Invoice Date Key] date,\n        [Delivery Date Key] date,\n        [WWI Invoice ID] int,\n        [Description] nvarchar(100),\n        [Package] nvarchar(50),\n        [Quantity] int,\n        [Unit Price] decimal(18,2),\n        [Tax Rate] decimal(18,3),\n        [Total Excluding Tax] decimal(18,2),\n        [Tax Amount] decimal(18,2),\n        [Profit] decimal(18,2),\n        [Total Including Tax] decimal(18,2),\n        [Total Dry Items] int,\n        [Total Chiller Items] int,\n        [WWI City ID] int,\n        [WWI Customer ID] int,\n        [WWI Bill To Customer ID] int,\n        [WWI Stock Item ID] int,\n        [WWI Salesperson ID] int,\n        [Last Modified When] datetime2(7)\n    )\n);'
    Original destination table: Integration.Sale_Staging

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
        .option("query", 'EXEC Integration.GetSaleUpdates ?, ?\nWITH RESULT SETS\n(\n    (\n        [Invoice Date Key] date,\n        [Delivery Date Key] date,\n        [WWI Invoice ID] int,\n        [Description] nvarchar(100),\n        [Package] nvarchar(50),\n        [Quantity] int,\n        [Unit Price] decimal(18,2),\n        [Tax Rate] decimal(18,3),\n        [Total Excluding Tax] decimal(18,2),\n        [Tax Amount] decimal(18,2),\n        [Profit] decimal(18,2),\n        [Total Including Tax] decimal(18,2),\n        [Total Dry Items] int,\n        [Total Chiller Items] int,\n        [WWI City ID] int,\n        [WWI Customer ID] int,\n        [WWI Bill To Customer ID] int,\n        [WWI Stock Item ID] int,\n        [WWI Salesperson ID] int,\n        [Last Modified When] datetime2(7)\n    )\n);' if False else "<TODO: parameterise with last_cutoff/new_cutoff>")
        .load()
    )
    target_fqn = f"{catalog}.bronze.integration_sale_staging"
    df.write.format("delta").mode("overwrite").saveAsTable(target_fqn)