# Iteration Process

**Version:** 20260324 V6
**Description:** How to build and iterate a oneshot prototype using the ticket-based workflow

---

## The Process

**Initial build:**
```
Specifications/<PROJECT>/  ──[oneshot.sh]──►  <PROJECT>/  (prototype + SCORECARD.md)
```

**Iteration loop:**
```
New spec files + CHANGE tickets  ──[iterate.sh]──►  iterate-prompt.md  ──[claude -p]──►  prototype updated + SCORECARD.md
```

---

## Step 1 — Build the Prototype

```bash
# From Specifications/
bash bin/oneshot.sh <PROJECT> > <PROJECT>/oneshot-prompt.md

mkdir -p /mnt/c/Users/barlo/projects/<PROJECT>
cd /mnt/c/Users/barlo/projects/<PROJECT>
git init && git checkout -b main
claude .
# paste <PROJECT>/oneshot-prompt.md
```

`oneshot.sh` tags the current commit (`oneshot/<PROJECT>/<date>.<n>`) and writes `PROTOTYPE_BUILD_TAG` and `PROTOTYPE_BUILD_COMMIT` to `<PROJECT>/.env`. These are the baseline for all subsequent iterations.

---

## Step 2 — Express Changes as Artifacts

Two kinds of spec changes — both live in `Specifications/<PROJECT>/`:

**New artifacts** (new feature, screen, or UI component):
Create `FEATURE-Name.md`, `SCREEN-Name.md`, or `UI-Name.md`. Fill in all required sections. Set `## Open Questions` to `None.` when ready.

**Mutations** (change to existing spec):
Create a CHANGE ticket in `changes/CHANGE-NNN-description.md`:

```markdown
# Change: 001 — Fix documentation path
**Status:** pending
**Type:** mutation
**Scope:** Scanner, Portfolio builder, ARCHITECTURE.md

## Intent
The docs/ directory was renamed from doc/. All prototype references to
doc/index.html must become docs/index.html.

## Changes Required
- Scanner has_docs flag: check for docs/index.html not doc/index.html
- Portfolio builder: check docs/index.html for documentation link
- Flask doc proxy route: detection logic only, not route pattern

## Open Questions
None.
```

**Status values:** `pending` | `applied` (set by LLM) | `rejected` (set by LLM with reason)

---

## Step 3 — Run iterate.sh

```bash
# From Specifications/
bash bin/iterate.sh <PROJECT> > <PROJECT>/iterate-prompt.md
```

```bash
# Run from the prototype directory (path printed by iterate.sh to stderr)
cd /mnt/c/Users/barlo/projects/<PROJECT>
claude -p "$(cat /mnt/c/Users/barlo/projects/Specifications/<PROJECT>/iterate-prompt.md)"
```

`iterate.sh` emits: pending CHANGE tickets + new FEATURE/SCREEN/UI files + ARCHITECTURE.md + AC + IDEAS + REFERENCE_GAPS. Does not include CLAUDE_RULES.md or stack files (already in prototype's AGENTS.md).

The LLM **validates each item** before touching code. Underspecified items are rejected with explanation — `**Status:** rejected` is written to the ticket and a `## Rejection Reason` section is added. Accepted items get `**Status:** applied`. After all items, the LLM writes `SCORECARD.md`.

`claude -p` uses your Claude subscription (not API tokens). Run it from the prototype directory so the agent can read the existing code.

Repeat Steps 2–3 until the prototype matches the specification.

---

## Capturing Changes from Interactive Sessions

After any interactive prototype session (debugging, exploration):

```bash
bash bin/tran_logger.sh <PROJECT>
```

Reads the Claude Code session log and recent git history. Classifies findings into:
- **CHANGE tickets** → `changes/CHANGE-NNN-description.md` (for concrete code changes)
- **ACCEPTANCE_CRITERIA.md** → behavioral MUST/MUST NOT statements
- **IDEAS.md** → fuzzy observations not yet actionable

Review the output, then run iterate.sh.

---

## Priority Levels (REFERENCE_GAPS.md)

| Level | Meaning |
|-------|---------|
| P0 | Blocks other work — fix immediately |
| P1 | Core feature missing |
| P2–P3 | Should have |
| P4+ | Backlog |
