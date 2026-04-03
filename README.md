# Specifications

Platform standards and project specifications for AI-orchestrated development.

## Roles

1. **RulesEngine** (`RulesEngine/`) — agent behavior contract, stack patterns, branding, and spec templates. Distributed to all projects by `create_project.py` / `update_projects.sh`.
2. **Project specifications** (`GAME/`, etc.) — concise specs (screens, features, architecture) that `build.sh` assembles into AI build prompts.

Operational tasks (pushing repos, running services) live in GAME. This repo is the standards authority.

## Workflow

```bash
# 1. Create a spec directory
bash bin/setup.sh <ProjectName>

# 2. Validate it
bash bin/validate.sh <ProjectName>

# 3. Build an AI prompt from the spec
bash bin/build.sh <ProjectName> > build-prompt.md

# 4. Promote to a live code project (run from GAME/)
python3 bin/create_project.py <ProjectName>
bash bin/update_projects.sh

# 5. Regenerate agent rules after editing RulesEngine/BUSINESS_RULES.md
bash bin/summarize_rules.sh > rules-prompt.md
# Feed rules-prompt.md to an AI agent → paste output over RulesEngine/CLAUDE_RULES.md
```

## Structure

```
Specifications/
  RulesEngine/                     Agent rules, stack patterns, branding, spec templates
    BUSINESS_RULES.md              Source for CLAUDE_RULES.md — edit here, then regenerate
    CLAUDE_RULES.md                Generated agent behavior contract (injected into projects)
    CONVERT.md                     Spec expansion rules (concise → detailed)
    DOCUMENTATION_BRANDING.md      Color variables, typography, theme standards
    stack/                         Prescriptive tech patterns (flask.md, sqlite.md, ...)
    spec_template/                 Template files for setup.sh
    templates/                     Canonical common.sh and common.py for code projects
    gitignore                      Standard .gitignore distributed to projects

  bin/                             Spec tooling (accept any directory: name, /abs, or ./rel)
    setup.sh                       Scaffold or update a spec directory from templates
    validate.sh                    Validate a spec directory for completeness and correctness
    convert.sh                     Generate concise→detailed expansion prompt
    build.sh                       Tag commit + generate complete build prompt
    summarize_rules.sh       Regenerate CLAUDE_RULES.md from BUSINESS_RULES.md
    test.sh                        Self-test the specification system

  GAME/                            GAME project specification
  data/                            HTML viewer templates (used by build_documentation.py)
  docs/                            Generated documentation
  archive/                         Superseded documents — not current spec
```

## Key Conventions

- **METADATA.md** — `key: value` format (not YAML). Single source of project identity.
- **AGENTS.md** — AI context file. Each project's `CLAUDE.md` is a bare `@AGENTS.md` pointer.
- **BUSINESS_RULES.md** — Edit rules here; never edit `CLAUDE_RULES.md` directly.
- **RulesEngine/stack/** — One prescriptive `.md` per technology. Referenced by build and convert prompts.
- **Version format** — `YYYY-MM-DD.N` (e.g., `2026-03-20.1`).
