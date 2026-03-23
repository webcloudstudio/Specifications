#!/bin/bash
# CommandCenter Operation
# Name: Build
# Category: maintenance
#
# DEPRECATED: oneshot.sh now handles both build modes automatically.
# This script is a backward-compatible wrapper — use bin/oneshot.sh directly.
#
# Feature Branch mode (git_repo + BUILD_FEATURE_BRANCH_NAME set):
#   oneshot.sh clones/fetches the project and creates the feature branch automatically.
#
# Bootstrap mode (no git_repo):
#   oneshot.sh writes <spec>/bootstrap.sh with absolute paths to create the target directory.
#
# Usage (identical to oneshot.sh):
#   bash bin/build.sh <spec-name>                    # Print prompt to stdout
#   bash bin/build.sh <spec-name> > build-prompt.md  # Save to file
#   bash bin/build.sh <spec-name> --dry-run          # Ignored (kept for backward compat)

exec bash "$(dirname "${BASH_SOURCE[0]}")/oneshot.sh" "$@"
