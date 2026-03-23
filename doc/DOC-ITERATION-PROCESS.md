# Iteration Process

**Version:** 20260323 V2
**Description:** How to iterate a oneshot-built prototype back through specifications

After `oneshot.sh` produces a working prototype, this document defines the low-friction process for improving it: finding defects, closing gaps, adding features, and keeping specifications current.

---

## Principles

1. **Specifications are the source of truth.** Code is derived from specs. When code and specs disagree, fix the spec first, then rebuild or update the code.
2. **The spec directory drives iteration.** All iteration artifacts live in `Specifications/<ProjectName>/`, not in the prototype directory. The prototype gets only generated artifacts (STUBS.md, SCORECARD.md).
3. **Low friction beats high ceremony.** Dump ideas raw, process them later. One-line acceptance criteria beat no acceptance criteria.
4. **Claude updates specs when working on the prototype.** When fixing code in the prototype directory, Claude also updates the corresponding spec files. This is a rule, not a suggestion. Rules are injected via `CLAUDE_PROTOTYPE_RULES.md`.
5. **One active oneshot per project.** Only one oneshot build or update runs at a time per specification directory.
6. **All documentation uses `docs/` (not `doc/`).** There is no `doc/` directory in any project.

---

## Priority Levels

Used in REFERENCE_GAPS.md to triage work.

| Level | Meaning |
|-------|---------|
| P0 | Must have — blocks other work |
| P1 | Must have — core feature gap |
| P2 | Should have — important for quality |
| P3 | Should have — operational feature |
| P4 | Should have — testing/validation |
| P5 | Nice to have — analytics/intelligence |
| P6 | Nice to have — spec tooling |
| P7 | Nice to have — publishing polish |
| P8 | Someday — infrastructure |
| P9–P10 | Backlog |

---

## File Inventory

### In `Specifications/<ProjectName>/` (author-maintained)

| File | Purpose | Created by |
|------|---------|-----------|
| README.md | Project description + intent | Author, setup.sh |
| METADATA.md | Identity, stack, port, status | Author, setup.sh |
| ARCHITECTURE.md | Module organization, data flow | Author |
| DATABASE.md | Schema, field sources | Author |
| FUNCTIONALITY.md | End-to-end flows | Author |
| UI-GENERAL.md | Shared visual patterns | Author |
| SCREEN-*.md | Per-screen specification | Author |
| FEATURE-*.md | Cross-cutting behavior | Author |
| **IDEAS.md** | Raw unprocessed ideas (inbox) | Author, Claude |
| **ACCEPTANCE_CRITERIA.md** | Testable MUST/MUST NOT statements | Author, Claude |
| **REFERENCE_GAPS.md** | Features not yet specified, tracked by target file | Author, Claude, `bin/update_reference_gaps.sh` |

### In prototype directory (generated or auto-maintained)

| File | Purpose | Created by |
|------|---------|-----------|
| STUBS.md | Every `# TODO: [stub]` in the codebase | oneshot build |
| SCORECARD.md | Quality checklist vs spec | `bin/scorecard.sh` |
| METADATA.md | Synced from spec, editable from UI | oneshot build, scanner |
| AGENTS.md | Dev commands + CLAUDE_RULES + CLAUDE_PROTOTYPE_RULES | oneshot build |

**No TODO.md in prototype.** All planning lives in `Specifications/<ProjectName>/REFERENCE_GAPS.md`.

---

## Build Reference Tracking

Each iteration artifact includes a `Build-ref:` header noting the oneshot tag at time of creation:

```
Build-ref: oneshot/GAME/2026-03-22.1
```

This links feedback to a specific build. When a new oneshot runs, update the Build-ref in ACCEPTANCE_CRITERIA.md and REFERENCE_GAPS.md.

---

## IDEAS.md — The Inbox

Lowest friction entry point. Dump raw thoughts here. No formatting required.

