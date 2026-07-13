# ARCHITECTURE: Setup Analyze

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | How the --analyze agent integrates with setup.sh and the existing toolchain. |

## Overview

`--analyze` is a new flag on `bin/setup.sh`. It delegates to a new script `bin/analyze_spec.sh` (or `bin/analyze_spec.py`) which assembles an LLM prompt and calls `claude -p`.

```
bin/setup.sh <ProjectName> --analyze
  └─► bin/analyze_spec.sh <ProjectDir>
        ├─ reads: all *.md files in <ProjectDir> that are NOT .imported
        ├─ reads: RulesEngine/SPECIFICATION_CONTRACT.md  (contract)
        ├─ reads: prompts/analyze_ingest.md              (conversion instructions)
        ├─ calls: claude -p  (LLM agent)
        └─ writes: conformed files into <ProjectDir>
              renames: original files → *.imported
```

## Modules

| File | Purpose |
|------|---------|
| `bin/setup.sh` | Add `--analyze` flag detection; call `analyze_spec.sh` when triggered |
| `bin/analyze_spec.sh` | Orchestrate: build prompt → call claude -p → rename originals → run validate |
| `prompts/analyze_ingest.md` | LLM prompt: rules for converting raw spec content into conformed files |
| `RulesEngine/ingest_templates/` | Saved format templates for recognized non-conformed file shapes |
| `bin/validate.sh` | Called after analysis to score the output (existing, unchanged) |

## Auto-Trigger Logic (setup.sh --create)

When `setup.sh <Name>` is called without `--update` or `--force`:
1. If directory does not exist → create from template (existing behavior)
2. If directory exists AND has METADATA.md → error: use --update or --force (existing behavior)
3. **NEW**: If directory exists AND has `.md` files but NO METADATA.md → auto-call `--analyze`

## Ingest Template Persistence

After a successful analyze run, the agent writes a template fingerprint to `RulesEngine/ingest_templates/<slug>.md` containing:
- The structural heuristics that identified this file shape (section headings found, keywords)
- The mapping decisions made (which content went into which conformed file)
- This is used on subsequent `--analyze` runs to provide the agent with precedent

## Directory Layout Impact

```
Prototyper/
  bin/
    setup.sh              (modified: --analyze flag)
    analyze_spec.sh       (new)
  prompts/
    analyze_ingest.md     (new: LLM conversion prompt)
  RulesEngine/
    ingest_templates/     (new: persisted format templates)
```

## Open Questions

- Should `analyze_spec.sh` be a Bash script driving `claude -p` (like `spec_iterate.sh`) or a Python script (like `build_plan_auto.py`)? Bash is simpler and consistent with the existing pattern.
- Token budget: the SPECIFICATION_CONTRACT is large. Should it be passed in full or as a compact summary for the analyze prompt?
