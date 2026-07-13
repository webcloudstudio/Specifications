# Screen: Projects — Configuration

| Field | Value |
|-------|-------|
| Version | 20260713 V2 |
| Route | `GET /projects/configuration` |
| Parent | PROJECTS |
| Main Menu | PROJECTS |
| Sub Menu | Configuration |
| Tab Order | 1: Dashboard · 2: Workflow · 3: Configuration · 4: Validation · 5: Maintenance |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Define project identity, organization, standards, and exposure defaults. |
| Description | Shared configuration for project metadata, namespaces, tags, workflow defaults, standards, and capability exposure. |
| Depends On | UI-GENERAL.md, FEATURE-PROJECT-ORGANIZATION.md, FEATURE-SERVICE-CATALOG.md |
| Provides | GET /projects/configuration |

## Layout

Two sections: organization defaults and project configuration. Project configuration can be filtered by
namespace and edited in a table; the selected project's full configuration is available in a drawer.

## Organization Defaults

| Setting | Behaviour |
|---------|-----------|
| Namespace list | Create, rename, archive, and choose the default namespace |
| Tag list | Create, rename, merge, archive, and set tag colour/description |
| Default workflow | Define initial state and allowed transitions |
| Standard profile | Select the checks required for a project to be Conformed |
| Exposure policy | Default capabilities to private, organization-visible, or disabled |

## Project Fields

| Field | Source | Input |
|-------|--------|-------|
| Display Name | `METADATA.md` / registry | Text |
| Short Description | `METADATA.md` / registry | Text |
| Lifecycle Status | `METADATA.md` / registry | IDEA / PROTOTYPE / ACTIVE / PRODUCTION / ARCHIVED |
| Namespace | organization record | Select |
| Tags | organization records | Multi-select |
| Stack | `METADATA.md` / registry | Text |
| Git Repository | git remote / `METADATA.md` | Text, read-only unless explicitly overridden |
| Standard Profile | project organization | Select |
| Exposure | capability catalog | Per-capability visibility control |

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Save field | Blur or Enter | Validate, persist registry, and update `METADATA.md` when the field is repository-owned |
| Assign tags | Tag picker change | Persist project-tag links and refresh dashboard filters |
| Configure workflow | Button click | Edit project states and transitions; affect only that project |
| Configure exposure | Button click | Open capability exposure editor |
| Rescan | Button click | Re-read repository-owned data while preserving user-managed organization data |

## Guardrails

- Unknown metadata keys are preserved.
- A namespace or tag cannot be deleted while assigned; archive or reassign first.
- A workflow transition cannot be removed while tickets use it.
- A capability is never exposed merely because it was discovered; exposure is explicit and disabled by default.
- Failed repository writes leave the registry unchanged and show the conflict.

## Open Questions

- None.
