#!/bin/bash
# CommandCenter Operation
# Name: Update
# Category: maintenance

# Reads the session transaction log and updates iteration feedback files.
# Analyzes recent prototype activity (git history + Claude Code session logs)
# and uses an AI model to extract bugs found and ideas from the session.
#
# The transaction log is the Claude Code session JSONL stored at:
#   ~/.claude/projects/<prototype-path>/
#
# Usage:
#   bash bin/update.sh <ProjectName>
#   bash bin/update.sh <ProjectName> --model=<model>
#
# Writes:
#   Specifications/<ProjectName>/IDEAS.md
#   Specifications/<ProjectName>/ACCEPTANCE_CRITERIA.md
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
    echo "Usage: bash bin/update.sh <ProjectName> [--model=<model>]" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"
PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"
PROTO_DIR="$PROJECTS_DIR/${PROJECT_NAME}_prototype"

# Fall back to non-_prototype directory
if [ ! -d "$PROTO_DIR" ]; then
    PROTO_DIR="$PROJECTS_DIR/$PROJECT_NAME"
fi

if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Specifications directory not found: $SPEC_DIR" >&2
    exit 1
fi

if [ ! -d "$PROTO_DIR" ]; then
    echo "ERROR: Prototype directory not found: $PROTO_DIR" >&2
    echo "       Expected: ${PROJECT_NAME}_prototype/ or ${PROJECT_NAME}/" >&2
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

# Most recent Claude Code sessions for the prototype
SESSION_PATH="$(echo "$PROTO_DIR" | tr '/' '-')"
CLAUDE_SESSIONS_DIR="$HOME/.claude/projects/$SESSION_PATH"
SESSION_CONTENT=""
if [ -d "$CLAUDE_SESSIONS_DIR" ]; then
    # Get 2 most recent JSONL sessions, extract assistant message text only
    SESSION_FILES=$(ls -t "$CLAUDE_SESSIONS_DIR"/*.jsonl 2>/dev/null | head -2 || true)
    for f in $SESSION_FILES; do
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
        [ -n "$CONTENT" ] && SESSION_CONTENT="$SESSION_CONTENT

### Session: $(basename "$f")
$CONTENT"
    done
fi

# Build the prompt
PROTOTYPE_RULES="$(cat "$REPO_DIR/RulesEngine/CLAUDE_PROTOTYPE.md" 2>/dev/null || true)"

PROMPT="${PROTOTYPE_RULES}

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

## Instructions

Read the current iteration files and prototype code, then update:

1. **ACCEPTANCE_CRITERIA.md** — Add MUST/MUST NOT statements for bugs found or behavior constraints.
   Format: \`- MUST <present tense statement>\` or \`- MUST NOT <present tense statement>\`

2. **IDEAS.md** — Add ideas, improvements, or observations not yet captured.
   Format: \`- <short description>\`

Only add genuinely new items. Do not duplicate existing entries.
Write only to files in: $SPEC_DIR/

If a file does not exist, create it with a minimal header line.

Print a summary of all changes at the end:
\`\`\`
--- Update ---
ACCEPTANCE_CRITERIA.md: +N entries
IDEAS.md: +N entries
\`\`\`
"

echo "Running claude -p (model: $MODEL)..." >&2
echo "" >&2

cd "$PROTO_DIR" && claude -p "$PROMPT" \
    --model "$MODEL" \
    --add-dir "$SPEC_DIR" \
    --allowedTools "Read,Write,Glob,Grep"

echo "" >&2
echo "Update complete. Check: $SPEC_DIR" >&2
