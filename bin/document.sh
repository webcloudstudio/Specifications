#!/bin/bash
# CommandCenter Operation
# Name: Document
# Category: maintenance
# Args: Spec
# Prompt: prompts/document.md

# Generate project documentation from specification files using AI summarization.
# Two-phase pipeline:
#   Phase 1: claude -p reads specs and writes curated DOC-*.md files into target docs/
#   Phase 2: build_project_docs.py assembles DOC-*.md + bin/ scripts into docs/index.html
#
# Usage:
#   bash bin/document.sh <ProjectName>
#   bash bin/document.sh <ProjectName> --theme=slate --target=../GAME_p2
#   bash bin/document.sh <ProjectName> --model=opus
#
# Arguments:
#   $1           Project name (required) — specification directory name
#   --theme      Theme name (default: slate)
#   --target     Target project directory (default: resolved from METADATA.md git_repo or ../<name>)
#   --model      Model override: sonnet (default) | opus | haiku
#
# Exit codes:
#   0  Documentation generated
#   1  Missing argument, missing spec directory, or claude CLI not found

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RULES_DIR="$REPO_DIR/RulesEngine"
STYLES_DIR="$REPO_DIR/docs/styles"

# --- Argument parsing ---
POSITIONAL=""
THEME="slate"
TARGET=""
MODEL="sonnet"
for arg in "$@"; do
    case "$arg" in
        --theme=*)  THEME="${arg#--theme=}" ;;
        --target=*) TARGET="${arg#--target=}" ;;
        --model=*)  MODEL="${arg#--model=}" ;;
        --*)        ;;
        *)          [ -z "$POSITIONAL" ] && POSITIONAL="$arg" ;;
    esac
done

if [ -z "$POSITIONAL" ]; then
    echo "Usage: bash bin/document.sh <ProjectName> [--theme=<name>] [--target=<path>] [--model=<name>]" >&2
    exit 1
fi

PROJECT_NAME="$POSITIONAL"
SPEC_DIR="$REPO_DIR/$PROJECT_NAME"

# --- Validate spec directory ---
if [ ! -d "$SPEC_DIR" ]; then
    echo "ERROR: Specification directory not found: $SPEC_DIR" >&2
    exit 1
fi

if [ ! -f "$SPEC_DIR/METADATA.md" ]; then
    echo "ERROR: METADATA.md not found in $SPEC_DIR" >&2
    exit 1
fi

# --- Resolve target directory ---
get_metadata() {
    grep "^${1}:" "$SPEC_DIR/METADATA.md" 2>/dev/null | head -1 | sed "s/^${1}:[[:space:]]*//" | tr -d '\r'
}

DISPLAY_NAME=$(get_metadata "display_name")
SHORT_DESC=$(get_metadata "short_description")
STATUS=$(get_metadata "status")
GIT_REPO=$(get_metadata "git_repo")

if [ -z "$TARGET" ]; then
    # Try to resolve from git_repo field (e.g., ../GAME or a full path)
    if [ -n "$GIT_REPO" ] && [ -d "$GIT_REPO" ]; then
        TARGET="$GIT_REPO"
    elif [ -n "$GIT_REPO" ]; then
        # Try relative to parent of repo dir
        PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"
        REPO_NAME="$(basename "$GIT_REPO" .git)"
        if [ -d "$PROJECTS_DIR/$REPO_NAME" ]; then
            TARGET="$PROJECTS_DIR/$REPO_NAME"
        fi
    fi
    # Fallback: sibling directory with same name
    if [ -z "$TARGET" ]; then
        PROJECTS_DIR="$(cd "$REPO_DIR/.." && pwd)"
        TARGET="$PROJECTS_DIR/$PROJECT_NAME"
    fi
fi

