# FEATURES — Platform Capabilities

What the orchestration platform must do. Each feature has a name, short description, status, and completeness score. Features are grouped by domain and listed in implementation priority within each group.

---

## Core Platform

### Feature 1: Control Panel
**Dashboard for all projects and actions.**
Shows every project with status, workflow state, operations, and links. All day-to-day actions happen here. Filter by tag, state, or type. Running process count in nav bar.
**Status:** Built | **Complete:** 85%

### Feature 2: Project Discovery
**Auto-registration via filesystem scan.**
Scans the filesystem for projects, reads METADATA.md and bin/ headers, registers capabilities. No manual setup — add the files, the platform finds them.
**Status:** Built | **Complete:** 75%

### Feature 3: Project Scaffolding
**Generate new projects pre-wired to all standards.**
User picks a template (web service, CLI tool, data pipeline). Gets a project with correct METADATA.md, CLAUDE.md, bin/ scripts with headers, .env.example, and a passing compliance score from day one.
**Status:** Not built | **Complete:** 0%

---

## Operations & Process Management

### Feature 4: Operations Engine
**Run bin/ scripts on demand from the dashboard.**
One-click script execution. Captures stdout/stderr. Tracks IDLE → STARTING → RUNNING → DONE/ERROR/STOPPED state machine. Run history per project.
**Status:** Built | **Complete:** 90%

### Feature 5: Process Monitor
**Live log viewer and process control.**
Shows everything the platform has run, is running, or has completed. Live log output with auto-scroll. Stop button for running processes.
**Status:** Built | **Complete:** 85%

### Feature 6: Scheduling & Cron
**Time-based execution of registered operations.**
Declare schedules in METADATA.md or bin/ headers (`# Schedule: daily 02:00`). Platform runs the operation at the declared time. Supports daily, weekly, cron expressions. Shows next-run time in dashboard. Missed-run detection and catch-up policy.
**Status:** Not built | **Complete:** 0%

### Feature 7: Job Pipelines
**Multi-step workflows with dependency ordering.**
Define a pipeline as an ordered list of operations. Steps run sequentially or in parallel (fan-out/fan-in). A failed step halts the pipeline. Retry policy per step. Pipeline status visible in dashboard. Inspired by Airflow DAGs and CI/CD pipelines but simpler — a YAML file, not code.
**Status:** Not built | **Complete:** 0%

---

## Observability

### Feature 8: Monitoring & Health Checks
**Poll services for health, alert on failure.**
Health polling via declared Port and health endpoint. Supports liveness checks (is it responding?) and readiness checks (is it ready for traffic?). UP/DOWN/UNKNOWN/SNOOZED states. In-UI alerts. Uptime history. Incident log.
**Status:** Not built | **Complete:** 0%

### Feature 9: Usage Analytics
**AI token usage and cost tracking.**
Reads AI session log files. Shows tokens consumed and cost by project and over time. Daily/weekly/monthly summaries. Nav bar cost indicator. User-editable rates table.
**Status:** Built | **Complete:** 80%

### Feature 10: Event Log
**Centralized timeline of all platform events.**
Every state transition, operation run, health change, and deployment is an event. Filterable by project, event type, and time range. JSON export for external tools. Retained for 90 days by default.
**Status:** Not built | **Complete:** 0%

---

## Governance & Compliance

### Feature 11: Compliance Verification
**Scan all projects against CLAUDE_RULES standards.**
Per-project pass/fail for every applicable rule. Maturity-aware: IDEA projects checked for basics, PRODUCTION projects checked for everything. Aggregate summary table. JSON output for CI. Implemented as `verify.py`.
**Status:** Built | **Complete:** 70%

### Feature 12: Workflow States
**Structured lifecycle for feature work.**
States: IDEA → PROPOSED → READY → IN DEVELOPMENT → TESTING → DONE. Kanban view across all projects. AI transaction log (what was decided, what was built, why). Rework paths back to READY or PROPOSED.
**Status:** Not built | **Complete:** 5%

### Feature 13: Environment Management
**Track .env files, detect drift, prevent leaks.**
Per-project .env.example detection. Diff between .env.example and actual .env (variables present/missing — never values). Secrets scanner warns if .env is committed to git. Comparison across deployments.
**Status:** Not built | **Complete:** 0%

---

## Publishing & Documentation

### Feature 14: Portfolio Publishing
**One-click static portfolio from project metadata.**
Card grid from METADATA.md fields. Site-wide branding config. Local preview server. One-click push to GitHub Pages. Documentation links per project.
**Status:** Built | **Complete:** 75%

