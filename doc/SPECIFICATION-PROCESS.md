# Specification Process

**Version:** 20260320 V1
**Description:** Step-by-step guide to the Prototyper specification workflow

Prototyper converts concise specification files into AI agent build prompts.

---

## Step 1 — Create the Spec Directory

```bash
bash bin/create_spec.sh <ProjectName>
```

Creates `Specifications/<ProjectName>/` with template files from `GLOBAL_RULES/spec_template/`.

Edit `METADATA.md` immediately. `validate.sh` requires all four fields to be set:
`name`, `display_name`, `short_description`, `status`.

---

## Step 2 — Write the Spec Files

Edit each file. Delete `DATABASE.md` or `UI.md` if not applicable.
Rename `SCREEN-Example.md` and `FEATURE-Example.md` to real names before Step 3.

| Convention | Rule |
|------------|------|
| Scope | Concise specs only: tables, bullets, short descriptions. `CONVERT.md` expands them. |
| Screens | `SCREEN-<Name>.md` — route, layout, columns, interactions |
| Features | `FEATURE-<Name>.md` — trigger, sequence, reads, writes |
| End section | All files except `README.md`, `METADATA.md`, `INTENT.md` must end with `## Open Questions` |
| Stack | Do not repeat stack patterns — they come from `GLOBAL_RULES/stack/` |

---

## Step 3 — Validate

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
| Stack files | If `stack:` is declared, `GLOBAL_RULES/stack/<component>.md` exists for each component |

---

## Step 4 — Convert  *(optional)*

```bash
bash bin/convert.sh <ProjectName> > convert-prompt.md
bash bin/convert.sh               > convert-prompt.md    # from within project directory
```

Generates: `CONVERT.md` expansion rules + stack references + concise spec files.
Feed to an AI agent to produce detailed, implementation-ready specs.
Replace the concise spec files with the expanded output, then proceed to Step 5.

`build.sh` includes `CONVERT.md` inline — the AI can expand during build without this step.

---

## Step 5 — Build

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

## Step 6 — Iterate

Edit spec files → validate → build. Each build creates a permanent git tag.

---

## Step 7 — Promote

```bash
cp -r Specifications/<ProjectName> ~/projects/<ProjectName>
cd ~/projects/<ProjectName>
git init && git add -A && git commit -m "Initial spec"
git remote add origin <url>
```

Run `python3 bin/create_project.py <ProjectName>` from `GAME/` to scaffold the code project.
