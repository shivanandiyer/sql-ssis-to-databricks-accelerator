# Source: OLTP:DataLoadSimulation.GetSupplierCategoryID  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Functions/GetSupplierCategoryID.sql)
# Converted: SCALAR_FUNCTION -> PySpark function (registered as a UDF where needed).
# Original T-SQL body is reproduced as a comment for reference; logic must be
# re-implemented in Python below.
#
# --- original T-SQL ---
# CREATE FUNCTION [DataLoadSimulation].[GetSupplierCategoryID]
# ( @SupplierCategoryName NVARCHAR(50) )
# RETURNS INT
# AS
# BEGIN
# 
# /*
# Notes:
#   Returns the SupplierCategoryID for the passed in Supplier Category Name
# 
# Usage:
#   DECLARE @SupplierCatID INT
#   SET @SupplierCatID = [DataLoadSimulation].[GetSupplierCategoryID] ('Toy Supplier')
#   SELECT @SupplierCatID
# 
# */
# 
#   DECLARE @SupCatID INT
# 
#   SELECT TOP 1 @SupCatID = SupplierCategoryID
#     FROM Purchasing.SupplierCategories
#    WHERE SupplierCategoryName = @SupplierCategoryName
#      AND ValidTo = '99991231 23:59:59.9999999'
# 
#   RETURN @SupCatID
# 
# END
# --- end original T-SQL ---

# NOTE: the source function's callers invoke it inline inside T-SQL SELECT
# statements (not as a separate batch step) — registering it as a SQL UDF
# (not just a DataFrame-API udf object) preserves that inline-SQL-callable
# shape. Found by adversarial review: a bare `udf(...)` object is only
# usable from PySpark DataFrame code, which would force every original
# inline-SQL caller to be rewritten as a separate join/precompute step.
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

spark = SparkSession.getActiveSession()


def getsuppliercategoryid(*args):
    """TODO: implement equivalent logic to the source T-SQL function above."""
    raise NotImplementedError('Manual conversion required — see source T-SQL above.')


getsuppliercategoryid_udf = udf(getsuppliercategoryid, StringType())  # TODO: confirm return type from source RETURNS clause
spark.udf.register('GetSupplierCategoryID', getsuppliercategoryid, StringType())  # makes it callable from Databricks SQL as GetSupplierCategoryID(...)