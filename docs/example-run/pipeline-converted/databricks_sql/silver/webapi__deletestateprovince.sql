-- Source: OLTP:WebApi.DeleteStateProvince  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/DeleteStateProvince.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

DELETE Application.StateProvinces
	WHERE StateProvinceID = @StateProvinceID;