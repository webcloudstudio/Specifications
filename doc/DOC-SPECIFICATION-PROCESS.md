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

Generates the complete build prompt. Validates the spec first — fails if any errors.

```bash
bash bin/oneshot.sh <ProjectName> > <ProjectName>/oneshot-prompt.md
```

The prompt is self-contained: CONVERT.md + CLAUDE_RULES.md + stack files + all spec files.
Paste it into Claude Code with no other instructions needed.

---

### New project (no git remote)

```bash
# 1. Generate the prompt
bash bin/oneshot.sh <ProjectName> > <ProjectName>/oneshot-prompt.md

# 2. Create and initialize the build directory
mkdir -p /mnt/c/Users/barlo/projects/<ProjectName>
cd /mnt/c/Users/barlo/projects/<ProjectName>
git init && git checkout -b main

# 3. Open Claude Code and paste the prompt
claude .
# paste <ProjectName>/oneshot-prompt.md
```

---

### Feature Branch (git_repo + BUILD_FEATURE_BRANCH_NAME set)

Set in `Specifications/<ProjectName>/.env`:
```
BUILD_FEATURE_BRANCH_NAME=feature/my-feature-name
```

```bash
# 1. Generate the prompt — also clones/fetches project and creates the branch
bash bin/oneshot.sh <ProjectName> > <ProjectName>/oneshot-prompt.md

# 2. Open Claude Code on the feature branch and paste the prompt
cd /mnt/c/Users/barlo/projects/<ProjectName>
claude .
# paste <ProjectName>/oneshot-prompt.md
```

---

### Update (apply spec changes to existing code)

```bash
bash bin/oneshot.sh <ProjectName> --update > <ProjectName>/oneshot-prompt.md
# open Claude Code in project dir, paste prompt
```

---

### Stub Policy

Any feature marked `[ROADMAP]` or underspecified is automatically stubbed by the agent:
- Real route/function returning a placeholder (not dead code)
- `# TODO: [stub] <what is needed>` comment inline
- `STUBS.md` at project root listing every stub: file, line, description
