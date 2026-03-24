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

**Updating an existing prototype** — when the spec changes and you want to apply those changes without rebuilding from scratch:

```
bash bin/oneshot.sh <ProjectName> --update > <ProjectName>/prompt.md
```

Open Claude Code in the existing prototype directory and paste the prompt. The agent reads the spec changes and applies them to the existing code.

---

## Step 5 — Iterate

Edit spec files in `Specifications/<ProjectName>/` to reflect the changes you want, then run:

```bash
bash bin/iterate.sh <ProjectName> > <ProjectName>/iterate-prompt.md
cd /mnt/c/Users/barlo/projects/<ProjectName>
claude -p "$(cat /mnt/c/Users/barlo/projects/Specifications/<ProjectName>/iterate-prompt.md)"
```

`iterate.sh` diffs the spec directory against the previous `PROTOTYPE_BUILD_TAG` and emits only the changed spec files plus `ACCEPTANCE_CRITERIA.md`. The agent applies those changes to the existing code — it does not rebuild from scratch. `claude -p` uses your Claude subscription (not API tokens).

Repeat until the prototype matches the spec.

**Transaction log:** After each prototype session, run to extract bugs and ideas from the session log:

```
bash bin/tran_logger.sh <ProjectName>
```

Reads the Claude Code session log and recent git history. Writes discovered items to `IDEAS.md` and `ACCEPTANCE_CRITERIA.md`. Review the output and update the relevant spec files before running iterate.sh.

Every prototype's `AGENTS.md` contains iteration rules from `RulesEngine/CLAUDE_PROTOTYPE.md`.
These rules auto-update Specification files when the agent fixes code.

---

## Step 6 — Promote

When the prototype passes its scorecard, merge it into the main branch.

For Feature Branch mode: squash-merge the feature branch into the base branch via `bin/merge.sh` or manually.
For new-project (no branch): the prototype directory IS the project — push to a remote when ready.

Promoted projects are discovered by the Prototyper platform and must conform to `CLAUDE_RULES.md`.
Run `bin/ProjectValidate.sh <project>` to check compliance.
Run `ProjectUpdate.sh <project>` to inject the latest rules and templates.
