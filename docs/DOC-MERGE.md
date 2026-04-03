# Step 4 — Merge

Promote a prototype to a project by squash-merging its feature branch into the base branch.

## What Happens

`merge.sh` collapses all feature branch commits into a single clean commit on the
base branch, then deletes the feature branch. The prototype becomes a project.

```bash
bash bin/merge.sh MyProject
bash bin/merge.sh MyProject --dry-run    # preview without merging
```

Reads the feature branch from `.env` and the base branch from `METADATA.md`.

## After Merge

Validate the promoted project against platform compliance rules:

```bash
bash bin/ProjectValidate.sh MyProject
```

This checks conformity by maturity level (IDEA, PROTOTYPE, ACTIVE, PRODUCTION)
and shows what the next level requires.

Keep the project current with the latest rules and templates:

```bash
bash bin/ProjectUpdate.sh MyProject
```

This injects the latest `CLAUDE_RULES.md` into the project's `AGENTS.md` and
copies updated template files.
