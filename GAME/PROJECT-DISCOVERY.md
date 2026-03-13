# Feature: Project Discovery

**spec_v4 · 2026-03-11**

---

## Purpose

Finds all projects on the filesystem and registers their capabilities with the platform.
No manual setup. A project that follows the contracts is automatically discovered and
surfaced in the dashboard.

---

## What the User Can Do

- Projects appear automatically after a scan
- Trigger a manual rescan at any time
- See which contracts each project has implemented (compliance summary)
- See when the last scan ran

---

## How Discovery Works

The platform scans a single root directory. Every subdirectory is a candidate project.

For each project directory:
1. Derive the display name from the directory name (CamelCase → spaced words)
2. Read each contract file if present — CLAUDE.md, git_homepage.md, Links.md, STACK.yaml
3. Read all bin/ scripts for CommandCenter headers
4. Read git status
5. Upsert the project record and its capabilities

A missing contract file is not an error — it produces a compliance gap, shown in the dashboard.

### Name Derivation

| Directory Name | Display Title |
|---------------|--------------|
| `MyProject` | My Project |
| `GAME` | GAME |
| `my-tool` | my tool |
| `conquer_2026` | Conquer 2026 |

### Scan Triggers

- On platform startup
- On user request (Rescan button)

Projects no longer found on disk are marked inactive — not deleted.

---

## Data Produced

| Data | Consumed By |
|------|-------------|
| Project records | CONTROL-PANEL |
| Operation registry (from bin/ headers) | OPERATIONS-ENGINE, CONTROL-PANEL |
| Endpoints and bookmarks (from CLAUDE.md) | CONTROL-PANEL |
| Card metadata (from git_homepage.md) | GITHUB-PUBLISHER |
| Links (from Links.md) | CONTROL-PANEL |
| Git status | CONTROL-PANEL, GIT-INTEGRATION |
| Compliance flags | CONTROL-PANEL |

---

## Contracts Read

All five contracts defined in THE-CONTRACT.md are read during discovery.

---

## Out of Scope

- Displaying projects → CONTROL-PANEL
- Executing operations → OPERATIONS-ENGINE
- Publishing portfolio → GITHUB-PUBLISHER
