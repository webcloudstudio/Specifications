# AGENTS.md — Specifications Repository

This repository contains project specifications only. The prototyper tooling (`bin/`, `RulesEngine/`, `prompts/`) lives in the **prototyper** repository at `../prototyper/`.

## Purpose

Each subdirectory is a project specification — a set of concise markdown files that define what to build. The prototyper's `bin/` scripts read specs from this directory via the `specification_directory: ../Specifications` field in `../prototyper/METADATA.md`.

## Wording

Use the word specification in preference to spec except in program names.

## Specification Authoring

Specifications consist of structured markdown files. Each project directory must have:

| File | Purpose | Required |
|------|---------|----------|
| `METADATA.md` | Project identity (name, display_name, short_description, status) | Yes |
| `README.md` | One-line description + `## Intent` section | Yes |
| `INTENT.md` | Standalone intent document — goals, constraints, success criteria | Yes |
| `ARCHITECTURE.md` | Modules, routes, directory layout | Yes |
| `FUNCTIONALITY.md` | What the application does — high-level feature summary | Yes |
| `DATABASE.md` | Tables, columns, types | If has DB |
| `UI-GENERAL.md` | Shared UI patterns | If has UI |
| `SCREEN-{Name}.md` | Per-screen: route, layout, interactions | If has UI |
| `FEATURE-{Name}.md` | Per-feature: trigger, sequence, reads, writes | As needed |

All specification files (except README, METADATA, and generated files) end with `## Open Questions`.

**Authoring phase — do not create during active authoring:**
- `REFERENCE_GAPS.md`, `SPEC_SCORECARD.md`, `SPEC_ITERATION.md` (run `spec_iterate.sh` after spec is stable)
- Numbered ticket files (`SCREEN-NNN-*`, `FEATURE-NNN-*`, `PATCH-NNN-*`, `AC-NNN-*`) (post-build only)

## Workflow (run from the prototyper directory)

```bash
cd ../prototyper

# Scaffold a new specification directory here in Specifications/
bash bin/setup.sh <ProjectName>

# Validate
bash bin/validate.sh <ProjectName>

# Generate build prompt
bash bin/oneshot.sh <ProjectName> > ../Specifications/<ProjectName>/oneshot-prompt.md
```

## Projects

| Directory | Description |
|-----------|-------------|
| `GAME/` | GAME dashboard specification |
| `Wyckoff/` | Wyckoff trading system specification |
| `Proposed.AlexaPrototypeOne/` | Alexa prototype specification |
