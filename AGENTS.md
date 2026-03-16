# AGENTS.md — Specifications Repository

## What This Repo Is

A platform specification and standards repository. It defines:
- **CLAUDE_RULES.md** — the agent behavior contract all projects must embed
- **PROCESS_RULES.md** — the full canonical compliance standard
- **stack/** — prescriptive, copy-paste-ready tech reference files per technology
- **templates/** — canonical `common.sh` and `common.py` distributed to all projects
- **GAME/** and **AlexaPrototypeOne/** — project specifications organized by screen/component

## Dev Commands

```bash
# Create a new project
python3 bin/create_project.py <name>

# Update all set-up projects with latest CLAUDE_RULES and templates
bash bin/update_projects.sh

# Validate a single project against compliance rules
bash bin/validate_project.sh <name>
bash bin/validate_project.sh <name> --verbose

# Build a complete AI build prompt for a project
bash bin/generate_prompt.sh GAME > build-prompt.md

# Regenerate browsable HTML index
bash bin/rebuild_index.sh

# Scan all projects for compliance
python3 bin/validate_project.py --projects ..

# Dry-run update
bash bin/update_projects.sh --dry-run
```

## Architecture

### bin/create_project.py
Creates new projects and updates existing ones.
- **Create mode** (`<name>`): scaffolds directory, METADATA.md, CLAUDE.md (@AGENTS.md), AGENTS.md with CLAUDE_RULES injected, bin/common.sh, bin/common.py, .env.sample, .gitignore
- **Update mode** (`--update`): scans all projects in `../`; updates only those with `CLAUDE_RULES_START` marker (= set-up projects). Projects without it are skipped (idea phase). Updates CLAUDE_RULES block + common.sh/common.py templates.
- **Flag for set-up**: presence of `# CLAUDE_RULES_START` in AGENTS.md (or CLAUDE.md if not a redirect)

### bin/validate_project.sh
Thin wrapper around `bin/verify.py` for a single project. Auto-detects projects directory.

### bin/validate_project.py
Compliance scanner. Reads each project's METADATA.md, determines its `status`, and applies cumulative rules per level (IDEA → PROTOTYPE → ACTIVE → PRODUCTION). Exit 0 = pass, 1 = fail. Requires `--projects <dir>` argument.

### bin/generate_prompt.sh
Builds a complete AI agent prompt by reading `stack:` from METADATA.md, mapping tokens to `stack/*.md` reference files, then concatenating: header + CLAUDE_RULES.md + stack files + all project `*.md` specs.

### templates/
Canonical source for `common.sh` and `common.py`. `create_project.py` copies these into `bin/` of new projects; `--update` refreshes them in existing set-up projects.

### METADATA.md format
Line-based key-value (not YAML). Parsed with grep/sed. Required fields:
```
name: <slug>
display_name: <Human Name>
port: 5000
short_description: One sentence.
health: /health
```

### Project spec organization
- **GAME/** — organized by screen (SCREEN-*.md) + ARCHITECTURE.md + DATABASE.md
- **AlexaPrototypeOne/** — organized numerically (01-OVERVIEW.md … 11-STARTUP.md)
- **stack/** — one file per technology (flask.md, sqlite.md, aws-sqs.md, etc.)

## Key Conventions

- CLAUDE.md in each project is a bare `@AGENTS.md` pointer; AGENTS.md holds the real instructions
- `archive/` holds superseded documents — do not treat as current spec
- `index.html` files are auto-generated; edit the templates (`_root_index_template.html`, `_project_index_template.html`), not the outputs
