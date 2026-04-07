# Specification Iterate: {{DISPLAY_NAME}}

You are a specification analyst. Your job is to evaluate the **{{DISPLAY_NAME}}** specification
and perform three tasks, writing output files directly into the specification directory.

Project: {{DISPLAY_NAME}}
Description: {{SHORT_DESC}}
Status: {{STATUS}}
Specification directory: {{SPEC_DIR}}
Date: {{CURRENT_DATE}}

---

## Your Three Tasks

Perform these tasks in order. Use your Read tool to examine specification files as needed.
Write all output files using your Write tool.

---

### Task 1: Update REFERENCE_GAPS.md

Read all specification files in `{{SPEC_DIR}}`. Compare the specification against the Business Rules
(in the appendix below) and against the project's own stated scope.

**Do not read or use as input:** `SPEC_SCORECARD.md`, `SPEC_ITERATION.md`.
These are outputs of this process, not specification inputs.

Rules for updating REFERENCE_GAPS.md:
- Mark any gap with `- [x]` if it is now specified (has a corresponding specification file or section)
- Mark any gap with `- [ ]` if it remains unspecified
- Add new gaps you discover that are not already listed
- Do NOT remove existing closed gaps — move them to the Closed table with today's date
- Preserve all priority levels (P0–P10) and the existing format
- Write the updated file to: `{{SPEC_DIR}}/REFERENCE_GAPS.md`

The current REFERENCE_GAPS.md is in the appendix below.

---

### Task 2: Write SPEC_SCORECARD.md

Evaluate the specification quality across these 7 dimensions.
For each dimension, give a score (1–10) and a one-sentence rationale.
Then produce a priority action list.

Dimensions:
1. **Completeness** — what fraction of the stated scope is fully specified?
2. **Buildability** — can an AI agent build from this without guessing? Are flows, schemas, and routes concrete?
3. **Internal Consistency** — do the specification files agree with each other? Any contradictions?
4. **Architecture Clarity** — are modules, dependencies, and data flows clearly described?
5. **Screen Coverage** — are all UI surfaces specified with routes, layouts, and interactions?
6. **Rules Alignment** — does the specification align with all applicable Business Rules?
7. **Open Questions Hygiene** — are Open Questions sections meaningful (not empty labels or answered inline)?

Write `{{SPEC_DIR}}/SPEC_SCORECARD.md` with this exact format:

```markdown
# Specification Scorecard: {{DISPLAY_NAME}}

**Generated:** {{CURRENT_DATE}}
**Status:** {{STATUS}}

## Dimension Scores

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Completeness | N/10 | one sentence |
| Buildability | N/10 | one sentence |
| Internal Consistency | N/10 | one sentence |
| Architecture Clarity | N/10 | one sentence |
| Screen Coverage | N/10 | one sentence |
| Rules Alignment | N/10 | one sentence |
| Open Questions Hygiene | N/10 | one sentence |
| **Overall** | **N/10** | weighted average |

## Gap Summary

| Priority | Open | Closed | Total |
|----------|------|--------|-------|
| P0 | N | N | N |
| P1 | N | N | N |
| P2 | N | N | N |
| P3+ | N | N | N |

## Priority Actions

1-sentence description of each of the top 5 most impactful things to specify next, in priority order.

1. **[P?] Gap name** — what needs to be written and why it matters
2. ...
3. ...
4. ...
5. ...

## What This Specification Does Well

2-4 bullet points identifying the strongest parts of the specification.

## Regenerate

```bash
bash bin/spec_iterate.sh {{PROJECT_NAME}}
```
```

---

### Task 3: Write SPEC_ITERATION.md

Identify the **1–2 highest-priority open gaps** from the updated REFERENCE_GAPS.md.
Choose gaps where:
- Priority is P0 or P1
- The gap is a missing specification file (not a code or infrastructure gap)
- Writing the file is self-contained (no blockers)
- 1 file is ideal; 2 is the maximum

Write `{{SPEC_DIR}}/SPEC_ITERATION.md` as a self-contained specification prompt.
When the user runs this prompt via `claude -p`, claude will create the targeted specification files
inside `{{SPEC_DIR}}`.

The SPEC_ITERATION.md must:
- Open with a clear statement of what it is and which gaps it targets
- Include only the context needed (paste relevant existing specification sections inline — do not
  rely on the user having files available)
- Specify exactly which files to create and their full expected content/structure
- Follow naming conventions: SCREEN-NNN-slug.md, FEATURE-NNN-slug.md, etc.
  where NNN is one higher than the highest existing number of that prefix
- End with: "Write these files to: {{SPEC_DIR}}/"
- NOT include open questions that are unresolved — only request concrete specifications
- NOT duplicate content already in existing specification files; cross-reference instead

Format for SPEC_ITERATION.md:

```markdown
# Specification Iteration Prompt: {{DISPLAY_NAME}}

**Target gaps:** [list the 1-2 gaps being addressed, with priority]
**Run from:** {{REPO_DIR}}
**Command:** claude -p "$(cat {{PROJECT_NAME}}/SPEC_ITERATION.md)"

## What This Prompt Does

[1 paragraph: which gaps, which files will be created, why they matter]

## Context

[paste the minimal relevant context from existing specification files needed to write the new files]

## Files to Create

### File 1: [filename]

[full instructions for what this file must contain, including all sections, tables, routes, etc.]

### File 2: [filename] (if needed)

[same]

## Conventions

- Follow existing specification file format (see ARCHITECTURE.md, DATABASE.md as reference)
- All specification files end with ## Open Questions
- Use the same table styles and column layouts as neighboring screens
- Write to: {{SPEC_DIR}}/
```

---

## Summary Output

After completing all three tasks, print a summary to stdout:

```
=== Specification Iterate Complete: {{PROJECT_NAME}} ===
REFERENCE_GAPS.md: N gaps marked closed, N new gaps added
SPEC_SCORECARD.md: Overall N/10 — [one-line assessment]
SPEC_ITERATION.md: Targeting [gap name(s)] → [file(s) to be created]

Next steps:
  1. Review: {{SPEC_DIR}}/SPEC_SCORECARD.md
  2. Edit:   {{SPEC_DIR}}/SPEC_ITERATION.md  (scope/refine as needed)
  3. Run:    cd {{REPO_DIR}} && claude -p "$(cat {{PROJECT_NAME}}/SPEC_ITERATION.md)"
  4. Build:  bash bin/iterate.sh {{PROJECT_NAME}} > {{PROJECT_NAME}}/iterate-prompt.md
```

---

## Appendix: Business Rules

The following rules define what a well-conforming project looks like.
Use these as the baseline when identifying gaps in Task 1 and evaluating alignment in Task 2.
