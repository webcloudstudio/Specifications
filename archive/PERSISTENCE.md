# Project Metadata Persistence

**spec_v4 · 2026-03-11**

---

## The Principle

A project stores its own metadata in plain text files that live inside its repository.
The platform reads these files. The platform never owns the source of truth for a
project's description, settings, or state.

This means:
- Project metadata travels with the project in git
- An AI agent can read and update project metadata without a running platform
- Metadata survives platform reinstalls, migrations, or stack changes
- Humans can read and edit metadata in any text editor

---

## Where Data Lives

### Data the Project Owns

Stored in files committed to the project's git repository.

| What | Where | Format |
|------|-------|--------|
| AI working context | `CLAUDE.md` | Markdown with standard sections |
| Portfolio card | `git_homepage.md` | YAML frontmatter |
| Project links | `Links.md` | Markdown table |
| Technology stack | `STACK.yaml` | YAML |
| Operation scripts | `bin/*.sh` | Shell script with header |

An AI agent updating any of these files is updating persistent project state. No
database call needed. The change is immediately readable by the platform on the next
scan.

### Data the Platform Owns

Stored in the platform's own runtime database. This is derived data — it can be
regenerated from the project files at any time.

| What | Derived From |
|------|-------------|
| Project list | Filesystem scan |
| Operation buttons | bin/ headers |
| Endpoint links | CLAUDE.md sections |
| Stack badges | STACK.yaml |
| Portfolio card data | git_homepage.md |

If the platform database is deleted, a full scan restores all derived data from the
source files. Nothing is lost.

### Data the Platform Adds

Some data is added by the user through the platform UI and stored in the platform's
own config files (also committed to git, but in the platform's repo):

| What | Stored In |
|------|-----------|
| Tag colors | `data/tag_colors.json` (platform repo) |
| Tag assignments | Platform database (derived from tags in git_homepage.md when possible) |
| AI config profiles | `config_engine/profiles/` (platform repo) |

---

## How an AI Agent Persists Data

When an AI agent needs to record something about a project — a decision, a setting, a
completed feature — it edits the appropriate file in the project directory.

**Example: Recording that a feature was completed**

The agent adds a line to `CLAUDE.md` under a `## Completed Features` section:

```markdown
## Completed Features
- User authentication (2026-03-10)
- Portfolio publishing (2026-02-28)
```

The platform surfaces this on the next scan. The information is in git history. No
database update needed.

**Example: Updating the portfolio card description**

The agent edits `git_homepage.md`:

```yaml
---
Title: My Project
Description: Updated description reflecting new capabilities.
Tags: web, tool
Show on Homepage: true
---
```

The change is reflected in the portfolio on the next publish run. The agent does not
need access to the platform to make this change.

---

## What This Means for Feature Specifications

Each feature spec that produces or consumes persistent data should state:

- What data it needs to store
- Which file it stores it in
- What the format looks like (a brief example)

The spec does not need to describe a database schema. It describes a file section or
YAML field that an AI agent can write and a human can read.
