<!-- Step 14: Architecture Override (Optional / On Demand) — paste this prompt directly into Claude Code -->

Run this step ONLY if you want to test or apply a non-medallion architecture.

Override the default medallion architecture with a custom target architecture.

User-specified architecture: [REPLACE WITH YOUR CHOICE]

Examples of valid overrides:
- Data Vault 2.0 (Hubs, Satellites, Links)
- Lambda (batch + speed layer)
- Kappa (streaming-first)
- Flat Lakehouse (single curated layer, no medallion tiers)
- Hybrid (medallion Bronze/Silver + Data Vault Gold)

Tasks:
1. Re-map all source objects against the new architecture
2. Update medallion_mapping.csv with the new layer assignments
3. Update target_state_architecture.md to reflect the override
4. Update orchestration_design.md if workflow task order changes
5. Identify any objects whose conversion strategy changes under this architecture
6. Update conversion_manifest.json accordingly
7. Document tradeoffs vs default medallion design

Do not re-run conversion unless I explicitly ask for it.
Only update the design artifacts.