# Resolve to absolute path
if [[ "$TARGET" != /* ]]; then
    TARGET="$(cd "$REPO_DIR" && cd "$TARGET" 2>/dev/null && pwd)" || TARGET="$REPO_DIR/$TARGET"
fi

if [ ! -d "$TARGET" ]; then
    echo "ERROR: Target project directory not found: $TARGET" >&2
    echo "  Use --target=<path> to specify the project directory" >&2
    exit 1
fi

# --- Validate theme ---
THEME_FILE="$STYLES_DIR/themes/${THEME}.css"
if [ ! -f "$THEME_FILE" ]; then
    echo "ERROR: Theme not found: $THEME_FILE" >&2
    echo "Available themes: $(ls "$STYLES_DIR/themes/" 2>/dev/null | sed 's/\.css//' | tr '\n' ' ')"
    exit 1
fi

# --- Validate claude CLI ---
if ! command -v claude &>/dev/null; then
    echo "ERROR: claude CLI not found. Install Claude Code to use this script." >&2
    exit 1
fi

echo "Document: $PROJECT_NAME" >&2
echo "  Specification: $SPEC_DIR" >&2
echo "  Target:        $TARGET" >&2
echo "  Theme:         $THEME" >&2
echo "  Model:         $MODEL" >&2
echo "" >&2

# --- Spec format adequacy warnings ---
echo "Documentation readiness:" >&2
DOC_WARNINGS=0

doc_warn() {
    echo "  WARN  $1" >&2
    DOC_WARNINGS=$((DOC_WARNINGS + 1))
}

doc_pass() {
    echo "  OK    $1" >&2
}

# Check SCREEN files
SCREEN_COUNT=0
for f in "$SPEC_DIR"/SCREEN-*.md; do
    [ -f "$f" ] || continue
    fname=$(basename "$f")
    # Skip numbered tickets
    [[ "$fname" =~ ^SCREEN-[0-9]{3}- ]] && continue
    [ "$fname" = "SCREEN-Example.md" ] && continue
    SCREEN_COUNT=$((SCREEN_COUNT + 1))
    if ! grep -q '## Route' "$f" 2>/dev/null; then
        doc_warn "$fname missing ## Route section"
    fi
    if ! grep -q '\*\*Description:\*\*' "$f" 2>/dev/null; then
        doc_warn "$fname missing **Description:** line"
    fi
done
if [ "$SCREEN_COUNT" -gt 0 ]; then
    doc_pass "$SCREEN_COUNT screen specification(s) found"
else
    doc_warn "No SCREEN-*.md files found — screens section will be empty"
fi

# Check FEATURE files
FEATURE_COUNT=0
for f in "$SPEC_DIR"/FEATURE-*.md; do
    [ -f "$f" ] || continue
    fname=$(basename "$f")
    [[ "$fname" =~ ^FEATURE-[0-9]{3}- ]] && continue
    [ "$fname" = "FEATURE-Example.md" ] && continue
    FEATURE_COUNT=$((FEATURE_COUNT + 1))
    if ! grep -q '\*\*Description:\*\*' "$f" 2>/dev/null; then
        doc_warn "$fname missing **Description:** line"
    fi
done
if [ "$FEATURE_COUNT" -gt 0 ]; then
    doc_pass "$FEATURE_COUNT feature specification(s) found"
fi

# Check ARCHITECTURE.md
if [ -f "$SPEC_DIR/ARCHITECTURE.md" ]; then
    if ! grep -q '## Directory Layout' "$SPEC_DIR/ARCHITECTURE.md" 2>/dev/null; then
        doc_warn "ARCHITECTURE.md missing ## Directory Layout section"
    else
        doc_pass "ARCHITECTURE.md has Directory Layout"
    fi
else
    doc_warn "No ARCHITECTURE.md found — architecture section will be empty"
fi

# Check DATABASE.md
if [ -f "$SPEC_DIR/DATABASE.md" ]; then
    doc_pass "DATABASE.md found"
else
    doc_pass "No DATABASE.md (will be skipped)"
fi

# Check FUNCTIONALITY.md
if [ -f "$SPEC_DIR/FUNCTIONALITY.md" ]; then
    doc_pass "FUNCTIONALITY.md found"
else
    doc_pass "No FUNCTIONALITY.md (flows section will be skipped)"
fi

if [ "$DOC_WARNINGS" -gt 0 ]; then
    echo "  ($DOC_WARNINGS warnings — documentation may be incomplete)" >&2
fi
echo "" >&2

# --- Collect spec files ---
SPEC_FILES=$(find "$SPEC_DIR" -maxdepth 1 -name "*.md" \
    ! -name "SPEC_SCORECARD.md" \
    ! -name "SPEC_ITERATION.md" \
    ! -name "REFERENCE_GAPS.md" \
    | sort)

SPEC_FILE_COUNT=$(echo "$SPEC_FILES" | grep -c '.' 2>/dev/null || true)
echo "  Spec files: $SPEC_FILE_COUNT" >&2

# --- Build the AI prompt ---
CURRENT_DATE=$(date '+%Y-%m-%d %H:%M')
TARGET_DOCS="$TARGET/docs"

# Concatenate all spec files
SPEC_CONTENT=""
while IFS= read -r filepath; do
    [ -f "$filepath" ] || continue
    label=$(basename "$filepath")
    SPEC_CONTENT+="
---

## $label

$(cat "$filepath")
"
done <<< "$SPEC_FILES"

# --- Assemble prompt from template ---
# Escape & and \ in SHORT_DESC so sed doesn't misinterpret them in the replacement
SHORT_DESC_SAFE=$(printf '%s' "${SHORT_DESC:-}" | sed 's/[&\]/\\&/g')
PROMPT=$(tr -d '\r' < "$REPO_DIR/prompts/document.md" | sed \
    -e "s|{{DISPLAY_NAME}}|${DISPLAY_NAME:-$PROJECT_NAME}|g" \
    -e "s|{{SHORT_DESC}}|$SHORT_DESC_SAFE|g" \
    -e "s|{{STATUS}}|${STATUS:-PROTOTYPE}|g" \
    -e "s|{{TARGET_DOCS}}|$TARGET_DOCS|g" \
    -e "s|{{CURRENT_DATE}}|$CURRENT_DATE|g")

# Append dynamic specification file content
PROMPT="$PROMPT

---

## Specification Files

$SPEC_CONTENT"

# --- Phase 1: AI content generation ---
echo "" >&2
echo "Phase 1: Generating documentation content (model: $MODEL)..." >&2
echo "This may take 30-60 seconds." >&2
echo "" >&2

mkdir -p "$TARGET_DOCS"

cd "$TARGET" && echo "$PROMPT" | claude -p \
    --model "$MODEL" \
    --allowedTools "Read,Write,Glob,Grep"

echo "" >&2
echo "Phase 1 complete." >&2

# --- Phase 2: CSS assembly ---
echo "" >&2
echo "Phase 2: Assembling HTML..." >&2

mkdir -p "$TARGET_DOCS/styles/themes"
cp "$STYLES_DIR/spec-base.css" "$TARGET_DOCS/styles/spec-base.css"
cp "$THEME_FILE" "$TARGET_DOCS/styles/themes/${THEME}.css"
cat "$THEME_FILE" "$STYLES_DIR/spec-base.css" > "$TARGET_DOCS/styles/spec.css"
echo "  CSS: themes/${THEME}.css + spec-base.css → styles/spec.css" >&2

# --- Phase 2: HTML assembly ---
python3 "$REPO_DIR/bin/build_project_docs.py" \
    --target="$TARGET" \
    --theme="$THEME" \
    --spec-name="$PROJECT_NAME"

# --- Phase 3: Install build_documentation.sh in target ---
TARGET_BIN="$TARGET/bin"
mkdir -p "$TARGET_BIN"

BUILD_DOC_SCRIPT="$TARGET_BIN/build_documentation.sh"
if [ ! -f "$BUILD_DOC_SCRIPT" ] || grep -q '# Generated by document.sh' "$BUILD_DOC_SCRIPT" 2>/dev/null; then
    cat > "$BUILD_DOC_SCRIPT" << 'BUILDEOF'
#!/bin/bash
# CommandCenter Operation
# Name: Build Doc
# Category: Operations
# Generated by document.sh — safe to overwrite on next run

# Rebuilds docs/index.html from specification files.
# Delegates to Specifications/bin/document.sh for the actual build.
#
# Usage:
#   bash bin/build_documentation.sh [--theme=<name>]
#
# Arguments:
#   --theme   Theme name (default: slate)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

PROJECT_NAME="$(grep '^name:' METADATA.md 2>/dev/null | head -1 | sed 's/^name:[[:space:]]*//' | tr -d '\r')"

THEME="slate"
for arg in "$@"; do
  case "$arg" in
    --theme=*) THEME="${arg#--theme=}" ;;
  esac
done

# Find Specifications repo
SPEC_PATH="${SPECIFICATIONS_PATH:-}"
if [ -z "$SPEC_PATH" ] || [ ! -d "$SPEC_PATH" ]; then
    SPEC_PATH="$(cd "$PROJECT_DIR/../Specifications" 2>/dev/null && pwd)" || true
fi

if [ -z "$SPEC_PATH" ] || [ ! -d "$SPEC_PATH" ]; then
    echo "ERROR: Specifications repo not found." >&2
    echo "  Set SPECIFICATIONS_PATH or place at ../Specifications/" >&2
    exit 1
fi

bash "$SPEC_PATH/bin/document.sh" "$PROJECT_NAME" --theme="$THEME" --target="$PROJECT_DIR"
BUILDEOF
    chmod +x "$BUILD_DOC_SCRIPT"
    echo "  Installed: $BUILD_DOC_SCRIPT" >&2
else
    echo "  Skipped: $BUILD_DOC_SCRIPT (exists and not generated — preserving)" >&2
fi

# --- Summary ---
echo "" >&2
echo "─────────────────────────────" >&2
echo "Documentation generated:" >&2
echo "  Target:  $TARGET_DOCS/index.html" >&2
DOC_COUNT=$(find "$TARGET_DOCS" -maxdepth 1 -name "DOC-*.md" 2>/dev/null | wc -l)
echo "  Content: $DOC_COUNT DOC-*.md files" >&2
echo "  Theme:   $THEME" >&2
echo "  Date:    $CURRENT_DATE" >&2
echo "─────────────────────────────" >&2
