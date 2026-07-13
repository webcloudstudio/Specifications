# FUNCTIONALITY: Setup Analyze

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | High-level feature index for the --analyze capability. |

## Feature Index

**STEP.1 — Ingest and Postfix**
Detect non-conformed files in the target spec directory. Rename each original file to `<filename>.imported` so it is preserved and excluded from future analyze runs. This step runs before any LLM call.

**STEP.2 — LLM Conversion Agent**
Assemble a prompt from the `.imported` source files + SPECIFICATION_CONTRACT.md + the conversion instructions in `prompts/analyze_ingest.md`. Call `claude -p` to generate the conformed output files (METADATA.md, INTENT.md, ARCHITECTURE.md, FUNCTIONALITY.md, and relevant FEATURE/DATABASE/SCREEN files). Write results into the spec directory without overwriting any files that already conform.

**STEP.3 — Ingest Template Save**
After a successful run, extract the structural fingerprint of the source format and save it to `RulesEngine/ingest_templates/` for use as precedent on future analyze runs against similar file shapes.

## Open Questions

- None at this time; detailed questions are in individual FEATURE files.
