# Architecture: Marina

| Field | Value |
|-------|-------|
| Version | 20260713 V2 |
| Description | Local-first Flask web application for registering projects, discovering capabilities, and exploring a shared project catalog, with one Marina library interface for local and AWS backends. |

Marina is a local web application first. It runs on the user's machine, reads and organizes Git projects,
and stores its working catalog locally. AWS is an optional second backend for selected catalog, health,
queue, and sharing data.

The architecture has four boundaries:

1. **Web server** — presents the UI and HTTP API.
2. **Application services** — implement registration, discovery, and exploration.
3. **Storage interfaces** — hide SQLite, filesystem, and AWS details.
4. **Marina library** — provides one stable client interface over local and AWS implementations.

## Initial Build

The initial build implements:

- Welcome and project registration
- Local repository scanning
- Project metadata and Git state discovery
- Capability discovery and storage
- Project Explorer

The initial build does not execute discovered operations, expose them to other users, run schedules, or
publish to AWS. Those features consume the same stored project and capability model later.

## Runtime Shape

```text
Browser
   │ HTML pages, HTMX fragments, JSON API
   ▼
Flask web server
   │ routes contain HTTP concerns only
   ▼
Application services
   ├── registration service
   ├── discovery service
   ├── project explorer service
   └── future operation/monitoring services
   │
   ▼
Marina library interfaces
   ├── Local backend  ── SQLite + local filesystem + Git
   └── AWS backend    ── signed Marina API ── API Gateway/Lambda ── AWS services
```

The browser never reads project files directly. Route handlers call application services. Application
services call the Marina library and discovery adapters. Only the discovery adapters read repository
files and execute read-only Git commands.

## Web Server

### Server Choice

- Python
- Flask application factory
- Jinja templates
- HTMX for partial page updates
- Bootstrap and Marina CSS for shared presentation
- SQLite for the local registry

The server listens on localhost by default. It does not require a public IP or public inbound connection.
Remote access is a later, explicitly secured capability.

### Application Factory

`create_app()` performs only application setup:

1. Load environment configuration.
2. Resolve the Marina data directory.
3. Create or migrate the local SQLite database.
4. Configure logging.
5. Construct the selected Marina backend.
6. Register route blueprints.
7. Register error handlers and health checks.

Application startup must not silently clone repositories, modify projects, or run project operations.
Discovery occurs on an explicit user action or an explicit post-clone registration flow.

### Route Boundaries

Routes are grouped by product area:

| Blueprint | Responsibility |
|-----------|----------------|
| `setup` | Welcome, configuration, repository sources, discovery candidates, registration |
| `projects` | Project Explorer, project identity, organization, capabilities, evidence |
| `api` | JSON endpoints used by the Marina library and external clients |
| `health` | Local process health endpoint for Marina itself |

Routes may return full HTML pages, HTMX fragments, or JSON. They must not contain discovery logic, SQL,
Git command construction, or AWS calls.

## Application Services

Application services own product behavior and are testable without Flask.

| Service | Responsibility |
|---------|----------------|
| `registration_service` | Candidate review, clone handoff, explicit registration, identity conflicts |
| `scanner_service` | Repository enumeration, Git evidence, scan lifecycle, reconciliation |
| `discovery_service` | Parse metadata, documentation, operation headers, and MCP declarations |
| `catalog_service` | Query current capability and warning projections for the Explorer |
| `project_service` | Project identity, organization fields, namespaces, and tags |
| `evidence_service` | Source locations, hashes, raw headers, discovery history, and warnings |
| `backend_service` | Select local or AWS backend and expose backend health |

Services return domain records and result objects. They do not return HTML.

## Discovery Adapters

Discovery is read-only and divided by source type:

| Adapter | Reads |
|---------|-------|
| `git_adapter` | Repository root, remotes, branches, commits, authors, status, upstream divergence |
| `metadata_adapter` | `METADATA.md` key/value fields and unknown fields |
| `documentation_adapter` | `AGENTS.md` / `CLAUDE.md` structured sections |
| `operation_adapter` | `bin/*` CommandCenter headers within the first 20 lines |
| `mcp_adapter` | `.mcp.json` and `mcp/*.service.yaml` |
| `source_adapter` | GitHub/source cache and remote provenance |