### Feature 15: Documentation Generation
**Generate browsable docs from specs and code.**
Per-project `bin/build_documentation.sh` operation. Generated HTML embeds all spec markdown. Published automatically with portfolio. Documentation link on portfolio card.
**Status:** Partial | **Complete:** 40%

---

## Configuration & Infrastructure

### Feature 16: Configuration Management
**Manage AI assistant config profiles.**
Profile library (YAML files). Deploy with diff preview. Deployment history in git. One-click rollback to any prior deployment.
**Status:** Built | **Complete:** 85%

### Feature 17: Git Integration
**Surface git state in the dashboard. Read-only.**
Branch, uncommitted changes, unpushed commits, last commit message. Governance checklist: initialized, remote configured, not persistently dirty.
**Status:** Built | **Complete:** 80%

### Feature 18: Tag Management
**Lightweight visual grouping for projects.**
Tags from METADATA.md. User-assigned colors in platform config. Inline tag assignment from dashboard. Filter by one or more tags.
**Status:** Built | **Complete:** 80%

### Feature 19: Secrets Management
**Secure storage and injection of sensitive values.**
Encrypted secrets store (separate from .env). Secrets injected into bin/ scripts at runtime via environment variables. Rotation tracking — flag secrets older than N days. Audit log of access. Never written to disk in plaintext outside the store.
**Status:** Not built | **Complete:** 0%

### Feature 20: Resource Limits
**Prevent runaway processes from consuming the host.**
Per-operation memory and CPU time limits declared in bin/ headers (`# MaxMemory: 512M`, `# Timeout: 300`). Platform enforces via ulimit or cgroups. Kills processes that exceed limits. Logs the event.
**Status:** Not built | **Complete:** 0%

---

## Orchestration (Kubernetes-Inspired)

### Feature 21: Desired State Reconciliation
**Declare what should be running; platform makes it so.**
Each project declares its desired state in METADATA.md (`desired_state: running`). A reconciliation loop compares desired vs actual state and takes corrective action (restart crashed services, stop services that should be idle). Inspired by Kubernetes controllers.
**Status:** Not built | **Complete:** 0%

### Feature 22: Rolling Restarts
**Restart services without downtime.**
When a project has multiple instances or a restart is requested, the platform stops and starts one instance at a time. Health check must pass before proceeding to the next. Rollback if the new version fails health checks.
**Status:** Not built | **Complete:** 0%

### Feature 23: Namespace Isolation
**Group projects into logical environments.**
Namespaces (dev, staging, prod) partition projects. Each namespace can have its own config overrides, port ranges, and access rules. A project belongs to one namespace at a time but can be promoted between them.
**Status:** Not built | **Complete:** 0%

### Feature 24: Service Discovery & Routing
**Projects find each other by name, not port.**
Register service endpoints in METADATA.md. Other projects reference them by name (`@project-name/api`). Platform resolves to actual host:port. Enables loose coupling between projects.
**Status:** Not built | **Complete:** 0%

---

## Summary

| # | Feature | Domain | Status | Complete |
|---|---------|--------|--------|----------|
| 1 | Control Panel | Core | Built | 85% |
| 2 | Project Discovery | Core | Built | 75% |
| 3 | Project Scaffolding | Core | Not built | 0% |
| 4 | Operations Engine | Ops | Built | 90% |
| 5 | Process Monitor | Ops | Built | 85% |
| 6 | Scheduling & Cron | Ops | Not built | 0% |
| 7 | Job Pipelines | Ops | Not built | 0% |
| 8 | Monitoring & Health | Observability | Not built | 0% |
| 9 | Usage Analytics | Observability | Built | 80% |
| 10 | Event Log | Observability | Not built | 0% |
| 11 | Compliance Verification | Governance | Built | 70% |
| 12 | Workflow States | Governance | Not built | 5% |
| 13 | Environment Management | Governance | Not built | 0% |
| 14 | Portfolio Publishing | Publishing | Built | 75% |
| 15 | Documentation Generation | Publishing | Partial | 40% |
| 16 | Configuration Management | Config | Built | 85% |
| 17 | Git Integration | Config | Built | 80% |
| 18 | Tag Management | Config | Built | 80% |
| 19 | Secrets Management | Config | Not built | 0% |
| 20 | Resource Limits | Config | Not built | 0% |
| 21 | Desired State Reconciliation | Orchestration | Not built | 0% |
| 22 | Rolling Restarts | Orchestration | Not built | 0% |
| 23 | Namespace Isolation | Orchestration | Not built | 0% |
| 24 | Service Discovery & Routing | Orchestration | Not built | 0% |

**Built:** 10 features | **Partial:** 1 | **Not built:** 13
