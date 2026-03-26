# Specification Conversion Rules

**Version:** 20260320 V1  
**Description:** Rules for expanding concise spec files into implementation-ready detailed specs

**How to expand concise project specs into detailed, implementation-ready specifications.**

These rules are global — they apply to all projects regardless of stack. Stack-specific expansion is handled by the corresponding `stack/*.md` file.

---

## Expansion Principles

1. **The spec author writes the WHAT.** Column names, screen layouts, triggers, sequences.
2. **The conversion expands the HOW.** Types, defaults, constraints, HTMX attributes, error handling — all inferred from stack rules and conventions.
3. **Stack implies conventions.** If METADATA.md says `stack: Python/Flask/SQLite`, apply every pattern from `stack/python.md`, `stack/flask.md`, `stack/sqlite.md` without the author restating them.
4. **Don't duplicate stack rules into specs.** If `stack/sqlite.md` says "WAL mode, FK pragma, Row factory" then DATABASE.md should NOT repeat that. The build prompt includes both.
5. **[ROADMAP] items preserve intent only.** Do not expand implementation detail for roadmap features. Keep the description and Open Questions.

---

## DATABASE.md Expansion

**Author writes:** table name, column names, types, and brief notes.

**Conversion adds:**
- `DEFAULT` clauses (infer from type: TEXT timestamps get `datetime('now')`, booleans get `0`, JSON gets `'{}'`)
- `NOT NULL` where the column is required (PKs, unique slugs, FKs)
- `UNIQUE` constraints noted in the author's comments
- FK references with `REFERENCES table(column)` syntax
- Index suggestions for columns used in WHERE/JOIN (prefix with `-- INDEX:`)
- The `_add_column_if_missing()` migration list from the column inventory
- Convention notes: WAL, FK pragma, JSON blob pattern — all from `stack/sqlite.md`

**Example — author writes:**

```markdown
## projects
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | TEXT | unique, machine slug |
| status | TEXT | IDEA/PROTOTYPE/ACTIVE/PRODUCTION/ARCHIVED |
| extra | JSON | |
| created_at | TEXT | timestamp |
```

**Conversion expands to full CREATE TABLE with defaults, constraints, indexes.**

---

## SCREEN-*.md Expansion

**Author writes:** route, columns/sections, interactions, Open Questions.

**Conversion adds:**
- HTMX attributes for each interaction (`hx-post`, `hx-target`, `hx-swap`)
- Server response type (HTML fragment vs full page)
- Reference to UI.md shared components used (nav bar, standard row header, filter bar)
- Flash message patterns for success/error states
- `columns=` directive mapped to Bootstrap grid or table layout

---

## FEATURE-*.md Expansion

**Author writes:** trigger, sequence (numbered steps), reads, writes, Open Questions.

**Conversion adds:**
- Route/endpoint signatures (method, path, return type)
- Event emissions (from the platform event model)
- Error handling pattern (catch at route, flash to user, log to platform, never crash)
- Concurrency notes (one instance per project, async where noted)
- Cross-references to SCREEN-*.md files that render this feature's output

---

## UI.md Expansion

**Author writes:** component name, purpose, key visual details.

**Conversion adds:**
- Bootstrap 5 class names and markup patterns
- CSS variable references (`--cc-surface`, `--cc-border`, etc.)
- HTMX loading states and swap targets
- Responsive behavior notes (desktop-first, 1024px minimum)

---

## ARCHITECTURE.md Expansion

**Author writes:** module names, responsibilities, directory layout.

**Conversion adds:**
- Import relationships between modules
- Public function signatures (name, params, return)
- Data flow arrows showing which module calls which
- Template directory structure with partial naming conventions

---

## Naming Conventions

| Prefix | Contains | Example |
|--------|----------|---------|
| `METADATA.md` | Project identity fields | Always present |
| `README.md` | One-line description + intent section | Always present |
| `DATABASE.md` | Tables and columns | If project has a database |
| `UI.md` | Shared visual patterns | If project has a UI |
| `ARCHITECTURE.md` | Code organization | Always present |
| `SCREEN-{Name}.md` | Per-screen specification | One per screen |
| `FEATURE-{Name}.md` | Cross-cutting behavior | One per major feature |

**Screen names** match the nav bar label: `SCREEN-Dashboard.md`, `SCREEN-Configuration.md`.

**Feature names** describe the capability: `FEATURE-Scan.md`, `FEATURE-Operations.md`.

### CHANGE Tickets (iteration only)

Mutations to existing specifications are expressed as CHANGE tickets, not edits fed raw to the build. Tickets live in `changes/CHANGE-NNN-description.md` within the spec directory.

| Prefix | Contains | Location |
|--------|----------|----------|
| `changes/CHANGE-NNN-description.md` | Targeted mutation to existing spec | `changes/` subdirectory |

**Ticket format:**

```markdown
# Change: NNN — Short description
**Status:** pending
**Type:** mutation
**Scope:** list of target files or areas

## Intent
Why this change is needed. One paragraph.

## Changes Required
- Specific, unambiguous instruction
- Another instruction

## Open Questions
None.
```

**Status values:** `pending` → `applied` (by LLM after apply) or `rejected` (by LLM if underspecified).
Rejected tickets gain a `## Rejection Reason` section. Applied tickets are kept for history.

---

## Open Questions Section

Spec files end with `## Open Questions` — except README.md and METADATA.md which do not have this section.

```markdown
## Open Questions
- Question about a design decision not yet resolved
- Question about scope or approach
```

Open Questions are preserved through conversion. They signal to the builder "ask the human before deciding." Agents add new questions to this section rather than creating new files.

---

## Build Tags

When `bin/build.sh` runs, it creates an annotated git tag:

```
build/{project}/{YYYY-MM-DD.N}
```

Annotated tags are permanent git objects — never pruned by `git gc`. This preserves the exact spec state used for each build. Diff between builds:

```bash
git diff build/Game-Build/2026-03-19.1..build/Game-Build/2026-03-19.2 -- Game-Build/
```

---

## Pipeline

```
setup.sh  →  (author edits)  →  validate.sh  →  convert.sh  →  build.sh
   CREATE             DRAFT            VALIDATED       CONVERTED       BUILT
```

| Step | Script | Output |
|------|--------|--------|
| CREATE | `bin/setup.sh <name> ["desc"]` | Spec directory with template files |
| DRAFT | (author edits files) | Concise specs |
| VALIDATED | `bin/validate.sh <name>` | Exit 0 = ready, exit 1 = fix issues |
| CONVERTED | `bin/convert.sh <name> > convert-prompt.md` | Detailed specs (optional — build handles inline) |
| BUILT | `bin/build.sh <name> > build-prompt.md` | Tagged commit + complete build prompt |
| PROMOTED | (copy spec dir to own repo) | Independent project |

One-shot path: skip CONVERTED, go straight from VALIDATED to BUILT. `bin/build.sh` includes ONESHOT_BUILD_RULES.md so the AI agent handles expansion and building in a single pass.
