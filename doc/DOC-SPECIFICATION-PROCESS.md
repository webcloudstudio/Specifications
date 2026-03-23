# Specification Process

**Version:** 20260323 V7
**Description:** Six-step process for building a prototype with the Prototyper system

---

## Step 1 — Setup

Create a new Specifications directory from templates.

`bin/setup.sh <ProjectName>` scaffolds `Specifications/<ProjectName>/` from `RulesEngine/spec_template/`.
Edit `METADATA.md` immediately — set `name`, `display_name`, `short_description`, `status`.
Set `git_repo:` only if the project already has a remote git repository to clone from.

---

## Step 2 — Create

Write the Specification files in `Specifications/<ProjectName>/`.
Delete `DATABASE.md` or `UI.md` if not applicable.
Rename `SCREEN-Example.md` and `FEATURE-Example.md` to real names before Step 3.

| Convention | Rule |
|------------|------|
| Scope | Concise: tables, bullets, short descriptions. Expansion rules are in `ONESHOT_BUILD_RULES.md`. |
| Screens | `SCREEN-<Name>.md` — route, layout, columns, interactions |
| Features | `FEATURE-<Name>.md` — trigger, sequence, reads, writes |
| End section | All files except `README.md`, `METADATA.md`, `INTENT.md` must end with `## Open Questions` |
| Stack | Do not repeat stack patterns — they come from `RulesEngine/stack/` |

---

## Step 3 — Validate

`bin/validate.sh <ProjectName>` checks the Specifications directory. Exit 0 = ready. Exit 1 = errors to fix.

| Check | Condition |
|-------|-----------|
| Required files | `METADATA.md`, `README.md`, `ARCHITECTURE.md` exist |
| METADATA fields | `name`, `display_name`, `short_description`, `status` are all set |
| Naming | Specification files use `SCREEN-*` or `FEATURE-*` prefix |
| Template cleanup | `SCREEN-Example.md` and `FEATURE-Example.md` have been renamed or deleted |
| Open Questions | All applicable files have `## Open Questions` section |
| Stack files | If `stack:` is declared, `RulesEngine/stack/<component>.md` exists for each component |
| Build target | INFO: "New build" or "Update build" based on whether target directory exists |

---

## Step 4 — OneShot

`bin/oneshot.sh <ProjectName>` validates, detects mode, then generates a complete build prompt.

The prompt is self-contained: `ONESHOT_BUILD_RULES.md` + `CLAUDE_RULES.md` + stack files + all Specification files.
Paste it into Claude Code with no other instructions — the agent builds the complete application.

**New project (no git remote):** create the target directory manually, git init, open Claude Code, paste the prompt.

**Feature Branch (git_repo + BUILD_FEATURE_BRANCH_NAME set):** oneshot.sh clones/fetches the project and creates the branch before generating the prompt.

A `SCORECARD.md` is written to the prototype directory at the end of the build session.
The oneshot tag and prototype build reference are recorded in `Specifications/<ProjectName>/.env`.

---

## Step 5 — Iterate

Test the prototype, record feedback in `Specifications/<ProjectName>/`, then run `bin/iterate.sh <ProjectName>`.

`bin/iterate.sh` generates an iteration prompt containing the current Specification files, `IDEAS.md`, `ACCEPTANCE_CRITERIA.md`, `REFERENCE_GAPS.md`, and the latest `SCORECARD.md`.
Paste into Claude Code in the prototype directory. The agent fixes scorecard failures, closes gaps, and updates Specification files.

Repeat until the scorecard passes.

| File | Purpose |
|------|---------|
| `IDEAS.md` | Raw thoughts, one bullet per line |
| `ACCEPTANCE_CRITERIA.md` | MUST/MUST NOT statements — testable behavior requirements |
| `REFERENCE_GAPS.md` | Missing features — one unchecked checkbox per gap with priority [P0]–[P4] |

**Trigger phrases** (say these in Claude Code inside the prototype directory):

| Say | Claude does |
|-----|------------|
| `process ideas` | Routes each `IDEAS.md` entry to the right file, then clears it |
| `this is a gap` | Adds entry to `REFERENCE_GAPS.md` |
| `add acceptance criteria` | Adds MUST statement to `ACCEPTANCE_CRITERIA.md` |
| `update the specification` | Reviews recent changes, updates Specification files |

**Auto-extract feedback** from recent sessions (runs haiku via `claude -p`):

```
bash bin/extract_session_feedback.sh <ProjectName>
```

Every prototype's `AGENTS.md` contains iteration rules from `RulesEngine/CLAUDE_PROTOTYPE.md`.
These rules auto-update Specification files and REFERENCE_GAPS.md when the agent fixes code.

---

## Step 6 — Promote

When the prototype passes its scorecard, merge it into the main branch.

For Feature Branch mode: squash-merge the feature branch into the base branch via `bin/merge.sh` or manually.
For new-project (no branch): the prototype directory IS the project — push to a remote when ready.

Promoted projects are discovered by the Prototyper platform and must conform to `CLAUDE_RULES.md`.
Run `bin/ProjectValidate.sh <project>` to check compliance.
Run `bin/ProjectUpdate.sh <project>` to inject the latest rules and templates.
