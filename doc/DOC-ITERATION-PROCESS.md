# Iteration Process

**Version:** 20260323 V4
**Description:** How to build and iterate a oneshot prototype

---

## The Process

**Initial build:**
```
Specifications/<PROJECT>/  ──[oneshot.sh]──►  <PROJECT>_prototype/  +  SCORECARD.md
```

**Iteration loop:**
```
Specifications/<PROJECT>/        ──[iterate.sh]──►  iterate-prompt.md
  IDEAS.md                                                │
  ACCEPTANCE_CRITERIA.md                                  ▼
  REFERENCE_GAPS.md                            <PROJECT>_prototype/  +  SCORECARD.md
```

---

## Step 1 — Build the Prototype

```bash
# From Specifications/
bash bin/oneshot.sh <PROJECT> > <PROJECT>/oneshot-prompt.md

mkdir -p /mnt/c/Users/barlo/projects/<PROJECT>_prototype
cd /mnt/c/Users/barlo/projects/<PROJECT>_prototype
git init && git checkout -b main
claude .
# paste <PROJECT>/oneshot-prompt.md
```

The prototype is built. A `SCORECARD.md` is written at the end of the session.

---

## Step 2 — Update the Specification

After testing the prototype, record feedback in `Specifications/<PROJECT>/`:

| File | What goes here |
|------|----------------|
| `IDEAS.md` | Raw thoughts, one bullet per line — no format required |
| `ACCEPTANCE_CRITERIA.md` | MUST/MUST NOT statements (testable behavior requirements) |
| `REFERENCE_GAPS.md` | Missing features — one unchecked checkbox per gap, with priority [P0]–[P4] |

Edit these files directly, or say **"process ideas"** in Claude Code inside the prototype — it routes `IDEAS.md` entries to the right files automatically.

---

## Step 3 — Run iterate.sh

```bash
# From Specifications/
bash bin/iterate.sh <PROJECT> > <PROJECT>/iterate-prompt.md

# Then in the prototype directory:
cd /mnt/c/Users/barlo/projects/<PROJECT>_prototype
claude .
# paste <PROJECT>/iterate-prompt.md
```

The iterate prompt includes: current Specification files, IDEAS.md, ACCEPTANCE_CRITERIA.md, REFERENCE_GAPS.md, and the latest SCORECARD.md.

Repeat Steps 2–3 until the scorecard passes.

---

## Trigger Phrases (in Claude Code, prototype directory)

| Say | Claude does |
|-----|------------|
| `process ideas` | IDEAS.md → routes each entry to the right file, deletes after routing |
| `this is a gap` | Adds entry to REFERENCE_GAPS.md |
| `add acceptance criteria` | Adds MUST statement to ACCEPTANCE_CRITERIA.md |
| `update the specification` | Reviews recent changes, updates Specification files |

---

## Auto-Updates

Every prototype's `AGENTS.md` contains iteration rules from `RulesEngine/CLAUDE_PROTOTYPE_RULES.md`.
When Claude fixes code in the prototype, it automatically:

- Updates the corresponding Specification file
- Adds acceptance criteria for the bug
- Checks off the gap in REFERENCE_GAPS.md

---

## Extracting Feedback from Sessions

After a prototype session, run to update the feedback files automatically:

```bash
bash bin/extract_session_feedback.sh <PROJECT>
```

Uses haiku via `claude -p` — reads recent prototype changes and updates IDEAS.md, ACCEPTANCE_CRITERIA.md, REFERENCE_GAPS.md in `Specifications/<PROJECT>/`.

---

## Priority Levels

| Level | Meaning |
|-------|---------|
| P0 | Blocks other work — fix immediately |
| P1 | Core feature missing |
| P2–P3 | Should have |
| P4+ | Backlog |
