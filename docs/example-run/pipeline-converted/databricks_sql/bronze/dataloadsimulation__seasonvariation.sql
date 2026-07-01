-- Source: OLTP:DataLoadSimulation.SeasonVariation  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Tables/SeasonVariation.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.dataloadsimulation__seasonvariation (
    Year INT NOT NULL,
    Season SMALLINT NOT NULL,
    YearlyVariation DOUBLE NOT NULL,
    SeasonalVariation DOUBLE NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:DataLoadSimulation.SeasonVariation'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
