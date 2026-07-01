-- Source: DW:Dimension.Date  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Dimension/Tables/Date.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.silver.date (
    Date DATE NOT NULL,
    DateKey INT NOT NULL,
    Day STRING NOT NULL COMMENT 'source type: Number]',
    Day STRING NOT NULL,
    Day STRING NOT NULL COMMENT 'source type: of',
    Day STRING NOT NULL COMMENT 'source type: of',
    Day STRING NOT NULL COMMENT 'source type: of',
    Day STRING NOT NULL COMMENT 'source type: of',
    Week STRING NOT NULL COMMENT 'source type: of',
    Month STRING NOT NULL,
    Short STRING NOT NULL COMMENT 'source type: Month]',
    Quarter STRING NOT NULL,
    Half STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Calendar STRING NOT NULL COMMENT 'source type: Day',
    Calendar STRING NOT NULL COMMENT 'source type: Day',
    Calendar STRING NOT NULL COMMENT 'source type: Week',
    Calendar STRING NOT NULL COMMENT 'source type: Week',
    Calendar STRING NOT NULL COMMENT 'source type: Month',
    Calendar STRING NOT NULL COMMENT 'source type: Month',
    Calendar STRING NOT NULL COMMENT 'source type: Month',
    Calendar STRING NOT NULL COMMENT 'source type: Quarter',
    Calendar STRING NOT NULL COMMENT 'source type: Quarter',
    Calendar STRING NOT NULL COMMENT 'source type: Quarter',
    Calendar STRING NOT NULL COMMENT 'source type: Half',
    Calendar STRING NOT NULL COMMENT 'source type: Half',
    Calendar STRING NOT NULL COMMENT 'source type: Year',
    Calendar STRING NOT NULL COMMENT 'source type: Year]',
    Calendar STRING NOT NULL COMMENT 'source type: Year',
    Fiscal STRING NOT NULL COMMENT 'source type: Month',
    Fiscal STRING NOT NULL COMMENT 'source type: Month',
    Fiscal STRING NOT NULL COMMENT 'source type: Quarter',
    Fiscal STRING NOT NULL COMMENT 'source type: Quarter',
    Fiscal STRING NOT NULL COMMENT 'source type: Half',
    Fiscal STRING NOT NULL COMMENT 'source type: Half',
    Fiscal STRING NOT NULL COMMENT 'source type: Year]',
    Fiscal STRING NOT NULL COMMENT 'source type: Year',
    Date STRING NOT NULL COMMENT 'source type: Key]',
    Year STRING NOT NULL COMMENT 'source type: Week',
    Year STRING NOT NULL COMMENT 'source type: Month',
    Year STRING NOT NULL COMMENT 'source type: Quarter',
    Year STRING NOT NULL COMMENT 'source type: Half',
    Year STRING NOT NULL COMMENT 'source type: Key]',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Beginning STRING NOT NULL COMMENT 'source type: of',
    Fiscal STRING NOT NULL COMMENT 'source type: Year',
    Fiscal STRING NOT NULL COMMENT 'source type: Year',
    Fiscal STRING NOT NULL COMMENT 'source type: Year',
    ISO STRING NOT NULL COMMENT 'source type: Week'
)
USING DELTA
COMMENT 'Converted from DW:Dimension.Date'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Day` (Number] -> STRING): Unrecognised SQL Server type 'Number]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Day` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Day` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Day` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Day` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Week` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Short` (Month] -> STRING): Unrecognised SQL Server type 'Month]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Half` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Calendar` (Day -> STRING): Unrecognised SQL Server type 'Day' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Calendar` (Day -> STRING): Unrecognised SQL Server type 'Day' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Calendar` (Week -> STRING): Unrecognised SQL Server type 'Week' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Week -> STRING): Unrecognised SQL Server type 'Week' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Month -> STRING): Unrecognised SQL Server type 'Month' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Month -> STRING): Unrecognised SQL Server type 'Month' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Month -> STRING): Unrecognised SQL Server type 'Month' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Quarter -> STRING): Unrecognised SQL Server type 'Quarter' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Quarter -> STRING): Unrecognised SQL Server type 'Quarter' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Quarter -> STRING): Unrecognised SQL Server type 'Quarter' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Half -> STRING): Unrecognised SQL Server type 'Half' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Half -> STRING): Unrecognised SQL Server type 'Half' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Year -> STRING): Unrecognised SQL Server type 'Year' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Year] -> STRING): Unrecognised SQL Server type 'Year]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Calendar` (Year -> STRING): Unrecognised SQL Server type 'Year' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Fiscal` (Month -> STRING): Unrecognised SQL Server type 'Month' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Fiscal` (Month -> STRING): Unrecognised SQL Server type 'Month' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Fiscal` (Quarter -> STRING): Unrecognised SQL Server type 'Quarter' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Fiscal` (Quarter -> STRING): Unrecognised SQL Server type 'Quarter' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Fiscal` (Half -> STRING): Unrecognised SQL Server type 'Half' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Fiscal` (Half -> STRING): Unrecognised SQL Server type 'Half' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Fiscal` (Year] -> STRING): Unrecognised SQL Server type 'Year]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Fiscal` (Year -> STRING): Unrecognised SQL Server type 'Year' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Year` (Week -> STRING): Unrecognised SQL Server type 'Week' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Year` (Month -> STRING): Unrecognised SQL Server type 'Month' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Year` (Quarter -> STRING): Unrecognised SQL Server type 'Quarter' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Year` (Half -> STRING): Unrecognised SQL Server type 'Half' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Year` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Beginning` (of -> STRING): Unrecognised SQL Server type 'of' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Fiscal` (Year -> STRING): Unrecognised SQL Server type 'Year' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Fiscal` (Year -> STRING): Unrecognised SQL Server type 'Year' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Fiscal` (Year -> STRING): Unrecognised SQL Server type 'Year' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `ISO` (Week -> STRING): Unrecognised SQL Server type 'Week' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.