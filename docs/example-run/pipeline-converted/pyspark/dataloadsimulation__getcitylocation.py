# Source: OLTP:DataLoadSimulation.GetCityLocation  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Functions/GetCityLocation.sql)
# Converted: SCALAR_FUNCTION -> PySpark function (registered as a UDF where needed).
# Original T-SQL body is reproduced as a comment for reference; logic must be
# re-implemented in Python below.
#
# --- original T-SQL ---
# CREATE FUNCTION [DataLoadSimulation].[GetCityLocation]
# (@CityID INT)
# RETURNS GEOGRAPHY
# AS
# BEGIN
# /*
# Notes:
#   Returns the location for the passed in city id
# 
# Usage:
#   DECLARE @myLoc GEOGRAPHY = [DataLoadSimulation].[GetCityLocation] (1)
#   SELECT @myLoc
# 
# */
# 
#   DECLARE @Loc AS GEOGRAPHY
# 
#   SELECT TOP 1 @Loc = [Location]
#     FROM [Application].Cities
#    WHERE CityID = @CityID
# 
#   RETURN @Loc
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


def getcitylocation(*args):
    """TODO: implement equivalent logic to the source T-SQL function above."""
    raise NotImplementedError('Manual conversion required — see source T-SQL above.')


getcitylocation_udf = udf(getcitylocation, StringType())  # TODO: confirm return type from source RETURNS clause
spark.udf.register('GetCityLocation', getcitylocation, StringType())  # makes it callable from Databricks SQL as GetCityLocation(...)