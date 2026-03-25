# Iteration Process

**Version:** 20260324 V7
**Specification:** `RulesEngine/PROTOTYPE_PROCESS.md`

> The authoritative process spec is `RulesEngine/PROTOTYPE_PROCESS.md`.
> This document covers the commands you run at each step.

---

## Build (first time)

```bash
# From Specifications/
bash bin/oneshot.sh <PROJECT> > <PROJECT>/oneshot-prompt.md

mkdir -p /mnt/c/Users/barlo/projects/<PROJECT>
cd /mnt/c/Users/barlo/projects/<PROJECT>
git init && git checkout -b main
claude .
# paste <PROJECT>/oneshot-prompt.md
```

`oneshot.sh` tags the commit, writes `PROTOTYPE_BUILD_TAG`, `PROTOTYPE_BUILD_COMMIT`,
and `PROTOTYPE_DIR` to `<PROJECT>/.env`, and appends to `DEPLOY_LOG.md`.

---

## Iterate (each change cycle)

**Step 1 — Express changes:**

| Change type | What to create |
|-------------|---------------|
| New screen / feature / UI component | `SCREEN-Name.md`, `FEATURE-Name.md`, `UI-Name.md` |
| Mutation to existing spec | `changes/CHANGE-NNN-description.md` |
| From interactive session | `bash bin/tran_logger.sh <PROJECT>` → creates `CHANGE-NNN-tl-*.md` |

**Step 2 — Generate prompt:**
```bash
# From Specifications/
bash bin/iterate.sh <PROJECT> > <PROJECT>/iterate-prompt.md
```

**Step 3 — Apply:**
```bash
cd /mnt/c/Users/barlo/projects/<PROJECT>
claude -p "$(cat /mnt/c/Users/barlo/projects/Specifications/<PROJECT>/iterate-prompt.md)"
```

The LLM validates each item, applies or rejects, then writes `SCORECARD.md`
with a KPI table (completion %, pending tickets, P0/P1 gaps, open questions).

Repeat Steps 1–3 until prototype matches specification.

---

## Capture Interactive Sessions

After any interactive prototype session, run from `Specifications/`:

```bash
bash bin/tran_logger.sh <PROJECT>
```

Reads new Claude Code session logs (cursor prevents reprocessing) and produces:
- `changes/CHANGE-NNN-tl-*.md` — auto-generated mutation tickets (`tl-` prefix)
- `ACCEPTANCE_CRITERIA.md` — appended MUST/MUST NOT statements
- `IDEAS.md` — appended fuzzy observations

Review, edit or delete noise, then run iterate.

---

## CHANGE Ticket Format

```markdown
# Change: 001 — Short description
**Status:** pending
**Type:** mutation
**Scope:** affected files or areas

## Intent
Why this change is needed.

## Changes Required
- Specific instruction
- Another instruction

## Open Questions
None.
```

**Status:** `pending` → `applied` (LLM) | `rejected` (LLM, adds `## Rejection Reason`)

---

## Priority Levels (REFERENCE_GAPS.md)

| Level | Meaning |
|-------|---------|
| P0 | Blocks other work — fix immediately |
| P1 | Core feature missing |
| P2–P3 | Should have |
| P4+ | Backlog |
