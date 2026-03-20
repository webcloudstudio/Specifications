# Promote

**Version:** 20260320 V1
**Description:** Scaffold and conform a new code project from a completed spec

Promote takes a finished spec directory and turns it into a working code project with all
platform standards applied. Run these steps from the `GAME/` project directory.

---

## Step 1 — Scaffold the Project

```bash
cd ~/projects/GAME
python3 bin/create_project.py <ProjectName>
```

Creates `~/projects/<ProjectName>/` with:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Dev commands + injected CLAUDE_RULES block |
| `CLAUDE.md` | `@AGENTS.md` pointer |
| `bin/common.sh` | Shared shell utilities |
| `bin/common.py` | Shared Python utilities |
| `index.html` | Redirect to `doc/index.html` |

The spec files from `Specifications/<ProjectName>/` are **not** copied — the AI agent reads
the build prompt and creates the code from scratch.

---

## Step 2 — Propagate Platform Standards

```bash
bash bin/update_projects.sh
```

Pushes the latest `GLOBAL_RULES/` files (CLAUDE_RULES.md, common.sh, common.py, etc.)
to every set-up project directory. Run this whenever global standards change.

Use `--dry-run` to preview changes without writing:

```bash
bash bin/update_projects.sh --dry-run
```

---

## Step 3 — Validate Conformance

```bash
bash bin/validate_project.sh <ProjectName> --verbose
```

Checks that the project meets platform standards:

| Check | Condition |
|-------|-----------|
| Required files | `AGENTS.md`, `CLAUDE.md`, `bin/common.sh`, `bin/common.py`, `index.html` |
| CLAUDE_RULES block | `AGENTS.md` contains the injected rules block |
| Script headers | `bin/` scripts have the required `CommandCenter Operation` header |
| METADATA | `METADATA.md` exists with required fields |

Exit 0 = conforms. Exit 1 = items to fix.

---

## Step 4 — Feed the Build Prompt to an AI Agent

```bash
cd ~/projects/Specifications
bash bin/build.sh <ProjectName> > build-prompt.md
```

Open `build-prompt.md` and give it to an AI agent (Claude Code, etc.) running in
`~/projects/<ProjectName>/`. The agent reads the spec and implements the application.

---

## After the Build

Once the AI agent has implemented the project, re-run conformance:

```bash
bash bin/validate_project.sh <ProjectName>
```

Fix any flagged issues, then push the project to its remote repository.
