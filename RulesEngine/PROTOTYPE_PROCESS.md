# Prototype Process Specification

**Version:** 20260324 V1
**Authority:** This file is the single definitive reference for the prototype build and iteration workflow.

---

## States

| State | Description | Entry Artifact |
|-------|-------------|----------------|
| `DRAFT` | Spec directory created, files being written | `setup.sh` run |
| `VALIDATED` | Spec passes all checks, ready to build | `validate.sh` exit 0 |
| `BUILT` | Prompt generated; prototype directory targeted | `oneshot.sh` run |
| `ITERATING` | Active iteration cycle; pending work exists | `iterate.sh` run |
| `PROMOTED` | Code merged into main branch or pushed to independent repo | `merge.sh` run |

---

## Transitions

| Transition | Script | From | To | Writes |
|-----------|--------|------|----|--------|
| Scaffold spec | `bin/setup.sh <Name>` | — | DRAFT | spec dir with template files, `changes/` |
| Validate spec | `bin/validate.sh <Name>` | DRAFT | VALIDATED | exit 0 = ready |
| Build prompt | `bin/oneshot.sh <Name> > Name/prompt.md` | VALIDATED | BUILT | git tag, `.env` (TAG, COMMIT, DIR), `DEPLOY_LOG.md` |
| Apply build | `claude -p "$(cat Name/prompt.md)"` *(in prototype dir)* | BUILT | ITERATING | prototype code, `SCORECARD.md` |
| Capture session | `bin/tran_logger.sh <Name>` | ITERATING | ITERATING | `changes/CHANGE-NNN-tl-*.md`, `ACCEPTANCE_CRITERIA.md`, `IDEAS.md` |
| Generate iterate | `bin/iterate.sh <Name> > Name/iterate-prompt.md` | ITERATING | ITERATING | `iterate-prompt.md`, `.env` (DIR), `DEPLOY_LOG.md` |
| Apply iterate | `claude -p "$(cat Name/iterate-prompt.md)"` *(in prototype dir)* | ITERATING | ITERATING | updated code, `SCORECARD.md` |
| Promote | `bin/merge.sh <Name>` | ITERATING | PROMOTED | squash commit on base branch |

---

## Artifacts

| File | Location | Created By | Purpose |
|------|----------|-----------|---------|
| `METADATA.md` | spec dir | `setup.sh` | Project identity: name, stack, port, status |
| `ARCHITECTURE.md` | spec dir | author | Code organization; always included in iterate prompt |
| `SCREEN-*.md` | spec dir | author | Per-screen specification |
| `FEATURE-*.md` | spec dir | author | Cross-cutting behavior specification |
| `UI-*.md` | spec dir | author | Reusable UI component specification |
| `ACCEPTANCE_CRITERIA.md` | spec dir | author / `tran_logger.sh` | Testable MUST/MUST NOT requirements |
| `IDEAS.md` | spec dir | author / `tran_logger.sh` | Fuzzy observations; process on request |
| `REFERENCE_GAPS.md` | spec dir | author | Unspecified features by priority (P0–P4) |
| `DEPLOY_LOG.md` | spec dir | `oneshot.sh` / `iterate.sh` | Record of every build and iterate run |
| `.env` | spec dir | `oneshot.sh` / `iterate.sh` | `PROTOTYPE_BUILD_TAG`, `PROTOTYPE_BUILD_COMMIT`, `PROTOTYPE_DIR` |
| `.tran_logger_cursor` | spec dir | `tran_logger.sh` | Processed session file basenames (idempotency) |
| `changes/CHANGE-NNN-*.md` | `changes/` | author | Human-authored mutation tickets |
| `changes/CHANGE-NNN-tl-*.md` | `changes/` | `tran_logger.sh` | Auto-generated mutation tickets (`tl-` = tran_logger) |
| `Name/prompt.md` | spec dir | `oneshot.sh` | Full build prompt for initial prototype creation |
| `Name/iterate-prompt.md` | spec dir | `iterate.sh` | Focused iteration prompt |
| `SCORECARD.md` | prototype dir | LLM (during apply) | KPI table + per-item PASS/FAIL/PARTIAL results |

---

## Iteration Cycle (steady state)

```
author edits spec  ──►  validate.sh  ──►  iterate.sh  ──►  claude -p iterate-prompt.md
       ▲                                                              │
       │                         tran_logger.sh  ◄────────────────── │
       └───────────────────────── review tickets ◄───────────────────┘
```

1. Edit spec files (canonical truth — always edit spec, never code directly for tracked changes)
2. For mutations: create `changes/CHANGE-NNN-description.md` (or let tran_logger create them)
3. Run `bin/iterate.sh <Name>` → writes `Name/iterate-prompt.md`
4. Run `claude -p "$(cat Name/iterate-prompt.md)"` from prototype directory
5. LLM validates each item, applies accepted, rejects underspecified with explanation
6. LLM writes `SCORECARD.md` (KPI table + results)
7. After interactive sessions: run `bin/tran_logger.sh <Name>` to capture changes as tickets

---

## CHANGE Ticket Lifecycle

```
pending  ──►  applied   (LLM marks after successful implementation)
         ──►  rejected  (LLM marks with ## Rejection Reason if underspecified)
```

**Human tickets:** `CHANGE-NNN-description.md`
**Auto tickets:** `CHANGE-NNN-tl-description.md` (created by `tran_logger.sh`)

Both types are processed identically by `iterate.sh`. The `tl-` prefix is visual only.

---

## Validation Protocol (enforced by iterate.sh)

Before implementing any item, the LLM checks:
1. Intent / description is concrete (not vague)
2. Changes Required are unambiguous
3. `## Open Questions` exists and is empty or `None.`
4. No placeholder text: `TODO`, `TBD`, `[placeholder]`

Failure → `[UNDERSPECIFIED]` label, status set to `rejected`, no code changes for that item.

---

## Scorecard KPIs (written by LLM after each iterate session)

| Metric | Source |
|--------|--------|
| Completion (this session) | applied / attempted × 100% |
| Pending tickets remaining | count `**Status:** pending` in `changes/CHANGE-*.md` |
| P0/P1 reference gaps | count P0/P1 lines in `REFERENCE_GAPS.md` |
| Unresolved open questions | count non-`None.` bullets in `## Open Questions` across spec files |

---

## Rules

1. **Fix code, then fix the spec.** Every code change that reveals a gap must produce an AC entry or spec update in the same session.
2. **Spec files are canonical truth.** Never modify prototype code for tracked changes without a ticket or spec change.
3. **Tickets before iterate.** Run `tran_logger.sh` after any interactive prototype session before the next `iterate.sh` run.
4. **Validate before building.** `oneshot.sh` runs `validate.sh` automatically and aborts on failure.
5. **Open Questions block builds.** Any spec file with unresolved Open Questions will have its items rejected during iterate.
6. **`tl-` tickets are auto-generated.** Review them before running iterate — edit, delete, or promote to human tickets as needed.
7. **Cursor prevents duplicates.** `tran_logger.sh` is safe to run at any time; the `.tran_logger_cursor` file tracks processed sessions.
8. **Documentation lives in `docs/`.** All prototype documentation paths use `docs/`, never `doc/`.
9. **Unix line endings.** All `bin/` scripts must use LF. Windows line endings cause failures in WSL.
