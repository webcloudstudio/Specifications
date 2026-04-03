# Step 2 — OneShot

Generate a single AI build prompt from your specification files. The AI agent reads
the prompt and builds the entire application in one pass.

## How It Works

`oneshot.sh` validates your specification, then assembles everything the AI needs:

- Your specification files (what to build)
- Stack patterns from `RulesEngine/stack/` (how to build it)
- Agent rules from `CLAUDE_RULES.md` (constraints and conventions)

The output is one prompt. One prompt, one build.

```bash
bash bin/oneshot.sh MyProject > MyProject/oneshot-prompt.md
```

## Build Modes

| Mode | When | What happens |
|------|------|-------------|
| **New project** | No `git_repo` in METADATA | Generates prompt only — you create the project directory and run the AI |
| **Feature branch** | `git_repo` + `BUILD_FEATURE_BRANCH_NAME` in `.env` | Clones/fetches, creates branch, generates prompt |
| **Update** | `--update` flag | Generates prompt targeting specification changes against existing code |

## Traceability

Every build creates an annotated git tag: `oneshot/MyProject/2026-04-02.1`

Tags are permanent. You can diff between builds at the specification level:

```bash
git diff oneshot/MyProject/2026-03-20.1..oneshot/MyProject/2026-04-02.1 -- MyProject/
```