```markdown
# Ideas

**Version:** 20260323 V1
**Purpose:** Low-friction inbox for raw ideas. Process into specs, then delete.

> Format: One idea per bullet. No formatting required.

---

- this is a wsl system and ^M newlines should be removed from bin files
- the monitoring screen should show a sparkline of response times
- need a way to bulk-tag projects
```

### Processing IDEAS.md

When Claude is told "process ideas" or "update the specification":

1. Read IDEAS.md
2. For each idea, determine where it belongs:
   - **Defect/constraint** → ACCEPTANCE_CRITERIA.md
   - **Missing feature** → REFERENCE_GAPS.md entry pointing to the spec file
   - **Spec clarification** → Direct edit to the relevant SCREEN-*.md or FUNCTIONALITY.md
3. Delete the processed idea from IDEAS.md
4. Commit: "Process ideas: [summary]"

Unprocessed ideas remain. IDEAS.md may be empty between sessions.

---

## ACCEPTANCE_CRITERIA.md — Testable Statements

Discovered during iteration. Each criterion names the spec file it refines.

### Format rules

- Group by topic, not by date
- Each group has a `**Target:**` line naming the spec file(s)
- Each criterion starts with the subject + MUST/MUST NOT
- When a criterion is folded into the target spec file, move it to a `## Folded` section at the bottom (don't delete — keeps history)
- Include `Build-ref:` header

---

## REFERENCE_GAPS.md — What's Missing

Organized by target spec file. Each gap tracks: what's missing, where it was observed, and priority.

### Format rules

- Sections are spec filenames (mark with `(NEW)` if file doesn't exist yet)
- Each gap is a checkbox: `- [ ]` open, `- [x]` specified
- Include GAME reference file when applicable
- Include priority (P0–P10)
- When a gap is fully specified, check the box and note the date
- Include `Build-ref:` header

### Automated gap analysis

```bash
bash bin/update_reference_gaps.sh GAME
```

Uses `claude -p` (subscription, not API tokens) to compare spec vs prototype vs reference implementation and update REFERENCE_GAPS.md.

---

## SCORECARD.md — Generated Quality Checklist

**Lives in the prototype directory, not in specs.** Generated by `bin/scorecard.sh`.

```bash
bash bin/scorecard.sh GAME
```

Produces a checklist of KPIs:

- **Route Coverage** — Do specified routes exist in routes.py?
- **Acceptance Criteria** — Do automatable criteria pass? (line endings, directory structure)
- **Stubs Remaining** — How many `# TODO: [stub]` comments remain?
- **Tests** — Do test files exist? Does bin/test.sh exist?
- **Project Structure** — Required files and directories present?
- **Reference Gaps** — Open/closed gap counts and priority breakdown

Each KPI is a checkbox: `[x]` pass, `[ ]` fail. Summary shows pass/fail/warn counts.

---

## The Iteration Cycle

```
 YOU (testing prototype)
  |
  |  find defect, want feature, have idea
  |
  v
 Specifications/<Project>/IDEAS.md     <-- dump it here (lowest friction)
  |
  |  "process ideas" or "update the specification"
  |
  v
 Claude processes IDEAS.md
  |
  +---> ACCEPTANCE_CRITERIA.md          <-- testable MUST statements
  +---> REFERENCE_GAPS.md              <-- missing features, tracked by file
  +---> Direct spec edits              <-- SCREEN-*.md, FUNCTIONALITY.md
  |
  |  Ideas removed from IDEAS.md after processing
  |
  v
 Spec files updated
  |
  |  oneshot.sh <Project> --update
  |
  v
 Update prompt generated
  |
  |  paste into Claude Code in prototype dir
  |
  v
 Prototype updated
  |
  |  bin/scorecard.sh <Project>
  |
  v
 SCORECARD.md generated in prototype
  |
  |  test again
  |
  v
 Repeat
```

### Quick iteration (no oneshot rebuild)

For small fixes during a session, skip the oneshot cycle:

```
 Find defect while working in prototype
  |
  v
 Fix code in prototype
  |
  v
 Claude also updates (automatically, per CLAUDE_PROTOTYPE_RULES):
   1. Spec file (SCREEN-*.md, FUNCTIONALITY.md, etc.)
   2. ACCEPTANCE_CRITERIA.md (add the testable statement)
   3. REFERENCE_GAPS.md (check off if gap is closed)
  |
  v
 Commit both prototype and spec changes
  |
  v
 Print session summary:
   --- Specification Updates ---
   ACCEPTANCE_CRITERIA.md: +2 criteria
   REFERENCE_GAPS.md: 1 gap closed
   SCREEN-MONITORING.md: updated health table section
```

---

## Rule Injection

Prototype iteration rules are delivered via `RulesEngine/CLAUDE_PROTOTYPE_RULES.md`.

- `oneshot.sh` includes this file in every build/update prompt
- The prompt instructs the agent to inject the rules into the prototype's AGENTS.md
- Rules are ONLY active when working in a prototype directory built by oneshot.sh
- No other code directories receive these rules

The RulesEngine directory accepts any `.md` file as a drop-in. All `.md` files in `RulesEngine/` (except BUSINESS_RULES.md, CONVERT.md, DOCUMENTATION_BRANDING.md, and the already-included CLAUDE_RULES.md and CLAUDE_PROTOTYPE_RULES.md) are automatically included in the oneshot prompt.

---

## Triggering Spec Updates

Low-friction phrases that tell Claude to update specs:

| You say | Claude does |
|---------|-----------|
| "update the specification" | Process IDEAS.md, review recent changes, update spec files |
| "process ideas" | Read IDEAS.md, distribute to proper files, delete processed |
| "add acceptance criteria for [X]" | Add MUST statement to ACCEPTANCE_CRITERIA.md |
| "this is a gap" | Add entry to REFERENCE_GAPS.md |
| "run scorecard" | Execute `bin/scorecard.sh`, review output |
| "fold criteria" | Move checked ACCEPTANCE_CRITERIA into target spec files |
| "run gap analysis" | Execute `bin/update_reference_gaps.sh` |

---

## Comparison to Reference Implementation

The reference implementation directory (e.g., `../GAME/`) is **read-only** — never modified during prototype iteration. It serves two purposes:

1. **Feature discovery** — When a gap is found, check if it's already implemented. Note the file and line in REFERENCE_GAPS.md.
2. **Implementation reference** — Read for guidance, but prototype code follows the spec, not the reference.

The reference is not the spec. The spec is the spec. The reference is evidence of what's possible.

---

## Daily Summary Integration

The `/daily-summary` skill generates activity reports from Claude Code session logs. For oneshot-built projects, it also:

1. Reviews `[BugFix]` entries → proposes acceptance criteria
2. Reviews `[Feature]` entries → checks against REFERENCE_GAPS.md for closures
3. Updates spec files in `Specifications/<ProjectName>/` when told to

Daily summary reports what happened. This process decides what to do about it.

---

## Relationship to Other Processes

| Process | Document | Script | Role |
|---------|----------|--------|------|
| Initial build | DOC-SPECIFICATION-PROCESS.md | `bin/oneshot.sh` | Spec → prompt → prototype |
| **Iteration** | **This document** | `bin/oneshot.sh --update` | **Prototype → feedback → spec → update** |
| Gap analysis | This document | `bin/update_reference_gaps.sh` | Compare spec vs code vs reference |
| Quality check | This document | `bin/scorecard.sh` | Checklist of KPIs vs spec |
| Daily summary | /daily-summary skill | `generate_daily_summary.py` | Activity log → spec updates |
| Validation | DOC-SPECIFICATION-PROCESS.md | `bin/validate.sh` | Check spec completeness |
