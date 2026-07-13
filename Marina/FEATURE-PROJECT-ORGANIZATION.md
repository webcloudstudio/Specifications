# Feature: Project Organization

| Field | Value |
|-------|-------|
| Version | 20260713 V1 |
| Description | Maintains the user's project registry: namespaces, tags, lifecycle status, metadata, and configurable project workflow. |
| Depends On | FEATURE-SCANNER.md, FEATURE-SERVICE-CATALOG.md, DATABASE.md |
| Provides | GET /api/projects, PATCH /api/projects/{project}/organization, GET /api/projects/{project}/workflow |

**Description:** Marina owns the local organization layer for repositories that the user creates,
clones, downloads, or discovers. A project remains a filesystem/git repository; Marina stores the
organization projection and writes approved metadata changes back to the repository.

## Trigger

- Repository import or local scan.
- Project Dashboard filter, edit, or tag action.
- Project Detail organization edit.
- Workflow Board ticket creation or transition.

## Sequence

1. Identify the repository by canonical local path and git remote.
2. Register or refresh project identity from `METADATA.md` and repository state.
3. Apply user-managed namespace, tags, lifecycle status, and workflow configuration.
4. Preserve unknown metadata keys and report file-write conflicts without losing the local projection.
5. Emit an organization event and make the project available to the service catalog and monitoring views.

## Organization Rules

- A project has one active namespace and zero or more tags.
- Namespaces are user-defined grouping values; tags are reusable cross-namespace labels.
- Filters can combine one namespace with multiple tags and a lifecycle status.
- A project may be archived without being removed from the registry.
- Removing a project from Marina unregisters the local projection only; it does not delete the repository.
- Workflow configuration is project-scoped. A global default supplies initial states and transitions; a
  project may override it.

## Reads

- Repository path, git remote, branch, and working-tree state.
- `METADATA.md` and `AGENTS.md`.
- Project organization, tags, workflow configuration, and ticket records.

## Writes

- `projects`, `project_tags`, `tags`, `workflow_configs`, and `workflow_tickets`.
- Approved metadata fields in the project's `METADATA.md`.
- Organization events.

## Open Questions

- None.
