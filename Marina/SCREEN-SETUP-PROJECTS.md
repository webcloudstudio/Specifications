# Screen: Setup — Projects

| Field | Value |
|-------|-------|
| Version | 20260713 V2 |
| Header Background | `mn-hdr-bg--git` |
| Header Help Text | Review repositories discovered on disk before adding them to Marina. |
| Route | `GET /setup/projects` |
| Parent | SETUP |
| Main Menu | SETUP |
| Sub Menu | Projects |
| Tab Order | 1: Summary · 2: AWS · 3: Terraform · 4: GitHub · 5: Git Scan · 6: Repositories · 7: Projects · 8: Settings |
| Description | Registration queue for local repository candidates. Ongoing project organization belongs to PROJECTS. |
| Depends On | UI-GENERAL.md, FEATURE-PROJECT-REGISTRATION.md, FEATURE-SCANNER.md |
| Provides | GET /setup/projects |

## Purpose

This screen is the handoff between discovery and management. It shows repositories found beneath
`PROJECTS_DIR` that are not yet registered, plus identity conflicts that require review. Managed projects
are linked to PROJECTS and are not duplicated here.

## Header KPIs

Candidates, Managed, and Warnings. Counts are independent of the current table filter.

## Unconfigured State

If `PROJECTS_DIR` is absent or unreadable, show a clear message and link to the Summary action. Do not show
an empty project state that could be mistaken for a successful scan.

## Filters

Search repository name, remote, owner, branch, author, or status. Filter by source type, remote host,
registration state, and warning state.

## Candidate Table

| Column | Source | Content |
|--------|--------|---------|
| Repository | git directory | Directory and display name |
| Remote | git | Normalized origin URL, host, owner, repository |
| Branch | git | Current branch and default branch |
| Author | git | HEAD author name and timestamp |
| State | scanner/registry | Discovered, managed, conflict, or local-only |
| Warnings | discovery | Count and highest severity |
| Action | registration | Review, Register, or Open Project |

## Registration Review

Selecting Review opens a panel showing:

- Repository path and source type.
- Originating and current remote.
- Current branch, default branch, HEAD SHA, subject, author, and working-tree state.
- Parsed `METADATA.md` fields and unknown fields.
- Detected links, endpoints, services, data, shared resources, operations, and MCP tools.
- Discovery warnings and source evidence.
- Namespace, tags, lifecycle status, and managed-state controls.

The panel distinguishes repository-owned evidence from user-managed organization fields. Registration is
not complete until the user confirms the project identity and managed state.

## Interactions

| Action | Trigger | Result |
|--------|---------|--------|
| Discover | Button click | POST `/api/projects/scan`; refresh candidates and discovery counts |
| Review | Candidate action | Open registration review panel |
| Register | Review confirmation | POST `/api/projects/{id}/register`; create managed projection |
| Dismiss | Candidate action | Hide candidate until the next material repository change or explicit restore |
| Open repository | Path/remote action | Open local directory or remote URL |
| Open Project Explorer | Managed row | GET `/projects/{id}` |

## API

| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/setup/projects` | — | Full page |
| POST | `/api/projects/scan` | — | Scan summary and candidate table |
| GET | `/api/projects/{id}/registration-preview` | — | Registration evidence JSON/HTML |
| POST | `/api/projects/{id}/register` | `namespace`, `tags[]`, `status` | Managed project row |
| POST | `/api/projects/{id}/dismiss` | — | Candidate row |

## Guardrails

- Discovery is read-only.
- Registration never deletes files or runs project operations.
- A candidate with a conflicting normalized remote requires explicit resolution.
- A local-only repository may be registered, but is visibly marked `LOCAL_ONLY`.

## Open Questions

- None.
