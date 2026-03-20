# Specification Process

How the spec-driven build system works. This is the methodology for one-shotting applications from specifications.

---

## Pipeline Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  You write   │     │  convert.sh  │     │  build.sh   │
│ concise specs│────>│  (optional)  │────>│  (tag+prompt)│───> AI builds app
│              │     │  AI expands  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Phase 1: Write** — You write concise markdown in a project specification directory (e.g., `Game-Build/`). Tables, bullet points, short descriptions. You define WHAT, not HOW.

**Phase 2: Convert (optional)** — `bin/convert.sh Game-Build` generates a prompt that includes your concise specs + GLOBAL_RULES/CONVERT.md expansion rules + stack files. Feed this to an AI agent. It outputs detailed specs. Review, edit, commit.

**Phase 3: Build** — `bin/build.sh Game-Build` creates an annotated git tag preserving the exact commit, then generates a complete build prompt (CONVERT rules + CLAUDE_RULES + stack files + all specs). Feed to an AI agent. It builds the app.

You can skip Phase 2 and go straight to Phase 3. The build prompt includes CONVERT.md so the AI can expand and build in one pass.

---

## File Types

| Prefix | What you write | What conversion expands |
|--------|---------------|------------------------|
| `METADATA.md` | Project identity fields | (not expanded) |
| `README.md` | Intent, stack, build instructions | (not expanded) |
| `DATABASE.md` | Table names, columns, types, notes | Full CREATE TABLE with defaults, constraints, indexes, migration list |
| `UI.md` | Component names, purposes, key visuals | Bootstrap classes, CSS variables, HTMX attributes |
| `ARCHITECTURE.md` | Module names, responsibilities, layout | Import relationships, function signatures, data flow |
| `SCREEN-{Name}.md` | Route, columns, interactions | HTMX attributes, server response types, component references |
| `FEATURE-{Name}.md` | Trigger, sequence, reads, writes | Route signatures, event emissions, error handling, concurrency |

Every file ends with `## Open Questions` for unresolved decisions.

---

## Build Tags

Every build creates an annotated git tag:

```
build/{project}/{YYYY-MM-DD.N}
```

Example: `build/Game-Build/2026-03-19.1`

**Why annotated tags:**
- They are full git objects (not just pointers)
- Never pruned by `git gc` or `git prune`
- Include metadata: who built, when, commit SHA, commit message
- Can be listed: `git tag -l "build/Game-Build/*"`
- Can be diffed: `git diff build/Game-Build/2026-03-19.1..build/Game-Build/2026-03-19.2 -- Game-Build/`

**This enables spec iteration:** after building, you can see exactly what changed in the specs between builds. If something broke, diff the tags to find which spec change caused it.

---

## Git Strategy

This is a single repo with a solo developer autocommitting.

- **Branch:** Stay on `main`. No feature branches needed.
- **Commits:** Autocommit as you work. Git is for rollback and safety.
- **Tags:** Build tags are the stable reference points. Commits flow continuously; tags mark "I built from this."
- **Rollback:** To see what changed: `git diff build/Game-Build/1..build/Game-Build/2 -- Game-Build/`. To revert a spec: `git checkout build/Game-Build/1 -- Game-Build/DATABASE.md`.
- **Never force-push.** Never rebase. Linear history, tags are immutable anchors.

---

## Directory Structure

```
Specifications/
  GLOBAL_RULES/
    CONVERT.md              ← Expansion rules (global methodology)
    CLAUDE_RULES.md         ← Agent behavior contract
    stack/                  ← Technology patterns (flask.md, sqlite.md, ...)
    templates/              ← Canonical common.sh, common.py

  bin/
    convert.sh              ← Generate conversion prompt for AI expansion
    build.sh                ← Tag commit + generate build prompt
    generate_prompt.sh      ← Legacy build prompt generator (no tagging)
    create_project.py       ← Scaffold new projects
    validate_project.py     ← Compliance checker
    update_projects.sh      ← Propagate rules to all projects
    rebuild_index.sh        ← Regenerate HTML indexes

  Game-Build/               ← Project specification directory
    METADATA.md             Identity
    README.md               Intent + stack + build instructions
    DATABASE.md             Schema
    UI.md                   Shared UI patterns
    ARCHITECTURE.md         Code organization
    SCREEN-Dashboard.md     Per-screen specs
    SCREEN-Configuration.md
    SCREEN-Processes.md
    SCREEN-Publisher.md
    SCREEN-Monitoring.md
    SCREEN-Workflow.md
    FEATURE-Scan.md         Per-feature specs
    FEATURE-Operations.md
    FEATURE-Publish.md
    FEATURE-Heartbeat.md
    FEATURE-Schedule.md
```

---

## Naming Conventions

**Directories:** PascalCase or hyphenated. Match METADATA.md `name` field. Example: `Game-Build`.

**Spec files:**

| Pattern | Purpose | Example |
|---------|---------|---------|
| `METADATA.md` | Identity | Always present |
| `README.md` | Overview | Always present |
| `DATABASE.md` | Schema | One per project (if it has a DB) |
| `UI.md` | Shared visuals | One per project (if it has a UI) |
| `ARCHITECTURE.md` | Code organization | Always present |
| `SCREEN-{NavLabel}.md` | One per screen | `SCREEN-Dashboard.md` |
| `FEATURE-{Capability}.md` | One per feature | `FEATURE-Scan.md` |

Screen names match the navigation label. Feature names describe the capability.

---

## What Goes Where

| Content | File | NOT in |
|---------|------|--------|
| Table columns and types | DATABASE.md | Architecture, Feature files |
| Startup/refresh behavior | FEATURE-Scan.md | DATABASE.md |
| Route table | ARCHITECTURE.md | Feature files (they reference routes, don't list them all) |
| Shared UI components | UI.md | Screen files (they reference UI.md) |
| Per-screen layout | SCREEN-*.md | UI.md, Architecture |
| Cross-cutting behavior | FEATURE-*.md | Screen files, Database |
| Stack conventions (WAL, etc.) | stack/*.md | DATABASE.md, Architecture |

**Rule:** If you're writing something that appears in two files, it's in the wrong place. Each fact lives in one file. Other files reference it.

---

## Quick Start: New Project

1. Create directory: `mkdir Specifications/MyProject`
2. Create METADATA.md with identity fields (name, display_name, stack, port, status)
3. Create README.md with intent and stack
4. Create DATABASE.md with tables (if applicable)
5. Create SCREEN-*.md for each screen
6. Create FEATURE-*.md for cross-cutting behaviors
7. Create UI.md for shared patterns (if applicable)
8. Create ARCHITECTURE.md for code organization
9. Run `bash bin/build.sh MyProject > build-prompt.md`
10. Feed to AI agent
