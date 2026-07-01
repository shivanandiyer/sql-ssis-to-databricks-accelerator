-- Source: DW:Integration.GetLineageKey  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/GetLineageKey.sql)
-- Split 1 of 2: SQL transformation logic extracted from an orchestration-heavy
-- stored procedure (rule: separate SQL transformation from workflow orchestration).
-- The CURSOR/WHILE control flow that drove row-by-row iteration in the source is
-- NOT reproduced here — see the companion PySpark orchestration file, which expresses
-- the same iteration as a set-based MERGE or a small parameterised loop.

INSERT Integration.Lineage
        ([Data Load Started], [Table Name], [Data Load Completed],
         [Was Successful], [Source System Cutoff Time])
    OUTPUT
        inserted.[Lineage Key] as LineageKey
    VALUES
        (@DataLoadStartedWhen, @TableName, NULL,
         0, @NewCutoffTime);