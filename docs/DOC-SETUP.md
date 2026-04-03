# Step 1 — Setup

Create a specification directory for a new project, or reverse-engineer an existing one.

## New Project

Run `setup.sh` to scaffold a specification directory from templates:

```bash
bash bin/setup.sh MyProject
```

This creates `Specifications/MyProject/` with template files for every specification type.
Edit each file to describe your project — concise tables and bullets, not prose.

## Existing Project

Run `decompose.sh` to generate a prompt that reverse-engineers an existing codebase
into specification files:

```bash
bash bin/decompose.sh /path/to/project > decompose-prompt.md
```

Feed the prompt to an AI agent. It reads the source code and produces structured
specification files matching the Prototyper format.

## Project Definition

Every specification directory contains these files:

| File | Purpose |
|------|---------|
| `METADATA.md` | Identity — name, stack, status, port, tags |
| `README.md` | One-line description + intent section |
| `INTENT.md` | Goals, constraints, success criteria |
| `ARCHITECTURE.md` | Modules, routes, directory layout |
| `FUNCTIONALITY.md` | What the application does — grouped by area |
| `DATABASE.md` | Tables, columns, types — schema only |
| `UI-GENERAL.md` | Shared UI patterns across screens |
| `SCREEN-{Name}.md` | Per-screen: route, layout, interactions |
| `FEATURE-{Name}.md` | Per-feature: trigger, sequence, reads, writes |
| `HOMEPAGE.md` | Portfolio page configuration (if applicable) |

All specification files except METADATA and README end with `## Open Questions`.

Write concise specifications. Tables and bullets — not paragraphs. The AI agent
expands them using the rules in `ONESHOT_BUILD_RULES.md` and the stack patterns
in `RulesEngine/stack/`.
