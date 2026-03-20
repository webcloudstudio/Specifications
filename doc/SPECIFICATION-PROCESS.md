# Specification Process

Prototyper converts concise specification files into AI agent build prompts.
Input: a directory of `.md` spec files. Output: a prompt that builds a working application.

---

## Step 1 — Create the Spec Directory

```bash
bash bin/create_spec.sh <ProjectName>
```

Creates `Specifications/<ProjectName>/` from `GLOBAL_RULES/spec_template/`.

**Generated files:**

| File | Required | Action |
|------|----------|--------|
| `METADATA.md` | Yes | Fill in required fields (see below) |
| `README.md` | Yes | One sentence: what this project is |
| `INTENT.md` | Yes | Why it exists, who it's for, what it is not |
| `ARCHITECTURE.md` | Yes | Modules, routes, directory layout |
| `DATABASE.md` | If has DB | Tables, columns, types — delete if no database |
| `UI.md` | If has UI | Shared patterns across screens — delete if no UI |
| `SCREEN-Example.md` | Rename | Rename to `SCREEN-<Name>.md` for each screen |
| `FEATURE-Example.md` | Rename | Rename to `FEATURE-<Name>.md` for cross-cutting behavior |

**Required METADATA.md fields:**

```
name:              ProjectName
display_name:      Project Name
short_description: One sentence description.
status:            IDEA
```

**Optional METADATA.md fields:**

```
stack:     flask/sqlite
port:      5000
tags:      dashboard, admin
```

---

## Step 2 — Write the Spec Files

Edit each file in `<ProjectName>/`. Delete `DATABASE.md` or `UI.md` if not applicable.
Rename `SCREEN-Example.md` → `SCREEN-<Name>.md` and `FEATURE-Example.md` → `FEATURE-<Name>.md`.

**Conventions:**

| Rule | Detail |
|------|--------|
| `## Open Questions` | Required at end of all files except `README.md`, `METADATA.md`, `INTENT.md` |
| SCREEN files | `SCREEN-<Name>.md` — route, layout, columns, interactions |
| FEATURE files | `FEATURE-<Name>.md` — trigger, sequence, reads, writes |
| Spec style | Write concise specs: tables, bullets, short descriptions. `CONVERT.md` rules expand them. |
| Stack patterns | Do not repeat stack patterns in specs — they come from `GLOBAL_RULES/stack/` |

---

## Step 3 — Validate

```bash
bash bin/validate.sh <ProjectName>    # from repo root
bash bin/validate.sh                  # from within the project directory
bash bin/validate.sh <ProjectName> --verbose
```

Exit 0 = ready to build. Exit 1 = errors (must fix before proceeding).

**Checks:**

| Check | Condition |
|-------|-----------|
| Required files | `METADATA.md`, `README.md`, `INTENT.md`, `ARCHITECTURE.md` |
| METADATA fields | `name`, `display_name`, `short_description`, `status` must be set |
| Status value | Must be one of: `IDEA` `PROTOTYPE` `ACTIVE` `PRODUCTION` `ARCHIVED` |
| INTENT.md | Must have content — not the template placeholder |
| Naming | Spec files must use `SCREEN-*` or `FEATURE-*` prefix |
| Template cleanup | `SCREEN-Example.md` and `FEATURE-Example.md` must not remain |
| Open Questions | All applicable files must have `## Open Questions` section |
| Stack files | If `stack:` declared in METADATA.md, `GLOBAL_RULES/stack/<component>.md` must exist |

---

## Step 4 — Convert (Optional)

```bash
bash bin/convert.sh <ProjectName> > convert-prompt.md
bash bin/convert.sh                > convert-prompt.md    # from within project directory
```

Generates an expansion prompt: `CONVERT.md` rules + stack reference files + concise spec files.
Feed `convert-prompt.md` to an AI agent to produce expanded, implementation-ready specs.
Replace concise spec files with the expanded versions, then proceed to Step 5.

> This step is optional. `build.sh` includes `CONVERT.md` inline — the AI can expand during build.

---

## Step 5 — Build

```bash
bash bin/build.sh <ProjectName> > build-prompt.md
bash bin/build.sh               > build-prompt.md    # from within project directory
```

Creates an annotated git tag `build/<ProjectName>/YYYY-MM-DD.N` and generates a complete build prompt.
Feed `build-prompt.md` to an AI agent to build the application.

**Flags:**

| Flag | Effect |
|------|--------|
| `--no-tag` | Generate prompt without creating a git tag |
| `--tag-only` | Tag the current commit without generating a prompt |

**Build tags** are annotated git objects — not pruned by `git gc`.

```bash
git tag -l "build/<Project>/*"                                                # list all build tags
git show build/<Project>/2026-03-20.1                                         # inspect a tag
git diff build/<Project>/2026-03-19.1..build/<Project>/2026-03-20.1 -- <Project>/  # compare specs
git checkout build/<Project>/2026-03-19.1 -- <Project>/DATABASE.md           # restore one file
```

---

## Step 6 — Iterate

Edit spec files → re-validate → re-build. Repeat until the build prompt produces the desired result.

---

## Step 7 — Promote

When the application works, promote the spec directory to its own repository:

```bash
cp -r Specifications/<ProjectName> ~/projects/<ProjectName>
cd ~/projects/<ProjectName>
git init && git add -A && git commit -m "Initial spec"
git remote add origin <url>
```

The spec directory becomes the project's authoritative specification.
Run `python3 bin/create_project.py <ProjectName>` from `Specifications/` to scaffold the code project.
