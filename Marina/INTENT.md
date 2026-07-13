# Intent

Marina is a trust and interoperability platform for software projects.

You dock a project in Marina. Marina helps you organize it, understand what it provides, and make it
work with your other projects.

Drydock is the system used to build Marina. Marina is the system that manages the projects after they
have been built.

## The Basic Idea

Every project contains useful capabilities. A project may provide:

- Services
- Data
- Shared resources
- Scripts and operations
- HTTP endpoints
- MCP tools

Marina discovers these capabilities from the project's files and records them in one catalog. The catalog
shows what each project provides, where the capability is defined, and whether the declaration is complete
and current.

Discovery does not automatically make a capability available to other people or projects. Sharing is an
explicit decision made after the capability has been reviewed.

## What Marina Does

### Organizes Projects

Marina gives every managed project a clear home. You can organize projects by:

- Namespace
- Tags
- Lifecycle status
- Owner
- Source repository
- Project type
- Technology stack

You can find projects by what they are, where they came from, or what they provide.

### Conforms Projects

Marina uses the Process Based Methodology and proven Technology Rules to bring projects into a common
form.

A conformed project has consistent identity, documentation, callable operations, health information, and
security expectations. The exact rules depend on the project's technology stack, but every project follows
the same basic approach.

Conformance makes projects easier to understand, operate, maintain, and connect to one another.

### Creates a Capability Catalog

Marina builds one catalog for all managed projects. The catalog answers:

- What does this project provide?
- Where is the capability defined?
- How is it used?
- What data or resources does it touch?
- Is the declaration valid and current?
- Who owns it?
- Is it local, private, or shared?

The catalog is the foundation for future interoperability. Projects can share capabilities without each
project needing a custom integration.

### Keeps Documentation Consistent

Marina helps projects describe themselves in a consistent way. This includes project identity,
capabilities, services, data, shared resources, endpoints, links, operations, and health checks.

Consistent documentation makes a collection of different repositories feel like one managed platform.

### Provides an Enterprise Command Center

Marina gives the owner one place to see and manage project activity:

- Logging
- Monitoring
- Alerts
- Scheduling
- Pipelines
- Project health
- Operation history

The command center connects an event to the project, capability, run, log, and action that explain it.

### Provides AWS Integration

Marina can use low-cost AWS services to make selected project information available when the local machine
is offline.

AWS integration is behind one Marina library. Projects use Marina's interface instead of writing their own
AWS integration code. This keeps cloud access consistent and allows the implementation to change without
changing every project.

## Trust and Security

Marina is built around controlled access.

- A project is not shared merely because Marina discovered it.
- A capability is not executable merely because it appears in the catalog.
- Operations must be explicitly defined and reviewed.
- Project paths and commands are controlled by Marina.
- Access follows project ownership and repository permissions.
- Secrets are not stored in project documentation or shared catalog data.
- Local machines do not need public inbound access.

The owner decides which projects are managed and which capabilities are shared.

## Initial Product

The first build focuses on three things:

1. Welcome and registration — discover local or downloaded Git projects and dock selected projects in Marina.
2. Capability discovery and storage — read project metadata, documentation, operation headers, endpoints,
   data, shared resources, and MCP declarations into a searchable catalog.
3. Project Explorer — browse project identity, Git status, provenance, organization, capabilities, and
   discovery warnings.

Later builds will add conformance enforcement, capability invocation, exposure controls, command-center
operations, pipelines, and AWS publication.

## Audience

Marina is for developers, technical teams, and organizations that manage many projects and want them to
work together without losing control of their code, data, or infrastructure.

## Success

Marina succeeds when a user can:

1. Dock a repository without changing it unexpectedly.
2. Understand what the project is and where it came from.
3. See what the project provides.
4. Find the project and its capabilities alongside all other managed projects.
5. Apply common standards when the project is ready.
6. Share selected capabilities with confidence.

## Open Questions

- None.
