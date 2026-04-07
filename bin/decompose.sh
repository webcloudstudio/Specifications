#!/bin/bash
# CommandCenter Operation
# Name: Decompose Project
# Category: Workflow
# Prompt: prompts/oneshot_build_rules.md
# Rules: RulesEngine/stack/*.md
#
# Reverse-engineer an existing project into specification files.
# Reads source code, detects the technology stack, and generates
# a prompt for an AI agent to produce structured specification files.
#
# The user runs setup.sh first to create the specification directory,
# then feeds the AI output into that directory.
#
# Usage:
#   bash bin/decompose.sh <project-path>
#   bash bin/decompose.sh <project-path> --spec-name <name>
#   bash bin/decompose.sh <project-name>
#
# Arguments:
#   <project-path>    Absolute path to the project directory, or a project name under ../
#   --spec-name       Override the specification directory name (default: directory basename)
#
# Examples:
#   bash bin/decompose.sh ../GAME > decompose-prompt.md
#   bash bin/decompose.sh /mnt/c/Users/barlo/projects/MyApp --spec-name MyApp > decompose-prompt.md
#   # Then: feed decompose-prompt.md to an AI agent, paste output into Specifications/<Name>/
#
# Exit codes:
#   0  Prompt generated
#   1  Project path not found or invalid
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
RULES_ENGINE="$PROJECT_DIR/RulesEngine"

# ── Parse arguments ──────────────────────────────────────────────────────────
TARGET=""
SPEC_NAME=""

for arg in "$@"; do
  case "$arg" in
    --spec-name=*) SPEC_NAME="${arg#--spec-name=}" ;;
    --spec-name)   shift_next=1 ;;
    -*)            echo "ERROR: Unknown flag: $arg" >&2; exit 1 ;;
    *)
      if [ "${shift_next:-}" = "1" ]; then
        SPEC_NAME="$arg"
        shift_next=""
      elif [ -z "$TARGET" ]; then
        TARGET="$arg"
      fi
      ;;
  esac
done

if [ -z "$TARGET" ]; then
  echo "Usage: bash bin/decompose.sh <project-path> [--spec-name <name>]" >&2
  exit 1
fi

# Resolve project path: absolute, relative, or project name under ../
if [ -d "$TARGET" ]; then
  PROJECT_PATH="$(cd "$TARGET" && pwd)"
elif [ -d "../$TARGET" ]; then
  PROJECT_PATH="$(cd "../$TARGET" && pwd)"
elif [ -d "$PROJECT_DIR/../$TARGET" ]; then
  PROJECT_PATH="$(cd "$PROJECT_DIR/../$TARGET" && pwd)"
else
  echo "ERROR: Project not found: $TARGET" >&2
  exit 1
fi

[ -z "$SPEC_NAME" ] && SPEC_NAME="$(basename "$PROJECT_PATH")"

# ── Detect stack ─────────────────────────────────────────────────────────────
STACK_HINTS=""
[ -f "$PROJECT_PATH/requirements.txt" ] && STACK_HINTS="$STACK_HINTS Python"
[ -f "$PROJECT_PATH/package.json" ] && STACK_HINTS="$STACK_HINTS Node.js"
[ -f "$PROJECT_PATH/Cargo.toml" ] && STACK_HINTS="$STACK_HINTS Rust"
[ -f "$PROJECT_PATH/go.mod" ] && STACK_HINTS="$STACK_HINTS Go"

# Detect Flask
if [ -f "$PROJECT_PATH/requirements.txt" ] && grep -qi flask "$PROJECT_PATH/requirements.txt" 2>/dev/null; then
  STACK_HINTS="$STACK_HINTS Flask"
fi

# Detect SQLite
if find "$PROJECT_PATH" -maxdepth 2 -name "*.db" -o -name "*.sqlite" 2>/dev/null | head -1 | grep -q .; then
  STACK_HINTS="$STACK_HINTS SQLite"
fi

# Detect Bootstrap
if grep -rq "bootstrap" "$PROJECT_PATH/templates/" 2>/dev/null || grep -rq "bootstrap" "$PROJECT_PATH/static/" 2>/dev/null; then
  STACK_HINTS="$STACK_HINTS Bootstrap"
fi

STACK_HINTS="$(echo "$STACK_HINTS" | xargs)"  # trim

# ── Helper: emit file with fence ─────────────────────────────────────────────
emit_file() {
  local label="$1" path="$2" max_lines="${3:-200}"
  if [ -f "$path" ]; then
    echo ""
    echo "### $label"
    echo '```'
    head -n "$max_lines" "$path"
    local total
    total=$(wc -l < "$path")
    if [ "$total" -gt "$max_lines" ]; then
      echo "... ($total lines total, showing first $max_lines)"
    fi
    echo '```'
  fi
}

# ── Helper: emit directory listing ───────────────────────────────────────────
emit_tree() {
  local label="$1" path="$2"
  if [ -d "$path" ]; then
    echo ""
    echo "### $label"
    echo '```'
    find "$path" -maxdepth 3 -not -path '*/\.*' \
      -not -path '*/__pycache__/*' -not -path '*/venv/*' \
      -not -path '*/node_modules/*' -not -path '*/.git/*' \
      | sort | head -100
    echo '```'
  fi
}

# ── Build the prompt ─────────────────────────────────────────────────────────
cat <<PROMPT_HEADER
# Decompose Project Into Specification Files

