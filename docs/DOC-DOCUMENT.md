# Step 6 — Document

Generate project documentation from specification files using AI summarization.

## How It Works

`document.sh` is an agent program that runs a two-phase pipeline:

1. **Phase 1: AI summarization** — `claude -p` reads specification files and writes curated `DOC-*.md` summaries into the target project's `docs/` directory.
2. **Phase 2: HTML assembly** — `build_project_docs.py` reads those summaries, discovers `bin/` scripts via CommandCenter headers, and assembles a single-page documentation app.

```bash
bash bin/document.sh <ProjectName>
bash bin/document.sh <ProjectName> --target=../GAME_p2
bash bin/document.sh <ProjectName> --theme=slate --model=opus
```

## Inputs

| File | Purpose |
|------|---------|
| `METADATA.md` | Project name, description, status |
| `README.md` | Project intent and overview |
| `SCREEN-*.md` | Screens — requires `## Route` and `**Description:**` |
| `FEATURE-*.md` | Features — requires `**Description:**` |
| `ARCHITECTURE.md` | Architecture — requires `## Directory Layout` |
| `DATABASE.md` | Schema (optional) |
| `FUNCTIONALITY.md` | Flows (optional) |

## Outputs

`DOC-*.md` files persist in the target's `docs/` and serve as the source for rebuilds. Edit them directly to customize.

| File | Content |
|------|---------|
| `DOC-OVERVIEW.md` | Project overview |
| `DOC-SCREENS.md` | Screen summaries |
| `DOC-FEATURES.md` | Feature summaries |
| `DOC-ARCHITECTURE.md` | Architecture summary |
| `DOC-DATABASE.md` | Database summary (if DATABASE.md exists) |
| `DOC-FLOWS.md` | Flow summaries (if FUNCTIONALITY.md exists) |

## Rebuild

After the first run, `bin/build_documentation.sh` is installed in the target project:

```bash
bash bin/build_documentation.sh
bash bin/build_documentation.sh --theme=slate
```

## Specification Readiness

Run `validate.sh` first — it warns about missing `## Route`, `**Description:**`, or `## Directory Layout` before the AI runs:

```bash
bash bin/validate.sh <ProjectName>
```
