# GAME — Generic AI Management Environment

A dashboard for managing multiple AI-built projects from one place.

## Intent

Solo practitioner or small team managing multiple AI-built projects. Standard format means standard operations: start/stop, logs, docs, health checks, unit tests all work the same way across every project.

Projects earn platform capabilities by adding files (contract-earns-capability). Add METADATA.md → project appears. Add bin/ scripts with headers → operation buttons appear. Add a health endpoint → monitoring activates.

## Stack

- **Language:** Python
- **Framework:** Flask (app factory, blueprints, HTMX partials)
- **Database:** SQLite (WAL mode, single file at `data/game.db`)
- **Frontend:** Bootstrap 5 (dark theme, CDN), HTMX (CDN)
- **Port:** 5001

Stack references: `GLOBAL_RULES/stack/` (python.md, flask.md, sqlite.md, bootstrap5.md).

## Building From This Specification

```bash
# Convert concise specs → detailed (optional, AI-assisted)
bash bin/convert.sh Game-Build > convert-prompt.md

# Build: tag commit + generate complete build prompt
bash bin/build.sh Game-Build > build-prompt.md

# Feed build-prompt.md to AI agent — it has everything needed to build from scratch
```
