# Project Discovery

**Auto-registration via filesystem scan.** Finds all projects, reads their contracts, registers capabilities. No manual setup.

---

## Capabilities

- Scan a root directory for project subdirectories
- Read METADATA.md for identity, status, tags, links
- Read CLAUDE.md for endpoints and bookmarks
- Read bin/ scripts for CommandCenter Operation headers
- Read git status per project
- Upsert project records and capabilities
- Mark removed projects as inactive (not deleted)

## How It Works

1. Scan root directory — every subdirectory is a candidate
2. Derive display name from directory name (CamelCase → spaced words)
3. Read METADATA.md if present
4. Read CLAUDE.md if present
5. Read bin/ headers for registered operations
6. Read git status
7. Upsert project record

Missing contract files produce compliance gaps, not errors.

## Scan Triggers

- Platform startup
- User request (Rescan button)

## Data Produced

| Data | Consumed By |
|------|-------------|
| Project records | CONTROL-PANEL |
| Operation registry (bin/ headers) | OPERATIONS-ENGINE, CONTROL-PANEL |
| Endpoints and bookmarks (CLAUDE.md) | CONTROL-PANEL |
| Portfolio metadata (METADATA.md) | GITHUB-PUBLISHER |
| Git status | CONTROL-PANEL, GIT-INTEGRATION |
| Compliance flags | CONTROL-PANEL |
