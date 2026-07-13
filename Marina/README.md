# Marina

A local-first control plane for agentic developers, with a private 24×7 AWS broadcast surface.

## Intent

Marina organizes a developer's local and downloaded git projects, applies a small set of standards,
catalogs their capabilities, and gives the owner observability and command-and-control over them.
Operations that act on local processes, disk, and logs stay on the developer's machine. The read-mostly
state worth sharing — the **capability catalog, project metadata, and last-known health** — can be
published to pay-per-call AWS services so it is reachable 24×7 by a private circle of trust, with **no
public inbound** anywhere.

Marina is the successor to the GAME prototype, built from the start around the two-plane hybrid analysed
in the prototyper project's Marina architecture notes.

## Product Model

Marina turns repositories into organized, observable project capabilities:

```text
Repository
    ↓
Project registration and identity
    ↓
Capability discovery and storage
    ↓
Project Explorer
    ↓
Future invocation, exposure, monitoring, and sharing
```

The central rule is that discovery is not exposure. Marina can catalog an operation, endpoint, service,
data resource, shared resource, or MCP tool without making it executable or visible to other users.

## The Two Planes

- **Local control plane** — welcome and registration, repository scanner, capability discovery, local
  registry, and Project Explorer. Later consumers include the process engine, log ingestor, scheduler,
  and local operations. Outbound-only; no listener on the public internet.
- **Cloud broadcast plane (this specification's focus)** — DynamoDB (catalog/state), API Gateway + Lambda
  (private IAM-authorised read/ingest), SQS (durable queue), S3 (blobs + company share). Accessed only
  through the `marina` client library, never raw boto3.

## Scope

This initial specification covers welcome/registration, repository identity, capability discovery and
storage, and the local Project Explorer. Project organization, conformance, invocation, monitoring, the
AWS broadcast plane, durable ingest, and company share consume this foundation in later increments.
Dockerization, Fargate, AgentCore, and Prototyper remain outside Marina's core scope.

## Initial Build

The initial build contains three end-to-end slices.

### Welcome and Registration

The user configures or confirms `PROJECTS_DIR`, discovers existing local Git repositories, optionally
configures remote sources, clones repositories, reviews their identity and provenance, and explicitly
registers selected projects.

Registration states are:

```text
AVAILABLE → CLONING → DISCOVERED → REGISTRATION_REVIEW → MANAGED
```

Discovery is repeatable and non-destructive. Registration never deletes files, overwrites a non-empty
clone destination, or runs project operations. A repository without `METADATA.md` may still be registered
with an `UNKNOWN` identity and completed later.

### Capability Discovery and Storage

Marina uses existing project artifacts as the capability contract.

Project identity is read from `METADATA.md`, including display name, description, status, type, stack,
version, namespace, tags, declared author, declared owner, port, health, desired state, and links to
project-owned metadata. Unknown fields are preserved.

Project documentation is read from `AGENTS.md`, with `CLAUDE.md` as a compatibility fallback. Marina
recognizes structured sections for endpoints, links, capabilities, data, and shared resources.

Callable operations are discovered from eligible files under `bin/`. A file is cataloged only when the
literal marker `# CommandCenter Operation` appears within its first 20 lines. Marina parses:

| Header | Purpose |
|--------|---------|
| `# Name:` | Human-readable operation name |
| `# Category:` | `Operations`, `Workflow`, or `Global` |
| `# Description:` | Operation summary |
| `# Args:` | Positional argument labels |
| `# Port:` | Port used by the operation |
| `# Type:` | `daemon` or `batch` |
| `# Schedule:` | Optional schedule metadata |

Marina also catalogs `.mcp.json` and `mcp/*.service.yaml` declarations. MCP tools are catalog-only in
the initial build.

Every normalized capability record retains its evidence:

- Source path
- Header, section, JSON, or YAML locator
- Content hash
- First-seen and last-seen timestamps
- Validity state
- Discovery run identifier
- Warnings and remediation context

This allows Marina to show added, removed, changed, stale, and invalid capabilities instead of presenting
an unexplained list.

### Project Explorer

The Project Explorer provides two views:

- **Project view:** project identity, registration state, remote provenance, Git status, branch, author,
  lifecycle, namespace, tags, and discovery history.
- **Capability view:** services, data, shared resources, endpoints, links, operations, and MCP tools
  grouped by project, capability kind, or category.

The project record includes:

- Canonical local path
- Originating and current Git remote
- Remote host, owner, and repository name
- Current and default branch
- HEAD commit, subject, author, and timestamps
- Working-tree state
- Staged, unstaged, and untracked file counts
- Ahead/behind counts
- Latest known remote push time
- Declared project author and owner
- Discovery warnings and last scan time

## What the Initial Build Does Not Do

The initial build discovers and explains capabilities. It does not yet:

- Execute discovered operations
- Expose capabilities to other users or projects
- Publish capabilities to AWS
- Schedule operations
- Enforce conformance profiles
- Provide remote capability invocation
- Provide enterprise alerting or command-and-control

Those features consume the registration and discovery foundation. They must use the stored capability
projection and evidence rather than inventing a second project or capability model.

## Specification Map

| Document | Answers |
|----------|---------|
| `INTENT.md` | Goals, audience, security posture |
| `ARCHITECTURE.md` | Two planes, the `marina` library, Terraform layout, directory structure |
| `DATABASE.md` | DynamoDB single-table hierarchical schema and access patterns |
| `FUNCTIONALITY.md` | Index of features by phase |
| `FEATURE-*.md` | Per-feature: trigger, sequence, reads/writes, and a callable test |
| `AGENTS.md` | Endpoints and capability catalog |
| `IDEAS.md` | Deferred phases and spikes |

## Building From This Specification

```bash
bash ../prototyper/bin/validate.sh Marina
python3 ../prototyper/bin/build_spec_relationships.py Marina
bash ../prototyper/bin/oneshot.sh Marina        # or per-feature minimal builds in dependency order
```
