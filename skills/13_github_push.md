<!-- Step 13: GitHub Push — paste this prompt directly into Claude Code -->

This step covers publishing the accelerator to GitHub: initial repo creation and
push, then tagging and creating the first release. Paste Part 1 first, review the
output, then paste Part 2. Replace the repo name, description, topics, and GitHub
username/URL with your own before pasting if reusing this skill for a different
project.

## Part 1 — Initialise Git and Create the GitHub Repository

Initialise git locally and create a new GitHub repository for this accelerator.

Tasks:
1. initialise a git repository in the project root:
   git init
   git add .
   git commit -m "feat: initial accelerator scaffold with WideWorldImporters sample support"

2. create a new GitHub repository using the GitHub CLI:
   - repo name: sql-ssis-to-databricks-accelerator
   - description: "A reusable Python accelerator that converts SQL Server/Synapse + SSIS solutions to Databricks using medallion architecture"
   - visibility: public
   - do not initialise with a README (we already have one)
   - add topics: databricks, ssis, sql-server, azure-synapse, data-migration, medallion-architecture, delta-lake, unity-catalog, etl, data-engineering

3. add the remote origin and push:
   git remote add origin https://github.com/shivanandiyer/sql-ssis-to-databricks-accelerator.git
   git branch -M main
   git push -u origin main

Run these commands now and confirm the repo was created and the push succeeded.

## Part 2 — Create the First Release

Create the first release on the GitHub repository.

Tasks:
1. create and push a version tag:
   git tag -a v0.1.0 -m "v0.1.0 - Initial release with WideWorldImporters sample support"
   git push origin v0.1.0

2. create a GitHub release using the GitHub CLI:
   gh release create v0.1.0 \
     --title "v0.1.0 - Initial Release" \
     --notes-file CHANGELOG.md \
     --latest

3. verify the release page shows:
   - correct tag
   - correct release notes from CHANGELOG.md
   - the release is marked as latest

Confirm the release URL and output it.
