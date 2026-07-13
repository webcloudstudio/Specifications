# Feature: Capability Discovery and Storage

| Field | Value |
|-------|-------|
| Version | 20260713 V1 |
| Description | Reads project metadata and callable-surface artifacts, normalizes them into a local capability catalog, and records discovery evidence and drift. |
| Depends On | DATABASE.md |
| Provides | GET /api/service-catalog, GET /api/projects/{project}/capabilities, POST /api/projects/scan |

**Description:** Discovery is the source of the capability contract for the initial build. Marina does not
invent capability definitions from filenames alone. It parses the project artifacts that already document
the project and its callable surface, then stores both the normalized projection and the evidence needed to
explain it.

## Discovery Sources

### Project Identity: `METADATA.md`

Read recognized key/value fields including:

`name`, `display_name`, `short_description`, `status`, `type`, `stack`, `version`, `updated`, `git_repo`,
`namespace`, `tags`, `author`, `owner`, `port`, `health`, `desired_state`, and `show_on_homepage`.

The declared `author` and `owner` are project metadata. They are distinct from the current Git commit
author and are displayed as separate evidence in the Project Explorer.

Unknown keys are preserved in `metadata_extra` and shown as discovered metadata. Values are not inferred
when the source file provides a value.

### Project Documentation: `AGENTS.md` / `CLAUDE.md`

Read supported structured sections:

- `## Endpoints`: HTTP method, path, and description.
- `## Links`: label and URL.
- `## Capabilities`: named project capabilities and descriptions, when present.
- `## Data`: declared data resources, when present.
- `## Shared Resources`: declared shared resources, when present.

`AGENTS.md` is preferred when both files exist; `CLAUDE.md` is a compatibility fallback. The source file
and section are stored with each discovered record.

### Callable Operations: `bin/*`

Scan eligible `.sh`, `.py`, and other configured executable files. A file is a callable operation only when
the literal marker `# CommandCenter Operation` appears within its first 20 lines.

Canonical header fields:

| Header | Required | Stored value |
|--------|----------|--------------|
| `# CommandCenter Operation` | Yes | Discovery marker |
| `# Name:` | Yes | Human-readable operation name |
| `# Category:` | Yes | `Operations`, `Workflow`, or `Global` |
| `# Description:` | Required for scheduled/platform invocation | One-line description |
| `# Args:` | Required when positional arguments exist | Ordered positional argument labels |
| `# Port:` | Required when the operation binds or uses a port | Integer port |
| `# Type:` | Optional | `daemon` or `batch`; default `batch` |
| `# Schedule:` | Optional | Schedule metadata when declared |

The scanner records the raw header and the first-line position. Missing required fields produce a catalog
warning and do not prevent the project from being registered. A malformed operation remains visible as an
invalid discovery record and is not runnable through Marina.

Category behavior follows the GAME convention:

- `Operations`: lifecycle and standard project operations.
- `Workflow`: project-specific or work-oriented operations.
- `Global`: operations that intentionally affect more than the current project.

Category matching is case-insensitive during parsing and normalized to the canonical values above.

### MCP Declarations

Read `.mcp.json` and `mcp/*.service.yaml` when present. Store service name, tool name, description, input
schema reference, and source path. MCP discovery is catalog-only in the initial build; invocation is not
required for registration or the first Project Explorer.

## Discovery Sequence

1. Create a discovery run with timestamp and scanner version.
2. Read repository identity and git state.
3. Parse project metadata and documentation artifacts.
4. Scan callable operation headers and MCP declarations.
5. Normalize records using stable project and capability identifiers.
6. Upsert the current projection and mark missing previous records as no longer discovered.
7. Store warnings, source locations, content hashes, and scan summary.
8. Update the Project Explorer and expose the changed/discovered counts.

## Stable Identity

- Project identity: normalized canonical local path; remote URL is retained as provenance.
- Operation identity: project identity + relative source path.
- Endpoint identity: project identity + HTTP method + path.
- MCP tool identity: project identity + service name + tool name.
- Metadata field identity: project identity + source path + key.

Renaming a display name does not create a new project. Moving a repository creates a new candidate until
the user confirms the identity match.

## Drift and Evidence

Each discovery record stores source path, source section/header, content hash, first-seen time, last-seen
time, and current validity. A later scan can therefore show:

- Added capability
- Removed capability
- Changed description or category
- Changed endpoint or operation arguments
- Changed project metadata
- Invalid or incomplete declaration

## Reads

- Registered project paths and repository files.
- Git commands and GitHub repository cache.

## Writes

- Discovery projection tables and capability records.
- Discovery warnings and scan history.
- `project_events` only for material discovery changes or invalid declarations.

## Guardrails

- Discovery never executes a discovered operation.
- Discovery never treats a filename alone as a callable capability.
- Raw source evidence is retained for every normalized record.
- Capability exposure and invocation are separate future decisions; initial build is discovery and storage.

## Open Questions

- None.
