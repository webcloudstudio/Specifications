# GAME — Project Management Dashboard

**Status**: Specification v4 | **Updated**: 2026-03-13

Discovers local projects via filesystem contracts and provides a unified dashboard for operations, monitoring, publishing, and AI-assisted development workflows.

---

# Catalog

## Feature Specifications

| File | Description |
|------|-------------|
| `CONTROL-PANEL.md` | Main dashboard — project list, status, inline actions, operation buttons |
| `PROJECT-DISCOVERY.md` | Filesystem scanner that auto-registers projects and their capabilities |
| `OPERATIONS-ENGINE.md` | Runs bin/ scripts on demand, captures output, reports status |
| `PROCESS-MONITOR.md` | Live log viewer and process control panel |
| `GIT-INTEGRATION.md` | Per-project git status display and governance checks |
| `GITHUB-PUBLISHER.md` | Generates and publishes a GitHub Pages portfolio from project metadata |
| `PROJECT-DOCUMENTATION.md` | Auto-includes project docs/ sites in the portfolio build |
| `TAG-MANAGEMENT.md` | Visual grouping with colored tags and filtering |
| `CONFIGURATION-MANAGEMENT.md` | AI assistant config profiles with versioned deployment and rollback |
| `USAGE-ANALYTICS.md` | Token usage and cost tracking across AI sessions |
| `MONITORING-HEARTBEATS.md` | Health polling and alerting for running services [ROADMAP] |
| `WORKFLOW-STATES.md` | Feature ticket lifecycle from IDEA to DONE [ROADMAP] |

## Contract & Standards Specifications

| File | Description |
|------|-------------|
| `09-SERVICE-SCRIPT-STANDARDS.md` | The bin/ script header contract — how scripts register as operations |
| `10-PROJECT-METADATA-STANDARDS.md` | File contracts: CLAUDE.md, git_homepage.md, Links.md, STACK.yaml |
| `15-FEATURE-INTERRELATIONSHIP-MAP.md` | Dependency graph showing how all features connect |
