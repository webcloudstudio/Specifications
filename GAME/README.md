# GAME — Generic AI Management Environment

A Flask/SQLite dashboard for managing AI-assisted projects. Discovers local projects via METADATA.md and bin/ scripts, provides operations, monitoring, publishing, and workflow management.

## Screens

| File | Screen | Status |
|------|--------|--------|
| `SCREEN-DASHBOARD.md` | Main project list, operations, git status | Built |
| `SCREEN-PROCESSES.md` | Live log viewer, process control | Built |
| `SCREEN-PUBLISHER.md` | Portfolio site builder and publisher | Built |
| `SCREEN-CONFIGURATION.md` | AI config profile management | Built |
| `SCREEN-USAGE.md` | Token usage and cost tracking | Built |
| `SCREEN-MONITORING.md` | Service health polling and alerts | Roadmap |
| `SCREEN-WORKFLOW.md` | Kanban ticket board with AI audit trail | Roadmap |

## Standards

All project integration standards (scripts, metadata, secrets, documentation) are defined in `../CLAUDE_RULES.md`. The GAME specs describe only what each screen does and how it interfaces with the platform.

## Stack

Python / Flask / SQLite / Bootstrap 5 | Port 5001
