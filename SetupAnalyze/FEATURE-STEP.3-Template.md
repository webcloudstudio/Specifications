# FEATURE: Ingest Template Save

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | After a successful conversion, fingerprint the source format and save it to RulesEngine/ingest_templates/ as a reusable precedent. |
| Phase       | 3 |

## Trigger

Called by `analyze_spec.sh` after STEP.2 produces at least one output file without error.

## Template Fingerprint

The fingerprint captures heuristics that identify this class of source document:
- List of H1/H2 section headings found in the source file(s).
- Keywords present: `INTENT`, `PROJECT PLAN`, `PHASE`, `DATABASE`, etc.
- Number of source files ingested.
- File size range.

The fingerprint is saved to `RulesEngine/ingest_templates/<slug>.md` where `<slug>` is derived from the source structure (e.g. `intent-projectplan-format.md`).

## Template Content Format

```markdown
# Ingest Template: <slug>

## Detected Heuristics
- Headings: ## INTENT, ## PROJECT PLAN, ## Target Universe, ...
- Keywords: INTENT, PROJECT PLAN, PHASE, schema
- Source file count: 1
- Approximate size: 10-20KB

## Mapping Decisions
- ## INTENT → INTENT.md (Goals + Constraints sections)
- ## PROJECT PLAN → FUNCTIONALITY.md + FEATURE-STEP.N files
- Database schema block → DATABASE.md
- Implementation stack table → ARCHITECTURE.md

## Notes
Written by analyze_spec.sh on 2026-05-19 from Edgar/Initial_Spec.md.imported
```

## Success Criteria

- Template file is written to `RulesEngine/ingest_templates/` after every successful analyze run.
- On subsequent analyze runs, the script prints: "Using precedent template: <slug>.md" if a matching template is found.
- Templates are committed to git (they are part of the RulesEngine governance artifacts).

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Template save fails (permissions, disk) | Log warning; do not fail the overall analyze run. |
| No matching template found on next run | Proceed without precedent (normal first-run behavior). |

## Open Questions

- Should template matching use exact heading comparison or fuzzy heuristics? Exact is simpler and less error-prone for now.
- Should the user be prompted to name/confirm the template, or is auto-naming acceptable for novice use?
