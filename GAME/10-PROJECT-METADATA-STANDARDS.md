# Project Metadata Standards

**The METADATA.md contract.** Single file for project identity, portfolio, links, and discovery.

---

## METADATA.md

**Location:** Project root. **Replaces:** `git_homepage.md`, `Links.md`, `STACK.yaml`.

```yaml
name: MyProject
title: My Project — Short Tagline
description: One to two sentence description.
port: 8000
status: ACTIVE
version: 1.0
updated: 2026-03-13
stack: Python/Flask/SQLite
image: images/myproject.webp
health: /health
show_on_homepage: true
tags: web, tool, api
desired_state: running
namespace: production
links:
    Production | https://myproject.example.com | Live site
    Docs       | https://docs.example.com       | API documentation
```

## Fields

| Field | Required At | Purpose |
|-------|------------|---------|
| `name` | All | Machine name (no spaces) |
| `status` | All | IDEA, PROTOTYPE, ACTIVE, PRODUCTION, ARCHIVED |
| `title` | PROTOTYPE+ | Display name with tagline |
| `description` | PROTOTYPE+ | One to two sentences |
| `port` | ACTIVE+ | Primary service port |
| `stack` | ACTIVE+ | Technology summary |
| `version` | ACTIVE+ | Semantic version |
| `updated` | ACTIVE+ | ISO date |
| `tags` | ACTIVE+ | Comma-separated |
| `show_on_homepage` | ACTIVE+ | Include in portfolio |
| `image` | Optional | Portfolio card image path |
| `health` | PRODUCTION | Health check path |
| `links` | Optional | Pipe-separated: Name | URL | Notes |

## Status Levels

| Status | Compliance Level |
|--------|-----------------|
| IDEA | name + status only |
| PROTOTYPE | METADATA.md complete + CLAUDE.md stub |
| ACTIVE | Full script + metadata compliance |
| PRODUCTION | All rules including health + git + env |
| ARCHIVED | METADATA.md only |

## CLAUDE.md

**Required at:** PROTOTYPE+. Provides AI working context. Must have `## Dev Commands`, `## Service Endpoints`, `## Bookmarks` at ACTIVE+.

## Interfaces

- **PROJECT-DISCOVERY:** reads METADATA.md on every scan
- **CONTROL-PANEL:** displays title, status, tags, links
- **GITHUB-PUBLISHER:** reads portfolio fields
- **COMPLIANCE-VERIFICATION:** checks field presence per status
