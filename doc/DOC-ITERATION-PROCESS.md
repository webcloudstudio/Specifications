# Iteration Process

**Version:** 20260323 V3
**Description:** How to update a oneshot prototype from specification feedback

---

## The Loop

```
Specs/<GAME>/IDEAS.md       ←  dump anything here, no format required
        ↓  tell Claude: "process ideas"
Specs/<GAME>/ updated       ←  ideas routed to REFERENCE_GAPS / ACCEPTANCE_CRITERIA / screen files
        ↓  bash bin/iterate.sh GAME > GAME/iterate-prompt.md
iterate-prompt.md           ←  paste into Claude Code inside the prototype directory
        ↓
code updated
spec files updated
SCORECARD.md regenerated
        ↓  test, find next issue → repeat
```

---

## Where Things Live

| File | Location | What goes here |
|------|----------|---------------|
| `IDEAS.md` | `Specifications/GAME/` | Raw thoughts, one bullet per line |
| `ACCEPTANCE_CRITERIA.md` | `Specifications/GAME/` | MUST/MUST NOT statements, auto-checked |
| `REFERENCE_GAPS.md` | `Specifications/GAME/` | Missing features, one checkbox per gap |
| `SCORECARD.md` | `GAME_prototype/` | Generated — failing checks = work to do |

`Build-ref: oneshot/GAME/2026-03-22.1` in ACCEPTANCE_CRITERIA.md and REFERENCE_GAPS.md
links the feedback to the specific build it came from.

---

## Priorities

P0 = blocks other work. P1 = core feature missing. P2–P3 = should have. P4+ = backlog.

---

## Commands

```bash
# From Specifications/ directory:
bash bin/iterate.sh GAME > GAME/iterate-prompt.md
# Then paste iterate-prompt.md into Claude Code in the GAME_prototype/ directory

# Scorecard only (no prompt):
bash bin/scorecard.sh GAME
```

---

## Trigger Phrases (in Claude Code, prototype directory)

| Say | Claude does |
|-----|------------|
| `process ideas` | IDEAS.md → routes to spec files, deletes processed entries |
| `this is a gap` | Adds entry to REFERENCE_GAPS.md |
| `add acceptance criteria` | Adds MUST statement to ACCEPTANCE_CRITERIA.md |
| `update the specification` | Reviews recent changes, updates spec files |

---

## Auto-Updates

Every oneshot prototype's `AGENTS.md` contains iteration rules injected from
`RulesEngine/CLAUDE_PROTOTYPE_RULES.md`. When Claude fixes code in the prototype
directory, it automatically:

- Updates the corresponding spec file
- Adds acceptance criteria for the bug
- Checks off the gap in REFERENCE_GAPS.md

No prompt needed — it's part of AGENTS.md.
