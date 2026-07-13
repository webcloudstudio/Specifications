# FEATURE: ProjectValidate.sh Updates

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Add --summary mode to ProjectValidate.sh with color-coded conformance metrics and .sh script classification. |
| Phase       | 4 |

## Trigger

`bash bin/ProjectValidate.sh <project> --summary`

New mode added to the existing script. Existing behavior (`verify <project>`) is unchanged.

## --summary Output Format

```
┌─────────────────────────────────────────────────────┐
│  ProjectValidate: MyProject  —  2026-05-19          │
├─────────────────────────────────────────────────────┤
│  CLAUDE_RULES Compliance                            │
│  ✅ METADATA.md present                             │
│  ✅ AGENTS.md present                               │
│  ✅ bin/common.sh Python fallback                   │
│  ⚠️  bin/start.sh: complex bash — consider .py     │
│  ❌ bin/test.sh missing                             │
│                                                     │
│  Script Classification                              │
│  Standard managed:  common.sh ✅  start.sh ✅       │
│                     stop.sh  ✅  test.sh ❌ missing │
│  App-specific:      ingest.sh  analyze.sh           │
│                                                     │
│  Conversion Analysis                                │
│  Python-fallback:  2 / 5 scripts                   │
│  Should → Python:  ingest.sh (complexity: HIGH)    │
│                    analyze.sh (complexity: HIGH)   │
│  .bat feasibility: 3 / 5 straightforward drivers   │
│                                                     │
│  Overall: 3 / 5 checks passing  🟡 PARTIAL         │
└─────────────────────────────────────────────────────┘
```

## Complexity Classification for .sh Scripts

`ProjectValidate.sh --summary` analyzes each `.sh` script and assigns:

| Complexity | Rule |
|-----------|------|
| DRIVER | < 30 lines, only argument parsing + one exec/source call |
| MEDIUM | 30-100 lines, some logic |
| HIGH | > 100 lines, loops, conditionals, awk/sed processing |

Scripts with complexity HIGH are flagged as candidates for Python conversion.

## .bat Feasibility

A script is "straightforward to convert to .bat" if:
- It only calls executables by name (no `$(...)` subprocess substitution)
- It uses only basic conditionals
- It does not use process substitution (`>(...)`)

## Color Standards

- Green (✅): passing check
- Yellow (⚠️): warning / recommendation
- Red (❌): failing check / missing required file

Uses ANSI codes directly (consistent with existing Prototyper bash scripts).

## Success Criteria

- `--summary` mode prints colored output for any project.
- Correctly identifies `bin/common.sh` with the Python fallback block as conformant.
- Correctly identifies scripts above complexity HIGH threshold.
- Overall score is numeric (N / M checks passing) with a visual signal level (PASS / PARTIAL / FAIL).
- Existing `--verbose` mode behavior is unchanged.

## Open Questions

- Should the complexity analysis use `wc -l` line count only, or also scan for `awk`/`sed`/`grep` pipelines as a secondary heuristic?
- Should `--summary` mode write a `SCORECARD.md` file to the project directory, or is stdout-only acceptable?
- Should v1.01.sh call `--summary` per project and aggregate results into a workspace-level report?
