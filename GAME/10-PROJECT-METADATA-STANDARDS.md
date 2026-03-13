# Project Metadata Standards

**spec_v5 · 2026-03-13**

---

## Purpose

Defines the single file a project uses to describe itself to the platform and to the AI development environment. All project identity, portfolio card, service links, and discovery metadata live in one place.

---

## The Consolidated Contract: METADATA.md

**Location:** Project root (`METADATA.md`)
**Replaces:** `git_homepage.md`, `Links.md`, `STACK.yaml` (those files are deprecated)

```
name: MyProject
title: My Project — Short Tagline
description: One to two sentence description of what this project does.
port: 8000
status: ACTIVE
version: 1.0
updated: 2026-03-13
stack: Python/Flask/SQLite
image: images/myproject.webp
health: /health
show_on_homepage: true
tags: web, tool, api
links:
    Production  | https://myproject.example.com | Live site
    Docs        | https://docs.example.com       | API documentation
    Staging     | https://staging.example.com    | Pre-production
```

---

## Field Reference

| Field | Required At | Purpose |
|-------|------------|---------|
| `name` | All statuses | Machine name (no spaces) |
| `status` | All statuses | Lifecycle stage: IDEA, PROTOTYPE, ACTIVE, PRODUCTION, ARCHIVED |
| `title` | PROTOTYPE+ | Display name with short tagline |
| `description` | PROTOTYPE+ | One to two sentences for portfolio card and dashboard |
| `port` | ACTIVE+ | Primary port the service listens on |
| `stack` | ACTIVE+ | Short technology summary (e.g. `Python/Flask/SQLite`) |
| `version` | ACTIVE+ | Semantic version |
| `updated` | ACTIVE+ | ISO date of last meaningful change |
| `tags` | ACTIVE+ | Comma-separated tags for dashboard filtering and portfolio badges |
| `show_on_homepage` | ACTIVE+ | `true` = include in published portfolio |
| `image` | Optional | Relative path to portfolio card image |
| `health` | PRODUCTION | Health check endpoint path (e.g. `/health`) |
| `links` | Optional | Pipe-separated table: `Name | URL | Notes` |

---

## Status Values

| Status | Meaning |
|--------|---------|
| `IDEA` | Concept only — no code expected |
| `PROTOTYPE` | Proof of concept — not stable |
| `ACTIVE` | Actively developed and in use |
| `PRODUCTION` | Stable, deployed, monitored |
| `ARCHIVED` | No longer maintained |

The compliance verifier (`verify.py`) uses status to determine which rules to enforce. IDEA projects are not penalized for missing bin/ scripts or CLAUDE.md. PRODUCTION projects are checked for health endpoints, git compliance, and clean environment handling.

---

## CLAUDE.md — AI Context File

**Location:** Project root (`CLAUDE.md`)
**Required at:** PROTOTYPE and above

Provides working context to the AI assistant. Standard sections parsed by the platform:

```markdown
# Project Title
One paragraph description.

## Dev Commands
- Start: `./bin/start.sh`
- Test: `./bin/test.sh`

## Service Endpoints
- Local: http://localhost:8000

## Bookmarks
### Useful Links
- [Production](https://...)
```

Sections `## Dev Commands`, `## Service Endpoints`, and `## Bookmarks` are required at ACTIVE and above.

---

## Deprecated Files

These files were used in earlier versions of the platform. Their fields have been merged into `METADATA.md`. Do not create them for new projects. Migrate existing projects and delete the originals.

| Deprecated File | Replaced By |
|----------------|-------------|
| `git_homepage.md` | `title`, `description`, `tags`, `image`, `show_on_homepage` in METADATA.md |
| `Links.md` | `links:` block in METADATA.md |
| `STACK.yaml` | `stack:` field in METADATA.md |

---

## Interfaces With

- **PROJECT-DISCOVERY**: reads METADATA.md on every scan
- **CONTROL-PANEL**: displays title, status, tags, links from METADATA.md
- **GITHUB-PUBLISHER**: reads `show_on_homepage`, `title`, `description`, `tags`, `image` for portfolio cards
- **COMPLIANCE-VERIFICATION** (`verify.py`): checks field presence and value validity per status level
