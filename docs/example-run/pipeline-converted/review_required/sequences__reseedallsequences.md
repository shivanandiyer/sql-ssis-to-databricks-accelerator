# Review Required: DW:Sequences.ReseedAllSequences

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Sequences/Stored Procedures/ReseedAllSequences.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Sequences.ReseedAllSequences
AS BEGIN
    -- Ensures that the next sequence values are above the maximum value of the related table columns
    SET NOCOUNT ON;

    EXEC Sequences.ReseedSequenceBeyondTableValues @SequenceName = 'CityKey', @SchemaName = 'Dimension', @TableName = 'City', @ColumnName = 'City Key';
    EXEC Sequences.ReseedSequenceBeyondTableValues @SequenceName = 'CustomerKey', @SchemaName = 'Dimension', @TableName = 'Customer', @ColumnName = 'Customer Key';
    EXEC Sequences.ReseedSequenceBeyondTableValues @SequenceName = 'EmployeeKey', @SchemaName = 'Dimension', @TableName = 'Employee', @ColumnName = 'Employee Key';
    EXEC Sequences.ReseedSequenceBeyondTableValues @SequenceName = 'LineageKey', @SchemaName = 'Integration', @TableName = 'Lineage', @ColumnName = 'Lineage Key';
    EXEC Sequences.ReseedSequenceBeyondTableValues @SequenceName = 'PaymentMethodKey', @SchemaName = 'Dimension', @TableName = 'Payment Method', @ColumnName = 'Payment Method Key';
    EXEC Sequences.ReseedSequenceBeyondTableValues @SequenceName = 'StockItemKey', @SchemaName = 'Dimension', @TableName = 'Stock Item', @ColumnName = 'Stock Item Key';
    EXEC Sequences.ReseedSequenceBeyondTableValues @SequenceName = 'SupplierKey', @SchemaName = 'Dimension', @TableName = 'Supplier', @ColumnName = 'Supplier Key';
    EXEC Sequences.ReseedSequenceBeyondTableValues @SequenceName = 'TransactionTypeKey', @SchemaName = 'Dimension', @TableName = 'Transaction Type', @ColumnName = 'Transaction Type Key';
END;
```