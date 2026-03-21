# Specification Process

**Version:** 20260321 V4
**Description:** Step-by-step guide to the Prototyper specification workflow

Prototyper converts concise specification files into AI agent build prompts that run on a Feature Branch.

---

## Step 1 — Setup the Prototype Directory

```bash
bash bin/setup.sh <ProjectName>
```

Creates `Specifications/<ProjectName>/` with template files from `RulesEngine/spec_template/`.

Edit `METADATA.md` immediately — set `name`, `display_name`, `short_description`, `status`.
Set `git_repo:` to the remote URL of the project repository.

---

## Step 2 — Create the Spec Files

Edit each file. Delete `DATABASE.md` or `UI.md` if not applicable.
Rename `SCREEN-Example.md` and `FEATURE-Example.md` to real names before Step 3.

| Convention | Rule |
|------------|------|
| Scope | Concise specs only: tables, bullets, short descriptions. `CONVERT.md` expands them. |
| Screens | `SCREEN-<Name>.md` — route, layout, columns, interactions |
| Features | `FEATURE-<Name>.md` — trigger, sequence, reads, writes |
| End section | All files except `README.md`, `METADATA.md`, `INTENT.md` must end with `## Open Questions` |
| Stack | Do not repeat stack patterns — they come from `RulesEngine/stack/` |

---

## Step 3 — Validate the Spec

```bash
bash bin/validate.sh <ProjectName>
bash bin/validate.sh <ProjectName> --verbose
```

Exit 0 = ready. Exit 1 = errors to fix.

| Check | Condition |
|-------|-----------|
| Required files | `METADATA.md`, `README.md`, `INTENT.md`, `ARCHITECTURE.md` exist |
| METADATA fields | `name`, `display_name`, `short_description`, `status` are all set |
| INTENT.md | Has content — not still the template placeholder |
| Naming | Spec files use `SCREEN-*` or `FEATURE-*` prefix |
| Template cleanup | `SCREEN-Example.md` and `FEATURE-Example.md` have been renamed or deleted |
| Open Questions | All applicable files have `## Open Questions` section |
| Stack files | If `stack:` is declared, `RulesEngine/stack/<component>.md` exists for each component |
| Feature Branch | If `type: oneshot`, `BUILD_FEATURE_BRANCH_NAME` must be set in `.env` |

---

## Step 4 — Convert to Detailed Specs  *(optional)*

```bash
bash bin/convert.sh <ProjectName> > convert-prompt.md
```

Generates: `CONVERT.md` expansion rules + stack references + concise spec files.
Feed to an AI agent to produce detailed, implementation-ready specs.
Replace the concise spec files with the expanded output, then proceed to Step 5.

`build.sh` includes `CONVERT.md` inline — the AI can expand during build without this step.

---

## Step 5 — Build

```bash
bash bin/build.sh <ProjectName> > build-prompt.md
```

Requires `BUILD_FEATURE_BRANCH_NAME=feature/my-name` in `Specifications/<ProjectName>/.env`.

1. Clones `git_repo` into `../<ProjectName>/` if it does not exist, or fetches if it does
2. Creates `feature/<name>` branch from `base_branch` (configured or auto-detected)
3. Generates the build prompt — feed `build-prompt.md` to Claude Code running in `../<ProjectName>/`

```
Feature Branch Created: feature/my-name
Open Claude Code in: ../<ProjectName>/
```

The AI agent implements the spec on the feature branch. The project is immediately runnable and testable.

