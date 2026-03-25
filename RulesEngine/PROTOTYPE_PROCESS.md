# Prototype Process Specification

**Version:** 20260324 V2
**Authority:** Single definitive reference for the prototype build and iteration workflow.

**Location convention used in this document:**
- `Specifications/<PROJECT>/` — specification files (this repo)
- `Prototype <PROJECT>/` — prototype code directory (`/mnt/c/Users/barlo/projects/<PROJECT>/`)

---

## States

| State | Description | Entry Condition |
|-------|-------------|-----------------|
| `DRAFT` | Spec directory exists, files being written | `setup.sh` run |
| `VALIDATED` | Spec passes all checks, ready to build | `validate.sh` exits 0 |
| `BUILT` | Build prompt generated; baseline tag set | `oneshot.sh` run |
| `ITERATING` | Prototype exists; changes are being applied | `iterate.sh` / `claude -p` cycle |
| `PROMOTED` | Code merged to main or in independent repo | `merge.sh` run |

---

## Transitions

| Transition | Command | From → To | Writes |
|-----------|---------|-----------|--------|
| Scaffold spec | `bin/setup.sh <PROJECT>` | — → DRAFT | `Specifications/<PROJECT>/` with template files and `changes/` |
| Validate | `bin/validate.sh <PROJECT>` | DRAFT → VALIDATED | exit 0 only |
| Generate build prompt | `bin/oneshot.sh <PROJECT> > Specifications/<PROJECT>/oneshot-prompt.md` | VALIDATED → BUILT | git tag `oneshot/<PROJECT>/<date>.<n>` · `Specifications/<PROJECT>/.env` · `DEPLOY_LOG.md` |
| Apply build | `cd Prototype <PROJECT> && claude -p "$(cat ...oneshot-prompt.md)"` | BUILT → ITERATING | `Prototype <PROJECT>/` code · `Prototype <PROJECT>/docs/SCORECARD.md` |
| Capture session | `bin/tran_logger.sh <PROJECT>` | ITERATING → ITERATING | `Specifications/<PROJECT>/changes/CHANGE-NNN-tl-*.md` · appends to `ACCEPTANCE_CRITERIA.md` · `IDEAS.md` |
| Generate iterate prompt | `bin/iterate.sh <PROJECT> > Specifications/<PROJECT>/iterate-prompt.md` | ITERATING → ITERATING | `Specifications/<PROJECT>/iterate-prompt.md` · `Specifications/<PROJECT>/.env` · `DEPLOY_LOG.md` |
| Apply iterate | `cd Prototype <PROJECT> && claude -p "$(cat ...iterate-prompt.md)"` | ITERATING → ITERATING | updated code · `Prototype <PROJECT>/docs/SCORECARD.md` |
| Promote | `bin/merge.sh <PROJECT>` | ITERATING → PROMOTED | squash commit on base branch |

---

## Baseline Tracking (`.env`)

`oneshot.sh` and `iterate.sh` write three values to `Specifications/<PROJECT>/.env` on every run.
`tran_logger.sh` and `iterate.sh` read these to locate the prototype.

| Key | Example | Set by |
|-----|---------|--------|
| `PROTOTYPE_BUILD_TAG` | `oneshot/GAME/2026-03-22.4` | `oneshot.sh` |
| `PROTOTYPE_BUILD_COMMIT` | `34c6af85a62e7b84aa83e35d61af0429819bee6` | `oneshot.sh` |
| `PROTOTYPE_DIR` | `/mnt/c/Users/barlo/projects/GAME` | `oneshot.sh` / `iterate.sh` |

`iterate.sh` diffs from `PROTOTYPE_BUILD_TAG` to find new spec files since the build.

---

## Artifacts

| File | Location | Created By | Purpose |
|------|----------|-----------|---------|
| `METADATA.md` | `Specifications/<PROJECT>/` | `setup.sh` | Identity: name, stack, port, status |
| `ARCHITECTURE.md` | `Specifications/<PROJECT>/` | author | Code organization; always included in iterate prompt |
| `SCREEN-*.md` | `Specifications/<PROJECT>/` | author | Per-screen specification |
| `FEATURE-*.md` | `Specifications/<PROJECT>/` | author | Cross-cutting behavior specification |
| `UI-*.md` | `Specifications/<PROJECT>/` | author | Reusable UI component specification |
| `ACCEPTANCE_CRITERIA.md` | `Specifications/<PROJECT>/` | author / `tran_logger.sh` | Testable MUST/MUST NOT requirements |
| `IDEAS.md` | `Specifications/<PROJECT>/` | author / `tran_logger.sh` | Fuzzy observations; process on request |
| `REFERENCE_GAPS.md` | `Specifications/<PROJECT>/` | `setup.sh` + author + LLM | Unspecified features by priority (P0–P4); LLM adds gaps found during build |
| `DEPLOY_LOG.md` | `Specifications/<PROJECT>/` | `oneshot.sh` / `iterate.sh` | Record of every build and iterate run with target directory |
| `.env` | `Specifications/<PROJECT>/` | `oneshot.sh` / `iterate.sh` | Baseline tracking: TAG, COMMIT, DIR (see above) |
| `.tran_logger_cursor` | `Specifications/<PROJECT>/` | `tran_logger.sh` | Processed session basenames — prevents duplicate processing |
| `changes/CHANGE-NNN-*.md` | `Specifications/<PROJECT>/changes/` | author | Human-authored mutation tickets |
| `changes/CHANGE-NNN-tl-*.md` | `Specifications/<PROJECT>/changes/` | `tran_logger.sh` | Auto-generated mutation tickets (`tl-` = tran_logger) |
| `oneshot-prompt.md` | `Specifications/<PROJECT>/` | author redirect (`>`) | Saved build prompt — optional, for reference |
| `iterate-prompt.md` | `Specifications/<PROJECT>/` | author redirect (`>`) | Saved iteration prompt — optional, for reference |
| `SCORECARD.md` | `Prototype <PROJECT>/docs/` | LLM (during apply) | KPI table + per-item PASS/FAIL/PARTIAL results |

