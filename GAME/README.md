# GAME — Generic AI Management Environment

**Status:** Specification v5 | **Updated:** 2026-03-13

A dashboard for managing AI-assisted projects. Discovers local projects via filesystem contracts, provides operations, monitoring, publishing, and workflow management.

---

## Feature Specifications

| File | Description |
|------|-------------|
| `CONTROL-PANEL.md` | Main dashboard — project list, status, operations |
| `PROJECT-DISCOVERY.md` | Filesystem scanner, auto-registration |
| `OPERATIONS-ENGINE.md` | Run bin/ scripts on demand, capture output |
| `PROCESS-MONITOR.md` | Live log viewer, process control |
| `GIT-INTEGRATION.md` | Per-project git status (read-only) |
| `GITHUB-PUBLISHER.md` | Static portfolio site from METADATA.md |
| `PROJECT-DOCUMENTATION.md` | Self-contained docs per project |
| `TAG-MANAGEMENT.md` | Visual grouping with colored tags |
| `CONFIGURATION-MANAGEMENT.md` | AI config profiles with rollback |
| `USAGE-ANALYTICS.md` | Token usage and cost tracking |
| `MONITORING-HEARTBEATS.md` | Health polling and alerting [ROADMAP] |
| `WORKFLOW-STATES.md` | Feature ticket lifecycle [ROADMAP] |

## Standards

| File | Description |
|------|-------------|
| `09-SERVICE-SCRIPT-STANDARDS.md` | bin/ script header contract |
| `10-PROJECT-METADATA-STANDARDS.md` | METADATA.md and CLAUDE.md contracts |
| `15-FEATURE-INTERRELATIONSHIP-MAP.md` | Feature dependency graph |

## Stack

Python / Flask / SQLite / Bootstrap 5 | Port 5001