An adapter produces normalized records plus evidence and warnings. It must not write to the repository or
execute a discovered operation.

## Marina Library: One Interface, Two Backends

`marina-lib` is the common client library used by the web application, future local agents, conformed
projects, and AWS-facing code. Consumers use the library interface and do not import `boto3`, construct
AWS URLs, or duplicate backend selection logic.

### Public Library Areas

| Area | Responsibility |
|------|----------------|
| `marina.projects` | Register and read project identity and organization |
| `marina.discovery` | Start scans and read discovery results |
| `marina.catalog` | Read projects, capabilities, evidence, and warnings |
| `marina.report` | Write/read health and events; later phase |
| `marina.queue` | Submit durable work; later phase |
| `marina.share` | Store and read shared objects; later phase |

### Backend Contract

The public methods have the same meaning in both modes:

```text
Local mode
  marina.catalog.projects()
      → LocalBackend → SQLite projection

AWS mode
  marina.catalog.projects()
      → AwsBackend → signed Marina API → API Gateway/Lambda → DynamoDB projection
```

Backend selection is configuration, not application logic:

| Mode | Use |
|------|-----|
| `local` | Initial build; SQLite and local filesystem |
| `aws` | Private remote catalog and reporting |
| `dual` | Local writes with selected catalog/report publication to AWS |

The local backend remains authoritative for repository files and registration. AWS receives selected
projections, never direct access to the user's filesystem.

### Library Rules

- Keep the public library methods backend-neutral.
- Return domain records, not SQLite rows or AWS response shapes.
- Keep retries, signing, serialization, and backend errors inside the library.
- Make reporting best-effort where the feature contract says reporting must not break a local operation.
- Do not add a raw AWS escape hatch.
- Use explicit capability/version fields when a local and AWS projection may differ.

## Directory Layout

Marina's repository contains code, templates, migrations, tests, and documentation. Runtime state lives
under `data/` and is gitignored. Managed projects live outside Marina under `PROJECTS_DIR`.

```text
Marina/
├── app.py                         # Flask entry point and application factory
├── config.py                      # Environment-backed configuration
├── src/
│   └── marina_app/
│       ├── routes/                # HTTP and HTMX route blueprints
│       ├── services/              # Application services
│       ├── discovery/             # Git, metadata, docs, operation, MCP adapters
│       ├── storage/               # SQLite repositories and migrations
│       ├── domain/                # Domain records and result types
│       └── web/                   # template context and presentation helpers
├── templates/                     # Jinja page templates and fragments
│   ├── base.html
│   ├── setup/
│   └── projects/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── migrations/                    # Ordered SQLite schema migrations
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── bin/
│   ├── start.sh                   # Start the local web server
│   ├── test.sh                    # Lint, format, and test
│   ├── scan.sh                    # Optional CLI scan wrapper
│   └── ...                        # CommandCenter operations
├── data/                          # Gitignored runtime state
│   ├── marina.db                  # Local SQLite registry
│   ├── logs/                      # Application and operation logs
│   ├── runs/                      # Run metadata and captured output; later phase
│   ├── discovery/                 # Optional raw scan snapshots and exports
│   ├── cache/                     # GitHub and remote-source cache
│   ├── queues/                    # Local durable queue; later phase
│   ├── backups/                   # Database and catalog backups
│   └── uploads/                   # Local user uploads; later phase
├── infra/                         # Optional AWS Terraform
├── pyproject.toml                 # Python dependencies and tool configuration
├── uv.lock                        # Reproducible dependency lockfile
├── .env.example                   # Documented configuration template
├── .gitignore                     # Excludes secrets and runtime state
├── METADATA.md
├── AGENTS.md
└── README.md
```

### Storage Rules

- `data/` is runtime state and is never committed.
- `migrations/` is committed and ordered; do not recreate the database by deleting it.
- Discovery projections and evidence live in SQLite. Raw snapshots in `data/discovery/` are optional and
  may be rotated; they are not the source of truth.
- Marina does not copy whole repositories into its own data directory.
- Marina does not write into a managed repository during discovery or registration unless a separate,
  explicit metadata-edit action is requested.
- Logs, runs, queues, and uploads have separate directories and retention policies.

## AWS Boundary

AWS is a backend and publication plane, not the local application's primary database.

