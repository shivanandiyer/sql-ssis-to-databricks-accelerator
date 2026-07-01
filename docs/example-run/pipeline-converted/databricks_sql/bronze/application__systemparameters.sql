-- Source: OLTP:Application.SystemParameters  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/SystemParameters.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.application__systemparameters (
    SystemParameterID INT NOT NULL,
    DeliveryAddressLine1 STRING NOT NULL,
    DeliveryAddressLine2 STRING,
    DeliveryCityID INT NOT NULL,
    DeliveryPostalCode STRING NOT NULL,
    DeliveryLocation STRING NOT NULL COMMENT 'source type: [sys].[geography]',
    PostalAddressLine1 STRING NOT NULL,
    PostalAddressLine2 STRING,
    PostalCityID INT NOT NULL,
    PostalPostalCode STRING NOT NULL,
    ApplicationSettings STRING NOT NULL,
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Application.SystemParameters'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `SystemParameterID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta
-- `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline
-- (see target_state_architecture.md, Unity Catalog section).
-- Column `DeliveryLocation` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake.
-- Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library
-- (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Application_SystemParameters_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[P
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Application_SystemParameters_DeliveryCityID_Application_Cities] FOREIGN KEY ([DeliveryCityID])
-- REFERENCES
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Application_SystemParameters_PostalCityID_Application_Cities] FOREIGN KEY ([PostalCityID])
-- REFERENCES [Ap