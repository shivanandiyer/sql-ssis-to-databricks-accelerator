# Review Required: OLTP:DataLoadSimulation.GetFicticiousName

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/GetFicticiousName.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[GetFicticiousName]
  @FirstName AS NVARCHAR(20) OUTPUT
, @LastName  AS NVARCHAR(20) OUTPUT
, @FullName  AS NVARCHAR(40) OUTPUT
, @Email     AS NVARCHAR(200) OUTPUT
AS
BEGIN
/*
Notes:
  Reads the table of Microsoft lawyer approved names, then randomly
  selects one that has not already been used in the Application.People
  table.

Usage:
  DECLARE @myFirstName AS NVARCHAR(20)
  DECLARE @myLastName  AS NVARCHAR(20)
  DECLARE @myFullName  AS NVARCHAR(40)
  DECLARE @myEmail     AS NVARCHAR(200)

  EXEC [DataLoadSimulation].[GetFicticiousName] @FirstName = @myFirstName OUTPUT
                                              , @LastName  = @myLastName OUTPUT
                                              , @FullName  = @myFullName OUTPUT
                                              , @Email     = @myEmail OUTPUT

  SELECT @myFirstName, @myLastName, @myFullName, @myEmail

*/

  -- Randomly pick a name from the ficticious name pool that has not
  -- already been used in the application people table
  SELECT TOP 1
         @FirstName = PreferredName
       , @LastName  = LastName
       , @FullName  = FullName
       , @Email     = ToEmail
    FROM [DataLoadSimulation].[FicticiousNamePool] fnp
   WHERE fnp.FullName NOT IN (SELECT ap.FullName
                                FROM [Application].[People] ap
                               WHERE ap.FullName = fnp.FullName
                             )
  ORDER BY NEWID()

  RETURN
END
;
GO
```