# Review Required: OLTP:Application.SystemParameters

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/SystemParameters.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `SystemParameterID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `DeliveryLocation` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Application_SystemParameters_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[P
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Application_SystemParameters_DeliveryCityID_Application_Cities] FOREIGN KEY ([DeliveryCityID]) REFERENCES
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Application_SystemParameters_PostalCityID_Application_Cities] FOREIGN KEY ([PostalCityID]) REFERENCES [Ap

## Source DDL (for reference)

```sql
CREATE TABLE [Application].[SystemParameters] (
    [SystemParameterID]    INT               CONSTRAINT [DF_Application_SystemParameters_SystemParameterID] DEFAULT (NEXT VALUE FOR [Sequences].[SystemParameterID]) NOT NULL,
    [DeliveryAddressLine1] NVARCHAR (60)     NOT NULL,
    [DeliveryAddressLine2] NVARCHAR (60)     NULL,
    [DeliveryCityID]       INT               NOT NULL,
    [DeliveryPostalCode]   NVARCHAR (10)     NOT NULL,
    [DeliveryLocation]     [sys].[geography] NOT NULL,
    [PostalAddressLine1]   NVARCHAR (60)     NOT NULL,
    [PostalAddressLine2]   NVARCHAR (60)     NULL,
    [PostalCityID]         INT               NOT NULL,
    [PostalPostalCode]     NVARCHAR (10)     NOT NULL,
    [ApplicationSettings]  NVARCHAR (MAX)    NOT NULL,
    [LastEditedBy]         INT               NOT NULL,
    [LastEditedWhen]       DATETIME2 (7)     CONSTRAINT [DF_Application_SystemParameters_LastEditedWhen] DEFAULT (sysdatetime()) NOT NULL,
    CONSTRAINT [PK_Application_SystemParameters] PRIMARY KEY CLUSTERED ([SystemParameterID] ASC),
    CONSTRAINT [FK_Application_SystemParameters_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [FK_Application_SystemParameters_DeliveryCityID_Application_Cities] FOREIGN KEY ([DeliveryCityID]) REFERENCES [Application].[Cities] ([CityID]),
    CONSTRAINT [FK_Application_SystemParameters_PostalCityID_Application_Cities] FOREIGN KEY ([PostalCityID]) REFERENCES [Application].[Cities] ([CityID])
);


GO
CREATE NONCLUSTERED INDEX [FK_Application_SystemParameters_DeliveryCityID]
    ON [Application].[SystemParameters]([DeliveryCityID] ASC);


GO
CREATE NONCLUSTERED INDEX [FK_Application_SystemParameters_PostalCityID]
    ON [Application].[SystemParameters]([PostalCityID] ASC);


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Auto-created to support a foreign key', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'SystemParameters', @level2type = N'INDEX', @level2name = N'FK_Application_SystemParameters_DeliveryCityID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Auto-created to support a foreign key', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'SystemParameters', @level2type = N'INDEX', @level2name = N'FK_Application_SystemParameters_PostalCityID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'Any configurable parameters for the whole system', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'SystemParameters';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Numeric ID used for row holding system parameters', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'SystemParameters', @level2type = N'COLUMN', @level2name = N'SystemParameterID';


GO
EXECUTE sp_addextendedproperty @name
```