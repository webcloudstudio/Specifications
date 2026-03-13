# Stack Configuration for Command Center

# This file declares which technology stack files to include when building
# or reviewing this project. Each key maps to a file in PROJECT/stack/.
#
# File mapping:
#   language: python    → stack/python.md
#   framework: flask    → stack/flask.md
#   database: sqlite    → stack/sqlite.md
#   frontend: bootstrap5 → stack/bootstrap5.md
#
# stack/common.md is ALWAYS included regardless of selections.

# --- Technology Stack ---

language: python
framework: flask
database: sqlite
frontend: bootstrap5

# --- Project Configuration ---

project:
  name: GAME
  title: "GAME — Generic Agent Management Environment"
  description: "AI-assisted workflow management platform. Governs a portfolio of projects via filesystem discovery, one-click operations, observability, and GitHub Pages publishing."

  # Port for the dev server
  port: 5001

  # Python virtual environment
  venv: true

# --- Custom Stack Rules ---
# These rules are enforced by scanner.py and config_engine/ on every project.
# Example rules per the StackSpec diagram (git, bash scripts, python logging, etc.)

stack_rules:
  require_git: true
  require_bin_scripts:
    - start.sh                 # Must have start script with CommandCenter header
    - stop.sh                  # Must have stop script
  require_claude_md: true      # CLAUDE.md must exist with standard sections
  require_git_homepage_md: true  # git_homepage.md must exist for portfolio cards
  logging:
    style: python              # Use Python logging module, not print()
    output: data/logs/

# --- Standard Directories ---
# These are created by the project scaffolding.
# Paths are relative to the project root.

directories:
  data: data                   # Runtime data (DB, uploads) — gitignored
  logs: data/logs              # Script and process output logs
  backups: data/backups        # Database and file backups
  tests: tests                 # Test suite
  static: static               # Static assets (CSS, JS, images)
  templates: templates          # Server-side templates
  scripts: bin                  # Operation scripts
  docs: docs                    # Project documentation

# --- Environment Variables ---
# Required env vars that must be set (validated at startup).

env:
  required:
    - PROJECTS_DIR             # Root directory containing all managed projects
  optional:
    - SECRET_KEY               # Flask secret key (defaults to dev key)
    - PRODUCTION_URL           # Homepage URL for publishing
    - APP_NAME                 # Display name (defaults to "Command Center")

# --- Database ---

database_config:
  path: data/cc.db             # SQLite database file
  wal_mode: true               # Write-ahead logging
  foreign_keys: true           # Enforce FK constraints

# --- Specification Files ---
# The numbered spec files that describe this specific project.
# Read in order to understand the full system.

specs:
  - 01-OVERVIEW.md
  - 02-DATABASE.md
  - 03-SCANNER.md
  - 04-OPERATIONS.md
  - 05-ROUTES-API.md
  - 06-UI-TEMPLATES.md
  - 07-STYLING.md
  - 08-PUBLISHER.md
  - 09-PROCESSES.md
  - 10-CONVENTIONS.md
  - 11-STARTUP.md
