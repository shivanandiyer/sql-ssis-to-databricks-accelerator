---
name: Unsupported object type / construct
about: A SQL Server, Synapse, or SSIS construct isn't recognized or isn't converted correctly
title: "[UNSUPPORTED] "
labels: unsupported-construct
assignees: ""
---

## What construct is this

- [ ] SQL Server / T-SQL syntax (e.g. a function, clause, or data type)
- [ ] An object type entirely (e.g. a kind of table/view/procedure the
      classifier doesn't recognize at all)
- [ ] SSIS task type or control-flow construct
- [ ] SSIS expression-language construct
- [ ] Other

## Source excerpt

Paste the actual DDL or DTSX excerpt (redact anything sensitive, but keep
the *structure* intact — a paraphrase often loses the exact detail that
matters):

```sql
-- paste here
```

## What the accelerator currently does

Run the relevant step and paste what happened — does it crash, silently
produce empty/incomplete output (the most important case to report — see
`docs/example-run/adversarial_review.md`'s OPENJSON finding for why), or
correctly flag `needs_review` with a generic rather than specific warning?

```
-- paste generated output or error here
```

## What it should do instead

If you know the correct Databricks/PySpark/Delta equivalent (or know that
none exists and it should be flagged for manual redesign), describe it —
this is the most useful part of the report and often the difference between
someone picking this up in a day vs. a month.

## Is this present in the bundled WWI sample corpus?

- [ ] Yes — should be detectable by re-running the pipeline against it
- [ ] No — this is from a different source repo (please share an anonymized
      excerpt as above; real source patterns make far better test fixtures
      than synthetic ones — see CONTRIBUTING.md)

## Would you be willing to contribute a fix?

A fix for this category of issue typically needs: a pattern addition to the
relevant parser/scorer, a conversion branch, a fixture, and a test — see
CONTRIBUTING.md's "How to add support for a new SQL Server object type" /
"How to add a new SSIS task mapping" sections.
