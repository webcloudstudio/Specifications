# Screen: Projects — Validation

| Field | Value |
|-------|-------|
| Version | 20260713 V2 |
| Route | `GET /projects/validation` |
| Parent | PROJECTS |
| Main Menu | PROJECTS |
| Sub Menu | Validation |
| Tab Order | 1: Dashboard · 2: Workflow · 3: Configuration · 4: Validation · 5: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Apply the selected Marina standard and prepare projects for safe exposure. |
| Description | Standards and conformance dashboard for all managed projects; it is independent of any particular build tool. |
| Depends On | UI-GENERAL.md, FEATURE-PROJECT-ORGANIZATION.md, FEATURE-SERVICE-CATALOG.md |
| Provides | GET /projects/validation |

## Header KPIs

Passing, Warning, Failing, and Not Evaluated counts for the active filters.

## Layout

Project table with standard-profile filter, result filter, project/namespace/tag filters, and validation
actions. Expand a row to show checks and remediation guidance.

## Check Groups

| Group | Examples |
|-------|----------|
| Identity | Required project metadata, repository identity, lifecycle state |
| Repository | Git repository, upstream, readable path, working-tree policy |
| Documentation | Required project documentation and callable-surface catalog |
| Security | Secret/configuration hygiene, allow-listed operations, exposure policy |
| Operations | Health metadata, logs, schedules, and run configuration |
| Publication | Capability payload is complete and only approved capabilities are exposed |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Validate one | Button click | Run selected standard profile and update the row |
| Validate visible | Button click | Queue one controlled validation run per visible project |
| Review result | Row expand | Show checks, evidence, output tail, and remediation |
| Accept exception | Exception action | Record owner, reason, expiry, and affected check |
| Recheck | Button click | Run the failed checks again |

## Guardrails

- A project is Conformed only when all required checks pass or have active approved exceptions.
- Validation is read-only by default; remediation is a separate explicit operation.
- The implementation may use any configured standards adapter. Marina does not depend on Prototyper.

## Open Questions

- None.