```text
Local web server
    ↓ marina-lib
AwsBackend
    ↓ SigV4
API Gateway
    ↓
Lambda handlers
    ↓
DynamoDB / SQS / S3
```

The AWS plane is private and outbound-oriented:

- IAM/SigV4 authorization only
- No anonymous API access
- No inbound listener on the user's local machine
- No secrets in Terraform, source code, or catalog records
- Organization and project access checked at the AWS boundary
- Thin Lambda handlers: validate, authorize, perform one storage operation, return a domain response

Terraform is divided into:

| Layer | Purpose |
|-------|---------|
| `infra/backend` | One-time remote state bootstrap |
| `infra/foundation` | Tables, buckets, queues, and IAM foundations |
| `infra/services` | Lambda functions, API routes, and integrations |
| `infra/modules` | Reusable Terraform modules |

AWS features are added only after the equivalent local domain contract exists.

## Build Rules

These rules guide the code generator and implementation. They are intentionally small.

### Rule 1 — Build from the domain boundary

Implement the domain record and application service before adding a screen or API route. A screen is a
view of a service result, not the owner of business logic.

### Rule 2 — Keep the local path complete

Every capability must work locally before it is given an AWS backend. Local mode is the development and
failure-tolerant default.

### Rule 3 — One source of truth per concern

- Repository files own project-declared metadata and capability declarations.
- Git owns repository state and provenance.
- SQLite owns Marina's local projection, organization, and discovery history.
- AWS owns only explicitly published projections and remote operational state.

### Rule 4 — Discovery is safe

Discovery may read files and run read-only Git commands. It must not execute project scripts, modify
repositories, clone over existing directories, or expose capabilities.

### Rule 5 — Preserve evidence

Every normalized record must identify its source path, locator, timestamp, validity, and content hash.
Warnings are stored, not discarded.

### Rule 6 — Use standard project structure

Python projects use `uv`, `pyproject.toml`, `uv.lock`, `ruff`, and `pytest`. Operations live in `bin/`
and use the CommandCenter header convention. Runtime state lives in gitignored `data/` directories.

### Rule 7 — Keep HTTP thin

Routes validate HTTP input, call an application service, and render a result. No SQL, Git commands,
filesystem traversal, subprocess execution, or AWS SDK calls belong in route handlers.

### Rule 8 — Test the boundaries

Tests cover discovery fixtures, registration conflicts, SQLite migrations, local backend behavior, API
responses, and the same service contract against a fake AWS backend. Tests must not require live AWS.

### Rule 9 — Make changes observable

Registration, discovery changes, warnings, backend changes, and future operations produce structured
events with project identity and timestamps.

### Rule 10 — Add infrastructure last

Do not add Terraform, Lambda, queues, or buckets until the local feature has a stable domain contract,
local storage behavior, and tests.

## Configuration

Configuration comes from environment variables or `.env` in local development. Secrets remain outside Git.

| Variable | Purpose |
|----------|---------|
| `PROJECTS_DIR` | Root directory containing managed repositories |
| `MARINA_MODE` | `local`, `aws`, or `dual` |
| `MARINA_DATA_DIR` | Runtime data directory; default `data/` |
| `MARINA_DB_PATH` | SQLite path; default `data/marina.db` |
| `MARINA_HOST` | Local bind host; default `127.0.0.1` |
| `MARINA_PORT` | Local web port |
| `MARINA_ORG` | AWS organization/catalog namespace |
| `MARINA_ENDPOINT` | Private Marina API endpoint for AWS mode |
| `AWS_PROFILE` | Local AWS credential profile when AWS mode is enabled |
| `AWS_REGION` | AWS region when AWS mode is enabled |

## Verification

The minimum initial-build verification is:

1. Start the Flask application with an empty data directory.
2. Configure `PROJECTS_DIR` through the Welcome screen.
3. Discover repositories without modifying them.
4. Register a repository with and without `METADATA.md`.
5. Verify Git remote, branch, author, working-tree, and commit data.
6. Verify operation headers, endpoints, links, MCP declarations, warnings, and evidence are stored.
7. Rediscover after changing a declaration and confirm drift is visible.
8. Browse the same records through the Project Explorer and JSON API.
9. Run the test suite using an isolated temporary SQLite database.

## Open Questions

- None.
