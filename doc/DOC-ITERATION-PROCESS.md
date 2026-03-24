# Iteration Process

**Version:** 20260324 V5
**Description:** How to build and iterate a oneshot prototype

---

## The Process

**Initial build:**
```
Specifications/<PROJECT>/  ──[oneshot.sh]──►  <PROJECT>/  (prototype)
```

**Iteration loop:**
```
Edit spec files  ──[iterate.sh]──►  iterate-prompt.md  ──[claude -p]──►  <PROJECT>/  (prototype updated)
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

## Step 2 — Update the Specification

Edit spec files in `Specifications/<PROJECT>/` to reflect the changes you want. You decide what changes — the agent applies them exactly as written.

Update `ACCEPTANCE_CRITERIA.md` with any hard requirements the prototype must satisfy.

---

## Step 3 — Run iterate.sh

```bash
# From Specifications/
bash bin/iterate.sh <PROJECT> > <PROJECT>/iterate-prompt.md
```

```bash
# From the prototype directory (printed by iterate.sh to stderr)
cd /mnt/c/Users/barlo/projects/<PROJECT>
claude -p "$(cat /mnt/c/Users/barlo/projects/Specifications/<PROJECT>/iterate-prompt.md)"
```

`iterate.sh` diffs the specification directory against `PROTOTYPE_BUILD_TAG`, emits only the changed specification files plus `ACCEPTANCE_CRITERIA.md`, `IDEAS.md`, and `REFERENCE_GAPS.md`. The agent applies those changes to the existing code — it does not rebuild from scratch.

`claude -p` uses your Claude subscription (not API tokens). Run it from the prototype directory so the agent can read the existing code.

Repeat Steps 2–3 until the prototype matches the specification.

---

## Transaction Log

After a prototype session, run to extract bugs and ideas from the session log:

```
bash bin/tran_logger.sh <PROJECT>
```

Reads the Claude Code session transaction log and recent git history. Writes discovered bugs and ideas to `IDEAS.md` and `ACCEPTANCE_CRITERIA.md` in `Specifications/<PROJECT>/`. Review and edit the output — then update the relevant spec files before running iterate.sh.

---

## Priority Levels

| Level | Meaning |
|-------|---------|
| P0 | Blocks other work — fix immediately |
| P1 | Core feature missing |
| P2–P3 | Should have |
| P4+ | Backlog |