---

## Engineering Reference Files

These files define HOW things are built (prescriptive patterns). They are included in `oneshot.sh` output.

| File | Location | Purpose |
|------|----------|---------|
| `CLAUDE_RULES.md` | `RulesEngine/` | Agent behavior contract — injected into every project's `AGENTS.md` |
| `ONESHOT_BUILD_RULES.md` | `RulesEngine/` | How to expand concise specs into implementation-ready code |
| `CLAUDE_PROTOTYPE.md` | `RulesEngine/` | Agent rules for working inside a prototype directory; injected into prototype `AGENTS.md` |
| `stack/<tech>.md` | `RulesEngine/stack/` | Prescriptive patterns per technology (flask, sqlite, bootstrap5, …) |

---

## Iteration Cycle (steady state)

```
edit Specifications/<PROJECT>/  ──►  iterate.sh  ──►  claude -p iterate-prompt.md  (in Prototype <PROJECT>/)
            ▲                                                        │
            │                  tran_logger.sh  ◄────────────────────│
            └───────────── review + edit tickets ◄──────────────────┘
```

1. Edit spec files — canonical truth; never code directly for tracked changes
2. For mutations: create `Specifications/<PROJECT>/changes/CHANGE-NNN-description.md`
   — or run `tran_logger.sh` after an interactive session to auto-generate them
3. `bin/iterate.sh <PROJECT> > Specifications/<PROJECT>/iterate-prompt.md`
4. `cd Prototype <PROJECT> && claude -p "$(cat ...iterate-prompt.md)"`
5. LLM validates each item → applies or rejects underspecified items
6. LLM writes `Prototype <PROJECT>/docs/SCORECARD.md`

---

## CHANGE Ticket Lifecycle

```
pending  ──►  applied   (LLM marks after implementation)
         ──►  rejected  (LLM marks; adds ## Rejection Reason section)
```

| Field | Human ticket | Auto ticket (`tl-`) |
|-------|-------------|-------------------|
| Filename | `CHANGE-NNN-description.md` | `CHANGE-NNN-tl-description.md` |
| `**Source:**` field | absent | `tran_logger` |
| Processing by `iterate.sh` | identical | identical |
| Review before iterate | required | required — edit, delete, or keep as-is |

---

## Validation Protocol (enforced by `iterate.sh`)

Before implementing any item the LLM checks:
1. Intent / description is concrete — not vague
2. Changes Required are unambiguous
3. `## Open Questions` exists and is empty or `None.`
4. No placeholder text: `TODO`, `TBD`, `[placeholder]`

Failure → item labeled `[UNDERSPECIFIED]`, status set to `rejected`, no code change.

---

## Scorecard KPIs

Written to `Prototype <PROJECT>/docs/SCORECARD.md` by LLM after each apply session.

| Metric | How computed |
|--------|-------------|
| Completion (this session) | applied / attempted × 100% |
| Pending tickets remaining | count `**Status:** pending` in `Specifications/<PROJECT>/changes/CHANGE-*.md` |
| P0/P1 reference gaps | count P0/P1 lines in `Specifications/<PROJECT>/REFERENCE_GAPS.md` |
| Unresolved open questions | count non-`None.` bullets in `## Open Questions` across `Specifications/<PROJECT>/` |

---

## Rules

1. **Spec is canonical truth.** Edit spec files; never modify prototype code for tracked changes without a ticket.
2. **Fix code, then fix spec.** Every code change revealing a gap must produce an AC entry or spec update in the same session.
3. **Tran_logger before iterate.** Run `tran_logger.sh` after any interactive prototype session before the next `iterate.sh` run.
4. **Validate before building.** `oneshot.sh` calls `validate.sh` and aborts on failure.
5. **Open Questions block items.** Unresolved Open Questions in a spec file cause its iterate items to be rejected.
6. **Review tl- tickets.** Auto-generated tickets must be reviewed before iterate — edit, delete, or promote as needed.
7. **Cursor prevents duplicates.** `tran_logger.sh` is safe to run at any time; `.tran_logger_cursor` tracks processed sessions.
8. **Prototype docs in `docs/`.** All prototype documentation including SCORECARD.md lives in `Prototype <PROJECT>/docs/`.
9. **Unix line endings.** All `bin/` scripts use LF. Windows line endings cause failures in WSL.
