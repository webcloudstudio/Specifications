# Feature: Project Registration

| Field | Value |
|-------|-------|
| Version | 20260713 V1 |
| Description | Welcomes the user, discovers repositories, captures project identity and provenance, and registers selected repositories in Marina. |
| Depends On | DATABASE.md, FEATURE-SCANNER.md, FEATURE-PROJECT-ORGANIZATION.md |
| Provides | GET /api/setup/status, POST /api/projects/{project}/register, POST /api/repositories/download |

**Description:** Registration is the boundary between a repository existing on disk and Marina managing
it. Marina never deletes or silently rewrites a repository during registration. It creates a local
projection from repository evidence, then lets the user assign organization fields and confirm ownership.

## Trigger

- First application visit.
- Welcome → Configure Projects Directory.
- Welcome → Discover Local Projects.
- Setup → Repositories → Clone.
- Setup → Projects → Add to Projects.
- Manual rediscovery.

## Registration States

`AVAILABLE` → `CLONING` → `DISCOVERED` → `REGISTRATION_REVIEW` → `MANAGED`.

Discovery is repeatable and non-destructive. Registration is explicit. A repository with no `METADATA.md`
may be registered with `UNKNOWN` identity and completed later from Project Detail.

## Sequence

1. Confirm `PROJECTS_DIR` is configured and resolve the target path beneath it.
2. Discover local repositories and available remote repositories.
3. For a clone, reject an existing non-empty destination and clone using the selected authenticated method.
4. Inspect repository evidence and produce a registration preview.
5. Show identity, originating remote, branch, author, status, detected capabilities, and metadata warnings.
6. Let the user select namespace, tags, lifecycle status, and whether the repository is managed.
7. Persist the local project projection and discovery snapshot.
8. Refresh the Project Explorer and capability catalog.

## Registration Preview

The preview must show the evidence used to populate each field, including the source file or git command.
Conflicts are visible and require a user choice. Marina does not overwrite repository-owned metadata merely
because a GitHub cache or directory name differs.

## Reads

- `PROJECTS_DIR` and repository filesystem.
- `METADATA.md`, `AGENTS.md`, `CLAUDE.md`, `bin/`, MCP declarations.
- Git remote, branch, commit, status, and author metadata.
- `github_repos` cache and configured GitHub sources.

## Writes

- `projects`, `project_sources`, `project_discovery_runs`, and discovery child records.
- Initial namespace and tag assignments after user confirmation.
- Clone destination for an explicit clone action only.
- `project_events` registration event.

## Guardrails

- A clone target must remain beneath `PROJECTS_DIR`.
- Existing non-empty directories are never overwritten.
- Discovery is read-only.
- Registration is idempotent by canonical local path and normalized git remote.
- Unregistered repositories remain visible as discovered candidates until dismissed or registered.

## Open Questions

- None.
