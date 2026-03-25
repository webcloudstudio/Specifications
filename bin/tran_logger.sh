#!/bin/bash
# CommandCenter Operation
# Name: Transaction Logger
# Category: maintenance
# Args: Spec

# Reads the session transaction log and updates iteration feedback files.
# Analyzes recent prototype activity (git history + Claude Code session logs)
# and uses an AI model to extract bugs found and ideas from the session.
#
# The transaction log is the Claude Code session JSONL stored at:
#   ~/.claude/projects/<prototype-path>/
#
# Usage:
#   bash bin/tran_logger.sh <ProjectName>
#   bash bin/tran_logger.sh <ProjectName> --model=<model>
#
# Writes:
#   Specifications/<ProjectName>/PATCH-NNN-tl-*.md  (code mutations)
#   Specifications/<ProjectName>/AC-NNN-tl-*.md     (acceptance criteria batches)
#   Specifications/<ProjectName>/IDEAS.md
#
# Options:
#   --model=<model>    AI model to use (default: claude-haiku-4-5-20251001)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSITIONAL=""
MODEL="claude-haiku-4-5-20251001"

for arg in "$@"; do
    case "$arg" in
        --model=*) MODEL="${arg#--model=}" ;;
        --*)       ;;
        *)         [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/tran_logger.sh <ProjectName> [--model=<model>]" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Specifications directory not found: $SPEC_DIR" >&2
    exit 1
fi

# Read prototype directory from .env (written by oneshot.sh / iterate.sh)
PROTO_DIR=""
ENV_FILE="$SPEC_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    PROTO_DIR=$(grep "^PROTOTYPE_DIR=" "$ENV_FILE" 2>/dev/null | head -1 | sed 's/^PROTOTYPE_DIR=//' | tr -d '\r' || true)
fi

if [ -z "$PROTO_DIR" ]; then
    echo "ERROR: PROTOTYPE_DIR not set in $ENV_FILE" >&2
    echo "       Run bash bin/iterate.sh $PROJECT_NAME or bash bin/oneshot.sh $PROJECT_NAME first." >&2
    exit 1
fi

if [ ! -d "$PROTO_DIR" ]; then
    echo "ERROR: Prototype directory not found: $PROTO_DIR" >&2
    echo "       Update PROTOTYPE_DIR in $ENV_FILE or re-run iterate.sh/oneshot.sh." >&2
    exit 1
fi

if ! command -v claude &>/dev/null; then
    echo "ERROR: claude CLI not found." >&2
    exit 1
fi

echo "Update: $PROJECT_NAME" >&2
echo "  Specifications: $SPEC_DIR" >&2
echo "  Prototype:      $PROTO_DIR" >&2
echo "  Model:          $MODEL" >&2
echo "" >&2

# Recent git activity from prototype (last 20 commits)
PROTO_LOG=""
if [ -d "$PROTO_DIR/.git" ]; then
    PROTO_LOG=$(git -C "$PROTO_DIR" log --oneline -20 2>/dev/null || true)
fi

# Recent specification changes (last 10 commits)
cd "$REPO_DIR"
SPEC_LOG=$(git log --oneline -10 -- "$PROJECT_NAME/" 2>/dev/null || true)

# Session cursor — tracks which JSONL files have already been processed
CURSOR_FILE="$SPEC_DIR/.tran_logger_cursor"
touch "$CURSOR_FILE"

# Most recent Claude Code sessions for the prototype
SESSION_PATH="$(echo "$PROTO_DIR" | tr '/' '-')"
CLAUDE_SESSIONS_DIR="$HOME/.claude/projects/$SESSION_PATH"
SESSION_CONTENT=""
NEW_SESSIONS=0
if [ -d "$CLAUDE_SESSIONS_DIR" ]; then
    # Get 10 most recent JSONL sessions (wider window for idempotency check)
    SESSION_FILES=$(ls -t "$CLAUDE_SESSIONS_DIR"/*.jsonl 2>/dev/null | head -10 || true)
    for f in $SESSION_FILES; do
        FBASE="$(basename "$f")"
        # Skip sessions already processed in a previous run
        if grep -qF "$FBASE" "$CURSOR_FILE" 2>/dev/null; then
            echo "  Skipping (already processed): $FBASE" >&2
            continue
        fi
        # Extract text content from assistant messages (trim to 300 lines per file)
        CONTENT=$(python3 -c "
import json, sys
lines = []
for line in open('$f', encoding='utf-8', errors='replace'):
    try:
        msg = json.loads(line)
        role = msg.get('message', {}).get('role', '')
        if role == 'assistant':
            for block in msg.get('message', {}).get('content', []):
                if isinstance(block, dict) and block.get('type') == 'text':
                    lines.append(block['text'][:500])
    except: pass
print('\n'.join(lines[:100]))
" 2>/dev/null || true)
        if [ -n "$CONTENT" ]; then
            SESSION_CONTENT="$SESSION_CONTENT

### Session: $FBASE
$CONTENT"
            NEW_SESSIONS=$((NEW_SESSIONS + 1))
        fi
        echo "$FBASE" >> "$CURSOR_FILE"
    done
fi

if [ "$NEW_SESSIONS" -eq 0 ] && [ -z "$SESSION_CONTENT" ]; then
    echo "No new sessions to process. Cursor is up to date." >&2
    exit 0
fi

# Build the prompt
PROTOTYPE_RULES="$(cat "$REPO_DIR/RulesEngine/CLAUDE_PROTOTYPE.md" 2>/dev/null || true)"

PROMPT=$(cat <<END_PROMPT
${PROTOTYPE_RULES}

---

# Update Task

You are updating the iteration feedback files for **${PROJECT_NAME}** based on recent session activity.

## Prototype directory: $PROTO_DIR

### Recent prototype git log:
\`\`\`
${PROTO_LOG:-"(no git history found)"}
\`\`\`

### Recent specification git log:
\`\`\`
${SPEC_LOG:-"(no recent changes)"}
\`\`\`
${SESSION_CONTENT:+
### Recent session activity (extracted from Claude Code session log):
$SESSION_CONTENT
}

## Artifact Taxonomy

Classify each discovery into exactly one of these three artifact types:

**PATCH ticket** — a concrete code change needed in the prototype.
Examples: a bug fix, a missing feature, a behavioral correction, a refactor.
Write to: \`$SPEC_DIR/PATCH-NNN-tl-description.md\`
(The \`tl-\` prefix marks this file as auto-generated by tran_logger.)

Use this format:
\`\`\`
# Patch: NNN-tl — Short description
**Type:** patch
**Source:** tran_logger
**Scope:** list of prototype files or areas affected

## Intent
Why this change is needed. One paragraph.

## Changes Required
- Specific, unambiguous instruction
- Another instruction

## Open Questions
None.
\`\`\`

**AC ticket** — a batch of testable behavioral requirements (MUST/MUST NOT).
Examples: "Login MUST redirect to dashboard", "API MUST NOT return 500 on invalid input".
Write to: \`$SPEC_DIR/AC-NNN-tl-description.md\`

Use this format:
\`\`\`
# AC: NNN-tl — Short description
**Type:** ac
**Source:** tran_logger
**Scope:** area or feature these criteria cover

## Criteria
- [ ] System MUST ...
- [ ] System MUST NOT ...

## Open Questions
None.
\`\`\`

**IDEAS.md entry** — a fuzzy observation, improvement idea, or question not yet actionable.
Examples: "Consider adding pagination", "Nav feels cluttered".
Write to: \`$SPEC_DIR/IDEAS.md\`

## Instructions

1. Determine the next ticket counter:
   Count existing files matching \`$SPEC_DIR/*-[0-9][0-9][0-9]-*.md\` and \`$SPEC_DIR/*-[0-9][0-9][0-9].md\`.
   Next number = count + 1, zero-padded to 3 digits.
   Use that number for ALL tickets created this run (increment per ticket).
   Filename examples: \`PATCH-004-tl-fix-nav.md\`, \`AC-005-tl-login-flow.md\`

2. For each discovery from the session activity and git log:
   - Classify as: PATCH ticket, AC ticket, or IDEA
   - Write one PATCH ticket file per concrete code change
   - Write one AC ticket file per group of related acceptance criteria
   - Append IDEA entries to IDEAS.md (create with header if missing)

3. Only add genuinely new items. Do not duplicate existing entries.
   Write only to files in: $SPEC_DIR/

Print a summary of all changes at the end:
\`\`\`
--- Transaction Log ---
PATCH-NNN-tl-description.md: created
AC-NNN-tl-description.md: created
IDEAS.md: +N entries
\`\`\`
END_PROMPT
)

echo "Running claude -p (model: $MODEL)..." >&2
echo "" >&2

cd "$PROTO_DIR" && claude -p "$PROMPT" \
    --model "$MODEL" \
    --add-dir "$SPEC_DIR" \
    --allowedTools "Read,Write,Glob,Grep"

echo "" >&2
echo "Update complete. Check: $SPEC_DIR" >&2
