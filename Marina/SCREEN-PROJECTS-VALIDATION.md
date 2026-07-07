# Screen: Projects — Validation

| Field | Value |
|-------|-------|
| Version | 20260707 V1 |
| Route | `GET /projects/validation` |
| Parent | — |
| Main Menu | PROJECTS |
| Sub Menu | Validation |
| Tab Order | 1: Dashboard · 2: Configuration · 3: Validation · 4: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Validate project conformance and report results into Marina. |
| Description | Project validation dashboard for Prototyper conformance checks and Marina publish readiness. |
| Depends On | UI-GENERAL.md, FEATURE-PROJECT-OPS.md, FEATURE-SCANNER.md |
| Provides | GET /projects/validation |

## Header KPIs

Left column uses three `mn-hdr-count` blocks:

| Count | Source |
|-------|--------|
| Passing | Latest validation state OK |
| Warning | Latest validation state WARN |
| Failing | Latest validation state ERROR |

## Layout

Full-width table. Action bar: `Validate Visible`, `Show failing only`, project search.

## Columns

| Column | Source | Interaction |
|--------|--------|-------------|
| Project | `projects.display_name` | Link to detail |
| Conformance | latest validation result | Badge |
| Checks | validation result summary | Expand row |
| Last Run | validation event timestamp | Link to process/event detail |
| Action | — | `Validate` button |

## Validation Action

| Action | Trigger | Result |
|--------|---------|--------|
| Validate one | Button click | Queue `project-ops.validate`, refresh row when result is reported |
| Validate visible | Button click | Queue one validation job per visible project |
| Expand checks | Row click | Show check list and last output tail |

## Result Groups

| Group | Checks |
|-------|--------|
| Metadata | Required `METADATA.md` fields, status value, git repo |
| Repository | Git repo present, upstream remote, clean readable path |
| Project Standard | AGENTS.md, bin helpers, docs, tests, health metadata |
| Marina Publish | Catalog payload can be built and signed |

## Open Questions
- None.