## Task

Read the source code of the **$SPEC_NAME** project below and produce a complete set of
specification files in the Prototyper format. Each file should be concise — tables, bullets,
and short descriptions. Do NOT write implementation code; write specifications that describe
what the project does.

## Detected Stack

$STACK_HINTS

## Target Specification Directory

\`Specifications/$SPEC_NAME/\`

## Output Files Required

Produce each file below. Use the exact filenames. Every specification file (except METADATA.md,
README.md, and IDEAS.md) must end with \`## Open Questions\` (leave empty if none).

1. **METADATA.md** — key: value format (not YAML). Required fields:
   - name, display_name, title, git_repo, short_description, port, version, updated, status, stack, health, tags, description

2. **README.md** — one-line description + \`## Intent\` section (why it exists, who it's for)

3. **INTENT.md** — goals, constraints, success criteria

4. **ARCHITECTURE.md** — modules, routes table, directory layout tree

5. **DATABASE.md** — one table per entity. Columns: name, type, constraints, description

6. **FUNCTIONALITY.md** — what the application does. Group by area. Tables or bullets.

7. **UI-GENERAL.md** — shared UI patterns (layout, navigation, color usage, component patterns)

8. **SCREEN-{Name}.md** — one file per distinct screen/page. Include: route, layout description,
   interactions, data displayed. Use the naming pattern SCREEN-AREA-NAME.md for hierarchical screens.

9. **FEATURE-{Name}.md** — one file per non-trivial feature. Include: trigger, sequence of steps,
   reads, writes.

## Rules

- Be concise — tables and bullets, not paragraphs
- Use the exact column formats shown in the specification template files below
- Screens and features should be separate files, not combined
- Route tables in ARCHITECTURE.md should list every route with method, path, and purpose
- DATABASE.md should show every table and column — do not summarize or skip fields
- Status should be PROTOTYPE unless the project is clearly production-ready

PROMPT_HEADER

# ── Include specification expansion rules for format reference ────────────────
ONESHOT_RULES="$PROJECT_DIR/prompts/oneshot_build_rules.md"
if [ -f "$ONESHOT_RULES" ]; then
  echo ""
  echo "---"
  echo ""
  echo "## Specification Format Reference (prompts/oneshot_build_rules.md)"
  echo ""
  echo '```markdown'
  cat "$ONESHOT_RULES"
  echo '```'
fi

# ── Include relevant stack files ─────────────────────────────────────────────
for hint in $STACK_HINTS; do
  hint_lower="$(echo "$hint" | tr '[:upper:]' '[:lower:]')"
  stack_file="$RULES_ENGINE/stack/${hint_lower}.md"
  if [ -f "$stack_file" ]; then
    echo ""
    echo "---"
    echo ""
    echo "## Stack Reference: $hint"
    echo ""
    echo '```markdown'
    cat "$stack_file"
    echo '```'
  fi
done

# ── Project source code ──────────────────────────────────────────────────────
echo ""
echo "---"
echo ""
echo "## Project Source Code"

emit_tree "Directory Structure" "$PROJECT_PATH"

# Key config files
emit_file "METADATA.md (if exists)" "$PROJECT_PATH/METADATA.md"
emit_file "README.md" "$PROJECT_PATH/README.md"
emit_file "requirements.txt" "$PROJECT_PATH/requirements.txt"
emit_file "package.json" "$PROJECT_PATH/package.json" 50

# Python source files
if [ -d "$PROJECT_PATH" ]; then
  for pyfile in $(find "$PROJECT_PATH" -maxdepth 2 -name "*.py" \
    -not -path '*/venv/*' -not -path '*/__pycache__/*' \
    -not -path '*/.git/*' -not -name "generate_*_image.py" \
    2>/dev/null | sort | head -20); do
    rel="${pyfile#$PROJECT_PATH/}"
    emit_file "$rel" "$pyfile" 200
  done
fi

# Templates
if [ -d "$PROJECT_PATH/templates" ]; then
  for tmpl in $(find "$PROJECT_PATH/templates" -name "*.html" 2>/dev/null | sort | head -30); do
    rel="${tmpl#$PROJECT_PATH/}"
    emit_file "$rel" "$tmpl" 80
  done
fi

# SQL schema files
for sqlfile in $(find "$PROJECT_PATH" -maxdepth 2 -name "*.sql" -o -name "schema.py" \
  2>/dev/null | sort | head -5); do
  rel="${sqlfile#$PROJECT_PATH/}"
  emit_file "$rel" "$sqlfile" 200
done

# JavaScript source (not vendor/node_modules)
if [ -d "$PROJECT_PATH/static" ]; then
  for jsfile in $(find "$PROJECT_PATH/static" -name "*.js" \
    -not -path '*/node_modules/*' -not -path '*/vendor/*' \
    2>/dev/null | sort | head -10); do
    rel="${jsfile#$PROJECT_PATH/}"
    emit_file "$rel" "$jsfile" 150
  done
fi

# Config files
emit_file "AGENTS.md" "$PROJECT_PATH/AGENTS.md"
emit_file ".env.example" "$PROJECT_PATH/.env.example" 30
emit_file "config.py" "$PROJECT_PATH/config.py"
emit_file "Dockerfile" "$PROJECT_PATH/Dockerfile" 50

echo ""
echo "---"
echo "END OF PROJECT SOURCE"
