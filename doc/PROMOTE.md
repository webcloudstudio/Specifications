# Promote Prototype To Project

**Version:** 20260320 V2
**Description:** Scaffold and conform a new code project directory from a completed spec

Once a spec has been built and an AI agent has produced a working prototype, promotion
moves it into the live project infrastructure — a real git repo with platform standards,
conformance validation, and a registered port.

---

## Command Reference

Run from the `GAME/` project directory:

```
usage: create_project.py [-h] [--update] [--project NAME] [--dry-run] [name]

Create or update projects conforming to CLAUDE_RULES standards.

positional arguments:
  name            Project name to create

options:
  -h, --help      show this help message and exit
  --update        Update all set-up projects with latest rules and templates
  --project NAME  With --update, target a specific project by name
  --dry-run       Preview without writing

examples:
  python3 bin/create_project.py MyProject
      Scaffold ~/projects/MyProject/ with standard directories, METADATA.md,
      CLAUDE.md (@AGENTS.md pointer), AGENTS.md (dev commands + CLAUDE_RULES),
      bin/common.sh, bin/common.py, index.html, .gitignore, .env.sample.

  python3 bin/create_project.py MyProject --dry-run
      Preview what would be created without writing anything.

  python3 bin/create_project.py --update
      Push the latest CLAUDE_RULES.md, common.sh, common.py, and index.html to
      every set-up project (those whose AGENTS.md contains CLAUDE_RULES_START).

  python3 bin/create_project.py --update --project MyProject
      Update a single project instead of all.

  python3 bin/create_project.py --update --dry-run
      Show which projects would be updated without writing anything.

what gets created:
  MyProject/
    METADATA.md          name, display_name, port, short_description, version
    CLAUDE.md            @AGENTS.md  (pointer only)
    AGENTS.md            Dev Commands + Service Endpoints + Bookmarks + CLAUDE_RULES block
    .gitignore           Standard ignore rules from RulesEngine/gitignore
    .env.sample          Placeholder for required environment variables
    index.html           Redirect to doc/index.html
    bin/
      common.sh          Shared shell utilities (logging, venv activation, port checks)
      common.py          Shared Python utilities (config, logging, path helpers)
    logs/  data/  tests/ Empty directories with .gitkeep placeholders

after creation:
  1. Fill in METADATA.md  — set port, short_description
  2. Create bin/start.sh, bin/stop.sh, bin/test.sh
  3. git init && git remote add origin <url> && git add -A && git commit -m "Initial scaffold"
  4. python3 bin/create_project.py --update --project MyProject  (fills git_repo from remote)
  5. Feed bin/build.sh output to an AI agent to implement the application
```

---

## Step-by-Step Promotion

### Step 1 — Scaffold the Project Directory

```bash
cd ~/projects/GAME
python3 bin/create_project.py <ProjectName>
```

Creates `~/projects/<ProjectName>/` with the full platform scaffold.
Preview first with `--dry-run`.

### Step 2 — Push Platform Standards

```bash
bash bin/update_projects.sh
```

Propagates the latest `RulesEngine/` files (CLAUDE_RULES.md, common.sh, common.py,
index.html) to every set-up project. Run after any change to global standards.

```bash
bash bin/update_projects.sh --dry-run    # preview without writing
```

### Step 3 — Validate Conformance

```bash
bash bin/validate_project.sh <ProjectName> --verbose
```

Checks platform conformance. Exit 0 = conforms. Fix any flagged items before building.

| Check | Condition |
|-------|-----------|
| Required files | `AGENTS.md`, `CLAUDE.md`, `bin/common.sh`, `bin/common.py`, `index.html` |
| CLAUDE_RULES block | `AGENTS.md` contains `CLAUDE_RULES_START` marker |
| Script headers | `bin/` scripts have `# CommandCenter Operation` header |
| METADATA | `METADATA.md` exists with required fields |

### Step 4 — Initialize Git and Set Remote

```bash
cd ~/projects/<ProjectName>
git init
git remote add origin <github-url>
git add -A
git commit -m "Initial scaffold"
git push -u origin main
```

Then back in GAME/, run update so `git_repo` is written into METADATA.md:

```bash
cd ~/projects/GAME
python3 bin/create_project.py --update --project <ProjectName>
```

### Step 5 — Feed the Build Prompt to an AI Agent

```bash
cd ~/projects/Specifications
bash bin/build.sh <ProjectName> > build-prompt.md
```

Open `build-prompt.md` and give it to an AI agent running inside `~/projects/<ProjectName>/`.
The agent reads the spec and implements the application.

---

## Example: Promoting "TaskBoard"

```bash
# 1. Scaffold
cd ~/projects/GAME
python3 bin/create_project.py TaskBoard

# 2. Propagate standards
bash bin/update_projects.sh

# 3. Validate
bash bin/validate_project.sh TaskBoard --verbose

# 4. Git init
cd ~/projects/TaskBoard
git init
git remote add origin https://github.com/yourname/TaskBoard.git
git add -A && git commit -m "Initial scaffold"
git push -u origin main

# 5. Fill in git_repo in METADATA.md
cd ~/projects/GAME
python3 bin/create_project.py --update --project TaskBoard

# 6. Build prompt and hand to AI
cd ~/projects/Specifications
bash bin/build.sh TaskBoard > build-prompt.md
# → open build-prompt.md and paste into Claude Code running in ~/projects/TaskBoard/
```

After the AI agent finishes:

```bash
# Re-validate to confirm platform compliance
cd ~/projects/GAME
bash bin/validate_project.sh TaskBoard

# Restart Prototyper to pick up the new project
bash bin/stop.sh && bash bin/start.sh
```

The new project appears in Prototyper's dashboard on the next scan.
