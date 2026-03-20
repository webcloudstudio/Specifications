# Specification Process

Contract and state machine for the spec-driven build system.

---

## State Machine

```
CREATE ──> DRAFT ──> VALIDATED ──> CONVERTED ──> BUILT ──> PROMOTED
                        │                          │
                        └──────── (iterate) ───────┘
```

| State | Entry Condition | Exit Condition |
|-------|----------------|----------------|
| **CREATE** | `bin/create_spec.sh` runs | Directory exists with template files |
| **DRAFT** | Author edits spec files | Author decides specs are complete enough |
| **VALIDATED** | `bin/validate.sh` exits 0 | Required files present, naming correct, fields set |
| **CONVERTED** | `bin/convert.sh` output reviewed | Detailed specs committed (or skipped — build handles inline) |
| **BUILT** | `bin/build.sh` tags commit + generates prompt | Build prompt fed to AI agent, application produced |
| **PROMOTED** | Spec directory copied to own repo (`../ProjectName/`) | Project lives independently with its own git history |

Iteration: after a build, edit specs → re-validate → re-build. Each build creates a new tag. Diff between tags to see what changed.

---

## Scripts

All scripts take the project specification directory name as the first argument.

### `bin/create_spec.sh`

```
bash bin/create_spec.sh <project-name> ["Short description"]
```

| Arg | Required | Description |
|-----|----------|-------------|
| `$1` | yes | Project name — becomes directory name and METADATA slug |
| `$2` | no | Short description — populates METADATA and README |

Creates `<project-name>/` from `GLOBAL_RULES/spec_template/`. Substitutes project name, slug, description, and date into templates.

**Produces:** METADATA.md, README.md, INTENT.md, ARCHITECTURE.md, DATABASE.md, UI.md, SCREEN-Example.md, FEATURE-Example.md

### `bin/validate.sh`

```
bash bin/validate.sh <project-name> [--verbose]
```

| Arg | Required | Description |
|-----|----------|-------------|
| `$1` | yes | Project name — specification directory to validate |
| `--verbose` | no | Show passing checks (default: errors and warnings only) |

**Exit 0** = valid. **Exit 1** = errors found.

Checks:
- Required files: METADATA.md, README.md, INTENT.md, ARCHITECTURE.md
- Required METADATA fields: name, display_name, short_description, status
- Status value is valid enum
- Stack files exist in GLOBAL_RULES/stack/ (if stack declared)
- INTENT.md has real content (not template placeholder)
- File naming conventions (SCREEN-*, FEATURE-* prefixes)
- Open Questions section in spec files (not README, METADATA, INTENT)
- No leftover template files (SCREEN-Example.md, FEATURE-Example.md)

### `bin/convert.sh`

```
bash bin/convert.sh <project-name> > convert-prompt.md
```

| Arg | Required | Description |
|-----|----------|-------------|
| `$1` | yes | Project name — specification directory to convert |

Generates a prompt to stdout. Contents: GLOBAL_RULES/CONVERT.md expansion rules + stack reference files + all concise spec files from the project directory. Feed to an AI agent for expansion into detailed specs.

**Requires:** METADATA.md with `stack:` field.

### `bin/build.sh`

```
bash bin/build.sh <project-name> [--no-tag] [--tag-only] > build-prompt.md
```

| Arg | Required | Description |
|-----|----------|-------------|
| `$1` | yes | Project name — specification directory to build from |
| `--no-tag` | no | Generate prompt without creating a build tag |
| `--tag-only` | no | Create build tag without generating prompt |

Creates annotated git tag `build/{project}/{YYYY-MM-DD.N}`, then generates a complete build prompt to stdout. Contents: CONVERT.md + CLAUDE_RULES.md + stack files + all spec files.

Warns on uncommitted changes. Shows diff stat from previous build tag.

### `bin/test.sh`

```
bash bin/test.sh
```

No arguments. Tests the specification system itself: verifies templates exist, scripts have correct headers, global rules are intact, and runs a create+validate round-trip.

---

## Build Tags

Every `bin/build.sh` run creates an annotated git tag:

```
build/{project}/{YYYY-MM-DD.N}
```

**Properties:**
- Annotated tags are full git objects — never pruned by `git gc`
- Include metadata: commit SHA, commit message, build timestamp
- Auto-increment: `.1`, `.2`, `.3` within same day

**Operations:**

```bash
# List builds for a project
git tag -l "build/Game-Build/*"

# Diff specs between builds
git diff build/Game-Build/2026-03-19.1..build/Game-Build/2026-03-20.1 -- Game-Build/

# See what commit a build used
git show build/Game-Build/2026-03-19.1

# Restore a spec file from a previous build
git checkout build/Game-Build/2026-03-19.1 -- Game-Build/DATABASE.md
```

---

## Git Strategy

Single repo, solo developer, autocommitting.

| Concern | Approach |
|---------|----------|
| Branching | Stay on `main`. No feature branches. |
| Commits | Autocommit as you work. Git is for rollback and safety. |
| Stable points | Build tags mark "I built from this state." |
| Rollback | `git checkout build/{tag} -- {file}` to restore a spec. |
| Diff | `git diff build/{old}..build/{new} -- {project}/` for spec-to-spec comparison. |
| Push | Never force-push. Never rebase. Linear history. |

---

## File Contract

### Required (every spec directory)

| File | Purpose | Has Open Questions |
|------|---------|-------------------|
| `METADATA.md` | Project identity fields | No |
| `README.md` | One-line description | No |
| `INTENT.md` | Why this project exists | No |
| `ARCHITECTURE.md` | Modules, routes, directory layout | Yes |

### Conditional

| File | When | Has Open Questions |
|------|------|-------------------|
| `DATABASE.md` | Project has a database | Yes |
| `UI.md` | Project has a user interface | Yes |
| `SCREEN-{Name}.md` | One per UI screen | Yes |
| `FEATURE-{Name}.md` | One per cross-cutting behavior | Yes |

### Required METADATA.md Fields

| Field | Description |
|-------|-------------|
| `name` | Machine slug, matches directory name |
| `display_name` | Human-readable name |
| `short_description` | One sentence |
| `status` | IDEA / PROTOTYPE / ACTIVE / PRODUCTION / ARCHIVED |

All other METADATA fields are optional. `stack:` is needed for convert/build but not required at IDEA status.

### Naming Rules

| Pattern | Use for |
|---------|---------|
| `SCREEN-{NavLabel}.md` | Screen specs — name matches nav bar label |
| `FEATURE-{Capability}.md` | Feature specs — name describes the capability |
| Uppercase with hyphens | All spec files |

---

## Global Rules Location

```
GLOBAL_RULES/
  CONVERT.md           Expansion methodology (how concise → detailed)
  CLAUDE_RULES.md      Agent behavior contract (injected into project AGENTS.md)
  stack/               Technology patterns (flask.md, sqlite.md, ...)
  spec_template/       Template files for create_spec.sh
  templates/           Code templates (common.sh, common.py)
```

CONVERT.md is global, not per-project. The methodology is shared. Project-specific decisions live in the spec files themselves.

---

## Promotion

When a spec is built and the application works, promote the spec directory to its own repo:

1. `cp -r Game-Build/ ../Game-Build/` (or wherever the project lives)
2. The spec files become the project's documentation
3. The Specifications repo retains the build tags — they remain valid for diffing
4. The project repo gets its own git history from that point forward
