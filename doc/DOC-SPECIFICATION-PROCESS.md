# Specification Process

**Version:** 20260322 V6
**Description:** Step-by-step guide to the Prototyper specification workflow

Prototyper converts concise specification files into AI agent build prompts.

---

## Step 1 — Setup the Prototype Directory

```bash
bash bin/setup.sh <ProjectName>
```

Creates `Specifications/<ProjectName>/` with template files from `RulesEngine/spec_template/`.

Edit `METADATA.md` immediately — set `name`, `display_name`, `short_description`, `status`.
Set `git_repo:` only if the project has a remote git repository to clone from.

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
| Required files | `METADATA.md`, `README.md`, `ARCHITECTURE.md` exist |
| METADATA fields | `name`, `display_name`, `short_description`, `status` are all set |
| Naming | Spec files use `SCREEN-*` or `FEATURE-*` prefix |
| Template cleanup | `SCREEN-Example.md` and `FEATURE-Example.md` have been renamed or deleted |
| Open Questions | All applicable files have `## Open Questions` section |
| Stack files | If `stack:` is declared, `RulesEngine/stack/<component>.md` exists for each component |
| Build target | Shown as INFO: "New build" or "Update build" based on whether target directory exists |
| Feature Branch | If `BUILD_FEATURE_BRANCH_NAME` is set in `.env`, shown as PASS — required only for Feature Branch mode |

---

## Step 4 — OneShot Build

```bash
bash bin/oneshot.sh <ProjectName> > oneshot-prompt.md
```

Validates the spec, detects build mode, then generates the build prompt.

### Mode A — Bootstrap (new project, no git remote)

Used when `git_repo` is not set or `BUILD_FEATURE_BRANCH_NAME` is not configured.

```
bash bin/oneshot.sh <ProjectName> > oneshot-prompt.md
```

1. Validates the spec (fails if any errors)
2. Writes `<ProjectName>/bootstrap.sh` — absolute paths, `git init`, ready to run
3. Generates the build prompt to stdout

Then:

```bash
bash <ProjectName>/bootstrap.sh        # create target dir and git init
cd /path/to/projects/<ProjectName>
claude .                               # open Claude Code in target dir
# paste oneshot-prompt.md
```

### Mode B — Feature Branch (existing project with git remote)

Used when `git_repo` is set in `METADATA.md` AND `BUILD_FEATURE_BRANCH_NAME` is set in `.env`.

```bash
# In Specifications/<ProjectName>/.env:
BUILD_FEATURE_BRANCH_NAME=feature/my-feature-name
```

```bash
bash bin/oneshot.sh <ProjectName> > oneshot-prompt.md
```

1. Validates the spec (fails if any errors)
2. Clones `git_repo` into `../<ProjectName>/` if it does not exist, or fetches if it does
3. Creates `feature/<name>` branch from `base_branch` (configured or auto-detected)
4. Generates the build prompt to stdout

Then:

```bash
cd /path/to/projects/<ProjectName>
claude .                               # open Claude Code on feature branch
# paste oneshot-prompt.md
```

### Stub Policy

Any feature marked `[ROADMAP]` or underspecified is automatically stubbed by the agent:
- Real route/function returning a placeholder (not dead code)
- `# TODO: [stub] <what is needed>` comment inline
- `STUBS.md` written at project root listing every stub: file, line, description

---

## Update Builds

To apply spec changes to an existing project:

```bash
bash bin/oneshot.sh <ProjectName> --update > oneshot-prompt.md
```

Generates an update prompt — agent applies spec changes to existing code, does not rebuild from scratch.

---

## Full Command Reference

```bash
# New project (no git_repo / no feature branch):
bash bin/validate.sh <ProjectName>
bash bin/oneshot.sh <ProjectName> > oneshot-prompt.md
bash <ProjectName>/bootstrap.sh        # create target dir, git init
cd /mnt/c/Users/barlo/projects/<ProjectName> && claude .
# paste oneshot-prompt.md

# Existing project (git_repo + BUILD_FEATURE_BRANCH_NAME set):
bash bin/validate.sh <ProjectName>
bash bin/oneshot.sh <ProjectName> > oneshot-prompt.md   # clones/fetches, creates branch
cd /mnt/c/Users/barlo/projects/<ProjectName> && claude .
# paste oneshot-prompt.md

# Update existing project with spec changes:
bash bin/oneshot.sh <ProjectName> --update > oneshot-prompt.md
# open Claude Code in project dir, paste prompt
```
