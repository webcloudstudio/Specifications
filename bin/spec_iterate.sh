#!/bin/bash
# CommandCenter Operation
# Name: Spec Iterate
# Category: maintenance
# Args: Spec

# AI-powered specification gap analysis and iteration planning.
# Calls claude -p (subscription, not API tokens) to:
#   1. Update <Spec>/REFERENCE_GAPS.md with current gap state
#   2. Write <Spec>/SPEC_SCORECARD.md — spec quality rating across 7 dimensions
#   3. Write <Spec>/SPEC_ITERATION.md — a focused prompt that creates 1-2 spec files
#      targeting the highest-priority open gaps
#
# Workflow:
#   Step 1:  bash bin/spec_iterate.sh <ProjectName>
#            Claude updates REFERENCE_GAPS.md, writes SPEC_SCORECARD.md and SPEC_ITERATION.md
#   Step 2:  Review and edit <ProjectName>/SPEC_ITERATION.md
#   Step 3:  cd /path/to/Specifications && claude -p "$(cat <ProjectName>/SPEC_ITERATION.md)"
#            Claude creates the targeted spec files inside the spec directory
#   Step 4:  Run iterate.sh or oneshot.sh to push spec changes to the prototype
#
# Usage:
#   bash bin/spec_iterate.sh <ProjectName>
#   bash bin/spec_iterate.sh <ProjectName> --model opus
#
# Arguments:
#   $1           Project name (required) — specification directory name
#   --model      Model override: sonnet (default) | opus | haiku
#
# Exit codes:
#   0  Completed
#   1  Missing argument, missing spec directory, or claude CLI not found

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Argument parsing ---
POSITIONAL=""
MODEL="sonnet"
for arg in "$@"; do
    case "$arg" in
        --model=*) MODEL="${arg#--model=}" ;;
        --model)   shift; MODEL="${1:-sonnet}" ;;
        --*)       ;;
        *)         [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/spec_iterate.sh <ProjectName> [--model sonnet|opus|haiku]" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Specification directory not found: $SPEC_DIR" >&2
    exit 1
fi

if [ ! -f "$SPEC_DIR/METADATA.md" ]; then
    echo "ERROR: METADATA.md not found in $SPEC_DIR" >&2
    exit 1
fi

if ! command -v claude &>/dev/null; then
    echo "ERROR: claude CLI not found. Install Claude Code to use this script." >&2
    exit 1
fi

# --- Metadata ---
get_metadata() {
    grep "^${1}:" "$SPEC_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r'
}
DISPLAY_NAME=$(get_metadata "display_name")
SHORT_DESC=$(get_metadata "short_description")
STATUS=$(get_metadata "status")

echo "Spec Iterate: $PROJECT_NAME" >&2
echo "  Spec:    $SPEC_DIR" >&2
echo "  Model:   $MODEL" >&2
echo "  Status:  ${STATUS:-unknown}" >&2
echo "" >&2

# --- Collect spec files ---
SPEC_FILES=$(find "$SPEC_DIR" -maxdepth 1 -name "*.md" \
    ! -name "SPEC_SCORECARD.md" \
    ! -name "SPEC_ITERATION.md" \
    ! -name "DEPLOY_LOG.md" \
    | sort)

SPEC_FILE_COUNT=$(echo "$SPEC_FILES" | grep -c '.' 2>/dev/null || true)
echo "  Spec files: $SPEC_FILE_COUNT" >&2
echo "" >&2

# --- Rules files ---
RULES_DIR="$REPO_DIR/RulesEngine"
BUSINESS_RULES=""
if [ -f "$RULES_DIR/BUSINESS_RULES.md" ]; then
    BUSINESS_RULES="$(cat "$RULES_DIR/BUSINESS_RULES.md")"
fi

# --- Build the prompt ---
CURRENT_DATE=$(date '+%Y-%m-%d')
CURRENT_GAPS=""
if [ -f "$SPEC_DIR/REFERENCE_GAPS.md" ]; then
    CURRENT_GAPS="$(cat "$SPEC_DIR/REFERENCE_GAPS.md")"
fi

PROMPT="$(cat <<PROMPT_EOF
# Spec Iterate: ${DISPLAY_NAME:-$PROJECT_NAME}

You are a specification analyst. Your job is to evaluate the **${DISPLAY_NAME:-$PROJECT_NAME}** specification
and perform three tasks, writing output files directly into the specification directory.

Project: ${DISPLAY_NAME:-$PROJECT_NAME}
Description: ${SHORT_DESC:-}
Status: ${STATUS:-PROTOTYPE}
Spec directory: $SPEC_DIR
Date: $CURRENT_DATE

---

## Business Rules (platform standards)

The following rules define what a well-conforming project looks like.
Use these as the baseline when identifying gaps.

${BUSINESS_RULES}

---

## Your Three Tasks

Perform these tasks in order. Use your Read tool to examine spec files as needed.
Write all output files using your Write tool.

---

### Task 1: Update REFERENCE_GAPS.md

Read all spec files in \`$SPEC_DIR\`. Compare the specification against the Business Rules
and against the project's own stated scope.

Rules for updating REFERENCE_GAPS.md:
- Mark any gap with \`- [x]\` if it is now specified (has a corresponding spec file or section)
- Mark any gap with \`- [ ]\` if it remains unspecified
- Add new gaps you discover that are not already listed
- Do NOT remove existing closed gaps — move them to the Closed table with today's date
- Preserve all priority levels (P0–P10) and the existing format
- Write the updated file to: \`$SPEC_DIR/REFERENCE_GAPS.md\`

Current REFERENCE_GAPS.md:
${CURRENT_GAPS}

---

### Task 2: Write SPEC_SCORECARD.md

Evaluate the specification quality across these 7 dimensions.
For each dimension, give a score (1–10) and a one-sentence rationale.
Then produce a priority action list.

Dimensions:
1. **Completeness** — what fraction of the stated scope is fully specified?
2. **Buildability** — can an AI agent build from this without guessing? Are flows, schemas, and routes concrete?
3. **Internal Consistency** — do the spec files agree with each other? Any contradictions?
4. **Architecture Clarity** — are modules, dependencies, and data flows clearly described?
5. **Screen Coverage** — are all UI surfaces specified with routes, layouts, and interactions?
6. **Rules Alignment** — does the spec align with all applicable Business Rules?
7. **Open Questions Hygiene** — are Open Questions sections meaningful (not empty labels or answered inline)?

Write \`$SPEC_DIR/SPEC_SCORECARD.md\` with this exact format:

\`\`\`markdown
# Spec Scorecard: ${DISPLAY_NAME:-$PROJECT_NAME}

**Generated:** $CURRENT_DATE
**Status:** ${STATUS:-PROTOTYPE}

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

## What This Spec Does Well

2-4 bullet points identifying the strongest parts of the specification.

## Regenerate

\`\`\`bash
bash bin/spec_iterate.sh ${PROJECT_NAME}
\`\`\`
\`\`\`

---

### Task 3: Write SPEC_ITERATION.md

Identify the **1–2 highest-priority open gaps** from the updated REFERENCE_GAPS.md.
Choose gaps where:
- Priority is P0 or P1
- The gap is a missing spec file (not a code or infrastructure gap)
- Writing the file is self-contained (no blockers)
- 1 file is ideal; 2 is the maximum

Write \`$SPEC_DIR/SPEC_ITERATION.md\` as a self-contained specification prompt.
When the user runs this prompt via \`claude -p\`, claude will create the targeted spec files
inside \`$SPEC_DIR\`.

The SPEC_ITERATION.md must:
- Open with a clear statement of what it is and which gaps it targets
- Include only the context needed (paste relevant existing spec sections inline — do not
  rely on the user having files available)
- Specify exactly which files to create and their full expected content/structure
- Follow naming conventions: SCREEN-NNN-slug.md, FEATURE-NNN-slug.md, etc.
  where NNN is one higher than the highest existing number of that prefix
- End with: "Write these files to: $SPEC_DIR/"
- NOT include open questions that are unresolved — only request concrete specs
- NOT duplicate content already in existing spec files; cross-reference instead

Format for SPEC_ITERATION.md:

\`\`\`markdown
# Spec Iteration Prompt: ${DISPLAY_NAME:-$PROJECT_NAME}

**Target gaps:** [list the 1-2 gaps being addressed, with priority]
**Run from:** $REPO_DIR
**Command:** claude -p "\$(cat ${PROJECT_NAME}/SPEC_ITERATION.md)"

## What This Prompt Does

[1 paragraph: which gaps, which files will be created, why they matter]

## Context

[paste the minimal relevant context from existing spec files needed to write the new files]

## Files to Create

### File 1: [filename]

[full instructions for what this file must contain, including all sections, tables, routes, etc.]

### File 2: [filename] (if needed)

[same]

## Conventions

- Follow existing spec file format (see ARCHITECTURE.md, DATABASE.md as reference)
- All spec files end with ## Open Questions
- Use the same table styles and column layouts as neighboring screens
- Write to: $SPEC_DIR/
\`\`\`

---

## Summary Output

After completing all three tasks, print a summary to stdout:

\`\`\`
=== Spec Iterate Complete: ${PROJECT_NAME} ===
REFERENCE_GAPS.md: N gaps marked closed, N new gaps added
SPEC_SCORECARD.md: Overall N/10 — [one-line assessment]
SPEC_ITERATION.md: Targeting [gap name(s)] → [file(s) to be created]

Next steps:
  1. Review: $SPEC_DIR/SPEC_SCORECARD.md
  2. Edit:   $SPEC_DIR/SPEC_ITERATION.md  (scope/refine as needed)
  3. Run:    cd $REPO_DIR && claude -p "\$(cat ${PROJECT_NAME}/SPEC_ITERATION.md)"
  4. Build:  bash bin/iterate.sh ${PROJECT_NAME} > ${PROJECT_NAME}/iterate-prompt.md
\`\`\`

PROMPT_EOF
)"

# --- Run ---
echo "Running claude -p (model: $MODEL)..." >&2
echo "This may take 30–60 seconds." >&2
echo "" >&2

cd "$SPEC_DIR" && claude -p "$PROMPT" \
    --model "$MODEL" \
    --allowedTools "Read,Write,Glob,Grep" \
    --add-dir "$REPO_DIR/RulesEngine"

echo "" >&2
echo "Done. Output files:" >&2
echo "  $SPEC_DIR/REFERENCE_GAPS.md" >&2
echo "  $SPEC_DIR/SPEC_SCORECARD.md" >&2
echo "  $SPEC_DIR/SPEC_ITERATION.md" >&2
