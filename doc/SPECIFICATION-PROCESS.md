# Specification Process

**Version:** 20260320 V3
**Description:** Step-by-step guide to the Prototyper specification workflow

Prototyper converts concise specification files into AI agent build prompts.

---

## Step 1 — Setup the Prototype Directory

```bash
bash bin/setup.sh <ProjectName>
```

Creates `Specifications/<ProjectName>/` with template files from `RulesEngine/spec_template/`.

Edit `METADATA.md` immediately. `validate.sh` requires all four fields to be set:
`name`, `display_name`, `short_description`, `status`.

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
bash bin/validate.sh <ProjectName>       # from repo root
bash bin/validate.sh                     # from within the project directory
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

---

## Step 4 — Convert to Detailed Specs  *(optional)*

```bash
bash bin/convert.sh <ProjectName> > convert-prompt.md
bash bin/convert.sh               > convert-prompt.md    # from within project directory
```

Generates: `CONVERT.md` expansion rules + stack references + concise spec files.
Feed to an AI agent to produce detailed, implementation-ready specs.
Replace the concise spec files with the expanded output, then proceed to Step 5.

`build.sh` includes `CONVERT.md` inline — the AI can expand during build without this step.

---

## Step 5 — Build the Prompt

```bash
bash bin/build.sh <ProjectName> > build-prompt.md
bash bin/build.sh               > build-prompt.md    # from within project directory
```

Creates annotated git tag `build/<ProjectName>/YYYY-MM-DD.N` and generates the build prompt.
Feed `build-prompt.md` to an AI agent to build the application.

| Flag | Effect |
|------|--------|
| `--no-tag` | Generate prompt without creating a tag |
| `--tag-only` | Tag the commit without generating a prompt |

```bash
git tag -l "build/<Project>/*"
git diff build/<Project>/2026-03-19.1..build/<Project>/2026-03-20.1 -- <Project>/
git checkout build/<Project>/2026-03-19.1 -- <Project>/DATABASE.md
```

---

## Promote — Create a Live Code Project

Once the spec is built, promote it to a running project using the GAME `create_project.py` tool.
See `PROMOTE.md` for the full step-by-step guide.

```bash
cd ~/projects/GAME
python3 bin/create_project.py <ProjectName>   # scaffold ~/projects/<ProjectName>/
bash bin/update_projects.sh                   # propagate RulesEngine standards
bash bin/validate_project.sh <ProjectName>    # check platform conformance
```

---

## RulesEngine Workflow — Updating Agent Rules

`RulesEngine/` is the authoritative source for agent behavioral rules, stack patterns, and branding.
When rules change, regenerate `CLAUDE_RULES.md` and propagate to all projects.

### Updating a Rule

1. Edit `RulesEngine/BUSINESS_RULES.md` — change the rule's `**Rule text:**` block
2. Regenerate `CLAUDE_RULES.md`:

```bash
bash bin/generate_claude_rules.sh > rules-prompt.md
# Feed rules-prompt.md to an AI agent — paste output over RulesEngine/CLAUDE_RULES.md
```

3. Propagate to all code projects:

```bash
cd ~/projects/GAME
bash bin/update_projects.sh    # pushes CLAUDE_RULES.md, common.sh/py, index.html
```

### Adding a Stack File

Add `RulesEngine/stack/<technology>.md` with prescriptive patterns. Declare it in project `METADATA.md` as `stack: .../Technology`. `convert.sh` and `build.sh` pick it up automatically.

### Adding a New Template File

To distribute a new file to all code projects, see the "Adding a New Standard Feature" pattern in `AGENTS.md`.
